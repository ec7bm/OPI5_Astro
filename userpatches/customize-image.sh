#!/bin/bash
# AstroOrange Customization Script - Headless & Auto-Hotspot

export DEBIAN_FRONTEND=noninteractive

# 1. INSTALACIÓN DE DEPENDENCIAS (Base, Gráficos y Red)
apt-get update
apt-get install -y --no-install-recommends \
    xfce4 xfce4-terminal xfce4-screenshooter \
    x11vnc xvfb novnc python3-pip python3-tk \
    network-manager nm-tray \
    git build-essential xterm xz-utils \
    curl wget firefox-esr \
    dbus-x11

# 2. CONFIGURACIÓN DEL SERVICIO VIRTUAL DISPLAY (Xvfb + X11VNC)
# Creamos el servicio que emula el monitor
cat <<EOF > /etc/systemd/system/vnc-desktop.service
[Unit]
Description=Virtual Desktop for Headless Operation (noVNC)
After=network.target

[Service]
Type=simple
Environment=DISPLAY=:0
ExecStartPre=-/usr/bin/rm /tmp/.X0-lock
ExecStart=/usr/bin/bash -c "/usr/bin/Xvfb :0 -screen 0 1920x1080x24 & sleep 2; /usr/bin/x11vnc -display :0 -forever -nopw -bg -xkb; /usr/share/novnc/utils/launch.sh --vnc localhost:5900 --listen 6080"
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 3. LÓGICA DE RED: HOTSPOT AUTOMÁTICO
# Script que verifica WiFi y levanta AP si falla
cat <<'EOF' > /usr/local/bin/astro-network.sh
#!/bin/bash
IFACE="wlan0"
SSID="AstroOrange"
PASS="astroorange"

sleep 10
if ! nmcli -t -f DEVICE,STATE dev | grep -q "^${IFACE}:connected"; then
    echo "No WiFi connection. Starting Hotspot..."
    nmcli con delete Hotspot 2>/dev/null
    nmcli con add type wifi ifname "$IFACE" con-name Hotspot autoconnect yes ssid "$SSID" mode ap ipv4.method shared
    nmcli con modify Hotspot wifi-sec.key-mgmt wpa-psk wifi-sec.psk "$PASS"
    nmcli con up Hotspot
fi
EOF
chmod +x /usr/local/bin/astro-network.sh

# 4. SCRIPT DEL WIZARD (Python + Tkinter para GUI)
mkdir -p /opt/astro-wizard
cat <<'EOF' > /opt/astro-wizard/wizard.py
import tkinter as tk
from tkinter import messagebox
import os

def install_software():
    # Aquí iría tu lógica de instalación real
    os.system("xfce4-terminal -e 'bash -c \"echo Instalando INDI y KStars...; sleep 5; echo Hecho!; read\"'")
    messagebox.showinfo("Éxito", "Instalación completada. Reinicia para aplicar cambios.")

root = tk.Tk()
root.title("AstroOrange Pro Wizard")
root.geometry("500x400")
try:
    # Intentar cargar fondo si existe
    bg_image = tk.PhotoImage(file="/usr/share/backgrounds/astro-wallpaper.jpg")
    background_label = tk.Label(root, image=bg_image)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)
except:
    pass

tk.Label(root, text="Bienvenido a AstroOrange", font=("Arial", 16), bg="#1a1b26", fg="white").pack(pady=20)
tk.Button(root, text="Instalar Stack Astronómico", command=install_software, height=2, width=30).pack(pady=10)
tk.Button(root, text="Configurar WiFi (nmtui)", command=lambda: os.system("xfce4-terminal -e nmtui"), height=2, width=30).pack(pady=10)
root.mainloop()
EOF

# 5. AUTOSTART DEL WIZARD EN XFCE
mkdir -p /etc/skel/.config/autostart
cat <<EOF > /etc/skel/.config/autostart/wizard.desktop
[Desktop Entry]
Type=Application
Name=AstroWizard
Exec=python3 /opt/astro-wizard/wizard.py
OnlyShowIn=XFCE;
EOF

# 6. HABILITAR SERVICIOS
systemctl enable vnc-desktop.service
# Agregamos el script de red al arranque mediante un servicio simple
cat <<EOF > /etc/systemd/system/astro-net.service
[Unit]
After=NetworkManager.service
[Service]
ExecStart=/usr/local/bin/astro-network.sh
[Install]
WantedBy=multi-user.target
EOF
systemctl enable astro-net.service

# Limpieza final
apt-get autoremove -y
