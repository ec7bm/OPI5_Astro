#!/bin/bash
# AstroOrange Pro v2.3 - SAFE Remaster Script for Orange Pi
# NO offline resize | NO partition rewriting | Orange Pi safe

set -e

echo "=== AstroOrange Pro v2.3 Remaster (SAFE MODE) ==="

# ---------------- CONFIG ----------------
BASE_DIR="$(pwd)"
WORK_DIR="${BASE_DIR}/remaster-work"
MOUNT_DIR="${WORK_DIR}/mount"
IMAGE_BASE_DIR="${BASE_DIR}/image-base"
USERPATCHES_DIR="${BASE_DIR}/userpatches"
OUTPUT_DIR="${BASE_DIR}/output"

mkdir -p "$WORK_DIR" "$MOUNT_DIR" "$IMAGE_BASE_DIR" "$OUTPUT_DIR"

# ---------------- IMAGE DETECTION ----------------
IMAGE_FILE=$(find "$WORK_DIR" -name "base_working_copy.img" 2>/dev/null | head -n1)

if [ -z "$IMAGE_FILE" ]; then
    IMAGE_SOURCE=$(find "$IMAGE_BASE_DIR" -name "*.img" -o -name "*.img.xz" | head -n1)
    if [ -z "$IMAGE_SOURCE" ]; then
        echo "❌ No se encontró imagen base en image-base/"
        exit 1
    fi

    echo "📦 Copiando imagen base..."
    cp "$IMAGE_SOURCE" "$WORK_DIR/base_working_copy.${IMAGE_SOURCE##*.}"
    IMAGE_FILE="$WORK_DIR/base_working_copy.${IMAGE_SOURCE##*.}"
fi

# ---------------- DECOMPRESS ----------------
if [[ "$IMAGE_FILE" == *.xz ]]; then
    echo "📂 Descomprimiendo imagen..."
    unxz "$IMAGE_FILE"
    IMAGE_FILE="${IMAGE_FILE%.xz}"
fi

echo "➡️ Usando imagen: $IMAGE_FILE"

# ---------------- SAFE EXPANSION (REQUIRED) ----------------
# El sistema necesita más espacio para XFCE/KStars.
# Usamos sgdisk para mover el header GPT y evitar corrupción.
echo "🔧 Expandiendo imagen +4GB..."
if command -v sgdisk &> /dev/null; then
    truncate -s +4G "$IMAGE_FILE"
    sync
    # Mover backup header al final del disco (Fix GPT)
    sgdisk -e "$IMAGE_FILE" > /dev/null 2>&1 || true
    # Informar al kernel cambio de tamaño
    partprobe "$IMAGE_FILE" 2>/dev/null || true
else
    echo "⚠️ 'gdisk' no instalado. Intentando expansión simple (puede fallar)..."
    truncate -s +4G "$IMAGE_FILE"
fi

# ---------------- LOOP + MOUNT ----------------
echo "🔧 Asociando loop device..."
LOOP_DEVICE=$(sudo losetup -f --show -P "$IMAGE_FILE")
sleep 2

# Expandir Partición y Filesystem
echo "📏 Redimensionando partición root..."
# Opción A: growpart (cloud-guest-utils)
if command -v growpart &> /dev/null; then
    sudo growpart "$LOOP_DEVICE" 2 || true
else
    # Opción B: parted
    sudo parted -s "$LOOP_DEVICE" resizepart 2 100% || true
fi

sleep 1
sudo e2fsck -f -y "${LOOP_DEVICE}p2" || true
sudo resize2fs "${LOOP_DEVICE}p2"

# Detectar particiones por filesystem
ROOT_PART=$(blkid | grep "$LOOP_DEVICE" | grep ext4 | cut -d: -f1 | head -n1)
BOOT_PART=$(blkid | grep "$LOOP_DEVICE" | grep vfat | cut -d: -f1 | head -n1)

if [ -z "$ROOT_PART" ]; then
    echo "❌ No se pudo detectar la partición root"
    sudo losetup -d "$LOOP_DEVICE"
    exit 1
fi

