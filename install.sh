#!/bin/bash
# Installation script for LoRaWAN Client on Raspberry Pi

set -e

echo "=========================================="
echo "LoRaWAN Client Installation Script"
echo "=========================================="
echo ""

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
    echo "⚠ Warning: This doesn't appear to be a Raspberry Pi"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run with sudo: sudo bash install.sh"
    exit 1
fi

echo "Step 1: Updating system packages..."
apt-get update

echo ""
echo "Step 2: Installing system dependencies..."
apt-get install -y python3-pip python3-dev python3-rpi.gpio git

echo ""
echo "Step 3: Checking SPI status..."
if lsmod | grep -q spi_bcm2835; then
    echo "✓ SPI is enabled"
else
    echo "⚠ SPI is not enabled. Enabling now..."
    if ! grep -q "^dtparam=spi=on" /boot/config.txt; then
        echo "dtparam=spi=on" >> /boot/config.txt
        echo "✓ SPI enabled. Please reboot after installation."
        REBOOT_NEEDED=1
    fi
fi

echo ""
echo "Step 4: Installing Python dependencies..."
pip3 install -r requirements.txt

echo ""
echo "Step 5: Installing pySX127x library..."
cd /tmp
rm -rf /tmp/pySX127x 2>/dev/null
echo "Cloning pySX127x repository..."
if git clone https://github.com/rpsreal/pySX127x.git; then
    cd pySX127x
    echo "Installing pySX127x..."
    python3 setup.py install
    cd /tmp
    rm -rf /tmp/pySX127x
    echo "✓ pySX127x installed"
else
    echo "⚠ Failed to clone from rpsreal, trying alternative..."
    git clone https://github.com/mayeranalytics/pySX127x.git
    cd pySX127x
    python3 setup.py install
    cd /tmp
    rm -rf /tmp/pySX127x
    echo "✓ pySX127x installed from alternative source"
fi

echo ""
echo "Step 6: Setting up permissions..."
chmod +x main.py
chmod +x test_connection.py

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit config.py with your ChirpStack credentials"
echo "2. Connect your SX1276 module (see README.md for wiring)"
echo "3. Run: sudo python3 test_connection.py"
echo "4. Run: sudo python3 main.py"
echo ""

if [ "$REBOOT_NEEDED" == "1" ]; then
    echo "⚠ REBOOT REQUIRED to enable SPI"
    read -p "Reboot now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        reboot
    fi
fi

echo "For detailed instructions, see README.md"
