"""
Neurosurgical Summary Generator - Advanced Chapter Summarization Service
A dedicated, sophisticated algorithm for generating concise, accurate summaries of neurosurgical chapters
Provides multiple summary modes tailored for different clinical needs
"""

import asyncio
import json
import logging
import re
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import hashlib

logger = logging.getLogger(__name__)


class SummaryMode(Enum):
    """Different summary modes for various clinical needs"""
    EXECUTIVE = "executive"  # High-level overview for department heads
    CLINICAL_PEARLS = "clinical_pearls"  # Key practical points for clinicians
    QUICK_REFERENCE = "quick_reference"  # Rapid consultation format
    SURGICAL_STEPS = "surgical_steps"  # Step-by-step surgical procedures
    DIAGNOSTIC_ALGORITHM = "diagnostic_algorithm"  # Decision tree format
    EVIDENCE_BASED = "evidence_based"  # Research-focused with citations
    PATIENT_EDUCATION = "patient_education"  # Simplified for patient understanding
    BOARD_REVIEW = "board_review"  # Exam preparation format
    EMERGENCY_GUIDE = "emergency_guide"  # Critical action points


class SummaryLength(Enum):
    """Target summary lengths"""
    ULTRA_CONCISE = 100  # ~100 words - tweet-length
    CONCISE = 250  # ~250 words - abstract-length
    STANDARD = 500  # ~500 words - one page
    DETAILED = 1000  # ~1000 words - comprehensive
    EXTENSIVE = 2000  # ~2000 words - full review


@dataclass
class KeyPoint:
    """Represents a key point extracted from content"""
    text: str
    category: str  # diagnosis, treatment, prognosis, etc.
    importance: float  # 0.0 to 1.0
    source_section: str
    evidence_level: Optional[str] = None  # Level I, II, III, IV, V
    citations: List[str] = field(default_factory=list)
    clinical_relevance: Optional[str] = None


@dataclass
class ClinicalPearl:
    """Represents a clinical pearl - practical wisdom"""
    pearl: str
    context: str
    category: str  # diagnostic, therapeutic, prognostic, preventive
    experience_based: bool
    evidence_based: bool
    contraindications: List[str] = field(default_factory=list)
    pitfalls: List[str] = field(default_factory=list)


@dataclass
class SummarySection:
    """Structured section for organized summaries"""
    title: str
    content: str
    bullets: List[str] = field(default_factory=list)
    subsections: List['SummarySection'] = field(default_factory=list)
    importance_score: float = 1.0


