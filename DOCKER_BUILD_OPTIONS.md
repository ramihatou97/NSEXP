# Docker Build Options - Simplified vs Full ML Stack

## Overview

This project provides **two Docker build options** to suit different use cases:

1. **Simplified Build** (Recommended for most users)
   - Lightweight and fast
   - ~300MB installation
   - 3-5 minute build time
   - Perfect for development and testing

2. **Full ML Build** (For advanced ML features)
   - Complete ML stack with PyTorch, transformers, medical NLP
   - ~3GB installation
   - 15-20 minute build time
   - Required for advanced medical NLP and research features

## Quick Start

### Option 1: Simplified Build (Recommended)

```bash
# Uses requirements_simplified.txt (~300MB)
docker compose -f docker-compose-simple.yml up --build

# Or build backend only
cd backend
docker build -f Dockerfile.simple -t nsexp-backend:simple .
```

**What you get:**
- ✅ FastAPI core
- ✅ Basic AI (OpenAI, Claude, Gemini)
- ✅ PDF processing with pytesseract
- ✅ Vector search with FAISS
- ✅ PostgreSQL + Redis
- ❌ No PyTorch/transformers
- ❌ No medical NLP (scispacy, medcat)
- ❌ No advanced ML models

### Option 2: Full ML Build

```bash
# Uses requirements.txt (~3GB with ML dependencies)
docker compose -f docker-compose-full.yml up --build

# Or build backend only
cd backend
docker build -f Dockerfile.full -t nsexp-backend:full .
```

**What you get:**
- ✅ Everything from simplified build
- ✅ PyTorch 2.1.1
- ✅ Transformers (Hugging Face)
- ✅ Medical NLP (scispacy, medcat)
- ✅ Advanced sentence transformers
- ✅ Elasticsearch integration
- ✅ Qdrant vector database
- ✅ Complete medical research stack

## Comparison

| Feature | Simplified | Full ML |
|---------|-----------|---------|
| **Installation Size** | ~300MB | ~3GB |
| **Build Time (first)** | 3-5 min | 15-20 min |
| **Build Time (cached)** | 30-60 sec | 2-3 min |
| **Memory Usage** | 1-2GB | 4-8GB |
| **Docker Image Size** | 851MB | 2.5-3GB |
| **FastAPI Core** | ✅ | ✅ |
| **Basic AI APIs** | ✅ | ✅ |
| **PDF Processing** | ✅ | ✅ |
| **Vector Search** | ✅ (FAISS) | ✅ (FAISS + Qdrant) |
| **PyTorch** | ❌ | ✅ |
| **Transformers** | ❌ | ✅ |
| **Medical NLP** | ❌ | ✅ |
| **Search (Elasticsearch)** | ❌ | ✅ |
| **Advanced ML Models** | ❌ | ✅ |

## Build Files Reference

### Backend Dockerfiles

1. **`Dockerfile`** (Production - Simplified)
   - Multi-stage build
   - Uses `requirements_simplified.txt`
   - Optimized for production (851MB)
   - Command: `uvicorn main_simplified:app`

2. **`Dockerfile.simple`** (Development - Simplified)
   - Single-stage build
   - Uses `requirements_simplified.txt`
   - Includes build tools
   - Best for local development (1.49GB)

3. **`Dockerfile.full`** (Production - Full ML)
   - Multi-stage build
   - Uses `requirements.txt` with ML dependencies
   - Complete ML stack
   - Command: `uvicorn main:app`

### Docker Compose Files

1. **`docker-compose-simple.yml`**
   - PostgreSQL + Redis + Backend + Frontend
   - Uses `Dockerfile.simple`
   - Fast startup, minimal resources
   - Perfect for development

2. **`docker-compose-full.yml`**
   - Everything from simple + Elasticsearch + Qdrant
   - Uses `Dockerfile.full`
   - Complete ML environment
   - Requires 8GB+ RAM

3. **`docker-compose.yml`**
   - Default configuration
   - Currently uses standard `Dockerfile`
   - Balanced setup

## Detailed Build Commands

### Simplified Build

```bash
# Backend simplified
cd backend
docker build -f Dockerfile.simple -t nsexp-backend:simple .
docker run -p 8000:8000 nsexp-backend:simple

# Full stack simplified
docker compose -f docker-compose-simple.yml up --build

# Stop
docker compose -f docker-compose-simple.yml down
```

### Full ML Build

