"""
Main FastAPI Application for Neurosurgical Knowledge Management System
Specialized for neurosurgical content synthesis, management, and AI-powered assistance
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from prometheus_client import make_asgi_app
import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
import os
from datetime import datetime

# Import routers
from api.auth.router import router as auth_router
from api.chapters.router import router as chapters_router
from api.synthesis.router import router as synthesis_router
from api.search.router import router as search_router
from api.qa.router import router as qa_router
from api.citations.router import router as citations_router
from api.neurosurgery.router import router as neurosurgery_router

# Import configuration
from config.settings import settings
from core.database import engine, Base
from utils.logger import setup_logging

# Setup logging
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle events
    """
    # Startup
    logger.info("Starting Neurosurgical Knowledge Management System...")

    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Initialize AI services
    from services.ai_manager import initialize_ai_services
    await initialize_ai_services()

    # Initialize vector database
    from services.vector_db import initialize_vector_db
    await initialize_vector_db()

    # Load medical ontologies
    from services.medical_ontology import load_neurosurgical_ontologies
    await load_neurosurgical_ontologies()

    logger.info("System initialized successfully")

    yield

    # Shutdown
    logger.info("Shutting down system...")

    # Cleanup connections
    await engine.dispose()

    logger.info("System shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Neurosurgical Knowledge Management System",
    description="""
    Advanced AI-powered system for neurosurgical knowledge synthesis, management, and assistance.

    ## Features
    * 🧠 **Neurosurgery-Specific Content**: Specialized for brain, spine, and peripheral nerve surgery
    * 📚 **Comprehensive Synthesis**: Generate complete chapters from multiple medical sources
    * 🤖 **AI-Powered Assistance**: Intelligent Q&A, knowledge gap detection, and content enhancement
    * 🔗 **Citation Network**: Automatic cross-referencing and citation management
    * 📊 **Behavioral Learning**: Adapts to user patterns and anticipates knowledge needs
    * 🏥 **Clinical Integration**: ICD-10, CPT codes, clinical trials, and evidence-based guidelines
    * 🔬 **Medical Imaging**: DICOM support, neuroimaging analysis, and surgical planning
    * 📈 **Quality Assurance**: Medical accuracy verification and evidence level tracking

    ## Specialties Covered
    * Brain Tumors (Gliomas, Meningiomas, Pituitary, etc.)
    * Vascular Neurosurgery (Aneurysms, AVMs, Cavernomas)
    * Spine Surgery (Degenerative, Tumor, Trauma, Deformity)
    * Functional Neurosurgery (DBS, Epilepsy, Pain)
    * Pediatric Neurosurgery
    * Skull Base Surgery
    * Peripheral Nerve Surgery
    * Neurotrauma and Critical Care
    """,
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Configure Sentry for error tracking
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        traces_sample_rate=0.1 if settings.ENVIRONMENT == "production" else 1.0,
    )
    app.add_middleware(SentryAsgiMiddleware)

# Add Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Handle uncaught exceptions globally
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    # Don't expose internal errors in production
    if settings.ENVIRONMENT == "production":
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal error occurred. Please try again later."}
        )

    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )


# Health check endpoints
@app.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "neurosurgical-knowledge-system",
        "version": "2.0.0"
    }


@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with component status"""

    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {}
    }

    # Check database
    try:
        from core.database import check_database_health
        db_health = await check_database_health()
        health_status["components"]["database"] = {
            "status": "healthy" if db_health else "unhealthy",
            "response_time_ms": db_health.get("response_time", 0) if isinstance(db_health, dict) else 0
        }
    except Exception as e:
        health_status["components"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"

    # Check AI services
    try:
        from services.ai_manager import check_ai_services_health
        ai_health = await check_ai_services_health()
        health_status["components"]["ai_services"] = ai_health
    except Exception as e:
        health_status["components"]["ai_services"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"

    # Check vector database
    try:
        from services.vector_db import check_vector_db_health
        vector_health = await check_vector_db_health()
        health_status["components"]["vector_db"] = {
            "status": "healthy" if vector_health else "unhealthy"
        }
    except Exception as e:
        health_status["components"]["vector_db"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"

    # Check cache
    try:
        from core.cache import check_cache_health
        cache_health = await check_cache_health()
        health_status["components"]["cache"] = {
            "status": "healthy" if cache_health else "unhealthy"
        }
    except Exception as e:
        health_status["components"]["cache"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        # Cache is not critical, don't degrade overall status

    return health_status


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "name": "Neurosurgical Knowledge Management System",
        "version": "2.0.0",
        "description": "Advanced AI-powered system for neurosurgical knowledge synthesis",
        "documentation": "/api/docs",
        "health": "/health",
        "specialties": [
            "Brain Tumors",
            "Vascular Neurosurgery",
            "Spine Surgery",
            "Functional Neurosurgery",
            "Pediatric Neurosurgery",
            "Skull Base Surgery",
            "Peripheral Nerve Surgery",
            "Neurotrauma"
        ],
        "features": [
            "AI-Powered Synthesis",
            "Intelligent Q&A",
            "Citation Networks",
            "Behavioral Learning",
            "Medical Imaging Support",
            "Clinical Integration"
        ],
        "contact": {
            "support": "support@neurosurgicalknowledge.com",
            "documentation": "https://docs.neurosurgicalknowledge.com"
        }
    }


# Include routers with prefixes
app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

app.include_router(
    chapters_router,
    prefix="/api/v1/chapters",
    tags=["Chapters"]
)

app.include_router(
    synthesis_router,
    prefix="/api/v1/synthesis",
    tags=["Synthesis"]
)

app.include_router(
    search_router,
    prefix="/api/v1/search",
    tags=["Search"]
)

app.include_router(
    qa_router,
    prefix="/api/v1/qa",
    tags=["Q&A"]
)

app.include_router(
    citations_router,
    prefix="/api/v1/citations",
    tags=["Citations"]
)

app.include_router(
    neurosurgery_router,
    prefix="/api/v1/neurosurgery",
    tags=["Neurosurgery-Specific"]
)

# Admin endpoints (protected)
from api.admin.router import router as admin_router
app.include_router(
    admin_router,
    prefix="/api/v1/admin",
    tags=["Admin"]
)


# WebSocket endpoint for real-time updates
from fastapi import WebSocket
from typing import Dict
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"WebSocket connection established for user {user_id}")

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            logger.info(f"WebSocket connection closed for user {user_id}")

    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)


manager = ConnectionManager()


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for real-time updates during synthesis and processing
    """
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)

            # Handle different message types
            if message.get("type") == "synthesis_progress":
                # Send synthesis progress updates
                await manager.send_personal_message(
                    json.dumps({
                        "type": "progress",
                        "data": {
                            "step": message.get("step"),
                            "progress": message.get("progress"),
                            "message": message.get("message")
                        }
                    }),
                    user_id
                )

            elif message.get("type") == "chapter_update":
                # Notify about chapter updates
                await manager.broadcast(
                    json.dumps({
                        "type": "chapter_updated",
                        "data": {
                            "chapter_id": message.get("chapter_id"),
                            "title": message.get("title"),
                            "updated_by": user_id
                        }
                    })
                )

    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
    finally:
        manager.disconnect(user_id)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level="info" if settings.ENVIRONMENT == "production" else "debug",
        access_log=True,
        use_colors=True,
    )