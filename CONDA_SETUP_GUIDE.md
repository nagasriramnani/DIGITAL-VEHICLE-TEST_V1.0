# 🐍 VTA Conda Setup Guide - Complete Instructions

**Virtual Testing Assistant - Conda Environment Setup**

This guide provides complete instructions for setting up and deploying VTA using Conda instead of system Python.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Option A: Conda + Docker (Recommended)](#option-a-conda--docker-recommended)
3. [Option B: Conda Only (Local Development)](#option-b-conda-only-local-development)
4. [Environment Setup](#environment-setup)
5. [Database Setup](#database-setup)
6. [Running the Application](#running-the-application)
7. [Troubleshooting](#troubleshooting)
8. [Quick Reference](#quick-reference)

---

## Prerequisites

### Required Software

1. **Conda/Miniconda/Anaconda**
   
   **⚠️ IMPORTANT: If you see "'conda' is not recognized":**
   - **Use Anaconda Prompt** instead of regular CMD (easiest solution)
   - Or see [CONDA_TROUBLESHOOTING.md](CONDA_TROUBLESHOOTING.md) for fixing PATH
   
   ```bash
   # Check conda installation
   # In Anaconda Prompt or after fixing PATH:
   conda --version
   # Should show: conda 23.x.x or higher
   ```
   
   **If conda is not installed:**
   - Download Anaconda: https://www.anaconda.com/download
   - Download Miniconda: https://docs.conda.io/en/latest/miniconda.html
   - **During installation, check "Add Anaconda to PATH"**

2. **Docker Desktop** (for Option A - Recommended)
   ```bash
   docker --version
   docker compose version
   ```

3. **Git** (if cloning repository)
   ```bash
   git --version
   ```

### System Requirements

- **CPU**: 4+ cores
- **RAM**: 8GB minimum (16GB recommended for ML models)
- **Storage**: 20GB+ free space
- **OS**: Windows 10+, macOS 10.14+, or Linux

---

## Option A: Conda + Docker (Recommended)

**Best for**: Production deployment, easier database management

This approach uses Conda for Python environment and Docker for databases.

### Step 1: Create Conda Environment

```bash
# Navigate to project directory
cd F:\DRIVING-TEST-SIMULATION

# Create conda environment from environment.yml
conda env create -f environment.yml

# Activate environment
conda activate vta

# Verify Python version
python --version
# Should show: Python 3.11.x
```

### Step 2: Verify Environment

```bash
# Check conda environment is active (should show "vta")
conda info --envs

# Verify key packages
python -c "import fastapi; print(fastapi.__version__)"
python -c "import torch; print(torch.__version__)"
python -c "import streamlit; print(streamlit.__version__)"
```

### Step 3: Configure Environment Variables

```bash
# Copy environment template
cp docker.env.example .env

# Edit .env file (IMPORTANT: Change passwords!)
# Use your preferred editor:
notepad .env        # Windows
nano .env           # Linux/Mac
code .env           # VS Code
```

**Edit `.env` and change:**
- `POSTGRES_PASSWORD=your_secure_password`
- `NEO4J_PASSWORD=your_secure_password`
- `REDIS_PASSWORD=your_secure_password`
- `SECRET_KEY=your_random_secret_key`

### Step 4: Start Databases with Docker

```bash
# Make sure conda environment is active
conda activate vta

# Start only database services (PostgreSQL, Neo4j, Redis)
docker compose up -d postgres neo4j redis

# Wait for databases to be ready (30 seconds)
# Windows PowerShell:
Start-Sleep -Seconds 30
# Linux/Mac:
sleep 30

# Verify databases are running
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

### Step 6: Run Application Locally

**Terminal 1 - FastAPI Backend:**
```bash
conda activate vta
cd F:\DRIVING-TEST-SIMULATION
uvicorn src.api.main:app --reload --port 8000
```

**Terminal 2 - Streamlit Dashboard:**
```bash
conda activate vta
cd F:\DRIVING-TEST-SIMULATION
streamlit run src/dashboard/app.py --server.port 8501
```

### Step 7: Access Services

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Dashboard**: http://localhost:8501
- **Neo4j Browser**: http://localhost:7474

---

## Option B: Conda Only (Local Development)

**Best for**: Full local development without Docker

This approach runs everything locally using Conda.

### Step 1: Create Conda Environment

```bash
# Navigate to project directory
cd F:\DRIVING-TEST-SIMULATION

# Create conda environment
conda env create -f environment.yml

# Activate environment
conda activate vta
```

### Step 2: Install PostgreSQL + pgvector Locally

**Windows:**
```bash
# Option 1: Use Docker for PostgreSQL only
docker run -d --name vta-postgres \
  -e POSTGRES_DB=vta \
  -e POSTGRES_USER=vta_user \
  -e POSTGRES_PASSWORD=your_password \
  -p 5432:5432 \
  pgvector/pgvector:pg16

# Option 2: Install PostgreSQL with pgvector manually
# Download from: https://www.postgresql.org/download/windows/
# Install pgvector extension
```

**Linux (Ubuntu/Debian):**
```bash
# Install PostgreSQL
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# Install pgvector
sudo apt-get install postgresql-16-pgvector

# Create database
sudo -u postgres psql
CREATE DATABASE vta;
CREATE USER vta_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE vta TO vta_user;
\q
```

**macOS:**
```bash
# Install PostgreSQL with Homebrew
brew install postgresql@16
brew install pgvector

# Start PostgreSQL
brew services start postgresql@16

# Create database
createdb vta
createuser vta_user
```

### Step 3: Install Neo4j Locally

**Option 1: Docker (Easiest)**
```bash
docker run -d --name vta-neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your_password \
  neo4j:5.14-community
```

**Option 2: Download Neo4j Desktop**
- Download from: https://neo4j.com/download/
- Install and create new database
- Set password
- Note connection URI: `bolt://localhost:7687`

### Step 4: Install Redis Locally

**Windows:**
```bash
# Use Docker (easiest)
docker run -d --name vta-redis \
  -p 6379:6379 \
  redis:7-alpine
```

**Linux:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

**macOS:**
```bash
brew install redis
brew services start redis
```

### Step 5: Configure Environment Variables

```bash
# Copy environment template
cp env.example .env

# Edit .env file
notepad .env  # Windows
nano .env     # Linux/Mac
```

**Update `.env` with local database connections:**
```bash
# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# PostgreSQL
PG_CONN=postgresql+psycopg2://vta_user:your_password@localhost:5432/vta

# Redis (if using)
REDIS_HOST=localhost
REDIS_PORT=6379
```

### Step 6: Initialize Databases

```bash
# Make sure conda environment is active
conda activate vta

# Generate test scenarios
python src/data/synthetic_data_generator.py

# Initialize Neo4j
python scripts/run_phase2_ingestion.py

# Initialize PostgreSQL (if needed)
# Connect to PostgreSQL and run:
# CREATE EXTENSION IF NOT EXISTS vector;
```

### Step 7: Run Application

**Terminal 1 - FastAPI:**
```bash
conda activate vta
cd F:\DRIVING-TEST-SIMULATION
uvicorn src.api.main:app --reload --port 8000
```

**Terminal 2 - Streamlit:**
```bash
conda activate vta
cd F:\DRIVING-TEST-SIMULATION
streamlit run src/dashboard/app.py --server.port 8501
```

---

## Environment Setup

### Creating Conda Environment

```bash
# Method 1: From environment.yml (Recommended)
conda env create -f environment.yml

# Method 2: Manual creation
conda create -n vta python=3.11
conda activate vta
pip install -r requirements.txt
```

### Activating Environment

```bash
# Activate conda environment
conda activate vta

# Verify activation (prompt should show "(vta)")
conda info --envs
```

### Updating Environment

```bash
# Update environment from environment.yml
conda env update -f environment.yml --prune

# Or update packages manually
conda activate vta
pip install --upgrade -r requirements.txt
```

### Deactivating Environment

```bash
# Deactivate when done
conda deactivate
```

---

## Database Setup

### PostgreSQL + pgvector Setup

**With Docker (Easiest):**
```bash
docker run -d --name vta-postgres \
  -e POSTGRES_DB=vta \
  -e POSTGRES_USER=vta_user \
  -e POSTGRES_PASSWORD=your_password \
  -p 5432:5432 \
  -v postgres-data:/var/lib/postgresql/data \
  pgvector/pgvector:pg16

# Enable pgvector extension
docker exec -it vta-postgres psql -U vta_user -d vta -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

**Verify Connection:**
```bash
conda activate vta
python -c "import psycopg2; conn = psycopg2.connect('postgresql://vta_user:your_password@localhost:5432/vta'); print('Connected!')"
```

### Neo4j Setup

**With Docker:**
```bash
docker run -d --name vta-neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your_password \
  -v neo4j-data:/data \
  neo4j:5.14-community
```

**Verify Connection:**
```bash
conda activate vta
python -c "from neo4j import GraphDatabase; driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'your_password')); driver.verify_connectivity(); print('Connected!')"
```

### Redis Setup

**With Docker:**
```bash
docker run -d --name vta-redis \
  -p 6379:6379 \
  redis:7-alpine
```

**Verify Connection:**
```bash
conda activate vta
python -c "import redis; r = redis.Redis(host='localhost', port=6379); r.ping(); print('Connected!')"
```

---

## Running the Application

### Development Mode (Hot Reload)

**Terminal 1 - API Server:**
```bash
conda activate vta
cd F:\DRIVING-TEST-SIMULATION
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Dashboard:**
```bash
conda activate vta
cd F:\DRIVING-TEST-SIMULATION
streamlit run src/dashboard/app.py --server.port 8501 --server.address 0.0.0.0
```

### Production Mode

**API:**
```bash
conda activate vta
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Dashboard:**
```bash
conda activate vta
streamlit run src/dashboard/app.py --server.port 8501 --server.address 0.0.0.0
```

### Running Tests

```bash
conda activate vta
cd F:\DRIVING-TEST-SIMULATION

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_api.py -v
```

---

## Troubleshooting

### Conda Environment Issues

**Environment not found:**
```bash
# List all environments
conda env list

# Recreate environment
conda env remove -n vta
conda env create -f environment.yml
```

**Package installation fails:**
```bash
# Update conda
conda update conda

# Clear cache
conda clean --all

# Try installing with pip instead
conda activate vta
pip install <package-name>
```

**Python version mismatch:**
```bash
# Check Python version
python --version

# Recreate with specific version
conda env remove -n vta
conda create -n vta python=3.11
conda activate vta
pip install -r requirements.txt
```

### Database Connection Issues

**PostgreSQL connection refused:**
```bash
# Check if PostgreSQL is running
docker ps | grep postgres
# or
sudo systemctl status postgresql

# Check connection string in .env
# Format: postgresql+psycopg2://user:password@host:port/database
```

**Neo4j connection failed:**
```bash
# Check Neo4j is running
docker ps | grep neo4j
# or check Neo4j Desktop

# Verify credentials in .env
# Test connection: http://localhost:7474
```

**pgvector extension missing:**
```bash
# Connect to PostgreSQL
docker exec -it vta-postgres psql -U vta_user -d vta

# Create extension
CREATE EXTENSION IF NOT EXISTS vector;

# Verify
\dx
```

### Import Errors

**Module not found:**
```bash
# Verify conda environment is active
conda activate vta
which python  # Should show conda path

# Reinstall package
pip install --force-reinstall <package-name>

# Or reinstall all
pip install -r requirements.txt --force-reinstall
```

**PyTorch/CUDA issues:**
```bash
# Install CPU-only PyTorch (if no GPU)
conda install pytorch cpuonly -c pytorch

# Or install with CUDA (if GPU available)
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia
```

### Port Already in Use

**Windows:**
```powershell
# Find process using port
Get-NetTCPConnection -LocalPort 8000 | Select-Object OwningProcess

# Kill process
Stop-Process -Id <ProcessId>
```

**Linux/Mac:**
```bash
# Find process
lsof -i :8000

# Kill process
kill -9 <PID>
```

---

## Quick Reference

### Essential Commands

```bash
# Environment Management
conda env create -f environment.yml    # Create environment
conda activate vta                     # Activate environment
conda deactivate                       # Deactivate
conda env list                         # List environments
conda env remove -n vta                # Remove environment

# Package Management
conda list                             # List installed packages
pip list                               # List pip packages
pip install -r requirements.txt        # Install from requirements
conda update --all                     # Update all packages

# Application
uvicorn src.api.main:app --reload      # Run API
streamlit run src/dashboard/app.py     # Run dashboard
pytest                                 # Run tests

# Database (Docker)
docker ps                              # List running containers
docker compose up -d postgres          # Start PostgreSQL
docker compose logs postgres           # View logs
docker compose stop postgres           # Stop service
```

### Environment Variables

**Key variables in `.env`:**
- `NEO4J_URI` - Neo4j connection string
- `NEO4J_USER` - Neo4j username
- `NEO4J_PASSWORD` - Neo4j password
- `PG_CONN` - PostgreSQL connection string
- `REDIS_HOST` - Redis host
- `REDIS_PORT` - Redis port

### File Structure

```
DRIVING-TEST-SIMULATION/
├── environment.yml          # Conda environment definition
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (create from template)
├── src/                     # Source code
├── scripts/                 # Utility scripts
└── tests/                   # Test files
```

---

## Next Steps

1. ✅ **Environment Created**: `conda activate vta`
2. ✅ **Databases Running**: Check with `docker ps` or local services
3. ✅ **Configuration Set**: Edit `.env` with your credentials
4. ✅ **Data Initialized**: Run data generation scripts
5. ✅ **Application Running**: Start API and Dashboard
6. ✅ **Test Access**: Open http://localhost:8501

---

## Support

**Common Issues:**
- Check logs: `docker compose logs` or application console
- Verify environment: `conda info --envs`
- Test connections: Use Python test scripts above

**Need Help?**
- Review troubleshooting section
- Check Docker logs: `docker compose logs [service]`
- Verify `.env` configuration
- Test database connections individually

---

**Last Updated**: Phase 10 Complete  
**Conda Version**: Tested with Conda 23.x+  
**Python Version**: 3.11

