# 🌌 Astro OPI 5 Pro (Armbian Jammy)
Este proyecto automatiza la creación de una imagen personalizada de **Armbian** para la **Orange Pi 5 Pro**, diseñada específicamente para astrofotografía. Incluye un stack completo de software astronómico y un entorno gráfico accesible desde el navegador.

## 🚀 Guía de Inicio Rápido (Post-Flasheo)

Una vez que hayas flasheado la imagen en tu tarjeta SD o eMMC, sigue estos pasos:

### 1. Primer Arranque
Conecta la Orange Pi a la alimentación. No necesitas monitor ni teclado. El sistema tardará un par de minutos en arrancar y auto-configurarse la primera vez.

### 2. Conexión al Hotspot
El sistema creará automáticamente una red Wi-Fi si no detecta una conocida:
*   **SSID (Nombre)**: `OPI5_Astro`
*   **Password**: `password`
*   **IP del Sistema**: `10.0.0.1`

Conecta tu móvil o PC a esta red `OPI5_Astro`.

### 3. Acceso al Escritorio Remoto
Abre tu navegador y ve a: **`http://10.0.0.1:6080`**

Verás el escritorio completo con:
*   Fondo astronómico de la Vía Láctea.
*   Widget de monitorización (Conky) en la esquina superior derecha.
*   **Barra de tareas** en la parte inferior con el **icono de red** (dos flechas o señal Wi-Fi).

### 4. Conectarte a tu Wi-Fi de Casa (Desde el Escritorio)
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
