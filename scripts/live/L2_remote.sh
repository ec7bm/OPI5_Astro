#!/bin/bash
# L2_remote.sh - VNC y noVNC

set -e
echo "🖥️ Configurando acceso remoto..."

sudo apt-get install -y x11vnc xvfb novnc websockify

# Crear script de servicio
sudo mkdir -p /opt/astroorange/bin
cat <<'EOF' | sudo tee /opt/astroorange/bin/astro-vnc.sh
#!/bin/bash
export DISPLAY=:0
rm -f /tmp/.X0-lock

# 1. ¿Hay monitor físico?
if ! xset -display :0 q &>/dev/null; then
    echo "Headless detectado. Iniciando pantalla virtual..."
    Xvfb :0 -screen 0 1920x1080x24 &
    sleep 3
    # FORZAR ARRANQUE DE SESIÓN XFCE
    DISPLAY=:0 startxfce4 &
fi

# 2. Configurar password fija
mkdir -p ~/.vnc
x11vnc -storepasswd "astroorange" ~/.vnc/passwd

# 3. Lanzar con password 'astroorange'
x11vnc -display :0 -forever -rfbauth ~/.vnc/passwd -shared -bg -xkb -noxrecord -noxfixes -noxdamage &
/usr/share/novnc/utils/launch.sh --vnc localhost:5900 --listen 6080
EOF
sudo chmod +x /opt/astroorange/bin/astro-vnc.sh

# Crear servicio
USER_ACTUAL=$(whoami)
cat <<EOF | sudo tee /etc/systemd/system/astro-vnc.service
[Unit]
Description=AstroOrange Headless VNC
After=network.target

[Service]
Type=simple
User=$USER_ACTUAL
ExecStart=/opt/astroorange/bin/astro-vnc.sh
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable astro-vnc.service
sudo systemctl start astro-vnc.service

echo "✅ Acceso remoto listo. Prueba en el navegador: http://$(hostname -I | awk '{print $1}'):6080/vnc.html"
