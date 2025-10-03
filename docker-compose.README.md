# Docker Compose Configuration Guide

## 📦 Available Configurations

### ✅ `docker-compose.yml` (RECOMMENDED - Default)
**Status:** Production-ready, simplified configuration  
**Use for:** Development and production deployment  
**Services:**
- PostgreSQL (database)
- Redis (cache)
- Backend (FastAPI with main_simplified.py)
- Frontend (Next.js)

**Start:** `docker-compose up`

---

### 📚 Archived Configurations

The following configurations are kept for reference but are NOT recommended for use:

#### `docker-compose-full.yml` (DEPRECATED)
**Status:** Uses broken main.py  
**Issues:** References non-existent API router modules  
**Don't use unless:** You've implemented the full router architecture

#### `docker-compose-production.yml` (ADVANCED)
**Status:** Full production setup with monitoring  
**Services:** Includes Nginx, Prometheus, Grafana, PgAdmin, MinIO  
**Use only if:** You need advanced monitoring and production features  
**Warning:** Requires additional configuration

#### `docker-compose-complex.yml` (ARCHIVED)
**Status:** Includes unnecessary services  
**Services:** Elasticsearch, Qdrant, Celery, Flower (not used)  
**Don't use:** These services aren't implemented in current codebase

---

## 🚀 Quick Start

### Development
```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop all services
docker-compose down
```

### Production
```bash
# For advanced production setup
docker-compose -f docker-compose-production.yml up -d

# Note: Requires environment configuration
```

---

## 🔧 Configuration

### Environment Variables
Create `.env` file in root directory:

```env
# Database
DATABASE_URL=postgresql+asyncpg://neurosurg:neurosurg123@postgres:5432/neurosurgical_knowledge

# AI Services (Optional)
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here

# Redis
REDIS_URL=redis://redis:6379/0
```

### Ports
- **3000** - Frontend (Next.js)
- **8000** - Backend (FastAPI)
- **5432** - PostgreSQL
- **6379** - Redis

---

## 📝 Migration from Old Configs

If you were using `docker-compose-simple.yml`:
```bash
# Old command
docker-compose -f docker-compose-simple.yml up

# New command (same functionality)
docker-compose up
```

The default `docker-compose.yml` now provides the same simplified configuration.

---

## ❌ Don't Use

- `docker-compose-full.yml` - Uses broken main.py
- Direct references to `main.py` - Use `main_simplified.py` instead

---

## ✅ Recommended Setup

1. Use default `docker-compose.yml`
2. Set environment variables in `.env`
3. Run: `docker-compose up`
4. Access:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

---

**Last Updated:** 2025-10-03  
**Current Version:** 2.1.0-optimized
