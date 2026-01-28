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
mkdir -p /tmp/userpatches
cp -r "$BASE_DIR/userpatches/"* /tmp/userpatches/

# ==================== 2. INJECT SYSTEM SCRIPTS ====================
echo -e "${GREEN}[2/5] Installing system scripts...${NC}"
mkdir -p /usr/local/bin

if [ -d "$BASE_DIR/scripts" ]; then
    cp "$BASE_DIR/scripts"/*.sh /usr/local/bin/
    chmod +x /usr/local/bin/*.sh
fi

# ==================== 3. INSTALL SERVICES ====================
echo -e "${GREEN}[3/5] Installing systemd services...${NC}"
if [ -d "$BASE_DIR/systemd" ]; then
    cp "$BASE_DIR/systemd"/*.service /etc/systemd/system/
fi

# ==================== 4. RUN CUSTOMIZATION ====================
echo -e "${GREEN}[4/5] Running customization (this may take 10-15 min)...${NC}"
chmod +x /tmp/userpatches/customize-image.sh
bash /tmp/userpatches/customize-image.sh

# ==================== 5. FINAL TOUCHES ====================
echo -e "${GREEN}[5/5] Finalizing...${NC}"

# Ensure wizard folder exists (it is created by customize-image.sh but let's be safe)
if [ -d "$BASE_DIR/wizard" ]; then
    mkdir -p /opt/astroorange/wizard
    cp -r "$BASE_DIR/wizard"/* /opt/astroorange/wizard/
fi

echo -e "${GREEN}✅ AstroOrange Setup Completed!${NC}"
echo -e "${YELLOW}🔄 The system will now reboot into the Wizard.${NC}"
echo ""
read -p "Press Enter to reboot..." 
reboot
