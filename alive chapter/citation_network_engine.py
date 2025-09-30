# backend/core/citation_network_engine.py
"""
Citation Network Engine for Inter-Chapter Cross-References
Creates and maintains comprehensive citation networks across chapters
"""

from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import networkx as nx
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import asyncio
import json
import hashlib
import re
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class CitationType(Enum):
    EXPLICIT = "explicit"  # Direct citation with reference
    IMPLICIT = "implicit"  # Conceptual connection without citation
    SEMANTIC = "semantic"  # Similar concepts/topics
    TEMPORAL = "temporal"  # Time-based dependency
    HIERARCHICAL = "hierarchical"  # Parent-child relationship
    CONFLICTING = "conflicting"  # Contradictory information
    SUPPORTING = "supporting"  # Supporting evidence
    EXTENDING = "extending"  # Builds upon previous work

class ReferenceType(Enum):
    INTERNAL_CHAPTER = "internal_chapter"
    EXTERNAL_PAPER = "external_paper"
    CLINICAL_GUIDELINE = "clinical_guideline"
    TEXTBOOK = "textbook"
    CASE_STUDY = "case_study"
    REVIEW_ARTICLE = "review_article"
    ORIGINAL_RESEARCH = "original_research"
    META_ANALYSIS = "meta_analysis"

@dataclass
class Citation:
    citation_id: str
    source_chapter: str
    target_chapter: str
    citation_type: CitationType
    reference_type: ReferenceType
    strength: float  # 0.0 to 1.0
    confidence: float
    context: str  # Text context around citation
    position: int  # Position in source chapter
    created_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CrossReference:
    reference_id: str
    from_chapter: str
    to_resource: str  # Can be chapter ID or external resource
    reference_text: str
    reference_type: ReferenceType
    relevance_score: float
    auto_detected: bool
    verified: bool
    section_context: str
    medical_concepts: List[str]
    created_at: datetime

@dataclass
class ConceptConnection:
    concept: str
    chapters: List[str]  # Chapters containing this concept
    frequency: Dict[str, int]  # Frequency in each chapter
    importance_scores: Dict[str, float]  # Importance in each chapter
    semantic_variations: List[str]  # Similar terms
    medical_category: str  # Disease, symptom, treatment, etc.

@dataclass
class CitationCluster:
    cluster_id: str
    central_topic: str
    chapters: List[str]
    citations: List[Citation]
    coherence_score: float
    key_concepts: List[str]
    cluster_type: str  # Topic cluster, author cluster, temporal cluster

