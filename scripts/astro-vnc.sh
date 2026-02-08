#!/bin/bash
# AstroOrange - Headless VNC Server (DYNAMIC SESSION SYNC)
# Provides remote desktop access for the current logged-in user

export DISPLAY=:0
export HOME=/root
rm -f /tmp/.X0-lock

# 1. Buscar Xauthority (Robust detection for any user)
echo "Searching for Xauthority..."
XAUTH=""
for i in {1..30}; do
    # Try LightDM path (official image/system sessions)
    XAUTH=$(find /var/run/lightdm /run/lightdm -name ":0*" 2>/dev/null | head -n 1)
    
    # Try to find the user actually logged into Display :0
    if [ -z "$XAUTH" ]; then
        # Look for the user in 'who' output associated with (:0)
        LOGGED_USER=$(who | grep "(:0)" | awk '{print $1}' | head -n 1)
        
        # Fallback to any user folder containing .Xauthority if only one exists
        if [ -z "$LOGGED_USER" ]; then
            XAUTH=$(find /home -maxdepth 2 -name ".Xauthority" 2>/dev/null | head -n 1)
        else
            XAUTH="/home/$LOGGED_USER/.Xauthority"
        fi
        
        [ ! -f "$XAUTH" ] && XAUTH=""
    fi
    
    [ -n "$XAUTH" ] && break
    echo "   ...waiting for session (:0) [$i/30]"
    sleep 1
done
export XAUTHORITY=$XAUTH
echo "Using XAUTHORITY=$XAUTHORITY"


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
