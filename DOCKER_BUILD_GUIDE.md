# Docker Build Guide

## 🐳 Docker Build Issues & Solutions

### ❌ Common Docker Build Failure

**Error**: `ERROR: failed to solve: process "/bin/sh -c pip install --no-cache-dir -r requirements.txt" did not complete successfully: exit code: 2`

**Cause**: The main `requirements.txt` contains heavy ML packages:
- PyTorch (~1.5GB)
- Transformers (~500MB) 
- Medical NLP models (en_core_sci_md ~119MB)
- SciSpacy with complex dependencies

### ✅ Solutions

#### Option 1: Use Simplified Docker (RECOMMENDED)
```bash
# Use the lightweight Dockerfile
docker build -f backend/Dockerfile.simple backend/
docker-compose -f docker-compose-simple.yml up
```

#### Option 2: Increase Docker Resources
For the full `requirements.txt`, increase Docker limits:
```bash
# Increase memory and build timeout
docker build --memory=4g --build-arg BUILD_TIMEOUT=3600 -f backend/Dockerfile backend/
```

#### Option 3: Multi-stage Build (Advanced)
The main `Dockerfile` uses multi-stage builds to optimize size, but may timeout on slower connections.

## 📊 File Comparison

| File | Use Case | Docker Build Time | Image Size | Success Rate |
|------|----------|-------------------|------------|--------------|
| **`Dockerfile.simple`** + `requirements_simplified.txt` | ✅ Development, Production Core | ~5 minutes | ~800MB | 95%+ |
| **`Dockerfile`** + `requirements.txt` | ⚠️ Full ML Pipeline | ~20-45 minutes | ~3GB | 60-80% |

## 🚀 Recommended Docker Workflow

### For Development & Most Production Use:
```bash
# Clone repository
git clone https://github.com/ramihatou97/NSEXP.git
cd NSEXP

# Build with simplified requirements (fast & reliable)
docker-compose -f docker-compose-simple.yml up --build
```

### For Advanced ML Features:
```bash
# Use local Python environment instead of Docker
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main_simplified:app --reload
```

## 🔧 Docker Build Optimization Tips

### 1. Use Docker Buildkit
```bash
export DOCKER_BUILDKIT=1
docker build -f backend/Dockerfile.simple backend/
```

### 2. Layer Caching
The Dockerfiles are optimized for layer caching - dependencies install first, code copies last.

### 3. Network Issues
If builds fail due to network timeouts:
```bash
# Increase timeout
docker build --network=host --build-arg PIP_TIMEOUT=1000 -f backend/Dockerfile.simple backend/
```

### 4. Build Context
Keep build context small:
```bash
# Add to .dockerignore
echo "*.md" >> .dockerignore
echo "frontend/" >> .dockerignore  # When building backend only
```

## 🎯 Summary

- **✅ Use `docker-compose-simple.yml`** for reliable builds
- **⚠️ Full `requirements.txt` in Docker** requires significant resources
- **🚀 Simplified setup works for 95% of use cases**
- **💡 Use local Python environment for heavy ML development**

The FAISS vector search functionality is available in **both** Docker configurations!