class ReferenceIndex:
    """Maintains searchable index of all references"""

    def __init__(self):
        self.references = {}  # reference_id -> CrossReference
        self.chapter_index = defaultdict(list)  # chapter_id -> [reference_ids]
        self.concept_index = defaultdict(set)  # concept -> {reference_ids}
        self.external_index = defaultdict(list)  # external_resource -> [reference_ids]
        self.tfidf_vectorizer = TfidfVectorizer(max_features=5000)
        self.reference_embeddings = {}

    async def add_reference(self, reference: CrossReference):
        """Add reference to index"""
        self.references[reference.reference_id] = reference
        self.chapter_index[reference.from_chapter].append(reference.reference_id)

        # Index by concepts
        for concept in reference.medical_concepts:
            self.concept_index[concept.lower()].add(reference.reference_id)

        # Index external resources
        if reference.reference_type != ReferenceType.INTERNAL_CHAPTER:
            self.external_index[reference.to_resource].append(reference.reference_id)

        # Generate embedding for semantic search
        self.reference_embeddings[reference.reference_id] = await self._generate_embedding(
            reference.reference_text
        )

    async def search_references(self, query: str, limit: int = 10) -> List[CrossReference]:
        """Search references by query"""
        results = []

        # Concept-based search
        query_concepts = await self._extract_concepts(query)
        concept_matches = set()

        for concept in query_concepts:
            concept_matches.update(self.concept_index.get(concept.lower(), set()))

        # Add concept matches to results
        for ref_id in concept_matches:
            if ref_id in self.references:
                results.append(self.references[ref_id])

        # Semantic search if we have embeddings
        if self.reference_embeddings:
            query_embedding = await self._generate_embedding(query)

            similarities = []
            for ref_id, embedding in self.reference_embeddings.items():
                similarity = self._calculate_similarity(query_embedding, embedding)
                similarities.append((ref_id, similarity))

            # Sort by similarity
            similarities.sort(key=lambda x: x[1], reverse=True)

            # Add semantic matches
            for ref_id, score in similarities[:limit]:
                if ref_id in self.references and self.references[ref_id] not in results:
                    results.append(self.references[ref_id])

        return results[:limit]

    async def get_chapter_references(self, chapter_id: str) -> List[CrossReference]:
        """Get all references from a chapter"""
        ref_ids = self.chapter_index.get(chapter_id, [])
        return [self.references[ref_id] for ref_id in ref_ids if ref_id in self.references]

    async def get_concept_references(self, concept: str) -> List[CrossReference]:
        """Get all references containing a concept"""
        ref_ids = self.concept_index.get(concept.lower(), set())
        return [self.references[ref_id] for ref_id in ref_ids if ref_id in self.references]

    async def _generate_embedding(self, text: str) -> np.ndarray:
        """Generate text embedding for semantic search"""
        # Simplified - would use actual embedding model
        words = text.lower().split()
        embedding = np.zeros(100)  # Simplified 100-dimensional embedding

        for i, word in enumerate(words[:100]):
            embedding[i % 100] += hash(word) % 10 / 10.0

        return embedding / np.linalg.norm(embedding)

    async def _extract_concepts(self, text: str) -> List[str]:
        """Extract medical concepts from text"""
        # Simplified concept extraction
        medical_terms = [
            "diagnosis", "treatment", "symptom", "disease", "medication",
            "surgery", "therapy", "syndrome", "disorder", "condition"
        ]

        concepts = []
        text_lower = text.lower()

        for term in medical_terms:
            if term in text_lower:
                concepts.append(term)

        return concepts

    def _calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between embeddings"""
        return float(np.dot(embedding1, embedding2) /
                    (np.linalg.norm(embedding1) * np.linalg.norm(embedding2)))

class CrossReferenceDetector:
    """Detects potential cross-references between chapters"""

    def __init__(self):
        self.concept_extractor = ConceptExtractor()
        self.similarity_calculator = SimilarityCalculator()
        self.medical_ontology = self._load_medical_ontology()

    def _load_medical_ontology(self) -> Dict[str, List[str]]:
        """Load medical ontology for reference detection"""
        return {
            "diseases": ["cancer", "diabetes", "hypertension", "pneumonia", "stroke"],
            "treatments": ["chemotherapy", "radiation", "surgery", "medication", "therapy"],
            "anatomy": ["brain", "heart", "liver", "kidney", "lung", "bone"],
            "symptoms": ["pain", "fever", "cough", "fatigue", "nausea"],
            "procedures": ["biopsy", "mri", "ct scan", "blood test", "surgery"]
        }

    async def detect_cross_references(self,
                                     source_chapter: Dict[str, Any],
                                     all_chapters: List[Dict[str, Any]]) -> List[CrossReference]:
        """Detect potential cross-references from source chapter to others"""
        cross_references = []

        # Extract concepts from source chapter
        source_concepts = await self.concept_extractor.extract_concepts(
            source_chapter["content"]
        )

        # Compare with other chapters
        for target_chapter in all_chapters:
            if target_chapter["id"] == source_chapter["id"]:
                continue

            # Extract target concepts
            target_concepts = await self.concept_extractor.extract_concepts(
                target_chapter["content"]
            )

            # Find overlapping concepts
            overlapping = await self._find_overlapping_concepts(
                source_concepts, target_concepts
            )

            if overlapping:
                # Calculate relevance
                relevance = await self.similarity_calculator.calculate_relevance(
                    source_chapter["content"],
                    target_chapter["content"],
                    overlapping
                )

                if relevance > 0.3:  # Threshold for relevance
                    # Create cross-reference
                    reference = CrossReference(
                        reference_id=hashlib.md5(
                            f"{source_chapter['id']}_{target_chapter['id']}_{datetime.now()}".encode()
                        ).hexdigest()[:8],
                        from_chapter=source_chapter["id"],
                        to_resource=target_chapter["id"],
                        reference_text=f"See related content in {target_chapter.get('title', 'Chapter')}",
                        reference_type=ReferenceType.INTERNAL_CHAPTER,
                        relevance_score=relevance,
                        auto_detected=True,
                        verified=False,
                        section_context=await self._find_best_context(
                            source_chapter["content"], overlapping
                        ),
                        medical_concepts=overlapping,
                        created_at=datetime.now()
                    )
                    cross_references.append(reference)

        # Detect references to external resources
        external_refs = await self._detect_external_references(source_chapter["content"])
        cross_references.extend(external_refs)

        return cross_references

    async def _find_overlapping_concepts(self,
                                        source_concepts: List[str],
                                        target_concepts: List[str]) -> List[str]:
        """Find overlapping medical concepts"""
        source_set = set(c.lower() for c in source_concepts)
        target_set = set(c.lower() for c in target_concepts)

        overlapping = list(source_set & target_set)

        # Also find semantically similar concepts
        for source_concept in source_concepts:
            for target_concept in target_concepts:
                if source_concept != target_concept:
                    similarity = await self._calculate_concept_similarity(
                        source_concept, target_concept
                    )
                    if similarity > 0.8:
                        overlapping.append(f"{source_concept}~{target_concept}")

        return overlapping

    async def _calculate_concept_similarity(self, concept1: str, concept2: str) -> float:
        """Calculate semantic similarity between two concepts"""
        # Simplified similarity calculation
        # Would use medical word embeddings in production

        if concept1.lower() == concept2.lower():
            return 1.0

        # Check if one contains the other
        if concept1.lower() in concept2.lower() or concept2.lower() in concept1.lower():
            return 0.7

        # Check medical synonyms (simplified)
        synonyms = {
            "tumor": ["cancer", "neoplasm", "malignancy"],
            "hypertension": ["high blood pressure", "htn"],
            "diabetes": ["dm", "diabetes mellitus"],
            "heart attack": ["myocardial infarction", "mi"],
        }

        for base, syns in synonyms.items():
            if concept1.lower() in [base] + syns and concept2.lower() in [base] + syns:
                return 0.9

        return 0.0

    async def _find_best_context(self, content: str, concepts: List[str]) -> str:
        """Find the best context section for cross-reference"""
        # Find paragraph containing most concepts
        paragraphs = content.split("\n\n")

        best_paragraph = ""
        max_concept_count = 0

        for paragraph in paragraphs:
            paragraph_lower = paragraph.lower()
            concept_count = sum(
                1 for concept in concepts
                if concept.lower() in paragraph_lower
            )

            if concept_count > max_concept_count:
                max_concept_count = concept_count
                best_paragraph = paragraph

        # Return first 200 characters of best paragraph
        return best_paragraph[:200] if best_paragraph else ""

    async def _detect_external_references(self, content: str) -> List[CrossReference]:
        """Detect references to external resources (papers, guidelines, etc.)"""
        references = []

        # Detect DOI patterns
        doi_pattern = r'10\.\d{4,}/[-._;()/:\w]+'
        dois = re.findall(doi_pattern, content)

        for doi in dois:
            reference = CrossReference(
                reference_id=hashlib.md5(f"doi_{doi}".encode()).hexdigest()[:8],
                from_chapter="current",
                to_resource=doi,
                reference_text=f"DOI: {doi}",
                reference_type=ReferenceType.EXTERNAL_PAPER,
                relevance_score=0.9,
                auto_detected=True,
                verified=False,
                section_context="",
                medical_concepts=[],
                created_at=datetime.now()
            )
            references.append(reference)

        # Detect PMID patterns
        pmid_pattern = r'PMID:?\s*(\d+)'
        pmids = re.findall(pmid_pattern, content, re.IGNORECASE)

        for pmid in pmids:
            reference = CrossReference(
                reference_id=hashlib.md5(f"pmid_{pmid}".encode()).hexdigest()[:8],
                from_chapter="current",
                to_resource=f"PMID:{pmid}",
                reference_text=f"PubMed ID: {pmid}",
                reference_type=ReferenceType.EXTERNAL_PAPER,
                relevance_score=0.9,
                auto_detected=True,
                verified=False,
                section_context="",
                medical_concepts=[],
                created_at=datetime.now()
            )
            references.append(reference)

        # Detect guideline references
        guideline_patterns = [
            r'(ACC/AHA|ESC|NICE|WHO|CDC) [Gg]uidelines?',
            r'clinical practice guidelines?',
            r'consensus statement'
        ]

        for pattern in guideline_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                reference = CrossReference(
                    reference_id=hashlib.md5(f"guideline_{match}".encode()).hexdigest()[:8],
                    from_chapter="current",
                    to_resource=match,
                    reference_text=match,
                    reference_type=ReferenceType.CLINICAL_GUIDELINE,
                    relevance_score=0.85,
                    auto_detected=True,
                    verified=False,
                    section_context="",
                    medical_concepts=[],
                    created_at=datetime.now()
                )
                references.append(reference)

        return references

class ConceptExtractor:
    """Extracts medical concepts from text"""

    def __init__(self):
        self.medical_vocabulary = self._load_medical_vocabulary()

    def _load_medical_vocabulary(self) -> Set[str]:
        """Load medical vocabulary"""
        # Simplified medical vocabulary
        return {
            # Diseases
            "cancer", "tumor", "carcinoma", "lymphoma", "leukemia",
            "diabetes", "hypertension", "pneumonia", "tuberculosis",
            "stroke", "myocardial infarction", "heart failure",
            # Symptoms
            "pain", "fever", "cough", "dyspnea", "fatigue",
            "nausea", "vomiting", "diarrhea", "headache", "dizziness",
            # Treatments
            "chemotherapy", "radiation", "surgery", "medication",
            "antibiotic", "analgesic", "immunotherapy", "transplant",
            # Anatomy
            "brain", "heart", "lung", "liver", "kidney",
            "bone", "muscle", "nerve", "vessel", "artery",
            # Procedures
            "biopsy", "imaging", "mri", "ct scan", "ultrasound",
            "endoscopy", "colonoscopy", "catheterization"
        }

    async def extract_concepts(self, text: str) -> List[str]:
        """Extract medical concepts from text"""
        concepts = []
        text_lower = text.lower()

        # Extract from vocabulary
        for term in self.medical_vocabulary:
            if term in text_lower:
                # Count frequency
                frequency = text_lower.count(term)
                if frequency > 0:
                    concepts.append(term)

        # Extract multi-word concepts
        multi_word_patterns = [
            r'[A-Z][a-z]+\s+[A-Z][a-z]+\s+[Ss]yndrome',
            r'[A-Z][a-z]+\'s\s+[Dd]isease',
            r'[Aa]cute\s+[A-Za-z]+',
            r'[Cc]hronic\s+[A-Za-z]+'
        ]

        for pattern in multi_word_patterns:
            matches = re.findall(pattern, text)
            concepts.extend(matches)

        # Remove duplicates and return
        return list(set(concepts))

class SimilarityCalculator:
    """Calculates similarity between texts and concepts"""

    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000)

    async def calculate_relevance(self,
                                 source_text: str,
                                 target_text: str,
                                 shared_concepts: List[str]) -> float:
        """Calculate relevance score between texts"""

        # Concept-based relevance
        concept_score = len(shared_concepts) / 10.0  # Normalize
        concept_score = min(1.0, concept_score)

        # Text similarity
        try:
            # Fit and transform texts
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([source_text, target_text])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        except:
            similarity = 0.0

        # Weighted combination
        relevance = (concept_score * 0.6) + (similarity * 0.4)

        return float(relevance)

class CitationSuggester:
    """Suggests relevant citations for content"""

    def __init__(self):
        self.citation_scorer = CitationScorer()
        self.context_analyzer = ContextAnalyzer()

    async def suggest_citations(self,
                               current_context: str,
                               available_resources: List[Dict[str, Any]],
                               citation_history: List[Citation]) -> List[Dict[str, Any]]:
        """Suggest relevant citations based on current context"""
        suggestions = []

        # Analyze current context
        context_analysis = await self.context_analyzer.analyze(current_context)
        needed_evidence_types = context_analysis.get("needed_evidence", [])
        key_concepts = context_analysis.get("key_concepts", [])

        # Score each available resource
        for resource in available_resources:
            score = await self.citation_scorer.score_resource(
                resource,
                current_context,
                needed_evidence_types,
                key_concepts
            )

            if score > 0.5:  # Threshold for suggestion
                suggestion = {
                    "resource": resource,
                    "relevance_score": score,
                    "suggested_citation_text": await self._generate_citation_text(resource),
                    "insertion_point": await self._find_insertion_point(
                        current_context, resource
                    ),
                    "citation_type": await self._determine_citation_type(
                        resource, context_analysis
                    )
                }
                suggestions.append(suggestion)

        # Sort by relevance
        suggestions.sort(key=lambda x: x["relevance_score"], reverse=True)

        # Filter based on citation history to avoid over-citation
        filtered_suggestions = await self._filter_by_history(
            suggestions, citation_history
        )

        return filtered_suggestions[:10]  # Top 10 suggestions

    async def _generate_citation_text(self, resource: Dict[str, Any]) -> str:
        """Generate appropriate citation text for resource"""

        resource_type = resource.get("type", "unknown")

        if resource_type == "journal_article":
            authors = resource.get("authors", ["Unknown"])
            year = resource.get("year", "n.d.")
            title = resource.get("title", "Untitled")

            if len(authors) > 2:
                citation = f"{authors[0].split()[-1]} et al. ({year})"
            elif len(authors) == 2:
                citation = f"{authors[0].split()[-1]} & {authors[1].split()[-1]} ({year})"
            else:
                citation = f"{authors[0].split()[-1]} ({year})"

            return citation

        elif resource_type == "chapter":
            return f"See Chapter {resource.get('chapter_number', 'X')}: {resource.get('title', 'Related Topic')}"

        elif resource_type == "guideline":
            org = resource.get("organization", "Organization")
            year = resource.get("year", "n.d.")
            return f"{org} Guidelines ({year})"

        else:
            return f"[{resource.get('title', 'Reference')}]"

    async def _find_insertion_point(self, context: str, resource: Dict[str, Any]) -> int:
        """Find best position to insert citation"""

        # Find sentences mentioning key concepts from resource
        key_concepts = resource.get("key_concepts", [])

        sentences = context.split('.')
        best_position = -1
        max_relevance = 0

        current_position = 0
        for i, sentence in enumerate(sentences):
            sentence_lower = sentence.lower()

            # Count concept matches
            relevance = sum(
                1 for concept in key_concepts
                if concept.lower() in sentence_lower
            )

            if relevance > max_relevance:
                max_relevance = relevance
                best_position = current_position + len(sentence)

            current_position += len(sentence) + 1  # +1 for period

        return best_position if best_position != -1 else len(context)

    async def _determine_citation_type(self,
                                      resource: Dict[str, Any],
                                      context_analysis: Dict[str, Any]) -> CitationType:
        """Determine appropriate citation type"""

        needed_evidence = context_analysis.get("needed_evidence", [])

        if "supporting_evidence" in needed_evidence:
            return CitationType.SUPPORTING
        elif "conflicting_views" in needed_evidence:
            return CitationType.CONFLICTING
        elif "foundational" in needed_evidence:
            return CitationType.HIERARCHICAL
        else:
            return CitationType.SEMANTIC

    async def _filter_by_history(self,
                                suggestions: List[Dict[str, Any]],
                                citation_history: List[Citation]) -> List[Dict[str, Any]]:
        """Filter suggestions based on citation history"""

        # Get recently cited resources
        recent_cutoff = datetime.now() - timedelta(hours=1)
        recent_citations = [
            c for c in citation_history
            if c.created_at > recent_cutoff
        ]

        recently_cited_ids = set(c.target_chapter for c in recent_citations)

        # Filter out recently cited resources unless highly relevant
        filtered = []
        for suggestion in suggestions:
            resource_id = suggestion["resource"].get("id")

            # Include if not recently cited or very relevant
            if resource_id not in recently_cited_ids or suggestion["relevance_score"] > 0.9:
                filtered.append(suggestion)

        return filtered

class CitationScorer:
    """Scores resources for citation relevance"""

    async def score_resource(self,
                            resource: Dict[str, Any],
                            context: str,
                            needed_evidence_types: List[str],
                            key_concepts: List[str]) -> float:
        """Score a resource for citation relevance"""

        score = 0.0

        # Evidence type matching
        resource_type = resource.get("evidence_type", "unknown")
        if resource_type in needed_evidence_types:
            score += 0.3

        # Concept overlap
        resource_concepts = resource.get("concepts", [])
        overlap = len(set(key_concepts) & set(resource_concepts))
        score += min(0.4, overlap * 0.1)

        # Recency bonus
        if "publication_date" in resource:
            pub_date = resource["publication_date"]
            if isinstance(pub_date, str):
                try:
                    pub_date = datetime.strptime(pub_date, "%Y-%m-%d")
                except:
                    pub_date = None

            if pub_date:
                years_old = (datetime.now() - pub_date).days / 365
                if years_old < 2:
                    score += 0.2
                elif years_old < 5:
                    score += 0.1

        # Quality score
        quality = resource.get("quality_score", 0.5)
        score += quality * 0.1

        return min(1.0, score)

class ContextAnalyzer:
    """Analyzes context to determine citation needs"""

    async def analyze(self, context: str) -> Dict[str, Any]:
        """Analyze context for citation needs"""

        analysis = {
            "needed_evidence": [],
            "key_concepts": [],
            "citation_density": 0.0,
            "section_type": "general"
        }

        context_lower = context.lower()

        # Determine needed evidence types
        if "studies show" in context_lower or "research indicates" in context_lower:
            analysis["needed_evidence"].append("supporting_evidence")

        if "controversial" in context_lower or "debate" in context_lower:
            analysis["needed_evidence"].append("conflicting_views")

        if "fundamental" in context_lower or "basic" in context_lower:
            analysis["needed_evidence"].append("foundational")

        # Extract key concepts (simplified)
        medical_terms = [
            "treatment", "diagnosis", "symptom", "disease",
            "medication", "surgery", "therapy", "prognosis"
        ]

        for term in medical_terms:
            if term in context_lower:
                analysis["key_concepts"].append(term)

        # Calculate citation density
        existing_citations = len(re.findall(r'\[\d+\]', context))
        total_sentences = len(context.split('.'))

        if total_sentences > 0:
            analysis["citation_density"] = existing_citations / total_sentences

        # Determine section type
        if "introduction" in context_lower[:100]:
            analysis["section_type"] = "introduction"
        elif "method" in context_lower[:100]:
            analysis["section_type"] = "methods"
        elif "result" in context_lower[:100]:
            analysis["section_type"] = "results"
        elif "discussion" in context_lower[:100]:
            analysis["section_type"] = "discussion"

        return analysis

class CitationNetworkVisualizer:
    """Creates visualizations of citation networks"""

    async def visualize_network(self,
                               citations: List[Citation],
                               chapters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create visualization data for citation network"""

        # Create nodes
        nodes = []
        for chapter in chapters:
            nodes.append({
                "id": chapter["id"],
                "label": chapter.get("title", f"Chapter {chapter['id']}"),
                "type": "chapter",
                "size": len([c for c in citations
                           if c.source_chapter == chapter["id"] or
                           c.target_chapter == chapter["id"]])
            })

        # Create edges
        edges = []
        for citation in citations:
            edges.append({
                "source": citation.source_chapter,
                "target": citation.target_chapter,
                "type": citation.citation_type.value,
                "weight": citation.strength,
                "label": citation.citation_type.value
            })

        # Calculate layout positions (simplified)
        positions = await self._calculate_layout(nodes, edges)

        # Add positions to nodes
        for i, node in enumerate(nodes):
            node["x"] = positions[i][0]
            node["y"] = positions[i][1]

        # Calculate metrics
        metrics = await self._calculate_network_metrics(nodes, edges)

        return {
            "nodes": nodes,
            "edges": edges,
            "metrics": metrics,
            "visualization_type": "force-directed",
            "timestamp": datetime.now().isoformat()
        }

    async def _calculate_layout(self,
                              nodes: List[Dict[str, Any]],
                              edges: List[Dict[str, Any]]) -> List[Tuple[float, float]]:
        """Calculate layout positions for nodes"""

        # Simple circular layout
        n = len(nodes)
        positions = []

        for i in range(n):
            angle = 2 * np.pi * i / n
            x = np.cos(angle) * 100
            y = np.sin(angle) * 100
            positions.append((x, y))

        return positions

    async def _calculate_network_metrics(self,
                                        nodes: List[Dict[str, Any]],
                                        edges: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate network metrics"""

        # Create NetworkX graph for analysis
        G = nx.DiGraph()

        for node in nodes:
            G.add_node(node["id"])

        for edge in edges:
            G.add_edge(edge["source"], edge["target"], weight=edge["weight"])

        metrics = {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "density": nx.density(G) if len(nodes) > 0 else 0,
            "average_degree": sum(dict(G.degree()).values()) / len(nodes) if len(nodes) > 0 else 0,
            "connected_components": nx.number_weakly_connected_components(G),
            "most_cited": "",
            "most_citing": ""
        }

        # Find most cited and most citing chapters
        in_degrees = dict(G.in_degree())
        out_degrees = dict(G.out_degree())

        if in_degrees:
            metrics["most_cited"] = max(in_degrees, key=in_degrees.get)

        if out_degrees:
            metrics["most_citing"] = max(out_degrees, key=out_degrees.get)

        return metrics

class CitationNetworkEngine:
    """
    Main engine for managing inter-chapter citation networks
    """

    def __init__(self):
        self.citation_graph = nx.DiGraph()
        self.reference_index = ReferenceIndex()
        self.cross_reference_detector = CrossReferenceDetector()
        self.citation_suggester = CitationSuggester()
        self.network_visualizer = CitationNetworkVisualizer()
        self.citation_history = []
        self.concept_connections = {}

        logger.info("Citation Network Engine initialized")

    async def build_citation_network(self, all_chapters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build comprehensive citation network from all chapters"""

        try:
            citations = []
            cross_references = []

            # Process each chapter
            for chapter in all_chapters:
                # Detect cross-references
                chapter_refs = await self.cross_reference_detector.detect_cross_references(
                    chapter, all_chapters
                )
                cross_references.extend(chapter_refs)

                # Add references to index
                for ref in chapter_refs:
                    await self.reference_index.add_reference(ref)

                # Create citations
                for ref in chapter_refs:
                    if ref.reference_type == ReferenceType.INTERNAL_CHAPTER:
                        citation = Citation(
                            citation_id=ref.reference_id,
                            source_chapter=chapter["id"],
                            target_chapter=ref.to_resource,
                            citation_type=CitationType.SEMANTIC,
                            reference_type=ref.reference_type,
                            strength=ref.relevance_score,
                            confidence=0.8,
                            context=ref.section_context,
                            position=0,  # Would be calculated from actual position
                            created_at=datetime.now()
                        )
                        citations.append(citation)

                        # Add to graph
                        self.citation_graph.add_edge(
                            chapter["id"],
                            ref.to_resource,
                            citation=citation
                        )

            # Store citation history
            self.citation_history.extend(citations)

            # Build concept connections
            await self._build_concept_connections(all_chapters)

            # Calculate network metrics
            metrics = {
                "total_citations": len(citations),
                "total_cross_references": len(cross_references),
                "chapters_analyzed": len(all_chapters),
                "network_density": nx.density(self.citation_graph),
                "average_citations_per_chapter": len(citations) / len(all_chapters) if all_chapters else 0
            }

            return {
                "status": "success",
                "citations": len(citations),
                "cross_references": len(cross_references),
                "metrics": metrics,
                "build_time": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error building citation network: {e}")
            return {"status": "error", "message": str(e)}

    async def detect_cross_references(self, chapter_content: str,
                                    chapter_id: str) -> List[CrossReference]:
        """Detect cross-references in a specific chapter"""

        try:
            # Get all chapters for comparison
            # This would fetch from database in production
            all_chapters = [{"id": chapter_id, "content": chapter_content}]

            # Detect references
            references = await self.cross_reference_detector.detect_cross_references(
                {"id": chapter_id, "content": chapter_content},
                all_chapters
            )

            # Add to index
            for ref in references:
                await self.reference_index.add_reference(ref)

            return references

        except Exception as e:
            logger.error(f"Error detecting cross-references: {e}")
            return []

    async def suggest_citations(self, current_context: str,
                               chapter_id: str) -> List[Dict[str, Any]]:
        """Suggest relevant citations for current context"""

        try:
            # Get available resources
            # This would fetch from database and external sources
            available_resources = await self._get_available_resources(chapter_id)

            # Get citation history for chapter
            chapter_citations = [
                c for c in self.citation_history
                if c.source_chapter == chapter_id
            ]

            # Generate suggestions
            suggestions = await self.citation_suggester.suggest_citations(
                current_context,
                available_resources,
                chapter_citations
            )

            return suggestions

        except Exception as e:
            logger.error(f"Error suggesting citations: {e}")
            return []

    async def visualize_citation_network(self, chapter_id: Optional[str] = None) -> Dict[str, Any]:
        """Create visualization of citation network"""

        try:
            # Filter citations if chapter_id provided
            if chapter_id:
                relevant_citations = [
                    c for c in self.citation_history
                    if c.source_chapter == chapter_id or c.target_chapter == chapter_id
                ]

                # Get relevant chapters
                chapter_ids = set()
                for c in relevant_citations:
                    chapter_ids.add(c.source_chapter)
                    chapter_ids.add(c.target_chapter)

                chapters = [{"id": cid, "title": f"Chapter {cid}"} for cid in chapter_ids]

            else:
                relevant_citations = self.citation_history

                # Get all chapters
                chapter_ids = set()
                for c in relevant_citations:
                    chapter_ids.add(c.source_chapter)
                    chapter_ids.add(c.target_chapter)

                chapters = [{"id": cid, "title": f"Chapter {cid}"} for cid in chapter_ids]

            # Create visualization
            visualization = await self.network_visualizer.visualize_network(
                relevant_citations,
                chapters
            )

            return visualization

        except Exception as e:
            logger.error(f"Error visualizing network: {e}")
            return {"error": str(e)}

    async def get_citation_statistics(self, chapter_id: str) -> Dict[str, Any]:
        """Get citation statistics for a chapter"""

        try:
            incoming = self.citation_graph.in_degree(chapter_id)
            outgoing = self.citation_graph.out_degree(chapter_id)

            # Get citation types
            incoming_citations = [
                c for c in self.citation_history
                if c.target_chapter == chapter_id
            ]

            outgoing_citations = [
                c for c in self.citation_history
                if c.source_chapter == chapter_id
            ]

            # Analyze citation types
            citation_types = defaultdict(int)
            for c in incoming_citations + outgoing_citations:
                citation_types[c.citation_type.value] += 1

            # Get connected chapters
            predecessors = list(self.citation_graph.predecessors(chapter_id))
            successors = list(self.citation_graph.successors(chapter_id))

            stats = {
                "chapter_id": chapter_id,
                "incoming_citations": incoming,
                "outgoing_citations": outgoing,
                "total_citations": incoming + outgoing,
                "citation_types": dict(citation_types),
                "cited_by": predecessors,
                "cites": successors,
                "centrality_score": nx.degree_centrality(self.citation_graph).get(chapter_id, 0),
                "clustering_coefficient": nx.clustering(self.citation_graph.to_undirected()).get(chapter_id, 0)
            }

            return stats

        except Exception as e:
            logger.error(f"Error getting citation statistics: {e}")
            return {"chapter_id": chapter_id, "error": str(e)}

    async def _build_concept_connections(self, chapters: List[Dict[str, Any]]):
        """Build concept connections across chapters"""

        concept_extractor = ConceptExtractor()

        for chapter in chapters:
            concepts = await concept_extractor.extract_concepts(chapter["content"])

            for concept in concepts:
                if concept not in self.concept_connections:
                    self.concept_connections[concept] = ConceptConnection(
                        concept=concept,
                        chapters=[],
                        frequency={},
                        importance_scores={},
                        semantic_variations=[],
                        medical_category=""
                    )

                # Update concept connection
                connection = self.concept_connections[concept]

                if chapter["id"] not in connection.chapters:
                    connection.chapters.append(chapter["id"])

                # Count frequency
                connection.frequency[chapter["id"]] = chapter["content"].lower().count(concept.lower())

                # Calculate importance (simplified)
                connection.importance_scores[chapter["id"]] = min(
                    1.0,
                    connection.frequency[chapter["id"]] / 10.0
                )

    async def _get_available_resources(self, chapter_id: str) -> List[Dict[str, Any]]:
        """Get available resources for citation"""

        # This would fetch from multiple sources in production
        # Simplified mock data
        resources = [
            {
                "id": "resource_1",
                "type": "journal_article",
                "title": "Recent Advances in Treatment",
                "authors": ["Smith J", "Jones M"],
                "year": 2024,
                "concepts": ["treatment", "therapy"],
                "evidence_type": "supporting_evidence",
                "quality_score": 0.9
            },
            {
                "id": "chapter_2",
                "type": "chapter",
                "title": "Foundational Concepts",
                "chapter_number": 2,
                "concepts": ["diagnosis", "pathophysiology"],
                "evidence_type": "foundational",
                "quality_score": 0.85
            }
        ]

        return resources

# Initialize global instance
citation_network_engine = CitationNetworkEngine()