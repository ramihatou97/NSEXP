#!/bin/bash
# Quick validation script for Docker setup

echo "🔍 Docker Setup Validation"
echo "=========================="
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi
echo "✅ Docker is installed: $(docker --version)"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "⚠️  docker-compose not found, checking for 'docker compose'"
    if ! docker compose version &> /dev/null; then
        echo "❌ Docker Compose is not available"
        exit 1
    fi
    echo "✅ Docker Compose is available: $(docker compose version)"
    COMPOSE_CMD="docker compose"
else
    echo "✅ Docker Compose is installed: $(docker-compose --version)"
    COMPOSE_CMD="docker-compose"
fi
echo ""

# Check Dockerfiles exist
echo "📁 Checking Dockerfiles..."
files=(
    "backend/Dockerfile"
    "backend/Dockerfile.simple"
    "frontend/Dockerfile"
    "frontend/Dockerfile.simple"
    "docker-compose-simple.yml"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file NOT FOUND"
        exit 1
    fi
done
echo ""

# Check .dockerignore files
echo "📁 Checking .dockerignore files..."
if [ -f "backend/.dockerignore" ]; then
    echo "  ✅ backend/.dockerignore"
else
    echo "  ⚠️  backend/.dockerignore not found (recommended)"
fi

if [ -f "frontend/.dockerignore" ]; then
    echo "  ✅ frontend/.dockerignore"
else
    echo "  ⚠️  frontend/.dockerignore not found (recommended)"
fi
echo ""

# Check requirements files
echo "📦 Checking requirements files..."
if [ -f "backend/requirements_simplified.txt" ]; then
    echo "  ✅ backend/requirements_simplified.txt ($(wc -l < backend/requirements_simplified.txt) lines)"
else
    echo "  ❌ backend/requirements_simplified.txt NOT FOUND"
    exit 1
fi

if [ -f "backend/requirements.txt" ]; then
    echo "  ✅ backend/requirements.txt ($(wc -l < backend/requirements.txt) lines)"
else
    echo "  ⚠️  backend/requirements.txt not found"
fi
echo ""

# Check for duplicate packages
echo "🔍 Checking for duplicate packages in requirements_simplified.txt..."
duplicates=$(sort backend/requirements_simplified.txt | grep -v "^#" | grep -v "^$" | cut -d'=' -f1 | uniq -d)
if [ -z "$duplicates" ]; then
    echo "  ✅ No duplicate packages found"
else
    echo "  ⚠️  Duplicate packages found:"
    echo "$duplicates"
fi
echo ""

# Check if easyocr is in simplified requirements
echo "🔍 Checking for heavy dependencies..."
if grep -q "easyocr" backend/requirements_simplified.txt; then
    echo "  ⚠️  easyocr found in simplified requirements (causes 2GB+ install)"
else
    echo "  ✅ easyocr not in simplified requirements (good for Docker)"
fi

if grep -q "torch" backend/requirements_simplified.txt; then
    echo "  ⚠️  torch found in simplified requirements (very heavy)"
else
    echo "  ✅ torch not in simplified requirements"
fi
echo ""

# Check backend application files
echo "📄 Checking backend application files..."
if [ -f "backend/main_simplified.py" ]; then
    echo "  ✅ backend/main_simplified.py"
else
    echo "  ❌ backend/main_simplified.py NOT FOUND"
    exit 1
fi
echo ""

# Check if images exist
echo "🖼️  Checking Docker images..."
if docker images | grep -q "nsexp-backend"; then
    echo "  ✅ nsexp-backend images found:"
    docker images | grep "nsexp-backend" | awk '{print "     " $1 ":" $2 " (" $7 ")"}'
else
    echo "  ⚠️  No nsexp-backend images found (run docker build first)"
fi
echo ""

# Summary
echo "=========================="
echo "✅ Docker setup validation complete!"
echo ""
echo "Next steps:"
echo "1. Build images:"
echo "   cd backend && docker build -f Dockerfile.simple -t nsexp-backend:simple ."
echo ""
echo "2. Or use docker-compose:"
echo "   $COMPOSE_CMD -f docker-compose-simple.yml up --build"
echo ""
echo "3. Verify services:"
echo "   curl http://localhost:8000/health"
echo "   curl http://localhost:8000/api/docs"
echo "   curl http://localhost:3000"
echo ""
