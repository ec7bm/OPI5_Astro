#!/bin/bash
# First boot setup: Launch setup wizard

LOG=/var/log/firstboot.log
echo "--- Iniciando First Boot Setup ---" > $LOG
date >> $LOG

# 1. Ajuste de Hostname
hostnamectl set-hostname astroorange
sed -i 's/127.0.1.1.*/127.0.1.1\tastroorange/' /etc/hosts

# 2. Permisos de Usuario
chown -R AstroOrange:AstroOrange /home/AstroOrange

# 3. Lanzar wizard de configuración
echo "Lanzando wizard de configuración..." >> $LOG
/usr/local/bin/setup-wizard.sh

# 4. Deshabilitar auto-reinicio
echo "First boot completado." >> $LOG
systemctl disable firstboot.service
