#!/bin/bash

# Astro OPI 5 Pro - Remaster Script
# Este script toma la imagen oficial de Ubuntu Jammy Server de Orange Pi
# y le inyecta toda nuestra personalización astronómica

set -e

echo "=== Astro OPI 5 Pro Remaster System ==="

# Directorios
BASE_DIR="$(pwd)"
WORK_DIR="${BASE_DIR}/remaster-work"
MOUNT_DIR="${WORK_DIR}/mount"
USERPATCHES_DIR="${BASE_DIR}/userpatches"

# Crear directorio de trabajo
mkdir -p "${WORK_DIR}"
mkdir -p "${MOUNT_DIR}"

# 1. Descargar imagen oficial de Orange Pi Ubuntu Jammy Server
echo "[1/6] Descargando imagen oficial de Ubuntu Jammy Server..."
cd "${WORK_DIR}"

# URL de la imagen oficial (necesitarás el ID del archivo de Google Drive)
# Por ahora usaremos gdown para descargar desde Google Drive
if ! command -v gdown &> /dev/null; then
    echo "Instalando gdown para descargar desde Google Drive..."
    pip3 install gdown
fi

# Descargar la imagen más reciente de Ubuntu Jammy Server
# Nota: Reemplaza este ID con el archivo correcto del Google Drive
GDRIVE_FOLDER="11tj_ivEBwvJx4vdNtK91YQeGOKDC4JNy"
echo "Por favor, descarga manualmente la imagen de Ubuntu Jammy Server desde:"
echo "https://drive.google.com/drive/folders/11tj_ivEBwvJx4vdNtK91YQeGOKDC4JNy"
echo ""
echo "Coloca el archivo .img.xz en: ${WORK_DIR}/"
echo "Presiona Enter cuando esté listo..."
read

# Buscar el archivo descargado
IMAGE_FILE=$(find "${WORK_DIR}" -name "*.img.xz" -o -name "*.img" | head -n 1)

if [ -z "$IMAGE_FILE" ]; then
    echo "ERROR: No se encontró ninguna imagen .img o .img.xz en ${WORK_DIR}"
    exit 1
fi

echo "Imagen encontrada: ${IMAGE_FILE}"

# 2. Descomprimir si es necesario
echo "[2/6] Descomprimiendo imagen..."
if [[ "$IMAGE_FILE" == *.xz ]]; then
    unxz -v "$IMAGE_FILE"
    IMAGE_FILE="${IMAGE_FILE%.xz}"
fi

# 2.5. Expandir la imagen para tener espacio
echo "[2.5/6] Expandiendo imagen en 3GB..."
# Usar truncate en lugar de dd para evitar depencias de /dev/zero
truncate -s +3G "$IMAGE_FILE"
# Buscar el dispositivo loop libre
LOOP_DEVICE=$(sudo losetup -f)
# Asociar imagen al loop device
sudo losetup "$LOOP_DEVICE" "$IMAGE_FILE"
# Leer la tabla de particiones
sudo partprobe "$LOOP_DEVICE"
# Expandir la partición root (la última, usualmente la 2)
# Usamos growpart (parte de cloud-guest-utils)
if ! command -v growpart &> /dev/null; then
    sudo apt-get update && sudo apt-get install -y cloud-guest-utils
fi
sudo growpart "$LOOP_DEVICE" 2
# Verificar y redimensionar el sistema de archivos (e2fsck + resize2fs)
sudo e2fsck -f -y "${LOOP_DEVICE}p2"
sudo resize2fs "${LOOP_DEVICE}p2"
# Liberar loop para volver a montarlo limpiamente después
sudo losetup -d "$LOOP_DEVICE"

# 3. Montar la imagen
echo "[3/6] Montando imagen..."
LOOP_DEVICE=$(sudo losetup -f)
sudo losetup -P "$LOOP_DEVICE" "$IMAGE_FILE"

# Esperar a que el kernel detecte las particiones
sleep 2

# Montar la partición root (normalmente p2)
sudo mount "${LOOP_DEVICE}p2" "${MOUNT_DIR}"
sudo mount "${LOOP_DEVICE}p1" "${MOUNT_DIR}/boot"

# 4. Inyectar personalización
echo "[4/6] Inyectando personalización astronómica..."

# Copiar scripts de overlay
echo "Copiando archivos de overlay..."
sudo cp -rv "${USERPATCHES_DIR}/overlay/"* "${MOUNT_DIR}/"

# Ejecutar customize-image.sh en el chroot
echo "Ejecutando script de personalización..."
sudo cp "${USERPATCHES_DIR}/customize-image.sh" "${MOUNT_DIR}/tmp/"

# Preparar chroot
sudo mount --bind /dev "${MOUNT_DIR}/dev"
sudo mount --bind /proc "${MOUNT_DIR}/proc"
sudo mount --bind /sys "${MOUNT_DIR}/sys"

# Ejecutar personalización
sudo chroot "${MOUNT_DIR}" /bin/bash /tmp/customize-image.sh

# Limpiar
sudo rm "${MOUNT_DIR}/tmp/customize-image.sh"

# 5. Desmontar
echo "[5/6] Desmontando imagen..."
sudo umount "${MOUNT_DIR}/dev"
sudo umount "${MOUNT_DIR}/proc"
sudo umount "${MOUNT_DIR}/sys"
sudo umount "${MOUNT_DIR}/boot"
sudo umount "${MOUNT_DIR}"
sudo losetup -d "$LOOP_DEVICE"

# 6. Comprimir imagen final
echo "[6/6] Comprimiendo imagen final..."
OUTPUT_DIR="${BASE_DIR}/output"
mkdir -p "${OUTPUT_DIR}"

OUTPUT_NAME="Astro-OPI5-Pro-Ubuntu-Jammy-$(date +%Y%m%d).img"
mv "$IMAGE_FILE" "${OUTPUT_DIR}/${OUTPUT_NAME}"

cd "${OUTPUT_DIR}"
echo "Comprimiendo con xz (esto puede tardar varios minutos)..."
xz -v -9 -T0 "${OUTPUT_NAME}"

echo ""
echo "=== ¡Proceso completado! ==="
echo "Imagen final: ${OUTPUT_DIR}/${OUTPUT_NAME}.xz"
echo ""
echo "Para limpiar archivos temporales:"
echo "sudo rm -rf ${WORK_DIR}"
