#!/usr/bin/env python3
"""
LoRa P2P Transmitter
Sends test messages continuously

Usage:
    python3 transmitter.py [message] [interval]
    
Example:
    python3 transmitter.py "Hello LoRa!" 2
"""

import sys
import time
from sx1276 import SX1276

# ============================================
# CONFIGURATION - Must match on both devices!
# ============================================
FREQUENCY = 433000000      # 433 MHz (change based on your region)
SPREADING_FACTOR = 7       # SF7-SF12 (higher = longer range, slower)
BANDWIDTH = 125000         # 125 kHz
CODING_RATE = 5            # 4/5
TX_POWER = 17              # dBm (2-20)
SYNC_WORD = 0x12           # Private sync word


def main():
    # Parse arguments
    message = sys.argv[1] if len(sys.argv) > 1 else "Hello from LoRa TX!"
    interval = float(sys.argv[2]) if len(sys.argv) > 2 else 3.0
    
    print("=" * 50)
    print("    LoRa P2P Transmitter (SX1276)")
    print("=" * 50)
    
    try:
        # Initialize LoRa
        print("\n[*] Initializing SX1276...")
        lora = SX1276()
        
        # Configure for P2P
        lora.set_frequency(FREQUENCY)
        lora.set_spreading_factor(SPREADING_FACTOR)
        lora.set_bandwidth(BANDWIDTH)
        lora.set_coding_rate(CODING_RATE)
        lora.set_tx_power(TX_POWER)
        lora.set_sync_word(SYNC_WORD)
        
        print("[✓] SX1276 initialized!")
        print("\n[*] Configuration:")
        for key, value in lora.get_config().items():
            print(f"    {key}: {value}")
        
        print(f"\n[*] Sending message every {interval} seconds")
        print(f"[*] Message: '{message}'")
        print("\n[*] Press Ctrl+C to stop\n")
        print("-" * 50)
        
        counter = 0
        while True:
            counter += 1
            payload = f"{message} #{counter}"
            
            print(f"[TX] Sending: {payload}")
            start = time.time()
            
            if lora.send(payload):
                elapsed = (time.time() - start) * 1000
                print(f"[✓] Sent successfully ({elapsed:.1f} ms)")
            else:
                print("[✗] Transmission timeout!")
                
            print("-" * 50)
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n\n[*] Stopping transmitter...")
    except Exception as e:
        print(f"\n[✗] Error: {e}")
        raise
    finally:
        if 'lora' in locals():
            lora.close()
            print("[*] Cleanup complete")


if __name__ == "__main__":
    main()
