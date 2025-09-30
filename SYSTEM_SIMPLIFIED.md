# Neurosurgical Knowledge Management System - Simplified

## Overview
This is a **single-user**, simplified version of the neurosurgical knowledge management system. All core functionality has been retained while removing unnecessary multi-user complexity, HIPAA compliance overhead, and authentication systems.

## Key Changes from Original

### ✅ RETAINED (Core Functionality)
- **All neurosurgical features**: Chapter management, surgical procedures, reference library
- **AI-powered synthesis**: OpenAI, Claude, Gemini integration
- **PDF processing**: Extract and process neurosurgical literature
- **Q&A system**: Context-aware question answering
- **Behavioral learning**: Pattern recognition for single user
- **Citation networks**: Track relationships between references
- **Medical imaging support**: DICOM and standard image formats
- **Specialty-specific content**: Tumor, vascular, spine, functional, pediatric, etc.

### ❌ REMOVED (Unnecessary Complexity)
- Multi-user authentication system
- User roles and permissions (RBAC)
- HIPAA compliance overhead
- Team collaboration features
- User management endpoints
- Session management
- Password reset workflows
- Multi-tenant architecture

## Architecture

### Backend (FastAPI)
```
backend/
├── models/
│   └── database_simplified.py          # Single-user database models
├── services/
│   ├── ai_service.py                   # AI integrations (OpenAI, Claude, Gemini)
│   ├── chapter_service.py              # Chapter management
│   ├── reference_service.py            # Reference/citation management
│   ├── synthesis_service.py            # Content synthesis
│   ├── qa_service.py                   # Question answering
│   └── pdf_service.py                  # PDF processing
├── core/
│   └── database_simplified.py          # Async database configuration
├── config/
│   └── settings_simplified.py          # Simplified settings
└── main_simplified.py                  # Simplified FastAPI app
```

### Frontend (Next.js 14)
```
frontend/
├── app/
│   ├── layout.tsx                      # Main layout (no auth)
│   ├── page.tsx                        # Home page (simplified CTAs)
│   └── providers.tsx                   # Providers (removed SessionProvider)
└── components/                         # React components
```

### Database Models

**Core Models:**
- `Chapter`: Neurosurgical chapters with AI synthesis
- `Reference`: Medical literature references
- `Citation`: Links between chapters and references
- `SurgicalProcedure`: Surgical procedure details
- `QASession`: Q&A history (no user_id)
- `SynthesisJob`: AI synthesis jobs (no user_id)
- `BehavioralPattern`: Learning patterns (single user)
- `UserPreferences`: Single user preferences

**Neurosurgical Specialties:**
- Tumor
- Vascular
- Spine
- Functional
- Pediatric
- Trauma
- Peripheral Nerve
- Skull Base
- Endoscopic
- Stereotactic

## API Endpoints (Simplified)

### Chapters
- `GET /api/v1/chapters` - List all chapters
- `GET /api/v1/chapters/{id}` - Get chapter details
- `POST /api/v1/chapters` - Create new chapter
- `PUT /api/v1/chapters/{id}` - Update chapter
- `DELETE /api/v1/chapters/{id}` - Delete chapter
- `GET /api/v1/chapters/{id}/versions` - Get version history

### References
- `GET /api/v1/references` - List all references
- `GET /api/v1/references/{id}` - Get reference details
- `POST /api/v1/references` - Add new reference
- `POST /api/v1/references/upload-pdf` - Upload and process PDF
- `GET /api/v1/references/search` - Search references

### Synthesis
- `POST /api/v1/synthesis/generate` - Generate synthesis from references
- `POST /api/v1/synthesis/compare` - Compare surgical techniques
- `POST /api/v1/synthesis/extract-concepts` - Extract key concepts

### Q&A
- `POST /api/v1/qa/ask` - Ask a question
- `POST /api/v1/qa/ask-with-refs` - Ask with specific references
- `GET /api/v1/qa/history` - Get Q&A history

## Setup & Installation

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Node.js 18+
- Docker & Docker Compose (optional)

