# LoRa P2P Setup Guide for Raspberry Pi 3 + SX1276

## Hardware Requirements

- Raspberry Pi 3 (or any Pi with SPI)
- 2x SX1276 LoRa modules
- Jumper wires
- Antennas for your LoRa modules (matching your frequency band)
- Power supply for Raspberry Pi

## Hardware Connections

### Wiring Diagram

Connect each SX1276 module to Raspberry Pi 3 as follows:

```
SX1276 Module          Raspberry Pi 3
─────────────────      ──────────────────
VCC (3.3V)        →    3.3V (Pin 1)
GND               →    GND (Pin 6)
MOSI              →    GPIO 10 / SPI0_MOSI (Pin 19)
MISO              →    GPIO 9 / SPI0_MISO (Pin 21)
SCK               →    GPIO 11 / SPI0_SCLK (Pin 23)
NSS (CS)          →    GPIO 8 / SPI0_CE0 (Pin 24)
RESET             →    GPIO 25 (Pin 22)
DIO0              →    GPIO 24 (Pin 18) [Optional]
```

**Note**: If you're using two modules on the same Pi (for testing), you can use:
- Module 1: CS → GPIO 8 (SPI0_CE0)
- Module 2: CS → GPIO 7 (SPI0_CE1)

## Software Setup

### Step 1: Enable SPI on Raspberry Pi

```bash
sudo raspi-config
```

Navigate to: **Interface Options** → **SPI** → **Enable**

Or manually edit `/boot/config.txt`:
```bash
sudo nano /boot/config.txt
```

Add or uncomment:
```
dtparam=spi=on
```

Reboot:
```bash
sudo reboot
```

### Step 2: Verify SPI is Enabled

```bash
lsmod | grep spi
ls -l /dev/spi*
```

You should see `/dev/spidev0.0` and `/dev/spidev0.1`

### Step 3: Install Python Dependencies

```bash
# Update package list
sudo apt-get update

# Install required system packages
sudo apt-get install -y python3-pip python3-dev python3-spidev python3-rpi.gpio

# Install Python libraries
pip3 install -r requirements.txt
```

**Note**: The `lora` library might need to be installed differently. If `pyLoRa` doesn't work, try:

```bash
pip3 install RPi.GPIO spidev
git clone https://github.com/lemariva/pyLoRa.git
cd pyLoRa
sudo python3 setup.py install
```

Or use an alternative library like `LoRa`:
```bash
pip3 install LoRa
```

### Step 4: Configure Parameters

Edit both `lora_p2p_sender.py` and `lora_p2p_receiver.py` to match your setup:

1. **GPIO Pins**: Adjust if your wiring is different
2. **Frequency**: 
   - 433 MHz: Europe/Asia (check local regulations)
   - 868 MHz: Europe
   - 915 MHz: North America
3. **Other parameters**: Keep defaults for initial testing

**CRITICAL**: Both sender and receiver MUST have identical parameters!

## Testing Procedure

### Option 1: Two Raspberry Pi 3s (Recommended)

1. **Setup Pi #1 (Receiver)**:
   ```bash
   python3 lora_p2p_receiver.py
   ```

2. **Setup Pi #2 (Sender)**:
   ```bash
   python3 lora_p2p_sender.py
   ```

3. Type messages in the sender terminal and watch them appear in the receiver terminal.

### Option 2: One Raspberry Pi 3 (Advanced)

If you have two SX1276 modules connected to one Pi:
- Modify the scripts to use different CS pins (GPIO 8 and GPIO 7)
- Run receiver in background: `python3 lora_p2p_receiver.py &`
- Run sender in foreground: `python3 lora_p2p_sender.py`

### Option 3: One Pi + Another Device

- Run receiver on Pi
- Use another microcontroller (Arduino, ESP32, etc.) with SX1276 as sender

## Troubleshooting

### Problem: "Failed to initialize LoRa"

**Solutions**:
1. Check SPI is enabled: `lsmod | grep spi`
2. Verify wiring, especially CS, MOSI, MISO, SCK
3. Check power supply (3.3V, not 5V!)
4. Verify GPIO pin numbers in code match your wiring

### Problem: No messages received

**Solutions**:
1. **CRITICAL**: Verify parameters match exactly on both modules
   - Frequency
   - Spreading Factor
   - Bandwidth
   - Coding Rate
   - Sync Word
2. Check antennas are connected
3. Start with modules close together (1-2 meters)
4. Verify both modules are powered on
5. Check that sender is actually transmitting (LED on module might blink)

### Problem: Module not detected

**Solutions**:
1. Check SPI connection: `sudo python3 -c "import spidev; s=spidev.SpiDev(); s.open(0,0); print('SPI OK')"`
2. Verify CS pin is correct
3. Try different CS pin (GPIO 7 or GPIO 8)
4. Check module is getting 3.3V power

### Problem: Import errors

**Solutions**:
1. Install missing packages: `pip3 install <package-name>`
2. Use Python 3: `python3` not `python`
3. Try alternative LoRa library if pyLoRa doesn't work

## Testing Range

1. Start with modules **1-2 meters apart**
2. Once working, gradually increase distance
3. Test in different environments:
   - Indoors (walls reduce range)
   - Outdoors line-of-sight (best range)
   - Through obstacles (walls, trees)

## Parameter Tuning for Range

If you need more range:
- **Increase Spreading Factor**: Try SF9, SF10, SF11, SF12 (slower but longer range)
- **Increase TX Power**: Up to 20 dBm (check local regulations)
- **Use lower bandwidth**: Try 62.5 kHz or 31.25 kHz

If you need faster transmission:
- **Decrease Spreading Factor**: Try SF6 or SF7
- **Increase bandwidth**: Try 250 kHz or 500 kHz

## Safety and Regulations

⚠️ **Important**: 
- Check your local regulations for ISM band usage
- Some frequencies require licenses
- Power limits vary by region
- 433 MHz: Often license-free but check local laws
- 868 MHz: EU license-free (with power limits)
- 915 MHz: US license-free (with power limits)

## Next Steps

Once basic P2P communication works:
1. Add acknowledgment (ACK) mechanism
2. Implement error handling and retries
3. Add packet sequence numbers
4. Create a simple protocol for structured data
5. Test maximum range in your environment
6. Add encryption if needed for security
