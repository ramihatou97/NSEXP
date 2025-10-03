# 🚀 NSEXP Production Deployment Guide

## Version 2.1.0 - Production Ready

This guide covers deploying the fully-enhanced NSEXP system with all production features enabled.

## ✨ New Features in 2.1.0

### Testing Infrastructure ✅
- **Backend Tests**: Unit, integration, and e2e tests organized by type
- **Frontend Tests**: Jest + React Testing Library configured
- **Coverage Reporting**: Automated coverage tracking with Codecov
- **Test Commands**: 
  ```bash
  cd backend && pytest tests/unit -v          # Unit tests
  cd backend && pytest tests/integration -v   # Integration tests
  cd backend && pytest tests/e2e -v          # E2E tests
  cd frontend && npm test                    # Frontend tests
  ```

### CI/CD Pipeline ✅
- **Automated Testing**: Backend and frontend tests on every push
- **Docker Builds**: Automated container builds and caching
- **Security Scanning**: Trivy vulnerability scanning
- **Code Quality**: SonarCloud integration (optional)
- **Coverage Reports**: Automatic coverage uploads to Codecov

### Security Enhancements ✅
- **Security Headers**: X-Frame-Options, CSP, HSTS, X-XSS-Protection
- **Rate Limiting**: 60 requests/minute per IP (configurable)
- **Input Sanitization**: Automatic detection of suspicious patterns
- **CORS Security**: Configurable allowed origins
- **Error Handling**: Standardized exception handling with logging

### Performance Monitoring ✅
- **Metrics Collection**: Response times, request counts, error rates
- **Performance Headers**: X-Response-Time on all responses
- **Health Checks**: `/health` and `/metrics` endpoints
- **Slow Request Detection**: Automatic logging of requests >1s
- **Statistics**: P50, P95, P99 response time percentiles

### Dependency Updates ✅
- **Backend**:
  - uvicorn: 0.24.0 → 0.25.0
  - openai: ≥1.3.0 → ≥1.6.0
  - anthropic: ≥0.7.0 → ≥0.8.0
  - httpx: 0.25.2 → 0.26.0
