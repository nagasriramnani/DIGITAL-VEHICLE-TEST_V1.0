#!/bin/bash
# Virtual Testing Assistant - Deployment Script
# One-command deployment for VTA full stack

set -e

echo "============================================"
echo "VTA Deployment Script"
echo "============================================"
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Warning: .env file not found${NC}"
    echo "Creating .env from docker.env.example..."
    cp docker.env.example .env
    echo -e "${GREEN}Created .env file${NC}"
    echo -e "${YELLOW}Please edit .env with your production passwords before deploying!${NC}"
    read -p "Press Enter to continue or Ctrl+C to abort..."
fi

# Check Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running${NC}"
    exit 1
fi

echo "Step 1/5: Building Docker images..."
docker-compose build

echo
echo "Step 2/5: Starting database services..."
docker-compose up -d postgres neo4j redis

echo
echo "Waiting for databases to be ready..."
sleep 10

echo
echo "Step 3/5: Initializing data..."
docker-compose run --rm init-data

echo
echo "Step 4/5: Starting application services..."
docker-compose up -d api dashboard

echo
echo "Step 5/5: Checking service health..."
sleep 5

# Check services
echo
echo "Service Status:"
echo "---------------"
docker-compose ps

echo
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}VTA Deployment Complete!${NC}"
echo -e "${GREEN}============================================${NC}"
echo
echo "Access the services:"
echo "  - API:       http://localhost:8000"
echo "  - Dashboard: http://localhost:8501"
echo "  - Neo4j:     http://localhost:7474"
echo "  - API Docs:  http://localhost:8000/docs"
echo
echo "Useful commands:"
echo "  - View logs:    docker-compose logs -f"
echo "  - Stop all:     docker-compose down"
echo "  - Restart:      docker-compose restart"
echo

