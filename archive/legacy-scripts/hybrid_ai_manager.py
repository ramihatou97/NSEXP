"""
Hybrid AI Manager - Intelligent AI Service Orchestration
Manages multiple AI models (Claude, GPT-4, local models) with fallback strategies
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import time
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class AIProvider(Enum):
    """Available AI service providers"""
    CLAUDE = "Claude"
    GPT4 = "GPT-4"
    GPT35 = "GPT-3.5"
    LOCAL = "Local"
    GEMINI = "Gemini"


@dataclass
class AIResponse:
    """Standardized response from AI services"""
    content: str
    provider: AIProvider
    model: str
    tokens_used: int
    response_time: float
    success: bool
    error: Optional[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class AIServiceConfig:
    """Configuration for individual AI service"""
    provider: AIProvider
    api_key: Optional[str]
    endpoint: Optional[str]
    model_name: str
    max_tokens: int = 4000
    temperature: float = 0.7
    priority: int = 1  # Lower number = higher priority
    cost_per_1k_tokens: float = 0.01
    rate_limit: int = 60  # Requests per minute
    timeout: int = 30  # Seconds


class AIServiceInterface(ABC):
    """Abstract interface for AI services"""

    @abstractmethod
    async def query(self, prompt: str, **kwargs) -> AIResponse:
        """Send query to AI service"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if service is available"""
        pass


class ClaudeService(AIServiceInterface):
    """Claude AI service implementation"""

    def __init__(self, config: AIServiceConfig):
        self.config = config
        self.last_request_time = 0
        self.request_count = 0

    async def query(self, prompt: str, **kwargs) -> AIResponse:
        """Query Claude API"""
        start_time = time.time()

        try:
            # Simulate Claude API call (replace with actual implementation)
            # import anthropic
            # client = anthropic.Client(api_key=self.config.api_key)

            # For demonstration, returning simulated response
            await asyncio.sleep(0.5)  # Simulate network delay

            response_content = f"[Claude Response - Simulated]\n{prompt[:100]}..."

            return AIResponse(
                content=response_content,
                provider=AIProvider.CLAUDE,
                model=self.config.model_name,
                tokens_used=len(prompt.split()) * 2,
                response_time=time.time() - start_time,
                success=True
            )

        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return AIResponse(
                content="",
                provider=AIProvider.CLAUDE,
                model=self.config.model_name,
                tokens_used=0,
                response_time=time.time() - start_time,
                success=False,
                error=str(e)
            )

    def is_available(self) -> bool:
        """Check if Claude service is available"""
        return self.config.api_key is not None


class GPTService(AIServiceInterface):
    """OpenAI GPT service implementation"""

    def __init__(self, config: AIServiceConfig):
        self.config = config

    async def query(self, prompt: str, **kwargs) -> AIResponse:
        """Query OpenAI API"""
        start_time = time.time()

        try:
            # Simulate OpenAI API call (replace with actual implementation)
            # import openai
            # openai.api_key = self.config.api_key

            await asyncio.sleep(0.5)  # Simulate network delay

            response_content = f"[GPT Response - Simulated]\n{prompt[:100]}..."

            return AIResponse(
                content=response_content,
                provider=self.config.provider,
                model=self.config.model_name,
                tokens_used=len(prompt.split()) * 2,
                response_time=time.time() - start_time,
                success=True
            )

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return AIResponse(
                content="",
                provider=self.config.provider,
                model=self.config.model_name,
                tokens_used=0,
                response_time=time.time() - start_time,
                success=False,
                error=str(e)
            )

    def is_available(self) -> bool:
        """Check if GPT service is available"""
        return self.config.api_key is not None


