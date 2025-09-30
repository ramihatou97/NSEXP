# backend/core/chapter_behavioral_learning.py
"""
Chapter Behavioral Learning Engine
Learns from user interactions to anticipate knowledge needs and optimize chapter evolution
"""

from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
import asyncio
import json
import hashlib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)

class InteractionType(Enum):
    READ = "read"
    EDIT = "edit"
    SEARCH = "search"
    QUESTION = "question"
    CITATION_ADD = "citation_add"
    EXTERNAL_REFERENCE = "external_reference"
    HIGHLIGHT = "highlight"
    ANNOTATION = "annotation"
    SECTION_FOCUS = "section_focus"
    KNOWLEDGE_GAP_IDENTIFIED = "knowledge_gap_identified"

class KnowledgeNeedType(Enum):
    DEFINITION = "definition"
    CLINICAL_EVIDENCE = "clinical_evidence"
    TREATMENT_PROTOCOL = "treatment_protocol"
    DIAGNOSTIC_CRITERIA = "diagnostic_criteria"
    PATHOPHYSIOLOGY = "pathophysiology"
    EPIDEMIOLOGY = "epidemiology"
    DIFFERENTIAL_DIAGNOSIS = "differential_diagnosis"
    COMPLICATIONS = "complications"
    RECENT_RESEARCH = "recent_research"
    CASE_STUDIES = "case_studies"

@dataclass
class UserInteraction:
    interaction_id: str
    user_id: str
    chapter_id: str
    interaction_type: InteractionType
    timestamp: datetime
    context_before: str  # Content context before interaction
    context_after: Optional[str]  # Content context after interaction
    metadata: Dict[str, Any]
    session_id: str
    duration_seconds: float
    scroll_depth: float = 0.0
    focus_area: Optional[str] = None

@dataclass
class KnowledgeGap:
    gap_id: str
    chapter_id: str
    gap_type: KnowledgeNeedType
    description: str
    confidence: float
    detected_at: datetime
    context: str
    related_concepts: List[str]
    suggested_sources: List[str]
    priority_score: float
    auto_fillable: bool

@dataclass
class LearningPattern:
    pattern_id: str
    pattern_type: str
    frequency: int
    confidence: float
    temporal_sequence: List[str]
    context_triggers: List[str]
    predicted_next_actions: List[Tuple[str, float]]  # (action, probability)
    last_observed: datetime

@dataclass
class AnticipatedNeed:
    need_id: str
    chapter_id: str
    need_type: KnowledgeNeedType
    anticipated_content: str
    confidence: float
    trigger_context: str
    preparation_actions: List[str]
    prefetch_sources: List[str]
    estimated_time_until_needed: timedelta
    priority: int

