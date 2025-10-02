# 🚀 Quick Start Deployment Guide

## For Local Testing (Recommended First)

### Step 1: Create Local Environment File
```bash
# Copy the production template
cp .env.production .env.local

# Edit for local development
```

### Step 2: Update `.env.local` for Local Testing
```bash
# Application Version
VERSION=2.1.0-optimized
ENVIRONMENT=development
DEBUG=true

# Database Configuration (Docker will create these)
POSTGRES_USER=neurosurg_prod
POSTGRES_PASSWORD=y1tH2Mg8GWNVf3UXBOkjpEcnDm0PZ4qI
POSTGRES_DB=neurosurgical_knowledge_prod
POSTGRES_PORT=5432

# Redis Configuration  
REDIS_PASSWORD=W5u94ND0Xfo3SdPzyVbnBKcgrCv8aYeH
REDIS_PORT=6379

# Backend Configuration
BACKEND_PORT=8000
BACKEND_WORKERS=4
BACKEND_REPLICAS=1
SECRET_KEY=Q7w9E2r4T6y8U1i3O5p0A9s8D7f6G5h4
LOG_LEVEL=INFO
MAX_CONNECTIONS=100

# Frontend Configuration - LOCAL URLS
FRONTEND_PORT=3000
FRONTEND_REPLICAS=1
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws

# Your AI API Keys
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
GOOGLE_API_KEY=your-google-api-key-here
PERPLEXITY_API_KEY=your-perplexity-api-key-here

# CORS Configuration - Allow localhost
CORS_ORIGINS=http://localhost:3000,http://localhost

# Nginx Ports
HTTP_PORT=80
HTTPS_PORT=443

# Monitoring (Optional)
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001
GRAFANA_USER=admin
GRAFANA_PASSWORD=M8n7B6v5C4x3Z2a1S0d9F8g7H6j5K4l3

# Feature Flags
ENABLE_METRICS=true
ENABLE_CACHE=true
ENABLE_MOCK_MODE=false

# External Services
PUBMED_API_KEY=baf7cba8137dd7be80c82c3b5a6110821808
PUBMED_EMAIL=ramihatoum00@gmail.com
SENTRY_DSN=
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
EMAIL_FROM=noreply@yourdomain.com
```

### Step 3: Start Local Deployment
```bash
# Use the simple Docker Compose (easier for local testing)
docker-compose -f docker-compose-simple.yml up -d

# Or use the production compose locally
docker-compose -f docker-compose-production.yml up -d
```

### Step 4: Access Your Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/health

---

## For Production with a Domain

### If You Have a Domain (e.g., neurosurgery-app.com)

1. **Point your domain to your server IP**
   - In your domain registrar (GoDaddy, Namecheap, etc.)
   - Create A record: `@ → Your-Server-IP`
   - Create A record: `www → Your-Server-IP`

2. **Update `.env.production`**:
   ```bash
   NEXT_PUBLIC_API_URL=https://neurosurgery-app.com/api/v1
   NEXT_PUBLIC_WS_URL=wss://neurosurgery-app.com/ws
   CORS_ORIGINS=https://neurosurgery-app.com,https://www.neurosurgery-app.com
   ```

3. **Update `nginx/conf.d/nssp.conf`**:
   Replace `yourdomain.com` with your actual domain

4. **Get SSL Certificate** (Let's Encrypt - FREE):
   ```bash
   sudo certbot certonly --standalone -d neurosurgery-app.com -d www.neurosurgery-app.com
   sudo cp /etc/letsencrypt/live/neurosurgery-app.com/fullchain.pem nginx/ssl/cert.pem
   sudo cp /etc/letsencrypt/live/neurosurgery-app.com/privkey.pem nginx/ssl/key.pem
   ```

5. **Deploy**:
   ```bash
   ./deploy-production.sh
   ```

---

## For Cloud Deployment (No Domain Yet)

### AWS/GCP/Azure with Public IP

If you deploy to cloud and get a public IP (e.g., 54.123.45.67):

```bash
NEXT_PUBLIC_API_URL=http://54.123.45.67:8000/api/v1
NEXT_PUBLIC_WS_URL=ws://54.123.45.67:8000/ws
CORS_ORIGINS=http://54.123.45.67:3000,http://54.123.45.67
```

---

## 🎯 Recommended Path for You

Since you already have all the API keys configured, I recommend:

### Option 1: Test Locally First (Safest)
```bash
# 1. Copy your current .env.production to .env
cp .env.production .env

# 2. Update just these two lines in .env:
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws

# 3. Start with simple compose
docker-compose -f docker-compose-simple.yml up -d

# 4. Open browser to http://localhost:3000
```

### Option 2: If You Have a Domain
```bash
# Update .env.production with your domain name
# Replace ALL instances of "yourdomain.com" with your actual domain
# Then deploy
```

---

## ⚠️ Important Security Note

I noticed your API keys are visible in the file. For security:

1. **Never commit `.env` or `.env.production` with real keys to Git**
   ```bash
   echo ".env*" >> .gitignore
   echo "!.env.example" >> .gitignore
   ```

2. **Consider regenerating the API keys** you've shared here, as they are now exposed

3. **Use environment variables** on your production server instead of files

---

## 🆘 Need Help?

**Don't have a domain?**
- Start with local testing (Option 1 above)
- Buy a domain later from: Namecheap, GoDaddy, Google Domains (~$10-15/year)

**Testing on your local network?**
- Use your computer's local IP (e.g., 192.168.1.100)
- Update URLs to `http://192.168.1.100:8000/api/v1`

**Deploying to a VPS/Cloud?**
- Get the server's public IP
- Update URLs to use that IP
- Later add a domain for better HTTPS support