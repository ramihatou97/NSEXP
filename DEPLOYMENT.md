# Deployment Guide - Neurosurgical Knowledge Management System

This guide will help you deploy the Neurosurgical Knowledge Management System in various environments.

## 🚀 Quick Start (Local Development)

### Prerequisites
- Docker Desktop (recommended) OR
- PostgreSQL 15+, Redis, Node.js 18+, Python 3.11+

### Option 1: Docker Compose (Recommended)

1. **Clone and Configure**
```bash
git clone https://github.com/ramihatou97/NNP.git
cd NNP
cp .env.development .env
```

2. **Start Services**
```bash
docker-compose -f docker-compose-simple.yml up -d
```

3. **Access Application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs

### Option 2: Manual Setup

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements_simplified.txt

# Set environment variables
export DATABASE_URL="postgresql+asyncpg://neurosurg:neurosurg123@localhost:5432/neurosurgical_knowledge"

# Start database (if not using Docker)
# Install PostgreSQL and create database
createdb -U postgres neurosurgical_knowledge

# Start backend
uvicorn main_simplified:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local

# Start development server
npm run dev
```

## 🐳 Docker Deployment

### Development Environment

```bash
# Start all services
docker-compose -f docker-compose-simple.yml up -d

# View logs
docker-compose -f docker-compose-simple.yml logs -f

# Stop services
docker-compose -f docker-compose-simple.yml down
```

### Production Environment

1. **Update .env file with production values:**
```bash
DEBUG=False
DATABASE_URL=postgresql+asyncpg://user:pass@prod-db:5432/neurosurg
OPENAI_API_KEY=your-production-key
# Add other production settings
```

2. **Deploy with production config:**
```bash
docker-compose -f docker-compose.yml --profile production up -d
```

## ☁️ Cloud Deployment

### Deploy to AWS

#### Prerequisites
- AWS account
- AWS CLI configured
- Docker

#### Steps

1. **Create RDS PostgreSQL Database**
```bash
aws rds create-db-instance \
  --db-instance-identifier neurosurg-db \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --master-username neurosurg \
  --master-user-password YOUR_PASSWORD \
  --allocated-storage 20
```

2. **Create ElastiCache Redis**
```bash
aws elasticache create-cache-cluster \
  --cache-cluster-id neurosurg-cache \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1
```

3. **Deploy to ECS**
```bash
# Build and push Docker images
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ECR_URI

docker build -t neurosurg-backend -f backend/Dockerfile.simple backend/
docker tag neurosurg-backend:latest YOUR_ECR_URI/neurosurg-backend:latest
docker push YOUR_ECR_URI/neurosurg-backend:latest

docker build -t neurosurg-frontend -f frontend/Dockerfile.simple frontend/
docker tag neurosurg-frontend:latest YOUR_ECR_URI/neurosurg-frontend:latest
docker push YOUR_ECR_URI/neurosurg-frontend:latest

# Create ECS task definition and service
# (Use AWS Console or CloudFormation template)
```

### Deploy to Vercel (Frontend) + Railway (Backend)

#### Frontend on Vercel

```bash
cd frontend

# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Configure environment variables in Vercel dashboard:
# NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app/api/v1
```

#### Backend on Railway

1. Go to https://railway.app
2. Create new project from GitHub repo
3. Select backend directory
4. Add environment variables:
   - DATABASE_URL (Railway will provide PostgreSQL)
   - REDIS_URL (Railway will provide Redis)
   - OPENAI_API_KEY
5. Deploy!

### Deploy to Render

1. **Create PostgreSQL Database**
   - Go to Render Dashboard → New PostgreSQL

2. **Deploy Backend**
   - New Web Service
   - Connect GitHub repo
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements_simplified.txt`
   - Start Command: `uvicorn main_simplified:app --host 0.0.0.0 --port $PORT`
   - Add environment variables

3. **Deploy Frontend**
   - New Static Site
   - Connect GitHub repo
   - Root Directory: `frontend`
   - Build Command: `npm install && npm run build`
   - Publish Directory: `.next`

## 🔑 Environment Variables

### Required
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
```

### Optional (with mock fallbacks)
```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
REDIS_URL=redis://localhost:6379/0
```

## 📊 Health Checks

### Backend
```bash
curl http://localhost:8000/health
```

### Frontend
```bash
curl http://localhost:3000
```

### Database
```bash
docker exec neurosurg_db pg_isready -U neurosurg
```

## 🔧 Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.11+

# Check database connection
psql $DATABASE_URL -c "SELECT 1"

# View logs
docker logs neurosurg_backend
```

### Frontend won't start
```bash
# Clear cache and reinstall
rm -rf node_modules .next
npm install
npm run dev

# Check for port conflicts
lsof -i :3000
```

### Database connection issues
```bash
# Test connection
psql -h localhost -U neurosurg -d neurosurgical_knowledge

# Restart database
docker-compose restart postgres
```

## 🔐 Security Checklist for Production

- [ ] Change default database credentials
- [ ] Use strong SECRET_KEY
- [ ] Enable HTTPS/SSL
- [ ] Set DEBUG=False
- [ ] Configure CORS properly
- [ ] Use environment-specific API keys
- [ ] Enable rate limiting
- [ ] Set up monitoring (Sentry, DataDog, etc.)
- [ ] Configure backups for database
- [ ] Use secrets management (AWS Secrets Manager, etc.)

## 📈 Monitoring

### Application Metrics
- Backend: http://localhost:8000/metrics (Prometheus format)
- Frontend: Enable Vercel Analytics

### Logs
```bash
# Backend logs
docker logs -f neurosurg_backend

# Frontend logs  
docker logs -f neurosurg_frontend

# Database logs
docker logs -f neurosurg_db
```

## 🔄 Updates and Maintenance

### Update Application
```bash
git pull origin main
docker-compose -f docker-compose-simple.yml down
docker-compose -f docker-compose-simple.yml up -d --build
```

### Backup Database
```bash
docker exec neurosurg_db pg_dump -U neurosurg neurosurgical_knowledge > backup.sql
```

### Restore Database
```bash
docker exec -i neurosurg_db psql -U neurosurg neurosurgical_knowledge < backup.sql
```

## 🆘 Support

For issues or questions:
1. Check logs: `docker-compose logs`
2. Run system test: `python test_system.py`
3. Review API docs: http://localhost:8000/api/docs
4. Check GitHub issues: https://github.com/ramihatou97/NNP/issues

## 📝 Notes

- The system works without AI API keys (uses mock responses)
- Redis is optional (system works without caching)
- Minimum 2GB RAM recommended
- PostgreSQL 15+ required for all features
