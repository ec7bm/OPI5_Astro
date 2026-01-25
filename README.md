# 🌌 Astro OPI 5 Pro - Ubuntu Jammy Remaster Edition

Este proyecto personaliza la **imagen oficial de Ubuntu Jammy Server de Orange Pi 5 Pro** añadiendo un stack completo de software astronómico y un asistente de instalación gráfico.

## 🚀 Guía de Construcción (Remaster)

### Requisitos Previos
- VM Ubuntu 22.04 con al menos 50GB libres
- Imagen oficial de Ubuntu Jammy Server para Orange Pi 5 Pro

### Pasos de Construcción

1. **Descargar imagen oficial de Orange Pi**
   - Ve a: https://drive.google.com/drive/folders/11tj_ivEBwvJx4vdNtK91YQeGOKDC4JNy
   - Descarga la imagen de **Ubuntu Jammy Server**
   - Colócala en `~/astro/OPI5_Astro/remaster-work/`

2. **Ejecutar el remaster**
   ```bash
   cd ~/astro/OPI5_Astro
   chmod +x remaster-orangepi.sh
   sudo ./remaster-orangepi.sh
   ```

3. **Resultado**
   - La imagen personalizada estará en: `output/Astro-OPI5-Pro-Ubuntu-Jammy-YYYYMMDD.img.xz`

### Limpiar Espacio

Para limpiar archivos temporales después del build:
```bash
sudo rm -rf ~/astro/OPI5_Astro/remaster-work
sudo rm -rf ~/astro/OPI5_Astro/output
```

## 📦 Contenido de la Imagen

La imagen incluye:
- **Sistema Base**: Ubuntu 22.04 LTS (Jammy) oficial de Orange Pi
- **Escritorio Remoto**: noVNC accesible desde navegador (puerto 6080)
- **Hotspot Wi-Fi**: Red `OPI5_Astro` (password: `password`)
- **Astro Setup Wizard**: Instalador gráfico de software astronómico
- **Software disponible**: INDI, KStars, PHD2, ASTAP, SkyChart, AstroDMx

## 🛠️ Credenciales

- **Usuario**: `orangepi` (o el que venga por defecto en la imagen oficial)
- **Password**: El que configure Orange Pi en su imagen
- **IP del Hotspot**: `10.0.0.1`
- **Puerto noVNC**: `6080`

## 🔧 Desarrollo

Este proyecto usa la imagen oficial de Orange Pi como base porque:
- ✅ Bootloader optimizado para la placa
- ✅ Drivers específicos del hardware
- ✅ Compatibilidad garantizada con Orange Pi 5 Pro

Los scripts de personalización están en `userpatches/`:
- `customize-image.sh`: Script principal de personalización
- `overlay/`: Archivos que se copian a la imagen
- `overlay/usr/local/bin/astro-wizard.sh`: Asistente de instalación

## 📝 Notas

- La imagen oficial de Orange Pi usa un bootloader específico que Armbian no replica correctamente
- Por eso usamos la imagen oficial como base en lugar de construir desde cero con Armbian
