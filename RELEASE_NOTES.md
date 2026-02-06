# AstroOrange V12.0 Release Notes

## 🚀 Highlights
This build (V12.0 MASTER) brings critical stabilization to the software installer and centralized UI management.

- **Software Wizard V12.0**:
    - **Thread-Safety**: Atomic UI updates using `root.after` to prevent random crashes.
    - **Persistence**: Real-time logging to `/var/log/astro_wiz.log` that survives system reboots.
    - **Safety**: Removed `dist-upgrade` to protect kernel/module integrity on SBCs.
    - **Hardened Apt**: Aggressive lock cleaning and dependency resolution (libgcc/gcc-11 force).
- **UI Centering**: All wizard windows (Network, User, Software) are now perfectly centered for better user experience.


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
