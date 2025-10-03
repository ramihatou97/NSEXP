# Quick Deployment Guide - Frontend Docker Build Fix

## 🚀 Quick Start

The frontend Docker build has been optimized and is now production-ready!

### One-Command Test
```bash
./test-frontend-docker-build.sh
```

### One-Command Validation
```bash
./validate-frontend-docker.sh
```

## 📦 Building the Image

### Local Development Build
```bash
cd frontend
docker build -t nsexp-frontend:dev -f Dockerfile .
```

### Production Build with Environment Variables
```bash
cd frontend
docker build -t nsexp-frontend:latest \
  --build-arg NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api/v1 \
  --build-arg NEXT_PUBLIC_WS_URL=wss://api.yourdomain.com/ws \
  -f Dockerfile .
```

### Using Docker Compose
```bash
# Simple setup (development)
docker-compose -f docker-compose-simple.yml up --build

# Full production setup
docker-compose -f docker-compose-production.yml up --build
```

## 🏃 Running the Container

### Basic Run
```bash
docker run -d -p 3000:3000 \
  --name nsexp-frontend \
  nsexp-frontend:latest
```

### With Environment Variables
```bash
docker run -d -p 3000:3000 \
  --name nsexp-frontend \
  -e NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1 \
  -e NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws \
  nsexp-frontend:latest
```

### With Health Checks
```bash
docker run -d -p 3000:3000 \
  --name nsexp-frontend \
  --health-cmd="wget --no-verbose --tries=1 --spider http://localhost:3000 || exit 1" \
  --health-interval=30s \
  --health-timeout=10s \
  --health-retries=3 \
  nsexp-frontend:latest
```

## 🔍 Monitoring & Debugging

### Check Container Logs
```bash
docker logs nsexp-frontend
docker logs -f nsexp-frontend  # Follow logs in real-time
```

### Check Container Health
```bash
docker ps --filter "name=nsexp-frontend"
docker inspect --format='{{.State.Health.Status}}' nsexp-frontend
```

### Access Container Shell
```bash
docker exec -it nsexp-frontend sh
```

### Test Application Endpoint
```bash
curl http://localhost:3000
curl http://localhost:3000/api/health
```

## 🛠️ Troubleshooting

### Build Fails with "libc6-compat" Error
**This is now handled gracefully!** You'll see a warning but the build continues.

### Build is Slow
Use Docker build cache:
```bash
docker build --cache-from nsexp-frontend:latest -t nsexp-frontend:latest .
```

### Container Exits Immediately
Check logs:
```bash
docker logs nsexp-frontend
```

Common issues:
- Missing environment variables
- Port already in use
- Backend API not accessible

### Can't Access Application
1. Check if container is running: `docker ps`
2. Check logs: `docker logs nsexp-frontend`
3. Verify port mapping: `docker port nsexp-frontend`
4. Test locally: `curl http://localhost:3000`

## 📊 Performance Tips

### Build Optimization
- Use `--cache-from` to reuse previous builds
- Use `--target` to build specific stages
- Enable BuildKit: `DOCKER_BUILDKIT=1 docker build ...`

### Runtime Optimization
- Use `--memory` and `--cpus` to limit resources
- Use health checks to ensure availability
- Mount volumes for persistent data if needed

## 🔐 Security Best Practices

### Run as Non-Root User
The Dockerfile already configures this - the application runs as user `nextjs` (UID 1001).

### Scan for Vulnerabilities
```bash
docker scan nsexp-frontend:latest
```

### Use Specific Tags
Instead of `:latest`, use version tags:
```bash
docker tag nsexp-frontend:latest nsexp-frontend:v2.0.0
```

## 📝 CI/CD Integration

### GitHub Actions (Automatic)
Push to main branch triggers automatic build and push:
```bash
git push origin main
```

Monitor at: https://github.com/ramihatou97/NSEXP/actions

### Manual Docker Hub Push
```bash
docker login
docker tag nsexp-frontend:latest yourusername/nsexp-frontend:latest
docker push yourusername/nsexp-frontend:latest
```

## 🌐 Production Deployment

### Using docker-compose (Recommended)
```bash
# Copy production compose file
cp docker-compose-production.yml docker-compose.yml

# Set environment variables
export DOCKER_USER=yourusername
export NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api/v1
export NEXT_PUBLIC_WS_URL=wss://api.yourdomain.com/ws

# Deploy
docker-compose up -d
```

### Using Kubernetes
```bash
# Build and tag
docker build -t yourusername/nsexp-frontend:v2.0.0 -f frontend/Dockerfile frontend/
docker push yourusername/nsexp-frontend:v2.0.0

# Deploy (assuming you have k8s manifests)
kubectl apply -f k8s/frontend-deployment.yaml
```

### Using Cloud Platforms

**AWS ECS:**
```bash
# Tag for ECR
docker tag nsexp-frontend:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/nsexp-frontend:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/nsexp-frontend:latest
```

**Google Cloud Run:**
```bash
gcloud builds submit --tag gcr.io/PROJECT-ID/nsexp-frontend
gcloud run deploy nsexp-frontend --image gcr.io/PROJECT-ID/nsexp-frontend --platform managed
```

**Azure Container Instances:**
```bash
az acr build --registry myregistry --image nsexp-frontend:latest .
az container create --resource-group mygroup --name nsexp-frontend --image myregistry.azurecr.io/nsexp-frontend:latest
```

## 📚 Additional Resources

- [FRONTEND_BUILD_FIX_2024.md](./FRONTEND_BUILD_FIX_2024.md) - Detailed fix documentation
- [FRONTEND_DOCKER_FIX.md](./FRONTEND_DOCKER_FIX.md) - Original fix documentation
- [DOCKER_BUILD_GUIDE.md](./DOCKER_BUILD_GUIDE.md) - General Docker guide
- [test-frontend-docker-build.sh](./test-frontend-docker-build.sh) - Comprehensive test script
- [validate-frontend-docker.sh](./validate-frontend-docker.sh) - Validation script

## ✅ Checklist

Before deploying to production:

- [ ] Run `./test-frontend-docker-build.sh` - all tests pass
- [ ] Run `./validate-frontend-docker.sh` - validation passes
- [ ] Set production environment variables
- [ ] Configure SSL/TLS certificates
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy
- [ ] Test health endpoints
- [ ] Review security settings
- [ ] Document deployment process
- [ ] Set up CI/CD pipeline

## 🆘 Need Help?

1. Check the troubleshooting section above
2. Review logs: `docker logs nsexp-frontend`
3. Run test script: `./test-frontend-docker-build.sh`
4. Check GitHub Actions if using CI/CD
5. Review comprehensive documentation in `FRONTEND_BUILD_FIX_2024.md`

---

**Build Status:** ✅ Production Ready  
**Last Updated:** 2024  
**Docker Version:** 20.10+  
**Node Version:** 18-alpine  
**Next.js Version:** 14.0.3
