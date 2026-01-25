#!/bin/bash
# First boot setup: Hostname and FS adjustments

LOG=/var/log/firstboot.log
echo "--- Iniciando First Boot Setup ---" > $LOG
date >> $LOG

# 1. Ajuste de Hostname
hostnamectl set-hostname astro-opi
sed -i 's/127.0.1.1.*/127.0.1.1\tastro-opi/' /etc/hosts

# 2. Permisos de Usuario
chown -R OPI5_Astro:OPI5_Astro /home/OPI5_Astro

# 3. Finalizar y deshabilitar auto-reinicio
echo "First boot completado." >> $LOG
systemctl disable firstboot.service
