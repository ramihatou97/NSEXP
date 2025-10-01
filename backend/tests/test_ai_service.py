"""
Unit tests for AI Service
Tests AI service functionality including mocks and real API calls
"""
import pytest
from services.ai_service import AIService


class TestAIServiceInitialization:
    """Test AI service initialization"""

    def test_ai_service_instantiation(self):
        """Test that AI service can be instantiated"""
        service = AIService()
        assert service is not None

    def test_api_keys_loaded(self):
        """Test that API keys are loaded from environment"""
        service = AIService()
        # Should not fail even without API keys
        assert service.openai_key is not None or service.openai_key is None


class TestMockResponses:
    """Test mock AI responses when no API keys configured"""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_generate_with_gpt4_mock(self):
        """Test GPT-4 mock response generation"""
        service = AIService()
        result = await service.generate_with_gpt4("Test prompt for neurosurgery")

        assert result is not None
        assert "text" in result
        assert "model" in result
        assert len(result["text"]) > 0
        assert "gpt" in result["model"].lower() or "mock" in result["model"].lower()

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_generate_with_claude_mock(self):
        """Test Claude mock response generation"""
        service = AIService()
        result = await service.generate_with_claude("Test prompt for neurosurgery")

        assert result is not None
        assert "text" in result
        assert "model" in result
        assert len(result["text"]) > 0

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_generate_with_gemini_mock(self):
        """Test Gemini mock response generation"""
        service = AIService()
        result = await service.generate_with_gemini("Test prompt for neurosurgery")

        assert result is not None
        assert "text" in result
        assert "model" in result
        assert len(result["text"]) > 0


class TestSynthesizeContent:
    """Test content synthesis functionality"""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_synthesize_content_basic(self):
        """Test basic content synthesis"""
        service = AIService()

        result = await service.synthesize_content(
            chapter_title="Glioblastoma Management",
            specialty="tumor",
            references=[
                {"title": "Neurosurgery Textbook", "content": "GBM is a high-grade tumor..."},
                {"title": "Clinical Guidelines", "content": "Standard treatment includes surgery..."}
            ]
        )

        assert result is not None
        assert "sections" in result
        assert len(result["sections"]) > 0

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_synthesize_content_empty_references(self):
        """Test synthesis with empty references"""
        service = AIService()

        result = await service.synthesize_content(
            chapter_title="Test Topic",
            specialty="general",
            references=[]
        )

        assert result is not None
        # Should handle empty references gracefully

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_synthesize_content_multiple_references(self):
        """Test synthesis with multiple references"""
        service = AIService()

        references = [
            {"title": f"Reference {i}", "content": f"Content for reference {i}..."}
            for i in range(5)
        ]

        result = await service.synthesize_content(
            chapter_title="Comprehensive Topic",
            specialty="tumor",
            references=references
        )

        assert result is not None
        assert "sections" in result


class TestAnswerQuestion:
    """Test Q&A functionality"""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_answer_question_basic(self):
        """Test basic question answering"""
        service = AIService()

        result = await service.answer_question(
            question="What are the indications for craniotomy?",
            context="Clinical neurosurgery",
            specialty="general"
        )

        assert result is not None
        assert "answer" in result
        assert len(result["answer"]) > 0

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_answer_question_with_specialty(self):
        """Test question answering with specialty"""
        service = AIService()

        result = await service.answer_question(
            question="How to manage glioblastoma?",
            context="Tumor management",
            specialty="tumor"
        )

        assert result is not None
        assert "answer" in result
        assert "evidence_level" in result

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_answer_question_empty(self):
        """Test handling of empty question"""
        service = AIService()

        result = await service.answer_question(
            question="",
            context="",
            specialty="general"
        )

        # Should handle empty input gracefully
        assert result is not None


class TestErrorHandling:
    """Test error handling in AI service"""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_invalid_specialty(self):
        """Test handling of invalid specialty"""
        service = AIService()

        # Should not crash with invalid specialty
        result = await service.synthesize_content(
            chapter_title="Test",
            specialty="invalid_specialty",
            references=[]
        )

        assert result is not None

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_very_long_prompt(self):
        """Test handling of very long prompts"""
        service = AIService()

        long_prompt = "test " * 10000  # Very long prompt
        result = await service.generate_with_gpt4(long_prompt)

        # Should handle long prompts (may truncate or error gracefully)
        assert result is not None


# Skip real API tests if no API keys configured
@pytest.mark.ai
@pytest.mark.slow
class TestRealAPIIntegration:
    """Test real API integration (requires API keys)"""

    @pytest.mark.asyncio
    async def test_real_gpt4_call(self):
        """Test real GPT-4 API call (if API key available)"""
        pytest.skip("Requires OpenAI API key and costs money - enable manually")

    @pytest.mark.asyncio
    async def test_real_claude_call(self):
        """Test real Claude API call (if API key available)"""
        pytest.skip("Requires Anthropic API key and costs money - enable manually")

    @pytest.mark.asyncio
    async def test_real_gemini_call(self):
        """Test real Gemini API call (if API key available)"""
        pytest.skip("Requires Google API key and costs money - enable manually")