echo "🗂 Root: $ROOT_PART"
[ -n "$BOOT_PART" ] && echo "🗂 Boot: $BOOT_PART"

sudo mount "$ROOT_PART" "$MOUNT_DIR"
[ -n "$BOOT_PART" ] && sudo mount "$BOOT_PART" "$MOUNT_DIR/boot"

# ---------------- CHROOT PREP ----------------
echo "🔗 Preparando chroot..."
sudo mount --bind /dev "$MOUNT_DIR/dev"
sudo mount --bind /dev/pts "$MOUNT_DIR/dev/pts"
sudo mount --bind /proc "$MOUNT_DIR/proc"
sudo mount --bind /sys "$MOUNT_DIR/sys"

sudo cp /etc/resolv.conf "$MOUNT_DIR/etc/resolv.conf"

# Bloquear arranque de servicios
echo -e '#!/bin/sh\nexit 101' | sudo tee "$MOUNT_DIR/usr/sbin/policy-rc.d" >/dev/null
sudo chmod +x "$MOUNT_DIR/usr/sbin/policy-rc.d"

# ---------------- INJECT FILES ----------------
echo "📂 Inyectando scripts..."
sudo cp -rv "$BASE_DIR/scripts/"* "$MOUNT_DIR/usr/local/bin/"
sudo chmod +x "$MOUNT_DIR/usr/local/bin/"*.sh

echo "📂 Inyectando servicios systemd..."
sudo cp -rv "$BASE_DIR/systemd/"*.service "$MOUNT_DIR/etc/systemd/system/"

echo "📂 Inyectando Wizard AstroOrange..."
sudo mkdir -p "$MOUNT_DIR/opt/astro-wizard"
sudo cp -rv "$BASE_DIR/wizard/"* "$MOUNT_DIR/opt/astro-wizard/"

echo "📂 Inyectando Assets (Fondos)..."
sudo mkdir -p "$MOUNT_DIR/tmp/assets"
sudo cp -rv "$BASE_DIR/assets/"* "$MOUNT_DIR/tmp/assets/"

# ---------------- CUSTOMIZE IMAGE ----------------
if [ -f "$USERPATCHES_DIR/customize-image.sh" ]; then
    echo "⚙️ Ejecutando customize-image.sh..."
    sudo cp "$USERPATCHES_DIR/customize-image.sh" "$MOUNT_DIR/tmp/"
    sudo chmod +x "$MOUNT_DIR/tmp/customize-image.sh"
    sudo chroot "$MOUNT_DIR" /bin/bash /tmp/customize-image.sh
    sudo rm "$MOUNT_DIR/tmp/customize-image.sh"
fi

# ---------------- CLEAN CHROOT ----------------
echo "🧹 Limpiando chroot..."
sudo rm "$MOUNT_DIR/usr/sbin/policy-rc.d"

sudo umount -l "$MOUNT_DIR/dev/pts"
sudo umount -l "$MOUNT_DIR/dev"
sudo umount -l "$MOUNT_DIR/proc"
sudo umount -l "$MOUNT_DIR/sys"
[ -n "$BOOT_PART" ] && sudo umount -l "$MOUNT_DIR/boot"
sudo umount -l "$MOUNT_DIR"

sudo losetup -d "$LOOP_DEVICE"
sync

# ---------------- FINAL IMAGE ----------------
OUTPUT_NAME="AstroOrange-v2.3-$(date +%Y%m%d).img"
mv "$IMAGE_FILE" "$OUTPUT_DIR/$OUTPUT_NAME"

echo "📦 Comprimiendo imagen..."
cd "$OUTPUT_DIR"
xz -1 -T0 "$OUTPUT_NAME"

echo ""
echo "✅ BUILD COMPLETADO"
echo "📀 Imagen final: $OUTPUT_DIR/$OUTPUT_NAME.xz"
echo ""

# ---------------- AUTO SERVE ----------------
echo "📡 Iniciando servidor de descarga..."
echo "--------------------------------------------------"
cd "$OUTPUT_DIR"
# Usamos ../scripts/serve_image.py porque estamos en output/
python3 ../scripts/serve_image.py
