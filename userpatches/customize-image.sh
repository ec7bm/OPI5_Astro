#!/bin/bash
# AstroOrange Distro Builder - 2-Stage Workflow (STRICT)
# Stage 1: Temporary Setup User -> Stage 2: Real User & Install

set -e
export DEBIAN_FRONTEND=noninteractive

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== AstroOrange Distro Construction (2-Stage CLEAN) ===${NC}"

# ==================== 1. DEPENDENCIAS BASE ====================
echo -e "${GREEN}[1/5] Installing Base System...${NC}"

# Forzar modo no interactivo y manejar conflictos de configuracion automaticamente
export DEBIAN_FRONTEND=noninteractive
APT_OPTS="-y --no-install-recommends -o Dpkg::Options::=--force-confdef -o Dpkg::Options::=--force-confold"

# Repositorios (Mozilla PPA para Firefox)
apt-get update
apt-get install $APT_OPTS software-properties-common
add-apt-repository -y ppa:mozillateam/ppa
echo '
Package: *
Pin: release o=LP-PPA-mozillateam
Pin-Priority: 1001
' > /etc/apt/preferences.d/mozilla-firefox
apt-get update

# Paquetes esenciales (INCLUYENDO dnsmasq-base para Hotspot + Temas modernos)
apt-get install $APT_OPTS \
    xfce4 xfce4-goodies lightdm lightdm-gtk-greeter \
    network-manager network-manager-gnome dnsmasq-base \
    openssh-server \
    xserver-xorg-video-dummy \
    x11vnc xvfb novnc websockify \
    python3 python3-pip python3-tk \
    curl wget git nano htop \
    firefox \
    dbus-x11 \
    feh \
    onboard \
    arc-theme papirus-icon-theme

# Fix: Desactivar dnsmasq de sistema para que no choque con NetworkManager
systemctl stop dnsmasq || true
systemctl disable dnsmasq || true
systemctl mask dnsmasq

# ==================== 2. USUARIO SETUP (TEMPORAL) ====================
echo -e "${GREEN}[2/5] Creating Setup User...${NC}"
SETUP_USER="astro-setup"
SETUP_PASS="setup"

if ! id "$SETUP_USER" &>/dev/null; then
    useradd -m -s /bin/bash -G sudo,dialout,video,input "$SETUP_USER"
    echo "$SETUP_USER:$SETUP_PASS" | chpasswd
fi

# NOPASSWD para el wizard
echo "$SETUP_USER ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/astro-setup
chmod 0440 /etc/sudoers.d/astro-setup

# Configurar LightDM para autologin en SETUP
mkdir -p /etc/lightdm/lightdm.conf.d
cat <<EOF > /etc/lightdm/lightdm.conf.d/50-setup.conf
[Seat:*]
autologin-user=$SETUP_USER
autologin-session=xfce
EOF

# ==================== 3. MODULOS (/opt/astroorange) ====================
echo -e "${GREEN}[3/5] Installing Modules...${NC}"
OPT_DIR="/opt/astroorange"
mkdir -p "$OPT_DIR/bin" "$OPT_DIR/wizard" "$OPT_DIR/assets"

# --- 0. ASSETS (Wallpaper/Logo) ---
mkdir -p /usr/share/backgrounds
if [ -f "/tmp/userpatches/astro-wallpaper.jpg" ]; then
    cp "/tmp/userpatches/astro-wallpaper.jpg" "/usr/share/backgrounds/astro-wallpaper.jpg"
fi

# --- 0.1 XFCE Theme Configuration (Arc + Papirus) ---
# Configurar tema para el usuario setup (se heredará al usuario final)
SETUP_HOME="/home/$SETUP_USER"
mkdir -p "$SETUP_HOME/.config/xfce4/xfconf/xfce-perchannel-xml"

# Tema de ventanas Arc-Dark
cat <<'XFWM' > "$SETUP_HOME/.config/xfce4/xfconf/xfce-perchannel-xml/xfwm4.xml"
<?xml version="1.0" encoding="UTF-8"?>
<channel name="xfwm4" version="1.0">
  <property name="general" type="empty">
    <property name="theme" type="string" value="Arc-Dark"/>
  </property>
</channel>
XFWM

# Tema GTK y iconos
cat <<'XSETTINGS' > "$SETUP_HOME/.config/xfce4/xfconf/xfce-perchannel-xml/xsettings.xml"
<?xml version="1.0" encoding="UTF-8"?>
<channel name="xsettings" version="1.0">
  <property name="Net" type="empty">
    <property name="ThemeName" type="string" value="Arc-Dark"/>
    <property name="IconThemeName" type="string" value="Papirus-Dark"/>
  </property>
</channel>
XSETTINGS

# Fondo de pantalla
cat <<'XFDESKTOP' > "$SETUP_HOME/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml"
<?xml version="1.0" encoding="UTF-8"?>
<channel name="xfce4-desktop" version="1.0">
  <property name="backdrop" type="empty">
    <property name="screen0" type="empty">
      <property name="monitor0" type="empty">
        <property name="workspace0" type="empty">
          <property name="image-path" type="string" value="/usr/share/backgrounds/astro-wallpaper.jpg"/>
          <property name="image-style" type="int" value="5"/>
        </property>
      </property>
    </property>
  </property>
