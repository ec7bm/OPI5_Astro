Armbian-unofficial_26.02.0-trunk_Orangepi5_jammy_vendor_6.1.115_minimal.img
Armbian-unofficial_26.02.0-trunk_Orangepi5_jammy_vendor_6.1.115_minimal.img.sha
Armbian-unofficial_26.02.0-trunk_Orangepi5_jammy_vendor_6.1.115_minimal.img.txt
# 🌌 Astro OPI 5 Pro (v2 - Setup Wizard)

Este proyecto automatiza la creación de una imagen base ligera de **Armbian Jammy** para la **Orange Pi 5 Pro**, optimizada para astrofotografía. 

A diferencia de las versiones tradicionales "todo en uno", este sistema utiliza un **Asistente de Instalación (Setup Wizard)** que permite elegir qué software instalar una vez que la placa ha arrancado.

## 🚀 Guía de Inicio Rápido

1.  **Flashear**: Graba el archivo `.img.xz` en una MicroSD usando **Raspberry Pi Imager**.
2.  **Arranque**: Inserta la tarjeta en la Orange Pi 5 Pro y conéctala a la alimentación. Espera 2-3 minutos.
3.  **Conexión**: Conéctate a la red Wi-Fi generada por la placa:
    *   **SSID**: `OPI5_Astro`
    *   **Password**: `password`
4.  **Acceso Gráfico**: Abre tu navegador y entra en: `http://10.0.0.1:6080`
5.  **Setup Wizard**: Al entrar, se lanzará automáticamente el asistente. Sigue los pasos:
    *   Mira el tour fotográfico inicial.
    *   Selecciona el software deseado (INDI, KStars, PHD2, ASTAP, etc.).
    *   Espera a que finalice la instalación con la barra de progreso.

## 🛠️ Credenciales y Puertos
*   **Usuario**: `OPI5_Astro`
*   **Contraseña**: `password`
*   **Escritorio Remoto (noVNC)**: Puerto `6080`
*   **Gestión de Red (Cockpit)**: Puerto `9090` (Opcional)
*   **Sincronización (Syncthing)**: Puerto `8384`

## 📦 Software Disponible en el Wizard
- **INDI Server (Core/Full)**: Drivers para hardware astronómico.
- **KStars / Ekos**: Suite completa de control y planetario.
- **PHD2**: Autoguiado de alta precisión.
- **ASTAP**: Plate Solving rápido con bases de datos estelares.
- **SkyChart (Cartes du Ciel)**: Software de mapas estelares.
- **AstroDMx Capture**: Captura avanzada para cámaras astronómicas.

## 📁 Estructura del Repositorio
- `build.sh`: Script principal para construir la imagen base.
- `userpatches/`: Configuraciones y hooks de personalización.
- `scripts/astro-wizard.sh`: El script del asistente gráfico.
a (Desde el Escritorio)
**Desde el escritorio remoto (noVNC)**:
1.  Haz clic en el **icono de red** de la barra de tareas (abajo).
2.  Se abrirá un menú con todas las redes Wi-Fi disponibles.
3.  Selecciona tu red Wi-Fi de casa.
4.  Introduce la contraseña y pulsa **Conectar**.
5.  La Orange Pi se conectará a tu red y el hotspot `OPI5_Astro` desaparecerá.

**Alternativa por SSH**: También puedes usar `ssh OPI5_Astro@10.0.0.1` (password: `password`) y ejecutar `sudo nmtui`.

Al reiniciar, la Orange Pi se conectará a tu Wi-Fi y el hotspot desaparecerá.

---

## 🛠️ Stack de Software Incluido
*   **INDI Server**: Drivers de monturas y cámaras.
*   **KStars / Ekos**: Suite de control astronómico principal.
*   **PHD2 / PHDLogViewer**: Autoguiado profesional y visor de logs.
*   **AstroDMx Capture**: Captura planetaria y de cielo profundo.
*   **ASTAP**: Plate solver ultra rápido con base de datos D50 incluida.
*   **Syncthing**: Sincronización automática de tus fotos con tu PC.
*   **GPSD**: Monitorización de satélites para sincronizar hora/ubicación vía GPS USB.
*   **Widget Conky**: Monitorización en tiempo real de temperatura y red.

---

## 💡 Guía de Uso de Servicios

### Cómo iniciar INDI Server manualmente
Si prefieres no usar Ekos para lanzar los drivers, puedes hacerlo por terminal:
```bash
# Ejemplo para una montura OnStep y una cámara ASI
indiserver -v indi_lx200_OnStep indi_asi_ccd
```

### Solución de Problemas (FAQ)
*   **Acceso a puertos serie**: El usuario `armbian` ya pertenece al grupo `dialout`. Si usas otro usuario, añádelo con `sudo usermod -a -G dialout $USER`.
*   **Cámaras DSLR**: Se ha desactivado el auto-montaje de discos para evitar que el sistema bloquee tu cámara antes de que INDI pueda usarla.
*   **Rendimiento**: El sistema ha sido optimizado eliminando `cloud-init`, lo que reduce el tiempo de arranque drásticamente.
*   **Estabilidad**: Se ha creado un archivo SWAP de 2GB para evitar cuelgues durante procesos pesados de apilado o captura.

---

## 🏗️ Cómo construir la imagen (Para Desarrolladores)

1.  Clonar este repositorio en una VM Ubuntu: `git clone https://github.com/ec7bm/OPI5_Astro.git`
2.  Dar permisos: `chmod +x build.sh`
3.  Ejecutar: `sudo ./build.sh`
4.  Subir a GitHub: `./scripts/upload-release.sh`
