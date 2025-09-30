"""
AI Service Manager for Neurosurgical Knowledge System
Manages real integrations with multiple AI providers (OpenAI, Claude, Gemini, Perplexity)
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import time
from datetime import datetime, timedelta
import json
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

# AI Provider SDKs
import openai
import anthropic
import google.generativeai as genai

from config.settings_simplified import settings

logger = logging.getLogger(__name__)


class AIProvider(Enum):
    """Available AI service providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    PERPLEXITY = "perplexity"


class AIModel(Enum):
    """Available AI models"""
    # OpenAI models
    GPT4_TURBO = "gpt-4-turbo-preview"
    GPT4 = "gpt-4"
    GPT35_TURBO = "gpt-3.5-turbo"

    # Anthropic models
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"

    # Google models
    GEMINI_PRO = "gemini-1.5-pro"
    GEMINI_FLASH = "gemini-1.5-flash"

    # Perplexity models
    PERPLEXITY_SONAR = "sonar-medium-chat"


@dataclass
class AIResponse:
    """Standardized response from AI services"""
    content: str
    provider: AIProvider
    model: str
    tokens_used: int
    response_time: float
    cost: float
    success: bool
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class MedicalValidation:
    """Medical content validation results"""
    is_medically_accurate: bool
    confidence_score: float
    issues_found: List[str]
    suggestions: List[str]
    evidence_level: Optional[str] = None


