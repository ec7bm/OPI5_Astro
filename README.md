# 🍊 AstroOrange V2

**Sistema operativo especializado para astrofotografía en Orange Pi 5 Pro**

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Platform](https://img.shields.io/badge/Platform-Orange%20Pi%205%20Pro-orange)](https://github.com/ec7bm/OPI5_Astro)
[![Based on](https://img.shields.io/badge/Based%20on-Armbian%20Debian-red)](https://www.armbian.com/)

---

## 📖 Descripción

AstroOrange V2 es una distribución Linux basada en Debian/Armbian optimizada para astrofotografía. Diseñada para funcionar en **Orange Pi 5 Pro**, proporciona un entorno completo y listo para usar con:

- 🛰️ **Hotspot de rescate automático** - Acceso garantizado sin WiFi
- 🖥️ **Escritorio remoto VNC** - Control desde navegador web
- 🧙 **Wizard de configuración** - Setup guiado en español
- 🔭 **Software astronómico modular** - KStars, INDI, PHD2, ASTAP, y más
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

3. **Inserta la SD** en tu Orange Pi 5 Pro y enciéndela

4. **Conéctate al Hotspot** `AstroOrange-Setup` (contraseña: `astrosetup`)

5. **Accede al VNC** en tu navegador: `http://10.42.0.1:6080/vnc.html`

📖 **Manual completo**: [MANUAL_USUARIO.md](MANUAL_USUARIO.md)

---

### Opción B: Construcción desde Fuente

**Para desarrolladores o usuarios avanzados:**

#### Requisitos

- **Sistema**: Ubuntu 22.04 o superior (VM o nativo)
- **Espacio**: Mínimo 30GB libres
- **RAM**: 4GB mínimo, 8GB recomendado
- **Imagen base**: Armbian para Orange Pi 5 Pro

#### Pasos

1. **Clona este repositorio**
   ```bash
   git clone https://github.com/ec7bm/OPI5_Astro.git
   cd OPI5_Astro
   ```

2. **Descarga la imagen base de Armbian**
   
   Descarga la imagen oficial de Armbian para Orange Pi 5 Pro:
   - **URL**: [Armbian Downloads](https://www.armbian.com/orange-pi-5-pro/)
   - **Versión recomendada**: Armbian 24.x Debian Bookworm (CLI o Desktop)
   
   Coloca el archivo `.img.xz` en la carpeta `image-base/`:
   ```bash
   mkdir -p image-base
   mv ~/Downloads/Armbian_*.img.xz image-base/
   ```

3. **Ejecuta el script de construcción**
   ```bash
   chmod +x build.sh
   sudo ./build.sh
   ```

4. **Espera 10-20 minutos** - El script:
   - Descomprimirá la imagen base
   - Expandirá el sistema de archivos
   - Instalará todos los componentes de AstroOrange
   - Generará la imagen final en `output/`

5. **Descarga la imagen**
   
   Al finalizar, el script levantará un servidor HTTP automáticamente:
   ```
   🌐 Starting HTTP server for download...
   Access from your network at:
   http://192.168.X.X:8000/
   ```
   
   Abre esa URL en tu navegador para descargar la imagen.

6. **Flashea la imagen** resultante en tu microSD

---

## 📁 Estructura del Proyecto

```
OPI5_Astro/
├── build.sh                    # Script principal de construcción
├── image-base/                 # Imagen base de Armbian (no incluida)
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
- **OS**: Debian 12 (Bookworm) con kernel Armbian
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

## 🆘 Solución de Problemas

### El Hotspot no aparece

**Solución**:
```bash
# Conecta por Ethernet y ejecuta:
sudo systemctl restart astro-network
sudo journalctl -u astro-network -n 20
```

### VNC no carga

**Solución**:
```bash
sudo systemctl restart astro-vnc
sudo systemctl status astro-vnc
```

### Más ayuda

Consulta el [Manual de Usuario](MANUAL_USUARIO.md) completo o abre un [Issue](https://github.com/ec7bm/OPI5_Astro/issues).

---

## 📄 Licencia

Este proyecto está licenciado bajo GPL v3 - ver el archivo [LICENSE](LICENSE) para detalles.

### Componentes de Terceros

- **Armbian**: [GPL v2](https://www.armbian.com/)
- **Debian**: [DFSG](https://www.debian.org/social_contract)
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

**⭐ Si este proyecto te resulta útil, considera darle una estrella en GitHub!**
