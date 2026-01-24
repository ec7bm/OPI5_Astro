#!/bin/bash

# Este script se ejecuta dentro del chroot de Armbian durante el build.
# Sirve para instalar software, configurar servicios y personalizar el sistema.

set -e

echo "=== Iniciando personalización de Astro OPI ==="

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
    libxml2-utils gsettings-desktop-schemas

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

# 2. Instalación de Software Astronómico
# ----------------------------------------------------------------------------
echo "Instalando Stack Astronómico..."

apt-get install -y \
    indi-full kstars-bleeding phd2 phdlogview \
    astrometry.net astrometry-data-tycho2 sextractor

# Instalar ASTAP (Astrometry) y Base de Datos D50
echo "Instalando ASTAP y base de datos de estrellas..."
# Nota: Usamos mirrors de SourceForge para mayor fiabilidad
wget https://master.dl.sourceforge.net/project/astap-program/star_databases/d50_star_database.deb -O /tmp/d50.deb || true
wget https://versaweb.dl.sourceforge.net/project/astap-program/linux_installer/astap_arm64.deb -O /tmp/astap.deb || true

if [ -f /tmp/astap.deb ]; then
    apt-get install -y /tmp/astap.deb /tmp/d50.deb || true
    rm /tmp/astap.deb /tmp/d50.deb
else
    echo "ERROR: No se pudo descargar ASTAP. Saltando..."
fi

# Instalar AstroDMx Capture (ARM64)
# Nota: El enlace puede variar según la versión. Se descarga la versión genérica de 64 bits para ARM.
echo "Instalando AstroDMx Capture..."
wget https://www.astrodmx-capture.org.uk/downloads/astrodmx-capture_2.11.2_arm64.deb -O /tmp/astrodmx.deb || true
if [ -f /tmp/astrodmx.deb ]; then
    apt-get install -y /tmp/astrodmx.deb
    rm /tmp/astrodmx.deb
fi

# ----------------------------------------------------------------------------
# 3. Entorno Headless (Xvfb + x11vnc + noVNC)
# ----------------------------------------------------------------------------
echo "Configurando entorno Headless Virtual con Estética..."
apt-get install -y \
    xvfb x11vnc fluxbox \
    websockify novnc \
    feh conky-all

# Crear directorio para noVNC si no existe
mkdir -p /opt/novnc
cp -r /usr/share/novnc/* /opt/novnc/ || true

# ----------------------------------------------------------------------------
# 4. Syncthing
# ----------------------------------------------------------------------------
echo "Instalando Syncthing..."
apt-get install -y syncthing

# ----------------------------------------------------------------------------
# 5. Configuración de Red (NetworkManager Hotspot)
# ----------------------------------------------------------------------------
# Crearemos un script de gestión de red que NM invocará o será un servicio.
# Por ahora pre-configuramos el Hotspot por defecto.

cat <<EOF > /etc/NetworkManager/system-connections/Hotspot.nmconnection
[connection]
id=Hotspot
uuid=$(cat /proc/sys/kernel/random/uuid)
type=wifi
autoconnect=false
interface-name=wlan0

[wifi]
mode=ap
ssid=OPI5_Astro

[wifi-security]
key-mgmt=wpa-psk
psk=password

[ipv4]
method=shared
address1=10.0.0.1/24

[ipv6]
addr-gen-mode=stable-privacy
method=ignore
EOF

chmod 600 /etc/NetworkManager/system-connections/Hotspot.nmconnection

# ----------------------------------------------------------------------------
# 6. Servicios Systemd Personalizados
# ----------------------------------------------------------------------------
# Servico VNC/noVNC (Headless Display)
cat <<EOF > /etc/systemd/system/astro-headless.service
[Unit]
Description=Astro Headless Virtual Display (Xvfb + VNC + noVNC)
After=network.target

[Service]
Type=simple
User=armbian
Environment=DISPLAY=:1
ExecStartPre=-/usr/bin/rm -f /tmp/.X1-lock
ExecStart=/usr/bin/bash -c "Xvfb :1 -screen 0 1920x1080x24 & sleep 2; feh --bg-fill /usr/share/backgrounds/astro-wallpaper.jpg; fluxbox & x11vnc -display :1 -forever -shared -nopw -rfbport 5900 & /usr/bin/websockify --web /opt/novnc 6080 localhost:5900 & sleep 5; conky -c /etc/conky/conky.conf"
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Servicio de Autoconmutación de Red (Simplificado)
cat <<EOF > /usr/local/bin/astro-net-check.sh
#!/bin/bash
# Esperar un poco al inicio
sleep 15
if ! nmcli -t -f TYPE,STATE dev | grep -q "wifi:connected"; then
    echo "No hay conexión Wifi conocida. Activando Hotspot..."
    nmcli con up Hotspot
fi
EOF
chmod +x /usr/local/bin/astro-net-check.sh

cat <<EOF > /etc/systemd/system/astro-network.service
[Unit]
Description=Astro Network Auto-Switcher
After=NetworkManager.service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/astro-net-check.sh

[Install]
WantedBy=multi-user.target
EOF

# Habilitar servicios
systemctl enable astro-headless
systemctl enable astro-network
systemctl enable gpsd

# ----------------------------------------------------------------------------
# 7. Ajustes Finales (Grupos, Swap, Auto-mount)
# ----------------------------------------------------------------------------
echo "Aplicando ajustes finales de AstroPi..."

# 1. Configurar grupos para el usuario 'armbian' (acceso a monturas/cámaras serie)
usermod -a -G dialout armbian
usermod -a -G tty armbian
usermod -a -G video armbian

# 2. Desactivar auto-montaje de cámaras (evita que el sistema bloquee la cámara antes que Ekos)
# Intentamos para MATE/GNOME schemes
dbus-run-session gsettings set org.mate.media-handling automount false || true

# 3. Crear archivo SWAP de 2GB (Mejora estabilidad con mucha carga de imágenes)
echo "Creando archivo SWAP..."
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
echo "/swapfile swap swap defaults 0 0" >> /etc/fstab

# ----------------------------------------------------------------------------
# 8. Script de Primer Arranque (First Boot)
# ----------------------------------------------------------------------------
echo "Configurando script de primer arranque..."
cat <<EOF > /usr/local/bin/astro-first-boot.sh
#!/bin/bash
# Este script se ejecuta una sola vez al primer inicio real.

LOG=/var/log/astro-first-boot.log
echo "--- Iniciando Script de Primer Arranque ---" > \$LOG
date >> \$LOG

# 1. Asegurar que el hotspot tiene la IP correcta (en caso de que NM falle)
nmcli con mod Hotspot ipv4.addresses 10.0.0.1/24 ipv4.method shared
nmcli con up Hotspot >> \$LOG 2>&1

# 2. Otros ajustes finales
hostnamectl set-hostname astro-opi

# 3. Marcar como completado y desactivar servicio
echo "Primer arranque completado." >> \$LOG
systemctl disable astro-first-boot.service
EOF

chmod +x /usr/local/bin/astro-first-boot.sh

cat <<EOF > /etc/systemd/system/astro-first-boot.service
[Unit]
Description=Astro First Boot Setup
After=NetworkManager.service
ConditionPathExists=!/var/log/astro-first-boot.log

[Service]
Type=oneshot
ExecStart=/usr/local/bin/astro-first-boot.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

systemctl enable astro-first-boot.service

echo "=== Personalización finalizada correctamente ==="
