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
echo -e "${GREEN}[1/4] Installing system dependencies...${NC}"
apt-get update
apt-get install -y python3-tk python3-pil python3-pil.imagetk network-manager wget curl

# 2. Create System Directories
echo -e "${GREEN}[2/4] Setting up directory structure...${NC}"
mkdir -p /opt/astroorange/wizard
mkdir -p /opt/astroorange/scripts
mkdir -p /opt/astroorange/wizard/gallery

# 3. Copy Files
echo -e "${GREEN}[3/4] Copying files...${NC}"
cp -r wizard/*.py /opt/astroorange/wizard/
cp -r scripts/*.sh /opt/astroorange/scripts/ 2>/dev/null || true

# Set permissions
chmod +x /opt/astroorange/wizard/*.py
chmod +x /opt/astroorange/scripts/*.sh

# 4. Create Desktop Shortcuts & Menu Entries
echo -e "${GREEN}[4/4] Creating application shortcuts...${NC}"

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

# Main Setup Wizard
create_shortcut "AstroOrange Setup" "python3 /opt/astroorange/wizard/astro-setup-wizard.py" "telescope" "Configure your AstroOrange system" "astro-setup-wizard.desktop"

# Individual Tools
create_shortcut "Astro User" "python3 /opt/astroorange/wizard/astro-user-gui.py" "system-users" "Manage main user" "astro-user.desktop"
create_shortcut "Astro Network" "python3 /opt/astroorange/wizard/astro-network-gui.py" "network-wireless" "Configure WiFi" "astro-network.desktop"
create_shortcut "Astro Software" "python3 /opt/astroorange/wizard/astro-software-gui.py" "system-software-install" "Install Astronomy Software" "astro-software.desktop"

echo ""
echo -e "${GREEN}✅ Installation Completed!${NC}"
echo "You can now find 'AstroOrange Setup' in your Applications menu under Science or Education."
echo ""
read -p "Do you want to run the Setup Wizard now? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python3 /opt/astroorange/wizard/astro-setup-wizard.py &
fi
