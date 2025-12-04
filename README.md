# LoRa P2P Communication Test - SX1276 & Raspberry Pi 3

This project demonstrates point-to-point (P2P) communication between two SX1276 LoRa modules or Helium LoRa modems using a Raspberry Pi 3.

## Supported Hardware

- **SX1276 LoRa modules** (generic)
- **SX1278 LoRa modules** (generic)
- **Helium LoRa modems** (RAK, LongAP, and other Helium-compatible devices based on SX1276/SX1278)

## Understanding LoRa P2P Mode

### How LoRa Works

LoRa (Long Range) uses **Chirp Spread Spectrum (CSS)** modulation:
- A chirp signal sweeps across the frequency band
- The **Spreading Factor (SF)** determines how many chirps encode each symbol
- Higher SF = longer range but slower data rate
- Lower SF = shorter range but faster data rate

### P2P Mode Characteristics

1. **Direct Communication**: Two modules communicate directly without a gateway
2. **Identical Configuration**: Both modules MUST use the same parameters:
   - Frequency
   - Spreading Factor (SF)
   - Bandwidth (BW)
   - Coding Rate (CR)
   - Preamble length
   - Sync word
3. **Half-Duplex**: Can send OR receive, not both simultaneously
4. **No Built-in Addressing**: All messages are broadcast on the same frequency

### Key Parameters Explained

- **Frequency**: Carrier frequency (e.g., 433MHz, 868MHz, 915MHz) - must match your region's regulations
- **Spreading Factor (SF)**: 6-12 (default 7)
  - SF7 = fastest, shortest range (~2-5 km)
  - SF12 = slowest, longest range (~15-20 km)
- **Bandwidth (BW)**: 7.8kHz to 500kHz (default 125kHz)
  - Lower BW = longer range, slower
  - Higher BW = shorter range, faster
- **Coding Rate (CR)**: 4/5 to 4/8 (default 4/5)
  - Higher CR = more error correction, slower
- **Preamble**: Usually 8-12 bytes, helps receiver detect the signal
- **Sync Word**: 0x12 (LoRaWAN default) or 0x34 (P2P default)

## Hardware Setup

### SX1276 Pin Connections to Raspberry Pi 3

```
SX1276 Pin    →    RPi3 GPIO Pin    →    Physical Pin
─────────────────────────────────────────────────────
VCC          →    3.3V             →    Pin 1
GND          →    GND              →    Pin 6
MOSI         →    GPIO 10 (SPI0)   →    Pin 19
MISO         →    GPIO 9 (SPI0)    →    Pin 21
SCK          →    GPIO 11 (SPI0)   →    Pin 23
NSS (CS)     →    GPIO 8 (CE0)     →    Pin 24
RST          →    GPIO 25          →    Pin 22
DIO0         →    GPIO 2           →    Pin 3 (optional)
```

### Enable SPI on Raspberry Pi

```bash
sudo raspi-config
# Navigate to: Interface Options → SPI → Enable
# Reboot after enabling
```

Or manually:
```bash
sudo nano /boot/config.txt
# Add or uncomment: dtparam=spi=on
sudo reboot
```

Verify SPI is enabled:
```bash
lsmod | grep spi
# Should show spi_bcm2835
```

## Software Setup

### Install Dependencies

```bash
pip3 install -r requirements.txt
```

Or manually:
```bash
pip3 install RPi.GPIO spidev
```

## Usage

### For Helium Modems

**First, test your Helium modem detection:**
```bash
python3 lora_p2p_test.py test
```

This will verify:
- Module is detected correctly
- SPI communication is working
- Configuration is set for P2P mode
- Current frequency and settings

See `HELIUM_MODEM_SETUP.md` for detailed Helium modem setup instructions.

### Testing with Two Modules

You need two Raspberry Pi 3 boards, each with an SX1276 module or Helium modem connected.

**Terminal 1 (Receiver):**
```bash
python3 lora_p2p_test.py rx
```

**Terminal 2 (Transmitter):**
```bash
python3 lora_p2p_test.py tx
```

The transmitter will send messages every 5 seconds, and the receiver will display them with RSSI and SNR values.

**Note**: You can mix and match - test a Helium modem with a regular SX1276 module, as long as both use the same configuration.

### Single Module Testing

If you only have one module, you can test by:
1. Running receiver mode first
2. Then running transmitter mode in another terminal
3. The module will switch between TX and RX modes

## Configuration

### Adjusting Parameters

Edit `lora_p2p_test.py` and modify the `init()` method:

```python
# Change frequency (adjust for your region)
freq = 433000000  # 433 MHz (Europe/Asia)
# or
freq = 915000000  # 915 MHz (North America)

# Change Spreading Factor (in REG_MODEM_CONFIG_2)
# SF7 = 0x74, SF8 = 0x84, SF9 = 0x94, SF10 = 0xA4, SF11 = 0xB4, SF12 = 0xC4
self.write_register(Registers.REG_MODEM_CONFIG_2, 0x74)  # SF7

# Change Bandwidth (in REG_MODEM_CONFIG_1)
# 7.8kHz = 0x00, 10.4kHz = 0x10, 15.6kHz = 0x20, 20.8kHz = 0x30,
# 31.25kHz = 0x40, 41.7kHz = 0x50, 62.5kHz = 0x60, 125kHz = 0x70, 250kHz = 0x80, 500kHz = 0x90
self.write_register(Registers.REG_MODEM_CONFIG_1, 0x72)  # 125kHz, CR 4/5
```

### Important Notes

- **Both modules must have identical settings** for communication to work
- **Check your local regulations** for allowed frequencies and power levels
- **Antenna quality** significantly affects range
- **Line of sight** provides best range (obstacles reduce range)

## Troubleshooting

### No Reception

1. Verify both modules use identical parameters
2. Check SPI connections
3. Verify antenna is connected
4. Try increasing preamble length
5. Check if modules are in same frequency band

### CRC Errors

1. Increase preamble length
2. Check antenna connections
3. Reduce distance or increase power
4. Try different spreading factor

### Short Range

1. Increase spreading factor (SF7 → SF12)
2. Reduce bandwidth (125kHz → 62.5kHz)
3. Check antenna quality and orientation
4. Ensure line of sight

### Module Not Detected

1. Check SPI is enabled: `lsmod | grep spi`
2. Verify wiring connections
3. Check power supply (3.3V)
4. Verify chip select (NSS) pin

### Helium Modem Specific Issues

1. **Modem in LoRaWAN mode**: Some Helium modems default to LoRaWAN mode. The code automatically switches to P2P mode, but you may need to power cycle the module
2. **AT command interference**: If your modem has AT command firmware, ensure it's not interfering with SPI communication
3. **Different pin configuration**: Check `HELIUM_MODEM_SETUP.md` for pin configurations specific to your Helium modem model
4. **Version mismatch**: Some Helium modems may report different version numbers but still work - run `python3 lora_p2p_test.py test` to verify

## Range Expectations

With default settings (SF7, 125kHz BW):
- **Indoor**: 50-200 meters
- **Outdoor (urban)**: 1-3 km
- **Outdoor (rural)**: 3-5 km

With SF12, 125kHz BW:
- **Outdoor (rural)**: 10-20 km (line of sight)

## Additional Resources

- **`HELIUM_MODEM_SETUP.md`** - Detailed guide for setting up Helium LoRa modems
- **`LORA_P2P_GUIDE.md`** - Technical explanation of LoRa P2P communication

## License

This code is provided as-is for educational and testing purposes.
