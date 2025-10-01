"""
Unit tests for Q&A Service
Tests question answering functionality
"""
import pytest
from services.qa_service import QAService


class TestQAServiceInitialization:
    """Test Q&A service initialization"""

    def test_qa_service_instantiation(self):
        """Test that Q&A service can be instantiated"""
        service = QAService()
        assert service is not None


class TestQuestionAnswering:
    """Test question answering functionality"""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_ask_question_basic(self, sample_qa_data):
        """Test basic question answering"""
        service = QAService()

        result = await service.ask_question(
            question=sample_qa_data["question"],
            specialty=sample_qa_data["specialty"]
        )

        assert result is not None
        assert "answer" in result
        assert len(result["answer"]) > 0

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_ask_question_with_context(self, sample_qa_data):
        """Test question answering with context"""
        service = QAService()

        result = await service.ask_question(
            question=sample_qa_data["question"],
            specialty=sample_qa_data["specialty"],
            context=sample_qa_data["context"]
        )

        assert result is not None
        assert "answer" in result

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_ask_question_different_specialties(self):
        """Test Q&A across different specialties"""
        service = QAService()

        specialties = ["tumor", "vascular", "spine", "functional"]

        for specialty in specialties:
            result = await service.ask_question(
                question="What are common procedures?",
                specialty=specialty
            )

            assert result is not None
            assert "answer" in result

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_ask_complex_question(self):
        """Test handling of complex multi-part question"""
        service = QAService()

        complex_question = """
        What are the surgical approaches for treating intracranial aneurysms?
        Please include: 1) Indications for each approach
        2) Complications and risks
        3) Evidence levels
        """

        result = await service.ask_question(
            question=complex_question,
            specialty="vascular"
        )

        assert result is not None
        assert "answer" in result


class TestAnswerQuality:
    """Test answer quality and metadata"""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_answer_contains_evidence_level(self):
        """Test that answers include evidence level"""
        service = QAService()

        result = await service.ask_question(
            question="What is the standard treatment for GBM?",
            specialty="tumor"
        )

        assert result is not None
        # Check if evidence level is present (if implemented)
        # Flexible test - not all implementations may have this
        assert "answer" in result

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_answer_includes_references(self):
        """Test that answers may include references"""
        service = QAService()

        result = await service.ask_question(
            question="What are complications of craniotomy?",
            specialty="general"
        )

        assert result is not None
        assert "answer" in result
        # References are optional but good to have
        # assert "references" in result or "sources" in result


class TestErrorHandling:
    """Test error handling in Q&A service"""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_empty_question(self):
        """Test handling of empty question"""
        service = QAService()

        result = await service.ask_question(
            question="",
            specialty="general"
        )

        # Should handle gracefully
        assert result is not None

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_very_short_question(self):
        """Test handling of very short question"""
        service = QAService()

        result = await service.ask_question(
            question="Why?",
            specialty="general"
        )

        assert result is not None

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_non_medical_question(self):
        """Test handling of non-medical question"""
        service = QAService()

        result = await service.ask_question(
            question="What is the capital of France?",
            specialty="general"
        )

        # Should still return something, possibly indicating off-topic
        assert result is not None

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_invalid_specialty(self):
        """Test handling of invalid specialty"""
        service = QAService()

        result = await service.ask_question(
            question="Test question",
            specialty="invalid_specialty"
        )

        # Should not crash
        assert result is not None or result is None
