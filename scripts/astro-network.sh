#!/bin/bash
# AstroOrange Network Watchdog Service V9.2.1 ("Corrected Edition")
# V9.2.1 Fix: Clean bash syntax (no escaping)

LOGFILE="/tmp/astro-network.log"
echo "---[ AstroOrange Network Watchdog V9.3 LOG $(date) ]---" > "$LOGFILE"

# V11.3 Fix: Startup delay for hardware detection
sleep 15
nmcli dev status >> "$LOGFILE" 2>&1


log() {
    echo "$(date '+%H:%M:%S') > $1" | tee -a "$LOGFILE"
}

get_wifi_iface() {
    # Try multiple times if not found
    for i in {1..5}; do
        IFACE=$(nmcli -t -f DEVICE,TYPE device | grep wifi | cut -d: -f1 | head -n1)
        [ -n "$IFACE" ] && echo "$IFACE" && return 0
        sleep 2
    done
    echo "wlan0"
}

WIFI_IFACE=$(get_wifi_iface)
log "WiFi Interface detected: $WIFI_IFACE"

check_ethernet() {
    nmcli -t -f TYPE,STATE device | grep "^ethernet:connected" >/dev/null 2>&1
    return $?
}

check_wifi_client() {
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
    sudo nmcli con add type wifi ifname "$WIFI_IFACE" con-name "astroorange-ap" autoconnect no ssid "AstroOrange-Autostart" mode ap connection.interface-name "$WIFI_IFACE" >> "$LOGFILE" 2>&1
    sudo nmcli con modify "astroorange-ap" ipv4.method shared ipv4.addresses 10.42.0.1/24 >> "$LOGFILE" 2>&1
    sudo nmcli con modify "astroorange-ap" wifi-sec.key-mgmt wpa-psk wifi-sec.psk "astroorange" >> "$LOGFILE" 2>&1
    sudo nmcli con modify "astroorange-ap" 802-11-wireless.band bg >> "$LOGFILE" 2>&1
    sudo nmcli con up "astroorange-ap" >> "$LOGFILE" 2>&1
    log "🔥 Hotspot 'AstroOrange-Autostart' is ACTIVE on $WIFI_IFACE"
}

log "Starting Watchdog Logic..."
# V13.1 Fix: Aggressive ethernet detection on start (3 attempts)
ETH_FOUND=false
for i in {1..3}; do
    log "🔍 Checking Ethernet (Attempt $i/3)..."
    if check_ethernet; then
        ETH_FOUND=true
        break
    fi
    sleep 5
done

if [ "$ETH_FOUND" = true ]; then
    log "✅ Ethernet Detected. Exiting and disabling rescue AP."
    kill_hotspot
    exit 0
fi


if nmcli con show "Astro-WIFI" >/dev/null 2>&1; then
    log "🔄 Found 'Astro-WIFI' profile. Attempting connection..."
    kill_hotspot
    log "🙏 Attempt 1/2: sudo nmcli con up Astro-WIFI..."
    sudo nmcli con up "Astro-WIFI" >> "$LOGFILE" 2>&1 &
    log "⏳ Waiting 15s..."
    sleep 15
    if check_wifi_client; then
        log "✅ SUCCESS: WiFi connected."
        exit 0
    fi
    log "⚠️ Attempt 1 failed. Retrying (Attempt 2)..."
    sudo nmcli con down "Astro-WIFI" >> "$LOGFILE" 2>&1
    sleep 2
    sudo nmcli con up "Astro-WIFI" >> "$LOGFILE" 2>&1 &
    log "⏳ Waiting 15s..."
    sleep 15
    if check_wifi_client; then
        log "✅ SUCCESS: WiFi connected (Attempt 2)."
        exit 0
    else
        log "❌ All WiFi attempts failed."
    fi
fi

log "⚠️ NO CONNECTIVITY FOUND. Launching Hotspot."
start_hotspot

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
