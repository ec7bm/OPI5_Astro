#!/bin/bash
# AstroOrange - Headless VNC Server (DYNAMIC SESSION SYNC)
# Provides remote desktop access for the current logged-in user

export DISPLAY=:0
export HOME=/root
rm -f /tmp/.X0-lock

# 1. Buscar Xauthority (Robust detection for any user)
echo "--------------------------------------------------"
echo "AstroOrange VNC Diagnostic Start: $(date)"
echo "--------------------------------------------------"

XAUTH=""
for i in {1..30}; do
    echo "Attempt $i: Searching for X session..."
    
    # Method A: Process discovery (Most reliable)
    # Search for the -auth flag in the running Xorg/X server process
    XAUTH=$(ps aux | grep -w Xorg | grep -v grep | grep -oP '(?<=-auth )[^ ]+' | head -n 1)
    
    # Method B: LightDM run directory 
    if [ -z "$XAUTH" ]; then
        XAUTH=$(find /var/run/lightdm /run/lightdm -name ":0*" 2>/dev/null | head -n 1)
    fi

    # Method C: Active Desktop User
    if [ -z "$XAUTH" ]; then
        LOGGED_USER=$(who | grep "(:0)" | awk '{print $1}' | head -n 1)
        if [ -n "$LOGGED_USER" ]; then
            XAUTH="/home/$LOGGED_USER/.Xauthority"
        fi
    fi

    if [ -n "$XAUTH" ] && [ -f "$XAUTH" ]; then
        echo "LOG: Found Xauthority: $XAUTH"
        export XAUTHORITY=$XAUTH
        break
    fi
    
    echo "   ...waiting for X session or authority file..."
    sleep 2
done

# 2. Esperar servidor X (with specific authority if found)
echo "Waiting for X server on :0..."
for i in {1..20}; do
    if xset -display :0 q &>/dev/null; then
        echo "LOG: X Server is READY."
        break
    fi
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
sleep 1

# Common base flags
COMMON_FLAGS="-display :0 -forever -rfbauth $VNC_PASS -shared -bg -noxrecord -noxfixes -noxdamage"

if [ -n "$XAUTHORITY" ]; then
    echo "LOG: Launching x11vnc with explicit auth ($XAUTHORITY)"
    x11vnc -auth "$XAUTHORITY" $COMMON_FLAGS
else
    echo "LOG: Launching x11vnc with AUTO-GUESS fallback"
    x11vnc -findauth $COMMON_FLAGS
fi

# 4. Lanzar noVNC y BLOQUEAR para systemd
echo "Starting noVNC proxy on port 6080..."
if [ -f "/usr/share/novnc/utils/launch.sh" ]; then
    /usr/share/novnc/utils/launch.sh --vnc localhost:5900 --listen 6080
elif [ -f "/usr/bin/novnc_proxy" ]; then
    /usr/bin/novnc_proxy --vnc localhost:5900 --listen 6080
else
    echo "ERROR: noVNC not found. Waiting indefinitely..."
    while true; do sleep 60; done
fi
