# ⚡ Quick Start: Run CARLA Simulation (dfaf323f-db0f-4014-93b3-a544618c798d.py)

## 🎯 You Have: CARLA 0.9.16 Downloaded

Follow these **4 simple steps**:

---

## Step 1: Install CARLA Python API

**Open PowerShell/Command Prompt:**

```powershell
# Activate your environment
conda activate vta

# Install CARLA Python API
pip install carla
```

**Verify it worked:**
```powershell
python -c "import carla; print('CARLA installed!')"
```

If you see an error, try:
```powershell
# Find your CARLA folder first, then:
pip install "C:\CARLA_0.9.16\PythonAPI\carla\dist\carla-0.9.16-py3.11-win-amd64.egg"
```

---

## Step 2: Start CARLA Server

**Open a NEW Terminal/PowerShell window:**

```powershell
# Navigate to your CARLA folder (adjust path to where you extracted it)
cd C:\CARLA_0.9.16

# Start CARLA
.\CarlaUE4.exe -carla-rpc-port=2000
```

**Wait for:**
- CARLA window to open (1-2 minutes)
- 3D environment to load
- **Keep this window open!**

---

## Step 3: Run Your Simulation

**In your ORIGINAL Terminal (where you installed CARLA):**

```powershell
# Make sure you're in the project directory
cd F:\DRIVING-TEST-SIMULATION

# Make sure environment is activated
conda activate vta

# Run your simulation
python sim_output\carla\dfaf323f-db0f-4014-93b3-a544618c798d.py
```

---

## Step 4: Watch It Run!

You'll see:
- **Terminal:** Progress messages every second
- **CARLA Window:** Vehicle moving in 3D environment

**To stop:** Press `Ctrl+C` in the terminal

---

## 🔍 Find Your CARLA Folder

If you don't know where CARLA is:

```powershell
# Search for it
Get-ChildItem -Path "C:\" -Filter "*CARLA*" -Directory -ErrorAction SilentlyContinue | Select-Object FullName
Get-ChildItem -Path "$env:USERPROFILE\Downloads" -Filter "*carla*" -Directory -ErrorAction SilentlyContinue | Select-Object FullName
```

Or use the helper script:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup_carla_0.9.16.ps1
```

---

## ⚠️ Common Issues

### "Module 'carla' not found"
→ Run: `pip install carla`

### "Connection refused"
→ Make sure CARLA server is running (Step 2)
→ Wait 30-60 seconds after starting CARLA

### CARLA won't start
→ Check you have 8GB+ RAM
→ Update graphics drivers

---

## 📋 Complete Example

**Terminal 1 (CARLA Server):**
```powershell
cd C:\CARLA_0.9.16
.\CarlaUE4.exe -carla-rpc-port=2000
```

**Terminal 2 (Run Simulation):**
```powershell
cd F:\DRIVING-TEST-SIMULATION
conda activate vta
python sim_output\carla\dfaf323f-db0f-4014-93b3-a544618c798d.py
```

---

## ✅ That's It!

Your simulation will run for ~8 hours. You can stop it anytime with `Ctrl+C`.

**For more details, see:** `CARLA_0.9.16_SETUP.md`

