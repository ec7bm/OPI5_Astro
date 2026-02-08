# 🍊 AstroOrange V2 - Manual de Usuario

**Sistema operativo especializado para astrofotografía en Orange Pi 5 Pro**

---

## 📖 Índice

1. [Introducción](#introducción)
2. [Primer Arranque](#primer-arranque)
3. [Conexión al Sistema](#conexión-al-sistema)
4. [Configuración Inicial](#configuración-inicial)
5. [Instalación de Software](#instalación-de-software)
6. [Uso en el Campo](#uso-en-el-campo)
7. [Solución de Problemas](#solución-de-problemas)

---

AstroOrange V2 es un sistema operativo basado en **Ubuntu 22.04 Jammy Server** diseñado específicamente para astrofotografía. Incluye:

- ✅ **Hotspot de rescate automático** - Siempre accesible sin WiFi
- ✅ **Escritorio remoto VNC (noVNC)** - Control desde cualquier navegador
- ✅ **Wizard de configuración V13.0 (MASTER)** - Setup guiado multilingüe con interfaz premium

  - **Paso 1**: Creación de usuario con validación de contraseña
  - **Paso 2**: Gestor de red WiFi con escaneo automático y recomendación de IP fija
  - **Paso 3**: Instalador de software astronómico con carrusel visual
- ✅ **Software astronómico modular** - KStars/INDI, PHD2, ASTAP, Stellarium, CCDciel, Syncthing
- ✅ **Interfaz moderna** - Tema Arc-Dark con iconos Papirus

---

## 🚀 Primer Arranque

### Requisitos
- Orange Pi 5 Pro
- Tarjeta microSD de 16GB o superior
- Fuente de alimentación 5V/4A
- **Cable Ethernet conectado al router** (Muy recomendable para el primer arranque)

### Proceso de Arranque

1. **Inserta la tarjeta SD** en la Orange Pi 5 Pro
2. **Conecta la alimentación** - El sistema arrancará automáticamente
3. **Espera 30-45 segundos** - El sistema se está inicializando

> ⏱️ **Nota**: El primer arranque puede tardar hasta 1 minuto mientras el sistema se configura.

---

## 📡 Conexión al Sistema

### Opción A (Recomendada): Con Cable Ethernet

1. Conecta la Orange Pi a tu router mediante un cable Ethernet antes de encenderla.
2. El sistema obtendrá una IP automáticamente.
3. Desde tu PC/Tablet, accede a: **`http://<ip-de-la-placa>:6080/vnc.html`**
4. Contraseña del VNC: **`astroorange`**

### Opción B: Sin Cable (Hotspot de Rescate)

Si no tienes cable a mano, el sistema activará un Hotspot propio:
- 📶 **Nombre (SSID):** `AstroOrange-Autostart`
- 🔐 **Contraseña:** `astroorange`
- 🌐 **Acceso VNC:** `http://10.42.0.1:6080/vnc.html`

---
 
 Al acceder por primera vez, verás el **AstroSetup** (Asistente Inicial) que te guiará por las tres herramientas modulares. El sistema detectará si es el primer arranque y te pedirá seleccionar **Español** o **English**.


### 👤 1. AstroUser (Gestión de Usuarios)
- Crea tu nombre de usuario y contraseña principal.
- Configura los permisos de administrador automáticamente.

### 📡 2. AstroNetwork (Gestión de Red)
- Escanea redes WiFi con un clic.
- **Botón "Modo Campo"**: Si no tienes WiFi, puedes omitir este paso y seguir configurando.
- **Detección Automática**: Si ya tienes cable Ethernet con internet, te preguntará si quieres saltar este paso.

### 🔭 3. AstroSoftware (Instalación de Aplicaciones)
Tras el primer arranque, podrás abrir el instalador cuando quieras para añadir:

| Software | Descripción |
|----------|-------------|
| **KStars + INDI** | Planetario y control de hardware |
| **PHD2 Guiding** | Autoguiado profesional |
| **ASTAP** | Plate Solving rápido |
| **Stellarium** | Atlas estelar visual |
| **AstroDMX** | Captura de imágenes planetaria/cielo profundo |
| **CCDciel** | Captura avanzada |
| **Syncthing** | Copia de seguridad automática de fotos |

---

## 🍱 Herramientas en el Escritorio

Gracias a la **Arquitectura V5.0**, tienes 4 iconos independientes en tu escritorio con alta visibilidad:

1.  ⚡ **AstroSetup**: Lanza la configuración completa (ideal para el primer uso).
2.  📶 **Red (WiFi)**: Abre el gestor de redes en cualquier momento con recomendación de IP fija para uso astronómico.
3.  👤 **Usuarios**: Gestiona o añade cuentas de operador.
4.  🔭 **Instalador Software V12.3**: Añade o repara tus programas de astronomía con carrusel visual y terminal de progreso compacto.
5.  🌍 **Idioma**: Cambia el idioma de los asistentes en cualquier momento.

---

## 🐍 Ejecución Standalone (Ubuntu/Debian)

Si no usas la imagen AstroOrange pero quieres usar estas herramientas en tu propia instalación de Linux:

1. **Clona el repositorio**:
   ```bash
   git clone https://github.com/ec7bm/OPI5_Astro.git
   cd OPI5_Astro
   ```

2. **Instala dependencias**:
   ```bash
   sudo apt update
   sudo apt install -y python3-tk python3-pil python3-pil.imagetk
   ```

3. **Instala los scripts y wizards**:
   ```bash
   sudo mkdir -p /opt/astroorange/{scripts,wizard}
   sudo cp -r scripts/* /opt/astroorange/scripts/
   sudo cp -r wizard/* /opt/astroorange/wizard/
   sudo chmod +x /opt/astroorange/scripts/*.sh
   ```

4. **Configura sudoers** (necesario para que los wizards funcionen correctamente):
   ```bash
   sudo cp userpatches/90-astroorange-wizards /etc/sudoers.d/
   sudo chmod 440 /etc/sudoers.d/90-astroorange-wizards
   ```

5. **Ejecuta los Wizards**:
   ```bash
   # Wizard principal (recomendado para primera vez)
   python3 /opt/astroorange/wizard/astro-setup-wizard.py
   
   # O ejecuta wizards individuales:
   python3 /opt/astroorange/wizard/astro-software-gui.py  # Instalador de software
   python3 /opt/astroorange/wizard/astro-network-gui.py   # Gestor de red
   python3 /opt/astroorange/wizard/astro-user-gui.py      # Gestor de usuarios
   ```


---

---

## 🔭 Uso en el Campo

### Escenario: Sesión de Astrofotografía sin WiFi

1. **Lleva tu Orange Pi al campo** (sin cable Ethernet)
2. **Enciende el sistema** - Espera 45 segundos
3. **Busca la red** `AstroOrange-Autostart` en tu móvil/tablet
4. **Conéctate** con la contraseña `astroorange`
5. **Abre el navegador** y accede a `http://10.42.0.1:6080/vnc.html`
6. **Inicia KStars/INDI** y conecta tu telescopio

### Acceso SSH (Avanzado)

Si prefieres usar la terminal:

```bash
ssh tu-usuario@10.42.0.1
```

Contraseña: La que creaste en el Wizard

---

## 🆘 Solución de Problemas

### No veo la red WiFi "AstroOrange-Setup"

**Posibles causas:**
- El sistema aún está arrancando → Espera 1 minuto completo
- Hay un cable Ethernet conectado → Desconéctalo y reinicia
- El WiFi de la Orange Pi está desactivado → Conecta por cable y verifica con `nmcli radio wifi on`

**Solución:**
```bash
# Conecta por cable Ethernet y ejecuta:
sudo systemctl restart astro-network
```

### La web 10.42.0.1:6080 no carga

**Verifica:**
- ✅ Estás conectado a la red `AstroOrange-Setup`
- ✅ Usas `http://` y no `https://`
- ✅ Desactiva los datos móviles si usas un teléfono

**Solución alternativa:**
```bash
# Conecta por cable y verifica el servicio VNC:
sudo systemctl status astro-vnc
```

### El Hotspot no se activa con cable Ethernet

**Comportamiento normal**: El Hotspot solo se activa si **no hay internet**. Si tienes cable Ethernet con internet, el Hotspot no se levantará.

**Para forzar el Hotspot:**
```bash
sudo nmcli con up "AstroOrange-Setup"
```

### Olvidé mi contraseña de usuario

**Solución**: Necesitarás acceso físico a la Orange Pi con teclado y monitor:

1. Arranca el sistema
2. Presiona `Ctrl+Alt+F2` para abrir una terminal
3. Inicia sesión como `root` (sin contraseña en el primer arranque)
4. Cambia la contraseña: `passwd tu-usuario`

---

## 📞 Soporte y Comunidad

- **GitHub**: [https://github.com/ec7bm/OPI5_Astro](https://github.com/ec7bm/OPI5_Astro)
- **Issues**: Reporta problemas en GitHub Issues
- **Documentación**: README.md en el repositorio

---

## 📄 Licencia

AstroOrange V2 es software libre basado en:
- Ubuntu 22.04 Jammy (GPL/Proprietary)
- Imagen oficial Orange Pi (GPL/Proprietary drivers)
- Software astronómico de código abierto

---

**Versión del Manual**: 3.0  
**Última actualización**: Febrero 2026  
**Compatible con**: Orange Pi 5 Pro / Ubuntu Standalone

