"""
Simplified Reference Service - Single User
Handles reference management for neurosurgical literature
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from models.database_simplified import Reference, Citation
from services.pdf_service import PDFProcessor


class ReferenceService:
    """Service for managing references and citations"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.pdf_processor = PDFProcessor()

    async def get_all_references(
        self,
        specialty: Optional[str] = None,
        source_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get all references with optional filters"""
        query = select(Reference)

        conditions = []
        if specialty:
            conditions.append(Reference.specialty == specialty)
        if source_type:
            conditions.append(Reference.source_type == source_type)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.limit(limit).order_by(Reference.added_at.desc())

        result = await self.db.execute(query)
        references = result.scalars().all()

        return [self._reference_to_dict(ref) for ref in references]

    async def get_reference(self, reference_id: int) -> Optional[Dict[str, Any]]:
        """Get a single reference by ID"""
        result = await self.db.execute(
            select(Reference).where(Reference.id == reference_id)
        )
        reference = result.scalar_one_or_none()
        return self._reference_to_dict(reference) if reference else None

    async def get_references_by_ids(self, reference_ids: List[int]) -> List[Dict[str, Any]]:
        """Get multiple references by IDs"""
        result = await self.db.execute(
            select(Reference).where(Reference.id.in_(reference_ids))
        )
        references = result.scalars().all()
        return [self._reference_to_dict(ref) for ref in references]

    async def create_reference(self, reference_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new reference"""
        reference = Reference(
            title=reference_data["title"],
            authors=reference_data.get("authors", []),
            source_type=reference_data["source_type"],
            specialty=reference_data.get("specialty"),
            content=reference_data.get("content", ""),
            metadata_=reference_data.get("metadata", {}),
            added_at=datetime.now(timezone.utc),
            last_accessed=datetime.now(timezone.utc)
        )

        self.db.add(reference)
        await self.db.commit()
        await self.db.refresh(reference)

        return self._reference_to_dict(reference)

    async def process_pdf_reference(self, pdf_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process a PDF and create a reference"""
        # Extract content from PDF
        pdf_data = await self.pdf_processor.process_pdf(pdf_path)

        reference_data = {
            "title": metadata.get("title", pdf_data.get("title", "Untitled")),
            "authors": metadata.get("authors", pdf_data.get("authors", [])),
            "source_type": "pdf",
            "specialty": metadata.get("specialty"),
            "content": pdf_data["text"],
            "metadata": {
                **metadata,
                "pdf_info": pdf_data.get("metadata", {}),
                "page_count": pdf_data.get("page_count", 0)
            }
        }

        return await self.create_reference(reference_data)

    async def update_reference(
        self,
        reference_id: int,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update an existing reference"""
        result = await self.db.execute(
            select(Reference).where(Reference.id == reference_id)
        )
        reference = result.scalar_one_or_none()

        if not reference:
            return None

        for key, value in updates.items():
            if hasattr(reference, key):
                setattr(reference, key, value)

        reference.last_accessed = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(reference)

        return self._reference_to_dict(reference)

    async def delete_reference(self, reference_id: int) -> bool:
        """Delete a reference"""
        result = await self.db.execute(
            select(Reference).where(Reference.id == reference_id)
        )
        reference = result.scalar_one_or_none()

        if not reference:
            return False

        await self.db.delete(reference)
        await self.db.commit()
        return True

    async def search_references(
        self,
        query: str,
        specialty: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Search references by title or content"""
        search_query = select(Reference).where(
            or_(
                Reference.title.ilike(f"%{query}%"),
                Reference.content.ilike(f"%{query}%")
            )
        )

        if specialty:
            search_query = search_query.where(Reference.specialty == specialty)

        search_query = search_query.limit(limit)

        result = await self.db.execute(search_query)
        references = result.scalars().all()

        return [self._reference_to_dict(ref) for ref in references]

    async def create_citation(
        self,
        chapter_id: int,
        reference_id: int,
        context: str,
        location: str
    ) -> Dict[str, Any]:
        """Create a citation linking chapter to reference"""
        citation = Citation(
            chapter_id=chapter_id,
            reference_id=reference_id,
            context=context,
            location=location,
            created_at=datetime.now(timezone.utc)
        )

        self.db.add(citation)
        await self.db.commit()
        await self.db.refresh(citation)

        return self._citation_to_dict(citation)

    async def get_chapter_citations(self, chapter_id: int) -> List[Dict[str, Any]]:
        """Get all citations for a chapter"""
        result = await self.db.execute(
            select(Citation).where(Citation.chapter_id == chapter_id)
        )
        citations = result.scalars().all()

        return [self._citation_to_dict(c) for c in citations]

    def _reference_to_dict(self, reference: Reference) -> Dict[str, Any]:
        """Convert reference to dictionary"""
        return {
            "id": reference.id,
            "title": reference.title,
            "authors": reference.authors,
            "source_type": reference.source_type,
            "specialty": reference.specialty,
            "content": reference.content,
            "metadata": reference.metadata_,
            "added_at": reference.added_at.isoformat() if reference.added_at else None,
            "last_accessed": reference.last_accessed.isoformat() if reference.last_accessed else None
        }

    def _citation_to_dict(self, citation: Citation) -> Dict[str, Any]:
        """Convert citation to dictionary"""
        return {
            "id": citation.id,
            "chapter_id": citation.chapter_id,
            "reference_id": citation.reference_id,
            "context": citation.context,
            "location": citation.location,
            "created_at": citation.created_at.isoformat() if citation.created_at else None
        }