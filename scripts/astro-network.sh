#!/bin/bash
# AstroOrange Network Watchdog Service V7.6
# Monitors connection state to prevent Router Saturation (DHCP conflicts)
# V7.6 Fix: "Stop-to-Connect". If 'Astro-WIFI' profile exists, we KILL the hotspot temporarily
# to allow the radio to switch modes. Simultaneous AP+Client often fails on Rockchip drivers.

echo "---[ AstroOrange Network Watchdog V7.6 ]---"

# Helper function
kill_hotspot() {
    sudo nmcli con down "astroorange-ap" 2>/dev/null
}

start_hotspot() {
    echo "⚠️ Starting Rescue Hotspot..."
    IFACE=$(nmcli -t -f DEVICE,TYPE device | grep wifi | cut -d: -f1 | head -n1)
    [ -z "$IFACE" ] && IFACE="wlan0"
    
    # Clean previous
    sudo nmcli con delete "astroorange-ap" 2>/dev/null || true

    # Create & Start
    sudo nmcli con add type wifi ifname "$IFACE" con-name "astroorange-ap" autoconnect no ssid "AstroOrange-Setup" mode ap connection.interface-name "$IFACE"
    sudo nmcli con modify "astroorange-ap" ipv4.method shared ipv4.addresses 10.42.0.1/24
    sudo nmcli con modify "astroorange-ap" wifi-sec.key-mgmt wpa-psk wifi-sec.psk "astrosetup"
    sudo nmcli con modify "astroorange-ap" 802-11-wireless.band bg
    sudo nmcli con up "astroorange-ap"
    echo "🔥 Hotspot 'AstroOrange-Setup' is ACTIVE on $IFACE"
}

# 1. Initial Check (Have we got Ethernet?)
echo "Checking Initial Connectivity..."
if ip route | grep "default" | grep -v "wlan" >/dev/null 2>&1; then
    echo "✅ Ethernet detected. Service exiting."
    exit 0
fi

# 2. V7.6 LOGIC: Do we have a User WiFi Configured?
# If so, we must KILL any hotspot and TRY to connect.
if nmcli con show "Astro-WIFI" >/dev/null 2>&1; then
    echo "🔄 Found 'Astro-WIFI' profile. Switching to Client Mode..."
    
    # Kill Hotspot to free radio
    kill_hotspot
    sleep 2
    
    # Try Connect
    echo "Trying to connect to Astro-WIFI..."
    sudo nmcli con up "Astro-WIFI"
    
    # Wait and Verify
    sleep 10
    
    # Check if connected
    if nmcli -t -f DEVICE,NAME,TYPE con show --active | grep "wlan0" | grep "Astro-WIFI" >/dev/null 2>&1; then
        echo "✅ SUCCESS: Connected to Astro-WIFI."
        exit 0
    else
        echo "❌ Connection Failed. Falling back to Hotspot."
    fi
fi

# 3. Fallback: Start Hotspot (If no internet, and no working WiFi profile)
if ping -c 1 -W 1 8.8.8.8 >/dev/null 2>&1; then
     echo "✅ Internet detected. Service exiting."
     exit 0
fi

start_hotspot

# 4. WATCHDOG LOOP
echo "👀 Entering Watchdog Mode..."

while true; do
    sleep 5
    # If Ethernet is plugged in...
    if ip route | grep "default" | grep -v "wlan" >/dev/null 2>&1; then
        echo "🚨 ETHERNET DETECTED! Killing Hotspot..."
        kill_hotspot
        sudo nmcli con delete "astroorange-ap" 2>/dev/null
        exit 0
    fi
    
    # If user connects to WiFi manually...
    if nmcli -t -f DEVICE,NAME,TYPE con show --active | grep "wlan0" | grep -v "astroorange-ap" >/dev/null 2>&1; then
        echo "🚨 CLIENT WIFI CONNECTED! Killing Hotspot..."
        kill_hotspot
        sudo nmcli con delete "astroorange-ap" 2>/dev/null
        exit 0
    fi
done
