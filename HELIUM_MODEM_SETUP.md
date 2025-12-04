# Helium LoRa Modem P2P Setup Guide

## Overview

Helium LoRa modems (like RAK, LongAP, or other Helium-compatible devices) are typically based on SX1276/SX1278 chips and can be used in P2P mode for direct communication.

## Common Helium Modem Models

- **RAK Wireless RAK811** / **RAK3172** / **RAK4631**
- **LongAP LoRaWAN Module**
- **Heltec LoRaWAN Modules**
- Other SX1276/SX1278 based Helium-compatible modems

## Important: P2P Mode vs LoRaWAN Mode

Most Helium modems come configured for **LoRaWAN mode** (Helium network). To use them in **P2P mode**, you need to:

1. **Option A**: Use AT commands to switch to P2P mode (if supported)
2. **Option B**: Directly control the SX1276 chip via SPI (bypassing AT commands)

This guide focuses on **Option B** - direct SPI control, which gives you full control over P2P communication.

## Hardware Connections

### For RAK Modules (RAK811, RAK3172, etc.)

```
Helium Modem Pin    →    RPi3 GPIO Pin    →    Physical Pin
────────────────────────────────────────────────────────────
VCC (3.3V)         →    3.3V             →    Pin 1
GND                →    GND              →    Pin 6
MOSI               →    GPIO 10 (SPI0)   →    Pin 19
MISO               →    GPIO 9 (SPI0)    →    Pin 21
SCK                →    GPIO 11 (SPI0)   →    Pin 23
NSS/CS             →    GPIO 8 (CE0)     →    Pin 24
RST                →    GPIO 25          →    Pin 22
DIO0               →    GPIO 2           →    Pin 3 (optional)
```

### For Modules with Different Pinouts

Some Helium modems may have different pin configurations. Check your module's datasheet for:
- **SPI pins** (MOSI, MISO, SCK, CS/NSS)
- **Reset pin** (RST)
- **Interrupt pin** (DIO0) - optional but recommended

## Software Setup

### 1. Enable SPI on Raspberry Pi

```bash
sudo raspi-config
# Interface Options → SPI → Enable
sudo reboot
```

Verify:
```bash
lsmod | grep spi
ls -l /dev/spi*
```

### 2. Install Dependencies

```bash
pip3 install -r requirements.txt
```

### 3. Identify Your Modem's Pin Configuration

You may need to adjust the GPIO pins in `lora_p2p_test.py` based on your specific Helium modem model.

## Testing Your Helium Modem

### Step 1: Test Module Detection

Run a simple test to see if the module is detected:

```bash
python3 lora_p2p_test.py test
```

This will attempt to read the version register and display module information.

### Step 2: Configure for P2P Mode

The code automatically configures the module for P2P mode. Key settings:
- **Sync Word**: Changed from 0x12 (LoRaWAN) to 0x34 (P2P)
- **Frequency**: 868.1 MHz (adjust for your region)
- **Explicit Header Mode**: Enabled for P2P

### Step 3: Test Communication

**Terminal 1 (Receiver):**
```bash
python3 lora_p2p_test.py rx
```

**Terminal 2 (Transmitter):**
```bash
python3 lora_p2p_test.py tx
```

## Troubleshooting Helium Modems

### Issue: Module Not Detected

1. **Check SPI connections**: Verify all SPI pins are connected correctly
2. **Check power**: Ensure 3.3V power supply is stable
3. **Check CS pin**: Verify the NSS/CS pin is connected to the correct GPIO
4. **Check SPI is enabled**: `lsmod | grep spi`

### Issue: Wrong Version Number

Some Helium modems may report different version numbers:
- SX1276: 0x12
- SX1278: 0x12 (same)
- Some clones: 0x11 or 0x13

The code will warn but should still work.

### Issue: No Communication

1. **Verify both modems use identical settings**:
   - Same frequency
   - Same spreading factor
   - Same bandwidth
   - Same sync word (0x34 for P2P)

2. **Check if modem was in LoRaWAN mode**: 
   - Some modems need a hard reset to exit LoRaWAN mode
   - Try power cycling the module

3. **Verify antenna is connected**: LoRa requires an antenna

4. **Check frequency regulations**: 
   - Europe: 868 MHz
   - North America: 915 MHz
   - Asia: 433 MHz or 868 MHz

### Issue: AT Command Interference

If your Helium modem has AT command firmware:
- The modem might be in AT command mode
- Try resetting the module
- Some modems need a specific sequence to enter SPI mode
- Check your modem's datasheet for "SPI mode" or "register mode"

## Frequency Configuration

Helium modems are typically configured for specific regions. Update the frequency in `lora_p2p_test.py`:

```python
# Europe (868 MHz band)
freq = 868100000  # 868.1 MHz

# North America (915 MHz band)
freq = 915000000  # 915 MHz

# Asia (433 MHz or 868 MHz)
freq = 433000000  # 433 MHz
# or
freq = 868100000  # 868 MHz
```

**Important**: Ensure both modems use the same frequency and comply with local regulations.

## Advanced: Using AT Commands (If Supported)

Some Helium modems support AT commands for P2P mode. If your modem supports this:

```bash
# Connect via serial (USB or UART)
# Example AT commands (check your modem's manual):
AT+MODE=TEST
AT+TEST=RFCFG,868,SF7,125,8,8,14,ON,OFF,OFF
AT+TEST=TXLRPKT,"Hello"
AT+TEST=RXLRPKT
```

However, direct SPI control (as in this code) gives you more flexibility and control.

## Testing with Your Existing SX1276 Module

You can test P2P communication between:
- **Helium modem** ↔ **Helium modem**
- **Helium modem** ↔ **SX1276 module**
- **SX1276 module** ↔ **SX1276 module**

As long as both use the same configuration (frequency, SF, BW, CR, sync word), they will communicate.

## Next Steps

1. Identify your Helium modem model
2. Check pin connections
3. Adjust GPIO pins in code if needed
4. Test module detection
5. Test P2P communication
