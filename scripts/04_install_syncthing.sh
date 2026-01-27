#!/bin/bash
# 04_install_syncthing.sh - AstroOrange Pro
set -e
TARGET_USER="AstroOrange"
HOME_DIR="/home/${TARGET_USER}"

if [ "$EUID" -eq 0 ]; then
  echo "❌ ERROR: No ejecutes como root."
  exit 1
fi

sudo mkdir -p /etc/apt/keyrings
sudo curl -L -o /etc/apt/keyrings/syncthing-archive-keyring.gpg https://syncthing.net/release-key.gpg
echo "deb [signed-by=/etc/apt/keyrings/syncthing-archive-keyring.gpg] https://apt.syncthing.net/ syncthing stable" | sudo tee /etc/apt/sources.list.d/syncthing.list
sudo apt update
sudo apt install -y syncthing
systemctl --user enable syncthing.service
systemctl --user start syncthing.service
sleep 5
sed -i 's/127.0.1.1:8384/0.0.0.0:8384/g' ${HOME_DIR}/.config/syncthing/config.xml || true
systemctl --user restart syncthing.service
echo "Syncthing listo en puerto 8384"
