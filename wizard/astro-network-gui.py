import tkinter as tk
from tkinter import messagebox
import subprocess, threading, os

BG_COLOR, SECONDARY_BG, FG_COLOR = "#0f172a", "#1e293b", "#e2e8f0"
ACCENT_COLOR, SUCCESS_COLOR, DANGER_COLOR = "#38bdf8", "#22c55e", "#ef4444"
BUTTON_COLOR = "#334155"

class NetWizard:
    def __init__(self, root):
        self.root = root
        self.root.title("AstroOrange Network Manager (V6.2)")
        self.root.geometry("800x800")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(True, True)
        self.ssid = ""
        self.main_content = tk.Frame(self.root, bg=BG_COLOR)
        self.main_content.pack(expand=True, fill="both")
        self.step_list()

    def clean(self):
        for w in self.main_content.winfo_children(): w.destroy()

    def head(self, t, s=""):
        try:
            icon_path = "/usr/share/icons/Papirus/32x32/apps/network-wireless-hotspot.png"
            if os.path.exists(icon_path):
                img = tk.PhotoImage(file=icon_path)
                l = tk.Label(self.main_content, image=img, bg=BG_COLOR)
                l.image = img
                l.pack(pady=(20, 0))
            else:
                tk.Label(self.main_content, text="📡", font=("Sans", 48), bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=(20, 0))
        except: 
            tk.Label(self.main_content, text="📡", font=("Sans", 48), bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=(20, 0))
        
        tk.Label(self.main_content, text=t, font=("Sans", 32, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=(10, 5))
        if s: tk.Label(self.main_content, text=s, font=("Sans", 14), bg=BG_COLOR, fg=FG_COLOR).pack(pady=(0, 20))

    def btn(self, parent, text, cmd, color=BUTTON_COLOR, width=18):
        return tk.Button(parent, text=text, command=cmd, bg=color, fg="white", 
                         font=("Sans", 11, "bold"), relief="flat", padx=25, pady=12, 
                         activebackground=ACCENT_COLOR, cursor="hand2", width=width)

    def step_list(self):
        self.clean(); self.head("Configuración WiFi", "Busca y selecciona una red")
        f = tk.Frame(self.main_content, bg=BG_COLOR); f.pack(fill="x", padx=120)
        self.lb = tk.Listbox(f, width=40, height=8, bg=SECONDARY_BG, fg="white", font=("Sans", 12), 
                             bd=0, highlightthickness=1, highlightbackground=BUTTON_COLOR, 
                             selectbackground=ACCENT_COLOR, borderwidth=10, relief="flat")
        self.lb.pack(pady=10, fill="x")
        
        btn_frame = tk.Frame(self.main_content, bg=BG_COLOR); btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="🔄 ACTUALIZAR LISTA", command=self.scan, bg=BUTTON_COLOR, fg="white", font=("Sans",10), relief="flat", padx=20, pady=8).pack(side="left", padx=5)
        tk.Button(btn_frame, text="⚡ REINICIAR WIFI", command=self.reset_wifi, bg=BUTTON_COLOR, fg="white", font=("Sans",10), relief="flat", padx=20, pady=8).pack(side="left", padx=5)

        nav = tk.Frame(self.main_content, bg=BG_COLOR); nav.pack(side="bottom", pady=40)
        self.btn(nav, "CERRAR", self.root.destroy, DANGER_COLOR, width=12).pack(side="left", padx=25)
        self.btn(nav, "SIGUIENTE", self.step_pass, ACCENT_COLOR, width=12).pack(side="left", padx=25)
        self.scan()

    def scan(self):
        self.lb.delete(0, tk.END); self.ssids = []
        try:
            subprocess.run(["nmcli", "dev", "wifi", "rescan"], stderr=subprocess.DEVNULL)
            o = subprocess.check_output(["nmcli","-t","-f","SSID","dev","wifi","list"], universal_newlines=True)
            for l in o.splitlines():
                if l and l not in self.ssids: 
                    self.ssids.append(l); self.lb.insert(tk.END, f"  📶  {l}")
        except: self.lb.insert(tk.END, "No se detectaron redes WiFi")

    def reset_wifi(self):
        self.lb.delete(0, tk.END); self.lb.insert(tk.END, "Reiniciando adaptador WiFi...")
        self.root.update()
        def run():
            subprocess.run(["nmcli", "radio", "wifi", "off"])
            import time; time.sleep(2)
            subprocess.run(["nmcli", "radio", "wifi", "on"])
            time.sleep(3)
            self.root.after(0, self.scan)
        threading.Thread(target=run, daemon=True).start()

    def step_pass(self):
        idx = self.lb.curselection()
        if not idx: messagebox.showwarning("WiFi", "Selecciona una red de la lista"); return
        self.ssid = self.ssids[idx[0]]
        self.clean(); self.head("Seguridad Red", f"Conectando a: {self.ssid}")
        f = tk.Frame(self.main_content, bg=SECONDARY_BG, padx=40, pady=20); f.pack(pady=10)
        
        tk.Label(f, text="CONTRASEÑA WIFI", bg=SECONDARY_BG, fg=ACCENT_COLOR, font=("Sans", 10, "bold")).pack(anchor="w")
        self.ep = tk.Entry(f, show="*", width=35, font=("Sans", 14), bg=BG_COLOR, fg="white", bd=0, insertbackground="white", highlightthickness=1, highlightbackground=BUTTON_COLOR)
        self.ep.pack(pady=(5, 5), ipady=8)
        
        self.show_pw = tk.BooleanVar(value=False)
        tk.Checkbutton(f, text="Mostrar contraseña", variable=self.show_pw, command=self.toggle_pw,
                       bg=SECONDARY_BG, fg="white", selectcolor=BG_COLOR, activebackground=SECONDARY_BG, font=("Sans", 9)).pack(anchor="w", pady=(0, 15))

        tk.Label(f, text="NOMBRE DEL EQUIPO (HOSTNAME)", bg=SECONDARY_BG, fg=ACCENT_COLOR, font=("Sans", 10, "bold")).pack(anchor="w")
        self.eh = tk.Entry(f, width=35, font=("Sans", 14), bg=BG_COLOR, fg="white", bd=0, insertbackground="white", highlightthickness=1, highlightbackground=BUTTON_COLOR)
        try: cur_host = subprocess.check_output(["hostname"], text=True).strip()
        except: cur_host = "orangepi5pro"
        self.eh.insert(0, cur_host)
        self.eh.pack(pady=(5, 15), ipady=8)

        self.static_ip_var = tk.BooleanVar(value=False)
        
        # V6.3: Static IP Recommendation
        rec_frame = tk.Frame(f, bg="#1e40af", padx=10, pady=8)
        rec_frame.pack(fill="x", pady=(10, 5))
        tk.Label(rec_frame, text="💡 RECOMENDACIÓN", bg="#1e40af", fg="white", font=("Sans", 9, "bold")).pack(anchor="w")
        tk.Label(rec_frame, text="Para uso astronómico, se recomienda IP FIJA para conexión estable.", 
                 bg="#1e40af", fg="white", font=("Sans", 9), wraplength=400, justify="left").pack(anchor="w")
        
        tk.Checkbutton(f, text="Configuración IP Manual (Avanzado)", variable=self.static_ip_var, command=self.toggle_ip,
                       bg=SECONDARY_BG, fg="white", selectcolor=BG_COLOR, activebackground=SECONDARY_BG, font=("Sans", 10)).pack(anchor="w", pady=5)
        
        self.ip_frame = tk.Frame(f, bg=SECONDARY_BG)
        self.entries = {}
        for lbl in ["Dirección IP (ej: 192.168.1.50/24)", "Puerta de Enlace (ej: 192.168.1.1)", "DNS (ej: 8.8.8.8)"]:
            tk.Label(self.ip_frame, text=lbl, bg=SECONDARY_BG, fg=FG_COLOR, font=("Sans", 9)).pack(anchor="w")
            e = tk.Entry(self.ip_frame, width=35, bg=BG_COLOR, fg="white", bd=0, insertbackground="white"); e.pack(pady=(0, 10), ipady=5)
            self.entries[lbl] = e
        
        nav = tk.Frame(self.main_content, bg=BG_COLOR); nav.pack(side="bottom", pady=40)
        self.btn(nav, "VOLVER", self.step_list, BUTTON_COLOR, width=10).pack(side="left", padx=20)
        self.btn(nav, "GUARDAR", self.connect, ACCENT_COLOR, width=15).pack(side="left", padx=20)

    def toggle_pw(self):
        if self.show_pw.get(): self.ep.config(show="")
        else: self.ep.config(show="*")

    def toggle_ip(self):
        if self.static_ip_var.get(): 
            self.ip_frame.pack(fill="x", pady=10)
            self.root.geometry("800x850")
        else: 
            self.ip_frame.pack_forget()
            self.root.geometry("800x800")

    def connect(self):
        pw = self.ep.get().strip()
        hname = self.eh.get().strip() or "orangepi5pro"
        con_name = "Astro-WIFI"
        is_static = self.static_ip_var.get()
        ip_val, gw_val, dns_val = "", "", ""
        if is_static:
            ip_val = self.entries["Dirección IP (ej: 192.168.1.50/24)"].get().strip()
            gw_val = self.entries["Puerta de Enlace (ej: 192.168.1.1)"].get().strip()
            dns_val = self.entries["DNS (ej: 8.8.8.8)"].get().strip()
            if not ip_val or not gw_val: messagebox.showwarning("Error IP", "IP/GW Faltan"); return

        self.clean(); self.head("Guardando...", f"Configurando {self.ssid}")
        tk.Label(self.main_content, text="Registrando configuración...\n(NO se conectará ahora para evitar bloqueos)", bg=BG_COLOR, fg=FG_COLOR, font=("Sans", 11)).pack(pady=10)
        
        log_box = tk.Text(self.main_content, height=12, bg="black", fg="#00ff00", font=("Consolas", 10))
        log_box.pack(fill="x", padx=20, pady=10)
        def log(msg):
            print(f"[DEBUG] {msg}")
            log_box.insert(tk.END, f"> {msg}\n"); log_box.see(tk.END)
        self.root.update()
        
        def run():
            try:
                log(f"Hostname: {hname}")
                subprocess.run(["sudo", "hostnamectl", "set-hostname", hname])
                subprocess.run(f"sudo sed -i 's/127.0.1.1.*/127.0.1.1\\t{hname}/' /etc/hosts", shell=True)

                log("Deshabilitando servicio Hotspot (para próximo boot)...")
                subprocess.run(["sudo", "systemctl", "disable", "astro-network.service"])

                log(f"Borrando perfil anterior '{con_name}'...")
                subprocess.run(["sudo", "nmcli", "con", "delete", con_name], stderr=subprocess.DEVNULL)

                log(f"Creando perfil {self.ssid}...")
                cmd_add = ["sudo", "nmcli", "con", "add", "type", "wifi", "ifname", "wlan0", "con-name", con_name, "ssid", self.ssid, "connection.autoconnect", "yes"]
                res = subprocess.run(cmd_add, capture_output=True, text=True)
                if res.returncode != 0: raise Exception(f"Add Fail: {res.stderr}")

                if pw:
                    log("Añadiendo password...")
                    cmd_sec = ["sudo", "nmcli", "con", "modify", con_name, "wifi-sec.key-mgmt", "wpa-psk", "wifi-sec.psk", pw]
                    subprocess.run(cmd_sec, check=True)

                if is_static:
                    log(f"IP Estática: {ip_val}")
                    cmd_ip = ["sudo", "nmcli", "con", "modify", con_name, "ipv4.method", "manual", "ipv4.addresses", ip_val, "ipv4.gateway", gw_val, "ipv4.dns", dns_val]
                    subprocess.run(cmd_ip, check=True)
                else:
                    log("DHCP Automático...")
                    subprocess.run(["sudo", "nmcli", "con", "modify", con_name, "ipv4.method", "auto"], check=True)

                log("✅ GUARDADO CORRECTAMENTE.")
                log("(Saltando activación en vivo para evitar bloqueo)")
                
                # V6.2: Show message FIRST, THEN close
                def show_success():
                    msg = f"✅ Configuración GUARDADA correctamente.\n\nPASO FINAL OBLIGATORIO:\n\n1. Desconecta el cable Ethernet\n2. REINICIA el sistema\n\nEl WiFi '{self.ssid}' se conectará automáticamente al arrancar."
                    messagebox.showinfo("🎉 Configuración Guardada", msg)
                    self.root.destroy()
                
                self.root.after(0, show_success)

            except Exception as e:
                log(f"ERROR: {e}")
                self.root.after(0, lambda: messagebox.showerror("Error", f"Fallo (Ver LOG): {e}"))
                self.root.after(0, self.show_back_button)

        threading.Thread(target=run, daemon=True).start()

    def show_back_button(self):
        tk.Button(self.main_content, text="VOLVER AL MENÚ", command=self.step_list, 
                  bg=DANGER_COLOR, fg="white", font=("Sans", 11, "bold"), padx=20, pady=10).pack(pady=20)

    def center_window(self):
        self.root.update_idletasks()
        w, h = self.root.winfo_width(), self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"+{x}+{y}")

if __name__ == "__main__":
    root = tk.Tk(); app = NetWizard(root); app.center_window()
    icon_paths = [
        "/usr/share/icons/Papirus/32x32/apps/network-wireless-hotspot.png",
        "/usr/share/icons/hicolor/48x48/apps/nm-device-wireless.png",
        "/usr/share/icons/Adwaita/48x48/devices/network-wireless.png",
        "/usr/share/pixmaps/nm-signal-100.png"
    ]
    for p in icon_paths:
        if os.path.exists(p):
            try: root.iconphoto(False, tk.PhotoImage(file=p)); break
            except: pass
    root.mainloop()
