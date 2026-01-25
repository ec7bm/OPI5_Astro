#!/bin/bash

# Astro Setup Wizard v1.0
# Este script guía al usuario para instalar el software astronómico.

export DISPLAY=:1
User="OPI5_Astro"
Log="/home/$User/astro-setup.log"
Nebula1="/usr/share/backgrounds/astro-nebula-1.jpg"
Nebula2="/usr/share/backgrounds/astro-nebula-2.jpg"

echo "Iniciando Astro Wizard..." > $Log

# 1. Bienvenida con Imagen
zenity --info \
    --title="🌌 Bienvenidos a Astro OPI 5 Pro" \
    --text="Gracias por elegir este sistema personalizado.\n\n⚠️ **IMPORTANTE**: Antes de continuar, asegúrate de estar conectado a una red Wi-Fi con Internet.\n\nPuedes usar el icono de red (dos flechas) en la barra inferior del escritorio para elegir tu red.\n\nPulsa 'Aceptar' una vez tengas Internet para ver el tour y elegir software." \
    --width=450 --height=250

# 2. Mini-Tour (Cambio de fondo intermitente)
(
echo "10" ; sleep 1 ; echo "# Mostrando Nebulosa del Velo..."
feh --bg-fill $Nebula1
echo "50" ; sleep 2 ; echo "# Sabías que... este sistema está optimizado para RK3588."
echo "90" ; sleep 2 ; echo "# Preparando menú de selección..."
feh --bg-fill $Nebula2
) | zenity --progress --title="Tour Astronómico" --text="Cargando entorno..." --percentage=0 --auto-close

# 3. Selección de Software
CHOICES=$(zenity --list --checklist \
    --title="Selección de Software para Astrofotografía" \
    --width=500 --height=400 \
    --column="Instalar" --column="Herramienta" --column="Descripción" \
    TRUE "INDI-Full" "Drivers para monturas, cámaras y enfocadores." \
    TRUE "KStars/Ekos" "Control total del observatorio y planetario." \
    TRUE "PHD2" "Software de autoguiado avanzado." \
    FALSE "ASTAP" "Plate Solving ultra-rápido (incluye base D50)." \
    FALSE "SkyChart" "Planetario Cartes du Ciel." \
    FALSE "AstroDMx" "Captura planetaria y de cielo profundo.")

if [ -z "$CHOICES" ]; then
    zenity --question --text="No has seleccionado nada. ¿Deseas salir del asistente?\n(Podrás lanzarlo más tarde desde el terminal)." || exec $0
    exit 0
fi

# 4. Proceso de Instalación
(
echo "10" ; echo "# Actualizando base de datos de paquetes..."
sudo apt-get update -y >> $Log 2>&1

if [[ $CHOICES == *"INDI-Full"* ]]; then
    echo "20" ; echo "# Instalando INDI Server y Drivers..."
    sudo apt-get install -y indi-full >> $Log 2>&1
fi

if [[ $CHOICES == *"KStars"* ]]; then
    echo "40" ; echo "# Instalando KStars y Ekos..."
    sudo apt-get install -y kstars-bleeding >> $Log 2>&1
fi

if [[ $CHOICES == *"PHD2"* ]]; then
    echo "60" ; echo "# Instalando PHD2 Guiding..."
    sudo apt-get install -y phd2 phdlogview >> $Log 2>&1
fi

if [[ $CHOICES == *"ASTAP"* ]]; then
    echo "80" ; echo "# Instalando ASTAP y Base D50 (Esto puede tardar)..."
    wget https://master.dl.sourceforge.net/project/astap-program/star_databases/d50_star_database.deb -O /tmp/d50.deb
    wget https://sourceforge.net/projects/astap-program/files/linux_installer/astap_aarch64.deb/download -O /tmp/astap.deb
    sudo apt-get install -y /tmp/astap.deb /tmp/d50.deb >> $Log 2>&1
    rm /tmp/*.deb
fi

if [[ $CHOICES == *"SkyChart"* ]]; then
    echo "90" ; echo "# Instalando Cartes du Ciel..."
    sudo apt-get install -y skychart >> $Log 2>&1
fi

if [[ $CHOICES == *"AstroDMx"* ]]; then
    echo "95" ; echo "# Instalando AstroDMx Capture..."
    wget https://www.astrodmx-capture.org.uk/downloads/astrodmx-capture_2.11.2_arm64.deb -O /tmp/astrodmx.deb
    sudo apt-get install -y /tmp/astrodmx.deb >> $Log 2>&1
    rm /tmp/astrodmx.deb
fi

echo "100" ; echo "# ¡Toda la base instalada con éxito!"
) | zenity --progress --title="Instalando Software" --text="Por favor, espera..." --percentage=0 --auto-close

# 5. Finalización
rm -f /home/$User/.first_boot_wizard
zenity --info --title="Instalación Completada" --text="¡Tu Astro OPI 5 Pro está lista!\n\nDisfruta de los cielos oscuros. Se recomienda reiniciar para aplicar todos los cambios."

echo "Wizard completado con éxito." >> $Log
