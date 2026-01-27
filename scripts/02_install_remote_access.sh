#!/bin/bash
# 02_install_remote_access.sh - AstroOrange Pro
set -e
TARGET_USER="AstroOrange"
HOME_DIR="/home/${TARGET_USER}"
GEOMETRY="1920x1080"

if [ "$EUID" -eq 0 ]; then
  echo "❌ ERROR: No ejecutes como root."
  exit 1
fi

echo "=== Instalando VNC y noVNC ==="
sudo apt update
sudo apt install -y tightvncserver novnc python3-websockify python3-numpy dbus-x11
vncpasswd
mkdir -p ${HOME_DIR}/.vnc
cat << EOF > ${HOME_DIR}/.vnc/xstartup
#!/bin/sh
unset SESSION_MANAGER
unset DBUS_SESSION_BUS_ADDRESS
startxfce4 &
EOF
chmod +x ${HOME_DIR}/.vnc/xstartup
openssl req -x509 -nodes -newkey rsa:2048 -keyout ${HOME_DIR}/novnc.pem -out ${HOME_DIR}/novnc.pem -days 365 -subj "/CN=astroorange"

sudo bash -c "cat << EOF > /etc/systemd/system/vncserver@.service
[Unit]
Description=Start TightVNC server
After=network.target
[Service]
Type=forking
User=${TARGET_USER}
Group=${TARGET_USER}
WorkingDirectory=${HOME_DIR}
ExecStart=/usr/bin/vncserver -geometry ${GEOMETRY} -depth 24 :%i
ExecStop=/usr/bin/vncserver -kill :%i
[Install]
WantedBy=multi-user.target
EOF"

sudo bash -c "cat << EOF > /etc/systemd/system/novnc.service
[Unit]
Description=noVNC Service
After=network.target
[Service]
Type=simple
User=${TARGET_USER}
ExecStart=/usr/share/novnc/utils/novnc_proxy --vnc localhost:5901 --listen 6080 --cert ${HOME_DIR}/novnc.pem
Restart=on-failure
[Install]
WantedBy=multi-user.target
EOF"

sudo systemctl daemon-reload
sudo systemctl enable vncserver@1.service novnc.service
sudo systemctl restart vncserver@1.service novnc.service
echo "Acceso web: https://<IP>:6080/vnc.html"
