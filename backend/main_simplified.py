"""
Simplified FastAPI Application for Single-User Neurosurgical Knowledge System
All functionality retained, authentication and multi-user complexity removed
"""

from fastapi import FastAPI, BackgroundTasks, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from datetime import datetime
import json

# Import simplified configuration
from config.settings_simplified import settings
from core.database_simplified import engine, Base
from services.ai_manager import ai_manager, initialize_ai_services
from utils.logger import setup_logging

# Setup logging
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Simplified application lifecycle"""
    logger.info("Starting Neurosurgical Knowledge System...")

    # Try to create database tables (skip if database unavailable)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialized")
    except Exception as e:
        logger.warning(f"Database connection failed (will use mock data): {e}")
        # System can still run with mock responses

    # Initialize AI services
    await initialize_ai_services()

    logger.info("System initialized successfully")

    yield

    # Cleanup
    try:
        await engine.dispose()
    except:
        pass
    logger.info("System shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Neurosurgical Knowledge System - Personal Edition",
    description="AI-powered neurosurgical knowledge synthesis and management for personal use",
    version="2.0.0-simplified",
    lifespan=lifespan,
)

# Simple CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0-simplified"
    }


# ============= CHAPTER ENDPOINTS (Core Functionality) =============

@app.get("/api/v1/chapters")
async def get_chapters(
    specialty: str = None,
    status: str = "all",
    limit: int = 100
):
    """Get all chapters"""
    from services.chapter_service import get_all_chapters
    return await get_all_chapters(specialty, status, limit)


@app.post("/api/v1/chapters")
async def create_chapter(chapter_data: dict, background_tasks: BackgroundTasks):
    """Create new chapter"""
    from services.chapter_service import create_new_chapter
    return await create_new_chapter(chapter_data, background_tasks)


@app.get("/api/v1/chapters/{chapter_id}")
async def get_chapter(chapter_id: str):
    """Get specific chapter"""
    from services.chapter_service import get_chapter_by_id
    return await get_chapter_by_id(chapter_id)


@app.put("/api/v1/chapters/{chapter_id}")
async def update_chapter(chapter_id: str, chapter_data: dict):
    """Update chapter"""
    from services.chapter_service import update_existing_chapter
    return await update_existing_chapter(chapter_id, chapter_data)


@app.delete("/api/v1/chapters/{chapter_id}")
async def delete_chapter(chapter_id: str):
    """Delete chapter"""
    from services.chapter_service import delete_chapter_by_id
    return await delete_chapter_by_id(chapter_id)


# ============= REFERENCE ENDPOINTS (Core Functionality) =============

@app.get("/api/v1/references")
async def get_references(
    chapter_id: str = None,
    limit: int = 100
):
    """Get all references"""
    from services.reference_service import get_all_references
    return await get_all_references(chapter_id, limit)


@app.post("/api/v1/references")
async def create_reference(reference_data: dict):
    """Create new reference"""
    from services.reference_service import create_new_reference
    return await create_new_reference(reference_data)


@app.get("/api/v1/references/{reference_id}")
async def get_reference(reference_id: str):
    """Get specific reference"""
    from services.reference_service import get_reference_by_id
    return await get_reference_by_id(reference_id)


@app.put("/api/v1/references/{reference_id}")
async def update_reference(reference_id: str, reference_data: dict):
    """Update reference"""
    from services.reference_service import update_existing_reference
    return await update_existing_reference(reference_id, reference_data)


@app.delete("/api/v1/references/{reference_id}")
async def delete_reference(reference_id: str):
    """Delete reference"""
    from services.reference_service import delete_reference_by_id
    return await delete_reference_by_id(reference_id)


# ============= SYNTHESIS ENDPOINTS (Core Functionality) =============

@app.post("/api/v1/synthesis/generate")
async def synthesize_chapter(
    topic: str,
    specialty: str = "neurosurgery",
    max_sources: int = 15,
    background_tasks: BackgroundTasks = None
):
    """Generate synthesized chapter"""
    from services.synthesis_service import synthesize_new_chapter

    result = await synthesize_new_chapter(
        topic=topic,
        specialty=specialty,
        max_sources=max_sources
    )

    # Optional: Track synthesis in background
    if background_tasks:
        background_tasks.add_task(log_synthesis, topic)

    return result


@app.get("/api/v1/synthesis/status/{job_id}")
async def get_synthesis_status(job_id: str):
    """Get synthesis job status"""
    from services.synthesis_service import get_job_status
    return await get_job_status(job_id)


# ============= SEARCH ENDPOINTS (Core Functionality) =============

@app.get("/api/v1/search")
async def search_content(
    query: str,
    search_type: str = "all",  # all, chapters, references, procedures
    limit: int = 20
):
    """Search across all content"""
    from services.search_service import search_all_content
    return await search_all_content(query, search_type, limit)


@app.post("/api/v1/search/semantic")
async def semantic_search(query: str, limit: int = 10):
    """Semantic search using embeddings"""
    from services.search_service import semantic_search_content
    return await semantic_search_content(query, limit)


# ============= Q&A ENDPOINTS (Core Functionality) =============

@app.post("/api/v1/qa/ask")
async def ask_question(
    question: str,
    chapter_id: str = None,
    context: str = None
):
    """Ask question and get AI-powered answer"""
    from services.qa_service import process_question
    return await process_question(question, chapter_id, context)


@app.get("/api/v1/qa/history")
async def get_qa_history(chapter_id: str = None, limit: int = 50):
    """Get Q&A history"""
    from services.qa_service import get_history
    return await get_history(chapter_id, limit)


# ============= CITATION ENDPOINTS (Core Functionality) =============

@app.get("/api/v1/citations/network/{chapter_id}")
async def get_citation_network(chapter_id: str):
    """Get citation network for chapter"""
    from services.citation_service import get_network
    return await get_network(chapter_id)


@app.post("/api/v1/citations/suggest")
async def suggest_citations(chapter_id: str, content: str):
    """Suggest citations for content"""
    from services.citation_service import suggest_for_content
    return await suggest_for_content(chapter_id, content)


# ============= BEHAVIORAL LEARNING (Simplified) =============

@app.post("/api/v1/behavioral/track")
async def track_behavior(
    action_type: str,
    context: dict,
    background_tasks: BackgroundTasks
):
    """Track user behavior for learning"""
    from services.behavioral_service import track_action
    background_tasks.add_task(track_action, action_type, context)
    return {"status": "tracked"}


@app.get("/api/v1/behavioral/suggestions")
async def get_suggestions():
    """Get AI suggestions based on behavior"""
    from services.behavioral_service import get_personalized_suggestions
    return await get_personalized_suggestions()


# ============= NEUROSURGERY-SPECIFIC ENDPOINTS =============

@app.get("/api/v1/procedures")
async def get_procedures(
    procedure_type: str = None,
    anatomical_region: str = None
):
    """Get surgical procedures"""
    from services.neurosurgery_service import get_surgical_procedures
    return await get_surgical_procedures(procedure_type, anatomical_region)


@app.get("/api/v1/procedures/{procedure_id}")
async def get_procedure_details(procedure_id: str):
    """Get detailed procedure information"""
    from services.neurosurgery_service import get_procedure_by_id
    return await get_procedure_by_id(procedure_id)


@app.post("/api/v1/medical/validate")
async def validate_medical_content(content: str, specialty: str = "neurosurgery"):
    """Validate medical accuracy"""
    validation = await ai_manager.validate_medical_content(content, specialty)
    return {
        "is_accurate": validation.is_medically_accurate,
        "confidence": validation.confidence_score,
        "issues": validation.issues_found,
        "suggestions": validation.suggestions
    }


# ============= TEXTBOOK/PDF MANAGEMENT =============

@app.post("/api/v1/textbooks/upload")
async def upload_textbook(
    file_path: str,
    title: str,
    specialty: str = None,
    background_tasks: BackgroundTasks = None
):
    """Upload and process textbook"""
    from services.textbook_service import process_textbook

    result = await process_textbook(file_path, title, specialty)

    if background_tasks:
        background_tasks.add_task(extract_chapters_background, result["textbook_id"])

    return result


@app.get("/api/v1/textbooks")
async def get_textbooks():
    """Get all processed textbooks"""
    from services.textbook_service import get_all_textbooks
    return await get_all_textbooks()


# ============= SETTINGS/PREFERENCES (Simplified) =============

@app.get("/api/v1/preferences")
async def get_preferences():
    """Get user preferences"""
    from services.preferences_service import get_user_preferences
    return await get_user_preferences()


@app.put("/api/v1/preferences")
async def update_preferences(preferences: dict):
    """Update user preferences"""
    from services.preferences_service import update_user_preferences
    return await update_user_preferences(preferences)


# ============= KNOWLEDGE GAPS =============

@app.get("/api/v1/gaps/{chapter_id}")
async def get_knowledge_gaps(chapter_id: str):
    """Get identified knowledge gaps"""
    from services.gap_service import get_gaps_for_chapter
    return await get_gaps_for_chapter(chapter_id)


@app.post("/api/v1/gaps/{gap_id}/fill")
async def fill_knowledge_gap(gap_id: str, background_tasks: BackgroundTasks):
    """Auto-fill knowledge gap"""
    from services.gap_service import auto_fill_gap

    result = await auto_fill_gap(gap_id)
    background_tasks.add_task(update_chapter_with_gap, result)

    return result


# ============= EXPORT/IMPORT =============

@app.get("/api/v1/export/{chapter_id}")
async def export_chapter(chapter_id: str, format: str = "json"):
    """Export chapter in various formats"""
    from services.export_service import export_chapter_content
    return await export_chapter_content(chapter_id, format)


@app.post("/api/v1/import")
async def import_content(content: dict, content_type: str = "chapter"):
    """Import content into system"""
    from services.import_service import import_external_content
    return await import_external_content(content, content_type)


# ============= WEBSOCKET FOR REAL-TIME UPDATES =============

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time synthesis updates"""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            # Handle different message types
            if message.get("type") == "synthesis_progress":
                # Send progress updates
                await websocket.send_json({
                    "type": "progress",
                    "data": message.get("data", {})
                })

            elif message.get("type") == "ping":
                # Heartbeat
                await websocket.send_json({"type": "pong"})

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await websocket.close()


# ============= UTILITY FUNCTIONS =============

async def log_synthesis(topic: str):
    """Log synthesis action"""
    logger.info(f"Synthesis completed for topic: {topic}")


async def extract_chapters_background(textbook_id: str):
    """Extract chapters from textbook in background"""
    logger.info(f"Extracting chapters from textbook: {textbook_id}")


async def update_chapter_with_gap(gap_data: dict):
    """Update chapter after filling knowledge gap"""
    logger.info(f"Updating chapter with filled gap: {gap_data.get('gap_id')}")


# ============= ERROR HANDLER =============

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "An error occurred", "detail": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main_simplified:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )