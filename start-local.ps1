# NSSP Local Testing - Quick Start Script for Windows

Write-Host "🚀 Starting NSSP for Local Testing..." -ForegroundColor Cyan

# Check if Docker is running
try {
    docker info | Out-Null
    Write-Host "✓ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Copy local environment file
if (-not (Test-Path ".env")) {
    Write-Host "📝 Creating .env from .env.local..." -ForegroundColor Yellow
    Copy-Item ".env.local" ".env"
    Write-Host "✓ .env file created" -ForegroundColor Green
} else {
    Write-Host "✓ .env file already exists" -ForegroundColor Green
}

# Create required directories
Write-Host "📁 Creating required directories..." -ForegroundColor Yellow
$directories = @("logs", "storage", "textbooks", "temp", "backups")
foreach ($dir in $directories) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
}
Write-Host "✓ Directories created" -ForegroundColor Green

# Stop any existing containers
Write-Host "🛑 Stopping any existing containers..." -ForegroundColor Yellow
docker-compose -f docker-compose-simple.yml down 2>$null

# Start services
Write-Host "🚀 Starting NSSP services..." -ForegroundColor Green
docker-compose -f docker-compose-simple.yml up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ NSSP is starting up!" -ForegroundColor Green
    Write-Host "`n⏳ Waiting 15 seconds for services to initialize..." -ForegroundColor Yellow
    Start-Sleep -Seconds 15
    
    Write-Host "`n🌐 Access your NSSP application:" -ForegroundColor Cyan
    Write-Host "   Frontend:      http://localhost:3000" -ForegroundColor White
    Write-Host "   Backend API:   http://localhost:8000" -ForegroundColor White
    Write-Host "   API Docs:      http://localhost:8000/api/docs" -ForegroundColor White
    Write-Host "   Health Check:  http://localhost:8000/health" -ForegroundColor White
    
    Write-Host "`n📊 Checking service status..." -ForegroundColor Yellow
    docker-compose -f docker-compose-simple.yml ps
    
    Write-Host "`n📝 Useful commands:" -ForegroundColor Cyan
    Write-Host "   View logs:     docker-compose -f docker-compose-simple.yml logs -f"
    Write-Host "   Stop services: docker-compose -f docker-compose-simple.yml down"
    Write-Host "   Restart:       docker-compose -f docker-compose-simple.yml restart"
    
    Write-Host "`n🎉 Ready to use! Open your browser to http://localhost:3000" -ForegroundColor Green
} else {
    Write-Host "`n❌ Failed to start services. Check the error messages above." -ForegroundColor Red
    Write-Host "Try running: docker-compose -f docker-compose-simple.yml logs" -ForegroundColor Yellow
}