@echo off
REM Neurosurgical Knowledge Management System - Startup Script (Windows)

echo.
echo 🧠 Neurosurgical Knowledge Management System
echo ==============================================
echo.

REM Check if Docker is available
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker not found
    echo.
    echo Please install Docker Desktop from: https://www.docker.com/products/docker-desktop
    echo Or follow manual setup in QUICKSTART.md
    exit /b 1
)

echo ✅ Docker found
echo.
echo Choose startup method:
echo 1) Docker Compose (Recommended - Everything automated)
echo 2) Manual Setup (Backend + Frontend separately)
set /p choice="Enter choice (1 or 2): "

if "%choice%"=="1" (
    echo.
    echo 🐳 Starting with Docker Compose...
    echo.
    
    REM Check if .env exists
    if not exist "backend\.env" (
        echo Creating .env file from template...
        copy .env.development backend\.env
    )
    
    echo Starting all services (database, cache, backend, frontend)...
    docker compose -f docker-compose-simple.yml up -d
    
    echo.
    echo ⏳ Waiting for services to be ready...
    timeout /t 10 /nobreak >nul
    
    echo.
    echo 🎉 System started successfully!
    echo.
    echo Access your application:
    echo   Frontend:  http://localhost:3000
    echo   Backend:   http://localhost:8000
    echo   API Docs:  http://localhost:8000/api/docs
    echo.
    echo View logs with: docker compose -f docker-compose-simple.yml logs -f
    echo Stop system with: docker compose -f docker-compose-simple.yml down
    
) else if "%choice%"=="2" (
    echo.
    echo 📝 Manual setup requires:
    echo   1. PostgreSQL database running
    echo   2. Python 3.11+ installed
    echo   3. Node.js 18+ installed
    echo.
    echo See QUICKSTART.md for detailed manual setup instructions
) else (
    echo Invalid choice. Exiting.
    exit /b 1
)
