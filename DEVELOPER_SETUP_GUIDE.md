# 🛠️ Developer Setup Guide - NSEXP

## Quick Start for Developers

This guide will get you up and running with NSEXP development environment in 10 minutes.

## Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **PostgreSQL 15+**
- **Redis 7+** (optional but recommended)
- **Git**
- **Docker & Docker Compose** (optional, for containerized development)

## Option 1: Docker Development (Fastest)

```bash
# Clone repository
git clone https://github.com/ramihatou97/NSEXP.git
cd NSEXP

# Start all services
docker-compose -f docker-compose-simple.yml up

# Access:
# - Frontend: http://localhost:3000
# - Backend: http://localhost:8000
# - API Docs: http://localhost:8000/api/docs
```

**Done!** The system is now running with hot-reload enabled.

---

## Option 2: Manual Setup (Full Control)

### Backend Setup

1. **Install system dependencies**

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y \
    postgresql-15 \
    redis-server \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1-mesa-glx \
    libglib2.0-0 \
    python3.11 \
    python3.11-venv
```

**macOS:**
```bash
brew install postgresql@15 redis poppler tesseract python@3.11
brew services start postgresql@15
brew services start redis
```

**Windows:**
- Install PostgreSQL from https://www.postgresql.org/download/windows/
- Install Redis from https://github.com/microsoftarchive/redis/releases
- Install Tesseract from https://github.com/UB-Mannheim/tesseract/wiki
- Install Poppler from https://github.com/oschwartz10612/poppler-windows/releases/

2. **Set up database**

```bash
# Create database
sudo -u postgres psql
```

```sql
CREATE DATABASE neurosurgical_knowledge;
CREATE USER neurosurg WITH PASSWORD 'neurosurg123';
GRANT ALL PRIVILEGES ON DATABASE neurosurgical_knowledge TO neurosurg;
\q
```

3. **Set up Python environment**

```bash
cd backend

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements_simplified.txt
```

4. **Configure environment**

```bash
# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql+asyncpg://neurosurg:neurosurg123@localhost:5432/neurosurgical_knowledge
REDIS_URL=redis://localhost:6379/0

# Optional: AI Provider API Keys
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
# GOOGLE_API_KEY=...
# PUBMED_API_KEY=...
EOF
```

5. **Initialize database**

```bash
# Database tables are created automatically on first run
python -c "from core.database_simplified import init_db; import asyncio; asyncio.run(init_db())"
```

6. **Run backend**

```bash
uvicorn main_simplified:app --reload --host 0.0.0.0 --port 8000
```

Backend is now running at http://localhost:8000

### Frontend Setup

1. **Install Node.js dependencies**

```bash
cd frontend
npm install
```

2. **Configure environment**

```bash
# Create .env.local
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
EOF
```

3. **Run frontend**

```bash
npm run dev
```

Frontend is now running at http://localhost:3000

---

## Verify Installation

### Backend Health Check

```bash
curl http://localhost:8000/health
```

Expected output:
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "ai_services": {...},
  "timestamp": "2024-01-15T10:30:00"
}
```

### Test New Enhanced Features

1. **Test Image Extraction**
```bash
curl -X POST "http://localhost:8000/api/v1/images/extract" \
  -H "Content-Type: application/json" \
  -d '{"pdf_path": "/textbooks/sample.pdf"}'
```

2. **Test Deep Search**
```bash
curl -X POST "http://localhost:8000/api/v1/search/deep" \
  -H "Content-Type: application/json" \
  -d '{"query": "glioblastoma", "sources": ["pubmed"], "max_results": 5}'
```

3. **Test Comprehensive Synthesis**
```bash
curl -X POST "http://localhost:8000/api/v1/synthesis/comprehensive" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Brain Tumor Surgery",
    "specialty": "TUMOR",
    "references": [],
    "include_images": true
  }'
```

4. **Test Alive Chapter Status**
```bash
curl http://localhost:8000/api/v1/alive-chapters/status
```

---

## Development Workflow

### Making Changes

1. **Backend changes**
- Edit files in `backend/`
- Server auto-reloads (uvicorn --reload)
- Check logs in terminal

2. **Frontend changes**
- Edit files in `frontend/`
- Hot-reload enabled by default
- View changes at http://localhost:3000

3. **Database changes**
- Edit models in `backend/models/database_simplified.py`
- Restart backend to apply changes
- Or use Alembic for migrations (optional)

### Testing

**Backend tests:**
```bash
cd backend
pytest tests/ -v
pytest tests/test_enhanced_services.py -v  # Test new services
```

**Frontend tests:**
```bash
cd frontend
npm test
npm run test:ci  # CI mode
```

### Code Quality

**Backend linting:**
```bash
cd backend
pylint services/
black services/  # Auto-format
mypy services/  # Type checking
```

**Frontend linting:**
```bash
cd frontend
npm run lint
npm run format
npm run type-check
```

---

## Directory Structure

