# Requirements Files Strategy

## 📁 File Structure Explanation

This project uses **two requirements files** for different deployment scenarios:

### 🚀 `requirements_simplified.txt` (RECOMMENDED for development)
- **Use for**: Local development, testing, lightweight deployments
- **Size**: ~300MB installation
- **Features**: Core functionality with optional AI services
- **Best for**: Getting started, CI/CD, containers with limited resources

```bash
# Quick start (recommended)
pip install -r requirements_simplified.txt
```

### 🏭 `requirements.txt` (Full production stack)
- **Use for**: Full production deployments with all medical NLP features
- **Size**: ~3GB installation  
- **Features**: Complete ML pipeline, medical libraries, monitoring
- **Best for**: Research environments, full-featured production

```bash
# Full installation (for advanced features)
pip install -r requirements.txt
```

## 🔄 Migration Path

1. **Start with simplified**: `requirements_simplified.txt`
2. **Add features as needed**: Install additional packages individually
3. **Upgrade to full**: Use `requirements.txt` when you need advanced features

## 📦 Key Differences

| Feature | Simplified | Full |
|---------|------------|------|
| **FastAPI Core** | ✅ | ✅ |
| **FAISS Vector Search** | ✅ | ✅ |
| **Basic AI (OpenAI, Claude)** | ✅ | ✅ |
| **PDF Processing** | ✅ | ✅ |
| **Advanced ML (torch, transformers)** | ❌ | ✅ |
| **Medical NLP (scispacy, medcat)** | ❌ | ✅ |
| **Neuroimaging (nibabel, dipy)** | ❌ | ✅ |
| **Monitoring (prometheus, sentry)** | ❌ | ✅ |
| **Dev Tools (black, mypy)** | ❌ | ✅ |

## 🎯 Which File to Use?

### Choose `requirements_simplified.txt` if:
- ✅ Getting started with the project
- ✅ Docker deployments
- ✅ CI/CD pipelines
- ✅ Limited disk space/bandwidth
- ✅ Just need core neurosurgical knowledge management

### Choose `requirements.txt` if:
- ✅ Running advanced medical NLP
- ✅ Processing neuroimaging data
- ✅ Full research environment
- ✅ Production with all monitoring
- ✅ Contributing to ML features

## 🔧 Docker Usage

```yaml
# Simplified (recommended)
FROM python:3.11-slim
COPY requirements_simplified.txt .
RUN pip install -r requirements_simplified.txt

# Full features
FROM python:3.11
COPY requirements.txt .
RUN pip install -r requirements.txt
```

## 📝 Maintenance

Both files should be kept in sync for **common dependencies**. Update both when changing:
- FastAPI version
- Database drivers
- Core utilities

The system is designed to work with **either file** - it gracefully handles missing optional dependencies.