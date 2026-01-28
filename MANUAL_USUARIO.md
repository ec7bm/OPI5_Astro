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

## 🌟 Introducción

AstroOrange V2 es un sistema operativo basado en Debian diseñado específicamente para astrofotografía. Incluye:

- ✅ **Hotspot de rescate automático** - Siempre accesible sin WiFi
- ✅ **Escritorio remoto VNC** - Control desde cualquier dispositivo
- ✅ **Wizard de instalación** - Configuración guiada en español
- ✅ **Software astronómico modular** - Instala solo lo que necesites
- ✅ **Interfaz moderna** - Tema Arc-Dark con iconos Papirus

---

## 🚀 Primer Arranque

### Requisitos
- Orange Pi 5 Pro
- Tarjeta microSD de 16GB o superior
- Fuente de alimentación 5V/4A
- (Opcional) Cable Ethernet para internet

### Proceso de Arranque

1. **Inserta la tarjeta SD** en la Orange Pi 5 Pro
2. **Conecta la alimentación** - El sistema arrancará automáticamente
3. **Espera 30-45 segundos** - El sistema se está inicializando

> ⏱️ **Nota**: El primer arranque puede tardar hasta 1 minuto mientras el sistema se configura.

---

## 📡 Conexión al Sistema

### Opción A: Sin Cable Ethernet (Hotspot Automático)

Si no conectas un cable Ethernet, el sistema creará automáticamente una red WiFi:

**Red WiFi:**
- 📶 **Nombre (SSID):** `AstroOrange-Setup`
- 🔐 **Contraseña:** `astrosetup`

**Pasos:**
1. Busca la red `AstroOrange-Setup` en tu móvil/tablet/PC
2. Conéctate usando la contraseña `astrosetup`
3. Abre tu navegador web
4. Accede a: **`http://10.42.0.1:6080/vnc.html`**
5. Contraseña del VNC: **`astroorange`**

### Opción B: Con Cable Ethernet

Si conectas un cable Ethernet:

1. El sistema obtendrá una IP de tu router automáticamente
2. Consulta la IP en tu router (busca "orangepi5pro")
3. Accede a: **`http://IP-DE-TU-ORANGEPI:6080/vnc.html`**
4. Contraseña del VNC: **`astroorange`**

---

## ⚙️ Configuración Inicial

Al acceder por primera vez verás el **AstroOrange Wizard**.

### Etapa 1: Usuario y WiFi

#### Crear Usuario
1. **Usuario**: Elige tu nombre de usuario (ej: `astro`, `ec7bm`)
2. **Contraseña**: Elige una contraseña segura

> 💡 **Importante**: Anota estas credenciales, las necesitarás para futuros accesos.

#### Configurar WiFi (Opcional)
Si quieres conectar la Orange Pi a tu red WiFi de casa/observatorio:

1. Haz clic en **"Configurar WiFi (nmtui)"**
2. Se abrirá una terminal con el gestor de redes
3. Selecciona **"Activate a connection"**
4. Elige tu red WiFi
5. Introduce la contraseña
6. Presiona `Esc` para salir

> 📶 Si no configuras WiFi, el Hotspot seguirá disponible siempre que no haya internet.

#### Finalizar Etapa 1
1. Haz clic en **"GUARDAR Y REINICIAR"**
2. El sistema se reiniciará (espera 30 segundos)
3. Vuelve a conectarte al VNC con las mismas credenciales

---

## 📦 Instalación de Software

Tras el reinicio verás la **Etapa 2: Instalador de Software**.

### Software Disponible

Selecciona los programas que necesites:

| Software | Descripción | Recomendado |
|----------|-------------|-------------|
| **KStars + INDI** | Planetario y control de telescopios/cámaras | ✅ Sí |
| **PHD2 Guiding** | Sistema de guiado automático | ✅ Sí |
| **ASTAP** | Resolución de placas (Plate Solving) | ✅ Sí |
| **Stellarium** | Planetario visual realista | ⭐ Opcional |
| **AstroDMX** | Captura profesional de imágenes | ⭐ Opcional |
| **CCDciel** | Control avanzado de cámaras CCD | ⭐ Opcional |
| **Syncthing** | Sincronización automática de fotos con tu PC | ⭐ Opcional |

### Proceso de Instalación

1. **Marca** los programas que quieres instalar
2. Haz clic en **"🚀 Iniciar Instalación"**
3. Confirma la instalación
4. **Espera 10-20 minutos** - Se abrirá una terminal mostrando el progreso
5. Cuando termine, presiona `Enter` para cerrar la terminal
6. El Wizard se cerrará automáticamente

> ⏱️ **Tiempo estimado**: 10-15 minutos dependiendo de tu conexión a internet.

---

## 🔭 Uso en el Campo

### Escenario: Sesión de Astrofotografía sin WiFi

1. **Lleva tu Orange Pi al campo** (sin cable Ethernet)
2. **Enciende el sistema** - Espera 45 segundos
3. **Busca la red** `AstroOrange-Setup` en tu móvil/tablet
4. **Conéctate** con la contraseña `astrosetup`
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
- Armbian (GPL)
- Debian (GPL)
- Software astronómico de código abierto

---

**Versión del Manual**: 2.0  
**Última actualización**: Enero 2026  
**Compatible con**: Orange Pi 5 Pro
