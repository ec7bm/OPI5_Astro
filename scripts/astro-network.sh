#!/bin/bash
# AstroOrange Network Watchdog Service V7.4
# Monitors connection state to prevent Router Saturation (DHCP conflicts)
# V7.4 Fix: Conflict Avoidance. Checks if 'wlan0' is already connected to a Client WiFi before forcing AP mode.
# This prevents the "Fight" between Home WiFi and Setup Hotspot.

echo "---[ AstroOrange Network Watchdog V7.4 ]---"

# 0. SAFETY FIRST: Kill any rogue hotspot immediately on script start
sudo nmcli con down "astroorange-ap" 2>/dev/null

# Helper function
kill_hotspot() {
    sudo nmcli con down "astroorange-ap" 2>/dev/null
}

# 1. Initial Check (Wait up to 30s for ANY network)
echo "Waiting for network (Ethernet or WiFi)..."
for i in {1..30}; do
    # A. Check Ethernet (Default route on non-wlan)
    if ip route | grep "default" | grep -v "wlan" >/dev/null 2>&1; then
        echo "✅ Ethernet detected. Service exiting."
        exit 0
    fi
    
    # B. Check Active WiFi Client Connection (Prevent AP Conflict)
    # If we are connected to "Ec7bm-Charlie" or similar, DO NOT START HOTSPOT.
    # We check if wlan0 has an active connection that is NOT our hotspot.
    if nmcli -t -f DEVICE,NAME,TYPE con show --active | grep "wlan0" | grep -v "astroorange-ap" >/dev/null 2>&1; then
        echo "✅ Connected to a WiFi Network. Service exiting."
        exit 0
    fi

    # C. Check Ping (Final confirm)
    if ping -c 1 -W 1 8.8.8.8 >/dev/null 2>&1; then
        echo "✅ Internet detected. Service exiting."
        exit 0
    fi
    sleep 1
done

# 2. No Internet & No Client WiFi -> Activate Rescue Hotspot
echo "⚠️ No network detected. Activating Rescue Hotspot..."

IFACE=$(nmcli -t -f DEVICE,TYPE device | grep wifi | cut -d: -f1 | head -n1)
[ -z "$IFACE" ] && IFACE="wlan0"

# Clean previous AP profiles
sudo nmcli con delete "astroorange-ap" 2>/dev/null || true

# AP Settings (autoconnect=no)
sudo nmcli con add type wifi ifname "$IFACE" con-name "astroorange-ap" autoconnect no ssid "AstroOrange-Setup" mode ap connection.interface-name "$IFACE"
sudo nmcli con modify "astroorange-ap" ipv4.method shared ipv4.addresses 10.42.0.1/24
sudo nmcli con modify "astroorange-ap" wifi-sec.key-mgmt wpa-psk wifi-sec.psk "astrosetup"
sudo nmcli con modify "astroorange-ap" 802-11-wireless.band bg

# Activate
sudo nmcli con up "astroorange-ap"

echo "🔥 Hotspot 'AstroOrange-Setup' is ACTIVE on $IFACE"

# 3. WATCHDOG LOOP
echo "👀 Entering Watchdog Mode..."

while true; do
    sleep 5
    # If Ethernet is plugged in...
    if ip route | grep "default" | grep -v "$IFACE" | grep -v "wlan" >/dev/null 2>&1; then
        echo "🚨 ETHERNET DETECTED! Killing Hotspot immediately..."
        kill_hotspot
        sudo nmcli con delete "astroorange-ap" 2>/dev/null
        exit 0
    fi
    
    # If user manually connects to a WiFi network via GUI...
    if nmcli -t -f DEVICE,NAME,TYPE con show --active | grep "wlan0" | grep -v "astroorange-ap" >/dev/null 2>&1; then
        echo "🚨 NEW WIFI CONNECTION DETECTED! Killing Hotspot..."
        kill_hotspot
        sudo nmcli con delete "astroorange-ap" 2>/dev/null
        exit 0
    fi
done
