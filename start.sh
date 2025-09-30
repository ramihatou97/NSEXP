#!/bin/bash

# Neurosurgical Knowledge Management System - Startup Script
# This script helps you start the system quickly

set -e

echo "🧠 Neurosurgical Knowledge Management System"
echo "=============================================="
echo ""

# Check if Docker is available
if command -v docker &> /dev/null; then
    echo "✅ Docker found"
    
    # Ask user which method to use
    echo ""
    echo "Choose startup method:"
    echo "1) Docker Compose (Recommended - Everything automated)"
    echo "2) Manual Setup (Backend + Frontend separately)"
    read -p "Enter choice (1 or 2): " choice
    
    if [ "$choice" = "1" ]; then
        echo ""
        echo "🐳 Starting with Docker Compose..."
        echo ""
        
        # Check if .env exists, if not create from template
        if [ ! -f "backend/.env" ]; then
            echo "Creating .env file from template..."
            cp .env.development backend/.env
        fi
        
        # Start services
        echo "Starting all services (database, cache, backend, frontend)..."
        docker compose -f docker-compose-simple.yml up -d
        
        echo ""
        echo "⏳ Waiting for services to be ready..."
        sleep 10
        
        # Check health
        echo ""
        echo "🔍 Checking service health..."
        
        if curl -s http://localhost:8000/health > /dev/null; then
            echo "✅ Backend is healthy"
        else
            echo "⚠️  Backend might not be ready yet, give it a few more seconds"
        fi
        
        echo ""
        echo "🎉 System started successfully!"
        echo ""
        echo "Access your application:"
        echo "  Frontend:  http://localhost:3000"
        echo "  Backend:   http://localhost:8000"
        echo "  API Docs:  http://localhost:8000/api/docs"
        echo ""
        echo "View logs with: docker compose -f docker-compose-simple.yml logs -f"
        echo "Stop system with: docker compose -f docker-compose-simple.yml down"
        
    elif [ "$choice" = "2" ]; then
        echo ""
        echo "📝 Manual setup requires:"
        echo "  1. PostgreSQL database running"
        echo "  2. Python 3.11+ installed"
        echo "  3. Node.js 18+ installed"
        echo ""
        echo "See QUICKSTART.md for detailed manual setup instructions"
        echo ""
        echo "Quick manual setup:"
        echo ""
        echo "Terminal 1 (Backend):"
        echo "  cd backend"
        echo "  python -m venv venv"
        echo "  source venv/bin/activate  # or venv\\Scripts\\activate on Windows"
        echo "  pip install -r requirements_simplified.txt"
        echo "  uvicorn main_simplified:app --reload"
        echo ""
        echo "Terminal 2 (Frontend):"
        echo "  cd frontend"
        echo "  npm install"
        echo "  npm run dev"
    else
        echo "Invalid choice. Exiting."
        exit 1
    fi
    
else
    echo "❌ Docker not found"
    echo ""
    echo "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop"
    echo "Or follow manual setup in QUICKSTART.md"
    exit 1
fi
