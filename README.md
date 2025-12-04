# LoRaWAN Client for Raspberry Pi + SX1276

This project connects a Raspberry Pi with SX1276 LoRa module to a ChirpStack gateway using LoRaWAN OTAA (Over-The-Air Activation).

## 📋 Requirements

### Hardware
- Raspberry Pi 3 (or any RPi with SPI support)
- SX1276 LoRa module
- LoRa Gateway with ChirpStack installed
- Jumper wires
- 3.3V power supply

### Software
- Raspberry Pi OS (Raspbian)
- Python 3.7+
- SPI enabled on Raspberry Pi

## 🔌 Wiring Diagram

Connect the SX1276 module to Raspberry Pi 3 as follows:

```
SX1276 Pin    →    Raspberry Pi 3 Pin    →    BCM GPIO
================================================================
VCC           →    Pin 1 or 17            →    3.3V Power
GND           →    Pin 6, 9, 14, 20, etc  →    Ground
MISO          →    Pin 21                 →    GPIO 9 (MISO)
MOSI          →    Pin 19                 →    GPIO 10 (MOSI)
SCK (SCLK)    →    Pin 23                 →    GPIO 11 (SCLK)
NSS (CS)      →    Pin 24                 →    GPIO 8 (CE0)
RESET (RST)   →    Pin 22                 →    GPIO 25
DIO0          →    Pin 18                 →    GPIO 24
DIO1          →    Pin 16                 →    GPIO 23
DIO2          →    (Optional)             →    Not connected
DIO3          →    (Optional)             →    Not connected
```

### Visual Pin Layout:
```
Raspberry Pi 3 GPIO Header (looking at the board):
    3.3V  [ 1] [ 2]  5V
         [ 3] [ 4]  5V
         [ 5] [ 6]  GND
         [ 7] [ 8]  (CE0) ← NSS
     GND [ 9] [10]
         [11] [12]
         [13] [14]  GND
         [15] [16]  GPIO 23 ← DIO1
    3.3V [17] [18]  GPIO 24 ← DIO0
    MOSI [19] [20]  GND
    MISO [21] [22]  GPIO 25 ← RESET
     SCK [23] [24]  CE0 ← NSS
```

### ⚠️ Important Notes:
- **Use 3.3V ONLY** - SX1276 is NOT 5V tolerant!
- Double-check all connections before powering on
- Ensure good quality jumper wires (poor connections cause intermittent issues)
- Keep antenna connected when transmitting to avoid damage

## 🚀 Installation

### 1. Enable SPI on Raspberry Pi

```bash
sudo raspi-config
```
- Navigate to: **Interface Options** → **SPI** → **Enable**
- Reboot: `sudo reboot`

Verify SPI is enabled:
```bash
lsmod | grep spi
# Should show: spi_bcm2835
```

### 2. Install System Dependencies

```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-dev python3-rpi.gpio
```

### 3. Clone or Download This Repository

```bash
cd /home/pi
git clone <your-repo-url>
cd <repo-directory>
```

Or if you copied the files manually, ensure all files are in the same directory.

### 4. Install Python Dependencies

**Option A: Automatic Installation (Recommended)**
```bash
sudo bash install.sh
```

**Option B: Manual Installation**

See `MANUAL_INSTALL.md` or `INSTALL_INSTRUCTIONS.md` for detailed steps.

Quick version:
```bash
# Install basic packages
pip3 install RPi.GPIO spidev pycryptodome

# Install pySX127x from GitHub
cd /tmp
git clone https://github.com/rpsreal/pySX127x.git
cd pySX127x
sudo python3 setup.py install
cd ~
```

**Verify Installation:**
```bash
python3 check_dependencies.py
```

## ⚙️ Configuration

### 1. Update Device Credentials

Edit `config.py` and update your ChirpStack device credentials:

```python
DEVICE_EUI = "0bbef9f59cc6986a"  # Your Device EUI
APP_KEY = "d8341a42c8894b3bb82d0f721a0fcdbc"  # Your Application Key
APP_EUI = "0000000000000000"  # Get from ChirpStack application
```

**Important:** Get the `APP_EUI` from your ChirpStack application:
1. Log into ChirpStack web interface
2. Go to Applications → Your Application
3. Copy the Application EUI (might be called JoinEUI in ChirpStack v4)

### 2. Set Frequency for Your Region

In `config.py`, set the appropriate frequency:

```python
# For Europe (EU868):
FREQUENCY = 868.1  # MHz

# For USA (US915):
# FREQUENCY = 915.0  # MHz

# For Asia (AS923):
# FREQUENCY = 923.2  # MHz
```

### 3. Adjust GPIO Pins (if needed)

If you used different GPIO pins, update them in `config.py`:

```python
PIN_NSS = 8      # Chip Select
PIN_RESET = 25   # Reset pin
PIN_DIO0 = 24    # DIO0
PIN_DIO1 = 23    # DIO1
```

## 🧪 Testing

### 1. Test Hardware Connection

Run the test script to verify your SX1276 is properly connected:

```bash
sudo python3 test_connection.py
```

Expected output:
```
✓ GPIO and SPI initialized
✓ LoRa instance created
✓ Chip version: 0x12
✓ SX1276 detected!
✓ All tests passed! Hardware is working correctly.
```

