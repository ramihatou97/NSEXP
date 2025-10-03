"""
Alive Chapter Integration Service
Bridges the alive chapter components with the main backend
"""
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add alive chapter directory to path
alive_chapter_path = Path(__file__).parent.parent.parent / "alive chapter"
if str(alive_chapter_path) not in sys.path:
    sys.path.insert(0, str(alive_chapter_path))

logger = logging.getLogger(__name__)


class AliveChapterIntegration:
    """
    Service to integrate alive chapter functionality into main backend
    """
    
    def __init__(self):
        self.qa_engine = None
        self.citation_network = None
        self.behavioral_learning = None
        self.nuance_merge = None
        
        # Try to import alive chapter components
        self._initialize_components()
    
    def _initialize_components(self):
        """
        Lazily initialize alive chapter components if available
        """
        try:
            from chapter_qa_engine import ChapterQAEngine
            self.qa_engine = ChapterQAEngine()
            logger.info("Chapter Q&A Engine initialized")
        except Exception as e:
            logger.warning(f"Chapter Q&A Engine not available: {e}")
        
        try:
            from citation_network_engine import CitationNetworkEngine
            self.citation_network = CitationNetworkEngine()
            logger.info("Citation Network Engine initialized")
        except Exception as e:
            logger.warning(f"Citation Network Engine not available: {e}")
        
        try:
            from chapter_behavioral_learning import ChapterBehavioralLearning
            self.behavioral_learning = ChapterBehavioralLearning()
            logger.info("Behavioral Learning Engine initialized")
        except Exception as e:
            logger.warning(f"Behavioral Learning Engine not available: {e}")
        
        try:
            from enhanced_nuance_merge_engine import EnhancedNuanceMergeEngine
            self.nuance_merge = EnhancedNuanceMergeEngine()
            logger.info("Nuance Merge Engine initialized")
        except Exception as e:
            logger.warning(f"Nuance Merge Engine not available: {e}")
    
    def is_available(self) -> Dict[str, bool]:
        """
        Check which alive chapter components are available
        """
        return {
            "qa_engine": self.qa_engine is not None,
            "citation_network": self.citation_network is not None,
            "behavioral_learning": self.behavioral_learning is not None,
            "nuance_merge": self.nuance_merge is not None
        }
    
    async def activate_chapter(
        self,
        chapter: Dict[str, Any],
        chapter_id: str
    ) -> Dict[str, Any]:
        """
        Activate a chapter to make it "alive" with interactive features
        
        Args:
            chapter: Chapter content and metadata
            chapter_id: Unique chapter identifier
            
        Returns:
            Activated chapter with alive features enabled
        """
        try:
            availability = self.is_available()
            
            activated_chapter = {
                **chapter,
                "alive_metadata": {
                    "chapter_id": chapter_id,
                    "activated_at": datetime.now().isoformat(),
                    "features_enabled": availability,
                    "interaction_count": 0,
                    "last_interaction": None,
                    "health_score": 1.0
                }
            }
            
            logger.info(f"Chapter {chapter_id} activated with features: {availability}")
            
            return {
                "success": True,
                "chapter": activated_chapter,
                "features_available": availability
            }
            
        except Exception as e:
            logger.error(f"Chapter activation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def process_chapter_question(
        self,
        chapter_id: str,
        question: str,
        user_id: str = "default_user",
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a question about a chapter using the Q&A engine
        """
        if not self.qa_engine:
            return {
                "success": False,
                "error": "Q&A engine not available"
            }
        
        try:
            # Process question through Q&A engine
            result = await self.qa_engine.answer_question(
                chapter_id=chapter_id,
                question=question,
                user_id=user_id,
                context=context
            )
            
            # Track in behavioral learning if available
            if self.behavioral_learning:
                await self.behavioral_learning.track_interaction(
                    user_id=user_id,
                    chapter_id=chapter_id,
                    interaction_type="qa",
                    metadata={
                        "question": question,
                        "confidence": result.get("confidence", 0)
                    }
                )
            
            return {
                "success": True,
                "answer": result.get("answer"),
                "confidence": result.get("confidence"),
                "sources": result.get("sources", []),
                "should_integrate": result.get("should_integrate", False)
            }
            
        except Exception as e:
            logger.error(f"Question processing failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_citation_network(
        self,
        chapter_id: str
    ) -> Dict[str, Any]:
        """
        Get citation network for a chapter
        """
        if not self.citation_network:
            return {
                "success": False,
                "error": "Citation network not available"
            }
        
        try:
            network = await self.citation_network.get_network(chapter_id)
            
            return {
                "success": True,
                "network": network
            }
            
        except Exception as e:
            logger.error(f"Citation network retrieval failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def suggest_citations(
        self,
        chapter_id: str,
        content: str
    ) -> Dict[str, Any]:
        """
        Suggest citations for content
        """
        if not self.citation_network:
            return {
                "success": False,
                "error": "Citation network not available"
            }
        
        try:
            suggestions = await self.citation_network.suggest_citations(
                chapter_id=chapter_id,
                content=content
            )
            
            return {
                "success": True,
                "suggestions": suggestions
            }
            
        except Exception as e:
            logger.error(f"Citation suggestion failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def merge_new_knowledge(
        self,
        chapter_id: str,
        new_content: str,
        source: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Intelligently merge new knowledge into chapter
        """
        if not self.nuance_merge:
            return {
                "success": False,
                "error": "Nuance merge engine not available"
            }
        
        try:
            result = await self.nuance_merge.merge(
                chapter_id=chapter_id,
                new_content=new_content,
                source=source,
                metadata=metadata
            )
            
            return {
                "success": True,
                "merged": result.get("merged"),
                "conflicts": result.get("conflicts", []),
                "changes": result.get("changes", [])
            }
            
        except Exception as e:
            logger.error(f"Knowledge merge failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_behavioral_suggestions(
        self,
        user_id: str,
        chapter_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get personalized suggestions based on behavioral learning
        """
        if not self.behavioral_learning:
            return {
                "success": False,
                "error": "Behavioral learning not available"
            }
        
        try:
            suggestions = await self.behavioral_learning.get_suggestions(
                user_id=user_id,
                chapter_id=chapter_id
            )
            
            return {
                "success": True,
                "suggestions": suggestions
            }
            
        except Exception as e:
            logger.error(f"Behavioral suggestions failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_chapter_health(
        self,
        chapter_id: str,
        user_id: str = "default_user"
    ) -> Dict[str, Any]:
        """
        Get comprehensive health metrics for an alive chapter
        """
        try:
            health_metrics = {
                "chapter_id": chapter_id,
                "timestamp": datetime.now().isoformat(),
                "overall_health_score": 0.0,
                "components": {}
            }
            
            scores = []
            
            # Q&A health
            if self.qa_engine:
                try:
                    qa_history = await self.qa_engine.get_history(chapter_id)
                    qa_score = min(len(qa_history) / 10, 1.0)  # Max at 10 questions
                    health_metrics["components"]["qa_activity"] = {
                        "score": qa_score,
                        "total_questions": len(qa_history)
                    }
                    scores.append(qa_score)
                except Exception as e:
                    logger.warning(f"Q&A health check failed: {e}")
            
            # Citation health
            if self.citation_network:
                try:
                    network = await self.citation_network.get_network(chapter_id)
                    citation_count = len(network.get("citations", []))
                    citation_score = min(citation_count / 20, 1.0)  # Max at 20 citations
                    health_metrics["components"]["citation_health"] = {
                        "score": citation_score,
                        "citation_count": citation_count
                    }
                    scores.append(citation_score)
                except Exception as e:
                    logger.warning(f"Citation health check failed: {e}")
            
            # Behavioral insights
            if self.behavioral_learning:
                try:
                    suggestions = await self.behavioral_learning.get_suggestions(
                        user_id=user_id,
                        chapter_id=chapter_id
                    )
                    behavioral_score = min(len(suggestions) / 5, 1.0)  # Max at 5 suggestions
                    health_metrics["components"]["behavioral_insights"] = {
                        "score": behavioral_score,
                        "suggestion_count": len(suggestions)
                    }
                    scores.append(behavioral_score)
                except Exception as e:
                    logger.warning(f"Behavioral health check failed: {e}")
            
            # Calculate overall health
            if scores:
                health_metrics["overall_health_score"] = sum(scores) / len(scores)
            
            return {
                "success": True,
                "health_metrics": health_metrics
            }
            
        except Exception as e:
            logger.error(f"Chapter health check failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def evolve_chapter(
        self,
        chapter_id: str,
        user_id: str = "default_user"
    ) -> Dict[str, Any]:
        """
        Trigger complete chapter evolution based on all available data
        """
        try:
            evolution_steps = []
            
            # Step 1: Analyze behavioral patterns
            if self.behavioral_learning:
                suggestions = await self.get_behavioral_suggestions(user_id, chapter_id)
                evolution_steps.append({
                    "step": "behavioral_analysis",
                    "suggestions": suggestions.get("suggestions", [])
                })
            
            # Step 2: Update citations
            if self.citation_network:
                # Placeholder for citation updates
                evolution_steps.append({
                    "step": "citation_update",
                    "status": "pending"
                })
            
            # Step 3: Integrate Q&A insights
            if self.qa_engine:
                # Placeholder for Q&A integration
                evolution_steps.append({
                    "step": "qa_integration",
                    "status": "pending"
                })
            
            return {
                "success": True,
                "chapter_id": chapter_id,
                "evolution_steps": evolution_steps,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Chapter evolution failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Global instance
alive_chapter_integration = AliveChapterIntegration()
