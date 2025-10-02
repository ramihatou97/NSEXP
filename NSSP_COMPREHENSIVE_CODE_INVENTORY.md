# NSSP - Neurosurgical Knowledge System
## Ultracomprehensive Algorithm and Function Inventory

**Generated:** 2025-10-01
**Version:** 2.1.0-optimized
**Project:** Neurosurgical Synthesis Platform (NSSP)

---

## Table of Contents
1. [System Overview](#system-overview)
2. [Backend Services & Algorithms](#backend-services--algorithms)
3. [Frontend Components & Functions](#frontend-components--functions)
4. [Alive Chapter System](#alive-chapter-system)
5. [Core Infrastructure](#core-infrastructure)
6. [Utilities & Helpers](#utilities--helpers)
7. [Database Models & Schemas](#database-models--schemas)
8. [Middleware & API Layer](#middleware--api-layer)

---

## System Overview

### Architecture
- **Backend**: Python (FastAPI) - Async/Await architecture
- **Frontend**: Next.js 14+ (React, TypeScript)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **AI Integration**: OpenAI, Anthropic Claude, Google Gemini, Perplexity
- **Special Features**: Alive Chapter System (Q&A, Behavioral Learning, Citations)

---

## Backend Services & Algorithms

### 1. AI Service Manager (`backend/services/ai_manager.py`)
**Purpose**: Multi-provider AI orchestration with medical specialization

#### Core Classes

##### `AIServiceManager`
**Purpose**: Central manager for all AI providers
- **Functions**:
  - `initialize_providers()` - Initialize OpenAI, Anthropic, Google, Perplexity clients
  - `generate_neurosurgical_content(prompt, context, specialty, preferred_provider, max_tokens, temperature)` - Generate medical content with provider fallback
  - `validate_medical_content(content, specialty)` - Validate medical accuracy
  - `synthesize_chapter_section(section_name, references, specialty)` - Generate chapter sections
  - `get_embeddings(text, model)` - Generate text embeddings for semantic search
- **Algorithm**: Provider fallback chain - tries preferred provider first, falls back to others on failure

##### `OpenAIService`
- **Functions**:
  - `query(prompt, max_tokens, temperature)` - Query OpenAI API
  - `get_embeddings(text, model)` - Generate embeddings
- **Pricing Calculation**: Dynamic cost tracking per model (GPT-4: $0.03/$0.06, GPT-3.5: $0.0005/$0.0015)

##### `AnthropicService`
- **Functions**:
  - `query(prompt, max_tokens, temperature)` - Query Claude API
- **Models Supported**: Claude 3 Opus, Sonnet, Haiku

##### `GeminiService`
- **Functions**:
  - `query(prompt, max_tokens, temperature)` - Query Gemini API
- **Special**: Runs synchronous API in executor for async compatibility

##### `PerplexityService`
- **Functions**:
  - `query(prompt, max_tokens, temperature)` - Query Perplexity for web-grounded responses
- **Special**: HTTP-based API via httpx

##### `MedicalPromptTemplates`
- **Functions**:
  - `enhance_prompt(prompt, context, specialty)` - Add medical context and requirements
  - `get_validation_prompt(content, specialty)` - Generate validation prompts
  - `get_synthesis_prompt(section, references, specialty)` - Generate synthesis prompts
- **Algorithm**: Template-based prompt engineering with medical guidelines

##### `UsageTracker`
- **Functions**:
  - `track_usage(provider, tokens, cost)` - Track AI usage statistics
  - `get_usage_report()` - Generate usage reports
  - `reset_usage()` - Reset tracking counters

---

### 2. Q&A Service (`backend/services/qa_service.py`)
**Purpose**: Question-answering with neurosurgical context

#### Core Functions
- `answer_question(question, context, specialty, model)` - Answer medical questions
- `answer_with_references(question, references, specialty)` - Answer using specific references
- `generate_follow_up_questions(original_question, answer, count)` - Generate contextual follow-ups
- `validate_answer(question, answer, references)` - Validate answer accuracy

**Algorithm**: Context-aware Q&A with evidence-based responses

---

### 3. Synthesis Service (`backend/services/synthesis_service.py`)
**Purpose**: AI-powered content synthesis from multiple sources

#### Core Functions
- `synthesize_content(references, topic, specialty, focus_areas)` - Synthesize from references
- `compare_techniques(technique_a, technique_b, specialty)` - Compare surgical techniques
- `extract_key_concepts(content, specialty)` - Extract medical concepts
- `generate_summary(content, max_length)` - Generate concise summaries

**Algorithm**: Multi-reference synthesis with coherence optimization

---

### 4. PDF Service (`backend/services/pdf_service.py`)
**Purpose**: PDF extraction for medical literature

#### `PDFProcessor`
- **Functions**:
  - `process_pdf(pdf_path)` - Extract text and metadata from PDF
  - `process_pdf_bytes(pdf_bytes)` - Process PDF from memory
  - `extract_sections(text)` - Extract common paper sections (abstract, methods, results, etc.)
- **Library**: PyPDF2

---

### 5. Search Service (`backend/services/search_service.py`)
**Purpose**: Multi-modal search across content

#### Core Functions
- `search_all_content(query, search_type, limit)` - Search chapters, references, procedures
- `semantic_search_content(query, limit)` - Semantic search using embeddings
- `_search_chapters(session, query, limit)` - Chapter-specific search
- `_search_references(session, query, limit)` - Reference search
- `_search_procedures(session, query, limit)` - Surgical procedure search

**Algorithm**: Hybrid search (text + semantic) with relevance scoring

---

### 6. Reference Service (`backend/services/reference_service.py`)
**Purpose**: Reference and citation management

#### `ReferenceService`
- **Functions**:
  - `get_all_references(specialty, source_type, limit)` - Retrieve references
  - `get_reference(reference_id)` - Get single reference
  - `create_reference(reference_data)` - Create new reference
  - `process_pdf_reference(pdf_path, metadata)` - Extract reference from PDF
  - `update_reference(reference_id, updates)` - Update reference
  - `delete_reference(reference_id)` - Delete reference
  - `search_references(query, specialty, limit)` - Search references
  - `create_citation(chapter_id, reference_id, context, location)` - Link chapter to reference
  - `get_chapter_citations(chapter_id)` - Get all citations for chapter

---

### 7. Chapter Service (`backend/services/chapter_service.py`)
**Purpose**: Chapter CRUD operations (simplified, mock-capable)

#### Core Functions
- `get_all_chapters(specialty, status, limit)` - Retrieve chapters
- `get_chapter_by_id(chapter_id)` - Get specific chapter
- `create_new_chapter(chapter_data, background_tasks)` - Create chapter
- `update_existing_chapter(chapter_id, chapter_data)` - Update chapter
- `delete_chapter_by_id(chapter_id)` - Delete chapter

**Special**: Can run without database (mock mode)

---

## Alive Chapter System

### 1. Chapter Q&A Engine (`alive chapter/chapter_qa_engine.py`)
**Purpose**: Intelligent Q&A with automatic integration into chapters

#### Core Classes & Algorithms

##### `QuestionAnalyzer`
- **Functions**:
  - `analyze_question(question, chapter_content, section_context)` - Full question analysis
  - `_detect_question_type(question)` - Classify question type (definition, explanation, comparison, etc.)
  - `_extract_medical_concepts(question)` - Extract medical concepts
  - `_assess_urgency(question, context)` - Calculate urgency (1-5 scale)
- **Algorithm**: Pattern matching + medical ontology lookup

##### `MultiSourceSearcher`
- **Functions**:
  - `search_all_sources(question_context, max_results)` - Parallel multi-source search
  - `_search_pubmed(context)` - Search PubMed
  - `_search_semantic_scholar(context)` - Search Semantic Scholar
  - `_search_knowledge_graph(context)` - Search internal knowledge
  - `_search_perplexity(context)` - Search Perplexity AI
  - `_search_local_knowledge(context)` - Search local chapters
  - `_score_and_rank_results(results, context)` - Rank by relevance + credibility
- **Algorithm**:
  1. Parallel search across all sources (asyncio.gather)
  2. Semantic similarity scoring (sentence transformers)
  3. Credibility weighting (gold standard: 1.0, high: 0.9, moderate: 0.7)
  4. Combined scoring: relevance_score × credibility_weight

##### `CredibilityScorer`
- **Function**: `score_credibility(source)` - Assign credibility level
- **Hierarchy**:
  - Gold Standard: Systematic reviews, clinical guidelines, Cochrane
  - High: RCTs, meta-analyses
  - Moderate: Cohort studies, case-control
  - Low: Case reports, expert opinion

##### `AnswerSynthesizer`
- **Functions**:
  - `synthesize_answer(search_results, question_context)` - Create comprehensive answer
  - `_extract_evidence_points(results)` - Extract key findings
  - `_generate_main_answer(context, evidence, resolved_conflicts)` - Generate answer text
  - `_determine_integration_strategy(context, answer)` - Choose integration method
  - `_calculate_confidence(evidence, conflicts)` - Calculate confidence score
- **Algorithm**: Evidence aggregation → conflict resolution → confidence scoring

##### `ConflictResolver`
- **Functions**:
  - `detect_conflicts(evidence_points)` - Find contradictory evidence
  - `resolve_conflicts(conflicts)` - Resolve using credibility + recency
  - `_are_conflicting(point1, point2)` - Check for contradictions
- **Algorithm**: Contradiction detection via opposing term pairs (effective/ineffective, increases/decreases)

##### `ContentIntegrator`
- **Functions**:
  - `integrate_answer(chapter_content, synthesized_answer, question_context)` - Integrate into chapter
  - `_inline_expansion(content, answer, section_context)` - Expand inline
  - `_footnote_addition(content, answer, section_context)` - Add as footnote
  - `_section_creation(content, answer, section_context)` - Create new section
  - `_parenthetical_insert(content, answer, section_context)` - Insert parenthetically
  - `_sidebar_note(content, answer, section_context)` - Add sidebar note
  - `_appendix_addition(content, answer, section_context)` - Add to appendix
  - `_add_citations(content, citations, integration_points)` - Add citation markers
- **Integration Strategies**:
  - Short (<200 chars): Inline expansion
  - Medium (200-500 chars): Footnote or parenthetical
  - Long (>500 chars): Section creation or sidebar

##### `ChapterQAEngine` (Main Engine)
- **Function**: `process_in_chapter_question(question, chapter_id, chapter_content, section_context, user_id)`
- **Complete Algorithm**:
  1. Analyze question (type, concepts, urgency)
  2. Search all sources in parallel
  3. Synthesize answer from results
  4. Integrate into chapter
  5. Track performance metrics
  6. Store in Q&A history
- **Performance**: Tracks avg processing time with exponential moving average

---

### 2. Behavioral Learning Engine (`alive chapter/chapter_behavioral_learning.py`)
**Purpose**: Learn from user interactions and anticipate knowledge needs

#### Core Classes & Algorithms

##### `InteractionMemory`
- **Functions**:
  - `store_interaction(interaction)` - Store with intelligent indexing
  - `get_interaction_patterns(chapter_id, lookback_hours)` - Extract patterns
  - `_extract_patterns(interactions)` - Pattern extraction
  - `_predict_next_actions(sequence, interactions)` - Predict next user actions
- **Algorithm**:
  - Temporal sequence analysis (Markov-chain style)
  - Minimum frequency threshold (3 occurrences)
  - Confidence = min(0.9, count / 10)

##### `KnowledgeGapDetector`
- **Functions**:
  - `detect_gaps(chapter_content, interaction_context)` - Detect missing knowledge
  - `_analyze_content_completeness(content)` - Check essential sections
  - `_analyze_user_questions(questions, content)` - Gaps from questions
  - `_analyze_concept_coverage(content)` - Check medical concept coverage
  - `_analyze_research_currency(content)` - Check for recent research
- **Algorithm**:
  1. Essential section check (epidemiology, pathophysiology, treatment, etc.)
  2. User question mapping to gap types
  3. Medical concept completeness analysis
  4. Temporal analysis (research within 2 years)

##### `AnticipationEngine`
- **Functions**:
  - `anticipate_needs(chapter_context, user_patterns, knowledge_gaps)` - Predict future needs
  - `_anticipate_from_patterns(patterns, context)` - Pattern-based anticipation
  - `_anticipate_from_gaps(gaps, context)` - Gap-based anticipation
  - `_anticipate_from_temporal_context(context)` - Time-of-day patterns
  - `_anticipate_from_content_progression(context)` - Section progression patterns
- **Algorithm**:
  - Pattern prediction (action probability > 0.5)
  - Gap auto-fill threshold (priority > 0.7)
  - Temporal patterns (9-11am: research, 2-5pm: writing)
  - Content progression map (intro → epidemiology → pathophysiology → diagnosis → treatment)

##### `ChapterBehavioralLearningEngine` (Main Engine)
- **Functions**:
  - `learn_from_interaction(interaction_data)` - Learn from single interaction
  - `anticipate_knowledge_needs(chapter_context)` - Full anticipation pipeline
  - `get_proactive_suggestions(chapter_id, user_id)` - Generate suggestions
- **Background Workers**:
  - `_background_prefetch_worker()` - Prefetch anticipated content
  - `_pattern_analysis_worker()` - Continuous pattern analysis (5-minute intervals)

---

### 3. Citation Network Engine (`alive chapter/citation_network_engine.py`)
**Purpose**: Build and maintain citation networks across chapters

#### Core Classes & Algorithms

##### `ReferenceIndex`
- **Functions**:
  - `add_reference(reference)` - Add to searchable index
  - `search_references(query, limit)` - Semantic + concept search
  - `get_chapter_references(chapter_id)` - Get all references from chapter
  - `get_concept_references(concept)` - Get references by medical concept
- **Algorithm**:
  - Multi-index: chapter_id, concept, external_resource
  - Embedding-based semantic search
  - TF-IDF vectorization

##### `CrossReferenceDetector`
- **Functions**:
  - `detect_cross_references(source_chapter, all_chapters)` - Find cross-references
  - `_find_overlapping_concepts(source_concepts, target_concepts)` - Find overlaps
  - `_calculate_concept_similarity(concept1, concept2)` - Semantic similarity
  - `_detect_external_references(content)` - Detect DOI, PMID, guidelines
- **Algorithm**:
  1. Extract concepts from source and targets
  2. Find overlapping concepts
  3. Calculate relevance (concept_score × 0.6 + text_similarity × 0.4)
  4. Threshold filtering (relevance > 0.3)
  5. Pattern matching for external refs (DOI: `10\.\d{4,}/...`, PMID: `PMID:?\s*(\d+)`)

##### `CitationSuggester`
- **Functions**:
  - `suggest_citations(current_context, available_resources, citation_history)` - Suggest relevant citations
  - `_generate_citation_text(resource)` - Generate citation format
  - `_find_insertion_point(context, resource)` - Find best position for citation
  - `_filter_by_history(suggestions, citation_history)` - Avoid over-citation
- **Algorithm**:
  - Context analysis for evidence needs
  - Resource scoring (evidence type + concept overlap + recency + quality)
  - Insertion point: sentence with max concept matches
  - History filtering: exclude recently cited (within 1 hour) unless highly relevant (>0.9)

##### `CitationNetworkVisualizer`
- **Functions**:
  - `visualize_network(citations, chapters)` - Create visualization data
  - `_calculate_layout(nodes, edges)` - Calculate node positions
  - `_calculate_network_metrics(nodes, edges)` - Network analysis
- **Algorithm**:
  - Layout: Circular (2πi/n spacing)
  - Metrics: NetworkX graph analysis (density, centrality, clustering)

##### `CitationNetworkEngine` (Main Engine)
- **Functions**:
  - `build_citation_network(all_chapters)` - Build complete network
  - `detect_cross_references(chapter_content, chapter_id)` - Detect refs for chapter
  - `suggest_citations(current_context, chapter_id)` - Suggest citations
  - `visualize_citation_network(chapter_id)` - Create network visualization
  - `get_citation_statistics(chapter_id)` - Calculate citation stats

---

### 4. Enhanced Nuance Merge Engine (`alive chapter/enhanced_nuance_merge_engine.py`)
**Purpose**: Intelligent content merging with behavioral learning

#### Core Functions
- `intelligent_knowledge_integration(chapter_content, new_knowledge, chapter_id, user_id, integration_context)` - Full integration pipeline
- `merge_qa_answer(chapter_content, qa_answer, chapter_id, user_id)` - Merge Q&A answers
- `merge_anticipated_knowledge(chapter_content, anticipated_needs, chapter_id, user_id)` - Merge anticipated content
- `apply_citation_network(chapter_content, chapter_id, all_chapters)` - Apply citations

**Integration Algorithm**:
1. Learn from interaction (behavioral tracking)
2. Get user preferences (merge strategy, thresholds)
3. Detect nuances (original vs new)
4. Analyze integration points
5. Detect conflicts
6. Resolve conflicts (prefer quality/recent/manual)
7. Apply behavioral insights
8. Perform intelligent merge
9. Add citations and references
10. Track merge pattern for learning

**User Preferences**:
- Merge strategies: conservative, balanced, aggressive
- Auto-apply thresholds: 0.75-0.90
- Conflict resolution: prefer_quality, prefer_recent, manual

---

### 5. Enhanced Chapters API (`alive chapter/enhanced_chapters_alive_api.py`)
**Purpose**: FastAPI endpoints for alive chapter features

#### Endpoints

**Q&A Endpoints**:
- `POST /api/v1/alive-chapters/ask` - Ask question in chapter context
  - Processes question through Q&A engine
  - Auto-integrates answer if confidence > threshold
  - Tracks interaction for learning

**Behavioral Learning Endpoints**:
- `POST /api/v1/alive-chapters/learn` - Learn from interaction
- `POST /api/v1/alive-chapters/anticipate` - Anticipate knowledge needs
  - Returns anticipated needs + knowledge gaps
  - Starts background prefetching
  - Optionally auto-fills high-confidence gaps
- `GET /api/v1/alive-chapters/suggestions/{chapter_id}` - Get proactive suggestions

**Citation Network Endpoints**:
- `POST /api/v1/alive-chapters/citations` - Manage citations
  - Operations: detect, suggest, visualize, apply
- `GET /api/v1/alive-chapters/citations/stats/{chapter_id}` - Citation statistics

**Intelligent Merge Endpoints**:
- `POST /api/v1/alive-chapters/merge` - Intelligent merge
  - Integrates new knowledge with nuance analysis
  - Updates citation network in background

**Chapter Health Endpoints**:
- `GET /api/v1/alive-chapters/health/{chapter_id}` - Comprehensive health metrics
  - Q&A activity, citation health, behavioral insights
  - Overall health score (0-1)

**Composite Endpoints**:
- `POST /api/v1/alive-chapters/evolve/{chapter_id}` - Complete chapter evolution
  - Algorithm:
    1. Anticipate needs
    2. Fill top 3 knowledge gaps (confidence > 0.7)
    3. Apply citations
    4. Calculate evolution metrics

---

## Core Infrastructure

### 1. Database Configuration (`backend/core/database_simplified.py`)

#### Core Components
- **Engine**: SQLAlchemy async engine with connection pooling (10 connections, 20 overflow)
- **Session**: Async session maker with auto-commit/rollback
- **Functions**:
  - `get_db()` - Get database session with transaction management
  - `init_db()` - Initialize all database tables

---

### 2. Database Models (`backend/models/database_simplified.py`)

#### Medical Enums
- `NeurosurgicalSpecialty`: tumor, vascular, spine, functional, pediatric, trauma, peripheral_nerve, skull_base, endoscopic, stereotactic
- `ProcedureType`: craniotomy, craniectomy, laminectomy, fusion, shunt, endoscopy, stereotactic_biopsy, radiosurgery, aneurysm_clipping, etc.
- `AnatomicalRegion`: frontal, parietal, temporal, occipital, cerebellum, brainstem, pituitary, ventricles, spinal regions

#### Core Models

##### `Textbook`
- **Fields**: title, authors, isbn, edition, publisher, publication_year, specialty, file_path, total_pages
- **Status**: is_processed, processing_completed_at, processing_error
- **Search**: Full-text search vector (TSVECTOR + GIN index)

##### `Chapter`
- **Fields**: title, topic, specialty, content (JSONB), surgical_anatomy, surgical_technique, complications_avoidance
- **Medical Codes**: icd10_codes, cpt_codes
- **Version Control**: version, parent_chapter_id
- **Quality**: completeness_score, medical_accuracy_score, evidence_level
- **AI Enhancement**: ai_enhanced, knowledge_gaps (JSONB)
- **Relationships**: references (many-to-many), procedures (many-to-many), qa_sessions

##### `SurgicalProcedure`
- **Fields**: name, procedure_type, cpt_code, anatomical_region, approach
- **Details**: average_duration_minutes, positioning, required_equipment (array)
- **Steps**: procedure_steps (JSONB), common_complications (array)

##### `Reference`
- **Fields**: title, authors (array), journal, year, doi (unique), pmid (unique)
- **Content**: abstract, key_findings (JSONB), evidence_level

##### `QASession`
- **Fields**: question, question_context, question_type, answer, answer_sources (JSONB)
- **Quality**: confidence_score, integrated_into_chapter

##### `BehavioralPattern`
- **Fields**: pattern_type, pattern_data (JSONB), frequency, last_occurrence
- **Purpose**: Store user behavioral patterns for learning

##### `CitationNetwork`
- **Fields**: source_chapter_id, target_chapter_id, citation_type, citation_strength

##### `KnowledgeGap`
- **Fields**: gap_type, description, confidence, auto_filled, filled_at

---

### 3. Main Application (`backend/main_simplified.py`)

#### FastAPI Application
- **Lifecycle**: Async context manager for startup/shutdown
- **Middleware**:
  - `VersionMiddleware` - API version validation
  - `LoggingMiddleware` - Request/response logging
  - `CORSMiddleware` - CORS configuration

#### Endpoint Categories (40+ endpoints)

**Chapter Endpoints** (8):
- GET/POST/PUT/DELETE `/api/v1/chapters`
- CRUD operations for chapters

**Reference Endpoints** (6):
- GET/POST/PUT/DELETE `/api/v1/references`
- Reference management

**Synthesis Endpoints** (2):
- POST `/api/v1/synthesis/generate` - Generate synthesized chapter
- GET `/api/v1/synthesis/status/{job_id}` - Get synthesis status

**Search Endpoints** (2):
- GET `/api/v1/search` - Search all content
- POST `/api/v1/search/semantic` - Semantic search

**Q&A Endpoints** (2):
- POST `/api/v1/qa/ask` - Ask question
- GET `/api/v1/qa/history` - Q&A history

**Citation Endpoints** (2):
- GET `/api/v1/citations/network/{chapter_id}` - Citation network
- POST `/api/v1/citations/suggest` - Suggest citations

**Neurosurgery-Specific** (3):
- GET `/api/v1/procedures` - Get surgical procedures
- GET `/api/v1/procedures/{procedure_id}` - Procedure details
- POST `/api/v1/medical/validate` - Validate medical accuracy

**Textbook/PDF** (2):
- POST `/api/v1/textbooks/upload` - Upload and process textbook
- GET `/api/v1/textbooks` - Get all textbooks

**Knowledge Gaps** (2):
- GET `/api/v1/gaps/{chapter_id}` - Get knowledge gaps
- POST `/api/v1/gaps/{gap_id}/fill` - Auto-fill gap

**Export/Import** (2):
- GET `/api/v1/export/{chapter_id}` - Export chapter
- POST `/api/v1/import` - Import content

**WebSocket**:
- `/ws` - Real-time synthesis updates

---

## Utilities & Helpers

### 1. Logger (`backend/utils/logger.py`)

#### Classes

##### `StructuredFormatter`
- **Function**: `format(record)` - Format logs as JSON
- **Output**: Timestamp, level, logger, message, module, function, line, exception info
- **Extra Fields**: request_id, user_id, endpoint, duration_ms

##### `ConsoleFormatter`
- **Function**: `format(record)` - Human-readable with colors
- **Colors**: DEBUG (cyan), INFO (green), WARNING (yellow), ERROR (red), CRITICAL (magenta)

#### Functions
- `setup_logging(log_level, log_file, json_logs, rotate_logs, max_bytes, backup_count)` - Configure logging
- `get_logger(name)` - Get child logger
- `log_with_context(logger, level, message, **context)` - Log with additional context

**Features**:
- Rotating file handler (10MB max, 7 backups)
- Separate error log file
- JSON format for machine parsing
- Console format for human reading

---

### 2. Performance Metrics (`backend/utils/metrics.py`)

#### `MetricData`
- **Fields**: count, total_duration, min_duration, max_duration, recent_values (deque)
- **Properties**:
  - `avg_duration` - Average duration
  - `p95_duration` - 95th percentile (from sorted recent values)

#### `PerformanceMetrics`
- **Functions**:
  - `record_api_call(endpoint, duration_ms)` - Record API call
  - `record_ai_call(provider, duration_ms)` - Record AI service call
  - `get_api_stats()` - Get API endpoint statistics
  - `get_ai_stats()` - Get AI provider statistics
  - `get_summary()` - Overall performance summary
  - `get_slow_endpoints(threshold_ms)` - Find slow endpoints (>1s default)
  - `reset()` - Reset all metrics

**Tracked Metrics**:
- Call counts, avg/min/max/p95 durations
- Uptime, total calls, calls per minute
- Slow endpoint detection

#### `TimingContext`
- **Usage**: Context manager for timing operations
- **Features**: Auto-logging for slow operations (>100ms: info, >1s: warning)

---

### 3. Cache (`backend/utils/cache.py`)

#### `SimpleCache`
- **Functions**:
  - `get(key)` - Get value with expiration check
  - `set(key, value, ttl)` - Set value with TTL
  - `delete(key)` - Delete key
  - `clear()` - Clear entire cache
  - `get_stats()` - Get cache statistics
- **Algorithm**: In-memory dict with timestamp tracking, auto-expiration

#### Functions
- `cache_key(*args, **kwargs)` - Generate MD5 hash from arguments
- `@cached(ttl, key_prefix)` - Decorator for caching function results
  - Supports both async and sync functions
  - Auto-detection via inspect.iscoroutinefunction

---

### 4. Middleware

#### `LoggingMiddleware` (`backend/middleware/logging_middleware.py`)
- **Function**: `dispatch(request, call_next)` - Log all requests/responses
- **Tracked**:
  - Request: method, path, query params, client host, request_id (UUID)
  - Response: status code, duration_ms
  - Errors: Exception type, message, duration
- **Excluded Paths**: /health, /metrics, /favicon.ico
- **Integration**: Adds request_id to response headers, records to metrics

#### `VersionMiddleware` (`backend/middleware/version_middleware.py`)
- **Function**: `dispatch(request, call_next)` - Validate API version
- **Supported Versions**: v1
- **Validation**: Checks path format `/api/v{version}/...`
- **Response**: 404 with helpful error for invalid versions

---

## Frontend Components & Functions

### 1. Home Page (`frontend/app/page.tsx`)

#### Components
- **HomePage**: Main landing page
  - **Functions**:
    - `handleSearch(query)` - Navigate to search page
  - **Features**:
    - Hero section with animated background
    - Search bar integration
    - Specialty chips (6 specialties)
    - Feature cards (6 features)
    - Statistics section
    - Recent chapters
    - CTA section

---

### 2. Q&A Page (`frontend/app/qa/page.tsx`)

#### `QAPage`
- **Functions**:
  - `handleSubmit(e)` - Submit question to backend
- **State Management**: question, answer, loading, error
- **API Integration**: `POST ${process.env.NEXT_PUBLIC_API_URL}/api/v1/qa/ask`

---

### 3. Layout Components

#### `Navigation` (`frontend/components/layout/Navigation.tsx`)
- **Links**: Home, Library, Synthesis, Search, Q&A
- **Responsive**: Desktop (flex) / Mobile (hamburger menu)

#### `Footer` (`frontend/components/layout/Footer.tsx`)
- Footer component (not detailed in provided code)

---

### 4. Home Components

#### `HeroSearch` (`frontend/components/home/HeroSearch.tsx`)
- **Props**: `onSearch(query)` callback
- **Features**:
  - Search input with Material-UI TextField
  - Glassmorphic design (backdrop blur)
  - Search icon adornment

#### `FeatureCard` (`frontend/components/home/FeatureCard.tsx`)
- **Props**: title, description, icon, href, color
- **Features**:
  - Framer Motion animations (hover: scale 1.02, y: -4)
  - Material-UI Card
  - Colored icon backgrounds
  - Arrow forward on hover

#### `StatisticsSection`, `RecentChapters`
- Statistics display and recent chapters list (not detailed in provided code)

---

## Key Algorithms & Patterns

### 1. Multi-Source Search Algorithm (Q&A Engine)
```
Input: Question context, max results
Process:
  1. Parallel search: PubMed, Semantic Scholar, Knowledge Graph, Perplexity, Local
  2. For each result: calculate semantic similarity (sentence transformers)
  3. Apply credibility weighting (gold: 1.0, high: 0.9, moderate: 0.7, low: 0.5)
  4. Combined score = relevance × credibility
  5. Filter: score > 0.5 AND credibility != uncertain
  6. Sort by combined score
  7. Return top N results
Output: Ranked, filtered search results
```

### 2. Behavioral Pattern Detection Algorithm
```
Input: User interaction history for chapter
Process:
  1. Filter interactions (last 72 hours)
  2. Extract temporal sequences: (interaction_i, interaction_i+1)
  3. Count sequence frequencies
  4. For sequences with frequency ≥ 3:
     a. Calculate confidence = min(0.9, count / 10)
     b. Predict next action (3rd in sequence)
     c. Calculate action probability = count_next / total_sequences
  5. Cache patterns (30-minute TTL)
Output: List of learning patterns with predicted actions
```

### 3. Knowledge Gap Detection Algorithm
```
Input: Chapter content, interaction context
Process:
  1. Content Completeness:
     - Check for essential sections (epidemiology, pathophysiology, diagnosis, treatment, complications)
     - Gap if section missing (confidence: 0.85)

  2. User Questions:
     - Map questions to gap types using templates
     - Check if content addresses question (word overlap > 0.5)
     - Gap if not addressed (confidence: 0.9)

  3. Concept Coverage:
     - Extract medical concepts from content
     - Compare with expected medical ontology
     - Gap for missing concepts (confidence: 0.7)

  4. Research Currency:
     - Check for year mentions (current year - 2 to current year)
     - Gap if no recent research (confidence: 0.8)

  5. Prioritize: Sort by priority_score × confidence
Output: Prioritized list of knowledge gaps
```

### 4. Citation Suggestion Algorithm
```
Input: Current context, available resources, citation history
Process:
  1. Analyze Context:
     - Extract needed evidence types (supporting, conflicting, foundational)
     - Extract key medical concepts
     - Calculate citation density (citations / sentences)

  2. Score Resources:
     For each resource:
       score = 0
       - Evidence type match: +0.3
       - Concept overlap: +min(0.4, overlap_count × 0.1)
       - Recency: +0.2 (if <2 years), +0.1 (if <5 years)
       - Quality: +resource.quality_score × 0.1
       score = min(1.0, score)

  3. Filter: score > 0.5

  4. Find Insertion Points:
     For each suggestion:
       - Find sentence with max concept matches
       - Position = end of that sentence

  5. Filter History:
     - Exclude recently cited (within 1 hour)
     - Unless relevance > 0.9

  6. Sort by relevance score descending
Output: Top 10 citation suggestions with insertion points
```

### 5. Intelligent Merge Algorithm
```
Input: Original content, new knowledge, user preferences
Process:
  1. Detect Nuances:
     - Sentence-level analysis
     - Calculate similarity (TF-IDF, medical term overlap)
     - Classify nuance type (addition, clarification, expansion, etc.)

  2. Detect Conflicts:
     - Check for contradictory term pairs
     - Identify conflicting statements

  3. Resolve Conflicts:
     Strategy based on user preference:
       - prefer_quality: Choose higher confidence content
       - prefer_recent: Choose newer content
       - manual: Keep original, flag for review

  4. Apply Behavioral Insights:
     - Get anticipated needs
     - Add markers for knowledge gaps

  5. Determine Integration Strategy:
     Length-based:
       - <200 chars: Inline expansion
       - 200-500 chars: Footnote or parenthetical
       - >500 chars: Section creation or sidebar

  6. Perform Merge:
     - Apply nuance changes
     - Preserve style (if user preference)
     - Add citations

  7. Quality Check:
     - Calculate: content growth, medical term density, readability, completeness
     - Overall quality = average of metrics

  8. Track Pattern:
     - Store merge record for learning
Output: Merged content + comprehensive analysis
```

---

## Statistics & Metrics

### Codebase Size (Analyzed Files)
- **Backend Services**: 8 files, ~4,500 lines
- **Alive Chapter System**: 5 files, ~4,200 lines
- **Core Infrastructure**: 4 files, ~1,200 lines
- **Utilities**: 3 files, ~600 lines
- **Middleware**: 2 files, ~200 lines
- **Frontend**: 5 files, ~400 lines
- **Total**: ~27 files, ~11,100 lines of code

### Function/Class Count
- **Classes**: 50+
- **Functions**: 250+
- **API Endpoints**: 40+
- **Database Models**: 15+

### Key Technologies
1. **Python**: asyncio, FastAPI, SQLAlchemy, sentence-transformers, networkx, numpy
2. **TypeScript/React**: Next.js 14+, Material-UI, Framer Motion
3. **AI**: OpenAI, Anthropic, Google Gemini, Perplexity
4. **Database**: PostgreSQL with TSVECTOR (full-text search), JSONB, arrays
5. **Search**: TF-IDF, cosine similarity, semantic embeddings

---

## Special Features

### 1. Alive Chapter Capabilities
- **Interactive Q&A**: Questions answered and automatically integrated
- **Behavioral Learning**: Learns from interactions, anticipates needs
- **Citation Network**: Automatic cross-referencing and citation suggestions
- **Intelligent Merging**: Nuance-aware content integration with conflict resolution
- **Proactive Evolution**: Auto-fills knowledge gaps based on patterns

### 2. Medical Specialization
- **Neurosurgery Focus**: 10 subspecialties supported
- **Medical Codes**: ICD-10, CPT integration
- **Evidence Levels**: I-V classification
- **Credibility Scoring**: Gold standard → Uncertain hierarchy
- **Clinical Context**: Surgical anatomy, techniques, complications

### 3. Multi-Provider AI
- **4 Providers**: OpenAI, Anthropic, Google Gemini, Perplexity
- **Fallback Strategy**: Automatic provider switching on failure
- **Cost Tracking**: Per-token cost calculation for each provider
- **Usage Monitoring**: Real-time usage metrics and reporting

### 4. Performance Optimization
- **Async Throughout**: Full async/await architecture
- **Connection Pooling**: Database connection management (10+20)
- **Caching**: In-memory cache with TTL and auto-expiration
- **Parallel Search**: asyncio.gather for multi-source searches
- **Background Workers**: Prefetching, pattern analysis (5-minute intervals)
- **Metrics Tracking**: P95 latency, slow endpoint detection (>1s)

---

## Architecture Patterns

### 1. Service Layer Pattern
- Clear separation: API → Service → Database
- Each service has single responsibility
- Services are testable in isolation

### 2. Repository Pattern
- Database models separate from business logic
- Simplified and full versions for flexibility

### 3. Strategy Pattern
- Multiple integration strategies (inline, footnote, section, etc.)
- Pluggable AI providers
- Configurable merge strategies

### 4. Observer Pattern
- Background workers observe interaction queues
- Behavioral learning tracks all interactions
- Metrics collection on all API calls

### 5. Factory Pattern
- AI provider initialization
- Question type detection
- Integration strategy selection

---

## Conclusion

This NSSP system represents a sophisticated neurosurgical knowledge platform with cutting-edge features:

1. **250+ functions** across 50+ classes
2. **40+ API endpoints** with full CRUD operations
3. **Advanced AI integration** with 4 providers and automatic fallback
4. **Alive Chapter System** with Q&A, behavioral learning, and citations
5. **Medical specialization** for neurosurgery with 10 subspecialties
6. **Performance optimized** with async, caching, and parallel processing
7. **Comprehensive tracking** of usage, performance, and user behavior

The system demonstrates advanced software engineering practices including async/await throughout, intelligent caching, comprehensive error handling, structured logging, and full observability with metrics tracking.

---

**Document Version**: 1.0
**Last Updated**: 2025-10-01
**Total Analysis Time**: ~30 minutes
**Files Analyzed**: 27 core files
**Lines of Code**: ~11,100
