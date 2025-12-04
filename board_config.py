#!/usr/bin/env python3
"""
Board configuration for Raspberry Pi with SX1276
This file configures the GPIO pins and SPI interface
"""

import RPi.GPIO as GPIO
import spidev
import config

# Use BCM GPIO numbering
GPIO.setwarnings(False)  # Disable warnings first
GPIO.setmode(GPIO.BCM)


class BOARD:
    """Board configuration for RPi + SX1276"""
    
    # SPI device
    SPI = None
    
    # GPIO pins (BCM numbering)
    DIO0 = config.PIN_DIO0
    DIO1 = config.PIN_DIO1
    DIO2 = config.PIN_DIO2
    DIO3 = config.PIN_DIO3
    RST = config.PIN_RESET
    NSS = config.PIN_NSS
    
    # LED (optional - for visual feedback)
    LED = None
    
    @staticmethod
    def setup():
        """Setup GPIO and SPI"""
        # Setup SPI
        BOARD.SPI = spidev.SpiDev()
        BOARD.SPI.open(config.SPI_BUS, config.SPI_DEVICE)
        BOARD.SPI.max_speed_hz = 5000000
        
        # Setup GPIO pins
        GPIO.setup(BOARD.RST, GPIO.OUT)
        GPIO.setup(BOARD.NSS, GPIO.OUT)
        
        if BOARD.DIO0:
            GPIO.setup(BOARD.DIO0, GPIO.IN)
        if BOARD.DIO1:
            GPIO.setup(BOARD.DIO1, GPIO.IN)
        if BOARD.DIO2:
            GPIO.setup(BOARD.DIO2, GPIO.IN)
        if BOARD.DIO3:
            GPIO.setup(BOARD.DIO3, GPIO.IN)
        
        # Set NSS high (chip not selected)
        GPIO.output(BOARD.NSS, GPIO.HIGH)
        
        # Reset the module
        GPIO.output(BOARD.RST, GPIO.LOW)
        import time
        time.sleep(0.01)
        GPIO.output(BOARD.RST, GPIO.HIGH)
        time.sleep(0.01)
    
    @staticmethod
    def teardown():
        """Cleanup GPIO and SPI"""
        if BOARD.SPI:
            BOARD.SPI.close()
        GPIO.cleanup()
    
    @staticmethod
    def spi_transfer(data):
        """SPI transfer"""
        GPIO.output(BOARD.NSS, GPIO.LOW)
        response = BOARD.SPI.xfer2(data)
        GPIO.output(BOARD.NSS, GPIO.HIGH)
        return response