```
NSEXP/
├── backend/
│   ├── services/
│   │   ├── image_extraction_service.py      # NEW: Image extraction
│   │   ├── enhanced_synthesis_service.py    # NEW: Comprehensive synthesis
│   │   ├── deep_search_service.py           # NEW: Literature search
│   │   ├── alive_chapter_integration.py     # NEW: Alive chapter bridge
│   │   ├── pdf_service.py                   # ENHANCED: Advanced PDF processing
│   │   ├── synthesis_service.py             # Basic synthesis
│   │   ├── ai_manager.py                    # AI provider management
│   │   ├── chapter_service.py               # Chapter CRUD
│   │   └── ...
│   ├── models/
│   │   └── database_simplified.py           # Database models
│   ├── main_simplified.py                   # API entry point (54 endpoints)
│   ├── requirements_simplified.txt          # Python dependencies
│   └── docs/
│       └── ENHANCED_API_DOCUMENTATION.md    # NEW: API docs
├── frontend/
│   ├── app/                                 # Next.js 14 app directory
│   ├── components/                          # React components
│   ├── services/                            # API client
│   └── package.json                         # Node dependencies
├── alive chapter/                           # Alive chapter components
│   ├── chapter_qa_engine.py
│   ├── citation_network_engine.py
│   └── ...
├── docker-compose-simple.yml                # Docker Compose config
└── ENHANCED_DEPLOYMENT_GUIDE.md             # NEW: Deployment guide
```

---

## Common Development Tasks

### Adding a New API Endpoint

1. Create service function in `backend/services/your_service.py`
2. Add endpoint to `backend/main_simplified.py`
3. Update API documentation
4. Add tests in `backend/tests/`

Example:
```python
# In backend/services/your_service.py
async def new_feature():
    return {"result": "data"}

# In backend/main_simplified.py
@app.get("/api/v1/new-feature")
async def new_feature_endpoint():
    from services.your_service import new_feature
    return await new_feature()
```

### Adding a New Database Model

1. Add model to `backend/models/database_simplified.py`
2. Restart backend (tables auto-create)
3. Or use Alembic for versioned migrations:

```bash
cd backend
alembic revision --autogenerate -m "Add new model"
alembic upgrade head
```

### Debugging

**Backend debugging with VS Code:**

Create `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "main_simplified:app",
        "--reload",
        "--host",
        "0.0.0.0",
        "--port",
        "8000"
      ],
      "jinja": true,
      "justMyCode": true
    }
  ]
}
```

**Frontend debugging:**
- Built-in Next.js DevTools
- React DevTools browser extension
- Console logging in browser

### Performance Profiling

**Backend profiling:**
```bash
pip install py-spy
py-spy record -o profile.svg -- python -m uvicorn main_simplified:app
```

**Frontend profiling:**
```bash
# In browser DevTools
# Performance tab → Record → Analyze
```

---

## IDE Setup Recommendations

### VS Code Extensions

**Backend development:**
- Python (Microsoft)
- Pylance
- Black Formatter
- autoDocstring
- SQLTools
- PostgreSQL

**Frontend development:**
- ESLint
- Prettier
- Tailwind CSS IntelliSense
- ES7+ React/Redux/React-Native snippets
- Auto Rename Tag

### VS Code Settings

Create `.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "./backend/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

---

## Environment Variables Reference

### Required

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/dbname
```

### Optional (with fallbacks)

```bash
# Redis cache
REDIS_URL=redis://localhost:6379/0

# AI Providers (system uses mocks if not provided)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...

# PubMed search
PUBMED_API_KEY=...
PUBMED_EMAIL=your@email.com

# Performance tuning
DB_POOL_SIZE=20
AI_MAX_CONCURRENT=10
AI_TIMEOUT_SECONDS=30

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

---

## Troubleshooting Development Issues

### Issue: Module not found

```bash
# Backend
cd backend
source venv/bin/activate
pip install -r requirements_simplified.txt

# Frontend
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Issue: Database connection error

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check credentials
psql -U neurosurg -d neurosurgical_knowledge -h localhost

# Reset database
dropdb neurosurgical_knowledge
createdb neurosurgical_knowledge
```

### Issue: Port already in use

```bash
# Find process using port 8000
lsof -i :8000
kill -9 <PID>

# Or use different port
uvicorn main_simplified:app --port 8001
```

### Issue: Frontend can't connect to backend

1. Check backend is running: `curl http://localhost:8000/health`
2. Check CORS settings in `backend/main_simplified.py`
3. Verify `NEXT_PUBLIC_API_URL` in `frontend/.env.local`

---

## Getting Help

- **API Documentation**: http://localhost:8000/api/docs
- **Issues**: https://github.com/ramihatou97/NSEXP/issues
- **Discussions**: https://github.com/ramihatou97/NSEXP/discussions

---

## Next Steps

1. ✅ Set up development environment
2. 📖 Read `ENHANCED_DEPLOYMENT_GUIDE.md`
3. 🔍 Explore `backend/docs/ENHANCED_API_DOCUMENTATION.md`
4. 🧪 Run tests: `pytest backend/tests/`
5. 🎯 Try the new features:
   - Image extraction
   - Comprehensive synthesis
   - Deep literature search
   - Alive chapter features
6. 🚀 Start building!

Happy coding! 🧠💻
