#!/bin/bash
# AstroOrange - Network Rescue Hotspot
# Auto-starts if no internet connection is detected

echo "AstroOrange Network Manager - Initializing..."
sleep 15  # Wait for NetworkManager to settle

# Detectar interfaz wifi dinamicamente
for i in {1..5}; do
    IFACE=$(nmcli -t -f DEVICE,TYPE device | grep wifi | cut -d: -f1 | head -n1)
    if [ -n "$IFACE" ]; then break; fi
    echo "Waiting for WiFi interface... ($i/5)"
    sleep 5
done

[ -z "$IFACE" ] && IFACE="wlan0"

SSID="AstroOrange-Setup"
PASS="astrosetup"

echo "Checking connectivity on $IFACE..."

# Verificar si hay conexión a internet real (no solo "connected")
if ping -c 1 -W 2 8.8.8.8 >/dev/null 2>&1; then
    echo "Internet detected. Hotspot not needed."
    exit 0
fi

echo "No internet detected. Starting rescue hotspot..."

nmcli device set "$IFACE" managed yes
nmcli con delete "$SSID" 2>/dev/null || true
nmcli con add type wifi ifname "$IFACE" con-name "$SSID" autoconnect yes ssid "$SSID" mode ap ipv4.method shared

# Fix: Forzar seguridad WPA2 compatible (evita supplicant-timeout en OPi5 Pro)
nmcli con modify "$SSID" wifi-sec.key-mgmt wpa-psk wifi-sec.psk "$PASS"
nmcli con modify "$SSID" wifi-sec.proto rsn
nmcli con modify "$SSID" wifi-sec.group ccmp
nmcli con modify "$SSID" wifi-sec.pairwise ccmp

echo "Bringing up hotspot..."
nmcli con up "$SSID"
echo "Hotspot '$SSID' is now active!"
