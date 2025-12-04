#!/usr/bin/env python3
"""
LoRaWAN Client for Raspberry Pi with SX1276 module
Connects to ChirpStack gateway using OTAA
"""

import time
import struct
import sys
import os

# Add current directory to path to use local board_config
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from SX127x.LoRa import LoRa
import board_config
BOARD = board_config.BOARD

from Crypto.Cipher import AES
from Crypto.Hash import CMAC
import binascii
import random


class LoRaWANClient(LoRa):
    """LoRaWAN OTAA client implementation for SX1276"""
    
    def __init__(self, device_eui, app_eui, app_key, frequency=868.1):
        """Initialize LoRaWAN client
        
        Args:
            device_eui: Device EUI as hex string
            app_eui: Application EUI as hex string  
            app_key: Application Key as hex string
            frequency: Frequency in MHz
        """
        # Initialize board and parent LoRa class
        BOARD.setup()
        super().__init__(verbose=False)
        
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
        
        # Configure radio
        self.set_mode(LoRa.MODE.SLEEP)
        self.set_freq(frequency)
        self.set_pa_config(pa_select=1, max_power=0x0F, output_power=0x0E)
        self.set_spreading_factor(7)
        self.set_bw(LoRa.BW.BW125)
        self.set_coding_rate(LoRa.CODING_RATE.CR4_5)
        self.set_preamble(8)
        self.set_sync_word(0x34)  # LoRaWAN sync word
        self.set_rx_crc(True)
        
        # Set explicit header mode
        self.set_implicit_header_mode(False)
        
        print(f"LoRaWAN Client initialized")
        print(f"DevEUI: {device_eui}")
        print(f"Frequency: {frequency} MHz")
    
    def aes128_encrypt(self, key, data):
        """AES-128 ECB encryption"""
        cipher = AES.new(key, AES.MODE_ECB)
        return cipher.encrypt(data)
    
    def calculate_mic(self, key, data):
        """Calculate LoRaWAN MIC (Message Integrity Code)"""
        cobj = CMAC.new(key, ciphermod=AES)
        cobj.update(data)
        return cobj.digest()[:4]
    
    def generate_join_request(self):
        """Generate LoRaWAN Join Request message"""
        # MHDR: Join Request (0x00)
        mhdr = bytes([0x00])
        
        # Join Request payload: AppEUI (LE) + DevEUI (LE) + DevNonce (2 bytes)
        app_eui_le = self.app_eui[::-1]  # Little endian
        dev_eui_le = self.dev_eui[::-1]  # Little endian
        dev_nonce = struct.pack('<H', random.randint(0, 65535))
        
        self.dev_nonce = dev_nonce
        
        # Build message for MIC calculation
        msg = mhdr + app_eui_le + dev_eui_le + dev_nonce
        
        # Calculate MIC
        mic = self.calculate_mic(self.app_key, msg)
        
        # Complete Join Request
        join_request = msg + mic
        
        return join_request
    
    def parse_join_accept(self, data):
        """Parse and decrypt Join Accept message"""
        if len(data) < 12:
            return False
        
        mhdr = data[0]
        encrypted = data[1:]
        
        # Decrypt Join Accept
        # Pad to 16 bytes if needed
        padded = encrypted + bytes(16 - len(encrypted) % 16)
        decrypted = self.aes128_encrypt(self.app_key, padded)
        decrypted = decrypted[:len(encrypted)]
        
        # Parse decrypted data
        app_nonce = decrypted[0:3]
        net_id = decrypted[3:6]
        dev_addr = decrypted[6:10]
        dl_settings = decrypted[10]
        rx_delay = decrypted[11]
        
        # Verify MIC (last 4 bytes)
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
        """Derive NwkSKey and AppSKey from Join Accept"""
        # NwkSKey = aes128_encrypt(AppKey, 0x01 | AppNonce | NetID | DevNonce | pad)
        nwk_s_key_msg = bytes([0x01]) + app_nonce + net_id + dev_nonce + bytes(7)
        self.nwk_s_key = self.aes128_encrypt(self.app_key, nwk_s_key_msg)
        
        # AppSKey = aes128_encrypt(AppKey, 0x02 | AppNonce | NetID | DevNonce | pad)
        app_s_key_msg = bytes([0x02]) + app_nonce + net_id + dev_nonce + bytes(7)
        self.app_s_key = self.aes128_encrypt(self.app_key, app_s_key_msg)
        
        print(f"NwkSKey: {binascii.hexlify(self.nwk_s_key).decode()}")
        print(f"AppSKey: {binascii.hexlify(self.app_s_key).decode()}")
    
    def join(self, timeout=30):
        """Perform OTAA join procedure"""
        print("\n=== Starting OTAA Join ===")
        
        join_request = self.generate_join_request()
        print(f"Sending Join Request: {binascii.hexlify(join_request).decode()}")
        
        # Send Join Request
        self.transmit(join_request)
        
        # Wait for Join Accept
        print("Waiting for Join Accept...")
        start_time = time.time()
        
        # Listen on RX1 window (1 second delay)
        time.sleep(1)
        
        while time.time() - start_time < timeout:
            payload = self.receive(timeout=5)
            
            if payload and len(payload) > 0:
                print(f"Received: {binascii.hexlify(bytes(payload)).decode()}")
                
                # Check if it's a Join Accept (MHDR = 0x20)
                if payload[0] == 0x20:
                    if self.parse_join_accept(bytes(payload)):
                        self.joined = True
                        print("=== Join Successful! ===\n")
                        return True
            
            time.sleep(0.5)
        
        print("Join failed: timeout")
        return False
    
    def transmit(self, payload):
        """Transmit data"""
        self.set_mode(LoRa.MODE.STDBY)
        self.set_payload(list(payload))
        self.set_mode(LoRa.MODE.TX)
        
        # Wait for TX done
        while (self.get_irq_flags()['tx_done'] == 0):
            time.sleep(0.01)
        
        self.clear_irq_flags(TxDone=1)
        self.set_mode(LoRa.MODE.STDBY)
    
    def receive(self, timeout=10):
        """Receive data"""
        self.set_mode(LoRa.MODE.STDBY)
        self.reset_ptr_rx()
        self.set_mode(LoRa.MODE.RXCONT)
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.get_irq_flags()['rx_done']:
                payload = self.read_payload(nocheck=True)
                self.clear_irq_flags(RxDone=1)
                self.set_mode(LoRa.MODE.STDBY)
                return payload
            time.sleep(0.1)
        
        self.set_mode(LoRa.MODE.STDBY)
        return None
    
    def encrypt_payload(self, data, fcnt):
        """Encrypt payload using AppSKey"""
        k = len(data) // 16 + 1
        s = b''
        
        for i in range(k):
            a = bytes([0x01, 0x00, 0x00, 0x00, 0x00, 0x00]) + self.dev_addr + struct.pack('<I', fcnt) + bytes([0x00, i + 1])
            s += self.aes128_encrypt(self.app_s_key, a)
        
        encrypted = bytes([data[i] ^ s[i] for i in range(len(data))])
        return encrypted
    
    def build_data_frame(self, payload, confirmed=False, port=1):
        """Build LoRaWAN data uplink frame"""
        # MHDR: Unconfirmed Data Up (0x40) or Confirmed Data Up (0x80)
        mhdr = bytes([0x80 if confirmed else 0x40])
        
        # FHDR: DevAddr (LE) + FCtrl + FCnt
        dev_addr_le = self.dev_addr[::-1]
        fctrl = bytes([0x00])  # No options
        fcnt = struct.pack('<H', self.fcnt_up & 0xFFFF)
        
        fhdr = dev_addr_le + fctrl + fcnt
        
        # FPort
        fport = bytes([port])
        
        # Encrypt payload
        frm_payload = self.encrypt_payload(payload, self.fcnt_up)
        
        # Build message for MIC
        b0 = bytes([0x49, 0x00, 0x00, 0x00, 0x00, 0x00]) + self.dev_addr + struct.pack('<I', self.fcnt_up) + bytes([0x00, len(fhdr) + len(fport) + len(frm_payload)])
        msg_for_mic = b0 + mhdr + fhdr + fport + frm_payload
        
        # Calculate MIC
        mic = self.calculate_mic(self.nwk_s_key, msg_for_mic)
        
        # Complete frame
        frame = mhdr + fhdr + fport + frm_payload + mic
        
        return frame
    
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
        
        self.transmit(frame)
        self.fcnt_up += 1
        
        print("Data sent successfully!")
        return True
    
    def cleanup(self):
        """Cleanup GPIO"""
        self.set_mode(LoRa.MODE.SLEEP)
        BOARD.teardown()