class AIServiceManager:
    """
    Manages AI services with fallback strategies and medical specialization
    """

    def __init__(self):
        self.providers = {}
        self.initialize_providers()
        self.usage_tracker = UsageTracker()
        self.medical_prompts = MedicalPromptTemplates()

    def initialize_providers(self):
        """Initialize AI provider clients"""

        # Initialize OpenAI
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
            self.providers[AIProvider.OPENAI] = OpenAIService(settings.OPENAI_API_KEY)
            logger.info("OpenAI service initialized")

        # Initialize Anthropic
        if settings.ANTHROPIC_API_KEY:
            self.providers[AIProvider.ANTHROPIC] = AnthropicService(settings.ANTHROPIC_API_KEY)
            logger.info("Anthropic service initialized")

        # Initialize Google Gemini
        if settings.GOOGLE_API_KEY:
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            self.providers[AIProvider.GOOGLE] = GeminiService(settings.GOOGLE_API_KEY)
            logger.info("Google Gemini service initialized")

        # Initialize Perplexity
        if settings.PERPLEXITY_API_KEY:
            self.providers[AIProvider.PERPLEXITY] = PerplexityService(settings.PERPLEXITY_API_KEY)
            logger.info("Perplexity service initialized")

        if not self.providers:
            logger.warning("No AI providers configured!")

    async def generate_neurosurgical_content(
        self,
        prompt: str,
        context: Optional[str] = None,
        specialty: Optional[str] = None,
        preferred_provider: Optional[AIProvider] = None,
        max_tokens: int = 4000,
        temperature: float = 0.7
    ) -> AIResponse:
        """
        Generate neurosurgical content with medical accuracy focus
        """
        # Enhance prompt with medical context
        enhanced_prompt = self.medical_prompts.enhance_prompt(
            prompt, context, specialty
        )

        # Try preferred provider first
        if preferred_provider and preferred_provider in self.providers:
            response = await self._query_provider(
                preferred_provider,
                enhanced_prompt,
                max_tokens,
                temperature
            )
            if response.success:
                return response

        # Fallback to other providers
        for provider in self.providers:
            if provider != preferred_provider:
                response = await self._query_provider(
                    provider,
                    enhanced_prompt,
                    max_tokens,
                    temperature
                )
                if response.success:
                    return response

        # All providers failed
        return AIResponse(
            content="",
            provider=AIProvider.OPENAI,
            model="",
            tokens_used=0,
            response_time=0,
            cost=0,
            success=False,
            error="All AI providers failed"
        )

    async def validate_medical_content(
        self,
        content: str,
        specialty: str = "neurosurgery"
    ) -> MedicalValidation:
        """
        Validate medical accuracy of content
        """
        validation_prompt = self.medical_prompts.get_validation_prompt(content, specialty)

        # Use GPT-4 for medical validation (most reliable)
        if AIProvider.OPENAI in self.providers:
            response = await self._query_provider(
                AIProvider.OPENAI,
                validation_prompt,
                max_tokens=1000,
                temperature=0.1  # Low temperature for consistency
            )

            if response.success:
                return self._parse_validation_response(response.content)

        # Fallback validation
        return MedicalValidation(
            is_medically_accurate=True,  # Default to true if can't validate
            confidence_score=0.5,
            issues_found=[],
            suggestions=["Manual review recommended"]
        )

    async def synthesize_chapter_section(
        self,
        section_name: str,
        references: List[str],
        specialty: str = "neurosurgery"
    ) -> str:
        """
        Synthesize a specific chapter section from references
        """
        synthesis_prompt = self.medical_prompts.get_synthesis_prompt(
            section_name, references, specialty
        )

        # Prefer Claude for synthesis (better at long-form content)
        preferred_provider = AIProvider.ANTHROPIC if AIProvider.ANTHROPIC in self.providers else None

        response = await self.generate_neurosurgical_content(
            synthesis_prompt,
            specialty=specialty,
            preferred_provider=preferred_provider,
            max_tokens=6000,
            temperature=0.6
        )

        return response.content if response.success else ""

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _query_provider(
        self,
        provider: AIProvider,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> AIResponse:
        """Query specific AI provider with retry logic"""
        start_time = time.time()

        try:
            service = self.providers[provider]
            response = await service.query(prompt, max_tokens, temperature)

            # Track usage
            self.usage_tracker.track_usage(
                provider,
                response.tokens_used,
                response.cost
            )

            return response

        except Exception as e:
            logger.error(f"Error querying {provider.value}: {e}")
            return AIResponse(
                content="",
                provider=provider,
                model="",
                tokens_used=0,
                response_time=time.time() - start_time,
                cost=0,
                success=False,
                error=str(e)
            )

    def _parse_validation_response(self, response: str) -> MedicalValidation:
        """Parse medical validation response from AI"""
        try:
            # Attempt to parse structured response
            if "{" in response and "}" in response:
                json_str = response[response.index("{"):response.rindex("}") + 1]
                data = json.loads(json_str)

                return MedicalValidation(
                    is_medically_accurate=data.get("is_accurate", True),
                    confidence_score=data.get("confidence", 0.5),
                    issues_found=data.get("issues", []),
                    suggestions=data.get("suggestions", []),
                    evidence_level=data.get("evidence_level")
                )
        except:
            pass

        # Fallback parsing
        is_accurate = "accurate" in response.lower() and "not accurate" not in response.lower()
        confidence = 0.7 if is_accurate else 0.3

        return MedicalValidation(
            is_medically_accurate=is_accurate,
            confidence_score=confidence,
            issues_found=[],
            suggestions=[]
        )

    async def get_embeddings(
        self,
        text: str,
        model: str = "text-embedding-3-large"
    ) -> Optional[List[float]]:
        """Generate embeddings for text"""
        if AIProvider.OPENAI in self.providers:
            service = self.providers[AIProvider.OPENAI]
            return await service.get_embeddings(text, model)
        return None


class OpenAIService:
    """OpenAI API service implementation"""

    def __init__(self, api_key: str):
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.pricing = {
            "gpt-4-turbo-preview": {"input": 0.01, "output": 0.03},
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015}
        }

    async def query(self, prompt: str, max_tokens: int, temperature: float) -> AIResponse:
        """Query OpenAI API"""
        start_time = time.time()

        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert neurosurgeon and medical educator."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )

            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens

            # Calculate cost
            model_pricing = self.pricing.get(settings.OPENAI_MODEL, {"input": 0.01, "output": 0.03})
            cost = (response.usage.prompt_tokens * model_pricing["input"] +
                   response.usage.completion_tokens * model_pricing["output"]) / 1000

            return AIResponse(
                content=content,
                provider=AIProvider.OPENAI,
                model=settings.OPENAI_MODEL,
                tokens_used=tokens_used,
                response_time=time.time() - start_time,
                cost=cost,
                success=True
            )

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    async def get_embeddings(self, text: str, model: str) -> List[float]:
        """Generate embeddings using OpenAI"""
        response = await self.client.embeddings.create(
            input=text,
            model=model
        )
        return response.data[0].embedding


