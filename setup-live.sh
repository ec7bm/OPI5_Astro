#!/bin/bash
# 🍊 AstroOrange V2 - Live Setup Script
# Use this on a fresh official Orange Pi image to transform it into AstroOrange

set -e

# ==================== COLORS ====================
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}=== AstroOrange V2 Live Setup ===${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}❌ Please run as root (use sudo ./setup-live.sh)${NC}"
  exit 1
fi

BASE_DIR="$(pwd)"

# ==================== 1. PREPARE ASSETS ====================
echo -e "${GREEN}[1/5] Preparing assets...${NC}"
mkdir -p /tmp/remaster-source
cp -r "$BASE_DIR/scripts" "$BASE_DIR/systemd" "$BASE_DIR/wizard" "$BASE_DIR/userpatches" /tmp/remaster-source/

# ==================== 2. RUN CUSTOMIZATION ====================
echo -e "${GREEN}[2/5] Running customization...${NC}"
# customize-image.sh ahora se encarga de mover todo a /opt/astroorange
chmod +x /tmp/remaster-source/userpatches/customize-image.sh
bash /tmp/remaster-source/userpatches/customize-image.sh

# ==================== 3. LIVE FIXES (Themes & Network) ====================
echo -e "${GREEN}[3/5] Applying live fixes...${NC}"

# Detectar el usuario real que ejecutó sudo
REAL_USER=${SUDO_USER:-$USER}
REAL_HOME=$(getent passwd "$REAL_USER" | cut -d: -f6)

echo "Applying themes to user: $REAL_USER ($REAL_HOME)"

# Copiar configuraciones de tema al usuario actual (desde el repo recién inyectado)
mkdir -p "$REAL_HOME/.config/xfce4/xfconf/xfce-perchannel-xml"
cp -r /tmp/remaster-source/userpatches/xfce4/xfconf/xfce-perchannel-xml/* "$REAL_HOME/.config/xfce4/xfconf/xfce-perchannel-xml/" || true
chown -R "$REAL_USER:$REAL_USER" "$REAL_HOME/.config"

# Forzar NetworkManager como renderizador (evita conflictos con netplan en Ubuntu Server)
if [ -d "/etc/netplan" ]; then
    echo "Configuring Netplan to use NetworkManager..."
    cat <<EOF > /etc/netplan/01-network-manager-all.yaml
network:
  version: 2
  renderer: NetworkManager
EOF
    netplan apply || true
fi

echo -e "${GREEN}✅ AstroOrange Setup Completed!${NC}"
echo -e "${YELLOW}🔄 The system will now reboot into the Wizard.${NC}"
echo ""
read -p "Press Enter to reboot..." 
reboot