- **Frontend**:
  - next: 14.0.3 → 14.1.0
  - react: 18.2.0 → 18.3.1
  - axios: 1.6.2 → 1.6.5
  - **Removed**: cornerstone-core, cornerstone-tools, dicom-parser, three.js, @react-three/* (unused ~80MB)

### Database Optimizations ✅
- **New Indexes**: status, created_at, updated_at, evidence_level
- **Connection Pooling**: Optimized pool settings in database config

### Developer Tools ✅
- **Pre-commit Hooks**: Black, isort, flake8, prettier, safety checks
- **Code Quality Config**: pyproject.toml with all tool configurations
- **Linting**: Consistent code style enforcement

## 📋 Prerequisites

- Docker & Docker Compose (recommended)
- OR Manual setup:
  - Python 3.11+ with pip
  - Node.js 18+ with npm
  - PostgreSQL 15+
  - Redis 7+ (optional but recommended)

## 🚀 Quick Start (Docker - Recommended)

### 1. Clone and Configure

```bash
git clone https://github.com/ramihatou97/NSEXP.git
cd NSEXP

# Copy environment template
cp .env.example .env

# Edit .env with your settings (optional AI keys)
nano .env
```

### 2. Start Services

```bash
# Development mode
docker-compose up

# Production mode (with optimizations)
docker-compose -f docker-compose-production.yml up -d
```

### 3. Verify Deployment

```bash
# Check backend health
curl http://localhost:8000/health

# Check metrics
curl http://localhost:8000/metrics

# Access frontend
open http://localhost:3000

# API documentation
open http://localhost:8000/docs
```

## 🔧 Manual Setup

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements_simplified.txt

# Run tests
pytest tests/ -v --cov=.

# Start server
uvicorn main_simplified:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm ci

# Run tests
npm test

# Development server
npm run dev

# Production build
npm run build
npm start
```

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest tests/ -v

# Run specific test types
pytest tests/unit -v -m unit                    # Unit tests only
pytest tests/integration -v -m integration      # Integration tests
pytest tests/e2e -v -m e2e                      # End-to-end tests

# With coverage
pytest tests/ -v --cov=. --cov-report=html

# View coverage
open htmlcov/index.html
```

### Frontend Tests

```bash
cd frontend

# Run tests in watch mode
npm test

# Run once (CI mode)
npm run test:ci

# Type checking
npm run type-check

# Lint
npm run lint
```

## 🔒 Security Configuration

### Rate Limiting

Configure in `backend/main_simplified.py`:

```python
app.add_middleware(RateLimitMiddleware, requests_per_minute=60)
```

### CORS Origins

Update allowed origins in `backend/main_simplified.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://yourdomain.com"
    ],
    ...
)
```

### Security Headers

All security headers are automatically added. To customize, edit:
`backend/middleware/security_middleware.py`

## 📊 Monitoring

### Health Check Endpoint

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "2.1.0-production-ready"
}
```

### Metrics Endpoint

```bash
curl http://localhost:8000/metrics
```

Provides:
- Total requests
- Success rate
- Response time percentiles (P50, P95, P99)
- Top endpoints
- Status code distribution
- Recent errors

### Performance Headers

Every response includes:
- `X-Response-Time`: Request processing time in milliseconds
- `X-RateLimit-Limit`: Rate limit threshold
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Reset timestamp

## 🔄 CI/CD

### GitHub Actions Workflow

Automatically runs on push to `main` or `develop`:

1. **Backend Tests**: Python 3.11 & 3.12, pytest with coverage
2. **Frontend Tests**: Node 18 & 20, Jest with coverage
3. **Docker Builds**: Backend and frontend images
4. **Integration Tests**: With PostgreSQL and Redis services
5. **Security Scanning**: Trivy vulnerability scanner
6. **Code Quality**: SonarCloud analysis (optional)

### Required Secrets

Add to GitHub repository secrets:
- `CODECOV_TOKEN`: For coverage uploads (optional)
- `SONAR_TOKEN`: For SonarCloud (optional)

## 🛠️ Development Workflow

### Pre-commit Hooks (Recommended)

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

Hooks run automatically on commit:
- trailing-whitespace, end-of-file-fixer
- black (Python formatter)
- isort (Python import sorter)
- flake8 (Python linter)
- prettier (Frontend formatter)
- safety (Security vulnerability checker)

### Code Formatting

```bash
# Backend
cd backend
black . --line-length 100
isort . --profile black
flake8 . --max-line-length=100

# Frontend
cd frontend
npm run format
npm run lint
```

## 📦 Production Deployment Checklist

### Pre-Deployment
- [ ] All tests passing (`pytest && npm test`)
- [ ] Dependencies updated (`pip list --outdated && npm outdated`)
- [ ] Security audit (`safety check && npm audit`)
- [ ] Environment variables configured
- [ ] Database backups configured
- [ ] SSL certificates installed (if using HTTPS)
- [ ] Domain DNS configured

### Deployment
- [ ] Deploy to staging first
- [ ] Run smoke tests
- [ ] Check logs for errors (`docker-compose logs`)
- [ ] Verify health endpoints
- [ ] Test critical workflows (chapter creation, synthesis, Q&A)
- [ ] Monitor for 15 minutes
- [ ] Deploy to production
- [ ] Monitor for 24 hours

### Post-Deployment
- [ ] Setup monitoring alerts
- [ ] Configure log aggregation
- [ ] Setup automated backups
- [ ] Document deployment process
- [ ] Update status page

## 🐛 Troubleshooting

### Backend Issues

**Tests Failing:**
```bash
cd backend
pytest tests/ -v -s  # Verbose with stdout
```

**Import Errors:**
```bash
# Ensure you're in virtual environment
source venv/bin/activate
pip install -r requirements_simplified.txt
```

**Database Connection:**
```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Check connection string
echo $DATABASE_URL
```

### Frontend Issues

**Build Errors:**
```bash
cd frontend
rm -rf node_modules .next
npm ci
npm run build
```

**Port Already in Use:**
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

### Docker Issues

**Containers Not Starting:**
```bash
docker-compose down
docker-compose up --build
```

**View Logs:**
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

## 📚 API Documentation

- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🎯 Performance Targets

Current benchmarks:
- API Response Time: <50ms (95th percentile)
- Database Queries: <20ms (95th percentile)
- Frontend Load: <1.5s (LCP)
- Success Rate: >99%

## 📞 Support

For issues, please create a GitHub issue with:
- Environment details (OS, Python/Node versions)
- Error logs
- Steps to reproduce
- Expected vs actual behavior

## 📄 License

MIT License - See LICENSE file for details

---

**Version**: 2.1.0-production-ready  
**Last Updated**: 2024-01-15  
**Status**: ✅ Production Ready
