# 🚀 VTA Docker Deployment - Complete Step-by-Step Guide

**Virtual Testing Assistant - Production Deployment Instructions**

This guide will walk you through deploying the complete VTA stack using Docker.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Pre-Deployment Checks](#pre-deployment-checks)
3. [Configuration](#configuration)
4. [Building Images](#building-images)
5. [Starting Services](#starting-services)
6. [Verification](#verification)
7. [Testing the System](#testing-the-system)
8. [Accessing Services](#accessing-services)
9. [Monitoring](#monitoring)
10. [Stopping Services](#stopping-services)
11. [Troubleshooting](#troubleshooting)

---

## 1. Prerequisites

### Required Software

```bash
# Check Docker version (need 20.10+)
docker --version

# Check Docker Compose version (need 2.0+)
docker compose version

# Check available disk space (need 20GB+)
# Windows PowerShell:
Get-PSDrive C | Select-Object Used,Free

# Linux/Mac:
df -h
```

**Required:**
- Docker Desktop 4.0+ (Windows/Mac) or Docker Engine 20.10+ (Linux)
- Docker Compose 2.0+
- 8GB RAM minimum (16GB recommended)
- 20GB free disk space
- Administrator/sudo access

---

## 2. Pre-Deployment Checks

### Step 2.1: Verify Docker is Running

```bash
# Test Docker
docker run hello-world

# Expected output: "Hello from Docker!"
```

### Step 2.2: Check Port Availability

**Ports Required:**
- `5432` - PostgreSQL
- `7474` - Neo4j HTTP
- `7687` - Neo4j Bolt
- `6379` - Redis
- `8000` - FastAPI
- `8501` - Streamlit

```bash
# Windows PowerShell - Check if ports are free
Test-NetConnection -ComputerName localhost -Port 5432
Test-NetConnection -ComputerName localhost -Port 7474
Test-NetConnection -ComputerName localhost -Port 7687
Test-NetConnection -ComputerName localhost -Port 6379
Test-NetConnection -ComputerName localhost -Port 8000
Test-NetConnection -ComputerName localhost -Port 8501

# If any port shows "TcpTestSucceeded: True", that port is in use!
```

**If ports are in use, you can either:**
1. Stop the conflicting service
2. Change ports in `.env` file (covered in next section)

### Step 2.3: Verify Project Files

```bash
# Navigate to project directory
cd F:\DRIVING-TEST-SIMULATION

# Check required files exist
ls Dockerfile
ls docker-compose.yml
ls docker.env.example
ls scripts\deploy.sh
```

---

## 3. Configuration

### Step 3.1: Create Environment File

```bash
# Copy the example environment file
Copy-Item docker.env.example .env

# Or manually:
cp docker.env.example .env
```

### Step 3.2: Edit Configuration (IMPORTANT!)

Open `.env` in your editor and **CHANGE THESE VALUES**:

```bash
# CRITICAL: Change all passwords!
POSTGRES_PASSWORD=YourSecurePassword123!
NEO4J_PASSWORD=YourNeo4jPassword456!
REDIS_PASSWORD=YourRedisPassword789!
SECRET_KEY=YourRandomSecretKey-Generate-A-Long-Random-String

# Optional: Change ports if conflicts exist
POSTGRES_PORT=5432
NEO4J_BOLT_PORT=7687
NEO4J_HTTP_PORT=7474
REDIS_PORT=6379
API_PORT=8000
DASHBOARD_PORT=8501

# Optional: Adjust performance
API_WORKERS=4
LOG_LEVEL=info
```

**Security Note:** Never commit `.env` to git! It's already in `.gitignore`.

---

## 4. Building Images

### Step 4.1: Validate Docker Compose Configuration

```bash
# Validate docker-compose.yml syntax
docker compose config --quiet

# If no errors, configuration is valid!
```

### Step 4.2: Build Docker Images

```bash
# Build all images (this takes 3-5 minutes first time)
docker compose build

# Or using Makefile:
make build
```

**Expected Output:**
```
[+] Building 180.5s (23/23) FINISHED
 => [api internal] load .dockerignore
 => [api internal] load build definition
 => [api builder 1/6] FROM docker.io/library/python:3.11-slim
 ...
 => [api] exporting to image
 => => exporting layers
 => => writing image sha256:...
```

### Step 4.3: Verify Images

```bash
# List built images
docker images | findstr vta

# Expected output:
# driving-test-simulation-api        latest    xxx    xxx MB
# driving-test-simulation-dashboard  latest    xxx    xxx MB
```

---

## 5. Starting Services

### Option A: Automated Deployment (Recommended)

```bash
# One-command deployment
bash scripts/deploy.sh

# Or using Makefile:
make deploy
```

This script will:
1. ✅ Check prerequisites
2. ✅ Build images
3. ✅ Start databases
4. ✅ Wait for health
5. ✅ Initialize data
6. ✅ Start API & Dashboard
7. ✅ Verify health

### Option B: Manual Step-by-Step

#### Step 5.1: Start Databases First

```bash
# Start database services
docker compose up -d postgres neo4j redis

# Check status
docker compose ps
```

**Expected Output:**
```
NAME            IMAGE                      STATUS         PORTS
vta-postgres    pgvector/pgvector:pg16     Up (healthy)   5432->5432
vta-neo4j       neo4j:5.14-community       Up (healthy)   7474->7474, 7687->7687
vta-redis       redis:7-alpine             Up (healthy)   6379->6379
```

#### Step 5.2: Wait for Databases (30 seconds)

```bash
# Wait for databases to be ready
Start-Sleep -Seconds 30

# Or check logs
docker compose logs postgres
docker compose logs neo4j
```

#### Step 5.3: Initialize Data

```bash
# Generate scenarios and initialize databases
docker compose run --rm init-data

# This will:
# - Generate 500 test scenarios
# - Create Neo4j schema
# - Ingest data into Neo4j
```

**Expected Output:**
```
Generating test scenarios...
Generated 500 scenarios
[OK] Scenarios saved to src/data/test_scenarios.json

Initializing Neo4j...
Created constraints
Created indexes
Ingested 500 test scenarios
[OK] Neo4j initialization complete
```

#### Step 5.4: Start Application Services

```bash
# Start API and Dashboard
docker compose up -d api dashboard

# Check all services
docker compose ps
```

**All services should show "Up (healthy)"**

---

## 6. Verification

### Step 6.1: Check All Services

```bash
# View service status
docker compose ps

# Using Makefile:
make ps
```

**Expected Output - All services should be "Up (healthy)":**
```
NAME              STATUS
vta-postgres      Up (healthy)
vta-neo4j         Up (healthy)
vta-redis         Up (healthy)
vta-api           Up (healthy)
vta-dashboard     Up (healthy)
```

### Step 6.2: Health Checks

```bash
# Check health of all services
make health

# Or manually:
# PostgreSQL
docker compose exec postgres pg_isready

# Neo4j
curl http://localhost:7474

# Redis
docker compose exec redis redis-cli ping

# API
curl http://localhost:8000/health

# Dashboard
curl http://localhost:8501/_stcore/health
```

**Expected Output:**
```
Checking service health...
PostgreSQL: ✓ PostgreSQL ready
Neo4j:      ✓ Neo4j ready
Redis:      ✓ Redis ready
API:        ✓ API ready
Dashboard:  ✓ Dashboard ready
```

### Step 6.3: View Logs

```bash
# View all logs
docker compose logs --tail=50

# View specific service logs
docker compose logs api --tail=50
docker compose logs dashboard --tail=50

# Follow logs in real-time
docker compose logs -f api
```

---

## 7. Testing the System

### Test 7.1: API Health Endpoint

```bash
# Test API health
curl http://localhost:8000/health

# Expected output:
{
  "status": "healthy",
  "timestamp": "2025-11-06T...",
  "version": "1.0"
}
```

### Test 7.2: API Documentation

Open browser: **http://localhost:8000/docs**

You should see:
- Swagger UI with all API endpoints
- 13 endpoints listed
- Interactive API testing interface

### Test 7.3: Test Recommendation Endpoint

```bash
# Get test recommendations (PowerShell)
$headers = @{"Content-Type"="application/json"}
$body = @{
    vehicle_model = "Ariya"
    platform = "EV"
    target_systems = @("Battery", "Powertrain")
    top_k = 5
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/recommendations" -Method POST -Headers $headers -Body $body
```

**Expected Output:**
```json
{
  "recommendations": [
    {
      "scenario_id": "...",
      "test_name": "Battery Thermal Performance Test",
      "score": 0.95,
      "explanation": "..."
    },
    ...
  ],
  "total_results": 5
}
```

### Test 7.4: Test Scenarios Endpoint

```bash
# List scenarios
curl http://localhost:8000/api/v1/scenarios?limit=10

# Get specific scenario
curl http://localhost:8000/api/v1/scenarios/SCENARIO_001
```

### Test 7.5: Test ROI Endpoint

```bash
# Calculate ROI (PowerShell)
$body = @{
    baseline_count = 100
    optimization_rate = 0.25
    implementation_cost_gbp = 50000
    analysis_period_years = 3
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/roi" -Method POST -Headers @{"Content-Type"="application/json"} -Body $body
```

### Test 7.6: Test Statistics Endpoint

```bash
# Get system statistics
curl http://localhost:8000/api/v1/stats
```

**Expected Output:**
```json
{
  "total_scenarios": 500,
  "platforms": {
    "EV": 167,
    "HEV": 167,
    "ICE": 166
  },
  "test_types": {
    "performance": 83,
    "durability": 83,
    "safety": 83,
    "regulatory": 83,
    "adas": 84,
    "emissions": 84
  }
}
```

---

## 8. Accessing Services

### 8.1: Streamlit Dashboard

**URL:** http://localhost:8501

**What to test:**
1. ✅ Dashboard loads
2. ✅ Navigate to "Recommendations" page
3. ✅ Select vehicle model (Ariya)
4. ✅ Click "Get Recommendations"
5. ✅ Verify results display
6. ✅ Navigate to "ROI Analysis"
7. ✅ Enter test counts
8. ✅ View ROI charts
9. ✅ Check "Metrics" page
10. ✅ Browse "Scenarios" page

### 8.2: API Documentation

**URL:** http://localhost:8000/docs

**What to test:**
1. ✅ Swagger UI loads
2. ✅ All 13 endpoints visible
3. ✅ Try "GET /health" endpoint
4. ✅ Try "GET /api/v1/scenarios" endpoint
5. ✅ Test POST endpoints with example data

### 8.3: Neo4j Browser

**URL:** http://localhost:7474

**Credentials:**
- Username: `neo4j`
- Password: (value from `.env` - NEO4J_PASSWORD)

**What to test:**
```cypher
// Check node count
MATCH (n) RETURN count(n)
// Expected: 500+ nodes

// View test scenarios
MATCH (t:TestScenario) RETURN t LIMIT 10

// Check relationships
MATCH ()-[r]->() RETURN type(r), count(r)
```

### 8.4: Database Connections

#### PostgreSQL:
```bash
# Connect to PostgreSQL
docker compose exec postgres psql -U vta_user -d vta

# Run queries
\dt vta.*                     # List tables
SELECT count(*) FROM vta.test_scenario_vectors;
\q                            # Quit
```

#### Redis:
```bash
# Connect to Redis
docker compose exec redis redis-cli

# Check status
PING                          # Should return PONG
INFO stats
exit
```

---

## 9. Monitoring

### 9.1: Container Resource Usage

```bash
# View real-time resource usage
docker stats

# Or using Makefile:
make stats
```

**Monitor:**
- CPU %
- Memory usage
- Network I/O
- Block I/O

### 9.2: View Logs

```bash
# All services
make logs

# Specific service
make logs-api
make logs-dash

# Follow logs
docker compose logs -f api
```

### 9.3: Process Monitoring

```bash
# View processes in containers
make top

# Or manually:
docker compose top api
```

---

## 10. Stopping Services

### Stop All Services

```bash
# Stop all services (keeps data)
docker compose down

# Or using Makefile:
make down
```

### Stop and Remove All Data (CAUTION!)

```bash
# This will DELETE all data!
docker compose down -v

# Or using Makefile:
make clean
# (Will ask for confirmation)
```

### Restart Services

```bash
# Restart all services
docker compose restart

# Or using Makefile:
make restart

# Restart specific service
docker compose restart api
```

---

## 11. Troubleshooting

### Issue 1: Port Already in Use

**Error:** "bind: address already in use"

**Solution:**
```bash
# Find process using port (PowerShell)
Get-NetTCPConnection -LocalPort 8000 | Select-Object OwningProcess
Get-Process -Id <ProcessId>

# Stop the process or change port in .env
API_PORT=8001
```

### Issue 2: Container Won't Start

**Check logs:**
```bash
docker compose logs [service-name]

# Examples:
docker compose logs postgres
docker compose logs neo4j
docker compose logs api
```

**Common fixes:**
```bash
# Rebuild container
docker compose build [service-name]
docker compose up -d [service-name]

# Remove and recreate
docker compose rm -f [service-name]
docker compose up -d [service-name]
```

### Issue 3: Database Connection Errors

**Check database is running:**
```bash
docker compose ps postgres
docker compose ps neo4j
```

**Restart databases:**
```bash
docker compose restart postgres neo4j
```

**Check database logs:**
```bash
docker compose logs postgres
docker compose logs neo4j
```

### Issue 4: Out of Memory

**Check resource usage:**
```bash
docker stats --no-stream
```

**Solutions:**
- Increase Docker memory limit (Docker Desktop Settings)
- Reduce API workers in `.env`:
  ```bash
  API_WORKERS=2
  ```
- Reduce Neo4j memory:
  ```yaml
  # In docker-compose.yml
  NEO4J_dbms_memory_heap_max__size: 1G
  ```

### Issue 5: Slow Performance

**Check resource allocation:**
```bash
make stats
```

**Optimize:**
1. Increase Docker resources (Settings → Resources)
2. Reduce concurrent workers
3. Clear Docker cache:
   ```bash
   docker system prune
   ```

### Issue 6: Services Show "Unhealthy"

**Check health:**
```bash
docker compose ps
```

**View health check logs:**
```bash
docker inspect vta-api | findstr Health
```

**Restart unhealthy service:**
```bash
docker compose restart [service-name]
```

---

## 📊 Verification Checklist

After deployment, verify all these:

### Infrastructure
- [ ] All 5 containers running
- [ ] All containers show "healthy" status
- [ ] No errors in logs
- [ ] Ports accessible

### Databases
- [ ] PostgreSQL accepting connections
- [ ] Neo4j browser accessible
- [ ] Redis responding to PING
- [ ] Test data loaded (500 scenarios)

### API
- [ ] Health endpoint returns 200
- [ ] API docs accessible at /docs
- [ ] Recommendations endpoint working
- [ ] ROI endpoint working
- [ ] Scenarios endpoint working
- [ ] Stats endpoint working

### Dashboard
- [ ] Dashboard loads at :8501
- [ ] All 7 pages accessible
- [ ] Recommendations page functional
- [ ] ROI analysis displays charts
- [ ] Metrics page shows data
- [ ] Scenarios browser works

### Performance
- [ ] API response < 1s
- [ ] Dashboard loads < 5s
- [ ] No memory leaks
- [ ] CPU usage reasonable (<50%)

---

## 🎉 Success!

If all checks pass, your VTA system is **fully deployed and operational**!

### Quick Access URLs

| Service | URL | Purpose |
|---------|-----|---------|
| **Dashboard** | http://localhost:8501 | Main UI |
| **API Docs** | http://localhost:8000/docs | API testing |
| **API Health** | http://localhost:8000/health | Health check |
| **Neo4j Browser** | http://localhost:7474 | Graph database |

### Next Steps

1. **Test the system** thoroughly
2. **Monitor resource usage** over time
3. **Set up backups** (use `make backup`)
4. **Review logs** regularly
5. **Document any issues** encountered

---

## 📞 Support

If you encounter issues:

1. Check logs: `docker compose logs`
2. Review troubleshooting section above
3. Check Docker resources (memory, disk)
4. Verify all ports are available
5. Ensure all passwords are set in `.env`

---

**Deployment Guide Version:** 1.0  
**Last Updated:** Phase 10 Complete  
**System Status:** ✅ Production Ready

