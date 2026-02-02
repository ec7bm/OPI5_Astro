#!/bin/bash
# AstroOrange Network Watchdog Service V9.2 ("Diagnostic Edition")
# V9.2 Fix: Dynamic interface detection + Logs in /tmp/astro-network.log

LOGFILE="/tmp/astro-network.log"
echo "---[ AstroOrange Network Watchdog V9.2 LOG $(date) ]---" > "$LOGFILE"

log() {
    echo "$(date '+%H:%M:%S') > $1" | tee -a "$LOGFILE"
}

# --- HELPER FUNCTIONS ---

get_wifi_iface() {
    # Detects the first wifi interface found (wlan0, wlan1, etc)
    IFACE=$(nmcli -t -f DEVICE,TYPE device | grep wifi | cut -d: -f1 | head -n1)
    [ -z "$IFACE" ] && IFACE="wlan0"
    echo "$IFACE"
}

WIFI_IFACE=$(get_wifi_iface)
log "WiFi Interface detected: $WIFI_IFACE"

check_ethernet() {
    nmcli -t -f TYPE,STATE device | grep "^ethernet:connected" >/dev/null 2>&1
    return $?
}

check_wifi_client() {
    # Check if the DETECTED interface is connected to something NOT the hotspot
    nmcli -t -f DEVICE,NAME,TYPE con show --active | grep "$WIFI_IFACE" | grep -v "astroorange-ap" >/dev/null 2>&1
    return $?
}

kill_hotspot() {
    if nmcli con show "astroorange-ap" >/dev/null 2>&1; then
        log "🔪 Killing Hotspot..."
        sudo nmcli con down "astroorange-ap" >> "$LOGFILE" 2>&1
        sudo nmcli con delete "astroorange-ap" >> "$LOGFILE" 2>&1
    fi
}

start_hotspot() {
    log "⚠️ Starting Rescue Hotspot (Final Fallback)..."
    kill_hotspot
    
    sudo nmcli con add type wifi ifname "$WIFI_IFACE" con-name "astroorange-ap" autoconnect no ssid "AstroOrange-Setup" mode ap connection.interface-name "$WIFI_IFACE" >> "$LOGFILE" 2>&1
    sudo nmcli con modify "astroorange-ap" ipv4.method shared ipv4.addresses 10.42.0.1/24 >> "$LOGFILE" 2>&1
    sudo nmcli con modify "astroorange-ap" wifi-sec.key-mgmt wpa-psk wifi-sec.psk "astrosetup" >> "$LOGFILE" 2>&1
    sudo nmcli con modify "astroorange-ap" 802-11-wireless.band bg >> "$LOGFILE" 2>&1

    sudo nmcli con up "astroorange-ap" >> "$LOGFILE" 2>&1
    log "🔥 Hotspot 'AstroOrange-Setup' is ACTIVE on $WIFI_IFACE"
}

# --- MAIN LOGIC ---

log "Starting Watchdog Logic..."

# 0. Immediate Cleanup on Launch
if check_ethernet; then
    log "✅ Ethernet Detected on Start. Exiting."
    kill_hotspot
    exit 0
fi

# 1. Try to Connect to User WiFi (if configured)
if nmcli con show "Astro-WIFI" >/dev/null 2>&1; then
    log "🔄 Found 'Astro-WIFI' profile. Attempting connection..."
    kill_hotspot
    
    # Attempt 1
    log "🙏 Attempt 1/2: sudo nmcli con up Astro-WIFI..."
    sudo nmcli con up "Astro-WIFI" >> "$LOGFILE" 2>&1 &
    
    log "⏳ Waiting 30s..."
    sleep 30
    
    if check_wifi_client; then
        log "✅ SUCCESS: WiFi connected."
        exit 0
    fi
    
    # Attempt 2
    log "⚠️ Attempt 1 failed. Retrying (Attempt 2)..."
    sudo nmcli con down "Astro-WIFI" >> "$LOGFILE" 2>&1
    sleep 2
    sudo nmcli con up "Astro-WIFI" >> "$LOGFILE" 2>&1 &
    
    log "⏳ Waiting 30s..."
    sleep 30

    if check_wifi_client; then
        log "✅ SUCCESS: WiFi connected (Attempt 2)."
        exit 0
    else
        log "❌ All WiFi attempts failed."
    fi
fi

# 2. Fallback
log "⚠️ NO CONNECTIVITY FOUND. Launching Hotspot."
start_hotspot

# 3. Watchdog Loop
log "👀 Entering Watchdog persistent loop..."
while true; do
    sleep 10
    if check_ethernet; then
        log "🚨 ETHERNET PLUGGED! Killing Hotspot..."
        kill_hotspot
    fi
    
    if check_wifi_client; then
         if nmcli con show --active | grep "astroorange-ap" >/dev/null 2>&1; then
             log "🚨 GHOST HOTSPOT! Killing..."
             kill_hotspot
         fi
    fi
done
