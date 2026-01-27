#!/bin/bash
# install-syncthing.sh
# Installs Syncthing

set -e

echo "🔄 Installing Syncthing..."
export DEBIAN_FRONTEND=noninteractive

# Add Key and Repo
sudo mkdir -p /etc/apt/keyrings
sudo curl -s -o /etc/apt/keyrings/syncthing-archive-keyring.gpg https://syncthing.net/release-key.gpg
echo "deb [signed-by=/etc/apt/keyrings/syncthing-archive-keyring.gpg] https://apt.syncthing.net/ syncthing stable" | sudo tee /etc/apt/sources.list.d/syncthing.list

sudo apt-get update
sudo apt-get install -y syncthing

# Enable for target user
if [ -n "$TARGET_USER" ]; then
    echo "👤 Enabling Syncthing for user: $TARGET_USER"
    # Try system-wide user instantiation if available, or just rely on autostart desktop entry
    if systemctl list-unit-files | grep -q "syncthing@.service"; then
        systemctl enable "syncthing@$TARGET_USER.service"
        systemctl start "syncthing@$TARGET_USER.service"
    else
        echo "⚠️  User service template not found, skipping auto-enable."
    fi
else
    echo "⚠️  TARGET_USER not set, skipping service enablement."
fi

echo "✅ Syncthing installed successfully."
