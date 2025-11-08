# ⚡ Conda Quick Start - 5 Minutes

**Get VTA running with Conda in 5 minutes!**

**⚠️ If you see "'conda' is not recognized":**
- **Use Anaconda Prompt** instead of regular CMD (easiest!)
- Or see [CONDA_TROUBLESHOOTING.md](CONDA_TROUBLESHOOTING.md) for help

---

## 🚀 One-Command Setup

### Windows (PowerShell)

```powershell
# 1. Setup conda environment
powershell -ExecutionPolicy Bypass -File .\scripts\setup_conda.ps1

# 2. Activate environment
conda activate vta

# 3. Start databases
docker compose up -d postgres neo4j redis

# 4. Run API (new terminal)
conda activate vta
uvicorn src.api.main:app --reload

# 5. Run Dashboard (another terminal)
conda activate vta
streamlit run src/dashboard/app.py
```

### Linux/Mac

```bash
# 1. Setup conda environment
bash scripts/setup_conda.sh

# 2. Activate environment
conda activate vta

# 3. Start databases
docker compose up -d postgres neo4j redis

# 4. Run API (new terminal)
conda activate vta
uvicorn src.api.main:app --reload

# 5. Run Dashboard (another terminal)
conda activate vta
streamlit run src/dashboard/app.py
```

---

## 📋 Manual Setup (If Scripts Don't Work)

### Step 1: Create Conda Environment

```bash
# From project directory
conda env create -f environment.yml

# Activate
conda activate vta
```

### Step 2: Verify Installation

```bash
# Check Python version
python --version  # Should show Python 3.11.x

# Test imports
python -c "import fastapi; print('FastAPI OK')"
python -c "import torch; print('PyTorch OK')"
python -c "import streamlit; print('Streamlit OK')"
```

### Step 3: Configure Environment

```bash
# Copy environment template
cp env.example .env

# Edit .env (change passwords!)
notepad .env  # Windows
nano .env     # Linux/Mac
```

### Step 4: Start Databases

```bash
# Start PostgreSQL, Neo4j, Redis
docker compose up -d postgres neo4j redis

# Wait 30 seconds for databases to start
Start-Sleep -Seconds 30  # PowerShell
sleep 30                 # Linux/Mac

# Verify
docker compose ps
```

### Step 5: Initialize Data

```bash
# Make sure conda environment is active
conda activate vta

# Generate test scenarios
python src/data/synthetic_data_generator.py

# Initialize Neo4j (if script exists)
python scripts/run_phase2_ingestion.py
```

### Step 6: Run Application

**Terminal 1 - API:**
```bash
conda activate vta
uvicorn src.api.main:app --reload --port 8000
```

**Terminal 2 - Dashboard:**
```bash
conda activate vta
streamlit run src/dashboard/app.py --server.port 8501
```

---

## ✅ Verify Everything Works

### 1. Check Services

```bash
# Databases
docker compose ps

# API
curl http://localhost:8000/health

# Dashboard
# Open browser: http://localhost:8501
```

### 2. Test API

```bash
# Get scenarios
curl http://localhost:8000/api/v1/scenarios?limit=5

# Or open API docs
# Browser: http://localhost:8000/docs
```

### 3. Test Dashboard

- Open: http://localhost:8501
- Navigate through pages
- Try recommendations feature

---

## 🆘 Common Issues

### Conda Environment Not Found

```bash
# List environments
conda env list

# Recreate if needed
conda env remove -n vta
conda env create -f environment.yml
```

### Port Already in Use

```bash
# Find process (Windows PowerShell)
Get-NetTCPConnection -LocalPort 8000

# Change port in command
uvicorn src.api.main:app --reload --port 8001
```

### Database Connection Error

```bash
# Check databases are running
docker compose ps

# Check logs
docker compose logs postgres
docker compose logs neo4j

# Restart if needed
docker compose restart postgres neo4j
```

### Import Errors

```bash
# Make sure environment is active
conda activate vta

# Verify Python path
which python  # Should show conda path

# Reinstall if needed
pip install -r requirements.txt --force-reinstall
```

---

## 📚 Next Steps

- **Full Guide**: See [CONDA_SETUP_GUIDE.md](CONDA_SETUP_GUIDE.md)
- **Docker Deployment**: See [DOCKER_DEPLOYMENT_GUIDE.md](DOCKER_DEPLOYMENT_GUIDE.md)
- **Troubleshooting**: Check troubleshooting section in full guide

---

## 🎯 Quick Access

| Service | URL |
|---------|-----|
| **Dashboard** | http://localhost:8501 |
| **API Docs** | http://localhost:8000/docs |
| **API Health** | http://localhost:8000/health |
| **Neo4j Browser** | http://localhost:7474 |

---

**Need help?** See [CONDA_SETUP_GUIDE.md](CONDA_SETUP_GUIDE.md) for detailed instructions.

