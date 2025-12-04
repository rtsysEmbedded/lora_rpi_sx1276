# Manual Installation Guide

If the automatic installer doesn't work, follow these steps manually.

## Prerequisites Check

First, check what you already have:

```bash
python3 check_dependencies.py
```

This will show you exactly what's missing.

## Step 1: Install RPi.GPIO

```bash
pip3 install RPi.GPIO
```

**Alternative if pip fails:**
```bash
sudo apt-get install python3-rpi.gpio
```

**Test it:**
```bash
python3 -c "import RPi.GPIO; print('✓ RPi.GPIO OK')"
```

## Step 2: Install spidev

```bash
pip3 install spidev
```

**Test it:**
```bash
python3 -c "import spidev; print('✓ spidev OK')"
```

## Step 3: Install pycryptodome

```bash
pip3 install pycryptodome
```

**Important:** Make sure it's `pycryptodome`, NOT `pycrypto` (old/insecure)

**Test it:**
```bash
python3 -c "from Crypto.Cipher import AES; print('✓ pycryptodome OK')"
```

## Step 4: Install pySX127x (The Tricky One)

This library is not on PyPI, so we install from GitHub:

### Method 1: From rpsreal repository

```bash
cd /tmp
git clone https://github.com/rpsreal/pySX127x.git
cd pySX127x
sudo python3 setup.py install
cd ~
rm -rf /tmp/pySX127x
```

**Test it:**
```bash
python3 -c "from SX127x.LoRa import LoRa; print('✓ pySX127x OK')"
```

### Method 2: From mayeranalytics repository (if above fails)

```bash
cd /tmp
git clone https://github.com/mayeranalytics/pySX127x.git
cd pySX127x
sudo python3 setup.py install
cd ~
rm -rf /tmp/pySX127x
```

### Method 3: If both fail, check what went wrong

Common issues:
- **No git installed**: `sudo apt-get install git`
- **No build tools**: `sudo apt-get install python3-dev build-essential`
- **Permission denied**: Use `sudo` for setup.py install

## Step 5: Verify Everything

Run the dependency checker:

```bash
python3 check_dependencies.py
```

You should see all checkmarks (✓).

## Step 6: Enable SPI

```bash
sudo raspi-config
```

- Navigate to: **Interface Options** → **SPI** → **Enable**
- Reboot

After reboot, check:
```bash
lsmod | grep spi_bcm2835
ls -l /dev/spidev*
```

## Complete Installation Test

Once everything is installed:

```bash
sudo python3 test_connection.py
```

This will test your hardware connection.

## Troubleshooting Individual Packages

### If RPi.GPIO fails:
```bash
# Try system package
sudo apt-get install python3-rpi.gpio

# Or upgrade pip and try again
pip3 install --upgrade pip
pip3 install RPi.GPIO --user
```

### If spidev fails:
```bash
# Install system dependencies first
sudo apt-get install python3-dev

# Then try again
pip3 install spidev
```

### If pycryptodome fails:
```bash
# Install build dependencies
sudo apt-get install build-essential libgmp3-dev

# Try again
pip3 install pycryptodome
```

### If pySX127x fails:

**Check if git is installed:**
```bash
git --version
# If not: sudo apt-get install git
```

**Check if you can clone:**
```bash
cd /tmp
git clone https://github.com/rpsreal/pySX127x.git
# If this works, continue with setup.py install
```

**If GitHub is blocked, I can provide the library files directly**

## What Each Package Does

- **RPi.GPIO**: Controls GPIO pins on Raspberry Pi (for RESET, DIO0, etc.)
- **spidev**: Enables SPI communication (for data transfer to SX1276)
- **pycryptodome**: Provides AES encryption (for LoRaWAN security)
- **pySX127x**: Driver for SX127x LoRa chips (controls the radio)

## Still Having Issues?

Run this diagnostic:

```bash
python3 << 'EOF'
import sys
import subprocess

print(f"Python: {sys.version}")
print(f"Pip location: {subprocess.getoutput('which pip3')}")
print(f"\nInstalled packages:")
print(subprocess.getoutput('pip3 list'))
EOF
```

Send me the output and I can help further!

## Quick Command Summary

```bash
# All in one (if you have all dependencies)
pip3 install RPi.GPIO spidev pycryptodome && \
cd /tmp && \
git clone https://github.com/rpsreal/pySX127x.git && \
cd pySX127x && \
sudo python3 setup.py install && \
cd ~ && \
rm -rf /tmp/pySX127x && \
python3 check_dependencies.py
```

## Next Steps

Once `check_dependencies.py` shows all ✓:

1. Edit `config.py` with your ChirpStack credentials
2. Connect your SX1276 hardware
3. Run: `sudo python3 test_connection.py`
4. Run: `sudo python3 main.py`

See `README.md` for complete usage instructions.
