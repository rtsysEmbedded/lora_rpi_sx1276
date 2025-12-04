# Helium Modem Pin Configuration

## Your Helium Modem Pin Mapping

Based on your module's pin configuration:

| Function | Wiring Pi Pin | BCM GPIO | Physical Pin | Usage |
|----------|---------------|----------|--------------|-------|
| NSS (CS) | 22 | **6** | Pin 31 | Chip Select (SPI) |
| RESET | 21 | **5** | Pin 29 | Reset pin |
| DIO0 | 24 | **19** | Pin 35 | Interrupt (optional) |
| DIO1 | 28 | **20** | Pin 38 | Not used |
| DIO2 | 29 | **21** | Pin 40 | Not used |
| MOSI | - | **10** | Pin 19 | SPI Data Out |
| MISO | - | **9** | Pin 21 | SPI Data In |
| SCLK | - | **11** | Pin 23 | SPI Clock |

## Raspberry Pi 3 Connection

```
Helium Modem    →    BCM GPIO    →    Physical Pin
─────────────────────────────────────────────────────
VCC (3.3V)      →    3.3V        →    Pin 1
GND             →    GND          →    Pin 6
MOSI            →    GPIO 10      →    Pin 19
MISO            →    GPIO 9       →    Pin 21
SCLK            →    GPIO 11     →    Pin 23
NSS/CS          →    GPIO 6       →    Pin 31  ⚠ UPDATED
RST             →    GPIO 5       →    Pin 29  ⚠ UPDATED
DIO0            →    GPIO 19      →    Pin 35  (optional)
```

## Code Configuration

The code has been updated with these default pins:
- `NSS_PIN = 6` (was 8)
- `RST_PIN = 5` (was 25)
- `DIO0_PIN = 19` (was 2)

## Testing

Now run the test:

```bash
python3 lora_p2p_test.py test
```

The code will automatically use the correct pins (GPIO 6 for NSS, GPIO 5 for RST).

If you need to override (for testing other configurations):

```bash
python3 lora_p2p_test.py test --nss-pin 6 --rst-pin 5
```

## Physical Pin Reference (Raspberry Pi 3)

```
    3.3V  [1]  [2]  5V
   GPIO2  [3]  [4]  5V
   GPIO3  [5]  [6]  GND
   GPIO4  [7]  [8]  GPIO14
     GND  [9] [10]  GPIO15
  GPIO17 [11] [12]  GPIO18
  GPIO27 [13] [14]  GND
  GPIO22 [15] [16]  GPIO23
    3.3V [17] [18]  GPIO24
  GPIO10 [19] [20]  GND  ← MOSI
   GPIO9 [21] [22]  GPIO25  ← MISO
  GPIO11 [23] [24]  GPIO8  ← SCLK
     GND [25] [26]  GPIO7
   GPIO0 [27] [28]  GPIO1
   GPIO5 [29] [30]  GND  ← RESET
   GPIO6 [31] [32]  GPIO12  ← NSS/CS
  GPIO13 [33] [34]  GND
  GPIO19 [35] [36]  GPIO16  ← DIO0
  GPIO26 [37] [38]  GPIO20
     GND [39] [40]  GPIO21
```

## Verification

After connecting, verify the pins are correct:

1. **Check SPI is enabled**:
   ```bash
   lsmod | grep spi
   ls -l /dev/spi*
   ```

2. **Run test**:
   ```bash
   python3 lora_p2p_test.py test
   ```

3. **Expected output** (if working):
   ```
   Version Register: 0x12 (or 0x11, 0x13)
   Operation Mode: 0x81
   Frequency: 868.100 MHz
   ```

## Troubleshooting

If you still get version 0x00:

1. **Double-check NSS pin**: Should be GPIO 6 (Pin 31), not GPIO 8
2. **Double-check RST pin**: Should be GPIO 5 (Pin 29), not GPIO 25
3. **Verify SPI connections**: MOSI (GPIO 10), MISO (GPIO 9), SCLK (GPIO 11)
4. **Check power**: 3.3V on Pin 1, GND on Pin 6
