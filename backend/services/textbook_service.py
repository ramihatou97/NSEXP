"""
Textbook Management Service
Handles PDF textbook uploads and processing
"""

import logging
from typing import List, Dict, Any
import uuid
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# In-memory textbook storage
_textbooks: List[Dict[str, Any]] = []


async def process_textbook(file_path: str, title: str, specialty: str = None):
    """Upload and process a textbook"""
    logger.info(f"Processing textbook: {title}")

    textbook_id = str(uuid.uuid4())

    textbook = {
        "id": textbook_id,
        "title": title,
        "authors": [],
        "specialty": specialty or "Neurosurgery General",
        "file_path": file_path,
        "file_size": 0,  # Would be calculated from actual file
        "page_count": None,
        "upload_status": "processing",
        "processing_progress": 0,
        "extracted_chapters": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }

    _textbooks.append(textbook)

    return {
        "success": True,
        "data": {
            "textbook_id": textbook_id,
            "status": "processing",
            "message": "Textbook upload initiated. Processing in background.",
            "processing_job_id": f"job_{textbook_id}"
        }
    }


async def get_all_textbooks():
    """Get all uploaded textbooks"""
    logger.info("Retrieving all textbooks")

    return {
        "success": True,
        "data": _textbooks,
        "total": len(_textbooks)
    }


async def get_textbook_by_id(textbook_id: str):
    """Get specific textbook"""
    logger.info(f"Retrieving textbook: {textbook_id}")

    textbook = next((t for t in _textbooks if t["id"] == textbook_id), None)

    if not textbook:
        return {
            "success": False,
            "error": "Textbook not found"
        }

    return {
        "success": True,
        "data": textbook
    }
