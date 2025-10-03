#!/bin/bash
# Frontend Docker Build Validation Script

set -e

echo "================================================"
echo "Frontend Docker Build Validation"
echo "================================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -d "frontend" ]; then
    echo -e "${RED}✗ Error: frontend directory not found${NC}"
    echo "Please run this script from the repository root"
    exit 1
fi

echo "1. Checking frontend directory..."
cd frontend

# Check for required files
echo ""
echo "2. Validating required files..."
files_missing=0

if [ ! -f "package.json" ]; then
    echo -e "${RED}✗ Missing: package.json${NC}"
    files_missing=1
else
    echo -e "${GREEN}✓ Found: package.json${NC}"
fi

if [ ! -f "package-lock.json" ]; then
    echo -e "${RED}✗ Missing: package-lock.json${NC}"
    files_missing=1
else
    echo -e "${GREEN}✓ Found: package-lock.json${NC}"
    # Check size
    size=$(wc -l < package-lock.json)
    echo "  Size: $size lines"
fi

if [ ! -f "Dockerfile" ]; then
    echo -e "${RED}✗ Missing: Dockerfile${NC}"
    files_missing=1
else
    echo -e "${GREEN}✓ Found: Dockerfile${NC}"
fi

if [ ! -f ".dockerignore" ]; then
    echo -e "${YELLOW}⚠ Missing: .dockerignore (optional but recommended)${NC}"
else
    echo -e "${GREEN}✓ Found: .dockerignore${NC}"
fi

if [ ! -f "next.config.js" ]; then
    echo -e "${RED}✗ Missing: next.config.js${NC}"
    files_missing=1
else
    echo -e "${GREEN}✓ Found: next.config.js${NC}"
fi

if [ $files_missing -eq 1 ]; then
    echo -e "\n${RED}✗ Some required files are missing${NC}"
    exit 1
fi

# Validate Dockerfile content
echo ""
echo "3. Validating Dockerfile configuration..."

# Check that npm ci is used (not npm install)
if grep -q "npm ci" Dockerfile; then
    echo -e "${GREEN}✓ Uses 'npm ci' for reproducible builds${NC}"
else
    echo -e "${YELLOW}⚠ Warning: 'npm ci' not found, using 'npm install'?${NC}"
fi

# Check that --only=production is NOT used in deps stage (we need devDeps for build)
if grep -q "npm ci --only=production" Dockerfile; then
    echo -e "${RED}✗ Error: 'npm ci --only=production' found${NC}"
    echo "  This will skip devDependencies needed for the build!"
    echo "  Use 'npm ci' without flags in the deps stage"
    exit 1
else
    echo -e "${GREEN}✓ npm ci configured correctly (includes devDependencies)${NC}"
fi

# Check for multi-stage build
if grep -q "AS deps" Dockerfile && grep -q "AS builder" Dockerfile && grep -q "AS runner" Dockerfile; then
    echo -e "${GREEN}✓ Multi-stage build detected${NC}"
else
    echo -e "${YELLOW}⚠ Multi-stage build not detected (may result in larger image)${NC}"
fi

# Check for standalone output in next.config.js
if [ -f "next.config.js" ]; then
    if grep -q "output.*standalone" next.config.js || grep -q "'standalone'" next.config.js || grep -q '"standalone"' next.config.js; then
        echo -e "${GREEN}✓ Next.js standalone output configured${NC}"
    else
        echo -e "${YELLOW}⚠ Next.js standalone output not configured (image may be larger)${NC}"
    fi
fi

# Check package.json for required scripts
echo ""
echo "4. Checking package.json scripts..."
if grep -q '"build"' package.json; then
    echo -e "${GREEN}✓ 'build' script found${NC}"
else
    echo -e "${RED}✗ Missing 'build' script in package.json${NC}"
    exit 1
fi

if grep -q '"start"' package.json; then
    echo -e "${GREEN}✓ 'start' script found${NC}"
else
    echo -e "${RED}✗ Missing 'start' script in package.json${NC}"
    exit 1
fi

# Summary
echo ""
echo "================================================"
echo -e "${GREEN}✓ Validation complete!${NC}"
echo "================================================"
echo ""
echo "The frontend Docker build configuration is valid."
echo ""
echo "To build the Docker image, run:"
echo "  docker build -t nsexp-frontend:latest -f frontend/Dockerfile frontend/"
echo ""
echo "To build with build args:"
echo "  docker build -t nsexp-frontend:latest \\"
echo "    --build-arg NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1 \\"
echo "    --build-arg NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws \\"
echo "    -f frontend/Dockerfile frontend/"
echo ""
echo "Or use docker-compose:"
echo "  docker-compose up --build"
echo ""

cd ..
exit 0
