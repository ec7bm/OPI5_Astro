# 🍊 AstroOrange V2

**Sistema operativo especializado para astrofotografía en Orange Pi 5 Pro**

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Platform](https://img.shields.io/badge/Platform-Orange%20Pi%205%20Pro-orange)](https://github.com/ec7bm/OPI5_Astro)
[![Based on](https://img.shields.io/badge/Based%20on-Ubuntu%2022.04%20LTS-E95420)](https://ubuntu.com/)

---

AstroOrange V2 es una distribución Linux basada en **Ubuntu 22.04 Jammy Server** optimizada para astrofotografía. Diseñada para funcionar en **Orange Pi 5 Pro**, proporciona un entorno completo y listo para usar.

## 🌟 Características Principales (V10.5)

- 🛰️ **Hotspot de rescate automático (V9.2)** - Acceso garantizado sin WiFi (`AstroOrange-Setup` / `astrosetup`).
- 🖥️ **Escritorio remoto VNC** - Control desde navegador web (noVNC).
- 🧙 **Wizard de configuración V8.4** - Setup guiado en español con UI premium.
  - **Nuevo**: Conexión manual a redes ocultas y soporte de IP estática seguro.
- 🔭 **Software astronómico modular** - Instalador gráfico para KStars, INDI, PHD2, ASTAP, Stellarium, CCDciel, Syncthing.
  - **Nuevo**: Creación automática de iconos en el escritorio.
- 🎨 **Interfaz moderna** - Tema Arc-Dark, iconos Papirus y wallpaper astronómico universal (V10.0).

---

## 🚀 Instalación y Descarga

Tienes **dos opciones** para disfrutar de AstroOrange V2:

### 📀 Opción A: Imagen Completa (Recomendada)
**Ideal para empezar de cero.** Flashea la imagen y tendrás el sistema listo.

1. **Descarga la imagen** (.img.xz):
   👉 **[DESCARGAR IMAGEN V10.5 AQUÍ](https://drive.google.com/file/d/1VjZFMH9JVxtrqRX7U5BXZ6T1KtZ6QjN6/view?usp=drive_link)**

2. **Flashea** en tu microSD con [balenaEtcher](https://www.balena.io/etcher/) o `dd`.
3. **Arranca** tu Orange Pi 5 Pro y conéctate al WiFi `AstroOrange-Setup` (Clave: `astrosetup`).

---

### 🛠️ Opción B: Script Universal (Para sistemas existentes)
**Ideal si ya tienes Armbian o Ubuntu instalado** y quieres añadir nuestras herramientas.

1. Abre una terminal en tu Orange Pi.
2. Clona y ejecuta el instalador:
   ```bash
   git clone https://github.com/ec7bm/OPI5_Astro.git
   cd OPI5_Astro
   sudo ./install.sh
   ```
3. Reinicia y disfruta de los wizards de AstroOrange.

---

## 📁 Estructura del Proyecto

```
OPI5_Astro/
├── build.sh                    # Script de construcción de imágenes
├── install.sh                  # Script de instalación universal
├── scripts/                    # Scripts del sistema (Hotspot, VNC)
├── systemd/                    # Servicios systemd
├── userpatches/               # Customización y Assets
├── wizard/                    # Código fuente de los Wizards (Python/Tkinter)
└── RELEASE_NOTES.md           # Notas de la versión
```

---

## 🔧 Primeros Pasos

### 1. Conexión Inicial
- **WiFi Hotspot**: `AstroOrange-Setup` (Password: `astrosetup`)
- **IP**: `10.42.0.1`

### 2. Acceso
- **VNC (Navegador)**: `http://10.42.0.1:6080/vnc.html` (Password: `astroorange`)
- **SSH**: Usuario `astro-setup` / Password `setup`

### 3. Configuración
Al arrancar, verás el **Setup Wizard** en el escritorio. Úsalo para:
- Crear tu usuario definitivo.
- Conectar a tu WiFi de casa (con opción de IP fija).
- Instalar el software que necesites (KStars, PHD2, etc).

---

## 📝 Licencia y Créditos

Este proyecto está licenciado bajo **GPL v3**.
Basado en el trabajo de **Armbian**, **INDI Library**, **KStars** y la comunidad Open Source.

- **Autor**: EC7BM
- **Proyecto**: [GitHub](https://github.com/ec7bm/OPI5_Astro)

Si este proyecto te resulta útil para tus sesiones de astrofotografía, ¡considera darle una ⭐ estrella en GitHub!
