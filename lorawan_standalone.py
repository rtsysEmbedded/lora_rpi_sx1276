#!/usr/bin/env python3
"""
Standalone LoRaWAN Client - No external LoRa library dependencies
Uses built-in sx127x_driver
"""

import time
import struct
from sx127x_driver import SX127x
from Crypto.Cipher import AES
from Crypto.Hash import CMAC
import binascii
import random
import config


class LoRaWANClient:
    """LoRaWAN OTAA client implementation"""
    
    def __init__(self, device_eui, app_eui, app_key, frequency=868.1):
        """Initialize LoRaWAN client"""
        # Store credentials
        self.dev_eui = bytes.fromhex(device_eui)
        self.app_eui = bytes.fromhex(app_eui)
        self.app_key = bytes.fromhex(app_key)
        
        # Session keys (obtained after join)
        self.nwk_s_key = None
        self.app_s_key = None
        self.dev_addr = None
        self.joined = False
        
        # Frame counters
        self.fcnt_up = 0
        self.fcnt_down = 0
        
        # Initialize radio
        self.radio = SX127x(
            spi_bus=config.SPI_BUS,
            spi_device=config.SPI_DEVICE,
            rst_pin=config.PIN_RESET,
            dio0_pin=config.PIN_DIO0,
            nss_pin=config.PIN_NSS
        )
        
        # Configure radio
        self.radio.set_frequency(frequency)
        self.radio.set_spreading_factor(config.SPREADING_FACTOR)
        self.radio.set_bandwidth(125)  # 125 kHz
        self.radio.set_coding_rate(config.CODING_RATE)
        self.radio.set_preamble_length(config.PREAMBLE_LENGTH)
        self.radio.set_sync_word(config.SYNC_WORD)
        self.radio.set_tx_power(config.TX_POWER)
        self.radio.set_crc(True)
        
        print(f"LoRaWAN Client initialized")
        print(f"DevEUI: {device_eui}")
        print(f"Frequency: {frequency} MHz")
    
    def aes128_encrypt(self, key, data):
        """AES-128 ECB encryption"""
        cipher = AES.new(key, AES.MODE_ECB)
        return cipher.encrypt(data)
    
    def calculate_mic(self, key, data):
        """Calculate LoRaWAN MIC"""
        cobj = CMAC.new(key, ciphermod=AES)
        cobj.update(data)
        return cobj.digest()[:4]
    
    def generate_join_request(self):
        """Generate LoRaWAN Join Request"""
        mhdr = bytes([0x00])
        app_eui_le = self.app_eui[::-1]
        dev_eui_le = self.dev_eui[::-1]
        dev_nonce = struct.pack('<H', random.randint(0, 65535))
        
        self.dev_nonce = dev_nonce
        msg = mhdr + app_eui_le + dev_eui_le + dev_nonce
        mic = self.calculate_mic(self.app_key, msg)
        
        return msg + mic
    
    def parse_join_accept(self, data):
        """Parse and decrypt Join Accept"""
        if len(data) < 12:
            return False
        
        mhdr = data[0]
        encrypted = data[1:]
        
        # Decrypt
        padded = encrypted + bytes(16 - len(encrypted) % 16)
        decrypted = self.aes128_encrypt(self.app_key, padded)
        decrypted = decrypted[:len(encrypted)]
        
        # Parse
        app_nonce = decrypted[0:3]
        net_id = decrypted[3:6]
        dev_addr = decrypted[6:10]
        
        # Verify MIC
        msg_for_mic = bytes([mhdr]) + decrypted[:-4]
        calculated_mic = self.calculate_mic(self.app_key, msg_for_mic)
        received_mic = decrypted[-4:]
        
        if calculated_mic != received_mic:
            print("Join Accept MIC verification failed!")
            return False
        
        # Derive session keys
        self.derive_session_keys(app_nonce, net_id, self.dev_nonce)
        self.dev_addr = dev_addr
        
        print(f"Join Accept received!")
        print(f"DevAddr: {binascii.hexlify(dev_addr).decode()}")
        
        return True
    
    def derive_session_keys(self, app_nonce, net_id, dev_nonce):
        """Derive session keys"""
        nwk_s_key_msg = bytes([0x01]) + app_nonce + net_id + dev_nonce + bytes(7)
        self.nwk_s_key = self.aes128_encrypt(self.app_key, nwk_s_key_msg)
        
        app_s_key_msg = bytes([0x02]) + app_nonce + net_id + dev_nonce + bytes(7)
        self.app_s_key = self.aes128_encrypt(self.app_key, app_s_key_msg)
        
        print(f"NwkSKey: {binascii.hexlify(self.nwk_s_key).decode()}")
        print(f"AppSKey: {binascii.hexlify(self.app_s_key).decode()}")
    
    def join(self, timeout=30):
        """Perform OTAA join"""
        print("\n=== Starting OTAA Join ===")
        
        join_request = self.generate_join_request()
        print(f"Sending Join Request: {binascii.hexlify(join_request).decode()}")
        
        # Send Join Request
        self.radio.transmit(join_request)
        
        # Wait for Join Accept
        print("Waiting for Join Accept...")
        time.sleep(1)  # RX1 delay
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            payload = self.radio.receive(timeout=5)
            
            if payload and len(payload) > 0:
                print(f"Received: {binascii.hexlify(payload).decode()}")
                
                if payload[0] == 0x20:  # Join Accept
                    if self.parse_join_accept(payload):
                        self.joined = True
                        print("=== Join Successful! ===\n")
                        return True
            
            time.sleep(0.5)
        
        print("Join failed: timeout")
        return False
    
    def encrypt_payload(self, data, fcnt):
        """Encrypt payload"""
        k = len(data) // 16 + 1
        s = b''
        
        for i in range(k):
            a = bytes([0x01, 0x00, 0x00, 0x00, 0x00, 0x00]) + self.dev_addr + struct.pack('<I', fcnt) + bytes([0x00, i + 1])
            s += self.aes128_encrypt(self.app_s_key, a)
        
        encrypted = bytes([data[i] ^ s[i] for i in range(len(data))])
        return encrypted
    
    def build_data_frame(self, payload, confirmed=False, port=1):
        """Build LoRaWAN data uplink frame"""
        mhdr = bytes([0x80 if confirmed else 0x40])
        dev_addr_le = self.dev_addr[::-1]
        fctrl = bytes([0x00])
        fcnt = struct.pack('<H', self.fcnt_up & 0xFFFF)
        
        fhdr = dev_addr_le + fctrl + fcnt
        fport = bytes([port])
        frm_payload = self.encrypt_payload(payload, self.fcnt_up)
        
        # Calculate MIC
        b0 = bytes([0x49, 0x00, 0x00, 0x00, 0x00, 0x00]) + self.dev_addr + struct.pack('<I', self.fcnt_up) + bytes([0x00, len(fhdr) + len(fport) + len(frm_payload)])
        msg_for_mic = b0 + mhdr + fhdr + fport + frm_payload
        mic = self.calculate_mic(self.nwk_s_key, msg_for_mic)
        
        return mhdr + fhdr + fport + frm_payload + mic
    
    def send_data(self, data, confirmed=False, port=1):
        """Send uplink data"""
        if not self.joined:
            print("Not joined! Call join() first.")
            return False
        
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        frame = self.build_data_frame(data, confirmed=confirmed, port=port)
        
        print(f"\n=== Sending Data ===")
        print(f"Payload: {data}")
        print(f"FCnt: {self.fcnt_up}")
        print(f"Frame: {binascii.hexlify(frame).decode()}")
        
        self.radio.transmit(frame)
        self.fcnt_up += 1
        
        print("Data sent successfully!")
        return True
    
    def cleanup(self):
        """Cleanup"""
        self.radio.cleanup()
