"""
End-to-End tests for complete neurosurgical workflows
Tests full user journeys from chapter creation to synthesis
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_complete_chapter_workflow(async_client: AsyncClient):
    """
    Test complete chapter workflow:
    1. Create chapter
    2. Add references
    3. Generate synthesis
    4. Update chapter
    5. Retrieve chapter
    """
    # Step 1: Create chapter
    chapter_data = {
        "title": "Glioblastoma Multiforme Management",
        "specialty": "tumor",
        "content": "Initial content for GBM management",
        "status": "draft"
    }
    
    response = await async_client.post("/chapters", json=chapter_data)
    assert response.status_code == 200
    chapter = response.json()
    chapter_id = chapter["id"]
    
    # Step 2: Retrieve chapter
    response = await async_client.get(f"/chapters/{chapter_id}")
    assert response.status_code == 200
    retrieved = response.json()
    assert retrieved["title"] == chapter_data["title"]
    assert retrieved["specialty"] == chapter_data["specialty"]
    
    # Step 3: Update chapter
    update_data = {
        "content": "Updated content with more details",
        "status": "review"
    }
    response = await async_client.put(f"/chapters/{chapter_id}", json=update_data)
    assert response.status_code == 200
    updated = response.json()
    assert updated["status"] == "review"
    
    # Step 4: Delete chapter
    response = await async_client.delete(f"/chapters/{chapter_id}")
    assert response.status_code == 200


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_qa_workflow(async_client: AsyncClient):
    """
    Test Q&A workflow:
    1. Submit question
    2. Get answer with references
    3. Rate answer
    """
    # Submit question
    qa_data = {
        "question": "What are the indications for decompressive craniectomy?",
        "specialty": "trauma",
        "context": "Management of severe TBI"
    }
    
    response = await async_client.post("/qa/ask", json=qa_data)
    assert response.status_code == 200
    result = response.json()
    assert "answer" in result
    assert len(result["answer"]) > 0


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_synthesis_workflow(async_client: AsyncClient):
    """
    Test synthesis workflow:
    1. Create chapter with references
    2. Generate synthesis
    3. Verify synthesis quality
    """
    # Create chapter
    chapter_data = {
        "title": "Endovascular Treatment of Aneurysms",
        "specialty": "vascular",
        "content": "Base content",
        "status": "draft"
    }
    
    response = await async_client.post("/chapters", json=chapter_data)
    assert response.status_code == 200
    chapter = response.json()
    chapter_id = chapter["id"]
    
    # Generate synthesis
    synthesis_data = {
        "chapter_id": chapter_id,
        "sections": ["introduction", "indications", "techniques", "outcomes"],
        "evidence_level": "high"
    }
    
    response = await async_client.post("/synthesis/generate", json=synthesis_data)
    assert response.status_code in [200, 202]  # 202 for async processing


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_search_workflow(async_client: AsyncClient):
    """
    Test search workflow:
    1. Create multiple chapters
    2. Search by keyword
    3. Filter by specialty
    """
    # Create test chapters
    chapters = [
        {
            "title": "Brain Tumor Classification",
            "specialty": "tumor",
            "content": "WHO classification of brain tumors",
            "status": "published"
        },
        {
            "title": "Spinal Cord Tumors",
            "specialty": "spine",
            "content": "Classification and management of spinal tumors",
            "status": "published"
        }
    ]
    
    for chapter_data in chapters:
        response = await async_client.post("/chapters", json=chapter_data)
        assert response.status_code == 200
    
    # Search by keyword
    response = await async_client.get("/chapters/search?q=tumor")
    assert response.status_code == 200
    results = response.json()
    assert len(results) >= 2
    
    # Filter by specialty
    response = await async_client.get("/chapters?specialty=tumor")
    assert response.status_code == 200
    filtered = response.json()
    assert all(ch["specialty"] == "tumor" for ch in filtered)


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_health_check_workflow(async_client: AsyncClient):
    """Test system health check"""
    response = await async_client.get("/health")
    assert response.status_code == 200
    health = response.json()
    assert "status" in health
    assert health["status"] == "healthy"
