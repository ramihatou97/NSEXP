# 🚀 Quick Start Guide - Neurosurgical Knowledge Management System

Get your system running in under 5 minutes!

## 📋 Prerequisites

Choose ONE of these options:

### Option 1: Docker (Easiest - Recommended)
- Docker Desktop installed ([download here](https://www.docker.com/products/docker-desktop))
- 4GB RAM available
- 10GB disk space

### Option 2: Manual Installation
- PostgreSQL 15+ ([download](https://www.postgresql.org/download/))
- Python 3.11+ ([download](https://www.python.org/downloads/))
- Node.js 18+ ([download](https://nodejs.org/))
- 4GB RAM available

## 🐳 Option 1: Docker Setup (5 minutes)

### Step 1: Clone Repository
```bash
git clone https://github.com/ramihatou97/NNP.git
cd NNP
```

### Step 2: Start Services
```bash
# Start all services (database, cache, backend, frontend)
docker compose -f docker-compose-simple.yml up -d

# Watch logs (optional)
docker compose -f docker-compose-simple.yml logs -f
```

### Step 3: Access Application
- 🌐 **Frontend**: http://localhost:3000
- 🔧 **Backend API**: http://localhost:8000
- 📚 **API Docs**: http://localhost:8000/api/docs

### Stop Services
```bash
docker compose -f docker-compose-simple.yml down
```

## 🔧 Option 2: Manual Setup (10 minutes)

### Step 1: Clone Repository
```bash
git clone https://github.com/ramihatou97/NNP.git
cd NNP
```

### Step 2: Setup Database
```bash
# Create PostgreSQL database
createdb -U postgres neurosurgical_knowledge

# Or using psql
psql -U postgres -c "CREATE DATABASE neurosurgical_knowledge;"
```

### Step 3: Setup Backend
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements_simplified.txt

# Set environment variable (or create .env file)
export DATABASE_URL="postgresql+asyncpg://postgres:yourpassword@localhost:5432/neurosurgical_knowledge"

# Start backend server
uvicorn main_simplified:app --reload --host 0.0.0.0 --port 8000
```

Keep this terminal open and backend running.

### Step 4: Setup Frontend (in new terminal)
```bash
cd frontend

# Install dependencies
npm install

# Create environment file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local

# Start frontend server
npm run dev
```

### Step 5: Access Application
- 🌐 **Frontend**: http://localhost:3000
- 🔧 **Backend API**: http://localhost:8000
- 📚 **API Docs**: http://localhost:8000/api/docs

## ✅ Verify Installation

### Test Backend
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

### Test System
```bash
cd NNP
python test_system.py
# Should show: All tests passed!
```

## 🎯 First Steps

1. **Open Frontend**: http://localhost:3000
2. **Try Q&A**: 
   - Go to Q&A page
   - Ask: "What are the indications for craniotomy?"
   - Get AI-powered answer (works without API keys using mock data)

3. **Generate Chapter**:
   - Go to Synthesis page
   - Enter topic: "Glioblastoma Management"
   - Click "Generate Chapter"

4. **Browse API**:
   - Open http://localhost:8000/api/docs
   - Try endpoints interactively

## 🔑 Optional: Add AI API Keys

The system works WITHOUT API keys using mock responses. To enable real AI:

### Create .env file in backend directory:
```bash
# Copy template
cp .env.development backend/.env

# Edit and add your keys
nano backend/.env  # or use any text editor
```

### Add API Keys:
```bash
# OpenAI (for GPT-4)
OPENAI_API_KEY=sk-your-key-here

# Anthropic (for Claude)
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Google (for Gemini)
GOOGLE_API_KEY=your-key-here
```

Get free API keys:
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/
- Google: https://makersuite.google.com/app/apikey

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check Python version (need 3.11+)
python --version

# Try reinstalling dependencies
cd backend
pip install --force-reinstall -r requirements_simplified.txt
```

### Frontend won't start
```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules .next
npm install
npm run dev
```

### Database connection error
```bash
# Verify PostgreSQL is running
psql -U postgres -c "SELECT 1"

# Check connection string in .env file
cat backend/.env | grep DATABASE_URL
```

### Docker issues
```bash
# Restart Docker Desktop

# Clean up and try again
docker compose -f docker-compose-simple.yml down -v
docker compose -f docker-compose-simple.yml up -d --build
```

### Port already in use
```bash
# Find process using port 3000 or 8000
# On macOS/Linux:
lsof -i :3000
lsof -i :8000

# On Windows:
netstat -ano | findstr :3000
netstat -ano | findstr :8000

# Kill the process or change ports in docker-compose-simple.yml
```

## 📚 Learn More

- **Full Deployment Guide**: See [DEPLOYMENT.md](DEPLOYMENT.md)
- **System Documentation**: See [SYSTEM_SIMPLIFIED.md](SYSTEM_SIMPLIFIED.md)
- **API Reference**: http://localhost:8000/api/docs
- **GitHub Repository**: https://github.com/ramihatou97/NNP

## 🆘 Need Help?

1. **Check logs**:
   ```bash
   # Docker logs
   docker compose -f docker-compose-simple.yml logs backend
   docker compose -f docker-compose-simple.yml logs frontend
   
   # Manual setup: check terminal output
   ```

2. **Run system test**:
   ```bash
   python test_system.py
   ```

3. **Review API docs**: http://localhost:8000/api/docs

4. **Check GitHub issues**: https://github.com/ramihatou97/NNP/issues

## 🎉 You're Ready!

Your Neurosurgical Knowledge Management System is now running!

**Next Steps:**
- Create your first chapter via AI synthesis
- Ask questions using the Q&A assistant
- Search across medical content
- Build your personal knowledge library

**Remember:** The system works without AI API keys using intelligent mock responses, perfect for testing and development!
