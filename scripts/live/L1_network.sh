#!/bin/bash
# L1_network.sh - Hotspot de Rescate

set -e
echo "📡 Configurando Hotspot..."

# Detectar interfaz wifi
IFACE=$(nmcli -t -f DEVICE,TYPE device | grep wifi | cut -d: -f1 | head -n1)
[ -z "$IFACE" ] && IFACE="wlan0"

SSID="AstroOrange-Setup"
PASS="astrosetup"

# Crear el script de servicio
sudo mkdir -p /opt/astroorange/bin
cat <<EOF | sudo tee /opt/astroorange/bin/astro-network.sh
#!/bin/bash
IFACE="$IFACE"
SSID="$SSID"
PASS="$PASS"
sleep 15
if nmcli -t -f STATE g | grep -q "^connected"; then
    exit 0
fi
nmcli device set "\$IFACE" managed yes
nmcli con delete "\$SSID" 2>/dev/null || true
nmcli con add type wifi ifname "\$IFACE" con-name "\$SSID" autoconnect yes ssid "\$SSID" mode ap ipv4.method shared
nmcli con modify "\$SSID" wifi-sec.key-mgmt wpa-psk wifi-sec.psk "\$PASS"
nmcli con up "\$SSID"
EOF
sudo chmod +x /opt/astroorange/bin/astro-network.sh

# Crear el servicio de systemd
cat <<EOF | sudo tee /etc/systemd/system/astro-network.service
[Unit]
Description=AstroOrange Rescue Hotspot
After=NetworkManager.service

[Service]
Type=oneshot
ExecStart=/opt/astroorange/bin/astro-network.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable astro-network.service
sudo systemctl start astro-network.service

echo "✅ Hotspot configurado y lanzado. Mira si aparece en tu móvil: $SSID"
