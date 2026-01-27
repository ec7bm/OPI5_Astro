#!/bin/bash
# install-stellarium.sh
# Installs Stellarium

set -e

echo "✨ Installing Stellarium..."
export DEBIAN_FRONTEND=noninteractive

# Add PPA
sudo add-apt-repository -y ppa:stellarium/stellarium-releases
sudo apt-get update

# Install
sudo apt-get install -y stellarium

echo "✅ Stellarium installed successfully."