class InteractionMemory:
    """Stores and retrieves user interaction history with intelligent indexing"""

    def __init__(self, memory_size: int = 10000):
        self.interactions = deque(maxlen=memory_size)
        self.interaction_index = defaultdict(list)  # Index by chapter_id
        self.user_index = defaultdict(list)  # Index by user_id
        self.pattern_cache = {}
        self.sequence_memory = defaultdict(list)

    async def store_interaction(self, interaction: UserInteraction):
        """Store interaction with intelligent indexing"""
        self.interactions.append(interaction)
        self.interaction_index[interaction.chapter_id].append(interaction)
        self.user_index[interaction.user_id].append(interaction)

        # Update sequence memory
        session_key = f"{interaction.user_id}:{interaction.session_id}"
        self.sequence_memory[session_key].append(interaction)

        # Invalidate pattern cache
        if interaction.chapter_id in self.pattern_cache:
            del self.pattern_cache[interaction.chapter_id]

    async def get_interaction_patterns(self, chapter_id: str,
                                      lookback_hours: int = 72) -> List[LearningPattern]:
        """Extract learning patterns from interactions"""
        if chapter_id in self.pattern_cache:
            cached_patterns, cache_time = self.pattern_cache[chapter_id]
            if datetime.now() - cache_time < timedelta(minutes=30):
                return cached_patterns

        cutoff_time = datetime.now() - timedelta(hours=lookback_hours)
        relevant_interactions = [
            i for i in self.interaction_index[chapter_id]
            if i.timestamp > cutoff_time
        ]

        patterns = await self._extract_patterns(relevant_interactions)
        self.pattern_cache[chapter_id] = (patterns, datetime.now())

        return patterns

    async def _extract_patterns(self, interactions: List[UserInteraction]) -> List[LearningPattern]:
        """Extract meaningful patterns from interaction sequences"""
        patterns = []

        # Temporal sequence analysis
        sequences = defaultdict(int)
        for i in range(len(interactions) - 1):
            seq = (interactions[i].interaction_type.value,
                   interactions[i+1].interaction_type.value)
            sequences[seq] += 1

        # Create patterns from frequent sequences
        for seq, count in sequences.items():
            if count >= 3:  # Minimum frequency threshold
                pattern = LearningPattern(
                    pattern_id=hashlib.md5(str(seq).encode()).hexdigest()[:8],
                    pattern_type="temporal_sequence",
                    frequency=count,
                    confidence=min(0.9, count / 10),  # Confidence based on frequency
                    temporal_sequence=list(seq),
                    context_triggers=[],
                    predicted_next_actions=await self._predict_next_actions(seq, interactions),
                    last_observed=datetime.now()
                )
                patterns.append(pattern)

        return patterns

    async def _predict_next_actions(self, sequence: Tuple[str, str],
                                   interactions: List[UserInteraction]) -> List[Tuple[str, float]]:
        """Predict likely next actions based on sequence"""
        next_actions = defaultdict(int)

        for i in range(len(interactions) - 2):
            if (interactions[i].interaction_type.value == sequence[0] and
                interactions[i+1].interaction_type.value == sequence[1]):
                if i + 2 < len(interactions):
                    next_actions[interactions[i+2].interaction_type.value] += 1

        total = sum(next_actions.values())
        if total == 0:
            return []

        predictions = [(action, count/total) for action, count in next_actions.items()]
        return sorted(predictions, key=lambda x: x[1], reverse=True)[:3]

