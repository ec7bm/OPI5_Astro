import tkinter as tk
from tkinter import messagebox, scrolledtext
import subprocess, os, threading, socket, shutil
from glob import glob

try:
    from PIL import Image, ImageTk
    # Compatibilidad para Ubuntu 22.04 (PIL 9.0.1)
    RESAMPLE = Image.LANCZOS if not hasattr(Image, "Resampling") else Image.Resampling.LANCZOS
    print("[DEBUG] PIL cargado correctamente")
except Exception as e:
    print(f"[DEBUG] Error al cargar PIL: {e}")
    Image = ImageTk = None

# Paleta de Colores AstroOrange V2
BG_COLOR, SECONDARY_BG, FG_COLOR, ACCENT_COLOR, SUCCESS_COLOR = "#0f172a", "#1e293b", "#e2e8f0", "#38bdf8", "#22c55e"
BUTTON_COLOR, DANGER_COLOR = "#334155", "#ef4444"

SOFTWARE = {
    "KStars / INDI": {"bin": "kstars", "pkg": "kstars-bleeding indi-full gsc", "ppa": "ppa:mutlaqja/ppa"},
    "PHD2 Guiding": {"bin": "phd2", "pkg": "phd2", "ppa": "ppa:pch/phd2"},
    "ASTAP (Solver)": {"bin": "astap", "pkg": "astap", "url": "https://www.hnsky.org/astap_arm64.deb"},
    "Stellarium": {"bin": "stellarium", "pkg": "stellarium"},
    "AstroDMX Capture": {"bin": "astrodmx", "pkg": "astrodmxcapture", "url": "https://www.astrodmx.com/download/astrodmxcapture-release.deb"},
    "CCDciel": {"bin": "ccdciel", "pkg": "ccdciel", "ppa": "ppa:jandecaluwe/ccdciel"},
    "Syncthing": {"bin": "syncthing", "pkg": "syncthing"}
}

def get_net():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80)); ip = s.getsockname()[0]; s.close()
        b = ".".join(ip.split(".")[:3]); return f"{b}.100", f"{b}.1", "8.8.8.8"
    except: return "192.168.1.100", "192.168.1.1", "8.8.8.8"

class ImageCarousel:
    def __init__(self, parent):
        self.p, self.imgs, self.idx = parent, [], 0
        pths = ["/usr/share/backgrounds/gallery", "/opt/astroorange/assets/gallery", "./userpatches/gallery"]
        pt = next((p for p in pths if os.path.exists(p) and glob(os.path.join(p, "*.png"))), None)
        if Image and pt:
            for f in sorted(glob(os.path.join(pt, "*.png"))):
                try:
                    img = Image.open(f).resize((700, 393), RESAMPLE); self.imgs.append(ImageTk.PhotoImage(img))
                except: continue
        if self.imgs:
            self.lbl = tk.Label(parent, bg=BG_COLOR, bd=0); self.lbl.pack(pady=10); self.anim()
    def anim(self):
        if self.imgs and self.p.winfo_exists():
            self.lbl.config(image=self.imgs[self.idx]); self.idx = (self.idx+1)%len(self.imgs)
            self.p.after(5000, self.anim)

