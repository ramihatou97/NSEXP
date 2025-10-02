#!/bin/bash
# NSSP Production Deployment Script

set -e

echo "🚀 NSSP Production Deployment Starting..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Warning: .env file not found. Copying from .env.production${NC}"
    cp .env.production .env
    echo -e "${RED}Please update .env with your production values before continuing!${NC}"
    exit 1
fi

# Validate required environment variables
required_vars=("POSTGRES_PASSWORD" "REDIS_PASSWORD" "SECRET_KEY")
for var in "${required_vars[@]}"; do
    if grep -q "^${var}=your-" .env || ! grep -q "^${var}=" .env; then
        echo -e "${RED}Error: ${var} is not properly set in .env file${NC}"
        exit 1
    fi
done

# Create required directories
echo "📁 Creating required directories..."
mkdir -p logs/backend logs/frontend logs/nginx
mkdir -p storage textbooks temp backups
mkdir -p nginx/ssl
mkdir -p monitoring/grafana/dashboards
mkdir -p monitoring/grafana/datasources

# Check for SSL certificates
if [ ! -f nginx/ssl/cert.pem ] || [ ! -f nginx/ssl/key.pem ]; then
    echo -e "${YELLOW}Warning: SSL certificates not found in nginx/ssl/${NC}"
    echo "For local testing, you can create self-signed certificates:"
    echo "  openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout nginx/ssl/key.pem -out nginx/ssl/cert.pem"
fi

# Build images
echo "🔨 Building Docker images..."
docker-compose -f docker-compose-production.yml build

# Start services
echo "🚀 Starting services..."
docker-compose -f docker-compose-production.yml up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check service health
services=("nssp_db_primary" "nssp_cache" "nssp_backend" "nssp_frontend" "nssp_nginx")
all_healthy=true

for service in "${services[@]}"; do
    if docker ps | grep -q "$service"; then
        health=$(docker inspect --format='{{.State.Health.Status}}' "$service" 2>/dev/null || echo "none")
        if [ "$health" = "healthy" ] || [ "$health" = "none" ]; then
            echo -e "${GREEN}✓ $service is running${NC}"
        else
            echo -e "${RED}✗ $service is unhealthy (status: $health)${NC}"
            all_healthy=false
        fi
    else
        echo -e "${RED}✗ $service is not running${NC}"
        all_healthy=false
    fi
done

if $all_healthy; then
    echo -e "${GREEN}✅ All services are running successfully!${NC}"
    echo ""
    echo "📊 Access your NSSP instance at:"
    echo "  - Application: https://localhost (or https://yourdomain.com)"
    echo "  - API Documentation: https://localhost/api/docs"
    echo "  - Health Check: https://localhost/health"
    
    if docker-compose -f docker-compose-production.yml ps | grep -q grafana; then
        echo "  - Monitoring (Grafana): http://localhost:3001"
        echo "  - Metrics (Prometheus): http://localhost:9090"
    fi
else
    echo -e "${RED}⚠️  Some services failed to start properly${NC}"
    echo "Check logs with: docker-compose -f docker-compose-production.yml logs"
fi

echo ""
echo "📝 Useful commands:"
echo "  - View logs: docker-compose -f docker-compose-production.yml logs -f"
echo "  - Stop services: docker-compose -f docker-compose-production.yml down"
echo "  - Restart services: docker-compose -f docker-compose-production.yml restart"
echo "  - Backup database: docker-compose -f docker-compose-production.yml run backup /backup.sh"