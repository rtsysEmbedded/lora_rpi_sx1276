# Quick Start Guide - Testing Helium LoRa Modem

## Step 1: Hardware Connection

Connect your Helium LoRa modem to Raspberry Pi 3:

```
Helium Modem    →    RPi3 GPIO
───────────────────────────────
VCC (3.3V)      →    3.3V (Pin 1)
GND             →    GND (Pin 6)
MOSI            →    GPIO 10 (Pin 19)
MISO            →    GPIO 9 (Pin 21)
SCK             →    GPIO 11 (Pin 23)
NSS/CS          →    GPIO 8 (Pin 24)
RST             →    GPIO 25 (Pin 22)
```

**Note**: Pin numbers may vary depending on your Helium modem model. Check `HELIUM_MODEM_SETUP.md` for specific models.

## Step 2: Enable SPI

```bash
sudo raspi-config
# Navigate to: Interface Options → SPI → Enable
sudo reboot
```

Verify SPI is enabled:
```bash
lsmod | grep spi
# Should show: spi_bcm2835
```

## Step 3: Install Dependencies

```bash
pip3 install -r requirements.txt
```

## Step 4: Test Your Helium Modem

Run the test mode to verify your modem is detected:

```bash
python3 lora_p2p_test.py test
```

**Expected output:**
```
=== TEST MODE ===
Testing Helium LoRa modem detection and configuration...

Module Information:
--------------------------------------------------
Version Register: 0x12
  ✓ SX1276/SX1278 detected
Operation Mode: 0x81
  ✓ LoRa mode enabled
Frequency: 868.100 MHz
Bandwidth: 125 kHz
Spreading Factor: SF7
Coding Rate: 4/5
Sync Word: 0x34
  ✓ P2P mode (sync word 0x34)
...
```

If you see errors, check:
- SPI connections
- Power supply (3.3V)
- GPIO pin numbers match your wiring

## Step 5: Test P2P Communication

### Option A: Two Helium Modems

**Terminal 1 (Receiver):**
```bash
python3 lora_p2p_test.py rx
```

**Terminal 2 (Transmitter):**
```bash
python3 lora_p2p_test.py tx
```

### Option B: Helium Modem + SX1276 Module

You can test your Helium modem with a regular SX1276 module. Just ensure both use the same configuration (which the code handles automatically).

## Troubleshooting

### "Module Not Detected"

1. **Check SPI**: `lsmod | grep spi`
2. **Check connections**: Verify all pins are connected correctly
3. **Check power**: Ensure 3.3V is stable
4. **Try reset**: Power cycle the Helium modem

### "Wrong Version Number"

Some Helium modems report version 0x11 or 0x13 instead of 0x12. This is usually fine - the code will warn but should still work.

### "No Communication"

1. **Verify both modems use same settings**: Run `test` mode on both
2. **Check frequency**: Ensure both are on the same frequency band (868 MHz, 915 MHz, etc.)
3. **Check antenna**: LoRa requires an antenna to work
4. **Check sync word**: Should be 0x34 for P2P mode (code sets this automatically)

### "Modem in LoRaWAN Mode"

Some Helium modems default to LoRaWAN mode. The code automatically switches to P2P mode, but if you have issues:
1. Power cycle the module
2. Run the test mode again
3. Verify sync word is 0x34 (not 0x12)

## Adjusting Frequency

If your Helium modem is configured for a different frequency (e.g., 915 MHz for North America), edit `lora_p2p_test.py`:

```python
# In the init() method, change:
freq = 915000000  # 915 MHz (North America)
# or
freq = 433000000  # 433 MHz (Asia)
# Default is 868100000 (868.1 MHz for Europe)
```

**Important**: Both modems must use the same frequency!

## Next Steps

- Read `HELIUM_MODEM_SETUP.md` for detailed information
- Read `README.md` for general LoRa P2P information
- Experiment with different spreading factors for longer range
- Test communication distance

## Common Helium Modem Models

- **RAK811** / **RAK3172** / **RAK4631**: Should work with default pin configuration
- **LongAP LoRaWAN Module**: May need pin adjustments
- **Heltec LoRaWAN**: Should work with default configuration

If your model isn't listed, check the datasheet for SPI pin connections and adjust GPIO pins in the code if needed.
