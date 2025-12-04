# Library Conflict Fix

## Problem

You have **`pyLoRa`** installed, but the code needs **`pySX127x`**. They have different APIs and are incompatible.

Your error:
```
Error initializing client: type object 'LoRa' has no attribute 'MODE'
```

This happens because `pyLoRa` has a different API than `pySX127x`.

## Solution

### Quick Fix (Recommended)

Run this script to automatically fix the issue:

```bash
sudo bash fix_library.sh
```

This will:
1. Remove the old `pyLoRa` package
2. Install the correct `pySX127x` package
3. Verify it works

### Manual Fix

If you prefer to do it manually:

```bash
# Step 1: Remove old library
sudo pip3 uninstall -y pyLoRa
sudo pip3 uninstall -y pySX127x

# Step 2: Clean up
sudo rm -rf /usr/local/lib/python3.9/dist-packages/pyLoRa*
sudo rm -rf /usr/local/lib/python3.9/dist-packages/SX127x*

# Step 3: Install correct library
cd /tmp
git clone https://github.com/rpsreal/pySX127x.git
cd pySX127x
sudo python3 setup.py install
cd ~

# Step 4: Verify
python3 check_library.py
```

### Verify the Fix

After running the fix:

```bash
python3 check_library.py
```

Should show:
```
✓ SX127x module found
✓ LoRa.MODE attribute exists
✓ This is pySX127x (COMPATIBLE)
```

## Why This Happened

There are two similar but incompatible libraries:

1. **`pyLoRa`** - Different project, different API
2. **`pySX127x`** - The one we need

When you installed dependencies, `pyLoRa` got installed instead of `pySX127x`.

## After Fixing

Once fixed, you can run:

```bash
sudo python3 test_connection.py
sudo python3 main.py
```

## Alternative: Check What You Have

```bash
# Check installed packages
pip3 list | grep -i lora

# Check SX127x location
python3 -c "import SX127x; print(SX127x.__file__)"
```

## If fix_library.sh Fails

Try the alternative repository:

```bash
cd /tmp
git clone https://github.com/mayeranalytics/pySX127x.git
cd pySX127x  
sudo python3 setup.py install
cd ~
```

---

**Run this now:** `sudo bash fix_library.sh`
