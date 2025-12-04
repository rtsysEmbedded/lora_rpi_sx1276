# Troubleshooting: Version 0x00 (SPI Communication Issue)

## Problem

When running `python3 lora_p2p_test.py test`, you see:
```
Version Register: 0x00
Operation Mode: 0x00
Frequency: 0.000 MHz
```

All registers reading `0x00` indicates **SPI communication is not working**.

## Quick Checks

### 1. Verify SPI is Enabled

```bash
lsmod | grep spi
```

**Expected output:**
```
spi_bcm2835             20480  0
```

If nothing appears, enable SPI:
```bash
sudo raspi-config
# Interface Options -> SPI -> Enable
sudo reboot
```

### 2. Check SPI Device Exists

```bash
ls -l /dev/spi*
```

**Expected output:**
```
/dev/spidev0.0
/dev/spidev0.1
```

If these don't exist, SPI is not enabled.

### 3. Verify Wiring

Check these critical connections:

```
Helium Modem    →    RPi3 GPIO    →    Physical Pin
─────────────────────────────────────────────────────
VCC (3.3V)      →    3.3V         →    Pin 1
GND             →    GND          →    Pin 6
MOSI            →    GPIO 10      →    Pin 19
MISO            →    GPIO 9       →    Pin 21
SCK             →    GPIO 11      →    Pin 23
NSS/CS          →    GPIO 8       →    Pin 24  ⚠ CRITICAL
RST             →    GPIO 25      →    Pin 22
```

**Most common issue**: Wrong NSS/CS pin!

### 4. Test with Different SPI Device

Try SPI device 1 instead of 0:

```bash
python3 lora_p2p_test.py test --spi-device 1
```

### 5. Test with Different NSS Pin

If your Helium modem uses a different CS pin, try:

```bash
# Try GPIO 7 (CE1)
python3 lora_p2p_test.py test --nss-pin 7

# Try GPIO 18
python3 lora_p2p_test.py test --nss-pin 18
```

### 6. Check Power Supply

- Ensure **3.3V** (not 5V!)
- Check with multimeter if possible
- Try different power source
- Ensure GND is connected

### 7. Verify Module is Responding

Some Helium modems need a specific reset sequence. The updated code now:
- Holds reset longer
- Waits longer after reset
- Uses slower SPI speed initially

## Common Causes

### Wrong NSS/CS Pin (Most Common)

Different Helium modem models use different CS pins:
- **RAK modules**: Usually GPIO 8 (CE0)
- **Some modules**: GPIO 7 (CE1)
- **Custom boards**: Check datasheet

**Solution**: Try different pins:
```bash
python3 lora_p2p_test.py test --nss-pin 7
python3 lora_p2p_test.py test --nss-pin 18
```

### SPI Not Enabled

**Solution**:
```bash
sudo raspi-config
# Interface Options -> SPI -> Enable
sudo reboot
```

### Wrong SPI Bus/Device

Some setups use SPI1 instead of SPI0:
```bash
python3 lora_p2p_test.py test --spi-bus 1 --spi-device 0
```

### Module in Wrong Mode

Some Helium modems have AT command firmware that interferes:
- Try power cycling the module
- Check if module has a mode switch
- Some modules need a specific sequence to enter SPI mode

### Wiring Issues

- **Loose connections**: Re-seat all wires
- **Wrong pins**: Double-check pin numbers
- **Short circuits**: Check for accidental connections
- **Bad wires**: Try different jumper wires

## Diagnostic Commands

### Check SPI Kernel Module

```bash
dmesg | grep -i spi
```

### Test SPI Communication (Advanced)

```bash
# Install spidev-test (if available)
sudo apt-get install -y git build-essential
git clone https://github.com/raspberrypi/linux.git
# Or use a simple Python test
python3 -c "
import spidev
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000
try:
    result = spi.xfer2([0x42, 0x00])
    print(f'SPI test result: {result}')
except Exception as e:
    print(f'SPI error: {e}')
spi.close()
"
```

### Check GPIO Pins

```bash
# Install gpio utility
sudo apt-get install -y wiringpi
# Or use Python
python3 -c "
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(8, GPIO.OUT)
GPIO.output(8, GPIO.HIGH)
print('GPIO 8 set high')
GPIO.cleanup()
"
```

## Helium Modem Specific Issues

### RAK Modules

- Usually use **GPIO 8 (CE0)** for NSS
- May need **GPIO 7 (CE1)** on some models
- Check RAK documentation for your specific model

### LongAP Modules

- May use different pin configuration
- Check LongAP datasheet
- Some models have DIP switches for configuration

### Modules with AT Command Firmware

If your Helium modem has AT command firmware:
1. It might be in AT mode instead of SPI mode
2. Try sending AT commands to switch modes (check modem manual)
3. Some modems need a hardware jumper to enable SPI mode
4. Power cycle the module

## Step-by-Step Debugging

1. **Run test with verbose output**:
   ```bash
   python3 lora_p2p_test.py test
   ```

2. **Check SPI device**:
   ```bash
   ls -l /dev/spi*
   ```

3. **Try different SPI device**:
   ```bash
   python3 lora_p2p_test.py test --spi-device 1
   ```

4. **Try different NSS pin**:
   ```bash
   python3 lora_p2p_test.py test --nss-pin 7
   ```

5. **Check wiring** - physically verify all connections

6. **Check power** - verify 3.3V with multimeter

7. **Try different module** - if you have another LoRa module, test with that

8. **Check module datasheet** - verify pin configuration matches your wiring

## Still Not Working?

1. **Share your Helium modem model** - different models have different requirements
2. **Check module datasheet** - look for SPI pin configuration
3. **Try oscilloscope/logic analyzer** - verify SPI signals are present
4. **Test with known working module** - verify your Raspberry Pi setup works
5. **Check for hardware issues** - module might be damaged

## Success Indicators

When SPI communication works, you should see:
```
Version Register: 0x12 (or 0x11, 0x13 for some clones)
Operation Mode: 0x81 (LoRa mode enabled)
Frequency: 868.100 MHz (or your configured frequency)
```

Even if version is not 0x12, if you see **non-zero values** in registers, SPI is working!
