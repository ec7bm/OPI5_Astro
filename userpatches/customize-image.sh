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
    python3-pip python3-setuptools

# Añadir PPAs de Astronomía de forma MANUAL (más fiable en chroot)
echo "Configurando repositorios PPA manualmente..."

# 1. PPA de Jas Mutlaq (INDI & KStars)
# Llave: F81D4F8C16975C8882D7B38333E72D44A5F2E962
gpg --no-default-keyring --keyring /etc/apt/trusted.gpg.d/mutlaqja.gpg --keyserver keyserver.ubuntu.com --recv-keys F81D4F8C16975C8882D7B38333E72D44A5F2E962
echo "deb [signed-by=/etc/apt/trusted.gpg.d/mutlaqja.gpg] https://ppa.launchpadcontent.net/mutlaqja/ppa/ubuntu jammy main" > /etc/apt/sources.list.d/mutlaqja.list

# 2. PPA de PHD2
# Llave: DAE27FFB13432BED41181735E3DBD5D75CFABF12
gpg --no-default-keyring --keyring /etc/apt/trusted.gpg.d/phd2.gpg --keyserver keyserver.ubuntu.com --recv-keys DAE27FFB13432BED41181735E3DBD5D75CFABF12
echo "deb [signed-by=/etc/apt/trusted.gpg.d/phd2.gpg] https://ppa.launchpadcontent.net/pch/phd2/ubuntu jammy main" > /etc/apt/sources.list.d/phd2.list

# Forzar actualización de listas
apt-get update -y

# ----------------------------------------------------------------------------
# 2. Instalación de Software Astronómico
# ----------------------------------------------------------------------------
echo "Instalando Stack Astronómico..."
apt-get install -y \
    indi-full kstars-bleeding phd2 \
    arduino arduino-core

# Instalar ASTAP y Base de datos de estrellas (H17/H18)
# Nota: Instalamos el binario para ARM64
wget https://www.hnsky.org/astap_arm64.deb -O /tmp/astap.deb
apt-get install -y /tmp/astap.deb
rm /tmp/astap.deb

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
echo "Configurando entorno Headless Virtual..."
apt-get install -y \
    xvfb x11vnc fluxbox \
    websockify novnc

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
ssid=RPI

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
ExecStart=/usr/bin/bash -c "Xvfb :1 -screen 0 1920x1080x24 & sleep 2; fluxbox & x11vnc -display :1 -forever -shared -nopw -rfbport 5900 & /usr/bin/websockify --web /opt/novnc 6080 localhost:5900"
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

# ----------------------------------------------------------------------------
# 7. Script de Primer Arranque (First Boot)
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
