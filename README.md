# 🌌 AstroOrange Pro v2.1 - Ubuntu Jammy Remaster Edition

AstroOrange is a robust, modular, and professional operating system image for **Orange Pi 5 Pro**, specifically designed for astrophotography. It is based on the official Orange Pi Ubuntu Jammy Server to guarantee maximum hardware compatibility and stability.

---

## 🚀 Guía de Arranque y Configuración (Tutorial)

### 1. Primer Inicio: Conexión al Hotspot
Al encender tu Orange Pi por primera vez, el sistema detectará que no hay una red Wi-Fi configurada y levantará automáticamente un punto de acceso (Hotspot).

- **Nombre de red (SSID)**: `AstroOrange`
- **Contraseña**: `password`
- **IP del Sistema**: `192.168.4.1`

### 2. Acceso al Escritorio Virtual
Una vez conectado al Wi-Fi `AstroOrange`, puedes acceder al escritorio gráfico desde cualquier dispositivo (Móvil, Tablet o Portátil) sin instalar nada:

1. Abre tu navegador web.
2. Ve a la dirección: `http://192.168.4.1:6080`
3. Verás el escritorio de AstroOrange (Nebulosa del Velo de fondo).

### 3. Configuración de Wi-Fi Real
Para poder descargar el software astronómico, necesitas conectar la placa a internet:

1. En el escritorio virtual, verás un icono de red en la barra de tareas (esquina inferior derecha).
2. Haz clic en él y selecciona tu red Wi-Fi de casa/observatorio.
3. Introduce tu contraseña y espera a que conecte.
4. **IMPORTANTE**: Una vez conectado, abre la terminal en el escritorio y escribe:
   ```bash
   sudo reboot
   ```

### 4. Segundo Inicio: El Setup Wizard
Tras el reinicio, AstroOrange se conectará a tu Wi-Fi. Accede de nuevo vía navegador (ahora usando la nueva IP que le haya dado tu router, o sigue usando el cable ethernet si prefieres).

Al entrar al escritorio, saltará automáticamente el **AstroOrange Setup Wizard** (pantalla azul).
- Selecciona el software que quieres instalar (INDI, KStars, PHD2, ASTAP, etc.).
- El sistema descargará e instalará todo automáticamente.
- Al terminar, se reiniciará una última vez y ¡listo para capturar el cielo! 🌌

---

## 🏗️ Guía de Construcción (Para Desarrolladores)

Si deseas "cocinar" tu propia imagen desde una VM Linux:

1. **Clonar el repo y actualizar**:
   ```bash
   cd ~/astro/OPI5_Astro
   git pull
   ```

2. **Ejecutar el Build Maestro**:
   ```bash
   sudo ./build.sh
   ```

3. **Recuperar la Imagen**:
   Una vez termine, usa el script de servicio para bajarla a tu Windows:
   ```bash
   python3 scripts/serve_image.py
   ```

---

## 🛠️ Detalles Técnicos
- **Base**: Ubuntu 22.04 Jammy (Vendor Kernel 5.10).
- **Escritorio**: Fluxbox (Ultra-ligero).
- **Remoto**: noVNC (Puerto 6080) + VNC (Puerto 5900).
- **Hostname**: `astroorange.local`
- **Usuario**: `OPI5_Astro` (Contraseña: `password`).

---

## 📝 Notas de Versión v2.1
- ✨ **Rebranding**: Cambio de nombre oficial a **AstroOrange**.
- 🛠️ **Arquitectura Modular**: Scripts separados en `/scripts` y servicios en `/systemd`.
- 🌐 **IP Estándar**: Hotspot actualizado a `192.168.4.1`.
- 📦 **Build Optimizado**: Compresión ligera para evitar errores de memoria en la VM.
