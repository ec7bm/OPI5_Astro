import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
import os
import threading
import socket
import shutil
from glob import glob

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = ImageTk = None

# --- DESIGN SYSTEM ---
BG_COLOR = "#0f172a"
SECONDARY_BG = "#1e293b"
FG_COLOR = "#e2e8f0"
ACCENT_COLOR = "#38bdf8"
SUCCESS_COLOR = "#22c55e"
BUTTON_COLOR = "#334155"
BUTTON_HOVER = "#475569"

# --- CONFIGURATION ---
SOFTWARE_LIST = {
    "KStars / INDI": {"bin": "kstars", "pkg": "kstars-bleeding indi-full gsc", "ppa": "ppa:mutlaqja/ppa"},
    "PHD2 Guiding": {"bin": "phd2", "pkg": "phd2", "ppa": "ppa:pch/phd2"},
    "ASTAP (Plate Solver)": {"bin": "astap", "pkg": "astap", "url": "https://www.hnsky.org/astap_arm64.deb"},
    "Stellarium": {"bin": "stellarium", "pkg": "stellarium", "ppa": None},
    "AstroDMX Capture": {"bin": "astrodmx", "pkg": "astrodmxcapture", "deb": True},
    "CCDciel": {"bin": "ccdciel", "pkg": "ccdciel", "deb": True},
    "Syncthing": {"bin": "syncthing", "pkg": "syncthing", "ppa": None}
}

def get_network_defaults():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        parts = ip.split(".")
        if len(parts) == 4:
            base = ".".join(parts[:3])
            return f"{base}.100", f"{base}.1", "8.8.8.8"
    except: pass
    return "192.168.1.100", "192.168.1.1", "8.8.8.8"

class ImageCarousel:
    def __init__(self, parent, size=(800, 450)):
        self.parent = parent
        self.images = []
        self.idx = 0
        self.size = size
        
        path = "/usr/share/backgrounds/gallery"
        if not os.path.exists(path):
            path = "/opt/astroorange/assets/gallery"
            
        if Image and os.path.exists(path):
            files = sorted(glob(os.path.join(path, "*.png")))
            for f in files:
                try:
                    img = Image.open(f).resize(self.size, Image.Resampling.LANCZOS)
                    self.images.append(ImageTk.PhotoImage(img))
                except: continue
        
        if self.images:
            self.label = tk.Label(parent, bg=BG_COLOR, bd=2, relief="flat")
            self.label.pack(pady=20)
            self.animate()
        else:
            tk.Label(parent, text="(Cargando vistas del cosmos...)", fg="grey", bg=BG_COLOR).pack(pady=50)

    def animate(self):
        if self.images and self.parent.winfo_exists():
            self.label.config(image=self.images[self.idx])
            self.idx = (self.idx + 1) % len(self.images)
            self.label.after(5000, self.animate)

