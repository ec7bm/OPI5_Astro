#!/bin/bash
# AstroOrange Distro Builder - 2-Stage Workflow (STRICT)
# Stage 1: Temporary Setup User -> Stage 2: Real User & Install

# ==================== 0. AUTOMATION & PATHS (V13.2.5 MASTER) ====================
export DEBIAN_FRONTEND=noninteractive
APT_OPTS="-y --no-install-recommends -o Dpkg::Options::=--force-confdef -o Dpkg::Options::=--force-confold"

REM_SRC="/tmp/remaster-source"
UP_SRC="$REM_SRC/userpatches"

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== AstroOrange Distro Construction (2-Stage CLEAN) ===${NC}"

# ==================== 1. DEPENDENCIAS BASE ====================
echo -e "${GREEN}[1/5] Installing Base System...${NC}"



# Repositorios (Mozilla PPA para Firefox)
apt-get update
apt-get install $APT_OPTS software-properties-common
add-apt-repository -y universe
add-apt-repository -y ppa:mozillateam/ppa
echo '
Package: *
Pin: release o=LP-PPA-mozillateam
Pin-Priority: 1001
' > /etc/apt/preferences.d/mozilla-firefox
apt-get update

# Paquetes esenciales (INCLUYENDO dnsmasq-base para Hotspot + Temas modernos)
apt-get install $APT_OPTS \
    xfce4 xfce4-goodies lightdm lightdm-gtk-greeter \
    network-manager network-manager-gnome dnsmasq-base \
    openssh-server \
    xserver-xorg-video-dummy \
    python3-pil python3-pil.imagetk \
    libglib2.0-bin \
    x11vnc xvfb novnc websockify \
    python3 python3-pip python3-tk \
    curl wget git nano htop \
    firefox \
    dbus-x11 \
    feh \
    onboard \
    arc-theme papirus-icon-theme

# Fix: Desactivar dnsmasq de sistema para que no choque con NetworkManager
systemctl stop dnsmasq || true
systemctl disable dnsmasq || true
systemctl mask dnsmasq

# V11.5: Create mandatory groups for the wizard
groupadd vnc || true
groupadd novnc || true


# ==================== 2. USUARIO SETUP (TEMPORAL) ====================
echo -e "${GREEN}[2/5] Creating Setup User...${NC}"
SETUP_USER="astro-setup"
SETUP_PASS="setup"

if ! id "$SETUP_USER" &>/dev/null; then
    useradd -m -s /bin/bash -G sudo,dialout,video,input "$SETUP_USER"
    echo "$SETUP_USER:$SETUP_PASS" | chpasswd
fi

# NOPASSWD para el wizard
echo "$SETUP_USER ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/astro-setup
chmod 0440 /etc/sudoers.d/astro-setup

# Configurar LightDM para autologin en SETUP
mkdir -p /etc/lightdm/lightdm.conf.d
cat <<EOF > /etc/lightdm/lightdm.conf.d/50-setup.conf
[Seat:*]
autologin-user=$SETUP_USER
autologin-session=xfce
EOF

# ==================== 3. MODULOS (/opt/astroorange) ====================
echo -e "${GREEN}[3/5] Installing Modules...${NC}"
OPT_DIR="/opt/astroorange"
mkdir -p "$OPT_DIR/bin" "$OPT_DIR/wizard" "$OPT_DIR/assets"

# --- 0. ASSETS (Wallpaper/Logo/Gallery) ---
# --- 0. ASSETS (Wallpaper/Logo/Gallery) ---
mkdir -p /usr/share/backgrounds
# V10.8: Brute Force Wallpaper Logic (No find, just copy)
# Try copying various extensions to the canonical path
# V11.0: Brute Force Wallpaper Logic (Using Correct Path)
# Try copying various extensions to the canonical path
cp "$UP_SRC/astro-wallpaper.png" /usr/share/backgrounds/astro-wallpaper.png 2>/dev/null || true
cp "$UP_SRC/astro-wallpaper.jpg" /usr/share/backgrounds/astro-wallpaper.png 2>/dev/null || true
cp "$UP_SRC/astro-wallpaper.jpeg" /usr/share/backgrounds/astro-wallpaper.png 2>/dev/null || true

if [ -f "/usr/share/backgrounds/astro-wallpaper.png" ]; then
    echo "   🖼️  Wallpaper installed successfully to /usr/share/backgrounds/astro-wallpaper.png"
else
    echo "   ⚠️  No custom wallpaper found in userpatches!"
