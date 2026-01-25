#!/bin/bash

# Astro Orange Pi 5 Image Build Wrapper
# Este script prepara el entorno de Armbian y lanza la construcción.

set -e

# Directorios
BASE_DIR="$(pwd)"
ARMBIAN_DIR="${BASE_DIR}/armbian-build"

echo "=== Astro OPI 5 Build System ==="

# 1. Clonar Armbian Build Framework si no existe
if [ ! -d "$ARMBIAN_DIR" ]; then
    echo "Clonando Armbian Build Framework..."
    git clone --depth 1 https://github.com/armbian/build "$ARMBIAN_DIR"
else
    echo "Armbian Build ya existe. Actualizando..."
    cd "$ARMBIAN_DIR" && git pull && cd "$BASE_DIR"
fi

# 2. Sincronizar nuestros parches de usuario
echo "Sincronizando userpatches..."
mkdir -p "${ARMBIAN_DIR}/userpatches"
cp -rv "${BASE_DIR}/userpatches/"* "${ARMBIAN_DIR}/userpatches/"

# 3. Lanzar la construcción
# Parámetros por defecto para Orange Pi 5 (RK3588)
# BOARD: orangepi5 o orangepi5-pro
# RELEASE: jammy (Ubuntu 22.04 LTS)
# BUILD_MINIMAL: yes (Sistemas Headless/Server)
# KERNEL_CONFIGURE: no (Usar config por defecto)

cd "$ARMBIAN_DIR"
./compile.sh \
    BOARD=orangepi5pro \
    BRANCH=vendor \
    RELEASE=jammy \
    BUILD_MINIMAL=yes \
    BUILD_DESKTOP=no \
    KERNEL_CONFIGURE=no \
    EXPERT=yes \
    COMPRESS_OUTPUTIMAGE=sha,gpg,xz \
    "$@"

echo "=== Proceso completado ==="
echo "La imagen resultante debería estar en ${ARMBIAN_DIR}/output/images/"

# Sugerencia para subir a GitHub
echo ""
echo "Opciones post-build:"
echo "1. Subir a GitHub: chmod +x scripts/upload-release.sh && ./scripts/upload-release.sh"
echo "2. Descargar localmente (Levantar servidor HTTP)"
echo ""
read -p "¿Deseas levantar el servidor de descarga ahora? (s/n): " choice
if [[ "$choice" == "s" || "$choice" == "S" ]]; then
    IMAGE_DIR="${ARMBIAN_DIR}/output/images"
    IP_ADDR=$(hostname -I | awk '{print $1}')
    echo "=== Servidor de descarga iniciado ==="
    echo "Abre este enlace en tu navegador de Windows:"
    echo "http://${IP_ADDR}:8080"
    echo ""
    echo "Presiona Ctrl+C para detener el servidor cuando termine la descarga."
    cd "$IMAGE_DIR" && python3 -m http.server 8080
fi
