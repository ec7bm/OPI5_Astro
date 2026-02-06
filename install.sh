#!/bin/bash

# AstroOrange V2 - Universal Installer
# Installs AstroOrange tools on any Ubuntu/Armbian system
# Copyright (c) 2026 EC7BM

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}=== AstroOrange V2 Universal Installer ===${NC}"
echo "This script will install the AstroOrange Wizard and tools on your system."
echo "It works best on Ubuntu 22.04 LTS (Jammy) or Armbian."
echo ""

if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}Please run as root (sudo ./install.sh)${NC}"
  exit 1
fi

# 1. Install Dependencies
echo -e "${GREEN}[1/5] Installing system dependencies...${NC}"
apt-get update
# V13.2 Upgrade: Full dependencies for Wizards + noVNC
apt-get install -y \
    python3-tk python3-pil python3-pil.imagetk \
    network-manager wget curl git \
    x11vnc novnc websockify xvfb \
    dbus-x11 libglib2.0-bin

# 2. Create System Directories
echo -e "${GREEN}[2/5] Setting up directory structure...${NC}"
mkdir -p /opt/astroorange/wizard
mkdir -p /opt/astroorange/bin
mkdir -p /opt/astroorange/assets/gallery

# 3. Copy Files (Wizards, Scripts, Services)
echo -e "${GREEN}[3/5] Deploying AstroOrange modules...${NC}"

# Wizards & i18n
cp wizard/*.py /opt/astroorange/wizard/
chmod +x /opt/astroorange/wizard/*.py

# Master Scripts
cp scripts/astro-network.sh /opt/astroorange/bin/
cp scripts/astro-vnc.sh /opt/astroorange/bin/
chmod +x /opt/astroorange/bin/*.sh

# Systemd Services
echo "   ⚙️ Configuring systemd services..."
cp systemd/astro-network.service /etc/systemd/system/
cp systemd/astro-vnc.service /etc/systemd/system/

systemctl daemon-reload
systemctl enable astro-network.service
systemctl enable astro-vnc.service

# 4. Create Desktop Shortcuts & Menu Entries
echo -e "${GREEN}[4/5] Creating application shortcuts...${NC}"

# Helper function to create .desktop file
create_shortcut() {
    local name=$1
    local exec=$2
    local icon=$3
    local comment=$4
    local filename=$5
    
    cat > "/usr/share/applications/$filename" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=$name
Comment=$comment
Exec=$exec
Icon=$icon
Terminal=false
Categories=Science;Astronomy;Education;
EOF
}

# Desktop Entries
create_shortcut "AstroOrange Setup" "python3 /opt/astroorange/wizard/astro-setup-wizard.py" "telescope" "Configure your AstroOrange system" "astro-setup-wizard.desktop"
create_shortcut "Astro User" "python3 /opt/astroorange/wizard/astro-user-gui.py" "system-users" "Manage main user" "astro-user.desktop"
create_shortcut "Astro Network" "python3 /opt/astroorange/wizard/astro-network-gui.py" "network-wireless" "Configure WiFi" "astro-network.desktop"
create_shortcut "Astro Software" "python3 /opt/astroorange/wizard/astro-software-gui.py" "system-software-install" "Install Astronomy Software" "astro-software.desktop"

# 5. Finalize & Guidance
echo -e "${GREEN}[5/5] Finalizing installation...${NC}"
IP_ADDR=$(hostname -I | awk '{print $1}')

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  ✅ ASTROORANGE INSTALLED SUCCESSFULLY!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "  🌐 REMOTE DESKTOP (noVNC) is now active."
echo -e "     Connect via: ${BLUE}http://$IP_ADDR:6080/vnc.html${NC}"
echo ""
echo "  🧙 WIZARDS are available in your Applications menu."
echo "     (Science / Education -> AstroOrange Setup)"
echo ""
echo "  ⚠️ IMPORTANT: If you just installed this on a fresh Ubuntu,"
echo "     reboot now to ensure all services start correctly."
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

read -p "Do you want to run the Setup Wizard now? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python3 /opt/astroorange/wizard/astro-setup-wizard.py &
fi

