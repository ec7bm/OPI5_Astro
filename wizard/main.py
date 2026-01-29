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
    """Detect current IP range to provide smart defaults"""
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
    """Displays a rotating carousel of astronomical images"""
    def __init__(self, parent, image_folder="/opt/astroorange/assets/gallery"):
        self.parent = parent
        self.images = []
        self.current_index = 0
        self.label = None
        
        # Priority search for images
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
                    # Resize to fit window while keeping aspect or slightly cropping
                    img = img.resize((800, 450), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    self.images.append(photo)
            except Exception as e:
                print(f"Error loading carousel images: {e}")
        
        if self.images:
            self.label = tk.Label(parent, bg=BG_COLOR)
            self.label.pack(pady=10)
            self.animate()
        else:
            tk.Label(parent, text="(No hay imágenes en la galería)", fg="grey", bg=BG_COLOR).pack(pady=50)
    
    def animate(self):
        if self.images and self.label and self.parent.winfo_exists():
            self.label.config(image=self.images[self.current_index])
            self.current_index = (self.current_index + 1) % len(self.images)
            self.label.after(5000, self.animate)

class WizardApp:
    def __init__(self, root):
        self.root = root
        self.wifi_list = []
        
        # State persistence
        self.username = "astro"
        self.password = ""
        self.selected_ssid = ""
        self.wifi_password = ""
        
        # Smart defaults
        def_ip, def_gw, def_dns = get_network_defaults()
        self.static_ip_enabled = False
        self.ip_addr = def_ip
        self.gateway = def_gw
        self.dns_server = def_dns
        
        self.static_ip_var = tk.BooleanVar(value=False)
        
        self.setup_window()
        
        if not os.path.exists("/etc/astro-configured"):
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
            img_path = "/usr/share/backgrounds/astro-wallpaper.jpg"
            if not os.path.exists(img_path):
                img_path = "/opt/astroorange/assets/astro-wallpaper.jpg"
            
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

    def nav_buttons(self, next_command, back_command=None, next_text="SIGUIENTE ➔"):
        btn_frame = tk.Frame(self.root, bg=BG_COLOR)
        btn_frame.pack(side="bottom", pady=40, fill="x")
        
        if back_command:
            tk.Button(btn_frame, text="⬅ VOLVER", font=("Sans", 12, "bold"), bg=BUTTON_COLOR, fg="white",
                      padx=20, pady=10, command=back_command).pack(side="left", padx=40)
        
        tk.Button(btn_frame, text=next_text, font=("Sans", 14, "bold"), bg=ACCENT_COLOR, fg=BG_COLOR, 
                  padx=30, pady=10, command=next_command).pack(side="right", padx=40)

    # --- PASO 0: ETHERNET ---
    def show_step_0(self):
        self.clear_window()
        self.header("¡Bienvenido a AstroOrange V2!", "Configuración Inicial Guiada")
        info = ("Para una experiencia óptima, conecta tu Orange Pi por cable ETHERNET\n"
                "al menos durante esta primera configuración.\n\n"
                "Esto garantiza que el Wizard funcione perfectamente y\n"
                "permite escanear las redes WiFi de forma segura.")
        tk.Label(self.root, text=info, font=("Sans", 13), bg=BG_COLOR, fg="white", justify="center").pack(pady=40)
        self.nav_buttons(next_command=self.show_step_1)

    # --- PASO 1: CUENTA ---
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
        self.username = self.entry_user.get()
        self.password = self.entry_pass.get()
        if not self.username or not self.password:
            messagebox.showerror("Error", "Usuario y contraseña requeridos.")
            return
        self.show_step_2()

    # --- PASO 2: SCAN WIFI ---
    def show_step_2(self):
        self.clear_window()
        self.header("Paso 2: Red WiFi", "Selecciona tu red inalámbrica")
        tk.Label(self.root, text="Buscando redes cercanas...", bg=BG_COLOR, fg=FG_COLOR).pack(pady=5)
        
        self.listbox = tk.Listbox(self.root, font=("Sans", 12), width=50, height=10, bg=BUTTON_COLOR, fg="white", selectbackground=ACCENT_COLOR)
        self.listbox.pack(pady=10)
        
        # Evento: Doble clic o Enter para seleccionar y pasar
        self.listbox.bind('<Double-Button-1>', lambda e: self.validate_step_2())
        
        btn_scan_frame = tk.Frame(self.root, bg=BG_COLOR); btn_scan_frame.pack(pady=5)
        tk.Button(btn_scan_frame, text="🔄 REESCANEAR", command=self.scan_wifi, bg=BUTTON_COLOR, fg="white").pack(side="left", padx=10)
        tk.Button(btn_scan_frame, text="🔧 CONFIGURACIÓN MANUAL", command=lambda: self.show_step_3(manual=True), bg=BUTTON_COLOR, fg="yellow").pack(side="left", padx=10)
        
        self.scan_wifi()
        self.nav_buttons(next_command=self.validate_step_2, back_command=self.show_step_1)

    def scan_wifi(self):
        self.listbox.delete(0, tk.END)
        try:
            output = subprocess.check_output(["nmcli", "-t", "-f", "SSID,SIGNAL", "device", "wifi", "list"], universal_newlines=True)
            self.wifi_list = []
            for line in output.splitlines():
                if line.strip() and ":" in line:
                    ssid = line.split(":")[0]
                    if ssid and ssid not in self.wifi_list:
                        self.wifi_list.append(ssid)
                        self.listbox.insert(tk.END, f"📶 {ssid}")
        except:
            self.listbox.insert(tk.END, "(No se detectó dispositivo WiFi)")

    def validate_step_2(self):
        idx = self.listbox.curselection()
        if idx:
            self.selected_ssid = self.wifi_list[idx[0]]
            self.show_step_3()
        else:
            # Si no hay nada marcado pero le da a siguiente, avisar o dejar manual
            if messagebox.askyesno("Sin WiFi", "¿Deseas continuar sin configurar WiFi?\n(Solo Ethernet)"):
                self.selected_ssid = ""
                self.show_step_3()

    # --- PASO 3: CONFIG WIFI ---
    def show_step_3(self, manual=False):
        self.clear_window()
        self.header("Configuración de Red", "Introduce los datos de conexión")
        frame = tk.Frame(self.root, bg=BG_COLOR); frame.pack(pady=20)
        
        # SSID Row
        tk.Label(frame, text="Nombre WiFi (SSID):", bg=BG_COLOR, fg="white", font=("Sans", 12)).grid(row=0, column=0, pady=10, padx=10, sticky="e")
        self.entry_ssid = tk.Entry(frame, font=("Sans", 12), width=30); self.entry_ssid.grid(row=0, column=1, pady=10, padx=10)
        self.entry_ssid.insert(0, self.selected_ssid)
        if not manual and self.selected_ssid: 
            self.entry_ssid.config(state="readonly")
        
        # Password Row
        tk.Label(frame, text="Contraseña WiFi:", bg=BG_COLOR, fg="white", font=("Sans", 12)).grid(row=1, column=0, pady=10, padx=10, sticky="e")
        self.wifi_pass = tk.Entry(frame, show="*", font=("Sans", 12), width=30); self.wifi_pass.grid(row=1, column=1, pady=10, padx=10)
        self.wifi_pass.insert(0, self.wifi_password)
        
        tk.Checkbutton(frame, text="Configuración IP Avanzada (Estática)", variable=self.static_ip_var,
                       bg=BG_COLOR, fg="yellow", selectcolor=BG_COLOR, command=self.toggle_static_fields).grid(row=2, columnspan=2, pady=20)
        
        self.static_frame = tk.Frame(frame, bg=BG_COLOR); self.static_frame.grid(row=3, columnspan=2)
        
        tk.Label(self.static_frame, text="IP Estática:", bg=BG_COLOR, fg=FG_COLOR).grid(row=0, column=0, padx=5, pady=2)
        self.entry_ip = tk.Entry(self.static_frame, width=20); self.entry_ip.grid(row=0, column=1, padx=5, pady=2)
        self.entry_ip.insert(0, self.ip_addr)
        
        tk.Label(self.static_frame, text="Puerta Enlace:", bg=BG_COLOR, fg=FG_COLOR).grid(row=1, column=0, padx=5, pady=2)
        self.entry_gw = tk.Entry(self.static_frame, width=20); self.entry_gw.grid(row=1, column=1, padx=5, pady=2)
        self.entry_gw.insert(0, self.gateway)
        
        tk.Label(self.static_frame, text="DNS:", bg=BG_COLOR, fg=FG_COLOR).grid(row=2, column=0, padx=5, pady=2)
        self.entry_dns = tk.Entry(self.static_frame, width=20); self.entry_dns.grid(row=2, column=1, padx=5, pady=2)
        self.entry_dns.insert(0, self.dns_server)
        
        self.toggle_static_fields()
        self.nav_buttons(next_command=self.finish_setup, back_command=self.show_step_2, next_text="GUARDAR Y FINALIZAR")

    def toggle_static_fields(self):
        state = "normal" if self.static_ip_var.get() else "disabled"
        for child in self.static_frame.winfo_children():
            child.configure(state=state)

    def finish_setup(self):
        # Save state before proceeding
        self.selected_ssid = self.entry_ssid.get()
        self.wifi_password = self.wifi_pass.get()
        self.static_ip_enabled = self.static_ip_var.get()
        if self.static_ip_enabled:
            self.ip_addr = self.entry_ip.get()
            self.gateway = self.entry_gw.get()
            self.dns_server = self.entry_dns.get()

        if messagebox.askyesno("Confirmar", "¿Aplicar configuración y reiniciar?"):
            self.clear_window()
            tk.Label(self.root, text="Aplicando cambios en el sistema...", font=("Sans", 18), bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=100)
            tk.Label(self.root, text="Esto tomará unos segundos. La placa se reiniciará sola.", bg=BG_COLOR, fg="white").pack()
            self.root.update()
            
            try:
                # 1. Crear usuario
                subprocess.call(f"sudo useradd -m -s /bin/bash -G sudo,dialout,video,input,plugdev,netdev {self.username}", shell=True)
                subprocess.call(f"echo '{self.username}:{self.password}' | sudo chpasswd", shell=True)
                
                # 2. Configurar Autologin
                # Usamos 90-astro.conf para asegurar que sobreescribe cualquier otra config previa
                username_clean = self.username.strip()
                subprocess.call(f"echo '[Seat:*]\nautologin-user={username_clean}\nautologin-session=xfce\n' | sudo tee /etc/lightdm/lightdm.conf.d/90-astro.conf", shell=True)
                
                # Intentar limpiar cualquier rastro de autologin previo
                subprocess.call("sudo rm -f /etc/lightdm/lightdm.conf.d/50-setup.conf", shell=True)
                subprocess.call("sudo rm -f /etc/lightdm/lightdm.conf.d/50-astro.conf", shell=True)
                
                # 3. Configurar WiFi
                if self.selected_ssid:
                    base_cmd = f"sudo nmcli dev wifi connect '{self.selected_ssid}' password '{self.wifi_password}'"
                    if self.static_ip_enabled:
                        subprocess.call(f"{base_cmd} ipv4.method manual ipv4.addresses {self.ip_addr}/24 ipv4.gateway {self.gateway} ipv4.dns {self.dns_server}", shell=True)
                    else:
                        subprocess.call(base_cmd, shell=True)
                
                # 4. Heredar config
                user_home = f"/home/{self.username}"
                subprocess.call(f"sudo mkdir -p {user_home}/.config/autostart", shell=True)
                subprocess.call(f"sudo cp /etc/xdg/autostart/astro-wizard.desktop {user_home}/.config/autostart/", shell=True)
                subprocess.call(f"sudo mkdir -p {user_home}/.config/xfce4/xfconf/xfce-perchannel-xml", shell=True)
                subprocess.call(f"sudo cp -r /home/astro-setup/.config/xfce4/xfconf/xfce-perchannel-xml/* {user_home}/.config/xfce4/xfconf/xfce-perchannel-xml/", shell=True)
                subprocess.call(f"sudo chown -R {self.username}:{self.username} {user_home}", shell=True)
                
                subprocess.call("sudo touch /etc/astro-configured", shell=True)
                messagebox.showinfo("AstroOrange V2", "Configuración completada. Reiniciando...")
                subprocess.call("sudo reboot", shell=True)
            except Exception as e:
                messagebox.showerror("Error Critico", f"Error al configurar: {e}")

    def is_installed(self, binary):
        """Checks if a binary is available in the system PATH"""
        return shutil.which(binary) is not None

    # --- ETAPA 2: INSTALADOR ---
    def show_stage_2(self):
        self.clear_window()
        self.header("Etapa 2: Instalador de Software", "Personaliza tu estación astronómica")
        
        frame = tk.Frame(self.root, bg=BG_COLOR); frame.pack(pady=10)
        
        # Mapping names to binaries to check if they are already installed
        software_map = {
            "KStars / INDI": "kstars",
            "PHD2 Guiding": "phd2",
            "ASTAP (Plate Solver)": "astap",
            "Stellarium": "stellarium",
            "AstroDMX Capture": "astrodmxcapture",
            "CCDciel": "ccdciel",
            "Syncthing": "syncthing"
        }

        self.vars = {}
        for i, (name, binary) in enumerate(software_map.items()):
            already_installed = self.is_installed(binary)
            # Default to True for kstars/phd/astap if not installed, otherwise reflect system state
            initial_val = True if name in ["KStars / INDI", "PHD2 Guiding", "ASTAP (Plate Solver)"] and not already_installed else already_installed
            
            self.vars[name] = tk.BooleanVar(value=initial_val)
            
            cb = tk.Checkbutton(frame, text=name, variable=self.vars[name], bg=BG_COLOR, fg="white", 
                               selectcolor=BG_COLOR, font=("Sans", 11))
            cb.grid(row=i//2, column=i%2, sticky="w", padx=20, pady=5)
            
            if already_installed:
                cb.config(fg=ACCENT_COLOR) # Visual hint that it's already there

        tk.Button(self.root, text="🚀 INICIAR INSTALACIÓN", command=self.start_install, 
                  bg=ACCENT_COLOR, fg=BG_COLOR, font=("Sans", 14, "bold"), width=30).pack(pady=20)

    def start_install(self):
        install_win = tk.Toplevel(self.root)
        install_win.title("Instalando Software Astronómico")
        install_win.geometry("900x750")
        install_win.configure(bg=BG_COLOR)
        
        tk.Label(install_win, text="🚀 Instalando... Por favor, no apagues la placa.", 
                 font=("Sans", 16, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=20)
        tk.Label(install_win, text="Mientras tanto, disfruta de estas vistas del cosmos:", 
                 bg=BG_COLOR, fg="white").pack()
        
        # FIX: Store carousel in instance to prevent GC
        self.carousel = ImageCarousel(install_win)
        
        threading.Thread(target=self.run_install, args=(install_win,)).start()

    def run_install(self, install_win):
        cmds = ["export DEBIAN_FRONTEND=noninteractive", "sudo apt-get update"]
        if self.vars["KStars / INDI"].get(): cmds.append("sudo add-apt-repository -y ppa:mutlaqja/ppa && sudo apt-get install -y kstars-bleeding indi-full gsc")
        if self.vars["PHD2 Guiding"].get(): cmds.append("sudo add-apt-repository -y ppa:pch/phd2 && sudo apt-get install -y phd2")
        if self.vars["ASTAP (Plate Solver)"].get(): cmds.append("wget https://www.hnsky.org/astap_arm64.deb -O /tmp/astap.deb && sudo apt-get install -y /tmp/astap.deb")
        if self.vars["Stellarium"].get(): cmds.append("sudo apt-get install -y stellarium")
        if self.vars["Syncthing"].get(): cmds.append("sudo apt-get install -y syncthing")
        
        full_command = " && ".join(cmds)
        # Better terminal message
        msg_finish = "echo '---------------------------------------------------'; echo '✅ INSTALACIÓN COMPLETADA'; echo 'Pulsa ENTER para cerrar esta ventana y finalizar'; read"
        
        subprocess.call(["xfce4-terminal", "--geometry=90x25", "--title=Progreso de Instalación", "-e", f"bash -c '{full_command}; {msg_finish}'"])
        
        subprocess.call("rm -f ~/.config/autostart/astro-wizard.desktop", shell=True)
        install_win.destroy()
        messagebox.showinfo("Finalizado", "Proceso completado.\nSi has instalado programas nuevos, ya aparecerán en el menú.")
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk(); app = WizardApp(root); root.mainloop()