class KnowledgeGapDetector:
    """Detects knowledge gaps in chapters based on various signals"""

    def __init__(self):
        self.medical_concepts_db = self._load_medical_concepts()
        self.gap_templates = self._initialize_gap_templates()
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000)

    def _load_medical_concepts(self) -> Set[str]:
        """Load database of medical concepts for gap detection"""
        # This would be loaded from a comprehensive medical database
        return {
            "pathophysiology", "etiology", "epidemiology", "clinical_presentation",
            "diagnosis", "differential_diagnosis", "treatment", "prognosis",
            "complications", "prevention", "risk_factors", "imaging_findings",
            "laboratory_findings", "histopathology", "genetics", "pharmacology"
        }

    def _initialize_gap_templates(self) -> Dict[KnowledgeNeedType, List[str]]:
        """Initialize templates for detecting different types of knowledge gaps"""
        return {
            KnowledgeNeedType.DEFINITION: [
                "what is", "define", "meaning of", "explanation of"
            ],
            KnowledgeNeedType.CLINICAL_EVIDENCE: [
                "evidence", "studies show", "research indicates", "clinical trials"
            ],
            KnowledgeNeedType.TREATMENT_PROTOCOL: [
                "treatment", "management", "therapy", "intervention", "protocol"
            ],
            KnowledgeNeedType.DIAGNOSTIC_CRITERIA: [
                "diagnosis", "criteria", "assessment", "evaluation", "testing"
            ],
            KnowledgeNeedType.PATHOPHYSIOLOGY: [
                "mechanism", "pathogenesis", "process", "development"
            ],
            KnowledgeNeedType.RECENT_RESEARCH: [
                "recent", "latest", "new findings", "current research", "2024", "2023"
            ]
        }

    async def detect_gaps(self, chapter_content: str,
                         interaction_context: Dict[str, Any]) -> List[KnowledgeGap]:
        """Detect knowledge gaps in chapter content"""
        gaps = []

        # Content completeness analysis
        completeness_gaps = await self._analyze_content_completeness(chapter_content)
        gaps.extend(completeness_gaps)

        # Interaction-based gap detection
        if "user_questions" in interaction_context:
            question_gaps = await self._analyze_user_questions(
                interaction_context["user_questions"],
                chapter_content
            )
            gaps.extend(question_gaps)

        # Medical concept coverage analysis
        concept_gaps = await self._analyze_concept_coverage(chapter_content)
        gaps.extend(concept_gaps)

        # Research currency analysis
        research_gaps = await self._analyze_research_currency(chapter_content)
        gaps.extend(research_gaps)

        # Prioritize gaps
        gaps = await self._prioritize_gaps(gaps)

        return gaps

    async def _analyze_content_completeness(self, content: str) -> List[KnowledgeGap]:
        """Analyze if content covers all essential medical aspects"""
        gaps = []
        content_lower = content.lower()

        essential_sections = {
            "epidemiology": KnowledgeNeedType.EPIDEMIOLOGY,
            "pathophysiology": KnowledgeNeedType.PATHOPHYSIOLOGY,
            "clinical presentation": KnowledgeNeedType.CLINICAL_EVIDENCE,
            "diagnosis": KnowledgeNeedType.DIAGNOSTIC_CRITERIA,
            "treatment": KnowledgeNeedType.TREATMENT_PROTOCOL,
            "complications": KnowledgeNeedType.COMPLICATIONS,
            "prognosis": KnowledgeNeedType.CLINICAL_EVIDENCE
        }

        for section, need_type in essential_sections.items():
            if section not in content_lower:
                gap = KnowledgeGap(
                    gap_id=hashlib.md5(f"{section}_{datetime.now()}".encode()).hexdigest()[:8],
                    chapter_id="current",
                    gap_type=need_type,
                    description=f"Missing section: {section}",
                    confidence=0.85,
                    detected_at=datetime.now(),
                    context=f"Essential medical content section '{section}' not found",
                    related_concepts=[section],
                    suggested_sources=["PubMed", "UpToDate", "Medical textbooks"],
                    priority_score=0.8,
                    auto_fillable=True
                )
                gaps.append(gap)

        return gaps

    async def _analyze_user_questions(self, questions: List[str],
                                     content: str) -> List[KnowledgeGap]:
        """Analyze user questions to identify knowledge gaps"""
        gaps = []

        for question in questions:
            question_lower = question.lower()

            # Check if question indicates a gap
            for need_type, templates in self.gap_templates.items():
                if any(template in question_lower for template in templates):
                    # Check if content addresses this question
                    if not await self._content_addresses_question(question, content):
                        gap = KnowledgeGap(
                            gap_id=hashlib.md5(f"{question}_{datetime.now()}".encode()).hexdigest()[:8],
                            chapter_id="current",
                            gap_type=need_type,
                            description=f"User question not addressed: {question}",
                            confidence=0.9,
                            detected_at=datetime.now(),
                            context=question,
                            related_concepts=await self._extract_concepts_from_question(question),
                            suggested_sources=["Research papers", "Clinical guidelines"],
                            priority_score=0.95,  # High priority for user questions
                            auto_fillable=True
                        )
                        gaps.append(gap)
                    break

        return gaps

    async def _analyze_concept_coverage(self, content: str) -> List[KnowledgeGap]:
        """Analyze coverage of medical concepts"""
        gaps = []
        content_lower = content.lower()

        # Extract mentioned concepts
        mentioned_concepts = set()
        for concept in self.medical_concepts_db:
            if concept in content_lower:
                mentioned_concepts.add(concept)

        # Identify missing related concepts
        expected_concepts = self.medical_concepts_db - mentioned_concepts

        for concept in list(expected_concepts)[:5]:  # Limit to top 5 gaps
            gap = KnowledgeGap(
                gap_id=hashlib.md5(f"{concept}_{datetime.now()}".encode()).hexdigest()[:8],
                chapter_id="current",
                gap_type=KnowledgeNeedType.DEFINITION,
                description=f"Medical concept not covered: {concept}",
                confidence=0.7,
                detected_at=datetime.now(),
                context=f"Expected medical concept '{concept}' not found in content",
                related_concepts=[concept],
                suggested_sources=["Medical literature", "Clinical resources"],
                priority_score=0.6,
                auto_fillable=True
            )
            gaps.append(gap)

        return gaps

    async def _analyze_research_currency(self, content: str) -> List[KnowledgeGap]:
        """Analyze if content includes recent research"""
        gaps = []

        # Check for recent year mentions
        current_year = datetime.now().year
        recent_years = [str(year) for year in range(current_year - 2, current_year + 1)]

        has_recent_research = any(year in content for year in recent_years)

        if not has_recent_research:
            gap = KnowledgeGap(
                gap_id=hashlib.md5(f"research_currency_{datetime.now()}".encode()).hexdigest()[:8],
                chapter_id="current",
                gap_type=KnowledgeNeedType.RECENT_RESEARCH,
                description="Content lacks recent research references",
                confidence=0.8,
                detected_at=datetime.now(),
                context="No references to research from the last 2 years",
                related_concepts=["recent studies", "current research", "latest findings"],
                suggested_sources=["PubMed recent articles", "Clinical trial databases"],
                priority_score=0.75,
                auto_fillable=True
            )
            gaps.append(gap)

        return gaps

    async def _content_addresses_question(self, question: str, content: str) -> bool:
        """Check if content addresses a specific question"""
        # Simple similarity check - could be enhanced with semantic search
        question_words = set(question.lower().split())
        content_words = set(content.lower().split())

        overlap = len(question_words & content_words) / len(question_words)
        return overlap > 0.5

    async def _extract_concepts_from_question(self, question: str) -> List[str]:
        """Extract medical concepts from a question"""
        concepts = []
        question_lower = question.lower()

        for concept in self.medical_concepts_db:
            if concept in question_lower:
                concepts.append(concept)

        return concepts

    async def _prioritize_gaps(self, gaps: List[KnowledgeGap]) -> List[KnowledgeGap]:
        """Prioritize gaps based on importance and confidence"""
        return sorted(gaps, key=lambda g: g.priority_score * g.confidence, reverse=True)

