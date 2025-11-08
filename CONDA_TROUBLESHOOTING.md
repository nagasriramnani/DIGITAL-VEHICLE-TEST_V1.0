# 🔧 Conda Troubleshooting Guide

**Common issues and solutions for Conda setup**

---

## Issue 1: 'conda' is not recognized

### Problem
```
'conda' is not recognized as an internal or external command,
operable program or batch file.
```

### Solutions

#### Solution A: Use Anaconda Prompt (Easiest)

**Windows:**
1. Press `Windows Key`
2. Search for "Anaconda Prompt" or "Anaconda PowerShell Prompt"
3. Open it (this has conda in PATH)
4. Navigate to project:
   ```cmd
   cd F:\DRIVING-TEST-SIMULATION
   ```
5. Now conda will work:
   ```cmd
   conda --version
   ```

#### Solution B: Add Conda to PATH

**Find Conda Installation:**
```cmd
# Common locations:
C:\Users\YourUsername\anaconda3
C:\Users\YourUsername\miniconda3
C:\ProgramData\Anaconda3
C:\ProgramData\Miniconda3
```

**Add to PATH:**
1. Press `Windows Key` → Search "Environment Variables"
2. Click "Edit the system environment variables"
3. Click "Environment Variables" button
4. Under "System variables", find "Path" → Click "Edit"
5. Click "New" and add:
   ```
   C:\Users\YourUsername\anaconda3
   C:\Users\YourUsername\anaconda3\Scripts
   C:\Users\YourUsername\anaconda3\Library\bin
   ```
   (Replace with your actual conda path)
6. Click OK on all dialogs
7. **Restart CMD/PowerShell** for changes to take effect

**Verify:**
```cmd
# Close and reopen CMD, then:
conda --version
```

#### Solution C: Initialize Conda in Current Shell

**If conda is installed but not initialized:**

```cmd
# Find conda installation
dir C:\Users\%USERNAME%\anaconda3\Scripts\conda.exe
# or
dir C:\ProgramData\Anaconda3\Scripts\conda.exe

# Initialize conda for CMD
C:\Users\YourUsername\anaconda3\Scripts\conda.exe init cmd.exe

# Close and reopen CMD
```

**For PowerShell:**
```powershell
C:\Users\YourUsername\anaconda3\Scripts\conda.exe init powershell
```

#### Solution D: Check if Conda is Installed

**Check common installation locations:**
```cmd
dir C:\Users\%USERNAME%\anaconda3
dir C:\Users\%USERNAME%\miniconda3
dir C:\ProgramData\Anaconda3
dir C:\ProgramData\Miniconda3
```

**If not found, install Conda:**
- Download Anaconda: https://www.anaconda.com/download
- Download Miniconda: https://docs.conda.io/en/latest/miniconda.html
- During installation, check "Add Anaconda to PATH"

---

## Issue 2: Conda Works in Anaconda Prompt but Not in Regular CMD

### Solution: Use Anaconda Prompt

**Always use Anaconda Prompt for conda commands:**
1. Open "Anaconda Prompt" from Start Menu
2. Navigate to project: `cd F:\DRIVING-TEST-SIMULATION`
3. Run all conda commands there

**Or initialize conda in your current shell:**
```cmd
# In Anaconda Prompt, run:
conda init cmd.exe
# Then close and reopen regular CMD
```

---

## Issue 3: Python Not Found After Activating Environment

### Problem
```cmd
conda activate vta
python --version
# 'python' is not recognized
```

### Solution

**Use full path or check activation:**
```cmd
# Verify environment is active (should show (vta) in prompt)
conda activate vta

# Check Python location
where python
# or
conda list python

# Try python3 instead
python3 --version
```

**Reinstall Python in environment:**
```cmd
conda activate vta
conda install python=3.11
```

---

## Issue 4: Package Installation Fails

### Problem
```cmd
pip install -r requirements.txt
# Errors during installation
```

### Solutions

**Update pip first:**
```cmd
conda activate vta
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Install packages one by one:**
```cmd
conda activate vta
pip install fastapi
pip install uvicorn
# etc.
```

**Use conda-forge channel:**
```cmd
conda activate vta
conda install -c conda-forge fastapi uvicorn
```

**Clear pip cache:**
```cmd
pip cache purge
pip install -r requirements.txt --no-cache-dir
```

---

## Issue 5: Environment Creation Fails

### Problem
```cmd
conda env create -f environment.yml
# Errors or hangs
```

### Solutions

**Check YAML syntax:**
```cmd
# Verify file exists and is readable
type environment.yml
```

**Create environment manually:**
```cmd
# Create base environment
conda create -n vta python=3.11

# Activate
conda activate vta

# Install from requirements.txt
pip install -r requirements.txt
```

**Update conda:**
```cmd
conda update conda
conda env create -f environment.yml
```

---

## Issue 6: Database Connection Errors

### Problem
```cmd
# Python can't connect to databases
Connection refused
```

### Solutions

**Check databases are running:**
```cmd
docker compose ps
```

**Start databases:**
```cmd
docker compose up -d postgres neo4j redis
```

**Check connection strings in .env:**
```cmd
type .env
# Verify:
# NEO4J_URI=bolt://localhost:7687
# PG_CONN=postgresql+psycopg2://user:pass@localhost:5432/vta
```

**Test connections:**
```cmd
conda activate vta
python -c "from neo4j import GraphDatabase; driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'your_password')); driver.verify_connectivity(); print('Neo4j OK')"
```

---

## Issue 7: Port Already in Use

### Problem
```cmd
# Error: Address already in use
```

### Solutions

**Find process using port:**
```cmd
# Windows PowerShell
Get-NetTCPConnection -LocalPort 8000 | Select-Object OwningProcess

# Windows CMD
netstat -ano | findstr :8000
```

**Kill process:**
```cmd
# Find PID from above, then:
taskkill /PID <ProcessID> /F
```

**Or change port:**
```cmd
# Run on different port
uvicorn src.api.main:app --reload --port 8001
```

---

## Quick Diagnostic Commands

**Check conda installation:**
```cmd
where conda
dir C:\Users\%USERNAME%\anaconda3
dir C:\ProgramData\Anaconda3
```

**Check Python:**
```cmd
where python
python --version
```

**Check environment:**
```cmd
conda env list
conda info --envs
```

**Check packages:**
```cmd
conda activate vta
conda list
pip list
```

---

## Alternative: Use Python venv Instead

**If conda continues to cause issues, use Python venv:**

```cmd
# Check Python is installed
python --version

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
uvicorn src.api.main:app --reload
```

---

## Getting Help

**Still having issues?**

1. **Check conda installation:**
   - Open Anaconda Prompt
   - Run: `conda --version`

2. **Verify environment:**
   - Run: `conda env list`
   - Should see "vta" environment

3. **Check logs:**
   - Look for error messages
   - Check Docker logs: `docker compose logs`

4. **Common fixes:**
   - Restart terminal/CMD
   - Restart computer
   - Reinstall conda
   - Use Anaconda Prompt instead of regular CMD

---

**Last Updated**: Phase 10 Complete  
**Tested On**: Windows 10/11, Anaconda 2023.x+

