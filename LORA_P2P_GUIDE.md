# LoRa P2P Communication Guide for SX1276

## How LoRa Works

### Basic Principles

1. **Chirp Spread Spectrum (CSS)**
   - LoRa uses a chirp signal that sweeps across the frequency band
   - The spreading factor determines how many chirps are used to encode each symbol
   - Higher SF = longer range but slower data rate

2. **Key Parameters**

   - **Frequency**: The carrier frequency (e.g., 433MHz, 868MHz, 915MHz)
   - **Spreading Factor (SF)**: 6-12 (default 7)
     - SF7 = fastest, shortest range
     - SF12 = slowest, longest range
   - **Bandwidth (BW)**: 7.8kHz to 500kHz (default 125kHz)
   - **Coding Rate (CR)**: 4/5 to 4/8 (default 4/5)
   - **Preamble Length**: Usually 8-12 bytes
   - **Sync Word**: 0x12 (default) or custom

3. **P2P Mode (Point-to-Point)**

   - **Direct Communication**: Two modules talk directly without a gateway
   - **Same Configuration**: Both modules MUST use identical parameters
   - **Half-Duplex**: Can send OR receive, not both simultaneously
   - **No Addressing**: All messages are broadcast on the same frequency

### Communication Flow

```
Module A (Transmitter)          Module B (Receiver)
     |                                |
     |---[LoRa Packet]--------------->|
     |   (Preamble + Header + Data)   |
     |                                |
     |<--[LoRa Packet]---------------|
     |   (Preamble + Header + Data)   |
```

### Important Notes

- **Both modules must have identical settings** (frequency, SF, BW, CR, etc.)
- **Only one module transmits at a time** (half-duplex)
- **No built-in addressing** - you need to add your own message headers
- **Range depends on**: SF, BW, power, antenna, obstacles

## Hardware Setup

### SX1276 Pin Connections to Raspberry Pi 3

```
SX1276 Pin    →    RPi3 GPIO Pin
─────────────────────────────────
VCC          →    3.3V (Pin 1)
GND          →    GND (Pin 6)
MOSI         →    GPIO 10 (Pin 19) - SPI0 MOSI
MISO         →    GPIO 9 (Pin 21)  - SPI0 MISO
SCK          →    GPIO 11 (Pin 23) - SPI0 SCLK
NSS (CS)     →    GPIO 8 (Pin 24)  - SPI0 CE0
RST          →    GPIO 25 (Pin 22) - Any GPIO
DIO0         →    GPIO 2 (Pin 3)   - Interrupt pin (optional)
```

### Enable SPI on Raspberry Pi

```bash
sudo raspi-config
# Navigate to: Interface Options → SPI → Enable
# Or edit /boot/config.txt and add: dtparam=spi=on
```

## Software Setup

### Required Python Libraries

```bash
pip3 install RPi.GPIO spidev
```

### For SX1276 Library

You can use:
- `pySX127x` library
- Or implement direct register access

## Testing Strategy

1. **Module 1**: Configure as transmitter, send periodic messages
2. **Module 2**: Configure as receiver, listen and display received messages
3. **Test**: Start receiver first, then transmitter
4. **Verify**: Check if messages are received correctly

## Common Issues

1. **No reception**: Check that both modules use identical parameters
2. **CRC errors**: Increase preamble length or check antenna connections
3. **Short range**: Increase spreading factor or check power settings
4. **Interference**: Try different frequency or adjust bandwidth
