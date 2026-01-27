#!/bin/bash
# 03_install_astronomy.sh - AstroOrange Pro
set -e
TARGET_USER="AstroOrange"

if [ "$EUID" -eq 0 ]; then
  echo "❌ ERROR: No ejecutes como root."
  exit 1
fi

sudo add-apt-repository ppa:mutlaqja/ppa -y
sudo add-apt-repository ppa:pch/phd2 -y
sudo apt update
sudo apt install -y indi-full kstars-bleeding phd2
sudo usermod -a -G dialout,video,tty ${TARGET_USER}
echo "=== Software Astronómico Instalado ==="
