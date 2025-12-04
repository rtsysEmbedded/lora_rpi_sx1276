# ChirpStack Setup Guide

This guide walks you through registering your device in ChirpStack.

## Prerequisites

- ChirpStack installed and running locally
- Gateway connected to ChirpStack
- Web browser access to ChirpStack

## Step-by-Step Device Registration

### 1. Access ChirpStack Web Interface

Open your browser and navigate to:
```
http://localhost:8080
```

Default credentials (if not changed):
- Username: `admin`
- Password: `admin`

### 2. Create or Select an Application

1. Click on **Applications** in the left menu
2. Either:
   - Select an existing application, OR
   - Click **+ Create** to create a new one:
     - **Application name**: "My LoRa Devices" (or any name)
     - **Description**: Optional
     - Click **Submit**

3. Note down the **Application EUI** (also called JoinEUI):
   - Click on your application
   - You'll see the Application ID/EUI at the top
   - Copy this value and update `APP_EUI` in `config.py`

### 3. Create Device Profile

Before adding a device, you need a device profile:

1. Click on **Device Profiles** in the left menu
2. Click **+ Create**
3. Fill in the details:

   **General:**
   - **Name**: "SX1276_OTAA"
   - **Region**: Select your region (e.g., EU868, US915)
   - **MAC version**: 1.0.3 or 1.0.4
   - **Regional parameters revision**: A or B

   **Join (OTAA/ABP):**
   - ✓ Check **Device supports OTAA**
   
   **Class-B/C:**
   - Leave defaults (Class A)

   **Codec:**
   - Leave as "None" (or configure if you want payload decoding)

4. Click **Submit**

### 4. Register Your Device

1. Go back to **Applications** → **Your Application**
2. Click on **Devices** tab
3. Click **+ Add device**
4. Fill in the device details:

   **General:**
   - **Device name**: "RPi-LoRa-1" (or any name)
   - **Device description**: Optional
   - **Device EUI**: `0bbef9f59cc6986a` (your device EUI)
   - **Device profile**: Select "SX1276_OTAA" (created in step 3)

5. Click **Submit**

### 5. Configure Device Keys

After creating the device:

1. You'll be redirected to the device page
2. Click on **Keys (OTAA)** tab
3. You should see:
   - **Application key**: Enter `d8341a42c8894b3bb82d0f721a0fcdbc`
   - Click **Submit**

Alternatively, if the key field is empty:
- Click **Generate** to create a new key
- Copy the generated key
- Update `APP_KEY` in your `config.py` file

### 6. Verify Configuration

Your device page should now show:
- **Device EUI**: `0bbef9f59cc6986a`
- **Join EUI (AppEUI)**: (copied to your config.py)
- **Application Key**: `d8341a42c8894b3bb82d0f721a0fcdbc`
- **Activation**: OTAA
- **Device Profile**: SX1276_OTAA (or your profile name)

## Configuration Summary

Update your `config.py` with these values:

```python
DEVICE_EUI = "0bbef9f59cc6986a"
APP_KEY = "d8341a42c8894b3bb82d0f721a0fcdbc"
APP_EUI = "XXXXXXXXXXXXXXXX"  # From your application in ChirpStack
```

## Frequency Configuration

Make sure the frequency in `config.py` matches your gateway and region:

### EU868 (Europe)
```python
FREQUENCY = 868.1  # MHz
RX2_FREQUENCY = 869.525
```

### US915 (USA)
```python
FREQUENCY = 915.0  # MHz (or use sub-band channels)
RX2_FREQUENCY = 923.3
```

### AS923 (Asia)
```python
FREQUENCY = 923.2  # MHz
RX2_FREQUENCY = 923.2
```

## Testing the Connection

1. **Check Gateway Status:**
   - In ChirpStack, go to **Gateways**
   - Verify your gateway shows as "Connected" with green dot
   - Check "Last seen at" timestamp is recent

2. **Run the Application:**
   ```bash
   sudo python3 main.py
   ```

3. **Monitor in ChirpStack:**
   - Go to **Applications** → **Your Application** → **Your Device**
   - Click on **LoRaWAN frames** tab
   - You should see:
     - **Join-request**: Sent from device
     - **Join-accept**: Response from server
     - **Uplink**: Data frames

4. **View Data:**
   - Click on **Device data** tab
   - You should see decoded messages like "Hello from RPi! Count: 0"

## Troubleshooting

### Join Request Not Appearing

**Check Gateway:**
```bash
# On gateway machine
sudo journalctl -u chirpstack-gateway-bridge -f
```

You should see LoRa packets being received.

**Common Issues:**
- Gateway not connected to ChirpStack
- Wrong frequency configuration
- Out of range
- No antenna connected

### Join Accept Not Received

**Check Device Configuration:**
1. Device EUI matches: `0bbef9f59cc6986a`
2. Application Key matches: `d8341a42c8894b3bb82d0f721a0fcdbc`
3. Device profile region matches your gateway region
4. OTAA is enabled

**Check ChirpStack Logs:**
```bash
# On ChirpStack server
sudo journalctl -u chirpstack -f
```

Look for join-request processing and any errors.

### Data Not Appearing

**Check Frame Counter:**
- In device details, verify frame counter is incrementing
- If stuck, the device might not be receiving confirmations

**Check Application Integration:**
- Go to **Applications** → **Integrations**
- Add an integration to forward data (HTTP, MQTT, etc.)

## ChirpStack v3 vs v4 Differences

### ChirpStack v3:
- Uses **Application Server**, **Network Server**, **Gateway Bridge**
- APP_EUI required and displayed in application
- Separate components with different configuration files

### ChirpStack v4:
- Unified single binary
- APP_EUI might default to `0000000000000000`
- Simplified configuration
- Join EUI field replaces APP_EUI terminology

If using ChirpStack v4 and APP_EUI is not clear:
1. Try using `0000000000000000` as APP_EUI
2. Or check Join Server configuration in device profile

## Additional Resources

- [ChirpStack Documentation](https://www.chirpstack.io/docs/)
- [LoRaWAN Frequency Plans](https://www.thethingsnetwork.org/docs/lorawan/frequency-plans/)
- [LoRaWAN Regional Parameters](https://lora-alliance.org/resource_hub/rp2-1-0-3-lorawan-regional-parameters/)

## MQTT Integration (Optional)

To receive data in your own application:

1. Go to **Applications** → **Your Application**
2. Click on **Integrations** tab
3. Click **+ Add integration**
4. Select **MQTT**
5. Configure:
   - **Server**: `tcp://localhost:1883` (or your MQTT broker)
   - **Username**: (if required)
   - **Password**: (if required)

6. Subscribe to topics:
   ```bash
   mosquitto_sub -h localhost -t "application/+/device/+/event/up"
   ```

This will show all uplink messages in JSON format.

---

**Good luck with your LoRaWAN setup! 📡**
