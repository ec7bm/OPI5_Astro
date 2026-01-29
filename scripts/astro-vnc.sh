#!/bin/bash
# AstroOrange - Headless VNC Server (DYNAMIC SESSION SYNC)
# Provides remote desktop access for the current logged-in user

export DISPLAY=:0
export HOME=/root
rm -f /tmp/.X0-lock

# 1. Buscar Xauthority de LightDM
echo "Searching for Xauthority..."
XAUTH=""
for i in {1..20}; do
    XAUTH=$(find /var/run/lightdm /run/lightdm -name ":0*" 2>/dev/null | head -n 1)
    [ -n "$XAUTH" ] && break
    sleep 1
done
export XAUTHORITY=$XAUTH

# 2. Esperar servidor X
echo "Waiting for X server on :0..."
for i in {1..30}; do
    xset -display :0 q &>/dev/null && break
    sleep 1
done

# 3. Lanzar x11vnc con contraseña global
VNC_PASS="/etc/x11vnc.pass"
if [ ! -f "$VNC_PASS" ]; then
    x11vnc -storepasswd "astroorange" "$VNC_PASS"
    chmod 600 "$VNC_PASS"
fi

echo "Starting x11vnc..."
pkill x11vnc || true
x11vnc -auth "$XAUTH" -display :0 -forever -rfbauth "$VNC_PASS" -shared -bg -noxrecord -noxfixes -noxdamage &

# 4. Lanzar noVNC y BLOQUEAR el script para que systemd no lo reinicie
echo "Starting noVNC proxy..."
if [ -f "/usr/share/novnc/utils/launch.sh" ]; then
    /usr/share/novnc/utils/launch.sh --vnc localhost:5900 --listen 6080
elif [ -f "/usr/bin/novnc_proxy" ]; then
    /usr/bin/novnc_proxy --vnc localhost:5900 --listen 6080
else
    echo "ERROR: noVNC not found. Waiting indefinitely to avoid service loop..."
    while true; do sleep 60; done
fi
