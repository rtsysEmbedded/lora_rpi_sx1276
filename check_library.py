#!/usr/bin/env python3
"""
Check which LoRa library is installed and its compatibility
"""

import sys

print("=" * 60)
print("LoRa Library Compatibility Check")
print("=" * 60)
print()

# Try to import SX127x
try:
    from SX127x.LoRa import LoRa
    from SX127x.board_config import BOARD
    print("✓ SX127x module found")
    
    # Check if it has the expected attributes
    if hasattr(LoRa, 'MODE'):
        print("✓ LoRa.MODE attribute exists")
        print("✓ This is pySX127x (COMPATIBLE)")
        print()
        print("Your library is correct!")
        print("You can run: sudo python3 main.py")
        sys.exit(0)
    else:
        print("✗ LoRa.MODE attribute missing")
        print("✗ This is pyLoRa (INCOMPATIBLE)")
        print()
        print("You have the wrong library installed.")
        print()
        print("Fix it by running:")
        print("  sudo bash fix_library.sh")
        sys.exit(1)
        
except ImportError as e:
    print(f"✗ SX127x module not found: {e}")
    print()
    print("Install pySX127x:")
    print("  sudo bash fix_library.sh")
    sys.exit(1)
