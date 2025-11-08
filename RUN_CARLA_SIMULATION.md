# 🚀 Quick Guide: Run Your CARLA Simulation

## ✅ You Have: CARLA 0.9.16 Downloaded

Follow these steps to run: `dfaf323f-db0f-4014-93b3-a544618c798d.py`

---

## 📍 Step 1: Find Your CARLA Folder

Your CARLA 0.9.16 should be extracted somewhere. Common locations:
- `C:\CARLA_0.9.16\`
- `C:\CARLA\`
- `C:\Users\YourName\Downloads\CARLA_0.9.16\`

**Quick Find:**
```powershell
# Run this helper script
powershell -ExecutionPolicy Bypass -File .\scripts\setup_carla_0.9.16.ps1
```

This will:
- Find your CARLA installation
- Check Python API setup
- Guide you through installation

---

## 🔧 Step 2: Install CARLA Python API

**Open PowerShell/Command Prompt:**

```powershell
# Activate your environment
conda activate vta

# Option A: Install from PyPI (Easiest)
pip install carla

# Option B: If Option A doesn't work, install from local CARLA
# First, find the .egg file in: C:\CARLA_0.9.16\PythonAPI\carla\dist\
pip install "C:\CARLA_0.9.16\PythonAPI\carla\dist\carla-0.9.16-py3.11-win-amd64.egg"
```

**Verify Installation:**
```powershell
python -c "import carla; print('CARLA version:', carla.__version__)"
```

Should show: `CARLA version: 0.9.16`

---

## 🚀 Step 3: Start CARLA Server

**Open Terminal 1 (PowerShell):**

```powershell
# Navigate to your CARLA folder (adjust path)
cd C:\CARLA_0.9.16

# Start CARLA
.\CarlaUE4.exe -carla-rpc-port=2000
```

**What happens:**
- CARLA window opens (takes 1-2 minutes)
- You'll see a 3D environment
- **Keep this window open!**

---

## ▶️ Step 4: Run Your Simulation

**Open Terminal 2 (PowerShell):**

```powershell
# Navigate to project
cd F:\DRIVING-TEST-SIMULATION

# Activate environment
conda activate vta

# Run your simulation
python sim_output\carla\dfaf323f-db0f-4014-93b3-a544618c798d.py
```

---

## 📊 What You'll See

### Terminal Output:
```
Spawned ego vehicle: vehicle.tesla.model3
Spawned 0 traffic vehicles
Running simulation for 28980.3 seconds...
Time: 1.0s | Position: (x, y) | Speed: 0.0 km/h
Time: 2.0s | Position: (x, y) | Speed: 5.2 km/h
Time: 3.0s | Position: (x, y) | Speed: 8.5 km/h
...
```

### CARLA Window:
- 3D visualization
- Vehicle moving in environment
- Real-time rendering

---

## ⚠️ Troubleshooting

### "Module 'carla' not found"
```powershell
pip install carla
# OR
pip install "C:\CARLA_0.9.16\PythonAPI\carla\dist\carla-0.9.16-py3.11-win-amd64.egg"
```

### "Connection refused"
- Make sure CARLA server is running (Step 3)
- Wait 30-60 seconds after starting CARLA
- Check port is 2000

### "No spawn points available"
- Wait a few more seconds for map to load
- CARLA needs time to initialize

### CARLA won't start
- Check you have 8GB+ RAM
- Update graphics drivers
- Try headless: `.\CarlaUE4.exe -RenderOffScreen`

---

## 🎯 Complete Command Sequence

### Terminal 1:
```powershell
cd C:\CARLA_0.9.16
.\CarlaUE4.exe -carla-rpc-port=2000
```

### Terminal 2:
```powershell
cd F:\DRIVING-TEST-SIMULATION
conda activate vta
python sim_output\carla\dfaf323f-db0f-4014-93b3-a544618c798d.py
```

---

## 📝 Your Simulation Details

- **File:** `dfaf323f-db0f-4014-93b3-a544618c798d.py`
- **Test:** Leaf_Thermal_Performance_Under_Load_Battery
- **Duration:** 28980 seconds (≈ 8 hours)
- **Vehicle:** Tesla Model 3 (EV)
- **Weather:** Clear conditions

**Note:** Simulation runs for ~8 hours. You can stop it anytime with `Ctrl+C`

---

## ✅ Quick Checklist

- [ ] CARLA 0.9.16 extracted to a folder
- [ ] CARLA Python API installed (`pip install carla`)
- [ ] CARLA import works (`python -c "import carla"`)
- [ ] CARLA server running (Terminal 1)
- [ ] Ready to run simulation (Terminal 2)

---

## 🆘 Need Help?

1. **Run the setup helper:**
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\scripts\setup_carla_0.9.16.ps1
   ```

2. **See detailed guide:** `CARLA_0.9.16_SETUP.md`

3. **Test connection:**
   ```python
   # Create test_carla.py
   import carla
   client = carla.Client('localhost', 2000)
   client.set_timeout(10.0)
   world = client.get_world()
   print("✓ Connected!")
   ```

---

**Ready? Start with Step 1! 🚗💨**

