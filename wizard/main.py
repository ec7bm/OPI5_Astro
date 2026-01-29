import tkinter as tk
from tkinter import messagebox, scrolledtext
import subprocess, os, threading, socket, shutil
from glob import glob
try:
    from PIL import Image, ImageTk
    print("[DEBUG] PIL loaded successfully")
except Exception as e:
    print(f"[DEBUG] PIL load failed: {e}")
    Image = ImageTk = None

# Pure Premium Styles
BG_COLOR, SECONDARY_BG, FG_COLOR, ACCENT_COLOR, SUCCESS_COLOR = "#0f172a", "#1e293b", "#e2e8f0", "#38bdf8", "#22c55e"
BUTTON_COLOR = "#334155"

SOFTWARE = {
    "KStars / INDI": {"bin": "kstars", "pkg": "kstars-bleeding indi-full gsc", "ppa": "ppa:mutlaqja/ppa"},
    "PHD2 Guiding": {"bin": "phd2", "pkg": "phd2", "ppa": "ppa:pch/phd2"},
    "ASTAP (Plate Solver)": {"bin": "astap", "pkg": "astap", "url": "https://www.hnsky.org/astap_arm64.deb"},
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
                    img = Image.open(f).resize((700, 393), Image.Resampling.LANCZOS)
                    self.imgs.append(ImageTk.PhotoImage(img))
                except: continue
        if self.imgs:
            self.lbl = tk.Label(parent, bg=BG_COLOR, bd=0); self.lbl.pack(pady=10); self.anim()
    def anim(self):
        if self.imgs and self.p.winfo_exists():
            self.lbl.config(image=self.imgs[self.idx]); self.idx = (self.idx+1)%len(self.imgs)
            self.p.after(5000, self.anim)

class WizardApp:
    def __init__(self, root):
        self.root = root
        self.u, self.p, self.ssid, self.wp = "astro", "", "", ""
        self.ip, self.gw, self.dns = get_net()
        self.st_var = tk.BooleanVar(); self.sw_vars = {}
        
        self.root.title("AstroOrange V2 - Premium Wizard"); self.root.geometry("900x750"); self.root.resizable(False, False)
        
        # Super-Layered Background
        self.bg_frame = tk.Frame(self.root, bg=BG_COLOR); self.bg_frame.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_img_label = tk.Label(self.bg_frame, bg=BG_COLOR); self.bg_img_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.up_bg()
        
        # Main Content Frame (transparent-ish)
        self.main_content = tk.Frame(self.root, bg=""); self.main_content.place(x=0, y=0, relwidth=1, relheight=1)
        self.main_content.config(bg="") # Transparent trick
        
        if "--autostart" in os.sys.argv and os.path.exists("/etc/astro-finished"):
            root.destroy(); return
        
        self.stage_selector()

    def stage_selector(self):
        if not os.path.exists("/etc/astro-configured"): self.step0()
        else: self.stage2()

    def up_bg(self):
        f = "/usr/share/backgrounds/astro-wallpaper.png"
        if Image and os.path.exists(f):
            try:
                img = Image.open(f).resize((900, 750), Image.Resampling.LANCZOS)
                self.bgh = ImageTk.PhotoImage(img)
                self.bg_img_label.config(image=self.bgh)
            except: pass

    def clean(self):
        for w in self.main_content.winfo_children(): w.destroy()

    def head(self, t, s=""):
        tk.Label(self.main_content, text=t, font=("Sans",28,"bold"), bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=(50,5))
        if s: tk.Label(self.main_content, text=s, font=("Sans",13,"italic"), bg=BG_COLOR, fg=FG_COLOR).pack(pady=(0,30))

    def Nav(self, n, b=None, txt="SIGUIENTE ➔"):
        f = tk.Frame(self.main_content, bg=BG_COLOR); f.pack(side="bottom", pady=40, fill="x")
        if b: tk.Button(f, text="⬅ VOLVER", bg=BUTTON_COLOR, fg="white", command=b, padx=20, pady=10).pack(side="left", padx=40)
        tk.Button(f, text=txt, bg=ACCENT_COLOR, fg=BG_COLOR, font=("Sans",14,"bold"), command=n, padx=30, pady=10).pack(side="right", padx=40)

    # --- FLOW ---
    def step0(self):
        self.clean(); self.head("¡Bienvenido! AstroOrange V2", "Setup Premium")
        tk.Label(self.main_content, text="⚠️ RECOMENDADO: CABLE ETHERNET CONECTADO ⚠️", font=("Sans",14,"bold"), bg=BG_COLOR, fg="orange").pack(pady=40); self.Nav(self.step1)

    def step1(self):
        self.clean(); self.head("Paso 1: Tu Cuenta"); f = tk.Frame(self.main_content, bg=SECONDARY_BG, padx=30, pady=30); f.pack(pady=20)
        tk.Label(f, text="Usuario:", bg=SECONDARY_BG, fg="white").grid(row=0,column=0,pady=10); self.eu = tk.Entry(f, width=25); self.eu.grid(row=0,column=1); self.eu.insert(0,self.u)
        tk.Label(f, text="Pass:", bg=SECONDARY_BG, fg="white").grid(row=1,column=0); self.ep = tk.Entry(f, show="*", width=25); self.ep.grid(row=1,column=1)
        self.Nav(self.v1, self.step0)

    def v1(self):
        self.u, self.p = self.eu.get().strip(), self.ep.get().strip()
        if self.u and self.p: self.step2()
        else: messagebox.showerror("Error", "Faltan datos")

    def step2(self):
        self.clean(); self.head("Paso 2: WiFi"); self.lb = tk.Listbox(self.main_content, width=55, height=10, bg=SECONDARY_BG, fg="white"); self.lb.pack(pady=10)
        self.lb.bind('<Double-Button-1>', lambda e: self.v2()); tk.Button(self.main_content, text="🔄 ESCANEAR", command=self.scan).pack(); self.scan(); self.Nav(self.v2, self.step1)

    def scan(self):
        self.lb.delete(0, tk.END); self.ssids = []
        try:
            o = subprocess.check_output(["nmcli","-t","-f","SSID","dev","wifi","list"], universal_newlines=True)
            for l in o.splitlines():
                if l and l not in self.ssids: self.ssids.append(l); self.lb.insert(tk.END, f" 📶  {l}")
        except: self.lb.insert(tk.END, "Sin WiFi")

    def v2(self):
        idx = self.lb.curselection(); self.ssid = self.ssids[idx[0]] if idx else ""; self.step3()

    def step3(self):
        self.clean(); self.head("Paso 3: Red"); f = tk.Frame(self.main_content, bg=SECONDARY_BG, padx=30, pady=20); f.pack(pady=10)
        tk.Label(f, text="SSID:", bg=SECONDARY_BG, fg="white").grid(row=0,column=0); self.es = tk.Entry(f, width=30); self.es.grid(row=0,column=1); self.es.insert(0, self.ssid)
        tk.Label(f, text="Pass:", bg=SECONDARY_BG, fg="white").grid(row=1,column=0); pf = tk.Frame(f, bg=SECONDARY_BG); pf.grid(row=1,column=1)
        self.ewp = tk.Entry(pf, show="*", width=25); self.ewp.pack(side="left"); self.sv = tk.BooleanVar()
        tk.Checkbutton(pf, variable=self.sv, command=lambda: self.ewp.config(show="" if self.sv.get() else "*"), bg=SECONDARY_BG).pack()
        tk.Checkbutton(f, text="IP Estática", variable=self.st_var, bg=SECONDARY_BG, fg="yellow", command=self.t_st).grid(row=2, columnspan=2)
        self.sf = tk.Frame(f, bg=SECONDARY_BG); self.sf.grid(row=3, columnspan=2); self.eip = tk.Entry(self.sf, width=15); self.eip.pack(side="left"); self.eip.insert(0, self.ip)
        self.egw = tk.Entry(self.sf, width=15); self.egw.pack(side="left"); self.egw.insert(0, self.gw); self.Nav(self.finish_v1, self.step2, "REINICIAR")

    def t_st(self):
        s = "normal" if self.st_var.get() else "disabled"
        for c in self.sf.winfo_children(): c.config(state=s)

    def finish_v1(self):
        if messagebox.askyesno("Confirmar", "¿Aplicar y reiniciar?"):
            self.clean(); tk.Label(self.main_content, text="Reiniciando con tu nueva cuenta...", font=("Sans",20), bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=100); self.root.update()
            try:
                u, p = self.u, self.p
                subprocess.call(f"sudo useradd -m -s /bin/bash -G sudo,dialout,video,input,plugdev,netdev {u}", shell=True)
                subprocess.call(f"echo '{u}:{p}' | sudo chpasswd", shell=True)
                subprocess.call(f"echo '[Seat:*]\nautologin-user={u}\nautologin-session=xfce\n' | sudo tee /etc/lightdm/lightdm.conf.d/90-astro.conf", shell=True)
                if self.es.get():
                    subprocess.call(f"sudo nmcli con delete '{self.es.get()}' 2>/dev/null || true", shell=True)
                    cmd = f"sudo nmcli con add type wifi ifname '*' con-name '{self.es.get()}' ssid '{self.es.get()}' -- 802-11-wireless-security.key-mgmt wpa-psk 802-11-wireless-security.psk '{self.ewp.get()}'"
                    subprocess.call(cmd, shell=True); subprocess.Popen(f"sudo nmcli con up '{self.es.get()}'", shell=True)
                subprocess.call("sudo touch /etc/astro-configured", shell=True); subprocess.call("sudo reboot", shell=True)
            except Exception as e: self.head("Error", str(e))

    def stage2(self):
        self.clean(); self.head("Instalador Software", "Premium Experience")
        f = tk.Frame(self.main_content, bg=BG_COLOR); f.pack(pady=10)
        for i, (n, info) in enumerate(SOFTWARE.items()):
            inst = bool(shutil.which(info["bin"]) or os.path.exists(f"/usr/bin/{info['bin']}"))
            self.sw_vars[n] = tk.BooleanVar(value=inst or n in ["KStars / INDI", "PHD2 Guiding"])
            cb = tk.Checkbutton(f, text=n, variable=self.sw_vars[n], bg=BG_COLOR, fg="white" if not inst else SUCCESS_COLOR, selectcolor=SECONDARY_BG, font=("Sans",12)); cb.grid(row=i//2, column=i%2, sticky="w", padx=30, pady=8)
        tk.Button(self.main_content, text="🚀 INICIAR INSTALACIÓN", font=("Sans",15,"bold"), bg=ACCENT_COLOR, fg=BG_COLOR, width=30, command=self.start_install).pack(pady=30)

    def start_install(self):
        self.clean(); self.head("Procesando...", "No cierres esta ventana")
        
        c_frm = tk.Frame(self.main_content, bg=BG_COLOR); c_frm.pack(pady=10)
        self.carousel = ImageCarousel(c_frm)
        
        t_frm = tk.Frame(self.main_content, bg="black", bd=2, relief="sunken"); t_frm.pack(fill="both", expand=True, padx=40, pady=10)
        self.console = scrolledtext.ScrolledText(t_frm, bg="black", fg="#00ff00", font=("Monospace", 10), state="disabled")
        self.console.pack(fill="both", expand=True)
        
        threading.Thread(target=self.run_install, daemon=True).start()

    def log(self, t):
        self.console.config(state="normal"); self.console.insert(tk.END, t + "\n"); self.console.see(tk.END); self.console.config(state="disabled"); self.root.update_idletasks()

    def run_install(self):
        cmds = ["sudo apt-get update"]
        for n, info in SOFTWARE.items():
            if self.sw_vars[n].get():
                self.log(f"-> Preparando {n}...")
                if info.get("ppa"): cmds.append(f"sudo add-apt-repository -y {info['ppa']}")
                if info.get("url"): cmds.append(f"wget {info['url']} -O /tmp/sw.deb && sudo apt install -y /tmp/sw.deb")
                cmds.append(f"sudo apt-get install -y {info['pkg']}")
        
        f_cmd = " && ".join(cmds)
        proc = subprocess.Popen(f_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in proc.stdout: self.log(line.strip())
        proc.wait()
        
        self.log("\n✅ COMPLETADO. El sistema está configurado."); subprocess.call("sudo touch /etc/astro-finished", shell=True)
        tk.Button(self.main_content, text="SALIR ASISTENTE", command=self.root.destroy, bg=SUCCESS_COLOR, fg="white", font=("Sans",14,"bold")).pack(pady=20)

if __name__ == "__main__":
    root = tk.Tk(); app = WizardApp(root); root.mainloop()
