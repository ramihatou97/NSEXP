"""
Alive Chapter Integration Bridge
Connects the static EXM pipeline with interactive Alive Chapter features
Provides a clean integration layer between batch processing and interactive chapter evolution
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import json
import sys

# Add alive chapter directory to path
alive_chapter_path = Path(__file__).parent / "alive chapter"
if str(alive_chapter_path) not in sys.path:
    sys.path.insert(0, str(alive_chapter_path))

logger = logging.getLogger(__name__)


# ============================================================================
# IMPORT ALIVE CHAPTER COMPONENTS WITH FALLBACK
# ============================================================================

try:
    from chapter_behavioral_learning import (
        ChapterBehavioralLearningEngine,
        InteractionType,
        KnowledgeNeedType
    )
    BEHAVIORAL_LEARNING_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Behavioral learning not available: {e}")
    BEHAVIORAL_LEARNING_AVAILABLE = False

try:
    from chapter_qa_engine import (
        ChapterQAEngine,
        QuestionType,
        IntegrationStrategy
    )
    QA_ENGINE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Q&A engine not available: {e}")
    QA_ENGINE_AVAILABLE = False

try:
    from citation_network_engine import (
        CitationNetworkEngine,
        CitationType,
        ReferenceType
    )
    CITATION_NETWORK_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Citation network not available: {e}")
    CITATION_NETWORK_AVAILABLE = False

try:
    from enhanced_nuance_merge_engine import EnhancedNuanceMergeEngine
    ENHANCED_MERGE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Enhanced merge engine not available: {e}")
    ENHANCED_MERGE_AVAILABLE = False


# ============================================================================
# ALIVE CHAPTER MANAGER
# ============================================================================

class AliveChapterManager:
    """
    Central manager for Alive Chapter features
    Bridges static chapter generation with interactive evolution
    """

    def __init__(self, ai_manager=None):
        """
        Initialize alive chapter manager

        Args:
            ai_manager: HybridAIManager from EXM for AI-powered features
        """
        self.ai_manager = ai_manager

        # Initialize available components
        self.behavioral_learning = None
        self.qa_engine = None
        self.citation_network = None
        self.enhanced_merge = None

        self._initialize_components()

    def _initialize_components(self):
        """Initialize available alive chapter components"""

        if BEHAVIORAL_LEARNING_AVAILABLE:
            try:
                self.behavioral_learning = ChapterBehavioralLearningEngine()
                logger.info("✓ Behavioral learning engine initialized")
            except Exception as e:
                logger.error(f"Failed to initialize behavioral learning: {e}")

        if QA_ENGINE_AVAILABLE:
            try:
                self.qa_engine = ChapterQAEngine()
                logger.info("✓ Q&A engine initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Q&A engine: {e}")

        if CITATION_NETWORK_AVAILABLE:
            try:
                self.citation_network = CitationNetworkEngine()
                logger.info("✓ Citation network engine initialized")
            except Exception as e:
                logger.error(f"Failed to initialize citation network: {e}")

        if ENHANCED_MERGE_AVAILABLE:
            try:
                self.enhanced_merge = EnhancedNuanceMergeEngine(self.ai_manager)
                logger.info("✓ Enhanced merge engine initialized")
            except Exception as e:
                logger.error(f"Failed to initialize enhanced merge: {e}")

    # ========================================================================
    # CHAPTER ACTIVATION
    # ========================================================================

    async def activate_chapter(
        self,
        chapter: Dict[str, Any],
        chapter_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Activate a static chapter to make it "alive"

        Args:
            chapter: Chapter dict from EXM pipeline
            chapter_id: Optional chapter identifier

        Returns:
            Activated chapter with alive features enabled
        """

        if not chapter_id:
            chapter_id = self._generate_chapter_id(chapter)

        logger.info(f"Activating chapter: {chapter_id}")

        # Add alive metadata
        chapter['alive_metadata'] = {
            'chapter_id': chapter_id,
            'activated_at': datetime.now().isoformat(),
            'behavioral_learning_enabled': self.behavioral_learning is not None,
            'qa_enabled': self.qa_engine is not None,
            'citation_network_enabled': self.citation_network is not None,
            'enhanced_merge_enabled': self.enhanced_merge is not None,
            'interaction_count': 0,
            'last_interaction': None,
            'knowledge_gaps_filled': 0,
            'citations_added': 0
        }

        # Build initial citation network
        if self.citation_network:
            try:
                await self._build_initial_citation_network(chapter, chapter_id)
                logger.info(f"✓ Built citation network for {chapter_id}")
            except Exception as e:
                logger.error(f"Failed to build citation network: {e}")

        # Initialize behavioral tracking
        if self.behavioral_learning:
            chapter['alive_metadata']['learning_session_id'] = self._generate_session_id()

        logger.info(f"✅ Chapter activated: {chapter_id}")

        return chapter

    # ========================================================================
    # Q&A INTEGRATION
    # ========================================================================

    async def process_chapter_question(
        self,
        chapter: Dict[str, Any],
        question: str,
        user_id: str = "default_user",
        section_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a question within chapter context and integrate answer

        Args:
            chapter: Activated chapter
            question: User question
            user_id: User identifier
            section_context: Optional section where question was asked

        Returns:
            Updated chapter with Q&A integrated
        """

        if not self.qa_engine:
            logger.warning("Q&A engine not available")
            return {
                "success": False,
                "error": "Q&A engine not available"
            }

        chapter_id = chapter.get('alive_metadata', {}).get('chapter_id', 'unknown')
        chapter_content = self._extract_chapter_text(chapter)

        logger.info(f"Processing question for chapter {chapter_id}: {question}")

        # Track interaction
        if self.behavioral_learning:
            await self._track_interaction(
                chapter_id,
                user_id,
                InteractionType.QUESTION,
                {"question": question, "section": section_context}
            )

        # Process question through Q&A engine
        try:
            qa_result = await self.qa_engine.process_in_chapter_question(
                question=question,
                chapter_id=chapter_id,
                chapter_content=chapter_content,
                section_context=section_context or chapter_content[:500],
                user_id=user_id
            )

            # Integrate answer into chapter if applicable
            if qa_result.get('integration_recommended'):
                updated_chapter = await self._integrate_qa_answer(
                    chapter,
                    qa_result,
                    user_id
                )

                return {
                    "success": True,
                    "answer": qa_result.get('answer'),
                    "chapter_updated": True,
                    "updated_chapter": updated_chapter,
                    "integration_points": qa_result.get('integration_points', [])
                }
            else:
                return {
                    "success": True,
                    "answer": qa_result.get('answer'),
                    "chapter_updated": False,
                    "reason": "Answer not suitable for integration"
                }

        except Exception as e:
            logger.error(f"Failed to process question: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    # ========================================================================
    # BEHAVIORAL LEARNING
    # ========================================================================

    async def anticipate_knowledge_needs(
        self,
        chapter: Dict[str, Any],
        user_id: str = "default_user"
    ) -> Dict[str, Any]:
        """
        Anticipate knowledge needs based on user behavior patterns

        Args:
            chapter: Activated chapter
            user_id: User identifier

        Returns:
            Anticipated needs and suggestions
        """

        if not self.behavioral_learning:
            logger.warning("Behavioral learning not available")
            return {"anticipated_needs": []}

        chapter_id = chapter.get('alive_metadata', {}).get('chapter_id', 'unknown')
        chapter_content = self._extract_chapter_text(chapter)

        logger.info(f"Anticipating knowledge needs for chapter {chapter_id}")

        try:
            anticipated = await self.behavioral_learning.anticipate_knowledge_needs(
                chapter_id=chapter_id,
                chapter_content=chapter_content,
                user_id=user_id
            )

            return {
                "success": True,
                "anticipated_needs": anticipated.get('needs', []),
                "suggestions": anticipated.get('suggestions', []),
                "confidence": anticipated.get('confidence', 0.0)
            }

        except Exception as e:
            logger.error(f"Failed to anticipate needs: {e}")
            return {
                "success": False,
                "error": str(e),
                "anticipated_needs": []
            }

    async def learn_from_interaction(
        self,
        chapter_id: str,
        user_id: str,
        interaction_type: str,
        context: Dict[str, Any]
    ):
        """
        Learn from user interaction for future anticipation

        Args:
            chapter_id: Chapter identifier
            user_id: User identifier
            interaction_type: Type of interaction
            context: Interaction context
        """

        if not self.behavioral_learning:
            return

        try:
            await self.behavioral_learning.learn_from_interaction({
                "chapter_id": chapter_id,
                "user_id": user_id,
                "type": interaction_type,
                "context": context,
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Failed to learn from interaction: {e}")

    # ========================================================================
    # CITATION NETWORK
    # ========================================================================

    async def build_citation_network(
        self,
        chapter: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build comprehensive citation network for chapter

        Args:
            chapter: Activated chapter

        Returns:
            Citation network analysis
        """

        if not self.citation_network:
            logger.warning("Citation network not available")
            return {"citations": []}

        chapter_id = chapter.get('alive_metadata', {}).get('chapter_id', 'unknown')
        chapter_content = self._extract_chapter_text(chapter)

        logger.info(f"Building citation network for chapter {chapter_id}")

        try:
            network = await self.citation_network.build_network(
                chapter_id=chapter_id,
                chapter_content=chapter_content
            )

            return {
                "success": True,
                "network": network,
                "total_citations": len(network.get('citations', [])),
                "internal_refs": len(network.get('internal_refs', [])),
                "external_refs": len(network.get('external_refs', []))
            }

        except Exception as e:
            logger.error(f"Failed to build citation network: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    # ========================================================================
    # ENHANCED MERGING
    # ========================================================================

    async def intelligent_merge(
        self,
        chapter: Dict[str, Any],
        new_knowledge: Dict[str, Any],
        user_id: str = "default_user"
    ) -> Dict[str, Any]:
        """
        Intelligently merge new knowledge using enhanced merge engine

        Args:
            chapter: Current chapter
            new_knowledge: New knowledge to integrate
            user_id: User identifier

        Returns:
            Merged chapter
        """

        if not self.enhanced_merge:
            # Fallback to basic merge
            logger.warning("Enhanced merge not available, using basic merge")
            return chapter

        chapter_id = chapter.get('alive_metadata', {}).get('chapter_id', 'unknown')
        chapter_content = self._extract_chapter_text(chapter)

        logger.info(f"Performing intelligent merge for chapter {chapter_id}")

        try:
            merged = await self.enhanced_merge.intelligent_knowledge_integration(
                chapter_content=chapter_content,
                new_knowledge=new_knowledge,
                chapter_id=chapter_id,
                user_id=user_id,
                integration_context={"source": "alive_chapter"}
            )

            # Update chapter with merged content
            updated_chapter = chapter.copy()
            updated_chapter['content'] = merged.get('content', chapter_content)
            updated_chapter['alive_metadata']['last_merge'] = datetime.now().isoformat()

            return updated_chapter

        except Exception as e:
            logger.error(f"Failed to perform intelligent merge: {e}")
            return chapter

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def _generate_chapter_id(self, chapter: Dict[str, Any]) -> str:
        """Generate unique chapter ID"""
        topic = chapter.get('topic', 'unknown')
        timestamp = datetime.now().isoformat()
        return f"chapter_{topic.lower().replace(' ', '_')}_{timestamp}"

    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        import hashlib
        timestamp = datetime.now().isoformat()
        return hashlib.md5(timestamp.encode()).hexdigest()

    def _extract_chapter_text(self, chapter: Dict[str, Any]) -> str:
        """Extract full text from chapter"""
        content = chapter.get('content', {})
        if isinstance(content, dict):
            # Join all sections
            return '\n\n'.join(str(v) for v in content.values())
        return str(content)

    async def _build_initial_citation_network(
        self,
        chapter: Dict[str, Any],
        chapter_id: str
    ):
        """Build initial citation network"""
        if not self.citation_network:
            return

        chapter_content = self._extract_chapter_text(chapter)
        await self.citation_network.detect_citations(chapter_id, chapter_content)

    async def _track_interaction(
        self,
        chapter_id: str,
        user_id: str,
        interaction_type,
        metadata: Dict[str, Any]
    ):
        """Track user interaction"""
        if not self.behavioral_learning:
            return

        await self.behavioral_learning.learn_from_interaction({
            "chapter_id": chapter_id,
            "user_id": user_id,
            "type": interaction_type.value if hasattr(interaction_type, 'value') else str(interaction_type),
            "metadata": metadata,
            "timestamp": datetime.now().isoformat()
        })

    async def _integrate_qa_answer(
        self,
        chapter: Dict[str, Any],
        qa_result: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """Integrate Q&A answer into chapter"""

        if not self.enhanced_merge:
            logger.warning("Enhanced merge not available for Q&A integration")
            return chapter

        new_knowledge = {
            "content": qa_result.get('answer', ''),
            "source": "qa_engine",
            "citations": qa_result.get('citations', []),
            "confidence": qa_result.get('confidence', 0.0)
        }

        return await self.intelligent_merge(chapter, new_knowledge, user_id)


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

async def activate_chapter(
    chapter: Dict[str, Any],
    ai_manager=None
) -> Dict[str, Any]:
    """
    Convenience function to activate a chapter

    Args:
        chapter: Chapter from EXM pipeline
        ai_manager: Optional AI manager

    Returns:
        Activated alive chapter
    """
    manager = AliveChapterManager(ai_manager)
    return await manager.activate_chapter(chapter)


async def process_question(
    chapter: Dict[str, Any],
    question: str,
    ai_manager=None
) -> Dict[str, Any]:
    """
    Convenience function to process a question

    Args:
        chapter: Activated chapter
        question: User question
        ai_manager: Optional AI manager

    Returns:
        Result with answer and optional chapter update
    """
    manager = AliveChapterManager(ai_manager)
    return await manager.process_chapter_question(chapter, question)


def get_alive_status() -> Dict[str, bool]:
    """
    Get status of alive chapter components

    Returns:
        Dict with component availability status
    """
    return {
        "behavioral_learning": BEHAVIORAL_LEARNING_AVAILABLE,
        "qa_engine": QA_ENGINE_AVAILABLE,
        "citation_network": CITATION_NETWORK_AVAILABLE,
        "enhanced_merge": ENHANCED_MERGE_AVAILABLE
    }