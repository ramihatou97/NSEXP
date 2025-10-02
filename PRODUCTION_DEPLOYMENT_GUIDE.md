# 🚀 NSSP Production Deployment Guide

This guide provides comprehensive instructions for deploying the Neurosurgical Knowledge Management System (NSSP) in a production environment using Docker Compose.

## 📋 Prerequisites

- **Docker Engine** 20.10+ and **Docker Compose** 2.0+
- **Domain name** with DNS configured (for HTTPS)
- **SSL certificates** (or use Let's Encrypt)
- **Minimum server requirements**:
  - 4 CPU cores
  - 8GB RAM
  - 50GB SSD storage
  - Ubuntu 20.04+ or similar Linux distribution

## 🔧 Quick Production Deployment

### 1. Clone and Configure

```bash
# Clone the repository
git clone https://github.com/ramihatou97/NNP.git
cd NNP

# Copy production environment template
cp .env.production .env

# Edit configuration with your values
nano .env  # or use your preferred editor
```

### 2. Update Critical Settings in `.env`

```bash
# Required changes:
POSTGRES_PASSWORD=<strong-password>
REDIS_PASSWORD=<strong-password>
SECRET_KEY=<generate-with: openssl rand -base64 32>

# Update domain
NEXT_PUBLIC_API_URL=https://your-domain.com/api/v1
NEXT_PUBLIC_WS_URL=wss://your-domain.com/ws
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com

# Optional: Add AI API keys
OPENAI_API_KEY=<your-key>
ANTHROPIC_API_KEY=<your-key>
GOOGLE_API_KEY=<your-key>
```

### 3. SSL Certificate Setup

#### Option A: Self-Signed (Testing Only)
```bash
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout nginx/ssl/key.pem \
    -out nginx/ssl/cert.pem \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
```

#### Option B: Let's Encrypt (Recommended)
```bash
# Install certbot
sudo apt-get update
sudo apt-get install certbot

# Generate certificates
sudo certbot certonly --standalone -d your-domain.com -d www.your-domain.com

# Copy to nginx/ssl
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/key.pem
```

### 4. Update Nginx Configuration

Edit `nginx/conf.d/nssp.conf` and replace `yourdomain.com` with your actual domain:

```nginx
server_name your-actual-domain.com www.your-actual-domain.com;
```

### 5. Deploy with Docker Compose

```bash
# Make deployment script executable
chmod +x deploy-production.sh

# Run deployment
./deploy-production.sh
```

Or manually:

```bash
# Build and start all services
docker-compose -f docker-compose-production.yml up -d

# Verify all services are running
docker-compose -f docker-compose-production.yml ps

# Check logs
docker-compose -f docker-compose-production.yml logs -f
```

## 🏗️ Production Architecture

### Services Deployed:

1. **PostgreSQL** (Primary database)
   - Persistent volume for data
   - Health checks enabled
   - Connection pooling configured

2. **Redis** (Caching layer)
   - Persistent AOF enabled
   - Memory limit: 512MB
   - LRU eviction policy

3. **Backend** (FastAPI)
   - Multiple workers (Gunicorn + Uvicorn)
   - Health checks
   - Auto-restart on failure

4. **Frontend** (Next.js)
   - Production build
   - Static asset optimization
   - Server-side rendering

5. **Nginx** (Reverse Proxy)
   - SSL termination
   - Load balancing
   - Static file serving
   - Gzip compression

6. **Monitoring** (Optional)
   - Prometheus metrics collection
   - Grafana dashboards
   - Database backups

## 📊 Monitoring & Maintenance

### Enable Monitoring Stack

```bash
# Deploy with monitoring
docker-compose -f docker-compose-production.yml --profile monitoring up -d

# Access monitoring
# Grafana: http://your-domain:3001 (admin/admin123)
# Prometheus: http://your-domain:9090
```

### Database Backups

Automated backups run daily at 2 AM. Manual backup:

```bash
docker-compose -f docker-compose-production.yml run backup /backup.sh
```

Restore from backup:
```bash
# Stop backend services
docker-compose -f docker-compose-production.yml stop backend

# Restore database
docker exec -i nssp_db_primary psql -U neurosurg_prod neurosurgical_knowledge_prod < backups/nssp_backup_20251002_120000.sql

# Restart services
docker-compose -f docker-compose-production.yml start backend
```

### Log Management

View logs:
```bash
# All services
docker-compose -f docker-compose-production.yml logs -f

# Specific service
docker-compose -f docker-compose-production.yml logs -f backend

# Save logs
docker-compose -f docker-compose-production.yml logs > nssp_logs_$(date +%Y%m%d).txt
```

## 🔒 Security Hardening

### 1. Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP (redirects to HTTPS)
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 2. Secure Environment Variables

```bash
# Set restrictive permissions
chmod 600 .env

# Use Docker secrets for sensitive data (optional)
docker secret create postgres_password ./postgres_password.txt
```

### 3. Enable Automatic Security Updates

```bash
sudo apt-get install unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

## 🚨 Troubleshooting

### Common Issues:

#### 1. Database Connection Failed
```bash
# Check PostgreSQL logs
docker logs nssp_db_primary

# Verify connection
docker exec -it nssp_db_primary psql -U neurosurg_prod -d neurosurgical_knowledge_prod
```

#### 2. Backend Not Starting
```bash
# Check backend logs
docker logs nssp_backend

# Verify environment variables
docker exec nssp_backend env | grep DATABASE_URL
```

#### 3. SSL Certificate Issues
```bash
# Test SSL configuration
openssl s_client -connect localhost:443 -servername your-domain.com

# Verify Nginx configuration
docker exec nssp_nginx nginx -t
```

#### 4. High Memory Usage
```bash
# Check container resources
docker stats

# Adjust memory limits in docker-compose-production.yml
```

## 📈 Scaling

### Horizontal Scaling

Increase replicas in `.env`:
```bash
BACKEND_REPLICAS=4
FRONTEND_REPLICAS=3
```

Then update deployment:
```bash
docker-compose -f docker-compose-production.yml up -d --scale backend=4 --scale frontend=3
```

### Database Optimization

For high load, consider:
1. **Read replicas** for query distribution
2. **Connection pooling** with PgBouncer
3. **Query optimization** using EXPLAIN ANALYZE
4. **Index optimization** for search performance

## 🔄 Updates & Maintenance

### Update Application

```bash
# Pull latest changes
git pull origin main

# Rebuild and deploy
docker-compose -f docker-compose-production.yml build
docker-compose -f docker-compose-production.yml up -d
```

### Zero-Downtime Deployment

```bash
# Build new images
docker-compose -f docker-compose-production.yml build

# Rolling update
docker-compose -f docker-compose-production.yml up -d --no-deps --build backend
docker-compose -f docker-compose-production.yml up -d --no-deps --build frontend
```

## 📞 Health Checks

Monitor system health:

```bash
# Application health
curl https://your-domain.com/health

# API health
curl https://your-domain.com/api/v1/health

# Metrics endpoint
curl https://your-domain.com/metrics
```

## 🎯 Performance Tuning

### PostgreSQL Optimization

Edit `scripts/postgres-init.sql` for your hardware:
```sql
-- For 8GB RAM server
ALTER SYSTEM SET shared_buffers = '2GB';
ALTER SYSTEM SET effective_cache_size = '6GB';
ALTER SYSTEM SET work_mem = '16MB';
```

### Redis Optimization

Adjust in docker-compose:
```yaml
command: >
  redis-server
  --maxmemory 2gb
  --maxmemory-policy allkeys-lru
```

### Nginx Optimization

Update `nginx/nginx.conf`:
```nginx
worker_processes auto;
worker_connections 2048;
```

## 🚀 Production Checklist

- [ ] Strong passwords set in `.env`
- [ ] SSL certificates installed
- [ ] Domain configured in Nginx
- [ ] Firewall rules applied
- [ ] Backup script tested
- [ ] Monitoring enabled
- [ ] Health checks verified
- [ ] Log rotation configured
- [ ] Security updates enabled
- [ ] Performance tuned for hardware

---

**Need help?** Check the logs first: `docker-compose -f docker-compose-production.yml logs`

**Support:** Open an issue at https://github.com/ramihatou97/NNP/issues