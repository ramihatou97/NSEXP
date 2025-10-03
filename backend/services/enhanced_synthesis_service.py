"""
Enhanced Synthesis Service for Comprehensive Neurosurgical Chapter Generation
Implements advanced synthesis with multi-reference integration and evidence-based structure
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from services.ai_manager import ai_manager
from services.pdf_service import PDFProcessor

logger = logging.getLogger(__name__)


class EnhancedSynthesisService:
    """
    Advanced synthesis service for generating comprehensive neurosurgical chapters
    Handles multi-reference synthesis with evidence-based content organization
    """
    
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.comprehensive_structure = self._get_comprehensive_chapter_structure()
    
    def _get_comprehensive_chapter_structure(self) -> List[str]:
        """
        Returns comprehensive chapter structure for neurosurgical topics
        Based on major neurosurgical textbooks and peer-reviewed standards
        """
        return [
            # Foundational Content
            "Title and Overview",
            "Executive Summary",
            "Key Points (Quick Reference)",
            "Learning Objectives",
            
            # Epidemiology and Background
            "Introduction",
            "Historical Perspective",
            "Epidemiology",
            "Incidence and Prevalence",
            "Risk Factors",
            "Demographics",
            
            # Pathophysiology
            "Pathophysiology",
            "Molecular Biology",
            "Genetics and Hereditary Factors",
            "Cellular Mechanisms",
            "Biochemical Pathways",
            
            # Classification
            "Classification Systems",
            "WHO Classification (if applicable)",
            "Grading Systems",
            "Staging Criteria",
            
            # Clinical Presentation
            "Clinical Presentation",
            "Signs and Symptoms",
            "Natural History",
            "Disease Progression",
            "Physical Examination Findings",
            "Neurological Examination",
            
            # Diagnosis
            "Differential Diagnosis",
            "Diagnostic Criteria",
            "Diagnostic Workup",
            "Laboratory Studies",
            "Biomarkers",
            
            # Imaging
            "Imaging",
            "Computed Tomography (CT)",
            "Magnetic Resonance Imaging (MRI)",
            "Advanced Imaging Techniques",
            "Functional Imaging",
            "Angiography",
            "Nuclear Medicine Studies",
            "Imaging Protocol Recommendations",
            
            # Anatomy
            "Relevant Anatomy",
            "Surgical Anatomy",
            "Anatomical Landmarks",
            "Vascular Anatomy",
            "Neural Structures",
            "Anatomical Variations",
            
            # Treatment Options
            "Treatment Overview",
            "Treatment Algorithms",
            "Conservative Management",
            "Medical Management",
            "Pharmacological Therapy",
            
            # Surgical Treatment
            "Surgical Indications",
            "Contraindications",
            "Preoperative Assessment",
            "Preoperative Planning",
            "Patient Selection Criteria",
            "Risk Stratification",
            
            # Surgical Techniques
            "Surgical Approaches",
            "Patient Positioning",
            "Anesthesia Considerations",
            "Step-by-Step Surgical Procedure",
            "Surgical Technique Variations",
            "Technical Pearls and Pitfalls",
            "Intraoperative Monitoring",
            "Neuromonitoring",
            "Intraoperative Imaging",
            "Microsurgical Techniques",
            "Endoscopic Techniques",
            "Minimally Invasive Approaches",
            
            # Perioperative Care
            "Postoperative Management",
            "Immediate Postoperative Care",
            "ICU Management",
            "Pain Management",
            "Wound Care",
            "Rehabilitation",
            
            # Complications
            "Complications",
            "Intraoperative Complications",
            "Early Postoperative Complications",
            "Late Complications",
            "Complication Prevention Strategies",
            "Complication Management",
            
            # Adjuvant Therapy
            "Adjuvant Therapy",
            "Radiation Therapy",
            "Chemotherapy",
            "Targeted Therapy",
            "Immunotherapy",
            "Emerging Therapies",
            
            # Pathology
            "Pathology",
            "Gross Pathology",
            "Histopathological Features",
            "Immunohistochemistry",
            "Molecular Markers",
            "Genetic Testing",
            
            # Outcomes
            "Outcomes",
            "Surgical Outcomes",
            "Functional Outcomes",
            "Quality of Life",
            "Survival Statistics",
            "Prognostic Factors",
            "Progression Patterns",
            
            # Follow-up
            "Follow-up Protocol",
            "Surveillance Imaging",
            "Long-term Monitoring",
            "Recurrence Detection",
            "Recurrence Management",
            
            # Special Considerations
            "Special Populations",
            "Pediatric Considerations",
            "Geriatric Considerations",
            "Pregnancy Considerations",
            
            # Evidence and Guidelines
            "Evidence-Based Recommendations",
            "Clinical Practice Guidelines",
            "Level of Evidence Summary",
            "Controversial Topics",
            "Areas of Ongoing Research",
            
            # Future Directions
            "Recent Advances",
            "Current Clinical Trials",
            "Future Directions",
            "Emerging Technologies",
            
            # Summary
            "Summary and Conclusions",
            "Key Takeaways",
            "Clinical Pearls",
            "Practice Points",
            
            # References
            "References",
            "Suggested Reading",
            "Online Resources"
        ]
    
    async def synthesize_comprehensive_chapter(
        self,
        topic: str,
        specialty: str,
        references: List[Dict[str, Any]],
        focus_areas: Optional[List[str]] = None,
        include_images: bool = True,
        evidence_level: str = "all"
    ) -> Dict[str, Any]:
        """
        Synthesize a comprehensive neurosurgical chapter from multiple references
        
        Args:
            topic: Chapter topic (e.g., "Glioblastoma Multiforme")
            specialty: Neurosurgical specialty
            references: List of reference materials
            focus_areas: Specific sections to emphasize
            include_images: Whether to include image references
            evidence_level: Filter by evidence level (I-V or "all")
            
        Returns:
            Comprehensive synthesized chapter with all sections
        """
        logger.info(f"Starting comprehensive synthesis for: {topic}")
        
        try:
            # Prepare reference content
            reference_content = await self._prepare_reference_content(references)
            
            # Determine which sections to generate
            sections_to_generate = self._determine_relevant_sections(
                topic,
                specialty,
                focus_areas
            )
            
            # Generate each section
            chapter_sections = {}
            for section in sections_to_generate:
                logger.info(f"Generating section: {section}")
                
                section_content = await self._synthesize_section(
                    topic=topic,
                    section=section,
                    references=reference_content,
                    specialty=specialty
                )
                
                if section_content:
                    chapter_sections[section] = section_content
            
            # Extract and organize images if requested
            image_references = []
            if include_images:
                image_references = await self._extract_image_references(references)
            
            # Generate citations
            citations = self._generate_citations(references)
            
            # Calculate quality metrics
            quality_metrics = self._calculate_quality_metrics(
                chapter_sections,
                references,
                image_references
            )
            
            return {
                "success": True,
                "topic": topic,
                "specialty": specialty,
                "sections": chapter_sections,
                "section_count": len(chapter_sections),
                "total_words": sum(len(content.split()) for content in chapter_sections.values()),
                "references": citations,
                "reference_count": len(references),
                "images": image_references,
                "image_count": len(image_references),
                "quality_metrics": quality_metrics,
                "evidence_level": evidence_level,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Comprehensive synthesis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "topic": topic
            }
    
    def _determine_relevant_sections(
        self,
        topic: str,
        specialty: str,
        focus_areas: Optional[List[str]] = None
    ) -> List[str]:
        """
        Determine which sections are relevant for the given topic
        """
        # Start with all sections
        relevant_sections = self.comprehensive_structure.copy()
        
        # Filter based on topic type
        topic_lower = topic.lower()
        
        # Remove pediatric section if not relevant
        if "pediatric" not in topic_lower and "child" not in topic_lower:
            relevant_sections = [s for s in relevant_sections if "Pediatric" not in s]
        
        # Prioritize focus areas if specified
        if focus_areas:
            # Move focus sections to the top
            prioritized = []
            for section in relevant_sections:
                if any(focus in section.lower() for focus in [f.lower() for f in focus_areas]):
                    prioritized.insert(0, section)
                else:
                    prioritized.append(section)
            relevant_sections = prioritized
        
        return relevant_sections
    
    async def _prepare_reference_content(
        self,
        references: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Prepare and organize reference content for synthesis
        """
        organized_content = {
            "full_text": [],
            "abstracts": [],
            "key_findings": [],
            "citations": []
        }
        
        for ref in references:
            # Extract full text if available
            if ref.get("content"):
                organized_content["full_text"].append({
                    "title": ref.get("title", ""),
                    "content": ref["content"][:5000],  # Limit to prevent token overflow
                    "authors": ref.get("authors", []),
                    "year": ref.get("year", "")
                })
            
            # Extract abstract
            if ref.get("abstract"):
                organized_content["abstracts"].append({
                    "title": ref.get("title", ""),
                    "abstract": ref["abstract"]
                })
            
            # Build citation
            organized_content["citations"].append({
                "title": ref.get("title", ""),
                "authors": ref.get("authors", []),
                "year": ref.get("year", ""),
                "journal": ref.get("journal", ""),
                "doi": ref.get("doi", "")
            })
        
        return organized_content
    
    async def _synthesize_section(
        self,
        topic: str,
        section: str,
        references: Dict[str, Any],
        specialty: str
    ) -> Optional[str]:
        """
        Synthesize a single chapter section using AI
        """
        try:
            # Create section-specific prompt
            prompt = self._create_section_prompt(
                topic, section, references, specialty
            )
            
            # Generate content using AI manager
            response = await ai_manager.synthesize_chapter_section(
                section_name=section,
                references=[str(ref) for ref in references.get("full_text", [])[:5]],
                specialty=specialty
            )
            
            if response:
                return response
            
            return None
            
        except Exception as e:
            logger.error(f"Section synthesis failed for {section}: {e}")
            return None
    
    def _create_section_prompt(
        self,
        topic: str,
        section: str,
        references: Dict[str, Any],
        specialty: str
    ) -> str:
        """
        Create a detailed prompt for section synthesis
        """
        refs_text = "\n".join([
            f"- {ref['title']} ({ref.get('year', 'N/A')})"
            for ref in references.get("full_text", [])[:5]
        ])
        
        prompt = f"""Generate the "{section}" section for a comprehensive neurosurgical chapter on: {topic}

Specialty: {specialty}

Available References:
{refs_text}

Requirements:
1. Base content on provided references
2. Include specific surgical details when applicable
3. Cite evidence appropriately
4. Use clear, academic medical writing
5. Include clinical pearls when relevant
6. Maintain scientific accuracy
7. Address current best practices
8. Include anatomical details for surgical sections

Generate a thorough, evidence-based section suitable for a medical textbook."""
        
        return prompt
    
    async def _extract_image_references(
        self,
        references: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Extract image references from source materials
        """
        images = []
        
        for ref in references:
            if ref.get("images"):
                for img in ref["images"]:
                    images.append({
                        "source": ref.get("title", ""),
                        "caption": img.get("caption", ""),
                        "page": img.get("page", ""),
                        "type": img.get("type", "figure")
                    })
        
        return images
    
    def _generate_citations(
        self,
        references: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Generate formatted citations for references
        """
        citations = []
        
        for i, ref in enumerate(references, 1):
            authors = ref.get("authors", [])
            author_str = ", ".join(authors[:3])
            if len(authors) > 3:
                author_str += " et al."
            
            citation = f"{i}. {author_str} ({ref.get('year', 'n.d.')}). {ref.get('title', '')}. "
            
            if ref.get("journal"):
                citation += f"{ref['journal']}. "
            
            if ref.get("doi"):
                citation += f"DOI: {ref['doi']}"
            
            citations.append(citation)
        
        return citations
    
    def _calculate_quality_metrics(
        self,
        sections: Dict[str, str],
        references: List[Dict[str, Any]],
        images: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate quality metrics for the synthesized chapter
        """
        total_words = sum(len(content.split()) for content in sections.values())
        
        return {
            "completeness_score": len(sections) / len(self.comprehensive_structure),
            "total_words": total_words,
            "average_section_length": total_words // len(sections) if sections else 0,
            "reference_density": len(references) / max(total_words // 500, 1),
            "has_images": len(images) > 0,
            "image_count": len(images),
            "estimated_reading_time_minutes": total_words // 200
        }
    
    async def generate_summary(
        self,
        chapter_content: Dict[str, Any],
        summary_type: str = "executive"
    ) -> Dict[str, Any]:
        """
        Generate different types of summaries from chapter content
        
        Args:
            chapter_content: Full chapter content
            summary_type: Type of summary (executive, detailed, technical, bullet_points)
            
        Returns:
            Generated summary
        """
        try:
            sections = chapter_content.get("sections", {})
            
            # Combine key sections for summarization
            content_to_summarize = ""
            key_sections = [
                "Introduction", "Clinical Presentation", "Diagnosis",
                "Treatment Overview", "Surgical Techniques", "Outcomes",
                "Summary and Conclusions"
            ]
            
            for section in key_sections:
                if section in sections:
                    content_to_summarize += f"\n\n{section}:\n{sections[section][:1000]}"
            
            # Create summary prompt based on type
            if summary_type == "executive":
                prompt = f"""Generate a concise executive summary (200-300 words) of this neurosurgical chapter:

{content_to_summarize}

Focus on: key clinical points, treatment approach, and outcomes."""
            
            elif summary_type == "bullet_points":
                prompt = f"""Generate 10-15 key bullet points summarizing this neurosurgical chapter:

{content_to_summarize}

Format as clear, actionable bullet points."""
            
            elif summary_type == "technical":
                prompt = f"""Generate a technical summary (400-500 words) emphasizing surgical techniques and clinical details:

{content_to_summarize}"""
            
            else:  # detailed
                prompt = f"""Generate a detailed summary (600-800 words) covering all major aspects:

{content_to_summarize}"""
            
            # Generate summary using AI
            summary = await ai_manager.generate_neurosurgical_content(
                prompt=prompt,
                specialty=chapter_content.get("specialty", "neurosurgery"),
                max_tokens=1000
            )
            
            return {
                "success": True,
                "summary_type": summary_type,
                "summary": summary.content if hasattr(summary, 'content') else str(summary),
                "word_count": len(summary.content.split()) if hasattr(summary, 'content') else 0
            }
            
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Global instance
enhanced_synthesis_service = EnhancedSynthesisService()
