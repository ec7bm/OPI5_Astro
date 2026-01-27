#!/bin/bash

# Este script se ejecuta dentro del chroot de Armbian durante el build.
# Sirve para instalar software, configurar servicios y personalizar el sistema.

set -e

# BLOQUEO DE DISPARADORES PELIGROSOS EN CHROOT
# Evita que se inicien servicios o se regenere el initramfs incorrectamente
echo "#!/bin/sh" > /usr/sbin/policy-rc.d
echo "exit 101" >> /usr/sbin/policy-rc.d
chmod +x /usr/sbin/policy-rc.d

# Prevenir actualización accidental del initramfs (Causa del error actual)
export INITRAMFS_SKIP=1
echo "update-initramfs: skipped by AstroOrange build"
alias update-initramfs='echo skipping update-initramfs'

echo "=== Iniciando personalización segura de AstroOrange ==="

# ----------------------------------------------------------------------------
# 1. Ajustes Básicos y Repositorios
# ----------------------------------------------------------------------------
export DEBIAN_FRONTEND=noninteractive

# Actualizar e instalar base
apt-get update
apt-get install -y --no-install-recommends \
    git build-essential wget curl software-properties-common \
    network-manager vim htop zip unzip tar xz-utils \
    python3-pip python3-setuptools gpsd gpsd-clients \
    libxml2-utils gsettings-desktop-schemas \
    network-manager-gnome tint2 zenity dnsmasq-base iptables

# Eliminar brltty (causa conflictos con dispositivos serial/USB de astronomía)
apt-get purge -y brltty || true

# Eliminar cloud-init para acelerar el arranque (como sugiere el Makefile)
echo "Acelerando arranque: eliminando cloud-init..."
apt-get purge -y cloud-init
rm -rf /etc/cloud/ /var/lib/cloud/

# Añadir PPAs de Astronomía de forma MANUAL (más fiable en chroot)
echo "Configurando repositorios PPA manualmente..."

# Asegurar que el directorio de llaves existe
mkdir -p /etc/apt/trusted.gpg.d/

# 1. PPA de Jas Mutlaq (INDI & KStars)
echo "Obteniendo llave PPA Mutlaqja..."
wget -qO - "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0xF81D4F8C16975C8882D7B38333E72D44A5F2E962" | gpg --dearmor > /etc/apt/trusted.gpg.d/mutlaqja.gpg
echo "deb [signed-by=/etc/apt/trusted.gpg.d/mutlaqja.gpg] https://ppa.launchpadcontent.net/mutlaqja/ppa/ubuntu jammy main" > /etc/apt/sources.list.d/mutlaqja.list

# 2. PPA de PHD2
echo "Obteniendo llave PPA PHD2..."
wget -qO - "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0xDAE27FFB13432BED41181735E3DBD5D75CFABF12" | gpg --dearmor > /etc/apt/trusted.gpg.d/phd2.gpg
echo "deb [signed-by=/etc/apt/trusted.gpg.d/phd2.gpg] https://ppa.launchpadcontent.net/pch/phd2/ubuntu jammy main" > /etc/apt/sources.list.d/phd2.list

# Forzar actualización de listas
apt-get update -y

# ----------------------------------------------------------------------------
# 1.5. Crear usuario AstroOrange
echo "Configurando usuario AstroOrange..."
if ! id "AstroOrange" &>/dev/null; then
    useradd -m -s /bin/bash AstroOrange
    echo "AstroOrange:astroorange" | chpasswd
    usermod -aG sudo AstroOrange
fi

# Configurar grupos para acceso a hardware
usermod -a -G dialout AstroOrange
usermod -a -G tty AstroOrange
usermod -a -G video AstroOrange

# 2. Configuración de Entorno Gráfico V2 (Pre-instalado)
# ----------------------------------------------------------------------------
echo "Instalando entorno gráfico XFCE4 completo..."
apt-get install -y --no-install-recommends \
    xfce4 xfce4-goodies lightdm \
    network-manager-gnome \
    firefox \
    fonts-noto-color-emoji

echo "Instalando infraestructura VNC y Wizard..."
apt-get install -y --no-install-recommends \
    tightvncserver \
    novnc \
    python3-websockify \
    python3-numpy \
    python3-gi \
    python3-gi-cairo \
    gir1.2-gtk-3.0 \
    dbus-x11 \
    net-tools

# Crear directorio para el Wizard V2
mkdir -p /opt/astro-wizard

# Preparar entorno noVNC
mkdir -p /opt/novnc
cp -r /usr/share/novnc/* /opt/novnc/ || true
ln -s /opt/novnc/vnc_auto.html /opt/novnc/index.html || true

# Habilitar servicios V2
systemctl enable hotspot.service
systemctl enable firstboot.service
systemctl enable vncserver@1.service
systemctl enable novnc.service
# systemctl enable wizard-autostart.service  <-- Se activará en firstboot, no aquí
systemctl enable gpsd

# LIMPIEZA DE DISPARADORES
rm -f /usr/sbin/policy-rc.d

# ----------------------------------------------------------------------------
# 7. Ajustes Finales (Swap, Auto-mount)
# ----------------------------------------------------------------------------
echo "Aplicando ajustes finales..."

# Crear archivo SWAP de 2GB (Vital para compilaciones o astrometria pesada futura)
echo "Creando archivo SWAP..."
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
echo "/swapfile swap swap defaults 0 0" >> /etc/fstab

# ----------------------------------------------------------------------------
# (Se delega configuración específica a firstboot.sh)

# Asegurar configuración de Polkit para que el usuario pueda gestionar redes sin sudo
mkdir -p /etc/polkit-1/localauthority/50-local.d/
cat <<EOF > /etc/polkit-1/localauthority/50-local.d/allow-network-manager.pkla
[Allow Network Manager]
Identity=unix-user:AstroOrange
Action=org.freedesktop.NetworkManager.*
ResultAny=yes
ResultInactive=yes
ResultActive=yes
EOF

# 9. Añadir rootwait y rootdelay
echo "extraargs=rootwait rootdelay=15" >> /boot/armbianEnv.txt

echo "=== Personalización finalizada correctamente ==="
