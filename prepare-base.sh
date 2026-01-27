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

# Partition detection (Robust)
echo "🔍 Detecting partitions..."
# Try to find the ext4 partition (usually root)
ROOT_PART=$(sudo blkid | grep "${LOOP_DEVICE}p" | grep "ext4" | head -n 1 | cut -d: -f1)

# Fallback: largest partition? or last partition?
if [ -z "$ROOT_PART" ]; then
    echo "⚠️  Could not detect ext4 partition via blkid. Using last partition as heuristic."
    ROOT_PART=$(ls -1 ${LOOP_DEVICE}p* | sort -V | tail -n 1)
fi

# Boot partition (usually the first one, or the one before root)
# Simple heuristic: First partition is often boot or loader.
# On OPi5, p1 often loader, p2 often boot/root.
# Let's assume standard Ubuntu layout: /boot might be a folder on root, or separate.
# If separate, it's usually the vfat/ext4 small one.
# For simplicity in this script, we mount ROOT first. Then checks if we need to mount boot.
echo "   Root partition detected: $ROOT_PART"

if [ ! -e "$ROOT_PART" ]; then
    echo "❌ Error: Root partition $ROOT_PART not found!"
    exit 1
fi

mkdir -p "${MOUNT_POINT}"
sudo mount "$ROOT_PART" "${MOUNT_POINT}"

# Check if /boot is empty, if so, try to find a boot partition
if [ -z "$(ls -A ${MOUNT_POINT}/boot 2>/dev/null)" ]; then
    echo "ℹ️  /boot appears empty, looking for separate boot partition..."
    BOOT_PART=$(ls -1 ${LOOP_DEVICE}p* | sort -V | head -n 2 | tail -n 1) # Guessing p2 if p3 is root? Or p1?
    # Actually, safely skipping strict boot mount unless we need to update kernel/initramfs (which we don't).
    # "Minimal Touch" means we probably don't even need /boot mounted unless dpkg triggers update-initramfs.
    # Apt install xfce might trigger it. So we should mount just in case.
    # Let's try to identify p1 or p2.
    # User's heuristic: BOOT_PART=$(ls ${LOOP_DEVICE}p* | head -n 1) is risky if p1 is u-boot binary blob.
    # Let's verify with blkid for vfat or ext4 label "boot"
    BOOT_CANDIDATE=$(sudo blkid | grep "${LOOP_DEVICE}p" | grep -E "vfat|ext4" | grep -v "$ROOT_PART" | head -n 1 | cut -d: -f1)
    if [ -n "$BOOT_CANDIDATE" ]; then
        echo "   Mounting potential boot partition: $BOOT_CANDIDATE"
        sudo mount "$BOOT_CANDIDATE" "${MOUNT_POINT}/boot"
    fi
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
# Added xserver-xorg-video-dummy for headless support
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
    hostapd \
    xserver-xorg-video-dummy

# Clean up
rm /usr/sbin/policy-rc.d
apt-get clean
rm -rf /var/lib/apt/lists/*
EOF

# 6. HEADLESS XORG CONFIG
echo "🖥️  Configuring Headless Xorg (Dummy Driver)..."
sudo mkdir -p "${MOUNT_POINT}/etc/X11/xorg.conf.d"
cat <<EOF | sudo tee "${MOUNT_POINT}/etc/X11/xorg.conf.d/20-dummy.conf"
Section "Device"
    Identifier  "DummyVideo"
    Driver      "dummy"
    VideoRam    16384
EndSection

Section "Monitor"
    Identifier  "DummyMonitor"
    HorizSync   28.0-80.0
    VertRefresh 48.0-75.0
EndSection

Section "Screen"
    Identifier  "DummyScreen"
    Device      "DummyVideo"
    Monitor     "DummyMonitor"
    DefaultDepth 24
    SubSection "Display"
        Depth 24
        Modes "1920x1080" "1280x720"
    EndSubSection
EndSection
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

echo ""
echo "========================================="
echo "  🚀 SERVIDOR DE DESCARGA"
echo "========================================="
read -p "¿Quieres iniciar un servidor web para bajar la imagen ahora? (S/n): " SERVER_REPLY
if [[ "$SERVER_REPLY" =~ ^[SsYy]$ ]] || [[ -z "$SERVER_REPLY" ]]; then
    IP_ADDR=$(hostname -I | awk '{print $1}')
    echo ""
    echo "📂 Sirviendo directorio actual..."
    echo "🔗 URL: http://${IP_ADDR}:8000/astroorange-v2-work.img"
    echo "⚠️  Pulsa Ctrl+C para detener."
    echo ""
    python3 -m http.server 8000
fi
