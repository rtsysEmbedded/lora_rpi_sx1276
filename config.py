# LoRaWAN Device Configuration for ChirpStack

# Device Credentials
DEVICE_EUI = "0bbef9f59cc6986a"  # Your device EUI
APP_KEY = "d8341a42c8894b3bb82d0f721a0fcdbc"  # Your application key

# You'll need to get the APP_EUI from ChirpStack application settings
# If using ChirpStack v4, APP_EUI might be all zeros or match join server
APP_EUI = "0000000000000000"  # Update this from your ChirpStack application

# LoRa Radio Configuration
FREQUENCY = 868.1  # MHz - EU868 default channel (change to 915.0 for US915)
SPREADING_FACTOR = 7  # SF7-SF12
BANDWIDTH = 125000  # 125 kHz
CODING_RATE = 5  # 4/5
PREAMBLE_LENGTH = 8
TX_POWER = 14  # dBm
SYNC_WORD = 0x34  # LoRaWAN sync word

# SPI Configuration for Raspberry Pi
SPI_BUS = 0
SPI_DEVICE = 0

# GPIO Pin Configuration (BCM numbering)
# Adjust these based on your wiring
PIN_NSS = 8      # Chip Select (CE0) - GPIO 8 / Pin 24
PIN_RESET = 25   # Reset pin - GPIO 25 / Pin 22
PIN_DIO0 = 24    # DIO0 for TX/RX done - GPIO 24 / Pin 18
PIN_DIO1 = 23    # DIO1 for RX timeout - GPIO 23 / Pin 16
PIN_DIO2 = None  # Optional
PIN_DIO3 = None  # Optional

# LoRaWAN Regional Settings
# For EU868
RX1_DELAY = 1  # seconds
RX2_FREQUENCY = 869.525  # MHz
RX2_DATARATE = 0  # SF12BW125

# For US915, uncomment and adjust:
# FREQUENCY = 915.0
# RX2_FREQUENCY = 923.3