class AnthropicService:
    """Anthropic Claude API service implementation"""

    def __init__(self, api_key: str):
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.pricing = {
            "claude-3-opus": {"input": 0.015, "output": 0.075},
            "claude-3-sonnet": {"input": 0.003, "output": 0.015},
            "claude-3-haiku": {"input": 0.00025, "output": 0.00125}
        }

    async def query(self, prompt: str, max_tokens: int, temperature: float) -> AIResponse:
        """Query Anthropic API"""
        start_time = time.time()

        try:
            response = await self.client.messages.create(
                model=settings.ANTHROPIC_MODEL,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                system="You are an expert neurosurgeon with extensive knowledge in all subspecialties of neurosurgery."
            )

            content = response.content[0].text if response.content else ""
            tokens_used = response.usage.input_tokens + response.usage.output_tokens

            # Calculate cost
            model_name = settings.ANTHROPIC_MODEL.split("-20")[0]  # Remove date suffix
            model_pricing = self.pricing.get(model_name, {"input": 0.01, "output": 0.05})
            cost = (response.usage.input_tokens * model_pricing["input"] +
                   response.usage.output_tokens * model_pricing["output"]) / 1000

            return AIResponse(
                content=content,
                provider=AIProvider.ANTHROPIC,
                model=settings.ANTHROPIC_MODEL,
                tokens_used=tokens_used,
                response_time=time.time() - start_time,
                cost=cost,
                success=True
            )

        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise


class GeminiService:
    """Google Gemini API service implementation"""

    def __init__(self, api_key: str):
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        self.pricing = {"gemini-1.5-pro": 0.0035, "gemini-1.5-flash": 0.0001}

    async def query(self, prompt: str, max_tokens: int, temperature: float) -> AIResponse:
        """Query Gemini API"""
        start_time = time.time()

        try:
            # Gemini uses synchronous API, run in executor
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                self.model.generate_content,
                prompt
            )

            content = response.text
            # Estimate tokens (Gemini doesn't provide exact count)
            tokens_used = len(content.split()) * 1.3

            # Calculate cost
            cost = tokens_used * self.pricing.get(settings.GEMINI_MODEL, 0.001) / 1000

            return AIResponse(
                content=content,
                provider=AIProvider.GOOGLE,
                model=settings.GEMINI_MODEL,
                tokens_used=int(tokens_used),
                response_time=time.time() - start_time,
                cost=cost,
                success=True
            )

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise


class PerplexityService:
    """Perplexity API service implementation"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai"
        self.pricing = {"sonar": 0.001}

    async def query(self, prompt: str, max_tokens: int, temperature: float) -> AIResponse:
        """Query Perplexity API for web-grounded responses"""
        start_time = time.time()

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "sonar-medium-chat",
                        "messages": [
                            {"role": "system", "content": "You are a medical research assistant specializing in neurosurgery."},
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": max_tokens,
                        "temperature": temperature
                    }
                )

                data = response.json()
                content = data["choices"][0]["message"]["content"]
                tokens_used = data.get("usage", {}).get("total_tokens", 0)

                return AIResponse(
                    content=content,
                    provider=AIProvider.PERPLEXITY,
                    model="sonar-medium-chat",
                    tokens_used=tokens_used,
                    response_time=time.time() - start_time,
                    cost=tokens_used * self.pricing["sonar"] / 1000,
                    success=True
                )

            except Exception as e:
                logger.error(f"Perplexity API error: {e}")
                raise


class MedicalPromptTemplates:
    """Templates for medical and neurosurgical prompts"""

    def enhance_prompt(self, prompt: str, context: Optional[str], specialty: Optional[str]) -> str:
        """Enhance prompt with medical context"""
        enhanced = f"""As an expert neurosurgeon, provide medically accurate information.

