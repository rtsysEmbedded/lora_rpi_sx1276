# 🚀 START HERE - For Python 3.9.2 Users

You have Python 3.9.2, which is perfect for this project!

## ⚡ Quick Start (3 commands)

### 1. Check What You Have

```bash
python3 check_dependencies.py
```

This shows what packages are installed and what's missing.

### 2. Install Missing Packages

```bash
sudo bash install.sh
```

This automatically installs everything.

### 3. Verify Installation

```bash
python3 check_dependencies.py
```

All packages should show ✓ now.

---

## 📦 What Packages Are Needed?

- **RPi.GPIO** - GPIO control
- **spidev** - SPI communication  
- **pycryptodome** - Encryption for LoRaWAN
- **pySX127x** - LoRa radio driver (installed from GitHub)

## ❓ If Automatic Install Doesn't Work

See these guides:

1. **INSTALL_INSTRUCTIONS.md** - Detailed installation guide
2. **MANUAL_INSTALL.md** - Step-by-step manual installation
3. **README.md** - Complete project documentation

## 🔧 Manual Installation (If You Prefer)

```bash
# Step 1: Install from pip
pip3 install RPi.GPIO spidev pycryptodome

# Step 2: Install pySX127x from GitHub
cd /tmp
git clone https://github.com/rpsreal/pySX127x.git
cd pySX127x
sudo python3 setup.py install
cd ~

# Step 3: Verify
python3 check_dependencies.py
```

## ✅ After Installation

Once `check_dependencies.py` shows all ✓:

### 1. Configure Your Device

Edit `config.py`:
```python
DEVICE_EUI = "0bbef9f59cc6986a"  # Already set
APP_KEY = "d8341a42c8894b3bb82d0f721a0fcdbc"  # Already set
APP_EUI = "GET_THIS_FROM_CHIRPSTACK"  # Update this
FREQUENCY = 868.1  # or 915.0 for US
```

### 2. Setup ChirpStack

Follow `chirpstack_setup_guide.md` to register your device.

### 3. Test Hardware

```bash
sudo python3 test_connection.py
```

Should show: `✓ SX1276 detected!`

### 4. Run Application

```bash
sudo python3 main.py
```

Should connect to ChirpStack and send data!

## 🆘 Common Issues

### "No module named 'SX127x'"

The pySX127x package didn't install. Try:

```bash
cd /tmp
git clone https://github.com/mayeranalytics/pySX127x.git
cd pySX127x
sudo python3 setup.py install
```

### "No module named 'Crypto'"

Wrong crypto package. Install pycryptodome (not pycrypto):

```bash
pip3 uninstall pycrypto  # Remove old one
pip3 install pycryptodome  # Install new one
```

### "Permission denied" or "GPIO errors"

Always run with `sudo`:

```bash
sudo python3 test_connection.py
sudo python3 main.py
```

### "SPI not found"

Enable SPI:
```bash
sudo raspi-config
# Interface Options → SPI → Enable
sudo reboot
```

## 📖 Documentation Overview

- **START_HERE.md** ← You are here
- **QUICKSTART.md** - 5-minute quick guide
- **INSTALL_INSTRUCTIONS.md** - Detailed installation
- **MANUAL_INSTALL.md** - Step-by-step manual install
- **README.md** - Complete documentation
- **chirpstack_setup_guide.md** - ChirpStack setup
- **PROJECT_STRUCTURE.md** - File explanations

## 🎯 Your Next Step

Run this now:

```bash
python3 check_dependencies.py
```

Then follow the instructions it gives you!

---

**Questions? See MANUAL_INSTALL.md or README.md for help!**
