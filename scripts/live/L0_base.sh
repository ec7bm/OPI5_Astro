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

echo "✅ Base instalada. Si estás por SSH, no necesitas reiniciar aún."
