#!/usr/bin/env python3
"""
Test script to verify SX1276 connection and basic LoRa functionality
Run this first to ensure your hardware is properly connected
"""

import time
import sys
import os

# Add current directory to path to use local board_config
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from SX127x.LoRa import LoRa
import board_config
BOARD = board_config.BOARD
import config


def test_spi_connection():
    """Test SPI connection to SX1276"""
    print("=" * 60)
    print("Testing SX1276 Connection")
    print("=" * 60)
    
    try:
        # Initialize board
        BOARD.setup()
        print("✓ GPIO and SPI initialized")
        
        # Create LoRa instance
        lora = LoRa(verbose=False)
        print("✓ LoRa instance created")
        
        # Read version register (should be 0x12 for SX1276)
        version = lora.get_version()
        print(f"✓ Chip version: 0x{version:02x}")
        
        if version == 0x12:
            print("✓ SX1276 detected!")
        elif version == 0x11:
            print("⚠ SX1272 detected (not SX1276)")
        else:
            print(f"⚠ Unknown chip version: 0x{version:02x}")
            print("  Expected 0x12 for SX1276")
        
        # Test basic configuration
        lora.set_mode(LoRa.MODE.STDBY)
        print("✓ Set to standby mode")
        
        lora.set_freq(config.FREQUENCY)
        freq = lora.get_freq()
        print(f"✓ Frequency set to: {freq} MHz")
        
        lora.set_spreading_factor(7)
        print("✓ Spreading factor set to: 7")
        
        lora.set_bw(LoRa.BW.BW125)
        print("✓ Bandwidth set to: 125 kHz")
        
        # Cleanup
        lora.set_mode(LoRa.MODE.SLEEP)
        BOARD.teardown()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed! Hardware is working correctly.")
        print("=" * 60)
        print("\nYou can now run: sudo python3 main.py")
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check wiring connections")
        print("2. Ensure SPI is enabled: sudo raspi-config -> Interface Options -> SPI")
        print("3. Verify 3.3V power supply to SX1276")
        print("4. Check that all Python packages are installed")
        
        try:
            BOARD.teardown()
        except:
            pass
        
        return False


def test_transmit_receive():
    """Test transmit and receive (requires 2 modules)"""
    print("\n" + "=" * 60)
    print("Basic LoRa Transmit Test")
    print("=" * 60)
    
    try:
        BOARD.setup()
        lora = LoRa(verbose=False)
        
        # Configure
        lora.set_mode(LoRa.MODE.STDBY)
        lora.set_freq(config.FREQUENCY)
        lora.set_spreading_factor(7)
        lora.set_bw(LoRa.BW.BW125)
        lora.set_coding_rate(LoRa.CODING_RATE.CR4_5)
        lora.set_sync_word(0x12)  # Test sync word
        
        # Transmit test message
        test_msg = "Test123"
        print(f"Transmitting: {test_msg}")
        
        lora.set_mode(LoRa.MODE.STDBY)
        lora.set_payload(list(test_msg.encode()))
        lora.set_mode(LoRa.MODE.TX)
        
        # Wait for TX done
        timeout = 5
        start = time.time()
        while (time.time() - start < timeout):
            if lora.get_irq_flags()['tx_done']:
                print("✓ Transmission complete!")
                break
            time.sleep(0.01)
        
        lora.clear_irq_flags(TxDone=1)
        lora.set_mode(LoRa.MODE.SLEEP)
        BOARD.teardown()
        
        print("✓ Transmit test completed")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        try:
            BOARD.teardown()
        except:
            pass
        return False


if __name__ == "__main__":
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║         SX1276 Hardware Test Suite                        ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    
    # Check if running as root
    import os
    if os.geteuid() != 0:
        print("⚠ Warning: This script should be run as root (sudo)")
        print("  Some GPIO operations may fail without root privileges\n")
    
    # Run tests
    success = True
    
    if not test_spi_connection():
        success = False
    
    if success:
        test_transmit_receive()
    
    if success:
        print("\n✓ Hardware is ready for LoRaWAN!")
    else:
        print("\n✗ Please fix the issues above before proceeding")
        sys.exit(1)
