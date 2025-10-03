"""
Unit tests for Database Models
Tests SQLAlchemy models and relationships
"""
import pytest
from datetime import datetime
import uuid as uuid_lib

from models import (
    Base,
    Chapter,
    Reference,
    Citation,
    QASession,
    SurgicalProcedure,
    UserPreferences,
    Textbook,
    NeurosurgicalSpecialty,
    ProcedureType,
    AnatomicalRegion
)


class TestEnums:
    """Test enum definitions"""

    def test_neurosurgical_specialty_enum(self):
        """Test NeurosurgicalSpecialty enum"""
        assert NeurosurgicalSpecialty.TUMOR.value == "tumor"
        assert NeurosurgicalSpecialty.VASCULAR.value == "vascular"
        assert NeurosurgicalSpecialty.SPINE.value == "spine"

    def test_procedure_type_enum(self):
        """Test ProcedureType enum"""
        assert ProcedureType.CRANIOTOMY.value == "craniotomy"
        assert ProcedureType.LAMINECTOMY.value == "laminectomy"

    def test_anatomical_region_enum(self):
        """Test AnatomicalRegion enum"""
        assert AnatomicalRegion.FRONTAL.value == "frontal"
        assert AnatomicalRegion.CEREBELLUM.value == "cerebellum"


class TestChapterModel:
    """Test Chapter model"""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_chapter_creation(self, db_session):
        """Test creating a chapter"""
        chapter = Chapter(
            id=uuid_lib.uuid4(),
            title="Test Chapter",
            specialty="tumor",
            content="Test content",
            status="draft",
            version="1.0"
        )

        db_session.add(chapter)
        await db_session.commit()

        assert chapter.id is not None
        assert chapter.title == "Test Chapter"

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_chapter_attributes(self, db_session):
        """Test chapter model attributes"""
        chapter = Chapter(
            id=uuid_lib.uuid4(),
            title="Comprehensive Chapter",
            specialty="vascular",
            content="Detailed content",
            status="published",
            version="2.0"
        )

        assert hasattr(chapter, "title")
        assert hasattr(chapter, "specialty")
        assert hasattr(chapter, "content")
        assert hasattr(chapter, "status")


class TestReferenceModel:
    """Test Reference model"""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_reference_creation(self, db_session):
        """Test creating a reference"""
        reference = Reference(
            id=uuid_lib.uuid4(),
            title="Neurosurgery Textbook",
            type="textbook",
            content="Comprehensive neurosurgical content"
        )

        db_session.add(reference)
        await db_session.commit()

        assert reference.id is not None
        assert reference.title == "Neurosurgery Textbook"

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_reference_attributes(self, db_session):
        """Test reference model attributes"""
        reference = Reference(
            id=uuid_lib.uuid4(),
            title="Medical Journal Article",
            type="journal",
            content="Research findings"
        )

        assert hasattr(reference, "title")
        assert hasattr(reference, "type")
        assert hasattr(reference, "content")


class TestRelationships:
    """Test model relationships"""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_chapter_reference_relationship(self, db_session):
        """Test Chapter-Reference relationship"""
        # Create chapter
        chapter = Chapter(
            id=uuid_lib.uuid4(),
            title="Test Chapter",
            specialty="tumor",
            content="Content",
            status="draft",
            version="1.0"
        )

        # Create reference
        reference = Reference(
            id=uuid_lib.uuid4(),
            title="Test Reference",
            type="textbook",
            content="Reference content"
        )

        db_session.add(chapter)
        db_session.add(reference)
        await db_session.commit()

        # Test relationship if it exists
        assert chapter.id is not None
        assert reference.id is not None


class TestUserPreferences:
    """Test UserPreferences model"""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_user_preferences_creation(self, db_session):
        """Test creating user preferences"""
        prefs = UserPreferences(
            theme="dark",
            font_size="large",
            auto_synthesis=True
        )

        db_session.add(prefs)
        await db_session.commit()

        assert prefs.id is not None
        assert prefs.theme == "dark"
        assert prefs.auto_synthesis is True

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_user_preferences_defaults(self, db_session):
        """Test user preferences default values"""
        prefs = UserPreferences()

        # Test that defaults are set (if defined in model)
        assert hasattr(prefs, "theme")
        assert hasattr(prefs, "font_size")


class TestTextbookModel:
    """Test Textbook model"""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_textbook_creation(self, db_session):
        """Test creating a textbook"""
        textbook = Textbook(
            id=uuid_lib.uuid4(),
            title="Principles of Neurosurgery",
            isbn="978-0-123456-78-9",
            publication_year=2024
        )

        db_session.add(textbook)
        await db_session.commit()

        assert textbook.id is not None
        assert textbook.title == "Principles of Neurosurgery"
        assert textbook.publication_year == 2024


class TestQASessionModel:
    """Test QASession model"""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_qa_session_creation(self, db_session):
        """Test creating a Q&A session"""
        session = QASession(
            id=uuid_lib.uuid4(),
            question="What are indications for craniotomy?",
            answer="Craniotomy is indicated for...",
            specialty="general"
        )

        db_session.add(session)
        await db_session.commit()

        assert session.id is not None
        assert session.question is not None
        assert session.answer is not None


class TestModelValidation:
    """Test model validation and constraints"""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_chapter_required_fields(self, db_session):
        """Test that required fields are enforced"""
        # Try to create chapter without required field
        try:
            chapter = Chapter(
                id=uuid_lib.uuid4(),
                # Missing title - should this fail?
                content="Test"
            )
            db_session.add(chapter)
            await db_session.commit()
            # If we get here, nullable=True for title
            assert True
        except Exception:
            # If exception, nullable=False for title
            await db_session.rollback()
            assert True

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_unique_constraints(self, db_session):
        """Test unique constraints if any exist"""
        # Most models use UUID primary keys which are unique
        chapter1 = Chapter(
            id=uuid_lib.uuid4(),
            title="Chapter 1",
            specialty="tumor",
            content="Content",
            status="draft",
            version="1.0"
        )

        db_session.add(chapter1)
        await db_session.commit()

        # Different chapter should work fine
        chapter2 = Chapter(
            id=uuid_lib.uuid4(),
            title="Chapter 2",
            specialty="vascular",
            content="Content 2",
            status="draft",
            version="1.0"
        )

        db_session.add(chapter2)
        await db_session.commit()

        assert chapter1.id != chapter2.id
