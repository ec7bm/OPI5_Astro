# Reorganización de Arquitectura - README

## 📁 Nueva Estructura

El proyecto ha sido reorganizado para mejorar la mantenibilidad y claridad:

```
OPI5_Astro_Build/
├── build.sh                    # Script principal (mejorado con HTTP server)
├── image-base/                 # Imágenes base de Armbian
├── scripts/                    # Scripts del sistema
│   ├── astro-network.sh       # Hotspot de rescate
│   └── astro-vnc.sh           # VNC headless
├── systemd/                    # Servicios systemd
│   ├── astro-network.service
│   └── astro-vnc.service
├── wizard/                     # Wizard Python (futuro)
├── userpatches/               # Customización
│   ├── customize-image.sh
│   └── astro-wallpaper.jpg
└── output/                    # Imágenes finales
```

## 🚀 Uso del Nuevo Build

```bash
# En la VM Ubuntu
cd ~/astro/OPI5_Astro_Build
git pull origin v2-architecture
sudo ./build.sh
```

Al terminar, el script levantará automáticamente un servidor HTTP para descargar la imagen.

## ✨ Mejoras del Nuevo Build

1. **Modular**: Scripts separados en archivos independientes
2. **Seguro**: Usa `mount --bind` en lugar de copiar sys/proc/dev
3. **Conveniente**: Servidor HTTP automático al finalizar
4. **Claro**: Mensajes con colores y progreso visual
5. **Profesional**: Nombres con timestamp y SHA256 automático
