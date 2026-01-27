#!/bin/bash
# install-kstars.sh
# Installs KStars (Bleeding), INDI Full, and GSC

set -e

echo "⭐ Installing KStars + INDI..."
export DEBIAN_FRONTEND=noninteractive

# Add PPA
sudo add-apt-repository -y ppa:mutlaqja/ppa
sudo apt-get update

# Install
sudo apt-get install -y indi-full kstars-bleeding gsc

# Add user to groups
if [ -n "$TARGET_USER" ]; then
    REAL_USER="$TARGET_USER"
else
    REAL_USER=$(whoami)
fi

echo "👤 Configuring permissions for user: $REAL_USER"
if [ "$REAL_USER" != "root" ]; then
    sudo usermod -a -G dialout,video,plugdev "$REAL_USER"
fi

echo "✅ KStars installed successfully."
