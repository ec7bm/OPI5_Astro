#!/bin/bash
# AstroOrange Network Watchdog Service V7.2
# Monitors connection state to prevent Router Saturation (DHCP conflicts)
# This script ensures the Hotspot is KILLED immediately if Ethernet is connected.

echo "---[ AstroOrange Network Watchdog V7.2 ]---"

# 1. Initial Check (Give NetworkManager 15s to connect automatically)
echo "Waiting for network..."
for i in {1..15}; do
    # Check for default route on Ethernet (usually eth0 or enP*)
    if ip route | grep "default" | grep -v "wlan" >/dev/null 2>&1; then
        echo "✅ Ethernet detected on boot. Service exiting (No Hotspot needed)."
        exit 0
    fi
    # Check for ping (in case of known WiFi)
    if ping -c 1 -W 1 8.8.8.8 >/dev/null 2>&1; then
        echo "✅ Internet detected. Service exiting."
        exit 0
    fi
    sleep 1
done

# 2. No Internet -> Activate Rescue Hotspot
echo "⚠️ No internet detected. Activating Rescue Hotspot..."

# Identify WiFi Interface (usually wlan0)
IFACE=$(nmcli -t -f DEVICE,TYPE device | grep wifi | cut -d: -f1 | head -n1)
[ -z "$IFACE" ] && IFACE="wlan0"

# Clean previous AP profiles to avoid conflicts
sudo nmcli con delete "astroorange-ap" 2>/dev/null || true

# Create & Activate AP
# Note: connection.interface-name forces it to stay on WiFi, avoiding bridge leaks
sudo nmcli con add type wifi ifname "$IFACE" con-name "astroorange-ap" autoconnect yes ssid "AstroOrange-Setup" mode ap connection.interface-name "$IFACE"
sudo nmcli con modify "astroorange-ap" ipv4.method shared ipv4.addresses 10.42.0.1/24
sudo nmcli con modify "astroorange-ap" wifi-sec.key-mgmt wpa-psk wifi-sec.psk "astrosetup"
sudo nmcli con modify "astroorange-ap" 802-11-wireless.band bg
sudo nmcli con up "astroorange-ap"

echo "🔥 Hotspot 'AstroOrange-Setup' is ACTIVE on $IFACE"

# 3. WATCHDOG LOOP (The Fix for Router Saturation)
echo "👀 Entering Watchdog Mode... (Will kill Hotspot if Ethernet is plugged detected)"

while true; do
    # Sleep first to save CPU
    sleep 5

    # Check for Ethernet connection (Default route NOT on wlan)
    # This detects if user plugs in cable
    if ip route | grep "default" | grep -v "$IFACE" | grep -v "wlan" >/dev/null 2>&1; then
        echo "🚨 ETHERNET DETECTED! Killing Hotspot immediately to protect LAN..."
        sudo nmcli con down "astroorange-ap"
        # We delete it so it doesn't auto-up again
        sudo nmcli con delete "astroorange-ap"
        echo "✅ Hotspot disabled. We are now a clean client."
        exit 0
    fi
    
    # Optional: Check for Internet access specifically
    if ping -c 1 -W 1 1.1.1.1 >/dev/null 2>&1; then
         echo "🚨 INTERNET RESTORED! Killing Hotspot..."
         sudo nmcli con down "astroorange-ap"
         sudo nmcli con delete "astroorange-ap"
         exit 0
    fi
done
