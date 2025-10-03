# Enhanced API Documentation - NSEXP

## New Enhanced Services

### Image Extraction & Analysis

#### Extract Images from PDF
```
POST /api/v1/images/extract
```

Extract images from PDF files with OCR and automatic classification.

**Parameters:**
- `pdf_path` (string, required): Path to PDF file
- `output_dir` (string, optional): Directory to save extracted images
- `min_width` (int, default: 100): Minimum image width to extract
- `min_height` (int, default: 100): Minimum image height to extract
- `extract_text` (bool, default: true): Whether to perform OCR on images

**Response:**
```json
{
  "success": true,
  "pdf_path": "/path/to/file.pdf",
  "total_pages": 150,
  "images_extracted": 23,
  "images": [
    {
      "page_number": 1,
      "image_index": 1,
      "filename": "page1_img1.png",
      "path": "/output/page1_img1.png",
      "width": 800,
      "height": 600,
      "format": "png",
      "type": "medical_illustration",
      "extracted_text": "Figure 1: Brain anatomy",
      "size_bytes": 125000
    }
  ],
  "output_directory": "/output"
}
```

**Image Types:**
- `diagram_or_chart` - Simple diagrams with few colors
- `medical_illustration` - Anatomical illustrations
- `photograph_or_scan` - Complex medical images/scans
- `medical_image` - General medical imagery
- `unknown` - Unable to classify

#### Analyze Anatomical Image
```
POST /api/v1/images/analyze
```

Analyze anatomical/medical images using AI vision.

**Parameters:**
- `image_path` (string, required): Path to image file

**Response:**
```json
{
  "success": true,
  "image_path": "/path/to/image.png",
  "width": 800,
  "height": 600,
  "format": "PNG",
  "type": "medical_illustration",
  "labels": "Corpus callosum, ventricles",
  "ai_description": "Sagittal section showing brain anatomy",
  "identified_structures": ["corpus callosum", "ventricles", "brainstem"],
  "medical_relevance": "high"
}
```

---

### Comprehensive Synthesis

#### Synthesize Comprehensive Chapter
```
POST /api/v1/synthesis/comprehensive
```

Generate comprehensive neurosurgical chapter with full 150+ section structure.

**Parameters:**
- `topic` (string, required): Chapter topic (e.g., "Glioblastoma Multiforme")
- `specialty` (string, required): Neurosurgical specialty
- `references` (array, optional): List of reference materials
- `focus_areas` (array, optional): Specific sections to emphasize
- `include_images` (bool, default: true): Include image references

**Request Body:**
```json
{
  "topic": "Glioblastoma Multiforme",
  "specialty": "TUMOR",
  "references": [
    {
      "title": "WHO Classification of CNS Tumors",
      "authors": ["Louis DN", "Perry A"],
      "year": "2021",
      "content": "...",
      "doi": "10.1093/neuonc/noab106"
    }
  ],
  "focus_areas": ["Surgical Techniques", "Molecular Biology"],
  "include_images": true
}
```

**Response:**
```json
{
  "success": true,
  "topic": "Glioblastoma Multiforme",
  "specialty": "TUMOR",
  "sections": {
    "Introduction": "Glioblastoma multiforme (GBM) is...",
    "Epidemiology": "GBM accounts for 45% of...",
    "Surgical Techniques": "Complete surgical resection...",
    ...
  },
  "section_count": 87,
  "total_words": 25000,
  "references": [
    "1. Louis DN, Perry A (2021). WHO Classification..."
  ],
  "reference_count": 15,
  "images": [
    {
      "source": "WHO Classification",
      "caption": "Figure 2.3: Histological features",
      "page": "45"
    }
  ],
  "image_count": 12,
  "quality_metrics": {
    "completeness_score": 0.87,
    "total_words": 25000,
    "average_section_length": 287,
    "reference_density": 0.0006,
    "has_images": true,
    "image_count": 12,
    "estimated_reading_time_minutes": 125
  },
  "generated_at": "2024-01-15T10:30:00"
}
```

#### Generate Chapter Summary
```
POST /api/v1/synthesis/summary
```

Generate different types of summaries from chapter content.

**Parameters:**
- `chapter_content` (object, required): Full chapter content
- `summary_type` (string, default: "executive"): Type of summary

**Summary Types:**
- `executive` - Concise 200-300 word summary
- `detailed` - Comprehensive 600-800 word summary
- `technical` - Technical details 400-500 words
- `bullet_points` - 10-15 key bullet points

**Response:**
```json
{
  "success": true,
  "summary_type": "executive",
  "summary": "Glioblastoma multiforme is the most aggressive...",
  "word_count": 287
}
```

---

### Deep Literature Search

#### Search Medical Literature
```
POST /api/v1/search/deep
```

Deep search across multiple medical literature databases.

**Parameters:**
- `query` (string, required): Search query
- `sources` (array, optional): Sources to search ["pubmed", "scholar", "arxiv"]
- `max_results` (int, default: 20): Maximum results per source
- `filters` (object, optional): Additional filters