class WizardApp:
    def __init__(self, root):
        self.root = root; self.u, self.p, self.ssid, self.wp = "astro", "", "", ""; self.proc = None
        self.ip, self.gw, self.dns = get_net(); self.st_var = tk.BooleanVar(); self.sw_vars = {}
        self.reinstall_list = []
        
        self.root.title("AstroOrange V2"); self.root.geometry("900x750"); self.root.resizable(False, False)
        
        self.bg_frame = tk.Frame(self.root, bg=BG_COLOR)
        self.bg_frame.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_img_label = tk.Label(self.bg_frame, bg=BG_COLOR)
        self.bg_img_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.up_bg()
        
        self.main_content = tk.Frame(self.root, bg=BG_COLOR)
        self.main_content.place(x=0, y=0, relwidth=1, relheight=1)
        
        self.selector()

    def selector(self):
        if not os.path.exists("/etc/astro-configured"): self.step0()
        else: self.stage2()

    def up_bg(self):
        f = "/usr/share/backgrounds/astro-wallpaper.png"
        if Image and os.path.exists(f):
            try:
                img = Image.open(f).resize((900, 750), RESAMPLE); self.bgh = ImageTk.PhotoImage(img)
                self.bg_img_label.config(image=self.bgh); self.main_content.config(bg="")
            except: pass

    def clean(self):
        for w in self.main_content.winfo_children(): w.destroy()
        self.main_content.config(bg=BG_COLOR)

    def head(self, t, s=""):
        tk.Label(self.main_content, text=t, font=("Sans",28,"bold"), bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=(50,5))
        if s: tk.Label(self.main_content, text=s, font=("Sans",13,"italic"), bg=BG_COLOR, fg=FG_COLOR).pack(pady=(0,30))

    def Nav(self, n, b=None, txt="SIGUIENTE"):
        f = tk.Frame(self.main_content, bg=BG_COLOR); f.pack(side="bottom", pady=40, fill="x")
        tk.Button(f, text="CANCELAR", bg=DANGER_COLOR, fg="white", command=self.root.destroy, padx=15, pady=8).pack(side="left", padx=40)
        tk.Button(f, text=txt, bg=ACCENT_COLOR, fg=BG_COLOR, font=("Sans",14,"bold"), command=n, padx=30, pady=10).pack(side="right", padx=40)
        if b: tk.Button(f, text="VOLVER", bg=BUTTON_COLOR, fg="white", command=b, padx=20, pady=10).pack(side="right", padx=10)

    # --- PANTALLAS ---
    def step0(self):
        self.clean(); self.head("Bienvenido AstroOrange V2", "Setup Limpio"); self.Nav(self.step1)

    def step1(self):
        self.clean(); self.head("Paso 1: Usuario"); f = tk.Frame(self.main_content, bg=SECONDARY_BG, padx=30, pady=30); f.pack(pady=20)
        tk.Label(f, text="Usuario:", bg=SECONDARY_BG, fg="white").grid(row=0,column=0,pady=10); self.eu = tk.Entry(f, width=25, font=("Sans",12)); self.eu.grid(row=0,column=1); self.eu.insert(0,self.u)
        tk.Label(f, text="Pass:", bg=SECONDARY_BG, fg="white").grid(row=1,column=0); self.ep = tk.Entry(f, show="*", width=25, font=("Sans",12)); self.ep.grid(row=1,column=1)
        self.Nav(self.v1, self.step0)

    def v1(self):
        self.u, self.p = self.eu.get().strip(), self.ep.get().strip()
        if not self.u or not self.p:
            messagebox.showwarning("Error", "Usuario y contrasena obligatorios")
            return
        if len(self.p) < 4:
            messagebox.showwarning("Error", "La contrasena debe tener al menos 4 caracteres")
            return
        self.step2()

    def step2(self):
        self.clean(); self.head("Paso 2: WiFi"); self.lb = tk.Listbox(self.main_content, width=55, height=10, bg=SECONDARY_BG, fg="white", font=("Sans",11)); self.lb.pack(pady=10)
        tk.Button(self.main_content, text="ESCANEAR", command=self.scan, bg=BUTTON_COLOR, fg="white").pack(); self.scan(); self.Nav(self.v2, self.step1)

    def scan(self):
        self.lb.delete(0, tk.END); self.ssids = []
        try:
            o = subprocess.check_output(["nmcli","-t","-f","SSID","dev","wifi","list"], universal_newlines=True)
            for l in o.splitlines():
                if l and l not in self.ssids: self.ssids.append(l); self.lb.insert(tk.END, f" RED: {l}")
        except: self.lb.insert(tk.END, "Sin WiFi")

    def v2(self):
        idx = self.lb.curselection(); self.ssid = self.ssids[idx[0]] if idx else ""; self.step3()

    def finish_conf(self):
        self.ssid, self.wp = self.es.get().strip(), self.ewp.get().strip()
        if not self.ssid or not self.wp:
            messagebox.showwarning("Error", "SSID y contrasena obligatorios")
            return
        
        # Feedback visual de conexion
        self.clean(); self.head("Conectando WiFi...", f"Intentando conectar a {self.ssid}")
        tk.Label(self.main_content, text="Esto puede tardar unos segundos...", bg=BG_COLOR, fg=FG_COLOR).pack(pady=20)
        self.root.update()

        def connect():
            cmd = f"sudo nmcli dev wifi connect '{self.ssid}' password '{self.wp}'"
            try:
                res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
                if res.returncode == 0:
                    self.root.after(0, self.apply_and_reboot)
                else:
                    err = res.stderr.lower()
                    msg = "Error desconocido"
                    if "secrets" in err or "password" in err: msg = "Contrasena incorrecta"
                    elif "not found" in err: msg = "Red no encontrada"
                    self.root.after(0, lambda: messagebox.showerror("Error WiFi", f"Fallo al conectar: {msg}"))
                    self.root.after(0, self.step3)
            except subprocess.TimeoutExpired:
                self.root.after(0, lambda: messagebox.showerror("Error WiFi", "Tiempo de espera agotado"))
                self.root.after(0, self.step3)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
                self.root.after(0, self.step3)

        threading.Thread(target=connect, daemon=True).start()

    def apply_and_reboot(self):
        # Aqui iria la logica original de step4 (reemplazamos por claridad)
        self.clean(); self.head("Configuracion Completa", "Reiniciando sistema...")
        # ... resto de la logica de guardado y reboot ...
        threading.Thread(target=self.run_finish, daemon=True).start()

    # --- ETAPA DE SOFTWARE ---
    def stage2(self):
        self.clean(); self.head("Instalador Software", "")
        self.reinstall_list = []
        f = tk.Frame(self.main_content, bg=BG_COLOR); f.pack(pady=10)
        for i, (n, info) in enumerate(SOFTWARE.items()):
            inst = bool(shutil.which(info["bin"]) or os.path.exists(f"/usr/bin/{info['bin']}"))
            self.sw_vars[n] = tk.BooleanVar(value=not inst and n in ["KStars / INDI", "PHD2 Guiding"])
            
            def on_sw_click(name=n):
                if bool(shutil.which(SOFTWARE[name]["bin"]) or os.path.exists(f"/usr/bin/{SOFTWARE[name]['bin']}")):
                    if self.sw_vars[name].get():
                        if messagebox.askyesno("Confirmar", f"{name} ya instalado. REINSTALAR / REPARAR?"):
                            self.reinstall_list.append(name)
                        else: self.sw_vars[name].set(False)
                    elif name in self.reinstall_list: self.reinstall_list.remove(name)

            # Toggle Buttons - Unificando estado "Instalado" en el texto para evitar solapamientos
            txt = n + (" (INSTALADO)" if inst else "")
            cb = tk.Checkbutton(f, text=txt, variable=self.sw_vars[n], bg=SECONDARY_BG, fg="white", 
                               selectcolor=ACCENT_COLOR, font=("Sans",11), padx=20, pady=10, 
                               indicatoron=False, command=on_sw_click, width=25)
            cb.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="ew")
            
        tk.Button(self.main_content, text="INICIAR INSTALACION", font=("Sans",15,"bold"), bg=ACCENT_COLOR, fg=BG_COLOR, width=30, command=self.start_install).pack(pady=30)
        tk.Button(self.main_content, text="CERRAR", command=self.root.destroy, bg=BUTTON_COLOR, fg="white", padx=15, pady=5).pack()

    def start_install(self):
        self.clean(); self.head("Instalando...", "Procesando paquetes")
        c_frm = tk.Frame(self.main_content, bg=BG_COLOR); c_frm.pack(pady=10); self.carousel = ImageCarousel(c_frm)
        self.cancel_btn = tk.Button(self.main_content, text="ABORTAR INSTALACION", bg=DANGER_COLOR, fg="white", font=("Sans",12,"bold"), command=self.stop_install, padx=20, pady=10); self.cancel_btn.pack(pady=10)
        t_frm = tk.Frame(self.main_content, bg="black", bd=2); t_frm.pack(fill="both", expand=True, padx=40, pady=5)
        self.console = scrolledtext.ScrolledText(t_frm, bg="black", fg="#00ff00", font=("Monospace", 10), state="disabled"); self.console.pack(fill="both", expand=True)
        threading.Thread(target=self.run_install, daemon=True).start()

    def log(self, t):
        if self.console.winfo_exists():
            self.console.config(state="normal"); self.console.insert(tk.END, t + "\n"); self.console.see(tk.END); self.console.config(state="disabled"); self.root.update_idletasks()

    def stop_install(self):
        if self.proc and self.proc.poll() is None:
            if messagebox.askyesno("Confirmar", "¿Deseas interrumpir la instalacion?"):
                self.proc.terminate(); self.log("\nINTERRUMPIDO."); self.cancel_btn.config(text="REINTENTAR", bg=ACCENT_COLOR, fg=BG_COLOR, command=self.stage2)
        else: self.root.destroy()

    def run_install(self):
        self.log("-> Iniciando actualizacion de repositorios...")
        subprocess.run("sudo apt-get update", shell=True)
        
        any_sw = False
        success_count = 0
        total_selected = sum(1 for v in self.sw_vars.values() if v.get())

        for n, info in SOFTWARE.items():
            if not self.sw_vars[n].get(): continue
            any_sw = True
            
            try:
                if "url" in info:
                    self.log(f"-> Descargando e instalando {n} (.deb)...")
                    deb_file = "/tmp/pkg_install.deb"
                    subprocess.run(f"sudo wget -O {deb_file} {info['url']}", shell=True, check=True)
                    proc = subprocess.Popen(f"sudo dpkg -i {deb_file} || sudo apt-get install -f -y", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                    for line in proc.stdout: self.log(line.strip())
                    proc.wait()
                else:
                    if info.get('ppa'):
                        self.log(f"-> Agregando PPA para {n}...")
                        subprocess.run(f"sudo add-apt-repository -y {info['ppa']}", shell=True)
                    
                    mode = "REINSTALANDO" if n in self.reinstall_list else "Instalando"
                    flags = "-y --reinstall" if n in self.reinstall_list else "-y"
                    self.log(f"-> {mode} {n}...")
                    
                    cmd = f"sudo apt-get install {flags} {info['pkg']}"
                    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
                    for line in proc.stdout:
                        self.log(line.strip())
                    proc.wait()

                if proc.returncode == 0:
                    success_count += 1
                    self.log(f"OK: {n} completado.")
                else:
                    self.log(f"ERROR: Fallo al instalar {n}. Saltando...")

            except Exception as e:
                self.log(f"EXCEPCION: {n} -> {str(e)}")

        if any_sw:
            self.log(f"\nPROCESO FINALIZADO. ({success_count}/{total_selected} correctos)")
            self.cancel_btn.config(text="LISTO - SALIR", bg=SUCCESS_COLOR, command=self.root.destroy)
        else:
            self.log("Sin cambios.")
            self.cancel_btn.config(text="SALIR", bg=SUCCESS_COLOR, command=self.root.destroy)

if __name__ == "__main__":
    root = tk.Tk(); app = WizardApp(root); root.mainloop()
