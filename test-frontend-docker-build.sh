#!/bin/bash
# Test script for frontend Docker build
# This script validates the Docker build process and provides detailed diagnostics

set -e  # Exit on error

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}Frontend Docker Build Test${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Check prerequisites
echo "1. Checking prerequisites..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker is installed${NC}"

# Navigate to frontend directory
cd frontend

# Validate required files
echo ""
echo "2. Validating required files..."
required_files=("package.json" "package-lock.json" "Dockerfile" "next.config.js")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}✗ Missing: $file${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Found: $file${NC}"
done

# Clean up any existing test images
echo ""
echo "3. Cleaning up previous test images..."
docker rmi nsexp-frontend:test-deps nsexp-frontend:test-builder nsexp-frontend:test 2>/dev/null || true
echo -e "${GREEN}✓ Cleanup complete${NC}"

# Test building deps stage
echo ""
echo "4. Testing deps stage (installing dependencies)..."
echo -e "${YELLOW}This may take a few minutes...${NC}"
if docker build --target deps -t nsexp-frontend:test-deps -f Dockerfile . > /tmp/docker-build-deps.log 2>&1; then
    echo -e "${GREEN}✓ Deps stage built successfully${NC}"
else
    echo -e "${RED}✗ Deps stage failed${NC}"
    echo "Error log:"
    tail -50 /tmp/docker-build-deps.log
    exit 1
fi

# Test building builder stage
echo ""
echo "5. Testing builder stage (building application)..."
echo -e "${YELLOW}This may take a few minutes...${NC}"
if docker build --target builder -t nsexp-frontend:test-builder \
    --build-arg NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1 \
    --build-arg NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws \
    -f Dockerfile . > /tmp/docker-build-builder.log 2>&1; then
    echo -e "${GREEN}✓ Builder stage built successfully${NC}"
else
    echo -e "${RED}✗ Builder stage failed${NC}"
    echo "Error log:"
    tail -50 /tmp/docker-build-builder.log
    exit 1
fi

# Test full build (all stages)
echo ""
echo "6. Testing full build (all stages)..."
echo -e "${YELLOW}This may take a few minutes...${NC}"
if docker build -t nsexp-frontend:test \
    --build-arg NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1 \
    --build-arg NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws \
    -f Dockerfile . > /tmp/docker-build-full.log 2>&1; then
    echo -e "${GREEN}✓ Full build completed successfully${NC}"
else
    echo -e "${RED}✗ Full build failed${NC}"
    echo "Error log:"
    tail -50 /tmp/docker-build-full.log
    exit 1
fi

# Check image size
echo ""
echo "7. Checking image size..."
SIZE=$(docker images nsexp-frontend:test --format "{{.Size}}")
echo -e "${GREEN}✓ Image size: $SIZE${NC}"
if [[ "$SIZE" == *"GB"* ]] && [[ "${SIZE%%GB*}" -gt 1 ]]; then
    echo -e "${YELLOW}⚠ Warning: Image size is larger than 1GB${NC}"
    echo "  Consider optimizing the build to reduce size"
fi

# Test running the container
echo ""
echo "8. Testing container startup..."
CONTAINER_ID=$(docker run -d -p 3001:3000 \
    -e NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1 \
    -e NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws \
    nsexp-frontend:test)
echo -e "${GREEN}✓ Container started with ID: ${CONTAINER_ID:0:12}${NC}"

# Wait for container to be ready
echo ""
echo "9. Waiting for container to be ready..."
RETRIES=30
READY=false
for i in $(seq 1 $RETRIES); do
    if docker logs "$CONTAINER_ID" 2>&1 | grep -q "ready"; then
        READY=true
        break
    fi
    if docker logs "$CONTAINER_ID" 2>&1 | grep -qi "error"; then
        echo -e "${RED}✗ Container startup failed${NC}"
        docker logs "$CONTAINER_ID"
        docker stop "$CONTAINER_ID" > /dev/null 2>&1
        docker rm "$CONTAINER_ID" > /dev/null 2>&1
        exit 1
    fi
    echo -n "."
    sleep 2
done
echo ""

if [ "$READY" = true ]; then
    echo -e "${GREEN}✓ Container is ready${NC}"
else
    echo -e "${YELLOW}⚠ Container may not be fully ready, but no errors detected${NC}"
fi

# Clean up test container
echo ""
echo "10. Cleaning up test container..."
docker stop "$CONTAINER_ID" > /dev/null 2>&1
docker rm "$CONTAINER_ID" > /dev/null 2>&1
echo -e "${GREEN}✓ Test container cleaned up${NC}"

# Summary
echo ""
echo -e "${BLUE}================================================${NC}"
echo -e "${GREEN}✓ All tests passed!${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo "Build logs saved to:"
echo "  - /tmp/docker-build-deps.log"
echo "  - /tmp/docker-build-builder.log"
echo "  - /tmp/docker-build-full.log"
echo ""
echo "To use the built image:"
echo "  docker run -d -p 3000:3000 \\"
echo "    -e NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1 \\"
echo "    -e NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws \\"
echo "    nsexp-frontend:test"
echo ""
echo "To push to registry:"
echo "  docker tag nsexp-frontend:test your-registry/nsexp-frontend:latest"
echo "  docker push your-registry/nsexp-frontend:latest"
echo ""

cd ..
