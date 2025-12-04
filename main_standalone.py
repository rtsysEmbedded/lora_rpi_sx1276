#!/usr/bin/env python3
"""
Main application - Standalone version
No external LoRa library dependencies
"""

import time
import sys
from lorawan_standalone import LoRaWANClient
import config


def main():
    """Main application"""
    print("=" * 60)
    print("LoRaWAN Client for ChirpStack (Standalone)")
    print("=" * 60)
    
    # Initialize client
    try:
        client = LoRaWANClient(
            device_eui=config.DEVICE_EUI,
            app_eui=config.APP_EUI,
            app_key=config.APP_KEY,
            frequency=config.FREQUENCY
        )
    except Exception as e:
        print(f"Error initializing client: {e}")
        print("\nMake sure:")
        print("1. SX1276 module is properly connected")
        print("2. SPI is enabled")
        print("3. Running with sudo")
        sys.exit(1)
    
    try:
        # Perform OTAA join
        if not client.join(timeout=30):
            print("Failed to join network. Check:")
            print("1. Device is registered in ChirpStack")
            print("2. Gateway is online and in range")
            print("3. Device credentials are correct")
            print("4. Frequency matches your region")
            sys.exit(1)
        
        # Send data periodically
        counter = 0
        while True:
            message = f"Hello from RPi! Count: {counter}"
            client.send_data(message, confirmed=False, port=1)
            counter += 1
            
            print(f"\nWaiting 30 seconds before next transmission...")
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n\nStopping...")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.cleanup()
        print("Cleaned up. Goodbye!")


if __name__ == "__main__":
    main()
