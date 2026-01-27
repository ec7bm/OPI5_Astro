# 🍊 Manual de Usuario - AstroOrange V2

## 🔑 Credenciales por Defecto

### 1. Sistema (SSH / Terminal Login)
*   **Usuario:** `orangepi`
*   **Contraseña:** `orangepi`  (o a veces `orange` en algunas distros antiguas)

### 2. Acceso Remoto (VNC / noVNC)
Al arrancar por primera vez, si no hay cable de red, se crea un punto WiFi.

*   **WiFi Hotspot SSID:** `AstroOrange`
*   **WiFi Password:** `astroorange`
*   **URL Web:** `http://192.168.4.1:6080/vnc.html` (o la IP que tenga si usas cable)
*   **VNC Password:** `astroorange`

---

## 🚀 Primeros Passos

1.  **Flashear la imagen** `astroorange-v2-work.img` en tu tarjeta SD/NVMe.
2.  **Encender** la Orange Pi 5 Pro.
3.  **Esperar unos 2-3 minutos** para el primer arranque y configuración automática.
4.  **Conectar**:
    *   Si usas cable Ethernet: Busca la IP en tu router.
    *   Si no: Busca la red WiFi `AstroOrange` y conéctate (clave: `astroorange`).
5.  **Abrir Navegador**: Ve a `http://<IP>:6080/vnc.html`.
6.  **Login VNC**: Usa la clave `astroorange`.
7.  **Asistente**: Verás el "AstroOrange Setup Wizard" en pantalla.
    *   Sigue los pasos para **Crear tu Usuario Personal** (ej. `ec7bm`).
    *   Configura tu WiFi real.
    *   Elige el software a instalar (KStars, etc.).

¡Listo! Una vez termine el asistente, el sistema se reiniciará y podrás entrar con tu nuevo usuario.
