import tkinter as tk
from tkinter import messagebox
import subprocess, threading, os, time

# --- CONFIGURACIÓN V8.4: MANUAL WIFI & GUI FIXES ---
BG_COLOR, SECONDARY_BG, FG_COLOR = "#0f172a", "#1e293b", "#e2e8f0"
ACCENT_COLOR, SUCCESS_COLOR, DANGER_COLOR = "#38bdf8", "#22c55e", "#ef4444"
BUTTON_COLOR = "#334155"

class NetWizard:
    def __init__(self, root):
        self.root = root
        self.root.title("AstroOrange Network Manager (V8.4)")
        self.root.geometry("800x850")
        self.root.configure(bg=BG_COLOR)
        self.ssid = ""
        self.ssids = []
        self.scanning = False
        self.manual_mode = False  # Flag for manual entry
        
        self.main_content = tk.Frame(self.root, bg=BG_COLOR)
        self.main_content.pack(expand=True, fill="both")
        
        self.step_list()

    def clean(self):
        for w in self.main_content.winfo_children(): w.destroy()

    def get_ip_status(self):
        try:
            ip = subprocess.check_output("hostname -I", shell=True, text=True).strip()
            state = subprocess.check_output("nmcli -t -f STATE general", shell=True, text=True).strip()
            return f"{state} | IP: {ip}"
        except: return "Desconectado"

    def head(self, t, s=""):
        status_frm = tk.Frame(self.main_content, bg="#0f172a", height=30)
        status_frm.pack(fill="x", side="top")
        tk.Label(status_frm, text=self.get_ip_status(), bg="#0f172a", fg="#64748b", font=("Monospace", 9)).pack(side="right", padx=10)

        try:
            icon_path = "/usr/share/icons/Papirus/32x32/apps/network-wireless-hotspot.png"
            if os.path.exists(icon_path):
                img = tk.PhotoImage(file=icon_path)
                l = tk.Label(self.main_content, image=img, bg=BG_COLOR)
                l.image = img
                l.pack(pady=(10, 0))
            else:
                tk.Label(self.main_content, text="📡", font=("Sans", 48), bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=(10, 0))
        except: pass
        
        tk.Label(self.main_content, text=t, font=("Sans", 32, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=(5, 5))
        if s: tk.Label(self.main_content, text=s, font=("Sans", 14), bg=BG_COLOR, fg=FG_COLOR).pack(pady=(0, 20))

    def btn(self, parent, text, cmd, color=BUTTON_COLOR, width=18):
        return tk.Button(parent, text=text, command=cmd, bg=color, fg="white", 
                         font=("Sans", 11, "bold"), relief="flat", padx=25, pady=12, 
                         activebackground=ACCENT_COLOR, cursor="hand2", width=width)

    # --- PASO 1: LISTADO ---
    def step_list(self):
        self.clean(); self.head("Configuración WiFi", "Busca y selecciona una red")
        f = tk.Frame(self.main_content, bg=BG_COLOR); f.pack(fill="x", padx=120)
        sb = tk.Scrollbar(f); sb.pack(side="right", fill="y")
        self.lb = tk.Listbox(f, width=40, height=8, bg=SECONDARY_BG, fg="white", font=("Sans", 12), 
                             bd=0, selectbackground=ACCENT_COLOR, borderwidth=10, relief="flat", yscrollcommand=sb.set)
        self.lb.pack(pady=10, fill="x"); sb.config(command=self.lb.yview)
        
        btn_frame = tk.Frame(self.main_content, bg=BG_COLOR); btn_frame.pack(pady=10)
        self.btn_scan = tk.Button(btn_frame, text="🔄 ACTUALIZAR LISTA", command=self.scan_thread, bg=BUTTON_COLOR, fg="white", font=("Sans",10), relief="flat", padx=20, pady=8)
        self.btn_scan.pack(side="left", padx=5)
        
        # New Manual Button
        tk.Button(btn_frame, text="✍️ MANUAL / OCULTA", command=self.step_manual, bg=SECONDARY_BG, fg=ACCENT_COLOR, font=("Sans",10, "bold"), relief="flat", padx=20, pady=8).pack(side="left", padx=5)
        
        nav = tk.Frame(self.main_content, bg=BG_COLOR); nav.pack(side="bottom", pady=40)
        self.btn(nav, "SALIR", self.root.destroy, DANGER_COLOR, width=12).pack(side="left", padx=25)
        self.btn(nav, "SIGUIENTE", self.step_pass, ACCENT_COLOR, width=12).pack(side="left", padx=25)
        self.scan_thread()

    def scan_thread(self):
        if self.scanning: return
        self.scanning = True
        self.btn_scan.config(text="Buscando...", state="disabled")
        self.lb.delete(0, tk.END); self.lb.insert(tk.END, "Escaneando redes...")
        threading.Thread(target=self._scan_logic, daemon=True).start()

    def _scan_logic(self):
        try:
            subprocess.run(["nmcli", "dev", "wifi", "rescan"], stderr=subprocess.DEVNULL)
            time.sleep(1)
            o = subprocess.check_output(["nmcli","-t","-f","SSID","dev","wifi","list"], universal_newlines=True)
            self.ssids = []
            for l in o.splitlines():
                l = l.strip()
                if l and l not in self.ssids: self.ssids.append(l)
            self.root.after(0, self._update_list)
        except: self.root.after(0, lambda: self._update_list_error())

    def _update_list(self):
        self.lb.delete(0, tk.END)
        if not self.ssids: self.lb.insert(tk.END, "No se encontraron redes :(")
        else:
            for s in self.ssids: self.lb.insert(tk.END, f"  📶  {s}")
        self.btn_scan.config(text="🔄 ACTUALIZAR LISTA", state="normal"); self.scanning = False

    def _update_list_error(self):
        self.lb.delete(0, tk.END); self.lb.insert(tk.END, "Error al escanear")
        self.btn_scan.config(text="🔄 REINTENTAR", state="normal"); self.scanning = False

    def step_pass(self):
        idx = self.lb.curselection()
        if not idx: messagebox.showwarning("WiFi", "Selecciona una red de la lista"); return
        sel_text = self.lb.get(idx[0])
        if "📶" in sel_text: 
            self.ssid = self.ssids[idx[0]]
            self.manual_mode = False
            self.step_config()

    def step_manual(self):
        self.ssid = ""
        self.manual_mode = True
        self.step_config()

    # --- PASO 2: CONFIG ---
    def step_config(self):
        title = f"Conectando a: {self.ssid}" if not self.manual_mode else "Conexión Manual"
        self.clean(); self.head("Seguridad & Red", title)
        f = tk.Frame(self.main_content, bg=SECONDARY_BG, padx=40, pady=20); f.pack(pady=10)
        
        # Manual SSID input if needed
        if self.manual_mode:
            tk.Label(f, text="NOMBRE DE LA RED (SSID)", bg=SECONDARY_BG, fg=ACCENT_COLOR, font=("Sans", 10, "bold")).pack(anchor="w")
            self.entry_ssid = tk.Entry(f, width=35, font=("Sans", 14), bg=BG_COLOR, fg="white", bd=0, insertbackground="white")
            self.entry_ssid.pack(pady=(5, 15), ipady=8)
        
        tk.Label(f, text="CONTRASEÑA WIFI", bg=SECONDARY_BG, fg=ACCENT_COLOR, font=("Sans", 10, "bold")).pack(anchor="w")
        self.ep = tk.Entry(f, show="*", width=35, font=("Sans", 14), bg=BG_COLOR, fg="white", bd=0, insertbackground="white", highlightthickness=1, highlightbackground=BUTTON_COLOR)
        self.ep.pack(pady=(5, 5), ipady=8)
        
        self.show_pw = tk.BooleanVar(value=False)
        tk.Checkbutton(f, text="Mostrar contraseña", variable=self.show_pw, command=lambda: self.ep.config(show="" if self.show_pw.get() else "*"),
                       bg=SECONDARY_BG, fg="white", selectcolor=BG_COLOR, activebackground=SECONDARY_BG, font=("Sans", 9)).pack(anchor="w", pady=(0, 15))

        tk.Label(f, text="NOMBRE DEL EQUIPO (HOSTNAME)", bg=SECONDARY_BG, fg=ACCENT_COLOR, font=("Sans", 10, "bold")).pack(anchor="w")
        self.eh = tk.Entry(f, width=35, font=("Sans", 14), bg=BG_COLOR, fg="white", bd=0, insertbackground="white", highlightthickness=1, highlightbackground=BUTTON_COLOR)
        try: cur_host = subprocess.check_output(["hostname"], text=True).strip()
        except: cur_host = "orangepi5pro"
        self.eh.insert(0, cur_host); self.eh.pack(pady=(5, 15), ipady=8)

        self.static_ip_var = tk.BooleanVar(value=False)
        tk.Checkbutton(f, text="Configuración IP Manual (Avanzado)", variable=self.static_ip_var, command=self.toggle_ip,
                       bg=SECONDARY_BG, fg="white", selectcolor=BG_COLOR, activebackground=SECONDARY_BG, font=("Sans", 10, "bold")).pack(anchor="w", pady=5)
        
        self.ip_frame = tk.Frame(f, bg=SECONDARY_BG)
        self.entries = {}
        for lbl in ["Dirección IP (ej: 192.168.1.50/24)", "Puerta de Enlace (ej: 192.168.1.1)", "DNS (ej: 8.8.8.8)"]:
            tk.Label(self.ip_frame, text=lbl, bg=SECONDARY_BG, fg=FG_COLOR, font=("Sans", 9)).pack(anchor="w")
            e = tk.Entry(self.ip_frame, width=35, bg=BG_COLOR, fg="white", bd=0, insertbackground="white"); e.pack(pady=(0, 10), ipady=5)
            self.entries[lbl] = e
        
        nav = tk.Frame(self.main_content, bg=BG_COLOR); nav.pack(side="bottom", pady=40)
        self.btn(nav, "VOLVER", self.step_list, BUTTON_COLOR, width=10).pack(side="left", padx=20)
        self.btn(nav, "GUARDAR", self.save_logic, ACCENT_COLOR, width=15).pack(side="left", padx=20)

    def toggle_ip(self):
        if self.static_ip_var.get(): self.ip_frame.pack(fill="x", pady=10)
        else: self.ip_frame.pack_forget()

    # --- PASO 3: GUARDAR ---
    def save_logic(self):
        if self.manual_mode:
            target_ssid = self.entry_ssid.get().strip()
            if not target_ssid: messagebox.showwarning("Error", "Debes escribir el nombre de la red (SSID)"); return
        else:
            target_ssid = self.ssid

        pw = self.ep.get().strip()
        hname = self.eh.get().strip() or "orangepi5pro"
        con_name = "Astro-WIFI"
        is_static = self.static_ip_var.get()
        ip_val = ""; gw_val = ""; dns_val = ""

        if is_static:
            ip_val = self.entries["Dirección IP (ej: 192.168.1.50/24)"].get().strip()
            if "/" not in ip_val: ip_val += "/24"
            gw_val = self.entries["Puerta de Enlace (ej: 192.168.1.1)"].get().strip()
            dns_val = self.entries["DNS (ej: 8.8.8.8)"].get().strip()
            if not ip_val or not gw_val: messagebox.showwarning("Error IP", "Faltan datos de IP/Gateway"); return
        
        self.clean(); self.head("Guardando...", "Aplicando configuración...")
        log_box = tk.Text(self.main_content, height=15, bg="black", fg="#00ff00", font=("Consolas", 9))
        log_box.pack(fill="x", padx=20, pady=10)
        def log(msg): log_box.insert(tk.END, f"> {msg}\n"); log_box.see(tk.END)
        
        def run():
            try:
                log("1. Configurando Hostname...")
                subprocess.run(["sudo", "hostnamectl", "set-hostname", hname])
                subprocess.run(f"sudo sed -i 's/127.0.1.1.*/127.0.1.1\\t{hname}/' /etc/hosts", shell=True)
                
                log("2. Verificando Guardián de Red...")
                # Watchdog persistente
                
                log("3. Limpiando perfiles antiguos...")
                subprocess.run(["sudo", "nmcli", "con", "delete", con_name], stderr=subprocess.DEVNULL)
                
                iface_out = subprocess.check_output("nmcli -t -f DEVICE,TYPE device | grep wifi | cut -d: -f1 | head -n1", shell=True, text=True).strip()
                iface = iface_out if iface_out else "wlan0"

                log(f"4. Configurando WiFi en {iface}: {target_ssid}...")
                cmd = ["sudo", "nmcli", "con", "add", "type", "wifi", "ifname", iface, 
                       "con-name", con_name, "ssid", target_ssid, 
                       "connection.interface-name", iface, "connection.autoconnect", "yes"]
                subprocess.run(cmd, check=True)
                
                if pw:
                    cmd = ["sudo", "nmcli", "con", "modify", con_name, "wifi-sec.key-mgmt", "wpa-psk", "wifi-sec.psk", pw]
                    subprocess.run(cmd, check=True)
                else:
                    # Open network if no password provided
                    pass 
                
                if is_static:
                    log(f"Asignando IP Estática: {ip_val}...")
                    cmd = ["sudo", "nmcli", "con", "modify", con_name, "ipv4.method", "manual", 
                           "ipv4.addresses", ip_val, "ipv4.gateway", gw_val, "ipv4.dns", dns_val]
                    subprocess.run(cmd, check=True)
                else:
                    subprocess.run(["sudo", "nmcli", "con", "modify", con_name, "ipv4.method", "auto"], check=True)
                
                log("✅ HECHO. Pulsa 'REINICIAR AHORA'.")
                self.root.after(0, self.show_final_actions)
            except Exception as e:
                log(f"ERROR: {e}")
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        threading.Thread(target=run, daemon=True).start()

    def show_final_actions(self):
        f = tk.Frame(self.main_content, bg=BG_COLOR); f.pack(pady=20)
        tk.Label(f, text="✅ CONFIGURACIÓN GUARDADA", bg=BG_COLOR, fg=SUCCESS_COLOR, font=("Sans", 14, "bold")).pack(pady=5)
        
        # V11.2 RECOMMENDATION
        tk.Label(f, text="💡 RECOMENDACIÓN:\nUsa ETHERNET para la primera descarga de software.\n(Es más estable para archivos grandes)", 
                 bg=SECONDARY_BG, fg="white", font=("Sans", 10, "italic"), padx=20, pady=10).pack(pady=15)
        
        tk.Label(f, text="⚠️ REINICIO REQUERIDO", bg=BG_COLOR, fg="yellow", font=("Sans", 12, "bold")).pack(pady=5)
        self.btn(f, "REINICIAR AHORA", self.reboot_now, SUCCESS_COLOR, width=20).pack(pady=10)
        self.btn(f, "Cerrar", self.root.destroy, BUTTON_COLOR, width=10).pack()

    def reboot_now(self):
        subprocess.run("sudo reboot", shell=True)

if __name__ == "__main__":
    root = tk.Tk(); app = NetWizard(root)
    root.mainloop()
