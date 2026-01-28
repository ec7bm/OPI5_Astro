#!/bin/bash
# AstroOrange - Network Rescue Hotspot
# Auto-starts if no internet connection is detected

# Detectar interfaz wifi dinamicamente
IFACE=$(nmcli -t -f DEVICE,TYPE device | grep wifi | cut -d: -f1 | head -n1)
[ -z "$IFACE" ] && IFACE="wlan0"

SSID="AstroOrange-Setup"
PASS="astrosetup"

echo "Checking network state on $IFACE..."
sleep 15

# Si ya hay conexion activa, saltar
if nmcli -t -f STATE g | grep -q "^connected"; then
    echo "Internet detected. Hotspot not needed."
    exit 0
fi

echo "No internet. Starting rescue hotspot..."

nmcli device set "$IFACE" managed yes
nmcli con delete "$SSID" 2>/dev/null || true
nmcli con add type wifi ifname "$IFACE" con-name "$SSID" autoconnect yes ssid "$SSID" mode ap ipv4.method shared

# Fix: Forzar seguridad WPA2 compatible (evita supplicant-timeout en OPi5 Pro)
nmcli con modify "$SSID" wifi-sec.key-mgmt wpa-psk wifi-sec.psk "$PASS"
nmcli con modify "$SSID" wifi-sec.proto rsn
nmcli con modify "$SSID" wifi-sec.group ccmp
nmcli con modify "$SSID" wifi-sec.pairwise ccmp

nmcli con up "$SSID"
echo "Hotspot '$SSID' is now active"
