# 🍊 AstroOrange V2

**Sistema operativo especializado para astrofotografía en Orange Pi 5 Pro**

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Platform](https://img.shields.io/badge/Platform-Orange%20Pi%205%20Pro-orange)](https://github.com/ec7bm/OPI5_Astro)
[![Based on](https://img.shields.io/badge/Based%20on-Ubuntu%2022.04%20LTS-E95420)](https://ubuntu.com/)

---

AstroOrange V2 es una distribución Linux basada en **Ubuntu 22.04 Jammy Server** optimizada para astrofotografía. Diseñada para funcionar en **Orange Pi 5 Pro**, proporciona un entorno completo y listo para usar con:

- 🛰️ **Hotspot de rescate automático** - Acceso garantizado sin WiFi
- 🖥️ **Escritorio remoto VNC** - Control desde navegador web (noVNC)
- 🧙 **Wizard de configuración V6.5** - Setup guiado en español con UI premium
  - Configuración de usuario con validación
  - Gestor de red WiFi con recomendación de IP fija
  - Instalador de software astronómico con carrusel visual
- 🔭 **Software astronómico modular** - KStars, INDI, PHD2, ASTAP, Stellarium, CCDciel, Syncthing
- 🎨 **Interfaz moderna** - Tema Arc-Dark con iconos Papirus


---

## 🚀 Instalación Rápida

Tienes **dos opciones** para instalar AstroOrange V2:

### Opción A: Imagen Pre-construida (Recomendada)

**La forma más rápida de empezar:**

1. **Descarga la imagen** desde [Releases](https://github.com/ec7bm/OPI5_Astro/releases)
   ```
   AstroOrange-YYYYMMDD.img.xz
   ```

2. **Flashea la imagen** en una microSD (16GB o superior)
   - **Windows/Mac/Linux**: Usa [balenaEtcher](https://www.balena.io/etcher/)
   - **Linux**: Usa `dd` o [Raspberry Pi Imager](https://www.raspberrypi.com/software/)

3. **Conecta un cable Ethernet** a tu Orange Pi 5 Pro (Recomendado para la configuración inicial).
4. **Enciende la placa** y accede al VNC en tu navegador: `http://<ip-de-la-placa>:6080/vnc.html`
   - *Nota: Si no usas cable, el sistema activará el Hotspot `AstroOrange-Setup` (clave: `astrosetup`) como método de rescate.*

📖 **Manual completo**: [MANUAL_USUARIO.md](MANUAL_USUARIO.md)

---

### Opción B: Transformación desde Imagen Oficial (Live Setup)

**Si ya tienes la imagen oficial instalada y quieres "AstroOrangizarla" en segundos:**

1. **Descarga e instala la imagen oficial** en tu Orange Pi:
   - **URL**: [Google Drive (Oficial OPi5 Pro)](https://drive.google.com/file/d/1VjZFMH9JVxtrqRX7U5BXZ6T1KtZ6QjN6/view?usp=drive_link)
2. **Arranca tu Orange Pi** y conéctate a internet (Ethernet recomendado).
3. **Clona y ejecuta el script de transformación**:
   ```bash
   git clone https://github.com/ec7bm/OPI5_Astro.git
   cd OPI5_Astro
   git checkout v2-release
   sudo chmod +x setup-live.sh
   sudo ./setup-live.sh
   ```
4. El script instalará automáticamente todos los temas, servicios y el Wizard.
5. Al finalizar, el sistema se reiniciará directamente en el **AstroOrange Wizard**.

---

## 📁 Estructura del Proyecto

```
OPI5_Astro/
├── build.sh                    # Script principal de construcción
├── image-base/                 # Imagen base oficial (no incluida)
├── scripts/                    # Scripts del sistema
│   ├── astro-network.sh       # Hotspot de rescate
│   └── astro-vnc.sh           # VNC headless
├── systemd/                    # Servicios systemd
│   ├── astro-network.service
│   └── astro-vnc.service
├── userpatches/               # Customización
│   ├── customize-image.sh     # Script de personalización
│   ├── astro-wallpaper.jpg    # Fondo astronómico
│   └── gallery/               # Imágenes del carrusel (v2-modular)
├── output/                    # Imágenes finales generadas
└── MANUAL_USUARIO.md          # Manual de usuario
```

---

## 🌟 Características

### Sistema Base
- **OS**: Ubuntu 22.04 LTS (Jammy Jellyfish)
- **Desktop**: XFCE4 con tema Arc-Dark
- **Iconos**: Papirus-Dark
- **Acceso remoto**: VNC + noVNC (acceso por navegador)

### Red
- **Hotspot automático**: Se activa si no hay internet
- **SSID**: `AstroOrange-Setup`
- **Seguridad**: WPA2-PSK compatible con Orange Pi 5 Pro
- **IP del Hotspot**: `10.42.0.1`

### Software Astronómico (Opcional)
- **KStars + INDI**: Planetario y control de equipos
- **PHD2**: Guiado automático
- **ASTAP**: Plate solving
- **Stellarium**: Planetario visual
- **AstroDMX**: Captura profesional
- **CCDciel**: Control avanzado de cámaras
- **Syncthing**: Sincronización de archivos

---

## 🔧 Configuración

### Primera Conexión

1. **Hotspot WiFi**:
   - SSID: `AstroOrange-Setup`
   - Contraseña: `astrosetup`

2. **VNC (Navegador)**:
   - URL: `http://10.42.0.1:6080/vnc.html`
   - Contraseña: `astroorange`

3. **SSH** (Opcional):
   ```bash
   ssh astro-setup@10.42.0.1
   # Contraseña: setup
   ```

### Wizard de Configuración

El sistema incluye un wizard gráfico que te guiará para:
1. Crear tu usuario permanente
2. Configurar WiFi (opcional)
3. Seleccionar e instalar software astronómico

---

## 🛠️ Desarrollo

### Ramas

- **`main`**: Rama principal (estable)
- **`v2-architecture`**: Versión actual estable con todas las mejoras
- **`v2-modular`**: Versión experimental con carrusel de imágenes NASA

### Contribuir

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📝 Changelog

### v2.0 (Enero 2026)
- ✅ Hotspot automático con detección de internet real (ping)
- ✅ Tema Arc-Dark + iconos Papirus
- ✅ Fondo de pantalla astronómico
- ✅ Fix del cursor "X" → flecha estándar
- ✅ Wizard mejorado con selección modular de software
- ✅ VNC headless (funciona sin monitor)
- ✅ Estructura de proyecto modular

### v2.1-experimental (v2-modular)
- 🎨 Carrusel de imágenes NASA durante instalación
- 🌍 Base para soporte multiidioma (futuro)

---

## 📄 Licencia

Este proyecto está licenciado bajo GPL v3 - ver el archivo [LICENSE](LICENSE) para detalles.

### Componentes de Terceros

- **Ubuntu**: [Canonical](https://ubuntu.com/)
- **KStars/INDI**: [GPL v2+](https://indilib.org/)
- **PHD2**: [BSD](https://github.com/OpenPHDGuiding/phd2)
- **ASTAP**: [Freeware](https://www.hnsky.org/astap.htm)

---

## 🙏 Agradecimientos

- **Armbian Team** - Por la excelente base para SBCs
- **INDI Project** - Por el framework de control astronómico
- **KStars Team** - Por el planetario más completo de Linux
- **Comunidad de astrofotografía** - Por el feedback y testing

---

## 📧 Contacto

- **Autor**: EC7BM
- **GitHub**: [@ec7bm](https://github.com/ec7bm)
- **Proyecto**: [OPI5_Astro](https://github.com/ec7bm/OPI5_Astro)

---

## ☕ Apoya el Proyecto

Si AstroOrange te ha ayudado en tus noches de astrofotografía y quieres agradecer el trabajo detrás de esta distribución, puedes invitarme a un café. Tu apoyo ayuda a mantener vivo el desarrollo y el soporte de herramientas para la comunidad.

<div align="center">
  <a href="TU_LINK_DE_PAYPAL_AQUI">
    <img src="assets/donation/paypal-donate.gif" alt="Donar con PayPal" />
  </a>
</div>

---

**⭐ Si este proyecto te resulta útil, considera darle una estrella en GitHub!**
