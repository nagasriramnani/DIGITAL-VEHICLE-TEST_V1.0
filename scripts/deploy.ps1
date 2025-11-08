# Virtual Testing Assistant - Windows PowerShell Deployment Script
# One-command deployment for VTA full stack

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "VTA Deployment Script (PowerShell)" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (-Not (Test-Path .env)) {
    Write-Host "Warning: .env file not found" -ForegroundColor Yellow
    Write-Host "Creating .env from docker.env.example..." -ForegroundColor Yellow
    Copy-Item docker.env.example .env
    Write-Host "Created .env file" -ForegroundColor Green
    Write-Host ""
    Write-Host "IMPORTANT: Please edit .env with your production passwords before deploying!" -ForegroundColor Yellow
    Write-Host "Press any key to continue or Ctrl+C to abort and edit .env first..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# Check Docker is running
Write-Host ""
Write-Host "Step 1/5: Checking Docker..." -ForegroundColor Yellow
try {
    docker info | Out-Null
    Write-Host "  Docker is running" -ForegroundColor Green
} catch {
    Write-Host "  Error: Docker is not running" -ForegroundColor Red
    Write-Host "  Please start Docker Desktop and try again" -ForegroundColor Red
    exit 1
}

# Build images
Write-Host ""
Write-Host "Step 2/5: Building Docker images..." -ForegroundColor Yellow
Write-Host "  (This may take 3-5 minutes on first run)" -ForegroundColor Cyan
docker compose build
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Error building images" -ForegroundColor Red
    exit 1
}
Write-Host "  Images built successfully" -ForegroundColor Green

# Start database services
Write-Host ""
Write-Host "Step 3/5: Starting database services..." -ForegroundColor Yellow
docker compose up -d postgres neo4j redis
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Error starting databases" -ForegroundColor Red
    exit 1
}
Write-Host "  Databases started" -ForegroundColor Green

# Wait for databases
Write-Host ""
Write-Host "Waiting for databases to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Initialize data
Write-Host ""
Write-Host "Step 4/5: Initializing data..." -ForegroundColor Yellow
docker compose run --rm init-data
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Warning: Data initialization had issues (may be normal if already initialized)" -ForegroundColor Yellow
}
Write-Host "  Data initialization complete" -ForegroundColor Green

# Start application services
Write-Host ""
Write-Host "Step 5/5: Starting application services..." -ForegroundColor Yellow
docker compose up -d api dashboard
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Error starting application services" -ForegroundColor Red
    exit 1
}
Write-Host "  Application services started" -ForegroundColor Green

# Wait a bit for services to start
Write-Host ""
Write-Host "Checking service health..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check services
Write-Host ""
Write-Host "Service Status:" -ForegroundColor Cyan
Write-Host "---------------" -ForegroundColor Cyan
docker compose ps

# Health checks
Write-Host ""
Write-Host "Performing health checks..." -ForegroundColor Yellow
$allHealthy = $true

# Check PostgreSQL
try {
    docker compose exec -T postgres pg_isready | Out-Null
    Write-Host "  PostgreSQL: OK" -ForegroundColor Green
} catch {
    Write-Host "  PostgreSQL: NOT READY" -ForegroundColor Yellow
    $allHealthy = $false
}

# Check Neo4j
try {
    $response = Invoke-WebRequest -Uri "http://localhost:7474" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
    Write-Host "  Neo4j:      OK" -ForegroundColor Green
} catch {
    Write-Host "  Neo4j:      NOT READY" -ForegroundColor Yellow
    $allHealthy = $false
}

# Check Redis
try {
    docker compose exec -T redis redis-cli ping | Out-Null
    Write-Host "  Redis:      OK" -ForegroundColor Green
} catch {
    Write-Host "  Redis:      NOT READY" -ForegroundColor Yellow
    $allHealthy = $false
}

# Check API
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
    Write-Host "  API:        OK" -ForegroundColor Green
} catch {
    Write-Host "  API:        NOT READY (may take 30-60 seconds)" -ForegroundColor Yellow
    $allHealthy = $false
}

# Check Dashboard
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8501/_stcore/health" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
    Write-Host "  Dashboard:  OK" -ForegroundColor Green
} catch {
    Write-Host "  Dashboard:  NOT READY (may take 30-60 seconds)" -ForegroundColor Yellow
    $allHealthy = $false
}

# Summary
Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "VTA Deployment Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""

if (-Not $allHealthy) {
    Write-Host "Note: Some services are still starting up." -ForegroundColor Yellow
    Write-Host "Wait 1-2 minutes and check: docker compose ps" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "Access the services:" -ForegroundColor White
Write-Host "  - Dashboard:  http://localhost:8501" -ForegroundColor Cyan
Write-Host "  - API:        http://localhost:8000" -ForegroundColor Cyan
Write-Host "  - API Docs:   http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  - Neo4j:      http://localhost:7474" -ForegroundColor Cyan
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor White
Write-Host "  - View logs:     docker compose logs -f" -ForegroundColor Yellow
Write-Host "  - Check status:  docker compose ps" -ForegroundColor Yellow
Write-Host "  - Stop all:      docker compose down" -ForegroundColor Yellow
Write-Host "  - Restart:       docker compose restart" -ForegroundColor Yellow
Write-Host ""

