#!/usr/bin/env python3
"""
LoRa P2P Communication Test for SX1276 / Helium Modems
Test communication between two SX1276 LoRa modules or Helium LoRa modems in P2P mode

Supported Hardware:
- SX1276/SX1278 LoRa modules (generic)
- Helium LoRa modems (RAK, LongAP, and other Helium-compatible devices)
"""

import time
import spidev
import RPi.GPIO as GPIO
from enum import IntEnum

# GPIO Pin Definitions (adjust based on your wiring)
# Default: Helium modem pin configuration
# NSS: BCM GPIO 6 (Wiring Pi 22)
# RESET: BCM GPIO 5 (Wiring Pi 21)
# DIO0: BCM GPIO 19 (Wiring Pi 24) - optional
NSS_PIN = 6   # Chip Select (CS) - BCM GPIO 6
RST_PIN = 5   # Reset pin - BCM GPIO 5
DIO0_PIN = 19 # DIO0 interrupt pin (optional) - BCM GPIO 19

# LoRa Registers
class Registers(IntEnum):
    REG_FIFO = 0x00
    REG_OP_MODE = 0x01
    REG_FRF_MSB = 0x06
    REG_FRF_MID = 0x07
    REG_FRF_LSB = 0x08
    REG_PA_CONFIG = 0x09
    REG_LNA = 0x0C
    REG_FIFO_ADDR_PTR = 0x0D
    REG_FIFO_TX_BASE_ADDR = 0x0E
    REG_FIFO_RX_BASE_ADDR = 0x0F
    REG_FIFO_RX_CURRENT_ADDR = 0x10
    REG_IRQ_FLAGS = 0x12
    REG_RX_NB_BYTES = 0x13
    REG_PKT_RSSI_VALUE = 0x1A
    REG_PKT_SNR_VALUE = 0x1B
    REG_MODEM_CONFIG_1 = 0x1D
    REG_MODEM_CONFIG_2 = 0x1E
    REG_MODEM_CONFIG_3 = 0x26
    REG_PREAMBLE_MSB = 0x20
    REG_PREAMBLE_LSB = 0x21
    REG_PAYLOAD_LENGTH = 0x22
    REG_MODEM_CONFIG_4 = 0x26
    REG_DETECTION_OPTIMIZE = 0x31
    REG_DETECTION_THRESHOLD = 0x37
    REG_SYNC_WORD = 0x39
    REG_DIO_MAPPING_1 = 0x40
    REG_VERSION = 0x42

# LoRa Modes
class Mode(IntEnum):
    SLEEP = 0x00
    STDBY = 0x01
    TX = 0x03
    RX_CONTINUOUS = 0x05
    RX_SINGLE = 0x06

class SX1276:
    def __init__(self, spi_bus=0, spi_device=0, nss_pin=NSS_PIN, rst_pin=RST_PIN, debug=False):
        self.nss_pin = nss_pin
        self.rst_pin = rst_pin
        self.debug = debug
        
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.nss_pin, GPIO.OUT)
        GPIO.setup(self.rst_pin, GPIO.OUT)
        
        # Ensure NSS is high (inactive) initially
        GPIO.output(self.nss_pin, GPIO.HIGH)
        
        # Setup SPI
        try:
            self.spi = spidev.SpiDev()
            self.spi.open(spi_bus, spi_device)
            self.spi.max_speed_hz = 1000000  # Start with 1MHz for reliability
            self.spi.mode = 0b00
            if self.debug:
                print(f"SPI opened: bus={spi_bus}, device={spi_device}")
        except Exception as e:
            print(f"ERROR: Failed to open SPI: {e}")
            print("Check if SPI is enabled: sudo raspi-config -> Interface Options -> SPI")
            raise
        
        # Initialize
        self.reset()
        self.init()
    
    def reset(self):
        """Reset the SX1276 module"""
        if self.debug:
            print(f"Resetting module (RST pin: GPIO {self.rst_pin})...")
        GPIO.output(self.rst_pin, GPIO.LOW)
        time.sleep(0.01)
        GPIO.output(self.rst_pin, GPIO.HIGH)
        time.sleep(0.05)  # Give more time after reset
    
    def write_register(self, address, value):
        """Write a value to a register"""
        GPIO.output(self.nss_pin, GPIO.LOW)
        time.sleep(0.0001)  # Small delay for CS setup
        try:
            self.spi.xfer2([address | 0x80, value])
        finally:
            GPIO.output(self.nss_pin, GPIO.HIGH)
            time.sleep(0.0001)  # Small delay for CS hold
    
    def read_register(self, address):
        """Read a value from a register"""
        GPIO.output(self.nss_pin, GPIO.LOW)
        time.sleep(0.0001)  # Small delay for CS setup
        try:
            response = self.spi.xfer2([address & 0x7F, 0x00])
            return response[1]
        finally:
            GPIO.output(self.nss_pin, GPIO.HIGH)
            time.sleep(0.0001)  # Small delay for CS hold
    
    def init(self):
        """Initialize LoRa module with P2P settings"""
        # First, try to read version multiple times to verify SPI communication
        versions = []
        for i in range(3):
            version = self.read_register(Registers.REG_VERSION)
            versions.append(version)
            time.sleep(0.01)
        
        if all(v == 0x00 for v in versions):
            print("\n⚠ WARNING: All registers reading 0x00 - SPI communication issue detected!")
            print("\nTroubleshooting steps:")
            print("1. Verify SPI is enabled: lsmod | grep spi")
            print("2. Check SPI device exists: ls -l /dev/spi*")
            print("3. Verify NSS/CS pin connection (GPIO 8 by default)")
            print("4. Check MOSI, MISO, SCK connections")
            print("5. Verify power supply (3.3V)")
            print("6. Try different SPI device: python3 lora_p2p_test.py test --spi-device 1")
            print("7. Check if module needs different reset sequence")
            print("\nTrying alternative initialization...")
            
            # Try longer reset
            GPIO.output(self.rst_pin, GPIO.LOW)
            time.sleep(0.1)
            GPIO.output(self.rst_pin, GPIO.HIGH)
            time.sleep(0.1)
            
            # Try reading version again
            version = self.read_register(Registers.REG_VERSION)
            if version == 0x00:
                print("\n✗ Still reading 0x00. SPI communication is not working.")
                print("This usually means:")
                print("  - Wrong CS/NSS pin")
                print("  - SPI not enabled")
                print("  - Wrong SPI bus/device")
                print("  - Module not powered")
                print("  - Wiring issue")
                raise Exception("SPI communication failed - cannot read module registers")
        
        version = versions[0]
        print(f"SX1276 detected. Version: 0x{version:02X}")
        
        if version != 0x12:
            if version == 0x00:
                print("  ✗ Version is 0x00 - SPI communication issue!")
            elif version in [0x11, 0x13]:
                print(f"  ⚠ Version {version:02X} - may still work (some clones use this)")
            else:
                print(f"  ⚠ Unexpected version (expected 0x12 for SX1276/SX1278)")
        
        # Set sleep mode
        self.write_register(Registers.REG_OP_MODE, Mode.SLEEP | 0x80)  # LoRa mode
        time.sleep(0.01)
        
        # Set to standby mode
        self.write_register(Registers.REG_OP_MODE, Mode.STDBY | 0x80)
        time.sleep(0.01)
        
        # Set frequency to 868.1 MHz (adjust for your region)
        # Frequency = (Freq * 2^19) / 32e6
        freq = 868100000  # 868.1 MHz
        freq_reg = int(freq * 524288 / 32000000)
        self.write_register(Registers.REG_FRF_MSB, (freq_reg >> 16) & 0xFF)
        self.write_register(Registers.REG_FRF_MID, (freq_reg >> 8) & 0xFF)
        self.write_register(Registers.REG_FRF_LSB, freq_reg & 0xFF)
        
        # Modem Config 1: BW=125kHz, CR=4/5, Explicit header
        self.write_register(Registers.REG_MODEM_CONFIG_1, 0x72)
        
        # Modem Config 2: SF=7, CRC enabled
        self.write_register(Registers.REG_MODEM_CONFIG_2, 0x74)
        
        # Modem Config 3: Low Data Rate Optimize OFF, AGC ON
        self.write_register(Registers.REG_MODEM_CONFIG_3, 0x04)
        
        # Preamble length (8 bytes default)
        self.write_register(Registers.REG_PREAMBLE_MSB, 0x00)
        self.write_register(Registers.REG_PREAMBLE_LSB, 0x08)
        
        # Sync word (0x12 default for LoRaWAN, use 0x34 for P2P)
        self.write_register(Registers.REG_SYNC_WORD, 0x34)
        
        # PA Config: PA_BOOST pin, Max power
        self.write_register(Registers.REG_PA_CONFIG, 0xFF)
        
        # LNA: Max gain
        self.write_register(Registers.REG_LNA, 0x23)
        
        # Set FIFO base addresses
        self.write_register(Registers.REG_FIFO_TX_BASE_ADDR, 0x00)
        self.write_register(Registers.REG_FIFO_RX_BASE_ADDR, 0x00)
        
        print("LoRa module initialized with P2P settings:")
        print("  Frequency: 868.1 MHz")
        print("  Spreading Factor: 7")
        print("  Bandwidth: 125 kHz")
        print("  Coding Rate: 4/5")
        print("  Preamble: 8 bytes")
    
    def set_mode(self, mode):
        """Set the operation mode"""
        self.write_register(Registers.REG_OP_MODE, mode | 0x80)
    
    def send_packet(self, data):
        """Send a packet"""
        # Set to standby
        self.set_mode(Mode.STDBY)
        time.sleep(0.01)
        
        # Clear FIFO
        self.write_register(Registers.REG_FIFO_ADDR_PTR, 0x00)
        
        # Write data to FIFO
        for i, byte in enumerate(data):
            self.write_register(Registers.REG_FIFO, byte)
        
        # Set payload length
        self.write_register(Registers.REG_PAYLOAD_LENGTH, len(data))
        
        # Set to TX mode
        self.set_mode(Mode.TX)
        
        # Wait for TX done
        while (self.read_register(Registers.REG_IRQ_FLAGS) & 0x08) == 0:
            time.sleep(0.01)
        
        # Clear TX done flag
        self.write_register(Registers.REG_IRQ_FLAGS, 0xFF)
        
        # Return to standby
        self.set_mode(Mode.STDBY)
        
        return True
    
    def receive_packet(self, timeout=5):
        """Receive a packet with timeout"""
        # Set to standby
        self.set_mode(Mode.STDBY)
        time.sleep(0.01)
        
        # Clear FIFO
        self.write_register(Registers.REG_FIFO_ADDR_PTR, 0x00)
        
        # Set to RX continuous mode
        self.set_mode(Mode.RX_CONTINUOUS)
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            # Check if packet received
            irq_flags = self.read_register(Registers.REG_IRQ_FLAGS)
            
            if irq_flags & 0x40:  # RxDone
                # Clear flags
                self.write_register(Registers.REG_IRQ_FLAGS, 0xFF)
                
                # Read packet
                rx_nb_bytes = self.read_register(Registers.REG_RX_NB_BYTES)
                fifo_addr = self.read_register(Registers.REG_FIFO_RX_CURRENT_ADDR)
                self.write_register(Registers.REG_FIFO_ADDR_PTR, fifo_addr)
                
                data = []
                for _ in range(rx_nb_bytes):
                    data.append(self.read_register(Registers.REG_FIFO))
                
                # Get RSSI and SNR
                rssi = self.read_register(Registers.REG_PKT_RSSI_VALUE) - 164
                snr = (self.read_register(Registers.REG_PKT_SNR_VALUE)) / 4
                
                # Return to standby
                self.set_mode(Mode.STDBY)
                
                return bytes(data), rssi, snr
            
            time.sleep(0.01)
        
        # Timeout - return to standby
        self.set_mode(Mode.STDBY)
        return None, None, None
    
    def close(self):
        """Clean up resources"""
        self.set_mode(Mode.SLEEP)
        self.spi.close()
        GPIO.cleanup()


