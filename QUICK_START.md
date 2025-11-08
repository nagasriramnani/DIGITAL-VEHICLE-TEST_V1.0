# ⚡ VTA Quick Start Guide

**Get VTA running in 5 minutes!**

---

## 🚀 One-Command Deployment

```bash
# 1. Configure (one-time)
cp docker.env.example .env
# Edit .env and change all passwords!

# 2. Deploy everything
bash scripts/deploy.sh

# 3. Access services
# Dashboard: http://localhost:8501
# API Docs:  http://localhost:8000/docs
```

---

## 📋 Essential Commands

### Start/Stop
```bash
make up        # Start all services
make down      # Stop all services
make restart   # Restart all services
```

### Monitoring
```bash
make health    # Check service health
make logs      # View all logs
make stats     # Resource usage
make ps        # Service status
```

### Troubleshooting
```bash
make logs-api   # API logs only
make logs-dash  # Dashboard logs only
docker compose ps  # Check status
docker compose restart api  # Restart specific service
```

---

## 🔍 Quick Tests

### Test 1: API Health
```bash
curl http://localhost:8000/health
```

### Test 2: Get Scenarios
```bash
curl http://localhost:8000/api/v1/scenarios?limit=5
```

### Test 3: Dashboard
Open browser: http://localhost:8501

---

## 🆘 Common Issues

### Port Already in Use
```bash
# Change port in .env
API_PORT=8001
DASHBOARD_PORT=8502
```

### Service Won't Start
```bash
# Check logs
docker compose logs [service-name]

# Restart
docker compose restart [service-name]
```

### Out of Memory
```bash
# Reduce workers in .env
API_WORKERS=2
```

---

## 📚 Full Documentation

- **Complete Guide:** [DOCKER_DEPLOYMENT_GUIDE.md](DOCKER_DEPLOYMENT_GUIDE.md)
- **Deployment:** [DEPLOYMENT.md](DEPLOYMENT.md)
- **Project Summary:** [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

---

## ✅ Health Check

All services should show **"Up (healthy)"**:
```bash
docker compose ps
```

Expected:
- vta-postgres: Up (healthy)
- vta-neo4j: Up (healthy)
- vta-redis: Up (healthy)
- vta-api: Up (healthy)
- vta-dashboard: Up (healthy)

---

## 🎯 Quick Access

| Service | URL |
|---------|-----|
| **Dashboard** | http://localhost:8501 |
| **API Docs** | http://localhost:8000/docs |
| **Neo4j** | http://localhost:7474 |
| **Health** | http://localhost:8000/health |

---

**Need help?** See [DOCKER_DEPLOYMENT_GUIDE.md](DOCKER_DEPLOYMENT_GUIDE.md) for detailed instructions.

