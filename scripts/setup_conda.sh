#!/bin/bash
# Virtual Testing Assistant - Conda Setup Script
# Quick setup for conda users

set -e

echo "============================================"
echo "VTA Conda Environment Setup"
echo "============================================"
echo

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check conda
if ! command -v conda &> /dev/null; then
    echo -e "${RED}Error: Conda is not installed or not in PATH${NC}"
    echo "Please install Anaconda or Miniconda first"
    exit 1
fi

echo -e "${GREEN}✓ Conda found: $(conda --version)${NC}"
echo

# Check if environment exists
if conda env list | grep -q "^vta "; then
    echo -e "${YELLOW}Warning: 'vta' environment already exists${NC}"
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing existing environment..."
        conda env remove -n vta -y
    else
        echo "Using existing environment"
        conda activate vta
        echo -e "${GREEN}Environment activated!${NC}"
        exit 0
    fi
fi

# Create environment
echo "Step 1/3: Creating conda environment..."
if [ -f environment.yml ]; then
    conda env create -f environment.yml
else
    echo -e "${RED}Error: environment.yml not found${NC}"
    exit 1
fi

echo
echo "Step 2/3: Activating environment..."
conda activate vta

echo
echo "Step 3/3: Verifying installation..."
python --version
python -c "import fastapi; print(f'FastAPI: {fastapi.__version__}')" || echo "FastAPI not found"
python -c "import torch; print(f'PyTorch: {torch.__version__}')" || echo "PyTorch not found"
python -c "import streamlit; print(f'Streamlit: {streamlit.__version__}')" || echo "Streamlit not found"

echo
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}============================================${NC}"
echo
echo "Next steps:"
echo "  1. Activate environment: conda activate vta"
echo "  2. Configure .env file: cp env.example .env"
echo "  3. Start databases: docker compose up -d postgres neo4j redis"
echo "  4. Run API: uvicorn src.api.main:app --reload"
echo "  5. Run Dashboard: streamlit run src/dashboard/app.py"
echo

