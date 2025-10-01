"""
Search Service for Neurosurgical Knowledge System
Provides search functionality across chapters, references, and procedures
"""
from typing import List, Dict, Any, Optional
import logging
from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from models.database_simplified import Chapter, Reference, SurgicalProcedure, Citation
from core.database_simplified import get_session

logger = logging.getLogger(__name__)


async def search_all_content(
    query: str,
    search_type: str = "all",
    limit: int = 20
) -> Dict[str, Any]:
    """
    Search across all content types
    
    Args:
        query: Search query string
        search_type: Type of content to search (all, chapters, references, procedures)
        limit: Maximum number of results
        
    Returns:
        Dictionary with search results
    """
    try:
        results = {
            "query": query,
            "search_type": search_type,
            "results": {
                "chapters": [],
                "references": [],
                "procedures": []
            },
            "total": 0
        }
        
        async with get_session() as session:
            # Search chapters
            if search_type in ["all", "chapters"]:
                chapters = await _search_chapters(session, query, limit)
                results["results"]["chapters"] = chapters
            
            # Search references
            if search_type in ["all", "references"]:
                references = await _search_references(session, query, limit)
                results["results"]["references"] = references
            
            # Search procedures
            if search_type in ["all", "procedures"]:
                procedures = await _search_procedures(session, query, limit)
                results["results"]["procedures"] = procedures
        
        # Calculate total
        results["total"] = (
            len(results["results"]["chapters"]) +
            len(results["results"]["references"]) +
            len(results["results"]["procedures"])
        )
        
        return {
            "success": True,
            "data": results
        }
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return {
            "success": False,
            "error": str(e),
            "data": None
        }


async def _search_chapters(
    session: AsyncSession,
    query: str,
    limit: int
) -> List[Dict[str, Any]]:
    """Search chapters by title, content, or specialty"""
    try:
        query_lower = query.lower()
        
        stmt = select(Chapter).where(
            or_(
                Chapter.title.ilike(f"%{query}%"),
                Chapter.content.ilike(f"%{query}%"),
                Chapter.specialty.ilike(f"%{query}%"),
                Chapter.summary.ilike(f"%{query}%")
            )
        ).limit(limit)
        
        result = await session.execute(stmt)
        chapters = result.scalars().all()
        
        return [
            {
                "id": str(chapter.id),
                "title": chapter.title,
                "specialty": chapter.specialty,
                "summary": chapter.summary[:200] if chapter.summary else None,
                "status": chapter.status,
                "created_at": chapter.created_at.isoformat() if chapter.created_at else None,
                "type": "chapter"
            }
            for chapter in chapters
        ]
    except Exception as e:
        logger.error(f"Chapter search error: {e}")
        return []


async def _search_references(
    session: AsyncSession,
    query: str,
    limit: int
) -> List[Dict[str, Any]]:
    """Search references by title, authors, or abstract"""
    try:
        stmt = select(Reference).where(
            or_(
                Reference.title.ilike(f"%{query}%"),
                Reference.authors.ilike(f"%{query}%"),
                Reference.abstract.ilike(f"%{query}%"),
                Reference.journal.ilike(f"%{query}%")
            )
        ).limit(limit)
        
        result = await session.execute(stmt)
        references = result.scalars().all()
        
        return [
            {
                "id": str(ref.id),
                "title": ref.title,
                "authors": ref.authors,
                "journal": ref.journal,
                "year": ref.year,
                "doi": ref.doi,
                "type": "reference"
            }
            for ref in references
        ]
    except Exception as e:
        logger.error(f"Reference search error: {e}")
        return []


async def _search_procedures(
    session: AsyncSession,
    query: str,
    limit: int
) -> List[Dict[str, Any]]:
    """Search surgical procedures by name or description"""
    try:
        stmt = select(SurgicalProcedure).where(
            or_(
                SurgicalProcedure.name.ilike(f"%{query}%"),
                SurgicalProcedure.description.ilike(f"%{query}%"),
                SurgicalProcedure.indications.ilike(f"%{query}%")
            )
        ).limit(limit)
        
        result = await session.execute(stmt)
        procedures = result.scalars().all()
        
        return [
            {
                "id": str(proc.id),
                "name": proc.name,
                "specialty": proc.specialty,
                "description": proc.description[:200] if proc.description else None,
                "type": "procedure"
            }
            for proc in procedures
        ]
    except Exception as e:
        logger.error(f"Procedure search error: {e}")
        return []


async def semantic_search_content(
    query: str,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Semantic search using embeddings (simplified version)
    In production, this would use vector similarity search
    For now, falls back to text search
    
    Args:
        query: Search query
        limit: Maximum results
        
    Returns:
        Search results with relevance scores
    """
    try:
        # For simplified version, use regular search
        # In production, this would use vector embeddings and similarity search
        results = await search_all_content(query, "all", limit)
        
        # Add mock relevance scores
        if results.get("success"):
            for category in results["data"]["results"].values():
                for item in category:
                    item["relevance_score"] = 0.85  # Mock score
        
        return results
        
    except Exception as e:
        logger.error(f"Semantic search error: {e}")
        return {
            "success": False,
            "error": str(e),
            "data": None
        }
