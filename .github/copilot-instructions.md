# Neurosurgical Knowledge Management System - AI Agent Instructions

## 🧠 System Overview
You're working with an AI-powered platform for neurosurgical knowledge synthesis and management. This is a **simplified, single-user version** designed for personal use without authentication or multi-tenancy overhead.

## 🏗️ Architecture Essentials

### Three-Layer Architecture
1. **Frontend (Next.js 14)**: React app at `localhost:3000`
2. **Backend (FastAPI)**: Python API at `localhost:8000`
3. **Data Layer**: PostgreSQL + Redis + file storage

### Key Service Boundaries
- **AI Services**: Multi-provider (OpenAI, Claude, Gemini) with graceful fallbacks
- **Chapter Management**: Core content organization by specialty
- **Reference System**: PDF processing and citation tracking
- **Q&A Engine**: Context-aware medical question answering

## � Development Environment Setup

### Required VS Code Extensions
```json
{
  "recommendations": [
    "ms-python.python",              // Python language support
    "ms-python.vscode-pylance",      // Python type checking
    "ms-python.black-formatter",     // Python formatting
    "dbaeumer.vscode-eslint",        // JavaScript/TypeScript linting
    "esbenp.prettier-vscode",        // Code formatting
    "bradlc.vscode-tailwindcss",     // Tailwind CSS IntelliSense
    "prisma.prisma",                 // Database schema
    "mtxr.sqltools",                 // SQL database explorer
    "mtxr.sqltools-driver-pg"        // PostgreSQL driver
  ]
}
```

### Workspace Settings
```json
{
  "python.defaultInterpreterPath": "./backend/venv/Scripts/python.exe",
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
  }
}
```

## �🛠️ Critical Development Workflows

### Initial Setup (Always Run First)
```bash
# Backend setup
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements_simplified.txt

# Frontend setup
cd ../frontend
npm install

# Test system integrity
cd ..
python test_system.py  # Validates all components
```

### Running the Application
```bash
# Option 1: Docker (Recommended)
docker-compose -f docker-compose-simple.yml up

# Option 2: Manual
# Terminal 1 - Backend
cd backend && uvicorn main_simplified:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend && npm run dev
```

### Database Operations
- **Connection**: `postgresql+asyncpg://neurosurg:neurosurg123@localhost:5432/neurosurgical_knowledge`
- **Auto-migration**: Tables created on startup via SQLAlchemy
- **Models Location**: `backend/models/database_simplified.py`

## 🎯 Project-Specific Patterns

### AI Service Integration Pattern
```python
# All AI services follow this pattern in backend/services/ai_service.py:
async def generate_with_provider(self, prompt: str) -> Dict[str, Any]:
    if not PROVIDER_AVAILABLE or not self.api_key:
        return self._mock_response(prompt, "provider-name")
    # Real implementation...
```

### Medical Specialties Enum
Always use these exact values when working with specialties:
```python
TUMOR, VASCULAR, SPINE, FUNCTIONAL, PEDIATRIC, TRAUMA, 
PERIPHERAL_NERVE, SKULL_BASE, ENDOSCOPIC, STEREOTACTIC
```

### API Endpoint Pattern
All endpoints follow: `/api/v1/{resource}` (e.g., `/api/v1/chapters`, `/api/v1/synthesis/generate`)

### Error Handling Convention
Services return structured responses:
```python
{
    "success": bool,
    "data": Optional[Any],
    "error": Optional[str],
    "metadata": Optional[Dict]
}
```

## 📍 Key File Locations

### Backend Structure
```
backend/
├── main_simplified.py          # Entry point - API routes
├── models/database_simplified.py # All database models
├── services/
│   ├── ai_service.py          # AI provider integrations
│   ├── chapter_service.py     # Chapter CRUD operations
│   ├── synthesis_service.py   # Content synthesis logic
│   └── qa_service.py          # Q&A functionality
└── config/settings_simplified.py # Environment configuration
```

### Frontend Key Components
```
frontend/
├── app/                       # Next.js 14 app directory
├── components/
│   └── chapters/             # Chapter UI components
├── services/api.ts           # Backend API client
└── hooks/                    # React custom hooks
```

