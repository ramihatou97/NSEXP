"""
External AI Searcher - Hybrid Web/API Search for Knowledge Gap Enrichment
Searches external AI sources (Gemini, Claude, Perplexity) to fill knowledge gaps
Uses both API calls and web automation with persistent login
"""

import asyncio
import json
import logging
import pickle
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path

import aiohttp
from playwright.async_api import async_playwright, Browser, Page, BrowserContext, Playwright

logger = logging.getLogger(__name__)


# ============================================================================
# DATA MODELS
# ============================================================================

class AccessMethod(Enum):
    """Access method for AI services"""
    API = "api"
    WEB = "web"
    HYBRID = "hybrid"


@dataclass
class SearchResult:
    """Result from external AI search"""
    query: str
    response: str
    source: str  # gemini, claude, perplexity
    method: str  # api or web
    timestamp: datetime
    tokens_used: int = 0
    cost: float = 0.0


@dataclass
class UsageStats:
    """Track usage statistics"""
    api_calls: int = 0
    web_calls: int = 0
    api_cost: float = 0.0
    tokens_used: int = 0
    last_reset: datetime = None
    daily_budget_used: float = 0.0


@dataclass
class ServiceConfig:
    """Configuration for each AI service"""
    name: str
    access_method: AccessMethod
    api_available: bool = False
    web_available: bool = False
    daily_budget: float = 10.0
    cost_per_1k_tokens: float = 0.001
    max_tokens: int = 4000
    rate_limit_per_minute: int = 60
    web_base_url: str = ""
    web_selectors: Dict[str, str] = field(default_factory=dict)


# ============================================================================
# SESSION MANAGER
# ============================================================================

class SessionManager:
    """Manages persistent browser sessions with saved cookies"""

    def __init__(self):
        self.session_dir = Path("data/browser_sessions")
        self.session_dir.mkdir(parents=True, exist_ok=True)

    async def save_session(self, page: Page, service: str):
        """Save cookies and storage for persistent login"""
        try:
            cookies = await page.context.cookies()
            local_storage = await page.evaluate('() => Object.assign({}, localStorage)')
            session_storage = await page.evaluate('() => Object.assign({}, sessionStorage)')

            session_data = {
                'cookies': cookies,
                'local_storage': local_storage,
                'session_storage': session_storage,
                'service': service,
                'timestamp': datetime.now().isoformat(),
                'url': page.url
            }

            session_file = self.session_dir / f"{service}_session.pkl"
            with open(session_file, 'wb') as f:
                pickle.dump(session_data, f)

            logger.info(f"Session saved for {service}")
        except Exception as e:
            logger.error(f"Failed to save session: {e}")

    async def restore_session(self, context: BrowserContext, service: str) -> bool:
        """Restore saved session"""
        session_file = self.session_dir / f"{service}_session.pkl"

        if not session_file.exists():
            return False

        try:
            with open(session_file, 'rb') as f:
                session_data = pickle.load(f)

            # Check if session is not too old (30 days)
            saved_time = datetime.fromisoformat(session_data['timestamp'])
            if datetime.now() - saved_time > timedelta(days=30):
                logger.warning(f"Session expired for {service}")
                return False

            await context.add_cookies(session_data['cookies'])
            logger.info(f"Session restored for {service}")
            return True
        except Exception as e:
            logger.error(f"Failed to restore session: {e}")
            return False


# ============================================================================
# EXTERNAL AI SEARCHER
# ============================================================================

