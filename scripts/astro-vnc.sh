#!/bin/bash
# AstroOrange - Headless VNC Server (DYNAMIC SESSION SYNC)
# Provides remote desktop access for the current logged-in user

export DISPLAY=:0
rm -f /tmp/.X0-lock

# 1. Detectar el archivo Xauthority de LightDM (CRÍTICO: Hacerlo antes de esperar)
echo "Searching for Xauthority..."
XAUTH=""
# Reintento de búsqueda de XAUTH si el sistema acaba de arrancar
for i in {1..30}; do
    XAUTH=$(find /var/run/lightdm /run/lightdm -name ":0*" 2>/dev/null | head -n 1)
    [ -n "$XAUTH" ] && break
    sleep 1
done

if [ -z "$XAUTH" ]; then
    X_USER=$(ps aux | grep Xorg | grep -v grep | awk '{print $1}' | head -n 1)
    [ -n "$X_USER" ] && [ "$X_USER" != "root" ] && XAUTH="/home/$X_USER/.Xauthority"
    [ "$X_USER" == "root" ] && XAUTH="/root/.Xauthority"
fi

echo "Using XAUTHORITY: $XAUTH"
export XAUTHORITY=$XAUTH

# 2. Esperar a que el servidor X esté listo (max 60s)
echo "Waiting for X server on :0..."
for i in {1..60}; do
    if xset -display :0 q &>/dev/null; then
        echo "X server detected!"
        break
    fi
    sleep 1
done

# 3. VNC Password Fija
VNC_PASS_FILE="/etc/x11vnc.pass"
if [ ! -f "$VNC_PASS_FILE" ]; then
    x11vnc -storepasswd "astroorange" "$VNC_PASS_FILE"
    chmod 600 "$VNC_PASS_FILE"
fi

# 4. Lanzar VNC y noVNC
echo "Starting VNC..."
pkill x11vnc || true
x11vnc -auth "$XAUTH" -display :0 -forever -rfbauth "$VNC_PASS_FILE" -shared -bg -xkb -noxrecord -noxfixes -noxdamage &

# Intentar localizar noVNC launch.sh en rutas comunes
NOVNC_LAUNCH=""
for p in "/usr/share/novnc/utils/launch.sh" "/usr/bin/novnc_proxy"; do
    if [ -f "$p" ]; then
        NOVNC_LAUNCH="$p"
        break
    fi
done

if [ -n "$NOVNC_LAUNCH" ]; then
    echo "Starting noVNC with $NOVNC_LAUNCH..."
    pkill -f "$(basename "$NOVNC_LAUNCH")" || true
    if [[ "$NOVNC_LAUNCH" == *"launch.sh"* ]]; then
        "$NOVNC_LAUNCH" --vnc localhost:5900 --listen 6080 &
    else
        "$NOVNC_LAUNCH" --vnc localhost:5900 --listen 6080
    fi
else
    echo "ERROR: noVNC launch script not found!"
    exit 1
fi
