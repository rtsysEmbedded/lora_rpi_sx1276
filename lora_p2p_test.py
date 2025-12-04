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
NSS_PIN = 8   # Chip Select (CS)
RST_PIN = 25  # Reset pin
DIO0_PIN = 2  # DIO0 interrupt pin (optional)

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
    def __init__(self, spi_bus=0, spi_device=0, nss_pin=NSS_PIN, rst_pin=RST_PIN):
        self.nss_pin = nss_pin
        self.rst_pin = rst_pin
        
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.nss_pin, GPIO.OUT)
        GPIO.setup(self.rst_pin, GPIO.OUT)
        
        # Setup SPI
        self.spi = spidev.SpiDev()
        self.spi.open(spi_bus, spi_device)
        self.spi.max_speed_hz = 5000000  # 5MHz
        self.spi.mode = 0b00
        
        # Initialize
        self.reset()
        self.init()
    
    def reset(self):
        """Reset the SX1276 module"""
        GPIO.output(self.rst_pin, GPIO.LOW)
        time.sleep(0.01)
        GPIO.output(self.rst_pin, GPIO.HIGH)
        time.sleep(0.01)
    
    def write_register(self, address, value):
        """Write a value to a register"""
        GPIO.output(self.nss_pin, GPIO.LOW)
        self.spi.xfer2([address | 0x80, value])
        GPIO.output(self.nss_pin, GPIO.HIGH)
    
    def read_register(self, address):
        """Read a value from a register"""
        GPIO.output(self.nss_pin, GPIO.LOW)
        response = self.spi.xfer2([address & 0x7F, 0x00])
        GPIO.output(self.nss_pin, GPIO.HIGH)
        return response[1]
    
    def init(self):
        """Initialize LoRa module with P2P settings"""
        # Check version
        version = self.read_register(Registers.REG_VERSION)
        print(f"SX1276 detected. Version: 0x{version:02X}")
        
        if version != 0x12:
            print("Warning: Version mismatch. Expected 0x12")
        
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


def transmitter_mode():
    """Run as transmitter"""
    print("\n=== TRANSMITTER MODE ===")
    print("Sending messages every 5 seconds...")
    print("Press Ctrl+C to stop\n")
    
    lora = SX1276()
    
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


def receiver_mode():
    """Run as receiver"""
    print("\n=== RECEIVER MODE ===")
    print("Listening for messages...")
    print("Press Ctrl+C to stop\n")
    
    lora = SX1276()
    
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


def test_mode():
    """Test mode - verify module detection and configuration"""
    print("\n=== TEST MODE ===")
    print("Testing Helium LoRa modem detection and configuration...\n")
    
    try:
        lora = SX1276()
        
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
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode == "tx" or mode == "transmit":
            transmitter_mode()
        elif mode == "rx" or mode == "receive":
            receiver_mode()
        elif mode == "test":
            test_mode()
        else:
            print("Usage: python3 lora_p2p_test.py [tx|rx|test]")
            print("  tx    - Transmitter mode (sends messages)")
            print("  rx    - Receiver mode (listens for messages)")
            print("  test  - Test mode (verify module detection)")
    else:
        print("LoRa P2P Test for SX1276 / Helium Modems")
        print("\nUsage: python3 lora_p2p_test.py [tx|rx|test]")
        print("\n  tx    - Transmitter mode (sends messages)")
        print("  rx    - Receiver mode (listens for messages)")
        print("  test  - Test mode (verify module detection)")
        print("\nExample:")
        print("  Terminal 1: python3 lora_p2p_test.py rx")
        print("  Terminal 2: python3 lora_p2p_test.py tx")
        print("\nFor Helium modems, first run:")
        print("  python3 lora_p2p_test.py test")
