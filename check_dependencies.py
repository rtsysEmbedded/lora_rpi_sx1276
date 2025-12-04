#!/usr/bin/env python3
"""
Check if all required dependencies are installed
Run this to diagnose installation issues
"""

import sys

print("=" * 60)
print("Dependency Check for LoRaWAN Client")
print("=" * 60)
print()

# Check Python version
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print()

# Required packages
packages = [
    ("RPi.GPIO", "RPi.GPIO", "GPIO control for Raspberry Pi"),
    ("spidev", "spidev", "SPI interface"),
    ("pycryptodome", "Crypto", "Cryptography for LoRaWAN"),
    ("pySX127x", "SX127x.LoRa", "SX127x LoRa driver"),
]

print("Checking packages:")
print("-" * 60)

all_ok = True
missing = []

for package_name, import_name, description in packages:
    try:
        module = __import__(import_name)
        
        # Try to get version if available
        version = "installed"
        if hasattr(module, "__version__"):
            version = module.__version__
        
        print(f"✓ {package_name:15} - OK ({version})")
        print(f"  └─ {description}")
        
    except ImportError as e:
        print(f"✗ {package_name:15} - MISSING")
        print(f"  └─ {description}")
        print(f"  └─ Error: {e}")
        all_ok = False
        missing.append(package_name)
    
    print()

print("=" * 60)

if all_ok:
    print("✓ All dependencies are installed!")
    print()
    print("You can now run:")
    print("  sudo python3 test_connection.py")
    print("  sudo python3 main.py")
else:
    print("✗ Some dependencies are missing!")
    print()
    print("Missing packages:", ", ".join(missing))
    print()
    print("Installation instructions:")
    print()
    
    for pkg in missing:
        if pkg == "RPi.GPIO":
            print(f"  pip3 install RPi.GPIO")
        elif pkg == "spidev":
            print(f"  pip3 install spidev")
        elif pkg == "pycryptodome":
            print(f"  pip3 install pycryptodome")
        elif pkg == "pySX127x":
            print(f"  # Install from GitHub:")
            print(f"  cd /tmp")
            print(f"  git clone https://github.com/rpsreal/pySX127x.git")
            print(f"  cd pySX127x")
            print(f"  sudo python3 setup.py install")
    
    print()
    print("Or run the automated installer:")
    print("  sudo bash install.sh")
    print()
    print("See INSTALL_INSTRUCTIONS.md for detailed help")

print("=" * 60)

sys.exit(0 if all_ok else 1)
