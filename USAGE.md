# 🎯 Usage Guide - Neurosurgical Knowledge Management System

Complete guide to using all features of the Neurosurgical Knowledge Management System.

## Table of Contents
1. [Getting Started](#getting-started)
2. [Chapter Management](#chapter-management)
3. [AI Synthesis](#ai-synthesis)
4. [Q&A System](#qa-system)
5. [Search](#search)
6. [Reference Library](#reference-library)
7. [API Usage](#api-usage)

## Getting Started

### Access the Application
After starting the system (see [QUICKSTART.md](QUICKSTART.md)):
- **Frontend UI**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs

### System Status
The system works in two modes:
- **Full Mode**: With database and AI API keys configured
- **Mock Mode**: Without database/API keys (perfect for testing)

Check system status:
```bash
curl http://localhost:8000/health
```

## Chapter Management

### View All Chapters
**Web UI**: Navigate to http://localhost:3000/library

**API**:
```bash
curl "http://localhost:8000/api/v1/chapters?limit=10"
```

Response:
```json
{
  "success": true,
  "data": {
    "chapters": [
      {
        "id": "1",
        "title": "Glioblastoma Management",
        "specialty": "tumor",
        "summary": "Comprehensive guide...",
        "status": "published",
        "created_at": "2024-01-15T10:00:00"
      }
    ],
    "total": 3
  }
}
```

### Get Specific Chapter
```bash
curl "http://localhost:8000/api/v1/chapters/1"
```

### Create New Chapter
**Web UI**: Click "New Chapter" button in Library

**API**:
```bash
curl -X POST "http://localhost:8000/api/v1/chapters" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Craniotomy Techniques",
    "specialty": "general",
    "content": "# Craniotomy\n\n..."
  }'
```

### Filter by Specialty
```bash
curl "http://localhost:8000/api/v1/chapters?specialty=tumor&limit=5"
```

Available specialties:
- `tumor` - Brain tumors
- `vascular` - Vascular neurosurgery
- `spine` - Spine surgery
- `functional` - Functional neurosurgery
- `pediatric` - Pediatric cases
- `trauma` - Neurotrauma
- `skull_base` - Skull base surgery

## AI Synthesis

### Generate a Chapter
**Web UI**: 
1. Go to http://localhost:3000/synthesis
2. Enter topic (e.g., "Glioblastoma Management")
3. Select specialty
4. Click "Generate Chapter"

**API**:
```bash
curl -X POST "http://localhost:8000/api/v1/synthesis/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Aneurysm Clipping Techniques",
    "specialty": "vascular",
    "max_sources": 15
  }'
```

### Example Topics
- "Grade IV Glioblastoma: Diagnosis and Treatment"
- "Microsurgical Techniques for Cerebral Aneurysms"
- "Lumbar Disc Herniation: Surgical Approaches"
- "Deep Brain Stimulation for Parkinson Disease"
- "Pediatric Medulloblastoma Management"
- "Traumatic Brain Injury: Initial Management"
- "Trigeminal Neuralgia: Microvascular Decompression"

### Synthesis Output
The AI generates:
- Structured chapter with sections
- Evidence-based content
- Citations and references
- Clinical implications
- Key takeaways

## Q&A System

### Ask a Question
**Web UI**: 
1. Go to http://localhost:3000/qa
2. Type your question
3. Click "Ask Question"

**API**:
```bash
curl -X POST "http://localhost:8000/api/v1/qa/ask?question=What+are+the+indications+for+craniotomy"
```

Response:
```json
{
  "success": true,
  "data": {
    "question": "What are the indications for craniotomy",
    "answer": "Craniotomy is indicated for...",
    "confidence": 0.85,
    "sources": [],
    "model": "gpt-4",
    "answered_at": "2024-01-15T10:30:00"
  }
}
```

### Example Questions
- "What are the indications for craniotomy?"
- "Explain the Stupp protocol for glioblastoma"
- "What is the Glasgow Coma Scale?"
- "Describe the circle of Willis anatomy"
- "What are the surgical approaches to the posterior fossa?"
- "How do you manage increased intracranial pressure?"

### With Context
Add specific chapter context:
```bash
curl -X POST "http://localhost:8000/api/v1/qa/ask?question=What+is+the+prognosis&chapter_id=1"
```

## Search

### Basic Search
**Web UI**: 
1. Go to http://localhost:3000/search
2. Enter search query
3. View results

**API**:
```bash
curl "http://localhost:8000/api/v1/search?query=glioblastoma&limit=10"
```

### Search Types
```bash
# Search everything
curl "http://localhost:8000/api/v1/search?query=aneurysm&search_type=all"

# Search only chapters
curl "http://localhost:8000/api/v1/search?query=spine&search_type=chapters"

# Search references
curl "http://localhost:8000/api/v1/search?query=treatment&search_type=references"

# Search procedures
curl "http://localhost:8000/api/v1/search?query=craniotomy&search_type=procedures"
```

### Semantic Search
Uses AI embeddings for better results:
```bash
curl -X POST "http://localhost:8000/api/v1/search/semantic" \
  -H "Content-Type: application/json" \
  -d '{"query": "brain tumor surgery", "limit": 5}'
```

## Reference Library

### List References
```bash
curl "http://localhost:8000/api/v1/references?limit=20"
```

### Add Reference
```bash
curl -X POST "http://localhost:8000/api/v1/references" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Glioblastoma: State of the Art",
    "authors": "Smith J, Doe A",
    "journal": "J Neurosurg",
    "year": 2024,
    "doi": "10.1000/example",
    "abstract": "..."
  }'
```

### Get Specific Reference
```bash
curl "http://localhost:8000/api/v1/references/1"
```

## API Usage

### Interactive API Docs
The best way to explore the API:
1. Open http://localhost:8000/api/docs
2. Browse available endpoints
3. Try them out interactively
4. See request/response examples

### Authentication
The simplified version doesn't require authentication.
All endpoints are publicly accessible.

### Rate Limiting
- No rate limits in development
- Production: Configure in docker-compose.yml

### Response Format
All API responses follow this format:
```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "message": "Optional message"
}
```

Error responses:
```json
{
  "success": false,
  "error": "Error description",
  "data": null
}
```

## Advanced Features

### Check Available AI Models
```bash
curl "http://localhost:8000/health"
```

### System Statistics
View in the home page or via API:
```bash
curl "http://localhost:8000/api/v1/chapters?limit=0"
```

### Export Chapter
Get chapter in different formats:
```bash
# Get as JSON
curl "http://localhost:8000/api/v1/chapters/1"

# Get as Markdown (in content field)
curl "http://localhost:8000/api/v1/chapters/1" | jq -r '.data.content'
```

## Tips & Best Practices

### 1. Start with Mock Mode
- Test the system without API keys
- Understand the workflows
- Configure API keys when ready for production

### 2. Organize by Specialty
- Use specialty tags consistently
- Filter chapters by specialty
- Create specialty-specific collections

### 3. Leverage AI Synthesis
- Be specific with topics
- Provide context when available
- Review and edit generated content

### 4. Use Contextual Q&A
- Reference specific chapters
- Build on previous answers
- Save important Q&A sessions

### 5. Build Your Knowledge Base
- Add chapters regularly
- Keep references organized
- Update content periodically

## Troubleshooting

### API Returns Mock Data
**Reason**: Database not connected or no API keys configured
**Solution**: This is expected in mock mode. Configure database and API keys for full functionality.

### Synthesis Takes Long Time
**Normal**: AI synthesis can take 30-60 seconds
**Tip**: Start with smaller, specific topics

### Search Returns No Results
**Check**: 
1. Database has content
2. Search query spelling
3. Try broader search terms

### Frontend Can't Connect to Backend
**Fix**:
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check frontend env: `NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1`
3. Restart both services

## Next Steps

1. **Add Real Content**: Import your medical textbooks and papers
2. **Configure AI**: Add API keys for real AI synthesis
3. **Customize**: Modify specialties and procedures for your needs
4. **Deploy**: Use DEPLOYMENT.md to deploy to production
5. **Backup**: Regularly export your chapters and references

## Support & Resources

- **Documentation**: See README.md, DEPLOYMENT.md, QUICKSTART.md
- **API Reference**: http://localhost:8000/api/docs
- **System Test**: `python test_system.py`
- **Logs**: Check backend console output
- **Issues**: https://github.com/ramihatou97/NNP/issues

---

**Happy Learning! 🧠**

The Neurosurgical Knowledge Management System is designed to be your personal medical knowledge companion.