fi

# V11.1 NUCLEAR OPTION: Overwrite System Defaults
# XFCE likes to revert to 'xfce-blue.jpg' or 'xfce-stripes.png'. We replace them.
echo "   ☢️  Enforcing Wallpaper (Nuclear Option)..."
TARGET_WP="/usr/share/backgrounds/astro-wallpaper.png"
if [ -f "$TARGET_WP" ]; then
    # Overwrite remote/default XFCE backgrounds
    find /usr/share/backgrounds/xfce -name "*.jpg" -exec cp "$TARGET_WP" {} \; 2>/dev/null || true
    find /usr/share/backgrounds/xfce -name "*.png" -exec cp "$TARGET_WP" {} \; 2>/dev/null || true
    
    # Ensure standard paths exist
    mkdir -p /usr/share/backgrounds/xfce
    cp "$TARGET_WP" /usr/share/backgrounds/xfce/xfce-blue.jpg
    cp "$TARGET_WP" /usr/share/backgrounds/xfce/xfce-stripes.png
    cp "$TARGET_WP" /usr/share/backgrounds/xfce/xfce-teal.jpg
fi

# Copy NASA gallery images for carousel
mkdir -p "$OPT_DIR/assets/gallery"
if [ -d "$REM_SRC/userpatches/gallery" ]; then
    cp "$REM_SRC/userpatches/gallery/"*.png "$OPT_DIR/assets/gallery/" 2>/dev/null || true
fi


# --- 0.1 XFCE Theme Configuration (Arc + Papirus) ---
# Configurar tema para el usuario setup (se heredará al usuario final)
SETUP_HOME="/home/$SETUP_USER"
mkdir -p "$SETUP_HOME/.config/xfce4/xfconf/xfce-perchannel-xml"
# UP_SRC defined at top


# Copiar configuraciones XFCE desde el repo (V13.2.2 Path Fix)
cp "$REM_SRC/userpatches/xfce4/xfconf/xfce-perchannel-xml/xfwm4.xml" "$SETUP_HOME/.config/xfce4/xfconf/xfce-perchannel-xml/"
cp "$REM_SRC/userpatches/xfce4/xfconf/xfce-perchannel-xml/xsettings.xml" "$SETUP_HOME/.config/xfce4/xfconf/xfce-perchannel-xml/"
cp "$REM_SRC/userpatches/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml" "$SETUP_HOME/.config/xfce4/xfconf/xfce-perchannel-xml/"
cp "$REM_SRC/userpatches/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml" "$SETUP_HOME/.config/xfce4/xfconf/xfce-perchannel-xml/"


# Fix wallpaper path (PNG instead of JPG)
sed -i 's/astro-wallpaper.jpg/astro-wallpaper.png/g' "$SETUP_HOME/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml"

# Asegurar que las carpetas existen y tienen permisos
chown -R $SETUP_USER:$SETUP_USER "$SETUP_HOME" || true
mkdir -p "$SETUP_HOME/.config/xfce4/xfconf/xfce-perchannel-xml"
chown -R $SETUP_USER:$SETUP_USER "$SETUP_HOME/.config"

# --- A. Master Scripts & Services (/opt/astroorange) ---
echo "   📜 Installing scripts and services from repository..."


# Scripts (V13.2.2 MASTER PATHS)
cp "$REM_SRC/scripts/astro-network.sh" "$OPT_DIR/bin/"
cp "$REM_SRC/scripts/astro-vnc.sh" "$OPT_DIR/bin/"
chmod +x "$OPT_DIR/bin/"*.sh


# Systemd Services (V13.2.2 MASTER PATHS)
cp "$REM_SRC/systemd/astro-network.service" /etc/systemd/system/
cp "$REM_SRC/systemd/astro-vnc.service" /etc/systemd/system/


# Habilitar servicios
systemctl enable astro-network.service
systemctl enable astro-vnc.service
systemctl enable lightdm
systemctl enable ssh

# --- B. Wizard de Configuración (MODULAR V5.0) ---
echo "   🧙 Installing Modular Wizards..."
cp -r "$REM_SRC/wizard/"* "$OPT_DIR/wizard/"

# Autostart del setup inicial
mkdir -p /etc/xdg/autostart
cp "$REM_SRC/userpatches/xdg/autostart/astro-wizard.desktop" /etc/xdg/autostart/


