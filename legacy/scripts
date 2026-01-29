#!/bin/bash
# 00_setup_network.sh - AstroOrange Pro
set -e
echo "=== Instalando NetworkManager ==="
sudo apt update
sudo apt install -y network-manager
echo "=== Configurando Netplan para usar NetworkManager ==="
sudo mkdir -p /etc/netplan/backup
sudo cp /etc/netplan/*.yaml /etc/netplan/backup/ || true
sudo bash -c "cat << EOF > /etc/netplan/01-network-manager-all.yaml
network:
  version: 2
  renderer: NetworkManager
EOF"
sudo chmod 600 /etc/netplan/01-network-manager-all.yaml
sudo netplan apply
echo "=== NetworkManager configurado correctamente ==="
echo "Ahora puedes usar 'sudo nmtui' para gestionar tus redes."
sudo nmtui