class WizardApp:
    def __init__(self, root):
        self.root = root
        self.u, self.p = "astro", ""
        self.ssid, self.wp = "", ""
        self.ip, self.gw, self.dns = get_network_defaults()
        self.st_var = tk.BooleanVar(value=False)
        self.software_vars = {}
        
        # Check autostart logic
        if "--autostart" in os.sys.argv and os.path.exists("/etc/astro-finished"):
            root.destroy(); return

        self.setup_ui()
        self.create_desktop_launcher()
        
        if not os.path.exists("/etc/astro-configured"):
            self.show_welcome()
        else:
            self.show_software_installer()

    def setup_ui(self):
        self.root.title("AstroOrange V2 - Wizard")
        self.root.geometry("900x750")
        self.root.configure(bg=BG_COLOR)
        
        # Background management
        self.bg_canvas = tk.Label(self.root)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.load_wallpaper()

    def load_wallpaper(self):
        f = "/usr/share/backgrounds/astro-wallpaper.png"
        if not os.path.exists(f): f = "/opt/astroorange/assets/astro-wallpaper.png"
        if Image and os.path.exists(f):
            try:
                img = Image.open(f).resize((900, 750), Image.Resampling.LANCZOS)
                self.wallpaper = ImageTk.PhotoImage(img)
                self.bg_canvas.config(image=self.wallpaper)
            except: self.bg_canvas.config(bg=BG_COLOR)
        else: self.bg_canvas.config(bg=BG_COLOR)

    def clear(self):
        for w in self.root.winfo_children():
            if w != self.bg_canvas: w.destroy()

    def header(self, title, subtitle=""):
        tk.Label(self.root, text=title, font=("Sans", 28, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=(50, 5))
        if subtitle:
            tk.Label(self.root, text=subtitle, font=("Sans", 13, "italic"), bg=BG_COLOR, fg=FG_COLOR).pack(pady=(0, 30))

    def nav_buttons(self, next_cmd, back_cmd=None, next_txt="SIGUIENTE ➔"):
        f = tk.Frame(self.root, bg=BG_COLOR)
        f.pack(side="bottom", pady=50, fill="x")
        
        if back_cmd:
            b = tk.Button(f, text="⬅ VOLVER", font=("Sans", 12, "bold"), bg=BUTTON_COLOR, fg="white", 
                          activebackground=BUTTON_HOVER, activeforeground="white", relief="flat", 
                          padx=20, pady=10, command=back_cmd)
            b.pack(side="left", padx=50)
        
        n = tk.Button(f, text=next_txt, font=("Sans", 14, "bold"), bg=ACCENT_COLOR, fg=BG_COLOR, 
                      activebackground=FG_COLOR, relief="flat", padx=35, pady=12, command=next_cmd)
        n.pack(side="right", padx=50)

    def create_desktop_launcher(self):
        try:
            d = os.path.expanduser("~/Desktop")
            os.makedirs(d, exist_ok=True)
            s = "/usr/share/applications/astro-wizard.desktop"
            dst = os.path.join(d, "astro-wizard.desktop")
            if os.path.exists(s) and not os.path.exists(dst):
                shutil.copy(s, dst)
                subprocess.call(f"gio set {dst} metadata::trusted true", shell=True)
                os.chmod(dst, 0o755)
        except: pass

    # --- STEPS ---
    def show_welcome(self):
        self.clear()
        self.header("¡Bienvenido a AstroOrange V2!", "Tu portal al cielo profundo")
        info = "Para garantizar el éxito de la instalación:\n\n1. Conecta el cable ETHERNET si es posible.\n2. No apagues la placa durante el proceso.\n3. Prepárate para descubrir el cosmos."
        tk.Label(self.root, text=info, font=("Sans", 14), bg=BG_COLOR, fg="white", justify="center").pack(pady=40)
        self.nav_buttons(self.show_account)

    def show_account(self):
        self.clear()
        self.header("Paso 1: Tu Cuenta", "Define tu identidad en el sistema")
        f = tk.Frame(self.root, bg=SECONDARY_BG, padx=30, pady=30, rounded=True if hasattr(tk, "rounded") else False)
        f.pack(pady=20)
        
        tk.Label(f, text="Nombre de Usuario:", font=("Sans", 12), bg=SECONDARY_BG, fg=FG_COLOR).grid(row=0, column=0, sticky="e", pady=10)
        self.eu = tk.Entry(f, font=("Sans", 12), width=25, bg=BG_COLOR, fg="white", insertbackground="white")
        self.eu.grid(row=0, column=1, padx=10); self.eu.insert(0, self.u)
        
        tk.Label(f, text="Nueva Contraseña:", font=("Sans", 12), bg=SECONDARY_BG, fg=FG_COLOR).grid(row=1, column=0, sticky="e", pady=10)
        self.ep = tk.Entry(f, font=("Sans", 12), width=25, show="*", bg=BG_COLOR, fg="white", insertbackground="white")
        self.ep.grid(row=1, column=1, padx=10); self.ep.insert(0, self.p)
        
        self.Nav(self.val_account, self.show_welcome)

    def val_account(self):
        self.u, self.p = self.eu.get().strip(), self.ep.get().strip()
        if self.u and self.p: self.show_wifi_scan()
        else: messagebox.showerror("Error", "Debes indicar usuario y contraseña.")

    def show_wifi_scan(self):
        self.clear()
        self.header("Paso 2: Conexión WiFi", "Selecciona tu red de confianza")
        
        main_f = tk.Frame(self.root, bg=BG_COLOR)
        main_f.pack(fill="both", expand=True, padx=100)
        
        self.lb = tk.Listbox(main_f, font=("Sans", 12), bg=SECONDARY_BG, fg="white", 
                             selectbackground=ACCENT_COLOR, borderwidth=0, highlightthickness=1)
        self.lb.pack(fill="both", expand=True, pady=10)
        self.lb.bind('<Double-Button-1>', lambda e: self.val_wifi_selection())
        
        btn_f = tk.Frame(main_f, bg=BG_COLOR)
        btn_f.pack(fill="x")
        tk.Button(btn_f, text="🔄 REESCANEAR", bg=BUTTON_COLOR, fg="white", relief="flat", command=self.do_scan).pack(side="left", padx=5)
        tk.Button(btn_f, text="🔧 CONFIG MANUAL", bg=BUTTON_COLOR, fg="yellow", relief="flat", command=lambda: self.show_net_config(True)).pack(side="left", padx=5)
        
        self.do_scan()
        self.Nav(self.val_wifi_selection, self.show_account)

    def do_scan(self):
        self.lb.delete(0, tk.END); self.ssids = []
        try:
            o = subprocess.check_output(["nmcli", "-t", "-f", "SSID", "dev", "wifi", "list"], universal_newlines=True)
            for s in o.splitlines():
                if s.strip() and s not in self.ssids:
                    self.ssids.append(s); self.lb.insert(tk.END, f" 📶  {s}")
        except: self.lb.insert(tk.END, "No se detectó WiFi")

    def val_wifi_selection(self):
        idx = self.lb.curselection()
        if idx: self.ssid = self.ssids[idx[0]]; self.show_net_config()
        elif messagebox.askyesno("Confirmar", "¿Continuar solo con Ethernet?"): self.ssid = ""; self.show_net_config()

    def show_net_config(self, manual=False):
        self.clear()
        self.header("Paso 3: Detalles de Red", "Configura el acceso a internet")
        f = tk.Frame(self.root, bg=SECONDARY_BG, padx=30, pady=20)
        f.pack(pady=10)
        
        tk.Label(f, text="SSID WiFi:", font=("Sans", 11), bg=SECONDARY_BG, fg=FG_COLOR).grid(row=0, column=0, sticky="e", pady=5)
        self.es = tk.Entry(f, font=("Sans", 12), width=30, bg=BG_COLOR, fg="white"); self.es.grid(row=0, column=1, padx=10)
        self.es.insert(0, self.ssid)
        
        tk.Label(f, text="Contraseña WiFi:", font=("Sans", 11), bg=SECONDARY_BG, fg=FG_COLOR).grid(row=1, column=0, sticky="e", pady=5)
        pf = tk.Frame(f, bg=SECONDARY_BG); pf.grid(row=1, column=1, sticky="w", padx=10)
        self.ewp = tk.Entry(pf, font=("Sans", 12), show="*", width=25, bg=BG_COLOR, fg="white"); self.ewp.pack(side="left")
        self.sv = tk.BooleanVar()
        tk.Checkbutton(pf, variable=self.sv, bg=SECONDARY_BG, selectcolor=BG_COLOR, command=lambda: self.ewp.config(show="" if self.sv.get() else "*")).pack(side="left")
        
        tk.Checkbutton(f, text="Configuración IP Estática (Avanzado)", variable=self.st_var, font=("Sans", 10, "bold"), 
                       bg=SECONDARY_BG, fg="yellow", selectcolor=BG_COLOR, command=self.t_st).grid(row=2, columnspan=2, pady=15)
        
        self.sf = tk.Frame(f, bg=SECONDARY_BG); self.sf.grid(row=3, columnspan=2)
        tk.Label(self.sf, text="IP:", bg=SECONDARY_BG, fg=FG_COLOR).pack(side="left"); self.eip = tk.Entry(self.sf, width=15); self.eip.pack(side="left", padx=5); self.eip.insert(0, self.ip)
        tk.Label(self.sf, text="Puerta:", bg=SECONDARY_BG, fg=FG_COLOR).pack(side="left"); self.egw = tk.Entry(self.sf, width=15); self.egw.pack(side="left", padx=5); self.egw.insert(0, self.gateway)
        
        self.t_st()
        self.Nav(self.apply_base_config, self.show_wifi_scan, "FINALIZAR CUENTA")

    def t_st(self):
        st = "normal" if self.st_var.get() else "disabled"
        for c in self.sf.winfo_children(): c.config(state=st)

    def apply_base_config(self):
        # Store latest data
        self.u, self.p = self.eu.get().strip(), self.ep.get().strip()
        self.ssid, self.wp = self.es.get().strip(), self.ewp.get().strip()
        
        if messagebox.askyesno("Confirmar", "¿Aplicar cambios y reiniciar?\nSe creará el usuario y se configurará la red."):
            self.clear()
            tk.Label(self.root, text="Aplicando configuración del sistema...\nLa placa se reiniciará automáticamente.", 
                     font=("Sans", 16, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=100)
            self.root.update()
            try:
                # 1. User
                subprocess.call(f"sudo useradd -m -s /bin/bash -G sudo,dialout,video,input,plugdev,netdev {self.u}", shell=True)
                subprocess.call(f"echo '{self.u}:{self.p}' | sudo chpasswd", shell=True)
                # 2. Autologin
                subprocess.call(f"echo '[Seat:*]\nautologin-user={self.u}\nautologin-session=xfce\n' | sudo tee /etc/lightdm/lightdm.conf.d/90-astro.conf", shell=True)
                # 3. WiFi
                if self.ssid:
                    subprocess.call(f"sudo nmcli con delete '{self.ssid}' 2>/dev/null || true", shell=True)
                    cmd = f"sudo nmcli con add type wifi ifname '*' con-name '{self.ssid}' ssid '{self.ssid}' -- 802-11-wireless-security.key-mgmt wpa-psk 802-11-wireless-security.psk '{self.wp}'"
                    if self.st_var.get(): cmd += f" ipv4.method manual ipv4.addresses '{self.eip.get()}/24' ipv4.gateway '{self.egw.get()}' ipv4.dns '8.8.8.8'"
                    else: cmd += " ipv4.method auto"
                    subprocess.call(cmd, shell=True); subprocess.Popen(f"sudo nmcli con up '{self.ssid}'", shell=True)
                # 4. Finish first stage
                subprocess.call("sudo touch /etc/astro-configured", shell=True)
                subprocess.call("sudo reboot", shell=True)
            except Exception as e: messagebox.showerror("Error Critico", str(e))

    # --- STAGE 2: SOFTWARE ---
    def show_software_installer(self):
        self.clear()
        self.header("Instalador de Software", "Personaliza tu equipo astronómico")
        
        f = tk.Frame(self.root, bg=BG_COLOR); f.pack(pady=10)
        
        # Mapping apps to binaries for detection
        row = 0
        for name, info in SOFTWARE_LIST.items():
            installed = self.is_installed(info["bin"])
            v = tk.BooleanVar(value=installed or name in ["KStars / INDI", "PHD2 Guiding", "ASTAP (Plate Solver)"])
            self.software_vars[name] = v
            
            cb = tk.Checkbutton(f, text=name, variable=v, bg=BG_COLOR, font=("Sans", 11), 
                               fg="white" if not installed else SUCCESS_COLOR, selectcolor=SECONDARY_BG, 
                               activebackground=BG_COLOR, activeforeground=ACCENT_COLOR)
            cb.grid(row=row//2, column=row%2, sticky="w", padx=30, pady=8)
            
            if installed:
                tk.Label(f, text="(INSTALADO)", font=("Sans", 8, "bold"), bg=BG_COLOR, fg=SUCCESS_COLOR).grid(row=row//2, column=row%2, sticky="e", padx=(0, 30))
            row += 1

        tk.Button(self.root, text="🚀 INICIAR INSTALACIÓN", font=("Sans", 14, "bold"), bg=ACCENT_COLOR, fg=BG_COLOR, 
                  activebackground=FG_COLOR, relief="flat", width=30, command=self.start_install_process).pack(pady=30)

    def is_installed(self, bin_name):
        return shutil.which(bin_name) or any(os.path.exists(os.path.join(p, bin_name)) for p in ["/usr/bin", "/usr/local/bin", "/opt/astroorange/bin"])

    def start_install_process(self):
        win = tk.Toplevel(self.root); win.title("Proceso de Instalación"); win.geometry("900x750"); win.configure(bg=BG_COLOR)
        tk.Label(win, text="🚀 Instalando... por favor espera", font=("Sans", 20, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=20)
        self.carousel = ImageCarousel(win)
        threading.Thread(target=self.run_apt_task, args=(win,)).start()

    def run_apt_task(self, win):
        cmds = ["sudo apt-get update"]
        for name, info in SOFTWARE_LIST.items():
            if self.software_vars[name].get() and not self.is_installed(info["bin"]):
                if info.get("ppa"): cmds.append(f"sudo add-apt-repository -y {info['ppa']}")
                if info.get("url"): cmds.append(f"wget {info['url']} -O /tmp/pkg.deb && sudo apt-get install -y /tmp/pkg.deb")
                elif info.get("deb"): cmds.append(f"echo '⚠️ {name} requiere instalador manual o repo externo'")
                else: cmds.append(f"sudo apt-get install -y {info['pkg']}")
        
        full_cmd = " && ".join(cmds)
        subprocess.call(["xfce4-terminal", "--title=AstroOrange Installer", "-e", f"bash -c '{full_cmd}; echo \"✅ INSTALACIÓN FINALIZADA. Pulsa ENTER para terminar.\"; read'"])
        subprocess.call("sudo touch /etc/astro-finished", shell=True)
        win.destroy(); self.root.destroy()
        messagebox.showinfo("Finalizado", "Tus aplicaciones están listas en el Menú de Inicio.")

if __name__ == "__main__":
    root = tk.Tk(); app = WizardApp(root); root.mainloop()
