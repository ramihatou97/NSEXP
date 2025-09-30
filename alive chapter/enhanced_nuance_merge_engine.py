# backend/core/enhanced_nuance_merge_engine.py
"""
Enhanced Nuance Merge Engine for Alive Chapter System
Extends the base nuance merge engine with behavioral learning integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the base nuance merge engine from EXM
# Add parent directory to path to access EXM modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from nuance_merge_engine import (
    NuanceMergeEngine, DetectedNuance, NuanceType, MergeCategory,
    SimilarityMetrics, MedicalContext, SentenceAnalysis,
    NuanceDetectionConfig, SimilarityAlgorithm
)

# Import behavioral learning and Q&A engines
from chapter_behavioral_learning import ChapterBehavioralLearningEngine
from chapter_qa_engine import ChapterQAEngine
from citation_network_engine import CitationNetworkEngine

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import logging
import hashlib
import asyncio

logger = logging.getLogger(__name__)

class EnhancedNuanceMergeEngine(NuanceMergeEngine):
    """
    Enhanced Nuance Merge Engine with Alive Chapter capabilities
    Integrates behavioral learning, Q&A knowledge, and citation networks
    """

    def __init__(self, ai_manager=None):
        """Initialize enhanced merge engine with all intelligent systems"""
        super().__init__(ai_manager)

        # Initialize intelligent systems
        self.behavioral_learning = ChapterBehavioralLearningEngine()
        self.qa_engine = ChapterQAEngine()
        self.citation_network = CitationNetworkEngine()

        # Track merge patterns for learning
        self.merge_history = []
        self.user_preferences = {}

        logger.info("Enhanced Nuance Merge Engine initialized with Alive Chapter capabilities")

    async def intelligent_knowledge_integration(
        self,
        chapter_content: str,
        new_knowledge: Dict[str, Any],
        chapter_id: str,
        user_id: str,
        integration_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Intelligently integrate new knowledge from Q&A or behavioral anticipation

        Args:
            chapter_content: Current chapter content
            new_knowledge: New knowledge to integrate (from Q&A, searches, etc.)
            chapter_id: Chapter identifier
            user_id: User identifier for personalization
            integration_context: Context about the integration request

        Returns:
            Integrated content with full analysis
        """

        logger.info(f"Starting intelligent knowledge integration for chapter {chapter_id}")

        # Learn from this integration attempt
        await self.behavioral_learning.learn_from_interaction({
            "user_id": user_id,
            "chapter_id": chapter_id,
            "type": "knowledge_integration",
            "context_before": chapter_content[:500],  # First 500 chars
            "metadata": integration_context
        })

        # Get user preferences from behavioral learning
        user_prefs = await self._get_user_integration_preferences(user_id)

        # Detect nuances between current and new knowledge
        nuance = await self.detect_nuance(
            original=chapter_content,
            updated=new_knowledge.get("content", ""),
            config=self._get_user_config(user_prefs)
        )

        if not nuance:
            logger.info("No significant nuances detected, keeping original content")
            return {
                "status": "no_changes",
                "content": chapter_content,
                "reason": "No significant differences detected"
            }

        # Analyze integration points
        integration_analysis = await self._analyze_integration_points(
            chapter_content,
            new_knowledge,
            nuance
        )

        # Check for conflicts with existing knowledge
        conflicts = await self._detect_knowledge_conflicts(
            chapter_content,
            new_knowledge,
            chapter_id
        )

        # Resolve conflicts if any
        if conflicts:
            resolved_content = await self._resolve_conflicts(
                chapter_content,
                new_knowledge,
                conflicts,
                user_prefs
            )
        else:
            resolved_content = new_knowledge.get("content", chapter_content)

        # Apply behavioral learning insights
        enhanced_content = await self._apply_behavioral_insights(
            resolved_content,
            user_id,
            chapter_id,
            integration_context
        )

        # Perform nuanced merge
        merged_content = await self._perform_intelligent_merge(
            original=chapter_content,
            enhanced=enhanced_content,
            nuance=nuance,
            user_prefs=user_prefs
        )

        # Add citations and cross-references
        final_content = await self._add_citations_and_references(
            merged_content,
            new_knowledge.get("sources", []),
            chapter_id
        )

        # Track merge for learning
        await self._track_merge_pattern(
            user_id,
            chapter_id,
            nuance,
            integration_context
        )

        # Generate comprehensive response
        return {
            "status": "success",
            "content": final_content,
            "nuance_analysis": {
                "type": nuance.nuance_type.value,
                "confidence": nuance.confidence_score,
                "merge_category": nuance.merge_category.value,
                "medical_context": {
                    "concepts_added": nuance.medical_context.medical_concepts_added,
                    "clinical_relevance": nuance.medical_context.clinical_relevance_score
                }
            },
            "integration_points": integration_analysis,
            "conflicts_resolved": len(conflicts),
            "citations_added": len(new_knowledge.get("sources", [])),
            "behavioral_enhancements": await self._get_behavioral_enhancements(user_id),
            "quality_metrics": await self._calculate_quality_metrics(
                chapter_content,
                final_content
            )
        }

    async def merge_qa_answer(
        self,
        chapter_content: str,
        qa_answer: Dict[str, Any],
        chapter_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Merge Q&A answer into chapter content seamlessly

        Args:
            chapter_content: Current chapter content
            qa_answer: Answer from Q&A engine
            chapter_id: Chapter identifier
            user_id: User identifier

        Returns:
            Merged content with Q&A integration
        """

        # Prepare new knowledge from Q&A answer
        new_knowledge = {
            "content": qa_answer.get("answer", ""),
            "sources": qa_answer.get("sources", []),
            "confidence": qa_answer.get("confidence", 0.5),
            "integration_strategy": qa_answer.get("integration_strategy", "inline_expansion")
        }

        # Integration context
        integration_context = {
            "type": "qa_integration",
            "question": qa_answer.get("question", ""),
            "answer_confidence": qa_answer.get("confidence", 0.5),
            "medical_accuracy": qa_answer.get("medical_accuracy", 0.8)
        }

        # Use intelligent integration
        result = await self.intelligent_knowledge_integration(
            chapter_content=chapter_content,
            new_knowledge=new_knowledge,
            chapter_id=chapter_id,
            user_id=user_id,
            integration_context=integration_context
        )

        return result

    async def merge_anticipated_knowledge(
        self,
        chapter_content: str,
        anticipated_needs: List[Dict[str, Any]],
        chapter_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Proactively merge anticipated knowledge needs

        Args:
            chapter_content: Current chapter content
            anticipated_needs: Knowledge anticipated by behavioral learning
            chapter_id: Chapter identifier
            user_id: User identifier

        Returns:
            Enhanced content with anticipated knowledge
        """

        merged_content = chapter_content
        total_enhancements = []

        # Process each anticipated need
        for need in anticipated_needs[:3]:  # Limit to top 3 needs
            if need.get("auto_fillable", False) and need.get("confidence", 0) > 0.7:

                # Fetch knowledge for this need
                fetched_knowledge = await self._fetch_anticipated_knowledge(need)

                if fetched_knowledge:
                    # Merge this knowledge
                    integration_result = await self.intelligent_knowledge_integration(
                        chapter_content=merged_content,
                        new_knowledge=fetched_knowledge,
                        chapter_id=chapter_id,
                        user_id=user_id,
                        integration_context={
                            "type": "anticipated_knowledge",
                            "need_type": need.get("type"),
                            "confidence": need.get("confidence")
                        }
                    )

                    if integration_result.get("status") == "success":
                        merged_content = integration_result.get("content", merged_content)
                        total_enhancements.append({
                            "need_type": need.get("type"),
                            "confidence": need.get("confidence"),
                            "applied": True
                        })

        return {
            "status": "success",
            "content": merged_content,
            "enhancements_applied": total_enhancements,
            "total_enhancements": len(total_enhancements)
        }

    async def apply_citation_network(
        self,
        chapter_content: str,
        chapter_id: str,
        all_chapters: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Apply citation network to add cross-references

        Args:
            chapter_content: Current chapter content
            chapter_id: Chapter identifier
            all_chapters: All chapters for cross-referencing

        Returns:
            Content with citations and cross-references
        """

        # Build citation network
        network_result = await self.citation_network.build_citation_network(all_chapters)

        # Detect cross-references for this chapter
        cross_refs = await self.citation_network.detect_cross_references(
            chapter_content,
            chapter_id
        )

        # Suggest citations
        citation_suggestions = await self.citation_network.suggest_citations(
            chapter_content,
            chapter_id
        )

        # Apply citations to content
        cited_content = chapter_content
        citations_added = 0

        for suggestion in citation_suggestions[:5]:  # Top 5 suggestions
            if suggestion.get("relevance_score", 0) > 0.7:
                # Insert citation at suggested point
                citation_text = suggestion.get("suggested_citation_text", "")
                insertion_point = suggestion.get("insertion_point", len(cited_content))

                cited_content = (
                    cited_content[:insertion_point] +
                    f" {citation_text}" +
                    cited_content[insertion_point:]
                )
                citations_added += 1

        return {
            "status": "success",
            "content": cited_content,
            "cross_references_detected": len(cross_refs),
            "citations_added": citations_added,
            "network_metrics": network_result.get("metrics", {})
        }

    # ========================================================================
    # PRIVATE HELPER METHODS
    # ========================================================================

    async def _get_user_integration_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user's integration preferences from behavioral learning"""

        # Get from behavioral learning system
        user_prefs = await self.behavioral_learning.learning_patterns.get_user_preferences(user_id)

        # Add merge-specific preferences
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {
                "merge_strategy": "conservative",  # conservative, balanced, aggressive
                "auto_apply_threshold": 0.85,
                "preserve_style": True,
                "add_citations": True,
                "conflict_resolution": "prefer_quality"  # prefer_quality, prefer_recent, manual
            }

        # Merge with learned preferences
        self.user_preferences[user_id].update(user_prefs.get("preferences", {}))

        return self.user_preferences[user_id]

    def _get_user_config(self, user_prefs: Dict[str, Any]) -> NuanceDetectionConfig:
        """Get nuance detection config based on user preferences"""

        config = NuanceDetectionConfig()

        # Adjust thresholds based on merge strategy
        if user_prefs.get("merge_strategy") == "aggressive":
            config.auto_apply_threshold = 0.75
            config.require_review_threshold = 0.65
        elif user_prefs.get("merge_strategy") == "conservative":
            config.auto_apply_threshold = 0.90
            config.require_review_threshold = 0.85

        config.auto_apply_threshold = user_prefs.get("auto_apply_threshold", config.auto_apply_threshold)

        return config

    async def _analyze_integration_points(
        self,
        original: str,
        new_knowledge: Dict[str, Any],
        nuance: DetectedNuance
    ) -> List[Dict[str, Any]]:
        """Analyze where and how to integrate new knowledge"""

        integration_points = []

        # Analyze sentence-level changes
        for analysis in nuance.sentence_analyses:
            if analysis.clinical_importance_score > 0.5:
                integration_points.append({
                    "position": analysis.sentence_position,
                    "type": analysis.change_type,
                    "importance": analysis.clinical_importance_score,
                    "impact": analysis.impact_category,
                    "content": analysis.enhanced_sentence[:100]  # First 100 chars
                })

        return integration_points

    async def _detect_knowledge_conflicts(
        self,
        original: str,
        new_knowledge: Dict[str, Any],
        chapter_id: str
    ) -> List[Dict[str, Any]]:
        """Detect conflicts between existing and new knowledge"""

        conflicts = []

        # Simple conflict detection (would be more sophisticated)
        original_lower = original.lower()
        new_content = new_knowledge.get("content", "").lower()

        # Check for contradictory statements
        contradictions = [
            ("increases", "decreases"),
            ("effective", "ineffective"),
            ("recommended", "not recommended"),
            ("safe", "dangerous")
        ]

        for term1, term2 in contradictions:
            if term1 in original_lower and term2 in new_content:
                conflicts.append({
                    "type": "contradiction",
                    "original_statement": term1,
                    "new_statement": term2,
                    "severity": "high"
                })
            elif term2 in original_lower and term1 in new_content:
                conflicts.append({
                    "type": "contradiction",
                    "original_statement": term2,
                    "new_statement": term1,
                    "severity": "high"
                })

        return conflicts

    async def _resolve_conflicts(
        self,
        original: str,
        new_knowledge: Dict[str, Any],
        conflicts: List[Dict[str, Any]],
        user_prefs: Dict[str, Any]
    ) -> str:
        """Resolve conflicts based on user preferences"""

        resolution_strategy = user_prefs.get("conflict_resolution", "prefer_quality")

        if resolution_strategy == "prefer_quality":
            # Prefer content with higher confidence/quality
            if new_knowledge.get("confidence", 0) > 0.8:
                return new_knowledge.get("content", original)
            else:
                return original

        elif resolution_strategy == "prefer_recent":
            # Prefer newer content
            return new_knowledge.get("content", original)

        else:
            # Manual resolution - keep original and flag for review
            return original

    async def _apply_behavioral_insights(
        self,
        content: str,
        user_id: str,
        chapter_id: str,
        context: Dict[str, Any]
    ) -> str:
        """Apply insights from behavioral learning"""

        # Get anticipated needs
        anticipation_result = await self.behavioral_learning.anticipate_knowledge_needs({
            "user_id": user_id,
            "chapter_id": chapter_id,
            "content": content,
            **context
        })

        # Get knowledge gaps
        gaps = anticipation_result.get("knowledge_gaps", [])

        # Add markers for gaps (simplified)
        enhanced_content = content
        for gap in gaps[:3]:  # Top 3 gaps
            if gap.get("auto_fillable"):
                marker = f"\n[Knowledge Gap: {gap.get('description')} - Priority: {gap.get('confidence'):.2f}]\n"
                enhanced_content += marker

        return enhanced_content

    async def _perform_intelligent_merge(
        self,
        original: str,
        enhanced: str,
        nuance: DetectedNuance,
        user_prefs: Dict[str, Any]
    ) -> str:
        """Perform the actual intelligent merge"""

        # Use parent class method with enhancements
        merged = await self._apply_nuance(original, nuance)

        # Apply user preferences
        if user_prefs.get("preserve_style"):
            # Preserve original writing style (simplified)
            # Would use more sophisticated style transfer
            merged = merged

        return merged

    async def _add_citations_and_references(
        self,
        content: str,
        sources: List[Dict[str, Any]],
        chapter_id: str
    ) -> str:
        """Add citations and cross-references to content"""

        if not sources:
            return content

        # Add citations section
        citations_text = "\n\n## References\n"
        for i, source in enumerate(sources, 1):
            citation = f"[{i}] {source.get('title', 'Unknown')} - {source.get('source', 'Unknown')}\n"
            citations_text += citation

        # Add to content if not already present
        if "## References" not in content:
            content += citations_text

        return content

    async def _track_merge_pattern(
        self,
        user_id: str,
        chapter_id: str,
        nuance: DetectedNuance,
        context: Dict[str, Any]
    ):
        """Track merge pattern for learning"""

        merge_record = {
            "user_id": user_id,
            "chapter_id": chapter_id,
            "timestamp": datetime.now(),
            "nuance_type": nuance.nuance_type.value,
            "confidence": nuance.confidence_score,
            "merge_category": nuance.merge_category.value,
            "context": context
        }

        self.merge_history.append(merge_record)

        # Learn from this merge
        await self.behavioral_learning.learn_from_interaction({
            "user_id": user_id,
            "chapter_id": chapter_id,
            "type": "merge_completed",
            "metadata": merge_record
        })

    async def _get_behavioral_enhancements(self, user_id: str) -> Dict[str, Any]:
        """Get behavioral enhancements applied"""

        suggestions = await self.behavioral_learning.get_proactive_suggestions(
            "current_chapter",
            user_id
        )

        return {
            "suggestions_count": len(suggestions),
            "top_suggestion": suggestions[0] if suggestions else None
        }

    async def _calculate_quality_metrics(
        self,
        original: str,
        merged: str
    ) -> Dict[str, float]:
        """Calculate quality metrics for merged content"""

        metrics = {
            "content_growth": len(merged) / len(original) if original else 1.0,
            "medical_term_density": self._calculate_medical_term_density(merged),
            "readability": self._calculate_readability(merged),
            "completeness": min(1.0, len(merged) / 5000)  # Assume 5000 chars is complete
        }

        # Overall quality score
        metrics["overall_quality"] = sum(metrics.values()) / len(metrics)

        return metrics

    def _calculate_medical_term_density(self, text: str) -> float:
        """Calculate density of medical terms"""

        medical_terms = []
        for patterns in self.medical_patterns.values():
            terms = self._identify_medical_terms(text, patterns)
            medical_terms.extend(terms)

        word_count = len(text.split())
        if word_count == 0:
            return 0.0

        return min(1.0, len(medical_terms) / word_count * 10)  # Normalize

    def _calculate_readability(self, text: str) -> float:
        """Calculate readability score"""

        sentences = [s for s in text.split('.') if s.strip()]
        words = text.split()

        if not sentences or not words:
            return 0.5

        avg_sentence_length = len(words) / len(sentences)

        # Simple readability formula
        if avg_sentence_length < 15:
            return 0.9
        elif avg_sentence_length < 25:
            return 0.7
        else:
            return 0.5

    async def _fetch_anticipated_knowledge(
        self,
        need: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Fetch knowledge for an anticipated need"""

        # This would integrate with research engines
        # For now, return mock data
        return {
            "content": f"Additional information for {need.get('type', 'unknown')} need",
            "sources": [{"title": "Anticipated Knowledge", "source": "System"}],
            "confidence": need.get("confidence", 0.5)
        }

# Initialize global instance
enhanced_nuance_merge = EnhancedNuanceMergeEngine()