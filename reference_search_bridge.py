"""
Reference Search Bridge - Clean Integration Layer
Connects PDF Library System to Enhanced Synthesizer Service
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class SearchConfig:
    """Configuration for reference search"""
    max_results: int = 20
    min_relevance_score: float = 0.3
    include_images: bool = True
    include_tables: bool = True
    chunk_overlap: int = 200  # For context preservation


class ReferenceSearchBridge:
    """
    Bridge between PDF Library System and Enhanced Synthesizer.
    Handles search, retrieval, and format conversion.
    """

    def __init__(self, reference_library_service, synthesizer_engine):
        self.library = reference_library_service
        self.synthesizer = synthesizer_engine
        self.config = SearchConfig()

    async def synthesize_from_library(
        self,
        topic: str,
        specialty: Optional[str] = "neurosurgery",
        max_sources: int = 20
    ) -> Dict[str, Any]:
        """
        Main pipeline: Search library → Format references → Synthesize chapter

        Args:
            topic: The medical topic to synthesize
            specialty: Medical specialty for focused search
            max_sources: Maximum number of reference sources to use

        Returns:
            Complete synthesized chapter with all content
        """
        try:
            # Step 1: Search the reference library
            logger.info(f"Searching library for topic: {topic}")
            search_results = await self.library.search_chapters(
                query=topic,
                specialty=specialty,
                limit=max_sources
            )

            if not search_results:
                logger.warning(f"No references found for topic: {topic}")
                return {
                    "topic": topic,
                    "content": {"Introduction": f"No internal references found for {topic}."},
                    "status": "NO_REFERENCES",
                    "metadata": {"search_query": topic, "sources_found": 0}
                }

            logger.info(f"Found {len(search_results)} relevant references")

            # Step 2: Convert search results to synthesizer format
            internal_references = await self._convert_to_synthesizer_format(
                search_results
            )

            # Step 3: Filter by relevance score
            filtered_references = self._filter_by_relevance(
                internal_references,
                min_score=self.config.min_relevance_score
            )

            logger.info(f"Using {len(filtered_references)} references after filtering")

            # Step 4: Synthesize the chapter
            synthesized_chapter = await self.synthesizer.synthesize_initial_chapter(
                topic=topic,
                internal_references=filtered_references,
                include_images=self.config.include_images
            )

            # Step 5: Add search metadata
            if synthesized_chapter:
                synthesized_chapter['search_metadata'] = {
                    'total_sources_found': len(search_results),
                    'sources_used': len(filtered_references),
                    'specialty': specialty,
                    'search_query': topic
                }

            return synthesized_chapter

        except Exception as e:
            logger.error(f"Failed to synthesize from library: {e}")
            return {
                "topic": topic,
                "content": {"Error": str(e)},
                "status": "ERROR",
                "metadata": {"error": str(e)}
            }

    async def _convert_to_synthesizer_format(
        self,
        search_results: List[Any]
    ) -> List[Dict[str, Any]]:
        """
        Converts PDF library search results to synthesizer's expected format.
        Handles async retrieval of full chapter content.
        """
        internal_references = []

        # Process results in parallel for speed
        tasks = []
        for result in search_results:
            tasks.append(self._process_single_result(result))

        # Gather all results
        processed_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out any failed retrievals
        for ref in processed_results:
            if isinstance(ref, dict) and ref.get('content'):
                internal_references.append(ref)
            elif isinstance(ref, Exception):
                logger.error(f"Failed to process reference: {ref}")

        return internal_references

    async def _process_single_result(self, result) -> Dict[str, Any]:
        """
        Process a single search result into synthesizer format.
        Retrieves full content and extracts all necessary elements.
        """
        try:
            # Get full chapter content from database
            chapter = await self.library.get_chapter_by_id(result.chapter_id)

            if not chapter:
                logger.warning(f"Chapter not found: {result.chapter_id}")
                return {}

            # Build reference in synthesizer's expected format
            reference = {
                'source_title': f"{result.textbook_title} - Chapter {chapter.chapter_number}: {chapter.title}",
                'content': chapter.content_text or result.text_chunk,  # Fallback to chunk if full content not available
                'citation': self._format_citation(result, chapter),
                'page_number': result.chunk_position // 3000 if hasattr(result, 'chunk_position') else None,
                'metadata': {
                    'chapter_id': str(chapter.id),
                    'textbook_id': str(chapter.textbook_id),
                    'relevance_score': getattr(result, 'relevance_score', 1.0),
                    'medical_terms': chapter.medical_terms or [],
                    'keywords': chapter.keywords or [],
                    'word_count': chapter.word_count,
                    'quality_score': chapter.complexity_score
                }
            }

            # Add tables if available and requested
            if self.config.include_tables:
                tables = await self._extract_tables_from_chapter(chapter)
                if tables:
                    reference['tables'] = tables

            # Add images if available and requested
            if self.config.include_images:
                images = await self._extract_images_from_chapter(chapter)
                if images:
                    reference['images'] = images

            # Add any extracted citations
            if hasattr(chapter, 'citations') and chapter.citations:
                reference['extracted_citations'] = chapter.citations

            return reference

        except Exception as e:
            logger.error(f"Error processing result {result.chapter_id}: {e}")
            return {}

    def _format_citation(self, result, chapter) -> str:
        """Create proper citation format"""
        authors = getattr(chapter, 'authors', ['Unknown'])
        year = getattr(chapter, 'publication_year', 'n.d.')

        # Format: Authors (Year). Chapter Title. In: Textbook Title, pp. X-Y
        citation = f"{', '.join(authors[:3])} ({year}). "
        citation += f"{chapter.title}. "
        citation += f"In: {result.textbook_title}"

        if hasattr(chapter, 'page_range'):
            citation += f", pp. {chapter.page_range}"

        return citation

    async def _extract_tables_from_chapter(self, chapter) -> List[Dict[str, Any]]:
        """Extract structured table data from chapter"""
        tables = []

        # If tables are already extracted and stored
        if hasattr(chapter, 'tables') and chapter.tables:
            return chapter.tables

        # Otherwise, attempt extraction from content
        if chapter.content_text:
            # Simple table detection (can be enhanced)
            table_markers = ['Table', 'TABLE', '|---|', '┌─', '╔═']

            for marker in table_markers:
                if marker in chapter.content_text:
                    # Extract table region (simplified - enhance as needed)
                    tables.append({
                        'title': f"Table from {chapter.title}",
                        'data': self._parse_table_region(chapter.content_text, marker),
                        'type': 'extracted'
                    })

        return tables

    async def _extract_images_from_chapter(self, chapter) -> List[Dict[str, Any]]:
        """Extract image references from chapter"""
        images = []

        # If images are already extracted
        if hasattr(chapter, 'figures') and chapter.figures:
            for fig in chapter.figures:
                images.append({
                    'path': fig.get('path', ''),
                    'caption': fig.get('caption', f'Figure from {chapter.title}'),
                    'figure_number': fig.get('number', ''),
                    'type': fig.get('type', 'diagram')
                })

        # Check if PDF has embedded images
        if chapter.file_path:
            pdf_path = Path(chapter.file_path)
            if pdf_path.exists():
                # Reference to image extraction location
                image_dir = pdf_path.parent / 'extracted_images' / pdf_path.stem
                if image_dir.exists():
                    for img_file in image_dir.glob('*.png'):
                        images.append({
                            'path': str(img_file),
                            'caption': f'Image from {chapter.title}',
                            'figure_number': img_file.stem
                        })

        return images

    def _filter_by_relevance(
        self,
        references: List[Dict[str, Any]],
        min_score: float = 0.3
    ) -> List[Dict[str, Any]]:
        """Filter references by relevance score and quality"""

        filtered = []
        for ref in references:
            relevance = ref.get('metadata', {}).get('relevance_score', 0)
            quality = ref.get('metadata', {}).get('quality_score', 0)

            # Combined score considering both relevance and quality
            combined_score = (relevance * 0.7) + (quality * 0.3 if quality else relevance)

            if combined_score >= min_score:
                # Add combined score for later sorting
                ref['metadata']['combined_score'] = combined_score
                filtered.append(ref)

        # Sort by combined score (best first)
        filtered.sort(key=lambda x: x['metadata']['combined_score'], reverse=True)

        return filtered

    def _parse_table_region(self, content: str, marker: str, max_lines: int = 50) -> str:
        """Extract table region from content (simplified parser)"""
        lines = content.split('\n')
        table_lines = []
        in_table = False

        for i, line in enumerate(lines):
            if marker in line and not in_table:
                in_table = True
                table_lines.append(line)
            elif in_table:
                # Simple heuristic: tables often have consistent formatting
                if '|' in line or '│' in line or line.strip().startswith(tuple('0123456789')):
                    table_lines.append(line)
                elif len(table_lines) > 2 and line.strip() == '':
                    # Empty line might signal end of table
                    break
                elif len(table_lines) > max_lines:
                    break
                else:
                    table_lines.append(line)

        return '\n'.join(table_lines)


class IntegratedReferenceSystem:
    """
    High-level API for the integrated reference and synthesis system.
    Provides simple interface for external systems.
    """

    def __init__(self, library_service, ai_manager, pdf_extractor=None, external_searcher=None):
        from enhanced_synthesizer_service import EnhancedSynthesisEngine

        self.library = library_service
        self.synthesizer = EnhancedSynthesisEngine(ai_manager, pdf_extractor)
        self.bridge = ReferenceSearchBridge(self.library, self.synthesizer)
        self.external_searcher = external_searcher  # Optional external AI searcher

    async def generate_chapter(
        self,
        topic: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Simple API to generate a complete chapter from library references.

        Args:
            topic: Medical topic to research and synthesize
            options: Optional configuration (specialty, max_sources, include_images, etc.)

        Returns:
            Complete synthesized chapter
        """
        options = options or {}

        return await self.bridge.synthesize_from_library(
            topic=topic,
            specialty=options.get('specialty', 'neurosurgery'),
            max_sources=options.get('max_sources', 20)
        )

    async def search_references(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search references without synthesis.
        Useful for preview or manual selection.
        """
        results = await self.library.search_chapters(
            query=query,
            limit=limit
        )

        # Convert to simplified format
        return [
            {
                'id': str(r.chapter_id),
                'title': r.title,
                'textbook': r.textbook_title,
                'relevance': r.relevance_score,
                'preview': r.text_chunk[:500] if hasattr(r, 'text_chunk') else ''
            }
            for r in results
        ]

    async def synthesize_from_selected(
        self,
        topic: str,
        chapter_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Synthesize using manually selected chapters.
        Gives user control over which references to use.
        """
        # Retrieve selected chapters
        references = []
        for chapter_id in chapter_ids:
            chapter = await self.library.get_chapter_by_id(chapter_id)
            if chapter:
                # Convert to synthesizer format
                result = await self.bridge._process_single_result(
                    type('Result', (), {'chapter_id': chapter_id, 'textbook_title': 'Selected'})()
                )
                if result:
                    references.append(result)

        # Synthesize with selected references
        return await self.synthesizer.synthesize_initial_chapter(
            topic=topic,
            internal_references=references,
            include_images=True
        )

    async def get_system_stats(self) -> Dict[str, Any]:
        """Get statistics about the reference library"""
        stats = await self.library.get_statistics()
        return {
            'total_textbooks': stats.textbooks_found,
            'total_chapters': stats.chapters_processed,
            'indexed_content_gb': stats.total_content_size_gb,
            'search_index_size': stats.index_entry_count,
            'extraction_quality': stats.average_extraction_accuracy
        }

    async def enrich_chapter(
        self,
        chapter: Dict[str, Any],
        service: str = "gemini",
        auto_confirm: bool = False
    ) -> Dict[str, Any]:
        """
        Enrich chapter by filling knowledge gaps with external AI search.
        This is manually triggered after initial internal synthesis.

        Args:
            chapter: Initial chapter generated from internal library
            service: External AI service to use (gemini, claude, perplexity)
            auto_confirm: If False, asks user to confirm each gap

        Returns:
            Enriched chapter with filled knowledge gaps
        """

        if not self.external_searcher:
            logger.warning("External searcher not configured. Cannot enrich chapter.")
            return chapter

        # Check for knowledge gaps
        knowledge_gaps = chapter.get('analysis', {}).get('knowledge_gaps', [])

        if not knowledge_gaps:
            logger.info("No knowledge gaps identified. Chapter does not need enrichment.")
            return chapter

        logger.info(f"Found {len(knowledge_gaps)} knowledge gaps to fill")

        # Show gaps to user
        print("\n" + "="*60)
        print("KNOWLEDGE GAPS IDENTIFIED")
        print("="*60)
        for i, gap in enumerate(knowledge_gaps, 1):
            print(f"{i}. {gap}")

        # Ask user to confirm enrichment
        if not auto_confirm:
            print("\nEnrich chapter with external AI search?")
            response = input("Enter 'yes' to proceed, or 'no' to skip: ").strip().lower()
            if response != 'yes':
                logger.info("User declined enrichment")
                return chapter

        # Enrich each gap
        topic = chapter.get('topic', 'Unknown')
        enrichment_results = await self.external_searcher.enrich_knowledge_gaps(
            topic=topic,
            knowledge_gaps=knowledge_gaps,
            service=service
        )

        # Integrate enrichment into chapter
        enriched_chapter = chapter.copy()

        # Add enrichment section
        enrichment_content = self._format_enrichment_content(enrichment_results)

        # Create new section for external information
        if 'content' in enriched_chapter:
            enriched_chapter['content']['External Knowledge (AI Enrichment)'] = enrichment_content

        # Update metadata
        enriched_chapter['metadata']['enriched'] = True
        enriched_chapter['metadata']['enrichment_source'] = service
        enriched_chapter['metadata']['gaps_filled'] = len([r for r in enrichment_results.values() if r])
        enriched_chapter['metadata']['enrichment_timestamp'] = datetime.now().isoformat()

        # Clear ready_for_enrichment flag
        enriched_chapter['ready_for_enrichment'] = False

        logger.info(f"✅ Chapter enrichment complete. Filled {enriched_chapter['metadata']['gaps_filled']} gaps.")

        return enriched_chapter

    async def merge_with_nuance_engine(
        self,
        internal_chapter: Dict[str, Any],
        enriched_chapter: Dict[str, Any],
        auto_merge_threshold: float = 0.85
    ) -> Dict[str, Any]:
        """
        Merge internal chapter with enriched external content using NuanceMergeEngine.
        This performs intelligent, nuanced merging with Claude assistance.

        Args:
            internal_chapter: Original chapter from internal sources
            enriched_chapter: Chapter with external enrichment added
            auto_merge_threshold: Confidence threshold for auto-merging (default 0.85)

        Returns:
            Merged comprehensive chapter with seamlessly integrated knowledge
        """

        from nuance_merge_engine import NuanceMergeEngine

        logger.info("🧬 Starting nuanced merge with AI-powered analysis...")

        # Create merge engine with AI manager
        merge_engine = NuanceMergeEngine(ai_manager=self.bridge.synthesizer.ai_manager)

        # Perform intelligent merge
        merged_chapter = await merge_engine.merge_chapters(
            internal_chapter=internal_chapter,
            external_enrichment=enriched_chapter,
            specialty="neurosurgery",
            auto_apply_threshold=auto_merge_threshold
        )

        logger.info("✅ Nuanced merge complete")

        return merged_chapter

    def _format_enrichment_content(self, enrichment_results: Dict[str, Any]) -> str:
        """Format enrichment results into readable content"""

        content = "## External AI-Sourced Information\n\n"
        content += "*This section contains information gathered from external AI sources to address knowledge gaps identified in the internal reference library.*\n\n"

        for gap, result in enrichment_results.items():
            if result:
                content += f"### {gap}\n\n"
                content += f"{result.response}\n\n"
                content += f"*Source: {result.source} ({result.method}) - {result.timestamp.strftime('%Y-%m-%d %H:%M')}*\n\n"
                content += "---\n\n"
            else:
                content += f"### {gap}\n\n"
                content += "*Unable to retrieve information for this topic.*\n\n"
                content += "---\n\n"

        return content


# Utility function for quick setup
def create_integrated_system(
    database_url: str,
    textbooks_path: str,
    ai_config: Dict[str, Any]
) -> IntegratedReferenceSystem:
    """
    Factory function to create a fully configured integrated system.

    Args:
        database_url: PostgreSQL connection string
        textbooks_path: Path to PDF textbooks directory
        ai_config: Configuration for AI services

    Returns:
        Ready-to-use IntegratedReferenceSystem
    """
    # Import required services
    from reference_library import ReferenceLibraryService
    from hybrid_ai_manager import HybridAIManager

    # Initialize services
    library_service = ReferenceLibraryService()
    library_service.textbooks_root = Path(textbooks_path)

    ai_manager = HybridAIManager(**ai_config)

    # Create integrated system
    return IntegratedReferenceSystem(
        library_service=library_service,
        ai_manager=ai_manager,
        pdf_extractor=None  # Optional PDF extractor
    )