# 🚗 CARLA Simulation - Quick Start Guide

## ⚡ Fastest Way to Run CARLA Simulations

### Step 1: Install CARLA

**Windows:**
1. Download from: https://github.com/carla-simulator/carla/releases
2. Extract to: `C:\CARLA\WindowsNoEditor`
3. Run: `C:\CARLA\WindowsNoEditor\CarlaUE4.exe`

**Linux:**
```bash
# Download and extract
wget https://github.com/carla-simulator/carla/releases/download/0.9.15/CARLA_0.9.15.tar.gz
tar -xzf CARLA_0.9.15.tar.gz
cd CARLA_0.9.15
./CarlaUE4.sh
```

### Step 2: Install CARLA Python API

```bash
# Activate your environment
conda activate vta  # or your environment

# Install CARLA
pip install carla
```

### Step 3: Start CARLA Server

**Terminal 1 - Start CARLA:**
```bash
# Windows
C:\CARLA\WindowsNoEditor\CarlaUE4.exe -carla-rpc-port=2000

# Linux
./CARLA/CarlaUE4.sh -carla-rpc-port=2000
```

**Keep this terminal/window open!**

### Step 4: Run Your Simulation

**Terminal 2 - Run Simulation:**

#### Option A: Using the Helper Script (Easiest)
```bash
cd F:\DRIVING-TEST-SIMULATION
conda activate vta
python scripts/run_carla_simulation.py
```

The script will:
- Check if CARLA is installed
- Check if CARLA server is running
- List available simulations
- Let you select and run one

#### Option B: Direct Execution
```bash
cd F:\DRIVING-TEST-SIMULATION
conda activate vta
python sim_output/carla/ef6c0832-ebd7-41cb-861d-b2c30ca3655a.py
```

#### Option C: Run All Simulations
```bash
for script in sim_output/carla/*.py; do
    echo "Running: $script"
    python "$script"
    sleep 5
done
```

---

## 🎯 What You'll See

### CARLA Window
- 3D visualization of the simulation
- Vehicle moving in the environment
- Real-time rendering

### Console Output
```
Spawned ego vehicle: vehicle.tesla.model3
Spawned 0 traffic vehicles
Running simulation for 30583.3 seconds...
Time: 1.0s | Position: (x, y) | Speed: 0.0 km/h
Time: 2.0s | Position: (x, y) | Speed: 5.2 km/h
...
Simulation completed
Actors cleaned up
Simulation finished
```

---

## ⚠️ Common Issues & Quick Fixes

### Issue: "Connection refused"
**Fix**: Make sure CARLA server is running (Step 3)

### Issue: "Module 'carla' not found"
**Fix**: 
```bash
pip install carla
```

### Issue: CARLA window doesn't open
**Fix**: 
- Check if you have enough RAM (8GB+)
- Try running in headless mode: `CarlaUE4.exe -carla-rpc-port=2000 -RenderOffScreen`

### Issue: "No spawn points available"
**Fix**: 
- Wait a few seconds for map to load
- Try a different CARLA map

---

## 📝 Example: Complete Run

```bash
# Terminal 1: Start CARLA
C:\CARLA\WindowsNoEditor\CarlaUE4.exe -carla-rpc-port=2000

# Terminal 2: Run Simulation
cd F:\DRIVING-TEST-SIMULATION
conda activate vta
python scripts/run_carla_simulation.py

# Select simulation number when prompted
# Watch the simulation run!
```

---

## 🔗 More Information

For detailed instructions, see: **CARLA_SIMULATION_GUIDE.md**

---

**That's it! You're ready to run CARLA simulations! 🚗💨**

