"""
Chapter Service - Simplified version without database dependency
Manages chapter CRUD operations with mock data support
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


async def get_all_chapters(specialty: str = None, status: str = "all", limit: int = 100) -> Dict[str, Any]:
    """
    Get all chapters with optional filtering
    Returns mock data when database is not available
    """
    try:
        # Mock chapter data
        mock_chapters = [
            {
                "id": "1",
                "title": "Glioblastoma Management",
                "specialty": "tumor",
                "summary": "Comprehensive guide to GBM diagnosis, surgical approaches, and multimodal treatment strategies",
                "status": "published",
                "created_at": "2024-01-15T10:00:00",
                "updated_at": "2024-01-15T10:00:00"
            },
            {
                "id": "2",
                "title": "Aneurysm Clipping Techniques",
                "specialty": "vascular",
                "summary": "Surgical approaches and microsurgical techniques for cerebral aneurysm clipping",
                "status": "published",
                "created_at": "2024-01-20T14:30:00",
                "updated_at": "2024-01-20T14:30:00"
            },
            {
                "id": "3",
                "title": "Lumbar Spinal Fusion",
                "specialty": "spine",
                "summary": "Indications, techniques, and outcomes of lumbar fusion procedures",
                "status": "published",
                "created_at": "2024-02-01T09:00:00",
                "updated_at": "2024-02-01T09:00:00"
            }
        ]
        
        # Filter by specialty if provided
        if specialty and specialty != "all":
            mock_chapters = [c for c in mock_chapters if c["specialty"] == specialty.lower()]
        
        # Filter by status
        if status and status != "all":
            mock_chapters = [c for c in mock_chapters if c["status"] == status.lower()]
        
        return {
            "success": True,
            "data": {
                "chapters": mock_chapters[:limit],
                "total": len(mock_chapters)
            }
        }
    except Exception as e:
        logger.error(f"Error getting chapters: {e}")
        return {
            "success": False,
            "error": str(e),
            "data": None
        }


async def get_chapter_by_id(chapter_id: str) -> Dict[str, Any]:
    """Get specific chapter by ID"""
    try:
        # Mock detailed chapter data
        chapter = {
            "id": chapter_id,
            "title": "Glioblastoma Management",
            "specialty": "tumor",
            "content": """
# Glioblastoma Management

## Introduction
Glioblastoma (GBM) is the most common and aggressive primary brain tumor in adults.

## Diagnosis
- MRI with contrast
- Biopsy or resection for histological confirmation
- Molecular markers (IDH, MGMT)

## Treatment
1. **Surgical Resection**: Maximal safe resection
2. **Radiation Therapy**: Standard dose (60 Gy)
3. **Chemotherapy**: Temozolomide (Stupp protocol)

## Prognosis
- Median survival: 14-16 months
- Better outcomes with MGMT methylation
""",
            "summary": "Comprehensive guide to GBM diagnosis and treatment",
            "status": "published",
            "metadata": {
                "evidence_level": "High",
                "last_reviewed": "2024-01-15",
                "sources": 15
            },
            "created_at": "2024-01-15T10:00:00",
            "updated_at": "2024-01-15T10:00:00"
        }
        
        return {
            "success": True,
            "data": chapter
        }
    except Exception as e:
        logger.error(f"Error getting chapter {chapter_id}: {e}")
        return {
            "success": False,
            "error": str(e),
            "data": None
        }


async def create_new_chapter(chapter_data: dict, background_tasks=None) -> Dict[str, Any]:
    """Create new chapter"""
    try:
        import time
        chapter_id = str(int(time.time()))
        
        chapter = {
            "id": chapter_id,
            "title": chapter_data.get("title", "Untitled Chapter"),
            "specialty": chapter_data.get("specialty", "neurosurgery"),
            "content": chapter_data.get("content", ""),
            "summary": chapter_data.get("summary", ""),
            "status": "draft",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Created chapter (mock): {chapter['title']}")
        
        return {
            "success": True,
            "data": chapter,
            "message": "Chapter created successfully. Note: Running in mock mode without database."
        }
    except Exception as e:
        logger.error(f"Error creating chapter: {e}")
        return {
            "success": False,
            "error": str(e),
            "data": None
        }


async def update_existing_chapter(chapter_id: str, chapter_data: dict) -> Dict[str, Any]:
    """Update existing chapter"""
    try:
        updated_chapter = {
            "id": chapter_id,
            "title": chapter_data.get("title", "Updated Chapter"),
            "specialty": chapter_data.get("specialty", "neurosurgery"),
            "content": chapter_data.get("content", ""),
            "summary": chapter_data.get("summary", ""),
            "status": chapter_data.get("status", "draft"),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Updated chapter (mock): {chapter_id}")
        
        return {
            "success": True,
            "data": updated_chapter,
            "message": "Chapter updated successfully. Note: Running in mock mode without database."
        }
    except Exception as e:
        logger.error(f"Error updating chapter {chapter_id}: {e}")
        return {
            "success": False,
            "error": str(e),
            "data": None
        }


async def delete_chapter_by_id(chapter_id: str) -> Dict[str, Any]:
    """Delete chapter"""
    try:
        logger.info(f"Deleted chapter (mock): {chapter_id}")
        
        return {
            "success": True,
            "message": f"Chapter {chapter_id} deleted successfully. Note: Running in mock mode without database."
        }
    except Exception as e:
        logger.error(f"Error deleting chapter {chapter_id}: {e}")
        return {
            "success": False,
            "error": str(e)
        }
