# Legacy Standalone Scripts

**Archived:** 2025-10-01
**Reason:** Code organization - these scripts are not used by the main FastAPI backend

## What's Here?

This directory contains standalone Python scripts that were part of an earlier iteration of the Neurosurgical Knowledge Management System. These scripts form a complete CLI-based system that can run independently of the FastAPI backend.

## Why Were They Archived?

- ✅ Not imported or used by the main FastAPI backend (`/backend/`)
- ✅ Represent a parallel/alternative implementation
- ✅ Self-contained and can run independently
- ✅ Preserved for reference and potential future use

## What Do These Scripts Do?

### Core Scripts
- **`run_integrated_system.py`** - Main CLI entry point for the standalone system
- **`system_config.py`** - Configuration management for standalone scripts

### Synthesis & Generation
- **`enhanced_synthesizer_service.py`** - Advanced synthesis service
- **`neurosurgical_summary_generator.py`** - Medical summary generation
- **`hybrid_ai_manager.py`** - AI provider management

### Search & References
- **`external_ai_searcher.py`** - External AI-powered search
- **`reference_library.py`** - Reference management
- **`reference_search_bridge.py`** - Search integration
- **`nuance_merge_engine.py`** - Content merging logic

### Utilities
- **`alive_chapter_bridge.py`** - Chapter integration bridge
- **`integrated_usage_example.py`** - Usage examples

## Can I Still Use These?

Yes! These scripts are fully functional standalone tools. To use them:

```bash
cd /path/to/NSSP
python run_integrated_system.py --help
```

## Relationship to Main Application

The main application uses:
- **Backend:** `/backend/` (FastAPI web API)
- **Frontend:** `/frontend/` (Next.js web UI)
- **Services:** `/backend/services/` (current implementation)

These archived scripts represent an alternative CLI-based approach that doesn't integrate with the web application.

## Restoration

If needed, these files can be restored to the root directory:

```bash
cd /path/to/NSSP
cp archive/legacy-scripts/*.py .
```

## History

See git history for full development timeline:
```bash
git log -- archive/legacy-scripts/
```