class ExternalAISearcher:
    """
    Hybrid AI Searcher for external knowledge enrichment
    Uses API calls when available, falls back to web automation
    """

    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        """
        Initialize searcher with optional API keys

        Args:
            api_keys: Dict with keys like {'gemini': 'key', 'claude': 'key', 'perplexity': 'key'}
        """
        self.api_keys = api_keys or {}
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.contexts: Dict[str, BrowserContext] = {}
        self.pages: Dict[str, Page] = {}
        self.usage_stats: Dict[str, UsageStats] = {}
        self.session_manager = SessionManager()
        self.logged_in_services = set()
        self.browser_initialized = False

        # Initialize service configurations
        self.services = self._initialize_services()
        self._load_usage_stats()

    def _initialize_services(self) -> Dict[str, ServiceConfig]:
        """Initialize service configurations"""
        return {
            "gemini": ServiceConfig(
                name="gemini",
                access_method=AccessMethod.HYBRID,
                api_available='gemini' in self.api_keys,
                web_available=True,
                daily_budget=15.0,
                cost_per_1k_tokens=0.001,
                max_tokens=8000,
                web_base_url="https://gemini.google.com/app",
                web_selectors={
                    "input": 'div[contenteditable="true"]',
                    "send_button": 'button[aria-label*="Send"]',
                    "response": 'div[data-message-author-role="model"]',
                    "new_chat": 'button[aria-label*="New chat"]'
                }
            ),
            "claude": ServiceConfig(
                name="claude",
                access_method=AccessMethod.HYBRID,
                api_available='claude' in self.api_keys,
                web_available=True,
                daily_budget=20.0,
                cost_per_1k_tokens=0.015,
                max_tokens=4000,
                web_base_url="https://claude.ai/chats",
                web_selectors={
                    "input": 'div[contenteditable="true"].ProseMirror',
                    "send_button": 'button[aria-label="Send Message"]',
                    "response": 'div[data-test-id="assistant-message-content"]',
                    "new_chat": 'button:has-text("New chat")'
                }
            ),
            "perplexity": ServiceConfig(
                name="perplexity",
                access_method=AccessMethod.API if 'perplexity' in self.api_keys else AccessMethod.WEB,
                api_available='perplexity' in self.api_keys,
                web_available=True,
                daily_budget=10.0,
                cost_per_1k_tokens=0.001,
                max_tokens=4000,
                web_base_url="https://www.perplexity.ai",
                web_selectors={
                    "input": 'textarea[placeholder*="Ask"]',
                    "send_button": 'button[aria-label*="Submit"]',
                    "response": 'div.prose',
                    "new_thread": 'button:has-text("New Thread")'
                }
            )
        }

    # ========================================================================
    # BROWSER MANAGEMENT
    # ========================================================================

    async def initialize_browser(self):
        """Initialize Playwright browser"""
        if not self.browser_initialized:
            try:
                self.playwright = await async_playwright().start()
                self.browser = await self.playwright.chromium.launch(
                    headless=False,  # Set to True for production
                    args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
                )
                self.browser_initialized = True
                logger.info("Browser initialized")
            except Exception as e:
                logger.error(f"Failed to initialize browser: {e}")
                raise

    async def get_page(self, service: str) -> Page:
        """Get or create page for service with automatic login"""
        if service in self.pages:
            try:
                # Test if page is still active
                await self.pages[service].evaluate('() => true')
                return self.pages[service]
            except:
                del self.pages[service]

        # Initialize browser if needed
        if not self.browser_initialized:
            await self.initialize_browser()

        # Create persistent context
        if service not in self.contexts:
            profile_dir = Path(f"data/browser_profiles/{service}")
            profile_dir.mkdir(parents=True, exist_ok=True)

            context = await self.browser.new_context(
                user_data_dir=str(profile_dir),
                viewport={'width': 1920, 'height': 1080}
            )

            await self.session_manager.restore_session(context, service)
            self.contexts[service] = context

        # Create page
        page = await self.contexts[service].new_page()
        page.set_default_timeout(30000)

        # Navigate to service
        config = self.services[service]
        await page.goto(config.web_base_url, wait_until="networkidle", timeout=60000)

        self.pages[service] = page
        await self.session_manager.save_session(page, service)

        return page

    # ========================================================================
    # LOGIN SETUP
    # ========================================================================

    async def setup_login(self, service: str, email: str, password: str) -> bool:
        """
        One-time login setup for a service
        User performs this once, then sessions are persisted
        """
        try:
            logger.info(f"Setting up login for {service}...")
            page = await self.get_page(service)

            # Wait for user to manually login
            print(f"\n{'='*60}")
            print(f"MANUAL LOGIN REQUIRED: {service}")
            print(f"{'='*60}")
            print(f"1. The browser window should now be open at {self.services[service].web_base_url}")
            print(f"2. Please login manually with your credentials")
            print(f"3. Once logged in and you see the chat interface, press Enter here...")
            input("Press Enter after logging in: ")

            # Save the session
            await self.session_manager.save_session(page, service)
            self.logged_in_services.add(service)

            logger.info(f"✅ Login saved for {service}")
            return True

        except Exception as e:
            logger.error(f"Failed to setup login for {service}: {e}")
            return False

    # ========================================================================
    # API CALLS
    # ========================================================================

    async def _call_api(self, service: str, prompt: str, **kwargs) -> str:
        """Call API for service"""
        if service == "gemini":
            return await self._call_gemini_api(prompt, **kwargs)
        elif service == "claude":
            return await self._call_claude_api(prompt, **kwargs)
        elif service == "perplexity":
            return await self._call_perplexity_api(prompt, **kwargs)
        else:
            raise ValueError(f"API not implemented for {service}")

    async def _call_gemini_api(self, prompt: str, **kwargs) -> str:
        """Call Gemini API"""
        api_key = self.api_keys.get('gemini')
        if not api_key:
            raise ValueError("Gemini API key not provided")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"

        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": kwargs.get("max_tokens", 2000),
                "temperature": kwargs.get("temperature", 0.7)
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, timeout=aiohttp.ClientTimeout(total=60)) as response:
                if response.status == 200:
                    result = await response.json()
                    text = result['candidates'][0]['content']['parts'][0]['text']

                    # Update stats
                    self._update_stats("gemini", api_call=True, tokens=len(text.split()) * 1.3)
                    return text
                else:
                    raise Exception(f"Gemini API error: {await response.text()}")

    async def _call_claude_api(self, prompt: str, **kwargs) -> str:
        """Call Claude API"""
        api_key = self.api_keys.get('claude')
        if not api_key:
            raise ValueError("Claude API key not provided")

        headers = {
            'Content-Type': 'application/json',
            'x-api-key': api_key,
            'anthropic-version': '2023-06-01'
        }

        data = {
            "model": "claude-3-opus-20240229",
            "max_tokens": kwargs.get("max_tokens", 2000),
            "messages": [{"role": "user", "content": prompt}]
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    text = result['content'][0]['text']

                    # Update stats
                    tokens = result.get('usage', {}).get('total_tokens', len(text.split()) * 1.3)
                    self._update_stats("claude", api_call=True, tokens=tokens)
                    return text
                else:
                    raise Exception(f"Claude API error: {await response.text()}")

    async def _call_perplexity_api(self, prompt: str, **kwargs) -> str:
        """Call Perplexity API"""
        api_key = self.api_keys.get('perplexity')
        if not api_key:
            raise ValueError("Perplexity API key not provided")

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }

        data = {
            "model": "llama-3.1-sonar-large-128k-online",
            "messages": [{"role": "user", "content": prompt}]
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.perplexity.ai/chat/completions",
                headers=headers,
                json=data,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    text = result['choices'][0]['message']['content']

                    # Update stats
                    tokens = result.get('usage', {}).get('total_tokens', len(text.split()) * 1.3)
                    self._update_stats("perplexity", api_call=True, tokens=tokens)
                    return text
                else:
                    raise Exception(f"Perplexity API error: {await response.text()}")

    # ========================================================================
    # WEB AUTOMATION
    # ========================================================================

    async def _call_web(self, service: str, prompt: str, **kwargs) -> str:
        """Call service via web interface"""
        page = await self.get_page(service)
        config = self.services[service]

        try:
            # Wait for input field
            input_selector = config.web_selectors["input"]
            await page.wait_for_selector(input_selector, state="visible", timeout=10000)

            # Clear and type prompt
            await page.click(input_selector)
            await page.keyboard.press("Control+A")
            await page.keyboard.press("Backspace")
            await page.type(input_selector, prompt, delay=10)

            # Send
            await page.click(config.web_selectors["send_button"])

            # Wait for response
            await page.wait_for_timeout(3000)  # Initial wait

            # Extract response
            response_selector = config.web_selectors["response"]
            await page.wait_for_selector(response_selector, timeout=60000)

            # Get last response
            elements = await page.query_selector_all(response_selector)
            if elements:
                text = await elements[-1].inner_text()

                # Update stats
                self._update_stats(service, web_call=True)
                return text.strip()
            else:
                raise Exception("No response found")

        except Exception as e:
            logger.error(f"Web call failed for {service}: {e}")
            raise

    # ========================================================================
    # MAIN SEARCH INTERFACE
    # ========================================================================

    async def search(self, query: str, service: str = "gemini", **kwargs) -> SearchResult:
        """
        Main search method - tries API first, falls back to web

        Args:
            query: Search query/prompt
            service: AI service to use (gemini, claude, perplexity)
            **kwargs: Additional parameters

        Returns:
            SearchResult with response and metadata
        """
        if service not in self.services:
            raise ValueError(f"Unknown service: {service}")

        config = self.services[service]
        method_used = None
        response_text = None

        try:
            # Try API first if available
            if config.api_available:
                try:
                    response_text = await self._call_api(service, query, **kwargs)
                    method_used = "api"
                    logger.info(f"✅ API search successful: {service}")
                except Exception as e:
                    logger.warning(f"API failed for {service}, trying web: {e}")
                    if not config.web_available:
                        raise

            # Fall back to web if API failed or not available
            if not response_text and config.web_available:
                response_text = await self._call_web(service, query, **kwargs)
                method_used = "web"
                logger.info(f"✅ Web search successful: {service}")

            if not response_text:
                raise Exception(f"No response from {service}")

            return SearchResult(
                query=query,
                response=response_text,
                source=service,
                method=method_used,
                timestamp=datetime.now(),
                tokens_used=len(response_text.split()),
                cost=self.usage_stats.get(service, UsageStats()).api_cost
            )

        except Exception as e:
            logger.error(f"Search failed for {service}: {e}")
            raise

    async def search_multiple(
        self,
        queries: List[str],
        service: str = "gemini",
        **kwargs
    ) -> List[SearchResult]:
        """Search multiple queries"""
        results = []
        for query in queries:
            try:
                result = await self.search(query, service, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Query failed: {query[:50]}... - {e}")
                results.append(None)
        return results

    # ========================================================================
    # KNOWLEDGE GAP ENRICHMENT
    # ========================================================================

    async def enrich_knowledge_gaps(
        self,
        topic: str,
        knowledge_gaps: List[str],
        service: str = "gemini"
    ) -> Dict[str, SearchResult]:
        """
        Enrich knowledge gaps with external AI search

        Args:
            topic: Main topic
            knowledge_gaps: List of knowledge gap descriptions
            service: AI service to use

        Returns:
            Dict mapping gap to search result
        """
        enrichment_results = {}

        for gap in knowledge_gaps:
            # Construct focused query
            query = f"""
            Topic: {topic}

            Knowledge Gap: {gap}

            Please provide comprehensive, medically accurate information to address this knowledge gap.
            Include:
            1. Key facts and findings
            2. Recent research or guidelines
            3. Clinical relevance
            4. Reliable sources or references if available

            Format the response in a structured, easy-to-integrate manner.
            """

            try:
                logger.info(f"Searching for: {gap[:60]}...")
                result = await self.search(query, service)
                enrichment_results[gap] = result
                logger.info(f"✅ Found information for gap")

                # Small delay between requests
                await asyncio.sleep(2)

            except Exception as e:
                logger.error(f"Failed to enrich gap '{gap[:40]}...': {e}")
                enrichment_results[gap] = None

        return enrichment_results

    # ========================================================================
    # USAGE TRACKING
    # ========================================================================

    def _update_stats(self, service: str, api_call: bool = False,
                     web_call: bool = False, tokens: int = 0):
        """Update usage statistics"""
        if service not in self.usage_stats:
            self.usage_stats[service] = UsageStats(last_reset=datetime.now())

        stats = self.usage_stats[service]

        if api_call:
            stats.api_calls += 1
            stats.tokens_used += tokens
            cost = tokens / 1000 * self.services[service].cost_per_1k_tokens
            stats.api_cost += cost
            stats.daily_budget_used += cost

        if web_call:
            stats.web_calls += 1
            stats.daily_budget_used += 0.0001  # Minimal cost for web

        self._save_usage_stats()

    def _load_usage_stats(self):
        """Load usage statistics"""
        stats_file = Path("data/external_usage_stats.json")
        if stats_file.exists():
            try:
                with open(stats_file, 'r') as f:
                    data = json.load(f)
                    for service, stats_data in data.items():
                        if 'last_reset' in stats_data and stats_data['last_reset']:
                            stats_data['last_reset'] = datetime.fromisoformat(stats_data['last_reset'])
                        self.usage_stats[service] = UsageStats(**stats_data)
            except Exception as e:
                logger.error(f"Failed to load stats: {e}")

        # Initialize missing stats
        for service in self.services.keys():
            if service not in self.usage_stats:
                self.usage_stats[service] = UsageStats(last_reset=datetime.now())

    def _save_usage_stats(self):
        """Save usage statistics"""
        try:
            os.makedirs("data", exist_ok=True)
            stats_file = Path("data/external_usage_stats.json")

            data = {}
            for service, stats in self.usage_stats.items():
                data[service] = asdict(stats)
                if stats.last_reset:
                    data[service]['last_reset'] = stats.last_reset.isoformat()

            with open(stats_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save stats: {e}")

    def get_usage_report(self) -> Dict[str, Any]:
        """Get comprehensive usage report"""
        report = {
            "services": {},
            "total_api_calls": 0,
            "total_web_calls": 0,
            "total_cost": 0.0,
            "timestamp": datetime.now().isoformat()
        }

        for service, stats in self.usage_stats.items():
            report["services"][service] = {
                "api_calls": stats.api_calls,
                "web_calls": stats.web_calls,
                "tokens_used": stats.tokens_used,
                "cost": f"${stats.api_cost:.4f}",
                "daily_budget_used": f"${stats.daily_budget_used:.4f}",
                "daily_budget_limit": f"${self.services[service].daily_budget:.2f}"
            }

            report["total_api_calls"] += stats.api_calls
            report["total_web_calls"] += stats.web_calls
            report["total_cost"] += stats.api_cost

        report["total_cost"] = f"${report['total_cost']:.4f}"
        return report

    # ========================================================================
    # CLEANUP
    # ========================================================================

    async def close(self):
        """Clean up resources"""
        self._save_usage_stats()

        # Save sessions
        for service, page in self.pages.items():
            try:
                await self.session_manager.save_session(page, service)
            except:
                pass

        # Close pages
        for page in self.pages.values():
            try:
                await page.close()
            except:
                pass

        # Close contexts
        for context in self.contexts.values():
            try:
                await context.close()
            except:
                pass

        # Close browser
        if self.browser:
            try:
                await self.browser.close()
            except:
                pass

        # Stop playwright
        if self.playwright:
            try:
                await self.playwright.stop()
            except:
                pass

        self.pages.clear()
        self.contexts.clear()
        self.browser_initialized = False

        logger.info("External AI Searcher closed")


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

async def create_searcher(api_keys: Optional[Dict[str, str]] = None) -> ExternalAISearcher:
    """
    Create and return an ExternalAISearcher instance

    Args:
        api_keys: Optional dict of API keys {'gemini': 'key', 'claude': 'key'}
    """
    return ExternalAISearcher(api_keys)


async def search_external(
    query: str,
    service: str = "gemini",
    api_keys: Optional[Dict[str, str]] = None
) -> SearchResult:
    """
    Quick external search - creates searcher, searches, closes

    Args:
        query: Search query
        service: AI service (gemini, claude, perplexity)
        api_keys: Optional API keys
    """
    searcher = await create_searcher(api_keys)
    try:
        result = await searcher.search(query, service)
        return result
    finally:
        await searcher.close()