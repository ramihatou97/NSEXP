#!/bin/bash
# Quick Docker Build and Test Script
# Usage: ./quick-docker-test.sh [simple|production]

set -e

BUILD_TYPE=${1:-simple}
COLOR_GREEN='\033[0;32m'
COLOR_YELLOW='\033[1;33m'
COLOR_RED='\033[0;31m'
COLOR_RESET='\033[0m'

echo -e "${COLOR_GREEN}🐳 NSEXP Docker Build & Test${COLOR_RESET}"
echo "Build type: $BUILD_TYPE"
echo "================================"
echo ""

# Clean up old containers
echo -e "${COLOR_YELLOW}🧹 Cleaning up old containers...${COLOR_RESET}"
docker compose -f docker-compose-simple.yml down 2>/dev/null || true
docker system prune -f > /dev/null 2>&1

# Build based on type
if [ "$BUILD_TYPE" == "simple" ]; then
    echo -e "${COLOR_GREEN}📦 Building simplified backend...${COLOR_RESET}"
    cd backend
    docker build -f Dockerfile.simple -t nsexp-backend:test . || {
        echo -e "${COLOR_RED}❌ Backend build failed!${COLOR_RESET}"
        exit 1
    }
    cd ..
    echo -e "${COLOR_GREEN}✅ Backend build successful!${COLOR_RESET}"
    
elif [ "$BUILD_TYPE" == "production" ]; then
    echo -e "${COLOR_GREEN}📦 Building production backend...${COLOR_RESET}"
    cd backend
    docker build -f Dockerfile -t nsexp-backend:test . || {
        echo -e "${COLOR_RED}❌ Backend build failed!${COLOR_RESET}"
        exit 1
    }
    cd ..
    echo -e "${COLOR_GREEN}✅ Backend build successful!${COLOR_RESET}"
else
    echo -e "${COLOR_RED}❌ Invalid build type: $BUILD_TYPE${COLOR_RESET}"
    echo "Usage: ./quick-docker-test.sh [simple|production]"
    exit 1
fi

echo ""
echo -e "${COLOR_GREEN}🧪 Testing image...${COLOR_RESET}"

# Test package imports
echo -e "${COLOR_YELLOW}  Testing Python imports...${COLOR_RESET}"
docker run --rm nsexp-backend:test python -c "
import sys
try:
    import fastapi
    import uvicorn
    import sqlalchemy
    import asyncpg
    import pydantic
    print('✅ All critical packages imported successfully')
    sys.exit(0)
except ImportError as e:
    print(f'❌ Import failed: {e}')
    sys.exit(1)
" || {
    echo -e "${COLOR_RED}❌ Package import test failed!${COLOR_RESET}"
    exit 1
}

# Check image size
echo ""
echo -e "${COLOR_YELLOW}📊 Image information:${COLOR_RESET}"
docker images nsexp-backend:test --format "  Size: {{.Size}}, Created: {{.CreatedSince}}"

echo ""
echo -e "${COLOR_GREEN}✅ All tests passed!${COLOR_RESET}"
echo ""
echo "Next steps:"
echo "  1. Run full stack: docker compose -f docker-compose-simple.yml up"
echo "  2. Test backend: curl http://localhost:8000/health"
echo "  3. View API docs: http://localhost:8000/api/docs"
echo ""
