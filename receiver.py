#!/usr/bin/env python3
"""
LoRa P2P Receiver
Listens for incoming messages and displays them

Usage:
    python3 receiver.py [timeout]
    
Example:
    python3 receiver.py 10  # Wait max 10 seconds per packet
    python3 receiver.py     # Wait forever for each packet
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
SYNC_WORD = 0x12           # Private sync word


def rssi_bars(rssi):
    """Convert RSSI to visual signal bars"""
    if rssi > -70:
        return "▂▄▆█ (Excellent)"
    elif rssi > -85:
        return "▂▄▆░ (Good)"
    elif rssi > -100:
        return "▂▄░░ (Fair)"
    elif rssi > -115:
        return "▂░░░ (Weak)"
    else:
        return "░░░░ (Very Weak)"


def main():
    # Parse arguments
    timeout = float(sys.argv[1]) if len(sys.argv) > 1 else None
    
    print("=" * 50)
    print("    LoRa P2P Receiver (SX1276)")
    print("=" * 50)
    
    try:
        # Initialize LoRa
        print("\n[*] Initializing SX1276...")
        lora = SX1276()
        
        # Configure for P2P (must match transmitter!)
        lora.set_frequency(FREQUENCY)
        lora.set_spreading_factor(SPREADING_FACTOR)
        lora.set_bandwidth(BANDWIDTH)
        lora.set_coding_rate(CODING_RATE)
        lora.set_sync_word(SYNC_WORD)
        
        print("[✓] SX1276 initialized!")
        print("\n[*] Configuration:")
        for key, value in lora.get_config().items():
            print(f"    {key}: {value}")
        
        timeout_str = f"{timeout}s" if timeout else "forever"
        print(f"\n[*] Waiting for packets (timeout: {timeout_str})")
        print("[*] Press Ctrl+C to stop\n")
        print("-" * 50)
        
        packets_received = 0
        start_time = time.time()
        
        while True:
            print("[RX] Listening...")
            data, rssi, snr = lora.receive(timeout=timeout)
            
            if data is not None:
                packets_received += 1
                try:
                    message = data.decode('utf-8')
                except:
                    message = data.hex()
                    
                print(f"\n[✓] Packet #{packets_received} received!")
                print(f"    Message: {message}")
                print(f"    Length:  {len(data)} bytes")
                print(f"    RSSI:    {rssi} dBm {rssi_bars(rssi)}")
                print(f"    SNR:     {snr:.1f} dB")
                print("-" * 50)
            else:
                print("[*] No packet received (timeout)")
                print("-" * 50)
                
    except KeyboardInterrupt:
        elapsed = time.time() - start_time
        print("\n\n[*] Stopping receiver...")
        print(f"[*] Statistics:")
        print(f"    Runtime:         {elapsed:.1f} seconds")
        print(f"    Packets received: {packets_received}")
        if elapsed > 0:
            print(f"    Rate:            {packets_received/elapsed*60:.1f} packets/min")
    except Exception as e:
        print(f"\n[✗] Error: {e}")
        raise
    finally:
        if 'lora' in locals():
            lora.close()
            print("[*] Cleanup complete")


if __name__ == "__main__":
    main()
