#!/usr/bin/env python3
"""
Standalone SX127x LoRa Driver for Raspberry Pi
No external dependencies except RPi.GPIO and spidev
"""

import time
import spidev
import RPi.GPIO as GPIO


class SX127x:
    """SX127x LoRa transceiver driver"""
    
    # SX127x Registers
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
    REG_PREAMBLE_MSB = 0x20
    REG_PREAMBLE_LSB = 0x21
    REG_PAYLOAD_LENGTH = 0x22
    REG_MODEM_CONFIG_3 = 0x26
    REG_FREQ_ERROR_MSB = 0x28
    REG_FREQ_ERROR_MID = 0x29
    REG_FREQ_ERROR_LSB = 0x2A
    REG_RSSI_WIDEBAND = 0x2C
    REG_DETECTION_OPTIMIZE = 0x31
    REG_INVERTIQ = 0x33
    REG_DETECTION_THRESHOLD = 0x37
    REG_SYNC_WORD = 0x39
    REG_INVERTIQ2 = 0x3B
    REG_DIO_MAPPING_1 = 0x40
    REG_DIO_MAPPING_2 = 0x41
    REG_VERSION = 0x42
    REG_PA_DAC = 0x4D
    
    # Modes
    MODE_SLEEP = 0x00
    MODE_STDBY = 0x01
    MODE_TX = 0x03
    MODE_RX_CONTINUOUS = 0x05
    MODE_RX_SINGLE = 0x06
    
    # PA Config
    PA_BOOST = 0x80
    
    # IRQ Flags
    IRQ_TX_DONE_MASK = 0x08
    IRQ_RX_DONE_MASK = 0x40
    IRQ_PAYLOAD_CRC_ERROR_MASK = 0x20
    
    def __init__(self, spi_bus=0, spi_device=0, rst_pin=25, dio0_pin=24, nss_pin=8):
        """Initialize SX127x driver"""
        self.rst_pin = rst_pin
        self.dio0_pin = dio0_pin
        self.nss_pin = nss_pin
        
        # Setup GPIO
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.rst_pin, GPIO.OUT)
        GPIO.setup(self.nss_pin, GPIO.OUT)
        GPIO.setup(self.dio0_pin, GPIO.IN)
        GPIO.output(self.nss_pin, GPIO.HIGH)
        
        # Setup SPI
        self.spi = spidev.SpiDev()
        self.spi.open(spi_bus, spi_device)
        self.spi.max_speed_hz = 5000000
        self.spi.mode = 0
        
        # Reset module
        self.reset()
        
        # Set LoRa mode
        self.write_register(self.REG_OP_MODE, 0x80)  # LoRa mode, sleep
        time.sleep(0.01)
        
        # Verify chip version
        version = self.read_register(self.REG_VERSION)
        if version != 0x12:
            raise RuntimeError(f"SX127x not found. Version: 0x{version:02x} (expected 0x12)")
    
    def reset(self):
        """Reset the module"""
        GPIO.output(self.rst_pin, GPIO.LOW)
        time.sleep(0.01)
        GPIO.output(self.rst_pin, GPIO.HIGH)
        time.sleep(0.01)
    
    def read_register(self, address):
        """Read single register"""
        GPIO.output(self.nss_pin, GPIO.LOW)
        response = self.spi.xfer2([address & 0x7F, 0x00])
        GPIO.output(self.nss_pin, GPIO.HIGH)
        return response[1]
    
    def write_register(self, address, value):
        """Write single register"""
        GPIO.output(self.nss_pin, GPIO.LOW)
        self.spi.xfer2([address | 0x80, value])
        GPIO.output(self.nss_pin, GPIO.HIGH)
    
    def set_mode(self, mode):
        """Set operating mode"""
        self.write_register(self.REG_OP_MODE, 0x80 | mode)  # LoRa mode | mode
        time.sleep(0.01)
    
    def set_frequency(self, freq_mhz):
        """Set frequency in MHz"""
        frf = int((freq_mhz * 1000000.0) / 61.03515625)
        self.write_register(self.REG_FRF_MSB, (frf >> 16) & 0xFF)
        self.write_register(self.REG_FRF_MID, (frf >> 8) & 0xFF)
        self.write_register(self.REG_FRF_LSB, frf & 0xFF)
    
    def set_spreading_factor(self, sf):
        """Set spreading factor (7-12)"""
        if sf < 7 or sf > 12:
            raise ValueError("SF must be 7-12")
        
        config2 = self.read_register(self.REG_MODEM_CONFIG_2)
        config2 = (config2 & 0x0F) | ((sf << 4) & 0xF0)
        self.write_register(self.REG_MODEM_CONFIG_2, config2)
        
        # SF6 optimization
        if sf == 6:
            self.write_register(self.REG_DETECTION_OPTIMIZE, 0xc5)
            self.write_register(self.REG_DETECTION_THRESHOLD, 0x0c)
        else:
            self.write_register(self.REG_DETECTION_OPTIMIZE, 0xc3)
            self.write_register(self.REG_DETECTION_THRESHOLD, 0x0a)
    
    def set_bandwidth(self, bw_khz):
        """Set bandwidth in kHz"""
        bw_map = {
            7.8: 0, 10.4: 1, 15.6: 2, 20.8: 3, 31.25: 4,
            41.7: 5, 62.5: 6, 125: 7, 250: 8, 500: 9
        }
        
        if bw_khz not in bw_map:
            raise ValueError(f"Invalid bandwidth: {bw_khz}")
        
        config1 = self.read_register(self.REG_MODEM_CONFIG_1)
        config1 = (config1 & 0x0F) | (bw_map[bw_khz] << 4)
        self.write_register(self.REG_MODEM_CONFIG_1, config1)
    
    def set_coding_rate(self, cr):
        """Set coding rate (5-8 for 4/5-4/8)"""
        if cr < 5 or cr > 8:
            raise ValueError("CR must be 5-8")
        
        config1 = self.read_register(self.REG_MODEM_CONFIG_1)
        config1 = (config1 & 0xF1) | ((cr - 4) << 1)
        self.write_register(self.REG_MODEM_CONFIG_1, config1)
    
    def set_preamble_length(self, length):
        """Set preamble length"""
        self.write_register(self.REG_PREAMBLE_MSB, (length >> 8) & 0xFF)
        self.write_register(self.REG_PREAMBLE_LSB, length & 0xFF)
    
    def set_sync_word(self, sw):
        """Set sync word"""
        self.write_register(self.REG_SYNC_WORD, sw)
    
    def set_tx_power(self, power):
        """Set TX power in dBm"""
        if power > 17:
            if power > 20:
                power = 20
            # Use PA_BOOST with PA_DAC
            self.write_register(self.REG_PA_DAC, 0x87)  # +20dBm
            self.write_register(self.REG_PA_CONFIG, self.PA_BOOST | (power - 5))
        else:
            # Use PA_BOOST
            self.write_register(self.REG_PA_DAC, 0x84)  # Default
            self.write_register(self.REG_PA_CONFIG, self.PA_BOOST | (power - 2))
    
    def set_crc(self, enable):
        """Enable/disable CRC"""
        config2 = self.read_register(self.REG_MODEM_CONFIG_2)
        if enable:
            config2 |= 0x04
        else:
            config2 &= 0xFB
        self.write_register(self.REG_MODEM_CONFIG_2, config2)
    
    def transmit(self, data):
        """Transmit data"""
        # Set standby mode
        self.set_mode(self.MODE_STDBY)
        
        # Set FIFO TX base address
        self.write_register(self.REG_FIFO_ADDR_PTR, 0)
        self.write_register(self.REG_FIFO_TX_BASE_ADDR, 0)
        
        # Write payload to FIFO
        for byte in data:
            self.write_register(self.REG_FIFO, byte)
        
        # Set payload length
        self.write_register(self.REG_PAYLOAD_LENGTH, len(data))
        
        # Start transmission
        self.set_mode(self.MODE_TX)
        
        # Wait for TX done
        start = time.time()
        while time.time() - start < 10:
            irq_flags = self.read_register(self.REG_IRQ_FLAGS)
            if irq_flags & self.IRQ_TX_DONE_MASK:
                # Clear IRQ
                self.write_register(self.REG_IRQ_FLAGS, 0xFF)
                self.set_mode(self.MODE_STDBY)
                return True
            time.sleep(0.01)
        
        raise TimeoutError("TX timeout")
    
    def receive(self, timeout=10):
        """Receive data"""
        # Set standby mode
        self.set_mode(self.MODE_STDBY)
        
        # Set FIFO RX base address
        self.write_register(self.REG_FIFO_ADDR_PTR, 0)
        self.write_register(self.REG_FIFO_RX_BASE_ADDR, 0)
        
        # Clear IRQ flags
        self.write_register(self.REG_IRQ_FLAGS, 0xFF)
        
        # Start continuous RX
        self.set_mode(self.MODE_RX_CONTINUOUS)
        
        # Wait for RX done
        start = time.time()
        while time.time() - start < timeout:
            irq_flags = self.read_register(self.REG_IRQ_FLAGS)
            
            if irq_flags & self.IRQ_RX_DONE_MASK:
                # Check CRC error
                if irq_flags & self.IRQ_PAYLOAD_CRC_ERROR_MASK:
                    self.write_register(self.REG_IRQ_FLAGS, 0xFF)
                    continue
                
                # Get packet length
                packet_length = self.read_register(self.REG_RX_NB_BYTES)
                
                # Get FIFO RX current address
                fifo_addr = self.read_register(self.REG_FIFO_RX_CURRENT_ADDR)
                self.write_register(self.REG_FIFO_ADDR_PTR, fifo_addr)
                
                # Read payload
                payload = []
                for i in range(packet_length):
                    payload.append(self.read_register(self.REG_FIFO))
                
                # Clear IRQ
                self.write_register(self.REG_IRQ_FLAGS, 0xFF)
                self.set_mode(self.MODE_STDBY)
                
                return bytes(payload)
            
            time.sleep(0.1)
        
        self.set_mode(self.MODE_STDBY)
        return None
    
    def cleanup(self):
        """Cleanup resources"""
        self.set_mode(self.MODE_SLEEP)
        self.spi.close()
        GPIO.cleanup()
