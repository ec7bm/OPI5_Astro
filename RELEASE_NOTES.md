# AstroOrange V13.1 MASTER - Release Notes

## 🚀 Highlights
This build (V13.1 MASTER "Armor") provides critical fixes for ethernet activation and system user persistence.

- **Ethernet Fix**: 
    - **Netplan Armor**: Forced NetworkManager as the renderer to ensure automatic ethernet activation on Ubuntu 22.04.
    - **Aggressive Watchdog**: Increased retries for hardware detection at boot.
- **User Persistence**:
    - **Hardened Wizard**: `UserWizard` now performs atomic command verification for `useradd`.
    - **Nuclear Sync**: Multi-stage `sync` calls to guarantee disk write completion on SD cards.




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
