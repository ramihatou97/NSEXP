"""
Simplified Q&A Service - Single User
Handles question-answering for neurosurgical queries
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

from services.ai_service import AIService


class QAService:
    """Service for answering neurosurgical questions"""

    def __init__(self):
        self.ai_service = AIService()

    async def answer_question(
        self,
        question: str,
        context: Optional[str] = None,
        specialty: Optional[str] = None,
        model: str = "gpt-4"
    ) -> Dict[str, Any]:
        """Answer a neurosurgical question"""

        prompt = self._create_qa_prompt(question, context, specialty)

        answer = await self.ai_service.generate_answer(
            prompt=prompt,
            model=model
        )

        return {
            "question": question,
            "answer": answer["text"],
            "confidence": answer.get("confidence", 0.8),
            "sources": answer.get("sources", []),
            "specialty": specialty,
            "model": model,
            "answered_at": datetime.utcnow().isoformat()
        }

    async def answer_with_references(
        self,
        question: str,
        references: List[Dict[str, Any]],
        specialty: Optional[str] = None
    ) -> Dict[str, Any]:
        """Answer question using specific references"""

        # Prepare context from references
        context = self._prepare_reference_context(references)

        prompt = f"""
Based on these neurosurgical references:

{context}

Answer this question: {question}

Provide:
1. Direct answer
2. Supporting evidence from the references
3. Clinical implications
4. Any caveats or limitations
        """

        answer = await self.ai_service.generate_answer(
            prompt=prompt,
            model="gpt-4"
        )

        return {
            "question": question,
            "answer": answer["text"],
            "references_used": [ref["id"] for ref in references],
            "specialty": specialty,
            "answered_at": datetime.utcnow().isoformat()
        }

    async def generate_follow_up_questions(
        self,
        original_question: str,
        answer: str,
        count: int = 3
    ) -> List[str]:
        """Generate follow-up questions"""

        prompt = f"""
Given this neurosurgical Q&A:

Question: {original_question}
Answer: {answer}

Generate {count} relevant follow-up questions that would deepen understanding.
        """

        result = await self.ai_service.generate_answer(
            prompt=prompt,
            model="gpt-3.5-turbo"
        )

        # Parse follow-up questions from response
        questions = result["text"].split("\n")
        questions = [q.strip().lstrip("0123456789.-) ") for q in questions if q.strip()]

        return questions[:count]

    async def validate_answer(
        self,
        question: str,
        answer: str,
        references: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Validate an answer against references"""

        ref_context = ""
        if references:
            ref_context = f"\n\nReferences:\n{self._prepare_reference_context(references)}"

        prompt = f"""
Validate this neurosurgical answer:

Question: {question}
Answer: {answer}
{ref_context}

Assess:
1. Accuracy (0-1 score)
2. Completeness (0-1 score)
3. Clinical relevance (0-1 score)
4. Evidence support (0-1 score)
5. Any inaccuracies or concerns

Provide JSON format response.
        """

        validation = await self.ai_service.generate_answer(
            prompt=prompt,
            model="gpt-4"
        )

        return {
            "validated": True,
            "scores": validation.get("scores", {}),
            "concerns": validation.get("concerns", []),
            "validated_at": datetime.utcnow().isoformat()
        }

    def _create_qa_prompt(
        self,
        question: str,
        context: Optional[str],
        specialty: Optional[str]
    ) -> str:
        """Create Q&A prompt"""

        specialty_text = f" in {specialty}" if specialty else ""
        context_text = f"\n\nContext:\n{context}" if context else ""

        prompt = f"""
You are a neurosurgical expert{specialty_text}.

Question: {question}
{context_text}

Provide a comprehensive, evidence-based answer including:
1. Direct answer
2. Clinical context
3. Technical details if relevant
4. Evidence level
5. Practical implications
        """

        return prompt

    def _prepare_reference_context(self, references: List[Dict[str, Any]]) -> str:
        """Prepare reference context"""
        context_parts = []

        for i, ref in enumerate(references, 1):
            ref_text = f"[{i}] {ref['title']}: {ref.get('content', '')[:1000]}"
            context_parts.append(ref_text)

        return "\n\n".join(context_parts)


# Simplified function exports for main_simplified.py
async def process_question(question: str, chapter_id: str = None, context: str = None) -> Dict[str, Any]:
    """
    Process a question and return answer
    Simplified wrapper function for easy use
    """
    try:
        qa_service = QAService()
        result = await qa_service.answer_question(
            question=question,
            context=context
        )
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": None
        }