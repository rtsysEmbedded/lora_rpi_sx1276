# Project Structure

This document explains the purpose of each file in the project.

## Core Application Files

### `main.py` ⭐
**Main application entry point**
- Initializes LoRaWAN client
- Performs OTAA join with ChirpStack
- Sends data periodically
- Run with: `sudo python3 main.py`

### `lorawan_client.py` 🔧
**LoRaWAN protocol implementation**
- Implements LoRaWAN 1.0.x protocol
- Handles OTAA join procedure
- Encrypts/decrypts messages
- Manages frame counters and session keys
- Core library that `main.py` uses

### `config.py` ⚙️
**Configuration file**
- Device credentials (DevEUI, AppKey, AppEUI)
- LoRa radio parameters (frequency, SF, BW)
- GPIO pin assignments
- Regional settings (EU868/US915/AS923)
- **YOU MUST EDIT THIS FILE** with your credentials!

### `board_config.py` 📟
**Hardware configuration**
- GPIO and SPI setup for Raspberry Pi
- Pin assignments for SX1276
- Hardware abstraction layer
- Required by pySX127x library

## Testing & Installation

### `test_connection.py` 🧪
**Hardware test suite**
- Verifies SX1276 connection
- Tests SPI communication
- Checks chip version
- Validates basic LoRa functionality
- **Run this first** before running main application

### `install.sh` 📦
**Automated installation script**
- Installs system dependencies
- Enables SPI if not already enabled
- Installs Python packages
- Sets up pySX127x library
- Run with: `sudo bash install.sh`

## Documentation

### `README.md` 📖
**Complete documentation**
- Detailed wiring instructions
- Installation steps
- Configuration guide
- Troubleshooting section
- Advanced usage examples
- **Read this for full setup instructions**

### `QUICKSTART.md` 🚀
**5-minute quick start guide**
- Condensed setup instructions
- Essential steps only
- Perfect for experienced users
- **Start here if you want to get running fast**

### `chirpstack_setup_guide.md` 🌐
**ChirpStack configuration guide**
- Step-by-step device registration
- Application creation
- Device profile setup
- Credential configuration
- **Use this to setup ChirpStack side**

### `PROJECT_STRUCTURE.md` 📂
**This file**
- Explains project organization
- Describes each file's purpose

## Dependency Files

### `requirements.txt` 📋
**Python package dependencies**
- Lists required Python packages
- Used by: `pip3 install -r requirements.txt`

### `.gitignore` 🚫
**Git ignore rules**
- Excludes Python cache files
- Excludes IDE files
- Excludes logs and temporary files

## File Dependencies

```
main.py
  ├─ imports → lorawan_client.py
  │             ├─ imports → board_config.py
  │             └─ imports → config.py
  └─ imports → config.py

test_connection.py
  ├─ imports → board_config.py
  └─ imports → config.py

install.sh
  └─ uses → requirements.txt
```

## Workflow

### First Time Setup
```
1. Hardware: Connect SX1276 to Raspberry Pi
2. Run: sudo bash install.sh
3. Edit: config.py (add your credentials)
4. Setup: ChirpStack (see chirpstack_setup_guide.md)
5. Test: sudo python3 test_connection.py
6. Run: sudo python3 main.py
```

### Daily Usage
```
1. Check: Gateway is online in ChirpStack
2. Run: sudo python3 main.py
3. Monitor: ChirpStack web interface
```

## Customization Points

### To change device credentials:
→ Edit `config.py` lines 4-6

### To change GPIO pins:
→ Edit `config.py` lines 21-26

### To change frequency/region:
→ Edit `config.py` line 9

### To change transmission interval:
→ Edit `main.py` line 59

### To change payload:
→ Edit `main.py` line 53

## File Sizes (Approximate)

```
lorawan_client.py    ~10 KB   (Core protocol implementation)
main.py              ~2 KB    (Application logic)
test_connection.py   ~5 KB    (Test suite)
config.py            ~1 KB    (Configuration)
board_config.py      ~2 KB    (Hardware setup)
install.sh           ~2 KB    (Installation script)
README.md            ~9 KB    (Documentation)
chirpstack_setup_guide.md ~7 KB (ChirpStack guide)
QUICKSTART.md        ~2 KB    (Quick reference)
```

## Key Concepts

### LoRaWAN OTAA Flow
```
Device (RPi)                  ChirpStack
    |                              |
    |------- Join Request -------->|
    |                              | (verifies DevEUI, AppKey)
    |<------ Join Accept ----------|
    |                              | (assigns DevAddr, session keys)
    |                              |
    |------- Data Uplink --------->|
    |                              | (decrypts, forwards to app)
    |                              |
```

### Code Architecture
```
┌─────────────────────────────────────────┐
│              main.py                     │  User Application
│  (Your business logic)                   │
└──────────────────┬──────────────────────┘
                   │
                   │ uses
                   ▼
┌─────────────────────────────────────────┐
│         lorawan_client.py               │  Protocol Layer
│  (LoRaWAN OTAA, encryption, MIC)        │
└──────────────────┬──────────────────────┘
                   │
                   │ uses
                   ▼
┌─────────────────────────────────────────┐
│        pySX127x Library                 │  Hardware Layer
│  (SX1276 register control)              │
└──────────────────┬──────────────────────┘
                   │
                   │ uses
                   ▼
┌─────────────────────────────────────────┐
│       board_config.py                   │  HAL
│  (GPIO, SPI interface)                  │
└─────────────────────────────────────────┘
```

## Debugging

### Problem: Join fails
→ Check: `test_connection.py` output
→ Check: `config.py` credentials
→ Check: ChirpStack device registration

### Problem: Hardware not detected
→ Check: Wiring connections
→ Check: SPI enabled (`lsmod | grep spi`)
→ Check: Running with `sudo`

### Problem: Data not appearing
→ Check: Join successful
→ Check: Gateway online in ChirpStack
→ Check: ChirpStack application integration

## License & Credits

- **LoRaWAN Protocol**: LoRa Alliance
- **SX1276 Driver**: Based on pySX127x
- **Crypto**: PyCryptodome library
- **Hardware**: Semtech SX1276, Raspberry Pi Foundation

---

**For support, see README.md or chirpstack_setup_guide.md**