If you see errors, check:
- Wiring connections
- SPI is enabled
- Running with `sudo`
- 3.3V power supply

### 2. Verify ChirpStack Configuration

Ensure your device is properly registered in ChirpStack:

1. **Application exists** with devices
2. **Device is registered** with:
   - Device EUI: `0bbef9f59cc6986a`
   - Activation: **OTAA**
   - Application Key: `d8341a42c8894b3bb82d0f721a0fcdbc`
3. **Gateway is online** (check ChirpStack dashboard)
4. **Device profile** matches your region (EU868/US915)

## 🎯 Running the Application

Start the LoRaWAN client:

```bash
sudo python3 main.py
```

Expected output:
```
============================================================
LoRaWAN Client for ChirpStack
============================================================
LoRaWAN Client initialized
DevEUI: 0bbef9f59cc6986a
Frequency: 868.1 MHz

=== Starting OTAA Join ===
Sending Join Request: ...
Waiting for Join Accept...
Received: ...
Join Accept received!
DevAddr: xxxxxxxx
=== Join Successful! ===

=== Sending Data ===
Payload: b'Hello from RPi! Count: 0'
FCnt: 0
Frame: ...
Data sent successfully!

Waiting 30 seconds before next transmission...
```

### Monitor in ChirpStack

1. Go to ChirpStack web interface
2. Navigate to: **Applications** → **Your Application** → **Your Device**
3. Click on **LoRaWAN frames** tab
4. You should see:
   - Join Request
   - Join Accept
   - Uplink data frames

## 📊 Monitoring and Debugging

### View Received Data

In ChirpStack, go to your device and check:
- **LoRaWAN frames**: See all raw frames
- **Device data**: See decoded application data
- **Events**: See join/uplink events

### Check Gateway Traffic

```bash
# On gateway machine
sudo journalctl -u chirpstack-gateway-bridge -f
```

### Common Issues

#### 1. Join Request Not Received
- **Check gateway**: Is it online in ChirpStack?
- **Check frequency**: Does it match your region?
- **Check range**: Are you within range of gateway?
- **Check antenna**: Is antenna properly connected?

#### 2. Join Accept Not Received
- **Device not registered**: Check ChirpStack device settings
- **Wrong credentials**: Verify DevEUI and AppKey
- **Wrong APP_EUI**: Update from ChirpStack application

#### 3. No Data in ChirpStack
- **Check join status**: Did join succeed?
- **Check frame counter**: Should increment with each send
- **Check application**: Is data being routed correctly?

#### 4. SPI Error
```bash
# Check SPI is enabled
ls /dev/spi*
# Should show: /dev/spidev0.0 /dev/spidev0.1

# Check permissions
sudo chmod 666 /dev/spidev0.0
```

#### 5. GPIO Error
- Run with `sudo` (GPIO requires root access)
- Check no other processes using GPIO pins

## 🔧 Advanced Configuration

### Change Transmission Interval

In `main.py`, modify:
```python
time.sleep(30)  # Change to desired seconds
```

### Send Different Data Types

```python
# Send JSON
import json
data = json.dumps({"temperature": 22.5, "humidity": 60})
client.send_data(data, port=1)

# Send binary data
data = struct.pack('ffi', temp, humidity, counter)
client.send_data(data, port=2)
```

### Adjust Spreading Factor (for range/speed)

In `config.py`:
```python
SPREADING_FACTOR = 12  # SF12 = max range, slow speed
# or
SPREADING_FACTOR = 7   # SF7 = short range, fast speed
```

### Enable Confirmed Uplinks

In `main.py`:
```python
client.send_data(message, confirmed=True, port=1)
```

## 📝 File Structure

```
.
├── config.py              # Configuration file (credentials, pins, etc)
├── lorawan_client.py      # LoRaWAN client implementation
├── board_config.py        # Board/GPIO configuration
├── main.py                # Main application
├── test_connection.py     # Hardware test script
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🛠️ Troubleshooting Commands

```bash
# Check SPI
lsmod | grep spi

# Check GPIO
gpio readall

# Check Python packages
pip3 list | grep -E "RPi.GPIO|spidev|pycrypto"

# Monitor system logs
sudo journalctl -f

# Test SPI communication
sudo apt-get install python3-spidev
python3 -c "import spidev; s=spidev.SpiDev(); s.open(0,0); print('SPI OK')"
```

## 📚 Resources

- [SX1276 Datasheet](https://www.semtech.com/products/wireless-rf/lora-transceivers/sx1276)
- [LoRaWAN Specification](https://lora-alliance.org/resource_hub/lorawan-specification-v1-1/)
- [ChirpStack Documentation](https://www.chirpstack.io/docs/)
- [Raspberry Pi GPIO Pinout](https://pinout.xyz/)

## 📄 License

This project is provided as-is for educational and development purposes.

## 🆘 Support

If you encounter issues:
1. Run `test_connection.py` first
2. Check all wiring connections
3. Verify ChirpStack configuration
4. Check gateway is online and in range
5. Review ChirpStack logs for errors

---

**Happy LoRa-ing! 📡**
