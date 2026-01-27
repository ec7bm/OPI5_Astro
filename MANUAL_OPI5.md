# Manual de Instalación: AstroOrange Pro (OPI5 Pro)

**Sistema Objetivo:** Orange Pi 5 Pro
**Sistema Operativo:** Ubuntu Server (Jammy/Noble)
**Repositorio:** `https://github.com/ec7bm/OPI5_Astro.git`

Este manual detalla el proceso para transformar una imagen oficial limpia de Orange Pi en una estación astronómica completa usando la rama `manual-setup`.

---

## 🚀 Instalación Rápida

### Paso 1: Obtener los Scripts
Conéctate por SSH a tu Orange Pi y clona la rama especializada:

```bash
git clone -b manual-setup https://github.com/ec7bm/OPI5_Astro.git setup-astro
cd setup-astro/scripts
chmod +x *.sh
```

### Paso 2: Ejecución Secuencial
Ejecuta los scripts en orden. **Lee los mensajes de pantalla.**

| Orden | Script | Acción |
| :--- | :--- | :--- |
| **00** | `sudo ./00_setup_network.sh` | Configura WiFi vía `nmtui`. |
| **01** | `sudo ./01_install_desktop.sh` | Instala XFCE4. **REQ. REINICIO** |
| **02** | `./02_install_remote_access.sh` | Configura VNC y noVNC (Puerto 6080). |
| **03** | `sudo ./03_install_astronomy.sh` | Instala KStars, INDI y PHD2. |
| **04** | `./04_install_syncthing.sh` | Instala Syncthing y limpia Firefox. |

---

## 🌐 Cómo Acceder

### 🖥️ Escritorio Remoto (Navegador)
*   **URL:** `http://<IP-DE-TU-PI>:6080/vnc.html`
*   **Contraseña:** La que definiste en el script `02`.

### 🔄 Sincronización (Syncthing)
*   **URL:** `http://<IP-DE-TU-PI>:8384`

---

## 🛠️ Utilidades Extras
Si Firefox deja de funcionar en el entorno remoto (común tras actualizaciones de Ubuntu), ejecuta:
`sudo ./fix_browser.sh`

---
*¡Cielos despejados!* 🌌🔭