```bash
# Backend full ML
cd backend
docker build -f Dockerfile.full -t nsexp-backend:full .
docker run -p 8000:8000 nsexp-backend:full

# Full stack with ML
docker compose -f docker-compose-full.yml up --build

# Stop
docker compose -f docker-compose-full.yml down
```

## System Requirements

### Simplified Build
- **RAM**: 2GB minimum, 4GB recommended
- **Disk**: 2GB free space
- **CPU**: 2 cores recommended
- **Build time**: 3-5 minutes

### Full ML Build
- **RAM**: 8GB minimum, 16GB recommended
- **Disk**: 10GB free space
- **CPU**: 4 cores recommended
- **Build time**: 15-20 minutes

## Environment Variables

Both builds use the same environment variables:

```bash
# Required
DATABASE_URL=postgresql+asyncpg://neurosurg:neurosurg123@postgres:5432/neurosurgical_knowledge
REDIS_URL=redis://redis:6379/0

# Optional AI Services
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key

# Additional for Full ML Build
ELASTICSEARCH_URL=http://elasticsearch:9200
VECTOR_DB_URL=http://qdrant:6333
PERPLEXITY_API_KEY=your_perplexity_key
PUBMED_API_KEY=your_pubmed_key
```

## When to Use Which Build?

### Use Simplified Build If:
- ✅ Getting started with the project
- ✅ Development and testing
- ✅ CI/CD pipelines
- ✅ Limited disk space or RAM
- ✅ Only need basic neurosurgical knowledge management
- ✅ Using external AI APIs (OpenAI, Claude, Gemini)

### Use Full ML Build If:
- ✅ Running advanced medical NLP
- ✅ Processing medical text with transformers
- ✅ Using local ML models
- ✅ Medical entity recognition (scispacy, medcat)
- ✅ Research environment with full ML stack
- ✅ Need Elasticsearch for advanced search
- ✅ Vector similarity with multiple databases

## Troubleshooting

### Simplified Build Issues

**Build fails with package errors:**
```bash
# Clean and rebuild
docker system prune -af
docker compose -f docker-compose-simple.yml build --no-cache
```

**SSL certificate errors:**
Already fixed with `PIP_TRUSTED_HOST` in Dockerfiles.

### Full ML Build Issues

**Out of memory during build:**
```bash
# Increase Docker memory limit (Docker Desktop: Settings → Resources)
# Or use --memory flag
docker build --memory=8g -f backend/Dockerfile.full -t nsexp-backend:full backend/
```

**PyTorch installation fails:**
```bash
# Ensure you have enough disk space
df -h

# Clean Docker cache
docker system prune -af --volumes
```

**Build takes too long:**
This is expected for full ML build. Consider:
- Using simplified build for development
- Pre-pulling base images
- Using build cache

## Performance Tips

### Simplified Build
1. Use for development (auto-reload works)
2. Build once, develop forever
3. Fast iteration cycles

### Full ML Build
1. Build overnight or during downtime
2. Use for specific ML tasks
3. Consider separate ML service container
4. Cache the built image for reuse

## Migration Between Builds

### From Simplified to Full
```bash
# Stop simplified
docker compose -f docker-compose-simple.yml down

# Start full ML
docker compose -f docker-compose-full.yml up --build

# Database and volumes are preserved
```

### From Full to Simplified
```bash
# Stop full ML
docker compose -f docker-compose-full.yml down

# Start simplified
docker compose -f docker-compose-simple.yml up --build

# Note: ML-specific features will be unavailable
```

## Validation

### Test Simplified Build
```bash
./validate-docker-setup.sh
./quick-docker-test.sh simple
```

### Test Full ML Build
```bash
# Build and test
cd backend
docker build -f Dockerfile.full -t nsexp-backend:test-full .

# Test imports
docker run --rm nsexp-backend:test-full python -c "
import torch
import transformers
import scispacy
print('✅ All ML packages imported successfully')
"
```

## Summary

- **For most users**: Use `docker-compose-simple.yml` with `Dockerfile.simple`
- **For ML research**: Use `docker-compose-full.yml` with `Dockerfile.full`
- **For production**: Use `Dockerfile` (simplified, optimized)

Both options are fully supported and tested. Choose based on your needs!

---

**Quick Commands Reference:**

```bash
# Simplified (default, recommended)
docker compose -f docker-compose-simple.yml up --build

# Full ML stack
docker compose -f docker-compose-full.yml up --build

# Production (simplified)
docker compose -f docker-compose-production.yml up --build
```
