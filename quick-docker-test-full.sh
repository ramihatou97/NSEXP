#!/bin/bash
# Quick Docker Full ML Build and Test Script
# Usage: ./quick-docker-test-full.sh

set -e

COLOR_GREEN='\033[0;32m'
COLOR_YELLOW='\033[1;33m'
COLOR_RED='\033[0;31m'
COLOR_RESET='\033[0m'

echo -e "${COLOR_GREEN}🐳 NSEXP Full ML Docker Build & Test${COLOR_RESET}"
echo "================================"
echo ""
echo -e "${COLOR_YELLOW}⚠️  WARNING: This build includes PyTorch and ML libraries${COLOR_RESET}"
echo "   - Build time: 15-20 minutes"
echo "   - Disk space: ~10GB required"
echo "   - Memory: 8GB RAM recommended"
echo ""
read -p "Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

# Clean up old containers
echo -e "${COLOR_YELLOW}🧹 Cleaning up old containers...${COLOR_RESET}"
docker compose -f docker-compose-full.yml down 2>/dev/null || true

echo ""
echo -e "${COLOR_GREEN}📦 Building full ML backend (this will take 15-20 minutes)...${COLOR_RESET}"
cd backend
docker build -f Dockerfile.full -t nsexp-backend:test-full . || {
    echo -e "${COLOR_RED}❌ Backend build failed!${COLOR_RESET}"
    exit 1
}
cd ..
echo -e "${COLOR_GREEN}✅ Backend build successful!${COLOR_RESET}"

echo ""
echo -e "${COLOR_GREEN}🧪 Testing ML packages...${COLOR_RESET}"

# Test ML package imports
echo -e "${COLOR_YELLOW}  Testing ML imports (PyTorch, transformers, scispacy)...${COLOR_RESET}"
docker run --rm nsexp-backend:test-full python -c "
import sys
try:
    import torch
    print('✅ PyTorch version:', torch.__version__)
    
    import transformers
    print('✅ Transformers version:', transformers.__version__)
    
    import scispacy
    print('✅ scispaCy imported successfully')
    
    import fastapi
    import uvicorn
    import sqlalchemy
    print('✅ Core packages working')
    
    sys.exit(0)
except ImportError as e:
    print(f'❌ Import failed: {e}')
    sys.exit(1)
" || {
    echo -e "${COLOR_RED}❌ ML package import test failed!${COLOR_RESET}"
    exit 1
}

# Check image size
echo ""
echo -e "${COLOR_YELLOW}📊 Image information:${COLOR_RESET}"
docker images nsexp-backend:test-full --format "  Size: {{.Size}}, Created: {{.CreatedSince}}"

echo ""
echo -e "${COLOR_GREEN}✅ All tests passed!${COLOR_RESET}"
echo ""
echo "Next steps:"
echo "  1. Run full stack: docker compose -f docker-compose-full.yml up"
echo "  2. Test backend: curl http://localhost:8000/health"
echo "  3. View API docs: http://localhost:8000/api/docs"
echo ""
echo -e "${COLOR_YELLOW}Note: Full ML stack requires:${COLOR_RESET}"
echo "  - 8GB+ RAM"
echo "  - PostgreSQL, Redis, Elasticsearch, Qdrant"
echo "  - See DOCKER_BUILD_OPTIONS.md for details"
echo ""
