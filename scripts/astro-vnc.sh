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
for i in {1..45}; do
    echo "Attempt $i: Searching for X session..."
    
    # Method A: LightDM run directory (Fastest/Official)
    XAUTH=$(find /var/run/lightdm /run/lightdm -name ":0*" 2>/dev/null | head -n 1)
    
    # Method B: Process discovery (Most reliable)
    # Search for the -auth flag in the running Xorg/X server process
    if [ -z "$XAUTH" ]; then
        XAUTH=$(ps aux | grep -w Xorg | grep -v grep | grep -oP '(?<=-auth )[^ ]+' | head -n 1)
    fi

    # Method C: Active Desktop User
    if [ -z "$XAUTH" ]; then
        LOGGED_USER=$(who | grep "(:0)" | awk '{print $1}' | head -n 1)
        if [ -n "$LOGGED_USER" ]; then
            XAUTH="/home/$LOGGED_USER/.Xauthority"
        fi
    fi

    # Method D: Global fallback search
    if [ -z "$XAUTH" ]; then
        XAUTH=$(find /home -maxdepth 2 -name ".Xauthority" 2>/dev/null | head -n 1)
    fi

    if [ -n "$XAUTH" ] && [ -f "$XAUTH" ]; then
        echo "Found Xauthority: $XAUTH"
        export XAUTHORITY=$XAUTH
        break
    fi
    
    echo "   ...waiting for X session or authority file..."
    sleep 2
done

if [ -z "$XAUTHORITY" ]; then
    echo "WARNING: No Xauthority found after 90s. VNC might fail."
fi

# 2. Esperar servidor X (with specific authority)
echo "Waiting for X server on :0..."
for i in {1..20}; do
    if xset -display :0 q &>/dev/null; then
        echo "X Server is READY."
        break
    fi
    echo "   ...waiting for X server (:0) [$i/20]"
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

# Common base flags
X11VNC_FLAGS="-display :0 -forever -rfbauth $VNC_PASS -shared -bg -noxrecord -noxfixes -noxdamage"

if [ -n "$XAUTHORITY" ]; then
    echo "Launching x11vnc with explicit auth..."
    x11vnc -auth "$XAUTHORITY" $X11VNC_FLAGS
else
    echo "Launching x11vnc with auto-discovery fallback..."
    x11vnc -find $X11VNC_FLAGS
fi

# 4. Lanzar noVNC y BLOQUEAR el script para que systemd no lo reinicie
echo "Starting noVNC proxy on port 6080..."
if [ -f "/usr/share/novnc/utils/launch.sh" ]; then
    /usr/share/novnc/utils/launch.sh --vnc localhost:5900 --listen 6080
elif [ -f "/usr/bin/novnc_proxy" ]; then
    /usr/bin/novnc_proxy --vnc localhost:5900 --listen 6080
else
    echo "ERROR: noVNC not found. Waiting indefinitely to avoid service loop..."
    while true; do sleep 60; done
fi
