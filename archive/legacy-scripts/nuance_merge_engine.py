"""
Nuance Merge Engine - Intelligent Medical Content Merging
Detects subtle differences and merges internal + external knowledge with medical accuracy
Uses multi-algorithm similarity detection with ML fallback and Claude-powered merging
"""

import asyncio
import difflib
import hashlib
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

logger = logging.getLogger(__name__)

# Optional ML imports with graceful fallback
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.info("sentence-transformers not available, using fallback methods")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.info("sklearn not available, using basic similarity methods")


# ============================================================================
# ENUMS AND DATA CLASSES
# ============================================================================

class SimilarityAlgorithm(Enum):
    """Similarity detection algorithms"""
    SEMANTIC_TRANSFORMER = "semantic_transformer"
    JACCARD_COEFFICIENT = "jaccard_coefficient"
    LEVENSHTEIN_DISTANCE = "levenshtein_distance"
    COSINE_SIMILARITY = "cosine_similarity"
    HYBRID_ANALYSIS = "hybrid_analysis"


class NuanceType(Enum):
    """Types of nuanced changes"""
    ENHANCEMENT = "enhancement"
    REFINEMENT = "refinement"
    EXPANSION = "expansion"
    CLARIFICATION = "clarification"
    PRECISION_IMPROVEMENT = "precision_improvement"
    CLINICAL_SPECIFICITY = "clinical_specificity"
    MEDICAL_ACCURACY = "medical_accuracy"
    TERMINOLOGY_UPGRADE = "terminology_upgrade"


class MergeCategory(Enum):
    """Merge decision categories"""
    AUTO_APPLY = "auto_apply"          # >95% confidence
    RECOMMEND_APPLY = "recommend_apply"  # 85-95% confidence
    REQUIRE_REVIEW = "require_review"    # <85% confidence
    REJECT = "reject"                    # Conflicts or low quality


@dataclass
class SimilarityMetrics:
    """Comprehensive similarity metrics"""
    semantic_similarity: float = 0.0
    jaccard_similarity: float = 0.0
    levenshtein_distance: int = 0
    cosine_similarity: float = 0.0
    normalized_levenshtein: float = 0.0
    word_overlap_ratio: float = 0.0
    sentence_structure_similarity: float = 0.0


@dataclass
class MedicalContext:
    """Medical context extracted from content"""
    medical_concepts_added: List[str] = field(default_factory=list)
    anatomical_references: List[str] = field(default_factory=list)
    procedure_references: List[str] = field(default_factory=list)
    drug_references: List[str] = field(default_factory=list)
    specialty_context: Optional[str] = None
    clinical_relevance_score: float = 0.0


@dataclass
class SentenceAnalysis:
    """Sentence-level analysis"""
    original_sentence: str
    enhanced_sentence: str
    sentence_position: int
    added_parts: List[str] = field(default_factory=list)
    modified_parts: List[str] = field(default_factory=list)
    removed_parts: List[str] = field(default_factory=list)
    sentence_similarity: float = 0.0
    medical_concept_density: float = 0.0
    clinical_importance_score: float = 0.0
    change_type: Optional[str] = None
    impact_category: Optional[str] = None


@dataclass
class DetectedNuance:
    """Detected nuance with full analysis"""
    original_content: str
    updated_content: str
    similarity_metrics: SimilarityMetrics
    nuance_type: NuanceType
    medical_context: MedicalContext
    sentence_analyses: List[SentenceAnalysis]
    confidence_score: float
    merge_category: MergeCategory
    ai_recommendations: Dict[str, Any]
    processing_time_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class NuanceDetectionConfig:
    """Configuration for nuance detection"""
    specialty: str = "neurosurgery"
    exact_duplicate_threshold: float = 0.98
    nuance_threshold_high: float = 0.92
    nuance_threshold_medium: float = 0.78
    nuance_threshold_low: float = 0.60
    auto_apply_threshold: float = 0.95
    require_review_threshold: float = 0.85


# ============================================================================
# NUANCE MERGE ENGINE
# ============================================================================

