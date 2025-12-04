#!/usr/bin/env python3
"""
LoRa P2P Receiver - Raspberry Pi 3 + SX1276
This script receives messages via LoRa in P2P mode
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
    
    # Set to receiver mode (continuous)
    lora.set_mode_rx()
    
    print("LoRa module configured:")
    print(f"  Frequency: {LORA_FREQUENCY} MHz")
    print(f"  Spreading Factor: {LORA_SPREADING_FACTOR}")
    print(f"  Bandwidth: {LORA_BANDWIDTH} kHz")
    print(f"  Coding Rate: 4/{LORA_CODING_RATE}")
    print(f"  Sync Word: 0x{LORA_SYNC_WORD:02X}")
    print(f"  CRC: {'Enabled' if LORA_CRC else 'Disabled'}")
    print()
    print("Listening for messages...")
    print("Press Ctrl+C to stop")
    print()
    
    return lora

def receive_message(lora, timeout=5):
    """Receive a message via LoRa"""
    try:
        # Wait for a packet (with timeout)
        start_time = time.time()
        while time.time() - start_time < timeout:
            if lora.received_packet():
                # Read the packet
                payload = lora.read_payload()
                message = payload.decode('utf-8', errors='ignore')
                rssi = lora.packet_rssi()
                snr = lora.packet_snr()
                
                return message, rssi, snr
            time.sleep(0.1)  # Small delay to avoid busy waiting
        
        return None, None, None
    except Exception as e:
        print(f"Error receiving message: {e}")
        return None, None, None

def main():
    """Main function"""
    print("=" * 50)
    print("LoRa P2P Receiver - SX1276 Module")
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
    
    message_count = 0
    
    try:
        while True:
            # Try to receive a message
            message, rssi, snr = receive_message(lora, timeout=1)
            
            if message:
                message_count += 1
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{timestamp}] Message #{message_count}: {message}")
                if rssi is not None:
                    print(f"  RSSI: {rssi} dBm", end="")
                if snr is not None:
                    print(f"  SNR: {snr} dB")
                print()
                
                # Reset receiver for next packet
                lora.set_mode_rx()
            
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        print(f"Total messages received: {message_count}")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        print("\nShutting down...")

if __name__ == "__main__":
    main()
