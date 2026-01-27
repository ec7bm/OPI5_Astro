#!/bin/bash
# auto-installer.sh - Automatic AstroOrange Scripts Execution
set -e

LOG_FILE="/var/log/astroorange-install.log"
FLAG_FILE="/var/lib/astroorange/stage2-pending"
SCRIPTS_DIR="/home/AstroOrange/setup"

exec > >(tee -a "${LOG_FILE}") 2>&1

echo "========================================="
echo "  AstroOrange - Instalación Automática"
echo "  $(date)"
echo "========================================="

# Verificar que existe el flag
if [ ! -f "${FLAG_FILE}" ]; then
    echo "No se encontró flag de stage2. Saliendo."
    exit 0
fi

echo ""
echo "=== Iniciando instalación automática ==="
echo ""

# Esperar a que la red esté lista
echo "[1/5] Esperando conexión de red..."
for i in {1..30}; do
    if ping -c 1 8.8.8.8 &>/dev/null; then
        echo "✓ Red disponible"
        break
    fi
    sleep 2
done

# Ejecutar scripts AstroOrange en orden
cd "${SCRIPTS_DIR}"

echo ""
echo "[2/5] Instalando escritorio XFCE4..."
sudo -u AstroOrange bash 01_install_desktop.sh || true

echo ""
echo "[3/5] Configurando acceso remoto (VNC/noVNC)..."
sudo -u AstroOrange bash 02_install_remote_access.sh || true

echo ""
echo "[4/5] Instalando software astronómico..."
sudo -u AstroOrange bash 03_install_astronomy.sh || true

echo ""
echo "[5/5] Instalando Syncthing y Firefox..."
sudo -u AstroOrange bash 04_install_syncthing.sh || true

# Eliminar flag
rm -f "${FLAG_FILE}"

echo ""
echo "========================================="
echo "  Instalación completada con éxito"
echo "  $(date)"
echo "========================================="
echo ""
echo "Acceso web VNC: https://<IP>:6080/vnc.html"
echo "Syncthing: http://<IP>:8384"
echo ""

# Deshabilitar el servicio para que no se ejecute de nuevo
systemctl disable auto-installer.service

echo "El sistema se reiniciará en 10 segundos..."
sleep 10
reboot
