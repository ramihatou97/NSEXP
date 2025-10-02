# NSSP Production Deployment Script for Windows

Write-Host "🚀 NSSP Production Deployment Starting..." -ForegroundColor Cyan

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "Warning: .env file not found. Copying from .env.production" -ForegroundColor Yellow
    Copy-Item ".env.production" ".env"
    Write-Host "Please update .env with your production values before continuing!" -ForegroundColor Red
    exit 1
}

# Validate required environment variables
$requiredVars = @("POSTGRES_PASSWORD", "REDIS_PASSWORD", "SECRET_KEY")
$envContent = Get-Content ".env"
$missingVars = $false

foreach ($var in $requiredVars) {
    $found = $false
    $hasDefault = $false
    
    foreach ($line in $envContent) {
        if ($line -match "^$var=(.+)$") {
            $found = $true
            if ($matches[1] -match "^your-") {
                $hasDefault = $true
            }
            break
        }
    }
    
    if (-not $found -or $hasDefault) {
        Write-Host "Error: $var is not properly set in .env file" -ForegroundColor Red
        $missingVars = $true
    }
}

if ($missingVars) {
    exit 1
}

# Create required directories
Write-Host "📁 Creating required directories..." -ForegroundColor Green
$directories = @(
    "logs\backend", "logs\frontend", "logs\nginx",
    "storage", "textbooks", "temp", "backups",
    "nginx\ssl",
    "monitoring\grafana\dashboards",
    "monitoring\grafana\datasources"
)

foreach ($dir in $directories) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
}

# Check for SSL certificates
if (-not (Test-Path "nginx\ssl\cert.pem") -or -not (Test-Path "nginx\ssl\key.pem")) {
    Write-Host "Warning: SSL certificates not found in nginx\ssl\" -ForegroundColor Yellow
    Write-Host "For local testing, you can create self-signed certificates using OpenSSL"
}

# Build images
Write-Host "🔨 Building Docker images..." -ForegroundColor Green
docker-compose -f docker-compose-production.yml build
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to build Docker images" -ForegroundColor Red
    exit 1
}

# Start services
Write-Host "🚀 Starting services..." -ForegroundColor Green
docker-compose -f docker-compose-production.yml up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to start services" -ForegroundColor Red
    exit 1
}

# Wait for services to be healthy
Write-Host "⏳ Waiting for services to be healthy..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check service health
$services = @("nssp_db_primary", "nssp_cache", "nssp_backend", "nssp_frontend", "nssp_nginx")
$allHealthy = $true

foreach ($service in $services) {
    $running = docker ps --format "table {{.Names}}" | Select-String $service
    
    if ($running) {
        try {
            $health = docker inspect --format='{{.State.Health.Status}}' $service 2>$null
            if ($health -eq "healthy" -or [string]::IsNullOrEmpty($health)) {
                Write-Host "✓ $service is running" -ForegroundColor Green
            } else {
                Write-Host "✗ $service is unhealthy (status: $health)" -ForegroundColor Red
                $allHealthy = $false
            }
        } catch {
            Write-Host "✓ $service is running (no health check)" -ForegroundColor Green
        }
    } else {
        Write-Host "✗ $service is not running" -ForegroundColor Red
        $allHealthy = $false
    }
}

if ($allHealthy) {
    Write-Host "`n✅ All services are running successfully!" -ForegroundColor Green
    Write-Host "`n📊 Access your NSSP instance at:" -ForegroundColor Cyan
    Write-Host "  - Application: https://localhost (or https://yourdomain.com)"
    Write-Host "  - API Documentation: https://localhost/api/docs"
    Write-Host "  - Health Check: https://localhost/health"
    
    $grafanaRunning = docker ps --format "table {{.Names}}" | Select-String "grafana"
    if ($grafanaRunning) {
        Write-Host "  - Monitoring (Grafana): http://localhost:3001"
        Write-Host "  - Metrics (Prometheus): http://localhost:9090"
    }
} else {
    Write-Host "`n⚠️  Some services failed to start properly" -ForegroundColor Red
    Write-Host "Check logs with: docker-compose -f docker-compose-production.yml logs"
}

Write-Host "`n📝 Useful commands:" -ForegroundColor Cyan
Write-Host "  - View logs: docker-compose -f docker-compose-production.yml logs -f"
Write-Host "  - Stop services: docker-compose -f docker-compose-production.yml down"
Write-Host "  - Restart services: docker-compose -f docker-compose-production.yml restart"
Write-Host "  - Backup database: docker-compose -f docker-compose-production.yml run backup /backup.sh"