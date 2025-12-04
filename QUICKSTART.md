# Quick Start Guide

Get your Raspberry Pi + SX1276 connected to ChirpStack in 5 minutes!

## 1️⃣ Hardware Setup

Connect SX1276 to Raspberry Pi:

```
SX1276 → Raspberry Pi
=====================
VCC    → Pin 1 (3.3V)
GND    → Pin 6 (GND)
MISO   → Pin 21 (GPIO 9)
MOSI   → Pin 19 (GPIO 10)
SCK    → Pin 23 (GPIO 11)
NSS    → Pin 24 (GPIO 8)
RESET  → Pin 22 (GPIO 25)
DIO0   → Pin 18 (GPIO 24)
DIO1   → Pin 16 (GPIO 23)
```

⚠️ **Use 3.3V only!** SX1276 is NOT 5V tolerant!

## 2️⃣ Install Software

```bash
# Enable SPI
sudo raspi-config
# Navigate to: Interface Options → SPI → Enable → Reboot

# Install dependencies
sudo bash install.sh
```

## 3️⃣ Configure ChirpStack

1. Open ChirpStack web interface: `http://localhost:8080`
2. Create/select an Application
3. Add new device:
   - **Device EUI**: `0bbef9f59cc6986a`
   - **Activation**: OTAA
   - **Application Key**: `d8341a42c8894b3bb82d0f721a0fcdbc`

See `chirpstack_setup_guide.md` for detailed steps.

## 4️⃣ Update Config

Edit `config.py`:

```python
DEVICE_EUI = "0bbef9f59cc6986a"
APP_KEY = "d8341a42c8894b3bb82d0f721a0fcdbc"
APP_EUI = "YOUR_APP_EUI_FROM_CHIRPSTACK"  # ← Update this!
FREQUENCY = 868.1  # or 915.0 for US
```

## 5️⃣ Test Hardware

```bash
sudo python3 test_connection.py
```

Expected output:
```
✓ SX1276 detected!
✓ All tests passed!
```

## 6️⃣ Run Application

```bash
sudo python3 main.py
```

Expected output:
```
=== Starting OTAA Join ===
Join Accept received!
=== Join Successful! ===
Data sent successfully!
```

## 7️⃣ View Data in ChirpStack

1. Go to Applications → Your Application → Your Device
2. Click **LoRaWAN frames** tab
3. See Join Request, Join Accept, and Uplink frames
4. Click **Device data** tab to see decoded messages

## 🎉 Success!

You should now see data like:
```
"Hello from RPi! Count: 0"
"Hello from RPi! Count: 1"
...
```

## 🔧 Troubleshooting

**No Join Accept?**
- Check gateway is online in ChirpStack
- Verify device credentials match
- Ensure frequency matches your region

**Hardware errors?**
- Run `test_connection.py` first
- Check all wiring connections
- Verify SPI is enabled: `lsmod | grep spi`
- Must run with `sudo`

**More help?**
- See `README.md` for detailed documentation
- See `chirpstack_setup_guide.md` for ChirpStack setup
- Check gateway logs: `sudo journalctl -u chirpstack-gateway-bridge -f`

---

**Happy LoRa-ing! 📡**
