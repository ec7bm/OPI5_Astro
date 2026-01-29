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
                    # Resize to fit nicely in the wizard (800x450)
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
            self.label.after(5000, self.animate)  # Change every 5 seconds

class WizardApp:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        if not os.path.exists("/etc/astro-configured"):
            self.show_stage_1()
        else:
            self.show_stage_2()

    def setup_window(self):
        self.root.title("AstroOrange V2 - Wizard")
        self.root.geometry("900x700")
        self.root.configure(bg=BG_COLOR)
        self.root.attributes("-topmost", True)
        # Intentar cargar fondo astronomico
        try:
            self.bg = tk.PhotoImage(file="/usr/share/backgrounds/astro-wallpaper.jpg")
            tk.Label(self.root, image=self.bg).place(x=0,y=0,relwidth=1,relheight=1)
        except: 
            try:
                self.bg = tk.PhotoImage(file="/opt/astroorange/assets/background.png")
                tk.Label(self.root, image=self.bg).place(x=0,y=0,relwidth=1,relheight=1)
            except: pass

    def header(self, text):
        # Header con logo si existe
        try:
            self.logo = tk.PhotoImage(file="/opt/astroorange/assets/logo.png").subsample(2,2)
            tk.Label(self.root, image=self.logo, bg=BG_COLOR).pack(pady=10)
        except: pass
        tk.Label(self.root, text=text, font=("Sans", 22, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=10)

    def show_stage_1(self):
        self.header("Etapa 1: Usuario y WiFi")
        frame = tk.Frame(self.root, bg=BG_COLOR)
        frame.pack(pady=10)
        tk.Label(frame, text="Usuario:", bg=BG_COLOR, fg="white", font=("Sans", 12)).grid(row=0, column=0, pady=10, padx=10)
        self.entry_user = tk.Entry(frame, font=("Sans", 12)); self.entry_user.grid(row=0, column=1, pady=10, padx=10)
        tk.Label(frame, text="Password:", bg=BG_COLOR, fg="white", font=("Sans", 12)).grid(row=1, column=0, pady=10, padx=10)
        self.entry_pass = tk.Entry(frame, show="*", font=("Sans", 12)); self.entry_pass.grid(row=1, column=1, pady=10, padx=10)
        
        tk.Button(self.root, text="Configurar WiFi (nmtui)", font=("Sans", 14), 
                  bg=BUTTON_COLOR, fg="white", command=self.run_nmtui).pack(pady=10)
        
        tk.Button(self.root, text="GUARDAR Y REINICIAR", font=("Sans", 16, "bold"), 
                  bg=ACCENT_COLOR, fg=BG_COLOR, command=self.save_and_reboot).pack(pady=40)

    def run_nmtui(self):
        subprocess.Popen(["xfce4-terminal", "-e", "nmtui"])

    def save_and_reboot(self):
        user, pwd = self.entry_user.get(), self.entry_pass.get()
        if not user or not pwd:
            messagebox.showerror("Error", "Rellena todos los campos.")
            return
        # Creacion de usuario real con grupos necesarios incluyendo 'input'
        subprocess.call(f"sudo bash -c \"useradd -m -s /bin/bash -G sudo,dialout,video,input,plugdev,netdev {user} && echo '{user}:{pwd}' | chpasswd\"", shell=True)
        # Configurar autologin para el nuevo usuario
        subprocess.call(f"echo '[Seat:*]\nautologin-user={user}\nautologin-session=xfce\n' | sudo tee /etc/lightdm/lightdm.conf.d/50-astro.conf", shell=True)
        subprocess.call("sudo rm -f /etc/lightdm/lightdm.conf.d/50-setup.conf", shell=True)
        # Actualizar servicio VNC para que corra como el nuevo usuario
        subprocess.call(f"sudo sed -i 's/User=astro-setup/User={user}/g' /etc/systemd/system/astro-vnc.service", shell=True)
        # Asegurar que el wizard salte para el nuevo usuario
        subprocess.call(f"sudo mkdir -p /home/{user}/.config/autostart", shell=True)
        subprocess.call(f"sudo cp /etc/xdg/autostart/astro-wizard.desktop /home/{user}/.config/autostart/", shell=True)
        subprocess.call(f"sudo chown -R {user}:{user} /home/{user}/.config", shell=True)
        # Marcar etapa 1 como completada
        subprocess.call("sudo touch /etc/astro-configured", shell=True)
        messagebox.showinfo("OK", "Usuario creado. El sistema se reiniciará.")
        subprocess.call("sudo reboot", shell=True)

    def show_stage_2(self):
        self.header("Etapa 2: Instalador de Software")
        tk.Label(self.root, text="Selecciona el software astronómico a instalar:", bg=BG_COLOR, fg="white").pack()
        
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
        
        # Grid para las checkboxes
        for i, (name, var) in enumerate(self.vars.items()):
            tk.Checkbutton(frame, text=name, variable=var, bg=BG_COLOR, fg="white", 
                           selectcolor="#0f172a", font=("Sans", 11)).grid(row=i//2, column=i%2, sticky="w", padx=20, pady=5)

        tk.Button(self.root, text="🚀 Iniciar Instalación", command=self.start_install, 
                  bg=ACCENT_COLOR, fg="black", font=("Sans", 14, "bold"), width=25).pack(pady=20)

    def start_install(self):
        if messagebox.askyesno("Confirmar", "¿Deseas instalar el software seleccionado?"):
            # Create installation window with carousel
            install_win = tk.Toplevel(self.root)
            install_win.title("Instalando Software Astronómico")
            install_win.geometry("900x700")
            install_win.configure(bg=BG_COLOR)
            
            tk.Label(install_win, text="Instalación en Progreso", 
                    font=("Sans", 18, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=10)
            
            # Carousel
            carousel = ImageCarousel(install_win)
            
            tk.Label(install_win, text="Mientras se instala el software, disfruta de estas imágenes del cosmos...", 
                    font=("Sans", 11), bg=BG_COLOR, fg=FG_COLOR).pack(pady=5)
            
            # Progress info
            self.install_label = tk.Label(install_win, text="Iniciando instalación...", 
                                         font=("Sans", 12), bg=BG_COLOR, fg="white")
            self.install_label.pack(pady=10)
            
            threading.Thread(target=self.run_install, args=(install_win,)).start()

    def run_install(self, install_win):
        cmds = ["export DEBIAN_FRONTEND=noninteractive", "sudo apt-get update"]
        
        if self.vars["KStars / INDI"].get():
            cmds.append("sudo add-apt-repository -y ppa:mutlaqja/ppa")
            cmds.append("sudo apt-get install -y kstars-bleeding indi-full gsc")
        if self.vars["PHD2 Guiding"].get():
            cmds.append("sudo add-apt-repository -y ppa:pch/phd2")
            cmds.append("sudo apt-get install -y phd2")
        if self.vars["ASTAP (Plate Solver)"].get():
            cmds.append("wget https://www.hnsky.org/astap_arm64.deb -O /tmp/astap.deb")
            cmds.append("sudo apt-get install -y /tmp/astap.deb")
        if self.vars["Stellarium"].get():
            cmds.append("sudo apt-get install -y stellarium")
        if self.vars["AstroDMX Capture"].get():
            cmds.append("wget https://www.astrodmx-astrophotography.org/downloads/astrodmx-capture/astrodmx_latest_arm64.deb -O /tmp/astrodmx.deb")
            cmds.append("sudo apt-get install -y /tmp/astrodmx.deb")
        if self.vars["CCDciel"].get():
            cmds.append("sudo apt-get install -y ccdciel")
        if self.vars["Syncthing"].get():
            cmds.append("sudo apt-get install -y syncthing")
        
        full_command = " && ".join(cmds)
        subprocess.call(["xfce4-terminal", "--title=Instalando Software", "--maximize", "-e", f"bash -c '{full_command}; echo; echo Instalación finalizada. Pulsa Enter para cerrar.; read'"])
        
        # Eliminar autostart para que no vuelva a salir
        subprocess.call("rm -f ~/.config/autostart/astro-wizard.desktop", shell=True)
        install_win.destroy()
        messagebox.showinfo("Finalizado", "Software instalado correctamente.")
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk(); app = WizardApp(root); root.mainloop()
