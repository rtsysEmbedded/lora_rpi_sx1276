"""
SX1276 LoRa Module Driver for Raspberry Pi
Supports P2P (Point-to-Point) communication

Wiring:
    SX1276      RPi3
    ------      ----
    VCC    -->  3.3V (Pin 1)
    GND    -->  GND (Pin 6)
    SCK    -->  SCLK/GPIO11 (Pin 23)
    MISO   -->  MISO/GPIO9 (Pin 21)
    MOSI   -->  MOSI/GPIO10 (Pin 19)
    NSS    -->  CE0/GPIO8 (Pin 24)
    DIO0   -->  GPIO4 (Pin 7)
    RST    -->  GPIO17 (Pin 11)
"""

import spidev
import RPi.GPIO as GPIO
import time

# SX1276 Register Addresses
REG_FIFO = 0x00
REG_OP_MODE = 0x01
REG_FRF_MSB = 0x06
REG_FRF_MID = 0x07
REG_FRF_LSB = 0x08
REG_PA_CONFIG = 0x09
REG_PA_RAMP = 0x0A
REG_OCP = 0x0B
REG_LNA = 0x0C
REG_FIFO_ADDR_PTR = 0x0D
REG_FIFO_TX_BASE_ADDR = 0x0E
REG_FIFO_RX_BASE_ADDR = 0x0F
REG_FIFO_RX_CURRENT_ADDR = 0x10
REG_IRQ_FLAGS_MASK = 0x11
REG_IRQ_FLAGS = 0x12
REG_RX_NB_BYTES = 0x13
REG_PKT_SNR_VALUE = 0x19
REG_PKT_RSSI_VALUE = 0x1A
REG_MODEM_CONFIG_1 = 0x1D
REG_MODEM_CONFIG_2 = 0x1E
REG_SYMB_TIMEOUT_LSB = 0x1F
REG_PREAMBLE_MSB = 0x20
REG_PREAMBLE_LSB = 0x21
REG_PAYLOAD_LENGTH = 0x22
REG_MAX_PAYLOAD_LENGTH = 0x23
REG_HOP_PERIOD = 0x24
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
MODE_LONG_RANGE_MODE = 0x80
MODE_SLEEP = 0x00
MODE_STDBY = 0x01
MODE_TX = 0x03
MODE_RX_CONTINUOUS = 0x05
MODE_RX_SINGLE = 0x06

# IRQ Flags
IRQ_TX_DONE_MASK = 0x08
IRQ_PAYLOAD_CRC_ERROR_MASK = 0x20
IRQ_RX_DONE_MASK = 0x40

# PA Config
PA_BOOST = 0x80

# Default pins (BCM numbering)
DEFAULT_NSS_PIN = 8      # CE0
DEFAULT_RESET_PIN = 17   # GPIO17
DEFAULT_DIO0_PIN = 4     # GPIO4


