# AstroOrange V13.0 MASTER - Release Notes

## 🚀 Highlights
This build (V13.0 MASTER "Global") introduces full internationalization and multi-language support.

- **Multi-language Support (i18n)**:
    - **V13.0 Engine**: Centralized translation module `i18n.py`.
    - **Language Selector**: New tool to toggle between **English** and **Spanish** at any time.
    - **Universal Wizards**: All 4 wizards (Setup, User, Network, Software) are now 100% bilingual.
- **Software Installer V12.3**:
    - **Refreshed Detection**: Improved logic to detect installed packages and shortcuts.
    - **Restart Mechanism**: New "Restart Wizard" button to see changes immediately.



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