## 🔗 External Dependencies & Integration Points

### AI Providers (Optional - Mock Mode Available)
- **OpenAI**: Set `OPENAI_API_KEY` for GPT-4 synthesis
- **Anthropic**: Set `ANTHROPIC_API_KEY` for Claude models
- **Google**: Set `GOOGLE_API_KEY` for Gemini models

### Data Storage
- **PostgreSQL**: Primary data store (required)
- **Redis**: Caching layer (optional but recommended)
- **File Storage**: PDFs in `./textbooks`, images in `./storage`

### Medical APIs
- PubMed integration ready (add `PUBMED_API_KEY`)
- ICD-10/CPT code lookups via external services

## 🤖 AI Provider Priority Guide

### Task-Specific Provider Selection

**Long-Form Synthesis (>2000 tokens)**
- **Primary**: Claude 3 Opus/Sonnet - Best for comprehensive medical synthesis
- **Fallback**: GPT-4 Turbo
- **Reason**: Claude excels at long-context understanding and maintaining medical accuracy

**Quick Q&A (<500 tokens)**
- **Primary**: GPT-3.5 Turbo or Gemini Flash
- **Fallback**: GPT-4
- **Reason**: Faster response times, cost-effective for simple queries

**Evidence-Based Analysis**
- **Primary**: GPT-4 or Claude 3 Opus
- **Fallback**: Perplexity API (web search enabled)
- **Reason**: Superior reasoning for complex medical evidence evaluation

**PDF Content Extraction**
- **Primary**: Gemini 1.5 Pro
- **Fallback**: GPT-4 Vision
- **Reason**: Large context window handles entire PDFs efficiently

**Citation Generation**
- **Primary**: GPT-4
- **Fallback**: Claude 3 Sonnet
- **Reason**: Consistent formatting and accuracy

### Provider Configuration Example
```python
# In backend/services/ai_service.py
TASK_PROVIDER_MAP = {
    "synthesis": "claude-3-opus",      # Long synthesis
    "qa_quick": "gpt-3.5-turbo",       # Quick answers
    "qa_complex": "gpt-4",              # Complex medical questions
    "pdf_extraction": "gemini-1.5-pro", # PDF processing
    "citation": "gpt-4"                 # Citation formatting
}
```

## 🩺 Medical Content Validation

### Evidence-Based Content Requirements

**Evidence Hierarchy (Use in order of preference)**
1. **Level I**: Systematic reviews, meta-analyses
2. **Level II**: Randomized controlled trials (RCTs)
3. **Level III**: Cohort studies, case-control studies
4. **Level IV**: Case series, case reports
5. **Level V**: Expert opinion, basic science

### Medical Accuracy Checks

**Mandatory Validation Steps**
```python
# All AI-generated medical content must pass:
def validate_medical_content(content: str) -> MedicalValidation:
    checks = {
        "has_citations": check_citations_present(content),
        "evidence_level": extract_evidence_level(content),
        "contraindications_mentioned": check_contraindications(content),
        "dosage_accuracy": validate_dosages(content),
        "anatomical_accuracy": validate_anatomy(content)
    }
    return MedicalValidation(**checks)
```

**Content Review Flags**
- ❌ **Never include**: Specific patient data, treatment recommendations without evidence
- ⚠️ **Always flag**: Dosage info, surgical technique details, off-label use
- ✅ **Always include**: Evidence levels, citation sources, limitations

### Specialty-Specific Validation

**Neurosurgery-Specific Checks**
```python
NEUROSURG_VALIDATION = {
    "tumor": ["WHO grade", "molecular markers", "surgical margins"],
    "vascular": ["aneurysm size", "Hunt-Hess grade", "Fisher scale"],
    "spine": ["spinal level", "approach (anterior/posterior)", "fusion levels"],
    "functional": ["target coordinates", "stimulation parameters"]
}
```

## 📊 Performance Benchmarks

### Target Response Times (95th Percentile)

