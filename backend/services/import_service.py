"""
Import Service - Handle importing content from external sources
Supports JSON, Markdown, and other formats
"""

import json
from typing import Dict, Any
from datetime import datetime
import logging
import uuid

logger = logging.getLogger(__name__)


async def import_external_content(
    content: Dict[str, Any],
    content_type: str = "chapter"
) -> Dict[str, Any]:
    """
    Import content into system

    Args:
        content: Content data to import
        content_type: Type of content (chapter, reference, procedure)

    Returns:
        Dictionary containing import result
    """
    try:
        if content_type == "chapter":
            return await import_chapter(content)
        elif content_type == "reference":
            return await import_reference(content)
        elif content_type == "procedure":
            return await import_procedure(content)
        else:
            return {
                "success": False,
                "error": f"Unsupported content type: {content_type}"
            }

    except Exception as e:
        logger.error(f"Import failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def import_chapter(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Import chapter from external source

    Args:
        data: Chapter data dictionary

    Returns:
        Import result with chapter ID
    """
    try:
        # Import here to avoid circular imports
        from services.chapter_service import create_new_chapter

        # Validate required fields
        if not data.get("title"):
            return {
                "success": False,
                "error": "Title is required"
            }

        # Prepare chapter data
        chapter_data = {
            "title": data.get("title"),
            "specialty": data.get("specialty", "Neurosurgery General"),
            "status": data.get("status", "draft"),
            "content": data.get("content", {}),
            "metadata": data.get("metadata", {}),
            "references": data.get("references", []),
        }

        # If importing from JSON with existing ID, preserve it as metadata
        if data.get("id"):
            if not chapter_data["metadata"]:
                chapter_data["metadata"] = {}
            chapter_data["metadata"]["original_id"] = data["id"]
            chapter_data["metadata"]["imported_at"] = datetime.utcnow().isoformat()

        # Create chapter
        result = await create_new_chapter(chapter_data, background_tasks=None)

        if result.get("success"):
            return {
                "success": True,
                "message": "Chapter imported successfully",
                "chapter_id": result.get("chapter_id"),
                "data": result.get("data")
            }
        else:
            return result

    except Exception as e:
        logger.error(f"Chapter import failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def import_reference(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Import reference from external source

    Args:
        data: Reference data dictionary

    Returns:
        Import result with reference ID
    """
    try:
        # Import here to avoid circular imports
        from services.reference_service import create_new_reference

        # Validate required fields
        if not data.get("title") or not data.get("authors"):
            return {
                "success": False,
                "error": "Title and authors are required"
            }

        # Prepare reference data
        reference_data = {
            "title": data.get("title"),
            "authors": data.get("authors", []),
            "year": data.get("year", datetime.now().year),
            "journal": data.get("journal", ""),
            "doi": data.get("doi", ""),
            "pmid": data.get("pmid", ""),
            "abstract": data.get("abstract", ""),
            "url": data.get("url", ""),
        }

        # Create reference
        result = await create_new_reference(reference_data)

        if result.get("success"):
            return {
                "success": True,
                "message": "Reference imported successfully",
                "reference_id": result.get("reference_id"),
                "data": result.get("data")
            }
        else:
            return result

    except Exception as e:
        logger.error(f"Reference import failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def import_procedure(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Import surgical procedure from external source

    Args:
        data: Procedure data dictionary

    Returns:
        Import result with procedure ID
    """
    try:
        # Validate required fields
        if not data.get("name"):
            return {
                "success": False,
                "error": "Procedure name is required"
            }

        # For now, return placeholder
        # This would integrate with neurosurgery_service
        return {
            "success": True,
            "message": "Procedure import placeholder - not yet fully implemented",
            "procedure_id": str(uuid.uuid4())
        }

    except Exception as e:
        logger.error(f"Procedure import failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def import_from_markdown(markdown_content: str) -> Dict[str, Any]:
    """
    Parse and import chapter from Markdown format

    Args:
        markdown_content: Markdown text content

    Returns:
        Parsed chapter data
    """
    try:
        lines = markdown_content.split('\n')
        chapter_data = {
            "title": "",
            "specialty": "Neurosurgery General",
            "status": "draft",
            "content": {
                "summary": "",
                "sections": []
            },
            "metadata": {
                "tags": [],
                "imported_from": "markdown",
                "imported_at": datetime.utcnow().isoformat()
            }
        }

        current_section = None
        current_content = []

        for line in lines:
            line = line.strip()

            # Title (H1)
            if line.startswith('# '):
                chapter_data["title"] = line[2:].strip()

            # Section (H2)
            elif line.startswith('## '):
                # Save previous section
                if current_section:
                    current_section["content"] = "\n".join(current_content)
                    chapter_data["content"]["sections"].append(current_section)
                    current_content = []

                # Start new section
                section_title = line[3:].strip()
                if section_title.lower() != "summary" and section_title.lower() != "references":
                    current_section = {
                        "id": str(uuid.uuid4()),
                        "title": section_title,
                        "content": "",
                        "order": len(chapter_data["content"]["sections"])
                    }
                elif section_title.lower() == "summary":
                    current_section = "summary"

            # Content
            elif line and current_section:
                if current_section == "summary":
                    chapter_data["content"]["summary"] += line + "\n"
                else:
                    current_content.append(line)

        # Save last section
        if current_section and current_section != "summary":
            current_section["content"] = "\n".join(current_content)
            chapter_data["content"]["sections"].append(current_section)

        return await import_chapter(chapter_data)

    except Exception as e:
        logger.error(f"Markdown import failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def import_batch(items: list, content_type: str = "chapter") -> Dict[str, Any]:
    """
    Import multiple items in batch

    Args:
        items: List of items to import
        content_type: Type of content

    Returns:
        Batch import results
    """
    try:
        results = {
            "success": True,
            "total": len(items),
            "imported": 0,
            "failed": 0,
            "errors": []
        }

        for item in items:
            result = await import_external_content(item, content_type)
            if result.get("success"):
                results["imported"] += 1
            else:
                results["failed"] += 1
                results["errors"].append({
                    "item": item.get("title", "Unknown"),
                    "error": result.get("error")
                })

        return results

    except Exception as e:
        logger.error(f"Batch import failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }
