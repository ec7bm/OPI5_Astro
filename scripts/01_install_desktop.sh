#!/bin/bash
# 01_install_desktop.sh - AstroOrange Pro
set -e
echo "=== Actualizando sistema ==="
sudo apt update && sudo apt upgrade -y
echo "=== Instalando XFCE4 y componentes ==="
sudo apt install -y xfce4 xfce4-goodies lightdm
sudo systemctl enable lightdm
sudo systemctl set-default graphical.target
echo "=== Instalación completada. Reinicia con: sudo reboot ==="
