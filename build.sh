#!/bin/bash
# AstroOrange V2 - Professional Build System
# Combines safety, clarity, and convenience

set -e

# ==================== COLORS ====================
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# ==================== PATHS ====================
BASE_DIR="$(pwd)"
WORK_DIR="$BASE_DIR/remaster-work"
MOUNT_DIR="$WORK_DIR/mount"
IMAGE_BASE_DIR="$BASE_DIR/image-base"
OUTPUT_DIR="$BASE_DIR/output"

mkdir -p "$WORK_DIR" "$MOUNT_DIR" "$OUTPUT_DIR"

echo -e "${BLUE}=== AstroOrange V2 Build System ===${NC}"

# ==================== FIND BASE IMAGE ====================
echo -e "${GREEN}[1/7] Locating base image...${NC}"
SRC_IMG=$(ls "$IMAGE_BASE_DIR"/*.img* 2>/dev/null | head -n1)
[ -z "$SRC_IMG" ] && { echo -e "${RED}❌ No base image found in $IMAGE_BASE_DIR${NC}"; exit 1; }
echo -e "   📀 Found: $(basename "$SRC_IMG")"

# ==================== DECOMPRESS ====================
echo -e "${GREEN}[2/7] Preparing image...${NC}"
if [[ "$SRC_IMG" == *.xz ]]; then
    echo "   🗜️  Decompressing XZ archive..."
    cp "$SRC_IMG" "$WORK_DIR/base.img.xz"
    cd "$WORK_DIR"
    unxz -f base.img.xz
    IMG="base.img"
elif [[ "$SRC_IMG" == *.img ]]; then
    echo "   📋 Copying raw image..."
    cp "$SRC_IMG" "$WORK_DIR/base.img"
    cd "$WORK_DIR"
    IMG="base.img"
else
    echo -e "${RED}❌ Unsupported format${NC}"
    exit 1
fi

# ==================== EXPAND IMAGE ====================
echo -e "${GREEN}[3/7] Expanding image (+4GB)...${NC}"
truncate -s +4G "$IMG"
sgdisk -e "$IMG" >/dev/null 2>&1 || true

LOOP=$(losetup -f --show -P "$IMG")
sleep 2

echo "   📏 Growing partition..."
growpart "$LOOP" 2 || true
e2fsck -f -y "${LOOP}p2" || true
resize2fs "${LOOP}p2"

# ==================== MOUNT ====================
echo -e "${GREEN}[4/7] Mounting filesystems...${NC}"
mount "${LOOP}p2" "$MOUNT_DIR"
mount "${LOOP}p1" "$MOUNT_DIR/boot" || true

# Bind system directories (SAFE MODE)
for i in dev proc sys; do
    mount --bind /$i "$MOUNT_DIR/$i"
done

cp /etc/resolv.conf "$MOUNT_DIR/etc/resolv.conf"

# Prevent services from starting during build
echo -e '#!/bin/sh\nexit 101' > "$MOUNT_DIR/usr/sbin/policy-rc.d"
chmod +x "$MOUNT_DIR/usr/sbin/policy-rc.d"

# ==================== INJECT FILES ====================
echo -e "${GREEN}[5/7] Injecting AstroOrange components...${NC}"

# Crear directorio temporal de inyección
mkdir -p "$MOUNT_DIR/tmp/remaster-source"

# Copiar todo el árbol de scripts, systemd y wizard para que customize-image.sh los use
for dir in scripts systemd wizard userpatches; do
    if [ -d "$BASE_DIR/$dir" ]; then
        echo "   📂 Injecting $dir..."
        cp -r "$BASE_DIR/$dir" "$MOUNT_DIR/tmp/remaster-source/"
    fi
done

# ==================== CUSTOMIZE ====================
echo -e "${GREEN}[6/7] Running customization script...${NC}"
if [ -f "$BASE_DIR/userpatches/customize-image.sh" ]; then
    cp "$BASE_DIR/userpatches/customize-image.sh" "$MOUNT_DIR/tmp/"
    chmod +x "$MOUNT_DIR/tmp/customize-image.sh"
    chroot "$MOUNT_DIR" /tmp/customize-image.sh
    rm "$MOUNT_DIR/tmp/customize-image.sh"
else
    echo -e "${YELLOW}   ⚠️  No customize-image.sh found, skipping${NC}"
fi

# ==================== CLEANUP ====================
echo -e "${GREEN}[7/7] Cleaning up...${NC}"
rm -f "$MOUNT_DIR/usr/sbin/policy-rc.d"
rm -rf "$MOUNT_DIR/tmp/userpatches"

# Unmount everything
for i in sys proc dev; do
    umount -l "$MOUNT_DIR/$i" 2>/dev/null || true
done

umount -l "$MOUNT_DIR/boot" 2>/dev/null || true
umount -l "$MOUNT_DIR" 2>/dev/null || true

losetup -d "$LOOP"

# ==================== OUTPUT ====================
OUT="$OUTPUT_DIR/AstroOrange-$(date +%Y%m%d-%H%M).img"
mv "$IMG" "$OUT"

echo "   🔐 Generating SHA256 checksum..."
sha256sum "$OUT" > "$OUT.sha256"

echo ""
echo -e "${GREEN}✅ BUILD COMPLETED SUCCESSFULLY${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "📀 Image: ${YELLOW}$(basename "$OUT")${NC}"
echo -e "📊 Size:  $(du -h "$OUT" | cut -f1)"
echo -e "🔐 SHA256: $(cat "$OUT.sha256" | cut -d' ' -f1)"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# ==================== HTTP SERVER ====================
echo ""
echo -e "${GREEN}🌐 Starting HTTP server for download...${NC}"
echo -e "   Access from your network at:"
echo -e "   ${YELLOW}http://$(hostname -I | awk '{print $1}'):8000/${NC}"
echo -e ""
echo -e "   Press ${RED}Ctrl+C${NC} to stop the server"
echo ""

cd "$OUTPUT_DIR"
python3 -m http.server 8000