class SX1276:
    """SX1276 LoRa transceiver driver for Raspberry Pi"""
    
    def __init__(self, spi_bus=0, spi_device=0, nss_pin=DEFAULT_NSS_PIN,
                 reset_pin=DEFAULT_RESET_PIN, dio0_pin=DEFAULT_DIO0_PIN):
        """
        Initialize SX1276 module
        
        Args:
            spi_bus: SPI bus number (usually 0)
            spi_device: SPI device number (0 for CE0, 1 for CE1)
            nss_pin: GPIO pin for chip select (NSS)
            reset_pin: GPIO pin for reset
            dio0_pin: GPIO pin for DIO0 interrupt
        """
        self.nss_pin = nss_pin
        self.reset_pin = reset_pin
        self.dio0_pin = dio0_pin
        self._frequency = 433000000  # Default 433 MHz
        self._tx_power = 17
        self._spreading_factor = 7
        self._bandwidth = 125000
        self._coding_rate = 5
        self._implicit_header = False
        self._on_receive = None
        
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.nss_pin, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(self.reset_pin, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(self.dio0_pin, GPIO.IN)
        
        # Setup SPI
        self.spi = spidev.SpiDev()
        self.spi.open(spi_bus, spi_device)
        self.spi.max_speed_hz = 5000000
        self.spi.mode = 0
        
        # Reset module
        self.reset()
        
        # Check version
        version = self._read_register(REG_VERSION)
        if version != 0x12:
            raise Exception(f"Invalid SX1276 version: 0x{version:02X} (expected 0x12)")
        
        # Initialize in sleep mode
        self.sleep()
        
        # Set base addresses
        self._write_register(REG_FIFO_TX_BASE_ADDR, 0x00)
        self._write_register(REG_FIFO_RX_BASE_ADDR, 0x00)
        
        # Set LNA boost
        self._write_register(REG_LNA, self._read_register(REG_LNA) | 0x03)
        
        # Set auto AGC
        self._write_register(REG_MODEM_CONFIG_3, 0x04)
        
        # Set default parameters
        self.set_tx_power(self._tx_power)
        self.set_frequency(self._frequency)
        self.set_spreading_factor(self._spreading_factor)
        self.set_bandwidth(self._bandwidth)
        self.set_coding_rate(self._coding_rate)
        self.set_sync_word(0x12)  # Private sync word
        
        # Go to standby
        self.standby()
        
    def _write_register(self, address, value):
        """Write a single byte to a register"""
        GPIO.output(self.nss_pin, GPIO.LOW)
        self.spi.xfer2([address | 0x80, value])
        GPIO.output(self.nss_pin, GPIO.HIGH)
        
    def _read_register(self, address):
        """Read a single byte from a register"""
        GPIO.output(self.nss_pin, GPIO.LOW)
        response = self.spi.xfer2([address & 0x7F, 0x00])
        GPIO.output(self.nss_pin, GPIO.HIGH)
        return response[1]
    
    def _write_fifo(self, data):
        """Write data to FIFO"""
        GPIO.output(self.nss_pin, GPIO.LOW)
        self.spi.xfer2([REG_FIFO | 0x80] + list(data))
        GPIO.output(self.nss_pin, GPIO.HIGH)
        
    def _read_fifo(self, length):
        """Read data from FIFO"""
        GPIO.output(self.nss_pin, GPIO.LOW)
        response = self.spi.xfer2([REG_FIFO] + [0x00] * length)
        GPIO.output(self.nss_pin, GPIO.HIGH)
        return bytes(response[1:])
    
    def reset(self):
        """Reset the module"""
        GPIO.output(self.reset_pin, GPIO.LOW)
        time.sleep(0.01)
        GPIO.output(self.reset_pin, GPIO.HIGH)
        time.sleep(0.01)
        
    def sleep(self):
        """Put module in sleep mode"""
        self._write_register(REG_OP_MODE, MODE_LONG_RANGE_MODE | MODE_SLEEP)
        
    def standby(self):
        """Put module in standby mode"""
        self._write_register(REG_OP_MODE, MODE_LONG_RANGE_MODE | MODE_STDBY)
        
    def set_frequency(self, frequency):
        """
        Set the center frequency
        
        Args:
            frequency: Frequency in Hz (e.g., 433000000 for 433 MHz)
        """
        self._frequency = frequency
        frf = int((frequency << 19) / 32000000)
        self._write_register(REG_FRF_MSB, (frf >> 16) & 0xFF)
        self._write_register(REG_FRF_MID, (frf >> 8) & 0xFF)
        self._write_register(REG_FRF_LSB, frf & 0xFF)
        
    def set_tx_power(self, level, use_pa_boost=True):
        """
        Set transmit power
        
        Args:
            level: Power level in dBm (2-20)
            use_pa_boost: Use PA_BOOST pin (required for >14 dBm)
        """
        self._tx_power = level
        if use_pa_boost:
            if level > 17:
                # Enable +20 dBm mode
                self._write_register(REG_PA_DAC, 0x87)
                level = min(level, 20)
                self._write_register(REG_PA_CONFIG, PA_BOOST | (level - 5))
            else:
                self._write_register(REG_PA_DAC, 0x84)
                level = min(level, 17)
                self._write_register(REG_PA_CONFIG, PA_BOOST | (level - 2))
        else:
            level = min(level, 14)
            self._write_register(REG_PA_CONFIG, 0x70 | level)
            
    def set_spreading_factor(self, sf):
        """
        Set spreading factor (SF7-SF12)
        
        Higher SF = longer range, slower data rate
        """
        if sf < 7 or sf > 12:
            raise ValueError("Spreading factor must be 7-12")
        self._spreading_factor = sf
        
        # Detection optimization
        if sf == 6:
            self._write_register(REG_DETECTION_OPTIMIZE, 0xC5)
            self._write_register(REG_DETECTION_THRESHOLD, 0x0C)
        else:
            self._write_register(REG_DETECTION_OPTIMIZE, 0xC3)
            self._write_register(REG_DETECTION_THRESHOLD, 0x0A)
            
        config2 = self._read_register(REG_MODEM_CONFIG_2)
        config2 = (config2 & 0x0F) | ((sf << 4) & 0xF0)
        self._write_register(REG_MODEM_CONFIG_2, config2)
        
        # Update LDO flag for low data rate
        self._set_ldo_flag()
        
    def set_bandwidth(self, bw):
        """
        Set signal bandwidth
        
        Args:
            bw: Bandwidth in Hz (7800, 10400, 15600, 20800, 31250,
                41700, 62500, 125000, 250000, 500000)
        """
        self._bandwidth = bw
        bw_map = {
            7800: 0, 10400: 1, 15600: 2, 20800: 3,
            31250: 4, 41700: 5, 62500: 6, 125000: 7,
            250000: 8, 500000: 9
        }
        if bw not in bw_map:
            raise ValueError(f"Invalid bandwidth: {bw}")
            
        config1 = self._read_register(REG_MODEM_CONFIG_1)
        config1 = (config1 & 0x0F) | (bw_map[bw] << 4)
        self._write_register(REG_MODEM_CONFIG_1, config1)
        self._set_ldo_flag()
        
    def set_coding_rate(self, cr):
        """
        Set coding rate (4/5, 4/6, 4/7, 4/8)
        
        Args:
            cr: Denominator (5, 6, 7, or 8)
        """
        if cr < 5 or cr > 8:
            raise ValueError("Coding rate must be 5-8 (for 4/5 to 4/8)")
        self._coding_rate = cr
        
        config1 = self._read_register(REG_MODEM_CONFIG_1)
        config1 = (config1 & 0xF1) | ((cr - 4) << 1)
        self._write_register(REG_MODEM_CONFIG_1, config1)
        
    def set_sync_word(self, sw):
        """
        Set sync word (must match between devices)
        
        Args:
            sw: Sync word (0x00-0xFF, default 0x12 for private, 0x34 for LoRaWAN)
        """
        self._write_register(REG_SYNC_WORD, sw)
        
    def set_preamble_length(self, length):
        """Set preamble length (6-65535)"""
        self._write_register(REG_PREAMBLE_MSB, (length >> 8) & 0xFF)
        self._write_register(REG_PREAMBLE_LSB, length & 0xFF)
        
    def _set_ldo_flag(self):
        """Set Low Data Rate Optimize flag when needed"""
        symbol_duration = 1000 / (self._bandwidth / (1 << self._spreading_factor))
        ldo_on = symbol_duration > 16
        
        config3 = self._read_register(REG_MODEM_CONFIG_3)
        if ldo_on:
            config3 |= 0x08
        else:
            config3 &= ~0x08
        self._write_register(REG_MODEM_CONFIG_3, config3)
        
    def send(self, data, timeout=2.0):
        """
        Send data packet
        
        Args:
            data: Bytes or string to send
            timeout: Maximum time to wait for TX completion
            
        Returns:
            True if sent successfully
        """
        if isinstance(data, str):
            data = data.encode()
            
        self.standby()
        
        # Set FIFO address
        self._write_register(REG_FIFO_ADDR_PTR, 0x00)
        
        # Write data to FIFO
        self._write_fifo(data)
        
        # Set payload length
        self._write_register(REG_PAYLOAD_LENGTH, len(data))
        
        # Set DIO0 mapping to TX Done
        self._write_register(REG_DIO_MAPPING_1, 0x40)
        
        # Start transmission
        self._write_register(REG_OP_MODE, MODE_LONG_RANGE_MODE | MODE_TX)
        
        # Wait for TX done
        start = time.time()
        while time.time() - start < timeout:
            irq = self._read_register(REG_IRQ_FLAGS)
            if irq & IRQ_TX_DONE_MASK:
                # Clear IRQ
                self._write_register(REG_IRQ_FLAGS, IRQ_TX_DONE_MASK)
                self.standby()
                return True
            time.sleep(0.01)
            
        self.standby()
        return False
    
    def receive(self, timeout=None):
        """
        Receive a single packet
        
        Args:
            timeout: Maximum time to wait (None = wait forever)
            
        Returns:
            Tuple of (data, rssi, snr) or (None, None, None) if timeout
        """
        self.standby()
        
        # Set FIFO address
        self._write_register(REG_FIFO_ADDR_PTR, 0x00)
        
        # Set DIO0 mapping to RX Done
        self._write_register(REG_DIO_MAPPING_1, 0x00)
        
        # Clear IRQ flags
        self._write_register(REG_IRQ_FLAGS, 0xFF)
        
        # Start receiving
        self._write_register(REG_OP_MODE, MODE_LONG_RANGE_MODE | MODE_RX_CONTINUOUS)
        
        start = time.time()
        while True:
            if timeout and (time.time() - start > timeout):
                self.standby()
                return None, None, None
                
            irq = self._read_register(REG_IRQ_FLAGS)
            
            if irq & IRQ_RX_DONE_MASK:
                # Check CRC
                if irq & IRQ_PAYLOAD_CRC_ERROR_MASK:
                    self._write_register(REG_IRQ_FLAGS, IRQ_PAYLOAD_CRC_ERROR_MASK)
                    continue
                    
                # Clear IRQ
                self._write_register(REG_IRQ_FLAGS, IRQ_RX_DONE_MASK)
                
                # Get packet length
                length = self._read_register(REG_RX_NB_BYTES)
                
                # Set FIFO address to current RX address
                self._write_register(REG_FIFO_ADDR_PTR,
                                    self._read_register(REG_FIFO_RX_CURRENT_ADDR))
                
                # Read packet
                data = self._read_fifo(length)
                
                # Get RSSI and SNR
                rssi = self._read_register(REG_PKT_RSSI_VALUE) - 157
                snr = self._read_register(REG_PKT_SNR_VALUE)
                if snr > 127:
                    snr = (snr - 256) / 4
                else:
                    snr = snr / 4
                    
                self.standby()
                return data, rssi, snr
                
            time.sleep(0.01)
            
    def get_rssi(self):
        """Get current RSSI value"""
        return self._read_register(REG_RSSI_WIDEBAND)
    
    def close(self):
        """Clean up resources"""
        self.sleep()
        self.spi.close()
        GPIO.cleanup()
        
    def get_config(self):
        """Return current configuration as a dictionary"""
        return {
            'frequency': self._frequency,
            'spreading_factor': self._spreading_factor,
            'bandwidth': self._bandwidth,
            'coding_rate': f"4/{self._coding_rate}",
            'tx_power': self._tx_power
        }
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


if __name__ == "__main__":
    # Quick test
    print("Testing SX1276 connection...")
    try:
        lora = SX1276()
        print("✓ SX1276 detected!")
        print(f"  Configuration: {lora.get_config()}")
        lora.close()
    except Exception as e:
        print(f"✗ Error: {e}")