class NuanceMergeEngine:
    """
    Intelligent medical content merging engine
    Detects subtle differences and merges with medical accuracy
    """

    def __init__(self, ai_manager=None):
        """
        Initialize merge engine

        Args:
            ai_manager: HybridAIManager for Claude-powered intelligent merging
        """
        self.ai_manager = ai_manager
        self.similarity_cache: Dict[str, Any] = {}
        self.processing_metrics: Dict[str, List] = defaultdict(list)

        # Initialize ML models if available
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.sentence_transformer_model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Loaded sentence transformer model")
            except Exception as e:
                logger.warning(f"Failed to load sentence transformer: {e}")
                self.sentence_transformer_model = None
        else:
            self.sentence_transformer_model = None

        # Specialty configurations
        self.specialty_configs = {
            'neurosurgery': NuanceDetectionConfig(
                specialty='neurosurgery',
                nuance_threshold_high=0.92,
                nuance_threshold_medium=0.78,
                require_review_threshold=0.85
            ),
            'general_medicine': NuanceDetectionConfig(
                specialty='general_medicine',
                nuance_threshold_high=0.85,
                nuance_threshold_medium=0.68,
                require_review_threshold=0.75
            )
        }

        # Medical term patterns
        self.medical_patterns = {
            'medical_concepts': [
                r'\b(?:glioblastoma|meningioma|astrocytoma|adenoma|carcinoma)\b',
                r'\b(?:hypertension|diabetes|epilepsy|seizure|stroke)\b',
                r'\b(?:MRI|CT|PET|ultrasound|angiography)\b'
            ],
            'anatomical': [
                r'\b(?:cerebral|cranial|spinal|vertebral|neural)\b',
                r'\b(?:frontal|parietal|temporal|occipital|cerebellum)\b',
                r'\b(?:cortex|hippocampus|thalamus|hypothalamus)\b'
            ],
            'procedures': [
                r'\b(?:craniotomy|craniectomy|laminectomy|resection)\b',
                r'\b(?:biopsy|excision|anastomosis|decompression)\b'
            ],
            'drugs': [
                r'\b(?:dexamethasone|mannitol|phenytoin|levetiracetam)\b',
                r'\b(?:chemotherapy|radiation|immunotherapy)\b'
            ]
        }

    # ========================================================================
    # MAIN MERGE INTERFACE
    # ========================================================================

    async def merge_chapters(
        self,
        internal_chapter: Dict[str, Any],
        external_enrichment: Dict[str, Any],
        specialty: str = "neurosurgery",
        auto_apply_threshold: float = 0.85
    ) -> Dict[str, Any]:
        """
        Main entry point: Merge internal chapter with external enrichment

        Args:
            internal_chapter: Initial chapter from internal PDF library
            external_enrichment: External AI search results
            specialty: Medical specialty for context
            auto_apply_threshold: Confidence threshold for auto-merge

        Returns:
            Merged comprehensive chapter
        """

        logger.info("Starting intelligent chapter merge...")
        start_time = datetime.now()

        # Get config for specialty
        config = self.specialty_configs.get(specialty, self.specialty_configs['neurosurgery'])
        config.auto_apply_threshold = auto_apply_threshold

        # Create merged chapter structure
        merged_chapter = internal_chapter.copy()
        merged_chapter['metadata'] = merged_chapter.get('metadata', {})
        merged_chapter['metadata']['merged'] = True
        merged_chapter['metadata']['merge_timestamp'] = datetime.now().isoformat()
        merged_chapter['metadata']['merge_stats'] = {
            'nuances_detected': 0,
            'nuances_applied': 0,
            'sections_enhanced': 0,
            'confidence_scores': []
        }

        # Extract external content
        external_content = external_enrichment.get('content', {}).get('External Knowledge (AI Enrichment)', '')

        if not external_content:
            logger.warning("No external content to merge")
            return merged_chapter

        # Parse external content by sections
        external_sections = self._parse_external_sections(external_content)

        # Merge each section intelligently
        for section_name, section_content in merged_chapter.get('content', {}).items():
            if section_name in external_sections:
                logger.info(f"Merging section: {section_name}")

                # Detect nuances
                nuance = await self.detect_nuance(
                    original=section_content,
                    updated=external_sections[section_name],
                    config=config
                )

                if nuance:
                    # Apply nuance based on confidence
                    if nuance.confidence_score >= config.auto_apply_threshold:
                        merged_content = await self._apply_nuance(
                            original=section_content,
                            nuance=nuance
                        )
                        merged_chapter['content'][section_name] = merged_content

                        # Update stats
                        merged_chapter['metadata']['merge_stats']['nuances_detected'] += 1
                        merged_chapter['metadata']['merge_stats']['nuances_applied'] += 1
                        merged_chapter['metadata']['merge_stats']['sections_enhanced'] += 1
                        merged_chapter['metadata']['merge_stats']['confidence_scores'].append(
                            nuance.confidence_score
                        )

                        logger.info(f"✅ Merged {section_name} (confidence: {nuance.confidence_score:.2%})")
                    else:
                        logger.info(f"⚠️ Low confidence for {section_name}, keeping original")
                        merged_chapter['metadata']['merge_stats']['nuances_detected'] += 1

        # Calculate average confidence
        scores = merged_chapter['metadata']['merge_stats']['confidence_scores']
        if scores:
            merged_chapter['metadata']['merge_stats']['avg_confidence'] = sum(scores) / len(scores)
        else:
            merged_chapter['metadata']['merge_stats']['avg_confidence'] = 0.0

        # Processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        merged_chapter['metadata']['merge_stats']['processing_time_seconds'] = processing_time

        logger.info(f"✅ Merge complete in {processing_time:.2f}s")
        logger.info(f"   - Sections enhanced: {merged_chapter['metadata']['merge_stats']['sections_enhanced']}")
        logger.info(f"   - Nuances applied: {merged_chapter['metadata']['merge_stats']['nuances_applied']}")
        logger.info(f"   - Avg confidence: {merged_chapter['metadata']['merge_stats']['avg_confidence']:.2%}")

        return merged_chapter

    # ========================================================================
    # NUANCE DETECTION
    # ========================================================================

    async def detect_nuance(
        self,
        original: str,
        updated: str,
        config: Optional[NuanceDetectionConfig] = None
    ) -> Optional[DetectedNuance]:
        """
        Detect nuanced differences between original and updated content

        Args:
            original: Original content
            updated: Updated/enriched content
            config: Detection configuration

        Returns:
            DetectedNuance if nuances found, None otherwise
        """

        start_time = datetime.now()

        if config is None:
            config = self.specialty_configs['neurosurgery']

        # Phase 1: Quick pre-screening
        if await self._is_exact_duplicate(original, updated, config):
            logger.debug("Exact duplicate detected, skipping")
            return None

        # Phase 2: Calculate comprehensive similarity metrics
        metrics = await self._calculate_all_similarity_metrics(original, updated)

        # Phase 3: Check if qualifies as nuance
        if not self._qualifies_as_nuance(metrics, config):
            logger.debug("Does not qualify as nuance")
            return None

        # Phase 4: Classify nuance type
        nuance_type = await self._classify_nuance_type(original, updated, metrics)

        # Phase 5: Extract medical context
        medical_context = await self._extract_medical_context(original, updated)

        # Phase 6: Sentence-level analysis
        sentence_analyses = await self._analyze_sentences(original, updated)

        # Phase 7: Calculate confidence score
        merge_category = self._determine_merge_category(metrics, config)
        confidence_score = await self._calculate_confidence_score(
            metrics, nuance_type, merge_category, medical_context
        )

        # Phase 8: Generate AI recommendations
        ai_recommendations = await self._generate_ai_recommendations(
            original, updated, confidence_score
        )

        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds() * 1000

        # Create detected nuance
        nuance = DetectedNuance(
            original_content=original,
            updated_content=updated,
            similarity_metrics=metrics,
            nuance_type=nuance_type,
            medical_context=medical_context,
            sentence_analyses=sentence_analyses,
            confidence_score=confidence_score,
            merge_category=merge_category,
            ai_recommendations=ai_recommendations,
            processing_time_ms=processing_time,
            timestamp=datetime.now()
        )

        return nuance

    async def _is_exact_duplicate(
        self,
        original: str,
        updated: str,
        config: NuanceDetectionConfig
    ) -> bool:
        """Check if content is an exact or near-exact duplicate"""
        # Normalize whitespace
        norm_original = ' '.join(original.split())
        norm_updated = ' '.join(updated.split())

        if norm_original == norm_updated:
            return True

        # Calculate quick similarity
        similarity = self._calculate_word_overlap_ratio(original, updated)
        return similarity > config.exact_duplicate_threshold

    # ========================================================================
    # SIMILARITY CALCULATIONS
    # ========================================================================

    async def _calculate_all_similarity_metrics(
        self,
        content1: str,
        content2: str
    ) -> SimilarityMetrics:
        """Calculate all similarity metrics in parallel"""

        # Check cache
        cache_key = self._generate_cache_key(content1, content2, "all_metrics")
        if cache_key in self.similarity_cache:
            return self.similarity_cache[cache_key]

        # Calculate all metrics
        semantic_sim = await self._calculate_semantic_similarity(content1, content2)
        jaccard_sim = self._calculate_jaccard_similarity(content1, content2)
        lev_dist = self._calculate_levenshtein_distance(content1, content2)
        cosine_sim = self._calculate_cosine_similarity(content1, content2)
        word_overlap = self._calculate_word_overlap_ratio(content1, content2)
        structure_sim = self._calculate_sentence_structure_similarity(content1, content2)

        # Normalized Levenshtein
        max_len = max(len(content1), len(content2))
        normalized_lev = 1.0 - (lev_dist / max_len) if max_len > 0 else 1.0

        metrics = SimilarityMetrics(
            semantic_similarity=semantic_sim,
            jaccard_similarity=jaccard_sim,
            levenshtein_distance=lev_dist,
            cosine_similarity=cosine_sim,
            normalized_levenshtein=normalized_lev,
            word_overlap_ratio=word_overlap,
            sentence_structure_similarity=structure_sim
        )

        # Cache result
        self.similarity_cache[cache_key] = metrics

        return metrics

    async def _calculate_semantic_similarity(self, content1: str, content2: str) -> float:
        """Calculate semantic similarity using available methods"""

        if SENTENCE_TRANSFORMERS_AVAILABLE and self.sentence_transformer_model:
            try:
                # Primary: Sentence transformers
                embeddings = self.sentence_transformer_model.encode([content1, content2])
                similarity = float(np.dot(embeddings[0], embeddings[1]) / (
                    np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
                ))
                return similarity
            except Exception as e:
                logger.warning(f"Sentence transformer failed: {e}")

        if SKLEARN_AVAILABLE:
            try:
                # Fallback 1: TF-IDF with cosine similarity
                vectorizer = TfidfVectorizer()
                tfidf_matrix = vectorizer.fit_transform([content1, content2])
                similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
                return float(similarity)
            except Exception as e:
                logger.warning(f"TF-IDF failed: {e}")

        # Fallback 2: Simple word overlap
        return self._calculate_word_overlap_ratio(content1, content2)

    def _calculate_jaccard_similarity(self, content1: str, content2: str) -> float:
        """Calculate Jaccard similarity coefficient"""
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())

        if not words1 and not words2:
            return 1.0

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union) if union else 0.0

    def _calculate_levenshtein_distance(self, content1: str, content2: str) -> int:
        """Calculate Levenshtein edit distance"""
        if len(content1) < len(content2):
            return self._calculate_levenshtein_distance(content2, content1)

        if len(content2) == 0:
            return len(content1)

        previous_row = range(len(content2) + 1)
        for i, c1 in enumerate(content1):
            current_row = [i + 1]
            for j, c2 in enumerate(content2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def _calculate_cosine_similarity(self, content1: str, content2: str) -> float:
        """Calculate cosine similarity (basic implementation)"""
        words1 = content1.lower().split()
        words2 = content2.lower().split()

        # Create word frequency vectors
        all_words = set(words1 + words2)
        vec1 = [words1.count(word) for word in all_words]
        vec2 = [words2.count(word) for word in all_words]

        # Calculate cosine similarity
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    def _calculate_word_overlap_ratio(self, content1: str, content2: str) -> float:
        """Calculate simple word overlap ratio"""
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())

        if not words1 and not words2:
            return 1.0

        intersection = words1 & words2
        total_unique = len(words1 | words2)

        return len(intersection) / total_unique if total_unique > 0 else 0.0

    def _calculate_sentence_structure_similarity(self, content1: str, content2: str) -> float:
        """Calculate sentence structure similarity"""
        sentences1 = [s.strip() for s in re.split(r'[.!?]+', content1) if s.strip()]
        sentences2 = [s.strip() for s in re.split(r'[.!?]+', content2) if s.strip()]

        if not sentences1 or not sentences2:
            return 0.0

        # Calculate average sentence length
        avg_len1 = sum(len(s.split()) for s in sentences1) / len(sentences1)
        avg_len2 = sum(len(s.split()) for s in sentences2) / len(sentences2)

        # Structure similarity based on sentence length patterns
        max_avg = max(avg_len1, avg_len2)
        if max_avg == 0:
            return 1.0

        length_similarity = 1.0 - abs(avg_len1 - avg_len2) / max_avg

        return float(length_similarity)

    def _qualifies_as_nuance(
        self,
        metrics: SimilarityMetrics,
        config: NuanceDetectionConfig
    ) -> bool:
        """Determine if changes qualify as a nuance"""
        # Must be similar enough to be a nuance but different enough to matter
        semantic_qualifies = (
            config.nuance_threshold_low <= metrics.semantic_similarity <= config.nuance_threshold_high
        )

        jaccard_qualifies = (
            config.nuance_threshold_low <= metrics.jaccard_similarity <= config.nuance_threshold_high
        )

        # At least one metric should qualify
        return semantic_qualifies or jaccard_qualifies

    # ========================================================================
    # MEDICAL CONTEXT ANALYSIS
    # ========================================================================

    async def _extract_medical_context(self, original: str, updated: str) -> MedicalContext:
        """Extract medical context from content"""

        # Identify new medical terms added
        medical_concepts = self._identify_medical_terms(updated, self.medical_patterns['medical_concepts'])
        anatomical_refs = self._identify_medical_terms(updated, self.medical_patterns['anatomical'])
        procedure_refs = self._identify_medical_terms(updated, self.medical_patterns['procedures'])
        drug_refs = self._identify_medical_terms(updated, self.medical_patterns['drugs'])

        # Calculate clinical relevance
        clinical_relevance = self._calculate_clinical_relevance(
            medical_concepts, anatomical_refs, procedure_refs
        )

        return MedicalContext(
            medical_concepts_added=medical_concepts,
            anatomical_references=anatomical_refs,
            procedure_references=procedure_refs,
            drug_references=drug_refs,
            specialty_context="neurosurgery",
            clinical_relevance_score=clinical_relevance
        )

    def _identify_medical_terms(self, text: str, patterns: List[str]) -> List[str]:
        """Identify medical terms using patterns"""
        terms = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            terms.extend(matches)
        return list(set(terms))  # Unique terms

    def _calculate_clinical_relevance(
        self,
        medical_concepts: List[str],
        anatomical_refs: List[str],
        procedure_refs: List[str]
    ) -> float:
        """Calculate clinical relevance score"""
        total_medical_terms = len(medical_concepts) + len(anatomical_refs) + len(procedure_refs)

        if total_medical_terms == 0:
            return 0.0
        elif total_medical_terms <= 2:
            return 0.4
        elif total_medical_terms <= 5:
            return 0.7
        else:
            return 0.9

    # ========================================================================
    # SENTENCE ANALYSIS
    # ========================================================================

    async def _analyze_sentences(self, original: str, updated: str) -> List[SentenceAnalysis]:
        """Perform sentence-level analysis"""

        original_sentences = [s.strip() for s in re.split(r'[.!?]+', original) if s.strip()]
        updated_sentences = [s.strip() for s in re.split(r'[.!?]+', updated) if s.strip()]

        analyses = []

        # Match sentences using sequence matcher
        matcher = difflib.SequenceMatcher(None, original_sentences, updated_sentences)

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                continue  # Skip unchanged sentences

            # Analyze modified/added sentences
            if tag in ['replace', 'insert']:
                for idx, updated_sent in enumerate(updated_sentences[j1:j2]):
                    original_sent = original_sentences[i1 + idx] if (i1 + idx) < len(original_sentences) else ""

                    analysis = await self._analyze_sentence_pair(
                        original_sent, updated_sent, j1 + idx
                    )
                    analyses.append(analysis)

        return analyses

    async def _analyze_sentence_pair(
        self,
        original_sent: str,
        updated_sent: str,
        position: int
    ) -> SentenceAnalysis:
        """Analyze a pair of sentences"""

        original_words = original_sent.split()
        updated_words = updated_sent.split()

        # Word-level changes
        matcher = difflib.SequenceMatcher(None, original_words, updated_words)
        added_parts = []
        modified_parts = []
        removed_parts = []

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'insert':
                added_parts.extend(updated_words[j1:j2])
            elif tag == 'delete':
                removed_parts.extend(original_words[i1:i2])
            elif tag == 'replace':
                modified_parts.extend(updated_words[j1:j2])

        # Calculate similarity
        similarity = self._calculate_word_overlap_ratio(original_sent, updated_sent)

        # Medical concept density
        medical_terms = self._identify_medical_terms(
            updated_sent,
            self.medical_patterns['medical_concepts']
        )
        concept_density = len(medical_terms) / len(updated_words) if updated_words else 0.0

        # Clinical importance
        clinical_importance = concept_density * 0.8

        # Determine change type
        if not original_sent:
            change_type = "addition"
        elif not updated_sent:
            change_type = "deletion"
        else:
            change_type = "modification"

        # Impact category
        if clinical_importance > 0.7:
            impact_category = "high"
        elif clinical_importance > 0.4:
            impact_category = "medium"
        else:
            impact_category = "low"

        return SentenceAnalysis(
            original_sentence=original_sent,
            enhanced_sentence=updated_sent,
            sentence_position=position,
            added_parts=added_parts,
            modified_parts=modified_parts,
            removed_parts=removed_parts,
            sentence_similarity=similarity,
            medical_concept_density=concept_density,
            clinical_importance_score=clinical_importance,
            change_type=change_type,
            impact_category=impact_category
        )

    # ========================================================================
    # CLASSIFICATION AND SCORING
    # ========================================================================

    async def _classify_nuance_type(
        self,
        original: str,
        updated: str,
        metrics: SimilarityMetrics
    ) -> NuanceType:
        """Classify the type of nuance"""

        # Simple heuristic classification
        len_ratio = len(updated) / len(original) if len(original) > 0 else 1.0

        if len_ratio > 1.5:
            return NuanceType.EXPANSION
        elif metrics.semantic_similarity > 0.85:
            return NuanceType.REFINEMENT
        elif metrics.semantic_similarity > 0.75:
            return NuanceType.ENHANCEMENT
        else:
            return NuanceType.CLARIFICATION

    def _determine_merge_category(
        self,
        metrics: SimilarityMetrics,
        config: NuanceDetectionConfig
    ) -> MergeCategory:
        """Determine merge category based on metrics"""

        avg_similarity = (
            metrics.semantic_similarity +
            metrics.jaccard_similarity +
            metrics.normalized_levenshtein
        ) / 3.0

        if avg_similarity >= config.auto_apply_threshold:
            return MergeCategory.AUTO_APPLY
        elif avg_similarity >= config.require_review_threshold:
            return MergeCategory.RECOMMEND_APPLY
        else:
            return MergeCategory.REQUIRE_REVIEW

    async def _calculate_confidence_score(
        self,
        metrics: SimilarityMetrics,
        nuance_type: NuanceType,
        merge_category: MergeCategory,
        medical_context: MedicalContext
    ) -> float:
        """Calculate confidence score for merge"""

        # Base confidence from similarity metrics
        base_confidence = (
            metrics.semantic_similarity * 0.4 +
            metrics.jaccard_similarity * 0.2 +
            metrics.normalized_levenshtein * 0.2 +
            metrics.cosine_similarity * 0.2
        )

        # Type multipliers
        type_multipliers = {
            NuanceType.MEDICAL_ACCURACY: 1.1,
            NuanceType.CLINICAL_SPECIFICITY: 1.05,
            NuanceType.ENHANCEMENT: 1.0,
            NuanceType.REFINEMENT: 0.95,
            NuanceType.CLARIFICATION: 0.9
        }

        confidence = base_confidence * type_multipliers.get(nuance_type, 1.0)

        # Boost for high clinical relevance
        confidence += medical_context.clinical_relevance_score * 0.1

        # Clamp to [0, 1]
        return max(0.0, min(1.0, confidence))

    async def _generate_ai_recommendations(
        self,
        original: str,
        updated: str,
        confidence: float
    ) -> Dict[str, Any]:
        """Generate AI recommendations"""

        return {
            "apply_automatically": confidence > 0.9,
            "require_review": confidence < 0.8,
            "suggested_action": "approve" if confidence > 0.85 else "review",
            "improvement_priority": "high" if confidence > 0.9 else "medium",
            "additional_validation_needed": confidence < 0.7
        }

    # ========================================================================
    # INTELLIGENT MERGING
    # ========================================================================

    async def _apply_nuance(self, original: str, nuance: DetectedNuance) -> str:
        """Apply detected nuance using Claude for intelligent merging"""

        if self.ai_manager:
            # Use Claude for intelligent merging
            prompt = f"""You are a neurosurgical knowledge expert. Merge these content versions intelligently:

Original Content:
{original}

Updated Content (with enhancements):
{nuance.updated_content}

Nuance Type: {nuance.nuance_type.value}
Confidence Score: {nuance.confidence_score:.2%}
Medical Concepts Added: {', '.join(nuance.medical_context.medical_concepts_added) if nuance.medical_context.medical_concepts_added else 'None'}

Instructions:
1. Preserve the original style and structure
2. Integrate new medical information seamlessly
3. Maintain clinical accuracy
4. Resolve any conflicts favoring higher quality evidence
5. Keep tone appropriate for medical professionals
6. Output ONLY the merged content, no additional commentary

Merged Content:"""

            try:
                merged_content = await self.ai_manager.query_with_adaptive_routing(
                    prompt=prompt,
                    task_type="medical_synthesis",
                    max_tokens=4000
                )
                return merged_content.strip()
            except Exception as e:
                logger.error(f"Claude merge failed, using fallback: {e}")

        # Fallback: Simple merge (prefer updated if confidence high)
        if nuance.confidence_score > 0.85:
            return nuance.updated_content
        else:
            return original

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def _generate_cache_key(self, content1: str, content2: str, algorithm: str) -> str:
        """Generate cache key for similarity calculations"""
        combined = f"{content1[:100]}::{content2[:100]}::{algorithm}"
        return hashlib.md5(combined.encode()).hexdigest()

    def _parse_external_sections(self, external_content: str) -> Dict[str, str]:
        """Parse external enrichment content into sections"""
        sections = {}

        # Split by ### headers
        parts = re.split(r'###\s+', external_content)

        for part in parts[1:]:  # Skip first empty part
            lines = part.strip().split('\n', 1)
            if len(lines) >= 2:
                section_name = lines[0].strip()
                section_content = lines[1].strip()
                sections[section_name] = section_content
            elif len(lines) == 1:
                section_name = lines[0].strip()
                sections[section_name] = ""

        return sections


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

async def merge_chapters_simple(
    internal_chapter: Dict[str, Any],
    external_enrichment: Dict[str, Any],
    ai_manager=None
) -> Dict[str, Any]:
    """
    Simple convenience function for chapter merging

    Args:
        internal_chapter: Internal chapter
        external_enrichment: External enrichment
        ai_manager: Optional AI manager for Claude-powered merging

    Returns:
        Merged chapter
    """
    engine = NuanceMergeEngine(ai_manager)
    return await engine.merge_chapters(internal_chapter, external_enrichment)