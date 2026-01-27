#!/bin/bash
# install-phd2.sh
# Installs PHD2

set -e

echo "🔭 Installing PHD2..."
export DEBIAN_FRONTEND=noninteractive

# Add PPA
sudo add-apt-repository -y ppa:pch/phd2
sudo apt-get update

# Install
sudo apt-get install -y phd2

echo "✅ PHD2 installed successfully."