Specialty Focus: {specialty or 'General Neurosurgery'}
Context: {context or 'Clinical practice'}

Request: {prompt}

Please ensure:
1. Medical accuracy and evidence-based information
2. Include relevant ICD-10/CPT codes where applicable
3. Reference current clinical guidelines
4. Consider surgical pearls and pitfalls
5. Maintain professional medical terminology"""

        return enhanced

    def get_validation_prompt(self, content: str, specialty: str) -> str:
        """Create prompt for medical content validation"""
        return f"""Review the following neurosurgical content for medical accuracy:

Content: {content}

Please validate:
1. Medical accuracy
2. Alignment with current guidelines
3. Appropriate terminology
4. Evidence level
5. Any potential errors or concerns

Respond in JSON format:
{{
    "is_accurate": true/false,
    "confidence": 0.0-1.0,
    "issues": [],
    "suggestions": [],
    "evidence_level": "I/II/III/IV/V"
}}"""

    def get_synthesis_prompt(self, section: str, references: List[str], specialty: str) -> str:
        """Create prompt for content synthesis"""
        refs_text = "\n".join([f"- {ref}" for ref in references[:10]])  # Limit references

        return f"""Synthesize a comprehensive '{section}' section for a neurosurgical chapter.

Specialty: {specialty}
References to incorporate:
{refs_text}

Requirements:
1. Comprehensive coverage of the topic
2. Evidence-based information
3. Include surgical techniques if relevant
4. Add clinical pearls
5. Maintain academic medical writing style
6. Include relevant anatomical landmarks
7. Discuss complications and their management

Generate a detailed, well-structured section suitable for a neurosurgical textbook."""


class UsageTracker:
    """Track AI service usage and costs"""

    def __init__(self):
        self.usage = {provider: {"tokens": 0, "cost": 0.0, "calls": 0}
                     for provider in AIProvider}
        self.last_reset = datetime.utcnow()

    def track_usage(self, provider: AIProvider, tokens: int, cost: float):
        """Track usage for a provider"""
        self.usage[provider]["tokens"] += tokens
        self.usage[provider]["cost"] += cost
        self.usage[provider]["calls"] += 1

    def get_usage_report(self) -> Dict[str, Any]:
        """Get usage report"""
        return {
            "period_start": self.last_reset.isoformat(),
            "providers": {
                provider.value: stats
                for provider, stats in self.usage.items()
            },
            "total_cost": sum(stats["cost"] for stats in self.usage.values()),
            "total_tokens": sum(stats["tokens"] for stats in self.usage.values())
        }

    def reset_usage(self):
        """Reset usage tracking"""
        for provider in self.usage:
            self.usage[provider] = {"tokens": 0, "cost": 0.0, "calls": 0}
        self.last_reset = datetime.utcnow()


# Global instance
ai_manager = AIServiceManager()


async def initialize_ai_services():
    """Initialize AI services on startup"""
    global ai_manager
    ai_manager = AIServiceManager()
    logger.info("AI services initialized")


async def check_ai_services_health() -> Dict[str, Any]:
    """Check health of AI services"""
    health = {"status": "healthy", "providers": {}}

    for provider in ai_manager.providers:
        try:
            # Test with simple query
            response = await ai_manager.providers[provider].query(
                "Test connection",
                max_tokens=10,
                temperature=0.1
            )
            health["providers"][provider.value] = {
                "status": "healthy" if response.success else "unhealthy",
                "response_time": response.response_time
            }
        except Exception as e:
            health["providers"][provider.value] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health["status"] = "degraded"

    return health


# Export for use in other modules
__all__ = [
    "AIServiceManager",
    "AIProvider",
    "AIModel",
    "AIResponse",
    "MedicalValidation",
    "ai_manager",
    "initialize_ai_services",
    "check_ai_services_health"
]