def transmitter_mode(spi_bus=0, spi_device=0, nss_pin=NSS_PIN, rst_pin=RST_PIN):
    """Run as transmitter"""
    print("\n=== TRANSMITTER MODE ===")
    print("Sending messages every 5 seconds...")
    print("Press Ctrl+C to stop\n")
    
    lora = SX1276(spi_bus=spi_bus, spi_device=spi_device, nss_pin=nss_pin, rst_pin=rst_pin)
    
    try:
        counter = 0
        while True:
            message = f"Hello from TX! Message #{counter}"
            data = message.encode('utf-8')
            
            print(f"Sending: {message}")
            lora.send_packet(data)
            print("  ✓ Sent successfully\n")
            
            counter += 1
            time.sleep(5)
    
    except KeyboardInterrupt:
        print("\nStopping transmitter...")
    finally:
        lora.close()


def receiver_mode(spi_bus=0, spi_device=0, nss_pin=NSS_PIN, rst_pin=RST_PIN):
    """Run as receiver"""
    print("\n=== RECEIVER MODE ===")
    print("Listening for messages...")
    print("Press Ctrl+C to stop\n")
    
    lora = SX1276(spi_bus=spi_bus, spi_device=spi_device, nss_pin=nss_pin, rst_pin=rst_pin)
    
    try:
        while True:
            data, rssi, snr = lora.receive_packet(timeout=10)
            
            if data:
                message = data.decode('utf-8', errors='ignore')
                print(f"Received: {message}")
                print(f"  RSSI: {rssi} dBm")
                print(f"  SNR: {snr} dB\n")
            else:
                print("  (No message received, still listening...)\n")
    
    except KeyboardInterrupt:
        print("\nStopping receiver...")
    finally:
        lora.close()


