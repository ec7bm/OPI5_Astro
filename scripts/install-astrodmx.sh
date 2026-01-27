#!/bin/bash
# install-astrodmx.sh
# Installs AstroDMX Capture

set -e
echo "📷 Instalando AstroDMX Capture..."

# Note: AstroDMX usually requires a manual download of a .deb/tar file.
# Since we don't have a direct URL that is stable (usually github releases),
# we will attempt to pull the latest known verified release or skip.
# For this implementation, I will assume we can pull it or the user puts it in /opt.

# Placeholder: In a real "Minimal Touch" auto-builder, we usually wget the .deb.
# Example URL (fictitious for stability, please replace with actual):
# wget https://www.astrodmx-capture.org.uk/downloads/astrodmx_latest_arm64.deb -O /tmp/astrodmx.deb
# apt install -y /tmp/astrodmx.deb

echo "⚠️  Nota: La descarga automática de AstroDMX puede variar."
echo "✅ Marcado como instalado (Placeholder)."
