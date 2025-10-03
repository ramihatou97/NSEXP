# Enhanced Deployment Guide - NSEXP v2.2

## 🚀 Quick Deployment Options

### Option 1: Docker Compose (Recommended)

#### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 20GB disk space

#### Steps

1. **Clone the repository**
```bash
git clone https://github.com/ramihatou97/NSEXP.git
cd NSEXP
```

2. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys (optional - system works with mocks)
```

3. **Start services**
```bash
docker-compose -f docker-compose-simple.yml up -d
```

4. **Verify deployment**
```bash
# Check service health
docker-compose -f docker-compose-simple.yml ps

# View logs
docker-compose -f docker-compose-simple.yml logs -f backend

# Test API
curl http://localhost:8000/health
```

5. **Access the system**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/api/docs

#### Stop services
```bash
docker-compose -f docker-compose-simple.yml down
```

---

### Option 2: Manual Local Development

#### Backend Setup

1. **Install system dependencies (Ubuntu/Debian)**
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

2. **Set up Python environment**
```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements_simplified.txt
```

3. **Configure database**
```bash
# Create database
sudo -u postgres psql
CREATE DATABASE neurosurgical_knowledge;
CREATE USER neurosurg WITH PASSWORD 'neurosurg123';
GRANT ALL PRIVILEGES ON DATABASE neurosurgical_knowledge TO neurosurg;
\q
```

4. **Set environment variables**
```bash
export DATABASE_URL="postgresql+asyncpg://neurosurg:neurosurg123@localhost:5432/neurosurgical_knowledge"
export REDIS_URL="redis://localhost:6379/0"
# Optional AI keys
export OPENAI_API_KEY="your-key-here"
export ANTHROPIC_API_KEY="your-key-here"
```

5. **Run backend**
```bash
uvicorn main_simplified:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

1. **Install Node.js dependencies**
```bash
cd frontend
npm install
```

2. **Configure frontend**
```bash
# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local
echo "NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws" >> .env.local
```

3. **Run frontend**
```bash
npm run dev
```

---

## 🔧 Configuration Options

### Enhanced Features Configuration

#### Image Processing
The system now supports advanced image extraction from PDFs with OCR:

```python
# In .env or environment
TESSERACT_CMD=/usr/bin/tesseract  # Path to tesseract executable
PDF_IMAGE_DPI=150  # DPI for PDF to image conversion
OCR_LANGUAGE=eng  # OCR language (eng, fra, etc.)
```

#### AI Services
Configure multiple AI providers with automatic fallback:

```bash
# Primary provider
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview

# Fallback providers
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-opus-20240229

GOOGLE_API_KEY=...
GEMINI_MODEL=gemini-1.5-pro
```

#### Deep Search
Enable PubMed and other literature searches:

```bash
PUBMED_API_KEY=your-ncbi-api-key  # Optional but recommended for higher rate limits
PUBMED_EMAIL=your@email.com  # Required for PubMed API
```

#### Performance Tuning
```bash
# Database
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10

# Redis cache
REDIS_MAX_MEMORY=500mb
REDIS_EVICTION_POLICY=allkeys-lru

# AI processing
AI_MAX_CONCURRENT=10
AI_TIMEOUT_SECONDS=30
```

---

## 🏥 Health Checks & Monitoring

### Service Health Endpoints

1. **Backend Health**
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "ai_services": {
    "openai": "available",
    "anthropic": "mock",
    "google": "mock"
  },
  "alive_chapter_features": {
    "qa_engine": false,
    "citation_network": false,
    "behavioral_learning": false,
    "nuance_merge": false
  }
}
```

2. **Metrics Endpoint**
```bash
curl http://localhost:8000/metrics
```

3. **Alive Chapter Status**
```bash
curl http://localhost:8000/api/v1/alive-chapters/status
```

### Monitoring with Docker

```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Check resource usage
docker stats

# Check service status
docker-compose ps
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Database Connection Failed
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check connection string
echo $DATABASE_URL

# Reset database
docker-compose down -v
docker-compose up -d postgres
```

#### 2. Image Extraction Fails
```bash
# Verify tesseract installation
tesseract --version

# Check poppler-utils
pdfinfo --version

# Test manually
tesseract test-image.png output
```

#### 3. AI Services Unavailable
The system automatically falls back to mock responses if AI services are unavailable. This is expected behavior when API keys are not configured.

To enable real AI services:
1. Add API keys to `.env`
2. Restart backend
3. Check status: `curl http://localhost:8000/health`

#### 4. Frontend Can't Connect to Backend
```bash
# Check backend is running
curl http://localhost:8000/health

# Check CORS settings in backend/main_simplified.py
# Ensure frontend URL is in allowed origins

# Check frontend environment variables
cat frontend/.env.local
```

#### 5. Memory Issues
```bash
# Increase Docker memory limit
# Edit ~/.docker/config.json or Docker Desktop settings

# Reduce concurrent AI requests
export AI_MAX_CONCURRENT=5

# Enable Redis eviction
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

---

## 📊 Performance Optimization

### For Production Deployment

1. **Enable Production Mode**
```bash
# Backend
export ENVIRONMENT=production
export DEBUG=false

# Frontend
npm run build
npm start
```

2. **Database Optimization**
```sql
-- Add indexes
CREATE INDEX idx_chapters_specialty ON chapters(specialty);
CREATE INDEX idx_references_title ON references USING gin(to_tsvector('english', title));
CREATE INDEX idx_chapters_content ON chapters USING gin(to_tsvector('english', content));
```

3. **Redis Configuration**
```bash
# In docker-compose-simple.yml, add to redis service:
command: redis-server --maxmemory 500mb --maxmemory-policy allkeys-lru
```

4. **Enable Logging Rotation**
```bash
# Already configured in backend/utils/logger.py
# Logs rotate at 10MB, keep 5 backups
```

---

## 🔒 Security Considerations

### For Production Deployment

1. **Change default passwords**
```bash
# PostgreSQL
POSTGRES_PASSWORD=strong-random-password