| Operation | Target | Timeout | Notes |
|-----------|--------|---------|-------|
| Chapter list | <200ms | 5s | Includes pagination |
| Chapter synthesis | <30s | 90s | ~2000 tokens |
| PDF processing | <5s/page | 60s | Depends on OCR |
| Q&A simple | <3s | 10s | Cached responses <500ms |
| Q&A complex | <10s | 30s | With reference search |
| Search query | <100ms | 5s | Full-text search |
| Semantic search | <500ms | 10s | Vector similarity |

### System Health Metrics

**Backend Performance**
```python
# Monitor in production:
HEALTH_THRESHOLDS = {
    "db_connection_pool": 0.8,      # Max 80% utilization
    "memory_usage_mb": 2000,        # Alert above 2GB
    "active_requests": 100,         # Max concurrent
    "ai_api_latency_ms": 5000,      # P95 latency
    "cache_hit_rate": 0.7           # Minimum 70%
}
```

**AI Service Benchmarks**
- **Token throughput**: 500-1000 tokens/second (GPT-4)
- **Concurrent requests**: Max 10 simultaneous AI calls
- **Cache effectiveness**: 70%+ hit rate for repeated queries
- **Fallback activation**: <100ms detection + switch time

### Resource Limits

**Database**
- Connection pool: 20 connections
- Query timeout: 30 seconds
- Transaction isolation: READ COMMITTED

**Redis Cache**
- TTL: 24 hours for AI responses
- Max memory: 500MB
- Eviction policy: LRU

**File Processing**
- Max PDF size: 100MB
- Concurrent uploads: 5
- Chunk size: 1000 tokens (overlap: 200)

## 🔄 Error Recovery Patterns

### AI Service Fallback Chain

**Automatic Fallback Strategy**
```python
# In backend/services/ai_service.py
async def generate_with_fallback(self, prompt: str, task_type: str):
    providers = [
        ("claude-3-opus", 30),      # Primary, 30s timeout
        ("gpt-4", 20),               # Secondary, 20s timeout
        ("gemini-1.5-pro", 15),     # Tertiary, 15s timeout
        ("mock", 1)                  # Always succeeds
    ]
    
    for provider, timeout in providers:
        try:
            return await self.call_provider(provider, prompt, timeout)
        except (TimeoutError, APIError) as e:
            logger.warning(f"{provider} failed: {e}, trying next...")
            continue
    
    raise AllProvidersFailedError()
```

**Error Types & Recovery**

| Error | Recovery Action | Retry | User Impact |
|-------|----------------|-------|-------------|
| API Rate Limit | Wait + exponential backoff | 3x | Queue request |
| API Timeout | Switch to faster model | 1x | Degraded quality |
| Invalid API Key | Use mock responses | 0x | Warn user |
| Network Error | Retry with backoff | 3x | Temporary failure |
| Token Limit | Reduce prompt size | 1x | Chunked response |
| Content Filter | Rephrase + retry | 2x | May fail |

### Database Connection Recovery

**Connection Pool Management**
```python
# In backend/core/database_simplified.py
from sqlalchemy.pool import QueuePool
from tenacity import retry, stop_after_attempt, wait_exponential

engine = create_async_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,        # Verify connections before use
    pool_recycle=3600,         # Recycle connections every hour
    echo=False
)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
async def execute_with_retry(query):
    """Execute database query with automatic retry"""
    async with engine.begin() as conn:
        return await conn.execute(query)
```

**Database Error Handling**
```python
# Common database errors and fixes:
try:
    result = await session.execute(query)
except asyncpg.exceptions.PostgresConnectionError:
    # Connection lost - reconnect automatically
    await engine.dispose()
    engine = create_new_engine()
except asyncpg.exceptions.QueryCanceledError:
    # Query timeout - reduce complexity or add index
    logger.error("Query timeout - optimize query")
except asyncpg.exceptions.DeadlockDetectedError:
    # Transaction deadlock - retry with backoff
    await asyncio.sleep(random.uniform(0.1, 0.5))
    # Retry transaction
```

### Redis Cache Failures

