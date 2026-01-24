# Astro Orange Pi 5 Image Build System

Sistema de construcción automatizado y reproducible para generar una imagen Linux ARM64 (basada en Armbian) optimizada para astrofotografía y control de telescopios en Orange Pi 5 / 5 Pro.

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

### 3. Acceso Remoto
Tienes tres formas de controlar el sistema:

*   **Navegador Web (noVNC)**: Abre `http://10.0.0.1:6080` en tu navegador. Verás el escritorio con el fondo astronómico y el widget de monitorización.
*   **Escritorio Remoto (VNC)**: Usa cualquier cliente VNC (como VNC Viewer) apuntando a `10.0.0.1:5900` (sin contraseña).
*   **Terminal (SSH)**:
    *   **Usuario**: `armbian` (o el que hayas configurado en el build)
    *   **Comando**: `ssh armbian@10.0.0.1`

### 4. Configurar tu Wi-Fi de Casa
Para que la Orange Pi se conecte a tu internet local y deje de crear el hotspot:
1.  Entra por SSH o abre una terminal en el escritorio remoto.
2.  Escribe: `sudo nmtui`
3.  Selecciona **"Activate a connection"**.
4.  Busca tu red Wi-Fi, pon la clave y acepta.
5.  Reinicia el sistema: `sudo reboot`

Al reiniciar, la Orange Pi se conectará a tu Wi-Fi y el hotspot desaparecerá.

---

## 🛠️ Stack de Software Incluido
*   **INDI Server**: Drivers de monturas y cámaras.
*   **KStars / Ekos**: Suite de control astronómico.
*   **PHD2**: Autoguiado profesional.
*   **AstroDMx Capture**: Captura planetaria y de cielo profundo.
*   **ASTAP**: Plate solver ultra rápido.
*   **Syncthing**: Sincronización automática de tus fotos con tu PC.
*   **Widget Conky**: Monitorización en tiempo real de temperatura y red.

---

## 🏗️ Cómo construir la imagen (Para Desarrolladores)

1.  Clonar este repositorio en una VM Ubuntu: `git clone https://github.com/ec7bm/OPI5_Astro.git`
2.  Dar permisos: `chmod +x build.sh`
3.  Ejecutar: `sudo ./build.sh`
4.  Subir a GitHub: `./scripts/upload-release.sh`