**Request Body:**
```json
{
  "query": "glioblastoma immunotherapy",
  "sources": ["pubmed", "arxiv"],
  "max_results": 20,
  "filters": {
    "year_min": 2020,
    "year_max": 2024
  }
}
```

**Response:**
```json
{
  "query": "glioblastoma immunotherapy",
  "sources_searched": ["pubmed", "arxiv"],
  "total_results": 35,
  "results": [
    {
      "source": "pubmed",
      "pmid": "34567890",
      "title": "CAR T-cell therapy for glioblastoma",
      "abstract": "Background: CAR T-cell therapy...",
      "authors": ["Smith J", "Johnson A"],
      "journal": "Neuro-Oncology",
      "year": "2023",
      "doi": "10.1093/neuonc/xyz123",
      "url": "https://pubmed.ncbi.nlm.nih.gov/34567890/",
      "relevance_score": 8.5
    }
  ],
  "search_metadata": {
    "timestamp": "2024-01-15T10:30:00",
    "filters_applied": {
      "year_min": 2020,
      "year_max": 2024
    }
  }
}
```

#### Enrich Reference Metadata
```
POST /api/v1/references/enrich
```

Enrich a reference with additional metadata from online databases.

**Request Body:**
```json
{
  "title": "WHO Classification of CNS Tumors",
  "authors": ["Louis DN"]
}
```

**Response:**
```json
{
  "title": "WHO Classification of CNS Tumors",
  "authors": ["Louis DN", "Perry A"],
  "doi": "10.1093/neuonc/noab106",
  "pmid": "34567890",
  "url": "https://pubmed.ncbi.nlm.nih.gov/34567890/",
  "abstract": "The updated WHO classification..."
}
```

---

### Advanced PDF Processing

#### Process PDF Advanced
```
POST /api/v1/pdf/process-advanced
```

Advanced PDF processing with PyMuPDF including image and table extraction.

**Parameters:**
- `pdf_path` (string, required): Path to PDF file
- `extract_images` (bool, default: false): Extract embedded images
- `extract_tables` (bool, default: false): Extract tables

**Response:**
```json
{
  "text": "Full text content...",
  "page_count": 150,
  "title": "Principles of Neurosurgery",
  "authors": ["Greenberg MS"],
  "metadata": {
    "subject": "Neurosurgery",
    "creator": "Adobe InDesign",
    "producer": "Adobe PDF Library",
    "creation_date": "2023-01-01",
    "keywords": "neurosurgery, brain, spine"
  },
  "page_details": [
    {
      "page_number": 1,
      "width": 612,
      "height": 792,
      "word_count": 450,
      "has_images": true
    }
  ],
  "extraction_method": "PyMuPDF",
  "images": [
    {
      "page": 5,
      "index": 1,
      "width": 800,
      "height": 600,
      "format": "png",
      "size_bytes": 125000
    }
  ],
  "image_count": 23,
  "tables": [
    {
      "page": 10,
      "table_count": 2,
      "note": "Table detection is basic - enhancement recommended"
    }
  ],
  "table_count": 5
}
```

#### Chunk PDF Content
```
POST /api/v1/pdf/chunk
```

Chunk PDF content for processing with AI models (token limit management).

**Parameters:**
- `pdf_path` (string, required): Path to PDF file
- `chunk_size` (int, default: 1000): Characters per chunk
- `overlap` (int, default: 200): Overlap between chunks

**Response:**
```json
{
  "success": true,
  "chunks": [
    {
      "chunk_number": 1,
      "text": "Chapter 1: Introduction...",
      "start_char": 0,
      "end_char": 1000,
      "length": 1000
    },
    {
      "chunk_number": 2,
      "text": "...continuation of text...",
      "start_char": 800,
      "end_char": 1800,
      "length": 1000
    }
  ],
  "chunk_count": 156
}
```

---

## Updated Endpoint Count

Total API endpoints: **46** (previously 38)

**New Endpoints:** 8
- Image extraction: 2
- Comprehensive synthesis: 2
- Deep search: 2
- Advanced PDF: 2

---

## Error Responses

All endpoints return consistent error responses:

```json
{
  "error": "Error message",
  "details": "Detailed error information"
}
```

**HTTP Status Codes:**
- `200` - Success
- `400` - Bad request (invalid parameters)
- `404` - Resource not found
- `500` - Internal server error

---

## Rate Limiting

**PubMed Search:**
- Without API key: 3 requests/second
- With API key: 10 requests/second

**AI Services:**
- Depends on provider limits
- Automatic fallback to mock responses if limits exceeded

---

## Authentication

Current version: Single-user, no authentication required.

Future versions will include JWT authentication for multi-user deployments.

---

## Testing Endpoints

Use the interactive API documentation:
```
http://localhost:8000/api/docs
```

Or with curl:
```bash
# Test image extraction
curl -X POST "http://localhost:8000/api/v1/images/extract" \
  -H "Content-Type: application/json" \
  -d '{"pdf_path": "/textbooks/sample.pdf"}'

# Test deep search
curl -X POST "http://localhost:8000/api/v1/search/deep" \
  -H "Content-Type: application/json" \
  -d '{"query": "glioblastoma treatment", "sources": ["pubmed"]}'
```
