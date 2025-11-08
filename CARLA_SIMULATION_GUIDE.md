# 🚗 CARLA Simulation Guide - Complete Setup & Run Instructions

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [CARLA Installation](#carla-installation)
4. [Python Environment Setup](#python-environment-setup)
5. [Running CARLA Simulations](#running-carla-simulations)
6. [Understanding Generated Scripts](#understanding-generated-scripts)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Usage](#advanced-usage)

---

## 🎯 Overview

VTA generates CARLA simulation scripts that can be executed to run virtual automotive tests. This guide will help you:

- Install and set up CARLA
- Configure your Python environment
- Run the generated simulation scripts
- Understand and customize simulations

---

## ✅ Prerequisites

### System Requirements

- **Operating System**: Windows 10/11, Linux (Ubuntu 18.04+), or macOS
- **RAM**: 8GB minimum, 16GB recommended
- **GPU**: NVIDIA GPU with 4GB+ VRAM (recommended for better performance)
- **Disk Space**: 20GB+ for CARLA installation
- **Python**: 3.7 - 3.11 (CARLA supports these versions)

### Software Requirements

- **CARLA Simulator**: Latest version (0.9.15+ recommended)
- **Python 3.7-3.11**: With pip
- **CARLA Python API**: Installed via pip

---

## 📦 CARLA Installation

### Option 1: Pre-compiled Binary (Easiest - Recommended)

#### Windows

1. **Download CARLA**:
   ```powershell
   # Visit: https://github.com/carla-simulator/carla/releases
   # Download: CARLA_0.9.15.zip (or latest version)
   ```

2. **Extract CARLA**:
   ```powershell
   # Extract to: C:\CARLA (or your preferred location)
   # Example: C:\CARLA\WindowsNoEditor
   ```

3. **Verify Installation**:
   ```powershell
   cd C:\CARLA\WindowsNoEditor
   .\CarlaUE4.exe
   # CARLA should launch (this may take a few minutes)
   ```

#### Linux

1. **Download CARLA**:
   ```bash
   # Visit: https://github.com/carla-simulator/carla/releases
   # Download: CARLA_0.9.15.tar.gz
   ```

2. **Extract CARLA**:
   ```bash
   tar -xzf CARLA_0.9.15.tar.gz
   cd CARLA_0.9.15
   ```

3. **Install Dependencies**:
   ```bash
   sudo apt-get update
   sudo apt-get install -y \
       libomp5 \
       libpng16-16 \
       libjpeg8 \
       libtiff5 \
       libwebp6 \
       libcurl4 \
       libssl1.1 \
       libsdl2-2.0-0 \
       libsdl2-image-2.0-0 \
       libsdl2-ttf-2.0-0 \
       libsdl2-mixer-2.0-0
   ```

4. **Run CARLA**:
   ```bash
   ./CarlaUE4.sh
   ```

#### macOS

1. **Download CARLA**:
   ```bash
   # Visit: https://github.com/carla-simulator/carla/releases
   # Download: CARLA_0.9.15.dmg
   ```

2. **Install CARLA**:
   - Open the .dmg file
   - Drag CARLA to Applications folder

3. **Run CARLA**:
   ```bash
   open /Applications/CARLA_0.9.15/CarlaUE4.app
   ```

### Option 2: Build from Source (Advanced)

If you need custom features, you can build CARLA from source. See: https://carla.readthedocs.io/en/latest/build_linux/

---

## 🐍 Python Environment Setup

### Step 1: Create Python Environment

```bash
# Using Conda (Recommended)
conda create -n carla python=3.9
conda activate carla

# OR using venv
python -m venv carla_env
# Windows:
carla_env\Scripts\activate
# Linux/Mac:
source carla_env/bin/activate
```

### Step 2: Install CARLA Python API

```bash
# Install carla package
pip install carla

# OR if you have CARLA installed locally, add the Python API to path
# Windows:
pip install -e "C:\CARLA\WindowsNoEditor\PythonAPI\carla\dist\carla-*.egg"

# Linux/Mac:
pip install -e "/path/to/CARLA/PythonAPI/carla/dist/carla-*.egg"
```

### Step 3: Install Additional Dependencies

```bash
# Install required packages
pip install numpy
pip install pygame  # For manual control (optional)
```

### Step 4: Verify Installation

```python
# Test CARLA import
python -c "import carla; print('CARLA version:', carla.__version__)"
```

---

## 🚀 Running CARLA Simulations

### Step 1: Start CARLA Server

**Important**: CARLA must be running before executing simulation scripts!

#### Windows:
```powershell
# Navigate to CARLA directory
cd C:\CARLA\WindowsNoEditor

# Start CARLA server
.\CarlaUE4.exe -carla-rpc-port=2000
```

#### Linux:
```bash
cd /path/to/CARLA
./CarlaUE4.sh -carla-rpc-port=2000
```

#### macOS:
```bash
open /Applications/CARLA_0.9.15/CarlaUE4.app --args -carla-rpc-port=2000
```

**Note**: 
- CARLA will open a window showing the simulation
- Keep this window open while running simulations
- Default port is 2000 (can be changed)

### Step 2: Run VTA Generated Simulation Script

#### Method 1: Direct Execution

```bash
# Navigate to your project
cd F:\DRIVING-TEST-SIMULATION

# Activate your environment (if using Conda)
conda activate vta  # or your CARLA environment

# Run the simulation script
python sim_output/carla/ef6c0832-ebd7-41cb-861d-b2c30ca3655a.py
```

#### Method 2: Using Python Module

```bash
# From project root
python -m sim_output.carla.ef6c0832-ebd7-41cb-861d-b2c30ca3655a
```

#### Method 3: Interactive Python

```python
# Start Python
python

# Import and run
exec(open('sim_output/carla/ef6c0832-ebd7-41cb-861d-b2c30ca3655a.py').read())
```

### Step 3: Monitor Simulation

While the simulation runs, you'll see:

1. **CARLA Window**: Visual simulation with vehicles
2. **Console Output**: Progress messages
   ```
   Spawned ego vehicle: vehicle.tesla.model3
   Spawned 0 traffic vehicles
   Running simulation for 30583.3 seconds...
   Time: 1.0s | Position: (x, y) | Speed: 0.0 km/h
   ...
   ```

3. **Simulation Data**: Vehicle states, positions, speeds

### Step 4: Stop Simulation

- **Normal Completion**: Script exits automatically when duration is reached
- **Manual Stop**: Press `Ctrl+C` in terminal
- **Close CARLA**: Close CARLA window (simulation will stop)

---

## 📝 Understanding Generated Scripts

### Script Structure

VTA generates CARLA scripts with this structure:

```python
#!/usr/bin/env python3
"""
CARLA Simulation Script: [Test Name]
Generated from VTA Test Scenario: [scenario_id]

Description: [Test description]
"""

import carla
import random
import time
import math

def main():
    """Main simulation function."""
    # 1. Connect to CARLA server
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    
    try:
        # 2. Get world
        world = client.get_world()
        
        # 3. Configure weather
        weather = carla.WeatherParameters(...)
        world.set_weather(weather)
        
        # 4. Spawn vehicles
        # - Ego vehicle (test vehicle)
        # - Traffic vehicles (if needed)
        
        # 5. Run simulation loop
        # - Collect data
        # - Monitor vehicle state
        # - Log metrics
        
        # 6. Cleanup
        # - Destroy vehicles
        # - Close connections
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Simulation finished")

if __name__ == '__main__':
    main()
```

### Key Components

#### 1. Connection Setup
```python
client = carla.Client('localhost', 2000)
client.set_timeout(10.0)
world = client.get_world()
```

#### 2. Weather Configuration
```python
weather = carla.WeatherParameters(
    cloudiness=10.0,
    precipitation=0.0,
    wind_intensity=5.0,
    sun_azimuth_angle=180.0,
    sun_altitude_angle=45.0
)
world.set_weather(weather)
```

#### 3. Vehicle Spawning
```python
# Get blueprint library
blueprint_library = world.get_blueprint_library()

# Select vehicle blueprint
ego_bp = blueprint_library.filter('vehicle.tesla.model3')[0]

# Get spawn points
spawn_points = world.get_map().get_spawn_points()

# Spawn vehicle
ego_vehicle = world.spawn_actor(ego_bp, spawn_points[0])
```

#### 4. Simulation Loop
```python
duration = 30583.3  # seconds
start_time = time.time()

while time.time() - start_time < duration:
    # Get vehicle state
    transform = ego_vehicle.get_transform()
    velocity = ego_vehicle.get_velocity()
    speed_kmh = 3.6 * math.sqrt(velocity.x**2 + velocity.y**2 + velocity.z**2)
    
    # Log data
    print(f"Time: {time.time() - start_time:.1f}s | "
          f"Position: ({transform.location.x:.1f}, {transform.location.y:.1f}) | "
          f"Speed: {speed_kmh:.1f} km/h")
    
    time.sleep(1.0)  # Update every second
```

---

## 🔧 Troubleshooting

### Issue 1: "Connection refused" or "Connection timeout"

**Problem**: CARLA server is not running or wrong port

**Solution**:
```bash
# 1. Make sure CARLA is running
# Check if CARLA window is open

# 2. Check port in script
# Default is 2000, make sure it matches

# 3. Try different port
client = carla.Client('localhost', 2000)  # Change if needed
```

### Issue 2: "Module 'carla' not found"

**Problem**: CARLA Python API not installed

**Solution**:
```bash
# Install carla package
pip install carla

# OR add CARLA Python API to path
# Windows:
set PYTHONPATH=%PYTHONPATH%;C:\CARLA\WindowsNoEditor\PythonAPI\carla\dist\carla-*.egg

# Linux/Mac:
export PYTHONPATH=$PYTHONPATH:/path/to/CARLA/PythonAPI/carla/dist/carla-*.egg
```

### Issue 3: "No spawn points available"

**Problem**: Map not loaded or no valid spawn points

**Solution**:
```python
# Check if map is loaded
map = world.get_map()
spawn_points = map.get_spawn_points()
print(f"Available spawn points: {len(spawn_points)}")

# If 0, try loading a different map
world = client.load_world('Town01')  # or Town02, Town03, etc.
```

### Issue 4: "Vehicle spawn failed"

**Problem**: Spawn point occupied or invalid blueprint

**Solution**:
```python
# Use try_spawn_actor instead of spawn_actor
vehicle = world.try_spawn_actor(bp, spawn_point)
if vehicle is None:
    print("Spawn failed, trying next spawn point")
    continue
```

### Issue 5: CARLA crashes or freezes

**Problem**: Insufficient resources or GPU issues

**Solution**:
```bash
# 1. Reduce quality settings
# In CARLA, go to Settings > Quality > Low

# 2. Run in headless mode (no graphics)
# Windows:
.\CarlaUE4.exe -carla-rpc-port=2000 -RenderOffScreen

# Linux:
./CarlaUE4.sh -carla-rpc-port=2000 -RenderOffScreen

# 3. Reduce simulation complexity
# - Fewer traffic vehicles
# - Shorter duration
# - Lower update frequency
```

### Issue 6: "ImportError: DLL load failed" (Windows)

**Problem**: Missing Visual C++ Redistributables

**Solution**:
```powershell
# Download and install:
# Microsoft Visual C++ 2015-2022 Redistributable (x64)
# From: https://aka.ms/vs/17/release/vc_redist.x64.exe
```

---

## 🎮 Advanced Usage

### Customizing Simulations

#### 1. Change Vehicle Model

```python
# Instead of Tesla Model 3
ego_bp = blueprint_library.filter('vehicle.tesla.model3')[0]

# Use different vehicle
ego_bp = blueprint_library.filter('vehicle.audi.a2')[0]
# or
ego_bp = blueprint_library.filter('vehicle.nissan.patrol')[0]
```

#### 2. Add Traffic Vehicles

```python
# Spawn multiple traffic vehicles
traffic_vehicles = []
vehicle_bps = blueprint_library.filter('vehicle.*')

for i in range(10):  # Spawn 10 traffic vehicles
    if i + 1 < len(spawn_points):
        bp = random.choice(vehicle_bps)
        vehicle = world.try_spawn_actor(bp, spawn_points[i + 1])
        if vehicle:
            traffic_vehicles.append(vehicle)
            vehicle.set_autopilot(True)  # Enable autopilot
```

#### 3. Custom Weather Conditions

```python
# Rainy weather
weather = carla.WeatherParameters(
    cloudiness=80.0,
    precipitation=50.0,
    precipitation_deposits=50.0,
    wind_intensity=20.0
)

# Foggy weather
weather = carla.WeatherParameters(
    fog_density=50.0,
    fog_distance=100.0
)

# Clear sunny day
weather = carla.WeatherParameters(
    cloudiness=0.0,
    precipitation=0.0,
    sun_azimuth_angle=0.0,
    sun_altitude_angle=90.0
)
```

#### 4. Collect Sensor Data

```python
# Add camera sensor
camera_bp = blueprint_library.find('sensor.camera.rgb')
camera_bp.set_attribute('image_size_x', '1920')
camera_bp.set_attribute('image_size_y', '1080')
camera = world.spawn_actor(camera_bp, transform, attach_to=ego_vehicle)

# Add callback to save images
def save_image(image):
    image.save_to_disk('output/%06d.png' % image.frame)

camera.listen(save_image)
```

#### 5. Custom Physics

```python
# Modify vehicle physics
physics_control = ego_vehicle.get_physics_control()
physics_control.mass = 2000.0  # kg
physics_control.drag_coefficient = 0.3
ego_vehicle.apply_physics_control(physics_control)
```

### Running Multiple Simulations

```bash
# Run all simulations in directory
for script in sim_output/carla/*.py; do
    echo "Running: $script"
    python "$script"
    sleep 5  # Wait between simulations
done
```

### Batch Processing

```python
# Create batch runner script
import os
import subprocess

carla_dir = "sim_output/carla"
scripts = [f for f in os.listdir(carla_dir) if f.endswith('.py')]

for script in scripts:
    script_path = os.path.join(carla_dir, script)
    print(f"Running {script}...")
    result = subprocess.run(['python', script_path], capture_output=True)
    if result.returncode == 0:
        print(f"✓ {script} completed successfully")
    else:
        print(f"✗ {script} failed: {result.stderr}")
```

---

## 📊 Data Collection

### Saving Simulation Data

Modify the script to save data:

```python
import json
import csv

# Collect data during simulation
data = []

while time.time() - start_time < duration:
    transform = ego_vehicle.get_transform()
    velocity = ego_vehicle.get_velocity()
    
    data.append({
        'timestamp': time.time() - start_time,
        'x': transform.location.x,
        'y': transform.location.y,
        'z': transform.location.z,
        'speed': 3.6 * math.sqrt(velocity.x**2 + velocity.y**2 + velocity.z**2)
    })
    
    time.sleep(1.0)

# Save to JSON
with open('simulation_data.json', 'w') as f:
    json.dump(data, f, indent=2)

# Save to CSV
with open('simulation_data.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
```

---

## 🔗 Useful Resources

### Official Documentation
- **CARLA Documentation**: https://carla.readthedocs.io/
- **CARLA GitHub**: https://github.com/carla-simulator/carla
- **CARLA Forum**: https://github.com/carla-simulator/carla/discussions

### Quick Reference

#### Available Maps
- `Town01` - Small town
- `Town02` - Small town (different layout)
- `Town03` - Large town
- `Town04` - Highway
- `Town05` - Square city block
- `Town06` - Long highway
- `Town07` - Rural environment
- `Town10` - Urban environment

#### Common Vehicle Blueprints
- `vehicle.tesla.model3`
- `vehicle.audi.a2`
- `vehicle.nissan.patrol`
- `vehicle.bmw.grandtourer`
- `vehicle.mercedes.coupe`
- `vehicle.lincoln.mkz2017`

---

## ✅ Quick Start Checklist

- [ ] CARLA installed and running
- [ ] Python environment set up with CARLA API
- [ ] CARLA server started (port 2000)
- [ ] Simulation script ready (`sim_output/carla/*.py`)
- [ ] Run script: `python sim_output/carla/your_script.py`
- [ ] Monitor simulation in CARLA window
- [ ] Check console output for progress

---

## 🎯 Example: Complete Run

```bash
# Terminal 1: Start CARLA
cd C:\CARLA\WindowsNoEditor
.\CarlaUE4.exe -carla-rpc-port=2000

# Terminal 2: Run Simulation
cd F:\DRIVING-TEST-SIMULATION
conda activate vta
python sim_output/carla/ef6c0832-ebd7-41cb-861d-b2c30ca3655a.py

# Expected Output:
# Spawned ego vehicle: vehicle.tesla.model3
# Spawned 0 traffic vehicles
# Running simulation for 30583.3 seconds...
# Time: 1.0s | Position: (x, y) | Speed: 0.0 km/h
# ...
# Simulation completed
# Actors cleaned up
# Simulation finished
```

---

**Happy Simulating! 🚗💨**

For issues or questions, check the troubleshooting section or CARLA documentation.