**Graceful Degradation**
```python
# Always work without Redis - it's optional
async def get_cached_response(key: str):
    try:
        if redis_available:
            return await redis.get(key)
    except redis.ConnectionError:
        logger.warning("Redis unavailable, bypassing cache")
    except redis.TimeoutError:
        logger.warning("Redis timeout, bypassing cache")
    
    return None  # Proceed without cache

# NEVER fail the request if Redis is down
```

### File Processing Errors

**PDF Processing Recovery**
```python
# In backend/services/pdf_service.py
async def process_pdf_with_recovery(file_path: Path):
    try:
        return await extract_pdf_text(file_path)
    except PDFEncryptedError:
        # Try with password or OCR
        return await ocr_fallback(file_path)
    except PDFCorruptedError:
        # Attempt repair
        repaired = await repair_pdf(file_path)
        return await extract_pdf_text(repaired)
    except MemoryError:
        # Process in smaller chunks
        return await extract_pdf_chunked(file_path, chunk_size=10)
```

### Critical Error Response Pattern

**User-Facing Error Messages**
```python
ERROR_MESSAGES = {
    "ai_service_down": "AI service temporarily unavailable. Using cached responses.",
    "db_connection_lost": "Database connection error. Reconnecting automatically...",
    "synthesis_timeout": "Synthesis taking longer than expected. Please try a smaller section.",
    "pdf_too_large": "PDF exceeds 100MB limit. Please split into smaller files.",
    "rate_limit_hit": "API rate limit reached. Request queued for processing."
}
```

**Never Expose**
- API keys or credentials
- Internal error stack traces
- Database connection strings
- Provider-specific error details

## ⚡ Performance Considerations

1. **Async Everything**: Backend uses `asyncio` throughout - maintain async/await patterns
2. **Connection Pooling**: Database connections managed by SQLAlchemy async pool (20 connections)
3. **AI Response Caching**: Redis caches AI responses for 24 hours by default (70%+ hit rate)
4. **PDF Processing**: Large files processed in chunks (1000 tokens, 200 overlap) to avoid memory issues
5. **Lazy Loading**: Load references and citations only when needed
6. **Batch Operations**: Group database operations - use `bulk_insert_mappings()` for >10 records

### Performance Monitoring

**Always check before deploying:**
```bash
# Backend performance test
cd backend
pytest tests/performance/ -v

# Load test (requires locust)
locust -f tests/load_test.py --host=http://localhost:8000

# Database query analysis
psql -d neurosurgical_knowledge -c "EXPLAIN ANALYZE SELECT ..."
```

## 🚨 Common Pitfalls & Solutions

### Environment Variables
Create `.env` file in backend directory - the system expects:
```bash
DATABASE_URL=postgresql+asyncpg://neurosurg:neurosurg123@localhost:5432/neurosurgical_knowledge
# AI keys are optional - system uses mocks if missing
```

### Frontend API URL
Frontend expects backend at `http://localhost:8000/api/v1` - update in `frontend/.env.local` if different

### Database Connection
If "database does not exist" error:
```bash
createdb -U postgres neurosurgical_knowledge
```

### Python Path Issues
Always run backend commands from the `backend/` directory to ensure proper imports

## 🧪 Testing Strategy

1. **System Test**: Run `python test_system.py` to validate all components
2. **API Testing**: Use `/api/docs` for interactive API testing
3. **Mock AI Mode**: Test without API keys - system provides realistic mock responses

## 📝 Medical Domain Specifics

- **Specialties**: Always use enum values from `NeurosurgicalSpecialty`
- **Procedures**: Reference `ProcedureType` enum for standard procedures
- **Anatomical Regions**: Use `AnatomicalRegion` enum for consistency
- **Evidence Levels**: Follow medical evidence hierarchy in synthesis

## 🔄 Typical Development Flow

1. Check system health: `python test_system.py`
2. Start services: `docker-compose -f docker-compose-simple.yml up`
3. Make changes in appropriate service file
4. Backend auto-reloads, frontend requires manual refresh
5. Test via API docs or frontend UI

Remember: This is a **simplified single-user system** - no authentication required, direct database access, and streamlined for personal medical knowledge management.