#!/bin/bash
# AstroOrange Network Watchdog Service V7.5
# Monitors connection state to prevent Router Saturation (DHCP conflicts)
# V7.5 Fix: Prioritize 'Astro-WIFI'. Actively attempts to connect to the user-configured WiFi
# before giving up and starting the Hotspot.

echo "---[ AstroOrange Network Watchdog V7.5 ]---"

# 0. SAFETY FIRST: Kill hotspot to clear radio
sudo nmcli con down "astroorange-ap" 2>/dev/null

# Helper function
kill_hotspot() {
    sudo nmcli con down "astroorange-ap" 2>/dev/null
}

# 1. Initial Attempt Phase (30 seconds)
echo "Looking for networks..."

for i in {1..15}; do
    echo "Scan cycle $i/15..."
    
    # A. Check Ethernet
    if ip route | grep "default" | grep -v "wlan" >/dev/null 2>&1; then
        echo "✅ Ethernet detected. Service exiting."
        exit 0
    fi
    
    # B. Check Active WiFi Client
    if nmcli -t -f DEVICE,NAME,TYPE con show --active | grep "wlan0" | grep -v "astroorange-ap" >/dev/null 2>&1; then
        echo "✅ WiFi Connected. Service exiting."
        exit 0
    fi

    # C. V7.5 Feature: Explicitly try to bring up 'Astro-WIFI' if configured
    # The wizard saves the profile as "Astro-WIFI". We force it to try connecting.
    if nmcli con show "Astro-WIFI" >/dev/null 2>&1; then
        echo "🔄 Found 'Astro-WIFI' profile. Attempting connection..."
        # We try to bring it up. If it succeeds, loop B or C will catch it next iteration.
        sudo nmcli con up "Astro-WIFI" >/dev/null 2>&1 &
        # We don't wait/block here, we let NM try in background and check status next loop
    fi

    # D. Check Internet Ping
    if ping -c 1 -W 1 8.8.8.8 >/dev/null 2>&1; then
        echo "✅ Internet detected. Service exiting."
        exit 0
    fi
    sleep 2
done

# 2. No Network Success -> Activate Rescue Hotspot
echo "⚠️ Connection failed. Activating Rescue Hotspot..."

IFACE=$(nmcli -t -f DEVICE,TYPE device | grep wifi | cut -d: -f1 | head -n1)
[ -z "$IFACE" ] && IFACE="wlan0"

sudo nmcli con delete "astroorange-ap" 2>/dev/null || true

# AP Settings
sudo nmcli con add type wifi ifname "$IFACE" con-name "astroorange-ap" autoconnect no ssid "AstroOrange-Setup" mode ap connection.interface-name "$IFACE"
sudo nmcli con modify "astroorange-ap" ipv4.method shared ipv4.addresses 10.42.0.1/24
sudo nmcli con modify "astroorange-ap" wifi-sec.key-mgmt wpa-psk wifi-sec.psk "astrosetup"
sudo nmcli con modify "astroorange-ap" 802-11-wireless.band bg

sudo nmcli con up "astroorange-ap"

echo "🔥 Hotspot 'AstroOrange-Setup' is ACTIVE on $IFACE"

# 3. WATCHDOG LOOP
echo "👀 Entering Watchdog Mode..."

while true; do
    sleep 5
    # If Ethernet is plugged in...
    if ip route | grep "default" | grep -v "$IFACE" | grep -v "wlan" >/dev/null 2>&1; then
        echo "🚨 ETHERNET DETECTED! Killing Hotspot..."
        kill_hotspot
        sudo nmcli con delete "astroorange-ap" 2>/dev/null
        exit 0
    fi
    
    # If user connects to WiFi manually...
    if nmcli -t -f DEVICE,NAME,TYPE con show --active | grep "wlan0" | grep -v "astroorange-ap" >/dev/null 2>&1; then
        echo "🚨 WIFI CLIENT DETECTED! Killing Hotspot..."
        kill_hotspot
        sudo nmcli con delete "astroorange-ap" 2>/dev/null
        exit 0
    fi
done
