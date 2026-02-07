#!/bin/bash
# AstroOrange - Pre-Build Cleanup Script
# Limpia archivos temporales antes de una nueva construcción

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== AstroOrange Pre-Build Cleanup ===${NC}"

# Verificar que estamos en el directorio correcto
if [ ! -f "build.sh" ]; then
    echo -e "${RED}❌ Error: Ejecuta este script desde el directorio OPI5_Astro${NC}"
    exit 1
fi

# 1. Mostrar espacio actual
echo -e "${YELLOW}📊 Espacio actual:${NC}"
df -h | grep -E "Filesystem|/$"

# 2. Verificar qué se va a borrar
echo -e "\n${YELLOW}📂 Archivos a borrar:${NC}"
du -sh remaster-work 2>/dev/null || echo "   remaster-work: no existe"
du -sh output 2>/dev/null || echo "   output: no existe"
du -sh /tmp/remaster-source 2>/dev/null || echo "   /tmp/remaster-source: no existe"

# 3. Confirmación
echo -e "\n${YELLOW}⚠️  Esto borrará:${NC}"
echo "   - remaster-work/ (archivos temporales del build)"
echo "   - output/ (imágenes antiguas generadas)"
echo "   - /tmp/remaster-source (cache del sistema)"
echo ""
echo -e "${GREEN}✅ Se conservará:${NC}"
echo "   - image-base/ (imagen original)"
echo "   - scripts/, wizard/, userpatches/ (código fuente)"
echo ""
read -p "¿Continuar? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}❌ Cancelado${NC}"
    exit 0
fi

# 4. Limpieza
echo -e "\n${GREEN}🧹 Limpiando...${NC}"

if [ -d "remaster-work" ]; then
    echo "   🗑️  Borrando remaster-work..."
    sudo rm -rf remaster-work
fi

if [ -d "output" ]; then
    echo "   🗑️  Borrando output..."
    rm -rf output
    mkdir -p output
fi

if [ -d "/tmp/remaster-source" ]; then
    echo "   🗑️  Borrando /tmp/remaster-source..."
    sudo rm -rf /tmp/remaster-source
fi

# 5. Verificar imagen base
echo -e "\n${GREEN}✅ Verificando imagen base...${NC}"
if [ -d "image-base" ] && [ "$(ls -A image-base)" ]; then
    ls -lh image-base/
else
    echo -e "${RED}⚠️  ADVERTENCIA: No se encontró imagen base en image-base/${NC}"
fi

# 6. Mostrar espacio liberado
echo -e "\n${GREEN}📊 Espacio después de la limpieza:${NC}"
df -h | grep -E "Filesystem|/$"

echo -e "\n${GREEN}✅ Limpieza completada. Listo para ejecutar: sudo ./build.sh${NC}"
