"""
Enhanced Synthesis Engine - Complete Knowledge Extraction and Integration
Implements internal-first philosophy with deep content understanding and comprehensive synthesis
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import re
from pathlib import Path

logger = logging.getLogger(__name__)

class ContentType(Enum):
    TEXT = "text"
    TABLE = "table"
    IMAGE = "image"
    FORMULA = "formula"
    DIAGRAM = "diagram"

@dataclass
class ContentElement:
    """Represents a single element of content from references"""
    type: ContentType
    content: str
    source: str
    citation: str
    page_number: Optional[int] = None
    confidence_score: float = 1.0
    metadata: Dict[str, Any] = None

@dataclass
class ContentAnalysis:
    """Analysis results for content understanding"""
    similarities: List[Dict[str, Any]]
    differences: List[Dict[str, Any]]
    complementary_info: List[Dict[str, Any]]
    contradictions: List[Dict[str, Any]]
    knowledge_gaps: List[str]
    unique_insights: List[Dict[str, Any]]

class EnhancedSynthesisEngine:
    """
    Advanced synthesis engine with deep content understanding and comprehensive integration.
    Ensures all knowledge, details, and subtleties are captured in structured, accurate chapters.
    """

    def __init__(self, hybrid_ai_manager=None, pdf_extractor=None):
        self.hybrid_ai_manager = hybrid_ai_manager
        self.pdf_extractor = pdf_extractor
        self.chapter_sections = self._get_comprehensive_structure()

        # Support for standalone operation if AI manager not provided
        self.standalone_mode = hybrid_ai_manager is None

    def _get_comprehensive_structure(self) -> List[str]:
        """Returns comprehensive chapter structure for neurosurgical topics"""
        return [
            "Introduction",
            "Epidemiology",
            "Risk Factors",
            "Pathophysiology",
            "Molecular Biology",
            "Genetics",
            "Classification Systems",
            "Clinical Presentation",
            "Physical Examination",
            "Differential Diagnosis",
            "Diagnostic Workup",
            "Laboratory Studies",
            "Imaging",
            "Advanced Imaging Techniques",
            "Surgical Anatomy",
            "Treatment Options and Alternatives",
            "Conservative Management",
            "Medical Management",
            "Surgical Indications",
            "Preoperative Planning",
            "Surgical Techniques",
            "Step-by-Step Surgical Procedure",
            "Intraoperative Monitoring",
            "Postoperative Management",
            "Complications",
            "Adjuvant Therapy",
            "Radiation Therapy",
            "Chemotherapy",
            "Targeted Therapy",
            "Pathology",
            "Histopathological Features",
            "Immunohistochemistry",
            "Molecular Markers",
            "Prognosis",
            "Survival Statistics",
            "Progression Patterns",
            "Quality of Life",
            "Follow-up Protocol",
            "Recurrence Management",
            "Recent Advances",
            "Future Directions",
            "Key Points Summary",
            "Conclusion",
            "References"
        ]

    async def synthesize_initial_chapter(
        self,
        topic: str,
        internal_references: List[Dict[str, Any]],
        include_images: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Main orchestration function for comprehensive initial synthesis.
        Implements deep understanding and complete knowledge extraction.
        """

        if not internal_references:
            logger.warning(f"No internal references provided for topic: {topic}")
            return None

        logger.info(f"Starting comprehensive synthesis for topic: {topic}")

        # Process Flow with Deep Understanding
        try:
            # 1. Extract and prepare all content elements (text, tables, images)
            content_elements = await self._extract_content_elements(internal_references, include_images)

            # 2. Deeply analyze content relationships
            content_analysis = await self._analyze_content_relationships(content_elements, topic)

            # 3. Determine optimal structure based on available content
            chapter_structure = self._determine_optimal_structure(topic, content_elements, content_analysis)

            # 4. Aggregate evidence with full context understanding
            aggregated_evidence = self._aggregate_evidence_advanced(content_elements, content_analysis)

            # 5. Generate content section by section with comprehensive integration
            chapter_content = {}
            for section in chapter_structure:
                section_content = await self._generate_comprehensive_section(
                    section_name=section,
                    content_elements=content_elements,
                    content_analysis=content_analysis,
                    aggregated_evidence=aggregated_evidence,
                    topic=topic,
                    include_images=include_images
                )
                if section_content:
                    chapter_content[section] = section_content

            # 6. Compile final comprehensive chapter
            compiled_chapter = self._compile_comprehensive_chapter(
                topic=topic,
                content=chapter_content,
                images=self._extract_image_references(content_elements) if include_images else [],
                content_analysis=content_analysis,
                metadata={
                    "total_sources": len(internal_references),
                    "content_elements": len(content_elements),
                    "knowledge_gaps": content_analysis.knowledge_gaps,
                    "contradictions_found": len(content_analysis.contradictions)
                }
            )

            logger.info(f"Successfully completed synthesis for topic: {topic}")
            return compiled_chapter

        except Exception as e:
            logger.error(f"Failed to synthesize chapter for topic {topic}: {e}")
            return None

    async def _extract_content_elements(
        self,
        references: List[Dict[str, Any]],
        include_images: bool
    ) -> List[ContentElement]:
        """
        Extracts all content elements from references including text, tables, and images.
        Implements deep content parsing and understanding.
        """
        content_elements = []

        for ref in references:
            source_title = ref.get('source_title', 'Unknown Source')

            # Extract text content
            if 'content' in ref:
                content_elements.append(ContentElement(
                    type=ContentType.TEXT,
                    content=ref['content'],
                    source=source_title,
                    citation=ref.get('citation', ''),
                    page_number=ref.get('page_number'),
                    metadata=ref.get('metadata', {})
                ))

            # Extract tables
            if 'tables' in ref:
                for table in ref['tables']:
                    content_elements.append(ContentElement(
                        type=ContentType.TABLE,
                        content=json.dumps(table),
                        source=source_title,
                        citation=ref.get('citation', ''),
                        metadata={'table_title': table.get('title', '')}
                    ))

            # Extract images if requested
            if include_images and 'images' in ref:
                for image in ref['images']:
                    content_elements.append(ContentElement(
                        type=ContentType.IMAGE,
                        content=image.get('path', ''),
                        source=source_title,
                        citation=ref.get('citation', ''),
                        metadata={
                            'caption': image.get('caption', ''),
                            'figure_number': image.get('figure_number', ''),
                            'draggable': True  # Enable easy drag-and-drop
                        }
                    ))

            # Extract formulas and diagrams
            if 'formulas' in ref:
                for formula in ref['formulas']:
                    content_elements.append(ContentElement(
                        type=ContentType.FORMULA,
                        content=formula,
                        source=source_title,
                        citation=ref.get('citation', '')
                    ))

        logger.info(f"Extracted {len(content_elements)} content elements from {len(references)} references")
        return content_elements

    async def _analyze_content_relationships(
        self,
        content_elements: List[ContentElement],
        topic: str
    ) -> ContentAnalysis:
        """
        Deeply analyzes relationships between content from different sources.
        Identifies similarities, differences, complementary info, and contradictions.
        """

        # Prepare content for AI analysis
        content_summary = self._prepare_content_for_analysis(content_elements)

        analysis_prompt = f"""
        Analyze the following medical content about '{topic}' from multiple sources.
        Identify and categorize:

        1. SIMILARITIES: Information that appears consistently across sources
        2. DIFFERENCES: Variations in approach, data, or recommendations
        3. COMPLEMENTARY: Information that adds to or extends other sources
        4. CONTRADICTIONS: Conflicting information that needs resolution
        5. UNIQUE INSIGHTS: Information found only in specific sources
        6. KNOWLEDGE GAPS: Missing information that would complete understanding

        Content from sources:
        {content_summary}

        Provide detailed analysis in JSON format.
        """

        try:
            # Handle standalone mode without AI
            if self.standalone_mode:
                logger.info("Running in standalone mode - using basic analysis")
                return self._basic_content_analysis(content_elements)

            analysis_result = await self.hybrid_ai_manager.query(
                "Claude",
                analysis_prompt,
                use_fallback=False
            )

            # Parse and structure the analysis
            return self._parse_content_analysis(analysis_result)

        except Exception as e:
            logger.error(f"Failed to analyze content relationships: {e}")
            # Return basic analysis structure
            return ContentAnalysis(
                similarities=[],
                differences=[],
                complementary_info=[],
                contradictions=[],
                knowledge_gaps=["Full content analysis not available"],
                unique_insights=[]
            )

    def _basic_content_analysis(self, content_elements: List[ContentElement]) -> ContentAnalysis:
        """Basic content analysis for standalone mode without AI"""
        # Group by source to detect overlaps
        sources_content = {}
        for element in content_elements:
            if element.source not in sources_content:
                sources_content[element.source] = []
            if element.type == ContentType.TEXT:
                sources_content[element.source].append(element.content.lower())

        # Simple similarity detection
        similarities = []
        all_text = ' '.join([' '.join(texts) for texts in sources_content.values()])

        # Find common medical terms across sources
        common_terms = ["treatment", "diagnosis", "surgery", "therapy", "management"]
        for term in common_terms:
            if all_text.count(term) > len(sources_content):
                similarities.append({"term": term, "frequency": all_text.count(term)})

        return ContentAnalysis(
            similarities=similarities,
            differences=[],
            complementary_info=[],
            contradictions=[],
            knowledge_gaps=["AI analysis not available in standalone mode"],
            unique_insights=[]
        )

    def _prepare_content_for_analysis(self, content_elements: List[ContentElement]) -> str:
        """Prepares content elements for AI analysis"""
        summary = ""

        # Group by source
        sources = {}
        for element in content_elements:
            if element.source not in sources:
                sources[element.source] = []
            sources[element.source].append(element)

        for source, elements in sources.items():
            summary += f"\n\n=== Source: {source} ===\n"
            for element in elements:
                if element.type == ContentType.TEXT:
                    summary += f"Text: {element.content[:500]}...\n"
                elif element.type == ContentType.TABLE:
                    summary += f"Table: {element.metadata.get('table_title', 'Data table')}\n"
                elif element.type == ContentType.IMAGE:
                    summary += f"Image: {element.metadata.get('caption', 'Medical image')}\n"

        return summary

    def _parse_content_analysis(self, analysis_result: str) -> ContentAnalysis:
        """Parses AI analysis into structured format"""
        try:
            # Attempt to extract JSON from the response
            import json

            # Find JSON in the response
            json_match = re.search(r'\{.*\}', analysis_result, re.DOTALL)
            if json_match:
                analysis_data = json.loads(json_match.group())
            else:
                analysis_data = {}

            return ContentAnalysis(
                similarities=analysis_data.get('similarities', []),
                differences=analysis_data.get('differences', []),
                complementary_info=analysis_data.get('complementary', []),
                contradictions=analysis_data.get('contradictions', []),
                knowledge_gaps=analysis_data.get('knowledge_gaps', []),
                unique_insights=analysis_data.get('unique_insights', [])
            )
        except Exception as e:
            logger.error(f"Failed to parse content analysis: {e}")
            return ContentAnalysis(
                similarities=[], differences=[], complementary_info=[],
                contradictions=[], knowledge_gaps=[], unique_insights=[]
            )

    def _determine_optimal_structure(
        self,
        topic: str,
        content_elements: List[ContentElement],
        content_analysis: ContentAnalysis
    ) -> List[str]:
        """
        Determines optimal chapter structure based on available content.
        Adapts structure to ensure all relevant information is included.
        """

        # Start with comprehensive structure
        base_structure = self._get_comprehensive_structure()

        # Analyze which sections have substantial content
        content_coverage = self._analyze_content_coverage(content_elements)

        # Filter sections based on content availability
        relevant_sections = []
        for section in base_structure:
            # Always include fundamental sections
            if section in ["Introduction", "Conclusion", "References"]:
                relevant_sections.append(section)
            # Include sections with available content
            elif self._has_content_for_section(section, content_coverage):
                relevant_sections.append(section)
            # Add custom sections for unique insights
            elif content_analysis.unique_insights:
                for insight in content_analysis.unique_insights:
                    if self._section_matches_insight(section, insight):
                        relevant_sections.append(section)

        # Add any custom sections based on content analysis
        custom_sections = self._identify_custom_sections(content_analysis, topic)
        for custom_section in custom_sections:
            if custom_section not in relevant_sections:
                # Insert in appropriate position
                relevant_sections.insert(-2, custom_section)  # Before conclusion

        logger.info(f"Determined {len(relevant_sections)} relevant sections for topic: {topic}")
        return relevant_sections

    def _analyze_content_coverage(self, content_elements: List[ContentElement]) -> Dict[str, int]:
        """Analyzes which topics are covered in the content"""
        coverage = {}

        # Keywords for each section
        section_keywords = {
            "Epidemiology": ["incidence", "prevalence", "demographics", "statistics"],
            "Pathophysiology": ["mechanism", "pathogenesis", "molecular", "cellular"],
            "Clinical Presentation": ["symptoms", "signs", "presentation", "clinical"],
            "Imaging": ["MRI", "CT", "X-ray", "ultrasound", "imaging"],
            "Surgical Techniques": ["procedure", "technique", "approach", "surgical"],
            # Add more mappings as needed
        }

        for element in content_elements:
            if element.type == ContentType.TEXT:
                content_lower = element.content.lower()
                for section, keywords in section_keywords.items():
                    for keyword in keywords:
                        if keyword in content_lower:
                            coverage[section] = coverage.get(section, 0) + 1

        return coverage

    def _has_content_for_section(self, section: str, coverage: Dict[str, int]) -> bool:
        """Determines if there's enough content for a section"""
        return coverage.get(section, 0) > 0

    def _section_matches_insight(self, section: str, insight: Dict[str, Any]) -> bool:
        """Checks if a section matches a unique insight"""
        insight_text = str(insight).lower()
        section_lower = section.lower()
        return section_lower in insight_text or any(
            word in insight_text for word in section_lower.split()
        )

    def _identify_custom_sections(
        self,
        content_analysis: ContentAnalysis,
        topic: str
    ) -> List[str]:
        """Identifies custom sections needed based on content analysis"""
        custom_sections = []

        # Add sections for significant contradictions
        if len(content_analysis.contradictions) > 2:
            custom_sections.append("Controversial Aspects and Current Debates")

        # Add sections for unique insights
        if content_analysis.unique_insights:
            for insight in content_analysis.unique_insights:
                if 'novel' in str(insight).lower():
                    custom_sections.append("Novel Approaches and Emerging Techniques")
                    break

        return custom_sections

    def _aggregate_evidence_advanced(
        self,
        content_elements: List[ContentElement],
        content_analysis: ContentAnalysis
    ) -> str:
        """
        Advanced evidence aggregation with deep understanding of relationships.
        Structures evidence to maintain context and relationships.
        """

        evidence_text = "=== AGGREGATED EVIDENCE WITH ANALYSIS ===\n\n"

        # Group content by type and source
        by_source = {}
        for element in content_elements:
            if element.source not in by_source:
                by_source[element.source] = {'text': [], 'tables': [], 'images': []}

            if element.type == ContentType.TEXT:
                by_source[element.source]['text'].append(element)
            elif element.type == ContentType.TABLE:
                by_source[element.source]['tables'].append(element)
            elif element.type == ContentType.IMAGE:
                by_source[element.source]['images'].append(element)

        # Structure evidence by source with relationships noted
        for source, content in by_source.items():
            evidence_text += f"\n### Source: {source}\n"

            # Add text content
            for text_element in content['text']:
                evidence_text += f"\nContent: {text_element.content}\n"
                evidence_text += f"Citation: {text_element.citation}\n"

                # Note relationships
                for similarity in content_analysis.similarities:
                    if source in str(similarity):
                        evidence_text += f"[CONSISTENT WITH OTHER SOURCES]\n"

                for contradiction in content_analysis.contradictions:
                    if source in str(contradiction):
                        evidence_text += f"[CONTRADICTS OTHER SOURCES - NEEDS RECONCILIATION]\n"

            # Add table references
            for table in content['tables']:
                evidence_text += f"\nTable: {table.metadata.get('table_title', 'Data table')}\n"
                evidence_text += f"Data: {table.content}\n"

            # Add image references
            for image in content['images']:
                evidence_text += f"\nImage: {image.metadata.get('caption', '')}\n"
                evidence_text += f"Path: {image.content}\n"
                evidence_text += "[IMAGE AVAILABLE FOR INCLUSION]\n"

        # Add analysis summary
        evidence_text += "\n\n=== CONTENT ANALYSIS SUMMARY ===\n"
        evidence_text += f"Contradictions found: {len(content_analysis.contradictions)}\n"
        evidence_text += f"Knowledge gaps identified: {', '.join(content_analysis.knowledge_gaps)}\n"
        evidence_text += f"Unique insights: {len(content_analysis.unique_insights)}\n"

        return evidence_text

    async def _generate_comprehensive_section(
        self,
        section_name: str,
        content_elements: List[ContentElement],
        content_analysis: ContentAnalysis,
        aggregated_evidence: str,
        topic: str,
        include_images: bool
    ) -> Optional[str]:
        """
        Generates comprehensive section content with all subtleties preserved.
        Integrates all available information seamlessly.
        """

        # Filter relevant content for this section
        section_evidence = self._filter_evidence_for_section(
            section_name,
            content_elements,
            aggregated_evidence
        )

        if not section_evidence and section_name not in ["Introduction", "Conclusion"]:
            return None  # Skip sections without relevant content

        # Identify images for this section
        section_images = []
        if include_images:
            section_images = self._identify_section_images(section_name, content_elements)

        # Generate comprehensive prompt with strict constraints
        prompt = self._create_comprehensive_section_prompt(
            section_name=section_name,
            topic=topic,
            section_evidence=section_evidence,
            content_analysis=content_analysis,
            section_images=section_images
        )

        try:
            # Handle standalone mode
            if self.standalone_mode:
                # Basic section generation without AI
                section_content = self._generate_basic_section(
                    section_name, topic, section_evidence, section_images
                )
            else:
                # Generate section using Claude with strict adherence
                section_content = await self.hybrid_ai_manager.query(
                    "Claude",
                    prompt,
                    use_fallback=False
                )

            # Post-process to ensure all subtleties are included
            section_content = self._post_process_section(
                section_content,
                section_images,
                content_analysis
            )

            return section_content

        except Exception as e:
            logger.error(f"Failed to generate section {section_name}: {e}")

            # Fallback: Return structured gap notification
            if not section_evidence:
                return f"Information regarding {section_name} for {topic} is not available in the internal reference library."
            else:
                return f"Error generating content for {section_name}. Evidence available but synthesis failed."

    def _filter_evidence_for_section(
        self,
        section_name: str,
        content_elements: List[ContentElement],
        aggregated_evidence: str
    ) -> str:
        """Filters evidence relevant to specific section"""

        section_keywords = {
            "Introduction": ["overview", "definition", "background", "introduction"],
            "Epidemiology": ["incidence", "prevalence", "demographics", "statistics", "frequency"],
            "Pathophysiology": ["mechanism", "pathogenesis", "molecular", "cellular", "pathway"],
            "Clinical Presentation": ["symptoms", "signs", "presentation", "clinical", "features"],
            "Diagnosis": ["diagnostic", "criteria", "diagnosis", "workup", "evaluation"],
            "Imaging": ["MRI", "CT", "X-ray", "ultrasound", "imaging", "radiological"],
            "Surgical Anatomy": ["anatomy", "anatomical", "landmarks", "structures", "approach"],
            "Surgical Techniques": ["procedure", "technique", "approach", "surgical", "operation"],
            "Complications": ["complication", "adverse", "risk", "morbidity", "mortality"],
            "Prognosis": ["survival", "outcome", "prognosis", "progression", "recurrence"],
            # Add more as needed
        }

        keywords = section_keywords.get(section_name, [section_name.lower()])

        filtered_evidence = ""
        for element in content_elements:
            if element.type == ContentType.TEXT:
                content_lower = element.content.lower()
                if any(keyword in content_lower for keyword in keywords):
                    filtered_evidence += f"\nSource: {element.source}\n"
                    filtered_evidence += f"Content: {element.content}\n"
                    filtered_evidence += f"Citation: {element.citation}\n\n"

        return filtered_evidence if filtered_evidence else ""

    def _generate_basic_section(
        self,
        section_name: str,
        topic: str,
        evidence: str,
        images: List[ContentElement]
    ) -> str:
        """Generate basic section content without AI for standalone mode"""
        content = f"## {section_name}\n\n"

        if evidence:
            # Extract and format the evidence
            lines = evidence.split('\n')
            current_source = None
            for line in lines:
                if line.startswith('Source:'):
                    current_source = line.replace('Source:', '').strip()
                elif line.startswith('Content:'):
                    text = line.replace('Content:', '').strip()
                    if text:
                        content += f"{text}\n\n"
                        if current_source:
                            content += f"*Source: {current_source}*\n\n"
        else:
            content += f"Information regarding {section_name} for {topic} is not available in the internal reference library.\n"

        # Add image references
        if images:
            content += "\n### Related Images\n"
            for img in images:
                caption = img.metadata.get('caption', 'Medical image')
                content += f"- [Image: {caption}]\n"

        return content

    def _identify_section_images(
        self,
        section_name: str,
        content_elements: List[ContentElement]
    ) -> List[ContentElement]:
        """Identifies images relevant to specific section"""

        section_images = []

        # Keywords for image relevance
        image_keywords = {
            "Surgical Anatomy": ["anatomy", "anatomical", "structure"],
            "Imaging": ["MRI", "CT", "scan", "radiograph"],
            "Surgical Techniques": ["procedure", "technique", "step", "approach"],
            "Pathology": ["histology", "microscopy", "specimen"]
        }

        keywords = image_keywords.get(section_name, [])

        for element in content_elements:
            if element.type == ContentType.IMAGE:
                caption = element.metadata.get('caption', '').lower()
                if any(keyword in caption for keyword in keywords):
                    section_images.append(element)

        return section_images

    def _create_comprehensive_section_prompt(
        self,
        section_name: str,
        topic: str,
        section_evidence: str,
        content_analysis: ContentAnalysis,
        section_images: List[ContentElement]
    ) -> str:
        """Creates comprehensive prompt for section generation"""

        prompt = f"""
        TASK: Generate the '{section_name}' section for a comprehensive neurosurgical chapter on '{topic}'.

        CRITICAL REQUIREMENTS:
        1. MUST synthesize ALL information provided in the evidence below
        2. MUST preserve ALL subtleties and detailed information
        3. MUST integrate information from multiple sources seamlessly
        4. MUST explicitly note any contradictions found between sources
        5. MUST include citations for all statements
        6. If evidence is insufficient, state: "Additional information regarding [specific aspect] is not available in the internal reference library."

        SYNTHESIS GUIDELINES:
        - Combine similar information from multiple sources into coherent paragraphs
        - Preserve unique details from each source
        - When sources disagree, present both perspectives with citations
        - Include all relevant statistics, measurements, and specific data
        - Maintain medical accuracy and professional terminology
        """

        # Add specific contradictions to address
        if content_analysis.contradictions:
            prompt += "\n\nCONTRADICTIONS TO ADDRESS:\n"
            for contradiction in content_analysis.contradictions[:3]:  # Limit to top 3
                prompt += f"- {contradiction}\n"

        # Add evidence
        prompt += f"\n\nEVIDENCE TO SYNTHESIZE:\n{section_evidence}"

        # Note available images
        if section_images:
            prompt += "\n\nIMAGES AVAILABLE FOR THIS SECTION:\n"
            for img in section_images:
                prompt += f"- {img.metadata.get('caption', 'Medical image')} [{img.citation}]\n"
            prompt += "Note: Reference these images where appropriate using [Image: caption]"

        prompt += "\n\nGenerate comprehensive, well-structured content that includes ALL provided information:"

        return prompt

    def _post_process_section(
        self,
        section_content: str,
        section_images: List[ContentElement],
        content_analysis: ContentAnalysis
    ) -> str:
        """Post-processes section to ensure completeness"""

        # Add image placeholders if not already included
        if section_images and "[Image:" not in section_content:
            image_refs = "\n\n**Relevant Images:**\n"
            for img in section_images:
                caption = img.metadata.get('caption', 'Medical image')
                image_refs += f"- [Image: {caption}] - {img.citation}\n"
            section_content += image_refs

        # Add contradiction notes if significant
        if len(content_analysis.contradictions) > 0 and "Note:" not in section_content:
            section_content += "\n\n*Note: Some variations exist in the literature regarding specific aspects of this topic.*"

        return section_content


    def _extract_image_references(self, content_elements: List[ContentElement]) -> List[Dict[str, Any]]:
        """Extracts all image references for the chapter"""

        images = []
        for element in content_elements:
            if element.type == ContentType.IMAGE:
                images.append({
                    'path': element.content,
                    'caption': element.metadata.get('caption', ''),
                    'source': element.source,
                    'citation': element.citation,
                    'draggable': True,
                    'figure_number': element.metadata.get('figure_number', '')
                })

        return images

    def _compile_comprehensive_chapter(
        self,
        topic: str,
        content: Dict[str, str],
        images: List[Dict[str, Any]],
        content_analysis: ContentAnalysis,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compiles all components into final comprehensive chapter"""

        return {
            "topic": topic,
            "content": content,
            "images": images,
            "analysis": {
                "contradictions": content_analysis.contradictions,
                "knowledge_gaps": content_analysis.knowledge_gaps,
                "unique_insights": content_analysis.unique_insights
            },
            "metadata": metadata,
            "status": "DRAFT_INTERNAL_COMPREHENSIVE",
            "synthesis_complete": True,
            "ready_for_enrichment": len(content_analysis.knowledge_gaps) > 0,
            "ready_for_summary": True  # Flag for separate summary service
        }


class ImageExtractor:
    """Handles extraction and management of images from PDFs and other sources"""

    def __init__(self, output_dir: Path = Path("extracted_images")):
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True)

    async def extract_images_from_pdf(
        self,
        pdf_path: str,
        topic_keywords: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Extracts relevant images from PDF based on topic keywords.
        Makes images easily draggable for manual insertion.
        """

        images = []

        try:
            # This would integrate with PDF extraction library
            # For now, returning structure
            logger.info(f"Extracting images from {pdf_path} for keywords: {topic_keywords}")

            # Example structure for extracted images
            images.append({
                'path': str(self.output_dir / f"{topic_keywords[0]}_anatomy.png"),
                'caption': f"Anatomical illustration relevant to {topic_keywords[0]}",
                'page_number': 42,
                'confidence': 0.95,
                'draggable': True
            })

        except Exception as e:
            logger.error(f"Failed to extract images: {e}")

        return images

    def prepare_images_for_drag_drop(self, images: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepares images for easy drag-and-drop into documents"""

        for image in images:
            # Ensure absolute path for easy access
            if 'path' in image:
                image['absolute_path'] = str(Path(image['path']).absolute())
                image['relative_path'] = image['path']
                image['draggable'] = True

                # Add HTML snippet for easy insertion
                caption = image.get('caption', '')
                image['html_snippet'] = f'<figure><img src="{image["path"]}" alt="{caption}"><figcaption>{caption}</figcaption></figure>'

        return images


# Integration with existing system
class SynthesizerServiceAdapter:
    """Adapter to integrate enhanced synthesizer with existing system"""

    def __init__(self, enhanced_engine: EnhancedSynthesisEngine):
        self.engine = enhanced_engine

    async def synthesize_chapter(
        self,
        topic: str,
        internal_refs: List[Dict[str, Any]],
        options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Adapter method for existing API"""

        options = options or {}

        return await self.engine.synthesize_initial_chapter(
            topic=topic,
            internal_references=internal_refs,
            include_images=options.get('include_images', True)
        )