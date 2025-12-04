#!/usr/bin/env python3
"""
Test script for standalone SX127x driver
"""

import time
import sys
from sx127x_driver import SX127x
import config


def main():
    print("=" * 60)
    print("Testing Standalone SX127x Driver")
    print("=" * 60)
    print()
    
    try:
        # Initialize radio
        print("Initializing SX127x...")
        radio = SX127x(
            spi_bus=config.SPI_BUS,
            spi_device=config.SPI_DEVICE,
            rst_pin=config.PIN_RESET,
            dio0_pin=config.PIN_DIO0,
            nss_pin=config.PIN_NSS
        )
        print("✓ SX1276 detected and initialized")
        print()
        
        # Configure
        print("Configuring radio...")
        radio.set_frequency(config.FREQUENCY)
        print(f"✓ Frequency: {config.FREQUENCY} MHz")
        
        radio.set_spreading_factor(7)
        print("✓ Spreading Factor: 7")
        
        radio.set_bandwidth(125)
        print("✓ Bandwidth: 125 kHz")
        
        radio.set_coding_rate(5)
        print("✓ Coding Rate: 4/5")
        
        radio.set_sync_word(0x12)
        print("✓ Sync Word: 0x12")
        
        radio.set_tx_power(14)
        print("✓ TX Power: 14 dBm")
        
        print()
        
        # Test transmission
        print("Testing transmission...")
        test_data = b"Test123"
        radio.transmit(test_data)
        print(f"✓ Transmitted: {test_data}")
        
        print()
        print("=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        print()
        print("Hardware is working correctly.")
        print()
        print("You can now run:")
        print("  sudo python3 main_standalone.py")
        
        # Cleanup
        radio.cleanup()
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check wiring connections")
        print("2. Ensure SPI is enabled")
        print("3. Verify 3.3V power supply")
        print("4. Make sure you're running with sudo")
        
        import traceback
        traceback.print_exc()
        
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
