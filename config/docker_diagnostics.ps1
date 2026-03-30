# Docker Diagnostics and Troubleshooting Script
# Run this with: powershell -ExecutionPolicy Bypass -File .\docker_diagnostics.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Docker Diagnostics" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check Docker Installation
Write-Host "[1] Checking Docker Installation..." -ForegroundColor Yellow
try {
    $dockerVersion = docker version --format "Client: {{.Client.Version}}, Server: {{.Server.Version}}"
    Write-Host "✓ Docker is installed: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 2. Check Docker Daemon
Write-Host "[2] Checking Docker Daemon..." -ForegroundColor Yellow
try {
    $ps = docker ps 2>$null
    Write-Host "✓ Docker daemon is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker daemon is NOT running. Start Docker Desktop!" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 3. Check API Versions
Write-Host "[3] Checking API Versions..." -ForegroundColor Yellow
try {
    $apiVersions = docker version --format "Client API: {{.Client.APIVersion}}, Server API: {{.Server.APIVersion}}"
    Write-Host "✓ $apiVersions" -ForegroundColor Green
} catch {
    Write-Host "✗ Could not retrieve API versions" -ForegroundColor Red
}

Write-Host ""

# 4. Test connectivity to Docker Hub
Write-Host "[4] Testing Docker Hub Connectivity..." -ForegroundColor Yellow
try {
    docker pull alpine:latest 2>&1 | Out-Null
    Write-Host "✓ Docker Hub is accessible" -ForegroundColor Green
} catch {
    Write-Host "✗ Cannot reach Docker Hub. Check internet connection." -ForegroundColor Red
}

Write-Host ""

# 5. Test Grafana image pull
Write-Host "[5] Testing Grafana Image Pull..." -ForegroundColor Yellow
try {
    Write-Host "   Pulling grafana/grafana:latest..." -ForegroundColor Cyan
    docker pull grafana/grafana:latest 2>&1
    Write-Host "✓ Grafana image pulled successfully" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to pull Grafana image" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
}

Write-Host ""

# 6. Check docker-compose
Write-Host "[6] Checking docker-compose..." -ForegroundColor Yellow
try {
    $composeVersion = docker-compose version --short
    Write-Host "✓ docker-compose is installed: v$composeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ docker-compose is not installed" -ForegroundColor Red
}

Write-Host ""

# 7. Validate docker-compose.yml
Write-Host "[7] Validating docker-compose.yml..." -ForegroundColor Yellow
try {
    docker-compose config > $null
    Write-Host "✓ docker-compose.yml is valid" -ForegroundColor Green
} catch {
    Write-Host "✗ docker-compose.yml has errors" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Diagnostics Complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. If all checks passed, run: docker-compose up -d" -ForegroundColor Cyan
Write-Host "2. If Docker daemon is not running, start Docker Desktop" -ForegroundColor Cyan
Write-Host "3. If Grafana pull failed, check internet connection" -ForegroundColor Cyan