### Environment Variables
Create `.env` file in backend directory:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://neurosurg:neurosurg123@localhost:5432/neurosurgical_knowledge

# AI Services (optional - will use mocks if not provided)
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here

# Application
DEBUG=True
```

### Backend Setup

```bash
cd backend
pip install -r requirements_simplified.txt
python test_system.py  # Run tests
uvicorn main_simplified:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Docker Setup (Simplified)

```bash
docker-compose -f docker-compose-simple.yml up -d
```

Services:
- `postgres`: PostgreSQL database
- `redis`: Redis cache
- `backend`: FastAPI application
- `frontend`: Next.js application

## AI Integration

The system supports multiple AI providers with graceful fallbacks:

### OpenAI (GPT-4)
- Comprehensive synthesis
- High-quality medical content
- Set `OPENAI_API_KEY` environment variable

### Anthropic (Claude)
- Alternative synthesis engine
- Long-context processing
- Set `ANTHROPIC_API_KEY` environment variable

### Google (Gemini)
- Additional AI option
- Free tier available
- Set `GOOGLE_API_KEY` environment variable

**Mock Mode**: If no API keys provided, system uses mock responses for development.

## Features

### 1. Chapter Management
- Create and organize neurosurgical chapters
- Version control for all changes
- Specialty-specific organization
- Full-text search

### 2. AI-Powered Synthesis
- Generate chapters from multiple references
- Compare surgical techniques
- Extract key medical concepts
- Evidence-based content generation

### 3. Reference Library
- Store and organize medical literature
- PDF processing and extraction
- Citation tracking
- PubMed integration (optional)

### 4. Question Answering
- Context-aware Q&A
- Reference-based answers
- Follow-up question suggestions
- Confidence scoring

### 5. Behavioral Learning
- Track usage patterns
- Anticipate information needs
- Personalized recommendations
- Learning preferences

## Testing

Run the comprehensive test suite:

```bash
python test_system.py
```

Tests cover:
- ✅ Database models import
- ✅ Service module instantiation
- ✅ Configuration loading
- ✅ FastAPI application initialization
- ✅ AI service mock responses

## Deployment

### Development
```bash
uvicorn main_simplified:app --reload --host 0.0.0.0 --port 8000
```

### Production
```bash
gunicorn main_simplified:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## File Structure Summary

### Essential Files
- `backend/main_simplified.py` - Main application
- `backend/models/database_simplified.py` - Database models
- `backend/config/settings_simplified.py` - Configuration
- `backend/requirements_simplified.txt` - Python dependencies
- `docker-compose-simple.yml` - Docker configuration
- `test_system.py` - Test suite

### Documentation
- `README.md` - Main documentation
- `SYSTEM_SIMPLIFIED.md` - This file

## Key Simplifications

1. **No Authentication**: Direct access to all features
2. **Single User**: All preferences and patterns for one user
3. **No HIPAA**: No confidential patient data handling
4. **Simplified Database**: Removed user tables, sessions, permissions
5. **Minimal Dependencies**: Only essential packages
6. **Mock AI Responses**: Works without API keys for development
7. **Streamlined Docker**: Only 4 services instead of 10+

## Performance

- **Async/Await**: Non-blocking I/O throughout
- **Connection Pooling**: Database connection reuse
- **Redis Caching**: Fast data retrieval
- **Lazy Loading**: Load resources as needed

## Next Steps

1. **Install Dependencies**: `pip install -r requirements_simplified.txt`
2. **Set up Database**: Create PostgreSQL database
3. **Configure Environment**: Add API keys to `.env`
4. **Run Tests**: `python test_system.py`
5. **Start Backend**: `uvicorn main_simplified:app --reload`
6. **Start Frontend**: `cd frontend && npm run dev`

## Support

For issues or questions about this simplified version:
1. Check `test_system.py` output for diagnostics
2. Review error logs
3. Verify environment variables
4. Check database connectivity

## License

MIT

---

**Version**: 2.0.0-simplified
**Last Updated**: 2025-09-30
**Status**: Production-ready for single-user deployment