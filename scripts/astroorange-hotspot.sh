#!/bin/bash
# astroorange-hotspot.sh - Hotspot auto-switcher

sleep 10

# Check if WiFi is connected
if ! nmcli -t -f TYPE,STATE dev | grep -q "wifi:connected"; then
    echo "No WiFi detected. Activating hotspot..."
    nmcli con up AstroOrange-Hotspot 2>/dev/null || true
fi
