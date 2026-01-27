#!/bin/bash
# astroorange-firstboot.sh - First boot initialization
# Handles network detection, Hotspot creation, and Wizard auto-launch.

set -e

LOG_FILE="/var/log/astroorange-firstboot.log"
FLAG_FILE="/etc/astroorange/.firstboot-done"
TARGET_USER="orangepi" # Default for Orange Pi images

# Redirect output
exec > >(tee -a "$LOG_FILE") 2>&1

echo "========================================="
echo "  AstroOrange First Boot - $(date)"
echo "========================================="

# 1. CHECK COMPLETION
if [ -f "$FLAG_FILE" ]; then
    echo "✅ First boot already completed."
    exit 0
fi

# 2. SYSTEM SETUP
echo "🔧 Configuring system basics..."
mkdir -p /etc/astroorange
hostnamectl set-hostname astroorange
sed -i 's/127.0.1.1.*/127.0.1.1\tastroorange/' /etc/hosts

# Ensure target user exists (fallback)
if ! id "$TARGET_USER" &>/dev/null; then
    echo "⚠️  User $TARGET_USER not found, checking for 'astroorange'..."
    if id "astroorange" &>/dev/null; then
        TARGET_USER="astroorange"
    else
        echo "❌ No suitable user found! Aborting."
        exit 1
    fi
fi
echo "👤 Target user: $TARGET_USER"

# 3. NETWORK LOGIC
echo "📡 Checking network connectivity..."
sleep 5 # Give drivers time to load

# Try to detect if we have an IP and internet access
INTERNET_OK=false
if ping -c 1 8.8.8.8 &>/dev/null; then
    echo "✅ Internet connection detected."
    INTERNET_OK=true
else
    echo "⚠️  No internet connection."
fi

if [ "$INTERNET_OK" = false ]; then
    echo "🔥 Activating Emergency Hotspot..."
    
    # Check if hotspot connection already exists
    if nmcli con show "AstroOrange-Hotspot" &>/dev/null; then
        nmcli con up "AstroOrange-Hotspot"
    else
        nmcli con add type wifi ifname wlan0 con-name AstroOrange-Hotspot \
            autoconnect yes ssid AstroOrange mode ap \
            wifi-sec.key-mgmt wpa-psk wifi-sec.psk "astroorange" \
            ipv4.method shared ipv4.addresses 192.168.4.1/24
        nmcli con up AstroOrange-Hotspot
    fi
    
    echo "✅ Hotspot active: SSID='AstroOrange', IP=192.168.4.1"
fi

# 4. LAUNCH SERVICES
echo "🚀 Starting noVNC & VNC Server..."

# Set VNC password if not set (default: astroorange)
if [ ! -f "/home/$TARGET_USER/.vnc/passwd" ]; then
    mkdir -p "/home/$TARGET_USER/.vnc"
    echo "astroorange" | vncpasswd -f > "/home/$TARGET_USER/.vnc/passwd"
    chown -R "$TARGET_USER:$TARGET_USER" "/home/$TARGET_USER/.vnc"
    chmod 600 "/home/$TARGET_USER/.vnc/passwd"
fi

# Start VNC Server (using systemd helper if available, or direct)
# Better to rely on a user service or running command as user
su - "$TARGET_USER" -c "vncserver :1 -geometry 1280x720 -depth 24"

# Start noVNC (websockify)
# We forward port 6080 to VNC port 5901
websockify -D --web=/usr/share/novnc 6080 localhost:5901

echo "✅ Remote access ready:"
echo "   - VNC: port 5901"
echo "   - Web: http://<IP>:6080/vnc.html"

# 5. COMPLETION MARKER
# We do NOT mark as done yet; the WIZARD is responsible for creating the flag file
# after the user completes the setup.
# However, to prevent this script from re-running logic that shouldn't run (like hostname reset),
# we might want a semi-flag. But for now, safe to re-run.

echo "========================================="
echo "  First boot logic finished. Wizard awaiting connection."
echo "========================================="