class AnticipationEngine:
    """Anticipates user knowledge needs based on patterns and context"""

    def __init__(self):
        self.prediction_models = {}
        self.anticipation_cache = {}
        self.prefetch_queue = asyncio.Queue()
        self.learning_rate = 0.1

    async def anticipate_needs(self,
                               chapter_context: Dict[str, Any],
                               user_patterns: List[LearningPattern],
                               knowledge_gaps: List[KnowledgeGap]) -> List[AnticipatedNeed]:
        """Anticipate what knowledge the user will need next"""
        anticipated_needs = []

        # Pattern-based anticipation
        pattern_needs = await self._anticipate_from_patterns(user_patterns, chapter_context)
        anticipated_needs.extend(pattern_needs)

        # Gap-based anticipation
        gap_needs = await self._anticipate_from_gaps(knowledge_gaps, chapter_context)
        anticipated_needs.extend(gap_needs)

        # Temporal anticipation (what users typically need at this stage)
        temporal_needs = await self._anticipate_from_temporal_context(chapter_context)
        anticipated_needs.extend(temporal_needs)

        # Content progression anticipation
        progression_needs = await self._anticipate_from_content_progression(chapter_context)
        anticipated_needs.extend(progression_needs)

        # Deduplicate and prioritize
        anticipated_needs = await self._prioritize_anticipated_needs(anticipated_needs)

        # Queue for prefetching
        await self._queue_for_prefetch(anticipated_needs[:5])  # Top 5 needs

        return anticipated_needs

    async def _anticipate_from_patterns(self, patterns: List[LearningPattern],
                                       context: Dict[str, Any]) -> List[AnticipatedNeed]:
        """Anticipate needs based on learning patterns"""
        needs = []

        for pattern in patterns:
            if pattern.confidence > 0.7:
                for action, probability in pattern.predicted_next_actions:
                    if probability > 0.5:
                        need = await self._create_anticipated_need_from_action(
                            action, probability, pattern, context
                        )
                        if need:
                            needs.append(need)

        return needs

    async def _anticipate_from_gaps(self, gaps: List[KnowledgeGap],
                                   context: Dict[str, Any]) -> List[AnticipatedNeed]:
        """Anticipate needs based on detected gaps"""
        needs = []

        for gap in gaps[:5]:  # Top 5 gaps
            if gap.auto_fillable and gap.priority_score > 0.7:
                need = AnticipatedNeed(
                    need_id=f"gap_{gap.gap_id}",
                    chapter_id=gap.chapter_id,
                    need_type=gap.gap_type,
                    anticipated_content=gap.description,
                    confidence=gap.confidence,
                    trigger_context=gap.context,
                    preparation_actions=[
                        f"search_{gap.gap_type.value}",
                        "fetch_relevant_papers",
                        "prepare_synthesis"
                    ],
                    prefetch_sources=gap.suggested_sources,
                    estimated_time_until_needed=timedelta(minutes=5),
                    priority=int(gap.priority_score * 10)
                )
                needs.append(need)

        return needs

    async def _anticipate_from_temporal_context(self, context: Dict[str, Any]) -> List[AnticipatedNeed]:
        """Anticipate needs based on temporal patterns"""
        needs = []

        # Time of day patterns
        current_hour = datetime.now().hour

        if 9 <= current_hour <= 11:  # Morning - typically research time
            need = AnticipatedNeed(
                need_id=f"temporal_morning_{datetime.now().strftime('%Y%m%d')}",
                chapter_id=context.get("chapter_id", "current"),
                need_type=KnowledgeNeedType.RECENT_RESEARCH,
                anticipated_content="Morning research session - latest papers",
                confidence=0.7,
                trigger_context="Morning research pattern detected",
                preparation_actions=["fetch_recent_papers", "prepare_summaries"],
                prefetch_sources=["PubMed", "arXiv"],
                estimated_time_until_needed=timedelta(minutes=10),
                priority=7
            )
            needs.append(need)

        elif 14 <= current_hour <= 17:  # Afternoon - typically writing time
            need = AnticipatedNeed(
                need_id=f"temporal_afternoon_{datetime.now().strftime('%Y%m%d')}",
                chapter_id=context.get("chapter_id", "current"),
                need_type=KnowledgeNeedType.CLINICAL_EVIDENCE,
                anticipated_content="Afternoon writing - clinical evidence needed",
                confidence=0.6,
                trigger_context="Afternoon writing pattern detected",
                preparation_actions=["gather_clinical_evidence", "prepare_citations"],
                prefetch_sources=["Clinical guidelines", "Case studies"],
                estimated_time_until_needed=timedelta(minutes=15),
                priority=6
            )
            needs.append(need)

        return needs

    async def _anticipate_from_content_progression(self, context: Dict[str, Any]) -> List[AnticipatedNeed]:
        """Anticipate needs based on content progression"""
        needs = []

        current_section = context.get("current_section", "")

        # Standard medical content progression
        progression_map = {
            "introduction": KnowledgeNeedType.EPIDEMIOLOGY,
            "epidemiology": KnowledgeNeedType.PATHOPHYSIOLOGY,
            "pathophysiology": KnowledgeNeedType.CLINICAL_EVIDENCE,
            "clinical_presentation": KnowledgeNeedType.DIAGNOSTIC_CRITERIA,
            "diagnosis": KnowledgeNeedType.TREATMENT_PROTOCOL,
            "treatment": KnowledgeNeedType.COMPLICATIONS,
            "complications": KnowledgeNeedType.RECENT_RESEARCH
        }

        if current_section.lower() in progression_map:
            next_need_type = progression_map[current_section.lower()]

            need = AnticipatedNeed(
                need_id=f"progression_{current_section}_{datetime.now().strftime('%Y%m%d')}",
                chapter_id=context.get("chapter_id", "current"),
                need_type=next_need_type,
                anticipated_content=f"Next section: {next_need_type.value}",
                confidence=0.8,
                trigger_context=f"Following {current_section} section",
                preparation_actions=[
                    f"prepare_{next_need_type.value}_content",
                    "fetch_relevant_resources"
                ],
                prefetch_sources=["Medical databases", "Clinical resources"],
                estimated_time_until_needed=timedelta(minutes=20),
                priority=8
            )
            needs.append(need)

        return needs

    async def _create_anticipated_need_from_action(self, action: str, probability: float,
                                                  pattern: LearningPattern,
                                                  context: Dict[str, Any]) -> Optional[AnticipatedNeed]:
        """Create anticipated need from predicted action"""
        action_to_need_map = {
            "search": KnowledgeNeedType.RECENT_RESEARCH,
            "edit": KnowledgeNeedType.CLINICAL_EVIDENCE,
            "question": KnowledgeNeedType.DEFINITION,
            "citation_add": KnowledgeNeedType.CLINICAL_EVIDENCE,
            "external_reference": KnowledgeNeedType.RECENT_RESEARCH
        }

        if action in action_to_need_map:
            need_type = action_to_need_map[action]

            return AnticipatedNeed(
                need_id=f"pattern_{pattern.pattern_id}_{action}",
                chapter_id=context.get("chapter_id", "current"),
                need_type=need_type,
                anticipated_content=f"Predicted {action} - preparing {need_type.value}",
                confidence=probability * pattern.confidence,
                trigger_context=f"Pattern: {pattern.pattern_type}",
                preparation_actions=[f"prepare_for_{action}", "cache_resources"],
                prefetch_sources=["Relevant databases"],
                estimated_time_until_needed=timedelta(minutes=10),
                priority=int(probability * 10)
            )

        return None

    async def _prioritize_anticipated_needs(self, needs: List[AnticipatedNeed]) -> List[AnticipatedNeed]:
        """Prioritize and deduplicate anticipated needs"""
        # Deduplicate by need_type and chapter_id
        unique_needs = {}
        for need in needs:
            key = f"{need.chapter_id}_{need.need_type.value}"
            if key not in unique_needs or need.priority > unique_needs[key].priority:
                unique_needs[key] = need

        # Sort by priority and confidence
        sorted_needs = sorted(
            unique_needs.values(),
            key=lambda n: n.priority * n.confidence,
            reverse=True
        )

        return sorted_needs

    async def _queue_for_prefetch(self, needs: List[AnticipatedNeed]):
        """Queue anticipated needs for background prefetching"""
        for need in needs:
            await self.prefetch_queue.put(need)

