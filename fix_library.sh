#!/bin/bash
# Fix library conflict: Remove pyLoRa and install pySX127x

echo "============================================================"
echo "Fixing LoRa Library Installation"
echo "============================================================"
echo ""

echo "Step 1: Removing old pyLoRa package..."
sudo pip3 uninstall -y pyLoRa
sudo pip3 uninstall -y pySX127x

echo ""
echo "Step 2: Cleaning up old installations..."
sudo rm -rf /usr/local/lib/python3.9/dist-packages/pyLoRa*
sudo rm -rf /usr/local/lib/python3.9/dist-packages/SX127x*
sudo rm -rf /usr/local/lib/python3.9/dist-packages/pySX127x*

echo ""
echo "Step 3: Installing pySX127x from GitHub..."
cd /tmp
rm -rf pySX127x
git clone https://github.com/rpsreal/pySX127x.git
cd pySX127x
sudo python3 setup.py install

echo ""
echo "Step 4: Verifying installation..."
python3 -c "from SX127x.LoRa import LoRa; from SX127x.board_config import BOARD; print('✓ pySX127x installed correctly')"

if [ $? -eq 0 ]; then
    echo ""
    echo "============================================================"
    echo "✓ Library fixed successfully!"
    echo "============================================================"
    echo ""
    echo "Now you can run:"
    echo "  sudo python3 test_connection.py"
    echo "  sudo python3 main.py"
else
    echo ""
    echo "✗ Installation failed. Trying alternative repository..."
    cd /tmp
    rm -rf pySX127x
    git clone https://github.com/mayeranalytics/pySX127x.git
    cd pySX127x
    sudo python3 setup.py install
    
    python3 -c "from SX127x.LoRa import LoRa; from SX127x.board_config import BOARD; print('✓ pySX127x installed from alternative source')"
fi

cd ~
rm -rf /tmp/pySX127x
