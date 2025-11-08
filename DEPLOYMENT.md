# Virtual Testing Assistant - Deployment Guide

## Overview

This guide covers deploying the VTA system using Docker and Docker Compose for production environments.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Configuration](#configuration)
4. [Deployment Options](#deployment-options)
5. [Service Management](#service-management)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Troubleshooting](#troubleshooting)
8. [Security](#security)
9. [Backup & Recovery](#backup--recovery)
10. [Scaling](#scaling)

---

## Prerequisites

### Required Software
- **Docker**: 20.10+ 
- **Docker Compose**: 2.0+
- **Git**: For cloning the repository
- **Make**: (Optional) For convenience commands

### System Requirements

#### Minimum (Development)
- **CPU**: 4 cores
- **RAM**: 8 GB
- **Storage**: 20 GB

#### Recommended (Production)
- **CPU**: 8+ cores
- **RAM**: 16 GB+
- **Storage**: 50 GB+ SSD

### Port Requirements
- `5432`: PostgreSQL
- `7474`: Neo4j HTTP
- `7687`: Neo4j Bolt
- `6379`: Redis
- `8000`: FastAPI
- `8501`: Streamlit Dashboard

---

## Quick Start

### 1. Clone Repository
```bash
git clone <repository-url>
cd DRIVING-TEST-SIMULATION
```

### 2. Configure Environment
```bash
# Copy environment template
cp docker.env.example .env

# Edit with your settings (IMPORTANT!)
nano .env  # or use your preferred editor
```

**⚠️ IMPORTANT**: Change all passwords in `.env` before deploying!

### 3. Deploy
```bash
# Option A: Using deployment script (recommended)
bash scripts/deploy.sh

# Option B: Using Make
make deploy

# Option C: Manual
docker-compose up -d
```

### 4. Verify Deployment
```bash
# Check all services
make health

# Or manually
docker-compose ps
curl http://localhost:8000/health
curl http://localhost:8501
```

### 5. Access Services
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Dashboard**: http://localhost:8501
- **Neo4j Browser**: http://localhost:7474

---

## Configuration

### Environment Variables

#### Database Configuration
```bash
# PostgreSQL
POSTGRES_DB=vta
POSTGRES_USER=vta_user
POSTGRES_PASSWORD=<strong-password>  # CHANGE THIS!

# Neo4j
NEO4J_USER=neo4j
NEO4J_PASSWORD=<strong-password>  # CHANGE THIS!

# Redis
REDIS_PASSWORD=<strong-password>  # CHANGE THIS!
```

#### Application Configuration
```bash
# API Settings
API_WORKERS=4           # Number of Uvicorn workers
LOG_LEVEL=info          # Logging level (debug, info, warning, error)

# LLM Settings
USE_MOCK_LLM=true       # Set to false for production LLMs
HF_MODEL_NAME=mock-llm  # HuggingFace model name

# Business Settings
HOURLY_RATE_GBP=75.0
PHYSICAL_TEST_MULTIPLIER=1.0
SIMULATION_COST_FACTOR=0.05
```

#### Security Configuration
```bash
# IMPORTANT: Change in production!
SECRET_KEY=<generate-random-key>
CORS_ORIGINS=http://localhost:8501,http://localhost:3000
```

---

## Deployment Options

### Option 1: Full Stack (Recommended)
Deploy all services including databases:
```bash
docker-compose up -d
```

### Option 2: Application Only
Use external databases:
```bash
# Edit .env to point to external databases
POSTGRES_HOST=external-postgres.example.com
NEO4J_URI=bolt://external-neo4j.example.com:7687

# Start only app services
docker-compose up -d api dashboard
```

### Option 3: Development Mode
With hot-reload and debug logging:
```bash
# Edit .env
LOG_LEVEL=debug
ENABLE_DEBUG=true

# Mount source as volume (edit docker-compose.yml)
# Then start
docker-compose up
```

### Option 4: Production with Scaling
Scale specific services:
```bash
# Scale API workers
docker-compose up -d --scale api=4

# Scale with specific resource limits
docker-compose --compatibility up -d
```

---

## Service Management

### Starting Services
```bash
# All services
docker-compose up -d

# Specific service
docker-compose up -d api

# With build
docker-compose up -d --build
```

### Stopping Services
```bash
# All services (keeps data)
docker-compose down

# All services (removes volumes - DELETES DATA!)
docker-compose down -v

# Specific service
docker-compose stop api
```

### Restarting Services
```bash
# All services
docker-compose restart

# Specific service
docker-compose restart api

# Using Make
make restart
```

### Viewing Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api

# Last 100 lines
docker-compose logs --tail=100 api

# Using Make
make logs
make logs-api
make logs-dash
```

### Service Status
```bash
# Check running containers
docker-compose ps

# Check health
make health

# Resource usage
make stats
```

---

## Monitoring & Maintenance

### Health Checks

All services include health checks:
```bash
# API Health
curl http://localhost:8000/health

# Dashboard Health
curl http://localhost:8501/_stcore/health

# Database Health
make health
```

### Resource Monitoring
```bash
# Container stats
docker stats

# Or using Make
make stats
make top
```

### Log Management
```bash
# View logs
docker-compose logs -f [service]

# Log rotation (configure in docker-compose.yml)
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### Database Maintenance

#### PostgreSQL
```bash
# Enter PostgreSQL shell
make db-shell

# Vacuum database
docker-compose exec postgres vacuumdb -U vta_user -d vta

# Check database size
docker-compose exec postgres psql -U vta_user -d vta -c "SELECT pg_size_pretty(pg_database_size('vta'));"
```

#### Neo4j
```bash
# Enter Neo4j shell
make neo4j-shell

# Check database status
CALL dbms.queryJmx("org.neo4j:instance=kernel#0,name=Store file sizes");
```

---

## Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Find process using port
sudo lsof -i :8000

# Kill process or change port in .env
API_PORT=8001
```

#### 2. Services Not Starting
```bash
# Check logs
docker-compose logs

# Check resources
docker system df
docker system prune  # Clean up if needed
```

#### 3. Database Connection Errors
```bash
# Verify databases are running
docker-compose ps

# Check database logs
docker-compose logs postgres
docker-compose logs neo4j

# Restart databases
docker-compose restart postgres neo4j
```

#### 4. Permission Issues
```bash
# Fix ownership
sudo chown -R $(id -u):$(id -g) .

# Or run as root (not recommended)
sudo docker-compose up -d
```

#### 5. Out of Memory
```bash
# Check memory usage
docker stats

# Increase Docker memory limit (Docker Desktop)
# Or reduce worker count in .env
API_WORKERS=2
```

### Debug Mode

Enable detailed logging:
```bash
# Edit .env
LOG_LEVEL=debug
ENABLE_DEBUG=true

# Restart services
docker-compose restart api
docker-compose logs -f api
```

---

## Security

### Pre-Deployment Security Checklist

- [ ] Change all default passwords in `.env`
- [ ] Set strong `SECRET_KEY`
- [ ] Configure `CORS_ORIGINS` appropriately
- [ ] Use HTTPS in production (reverse proxy)
- [ ] Restrict database ports (don't expose publicly)
- [ ] Enable firewall rules
- [ ] Regular security updates
- [ ] Implement backup strategy

### Securing Databases

#### PostgreSQL
```bash
# Restrict network access
# In docker-compose.yml, remove ports exposure:
# ports:
#   - "5432:5432"  # Comment this out
```

#### Neo4j
```bash
# Enable authentication (default)
# Change default password immediately
```

### HTTPS/TLS

Use a reverse proxy (Nginx, Traefik) for HTTPS:
```nginx
# Nginx example
server {
    listen 443 ssl;
    server_name vta.example.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8000;
    }
}
```

---

## Backup & Recovery

### Automated Backups

#### PostgreSQL Backup
```bash
# Manual backup
make backup

# Or directly
docker-compose exec postgres pg_dump -U vta_user vta > backup.sql

# Automated daily backup (crontab)
0 2 * * * cd /path/to/vta && make backup
```

#### Neo4j Backup
```bash
# Export database
docker-compose exec neo4j neo4j-admin database dump neo4j --to-path=/backups

# Copy backup
docker cp vta-neo4j:/backups/neo4j.dump ./backups/
```

### Restore from Backup

#### PostgreSQL Restore
```bash
# Stop services
docker-compose down

# Start only PostgreSQL
docker-compose up -d postgres

# Restore
cat backup.sql | docker-compose exec -T postgres psql -U vta_user -d vta

# Start all services
docker-compose up -d
```

#### Neo4j Restore
```bash
# Stop Neo4j
docker-compose stop neo4j

# Copy backup to container
docker cp backup.dump vta-neo4j:/backups/

# Restore
docker-compose exec neo4j neo4j-admin database load --from-path=/backups neo4j

# Start Neo4j
docker-compose start neo4j
```

---

## Scaling

### Horizontal Scaling

#### Scale API Workers
```bash
# Scale to 4 instances
docker-compose up -d --scale api=4

# With load balancer (nginx)
upstream vta_api {
    server api:8000;
    # Add more backends
}
```

#### Database Scaling
- **PostgreSQL**: Use read replicas
- **Neo4j**: Use clustering (Enterprise)
- **Redis**: Use Redis Cluster

### Vertical Scaling

Allocate more resources in `docker-compose.yml`:
```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

---

## Production Checklist

### Before Deployment
- [ ] Review and test all configurations
- [ ] Change all default passwords
- [ ] Set up monitoring and alerting
- [ ] Configure backup strategy
- [ ] Test backup restoration
- [ ] Set up log aggregation
- [ ] Configure firewall rules
- [ ] Set up HTTPS/TLS
- [ ] Review resource limits
- [ ] Document custom configurations

### After Deployment
- [ ] Verify all services are running
- [ ] Test all endpoints
- [ ] Verify database connections
- [ ] Check logs for errors
- [ ] Perform health checks
- [ ] Test backup procedures
- [ ] Monitor resource usage
- [ ] Set up alerts
- [ ] Document deployment process

---

## Support

For issues or questions:
- Check logs: `docker-compose logs`
- Review troubleshooting section
- Contact: VTA Team

---

**Last Updated**: Phase 10 Complete  
**Version**: 1.0  
**Maintained By**: Nissan NTCE + Cranfield University KTP Team

