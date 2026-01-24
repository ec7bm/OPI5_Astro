#!/bin/bash

# Astro OPI - Script de subida a GitHub Releases
# Requiere 'gh' (GitHub CLI) instalado y autenticado.

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ARMBIAN_OUT="${REPO_DIR}/armbian-build/output/images"

echo "=== Preparando subida a GitHub Releases ==="

# 1. Verificar si gh está instalado
if ! command -v gh &> /dev/null; then
    echo "Error: 'gh' (GitHub CLI) no está instalado."
    echo "Instálalo con: sudo apt install gh"
    exit 1
fi

# 2. Buscar la imagen más reciente
IMAGE=$(ls -t ${ARMBIAN_OUT}/*.img.xz 2>/dev/null | head -n 1)

if [ -z "$IMAGE" ]; then
    echo "Error: No se encontró ninguna imagen .img.xz en ${ARMBIAN_OUT}"
    exit 1
fi

IMAGE_NAME=$(basename "$IMAGE")
TAG="v$(date +%Y%m%d-%H%M)"
RELEASE_NAME="Astro Image - $(date +'%Y-%m-%d %H:%M')"

echo "Imagen detectada: ${IMAGE_NAME}"
echo "Creando Release: ${TAG}"

# 3. Crear Release y subir el asset
gh release create "$TAG" "$IMAGE" \
    --title "$RELEASE_NAME" \
    --notes "Imagen generada automáticamente para Orange Pi 5. Lista para flashear."

echo "=== Subida completada con éxito ==="
echo "Puedes descargarla en: https://github.com/ec7bm/OPI5_Astro/releases"
