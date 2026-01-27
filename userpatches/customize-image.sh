#!/bin/bash
# AstroOrange Customization Script - SAFE Headless + Hotspot + noVNC

set -e
export DEBIAN_FRONTEND=noninteractive

echo "🚀 AstroOrange customization starting..."

# ---------------- BASE PACKAGES ----------------
apt-get update
apt-get install -y --no-install-recommends \
    xfce4 xfce4-terminal xfce4-screenshooter \
    x11vnc xvfb novnc websockify \
    network-manager \
    git curl wget xterm xz-utils \
    python3 python3-pip python3-tk \
    firefox-esr \
    dbus-x11

apt-get clean
rm -rf /var/lib/apt/lists/*

# ---------------- RESTORE WALLPAPER (Integration) ----------------
# Si hemos inyectado assets en /tmp/assets, los copiamos
if [ -d "/tmp/assets/backgrounds" ]; then
    echo "🌌 Installing AstroOrange Wallpaper..."
    mkdir -p /usr/share/backgrounds
    cp /tmp/assets/backgrounds/* /usr/share/backgrounds/ || true
fi

# ---------------- VIRTUAL DESKTOP SCRIPT ----------------
cat <<'EOF' > /usr/local/bin/astro-vnc.sh
#!/bin/bash
export DISPLAY=:0

rm -f /tmp/.X0-lock

Xvfb :0 -screen 0 1920x1080x24 &
sleep 3

# Si existe el wallpaper, lo configuramos (best effort con xsetroot o similar si fuera wm simple, 
# pero XFCE maneja el fondo independientemente. Esto es solo inicializacion)

x11vnc -display :0 -forever -nopw -shared -xkb &
sleep 2

/usr/share/novnc/utils/launch.sh --vnc localhost:5900 --listen 6080
EOF

chmod +x /usr/local/bin/astro-vnc.sh

# ---------------- SYSTEMD SERVICE (VNC) ----------------
cat <<EOF > /etc/systemd/system/astro-vnc.service
[Unit]
Description=AstroOrange Headless Desktop (XFCE + noVNC)
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/astro-vnc.sh
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# ---------------- HOTSPOT SCRIPT ----------------
cat <<'EOF' > /usr/local/bin/astro-network.sh
#!/bin/bash

IFACE="wlan0"
SSID="AstroOrange"
PASS="astroorange"

sleep 15

if ! nmcli -t -f DEVICE,STATE dev | grep -q "^${IFACE}:connected"; then
    echo "📡 No WiFi detected, starting hotspot..."

    nmcli device set "$IFACE" managed yes
    nmcli con delete AstroHotspot 2>/dev/null || true

    nmcli con add type wifi ifname "$IFACE" con-name AstroHotspot \
        ssid "$SSID" mode ap ipv4.method shared

    nmcli con modify AstroHotspot \
        wifi-sec.key-mgmt wpa-psk \
        wifi-sec.psk "$PASS"

    nmcli con up AstroHotspot
fi
EOF

chmod +x /usr/local/bin/astro-network.sh

# ---------------- NETWORK SERVICE ----------------
cat <<EOF > /etc/systemd/system/astro-network.service
[Unit]
Description=AstroOrange Network Auto-Hotspot
After=NetworkManager.service
Wants=NetworkManager.service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/astro-network.sh

[Install]
WantedBy=multi-user.target
EOF

# ---------------- WIZARD ----------------
mkdir -p /opt/astro-wizard

cat <<'EOF' > /opt/astro-wizard/wizard.py
import tkinter as tk
from tkinter import messagebox
import os

def install_stack():
    # Aquí es donde irá la lógica real de los scripts V1 si el usuario quiere
    # Por ahora es un placeholder visual
    os.system("xfce4-terminal -e 'bash -c \"echo Installing KStars + INDI...; sleep 5; echo Done; read\"'")
    messagebox.showinfo("AstroOrange", "Installation finished. System ready.")

root = tk.Tk()
root.title("AstroOrange Wizard")
root.geometry("800x600")

# Intentar poner fondo bonito si existe
try:
    bg_image = tk.PhotoImage(file="/usr/share/backgrounds/astro-wallpaper.jpg")
    background_label = tk.Label(root, image=bg_image)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)
    
    # Estilo oscuro para el texto si hay fondo
    bg_color = "#1a1b26"
    fg_color = "white"
except:
    bg_color = "SystemButtonFace"
    fg_color = "black"

tk.Label(root, text="AstroOrange Pro V2", font=("Arial", 24, "bold"), bg=bg_color, fg=fg_color).pack(pady=40)

frame = tk.Frame(root, bg=bg_color)
frame.pack(pady=20)

tk.Button(frame, text="📡 Configure WiFi", command=lambda: os.system("xfce4-terminal -e nmtui"), height=2, width=30, bg="#f7768e", fg="black").pack(pady=10)
tk.Button(frame, text="🔭 Install Astronomy Stack", command=install_stack, height=2, width=30, bg="#7aa2f7", fg="black").pack(pady=10)

root.mainloop()
EOF

# ---------------- AUTOSTART (GLOBAL) ----------------
mkdir -p /etc/xdg/autostart
cat <<EOF > /etc/xdg/autostart/astro-wizard.desktop
[Desktop Entry]
Type=Application
Name=AstroOrange Wizard
Exec=python3 /opt/astro-wizard/wizard.py
OnlyShowIn=XFCE;
EOF

# ---------------- ENABLE SERVICES ----------------
systemctl enable astro-vnc.service
systemctl enable astro-network.service
systemctl enable NetworkManager

echo "✅ AstroOrange customization complete."
