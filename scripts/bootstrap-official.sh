#!/bin/bash

# AstroOrange Bootstrap Script for Official Images
# Este script transforma una imagen oficial limpia en un AstroOrange Pro
# Ejecutar como root: sudo bash bootstrap-official.sh

set -e

LOG_FILE="/var/log/astro-bootstrap.log"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "=== AstroOrange Pro: Bootstrap de Imagen Oficial ==="
date

# 0. Crear Usuario de Trabajo
echo "[0/5] Configurando usuario del sistema..."
read -p "Introduce el nombre del usuario astronómico (ej: astro): " NEW_USER

if id "$NEW_USER" &>/dev/null; then
    echo "El usuario $NEW_USER ya existe. Usando este usuario."
else
    echo "Creando usuario $NEW_USER..."
    useradd -m -s /bin/bash "$NEW_USER"
    passwd "$NEW_USER"
    
    # Añadir a grupos críticos
    usermod -aG sudo,dialout,tty,video,input,plugdev "$NEW_USER"
    echo "✅ Usuario $NEW_USER creado y configurado."
fi

# Hacer que el script use este usuario para las configuraciones posteriores
BASE_USER="$NEW_USER"

# 1. Comprobar Hostname y Red
echo "[1/5] Configurando identidad y red..."
hostnamectl set-hostname astroorange
sed -i 's/127.0.1.1.*/127.0.1.1\tastroorange/' /etc/hosts

# Instalar dependencias iniciales si es posible
apt-get update
apt-get install -y network-manager curl

# Función para comprobar internet
check_internet() {
    ping -c 1 google.com &>/dev/null
}

# Bucle de conexión interactiva
while ! check_internet; do
    echo "--------------------------------------------------------"
    echo "⚠️  ADVERTENCIA: No se detectó conexión a Internet."
    echo "Necesito conexión para descargar el escritorio y las herramientas."
    echo "--------------------------------------------------------"
    
    # Crear Hotspot temporal si no hay WiFi
    WIFI_DEV=$(nmcli dev | grep wifi | awk '{print $1}' | head -n 1)
    if [ -n "$WIFI_DEV" ]; then
        echo "Levantando Hotspot de emergencia para que puedas entrar por SSH..."
        nmcli con delete Hotspot &>/dev/null || true
        nmcli con add type wifi ifname "$WIFI_DEV" mode ap con-name Hotspot ssid AstroOrange autoconnect yes
        nmcli con modify Hotspot ipv4.method shared ipv4.addresses 192.168.4.1/24
        nmcli con modify Hotspot wifi-sec.key-mgmt wpa-psk
        nmcli con modify Hotspot wifi-sec.psk "astroorange"
        nmcli con up Hotspot || true
        echo "✅ Hotspot 'AstroOrange' activo (IP 192.168.4.1)."
    fi

    echo ""
    echo "Acción requerida:"
    echo "1. Si estás por Serial/Teclado: Pulsa una tecla para lanzar 'nmtui' y conectar el WiFi."
    echo "2. Si estás por SSH (vía Ethernet/Hotspot): Lanza 'nmtui' en otra terminal."
    echo "3. Una vez conectado, el script continuará automáticamente."
    echo ""
    
    read -n 1 -s -p "Pulsa cualquier tecla para lanzar nmtui (o Ctrl+C para abortar)..."
    nmtui
    
    echo "Comprobando conexión..."
    sleep 5
done

echo "✅ Conexión a Internet detectada. Procediendo con la instalación..."

# 2. Instalación de Escritorio Ligero (XFCE4) y VNC
echo "[2/5] Instalando entorno de escritorio y acceso remoto..."
apt-get install -y --no-install-recommends \
    xfce4 xfce4-terminal xfce4-session \
    x11vnc websockify novnc xvfb \
    apt-transport-https curl wget gpg

# 3. Configurar Acceso VNC (vía Navegador en puerto 6080)
echo "[3/5] Configurando noVNC y auto-arranque..."

# Crear carpeta de logs para servicios
mkdir -p /var/log/astro

# Crear script de arranque del escritorio virtual
cat <<EOF > /usr/local/bin/astro-desktop-start.sh
#!/bin/bash
# 1. Iniciar X virtual
Xvfb :1 -screen 0 1280x720x24 &
export DISPLAY=:1
sleep 2
# 2. Iniciar sesión XFCE
startxfce4 &
# 3. Iniciar servidor VNC
x11vnc -display :1 -nopw -forever -shared -bg &
# 4. Iniciar Bridge noVNC (Puerto 6080)
/usr/share/novnc/utils/novnc_proxy --vnc localhost:5900 --listen 6080 &
EOF

chmod +x /usr/local/bin/astro-desktop-start.sh

# 4. Repositorios de Astronomía
echo "[4/5] Añadiendo repositorios PPA de Astronomía..."
add-apt-repository -y ppa:mutlaqja/ppa
add-apt-repository -y ppa:pch/phd2

# 5. Preparar el Wizard y Servicios
echo "[5/5] Registrando servicios de sistema..."

# Copiar el wizard si está en el directorio actual
if [ -f "./astro-wizard.sh" ]; then
    cp ./astro-wizard.sh /usr/local/bin/
    chmod +x /usr/local/bin/astro-wizard.sh
fi

# A. Servicio para el Escritorio Virtual (noVNC)
cat <<EOF > /etc/systemd/system/astro-desktop.service
[Unit]
Description=AstroOrange Virtual Desktop (noVNC)
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/astro-desktop-start.sh
User=$BASE_USER
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# B. Servicio para el Wizard (Desktop Startup)
# Configuramos el wizard para que se lance cuando se inicie la sesión XFCE
mkdir -p "/home/$BASE_USER/.config/autostart"
cat <<EOF > "/home/$BASE_USER/.config/autostart/astro-wizard.desktop"
[Desktop Entry]
Type=Application
Name=AstroOrange Wizard
Exec=lxterminal -e "/usr/local/bin/astro-wizard.sh"
OnlyShowIn=XFCE;
EOF
chown -R "$BASE_USER:$BASE_USER" "/home/$BASE_USER/.config"

systemctl daemon-reload
systemctl enable astro-desktop.service

# Crear flag para el wizard
touch "/home/$BASE_USER/.first_boot_wizard"
chown "$BASE_USER:$BASE_USER" "/home/$BASE_USER/.first_boot_wizard"

echo ""
echo "=== Bootstrap Completado ==="
echo "Por favor, reinicia el sistema: sudo reboot"
echo "Tras el reinicio, accede a: http://localhost:6080/vnc.html (o la IP de la placa)"
echo "El Wizard de instalación aparecerá automáticamente dentro del escritorio."
