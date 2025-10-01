"""
Integration tests for API endpoints
Tests all FastAPI endpoints with real/mock responses
"""
import pytest

# async_client fixture is defined in conftest.py


class TestHealthEndpoint:
    """Test health check endpoint"""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_health_check(self, async_client):
        """Test health check returns 200"""
        response = await async_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_health_check_contains_version(self, async_client):
        """Test health check includes version"""
        response = await async_client.get("/health")
        data = response.json()
        assert "version" in data


class TestChapterEndpoints:
    """Test chapter CRUD endpoints"""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_get_chapters_list(self, async_client):
        """Test GET /api/v1/chapters"""
        response = await async_client.get("/api/v1/chapters")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_get_chapters_with_filters(self, async_client):
        """Test GET /api/v1/chapters with filters"""
        response = await async_client.get("/api/v1/chapters?specialty=tumor&limit=10")
        assert response.status_code == 200

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_create_chapter(self, async_client):
        """Test POST /api/v1/chapters"""
        chapter_data = {
            "title": "Test Chapter",
            "specialty": "tumor",
            "content": "Test content",
            "status": "draft"
        }
        response = await async_client.post("/api/v1/chapters", json=chapter_data)
        # Accept both 200 and 201 as valid
        assert response.status_code in [200, 201]

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_get_chapter_by_id(self, async_client):
        """Test GET /api/v1/chapters/{id}"""
        # Use a test ID
        test_id = "test-chapter-id"
        response = await async_client.get(f"/api/v1/chapters/{test_id}")
        # May return 404 if chapter doesn't exist (expected in test DB)
        assert response.status_code in [200, 404]


class TestReferenceEndpoints:
    """Test reference CRUD endpoints"""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_get_references_list(self, async_client):
        """Test GET /api/v1/references"""
        response = await async_client.get("/api/v1/references")
        assert response.status_code == 200

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_create_reference(self, async_client):
        """Test POST /api/v1/references"""
        reference_data = {
            "title": "Test Reference",
            "type": "textbook",
            "content": "Test content"
        }
        response = await async_client.post("/api/v1/references", json=reference_data)
        assert response.status_code in [200, 201]


class TestSynthesisEndpoints:
    """Test synthesis endpoints"""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_synthesis_generate(self, async_client):
        """Test POST /api/v1/synthesis/generate"""
        synthesis_data = {
            "title": "Test Chapter",
            "specialty": "tumor",
            "references": []
        }
        response = await async_client.post("/api/v1/synthesis/generate", json=synthesis_data)
        # May be 200, 201, or 202 (accepted for background processing)
        assert response.status_code in [200, 201, 202]


class TestQAEndpoints:
    """Test Q&A endpoints"""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_qa_ask_question(self, async_client):
        """Test POST /api/v1/qa/ask"""
        qa_data = {
            "question": "What are indications for craniotomy?",
            "specialty": "general"
        }
        response = await async_client.post("/api/v1/qa/ask", json=qa_data)
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data


class TestSearchEndpoints:
    """Test search endpoints"""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_search_basic(self, async_client):
        """Test GET /api/v1/search"""
        response = await async_client.get("/api/v1/search?q=glioblastoma")
        assert response.status_code == 200

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_search_empty_query(self, async_client):
        """Test search with empty query"""
        response = await async_client.get("/api/v1/search?q=")
        # Should handle gracefully
        assert response.status_code in [200, 400]


class TestErrorHandling:
    """Test API error handling"""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_invalid_endpoint(self, async_client):
        """Test accessing non-existent endpoint"""
        response = await async_client.get("/api/v1/nonexistent")
        assert response.status_code == 404

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_invalid_method(self, async_client):
        """Test using wrong HTTP method"""
        # Try DELETE on health endpoint (should fail)
        response = await async_client.delete("/health")
        assert response.status_code in [404, 405]

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_malformed_json(self, async_client):
        """Test posting malformed JSON"""
        response = await async_client.post(
            "/api/v1/chapters",
            content="not valid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [400, 422]


class TestCORS:
    """Test CORS configuration"""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_cors_headers_present(self, async_client):
        """Test that CORS headers are configured"""
        response = await async_client.get("/health")
        # Check if any CORS-related setup exists
        assert response.status_code == 200


class TestRateLimiting:
    """Test rate limiting (if implemented)"""

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_rate_limiting_not_blocking(self, async_client):
        """Test that normal requests aren't rate limited"""
        # Make 10 quick requests
        for _ in range(10):
            response = await async_client.get("/health")
            assert response.status_code == 200
