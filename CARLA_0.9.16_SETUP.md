# 🚗 CARLA 0.9.16 Setup & Run Guide

## ✅ Step-by-Step Instructions for CARLA 0.9.16

### Step 1: Locate Your CARLA Installation

Your CARLA 0.9.16 should be extracted somewhere. Common locations:
- `C:\CARLA_0.9.16\`
- `C:\CARLA\`
- `C:\Users\YourName\Downloads\CARLA_0.9.16\`
- `C:\Program Files\CARLA_0.9.16\`

**Find it:**
```powershell
# Search for CARLA folder
Get-ChildItem -Path "C:\" -Filter "*CARLA*" -Directory -Recurse -ErrorAction SilentlyContinue | Select-Object FullName
```

### Step 2: Verify CARLA Structure

Your CARLA folder should contain:
```
CARLA_0.9.16/
├── CarlaUE4.exe          (Windows executable)
├── PythonAPI/
│   └── carla/
│       └── dist/
│           └── carla-0.9.16-*.egg  (Python API)
├── Import/
├── Content/
└── ... (other files)
```

### Step 3: Install CARLA Python API

**Option A: Using pip (Easiest)**
```powershell
# Activate your VTA environment
conda activate vta

# Install CARLA Python API
pip install carla
```

**Option B: Install from Local CARLA Installation**
```powershell
# Navigate to CARLA PythonAPI
cd C:\CARLA_0.9.16\PythonAPI\carla\dist

# Find the .egg file
Get-ChildItem *.egg

# Install it (replace with actual filename)
pip install carla-0.9.16-py3.11-win-amd64.egg
# OR
pip install -e "C:\CARLA_0.9.16\PythonAPI\carla\dist\carla-0.9.16-py3.11-win-amd64.egg"
```

**Option C: Add to PYTHONPATH**
```powershell
# Temporarily (for current session)
$env:PYTHONPATH = "C:\CARLA_0.9.16\PythonAPI\carla\dist\carla-0.9.16-py3.11-win-amd64.egg;$env:PYTHONPATH"

# Permanently (add to system)
[Environment]::SetEnvironmentVariable("PYTHONPATH", "C:\CARLA_0.9.16\PythonAPI\carla\dist\carla-0.9.16-py3.11-win-amd64.egg", "User")
```

### Step 4: Verify CARLA Python API Installation

```powershell
# Activate environment
conda activate vta

# Test import
python -c "import carla; print('CARLA version:', carla.__version__)"
```

**Expected output:**
```
CARLA version: 0.9.16
```

If you see an error, go back to Step 3.

---

## 🚀 Running Your Simulation

### Step 5: Start CARLA Server

**Open Terminal 1 (PowerShell or Command Prompt):**

```powershell
# Navigate to CARLA directory (adjust path to your location)
cd C:\CARLA_0.9.16

# Start CARLA server
.\CarlaUE4.exe -carla-rpc-port=2000
```

**What to expect:**
- CARLA window will open (may take 1-2 minutes)
- You'll see a 3D environment
- Keep this window open!

**Alternative: Headless Mode (No Graphics)**
```powershell
.\CarlaUE4.exe -carla-rpc-port=2000 -RenderOffScreen
```

### Step 6: Run Your Simulation

**Open Terminal 2 (PowerShell or Command Prompt):**

```powershell
# Navigate to your project
cd F:\DRIVING-TEST-SIMULATION

# Activate environment
conda activate vta

# Run your specific simulation
python sim_output\carla\dfaf323f-db0f-4014-93b3-a544618c798d.py
```

**What to expect:**
```
Spawned ego vehicle: vehicle.tesla.model3
Spawned 0 traffic vehicles
Running simulation for 28980.3 seconds...
Time: 1.0s | Position: (x, y) | Speed: 0.0 km/h
Time: 2.0s | Position: (x, y) | Speed: 5.2 km/h
...
```

---

## 📋 Complete Command Sequence

### Terminal 1: Start CARLA
```powershell
cd C:\CARLA_0.9.16
.\CarlaUE4.exe -carla-rpc-port=2000
```

### Terminal 2: Run Simulation
```powershell
cd F:\DRIVING-TEST-SIMULATION
conda activate vta
python sim_output\carla\dfaf323f-db0f-4014-93b3-a544618c798d.py
```

---

## 🔍 Troubleshooting

### Issue: "Module 'carla' not found"

**Solution:**
```powershell
# Check if CARLA is in Python path
python -c "import sys; print('\n'.join(sys.path))"

