# Virtual Testing Assistant - Conda Setup Script (PowerShell)
# Quick setup for conda users on Windows

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "VTA Conda Environment Setup" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check conda
try {
    $condaVersion = conda --version
    Write-Host "✓ Conda found: $condaVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Conda is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Anaconda or Miniconda first" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Check if environment exists
$envExists = conda env list | Select-String "^vta "
if ($envExists) {
    Write-Host "Warning: 'vta' environment already exists" -ForegroundColor Yellow
    $response = Read-Host "Do you want to recreate it? (y/N)"
    if ($response -eq "y" -or $response -eq "Y") {
        Write-Host "Removing existing environment..." -ForegroundColor Yellow
        conda env remove -n vta -y
    } else {
        Write-Host "Using existing environment" -ForegroundColor Green
        Write-Host ""
        Write-Host "To activate: conda activate vta" -ForegroundColor Cyan
        exit 0
    }
}

# Create environment
Write-Host "Step 1/3: Creating conda environment..." -ForegroundColor Yellow
if (Test-Path environment.yml) {
    conda env create -f environment.yml
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error creating environment" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Error: environment.yml not found" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 2/3: Environment created successfully!" -ForegroundColor Green

Write-Host ""
Write-Host "Step 3/3: Verifying installation..." -ForegroundColor Yellow
conda activate vta
python --version

try {
    $fastapi = python -c "import fastapi; print(fastapi.__version__)" 2>$null
    Write-Host "  FastAPI: $fastapi" -ForegroundColor Green
} catch {
    Write-Host "  FastAPI: Not found" -ForegroundColor Yellow
}

try {
    $torch = python -c "import torch; print(torch.__version__)" 2>$null
    Write-Host "  PyTorch: $torch" -ForegroundColor Green
} catch {
    Write-Host "  PyTorch: Not found" -ForegroundColor Yellow
}

try {
    $streamlit = python -c "import streamlit; print(streamlit.__version__)" 2>$null
    Write-Host "  Streamlit: $streamlit" -ForegroundColor Green
} catch {
    Write-Host "  Streamlit: Not found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "  1. Activate environment: conda activate vta" -ForegroundColor Cyan
Write-Host "  2. Configure .env file: Copy-Item env.example .env" -ForegroundColor Cyan
Write-Host "  3. Start databases: docker compose up -d postgres neo4j redis" -ForegroundColor Cyan
Write-Host "  4. Run API: uvicorn src.api.main:app --reload" -ForegroundColor Cyan
Write-Host "  5. Run Dashboard: streamlit run src/dashboard/app.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "For detailed instructions, see: CONDA_SETUP_GUIDE.md" -ForegroundColor Yellow
Write-Host ""

