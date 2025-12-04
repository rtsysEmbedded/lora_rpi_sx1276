# Troubleshooting Guide

Common issues and solutions for the LoRaWAN client.

## Installation Issues

### ❌ "type object 'LoRa' has no attribute 'MODE'"

**Problem:** Wrong library installed (pyLoRa instead of pySX127x)

**Solution:**
```bash
sudo bash fix_library.sh
```

Or manually:
```bash
sudo pip3 uninstall -y pyLoRa
sudo rm -rf /usr/local/lib/python3.9/dist-packages/pyLoRa*
cd /tmp
git clone https://github.com/rpsreal/pySX127x.git
cd pySX127x
sudo python3 setup.py install
```

**Verify:**
```bash
python3 check_library.py
```

See `LIBRARY_FIX.md` for details.

---

### ❌ "No module named 'Crypto'"

**Problem:** pycryptodome not installed

**Solution:**
```bash
pip3 install pycryptodome
```

**Not** pycrypto (old version)!

---

### ❌ "No module named 'RPi.GPIO'" or "No module named 'spidev'"

**Problem:** Missing basic packages

**Solution:**
```bash
pip3 install RPi.GPIO spidev
# or
sudo apt-get install python3-rpi.gpio python3-spidev
```

---

### ❌ "This channel is already in use"

**Problem:** GPIO pins already configured (warning only, usually safe)

**Solution:** This warning is suppressed in the code. If it causes issues:
```bash
# Reboot to reset GPIO
sudo reboot
```

---

## Hardware Issues

### ❌ "Chip version: 0x00" or "SX1276 not detected"

**Problem:** SX1276 not connected or wrong wiring

**Checklist:**
1. Check all wire connections (see README.md wiring diagram)
2. Verify 3.3V power (NOT 5V!)
3. Check SPI is enabled: `lsmod | grep spi`
4. Try different jumper wires (poor contact common)
5. Check SX1276 module is not damaged

**Test SPI:**
```bash
ls -l /dev/spidev*
# Should show: /dev/spidev0.0 and /dev/spidev0.1
```

---

### ❌ "Permission denied" on /dev/spidev0.0

**Problem:** Not running with sudo

**Solution:**
```bash
sudo python3 test_connection.py
sudo python3 main.py
```

**Alternative:** Add user to spi group (then reboot):
```bash
sudo usermod -a -G spi,gpio $USER
```

---

### ❌ SPI not enabled

**Problem:** SPI interface not activated

**Solution:**
```bash
sudo raspi-config
# Navigate to: Interface Options → SPI → Enable
sudo reboot
```

**Verify:**
```bash
lsmod | grep spi_bcm2835
# Should show output
```

---

## LoRaWAN Issues

### ❌ "Failed to join network" or Join timeout

**Problem:** Can't connect to ChirpStack

**Checklist:**

1. **Gateway online?**
   - Check ChirpStack web interface
   - Gateways should show green/online
   - Check "Last seen" timestamp

2. **Device registered?**
   - Device exists in ChirpStack
   - DevEUI matches: `0bbef9f59cc6986a`
   - AppKey matches: `d8341a42c8894b3bb82d0f721a0fcdbc`
   - Activation mode: OTAA

3. **Correct frequency?**
   - EU868: 868.1 MHz
   - US915: 915.0 MHz
   - Must match gateway region

4. **In range?**
   - Within range of gateway (test close first)
   - Antenna connected properly
   - No metal obstructions

5. **ChirpStack logs:**
   ```bash
   # On gateway/server
   sudo journalctl -u chirpstack -f
   sudo journalctl -u chirpstack-gateway-bridge -f
   ```

---

### ❌ Join Request not appearing in ChirpStack

**Problem:** Gateway not receiving signal

**Check:**
```bash
# On gateway machine
sudo journalctl -u chirpstack-gateway-bridge -f
```

Look for packet reception.

**Possible causes:**
- Wrong frequency
- Out of range
- Antenna not connected
- Gateway not running
- Wrong region configuration

---

### ❌ Join Request appears but no Join Accept

**Problem:** ChirpStack rejecting join

**Check in ChirpStack:**
1. Device Events tab - see join attempt?
2. Device credentials match exactly?
3. Device profile region correct?

