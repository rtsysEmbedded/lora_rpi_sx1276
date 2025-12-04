# LoRa P2P Communication Test (SX1276 + Raspberry Pi 3)

This project demonstrates Point-to-Point (P2P) communication between two SX1276 LoRa modules using Raspberry Pi 3.

## 📦 Hardware Required

- 2x Raspberry Pi 3 (or any RPi with SPI)
- 2x SX1276 LoRa Module (433/868/915 MHz)
- Jumper wires
- 2x Antenna (matching your module frequency)

## 🔌 Wiring Diagram

Connect each SX1276 module to its Raspberry Pi:

```
SX1276 Module          Raspberry Pi 3
─────────────          ──────────────
VCC  ─────────────────> 3.3V (Pin 1)
GND  ─────────────────> GND (Pin 6)
SCK  ─────────────────> SCLK/GPIO11 (Pin 23)
MISO ─────────────────> MISO/GPIO9 (Pin 21)
MOSI ─────────────────> MOSI/GPIO10 (Pin 19)
NSS  ─────────────────> CE0/GPIO8 (Pin 24)
DIO0 ─────────────────> GPIO4 (Pin 7)
RST  ─────────────────> GPIO17 (Pin 11)
```

### Pin Reference Table

| SX1276 | Function | RPi Pin | GPIO |
|--------|----------|---------|------|
| VCC | Power 3.3V | 1 | - |
| GND | Ground | 6 | - |
| SCK | SPI Clock | 23 | GPIO11 |
| MISO | SPI Data Out | 21 | GPIO9 |
| MOSI | SPI Data In | 19 | GPIO10 |
| NSS | Chip Select | 24 | GPIO8/CE0 |
| DIO0 | Interrupt | 7 | GPIO4 |
| RST | Reset | 11 | GPIO17 |

⚠️ **Important**: Connect the antenna before powering on! Transmitting without an antenna can damage the module.

## 🛠️ Setup

### 1. Enable SPI on Raspberry Pi

```bash
sudo raspi-config
# Navigate to: Interface Options -> SPI -> Enable
sudo reboot
```

Verify SPI is enabled:
```bash
ls /dev/spi*
# Should show: /dev/spidev0.0  /dev/spidev0.1
```

### 2. Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python packages
sudo apt install python3-pip python3-dev -y

# Install required libraries
pip3 install spidev RPi.GPIO
# or
pip3 install -r requirements.txt
```

### 3. Clone/Copy Files

Copy these files to both Raspberry Pis:
- `sx1276.py` - Driver module
- `transmitter.py` - Transmitter script
- `receiver.py` - Receiver script

## 🚀 Running the Test

### Quick Test

**On Raspberry Pi #1 (Receiver):**
```bash
python3 receiver.py
```

**On Raspberry Pi #2 (Transmitter):**
```bash
python3 transmitter.py
```

### Custom Messages

```bash
# Send custom message every 5 seconds
python3 transmitter.py "My custom message" 5
```

### With Timeout

```bash
# Receiver with 10-second timeout
python3 receiver.py 10
```

## ⚙️ Configuration

Edit the configuration section in both `transmitter.py` and `receiver.py`:

```python
# CONFIGURATION - Must match on both devices!
FREQUENCY = 433000000      # 433 MHz
SPREADING_FACTOR = 7       # SF7-SF12
BANDWIDTH = 125000         # 125 kHz
CODING_RATE = 5            # 4/5
TX_POWER = 17              # dBm
SYNC_WORD = 0x12           # Private sync word
```

### Frequency Options

| Region | Frequency |
|--------|-----------|
| Europe (EU) | 868 MHz |
| Americas (US) | 915 MHz |
| Asia | 433 MHz or 923 MHz |

Change frequency:
```python
FREQUENCY = 868000000  # 868 MHz for EU
```

### Range vs Speed Tradeoff

| Setting | More Range | Faster Speed |
|---------|------------|--------------|
| Spreading Factor | SF12 | SF7 |
| Bandwidth | 125 kHz | 500 kHz |

For maximum range:
```python
SPREADING_FACTOR = 12
BANDWIDTH = 125000
```

For faster speed:
```python
SPREADING_FACTOR = 7
BANDWIDTH = 250000
```

## 📊 Expected Output

### Transmitter
```
==================================================
    LoRa P2P Transmitter (SX1276)
==================================================

[*] Initializing SX1276...
[✓] SX1276 initialized!

[*] Configuration:
    frequency: 433000000
    spreading_factor: 7
    bandwidth: 125000
    coding_rate: 4/5
    tx_power: 17

[*] Sending message every 3.0 seconds
[*] Message: 'Hello from LoRa TX!'

[*] Press Ctrl+C to stop

--------------------------------------------------
[TX] Sending: Hello from LoRa TX! #1
[✓] Sent successfully (52.3 ms)
--------------------------------------------------
[TX] Sending: Hello from LoRa TX! #2
[✓] Sent successfully (51.8 ms)
```

### Receiver
```
==================================================
    LoRa P2P Receiver (SX1276)
==================================================

[*] Initializing SX1276...
[✓] SX1276 initialized!

[*] Configuration:
    frequency: 433000000
    spreading_factor: 7
    bandwidth: 125000
    coding_rate: 4/5
    tx_power: 17

[*] Waiting for packets (timeout: forever)
[*] Press Ctrl+C to stop

--------------------------------------------------
[RX] Listening...

[✓] Packet #1 received!
    Message: Hello from LoRa TX! #1
    Length:  22 bytes
    RSSI:    -45 dBm ▂▄▆█ (Excellent)
    SNR:     9.5 dB
--------------------------------------------------
```

## 🔧 Troubleshooting

### "Invalid SX1276 version" Error

1. Check wiring connections
2. Ensure SPI is enabled: `ls /dev/spi*`
3. Check VCC is connected to 3.3V (not 5V!)
4. Verify module is powered (some have LED)

### No Packets Received

1. **Verify configurations match** on both devices
2. Check both antennas are connected
3. Move devices closer together
4. Try increasing spreading factor (SF12)
5. Check frequency matches your module

### Permission Denied

```bash
# Run with sudo
sudo python3 receiver.py

# Or add user to gpio group
sudo usermod -aG gpio $USER
sudo usermod -aG spi $USER
# Then logout and login again
```

### SPI Not Found

```bash
# Enable SPI
sudo raspi-config
# Interface Options -> SPI -> Enable
sudo reboot
```

## 📚 Understanding the Output

### RSSI (Received Signal Strength Indicator)
- **> -70 dBm**: Excellent signal
- **-70 to -85 dBm**: Good signal
- **-85 to -100 dBm**: Fair signal
- **-100 to -115 dBm**: Weak signal
- **< -115 dBm**: Very weak

### SNR (Signal-to-Noise Ratio)
- **> 0 dB**: Signal stronger than noise (good)
- **< 0 dB**: Signal weaker than noise (LoRa can still decode up to -20 dB!)

## 📁 File Structure

```
.
├── README.md           # This file
├── requirements.txt    # Python dependencies
├── sx1276.py          # SX1276 driver module
├── transmitter.py     # Transmitter script
└── receiver.py        # Receiver script
```

## 🔗 References

- [SX1276 Datasheet](https://www.semtech.com/products/wireless-rf/lora-connect/sx1276)
- [LoRa Modulation Basics](https://www.semtech.com/lora)
- [Raspberry Pi SPI](https://www.raspberrypi.org/documentation/hardware/raspberrypi/spi/)
