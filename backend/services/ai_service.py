"""
AI Service - Simplified
Handles interactions with AI models (OpenAI, Claude, Gemini)
"""
import os
from typing import Dict, Any, Optional, List

# Try to import AI libraries, use mocks if not available
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class AIService:
    """Service for AI model interactions"""

    def __init__(self):
        # Initialize API clients
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.google_key = os.getenv("GOOGLE_API_KEY")

        if OPENAI_AVAILABLE and self.openai_key:
            openai.api_key = self.openai_key

        if ANTHROPIC_AVAILABLE and self.anthropic_key:
            self.anthropic = Anthropic(api_key=self.anthropic_key)
        else:
            self.anthropic = None

        if GEMINI_AVAILABLE and self.google_key:
            genai.configure(api_key=self.google_key)

    async def synthesize_content(
        self,
        chapter_title: str,
        specialty: str,
        references: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Synthesize chapter content from references"""

        # Prepare context
        ref_context = "\n\n".join([
            f"Reference: {ref['title']}\n{ref.get('content', '')[:1500]}"
            for ref in references[:5]  # Limit to 5 refs to avoid token overflow
        ])

        prompt = f"""
Synthesize a comprehensive neurosurgical chapter section on: {chapter_title}
Specialty: {specialty}

Based on these references:
{ref_context}

Create a well-structured section covering:
1. Current evidence
2. Technical considerations
3. Clinical outcomes
4. Recommendations

Maintain scientific accuracy and cite evidence.
        """

        result = await self.generate_with_gpt4(prompt)

        return {
            "content": result["text"],
            "model": result["model"],
            "summary": result.get("text", "")[:500]
        }

    async def generate_synthesis(
        self,
        prompt: str,
        model: str = "gpt-4"
    ) -> Dict[str, Any]:
        """Generate synthesis using specified model"""

        if model.startswith("gpt"):
            return await self.generate_with_gpt4(prompt)
        elif model.startswith("claude"):
            return await self.generate_with_claude(prompt)
        elif model.startswith("gemini"):
            return await self.generate_with_gemini(prompt)
        else:
            return await self.generate_with_gpt4(prompt)

    async def generate_answer(
        self,
        prompt: str,
        model: str = "gpt-4"
    ) -> Dict[str, Any]:
        """Generate answer to question"""
        return await self.generate_synthesis(prompt, model)

    async def generate_with_gpt4(self, prompt: str) -> Dict[str, Any]:
        """Generate using OpenAI GPT-4"""

        if not OPENAI_AVAILABLE or not self.openai_key:
            return self._mock_response(prompt, "gpt-4")

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a neurosurgical knowledge expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )

            return {
                "text": response.choices[0].message.content,
                "model": "gpt-4",
                "token_count": response.usage.total_tokens
            }
        except Exception as e:
            print(f"OpenAI error: {e}")
            return self._mock_response(prompt, "gpt-4")

    async def generate_with_claude(self, prompt: str) -> Dict[str, Any]:
        """Generate using Anthropic Claude"""

        if not ANTHROPIC_AVAILABLE or not self.anthropic_key:
            return self._mock_response(prompt, "claude-3")

        try:
            message = self.anthropic.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            return {
                "text": message.content[0].text,
                "model": "claude-3-sonnet",
                "token_count": message.usage.input_tokens + message.usage.output_tokens
            }
        except Exception as e:
            print(f"Claude error: {e}")
            return self._mock_response(prompt, "claude-3")

    async def generate_with_gemini(self, prompt: str) -> Dict[str, Any]:
        """Generate using Google Gemini"""

        if not GEMINI_AVAILABLE or not self.google_key:
            return self._mock_response(prompt, "gemini")

        try:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)

            return {
                "text": response.text,
                "model": "gemini-pro",
                "token_count": 0  # Gemini doesn't provide token count easily
            }
        except Exception as e:
            print(f"Gemini error: {e}")
            return self._mock_response(prompt, "gemini")

    def _mock_response(self, prompt: str, model: str) -> Dict[str, Any]:
        """Mock response when API keys not available"""
        return {
            "text": f"[Mock {model} response for development]\n\nThis is a simulated response. Configure API keys for real AI integration.\n\nPrompt received: {prompt[:200]}...",
            "model": f"{model}-mock",
            "token_count": 100
        }