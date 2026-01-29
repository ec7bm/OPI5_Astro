import tkinter as tk
from tkinter import messagebox, ttk
import subprocess, os, threading, socket, shutil
from glob import glob
try: from PIL import Image, ImageTk
except: Image = ImageTk = None

BG_COLOR, SECONDARY_BG, FG_COLOR, ACCENT_COLOR, SUCCESS_COLOR = "#0f172a", "#1e293b", "#e2e8f0", "#38bdf8", "#22c55e"
BUTTON_COLOR = "#334155"

# Apps a incluir
SOFTWARE = {
    "KStars / INDI": {"bin": "kstars", "pkg": "kstars-bleeding indi-full gsc", "ppa": "ppa:mutlaqja/ppa"},
    "PHD2 Guiding": {"bin": "phd2", "pkg": "phd2", "ppa": "ppa:pch/phd2"},
    "ASTAP (Plate Solver)": {"bin": "astap", "pkg": "astap", "url": "https://www.hnsky.org/astap_arm64.deb"},
    "Stellarium": {"bin": "stellarium", "pkg": "stellarium"},
    "AstroDMX Capture": {"bin": "astrodmx", "pkg": "astrodmxcapture", "deb_url": "https://www.astrodmx.com/download/astrodmxcapture-release.deb"},
    "CCDciel": {"bin": "ccdciel", "pkg": "ccdciel", "ppa": "ppa:jandecaluwe/ccdciel"}, # Note: CCDciel often uses kstars/indi ppa too
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
        path = "/usr/share/backgrounds/gallery"
        if not os.path.exists(path): path = "/opt/astroorange/assets/gallery"
        if Image and os.path.exists(path):
            for f in sorted(glob(os.path.join(path, "*.png"))):
                try: self.imgs.append(ImageTk.PhotoImage(Image.open(f).resize((800,450))))
                except: continue
        if self.imgs: self.lbl = tk.Label(parent, bg=BG_COLOR); self.lbl.pack(pady=20); self.anim()
    def anim(self):
        if self.imgs and self.p.winfo_exists():
            self.lbl.config(image=self.imgs[self.idx]); self.idx = (self.idx+1)%len(self.imgs)
            self.lbl.after(5000, self.anim)

class WizardApp:
    def __init__(self, root):
        self.root = root
        self.u, self.p, self.ssid, self.wp = "astro", "", "", ""
        self.ip, self.gw, self.dns = get_net()
        self.st_var = tk.BooleanVar()
        if "--autostart" in os.sys.argv and os.path.exists("/etc/astro-finished"): root.destroy(); return
        self.setup(); self.shortcut()
        if not os.path.exists("/etc/astro-configured"): self.step0()
        else: self.stage2()

    def setup(self):
        self.root.title("AstroOrange V2"); self.root.geometry("900x750"); self.root.configure(bg=BG_COLOR)
        self.bg = tk.Label(self.root); self.bg.place(x=0,y=0,relwidth=1,relheight=1); self.up_bg()
    def up_bg(self):
        f = "/usr/share/backgrounds/astro-wallpaper.png"
        if not os.path.exists(f): f = "/opt/astroorange/assets/astro-wallpaper.png"
        if Image and os.path.exists(f): 
            try:
                self.bgh = ImageTk.PhotoImage(Image.open(f).resize((900,750)))
                self.bg.config(image=self.bgh)
            except: self.bg.config(bg=BG_COLOR)
        else: self.bg.config(bg=BG_COLOR)
    def clean(self):
        for w in self.root.winfo_children():
            if w != self.bg: w.destroy()
    def head(self, t, s=""):
        tk.Label(self.root, text=t, font=("Sans",28,"bold"), bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=(50,5))
        if s: tk.Label(self.root, text=s, font=("Sans",13,"italic"), bg=BG_COLOR, fg=FG_COLOR).pack(pady=(0,30))
    def shortcut(self):
        d = os.path.expanduser("~/Desktop"); os.makedirs(d, exist_ok=True)
        s, dst = "/usr/share/applications/astro-wizard.desktop", os.path.join(d, "astro-wizard.desktop")
        if os.path.exists(s) and not os.path.exists(dst): 
            shutil.copy(s, dst); subprocess.call(f"gio set {dst} metadata::trusted true", shell=True); os.chmod(dst, 0o755)
    def Nav(self, n, b=None, txt="SIGUIENTE ➔"):
        f = tk.Frame(self.root, bg=BG_COLOR); f.pack(side="bottom", pady=40, fill="x")
        if b: tk.Button(f, text="⬅ VOLVER", bg=BUTTON_COLOR, fg="white", command=b, padx=20, pady=10).pack(side="left", padx=40)
        tk.Button(f, text=txt, bg=ACCENT_COLOR, fg=BG_COLOR, font=("Sans",14,"bold"), command=n, padx=30, pady=10).pack(side="right", padx=40)

    def step0(self):
        self.clean(); self.head("¡Bienvenido! AstroOrange V2", "Configuración Premium")
        info = ("Para una instalación exitosa de todos los programas:\n\n"
                "⚠️ MANTÉN EL CABLE ETHERNET CONECTADO ⚠️\n\n"
                "La descarga de software astronómico puede ser pesada y\n"
                "requiere una conexión estable para evitar errores.")
        tk.Label(self.root, text=info, font=("Sans",14), bg=BG_COLOR, fg="white", justify="center").pack(pady=40); self.Nav(self.step1)
    def step1(self):
        self.clean(); self.head("Paso 1: Tu Cuenta"); f = tk.Frame(self.root, bg=SECONDARY_BG, padx=30, pady=30); f.pack(pady=20)
        tk.Label(f, text="Usuario:", bg=SECONDARY_BG, fg="white").grid(row=0,column=0,pady=10); self.eu = tk.Entry(f, width=25, font=("Sans",12)); self.eu.grid(row=0,column=1); self.eu.insert(0,self.u)
        tk.Label(f, text="Contraseña:", bg=SECONDARY_BG, fg="white").grid(row=1,column=0); self.ep = tk.Entry(f, show="*", width=25, font=("Sans",12)); self.ep.grid(row=1,column=1)
        self.Nav(self.v1, self.step0)
    def v1(self):
        self.u, self.p = self.eu.get().strip(), self.ep.get().strip()
        if self.u and self.p: self.step2()
        else: messagebox.showerror("Error", "Debes indicar usuario y contraseña.")
    def step2(self):
        self.clean(); self.head("Paso 2: WiFi"); self.lb = tk.Listbox(self.root, width=55, height=10, bg=SECONDARY_BG, fg="white", font=("Sans",12), selectbackground=ACCENT_COLOR); self.lb.pack(pady=10)
        self.lb.bind('<Double-Button-1>', lambda e: self.v2()); tk.Button(self.root, text="🔄 ESCANEAR", command=self.scan, bg=BUTTON_COLOR, fg="white").pack(); self.scan(); self.Nav(self.v2, self.step1)
    def scan(self):
        self.lb.delete(0, tk.END); self.ssids = []
        try:
            o = subprocess.check_output(["nmcli","-t","-f","SSID","dev","wifi","list"], universal_newlines=True)
            for l in o.splitlines():
                if l and l not in self.ssids: self.ssids.append(l); self.lb.insert(tk.END, f" 📶  {l}")
        except: self.lb.insert(tk.END, "Sin WiFi disponible")
    def v2(self):
        idx = self.lb.curselection()
        if idx: self.ssid = self.ssids[idx[0]]; self.step3()
        elif messagebox.askyesno("WiFi", "¿Seguir solo con Ethernet?"): self.ssid = ""; self.step3()
    def step3(self):
        self.clean(); self.head("Paso 3: Red"); f = tk.Frame(self.root, bg=SECONDARY_BG, padx=30, pady=20); f.pack(pady=10)
        tk.Label(f, text="SSID:", bg=SECONDARY_BG, fg="white").grid(row=0,column=0, sticky="e"); self.es = tk.Entry(f, width=30); self.es.grid(row=0,column=1, padx=10); self.es.insert(0, self.ssid)
        tk.Label(f, text="WiFi Pass:", bg=SECONDARY_BG, fg="white").grid(row=1,column=0, sticky="e"); pf = tk.Frame(f, bg=SECONDARY_BG); pf.grid(row=1,column=1, sticky="w", padx=10)
        self.ewp = tk.Entry(pf, show="*", width=25); self.ewp.pack(side="left"); self.sv = tk.BooleanVar()
        tk.Checkbutton(pf, variable=self.sv, command=lambda: self.ewp.config(show="" if self.sv.get() else "*"), bg=SECONDARY_BG, selectcolor=BG_COLOR).pack()
        tk.Checkbutton(f, text="Configuración IP Estática", variable=self.st_var, bg=SECONDARY_BG, fg="yellow", selectcolor=BG_COLOR, command=self.t_st).grid(row=2, columnspan=2, pady=10)
        self.sf = tk.Frame(f, bg=SECONDARY_BG); self.sf.grid(row=3, columnspan=2)
        tk.Label(self.sf, text="IP:", bg=SECONDARY_BG, fg=FG_COLOR).pack(side="left"); self.eip = tk.Entry(self.sf, width=15); self.eip.pack(side="left", padx=5); self.eip.insert(0, self.ip)
        tk.Label(self.sf, text="GW:", bg=SECONDARY_BG, fg=FG_COLOR).pack(side="left"); self.egw = tk.Entry(self.sf, width=15); self.egw.pack(side="left", padx=5); self.egw.insert(0, self.gw); self.t_st()
        self.Nav(self.v3, self.step2, "FINALIZAR CUENTA")
    def t_st(self):
        s = "normal" if self.st_var.get() else "disabled"
        for c in self.sf.winfo_children(): c.config(state=s)
    def v3(self):
        self.ssid, self.wp = self.es.get().strip(), self.ewp.get().strip()
        if messagebox.askyesno("Confirmar", "¿Aplicar cambios y reiniciar?"):
            self.clean(); tk.Label(self.root, text="Aplicando cambios en el sistema...\nLa placa se reiniciará sola.", font=("Sans",18), bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=100); self.root.update()
            try:
                subprocess.call(f"sudo useradd -m -s /bin/bash -G sudo,dialout,video,input,plugdev,netdev {self.u}", shell=True)
                subprocess.call(f"echo '{self.u}:{self.p}' | sudo chpasswd", shell=True)
                subprocess.call(f"echo '[Seat:*]\nautologin-user={self.u}\nautologin-session=xfce\n' | sudo tee /etc/lightdm/lightdm.conf.d/90-astro.conf", shell=True)
                if self.ssid:
                    subprocess.call(f"sudo nmcli con delete '{self.ssid}' 2>/dev/null || true", shell=True)
                    cmd = f"sudo nmcli con add type wifi ifname '*' con-name '{self.ssid}' ssid '{self.ssid}' -- 802-11-wireless-security.key-mgmt wpa-psk 802-11-wireless-security.psk '{self.wp}'"
                    if self.st_var.get(): cmd += f" ipv4.method manual ipv4.addresses '{self.eip.get()}/24' ipv4.gateway '{self.egw.get()}' ipv4.dns '8.8.8.8'"
                    else: cmd += " ipv4.method auto"
                    subprocess.call(cmd, shell=True); subprocess.Popen(f"sudo nmcli con up '{self.ssid}'", shell=True)
                subprocess.call("sudo touch /etc/astro-configured", shell=True); subprocess.call("sudo reboot", shell=True)
            except Exception as e: messagebox.showerror("Error", str(e))

    def stage2(self):
        self.clean(); self.head("Instalador de Software", "Detección inteligente de programas")
        tk.Label(self.root, text="🚨 Mantén el cable de red conectado para la descarga masiva 🚨", bg=BG_COLOR, fg="orange", font=("Sans", 10, "bold")).pack()
        f = tk.Frame(self.root, bg=BG_COLOR); f.pack(pady=10)
        self.vars = {}
        for i, (n, info) in enumerate(SOFTWARE.items()):
            inst = shutil.which(info["bin"]) or os.path.exists(f"/usr/bin/{info['bin']}")
            self.vars[n] = tk.BooleanVar(value=inst or n in ["KStars / INDI", "PHD2 Guiding"])
            cb = tk.Checkbutton(f, text=n, variable=self.vars[n], bg=BG_COLOR, fg="white" if not inst else SUCCESS_COLOR, selectcolor=SECONDARY_BG, font=("Sans",11), activebackground=BG_COLOR, activeforeground=ACCENT_COLOR)
            cb.grid(row=i//2, column=i%2, sticky="w", padx=30, pady=8)
            if inst: tk.Label(f, text="(INSTALADO)", font=("Sans",8,"bold"), bg=BG_COLOR, fg=SUCCESS_COLOR).grid(row=i//2, column=i%2, sticky="e")
        tk.Button(self.root, text="🚀 INICIAR INSTALACIÓN", font=("Sans",14,"bold"), bg=ACCENT_COLOR, fg=BG_COLOR, width=30, command=self.start, relief="flat").pack(pady=30)
    def start(self):
        win = tk.Toplevel(self.root); win.geometry("900x750"); win.configure(bg=BG_COLOR); win.title("AstroOrange V2 - Instalando")
        tk.Label(win, text="🚀 Instalando aplicaciones seleccionadas...", font=("Sans",20,"bold"), bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=20); self.car = ImageCarousel(win)
        threading.Thread(target=self.run, args=(win,)).start()
    def run(self, win):
        cmds = ["sudo apt-get update"]
        for n, info in SOFTWARE.items():
            if self.vars[n].get():
                if info.get("ppa"): cmds.append(f"sudo add-apt-repository -y {info['ppa']} && sudo apt-get update")
                if info.get("deb_url"): cmds.append(f"wget {info['deb_url']} -O /tmp/sw.deb && sudo apt-get install -y /tmp/sw.deb")
                elif info.get("url"): cmds.append(f"wget {info['url']} -O /tmp/sw.deb && sudo apt-get install -y /tmp/sw.deb")
                cmds.append(f"sudo apt-get install -y {info['pkg']}")
        f = " && ".join(cmds); subprocess.call(["xfce4-terminal", "-e", f"bash -c '{f}; echo \"✅ INSTALACIÓN COMPLETADA. Pulsa ENTER para cerrar.\"; read'"])
        subprocess.call("sudo touch /etc/astro-finished", shell=True); win.destroy(); self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk(); app = WizardApp(root); root.mainloop()
