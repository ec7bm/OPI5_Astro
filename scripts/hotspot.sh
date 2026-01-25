#!/bin/bash
# Hotspot Auto-Switcher logic
# SSID: AstroOrange | IP: 192.168.4.1

# 1. Esperar a que el sistema se asiente
sleep 20

# 2. Comprobar si ya estamos conectados a un WiFi (modo cliente)
if ! nmcli -t -f TYPE,STATE dev | grep -q "wifi:connected"; then
    echo "No se detectó conexión WiFi cliente. Levantando Hotspot 'AstroOrange'..."
    nmcli con up Hotspot
fi
