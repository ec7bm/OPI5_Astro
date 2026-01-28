#!/bin/bash
# L0_base.sh - Entorno Gráfico y Herramientas Base

set -e
export DEBIAN_FRONTEND=noninteractive

echo "📦 Instalando XFCE y dependencias..."
sudo apt-get update
sudo apt-get install -y --no-install-recommends \
    xfce4 xfce4-goodies lightdm lightdm-gtk-greeter \
    network-manager network-manager-gnome \
    python3 python3-pip python3-tk \
    curl wget git nano htop dbus-x11 feh onboard

# Automatización del escritorio
echo "⚙️ Forzando LightDM como gestor por defecto..."
sudo systemctl stop gdm3 sddm nodm 2>/dev/null || true
echo "/usr/sbin/lightdm" | sudo tee /etc/X11/default-display-manager
sudo systemctl enable lightdm
sudo systemctl restart lightdm || echo "⚠️ LightDM no pudo arrancar, puede ser por falta de monitor o drivers."

echo "✅ Base instalada. Si ves este mensaje, pasa al SCRIPT 1."