# Install CARLA API
pip install carla

# OR add to PYTHONPATH
$env:PYTHONPATH = "C:\CARLA_0.9.16\PythonAPI\carla\dist\carla-0.9.16-py3.11-win-amd64.egg;$env:PYTHONPATH"
```

### Issue: "Connection refused" or "Connection timeout"

**Solution:**
1. Make sure CARLA server is running (Terminal 1)
2. Wait 30-60 seconds after starting CARLA for it to fully load
3. Check the port matches (default: 2000)

### Issue: "No spawn points available"

**Solution:**
```python
# The script will handle this, but if it persists:
# Wait a few more seconds for the map to load
# Or modify the script to load a specific map:
world = client.load_world('Town01')
```

### Issue: CARLA window doesn't open

**Solutions:**
1. Check if you have enough RAM (8GB+)
2. Try headless mode: `.\CarlaUE4.exe -RenderOffScreen`
3. Check Windows Event Viewer for errors
4. Update graphics drivers

### Issue: "DLL load failed" (Windows)

**Solution:**
Install Visual C++ Redistributables:
- Download: https://aka.ms/vs/17/release/vc_redist.x64.exe
- Install and restart

---

## 🎯 Quick Test Script

Create a test file to verify everything works:

**`test_carla_connection.py`:**
```python
import carla

try:
    # Connect to CARLA
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    
    # Get world
    world = client.get_world()
    print("✓ Successfully connected to CARLA!")
    print(f"✓ World: {world.get_map().name}")
    print(f"✓ Available spawn points: {len(world.get_map().get_spawn_points())}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    print("\nMake sure:")
    print("1. CARLA server is running (CarlaUE4.exe)")
    print("2. CARLA Python API is installed (pip install carla)")
```

**Run it:**
```powershell
python test_carla_connection.py
```

---

## 📊 Your Simulation Details

**File:** `dfaf323f-db0f-4014-93b3-a544618c798d.py`
- **Test Name:** Leaf_Thermal_Performance_Under_Load_Battery
- **Duration:** 28980.3 seconds (≈ 8 hours)
- **Vehicle:** Tesla Model 3 (representing EV)
- **Platform:** EV
- **Weather:** Clear (cloudiness: 10%, no precipitation)
- **Traffic:** 0 vehicles (just ego vehicle)

---

## ✅ Checklist

Before running, make sure:

- [ ] CARLA 0.9.16 is extracted to a known location
- [ ] CARLA Python API is installed (`pip install carla`)
- [ ] CARLA import works (`python -c "import carla"`)
- [ ] CARLA server is running (Terminal 1)
- [ ] VTA environment is activated (`conda activate vta`)
- [ ] You're in the project directory (`F:\DRIVING-TEST-SIMULATION`)

---

## 🚀 Ready to Run!

Once everything is set up:

1. **Terminal 1:** Start CARLA
   ```powershell
   cd C:\CARLA_0.9.16
   .\CarlaUE4.exe -carla-rpc-port=2000
   ```

2. **Terminal 2:** Run simulation
   ```powershell
   cd F:\DRIVING-TEST-SIMULATION
   conda activate vta
   python sim_output\carla\dfaf323f-db0f-4014-93b3-a544618c798d.py
   ```

3. **Watch:** CARLA window shows the simulation running!

---

## 📝 Notes

- **Simulation Duration:** ~8 hours (you can stop with Ctrl+C)
- **Data Collection:** The script prints position and speed every second
- **Stopping:** Press Ctrl+C in Terminal 2 to stop early
- **CARLA Window:** Close it to stop the server

---

**Need help? Check the troubleshooting section or see `CARLA_SIMULATION_GUIDE.md` for more details!**

