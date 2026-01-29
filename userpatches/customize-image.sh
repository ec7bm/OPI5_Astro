#!/bin/bash
# AstroOrange Distro Builder - 2-Stage Workflow (STRICT)
# Stage 1: Temporary Setup User -> Stage 2: Real User & Install

set -e
export DEBIAN_FRONTEND=noninteractive

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== AstroOrange Distro Construction (2-Stage CLEAN) ===${NC}"

# ==================== 1. DEPENDENCIAS BASE ====================
echo -e "${GREEN}[1/5] Installing Base System...${NC}"

# Forzar modo no interactivo y manejar conflictos de configuracion automaticamente
export DEBIAN_FRONTEND=noninteractive
APT_OPTS="-y --no-install-recommends -o Dpkg::Options::=--force-confdef -o Dpkg::Options::=--force-confold"

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
mkdir -p /usr/share/backgrounds
if [ -f "/tmp/userpatches/astro-wallpaper.jpg" ]; then
    cp "/tmp/userpatches/astro-wallpaper.jpg" "/usr/share/backgrounds/astro-wallpaper.jpg"
fi

# Copy NASA gallery images for carousel
mkdir -p "$OPT_DIR/assets/gallery"
if [ -d "/tmp/userpatches/gallery" ]; then
    cp /tmp/userpatches/gallery/*.png "$OPT_DIR/assets/gallery/" 2>/dev/null || true
fi

# --- 0.1 XFCE Theme Configuration (Arc + Papirus) ---
# Configurar tema para el usuario setup (se heredará al usuario final)
SETUP_HOME="/home/$SETUP_USER"
mkdir -p "$SETUP_HOME/.config/xfce4/xfconf/xfce-perchannel-xml"
UP_SRC="/tmp/remaster-source/userpatches"

# Copiar configuraciones XFCE desde el repo
cp "$UP_SRC/xfce4/xfconf/xfce-perchannel-xml/xfwm4.xml" "$SETUP_HOME/.config/xfce4/xfconf/xfce-perchannel-xml/"
cp "$UP_SRC/xfce4/xfconf/xfce-perchannel-xml/xsettings.xml" "$SETUP_HOME/.config/xfce4/xfconf/xfce-perchannel-xml/"
cp "$UP_SRC/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml" "$SETUP_HOME/.config/xfce4/xfconf/xfce-perchannel-xml/"
cp "$UP_SRC/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml" "$SETUP_HOME/.config/xfce4/xfconf/xfce-perchannel-xml/"

# Fix wallpaper path (PNG instead of JPG)
sed -i 's/astro-wallpaper.jpg/astro-wallpaper.png/g' "$SETUP_HOME/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml"

# Asegurar que las carpetas existen y tienen permisos
chown -R $SETUP_USER:$SETUP_USER "$SETUP_HOME" || true
mkdir -p "$SETUP_HOME/.config/xfce4/xfconf/xfce-perchannel-xml"
chown -R $SETUP_USER:$SETUP_USER "$SETUP_HOME/.config"

# --- A. Master Scripts & Services (/opt/astroorange) ---
REM_SRC="/tmp/remaster-source"

echo "   📜 Installing scripts and services from repository..."

# Scripts
cp "$REM_SRC/scripts/astro-network.sh" "$OPT_DIR/bin/"
cp "$REM_SRC/scripts/astro-vnc.sh" "$OPT_DIR/bin/"
chmod +x "$OPT_DIR/bin/"*.sh

# Systemd Services
cp "$REM_SRC/systemd/astro-network.service" /etc/systemd/system/
cp "$REM_SRC/systemd/astro-vnc.service" /etc/systemd/system/

# Habilitar servicios
systemctl enable astro-network.service
systemctl enable astro-vnc.service
systemctl enable lightdm
systemctl enable ssh

# --- B. Wizard de Configuración ---
echo "   🧙 Installing Wizard..."
cp -r "$REM_SRC/wizard/"* "$OPT_DIR/wizard/"

# Autostart del Wizard
mkdir -p /etc/xdg/autostart
cp "$UP_SRC/xdg/autostart/astro-wizard.desktop" /etc/xdg/autostart/

# Permanent Menu Entry
mkdir -p /usr/share/applications
cp "$UP_SRC/xdg/applications/astro-wizard.desktop" /usr/share/applications/

# --- C. Headless & Networking Fixes ---
echo "   🖥️ Configuring Headless Support & Networking..."
mkdir -p /etc/X11/xorg.conf.d
cp "$UP_SRC/overlay/etc/X11/xorg.conf.d/99-dummy-display.conf" /etc/X11/xorg.conf.d/

# Ensure NetworkManager manages everything
sed -i 's/managed=false/managed=true/g' /etc/NetworkManager/NetworkManager.conf || true

# --- D. Fixes for Headless / Resolution ---
echo "   🖥️  Hardening Headless Resolution..."
rm -f /etc/X11/xorg.conf.d/20-modesetting.conf || true

# --- E. Visuals & Themes ---
echo -e "${GREEN}[5/5] Deploying AstroOrange Style...${NC}"
mkdir -p /usr/share/backgrounds
cp "$UP_SRC/astro-wallpaper.png" /usr/share/backgrounds/ || true

# System-wide XFCE Defaults (for any new user)
mkdir -p /etc/xdg/xfce4/xfconf/xfce-perchannel-xml
cp "$UP_SRC/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml" /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/

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
