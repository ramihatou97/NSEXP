"""
Simplified Chapter Service - Single User
Handles chapter operations for neurosurgical knowledge management
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime

from models.database_simplified import Chapter, ChapterVersion, AliveChapter
from services.ai_service import AIService
from services.pdf_service import PDFProcessor


class ChapterService:
    """Service for managing neurosurgical chapters"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.ai_service = AIService()
        self.pdf_processor = PDFProcessor()

    async def get_all_chapters(
        self,
        specialty: Optional[str] = None,
        status: str = "all",
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get all chapters with optional filters"""
        query = select(Chapter)

        if specialty:
            query = query.where(Chapter.specialty == specialty)

        if status != "all":
            query = query.where(Chapter.status == status)

        query = query.limit(limit).order_by(Chapter.updated_at.desc())

        result = await self.db.execute(query)
        chapters = result.scalars().all()

        return [self._chapter_to_dict(chapter) for chapter in chapters]

    async def get_chapter(self, chapter_id: int) -> Optional[Dict[str, Any]]:
        """Get a single chapter by ID"""
        result = await self.db.execute(
            select(Chapter).where(Chapter.id == chapter_id)
        )
        chapter = result.scalar_one_or_none()
        return self._chapter_to_dict(chapter) if chapter else None

    async def create_chapter(self, chapter_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new chapter"""
        chapter = Chapter(
            title=chapter_data["title"],
            specialty=chapter_data["specialty"],
            content=chapter_data.get("content", ""),
            status="draft",
            metadata_=chapter_data.get("metadata", {}),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        self.db.add(chapter)
        await self.db.commit()
        await self.db.refresh(chapter)

        # Create initial version
        await self._create_version(chapter, "Initial creation")

        return self._chapter_to_dict(chapter)

    async def update_chapter(
        self,
        chapter_id: int,
        updates: Dict[str, Any],
        change_summary: str = "Updated chapter"
    ) -> Optional[Dict[str, Any]]:
        """Update an existing chapter"""
        result = await self.db.execute(
            select(Chapter).where(Chapter.id == chapter_id)
        )
        chapter = result.scalar_one_or_none()

        if not chapter:
            return None

        # Update fields
        for key, value in updates.items():
            if hasattr(chapter, key):
                setattr(chapter, key, value)

        chapter.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(chapter)

        # Create version
        await self._create_version(chapter, change_summary)

        return self._chapter_to_dict(chapter)

    async def delete_chapter(self, chapter_id: int) -> bool:
        """Delete a chapter"""
        result = await self.db.execute(
            select(Chapter).where(Chapter.id == chapter_id)
        )
        chapter = result.scalar_one_or_none()

        if not chapter:
            return False

        await self.db.delete(chapter)
        await self.db.commit()
        return True

    async def synthesize_chapter(
        self,
        chapter_id: int,
        reference_ids: List[int]
    ) -> Dict[str, Any]:
        """Synthesize chapter content from references using AI"""
        chapter = await self.get_chapter(chapter_id)
        if not chapter:
            raise ValueError(f"Chapter {chapter_id} not found")

        # Get references
        from services.reference_service import ReferenceService
        ref_service = ReferenceService(self.db)
        references = await ref_service.get_references_by_ids(reference_ids)

        # Synthesize using AI
        synthesis = await self.ai_service.synthesize_content(
            chapter_title=chapter["title"],
            specialty=chapter["specialty"],
            references=references
        )

        # Update chapter
        await self.update_chapter(
            chapter_id,
            {
                "content": synthesis["content"],
                "metadata_": {
                    **chapter.get("metadata", {}),
                    "synthesis": {
                        "reference_count": len(references),
                        "generated_at": datetime.utcnow().isoformat(),
                        "model": synthesis.get("model", "unknown")
                    }
                }
            },
            change_summary="AI synthesis from references"
        )

        return synthesis

    async def get_chapter_versions(self, chapter_id: int) -> List[Dict[str, Any]]:
        """Get all versions of a chapter"""
        result = await self.db.execute(
            select(ChapterVersion)
            .where(ChapterVersion.chapter_id == chapter_id)
            .order_by(ChapterVersion.created_at.desc())
        )
        versions = result.scalars().all()

        return [self._version_to_dict(v) for v in versions]

    async def _create_version(self, chapter: Chapter, change_summary: str):
        """Create a version snapshot of a chapter"""
        version = ChapterVersion(
            chapter_id=chapter.id,
            version_number=await self._get_next_version_number(chapter.id),
            content=chapter.content,
            metadata_=chapter.metadata_,
            change_summary=change_summary,
            created_at=datetime.utcnow()
        )

        self.db.add(version)
        await self.db.commit()

    async def _get_next_version_number(self, chapter_id: int) -> int:
        """Get the next version number for a chapter"""
        result = await self.db.execute(
            select(ChapterVersion.version_number)
            .where(ChapterVersion.chapter_id == chapter_id)
            .order_by(ChapterVersion.version_number.desc())
            .limit(1)
        )
        last_version = result.scalar_one_or_none()
        return (last_version or 0) + 1

    def _chapter_to_dict(self, chapter: Chapter) -> Dict[str, Any]:
        """Convert chapter to dictionary"""
        return {
            "id": chapter.id,
            "title": chapter.title,
            "specialty": chapter.specialty,
            "content": chapter.content,
            "status": chapter.status,
            "metadata": chapter.metadata_,
            "created_at": chapter.created_at.isoformat() if chapter.created_at else None,
            "updated_at": chapter.updated_at.isoformat() if chapter.updated_at else None
        }

    def _version_to_dict(self, version: ChapterVersion) -> Dict[str, Any]:
        """Convert version to dictionary"""
        return {
            "id": version.id,
            "chapter_id": version.chapter_id,
            "version_number": version.version_number,
            "content": version.content,
            "metadata": version.metadata_,
            "change_summary": version.change_summary,
            "created_at": version.created_at.isoformat() if version.created_at else None
        }


async def get_all_chapters(
    specialty: Optional[str] = None,
    status: str = "all",
    limit: int = 100,
    db: AsyncSession = None
) -> List[Dict[str, Any]]:
    """Helper function for direct access"""
    service = ChapterService(db)
    return await service.get_all_chapters(specialty, status, limit)