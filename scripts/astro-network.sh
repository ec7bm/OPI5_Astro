#!/bin/bash
# AstroOrange Auto Hotspot (Runtime) - V4.5 ROBUST
# Este script se ejecuta al inicio para asegurar que siempre haya una forma de entrar.

echo "---[ AstroOrange Network Service V4.5 ]---"

# 1. PEQUEÑA ESPERA INICIAL Y BUCLE DE DETECCIÓN (Máximo 30 segundos)
# Damos tiempo a que NetworkManager escanee y se conecte a redes conocidas.
for i in {1..15}; do
    echo "Verificando estado de red ($i/15)..."
    # ¿Tenemos internet real?
    if ping -c 1 -W 2 8.8.8.8 >/dev/null 2>&1; then
        echo "Internet detectado via Ethernet o WiFi. No se requiere Hotspot."
        exit 0
    fi
    sleep 2
done

# 2. SI LLEGAMOS AQUÍ, NO HAY INTERNET. LANZAMOS HOTSPOT DE RESCATE.
echo "No se detecto conexion a Internet. Iniciando Hotspot de rescate..."

# Identificar interfaz wifi
IFACE=$(nmcli -t -f DEVICE,TYPE device | grep wifi | cut -d: -f1 | head -n1)
[ -z "$IFACE" ] && IFACE="wlan0"

# Limpiar conexiones de AP previas para evitar conflictos
sudo nmcli con delete "astroorange-ap" 2>/dev/null || true

# Crear conexión AP
sudo nmcli con add type wifi ifname "$IFACE" con-name "astroorange-ap" autoconnect yes ssid "AstroOrange-Setup" mode ap connection.interface-name "$IFACE"

# Configuración de IP (10.42.0.1 es el estándar de NM para compartición)
sudo nmcli con modify "astroorange-ap" ipv4.method shared ipv4.addresses 10.42.0.1/24

# Seguridad WPA2-PSK (astrosetup)
sudo nmcli con modify "astroorange-ap" wifi-sec.key-mgmt wpa-psk
sudo nmcli con modify "astroorange-ap" wifi-sec.psk "astrosetup"

# Forzar banda 2.4GHz para máxima compatibilidad con drivers Rockchip/Realtek
sudo nmcli con modify "astroorange-ap" 802-11-wireless.band bg

echo "Activando Hotspot 'AstroOrange-Setup'..."
sudo nmcli con up "astroorange-ap"
