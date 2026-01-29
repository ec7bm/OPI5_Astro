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
    Image = None
    ImageTk = None

BG_COLOR = "#0f172a"
FG_COLOR = "#e2e8f0"
ACCENT_COLOR = "#38bdf8"
BUTTON_COLOR = "#475569"

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
    except:
        pass
    return "192.168.1.100", "192.168.1.1", "8.8.8.8"

class ImageCarousel:
    def __init__(self, parent, image_folder="/opt/astroorange/assets/gallery"):
        self.parent = parent
        self.images = []
        self.current_index = 0
        self.label = None
        paths = [image_folder, "/usr/share/backgrounds/gallery", "./userpatches/gallery"]
        actual_path = image_folder
        for p in paths:
            if os.path.exists(p) and glob(os.path.join(p, "*.png")):
                actual_path = p
                break
        if Image and ImageTk and os.path.exists(actual_path):
            try:
                image_files = sorted(glob(os.path.join(actual_path, "*.png")))
                for img_path in image_files:
                    img = Image.open(img_path)
                    img = img.resize((800, 450), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    self.images.append(photo)
            except Exception as e:
                print(f"Error loading carousel: {e}")
        if self.images:
            self.label = tk.Label(parent, bg=BG_COLOR)
            self.label.pack(pady=10)
            self.animate()

    def animate(self):
        if self.images and self.label and self.parent.winfo_exists():
            self.label.config(image=self.images[self.current_index])
            self.current_index = (self.current_index + 1) % len(self.images)
            self.label.after(5000, self.animate)

class WizardApp:
    def __init__(self, root):
        self.root = root
        self.wifi_list = []
        
        # PERSISTENT STATE
        self.username = "astro"
        self.password = ""
        self.selected_ssid = ""
        self.wifi_password = ""
        
        def_ip, def_gw, def_dns = get_network_defaults()
        self.static_ip_enabled = False
        self.ip_addr = def_ip
        self.gateway = def_gw
        self.dns_server = def_dns
        
        self.static_ip_var = tk.BooleanVar(value=False)
        
        import sys
        is_autostart = "--autostart" in sys.argv
        is_configured = os.path.exists("/etc/astro-configured")
        is_finished = os.path.exists("/etc/astro-finished")
        
        if is_autostart and is_finished:
            self.root.destroy()
            return

        self.setup_window()
        self.create_wizard_shortcut()
        
        if not is_configured:
            self.show_step_0() 
        else:
            self.show_stage_2() 

    def setup_window(self):
        self.root.title("AstroOrange V2 - Wizard")
        self.root.geometry("900x750")
        self.root.configure(bg=BG_COLOR)
        
        self.bg_label = tk.Label(self.root)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.update_background()

    def update_background(self):
        try:
            img_path = "/usr/share/backgrounds/astro-wallpaper.png"
            if not os.path.exists(img_path):
                img_path = "/opt/astroorange/assets/astro-wallpaper.png"
            
            if Image and os.path.exists(img_path):
                img = Image.open(img_path)
                img = img.resize((900, 750), Image.Resampling.LANCZOS)
                self.bg_photo = ImageTk.PhotoImage(img)
                self.bg_label.config(image=self.bg_photo)
            else:
                self.bg_label.config(bg=BG_COLOR)
        except:
            self.bg_label.config(bg=BG_COLOR)

    def clear_window(self):
        for widget in self.root.winfo_children():
            if widget != self.bg_label:
                widget.destroy()

    def header(self, title, subtitle=""):
        tk.Label(self.root, text=title, font=("Sans", 26, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=(40, 5))
        if subtitle:
            tk.Label(self.root, text=subtitle, font=("Sans", 12, "italic"), bg=BG_COLOR, fg=FG_COLOR).pack(pady=(0, 20))

    def create_wizard_shortcut(self):
        try:
            desktop_dir = os.path.expanduser("~/Desktop")
            os.makedirs(desktop_dir, exist_ok=True)
            src = "/usr/share/applications/astro-wizard.desktop"
            dst = os.path.join(desktop_dir, "astro-wizard.desktop")
            if os.path.exists(src) and not os.path.exists(dst):
                shutil.copy(src, dst)
                subprocess.call(f"gio set {dst} metadata::trusted true", shell=True)
                subprocess.call(f"chmod +x {dst}", shell=True)
        except:
            pass

    def nav_buttons(self, next_command, back_command=None, next_text="SIGUIENTE ➔"):
        btn_frame = tk.Frame(self.root, bg=BG_COLOR)
        btn_frame.pack(side="bottom", pady=40, fill="x")
        
        if back_command:
            tk.Button(btn_frame, text="⬅ VOLVER", font=("Sans", 12, "bold"), bg=BUTTON_COLOR, fg="white",
                      padx=20, pady=10, command=back_command).pack(side="left", padx=40)
        
        tk.Button(btn_frame, text=next_text, font=("Sans", 14, "bold"), bg=ACCENT_COLOR, fg=BG_COLOR, 
                  padx=30, pady=10, command=next_command).pack(side="right", padx=40)

    def show_step_0(self):
        self.clear_window()
        self.header("¡Bienvenido! AstroOrange V2", "Configuración Inicial Guiada")
        info = ("Recomendamos usar cable ETHERNET durante la primera configuración.\n"
                "Esto asegura estabilidad y permite escanear redes WiFi.")
        tk.Label(self.root, text=info, font=("Sans", 13), bg=BG_COLOR, fg="white", justify="center").pack(pady=40)
        self.nav_buttons(next_command=self.show_step_1)

    def show_step_1(self):
        self.clear_window()
        self.header("Paso 1: Tu Cuenta", "Crea el usuario principal del sistema")
        frame = tk.Frame(self.root, bg=BG_COLOR); frame.pack(pady=40)
        
        tk.Label(frame, text="Nombre de Usuario:", bg=BG_COLOR, fg="white", font=("Sans", 12)).grid(row=0, column=0, pady=10, padx=10, sticky="e")
        self.entry_user = tk.Entry(frame, font=("Sans", 12), width=25); self.entry_user.grid(row=0, column=1, pady=10, padx=10)
        self.entry_user.insert(0, self.username)
        
        tk.Label(frame, text="Contraseña:", bg=BG_COLOR, fg="white", font=("Sans", 12)).grid(row=1, column=0, pady=10, padx=10, sticky="e")
        self.entry_pass = tk.Entry(frame, show="*", font=("Sans", 12), width=25); self.entry_pass.grid(row=1, column=1, pady=10, padx=10)
        self.entry_pass.insert(0, self.password)
        
        self.nav_buttons(next_command=self.validate_step_1, back_command=self.show_step_0)

    def validate_step_1(self):
        self.username = self.entry_user.get().strip()
        self.password = self.entry_pass.get().strip()
        if not self.username or not self.password:
            messagebox.showerror("Error", "Usuario y contraseña requeridos.")
            return
        self.show_step_2()

    def show_step_2(self):
        self.clear_window()
        self.header("Paso 2: Red WiFi", "Selecciona tu red inalámbrica")
        tk.Label(self.root, text="Buscando redes cercanas...", bg=BG_COLOR, fg=FG_COLOR).pack(pady=5)
        
        self.listbox = tk.Listbox(self.root, font=("Sans", 12), width=50, height=10, bg=BUTTON_COLOR, fg="white", selectbackground=ACCENT_COLOR)
        self.listbox.pack(pady=10)
        self.listbox.bind('<Double-Button-1>', lambda e: self.validate_step_2())
        
        btn_scan_frame = tk.Frame(self.root, bg=BG_COLOR); btn_scan_frame.pack(pady=5)
        tk.Button(btn_scan_frame, text="🔄 REESCANEAR", command=self.scan_wifi, bg=BUTTON_COLOR, fg="white").pack(side="left", padx=10)
        tk.Button(btn_scan_frame, text="🔧 MANUAL", command=lambda: self.show_step_3(manual=True), bg=BUTTON_COLOR, fg="yellow").pack(side="left", padx=10)
        
        self.scan_wifi()
        self.nav_buttons(next_command=self.validate_step_2, back_command=self.show_step_1)

    def scan_wifi(self):
        self.listbox.delete(0, tk.END)
        try:
            output = subprocess.check_output(["nmcli", "-t", "-f", "SSID", "device", "wifi", "list"], universal_newlines=True)
            self.wifi_list = [line.strip() for line in output.splitlines() if line.strip()]
            for ssid in self.wifi_list:
                self.listbox.insert(tk.END, f"📶 {ssid}")
        except:
            self.listbox.insert(tk.END, "(No se detectó dispositivo WiFi)")

    def validate_step_2(self):
        idx = self.listbox.curselection()
        if idx:
            self.selected_ssid = self.wifi_list[idx[0]]
            self.show_step_3()
        else:
            if messagebox.askyesno("Sin WiFi", "¿Deseas continuar solo con Ethernet?"):
                self.selected_ssid = ""
                self.show_step_3()

    def show_step_3(self, manual=False):
        self.clear_window()
        self.header("Configuración de Red", "Introduce los datos de conexión")
        frame = tk.Frame(self.root, bg=BG_COLOR); frame.pack(pady=20)
        
        tk.Label(frame, text="Nombre WiFi (SSID):", bg=BG_COLOR, fg="white", font=("Sans", 12)).grid(row=0, column=0, pady=10, padx=10, sticky="e")
        self.entry_ssid = tk.Entry(frame, font=("Sans", 12), width=30); self.entry_ssid.grid(row=0, column=1, pady=10, padx=10)
        self.entry_ssid.insert(0, self.selected_ssid)
        if not manual and self.selected_ssid: 
            self.entry_ssid.config(state="readonly")
        
        tk.Label(frame, text="Contraseña WiFi:", bg=BG_COLOR, fg="white", font=("Sans", 12)).grid(row=1, column=0, pady=10, padx=10, sticky="e")
        pf = tk.Frame(frame, bg=BG_COLOR); pf.grid(row=1, column=1, pady=10, padx=10, sticky="w")
        self.wifi_pass = tk.Entry(pf, show="*", font=("Sans", 12), width=25); self.wifi_pass.pack(side=tk.LEFT)
        self.wifi_pass.insert(0, self.wifi_password)
        
        self.show_pass_var = tk.BooleanVar(value=False)
        tk.Checkbutton(pf, variable=self.show_pass_var, command=self.toggle_pass, bg=BG_COLOR, selectcolor=BG_COLOR).pack(side=tk.LEFT, padx=5)

        tk.Checkbutton(frame, text="Configuración IP Estática", variable=self.static_ip_var, bg=BG_COLOR, fg="yellow", command=self.toggle_static_fields).grid(row=2, columnspan=2, pady=20)
        
        self.static_frame = tk.Frame(frame, bg=BG_COLOR); self.static_frame.grid(row=3, columnspan=2)
        tk.Label(self.static_frame, text="IP:", bg=BG_COLOR, fg=FG_COLOR).grid(row=0, column=0, padx=5); self.entry_ip = tk.Entry(self.static_frame, width=15); self.entry_ip.grid(row=0, column=1); self.entry_ip.insert(0, self.ip_addr)
        tk.Label(self.static_frame, text="GW:", bg=BG_COLOR, fg=FG_COLOR).grid(row=0, column=2, padx=5); self.entry_gw = tk.Entry(self.static_frame, width=15); self.entry_gw.grid(row=0, column=3); self.entry_gw.insert(0, self.gateway)
        
        self.toggle_static_fields()
        self.nav_buttons(next_command=self.finish_setup, back_command=self.show_step_2, next_text="GUARDAR Y FINALIZAR")

    def toggle_pass(self):
        self.wifi_pass.config(show="" if self.show_pass_var.get() else "*")

    def toggle_static_fields(self):
        state = "normal" if self.static_ip_var.get() else "disabled"
        for child in self.static_frame.winfo_children(): child.configure(state=state)

    def finish_setup(self):
        # Capture current widgets data BEFORE clear_window
        self.selected_ssid = self.entry_ssid.get().strip()
        self.wifi_password = self.wifi_pass.get().strip()
        self.static_ip_enabled = self.static_ip_var.get()
        if self.static_ip_enabled:
            self.ip_addr = self.entry_ip.get().strip()
            self.gateway = self.entry_gw.get().strip()

        if messagebox.askyesno("Confirmar", "¿Aplicar cambios y reiniciar?"):
            self.clear_window()
            tk.Label(self.root, text="Aplicando cambios...", font=("Sans", 18), bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=100)
            self.root.update()
            try:
                # Use stored self.username and self.password
                subprocess.call(f"sudo useradd -m -s /bin/bash -G sudo,dialout,video,input,plugdev,netdev {self.username}", shell=True)
                subprocess.call(f"echo '{self.username}:{self.password}' | sudo chpasswd", shell=True)
                subprocess.call(f"echo '[Seat:*]\nautologin-user={self.username}\nautologin-session=xfce\n' | sudo tee /etc/lightdm/lightdm.conf.d/90-astro.conf", shell=True)
                
                if self.selected_ssid:
                    subprocess.call(f"sudo nmcli con delete '{self.selected_ssid}' 2>/dev/null || true", shell=True)
                    cmd = f"sudo nmcli con add type wifi ifname '*' con-name '{self.selected_ssid}' ssid '{self.selected_ssid}' -- 802-11-wireless-security.key-mgmt wpa-psk 802-11-wireless-security.psk '{self.wifi_password}'"
                    if self.static_ip_enabled:
                        cmd += f" ipv4.method manual ipv4.addresses '{self.ip_addr}/24' ipv4.gateway '{self.gateway}' ipv4.dns '8.8.8.8'"
                    else:
                        cmd += " ipv4.method auto"
                    subprocess.call(cmd, shell=True); subprocess.Popen(f"sudo nmcli con up '{self.selected_ssid}'", shell=True)
                
                subprocess.call("sudo touch /etc/astro-configured", shell=True)
                messagebox.showinfo("AstroOrange V2", "¡Listo! Reiniciando...")
                subprocess.call("sudo reboot", shell=True)
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def is_installed(self, binary):
        return shutil.which(binary) or any(os.path.exists(os.path.join(p, binary)) for p in ["/usr/bin", "/usr/local/bin", "/opt/astroorange/bin"])

    def show_stage_2(self):
        self.clear_window(); self.header("Etapa 2: Aplicaciones", "Instalador de Software")
        frame = tk.Frame(self.root, bg=BG_COLOR); frame.pack(pady=10)
        sw_map = {"KStars": "kstars", "PHD2": "phd2", "ASTAP": "astap", "Stellarium": "stellarium", "AstroDMX": "astrodmx", "CCDciel": "ccdciel"}
        self.vars = {}
        for i, (name, bin) in enumerate(sw_map.items()):
            inst = self.is_installed(bin)
            self.vars[name] = tk.BooleanVar(value=inst or name in ["KStars", "PHD2"])
            cb = tk.Checkbutton(frame, text=name, variable=self.vars[name], bg=BG_COLOR, fg="white" if not inst else "#00ff00", selectcolor=BG_COLOR, font=("Sans", 11))
            cb.grid(row=i//2, column=i%2, sticky="w", padx=20, pady=5)
            if inst: tk.Label(frame, text="(Ya instalado)", bg=BG_COLOR, fg="#00ff00", font=("Sans", 8)).grid(row=i//2, column=i%2, sticky="e")
        tk.Button(self.root, text="🚀 INICIAR INSTALACIÓN", command=self.start_install, bg=ACCENT_COLOR, fg=BG_COLOR, font=("Sans", 14, "bold"), width=30).pack(pady=20)

    def start_install(self):
        win = tk.Toplevel(self.root); win.geometry("900x750"); win.configure(bg=BG_COLOR)
        tk.Label(win, text="🚀 Instalando...", font=("Sans", 16, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=20)
        self.carousel = ImageCarousel(win)
        threading.Thread(target=self.run_install, args=(win,)).start()

    def run_install(self, win):
        cmds = ["sudo apt-get update"]
        if self.vars["KStars"].get(): cmds.append("sudo add-apt-repository -y ppa:mutlaqja/ppa && sudo apt-get install -y kstars-bleeding indi-full")
        if self.vars["PHD2"].get(): cmds.append("sudo add-apt-repository -y ppa:pch/phd2 && sudo apt-get install -y phd2")
        if self.vars["ASTAP"].get(): cmds.append("wget https://www.hnsky.org/astap_arm64.deb -O /tmp/astap.deb && sudo apt-get install -y /tmp/astap.deb")
        fcmd = " && ".join(cmds); subprocess.call(["xfce4-terminal", "-e", f"bash -c '{fcmd}; echo \"✅ COMPLETADO. Pulsa ENTER.\"; read'"])
        subprocess.call("sudo touch /etc/astro-finished", shell=True); win.destroy(); self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk(); app = WizardApp(root); root.mainloop()
