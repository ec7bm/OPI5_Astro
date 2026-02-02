#!/bin/bash
# AstroOrange Network Watchdog Service V8.0 ("The Nuclear Option")
# Monitors connection state to prevent Router Saturation (DHCP conflicts)
# V8.0 Fix: switched to 'nmcli' device polling instead of 'ip route' for reliability.
# includes "Conflict Resolution" to ensure Router safety.

echo "---[ AstroOrange Network Watchdog V8.0 ]---"

# --- HELPER FUNCTIONS ---

check_ethernet() {
    # Returns 0 (true) if ANY ethernet device is connected
    nmcli -t -f TYPE,STATE device | grep "^ethernet:connected" >/dev/null 2>&1
    return $?
}

check_wifi_client() {
    # Returns 0 (true) if wlan0 is connected to something that is NOT our hotspot
    nmcli -t -f DEVICE,NAME,TYPE con show --active | grep "wlan0" | grep -v "astroorange-ap" >/dev/null 2>&1
    return $?
}

kill_hotspot() {
    # Aggressively remove the hotspot
    if nmcli con show "astroorange-ap" >/dev/null 2>&1; then
        echo "🔪 Killing Hotspot..."
        sudo nmcli con down "astroorange-ap" >/dev/null 2>&1
        sudo nmcli con delete "astroorange-ap" >/dev/null 2>&1
    fi
}

start_hotspot() {
    echo "⚠️ Starting Rescue Hotspot..."
    
    # 1. Clean slate
    kill_hotspot

    # 2. Identify Interface
    IFACE=$(nmcli -t -f DEVICE,TYPE device | grep wifi | cut -d: -f1 | head -n1)
    [ -z "$IFACE" ] && IFACE="wlan0"
    
    # 3. Create (Manual only, no autoconnect)
    sudo nmcli con add type wifi ifname "$IFACE" con-name "astroorange-ap" autoconnect no ssid "AstroOrange-Setup" mode ap connection.interface-name "$IFACE" >/dev/null
    sudo nmcli con modify "astroorange-ap" ipv4.method shared ipv4.addresses 10.42.0.1/24
    sudo nmcli con modify "astroorange-ap" wifi-sec.key-mgmt wpa-psk wifi-sec.psk "astrosetup"
    sudo nmcli con modify "astroorange-ap" 802-11-wireless.band bg

    # 4. Launch
    sudo nmcli con up "astroorange-ap"
    echo "🔥 Hotspot 'AstroOrange-Setup' is ACTIVE on $IFACE"
}

# --- MAIN LOGIC ---

# 0. Immediate Cleanup on Launch
# If Ethernet is already there, kill everything immediately.
if check_ethernet; then
    echo "✅ Ethernet Detected on Start. Cleaning up..."
    kill_hotspot
    exit 0
fi

# 1. Try to Connect to User WiFi (if configured)
if nmcli con show "Astro-WIFI" >/dev/null 2>&1; then
    echo "🔄 Found 'Astro-WIFI' profile."
    
    # Ensure radio is free
    kill_hotspot
    
    echo "🙏 Attempting connection to 'Astro-WIFI'..."
    sudo nmcli con up "Astro-WIFI"
    
    # Wait for results (gives NM time to DHCP)
    sleep 10
    
    # Check Result
    if check_wifi_client; then
        echo "✅ SUCCESS: Connected to home WiFi."
        exit 0
    else
        echo "❌ User WiFi Failed. Falling back."
    fi
fi

# 2. Fallback: If no Ethernet and no User WiFi -> Hotspot
echo "⚠️ No connectivity. Launching Setup Mode."
start_hotspot

# 3. WATCHDOG LOOP (Persistent Monitor)
echo "👀 Entering Watchdog Mode..."

while true; do
    sleep 5
    
    # A. Ethernet Plugged In? -> KILL HOTSPOT
    if check_ethernet; then
        echo "🚨 ETHERNET DETECTED! Killing Hotspot immediately to save Router..."
        kill_hotspot
        # We exit, because we don't need to monitor anymore (systemd will restart us on reboot)
        # OR we can stay alive to kill it again if it spawns. Let's stay alive but silent.
        # Check every 10s just to be sure it stays dead.
        continue
    fi
    
    # B. Wifi Client Connected? -> KILL HOTSPOT
    if check_wifi_client; then
         # Only kill if hotspot is ALSO active (ghost presence)
         if nmcli con show --active | grep "astroorange-ap" >/dev/null 2>&1; then
             echo "🚨 GHOST HOTSPOT DETECTED! Killing..."
             kill_hotspot
         fi
    fi
done
