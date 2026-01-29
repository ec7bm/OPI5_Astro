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
- 📶 **Nombre (SSID):** `AstroOrange-Setup`
- 🔐 **Contraseña:** `astrosetup`
- 🌐 **Acceso VNC:** `http://10.42.0.1:6080/vnc.html`

---

Al acceder por primera vez, verás el **AstroOrange Wizard** rediseñado como un asistente paso a paso.

#### Paso 0: Bienvenida
Instrucciones básicas. Se recomienda que la placa esté conectada por cable para que el escaneo de redes WiFi sea fiable.

#### Paso 1: Tu Cuenta
1. **Nombre de Usuario**: Elige tu nombre (ej: `astro`).
2. **Contraseña**: Define tu clave de acceso.
*Estas serán tus credenciales definitivas.*

#### Paso 2: Red WiFi
1. El Wizard escaneará las redes disponibles. Selecciona la tuya de la lista.
2. **Configuración Manual**: Si tu red es oculta o no aparece, haz clic en el botón amarillo **"CONFIGURACIÓN MANUAL"** para escribir el nombre (SSID) tú mismo.

#### Paso 3: Configuración de Red
1. Introduce la **contraseña de tu WiFi**.
2. **IP Estática (Opcional)**: Si marcas esta casilla, podrás fijar la IP, Puerta de enlace y DNS (ideal para observatorios fijos).

#### Paso 4: Finalizar
El sistema aplicará los cambios y se reiniciará automáticamente. Tras el reinicio, la placa se conectará a tu WiFi real y entrará con tu nuevo usuario.

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

1. **Selecciona** los programas que quieres instalar.
   - Si un programa ya está instalado, aparecerá la etiqueta **(INSTALADO)**.
   - Si seleccionas un programa ya instalado, el Wizard te preguntará si deseas **REINSTALAR / REPARAR**.
2. Haz clic en **"SIGUIENTE"** para pasar a la pantalla de ejecución.
3. Haz clic en **"🚀 Iniciar Instalación"**.
4. **Progreso en vivo**: Se abrirá una consola integrada mostrando el progreso de `apt-get`.
5. **Abortar**: Si necesitas detener el proceso, puedes usar el botón rojo **"ABORTAR INSTALACION"**.
6. Cuando termine, el botón cambiará a **"LISTO - SALIR"**.

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
- Ubuntu 22.04 Jammy (GPL/Proprietary)
- Imagen oficial Orange Pi (GPL/Proprietary drivers)
- Software astronómico de código abierto

---

**Versión del Manual**: 2.0  
**Última actualización**: Enero 2026  
**Compatible con**: Orange Pi 5 Pro
