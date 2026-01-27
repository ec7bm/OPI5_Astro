#!/bin/bash
# prepare-base.sh - AstroOrange V2 Base Image Preparation
# STATIC & SAFE: NO partition changes, NO resizing, NO UUID changes.
# Focus: Inject files, install minimal GUI, enable firstboot.

set -e

# --- CONFIGURATION ---
BASE_IMAGE="image-base/base.img"
WORK_IMAGE="astroorange-v2-work.img"
MOUNT_POINT="/tmp/astroorange-mount"
LOOP_DEVICE=""

# --- CLEANUP TRAP ---
cleanup() {
    echo "🧹 Cleaning up..."
    # Unmount chroot binds safely
    sudo umount -l "${MOUNT_POINT}/dev/pts" 2>/dev/null || true
    sudo umount -l "${MOUNT_POINT}/dev" 2>/dev/null || true
    sudo umount -l "${MOUNT_POINT}/proc" 2>/dev/null || true
    sudo umount -l "${MOUNT_POINT}/sys" 2>/dev/null || true
    
    # Unmount partitions
    sudo umount -l "${MOUNT_POINT}/boot" 2>/dev/null || true
    sudo umount -l "${MOUNT_POINT}" 2>/dev/null || true
    
    # Detach loop device
    if [ -n "$LOOP_DEVICE" ]; then
        sudo losetup -d "$LOOP_DEVICE" 2>/dev/null || true
    fi
    
    # Remove mount point
    if [ -d "${MOUNT_POINT}" ]; then
        rmdir "${MOUNT_POINT}" 2>/dev/null || true
    fi
}
trap cleanup EXIT

echo "========================================="
echo "  AstroOrange V2 - Safe Base Prep"
echo "========================================="

# 1. VERIFY INPUT
if [ ! -f "$BASE_IMAGE" ]; then
    echo "❌ Error: Base image not found at $BASE_IMAGE"
    exit 1
fi

# 2. CREATE WORK COPY
if [ ! -f "$WORK_IMAGE" ]; then
    echo "📦 Creating working copy ($WORK_IMAGE)..."
    cp "$BASE_IMAGE" "$WORK_IMAGE"
else
    echo "⚠️  Using existing working copy: $WORK_IMAGE"
fi

# 3. MOUNT IMAGE (SAFE MODE)
echo "🔧 Mounting image (NO partition changes)..."
# -P forces kernel to scan partitions
LOOP_DEVICE=$(sudo losetup -f --show -P "$WORK_IMAGE")
echo "   Loop device: $LOOP_DEVICE"

# Partition detection (standard Orange Pi images: p1=boot, p2=rootfs usually, but checking widely)
# Assuming standard layout: p3 or p2 is often root on OPi, but let's stick to standard p2 for linux-root usually.
# You might need to adjust this depending on the specific OPi image layout!
# For this script we assume p2 is root, p1 is boot (fairly standard).
ROOT_PART="${LOOP_DEVICE}p2"
BOOT_PART="${LOOP_DEVICE}p1"

if [ ! -e "$ROOT_PART" ]; then
    echo "❌ Error: Root partition $ROOT_PART not found!"
    exit 1
fi

mkdir -p "${MOUNT_POINT}"
sudo mount "$ROOT_PART" "${MOUNT_POINT}"
if [ -e "$BOOT_PART" ]; then
    sudo mount "$BOOT_PART" "${MOUNT_POINT}/boot"
fi

# 4. PREPARE CHROOT
echo "🔗 Binding filesystems..."
sudo mount --bind /dev "${MOUNT_POINT}/dev"
sudo mount --bind /dev/pts "${MOUNT_POINT}/dev/pts"
sudo mount --bind /proc "${MOUNT_POINT}/proc"
sudo mount --bind /sys "${MOUNT_POINT}/sys"

# Copy DNS config for internet access within chroot
if [ -f /etc/resolv.conf ]; then
    sudo cp /etc/resolv.conf "${MOUNT_POINT}/etc/resolv.conf.bak"
    sudo cp /etc/resolv.conf "${MOUNT_POINT}/etc/resolv.conf"
fi

# 5. INSTALL PACKAGES
echo "⬇️  Installing GUI & Base Utilities in chroot..."
sudo chroot "${MOUNT_POINT}" /bin/bash <<'EOF'
export DEBIAN_FRONTEND=noninteractive

# Prevent services from starting during install
echo -e '#!/bin/sh\nexit 101' > /usr/sbin/policy-rc.d
chmod +x /usr/sbin/policy-rc.d

apt-get update

# Core GUI Requirements (XFCE + VNC)
# - xfce4: Desktop environment
# - tightvncserver: VNC Server
# - novnc + websockify: Browser based VNC
# - network-manager: For hotspot control
apt-get install -y --no-install-recommends \
    xfce4 \
    xfce4-terminal \
    dbus-x11 \
    tightvncserver \
    novnc \
    websockify \
    network-manager \
    git \
    python3-gi \
    python3-gi-cairo \
    gir1.2-gtk-3.0 \
    gir1.2-vte-2.91 \
    dnsmasq-base \
    hostapd

# Clean up
rm /usr/sbin/policy-rc.d
apt-get clean
rm -rf /var/lib/apt/lists/*
EOF

# 6. INJECT FILES
echo "📂 Injecting Wizard and Scripts..."
TARGET_OPT="${MOUNT_POINT}/opt/astroorange"
TARGET_BIN="${MOUNT_POINT}/usr/local/bin"
TARGET_SYSTEMD="${MOUNT_POINT}/etc/systemd/system"

sudo mkdir -p "$TARGET_OPT"
sudo mkdir -p "$TARGET_BIN"

# Copy Wizard Code
if [ -d "wizard" ]; then
    sudo cp -r wizard/* "$TARGET_OPT/"
    # Install autostart
    if [ -f "wizard/astro-wizard.desktop" ]; then
        sudo mkdir -p "${MOUNT_POINT}/etc/xdg/autostart"
        sudo cp wizard/astro-wizard.desktop "${MOUNT_POINT}/etc/xdg/autostart/"
        sudo chmod 644 "${MOUNT_POINT}/etc/xdg/autostart/astro-wizard.desktop"
    fi
else
    echo "⚠️  Warning: 'wizard' directory not found locally."
fi

# Copy Scripts
# We renamed them in the plan, but let's assume they are in ./scripts/
if [ -d "scripts" ]; then
    sudo cp scripts/*.sh "$TARGET_BIN/"
    sudo chmod +x "$TARGET_BIN/"*.sh
fi

# Copy Systemd Services
if [ -d "systemd" ]; then
    sudo cp systemd/*.service "$TARGET_SYSTEMD/"
fi

# 7. ENABLE SERVICES
echo "🔌 Enabling First-Boot & VNC Services..."
sudo chroot "${MOUNT_POINT}" /bin/bash <<'EOF'
# Enable firstboot service logic
if [ -f /etc/systemd/system/astroorange-firstboot.service ]; then
    systemctl enable astroorange-firstboot.service
fi

# Ensure NetworkManager is enabled
systemctl enable NetworkManager

# We do NOT enable the hotspot service directly; firstboot script handles that dynamic logic.
EOF

# Restore DNS
if [ -f "${MOUNT_POINT}/etc/resolv.conf.bak" ]; then
    sudo mv "${MOUNT_POINT}/etc/resolv.conf.bak" "${MOUNT_POINT}/etc/resolv.conf"
fi

echo "✅ Done! Cleanup trap will handle unmounting."
