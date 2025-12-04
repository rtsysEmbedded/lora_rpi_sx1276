# Installing LoRa Library for SX1276

The Python scripts require a LoRa library to communicate with the SX1276 module. Here are several options:

## Option 1: pyLoRa (Recommended for SX1276)

```bash
# Clone the repository
git clone https://github.com/lemariva/pyLoRa.git
cd pyLoRa

# Install
sudo python3 setup.py install

# Or install via pip if available
pip3 install pyLoRa
```

## Option 2: LoRa Library (Alternative)

```bash
pip3 install LoRa
```

**Note**: You may need to modify the import statement in the scripts:
```python
from LoRa import SX127x  # Instead of 'from lora import SX127x'
```

## Option 3: Direct Register Manipulation

If libraries don't work, you can use direct SPI register access (see `test_lora_basic.py` for an example). This requires implementing the full SX1276 register map yourself.

## Option 4: Use CircuitPython/Adafruit Library

If you're using CircuitPython:
```bash
pip3 install adafruit-circuitpython-rfm9x
```

## Verifying Installation

After installing, test with:
```bash
python3 -c "from lora import SX127x; print('Library OK')"
```

Or for LoRa library:
```bash
python3 -c "from LoRa import SX127x; print('Library OK')"
```

## Troubleshooting

If you get import errors:
1. Make sure you're using Python 3: `python3` not `python`
2. Try installing with `sudo pip3 install`
3. Check if the library name is correct (case-sensitive)
4. Consider using the basic test script (`test_lora_basic.py`) which uses direct SPI

## Alternative: Modify Scripts for Your Library

If you have a different LoRa library, you'll need to adapt the scripts. The key functions needed are:
- Initialize module with parameters
- Set to TX mode
- Set to RX mode  
- Send data
- Receive data
- Read RSSI/SNR
