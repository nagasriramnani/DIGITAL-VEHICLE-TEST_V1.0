# CARLA 0.9.16 Setup Helper Script for Windows
# This script helps you find CARLA and set it up

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CARLA 0.9.16 Setup Helper" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Find CARLA installation
Write-Host "Step 1: Searching for CARLA 0.9.16..." -ForegroundColor Yellow

$carlaPaths = @(
    "C:\CARLA_0.9.16",
    "C:\CARLA",
    "$env:USERPROFILE\Downloads\CARLA_0.9.16",
    "$env:USERPROFILE\Downloads\carla-0.9.16",
    "C:\Program Files\CARLA_0.9.16"
)

$carlaFound = $null
foreach ($path in $carlaPaths) {
    if (Test-Path $path) {
        $carlaExe = Join-Path $path "CarlaUE4.exe"
        if (Test-Path $carlaExe) {
            $carlaFound = $path
            Write-Host "✓ Found CARLA at: $path" -ForegroundColor Green
            break
        }
    }
}

if (-not $carlaFound) {
    Write-Host "✗ CARLA not found in common locations" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please enter your CARLA installation path:" -ForegroundColor Yellow
    $carlaFound = Read-Host "CARLA Path"
    
    if (-not (Test-Path $carlaFound)) {
        Write-Host "✗ Path does not exist!" -ForegroundColor Red
        exit 1
    }
    
    $carlaExe = Join-Path $carlaFound "CarlaUE4.exe"
    if (-not (Test-Path $carlaExe)) {
        Write-Host "✗ CarlaUE4.exe not found in that directory!" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Step 2: Checking CARLA Python API..." -ForegroundColor Yellow

$pythonApiPath = Join-Path $carlaFound "PythonAPI\carla\dist"
if (Test-Path $pythonApiPath) {
    $eggFiles = Get-ChildItem -Path $pythonApiPath -Filter "*.egg" -ErrorAction SilentlyContinue
    if ($eggFiles) {
        Write-Host "✓ Found Python API: $($eggFiles[0].Name)" -ForegroundColor Green
        $eggPath = $eggFiles[0].FullName
    } else {
        Write-Host "✗ No .egg file found in PythonAPI" -ForegroundColor Red
        $eggPath = $null
    }
} else {
    Write-Host "✗ PythonAPI directory not found" -ForegroundColor Red
    $eggPath = $null
}

Write-Host ""
Write-Host "Step 3: Checking Python environment..." -ForegroundColor Yellow

# Check if conda is available
$condaAvailable = $false
try {
    $condaVersion = conda --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        $condaAvailable = $true
        Write-Host "✓ Conda is available" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ Conda not found" -ForegroundColor Yellow
}

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python is available: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 4: Testing CARLA import..." -ForegroundColor Yellow

try {
    $testResult = python -c "import carla; print('CARLA version:', carla.__version__)" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ CARLA Python API is installed!" -ForegroundColor Green
        Write-Host "  $testResult" -ForegroundColor Gray
    } else {
        Write-Host "✗ CARLA Python API not installed" -ForegroundColor Red
        Write-Host ""
        Write-Host "Installing CARLA Python API..." -ForegroundColor Yellow
        
        if ($eggPath) {
            Write-Host "Installing from: $eggPath" -ForegroundColor Gray
            pip install "$eggPath"
        } else {
            Write-Host "Installing from PyPI..." -ForegroundColor Gray
            pip install carla
        }
        
        # Test again
        $testResult = python -c "import carla; print('CARLA version:', carla.__version__)" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ CARLA Python API installed successfully!" -ForegroundColor Green
        } else {
            Write-Host "✗ Installation failed" -ForegroundColor Red
            Write-Host "  Error: $testResult" -ForegroundColor Red
        }
    }
} catch {
    Write-Host "✗ Error testing CARLA: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CARLA Path: $carlaFound" -ForegroundColor White
Write-Host "CARLA Executable: $carlaExe" -ForegroundColor White
Write-Host ""

Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Start CARLA server:" -ForegroundColor White
Write-Host "   cd `"$carlaFound`"" -ForegroundColor Gray
Write-Host "   .\CarlaUE4.exe -carla-rpc-port=2000" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Run your simulation (in another terminal):" -ForegroundColor White
Write-Host "   cd F:\DRIVING-TEST-SIMULATION" -ForegroundColor Gray
Write-Host "   conda activate vta" -ForegroundColor Gray
Write-Host "   python sim_output\carla\dfaf323f-db0f-4014-93b3-a544618c798d.py" -ForegroundColor Gray
Write-Host ""

