# LoRa P2P Quick Reference

## How LoRa P2P Works (Simple Explanation)

1. **Direct Communication**: Two modules talk directly to each other (no gateway needed)
2. **Half-Duplex**: One sends, one receives (can't do both at same time)
3. **Must Match**: Both modules need identical settings (frequency, SF, BW, etc.)
4. **Chirp Spread Spectrum**: Uses frequency "chirps" to encode data - very robust!

## Key Parameters (Must Match!)

```
Frequency:        433.0 MHz  (or 868.0, 915.0 based on region)
Spreading Factor: 7          (6-12, higher = longer range but slower)
Bandwidth:        125 kHz    (standard, lower = longer range)
Coding Rate:      4/5        (error correction, 4/5 to 4/8)
Sync Word:        0x12       (filter to ignore other LoRa devices)
TX Power:         14 dBm     (2-20, higher = longer range)
```

## Typical Range

- **Indoors**: 50-200 meters (through walls)
- **Outdoors LOS**: 2-5 km (line of sight)
- **Optimal**: 10-15 km (rural, clear line of sight)

## Range vs Speed Trade-off

| Spreading Factor | Range | Speed | Use Case |
|-----------------|-------|-------|----------|
| SF6 | Short | Fast | Close range, high data rate |
| SF7 | Medium | Medium | **Good default** |
| SF9 | Long | Slow | Long range, low data rate |
| SF12 | Very Long | Very Slow | Maximum range |

## Common Frequencies by Region

- **433 MHz**: Europe, Asia (check local regulations)
- **868 MHz**: Europe (license-free, power limited)
- **915 MHz**: North America (license-free, power limited)

## Testing Checklist

- [ ] SPI enabled on Raspberry Pi
- [ ] Wiring correct (especially CS, MOSI, MISO, SCK)
- [ ] Power supply 3.3V (not 5V!)
- [ ] Antennas connected
- [ ] Parameters match exactly on both modules
- [ ] Start close together (1-2 meters)
- [ ] Both modules powered on

## Quick Test Commands

```bash
# Test hardware
python3 test_lora_basic.py

# Run receiver (Terminal 1)
python3 lora_p2p_receiver.py

# Run sender (Terminal 2)
python3 lora_p2p_sender.py
```

## If Nothing Works

1. Run `test_lora_basic.py` first - verifies hardware
2. Check SPI: `lsmod | grep spi` and `ls -l /dev/spi*`
3. Verify parameters match EXACTLY
4. Check wiring with multimeter
5. Try different CS pin (GPIO 7 or 8)
6. Start with modules touching (eliminate range issues)