def test_mode(spi_bus=0, spi_device=0, nss_pin=NSS_PIN, rst_pin=RST_PIN):
    """Test mode - verify module detection and configuration"""
    print("\n=== TEST MODE ===")
    print("Testing Helium LoRa modem detection and configuration...\n")
    
    print(f"Configuration:")
    print(f"  SPI Bus: {spi_bus}")
    print(f"  SPI Device: {spi_device}")
    print(f"  NSS/CS Pin: GPIO {nss_pin}")
    print(f"  RST Pin: GPIO {rst_pin}")
    print()
    
    # First, check if SPI is available
    try:
        import os
        if not os.path.exists(f'/dev/spidev{spi_bus}.{spi_device}'):
            print(f"✗ ERROR: SPI device /dev/spidev{spi_bus}.{spi_device} not found!")
            print("\nEnable SPI:")
            print("  sudo raspi-config")
            print("  Interface Options -> SPI -> Enable")
            print("  sudo reboot")
            return
        else:
            print(f"✓ SPI device /dev/spidev{spi_bus}.{spi_device} found")
    except Exception as e:
        print(f"⚠ Could not check SPI device: {e}")
    
    print()
    
    try:
        lora = SX1276(spi_bus=spi_bus, spi_device=spi_device, nss_pin=nss_pin, rst_pin=rst_pin, debug=True)
        
        # Read and display key registers
        print("Module Information:")
        print("-" * 50)
        
        version = lora.read_register(Registers.REG_VERSION)
        print(f"Version Register: 0x{version:02X}")
        if version == 0x12:
            print("  ✓ SX1276/SX1278 detected")
        elif version == 0x11:
            print("  ⚠ Version 0x11 (may be compatible)")
        elif version == 0x13:
            print("  ⚠ Version 0x13 (may be compatible)")
        else:
            print(f"  ⚠ Unexpected version (expected 0x12)")
        
        # Read operation mode
        op_mode = lora.read_register(Registers.REG_OP_MODE)
        print(f"Operation Mode: 0x{op_mode:02X}")
        if op_mode & 0x80:
            print("  ✓ LoRa mode enabled")
        else:
            print("  ✗ Not in LoRa mode!")
        
        # Read frequency
        frf_msb = lora.read_register(Registers.REG_FRF_MSB)
        frf_mid = lora.read_register(Registers.REG_FRF_MID)
        frf_lsb = lora.read_register(Registers.REG_FRF_LSB)
        freq_reg = (frf_msb << 16) | (frf_mid << 8) | frf_lsb
        freq = (freq_reg * 32000000) / 524288
        print(f"Frequency: {freq/1000000:.3f} MHz")
        
        # Read modem config
        modem_cfg1 = lora.read_register(Registers.REG_MODEM_CONFIG_1)
        modem_cfg2 = lora.read_register(Registers.REG_MODEM_CONFIG_2)
        modem_cfg3 = lora.read_register(Registers.REG_MODEM_CONFIG_3)
        
        # Decode bandwidth
        bw = (modem_cfg1 >> 4) & 0x0F
        bw_values = {
            0: "7.8 kHz", 1: "10.4 kHz", 2: "15.6 kHz", 3: "20.8 kHz",
            4: "31.25 kHz", 5: "41.7 kHz", 6: "62.5 kHz", 7: "125 kHz",
            8: "250 kHz", 9: "500 kHz"
        }
        print(f"Bandwidth: {bw_values.get(bw, 'Unknown')}")
        
        # Decode spreading factor
        sf = (modem_cfg2 >> 4) & 0x0F
        print(f"Spreading Factor: SF{sf}")
        
        # Decode coding rate
        cr = ((modem_cfg1 >> 1) & 0x07) + 5
        print(f"Coding Rate: 4/{cr}")
        
        # Read sync word
        sync_word = lora.read_register(Registers.REG_SYNC_WORD)
        print(f"Sync Word: 0x{sync_word:02X}")
        if sync_word == 0x34:
            print("  ✓ P2P mode (sync word 0x34)")
        elif sync_word == 0x12:
            print("  ⚠ LoRaWAN mode (sync word 0x12) - should be 0x34 for P2P")
        else:
            print(f"  ⚠ Custom sync word")
        
        # Read PA config
        pa_config = lora.read_register(Registers.REG_PA_CONFIG)
        print(f"PA Config: 0x{pa_config:02X}")
        
        print("\n" + "-" * 50)
        print("Test completed!")
        print("\nIf module is detected correctly, you can now:")
        print("  - Run 'python3 lora_p2p_test.py rx' to receive")
        print("  - Run 'python3 lora_p2p_test.py tx' to transmit")
        
        lora.close()
        
    except Exception as e:
        print(f"\n✗ Error during test: {e}")
        print("\nTroubleshooting:")
        print("  1. Check SPI connections (MOSI, MISO, SCK, CS)")
        print("  2. Verify power supply (3.3V)")
        print("  3. Check if SPI is enabled: lsmod | grep spi")
        print("  4. Verify GPIO pin numbers match your wiring")
        print("  5. Try resetting the module (power cycle)")
        raise