</channel>
XFDESKTOP

chown -R $SETUP_USER:$SETUP_USER "$SETUP_HOME/.config"

# --- A. Script de Red (Rescue Hotspot - VERIFICADO) ---
cat <<'EOF' > "$OPT_DIR/bin/astro-network.sh"
#!/bin/bash
# Detectar interfaz wifi dinamicamente
IFACE=$(nmcli -t -f DEVICE,TYPE device | grep wifi | cut -d: -f1 | head -n1)
[ -z "$IFACE" ] && IFACE="wlan0"

SSID="AstroOrange-Setup"
PASS="astrosetup"

echo "AstroOrange Network Manager - Checking connectivity..."
sleep 15

# Verificar si hay conexión a internet real (no solo "connected")
if ping -c 1 -W 2 8.8.8.8 >/dev/null 2>&1; then
    echo "Internet detected. Hotspot not needed."
    exit 0
fi

echo "No internet detected. Starting rescue hotspot..."

nmcli device set "$IFACE" managed yes
nmcli con delete "$SSID" 2>/dev/null || true
nmcli con add type wifi ifname "$IFACE" con-name "$SSID" autoconnect yes ssid "$SSID" mode ap ipv4.method shared

# Fix: Forzar seguridad WPA2 compatible (evita supplicant-timeout en OPi5 Pro)
nmcli con modify "$SSID" wifi-sec.key-mgmt wpa-psk wifi-sec.psk "$PASS"
nmcli con modify "$SSID" wifi-sec.proto rsn
nmcli con modify "$SSID" wifi-sec.group ccmp
nmcli con modify "$SSID" wifi-sec.pairwise ccmp
nmcli con up "$SSID"

echo "Hotspot '$SSID' is now active!"
EOF
chmod +x "$OPT_DIR/bin/astro-network.sh"

# --- B. Script VNC (Con Fix de Sesión - VERIFICADO) ---
cat <<'EOF' > "$OPT_DIR/bin/astro-vnc.sh"
#!/bin/bash
export DISPLAY=:0
rm -f /tmp/.X0-lock

# 1. ¿Hay monitor físico?
if ! xset -display :0 q &>/dev/null; then
    echo "Headless detectado. Iniciando pantalla virtual..."
    Xvfb :0 -screen 0 1920x1080x24 &
    sleep 3
    # FIX: Arrancar XFCE en la pantalla virtual si no hay monitor
    DISPLAY=:0 startxfce4 &
fi

# 1.5 FIX: Cambiar el cursor 'X' por defecto a una flecha
xsetroot -cursor_name left_ptr

# 2. VNC Password Fija
mkdir -p ~/.vnc
x11vnc -storepasswd "astroorange" ~/.vnc/passwd

# 3. Lanzar VNC y noVNC
x11vnc -display :0 -forever -rfbauth ~/.vnc/passwd -shared -bg -xkb -noxrecord -noxfixes -noxdamage &
/usr/share/novnc/utils/launch.sh --vnc localhost:5900 --listen 6080
EOF
chmod +x "$OPT_DIR/bin/astro-vnc.sh"

# ==================== 4. SYSTEMD SERVICES ====================
# Servicio Red
cat <<EOF > /etc/systemd/system/astro-network.service
[Unit]
Description=AstroOrange Rescue Hotspot
After=NetworkManager.service

[Service]
Type=oneshot
ExecStart=$OPT_DIR/bin/astro-network.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

# Servicio VNC (Inicia como el usuario de SETUP inicialmente)
cat <<EOF > /etc/systemd/system/astro-vnc.service
[Unit]
Description=AstroOrange Headless VNC
After=network.target

[Service]
Type=simple
User=$SETUP_USER
ExecStart=$OPT_DIR/bin/astro-vnc.sh
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl enable astro-network.service
systemctl enable astro-vnc.service
systemctl enable lightdm
systemctl enable ssh

# ==================== 5. EL WIZARD (Python) ====================
echo -e "${GREEN}[5/5] Installing Wizard...${NC}"

cat <<'PY_EOF' > "$OPT_DIR/wizard/main.py"
import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
import os
import threading

BG_COLOR = "#0f172a"
FG_COLOR = "#e2e8f0"
ACCENT_COLOR = "#38bdf8"

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
            threading.Thread(target=self.run_install).start()

    def run_install(self):
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
        messagebox.showinfo("Finalizado", "Software instalado correctamente.")
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk(); app = WizardApp(root); root.mainloop()
PY_EOF

# Autostart
mkdir -p /etc/xdg/autostart
cat <<EOF > /etc/xdg/autostart/astro-wizard.desktop
[Desktop Entry]
Type=Application
Name=AstroWizard
Exec=python3 $OPT_DIR/wizard/main.py
OnlyShowIn=XFCE;
EOF

echo -e "${GREEN}✅ Base Distro Ready! (CLEAN)${NC}"
