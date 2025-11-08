# VTA Full System Demo Script
# Runs complete demonstration of all features

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Virtual Testing Assistant - Full System Demo" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "[1/6] Checking Docker..." -ForegroundColor Yellow
try {
    docker info | Out-Null
    Write-Host "  ✓ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Check if services are running
Write-Host ""
Write-Host "[2/6] Checking VTA services..." -ForegroundColor Yellow
$services = docker compose ps --format json | ConvertFrom-Json

if ($services.Count -eq 0) {
    Write-Host "  ✗ Services not running. Starting deployment..." -ForegroundColor Yellow
    Write-Host ""
    & bash scripts/deploy.sh
} else {
    Write-Host "  ✓ Services are running" -ForegroundColor Green
}

# Wait for services to be healthy
Write-Host ""
Write-Host "[3/6] Waiting for services to be healthy..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Test API
Write-Host ""
Write-Host "[4/6] Testing API..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET
    Write-Host "  ✓ API is healthy" -ForegroundColor Green
} catch {
    Write-Host "  ✗ API not responding. Check logs with: docker compose logs api" -ForegroundColor Red
    exit 1
}

# Open browser windows
Write-Host ""
Write-Host "[5/6] Opening browser windows..." -ForegroundColor Yellow
Write-Host "  Opening Dashboard..." -ForegroundColor Cyan
Start-Process "http://localhost:8501"
Start-Sleep -Seconds 2

Write-Host "  Opening API Docs..." -ForegroundColor Cyan
Start-Process "http://localhost:8000/docs"
Start-Sleep -Seconds 2

Write-Host "  Opening Neo4j Browser..." -ForegroundColor Cyan
Start-Process "http://localhost:7474"

# Run quick tests
Write-Host ""
Write-Host "[6/6] Running quick tests..." -ForegroundColor Yellow

# Test 1: Get Statistics
Write-Host ""
Write-Host "  Test 1: Getting system statistics..." -ForegroundColor Cyan
try {
    $stats = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/stats" -Method GET
    Write-Host "    ✓ Total Scenarios: $($stats.total_scenarios)" -ForegroundColor Green
    Write-Host "    ✓ Platforms: EV=$($stats.platforms.EV), HEV=$($stats.platforms.HEV), ICE=$($stats.platforms.ICE)" -ForegroundColor Green
} catch {
    Write-Host "    ✗ Failed to get statistics" -ForegroundColor Red
}

# Test 2: Get Recommendations
Write-Host ""
Write-Host "  Test 2: Getting AI recommendations..." -ForegroundColor Cyan
try {
    $body = @{
        vehicle_model = "Ariya"
        platform = "EV"
        target_systems = @("Battery", "Powertrain")
        top_k = 3
    } | ConvertTo-Json

    $recommendations = Invoke-RestMethod `
        -Uri "http://localhost:8000/api/v1/recommendations" `
        -Method POST `
        -Headers @{"Content-Type"="application/json"} `
        -Body $body

    Write-Host "    ✓ Generated $($recommendations.total_results) recommendations" -ForegroundColor Green
    Write-Host "    Top recommendation: $($recommendations.recommendations[0].test_name)" -ForegroundColor Green
} catch {
    Write-Host "    ✗ Failed to get recommendations" -ForegroundColor Red
}

# Test 3: Calculate ROI
Write-Host ""
Write-Host "  Test 3: Calculating ROI..." -ForegroundColor Cyan
try {
    $body = @{
        baseline_count = 100
        optimization_rate = 0.25
        implementation_cost_gbp = 50000
        analysis_period_years = 3
    } | ConvertTo-Json

    $roi = Invoke-RestMethod `
        -Uri "http://localhost:8000/api/v1/roi" `
        -Method POST `
        -Headers @{"Content-Type"="application/json"} `
        -Body $body

    Write-Host "    ✓ Annual Savings: £$([math]::Round($roi.cost_savings_gbp, 0))" -ForegroundColor Green
    Write-Host "    ✓ ROI: $([math]::Round($roi.roi_percent, 1))%" -ForegroundColor Green
    Write-Host "    ✓ Payback: $([math]::Round($roi.payback_period_months, 1)) months" -ForegroundColor Green
} catch {
    Write-Host "    ✗ Failed to calculate ROI" -ForegroundColor Red
}

# Summary
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Demo Complete!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Browser windows opened:" -ForegroundColor White
Write-Host "  • Dashboard:    http://localhost:8501" -ForegroundColor Cyan
Write-Host "  • API Docs:     http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  • Neo4j:        http://localhost:7474" -ForegroundColor Cyan
Write-Host ""
Write-Host "Quick commands:" -ForegroundColor White
Write-Host "  • View logs:    docker compose logs -f" -ForegroundColor Yellow
Write-Host "  • Check health: make health" -ForegroundColor Yellow
Write-Host "  • Stop all:     docker compose down" -ForegroundColor Yellow
Write-Host ""
Write-Host "For complete demo guide, see: FULL_SYSTEM_DEMO.md" -ForegroundColor White
Write-Host ""

