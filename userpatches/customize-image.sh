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
# 1.5. Crear usuario OPI5_Astro PRIMERO (antes de configurar servicios)
# ----------------------------------------------------------------------------
echo "Configurando usuario OPI5_Astro..."
if ! id "OPI5_Astro" &>/dev/null; then
    useradd -m -s /bin/bash OPI5_Astro
    echo "OPI5_Astro:password" | chpasswd
    usermod -aG sudo OPI5_Astro
fi

# Configurar grupos para acceso a hardware
usermod -a -G dialout OPI5_Astro
usermod -a -G tty OPI5_Astro
usermod -a -G video OPI5_Astro

# 2. Preparación para el Software Astronómico (PPAs)
# ----------------------------------------------------------------------------
echo "Configurando repositorios para el Wizard..."

# Nota: No instalamos nada aquí para mantener la imagen ligera. 
# El Wizard se encargará de la instalación post-arranque.

# ----------------------------------------------------------------------------
# 3. Entorno Headless (Xvfb + x11vnc + noVNC)
# ----------------------------------------------------------------------------
echo "Configurando entorno Headless Virtual con Estética y Gestión de Red..."
apt-get install -y \
    xvfb x11vnc fluxbox \
    websockify novnc \
    feh conky-all lxterminal

# Crear directorio para noVNC y configurar index automático
mkdir -p /opt/novnc
cp -r /usr/share/novnc/* /opt/novnc/ || true
ln -s /opt/novnc/vnc_auto.html /opt/novnc/index.html || true

# Configurar Fluxbox para que lance nm-applet y tint2 automáticamente
# (El usuario OPI5_Astro ya existe en este punto)
mkdir -p /home/OPI5_Astro/.fluxbox
cat <<EOF > /home/OPI5_Astro/.fluxbox/startup
#!/bin/sh
# Lanzar applet de red (nm-applet)
nm-applet &
# Lanzar barra de tareas ligera
tint2 &
# Iniciar Fluxbox
exec fluxbox
EOF
# Crear flag de primer arranque para el Wizard
touch /home/OPI5_Astro/.first_boot_wizard
chmod +x /home/OPI5_Astro/.fluxbox/startup
chown -R OPI5_Astro:OPI5_Astro /home/OPI5_Astro/.fluxbox /home/OPI5_Astro/.first_boot_wizard

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
User=OPI5_Astro
Environment=DISPLAY=:1
ExecStartPre=-/usr/bin/rm -f /tmp/.X1-lock
ExecStart=/usr/bin/bash -c "Xvfb :1 -screen 0 1920x1080x24 & sleep 2; feh --bg-fill /usr/share/backgrounds/astro-nebula-1.jpg; fluxbox & x11vnc -display :1 -forever -shared -nopw -rfbport 5900 & /usr/bin/websockify --web /opt/novnc 6080 localhost:5900 & sleep 10; [ -f /home/OPI5_Astro/.first_boot_wizard ] && /usr/local/bin/astro-wizard.sh; conky -c /etc/conky/conky.conf"
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
# 7. Ajustes Finales (Swap, Auto-mount)
# ----------------------------------------------------------------------------
echo "Aplicando ajustes finales de AstroPi..."

# 1. Desactivar auto-montaje de cámaras
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
echo "Primer arranque completado de OPI5_Astro." >> \$LOG
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

# Asegurar que Cockpit no pida autenticación pesada para red (opcional, permite mayor control web)
mkdir -p /etc/polkit-1/localauthority/50-local.d/
cat <<EOF > /etc/polkit-1/localauthority/50-local.d/allow-cockpit-network.pkla
[Allow Cockpit to manage network]
Identity=unix-user:OPI5_Astro
Action=org.freedesktop.NetworkManager.*
ResultAny=yes
ResultInactive=yes
ResultActive=yes
EOF

# 9. Añadir retardo de arranque (rootdelay) para mayor estabilidad de montaje
echo "extraargs=rootdelay=15" >> /boot/armbianEnv.txt

echo "=== Personalización finalizada correctamente ==="