**Check logs:**
```bash
sudo journalctl -u chirpstack -f | grep -i join
```

**Common issues:**
- Wrong AppKey
- Wrong AppEUI
- Device not enabled
- Wrong device profile

---

### ❌ "MIC verification failed"

**Problem:** Security/encryption mismatch

**Solution:**
- Verify AppKey is exactly: `d8341a42c8894b3bb82d0f721a0fcdbc`
- Re-register device in ChirpStack
- Reset frame counters in ChirpStack (Device settings)

---

### ❌ Data not appearing in ChirpStack

**Problem:** Join succeeded but uplinks not received

**Check:**
1. Frame counter incrementing in code?
2. ChirpStack "LoRaWAN frames" tab shows uplinks?
3. Application integration configured?

**Gateway logs:**
```bash
sudo journalctl -u chirpstack-gateway-bridge -f
```

---

## Code/Python Issues

### ❌ "ImportError" or "ModuleNotFoundError"

**Solution:** Check dependencies
```bash
python3 check_dependencies.py
```

Install missing packages.

---

### ❌ "IndentationError" or "SyntaxError"

**Problem:** File corrupted or edited incorrectly

**Solution:** Re-download the original files or check indentation.

---

### ❌ Script hangs or freezes

**Problem:** Waiting for response that never comes

**Solution:**
- Ctrl+C to stop
- Check if issue is during join or data send
- Reduce timeout in code
- Check gateway connectivity

---

## Configuration Issues

### ❌ Need to change frequency

Edit `config.py`:
```python
# EU868
FREQUENCY = 868.1

# US915  
FREQUENCY = 915.0

# AS923
FREQUENCY = 923.2
```

Also update:
```python
# For US915
RX2_FREQUENCY = 923.3
```

---

### ❌ Need to change GPIO pins

Edit `config.py`:
```python
PIN_NSS = 8      # Your CS pin
PIN_RESET = 25   # Your RST pin  
PIN_DIO0 = 24    # Your DIO0 pin
PIN_DIO1 = 23    # Your DIO1 pin
```

Use BCM numbering!

---

### ❌ Wrong DevEUI or AppKey

Edit `config.py`:
```python
DEVICE_EUI = "your_device_eui"
APP_KEY = "your_app_key"
APP_EUI = "your_app_eui"
```

Get these from ChirpStack device page.

---

## Diagnostic Commands

### Check Python installation
```bash
python3 --version
which python3
pip3 --version
```

### Check installed packages
```bash
pip3 list | grep -E "GPIO|spi|crypto|SX127x|LoRa"
```

### Check GPIO state
```bash
gpio readall  # If gpio command installed
# or
cat /sys/kernel/debug/gpio
```

### Check SPI
```bash
ls -l /dev/spidev*
lsmod | grep spi
```

### Test SPI communication
```bash
# Install spi-tools if not available
sudo apt-get install spi-tools
# Test SPI
spi-config -d /dev/spidev0.0 -q
```

### Monitor system logs
```bash
# All system logs
sudo journalctl -f

# Python errors
sudo journalctl -f | grep -i python

# SPI errors
sudo dmesg | grep -i spi
```

---

## Still Not Working?

1. **Run all diagnostics:**
```bash
python3 check_dependencies.py
python3 check_library.py
sudo python3 test_connection.py
```

2. **Check logs carefully:**
- Look for specific error messages
- Note where it fails (join, send, receive)

3. **Start simple:**
- Test with gateway very close (1-2 meters)
- Use default settings
- Test P2P mode first (if you have 2 modules)

4. **Hardware test:**
- Swap jumper wires
- Try different GPIO pins
- Test SX1276 module on different device
- Verify with multimeter: 3.3V on VCC pin

5. **Documentation:**
- Re-read README.md
- Check ChirpStack setup guide
- Verify wiring diagram

---

## Getting Help

When asking for help, provide:
1. Output of `python3 check_dependencies.py`
2. Output of `python3 check_library.py`
3. Output of `sudo python3 test_connection.py`
4. Full error message
5. Your config.py settings (without revealing full keys)
6. ChirpStack version
7. RPi model and OS version

---

**Most common issue:** Wrong library (pyLoRa vs pySX127x)
**Fix:** `sudo bash fix_library.sh`
