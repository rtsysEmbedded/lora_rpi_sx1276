# Installation Instructions for Python 3.9.2

## Step-by-Step Installation

Your Python version (3.9.2) is compatible. Follow these steps:

### 1. Update System Packages

```bash
sudo apt-get update
sudo apt-get upgrade
```

### 2. Install System Dependencies

```bash
sudo apt-get install -y python3-pip python3-dev python3-setuptools git
```

### 3. Enable SPI Interface

```bash
sudo raspi-config
```
- Select: **3 Interface Options**
- Select: **I4 SPI**
- Select: **Yes** to enable
- Select: **Finish**
- Reboot: `sudo reboot`

After reboot, verify SPI is enabled:
```bash
lsmod | grep spi_bcm2835
ls -l /dev/spidev*
```

You should see `/dev/spidev0.0` and `/dev/spidev0.1`

### 4. Install Python Packages

```bash
# Install basic packages
pip3 install RPi.GPIO spidev pycryptodome

# Verify installation
python3 -c "import RPi.GPIO; import spidev; from Crypto.Cipher import AES; print('✓ Packages installed successfully')"
```

### 5. Install pySX127x Library

The SX127x library needs to be installed from GitHub:

```bash
cd /tmp
git clone https://github.com/rpsreal/pySX127x.git
cd pySX127x
sudo python3 setup.py install
cd ~
```

Verify installation:
```bash
python3 -c "from SX127x.LoRa import LoRa; print('✓ SX127x library installed')"
```

### 6. Alternative: Install from Different pySX127x Repository

If the above doesn't work, try this alternative:

```bash
cd /tmp
git clone https://github.com/mayeranalytics/pySX127x.git
cd pySX127x
sudo python3 setup.py install
cd ~
```

### 7. Manual Installation (If Git Install Fails)

If you can't install from git, I'll provide a standalone version that doesn't require the external library.

Would you like me to create a version that works without pySX127x?

## Quick Check: What Do You Have?

Run this to see what's installed:

```bash
pip3 list | grep -E "RPi.GPIO|spidev|pycrypto"
```

## Troubleshooting

### Error: "No module named 'RPi.GPIO'"
```bash
pip3 install RPi.GPIO --upgrade
# or
sudo apt-get install python3-rpi.gpio
```

### Error: "No module named 'spidev'"
```bash
pip3 install spidev --upgrade
```

### Error: "No module named 'Crypto'"
```bash
pip3 install pycryptodome --upgrade
# Note: NOT pycrypto (old/deprecated)
```

### Error: "No module named 'SX127x'"
```bash
# This means pySX127x library is not installed
# Follow step 5 above
```

## What You Should Have After Installation

Run this test:
```bash
python3 << 'EOF'
import sys
print(f"Python version: {sys.version}")

packages = {
    'RPi.GPIO': 'RPi.GPIO',
    'spidev': 'spidev', 
    'pycryptodome': 'Crypto',
    'pySX127x': 'SX127x.LoRa'
}

for name, module in packages.items():
    try:
        __import__(module)
        print(f"✓ {name} - OK")
    except ImportError as e:
        print(f"✗ {name} - MISSING ({e})")
EOF
```

## Next Steps

Once all packages show "OK":
```bash
sudo python3 test_connection.py
```

If you still have issues, tell me:
1. Which packages are missing?
2. What error messages do you see?

I can create a standalone version that doesn't require external libraries!
