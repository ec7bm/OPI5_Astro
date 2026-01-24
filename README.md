# Astro Orange Pi 5 Image Build System

Sistema de construcción automatizado y reproducible para generar una imagen Linux ARM64 (basada en Armbian) optimizada para astrofotografía y control de telescopios en Orange Pi 5 / 5 Pro.

## Objetivos del Proyecto

* **Headless por defecto**: Operación sin necesidad de monitor, teclado o ratón.
* **Red Inteligente**: Conexión automática a Wi-Fi conocida o creación de un Hotspot (RPI) de respaldo.
* **Acceso Remoto**: SSH, VNC y noVNC (navegador) preconfigurados.
* **Stack Astronómico Completo**: INDI Server, KStars/Ekos, PHD2, AstroDMx, ASTAP.
* **Sincronización Automática**: Syncthing para transferencia de capturas.
* **Reproducible**: Basado en Armbian Build Framework con parches de usuario personalizados (`userpatches`).

## Estructura del Repositorio

* `build.sh`: Script principal para iniciar la construcción.
* `userpatches/`: Configuraciones y hooks que Armbian usará durante el build.
* `scripts/`: Scripts que se incluirán en la imagen final (redes, primer arranque).
* `configs/`: Plantillas de configuración para servicios (Systemd, VNC, Syncthing).

## Requisitos de Construcción

* Máquina con Ubuntu 22.04 o superior (VM recomendada).
* Acceso a Internet para descargar dependencias y paquetes.
* Espacio en disco (~20GB mínimo).

## Cómo empezar (Próximamente)

1. Clonar este repositorio.
2. Ejecutar `./build.sh`.
3. Flashear la imagen resultante en `/output/images/`.
