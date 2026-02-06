# AstroOrange V13.2 MASTER - Release Notes

## 🚀 Highlights
This build (V13.2 MASTER "Universal") introduces a heavy-duty standalone installer for any Ubuntu-based system.

- **Universal Installer (`install.sh`)**:
    - **One-Command Setup**: Now installs Wizards + Remote Desktop (noVNC) on any PC, Raspberry Pi, or MiniPC running Ubuntu/Armbian.
    - **Remote Desktop Engine**: Automatically configures `x11vnc` and `noVNC` with systemd services.
    - **Portable Wizards**: Full localization and modular icons for a professional "Distro" feel on stock OS.
- **Ethernet Fix (V13.1 Recap)**: 
    - Forced Netplan NetworkManager renderer for reliable boot-time activation.
- **User Persistence**:
    - Hardened `UserWizard` with atomic verification for SD card reliability.





- **Network Watchdog V9.2.1**: Rock-solid WiFi connection logic, dynamic interface detection, and intelligent Hotspot fallback.
- **Wizards V8.4/V5.2**:
    - **AstroNetwork**: New "Manual Connect" mode for hidden networks and editable SSID fields.
    - **AstroUser**: Improved button layout for all screen resolutions.
- **Universal Wallpaper V10.0**: Intelligent detection of wallpapers with any extension (or no extension).
- **Desktop Shortcuts**: Automatic shortcut creation for all installed astronomy software.

## 📦 Changes
- [NEW] `install.sh` script for installing AstroOrange tools on existing systems.
- [FIX] `customize-image.sh` detects `.jpg`, `.png`, and extension-less wallpapers.
- [FIX] `astro-software-gui.py` creates icons for the actual active user (not root).
- [CLEAN] Removed legacy scripts (`build-old.sh`) and unused configurations (`conky`).

## 💿 Installation
See `README.md` for dual installation methods:
1. **Direct Image**: Flash `AstroOrange_V10.5.img`.
2. **Script**: Run `curl -sL [URL] | sudo bash`.
