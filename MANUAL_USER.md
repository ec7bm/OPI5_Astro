# 🍊 AstroOrange V2 - User Manual

**Specialized OS for Astrophotography on Orange Pi 5 Pro**

---

## 📖 Table of Contents

1. [Introduction](#introduction)
2. [First Boot](#first-boot)
3. [Connecting to the System](#connecting-to-the-system)
4. [Initial Setup](#initial-setup)
5. [Software Installation](#software-installation)
6. [Field Usage](#field-usage)
7. [Troubleshooting](#troubleshooting)

---

## 1. Introduction

AstroOrange V2 is an operating system based on **Ubuntu 22.04 Jammy Server**, specifically designed for astrophotography. It includes:

- ✅ **Automatic Rescue Hotspot** - Always accessible without WiFi.
- ✅ **VNC Remote Desktop (noVNC)** - Control from any browser.
- ✅ **Configuration Wizard V13.0 (MASTER)** - Guided multi-language setup.

  - **Step 1**: User creation with password validation.
  - **Step 2**: WiFi manager with auto-scan and Static IP recommendation.
  - **Step 3**: Astronomy software installer with visual carousel.
- ✅ **Modular Astronomy Software** - KStars/INDI, PHD2, ASTAP, Stellarium, CCDciel, Syncthing.
- ✅ **Modern Interface** - Arc-Dark theme with Papirus icons.

---

## 2. First Boot

### Requirements
- Orange Pi 5 Pro
- microSD card (16GB or larger)
- 5V/4A Power Supply
- **Ethernet Cable connected to router** (Highly recommended for first boot)

### Boot Process

1. **Insert microSD** into Orange Pi 5 Pro.
2. **Connect Power** - System starts automatically.
3. **Wait 30-45 seconds** - System initialization.

> ⏱️ **Note**: First boot may take up to 1 minute while the system configures itself.

---

## 3. Connecting to the System

### Option A (Recommended): Wired Ethernet

1. Connect Orange Pi to router via Ethernet *before* powering on.
2. System obtains an IP automatically.
3. From PC/Tablet, go to: **`http://<board-ip>:6080/vnc.html`**
4. VNC Password: **`astroorange`**

### Option B: Wireless (Rescue Hotspot)

If no cable is available, the system activates its own Hotspot:
- 📶 **Name (SSID):** `AstroOrange-Autostart`
- 🔐 **Password:** `astroorange`
- 🌐 **VNC Access:** `http://10.42.0.1:6080/vnc.html`

---

## 4. Initial Setup

On first access, you will see **AstroSetup** on the desktop. It guides you through three modular tools. The system will detect if it is the first run and prompt you to select **English** or **Español**.


### 👤 1. AstroUser (User Management)
- Create your main username and password.
- Automatically configures admin permissions.

### 📡 2. AstroNetwork (Network Management)
- One-click WiFi scanning.
- **"Manual / Hidden" Button**: Connect to hidden networks or set Static IP.
- **Field Mode**: Skip if no WiFi is available.

### 🔭 3. AstroSoftware (App Installer)
Install tools anytime. Includes desktop shortcut creation:

| Software | Description |
|----------|-------------|
| **KStars + INDI** | Planetarium & Hardware Control |
| **PHD2 Guiding** | Professional Autoguiding |
| **ASTAP** | Fast Plate Solving |
| **Stellarium** | Visual Star Atlas |
| **AstroDMX** | Planetary/Deep Sky Capture |
| **CCDciel** | Advanced Capture |
| **Syncthing** | Auto-backup of photos |

---

## 5. Desktop Tools

Thanks to **V5.0 Architecture**, you have 4 independent desktop icons:

1.  ⚡ **AstroSetup**: Launches full setup (ideal for first run).
2.  📶 **Network (WiFi)**: Open network manager anytime.
3.  👤 **Users**: Manage or add operator accounts.
4.  🔭 **Software Installer V12.3**: Add/Repair astronomy apps.
5.  🌍 **Language**: Change the language of the wizards at any time.

---

## 🐍 Standalone Execution (Ubuntu/Debian)

If you are not using the AstroOrange image but want to use these tools on your own Linux installation:

1. **Install dependencies**:
   ```bash
   sudo apt update && sudo apt install -y python3-tk python3-pil.imagetk
   ```

2. **Run the Wizards**:
   ```bash
   cd /opt/astroorange/wizard  # Or where you cloned the repo
   python3 astro-setup-wizard.py
   ```


---

## 6. Field Usage

### Scenario: Astrophotography Session without WiFi

1. **Bring Orange Pi to the field** (no Ethernet).
2. **Power on** - Wait 45 seconds.
3. **Connect to WiFi** `AstroOrange-Autostart` on your phone/tablet.
4. **Password**: `astroorange`
5. **Open Browser**: `http://10.42.0.1:6080/vnc.html`
6. **Start KStars/INDI** and connect telescope.

### SSH Access (Advanced)

```bash
ssh your-user@10.42.0.1
```
Password: The one you created in the Wizard.

---

## 7. Troubleshooting

### Can't see "AstroOrange-Setup" WiFi

**Causes:**
- System still booting → Wait 1 full minute.
- Ethernet cable connected → Disconnect and reboot.
- WiFi radio off → Connect via cable and check `nmcli radio wifi on`.

**Solution:**
```bash
# Connect via Ethernet and run:
sudo systemctl restart astro-network
```

### Web 10.42.0.1:6080 won't load

**Check:**
- ✅ Connected to `AstroOrange-Setup` network?
- ✅ Using `http://` (not https)?
- ✅ Turn off mobile data (4G/5G) on phone.

### Hotspot won't active with Ethernet

**Normal Behavior**: Hotspot only activates if **no internet** is detected.

**Force Hotspot:**
```bash
sudo nmcli con up "AstroOrange-Setup"
```

---

## 📞 Support

- **GitHub**: [https://github.com/ec7bm/OPI5_Astro](https://github.com/ec7bm/OPI5_Astro)
- **Issues**: Report bugs on GitHub Issues

---

**Manual Version**: 3.0 (EN)
**Last Updated**: Feb 2026
**Compatible with**: Orange Pi 5 Pro / Ubuntu Standalone

