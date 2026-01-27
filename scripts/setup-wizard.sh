#!/bin/bash
# setup-wizard.sh - Interactive Network Configuration Wizard
set -e

CONF_DIR="/etc/astroorange"
CONF_FILE="${CONF_DIR}/network.conf"
FLAG_DIR="/var/lib/astroorange"
STAGE2_FLAG="${FLAG_DIR}/stage2-pending"

echo "========================================="
echo "  AstroOrange - Asistente de Red"
echo "========================================="
echo ""

# Crear directorios si no existen
mkdir -p "${CONF_DIR}"
mkdir -p "${FLAG_DIR}"

# 1. Configuración WiFi
echo "=== Configuración WiFi ==="
read -p "SSID de tu red WiFi: " WIFI_SSID
read -sp "Contraseña WiFi: " WIFI_PASS
echo ""

# 2. Configuración IP
echo ""
echo "=== Configuración de IP ==="
echo "1) DHCP (automática)"
echo "2) IP Estática"
read -p "Selecciona opción [1/2]: " IP_OPTION

if [ "$IP_OPTION" == "2" ]; then
    read -p "IP Estática (ej: 192.168.1.100): " STATIC_IP
    read -p "Gateway (ej: 192.168.1.1): " GATEWAY
    read -p "DNS (ej: 8.8.8.8): " DNS
    IP_MODE="static"
else
    IP_MODE="dhcp"
    STATIC_IP=""
    GATEWAY=""
    DNS=""
fi

# Guardar configuración
cat > "${CONF_FILE}" <<EOF
WIFI_SSID="${WIFI_SSID}"
WIFI_PASS="${WIFI_PASS}"
IP_MODE="${IP_MODE}"
STATIC_IP="${STATIC_IP}"
GATEWAY="${GATEWAY}"
DNS="${DNS}"
EOF

chmod 600 "${CONF_FILE}"

echo ""
echo "=== Aplicando configuración de red ==="

# Configurar WiFi con NetworkManager
if [ "$IP_MODE" == "static" ]; then
    nmcli con add type wifi ifname wlan0 con-name "AstroWiFi" ssid "${WIFI_SSID}"
    nmcli con modify "AstroWiFi" wifi-sec.key-mgmt wpa-psk
    nmcli con modify "AstroWiFi" wifi-sec.psk "${WIFI_PASS}"
    nmcli con modify "AstroWiFi" ipv4.method manual
    nmcli con modify "AstroWiFi" ipv4.addresses "${STATIC_IP}/24"
    nmcli con modify "AstroWiFi" ipv4.gateway "${GATEWAY}"
    nmcli con modify "AstroWiFi" ipv4.dns "${DNS}"
else
    nmcli dev wifi connect "${WIFI_SSID}" password "${WIFI_PASS}"
fi

# Crear flag para stage 2
touch "${STAGE2_FLAG}"

echo ""
echo "========================================="
echo "  Configuración completada"
echo "========================================="
echo ""
echo "El sistema se reiniciará en 10 segundos..."
echo "Después del reinicio, la instalación"
echo "continuará AUTOMÁTICAMENTE."
echo ""
echo "Puedes seguir el progreso en:"
echo "  /var/log/astroorange-install.log"
echo ""

sleep 10
reboot
