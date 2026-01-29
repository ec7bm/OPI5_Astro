import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
import os
import threading
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

class ImageCarousel:
    """Displays a rotating carousel of astronomical images"""
    def __init__(self, parent, image_folder="/opt/astroorange/assets/gallery"):
        self.parent = parent
        self.images = []
        self.current_index = 0
        self.label = None
        
        if Image and ImageTk and os.path.exists(image_folder):
            try:
                image_files = sorted(glob(os.path.join(image_folder, "*.png")))
                for img_path in image_files:
                    img = Image.open(img_path)
                    img = img.resize((800, 450), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    self.images.append(photo)
            except Exception as e:
                print(f"Error loading carousel images: {e}")
        
        if self.images:
            self.label = tk.Label(parent, bg=BG_COLOR)
            self.label.pack(pady=10)
            self.animate()
    
    def animate(self):
        if self.images and self.label:
            self.label.config(image=self.images[self.current_index])
            self.current_index = (self.current_index + 1) % len(self.images)
            self.label.after(5000, self.animate)

class WizardApp:
    def __init__(self, root):
        self.root = root
        self.step = 0
        self.wifi_list = []
        self.selected_ssid = ""
        self.static_ip_var = tk.BooleanVar(value=False)
        
        self.setup_window()
        
        if not os.path.exists("/etc/astro-configured"):
            self.show_step_0() # Bienvenida
        else:
            self.show_stage_2() # Instalador

    def setup_window(self):
        self.root.title("AstroOrange V2 - Wizard")
        self.root.geometry("900x750")
        self.root.configure(bg=BG_COLOR)
        
        # El background se carga en cada pantalla para asegurar que está debajo
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

    def next_button(self, text="SIGUIENTE ➔", command=None, color=ACCENT_COLOR):
        tk.Button(self.root, text=text, font=("Sans", 14, "bold"), bg=color, fg=BG_COLOR, 
                  padx=30, pady=10, command=command).pack(side="bottom", pady=40)

    # --- PASO 0: ETHERNET ---
    def show_step_0(self):
        self.clear_window()
        self.header("¡Bienvenido a AstroOrange V2!", "Configuración Inicial Guiada")
        
        info = ("Para una experiencia óptima, conecta tu Orange Pi por cable ETHERNET\n"
                "al menos durante esta primera configuración.\n\n"
                "Esto garantiza que el Wizard funcione perfectamente y\n"
                "permite escanear las redes WiFi de forma segura.")
        
        tk.Label(self.root, text=info, font=("Sans", 13), bg=BG_COLOR, fg="white", justify="center").pack(pady=40)
        self.next_button(command=self.show_step_1)

    # --- PASO 1: CUENTA ---
    def show_step_1(self):
        self.clear_window()
        self.header("Paso 1: Tu Cuenta", "Crea el usuario principal del sistema")
        
        frame = tk.Frame(self.root, bg=BG_COLOR)
        frame.pack(pady=40)
        
        tk.Label(frame, text="Nombre de Usuario:", bg=BG_COLOR, fg="white", font=("Sans", 12)).grid(row=0, column=0, pady=10, padx=10, sticky="e")
        self.entry_user = tk.Entry(frame, font=("Sans", 12), width=25); self.entry_user.grid(row=0, column=1, pady=10, padx=10)
        self.entry_user.insert(0, "astro")
        
        tk.Label(frame, text="Contraseña:", bg=BG_COLOR, fg="white", font=("Sans", 12)).grid(row=1, column=0, pady=10, padx=10, sticky="e")
        self.entry_pass = tk.Entry(frame, show="*", font=("Sans", 12), width=25); self.entry_pass.grid(row=1, column=1, pady=10, padx=10)
        
        self.next_button(command=self.show_step_2)

    # --- PASO 2: SCAN WIFI ---
    def show_step_2(self):
        self.clear_window()
        self.header("Paso 2: Red WiFi", "Selecciona tu red inalámbrica")
        
        tk.Label(self.root, text="Buscando redes cercanas...", bg=BG_COLOR, fg=FG_COLOR).pack(pady=5)
        
        self.listbox = tk.Listbox(self.root, font=("Sans", 12), width=50, height=10, 
                                 bg=BUTTON_COLOR, fg="white", selectbackground=ACCENT_COLOR)
        self.listbox.pack(pady=10)
        
        btn_frame = tk.Frame(self.root, bg=BG_COLOR)
        btn_frame.pack(pady=5)
        
        tk.Button(btn_frame, text="🔄 REESCANEAR", command=self.scan_wifi, bg=BUTTON_COLOR, fg="white").pack(side="left", padx=10)
        tk.Button(btn_frame, text="🔧 CONFIGURACIÓN MANUAL", command=self.show_manual_wifi, bg=BUTTON_COLOR, fg="yellow").pack(side="left", padx=10)
        
        self.scan_wifi()
        self.next_button(command=self.show_step_3)

    def show_manual_wifi(self):
        self.selected_ssid = ""
        self.show_step_3(manual=True)

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

    # --- PASO 3: CONFIG WIFI ---
    def show_step_3(self, manual=False):
        if not manual:
            idx = self.listbox.curselection()
            self.selected_ssid = self.wifi_list[idx[0]] if idx else ""
        
        self.clear_window()
        self.header("Configuración de Red", "Introduce los datos de conexión")
        
        frame = tk.Frame(self.root, bg=BG_COLOR)
        frame.pack(pady=20)
        
        # SSID Row
        tk.Label(frame, text="Nombre WiFi (SSID):", bg=BG_COLOR, fg="white", font=("Sans", 12)).grid(row=0, column=0, pady=10, padx=10, sticky="e")
        self.entry_ssid = tk.Entry(frame, font=("Sans", 12), width=30)
        self.entry_ssid.grid(row=0, column=1, pady=10, padx=10)
        if self.selected_ssid:
            self.entry_ssid.insert(0, self.selected_ssid)
            self.entry_ssid.config(state="readonly")
        
        # Password Row
        tk.Label(frame, text="Contraseña WiFi:", bg=BG_COLOR, fg="white", font=("Sans", 12)).grid(row=1, column=0, pady=10, padx=10, sticky="e")
        self.wifi_pass = tk.Entry(frame, show="*", font=("Sans", 12), width=30)
        self.wifi_pass.grid(row=1, column=1, pady=10, padx=10)
        
        tk.Checkbutton(frame, text="Configuración IP Avanzada (Estática)", variable=self.static_ip_var,
                       bg=BG_COLOR, fg="yellow", selectcolor=BG_COLOR, command=self.toggle_static_fields).grid(row=2, columnspan=2, pady=20)
        
        self.static_frame = tk.Frame(frame, bg=BG_COLOR)
        self.static_frame.grid(row=3, columnspan=2)
        
        tk.Label(self.static_frame, text="IP Estática:", bg=BG_COLOR, fg=FG_COLOR).grid(row=0, column=0, padx=5, pady=2)
        self.entry_ip = tk.Entry(self.static_frame, width=20); self.entry_ip.grid(row=0, column=1, padx=5, pady=2)
        self.entry_ip.insert(0, "192.168.1.100")
        
        tk.Label(self.static_frame, text="Puerta Enlace:", bg=BG_COLOR, fg=FG_COLOR).grid(row=1, column=0, padx=5, pady=2)
        self.entry_gw = tk.Entry(self.static_frame, width=20); self.entry_gw.grid(row=1, column=1, padx=5, pady=2)
        self.entry_gw.insert(0, "192.168.1.1")
        
        tk.Label(self.static_frame, text="DNS:", bg=BG_COLOR, fg=FG_COLOR).grid(row=2, column=0, padx=5, pady=2)
        self.entry_dns = tk.Entry(self.static_frame, width=20); self.entry_dns.grid(row=2, column=1, padx=5, pady=2)
        self.entry_dns.insert(0, "8.8.8.8")
        
        self.toggle_static_fields()
        self.next_button("GUARDAR Y FINALIZAR", command=self.finish_setup)

    def toggle_static_fields(self):
        state = "normal" if self.static_ip_var.get() else "disabled"
        for child in self.static_frame.winfo_children():
            child.configure(state=state)

    # --- FINALIZATION ---
    def finish_setup(self):
        user = self.entry_user.get()
        pwd = self.entry_pass.get()
        ssid = self.entry_ssid.get()
        
        if not user or not pwd:
            messagebox.showerror("Error", "El usuario y contraseña son obligatorios.")
            return

        # 1. Crear usuario
        subprocess.call(f"sudo useradd -m -s /bin/bash -G sudo,dialout,video,input,plugdev,netdev {user}", shell=True)
        subprocess.call(f"echo '{user}:{pwd}' | sudo chpasswd", shell=True)
        
        # 2. Configurar Autologin
        subprocess.call(f"echo '[Seat:*]\nautologin-user={user}\nautologin-session=xfce\n' | sudo tee /etc/lightdm/lightdm.conf.d/50-astro.conf", shell=True)
        subprocess.call("sudo rm -f /etc/lightdm/lightdm.conf.d/50-setup.conf", shell=True)
        
        # 3. Configurar WiFi e IP si hay SSID
        if ssid:
            wpwd = self.wifi_pass.get()
            base_cmd = f"sudo nmcli dev wifi connect '{ssid}' password '{wpwd}'"
            if self.static_ip_var.get():
                ip, gw, dns = self.entry_ip.get(), self.entry_gw.get(), self.entry_dns.get()
                subprocess.call(f"{base_cmd} ipv4.method manual ipv4.addresses {ip}/24 ipv4.gateway {gw} ipv4.dns {dns}", shell=True)
            else:
                subprocess.call(base_cmd, shell=True)
                
        # 4. Heredar config y wallpaper
        user_home = f"/home/{user}"
        subprocess.call(f"sudo mkdir -p {user_home}/.config/autostart", shell=True)
        subprocess.call(f"sudo cp /etc/xdg/autostart/astro-wizard.desktop {user_home}/.config/autostart/", shell=True)
        subprocess.call(f"sudo mkdir -p {user_home}/.config/xfce4/xfconf/xfce-perchannel-xml", shell=True)
        subprocess.call(f"sudo cp -r /home/astro-setup/.config/xfce4/xfconf/xfce-perchannel-xml/* {user_home}/.config/xfce4/xfconf/xfce-perchannel-xml/", shell=True)
        subprocess.call(f"sudo chown -R {user}:{user} {user_home}", shell=True)
        
        subprocess.call("sudo touch /etc/astro-configured", shell=True)
        messagebox.showinfo("AstroOrange V2", "Fase 1 completada. El sistema se reiniciará.")
        subprocess.call("sudo reboot", shell=True)

    # --- ETAPA 2: INSTALADOR ---
    def show_stage_2(self):
        self.clear_window()
        self.header("Etapa 2: Instalador de Software", "Personaliza tu estación astronómica")
        
        frame = tk.Frame(self.root, bg=BG_COLOR); frame.pack(pady=10)
        self.vars = {
            "KStars / INDI": tk.BooleanVar(value=True),
            "PHD2 Guiding": tk.BooleanVar(value=True),
            "ASTAP (Plate Solver)": tk.BooleanVar(value=True),
            "Stellarium": tk.BooleanVar(value=False),
            "AstroDMX Capture": tk.BooleanVar(value=False),
            "CCDciel": tk.BooleanVar(value=False),
            "Syncthing": tk.BooleanVar(value=False)
        }
        
        for i, (name, var) in enumerate(self.vars.items()):
            tk.Checkbutton(frame, text=name, variable=var, bg=BG_COLOR, fg="white", 
                           selectcolor=BG_COLOR, font=("Sans", 11)).grid(row=i//2, column=i%2, sticky="w", padx=20, pady=5)

        tk.Button(self.root, text="🚀 INICIAR INSTALACIÓN", command=self.start_install, 
                  bg=ACCENT_COLOR, fg=BG_COLOR, font=("Sans", 14, "bold"), width=30).pack(pady=20)

    def start_install(self):
        install_win = tk.Toplevel(self.root)
        install_win.title("Instalando Software Astronómico")
        install_win.geometry("900x700")
        install_win.configure(bg=BG_COLOR)
        carousel = ImageCarousel(install_win)
        threading.Thread(target=self.run_install, args=(install_win,)).start()

    def run_install(self, install_win):
        cmds = ["export DEBIAN_FRONTEND=noninteractive", "sudo apt-get update"]
        # (Lógica de instalación simplificada por espacio)
        if self.vars["KStars / INDI"].get(): cmds.append("sudo add-apt-repository -y ppa:mutlaqja/ppa && sudo apt-get install -y kstars-bleeding indi-full gsc")
        if self.vars["PHD2 Guiding"].get(): cmds.append("sudo add-apt-repository -y ppa:pch/phd2 && sudo apt-get install -y phd2")
        if self.vars["ASTAP (Plate Solver)"].get(): cmds.append("wget https://www.hnsky.org/astap_arm64.deb -O /tmp/astap.deb && sudo apt-get install -y /tmp/astap.deb")
        
        full_command = " && ".join(cmds)
        subprocess.call(["xfce4-terminal", "--maximize", "-e", f"bash -c '{full_command}; echo Finalizado; read'"])
        subprocess.call("rm -f ~/.config/autostart/astro-wizard.desktop", shell=True)
        install_win.destroy()
        messagebox.showinfo("Finalizado", "Software instalado.")
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk(); app = WizardApp(root); root.mainloop()
