#!/bin/bash
# AstroOrange Auto Hotspot (Runtime) - Ultra Robust Version

# Esperar a que el sistema y el WiFi despierten
sleep 25

# Buscar interfaz WiFi (reintenta si es necesario)
IFACE=$(nmcli -t -f DEVICE,TYPE device | grep wifi | cut -d: -f1 | head -n1)
[ -z "$IFACE" ] && IFACE="wlan0"

CON_NAME="astroorange-ap"
SSID="AstroOrange-Setup"
PASS="astrosetup"

# ¿Hay conexión a INTERNET real? (Si no hay ping, levantamos rescate)
if ping -c 1 -W 2 8.8.8.8 >/dev/null 2>&1; then
    echo "Internet detectado. Hotspot no necesario."
    exit 0
fi

echo "Sin internet. Iniciando Hotspot de rescate..."

# Limpiar posibles restos
nmcli device set "$IFACE" managed yes 2>/dev/null || true
nmcli con delete "$CON_NAME" 2>/dev/null || true

# Crear conexión AP
nmcli con add type wifi ifname "$IFACE" con-name "$CON_NAME" \
    autoconnect yes ssid "$SSID" \
    mode ap ipv4.method shared

# FORZAR WPA2 (Crucial para compatibilidad OPi5 Pro)
nmcli con modify "$CON_NAME" \
    wifi-sec.key-mgmt wpa-psk \
    wifi-sec.psk "$PASS" \
    wifi-sec.proto rsn \
    wifi-sec.group ccmp \
    wifi-sec.pairwise ccmp

nmcli con up "$CON_NAME"
echo "Hotspot '$SSID' is now active!"
