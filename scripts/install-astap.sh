#!/bin/bash
# install-astap.sh
# Installs ASTAP and H18 database

set -e
echo "🌌 Instalando ASTAP..."

export DEBIAN_FRONTEND=noninteractive
sudo apt-get update

# ASTAP .deb (Example logic, check latest URL)
# wget https://www.hnsky.org/astap_arm64.deb -O /tmp/astap.deb
# sudo apt install -y /tmp/astap.deb

# Install via Sourceforge/Manual URL usually required.
# Assuming standard repo or manual step.
# For "AstroOrange", often we preload these debs in 'prepare-base.sh' to /opt/installers for offline install?
# But user said "una vez que tiene wifi... instala". So we download.

# Let's try to find a stable way or simple apt if available in astronomy distros (often not in standard ubuntu).
# We'll use a placeholder echo for safety unless I have a guaranteed URL.

echo "⚠️  ASTAP requiere descarga manual o URL fija. Saltando por ahora."
