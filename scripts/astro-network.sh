#!/bin/bash
# AstroOrange Auto Hotspot (Runtime) - FINAL HARDWARE-VERIFIED
sleep 15
IFACE=$(nmcli -t -f DEVICE,TYPE device | grep wifi | cut -d: -f1 | head -n1)
[ -z "$IFACE" ] && IFACE="wlan0"

# ¿Hay conexión a INTERNET real?
if ping -c 1 -W 2 8.8.8.8 >/dev/null 2>&1; then
    echo "Internet detectado via Ethernet/WiFi. Hotspot no necesario."
    exit 0
fi

echo "Sin internet. Iniciando Hotspot de compatibilidad..."
sudo nmcli con delete "astroorange-ap" 2>/dev/null || true

# Crear conexión AP con parámetros de compatibilidad masiva
sudo nmcli con add type wifi ifname "$IFACE" con-name "astroorange-ap" autoconnect yes ssid "AstroOrange-Setup" mode ap connection.interface-name "$IFACE"

# Configuración de IP y DHCP
sudo nmcli con modify "astroorange-ap" ipv4.method shared ipv4.addresses 10.42.0.1/24

# SEGURIDAD RELAJADA (WPA2-PSK Estándar) - Evita el error '802.1X timeout'
sudo nmcli con modify "astroorange-ap" wifi-sec.key-mgmt wpa-psk
sudo nmcli con modify "astroorange-ap" wifi-sec.psk "astrosetup"

# FORZAR BANDA BG (2.4GHz) - Máxima estabilidad para driver Rockchip
sudo nmcli con modify "astroorange-ap" 802-11-wireless.band bg

echo "Activando..."
sudo nmcli con up "astroorange-ap"