# Menu Entries (Modular Tools) -- ALL of them into System Menu
mkdir -p /usr/share/applications
cp "$REM_SRC/userpatches/xdg/applications/astro-network.desktop" /usr/share/applications/
cp "$REM_SRC/userpatches/xdg/applications/astro-user.desktop" /usr/share/applications/
cp "$REM_SRC/userpatches/xdg/applications/astro-software.desktop" /usr/share/applications/
cp "$REM_SRC/userpatches/xdg/applications/astro-setup.desktop" /usr/share/applications/


# Desktop Shortcuts (Exclude Setup)
# Setup is only for first run or menu access, keeping desktop clean
mkdir -p /home/$SETUP_USER/Desktop
cp "$REM_SRC/userpatches/xdg/applications/astro-network.desktop" /home/$SETUP_USER/Desktop/
cp "$REM_SRC/userpatches/xdg/applications/astro-user.desktop" /home/$SETUP_USER/Desktop/
cp "$REM_SRC/userpatches/xdg/applications/astro-software.desktop" /home/$SETUP_USER/Desktop/

chmod +x /home/$SETUP_USER/Desktop/*.desktop
chown -R $SETUP_USER:$SETUP_USER /home/$SETUP_USER/Desktop

# --- C. Headless & Networking Fixes ---
echo "   🖥️ Configuring Headless Support & Networking..."
mkdir -p /etc/X11/xorg.conf.d
cp "$REM_SRC/userpatches/overlay/etc/X11/xorg.conf.d/99-dummy-display.conf" /etc/X11/xorg.conf.d/


# Ensure NetworkManager manages everything
cat <<EOF > /etc/NetworkManager/NetworkManager.conf
[main]
plugins=ifupdown,keyfile

[ifupdown]
managed=true

[device]
type=ethernet
managed=true

[keyfile]
unmanaged-devices=none

[device-mac-randomization]
wifi.scan-rand-mac-address=no

[connectivity]
uri=http://nmcheck.gnome.org/check_network_status.txt
EOF





# V11.3: CLEAN NETWORK INTERFACES (Full NM control)
# Static definitions in /etc/network/interfaces can block NM from managing eth/wifi
cat <<EOF > /etc/network/interfaces
auto lo
iface lo inet loopback
EOF

# V13.1 Fix: Force NetworkManager in Netplan
echo "   🌐 Configuring Netplan for NetworkManager..."
rm -f /etc/netplan/*.yaml || true
cat <<EOF > /etc/netplan/01-network-manager-all.yaml
network:
  version: 2
  renderer: NetworkManager
EOF
chmod 600 /etc/netplan/01-network-manager-all.yaml


# V13.1 Update: Let NM handle Ethernet automatically (remove manual static profile)
echo "   🌐 Allowing NM to control Ethernet automatically..."
rm -f /etc/NetworkManager/system-connections/Wired.nmconnection




# --- D. Fixes for Headless / Resolution ---
echo "   🖥️  Hardening Headless Resolution..."
rm -f /etc/X11/xorg.conf.d/20-modesetting.conf || true

# --- E. Visuals & Themes ---
echo -e "${GREEN}[5/5] Deploying AstroOrange Style...${NC}"
mkdir -p /usr/share/backgrounds

# Fallback: Enforce standardized path again
if [ ! -f "/usr/share/backgrounds/astro-wallpaper.png" ]; then
    echo "   ⚠️  CRITICAL: Wallpaper missing. Copying fallback if available."
    cp "$REM_SRC/userpatches/astro-wallpaper.png" "/usr/share/backgrounds/astro-wallpaper.png" 2>/dev/null || true
fi


# System-wide XFCE Defaults (for any new user)
mkdir -p /etc/xdg/xfce4/xfconf/xfce-perchannel-xml
cp "$REM_SRC/userpatches/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml" /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/


# LightDM Background
if [ -f "/etc/lightdm/lightdm-gtk-greeter.conf" ]; then
    sed -i 's|^#background=.*|background=/usr/share/backgrounds/astro-wallpaper.png|' /etc/lightdm/lightdm-gtk-greeter.conf
    sed -i 's|^background=.*|background=/usr/share/backgrounds/astro-wallpaper.png|' /etc/lightdm/lightdm-gtk-greeter.conf
fi

# --- F. Permissions & Sudoers ---
echo "   🔑 Configuring Permissions..."
echo "%sudo ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/90-astro-users
chmod 440 /etc/sudoers.d/90-astro-users

echo -e "${GREEN}✅ Base Distro Ready! (CLEAN)${NC}"