class HybridAIManager:
    """
    Central AI orchestration manager that:
    1. Routes queries to appropriate AI models
    2. Implements fallback strategies
    3. Manages rate limiting and costs
    4. Provides unified interface for all AI operations
    """

    def __init__(
        self,
        claude_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        gemini_api_key: Optional[str] = None,
        enable_fallback: bool = True,
        cost_limit_per_day: float = 100.0
    ):
        self.services: Dict[AIProvider, AIServiceInterface] = {}
        self.enable_fallback = enable_fallback
        self.cost_limit_per_day = cost_limit_per_day
        self.daily_cost = 0.0
        self.request_history: List[AIResponse] = []

        # Initialize available services
        self._initialize_services(claude_api_key, openai_api_key, gemini_api_key)

        # Service selection strategy
        self.service_priorities = self._determine_priorities()

    def _initialize_services(
        self,
        claude_api_key: Optional[str],
        openai_api_key: Optional[str],
        gemini_api_key: Optional[str]
    ):
        """Initialize AI services based on available API keys"""

        # Initialize Claude
        if claude_api_key:
            claude_config = AIServiceConfig(
                provider=AIProvider.CLAUDE,
                api_key=claude_api_key,
                model_name="claude-3-opus",
                max_tokens=4000,
                temperature=0.7,
                priority=1,  # Highest priority for medical content
                cost_per_1k_tokens=0.015
            )
            self.services[AIProvider.CLAUDE] = ClaudeService(claude_config)
            logger.info("Claude service initialized")

        # Initialize GPT-4
        if openai_api_key:
            gpt4_config = AIServiceConfig(
                provider=AIProvider.GPT4,
                api_key=openai_api_key,
                model_name="gpt-4-turbo",
                max_tokens=4000,
                temperature=0.7,
                priority=2,
                cost_per_1k_tokens=0.010
            )
            self.services[AIProvider.GPT4] = GPTService(gpt4_config)
            logger.info("GPT-4 service initialized")

            # Also add GPT-3.5 as economical fallback
            gpt35_config = AIServiceConfig(
                provider=AIProvider.GPT35,
                api_key=openai_api_key,
                model_name="gpt-3.5-turbo",
                max_tokens=4000,
                temperature=0.7,
                priority=3,
                cost_per_1k_tokens=0.001
            )
            self.services[AIProvider.GPT35] = GPTService(gpt35_config)
            logger.info("GPT-3.5 service initialized")

    def _determine_priorities(self) -> List[AIProvider]:
        """Determine service priority order"""
        available_services = [
            (provider, service)
            for provider, service in self.services.items()
            if service.is_available()
        ]

        # Sort by priority (from service config)
        available_services.sort(
            key=lambda x: getattr(x[1].config, 'priority', 999)
        )

        return [provider for provider, _ in available_services]

    async def query(
        self,
        preferred_provider: Union[str, AIProvider],
        prompt: str,
        use_fallback: bool = True,
        max_retries: int = 2,
        **kwargs
    ) -> str:
        """
        Main query method with intelligent routing and fallback

        Args:
            preferred_provider: Preferred AI service ("Claude", "GPT-4", etc.)
            prompt: The prompt to send
            use_fallback: Whether to try other services if preferred fails
            max_retries: Maximum retry attempts per service

        Returns:
            AI response content as string
        """

        # Convert string to enum if necessary
        if isinstance(preferred_provider, str):
            try:
                preferred_provider = AIProvider(preferred_provider)
            except ValueError:
                logger.warning(f"Unknown provider: {preferred_provider}, using priority order")
                preferred_provider = self.service_priorities[0] if self.service_priorities else None

        # Check if preferred service is available
        if preferred_provider and preferred_provider in self.services:
            response = await self._query_service(
                self.services[preferred_provider],
                prompt,
                max_retries
            )

            if response.success:
                self._track_usage(response)
                return response.content

        # Fallback logic
        if use_fallback and self.enable_fallback:
            logger.info("Attempting fallback to other AI services")

            for provider in self.service_priorities:
                if provider == preferred_provider:
                    continue  # Already tried

                service = self.services.get(provider)
                if service and service.is_available():
                    response = await self._query_service(service, prompt, max_retries)

                    if response.success:
                        logger.info(f"Successful fallback to {provider.value}")
                        self._track_usage(response)
                        return response.content

        # All services failed
        error_msg = "All AI services failed or unavailable"
        logger.error(error_msg)
        return f"[AI Service Error: {error_msg}]"

    async def _query_service(
        self,
        service: AIServiceInterface,
        prompt: str,
        max_retries: int
    ) -> AIResponse:
        """Query a specific service with retry logic"""

        for attempt in range(max_retries):
            try:
                response = await service.query(prompt)

                if response.success:
                    return response

                logger.warning(f"Service returned error: {response.error}, attempt {attempt + 1}/{max_retries}")

                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff

            except Exception as e:
                logger.error(f"Service query exception: {e}")

                if attempt == max_retries - 1:
                    return AIResponse(
                        content="",
                        provider=service.config.provider,
                        model=service.config.model_name,
                        tokens_used=0,
                        response_time=0,
                        success=False,
                        error=str(e)
                    )

        return AIResponse(
            content="",
            provider=service.config.provider,
            model=service.config.model_name,
            tokens_used=0,
            response_time=0,
            success=False,
            error="Max retries exceeded"
        )

    def _track_usage(self, response: AIResponse):
        """Track usage for cost management and analytics"""
        self.request_history.append(response)

        # Calculate cost
        if hasattr(self.services[response.provider], 'config'):
            config = self.services[response.provider].config
            cost = (response.tokens_used / 1000) * config.cost_per_1k_tokens
            self.daily_cost += cost

            logger.info(
                f"AI Usage - Provider: {response.provider.value}, "
                f"Tokens: {response.tokens_used}, Cost: ${cost:.4f}"
            )

    async def parallel_query(
        self,
        prompt: str,
        providers: List[AIProvider] = None
    ) -> Dict[AIProvider, str]:
        """
        Query multiple AI services in parallel for comparison

        Args:
            prompt: The prompt to send
            providers: List of providers to query (None = all available)

        Returns:
            Dictionary mapping provider to response content
        """

        if providers is None:
            providers = list(self.services.keys())

        tasks = []
        for provider in providers:
            if provider in self.services:
                service = self.services[provider]
                if service.is_available():
                    tasks.append((provider, service.query(prompt)))

        results = {}

        if tasks:
            responses = await asyncio.gather(
                *[task for _, task in tasks],
                return_exceptions=True
            )

            for (provider, _), response in zip(tasks, responses):
                if isinstance(response, AIResponse) and response.success:
                    results[provider] = response.content
                    self._track_usage(response)
                else:
                    results[provider] = f"[Error: {response}]"

        return results

    async def specialized_query(
        self,
        task_type: str,
        prompt: str,
        **kwargs
    ) -> str:
        """
        Route queries based on task type to optimal provider

        Args:
            task_type: Type of task ("medical_synthesis", "code_generation", "translation", etc.)
            prompt: The prompt to send

        Returns:
            AI response content
        """

        # Task-to-provider mapping based on strengths
        task_mapping = {
            "medical_synthesis": AIProvider.CLAUDE,  # Best for medical content
            "medical_analysis": AIProvider.CLAUDE,
            "content_analysis": AIProvider.CLAUDE,
            "code_generation": AIProvider.GPT4,
            "data_extraction": AIProvider.GPT4,
            "summarization": AIProvider.GPT35,  # Good enough and economical
            "translation": AIProvider.GPT35,
            "basic_qa": AIProvider.GPT35
        }

        preferred_provider = task_mapping.get(task_type, AIProvider.CLAUDE)

        return await self.query(
            preferred_provider=preferred_provider,
            prompt=prompt,
            use_fallback=True,
            **kwargs
        )

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics for monitoring"""

        stats = {
            "total_requests": len(self.request_history),
            "daily_cost": self.daily_cost,
            "cost_limit": self.cost_limit_per_day,
            "services_available": len(self.services),
            "providers": {}
        }

        # Group stats by provider
        for response in self.request_history:
            provider = response.provider.value
            if provider not in stats["providers"]:
                stats["providers"][provider] = {
                    "requests": 0,
                    "tokens": 0,
                    "avg_response_time": 0,
                    "errors": 0
                }

            stats["providers"][provider]["requests"] += 1
            stats["providers"][provider]["tokens"] += response.tokens_used

            if not response.success:
                stats["providers"][provider]["errors"] += 1

        return stats

    def reset_daily_usage(self):
        """Reset daily usage counters"""
        self.daily_cost = 0.0
        self.request_history = []
        logger.info("Daily usage counters reset")


# Specialized medical AI configurations
class MedicalAIManager(HybridAIManager):
    """
    Specialized AI manager for medical content synthesis
    Optimized for medical accuracy and terminology
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Medical-specific prompt templates
        self.medical_templates = {
            "synthesis": "As a medical expert, synthesize the following information with clinical accuracy:\n",
            "analysis": "Analyze the following medical content for clinical relevance:\n",
            "extraction": "Extract medical data including diagnoses, treatments, and outcomes:\n"
        }

    async def medical_synthesis(
        self,
        content: str,
        section_type: str = "general"
    ) -> str:
        """
        Specialized method for medical content synthesis

        Args:
            content: Raw medical content to synthesize
            section_type: Type of medical section being synthesized

        Returns:
            Synthesized medical content
        """

        # Add medical context to prompt
        prompt = self.medical_templates["synthesis"]
        prompt += f"\nSection Type: {section_type}\n"
        prompt += f"\nContent to synthesize:\n{content}\n"
        prompt += "\nProvide accurate medical synthesis with proper citations."

        # Use Claude for medical content (best performance)
        return await self.specialized_query(
            task_type="medical_synthesis",
            prompt=prompt
        )


# Utility functions
def create_ai_manager(config: Dict[str, Any]) -> HybridAIManager:
    """Factory function to create AI manager from configuration"""

    return HybridAIManager(
        claude_api_key=config.get("claude_api_key"),
        openai_api_key=config.get("openai_api_key"),
        gemini_api_key=config.get("gemini_api_key"),
        enable_fallback=config.get("enable_fallback", True),
        cost_limit_per_day=config.get("cost_limit_per_day", 100.0)
    )


def create_medical_ai_manager(config: Dict[str, Any]) -> MedicalAIManager:
    """Factory function to create medical-specific AI manager"""

    return MedicalAIManager(
        claude_api_key=config.get("claude_api_key"),
        openai_api_key=config.get("openai_api_key"),
        gemini_api_key=config.get("gemini_api_key"),
        enable_fallback=config.get("enable_fallback", True),
        cost_limit_per_day=config.get("cost_limit_per_day", 100.0)
    )