# Update DATABASE_URL accordingly
```

2. **Use environment-specific secrets**
```bash
# Never commit .env files
# Use secret management (AWS Secrets Manager, Azure Key Vault, etc.)
```

3. **Enable HTTPS**
```bash
# Add nginx reverse proxy
# See nginx/nginx.conf for configuration
```

4. **Restrict CORS**
```python
# In backend/main_simplified.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🚢 Deployment to Cloud

### AWS Deployment (EC2)

1. **Launch EC2 instance**
- AMI: Ubuntu 22.04 LTS
- Instance type: t3.medium (minimum)
- Security group: Allow ports 80, 443, 22

2. **Install Docker**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu
```

3. **Clone and deploy**
```bash
git clone https://github.com/ramihatou97/NSEXP.git
cd NSEXP
docker-compose -f docker-compose-simple.yml up -d
```

4. **Configure nginx**
```bash
sudo apt-get install nginx
sudo cp nginx/nginx.conf /etc/nginx/sites-available/nsexp
sudo ln -s /etc/nginx/sites-available/nsexp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Azure Deployment (Container Instances)

```bash
# Create resource group
az group create --name nsexp-rg --location eastus

# Deploy PostgreSQL
az postgres flexible-server create \
  --name nsexp-db \
  --resource-group nsexp-rg \
  --location eastus \
  --admin-user neurosurg \
  --admin-password <password> \
  --sku-name Standard_B1ms

# Deploy backend container
az container create \
  --resource-group nsexp-rg \
  --name nsexp-backend \
  --image <your-registry>/nsexp-backend:latest \
  --dns-name-label nsexp-backend \
  --ports 8000 \
  --environment-variables \
    DATABASE_URL=<connection-string> \
    REDIS_URL=<redis-url>

# Deploy frontend container
az container create \
  --resource-group nsexp-rg \
  --name nsexp-frontend \
  --image <your-registry>/nsexp-frontend:latest \
  --dns-name-label nsexp-frontend \
  --ports 3000 \
  --environment-variables \
    NEXT_PUBLIC_API_URL=http://<backend-fqdn>:8000/api/v1
```

### Google Cloud Platform (Cloud Run)

```bash
# Build and push images
gcloud builds submit --tag gcr.io/PROJECT_ID/nsexp-backend ./backend
gcloud builds submit --tag gcr.io/PROJECT_ID/nsexp-frontend ./frontend

# Deploy backend
gcloud run deploy nsexp-backend \
  --image gcr.io/PROJECT_ID/nsexp-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL=<connection-string>

# Deploy frontend
gcloud run deploy nsexp-frontend \
  --image gcr.io/PROJECT_ID/nsexp-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars NEXT_PUBLIC_API_URL=<backend-url>
```

---

## 📈 Scaling Considerations

### Horizontal Scaling

The backend is stateless and can be scaled horizontally:

```yaml
# In docker-compose or Kubernetes
services:
  backend:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1'
          memory: 2G
```

### Database Scaling

For large deployments:
- Enable PostgreSQL replication
- Use read replicas for search queries
- Implement connection pooling (PgBouncer)

### Caching Strategy

- Redis for AI response caching (70%+ hit rate)
- CDN for static frontend assets
- Browser caching for images and PDFs

---

## 🔄 Backup & Recovery

### Database Backup
```bash
# Manual backup
docker-compose exec postgres pg_dump -U neurosurg neurosurgical_knowledge > backup.sql

# Automated daily backups
0 2 * * * docker-compose exec postgres pg_dump -U neurosurg neurosurgical_knowledge > /backups/$(date +\%Y\%m\%d).sql
```

### File Storage Backup
```bash
# Backup textbooks and storage
tar -czf backup-storage-$(date +%Y%m%d).tar.gz storage/ textbooks/
```

### Restore
```bash
# Restore database
docker-compose exec -T postgres psql -U neurosurg neurosurgical_knowledge < backup.sql

# Restore files
tar -xzf backup-storage-20240115.tar.gz
```

---

## 📞 Support & Maintenance

### Logs Location
- Backend: `backend/logs/app.log`
- Error logs: `backend/logs/error.log`
- Docker logs: `docker-compose logs`

### Update Process
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose-simple.yml down
docker-compose -f docker-compose-simple.yml build
docker-compose -f docker-compose-simple.yml up -d
```

### Health Monitoring Script
```bash
#!/bin/bash
# monitor.sh
while true; do
  if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "Backend unhealthy, restarting..."
    docker-compose restart backend
  fi
  sleep 60
done
```

---

## 🎯 New Features Checklist

Verify all enhanced features are working:

- [ ] Image extraction from PDFs
- [ ] OCR text extraction
- [ ] Comprehensive chapter synthesis (150+ sections)
- [ ] Multi-level summaries
- [ ] PubMed literature search
- [ ] Advanced PDF processing
- [ ] Alive chapter status checking
- [ ] All 54 API endpoints responding
- [ ] Health checks passing
- [ ] Metrics endpoint working

---

## 📚 Additional Resources

- API Documentation: http://localhost:8000/api/docs
- Enhanced API Guide: `backend/docs/ENHANCED_API_DOCUMENTATION.md`
- System Requirements: `README.md`
- Architecture Overview: `COMPREHENSIVE_ASSESSMENT_REPORT.md`
