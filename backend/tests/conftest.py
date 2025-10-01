"""
Pytest configuration and fixtures for Neurosurgical Knowledge System
"""
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

# Import models and base
from models import Base
from config.settings_simplified import settings


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def async_client():
    """Create async HTTP client for API tests"""
    from httpx import AsyncClient, ASGITransport
    from main_simplified import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine (in-memory SQLite)"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session"""
    AsyncSessionLocal = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture
def sample_chapter_data():
    """Sample chapter data for testing"""
    return {
        "title": "Glioblastoma Management",
        "specialty": "tumor",
        "content": "Comprehensive guide to glioblastoma treatment...",
        "status": "draft",
        "version": "1.0"
    }


@pytest.fixture
def sample_reference_data():
    """Sample reference data for testing"""
    return {
        "title": "Neurosurgery Textbook",
        "authors": ["Dr. Smith", "Dr. Jones"],
        "publication_year": 2024,
        "type": "textbook",
        "content": "Detailed neurosurgical content..."
    }


@pytest.fixture
def sample_qa_data():
    """Sample Q&A data for testing"""
    return {
        "question": "What are the indications for craniotomy?",
        "specialty": "general",
        "context": "Clinical decision making"
    }


@pytest.fixture
def mock_ai_response():
    """Mock AI service response"""
    return {
        "content": "This is a comprehensive neurosurgical response covering all aspects of the query with evidence-based information and clinical guidelines.",
        "model": "gpt-4-mock",
        "tokens_used": 150,
        "success": True
    }


@pytest.fixture
def mock_synthesis_result():
    """Mock synthesis service result"""
    return {
        "sections": {
            "Introduction": "Comprehensive introduction to the topic...",
            "Clinical Presentation": "Detailed clinical presentation...",
            "Diagnosis": "Diagnostic approaches and imaging...",
            "Treatment": "Treatment options and surgical techniques...",
            "Outcomes": "Expected outcomes and complications..."
        },
        "references_used": 10,
        "evidence_level": "I-A",
        "word_count": 2500
    }


# Markers for categorizing tests
def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line("markers", "unit: Unit tests (fast, isolated)")
    config.addinivalue_line("markers", "integration: Integration tests (database, external services)")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "ai: Tests requiring AI API keys")
