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

# Repositorios (Mozilla PPA para Firefox)
apt-get update
apt-get install -y --no-install-recommends software-properties-common
add-apt-repository -y ppa:mozillateam/ppa
echo '
Package: *
Pin: release o=LP-PPA-mozillateam
Pin-Priority: 1001
' > /etc/apt/preferences.d/mozilla-firefox
apt-get update

# Paquetes esencialmente LIGEROS
apt-get install -y --no-install-recommends \
    xfce4 xfce4-goodies lightdm lightdm-gtk-greeter \
    network-manager network-manager-gnome \
    openssh-server \
    xserver-xorg-video-dummy \
    x11vnc xvfb novnc websockify \
    python3 python3-pip python3-tk \
    curl wget git nano htop \
    firefox \
    dbus-x11 \
    feh \
    onboard

# ==================== 2. USUARIO SETUP (TEMPORAL) ====================
echo -e "${GREEN}[2/5] Creating Setup User...${NC}"
SETUP_USER="astro-setup"
SETUP_PASS="setup"

if ! id "$SETUP_USER" &>/dev/null; then
    useradd -m -s /bin/bash -G sudo,dialout,video "$SETUP_USER"
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

# Copiar wallpaper si existe
if [ -d "/tmp/assets/backgrounds" ]; then
    mkdir -p /usr/share/backgrounds
    cp /tmp/assets/backgrounds/* /usr/share/backgrounds/ || true
fi

# --- A. Script de Red (Rescue Hotspot) ---
cat <<'EOF' > "$OPT_DIR/bin/astro-network.sh"
#!/bin/bash
IFACE="wlan0"
SSID="AstroOrange-Setup"
PASS="astrosetup"
sleep 10
if nmcli -t -f STATE g | grep -q connected; then
    exit 0
fi
nmcli con delete "$SSID" 2>/dev/null || true
nmcli con add type wifi ifname "$IFACE" con-name "$SSID" autoconnect yes ssid "$SSID" mode ap ipv4.method shared
nmcli con modify "$SSID" wifi-sec.key-mgmt wpa-psk wifi-sec.psk "$PASS"
nmcli con up "$SSID"
EOF
chmod +x "$OPT_DIR/bin/astro-network.sh"

# --- B. Script VNC ---
cat <<'EOF' > "$OPT_DIR/bin/astro-vnc.sh"
#!/bin/bash
export DISPLAY=:0
rm -f /tmp/.X0-lock
Xvfb :0 -screen 0 1920x1080x24 &
sleep 2
x11vnc -display :0 -forever -nopw -shared -bg -xkb &
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
        self.root.title("AstroOrange Wizard")
        self.root.geometry("900x650")
        self.root.configure(bg=BG_COLOR)
        try:
            self.bg = tk.PhotoImage(file="/usr/share/backgrounds/astro-wallpaper.jpg")
            tk.Label(self.root, image=self.bg).place(x=0,y=0,relwidth=1,relheight=1)
        except: pass

    def header(self, text):
        tk.Label(self.root, text=text, font=("Sans", 24, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=30)

    def show_stage_1(self):
        self.header("Configuración Inicial")
        frame = tk.Frame(self.root, bg=BG_COLOR)
        frame.pack(pady=10)
        tk.Label(frame, text="Nuevo Usuario:", bg=BG_COLOR, fg="white").grid(row=0,0,pady=5)
        self.entry_user = tk.Entry(frame); self.entry_user.grid(row=0,1,pady=5)
        tk.Label(frame, text="Contraseña:", bg=BG_COLOR, fg="white").grid(row=1,0,pady=5)
        self.entry_pass = tk.Entry(frame, show="*"); self.entry_pass.grid(row=1,1,pady=5)
        tk.Button(self.root, text="📡 Configurar WiFi", command=lambda: subprocess.Popen(["xfce4-terminal", "-e", "nmtui"]), bg="#475569", fg="white", width=20).pack(pady=20)
        tk.Button(self.root, text="Aplicar y Reiniciar 🚀", command=self.apply_stage_1, bg=ACCENT_COLOR, fg="black", font=("Sans", 14, "bold"), width=25).pack(pady=10)

    def apply_stage_1(self):
        user, pwd = self.entry_user.get(), self.entry_pass.get()
        if not user or not pwd:
            messagebox.showerror("Error", "Completa los datos.")
            return
        subprocess.call(f"sudo bash -c \"useradd -m -s /bin/bash -G sudo,dialout,video {user} && echo '{user}:{pwd}' | chpasswd\"", shell=True)
        subprocess.call(f"echo '[Seat:*]\nautologin-user={user}\nautologin-session=xfce\n' | sudo tee /etc/lightdm/lightdm.conf.d/50-astro.conf", shell=True)
        subprocess.call("sudo rm /etc/lightdm/lightdm.conf.d/50-setup.conf", shell=True)
        subprocess.call(f"sudo sed -i 's/User=astro-setup/User={user}/g' /etc/systemd/system/astro-vnc.service", shell=True)
        subprocess.call(f"sudo mkdir -p /home/{user}/.config/autostart", shell=True)
        subprocess.call(f"sudo cp /etc/xdg/autostart/astro-wizard.desktop /home/{user}/.config/autostart/", shell=True)
        subprocess.call(f"sudo chown -R {user}:{user} /home/{user}/.config", shell=True)
        subprocess.call("sudo touch /etc/astro-configured", shell=True)
        messagebox.showinfo("OK", "Reiniciando...")
        subprocess.call("sudo reboot", shell=True)

    def show_stage_2(self):
        self.header("Instalador de Software")
        self.vars = {"kstars": tk.BooleanVar(value=True), "phd2": tk.BooleanVar(value=True), "syncthing": tk.BooleanVar(value=False)}
        frame = tk.Frame(self.root, bg=BG_COLOR); frame.pack(pady=20)
        for name, var in self.vars.items():
            tk.Checkbutton(frame, text=name.upper(), variable=var, bg=BG_COLOR, fg="white", selectcolor="#0f172a").pack(anchor="w")
        tk.Button(self.root, text="Instalar", command=self.start_install, bg=ACCENT_COLOR, fg="black").pack(pady=30)

    def start_install(self): threading.Thread(target=self.run_install).start()
    def run_install(self):
        cmds = ["sudo apt-get update"]
        if self.vars["kstars"].get(): cmds.append("sudo add-apt-repository -y ppa:mutlaqja/ppa && sudo apt-get install -y kstars-bleeding indi-full")
        if self.vars["phd2"].get(): cmds.append("sudo add-apt-repository -y ppa:pch/phd2 && sudo apt-get install -y phd2")
        if self.vars["syncthing"].get(): cmds.append("sudo apt-get install -y syncthing")
        subprocess.call(["xfce4-terminal", "-e", f"bash -c '{' && '.join(cmds)}; echo Fin; read'"])
        subprocess.call("rm ~/.config/autostart/astro-wizard.desktop", shell=True)
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
