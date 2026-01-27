# 🍊 Manual de Usuario: AstroOrange V2

Bienvenido a **AstroOrange V2**, tu sistema astronómico listo para usar en Orange Pi 5 Pro. Esta versión incluye un asistente gráfico que facilita la configuración inicial sin necesidad de comandos complejos.

---

## 🚀 1. Primer Arranque (First Boot)

La primera vez que enciendas tu Orange Pi con la tarjeta SD de AstroOrange, el sistema realizará una configuración automática inicial que puede tardar **2-3 minutos**. Durante este tiempo:
1.  Se expandirá el sistema de archivos para usar toda la SD.
2.  Se generarán las claves de seguridad.
3.  Se verificará la conexión a internet.

### 📶 Conexión Automática
Si no tienes el cable Ethernet conectado, el sistema creará automáticamente una red WiFi para que te conectes.

*   **Nombre de Red (SSID):** `AstroOrange`
*   **Contraseña:** `astroorange`

---

## 🧙 2. Asistente de Configuración (Wizard)

Una vez conectado al Hotspot (o si usas cable Ethernet y sabes la IP), abre tu navegador web favorito (Chrome, Firefox, Safari, Edge) en tu PC, Tablet o Móvil.

### 🔗 Acceso al Asistente
Escribe la siguiente dirección en la barra de navegación:

> **http://192.168.4.1:6080/vnc.html**

*(Si estás por cable Ethernet, usa la IP que le haya asignado tu router, ej: http://192.168.1.XX:6080/vnc.html)*

Verás el escritorio de **AstroOrange** y una ventana de bienvenida llamada **"AstroOrange V2 Setup"**.

---

## ⚙️ 3. Pasos de Configuración

El asistente te guiará paso a paso:

### Paso A: Conexión WiFi 📡
Si quieres conectar la Orange Pi a tu red de casa o del observatorio:
1.  Despliega la lista "Configuración WiFi".
2.  Selecciona tu red WiFi.
3.  Escribe la contraseña.
4.  *(Opcional)* Si prefieres seguir usando el Hotspot o Cable, puedes saltar este paso.

### Paso B: Selección de Software 🔭
Elige qué programas quieres instalar. Por defecto vienen los más importantes marcados:
*   **[x] KStars + INDI:** Planetario completo y control de dispositivos (Telescopios, Cámaras, Focuser...). **(Recomendado)**
*   **[x] PHD2:** Sistema de guiado automático.
*   **[ ] Syncthing:** Para sincronizar las fotos automáticamente con tu PC al llegar a casa.

### Paso C: Instalación 💾
1.  Haz clic en el botón **"Instalar y Configurar"**.
2.  Verás una barra de progreso y un registro de las acciones.
3.  **No apagues la Orange Pi** durante este proceso. Puede tardar entre 5 y 15 minutos dependiendo de tu conexión a internet.

---

## ✅ 4. Finalización

Cuando la instalación termine:
1.  El asistente te mostrará un mensaje de "Éxito".
2.  El sistema se reiniciará automáticamente.
3.  Al volver a arrancar, ya tendrás todo el software listo para usar.

### 🔑 Credenciales por Defecto
Para acceder en el futuro (VNC, SSH, o monitor directo):

*   **Usuario:** `AstroOrange`
*   **Contraseña:** `astroorange`

---

## 🆘 Solución de Problemas

**No veo la red WiFi "AstroOrange"**
*   Espera un poco más (hasta 3-4 minutos en el primer arranque).
*   Asegúrate de no tener cable Ethernet conectado si quieres forzar el modo Hotspot.

**La web 192.168.4.1:6080 no carga**
*   Verifica que estás conectado a la WiFi `AstroOrange`.
*   Asegúrate de poner `http://` y no `https://`.
*   Prueba a desactivar los datos móviles de tu teléfono si lo estás haciendo desde allí.

**La instalación falló**
*   Verifica que la contraseña de tu WiFi sea correcta en el Paso A, ya que el sistema necesita internet para descargar los programas.
