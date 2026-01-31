import tkinter as tk
from tkinter import messagebox
import subprocess, threading

# Estilo Premium AstroOrange
BG_COLOR, SECONDARY_BG, FG_COLOR = "#0f172a", "#1e293b", "#e2e8f0"
ACCENT_COLOR, SUCCESS_COLOR, DANGER_COLOR = "#38bdf8", "#22c55e", "#ef4444"
BUTTON_COLOR = "#334155"

class NetWizard:
    def __init__(self, root):
        self.root = root
        self.root.title("AstroOrange Network Manager")
        self.root.geometry("800x650")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)
        
        self.ssid = ""
        self.main_content = tk.Frame(self.root, bg=BG_COLOR)
        self.main_content.pack(expand=True, fill="both")
        self.step_list()

    def clean(self):
        for w in self.main_content.winfo_children(): w.destroy()

    def head(self, t, s=""):
        tk.Label(self.main_content, text="📡 " + t, font=("Sans", 32, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=(50, 5))
        if s: tk.Label(self.main_content, text=s, font=("Sans", 14), bg=BG_COLOR, fg=FG_COLOR).pack(pady=(0, 30))

    def btn(self, parent, text, cmd, color=BUTTON_COLOR, width=18):
        return tk.Button(parent, text=text, command=cmd, bg=color, fg="white", 
                         font=("Sans", 11, "bold"), relief="flat", padx=25, pady=12, 
                         activebackground=ACCENT_COLOR, cursor="hand2", width=width)

    def step_list(self):
        self.clean(); self.head("Configuración WiFi", "Busca y conéctate a una red cercana")
        
        f = tk.Frame(self.main_content, bg=BG_COLOR); f.pack(fill="x", padx=120)
        self.lb = tk.Listbox(f, width=40, height=8, bg=SECONDARY_BG, fg="white", font=("Sans", 12), 
                             bd=0, highlightthickness=1, highlightbackground=BUTTON_COLOR, 
                             selectbackground=ACCENT_COLOR, borderwidth=10, relief="flat")
        self.lb.pack(pady=10, fill="x")
        
        tk.Button(self.main_content, text="🔄 ACTUALIZAR LISTA", command=self.scan, bg=BUTTON_COLOR, fg="white", font=("Sans",10), relief="flat", padx=20, pady=8).pack(pady=10)
        
        nav = tk.Frame(self.main_content, bg=BG_COLOR); nav.pack(side="bottom", pady=50)
        self.btn(nav, "CERRAR", self.root.destroy, DANGER_COLOR, width=12).pack(side="left", padx=25)
        self.btn(nav, "SIGUIENTE", self.step_pass, ACCENT_COLOR, width=12).pack(side="left", padx=25)
        self.scan()

    def scan(self):
        self.lb.delete(0, tk.END); self.ssids = []
        try:
            # Forzar un escaneo nuevo para que no salga la lista vieja/vacía
            subprocess.run(["nmcli", "dev", "wifi", "rescan"], stderr=subprocess.DEVNULL)
            o = subprocess.check_output(["nmcli","-t","-f","SSID","dev","wifi","list"], universal_newlines=True)
            for l in o.splitlines():
                if l and l not in self.ssids: 
                    self.ssids.append(l); self.lb.insert(tk.END, f"  📶  {l}")
        except: self.lb.insert(tk.END, "No se detectaron redes WiFi")

    def step_pass(self):
        idx = self.lb.curselection()
        if not idx: messagebox.showwarning("WiFi", "Selecciona una red de la lista"); return
        self.ssid = self.ssids[idx[0]]
        
        self.clean(); self.head("Seguridad Red", f"Conectando a: {self.ssid}")
        f = tk.Frame(self.main_content, bg=SECONDARY_BG, padx=40, pady=30); f.pack(pady=10)
        
        # Password Field
        tk.Label(f, text="CONTRASEÑA WIFI", bg=SECONDARY_BG, fg=ACCENT_COLOR, font=("Sans", 10, "bold")).pack(anchor="w")
        self.ep = tk.Entry(f, show="*", width=35, font=("Sans", 14), bg=BG_COLOR, fg="white", bd=0, insertbackground="white", highlightthickness=1, highlightbackground=BUTTON_COLOR)
        self.ep.pack(pady=(5, 20), ipady=8)

        # Static IP Toggle
        self.static_ip_var = tk.BooleanVar(value=False)
        tk.Checkbutton(f, text="Configuración IP Manual (Avanzado)", variable=self.static_ip_var, command=self.toggle_ip,
                       bg=SECONDARY_BG, fg="white", selectcolor=BG_COLOR, font=("Sans", 10)).pack(anchor="w", pady=5)
        
        self.ip_frame = tk.Frame(f, bg=SECONDARY_BG)
        self.entries = {}
        for lbl in ["Dirección IP (ej: 192.168.1.50/24)", "Puerta de Enlace (ej: 192.168.1.1)", "DNS (ej: 8.8.8.8)"]:
            tk.Label(self.ip_frame, text=lbl, bg=SECONDARY_BG, fg=FG_COLOR, font=("Sans", 9)).pack(anchor="w")
            e = tk.Entry(self.ip_frame, width=35, bg=BG_COLOR, fg="white", bd=0, insertbackground="white"); e.pack(pady=(0, 10), ipady=5)
            self.entries[lbl] = e
        
        nav = tk.Frame(self.main_content, bg=BG_COLOR); nav.pack(side="bottom", pady=40)
        self.btn(nav, "VOLVER", self.step_list, BUTTON_COLOR, width=10).pack(side="left", padx=20)
        self.btn(nav, "CONECTAR", self.connect, ACCENT_COLOR, width=15).pack(side="left", padx=20)

    def toggle_ip(self):
        if self.static_ip_var.get(): 
            self.ip_frame.pack(fill="x", pady=10)
            self.root.geometry("800x800") # More height for static IP fields
        else: 
            self.ip_frame.pack_forget()
            self.root.geometry("800x650")

    def connect(self):
        pw = self.ep.get().strip()
        cmd = f"sudo nmcli dev wifi connect '{self.ssid}' password '{pw}'"
        
        # Static IP Logic
        if self.static_ip_var.get():
            ip = self.entries["Dirección IP (ej: 192.168.1.50/24)"].get().strip()
            gw = self.entries["Puerta de Enlace (ej: 192.168.1.1)"].get().strip()
            dns = self.entries["DNS (ej: 8.8.8.8)"].get().strip()
            if not ip or not gw: messagebox.showwarning("Error IP", "IP y Puerta de Enlace obligatorias"); return
            cmd += f" ipv4.method manual ipv4.addresses {ip} ipv4.gateway {gw} ipv4.dns {dns}"

        self.clean(); self.head("Conectando...", f"Estableciendo enlace con {self.ssid}")
        tk.Label(self.main_content, text="Deteniendo Hotspot y aplicando cambios...\n(Esto puede tardar hasta 45s)", bg=BG_COLOR, fg=FG_COLOR, font=("Sans", 11)).pack(pady=30); self.root.update()
        
        def run():
            import time
            # 1. CRITICAL: Stop Hotspot/Network-Script to prevent conflicts/loops
            subprocess.run("sudo systemctl stop astro-network.service", shell=True)
            subprocess.run("sudo nmcli con down AstroOrange-Setup 2>/dev/null", shell=True)
            
            # SAFETY DELAY: Wait 5s for WiFi chip to reset/clean buffer and avoid Router Freeze
            time.sleep(5)
            
            # 2. Connect
            res = subprocess.run(cmd, shell=True, capture_output=True, timeout=60)
            if res.returncode == 0:
                self.root.after(0, lambda: messagebox.showinfo("Éxito", f"Conectado a {self.ssid}"))
                self.root.after(0, self.root.destroy)
            else:
                err_msg = res.stderr.decode().strip() or "Error desconocido"
                self.root.after(0, lambda: messagebox.showerror("Error Conexión", f"Fallo al conectar:\n{err_msg}"))
                self.root.after(0, self.step_list)

        threading.Thread(target=run, daemon=True).start()

    def center_window(self):
        self.root.update_idletasks()
        w, h = self.root.winfo_width(), self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"+{x}+{y}")

if __name__ == "__main__":
    root = tk.Tk()
    app = NetWizard(root)
    app.center_window()
    
    # Robust Icon Loading
    icon_paths = [
        "/usr/share/icons/Papirus/32x32/apps/network-wireless-hotspot.png",
        "/usr/share/icons/hicolor/48x48/apps/nm-device-wireless.png",
        "/usr/share/pixmaps/nm-signal-100.png"
    ]
    for p in icon_paths:
        if os.path.exists(p):
            try:
                img = tk.PhotoImage(file=p)
                root.iconphoto(False, img)
                break
            except: pass
            
    root.mainloop()
