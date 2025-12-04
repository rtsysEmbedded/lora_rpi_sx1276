#!/usr/bin/env python3
"""
Basic LoRa Test Script - Tests SPI communication with SX1276
Run this first to verify your hardware setup is correct
"""

import RPi.GPIO as GPIO
import spidev
import time

# Pin configuration
CS_PIN = 8      # Chip Select
RESET_PIN = 25  # Reset

def setup_gpio():
    """Setup GPIO pins"""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(CS_PIN, GPIO.OUT)
    GPIO.setup(RESET_PIN, GPIO.OUT)
    GPIO.output(CS_PIN, GPIO.HIGH)
    GPIO.output(RESET_PIN, GPIO.HIGH)

def reset_module():
    """Reset the SX1276 module"""
    print("Resetting module...")
    GPIO.output(RESET_PIN, GPIO.LOW)
    time.sleep(0.01)
    GPIO.output(RESET_PIN, GPIO.HIGH)
    time.sleep(0.01)

def read_register(spi, reg_addr):
    """Read a register from SX1276"""
    GPIO.output(CS_PIN, GPIO.LOW)
    # Read command: MSB=0, address
    cmd = [reg_addr & 0x7F, 0x00]
    response = spi.xfer2(cmd)
    GPIO.output(CS_PIN, GPIO.HIGH)
    return response[1]

def write_register(spi, reg_addr, value):
    """Write to a register on SX1276"""
    GPIO.output(CS_PIN, GPIO.LOW)
    # Write command: MSB=1, address, value
    cmd = [(reg_addr | 0x80), value]
    spi.xfer2(cmd)
    GPIO.output(CS_PIN, GPIO.HIGH)

def test_spi_connection():
    """Test SPI connection by reading SX1276 version register"""
    print("Testing SPI connection...")
    
    try:
        # Open SPI bus
        spi = spidev.SpiDev()
        spi.open(0, 0)  # Bus 0, Device 0
        spi.max_speed_hz = 10000000  # 10 MHz
        spi.mode = 0
        
        # Reset module
        reset_module()
        time.sleep(0.1)
        
        # Read version register (RegVersion = 0x42)
        # Should return 0x12 for SX1276
        version = read_register(spi, 0x42)
        
        print(f"Version register (0x42): 0x{version:02X}")
        
        if version == 0x12:
            print("✓ SX1276 detected successfully!")
            return True, spi
        else:
            print(f"⚠ Unexpected version: 0x{version:02X} (expected 0x12)")
            print("  Module might be different or not responding correctly")
            return False, spi
            
    except Exception as e:
        print(f"✗ SPI connection failed: {e}")
        return False, None

def test_basic_registers(spi):
    """Test reading some basic registers"""
    print("\nTesting basic registers...")
    
    registers_to_test = {
        0x01: "RegFrfMsb",
        0x09: "RegPaConfig",
        0x0E: "RegFifoAddrPtr",
        0x1D: "RegModemConfig1",
    }
    
    for addr, name in registers_to_test.items():
        value = read_register(spi, addr)
        print(f"  {name} (0x{addr:02X}): 0x{value:02X}")

def main():
    """Main test function"""
    print("=" * 50)
    print("SX1276 LoRa Module Basic Test")
    print("=" * 50)
    print()
    
    try:
        # Setup GPIO
        setup_gpio()
        print("GPIO configured")
        
        # Test SPI
        success, spi = test_spi_connection()
        
        if success and spi:
            test_basic_registers(spi)
            print("\n✓ Basic hardware test passed!")
            print("\nNext steps:")
            print("1. Verify your wiring matches the configuration")
            print("2. Run lora_p2p_receiver.py on one device")
            print("3. Run lora_p2p_sender.py on another device")
        else:
            print("\n✗ Hardware test failed")
            print("\nTroubleshooting:")
            print("1. Check SPI is enabled: sudo raspi-config")
            print("2. Verify wiring connections")
            print("3. Check power supply (3.3V)")
            print("4. Verify CS pin is correct")
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        GPIO.cleanup()
        if 'spi' in locals() and spi:
            spi.close()
        print("\nCleanup complete")

if __name__ == "__main__":
    main()