if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='LoRa P2P Test for SX1276 / Helium Modems')
    parser.add_argument('mode', nargs='?', choices=['tx', 'rx', 'test', 'transmit', 'receive'],
                       help='Operation mode: tx (transmit), rx (receive), or test')
    parser.add_argument('--spi-bus', type=int, default=0, help='SPI bus number (default: 0)')
    parser.add_argument('--spi-device', type=int, default=0, help='SPI device number (default: 0)')
    parser.add_argument('--nss-pin', type=int, default=NSS_PIN, help=f'NSS/CS GPIO pin (default: {NSS_PIN})')
    parser.add_argument('--rst-pin', type=int, default=RST_PIN, help=f'RST GPIO pin (default: {RST_PIN})')
    
    args = parser.parse_args()
    
    if args.mode:
        mode = args.mode.lower()
        if mode == "tx" or mode == "transmit":
            transmitter_mode(spi_bus=args.spi_bus, spi_device=args.spi_device,
                           nss_pin=args.nss_pin, rst_pin=args.rst_pin)
        elif mode == "rx" or mode == "receive":
            receiver_mode(spi_bus=args.spi_bus, spi_device=args.spi_device,
                         nss_pin=args.nss_pin, rst_pin=args.rst_pin)
        elif mode == "test":
            test_mode(spi_bus=args.spi_bus, spi_device=args.spi_device, 
                     nss_pin=args.nss_pin, rst_pin=args.rst_pin)
    else:
        print("LoRa P2P Test for SX1276 / Helium Modems")
        print("\nUsage: python3 lora_p2p_test.py [tx|rx|test] [options]")
        print("\nModes:")
        print("  tx    - Transmitter mode (sends messages)")
        print("  rx    - Receiver mode (listens for messages)")
        print("  test  - Test mode (verify module detection)")
        print("\nOptions:")
        print("  --spi-bus N      SPI bus number (default: 0)")
        print("  --spi-device N   SPI device number (default: 0)")
        print(f"  --nss-pin N      NSS/CS GPIO pin (default: {NSS_PIN})")
        print(f"  --rst-pin N      RST GPIO pin (default: {RST_PIN})")
        print("\nExamples:")
        print("  python3 lora_p2p_test.py test")
        print("  python3 lora_p2p_test.py test --spi-device 1")
        print("  python3 lora_p2p_test.py test --nss-pin 7")
        print("  python3 lora_p2p_test.py rx")
        print("  python3 lora_p2p_test.py tx")
        print("\nFor Helium modems, first run:")
        print("  python3 lora_p2p_test.py test")
