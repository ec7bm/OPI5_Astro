#!/bin/bash
# AstroOrange - Headless VNC Server
# Provides remote desktop access via browser

export DISPLAY=:0
rm -f /tmp/.X0-lock

# 1. ¿Hay monitor físico?
if ! xset -display :0 q &>/dev/null; then
    echo "Headless mode detected. Starting virtual display..."
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
echo "Starting VNC and noVNC..."
x11vnc -display :0 -forever -rfbauth ~/.vnc/passwd -shared -bg -xkb -noxrecord -noxfixes -noxdamage &
/usr/share/novnc/utils/launch.sh --vnc localhost:5900 --listen 6080
