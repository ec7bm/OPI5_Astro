#!/bin/bash

# AstroOrange Pro - Remaster Script
# Este script toma la imagen oficial de Ubuntu Jammy Server de Orange Pi
# y le inyecta toda nuestra personalización astronómica

set -e

echo "=== AstroOrange Pro v2.3 Remaster System (Auto-Cleanup Edition) ==="

# Directorios
BASE_DIR="$(pwd)"
WORK_DIR="${BASE_DIR}/remaster-work"
MOUNT_DIR="${WORK_DIR}/mount"
USERPATCHES_DIR="${BASE_DIR}/userpatches"

# Crear directorio de trabajo
mkdir -p "${WORK_DIR}"
mkdir -p "${MOUNT_DIR}"

# 1. Localizar imagen base o descargar
IMAGE_BASE_DIR="${BASE_DIR}/image-base"
mkdir -p "${IMAGE_BASE_DIR}"

# NUEVO: Comprobar si ya existe una copia de trabajo para no copiarla de nuevo
IMAGE_FILE=$(find "${WORK_DIR}" -name "base_working_copy.img" | head -n 1)

if [ -n "$IMAGE_FILE" ]; then
    echo "[1/6] Usando copia de trabajo existente en: ${IMAGE_FILE}"
else
    # Buscar en la caché de imagen base
    IMAGE_SOURCE=$(find "${IMAGE_BASE_DIR}" -name "*.img" -o -name "*.img.xz" | head -n 1)

    if [ -n "$IMAGE_SOURCE" ]; then
        echo "[1/6] Imagen base encontrada en caché: $(basename "$IMAGE_SOURCE")"
        echo "Copiando a directorio de trabajo (esto preserva la original)..."
        # Determinamos extensión
        EXT="${IMAGE_SOURCE##*.}"
        cp -v "$IMAGE_SOURCE" "${WORK_DIR}/base_working_copy.${EXT}"
        IMAGE_FILE="${WORK_DIR}/base_working_copy.${EXT}"
    else
        echo "[1/6] No se encontró imagen en ${IMAGE_BASE_DIR}. Iniciando modo manual..."
        cd "${WORK_DIR}"
        echo "Por favor, coloca la imagen oficial (.img o .img.xz) en: ${IMAGE_BASE_DIR}/"
        echo "Presiona Enter cuando esté listo..."
        read
        IMAGE_FILE=$(find "${WORK_DIR}" -name "*.img.xz" -o -name "*.img" | head -n 1)
        if [ -z "$IMAGE_FILE" ]; then
            echo "ERROR: Sigo sin encontrar ninguna imagen base."
            exit 1
        fi
    fi
fi

echo "Procesando: ${IMAGE_FILE}"

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

# A. Copiar scripts al sistema (usr/local/bin)
echo "Copiando scripts de sistema..."
sudo cp -rv "${BASE_DIR}/scripts/"* "${MOUNT_DIR}/usr/local/bin/"
sudo chmod +x "${MOUNT_DIR}/usr/local/bin/"*.sh

# B. Copiar servicios systemd
echo "Copiando servicios systemd..."
sudo cp -rv "${BASE_DIR}/systemd/"*.service "${MOUNT_DIR}/etc/systemd/system/"

# C. Copiar scripts de instalación SARA al home del usuario
echo "Inyectando scripts SARA en el home del usuario..."
mkdir -p "${MOUNT_DIR}/home/AstroOrange/setup"
cp -rv "${BASE_DIR}/scripts/"* "${MOUNT_DIR}/home/AstroOrange/setup/"
chown -R 1000:1000 "${MOUNT_DIR}/home/AstroOrange/setup"
chmod +x "${MOUNT_DIR}/home/AstroOrange/setup/"*.sh

# Ejecutar customize-image.sh en el chroot para habilitar todo
echo "Habilitando servicios en chroot..."
sudo cp "${USERPATCHES_DIR}/customize-image.sh" "${MOUNT_DIR}/tmp/"

# Preparar chroot
sudo mount --bind /dev "${MOUNT_DIR}/dev"
sudo mount --bind /proc "${MOUNT_DIR}/proc"
sudo mount --bind /sys "${MOUNT_DIR}/sys"

# Ejecutar personalización
sudo chroot "${MOUNT_DIR}" /bin/bash /tmp/customize-image.sh

# Limpiar
sudo rm "${MOUNT_DIR}/tmp/customize-image.sh"

# 5. Desmontar y Limpiar de forma robusta
echo "[5/6] Desmontando imagen de forma segura..."
sync
sleep 2

# Desmontar en orden inverso
sudo umount -l "${MOUNT_DIR}/dev" || true
sudo umount -l "${MOUNT_DIR}/proc" || true
sudo umount -l "${MOUNT_DIR}/sys" || true
sudo umount -l "${MOUNT_DIR}/boot" || true
sudo umount -l "${MOUNT_DIR}" || true

# Asegurar que los procesos en el chroot han muerto
sudo fuser -k "${MOUNT_DIR}" || true

# Liberar loop device
sudo losetup -d "$LOOP_DEVICE" || true
sync

# Verificación final de consistencia
echo "Realizando chequeo final de integridad..."
sudo e2fsck -f -y "$IMAGE_FILE" || true

# 6. Comprimir imagen final
echo "[6/6] Comprimiendo imagen final..."
OUTPUT_DIR="${BASE_DIR}/output"
mkdir -p "${OUTPUT_DIR}"

OUTPUT_NAME="AstroOrange-v2.3-$(date +%Y%m%d).img"
mv "$IMAGE_FILE" "${OUTPUT_DIR}/${OUTPUT_NAME}"

cd "${OUTPUT_DIR}"
echo "Comprimiendo con xz (nivel ligero para evitar falta de RAM)..."
xz -v -1 -T0 "${OUTPUT_NAME}"

echo ""
echo "=== ¡Proceso de construcción completado! ==="
echo "Imagen final: ${OUTPUT_DIR}/${OUTPUT_NAME}.xz"
echo ""

# 7. ENTREGA Y LIMPIEZA AUTOMÁTICA
echo "[7/7] Iniciando servidor de entrega..."
echo "Una vez descargues la imagen en tu Windows, cierra este servidor (Ctrl+C) para limpiar los temporales."
python3 "${BASE_DIR}/scripts/serve_image.py"

echo "Limpiando directorio de trabajo..."
sudo rm -rf "${WORK_DIR}"
echo "✅ Sistema limpio. ¡Misión cumplida!"
