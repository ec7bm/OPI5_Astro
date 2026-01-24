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
    BOARD=orangepi5 \
    BRANCH=vendor \
    RELEASE=jammy \
    BUILD_MINIMAL=yes \
    BUILD_DESKTOP=no \
    KERNEL_CONFIGURE=no \
    EXPERT=yes \
    "$@"

echo "=== Proceso completado ==="
echo "La imagen resultante debería estar en ${ARMBIAN_DIR}/output/images/"
