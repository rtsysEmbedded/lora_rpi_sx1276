# LoRa P2P Communication Test - Raspberry Pi 3 + SX1276

This project demonstrates peer-to-peer (P2P) LoRa communication between two SX1276 modules using Raspberry Pi 3.

## Quick Start

1. **Read the explanation**: See `LORA_EXPLANATION.md` for how LoRa and P2P mode work
2. **Follow setup guide**: See `setup_guide.md` for hardware and software setup
3. **Run the tests**: Use `lora_p2p_sender.py` and `lora_p2p_receiver.py`

## Files

- `LORA_EXPLANATION.md` - Detailed explanation of LoRa technology and P2P mode
- `setup_guide.md` - Step-by-step hardware and software setup instructions
- `lora_p2p_sender.py` - Script to send messages via LoRa
- `lora_p2p_receiver.py` - Script to receive messages via LoRa
- `requirements.txt` - Python dependencies

## Key Points for P2P Mode

⚠️ **CRITICAL**: Both modules MUST have identical parameters:
- Frequency (e.g., 433.0 MHz)
- Spreading Factor (e.g., 7)
- Bandwidth (e.g., 125 kHz)
- Coding Rate (e.g., 4/5)
- Sync Word (e.g., 0x12)

## Hardware Connections

```
SX1276 → Raspberry Pi 3
VCC    → 3.3V
GND    → GND
MOSI   → GPIO 10 (SPI0_MOSI)
MISO   → GPIO 9 (SPI0_MISO)
SCK    → GPIO 11 (SPI0_SCLK)
NSS    → GPIO 8 (SPI0_CE0)
RESET  → GPIO 25
DIO0   → GPIO 24 (optional)
```

## Installation

```bash
# Enable SPI
sudo raspi-config  # Interface Options → SPI → Enable

# Install dependencies
sudo apt-get update
sudo apt-get install -y python3-pip python3-dev python3-spidev python3-rpi.gpio
pip3 install -r requirements.txt
```

## Usage

**Terminal 1 (Receiver)**:
```bash
python3 lora_p2p_receiver.py
```

**Terminal 2 (Sender)**:
```bash
python3 lora_p2p_sender.py
```

Type messages in the sender terminal and watch them appear in the receiver terminal!

## Troubleshooting

If you encounter issues:
1. Verify SPI is enabled: `lsmod | grep spi`
2. Check all parameters match exactly on both modules
3. Start with modules close together (1-2 meters)
4. Verify wiring connections
5. Check power supply (3.3V, not 5V!)

See `setup_guide.md` for detailed troubleshooting.
