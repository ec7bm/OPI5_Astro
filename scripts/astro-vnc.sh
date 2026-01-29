#!/bin/bash
# AstroOrange - Headless VNC Server (DYNAMIC SESSION SYNC)
# Provides remote desktop access for the current logged-in user

export DISPLAY=:0
rm -f /tmp/.X0-lock

# 1. Esperar a que el servidor X esté listo (max 60s)
echo "Waiting for X server on :0..."
for i in {1..60}; do
    if xset -display :0 q &>/dev/null; then
        echo "X server detected!"
        break
    fi
    sleep 1
done

# 2. Detectar usuario activo y su .Xauthority
# Buscamos quién es el dueño del proceso Xorg
X_USER=$(ps aux | grep Xorg | grep -v grep | awk '{print $1}' | head -n 1)
[ -z "$X_USER" ] && X_USER="astro-setup" # Fallback

echo "Active user detected: $X_USER"
XAUTH="/home/$X_USER/.Xauthority"
[ ! -f "$XAUTH" ] && XAUTH="/run/user/$(id -u $X_USER)/.mutter-Xwaylandauth.*" # Para Wayland si aplica

# 3. Configurar entorno para el VNC
export XAUTHORITY=$XAUTH

# 4. VNC Password Fija
mkdir -p /home/$X_USER/.vnc
x11vnc -storepasswd "astroorange" /home/$X_USER/.vnc/passwd
chown $X_USER:$X_USER /home/$X_USER/.vnc/passwd

# 5. Lanzar VNC y noVNC
echo "Starting VNC for $X_USER..."
# Matar instancias previas para evitar bloqueos
pkill x11vnc || true
x11vnc -auth $XAUTH -display :0 -forever -rfbauth /home/$X_USER/.vnc/passwd -shared -bg -xkb -noxrecord -noxfixes -noxdamage &

# Lanzar noVNC (siempre en puerto 6080)
pkill -f launch.sh || true
/usr/share/novnc/utils/launch.sh --vnc localhost:5900 --listen 6080
