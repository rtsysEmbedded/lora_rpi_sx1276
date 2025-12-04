#!/usr/bin/env python3
"""
LoRa P2P Ping-Pong Test
Bidirectional communication test between two LoRa modules

Usage:
    Node A: python3 ping_pong.py A
    Node B: python3 ping_pong.py B
    
Node A sends first, then they alternate.
"""

import sys
import time
from sx1276 import SX1276

# ============================================
# CONFIGURATION - Must match on both devices!
# ============================================
FREQUENCY = 433000000
SPREADING_FACTOR = 7
BANDWIDTH = 125000
CODING_RATE = 5
TX_POWER = 17
SYNC_WORD = 0x12


def main():
    if len(sys.argv) < 2 or sys.argv[1].upper() not in ['A', 'B']:
        print("Usage: python3 ping_pong.py [A|B]")
        print("  A = This node sends first (PING)")
        print("  B = This node listens first (PONG)")
        sys.exit(1)
        
    node_id = sys.argv[1].upper()
    is_sender_first = (node_id == 'A')
    
    print("=" * 50)
    print(f"    LoRa P2P Ping-Pong Test - Node {node_id}")
    print("=" * 50)
    
    try:
        print("\n[*] Initializing SX1276...")
        lora = SX1276()
        
        # Configure
        lora.set_frequency(FREQUENCY)
        lora.set_spreading_factor(SPREADING_FACTOR)
        lora.set_bandwidth(BANDWIDTH)
        lora.set_coding_rate(CODING_RATE)
        lora.set_tx_power(TX_POWER)
        lora.set_sync_word(SYNC_WORD)
        
        print("[✓] SX1276 initialized!")
        print(f"\n[*] Mode: {'PING (send first)' if is_sender_first else 'PONG (listen first)'}")
        print("[*] Press Ctrl+C to stop\n")
        print("-" * 50)
        
        counter = 0
        successes = 0
        failures = 0
        
        while True:
            if is_sender_first:
                # Send PING
                counter += 1
                msg = f"PING-{node_id}-{counter}"
                print(f"\n[TX] Sending: {msg}")
                start = time.time()
                
                if lora.send(msg):
                    tx_time = (time.time() - start) * 1000
                    print(f"[✓] Sent ({tx_time:.1f}ms)")
                    
                    # Wait for PONG
                    print("[RX] Waiting for PONG...")
                    data, rssi, snr = lora.receive(timeout=5)
                    
                    if data:
                        rtt = (time.time() - start) * 1000
                        successes += 1
                        print(f"[✓] Received: {data.decode()}")
                        print(f"    RTT: {rtt:.1f}ms, RSSI: {rssi}dBm, SNR: {snr:.1f}dB")
                    else:
                        failures += 1
                        print("[✗] No response (timeout)")
                else:
                    failures += 1
                    print("[✗] TX failed")
                    
                # Stats
                total = successes + failures
                if total > 0:
                    print(f"\n    Stats: {successes}/{total} ({100*successes/total:.1f}%)")
                print("-" * 50)
                time.sleep(2)
                
            else:
                # Wait for PING
                print("\n[RX] Waiting for PING...")
                data, rssi, snr = lora.receive(timeout=10)
                
                if data:
                    counter += 1
                    print(f"[✓] Received: {data.decode()}")
                    print(f"    RSSI: {rssi}dBm, SNR: {snr:.1f}dB")
                    
                    # Send PONG
                    msg = f"PONG-{node_id}-{counter}"
                    print(f"[TX] Sending: {msg}")
                    time.sleep(0.1)  # Small delay before responding
                    
                    if lora.send(msg):
                        successes += 1
                        print("[✓] PONG sent!")
                    else:
                        failures += 1
                        print("[✗] PONG failed")
                else:
                    print("[*] No PING received (timeout)")
                    
                print("-" * 50)
                
    except KeyboardInterrupt:
        print("\n\n[*] Stopping...")
        print(f"[*] Final stats: {successes} successful, {failures} failed")
    finally:
        if 'lora' in locals():
            lora.close()
            print("[*] Cleanup complete")


if __name__ == "__main__":
    main()
