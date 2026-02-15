# 🍊 AstroOrange V2

**Specialized OS for Astrophotography on Orange Pi 5 Pro**  
*(Versión en español más abajo)*

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Platform](https://img.shields.io/badge/Platform-Orange%20Pi%205%20Pro-orange)](https://github.com/ec7bm/OPI5_Astro)
[![Based on](https://img.shields.io/badge/Based%20on-Ubuntu%2022.04%20LTS-E95420)](https://ubuntu.com/)

---

## 🇬🇧 English Version

AstroOrange V2 is a Linux distribution based on **Ubuntu 22.04 Jammy Server** optimized for astrophotography. Designed for **Orange Pi 5 Pro**, it provides a ready-to-use environment with:

- 🛰️ **Automatic Rescue Hotspot** - Always accessible without WiFi.
- 🖥️ **VNC Remote Desktop** - Control via web browser (noVNC).
- 🧙 **Configuration Wizard V1.0 (OFFICIAL)** - Guided setup with multi-language support.
- 🔭 **Modular Astronomy Software** - KStars, INDI, PHD2, ASTAP, Stellarium, CCDciel, Syncthing.
- 🌍 **Full Multi-language (i18n)** - Interface in Spanish and English with easy switching.


### 🚀 Installation

#### Option A: Flash Image (Recommended)
1. **Download Image**: 👉 **[DOWNLOAD V1.0 RELEASE](https://mega.nz/file/JyoyUYbY#9YIcKYpPqbDiS3IK3Sx8MahcoyAL5AGG3Yovx1qYYbQ)**
2. Flash to microSD using [balenaEtcher](https://www.balena.io/etcher/).
3. Boot and connect to WiFi: `AstroOrange-Autostart` (Pass: `astroorange`).

#### Option B: Universal Script
Run on existing Armbian/Ubuntu system:
```bash
git clone https://github.com/ec7bm/OPI5_Astro.git
cd OPI5_Astro
sudo ./install.sh
```

#### Option C: Standalone Wizards
If you only want to use the wizards on your own Linux system (Ubuntu/Debian):
```bash
# 1. Clone the repository
git clone https://github.com/ec7bm/OPI5_Astro.git
cd OPI5_Astro

# 2. Install dependencies
sudo apt update
sudo apt install -y python3-tk python3-pil python3-pil.imagetk

# 3. Install scripts and wizards
sudo mkdir -p /opt/astroorange/{scripts,wizard}
sudo cp -r scripts/* /opt/astroorange/scripts/
sudo cp -r wizard/* /opt/astroorange/wizard/
sudo chmod +x /opt/astroorange/scripts/*.sh

# 4. Configure sudoers (required for wizards)
sudo cp userpatches/90-astroorange-wizards /etc/sudoers.d/
sudo chmod 440 /etc/sudoers.d/90-astroorange-wizards

# 5. Run the Setup Wizard
python3 /opt/astroorange/wizard/astro-setup-wizard.py
```


📖 **[READ FULL USER MANUAL (ENGLISH)](MANUAL_USER.md)**

---

## 🇪🇸 Versión en Español

AstroOrange V2 es una distribución Linux basada en **Ubuntu 22.04 Jammy Server** optimizada para astrofotografía. Diseñada para funcionar en **Orange Pi 5 Pro**.

### Características Principales
- 🛰️ **Hotspot de rescate automático** - Acceso garantizado sin WiFi (`AstroOrange-Autostart` / `astroorange`).
- 🖥️ **Escritorio remoto VNC** - Control desde navegador web (noVNC).
- 🧙 **Wizard de configuración V1.0 (OFICIAL)** - Setup guiado multilingüe con UI premium.
  - **Nuevo**: Soporte completo para **Español e Inglés**.
  - **Nuevo**: Conexión manual a redes ocultas y soporte de IP estática seguro.
- 🔭 **Software astronómico modular** - Instalador gráfico para KStars, INDI, PHD2, ASTAP, Stellarium, CCDciel, Syncthing.
  - **Nuevo**: Creación automática de iconos en el escritorio.
- 🌍 **Internacionalización (i18n)** - Cambia de idioma en segundos desde el selector integrado.

- 🎨 **Interfaz moderna** - Tema Arc-Dark, iconos Papirus y wallpaper astronómico universal.

### 🚀 Instalación y Descarga

#### 📀 Opción A: Imagen Completa (Recomendada)
**Ideal para empezar de cero.** Flashea la imagen y tendrás el sistema listo.

1. **Descarga la imagen** (.img.xz):
   👉 **[DESCARGAR IMAGEN V1.0 AQUÍ](https://mega.nz/file/JyoyUYbY#9YIcKYpPqbDiS3IK3Sx8MahcoyAL5AGG3Yovx1qYYbQ)**

2. **Flashea** en tu microSD con [balenaEtcher](https://www.balena.io/etcher/).
3. **Arranca** tu Orange Pi 5 Pro y conéctate al WiFi `AstroOrange-Autostart` (Clave: `astroorange`).

#### 🛠️ Opción B: Script Universal
**Para sistemas existentes (Armbian/Ubuntu).**

```bash
git clone https://github.com/ec7bm/OPI5_Astro.git
cd OPI5_Astro
sudo ./install.sh
```

#### 🐍 Opción C: Ejecución Manual de Wizards
Si solo quieres usar las herramientas gráficas en tu propio Linux:
```bash
# 1. Clonar el repositorio
git clone https://github.com/ec7bm/OPI5_Astro.git
cd OPI5_Astro

# 2. Instalar dependencias
sudo apt update
sudo apt install -y python3-tk python3-pil python3-pil.imagetk

# 3. Instalar scripts y wizards
sudo mkdir -p /opt/astroorange/{scripts,wizard}
sudo cp -r scripts/* /opt/astroorange/scripts/
sudo cp -r wizard/* /opt/astroorange/wizard/
sudo chmod +x /opt/astroorange/scripts/*.sh

# 4. Configurar sudoers (necesario para los wizards)
sudo cp userpatches/90-astroorange-wizards /etc/sudoers.d/
sudo chmod 440 /etc/sudoers.d/90-astroorange-wizards

# 5. Ejecutar el wizard de configuración
python3 /opt/astroorange/wizard/astro-setup-wizard.py
```


📖 **[LEER MANUAL DE USUARIO (ESPAÑOL)](MANUAL_USUARIO.md)**

---

## ☕ Support / Donaciones

If AstroOrange helps you in your astrophotography nights, consider buying me a coffee. Your support keeps development alive!

Si AstroOrange te ha ayudado en tus noches de astrofotografía y quieres agradecer el trabajo, puedes invitarme a un café.

<div align="center">
  <a href="https://paypal.me/astroopi5">
    <img src="assets/donation/paypal-donate.gif" alt="Donate with PayPal" width="200" />
  </a>
  <br>
  <a href="https://paypal.me/astroopi5">
    <b>Click here to Donate / Clic aquí para Donar</b>
  </a>
</div>

---

## 📝 License & Credits

Licensed under **GPL v3**.
Based on **Armbian**, **INDI Library**, **KStars**, and the Open Source community.

- **Author**: EC7BM
- **GitHub**: [@ec7bm](https://github.com/ec7bm)

⭐ **Star this project on GitHub!**
