#!/bin/bash

# Astro Wizard TUI - Asistente de Instalación Astronómica
# Se ejecuta en el segundo arranque (Fase 2) tras configurar la red

set -e

# Colores y variables
TITLE="Astro OPI 5 Pro - Setup Wizard"
BACKTITLE="Instalador de Software Astronómico v1.0"
LOGfile="/var/log/astro-wizard.log"

# Función para registrar log
log() {
    echo "$(date) - $1" >> "$LOGfile"
}

log "Iniciando Astro Wizard..."

# Comprobar si somos root
if [ "$EUID" -ne 0 ]; then
  whiptail --title "Error" --msgbox "Este script debe ejecutarse como root (sudo)." 8 45
  exit 1
fi

# Pantalla de bienvenida
whiptail --title "$TITLE" --msgbox "¡Bienvenido a tu Astro OPI 5 Pro! 🌌🔭\n\nEste asistente te ayudará a instalar el software astronómico que necesitas.\n\nAsegúrate de estar conectado a Internet antes de continuar." 15 60

# Menú principal de selección de software
CHOICES=$(whiptail --title "Selección de Software" --checklist \
"Selecciona los componentes que deseas instalar:" 20 78 12 \
"INDI" "Servidor INDI + Drivers (Core)" ON \
"KSTARS" "Planetario KStars + Ekos (Control total)" ON \
"PHD2" "Guiado PHD2 Guiding" ON \
"ASTAP" "Plate Solving Rápido + Base de datos D50" ON \
"SKYCHART" "Cartes du Ciel (Planetario clásico)" OFF \
"ASTRODMX" "AstroDMx Capture (Cámaras)" OFF \
"SYNCTHING" "Sincronización de archivos (Nube personal)" ON \
3>&1 1>&2 2>&3)

# Si el usuario cancela
if [ $? -ne 0 ]; then
    log "Usuario canceló el wizard."
    exit 0
fi

# Confirmación
whiptail --title "Confirmación" --yesno "Se instalarán los siguientes componentes:\n$CHOICES\n\n¿Deseas continuar? (Esto puede tardar unos minutos)" 15 60
if [ $? -ne 0 ]; then
    log "Usuario rechazó la instalación."
    exit 0
fi

# Proceso de instalación
{
    PKG_LIST=""
    
    # 1. Preparar lista de paquetes según selección
    if [[ "$CHOICES" == *"INDI"* ]]; then
        echo "XXX\n10\nPreparando INDI Core...\nXXX"
        PKG_LIST="$PKG_LIST indi-full gsc"
    fi

    if [[ "$CHOICES" == *"KSTARS"* ]]; then
        echo "XXX\n20\nPreparando KStars y Ekos...\nXXX"
        PKG_LIST="$PKG_LIST kstars-bleeding"
    fi

    if [[ "$CHOICES" == *"PHD2"* ]]; then
        echo "XXX\n30\nPreparando PHD2...\nXXX"
        PKG_LIST="$PKG_LIST phd2"
    fi

    if [[ "$CHOICES" == *"SKYCHART"* ]]; then
        echo "XXX\n40\nPreparando SkyChart...\nXXX"
        PKG_LIST="$PKG_LIST skychart"
    fi

    # Instalación real de paquetes APT
    echo "XXX\n50\nActualizando repositorios y descargando paquetes...\nXXX"
    apt-get update >> "$LOGfile" 2>&1
    
    if [ ! -z "$PKG_LIST" ]; then
        echo "XXX\n60\nInstalando paquetes seleccionados: $PKG_LIST...\nXXX"
        DEBIAN_FRONTEND=noninteractive apt-get install -y $PKG_LIST >> "$LOGfile" 2>&1
    fi

    # Instalación especial: ASTAP (deb externo)
    if [[ "$CHOICES" == *"ASTAP"* ]]; then
        echo "XXX\n70\nInstalando ASTAP y base de datos D50...\nXXX"
        # ASTAP binario
        wget -q https://github.com/hn-88/astap_binary/raw/main/astap_aarch64.deb -O /tmp/astap.deb
        apt-install /tmp/astap.deb >> "$LOGfile" 2>&1 || apt-get install -f -y >> "$LOGfile" 2>&1
        
        # Base de datos D50 (ligera)
        wget -q https://downloads.sourceforge.net/project/astap-program/star_databases/d50_star_database.zip -O /tmp/d50.zip
        unzip -o /tmp/d50.zip -d /opt/astap >> "$LOGfile" 2>&1
        rm /tmp/astap.deb /tmp/d50.zip
    fi

    # Instalación especial: AstroDMx
    if [[ "$CHOICES" == *"ASTRODMX"* ]]; then
        echo "XXX\n80\nInstalando AstroDMx Capture...\nXXX"
        # URL de ejemplo, habría que buscar la url real dinámica o fija
        # Por ahora lo dejamos como placeholder funcional
        log "AstroDMx seleccionado pero URL pendiente de definir."
    fi

    # Configuración de Syncthing
    if [[ "$CHOICES" == *"SYNCTHING"* ]]; then
        echo "XXX\n90\nConfigurando Syncthing...\nXXX"
        systemctl enable syncthing@OPI5_Astro --now >> "$LOGfile" 2>&1
    fi

    echo "XXX\n100\n¡Instalación completada!\nXXX"
    sleep 2

} | whiptail --title "Instalando..." --gauge "Por favor espere mientras se configura su sistema astronómico..." 10 70 0

# Finalización
whiptail --title "¡Éxito!" --msgbox "La instalación ha finalizado correctamente.\n\nEl sistema se reiniciará ahora para aplicar todos los cambios.\n\n¡Cielos despejados! 🌠" 10 60

# Desactivar el flag de primer arranque para que no vuelva a salir el wizard
rm -f /home/OPI5_Astro/.first_boot_wizard

# Reiniciar
reboot