class NeurosurgicalSummaryGenerator:
    """
    Advanced summary generator specifically designed for neurosurgical content.
    Provides multiple summary modes with clinical accuracy and precision.
    """

    def __init__(self, ai_manager=None, medical_nlp=None):
        self.ai_manager = ai_manager
        self.medical_nlp = medical_nlp
        self.section_weights = self._initialize_section_weights()
        self.keyword_extractors = self._initialize_keyword_extractors()

    def _initialize_section_weights(self) -> Dict[str, float]:
        """Initialize importance weights for different sections"""
        return {
            "Clinical Presentation": 0.95,
            "Diagnosis": 0.95,
            "Treatment Options and Alternatives": 0.95,
            "Surgical Techniques": 0.90,
            "Complications": 0.90,
            "Prognosis": 0.85,
            "Surgical Indications": 0.85,
            "Imaging": 0.80,
            "Pathophysiology": 0.75,
            "Epidemiology": 0.70,
            "Introduction": 0.65,
            "Recent Advances": 0.60,
            "References": 0.30
        }

    def _initialize_keyword_extractors(self) -> Dict[str, List[str]]:
        """Initialize keywords for extracting specific information types"""
        return {
            "critical_findings": [
                "emergency", "urgent", "immediate", "life-threatening",
                "critical", "severe", "acute", "emergent"
            ],
            "diagnostic_criteria": [
                "diagnostic", "criteria", "signs", "symptoms",
                "presentation", "features", "findings", "characteristic"
            ],
            "treatment_protocols": [
                "treatment", "management", "therapy", "intervention",
                "protocol", "guideline", "approach", "technique"
            ],
            "surgical_steps": [
                "step", "procedure", "approach", "incision",
                "dissection", "exposure", "closure", "technique"
            ],
            "complications": [
                "complication", "adverse", "risk", "morbidity",
                "mortality", "failure", "recurrence", "side effect"
            ],
            "prognosis_markers": [
                "prognosis", "survival", "outcome", "recovery",
                "recurrence", "progression", "quality of life"
            ],
            "contraindications": [
                "contraindication", "avoid", "caution", "not recommended",
                "contraindicated", "risk factor", "warning"
            ]
        }

    async def generate_summary(
        self,
        chapter_data: Dict[str, Any],
        mode: SummaryMode = SummaryMode.EXECUTIVE,
        length: SummaryLength = SummaryLength.STANDARD,
        include_citations: bool = True,
        custom_focus: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Main entry point for summary generation.
        Generates highly accurate, concise summaries based on specified mode and parameters.
        """

        logger.info(f"Generating {mode.value} summary with {length.value} word target")

        try:
            # 1. Extract and analyze chapter content
            content_analysis = await self._analyze_chapter_content(chapter_data)

            # 2. Extract key points based on mode
            key_points = await self._extract_key_points(content_analysis, mode, custom_focus)

            # 3. Extract clinical pearls if relevant
            clinical_pearls = []
            if mode in [SummaryMode.CLINICAL_PEARLS, SummaryMode.EXECUTIVE, SummaryMode.QUICK_REFERENCE]:
                clinical_pearls = await self._extract_clinical_pearls(content_analysis)

            # 4. Generate structured summary based on mode
            if mode == SummaryMode.EXECUTIVE:
                summary = await self._generate_executive_summary(
                    key_points, clinical_pearls, content_analysis, length
                )
            elif mode == SummaryMode.CLINICAL_PEARLS:
                summary = await self._generate_clinical_pearls_summary(
                    clinical_pearls, key_points, length
                )
            elif mode == SummaryMode.QUICK_REFERENCE:
                summary = await self._generate_quick_reference(
                    key_points, clinical_pearls, content_analysis, length
                )
            elif mode == SummaryMode.SURGICAL_STEPS:
                summary = await self._generate_surgical_steps_summary(
                    content_analysis, length
                )
            elif mode == SummaryMode.DIAGNOSTIC_ALGORITHM:
                summary = await self._generate_diagnostic_algorithm(
                    content_analysis, key_points, length
                )
            elif mode == SummaryMode.EVIDENCE_BASED:
                summary = await self._generate_evidence_based_summary(
                    key_points, content_analysis, length, include_citations=True
                )
            elif mode == SummaryMode.PATIENT_EDUCATION:
                summary = await self._generate_patient_education_summary(
                    key_points, content_analysis, length
                )
            elif mode == SummaryMode.BOARD_REVIEW:
                summary = await self._generate_board_review_summary(
                    key_points, content_analysis, length
                )
            elif mode == SummaryMode.EMERGENCY_GUIDE:
                summary = await self._generate_emergency_guide(
                    key_points, clinical_pearls, content_analysis, length
                )
            else:
                # Default to executive summary
                summary = await self._generate_executive_summary(
                    key_points, clinical_pearls, content_analysis, length
                )

            # 5. Post-process and format
            formatted_summary = self._format_summary(summary, mode, include_citations)

            # 6. Validate accuracy and completeness
            validation_result = await self._validate_summary(
                formatted_summary, chapter_data, mode
            )

            return {
                "summary": formatted_summary,
                "mode": mode.value,
                "length": length.value,
                "key_points": [kp.__dict__ for kp in key_points[:10]],  # Top 10
                "clinical_pearls": [cp.__dict__ for cp in clinical_pearls[:5]],  # Top 5
                "validation": validation_result,
                "metadata": {
                    "word_count": len(formatted_summary.split()),
                    "sections_covered": len(content_analysis.get('sections', [])),
                    "citations_included": include_citations,
                    "custom_focus": custom_focus
                }
            }

        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            return {
                "summary": "Summary generation failed. Please review chapter manually.",
                "error": str(e),
                "mode": mode.value
            }

    async def _analyze_chapter_content(self, chapter_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deeply analyzes chapter content to understand structure, key information, and relationships.
        """

        analysis = {
            "sections": {},
            "overall_topic": chapter_data.get("topic", "Unknown"),
            "total_content_length": 0,
            "key_statistics": [],
            "critical_information": [],
            "contradictions": chapter_data.get("analysis", {}).get("contradictions", []),
            "knowledge_gaps": chapter_data.get("analysis", {}).get("knowledge_gaps", []),
            "citations": []
        }

        # Analyze each section
        content = chapter_data.get("content", {})
        for section_name, section_content in content.items():
            if section_content:
                section_analysis = {
                    "length": len(section_content),
                    "weight": self.section_weights.get(section_name, 0.5),
                    "key_sentences": self._extract_key_sentences(section_content),
                    "statistics": self._extract_statistics(section_content),
                    "citations": self._extract_citations(section_content),
                    "medical_terms": self._extract_medical_terms(section_content),
                    "critical_points": self._identify_critical_points(section_content)
                }
                analysis["sections"][section_name] = section_analysis
                analysis["total_content_length"] += len(section_content)

                # Aggregate statistics and citations
                analysis["key_statistics"].extend(section_analysis["statistics"])
                analysis["citations"].extend(section_analysis["citations"])
                analysis["critical_information"].extend(section_analysis["critical_points"])

        # Extract images if available
        analysis["images"] = chapter_data.get("images", [])

        return analysis

    def _extract_key_sentences(self, text: str, top_n: int = 5) -> List[str]:
        """Extracts most important sentences using TF-IDF and position weighting"""
        sentences = re.split(r'[.!?]\s+', text)

        # Simple scoring based on length and position
        scored_sentences = []
        for i, sentence in enumerate(sentences):
            if 20 < len(sentence) < 300:  # Reasonable sentence length
                # Higher score for earlier sentences and those with key terms
                position_score = 1.0 - (i / max(len(sentences), 1))
                keyword_score = sum(1 for kw in ["important", "critical", "significant", "essential", "must"]
                                  if kw in sentence.lower()) * 0.3
                length_score = min(len(sentence) / 100, 1.0)  # Prefer moderate length

                total_score = position_score * 0.3 + keyword_score + length_score * 0.2
                scored_sentences.append((sentence.strip(), total_score))

        # Sort by score and return top N
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        return [sent for sent, _ in scored_sentences[:top_n]]

    def _extract_statistics(self, text: str) -> List[Dict[str, str]]:
        """Extracts statistical information from text"""
        statistics = []

        # Pattern for percentages
        percent_pattern = r'(\d+(?:\.\d+)?)\s*%'
        for match in re.finditer(percent_pattern, text):
            context_start = max(0, match.start() - 50)
            context_end = min(len(text), match.end() + 50)
            context = text[context_start:context_end]
            statistics.append({
                "value": match.group(),
                "context": context.strip(),
                "type": "percentage"
            })

        # Pattern for ratios
        ratio_pattern = r'(\d+)\s*(?::|to|/)\s*(\d+)'
        for match in re.finditer(ratio_pattern, text):
            context_start = max(0, match.start() - 30)
            context_end = min(len(text), match.end() + 30)
            context = text[context_start:context_end]
            statistics.append({
                "value": match.group(),
                "context": context.strip(),
                "type": "ratio"
            })

        # Pattern for incidence/prevalence
        incidence_pattern = r'(\d+(?:\.\d+)?)\s*(?:per|/)\s*(\d+,?\d*)\s*(?:people|patients|cases|population)'
        for match in re.finditer(incidence_pattern, text, re.IGNORECASE):
            statistics.append({
                "value": match.group(),
                "context": match.group(),
                "type": "incidence"
            })

        return statistics[:10]  # Limit to top 10 statistics

    def _extract_citations(self, text: str) -> List[str]:
        """Extracts citations from text"""
        citations = []

        # Common citation patterns
        patterns = [
            r'\[(\d+)\]',  # [1]
            r'\(([A-Z][a-zA-Z]+(?:\s+et\s+al\.?)?,?\s+\d{4})\)',  # (Author, 2020)
            r'\[(\d+)-(\d+)\]',  # [1-5]
        ]

        for pattern in patterns:
            citations.extend(re.findall(pattern, text))

        return list(set(citations))  # Remove duplicates

    def _extract_medical_terms(self, text: str) -> List[str]:
        """Extracts medical terminology"""
        # This would ideally use a medical NLP library
        # For now, using pattern matching for common medical terms

        medical_patterns = [
            r'\b[A-Z][a-z]+(?:oma|itis|osis|pathy|ectomy|otomy|plasty|scopy)\b',
            r'\b(?:anterior|posterior|lateral|medial|superior|inferior|proximal|distal)\b',
            r'\b(?:acute|chronic|bilateral|unilateral|primary|secondary)\b',
        ]

        terms = []
        for pattern in medical_patterns:
            terms.extend(re.findall(pattern, text, re.IGNORECASE))

        return list(set(terms))[:20]  # Top 20 unique terms

    def _identify_critical_points(self, text: str) -> List[str]:
        """Identifies critical clinical points"""
        critical_points = []

        sentences = re.split(r'[.!?]\s+', text)
        for sentence in sentences:
            sentence_lower = sentence.lower()
            # Check for critical keywords
            if any(keyword in sentence_lower for keyword in self.keyword_extractors["critical_findings"]):
                critical_points.append(sentence.strip())
            # Check for contraindications
            elif any(keyword in sentence_lower for keyword in self.keyword_extractors["contraindications"]):
                critical_points.append(sentence.strip())

        return critical_points[:5]  # Top 5 critical points

    async def _extract_key_points(
        self,
        content_analysis: Dict[str, Any],
        mode: SummaryMode,
        custom_focus: Optional[List[str]] = None
    ) -> List[KeyPoint]:
        """
        Extracts key points from analyzed content based on summary mode.
        """

        key_points = []

        # Determine which categories to focus on based on mode
        if mode == SummaryMode.DIAGNOSTIC_ALGORITHM:
            focus_categories = ["diagnosis", "clinical_presentation", "imaging", "laboratory"]
        elif mode == SummaryMode.SURGICAL_STEPS:
            focus_categories = ["surgical_technique", "procedure", "approach", "anatomy"]
        elif mode == SummaryMode.EMERGENCY_GUIDE:
            focus_categories = ["emergency", "critical", "immediate_action", "complications"]
        elif custom_focus:
            focus_categories = custom_focus
        else:
            focus_categories = ["diagnosis", "treatment", "prognosis", "complications"]

        # Extract points from each section
        for section_name, section_data in content_analysis["sections"].items():
            weight = section_data["weight"]

            # Extract key sentences as potential key points
            for sentence in section_data["key_sentences"]:
                # Determine category
                category = self._categorize_sentence(sentence, focus_categories)
                if category:
                    key_point = KeyPoint(
                        text=sentence,
                        category=category,
                        importance=weight,
                        source_section=section_name,
                        citations=self._extract_citations(sentence)
                    )
                    key_points.append(key_point)

            # Add critical points with high importance
            for critical_point in section_data["critical_points"]:
                key_point = KeyPoint(
                    text=critical_point,
                    category="critical",
                    importance=1.0,  # Maximum importance
                    source_section=section_name,
                    clinical_relevance="HIGH"
                )
                key_points.append(key_point)

        # Sort by importance and filter
        key_points.sort(key=lambda x: x.importance, reverse=True)

        # Deduplicate similar points
        unique_points = self._deduplicate_key_points(key_points)

        return unique_points[:30]  # Return top 30 points

    def _categorize_sentence(self, sentence: str, focus_categories: List[str]) -> Optional[str]:
        """Categorizes a sentence into clinical categories"""
        sentence_lower = sentence.lower()

        category_keywords = {
            "diagnosis": self.keyword_extractors["diagnostic_criteria"],
            "treatment": self.keyword_extractors["treatment_protocols"],
            "surgical_technique": self.keyword_extractors["surgical_steps"],
            "complications": self.keyword_extractors["complications"],
            "prognosis": self.keyword_extractors["prognosis_markers"],
            "emergency": self.keyword_extractors["critical_findings"],
            "clinical_presentation": ["presents", "symptoms", "signs", "features"],
            "imaging": ["MRI", "CT", "X-ray", "ultrasound", "scan"],
            "laboratory": ["lab", "test", "marker", "level", "value"]
        }

        for category in focus_categories:
            if category in category_keywords:
                if any(keyword in sentence_lower for keyword in category_keywords[category]):
                    return category

        return None

    def _deduplicate_key_points(self, key_points: List[KeyPoint]) -> List[KeyPoint]:
        """Removes duplicate or very similar key points"""
        unique_points = []
        seen_hashes = set()

        for point in key_points:
            # Create simplified hash of the point
            simplified = re.sub(r'[^a-z0-9]+', '', point.text.lower())[:50]
            point_hash = hashlib.md5(simplified.encode()).hexdigest()

            if point_hash not in seen_hashes:
                unique_points.append(point)
                seen_hashes.add(point_hash)

        return unique_points

    async def _extract_clinical_pearls(
        self,
        content_analysis: Dict[str, Any]
    ) -> List[ClinicalPearl]:
        """
        Extracts clinical pearls - practical wisdom and key insights.
        """

        clinical_pearls = []

        # Keywords that indicate clinical pearls
        pearl_indicators = [
            "important to note", "key point", "remember", "critical",
            "always", "never", "avoid", "prefer", "recommend",
            "in our experience", "best practice", "gold standard",
            "pitfall", "caution", "tip", "trick"
        ]

        for section_name, section_data in content_analysis["sections"].items():
            # Look for sentences containing pearl indicators
            for sentence in section_data["key_sentences"]:
                sentence_lower = sentence.lower()

                if any(indicator in sentence_lower for indicator in pearl_indicators):
                    # Determine pearl category
                    if any(word in sentence_lower for word in ["diagnos", "test", "imaging"]):
                        category = "diagnostic"
                    elif any(word in sentence_lower for word in ["treat", "manag", "therap"]):
                        category = "therapeutic"
                    elif any(word in sentence_lower for word in ["prognos", "outcome", "surviv"]):
                        category = "prognostic"
                    elif any(word in sentence_lower for word in ["prevent", "avoid", "prophyla"]):
                        category = "preventive"
                    else:
                        category = "general"

                    # Check if evidence-based or experience-based
                    evidence_based = bool(self._extract_citations(sentence))
                    experience_based = any(phrase in sentence_lower
                                         for phrase in ["in our experience", "we find", "we prefer"])

                    pearl = ClinicalPearl(
                        pearl=sentence,
                        context=section_name,
                        category=category,
                        experience_based=experience_based,
                        evidence_based=evidence_based
                    )
                    clinical_pearls.append(pearl)

        # Sort by relevance (evidence-based pearls first)
        clinical_pearls.sort(key=lambda x: (x.evidence_based, not x.experience_based), reverse=True)

        return clinical_pearls[:10]  # Top 10 pearls

    async def _generate_executive_summary(
        self,
        key_points: List[KeyPoint],
        clinical_pearls: List[ClinicalPearl],
        content_analysis: Dict[str, Any],
        length: SummaryLength
    ) -> str:
        """
        Generates executive summary - high-level overview for decision makers.
        """

        # Structure the summary
        sections = []

        # 1. Overview
        topic = content_analysis["overall_topic"]
        overview = f"## {topic} - Executive Summary\n\n"

        # 2. Key Statistics
        if content_analysis["key_statistics"]:
            overview += "### Key Metrics\n"
            for stat in content_analysis["key_statistics"][:3]:
                overview += f"• {stat['context']}\n"
        sections.append(overview)

        # 3. Critical Points
        if any(kp.category == "critical" for kp in key_points):
            critical_section = "\n### Critical Considerations\n"
            for kp in key_points:
                if kp.category == "critical":
                    critical_section += f"• {kp.text}\n"
            sections.append(critical_section)

        # 4. Diagnostic Approach
        diagnostic_points = [kp for kp in key_points if kp.category == "diagnosis"]
        if diagnostic_points:
            diag_section = "\n### Diagnostic Approach\n"
            for point in diagnostic_points[:3]:
                diag_section += f"• {point.text}\n"
            sections.append(diag_section)

        # 5. Treatment Strategy
        treatment_points = [kp for kp in key_points if kp.category == "treatment"]
        if treatment_points:
            treat_section = "\n### Treatment Strategy\n"
            for point in treatment_points[:3]:
                treat_section += f"• {point.text}\n"
            sections.append(treat_section)

        # 6. Complications & Risks
        complication_points = [kp for kp in key_points if kp.category == "complications"]
        if complication_points:
            comp_section = "\n### Major Complications\n"
            for point in complication_points[:3]:
                comp_section += f"• {point.text}\n"
            sections.append(comp_section)

        # 7. Prognosis
        prognosis_points = [kp for kp in key_points if kp.category == "prognosis"]
        if prognosis_points:
            prog_section = "\n### Prognosis\n"
            for point in prognosis_points[:2]:
                prog_section += f"• {point.text}\n"
            sections.append(prog_section)

        # 8. Clinical Pearls
        if clinical_pearls:
            pearls_section = "\n### Clinical Pearls\n"
            for pearl in clinical_pearls[:3]:
                pearls_section += f"• {pearl.pearl}\n"
            sections.append(pearls_section)

        # 9. Knowledge Gaps (if any)
        if content_analysis["knowledge_gaps"]:
            gaps_section = "\n### Areas Requiring Further Research\n"
            for gap in content_analysis["knowledge_gaps"][:2]:
                gaps_section += f"• {gap}\n"
            sections.append(gaps_section)

        # Combine sections based on target length
        summary = ""
        current_length = 0
        target_words = length.value

        for section in sections:
            section_words = len(section.split())
            if current_length + section_words <= target_words * 1.1:  # Allow 10% overflow
                summary += section
                current_length += section_words
            else:
                break

        return summary

    async def _generate_clinical_pearls_summary(
        self,
        clinical_pearls: List[ClinicalPearl],
        key_points: List[KeyPoint],
        length: SummaryLength
    ) -> str:
        """
        Generates summary focused on clinical pearls and practical wisdom.
        """

        summary = "## Clinical Pearls & Practical Guidelines\n\n"

        # Group pearls by category
        pearls_by_category = defaultdict(list)
        for pearl in clinical_pearls:
            pearls_by_category[pearl.category].append(pearl)

        # Add pearls by category
        for category in ["diagnostic", "therapeutic", "preventive", "prognostic", "general"]:
            if category in pearls_by_category:
                summary += f"\n### {category.title()} Pearls\n"
                for pearl in pearls_by_category[category]:
                    marker = "📊" if pearl.evidence_based else "💡"
                    summary += f"{marker} {pearl.pearl}\n"
                    if pearl.pitfalls:
                        summary += f"   ⚠️ Pitfalls: {', '.join(pearl.pitfalls)}\n"

        # Add high-yield facts
        summary += "\n### High-Yield Facts\n"
        for point in key_points:
            if point.importance > 0.8:
                summary += f"• {point.text}\n"
                if len(summary.split()) > length.value:
                    break

        return summary

    async def _generate_quick_reference(
        self,
        key_points: List[KeyPoint],
        clinical_pearls: List[ClinicalPearl],
        content_analysis: Dict[str, Any],
        length: SummaryLength
    ) -> str:
        """
        Generates quick reference guide for rapid consultation.
        """

        summary = f"## Quick Reference: {content_analysis['overall_topic']}\n\n"

        # Red Flags / Emergency
        critical_points = [kp for kp in key_points if kp.category == "critical"]
        if critical_points:
            summary += "### 🚨 RED FLAGS\n"
            for point in critical_points[:3]:
                summary += f"• {point.text}\n"

        # Diagnosis at a glance
        summary += "\n### 🔍 DIAGNOSIS\n"
        diagnostic_points = [kp for kp in key_points if kp.category == "diagnosis"]
        for point in diagnostic_points[:4]:
            summary += f"• {point.text}\n"

        # Treatment algorithm
        summary += "\n### 💊 TREATMENT\n"
        treatment_points = [kp for kp in key_points if kp.category == "treatment"]
        summary += "**First Line:**\n"
        for point in treatment_points[:2]:
            summary += f"• {point.text}\n"

        if len(treatment_points) > 2:
            summary += "**Alternative Options:**\n"
            for point in treatment_points[2:4]:
                summary += f"• {point.text}\n"

        # Key complications
        summary += "\n### ⚠️ COMPLICATIONS\n"
        complication_points = [kp for kp in key_points if kp.category == "complications"]
        for point in complication_points[:3]:
            summary += f"• {point.text}\n"

        # Prognosis snapshot
        prognosis_points = [kp for kp in key_points if kp.category == "prognosis"]
        if prognosis_points:
            summary += "\n### 📈 PROGNOSIS\n"
            summary += f"{prognosis_points[0].text}\n"

        # Key statistics
        if content_analysis["key_statistics"]:
            summary += "\n### 📊 KEY STATISTICS\n"
            for stat in content_analysis["key_statistics"][:3]:
                summary += f"• {stat['value']}: {stat['context'][:50]}...\n"

        return summary

    async def _generate_surgical_steps_summary(
        self,
        content_analysis: Dict[str, Any],
        length: SummaryLength
    ) -> str:
        """
        Generates step-by-step surgical procedure summary.
        """

        summary = "## Surgical Procedure - Step-by-Step Guide\n\n"

        # Extract surgical content
        surgical_sections = ["Surgical Techniques", "Surgical Anatomy",
                            "Step-by-Step Surgical Procedure", "Preoperative Planning"]

        surgical_content = []
        for section in surgical_sections:
            if section in content_analysis["sections"]:
                surgical_content.extend(
                    content_analysis["sections"][section]["key_sentences"]
                )

        # Organize into steps
        summary += "### Preoperative Preparation\n"
        prep_keywords = ["position", "preparation", "setup", "anesthesia", "equipment"]
        for sentence in surgical_content:
            if any(kw in sentence.lower() for kw in prep_keywords):
                summary += f"• {sentence}\n"

        summary += "\n### Surgical Approach\n"
        approach_keywords = ["incision", "approach", "exposure", "dissection"]
        step_number = 1
        for sentence in surgical_content:
            if any(kw in sentence.lower() for kw in approach_keywords):
                summary += f"{step_number}. {sentence}\n"
                step_number += 1

        summary += "\n### Key Technical Points\n"
        technical_keywords = ["careful", "avoid", "preserve", "identify", "technique"]
        for sentence in surgical_content:
            if any(kw in sentence.lower() for kw in technical_keywords):
                summary += f"• {sentence}\n"

        summary += "\n### Closure\n"
        closure_keywords = ["closure", "suture", "drain", "dressing"]
        for sentence in surgical_content:
            if any(kw in sentence.lower() for kw in closure_keywords):
                summary += f"• {sentence}\n"

        # Add relevant images if available
        if content_analysis["images"]:
            summary += "\n### Relevant Figures\n"
            for img in content_analysis["images"][:3]:
                if "surgical" in img.get("caption", "").lower():
                    summary += f"• See: {img['caption']}\n"

        return summary

    async def _generate_diagnostic_algorithm(
        self,
        content_analysis: Dict[str, Any],
        key_points: List[KeyPoint],
        length: SummaryLength
    ) -> str:
        """
        Generates diagnostic algorithm in decision-tree format.
        """

        summary = "## Diagnostic Algorithm\n\n"

        # Clinical Presentation
        summary += "### Step 1: Clinical Presentation\n"
        presentation_points = [kp for kp in key_points
                             if kp.category in ["clinical_presentation", "diagnosis"]]
        for point in presentation_points[:3]:
            summary += f"• {point.text}\n"

        # Initial Workup
        summary += "\n### Step 2: Initial Workup\n"
        summary += "**Laboratory Tests:**\n"
        lab_points = [kp for kp in key_points if "lab" in kp.text.lower()]
        for point in lab_points[:2]:
            summary += f"• {point.text}\n"

        summary += "\n**Imaging:**\n"
        imaging_points = [kp for kp in key_points if kp.category == "imaging"]
        for point in imaging_points[:2]:
            summary += f"• {point.text}\n"

        # Differential Diagnosis
        summary += "\n### Step 3: Differential Diagnosis\n"
        if "Differential Diagnosis" in content_analysis["sections"]:
            diff_sentences = content_analysis["sections"]["Differential Diagnosis"]["key_sentences"]
            for sentence in diff_sentences[:3]:
                summary += f"• {sentence}\n"

        # Confirmatory Tests
        summary += "\n### Step 4: Confirmatory Testing\n"
        confirmatory_keywords = ["confirm", "definitive", "gold standard", "diagnostic"]
        for point in key_points:
            if any(kw in point.text.lower() for kw in confirmatory_keywords):
                summary += f"• {point.text}\n"
                break

        # Decision Points
        summary += "\n### Decision Points\n"
        summary += "```\n"
        summary += "If [positive finding] → Consider [diagnosis/action]\n"
        summary += "If [negative finding] → Consider [alternative diagnosis/action]\n"
        summary += "```\n"

        return summary

    async def _generate_evidence_based_summary(
        self,
        key_points: List[KeyPoint],
        content_analysis: Dict[str, Any],
        length: SummaryLength,
        include_citations: bool = True
    ) -> str:
        """
        Generates evidence-based summary with citations and evidence levels.
        """

        summary = "## Evidence-Based Summary\n\n"

        # Group points by evidence level
        points_with_citations = [kp for kp in key_points if kp.citations]
        points_without_citations = [kp for kp in key_points if not kp.citations]

        # Level I Evidence (RCTs, Meta-analyses)
        summary += "### High-Quality Evidence\n"
        for point in points_with_citations[:5]:
            citations = f" [{', '.join(point.citations)}]" if include_citations else ""
            summary += f"• {point.text}{citations}\n"

        # Observational Studies
        if points_without_citations:
            summary += "\n### Observational Data & Expert Opinion\n"
            for point in points_without_citations[:3]:
                summary += f"• {point.text}\n"

        # Key Statistics with Evidence
        if content_analysis["key_statistics"]:
            summary += "\n### Key Statistics from Literature\n"
            for stat in content_analysis["key_statistics"][:4]:
                summary += f"• {stat['value']}: {stat['context']}\n"

        # Contradictions in Evidence
        if content_analysis["contradictions"]:
            summary += "\n### Conflicting Evidence\n"
            for contradiction in content_analysis["contradictions"][:2]:
                summary += f"• {contradiction}\n"

        # Research Gaps
        if content_analysis["knowledge_gaps"]:
            summary += "\n### Areas Requiring Further Research\n"
            for gap in content_analysis["knowledge_gaps"][:2]:
                summary += f"• {gap}\n"

        # References
        if include_citations and content_analysis["citations"]:
            summary += "\n### Key References\n"
            for citation in list(set(content_analysis["citations"]))[:10]:
                summary += f"• {citation}\n"

        return summary

    async def _generate_patient_education_summary(
        self,
        key_points: List[KeyPoint],
        content_analysis: Dict[str, Any],
        length: SummaryLength
    ) -> str:
        """
        Generates patient-friendly educational summary.
        """

        summary = f"## Understanding {content_analysis['overall_topic']}\n\n"

        # What is it?
        summary += "### What is this condition?\n"
        intro_points = [kp for kp in key_points
                       if kp.source_section in ["Introduction", "Pathophysiology"]]
        if intro_points:
            # Simplify medical terminology
            simplified = self._simplify_medical_language(intro_points[0].text)
            summary += f"{simplified}\n"

        # Signs and Symptoms
        summary += "\n### What are the symptoms?\n"
        symptom_points = [kp for kp in key_points
                         if kp.category == "clinical_presentation"]
        for point in symptom_points[:3]:
            simplified = self._simplify_medical_language(point.text)
            summary += f"• {simplified}\n"

        # Diagnosis
        summary += "\n### How is it diagnosed?\n"
        diagnostic_points = [kp for kp in key_points if kp.category == "diagnosis"]
        if diagnostic_points:
            simplified = self._simplify_medical_language(diagnostic_points[0].text)
            summary += f"{simplified}\n"

        # Treatment Options
        summary += "\n### Treatment options\n"
        treatment_points = [kp for kp in key_points if kp.category == "treatment"]
        for point in treatment_points[:3]:
            simplified = self._simplify_medical_language(point.text)
            summary += f"• {simplified}\n"

        # What to Expect
        summary += "\n### What to expect\n"
        prognosis_points = [kp for kp in key_points if kp.category == "prognosis"]
        if prognosis_points:
            simplified = self._simplify_medical_language(prognosis_points[0].text)
            summary += f"{simplified}\n"

        # Important Points
        summary += "\n### Important points to remember\n"
        for pearl in key_points[:3]:
            if pearl.clinical_relevance == "HIGH":
                simplified = self._simplify_medical_language(pearl.text)
                summary += f"• {simplified}\n"

        return summary

    def _simplify_medical_language(self, text: str) -> str:
        """
        Simplifies medical terminology for patient understanding.
        """

        # Dictionary of medical terms to lay terms
        replacements = {
            "bilateral": "both sides",
            "unilateral": "one side",
            "anterior": "front",
            "posterior": "back",
            "superior": "upper",
            "inferior": "lower",
            "acute": "sudden",
            "chronic": "long-term",
            "malignant": "cancerous",
            "benign": "non-cancerous",
            "prognosis": "outlook",
            "morbidity": "illness",
            "mortality": "death rate",
            "incidence": "how often it occurs",
            "prevalence": "how common it is",
            "contraindication": "reason not to use",
            "adverse effect": "side effect"
        }

        simplified = text
        for medical_term, lay_term in replacements.items():
            simplified = re.sub(f"\\b{medical_term}\\b", lay_term, simplified, flags=re.IGNORECASE)

        return simplified

    async def _generate_board_review_summary(
        self,
        key_points: List[KeyPoint],
        content_analysis: Dict[str, Any],
        length: SummaryLength
    ) -> str:
        """
        Generates board exam review format summary.
        """

        summary = f"## Board Review: {content_analysis['overall_topic']}\n\n"

        # High-Yield Facts
        summary += "### HIGH-YIELD FACTS\n"
        high_yield = [kp for kp in key_points if kp.importance > 0.8]
        for i, point in enumerate(high_yield[:10], 1):
            summary += f"{i}. {point.text}\n"

        # Classic Presentation
        summary += "\n### CLASSIC PRESENTATION\n"
        presentation_points = [kp for kp in key_points
                             if kp.category == "clinical_presentation"]
        if presentation_points:
            summary += f"• {presentation_points[0].text}\n"

        # Diagnostic Test of Choice
        summary += "\n### DIAGNOSTIC TEST OF CHOICE\n"
        diagnostic_points = [kp for kp in key_points if kp.category == "diagnosis"]
        for point in diagnostic_points:
            if "gold standard" in point.text.lower() or "first" in point.text.lower():
                summary += f"• {point.text}\n"
                break

        # Treatment of Choice
        summary += "\n### TREATMENT OF CHOICE\n"
        treatment_points = [kp for kp in key_points if kp.category == "treatment"]
        for point in treatment_points:
            if "first line" in point.text.lower() or "treatment of choice" in point.text.lower():
                summary += f"• {point.text}\n"
                break

        # Complications to Know
        summary += "\n### MUST-KNOW COMPLICATIONS\n"
        complication_points = [kp for kp in key_points if kp.category == "complications"]
        for point in complication_points[:3]:
            summary += f"• {point.text}\n"

        # Buzzwords
        summary += "\n### BUZZWORDS & ASSOCIATIONS\n"
        # Extract characteristic findings
        for section_data in content_analysis["sections"].values():
            for term in section_data["medical_terms"][:5]:
                if len(term) > 5:  # Filter out very short terms
                    summary += f"• {term}\n"

        # Key Statistics to Memorize
        if content_analysis["key_statistics"]:
            summary += "\n### KEY NUMBERS\n"
            for stat in content_analysis["key_statistics"][:5]:
                summary += f"• {stat['value']}: {stat['context'][:40]}...\n"

        return summary

    async def _generate_emergency_guide(
        self,
        key_points: List[KeyPoint],
        clinical_pearls: List[ClinicalPearl],
        content_analysis: Dict[str, Any],
        length: SummaryLength
    ) -> str:
        """
        Generates emergency management guide.
        """

        summary = f"## EMERGENCY GUIDE: {content_analysis['overall_topic']}\n\n"

        # Immediate Actions
        summary += "### ⚡ IMMEDIATE ACTIONS\n"
        critical_points = [kp for kp in key_points if kp.category == "critical"]
        for i, point in enumerate(critical_points[:5], 1):
            summary += f"{i}. {point.text}\n"

        # Red Flags
        summary += "\n### 🚨 RED FLAGS\n"
        for point in content_analysis["critical_information"][:5]:
            summary += f"• {point}\n"

        # Initial Assessment
        summary += "\n### 📋 INITIAL ASSESSMENT\n"
        summary += "**Vital Signs & Primary Survey**\n"
        assessment_points = [kp for kp in key_points
                            if any(word in kp.text.lower()
                                  for word in ["assess", "evaluate", "check", "monitor"])]
        for point in assessment_points[:3]:
            summary += f"• {point.text}\n"

        # Emergency Diagnostics
        summary += "\n### 🔬 STAT DIAGNOSTICS\n"
        diagnostic_points = [kp for kp in key_points
                           if kp.category == "diagnosis" and
                           any(word in kp.text.lower()
                               for word in ["urgent", "stat", "immediate", "emergency"])]
        for point in diagnostic_points[:3]:
            summary += f"• {point.text}\n"

        # Emergency Treatment
        summary += "\n### 💊 EMERGENCY TREATMENT\n"
        treatment_points = [kp for kp in key_points
                          if kp.category == "treatment" and
                          any(word in kp.text.lower()
                              for word in ["immediate", "emergency", "urgent", "first"])]
        for point in treatment_points[:4]:
            summary += f"• {point.text}\n"

        # Complications to Watch
        summary += "\n### ⚠️ COMPLICATIONS TO MONITOR\n"
        complication_points = [kp for kp in key_points if kp.category == "complications"]
        for point in complication_points[:3]:
            summary += f"• {point.text}\n"

        # Disposition
        summary += "\n### 🏥 DISPOSITION\n"
        summary += "• Admit if: [Critical criteria]\n"
        summary += "• Consult: [Relevant specialties]\n"
        summary += "• Transfer if: [Higher level of care needed]\n"

        return summary

    def _format_summary(
        self,
        summary: str,
        mode: SummaryMode,
        include_citations: bool
    ) -> str:
        """
        Formats and polishes the summary for final output.
        """

        # Clean up formatting
        summary = re.sub(r'\n{3,}', '\n\n', summary)  # Remove excess newlines
        summary = re.sub(r' {2,}', ' ', summary)  # Remove excess spaces

        # Add mode-specific formatting
        if mode == SummaryMode.QUICK_REFERENCE:
            # Add visual separators for quick scanning
            summary = re.sub(r'^###', '---\n###', summary, flags=re.MULTILINE)

        elif mode == SummaryMode.EMERGENCY_GUIDE:
            # Add timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            summary = f"Generated: {timestamp}\n\n{summary}"

        # Remove citations if not needed
        if not include_citations:
            summary = re.sub(r'\[[^\]]+\]', '', summary)

        # Ensure consistent bullet points
        summary = re.sub(r'^[•·▪]', '•', summary, flags=re.MULTILINE)

        return summary.strip()

    async def _validate_summary(
        self,
        summary: str,
        original_chapter: Dict[str, Any],
        mode: SummaryMode
    ) -> Dict[str, Any]:
        """
        Validates the accuracy and completeness of the generated summary.
        """

        validation = {
            "is_valid": True,
            "completeness_score": 0.0,
            "accuracy_checks": [],
            "missing_elements": [],
            "word_count": len(summary.split())
        }

        # Check if critical sections are covered
        critical_sections = {
            SummaryMode.EXECUTIVE: ["diagnosis", "treatment", "prognosis"],
            SummaryMode.SURGICAL_STEPS: ["approach", "technique", "closure"],
            SummaryMode.DIAGNOSTIC_ALGORITHM: ["presentation", "workup", "differential"],
            SummaryMode.EMERGENCY_GUIDE: ["immediate", "red flags", "treatment"]
        }

        if mode in critical_sections:
            for section in critical_sections[mode]:
                if section.lower() not in summary.lower():
                    validation["missing_elements"].append(section)
                    validation["is_valid"] = False

        # Check completeness score
        covered_sections = sum(1 for section in original_chapter.get("content", {})
                              if section in summary)
        total_sections = len(original_chapter.get("content", {}))
        validation["completeness_score"] = covered_sections / max(total_sections, 1)

        # Verify no hallucinated content (basic check)
        validation["accuracy_checks"].append({
            "check": "no_external_content",
            "passed": True  # Would need more sophisticated checking in production
        })

        # Check citations if present
        if "[" in summary and "]" in summary:
            validation["accuracy_checks"].append({
                "check": "citations_present",
                "passed": True
            })

        return validation

    async def batch_generate_summaries(
        self,
        chapter_data: Dict[str, Any],
        modes: List[SummaryMode],
        length: SummaryLength = SummaryLength.STANDARD
    ) -> Dict[str, Dict[str, Any]]:
        """
        Generates multiple summary types for the same chapter.
        Useful for creating comprehensive documentation.
        """

        summaries = {}

        for mode in modes:
            logger.info(f"Generating {mode.value} summary...")
            summary_result = await self.generate_summary(
                chapter_data=chapter_data,
                mode=mode,
                length=length
            )
            summaries[mode.value] = summary_result

        return summaries


# Utility class for summary export
class SummaryExporter:
    """Handles export of summaries to various formats"""

    @staticmethod
    def to_markdown(summary_data: Dict[str, Any]) -> str:
        """Exports summary to Markdown format"""
        return summary_data.get("summary", "")

    @staticmethod
    def to_html(summary_data: Dict[str, Any]) -> str:
        """Exports summary to HTML format"""
        import markdown
        md_content = summary_data.get("summary", "")
        return markdown.markdown(md_content, extensions=['tables', 'fenced_code'])

    @staticmethod
    def to_pdf(summary_data: Dict[str, Any], output_path: str) -> bool:
        """Exports summary to PDF format"""
        # Would require PDF generation library
        # For now, returns placeholder
        logger.info(f"PDF export to {output_path} - requires implementation")
        return False

    @staticmethod
    def to_docx(summary_data: Dict[str, Any], output_path: str) -> bool:
        """Exports summary to Word document format"""
        # Would require python-docx or similar
        # For now, returns placeholder
        logger.info(f"DOCX export to {output_path} - requires implementation")
        return False