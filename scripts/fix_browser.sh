#!/bin/bash
# fix_browser.sh
set -e
sudo snap remove firefox || true
sudo add-apt-repository -y ppa:mozillateam/ppa
echo 'Package: *
Pin: release o=LP-PPA-mozillateam
Pin-Priority: 1001' | sudo tee /etc/apt/preferences.d/mozilla-firefox
sudo apt update
sudo apt install -y --allow-downgrades firefox
echo "Firefox DEB instalado."
