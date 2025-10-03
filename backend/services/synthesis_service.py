"""
Simplified Synthesis Service - Single User
Handles AI-powered content synthesis for neurosurgical knowledge
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from services.ai_service import AIService


class SynthesisService:
    """Service for synthesizing neurosurgical content using AI"""

    def __init__(self):
        self.ai_service = AIService()

    async def synthesize_content(
        self,
        references: List[Dict[str, Any]],
        topic: str,
        specialty: str,
        focus_areas: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Synthesize content from multiple references"""

        # Prepare reference context
        reference_context = self._prepare_reference_context(references)

        # Generate synthesis prompt
        prompt = self._create_synthesis_prompt(
            topic=topic,
            specialty=specialty,
            references=reference_context,
            focus_areas=focus_areas
        )

        # Get AI synthesis
        synthesis = await self.ai_service.generate_synthesis(
            prompt=prompt,
            model="gpt-4"
        )

        return {
            "content": synthesis["text"],
            "summary": synthesis.get("summary", ""),
            "key_points": synthesis.get("key_points", []),
            "references_used": [ref["id"] for ref in references],
            "metadata": {
                "topic": topic,
                "specialty": specialty,
                "focus_areas": focus_areas,
                "model": synthesis.get("model", "gpt-4"),
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "token_count": synthesis.get("token_count", 0)
            }
        }

    async def compare_techniques(
        self,
        technique_a: Dict[str, Any],
        technique_b: Dict[str, Any],
        specialty: str
    ) -> Dict[str, Any]:
        """Compare two surgical techniques"""

        prompt = f"""
        Compare these two neurosurgical techniques for {specialty}:

        Technique A: {technique_a['name']}
        Description: {technique_a['description']}

        Technique B: {technique_b['name']}
        Description: {technique_b['description']}

        Provide a detailed comparison covering:
        1. Indications
        2. Advantages and disadvantages
        3. Technical considerations
        4. Outcomes
        5. Complications
        6. Recommendations for use
        """

        comparison = await self.ai_service.generate_synthesis(
            prompt=prompt,
            model="gpt-4"
        )

        return {
            "comparison": comparison["text"],
            "technique_a": technique_a["name"],
            "technique_b": technique_b["name"],
            "specialty": specialty,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

    async def extract_key_concepts(
        self,
        content: str,
        specialty: str
    ) -> Dict[str, Any]:
        """Extract key concepts from content"""

        prompt = f"""
        Extract key neurosurgical concepts from this {specialty} content:

        {content[:4000]}  # Limit to avoid token overflow

        Identify:
        1. Main surgical techniques mentioned
        2. Anatomical structures involved
        3. Clinical indications
        4. Potential complications
        5. Evidence quality (if mentioned)
        """

        concepts = await self.ai_service.generate_synthesis(
            prompt=prompt,
            model="gpt-3.5-turbo"
        )

        return {
            "concepts": concepts.get("key_points", []),
            "techniques": concepts.get("techniques", []),
            "anatomy": concepts.get("anatomy", []),
            "specialty": specialty,
            "extracted_at": datetime.now(timezone.utc).isoformat()
        }

    async def generate_summary(
        self,
        content: str,
        max_length: int = 500
    ) -> str:
        """Generate a concise summary of content"""

        prompt = f"""
        Provide a concise neurosurgical summary (max {max_length} chars) of:

        {content[:8000]}

        Focus on: techniques, indications, outcomes, and key clinical points.
        """

        summary = await self.ai_service.generate_synthesis(
            prompt=prompt,
            model="gpt-3.5-turbo"
        )

        return summary["text"][:max_length]

    def _prepare_reference_context(self, references: List[Dict[str, Any]]) -> str:
        """Prepare reference context for synthesis"""
        context_parts = []

        for i, ref in enumerate(references, 1):
            ref_text = f"""
Reference {i}: {ref['title']}
Authors: {', '.join(ref.get('authors', []))}
Content: {ref.get('content', '')[:2000]}
---
            """
            context_parts.append(ref_text)

        return "\n".join(context_parts)

    def _create_synthesis_prompt(
        self,
        topic: str,
        specialty: str,
        references: str,
        focus_areas: Optional[List[str]] = None
    ) -> str:
        """Create a synthesis prompt"""

        focus_text = ""
        if focus_areas:
            focus_text = f"\n\nSpecial focus on: {', '.join(focus_areas)}"

        prompt = f"""
You are a neurosurgical knowledge synthesis expert specializing in {specialty}.

Synthesize a comprehensive chapter section on: {topic}

Based on these references:
{references}
{focus_text}

Structure your synthesis:
1. Introduction and context
2. Current evidence and techniques
3. Technical considerations
4. Clinical outcomes
5. Complications and management
6. Summary and recommendations

Maintain scientific rigor and cite evidence appropriately.
        """

        return prompt