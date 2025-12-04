#!/usr/bin/env python3
"""
LoRa P2P Sender - Raspberry Pi 3 + SX1276
This script sends messages via LoRa in P2P mode
"""

import time
import sys
from lora import SX127x

# GPIO pin configuration for Raspberry Pi 3
# Adjust these based on your wiring
LORA_CS_PIN = 8      # Chip Select (NSS) - GPIO 8 (SPI0_CE0)
LORA_RESET_PIN = 25  # Reset pin - GPIO 25
LORA_DIO0_PIN = 24   # DIO0 pin (optional, for interrupts) - GPIO 24

# LoRa P2P Configuration
# IMPORTANT: These parameters MUST match on both sender and receiver!
LORA_FREQUENCY = 433.0  # MHz (change to 868.0 or 915.0 based on your region)
LORA_SPREADING_FACTOR = 7  # 6-12 (7 is good balance of speed/range)
LORA_BANDWIDTH = 125  # kHz (125 is standard)
LORA_CODING_RATE = 5  # 4/5 (value 5 means 4/5)
LORA_PREAMBLE_LENGTH = 8  # bytes
LORA_SYNC_WORD = 0x12  # 2-byte sync word (0x12 = 18 decimal)
LORA_TX_POWER = 14  # dBm (2-20, 14 is good default)
LORA_CRC = True  # Enable CRC for error checking

def setup_lora():
    """Initialize and configure the LoRa module"""
    print("Initializing LoRa module...")
    
    # Create LoRa object
    lora = SX127x(
        cs=LORA_CS_PIN,
        reset=LORA_RESET_PIN,
        dio0=LORA_DIO0_PIN,
        frequency=LORA_FREQUENCY,
        spreading_factor=LORA_SPREADING_FACTOR,
        bandwidth=LORA_BANDWIDTH,
        coding_rate=LORA_CODING_RATE,
        preamble_length=LORA_PREAMBLE_LENGTH,
        sync_word=LORA_SYNC_WORD,
        tx_power=LORA_TX_POWER,
        crc=LORA_CRC
    )
    
    # Set to transmitter mode
    lora.set_mode_tx()
    
    print("LoRa module configured:")
    print(f"  Frequency: {LORA_FREQUENCY} MHz")
    print(f"  Spreading Factor: {LORA_SPREADING_FACTOR}")
    print(f"  Bandwidth: {LORA_BANDWIDTH} kHz")
    print(f"  Coding Rate: 4/{LORA_CODING_RATE}")
    print(f"  TX Power: {LORA_TX_POWER} dBm")
    print(f"  Sync Word: 0x{LORA_SYNC_WORD:02X}")
    print(f"  CRC: {'Enabled' if LORA_CRC else 'Disabled'}")
    print()
    
    return lora

def send_message(lora, message):
    """Send a message via LoRa"""
    try:
        print(f"Sending: {message}")
        lora.send(message.encode('utf-8'))
        print("Message sent successfully!")
        return True
    except Exception as e:
        print(f"Error sending message: {e}")
        return False

def main():
    """Main function"""
    print("=" * 50)
    print("LoRa P2P Sender - SX1276 Module")
    print("=" * 50)
    print()
    
    # Initialize LoRa
    try:
        lora = setup_lora()
    except Exception as e:
        print(f"Failed to initialize LoRa: {e}")
        print("\nTroubleshooting:")
        print("1. Check SPI is enabled: sudo raspi-config -> Interface Options -> SPI -> Enable")
        print("2. Verify wiring connections")
        print("3. Check GPIO pin numbers match your setup")
        sys.exit(1)
    
    print("Ready to send messages!")
    print("Type your message and press Enter (or 'quit' to exit)")
    print()
    
    try:
        while True:
            # Get user input
            message = input("Message: ").strip()
            
            if message.lower() in ['quit', 'exit', 'q']:
                break
            
            if not message:
                continue
            
            # Send message
            send_message(lora, message)
            
            # Small delay between transmissions
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        print("\nShutting down...")
        # Clean up would go here if needed

if __name__ == "__main__":
    main()