class UserLearningPatterns:
    """Manages user-specific learning patterns and preferences"""

    def __init__(self):
        self.user_preferences = defaultdict(dict)
        self.expertise_levels = defaultdict(dict)
        self.writing_styles = defaultdict(str)
        self.peak_productivity_times = defaultdict(list)

    async def update_user_pattern(self, user_id: str, pattern_data: Dict[str, Any]):
        """Update user-specific patterns"""
        if "preference" in pattern_data:
            self.user_preferences[user_id].update(pattern_data["preference"])

        if "expertise" in pattern_data:
            domain = pattern_data["expertise"]["domain"]
            level = pattern_data["expertise"]["level"]
            self.expertise_levels[user_id][domain] = level

        if "writing_style" in pattern_data:
            self.writing_styles[user_id] = pattern_data["writing_style"]

        if "productivity_time" in pattern_data:
            self.peak_productivity_times[user_id].append(pattern_data["productivity_time"])

    async def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user preferences for personalization"""
        return {
            "preferences": self.user_preferences.get(user_id, {}),
            "expertise": self.expertise_levels.get(user_id, {}),
            "writing_style": self.writing_styles.get(user_id, "professional"),
            "peak_times": self.peak_productivity_times.get(user_id, [])
        }

class ChapterBehavioralLearningEngine:
    """
    Main engine that orchestrates behavioral learning and knowledge anticipation
    """

    def __init__(self):
        self.interaction_memory = InteractionMemory()
        self.knowledge_gap_detector = KnowledgeGapDetector()
        self.anticipation_engine = AnticipationEngine()
        self.learning_patterns = UserLearningPatterns()
        self.active_sessions = {}
        self.learning_enabled = True

        # Start background tasks
        asyncio.create_task(self._background_prefetch_worker())
        asyncio.create_task(self._pattern_analysis_worker())

        logger.info("Chapter Behavioral Learning Engine initialized")

    async def learn_from_interaction(self, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for learning from user interactions
        """
        if not self.learning_enabled:
            return {"status": "learning_disabled"}

        try:
            # Create interaction object
            interaction = UserInteraction(
                interaction_id=hashlib.md5(
                    f"{interaction_data.get('user_id')}_{datetime.now()}".encode()
                ).hexdigest()[:8],
                user_id=interaction_data.get("user_id", "anonymous"),
                chapter_id=interaction_data.get("chapter_id", "unknown"),
                interaction_type=InteractionType(interaction_data.get("type", "read")),
                timestamp=datetime.now(),
                context_before=interaction_data.get("context_before", ""),
                context_after=interaction_data.get("context_after"),
                metadata=interaction_data.get("metadata", {}),
                session_id=interaction_data.get("session_id", "default"),
                duration_seconds=interaction_data.get("duration", 0),
                scroll_depth=interaction_data.get("scroll_depth", 0),
                focus_area=interaction_data.get("focus_area")
            )

            # Store interaction
            await self.interaction_memory.store_interaction(interaction)

            # Update user patterns
            await self.learning_patterns.update_user_pattern(
                interaction.user_id,
                {"interaction": interaction_data}
            )

            # Extract patterns
            patterns = await self.interaction_memory.get_interaction_patterns(
                interaction.chapter_id
            )

            # Return learning insights
            return {
                "status": "learned",
                "interaction_id": interaction.interaction_id,
                "patterns_detected": len(patterns),
                "confidence": max([p.confidence for p in patterns]) if patterns else 0
            }

        except Exception as e:
            logger.error(f"Error learning from interaction: {e}")
            return {"status": "error", "message": str(e)}

    async def anticipate_knowledge_needs(self, chapter_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Anticipate what knowledge the user will need next
        """
        try:
            chapter_id = chapter_context.get("chapter_id", "current")
            user_id = chapter_context.get("user_id", "anonymous")
            content = chapter_context.get("content", "")

            # Get user patterns
            patterns = await self.interaction_memory.get_interaction_patterns(chapter_id)

            # Detect knowledge gaps
            gaps = await self.knowledge_gap_detector.detect_gaps(content, chapter_context)

            # Anticipate needs
            anticipated_needs = await self.anticipation_engine.anticipate_needs(
                chapter_context, patterns, gaps
            )

            # Get user preferences for personalization
            user_prefs = await self.learning_patterns.get_user_preferences(user_id)

            # Prepare response
            return {
                "status": "success",
                "anticipated_needs": [
                    {
                        "need_id": need.need_id,
                        "type": need.need_type.value,
                        "content": need.anticipated_content,
                        "confidence": need.confidence,
                        "priority": need.priority,
                        "time_until_needed": str(need.estimated_time_until_needed),
                        "sources": need.prefetch_sources
                    }
                    for need in anticipated_needs[:10]  # Top 10 needs
                ],
                "knowledge_gaps": [
                    {
                        "gap_id": gap.gap_id,
                        "type": gap.gap_type.value,
                        "description": gap.description,
                        "confidence": gap.confidence,
                        "auto_fillable": gap.auto_fillable
                    }
                    for gap in gaps[:5]  # Top 5 gaps
                ],
                "user_preferences": user_prefs,
                "learning_confidence": sum([p.confidence for p in patterns]) / len(patterns) if patterns else 0
            }

        except Exception as e:
            logger.error(f"Error anticipating knowledge needs: {e}")
            return {"status": "error", "message": str(e)}

    async def get_proactive_suggestions(self, chapter_id: str, user_id: str) -> List[Dict[str, Any]]:
        """
        Get proactive suggestions based on learning
        """
        suggestions = []

        # Get patterns
        patterns = await self.interaction_memory.get_interaction_patterns(chapter_id)

        # Generate suggestions from patterns
        for pattern in patterns[:3]:  # Top 3 patterns
            if pattern.predicted_next_actions:
                action, probability = pattern.predicted_next_actions[0]
                suggestions.append({
                    "type": "predicted_action",
                    "action": action,
                    "probability": probability,
                    "reason": f"Based on pattern: {pattern.pattern_type}",
                    "confidence": pattern.confidence
                })

        # Get user preferences
        user_prefs = await self.learning_patterns.get_user_preferences(user_id)

        # Add preference-based suggestions
        if user_prefs["peak_times"]:
            current_hour = datetime.now().hour
            peak_hours = user_prefs["peak_times"]
            if any(abs(current_hour - peak) <= 1 for peak in peak_hours):
                suggestions.append({
                    "type": "optimal_timing",
                    "action": "focus_work",
                    "reason": "You're in your peak productivity window",
                    "confidence": 0.8
                })

        return suggestions

    async def _background_prefetch_worker(self):
        """Background worker for prefetching anticipated content"""
        while True:
            try:
                if not self.anticipation_engine.prefetch_queue.empty():
                    need = await self.anticipation_engine.prefetch_queue.get()
                    # Here you would implement actual prefetching logic
                    logger.info(f"Prefetching for anticipated need: {need.need_id}")
                    # Simulate prefetching
                    await asyncio.sleep(1)
                else:
                    await asyncio.sleep(10)  # Check every 10 seconds
            except Exception as e:
                logger.error(f"Error in prefetch worker: {e}")
                await asyncio.sleep(10)

    async def _pattern_analysis_worker(self):
        """Background worker for continuous pattern analysis"""
        while True:
            try:
                # Analyze patterns every 5 minutes
                await asyncio.sleep(300)

                # Get all active chapters
                for chapter_id in self.interaction_memory.interaction_index.keys():
                    patterns = await self.interaction_memory.get_interaction_patterns(chapter_id)
                    logger.info(f"Analyzed {len(patterns)} patterns for chapter {chapter_id}")

            except Exception as e:
                logger.error(f"Error in pattern analysis worker: {e}")
                await asyncio.sleep(60)

# Initialize global instance
chapter_behavioral_learning = ChapterBehavioralLearningEngine()