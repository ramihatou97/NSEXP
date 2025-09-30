"""
Example Usage - Integrated Reference Search & Synthesis System
Shows how to use the integrated system for various scenarios
"""

import asyncio
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def example_basic_synthesis():
    """
    Example 1: Basic chapter synthesis from library
    """
    from reference_search_bridge import create_integrated_system

    # Initialize the integrated system
    system = create_integrated_system(
        database_url="postgresql://user:pass@localhost/medical_db",
        textbooks_path="/path/to/textbooks",
        ai_config={
            "claude_api_key": "your-key",
            "gpt4_api_key": "your-key"
        }
    )

    # Generate a complete chapter on a topic
    chapter = await system.generate_chapter(
        topic="Glioblastoma Multiforme",
        options={
            "specialty": "neurosurgery",
            "max_sources": 15,
            "include_images": True
        }
    )

    # Access the synthesized content
    print(f"Chapter Status: {chapter['status']}")
    print(f"Sources Used: {chapter['search_metadata']['sources_used']}")

    # Print each section
    for section_name, content in chapter['content'].items():
        print(f"\n=== {section_name} ===")
        print(content[:500] + "...")  # Preview first 500 chars


async def example_search_then_select():
    """
    Example 2: Search first, then manually select references for synthesis
    """
    from reference_search_bridge import IntegratedReferenceSystem
    from reference_library import ReferenceLibraryService
    from hybrid_ai_manager import HybridAIManager

    # Initialize components
    library = ReferenceLibraryService()
    ai_manager = HybridAIManager(claude_api_key="your-key")
    system = IntegratedReferenceSystem(library, ai_manager)

    # Step 1: Search for references
    search_results = await system.search_references(
        query="cerebral aneurysm clipping",
        limit=20
    )

    # Step 2: Display results for user selection
    print("Found References:")
    for i, ref in enumerate(search_results):
        print(f"{i+1}. {ref['title']} ({ref['textbook']}) - Relevance: {ref['relevance']:.2f}")

    # Step 3: Simulate user selection (in real app, this would be interactive)
    selected_indices = [0, 2, 4, 7]  # User selects these references
    selected_ids = [search_results[i]['id'] for i in selected_indices]

    # Step 4: Synthesize with selected references
    chapter = await system.synthesize_from_selected(
        topic="Cerebral Aneurysm Clipping Technique",
        chapter_ids=selected_ids
    )

    print(f"\nSynthesized chapter using {len(selected_ids)} selected references")


async def example_multi_topic_batch():
    """
    Example 3: Batch process multiple topics
    """
    from reference_search_bridge import create_integrated_system

    system = create_integrated_system(
        database_url="postgresql://user:pass@localhost/medical_db",
        textbooks_path="/path/to/textbooks",
        ai_config={"claude_api_key": "your-key"}
    )

    # List of topics to process
    topics = [
        "Acoustic Neuroma",
        "Pituitary Adenoma",
        "Meningioma",
        "Hydrocephalus",
        "Spinal Stenosis"
    ]

    # Process all topics in parallel
    tasks = []
    for topic in topics:
        tasks.append(system.generate_chapter(topic))

    # Wait for all to complete
    chapters = await asyncio.gather(*tasks, return_exceptions=True)

    # Report results
    for topic, chapter in zip(topics, chapters):
        if isinstance(chapter, dict):
            status = chapter.get('status', 'UNKNOWN')
            sources = chapter.get('search_metadata', {}).get('sources_used', 0)
            print(f"{topic}: {status} ({sources} sources)")
        else:
            print(f"{topic}: ERROR - {chapter}")


async def example_progressive_enrichment():
    """
    Example 4: Progressive enrichment - Start with internal, then add external
    """
    from reference_search_bridge import IntegratedReferenceSystem
    from reference_library import ReferenceLibraryService
    from enhanced_synthesizer_service import EnhancedSynthesisEngine
    from hybrid_ai_manager import HybridAIManager

    # Initialize
    library = ReferenceLibraryService()
    ai_manager = HybridAIManager(claude_api_key="your-key")
    synthesizer = EnhancedSynthesisEngine(ai_manager)
    system = IntegratedReferenceSystem(library, ai_manager)

    topic = "Deep Brain Stimulation"

    # Step 1: Initial synthesis from internal library
    logger.info(f"Step 1: Synthesizing from internal library...")
    initial_chapter = await system.generate_chapter(topic)

    # Step 2: Identify knowledge gaps
    knowledge_gaps = initial_chapter.get('analysis', {}).get('knowledge_gaps', [])
    print(f"Knowledge gaps identified: {knowledge_gaps}")

    # Step 3: If gaps exist, enrich with external sources (future integration)
    if knowledge_gaps:
        logger.info("Step 2: Enriching with external sources...")
        # This would integrate with external search services
        # For now, we'll just note the gaps
        enriched_chapter = initial_chapter
        enriched_chapter['metadata']['enrichment_needed'] = True
        enriched_chapter['metadata']['gaps_to_fill'] = knowledge_gaps

    print(f"Chapter ready with {len(knowledge_gaps)} areas for potential enrichment")


async def example_quality_filtering():
    """
    Example 5: Synthesis with quality thresholds
    """
    from reference_search_bridge import ReferenceSearchBridge, SearchConfig
    from reference_library import ReferenceLibraryService
    from enhanced_synthesizer_service import EnhancedSynthesisEngine
    from hybrid_ai_manager import HybridAIManager

    # Initialize with custom config
    library = ReferenceLibraryService()
    ai_manager = HybridAIManager(claude_api_key="your-key")
    synthesizer = EnhancedSynthesisEngine(ai_manager)

    # Create bridge with custom config
    bridge = ReferenceSearchBridge(library, synthesizer)
    bridge.config = SearchConfig(
        max_results=30,
        min_relevance_score=0.7,  # Higher threshold
        include_images=True,
        include_tables=True
    )

    # Synthesize with quality filtering
    high_quality_chapter = await bridge.synthesize_from_library(
        topic="Microsurgical Techniques",
        specialty="neurosurgery",
        max_sources=10  # Will be filtered by relevance score
    )

    sources_found = high_quality_chapter['search_metadata']['total_sources_found']
    sources_used = high_quality_chapter['search_metadata']['sources_used']

    print(f"Found {sources_found} sources, used {sources_used} after quality filtering")


async def example_monitoring_and_stats():
    """
    Example 6: Monitor system performance and statistics
    """
    from reference_search_bridge import create_integrated_system
    import time

    system = create_integrated_system(
        database_url="postgresql://user:pass@localhost/medical_db",
        textbooks_path="/path/to/textbooks",
        ai_config={"claude_api_key": "your-key"}
    )

    # Get system statistics
    stats = await system.get_system_stats()
    print("System Statistics:")
    print(f"- Total Textbooks: {stats['total_textbooks']}")
    print(f"- Total Chapters: {stats['total_chapters']}")
    print(f"- Indexed Content: {stats['indexed_content_gb']} GB")
    print(f"- Search Index Size: {stats['search_index_size']} entries")
    print(f"- Extraction Quality: {stats['extraction_quality']:.2%}")

    # Measure synthesis performance
    start_time = time.time()

    chapter = await system.generate_chapter("Brain Tumor Classification")

    end_time = time.time()
    synthesis_time = end_time - start_time

    print(f"\nSynthesis Performance:")
    print(f"- Time taken: {synthesis_time:.2f} seconds")
    print(f"- Sources processed: {chapter['search_metadata']['sources_used']}")
    print(f"- Sections generated: {len(chapter['content'])}")
    print(f"- Performance: {len(chapter['content']) / synthesis_time:.2f} sections/second")


# Main execution
async def main():
    """Run examples"""
    print("=" * 60)
    print("INTEGRATED REFERENCE SEARCH & SYNTHESIS SYSTEM")
    print("=" * 60)

    # Choose which example to run
    examples = {
        "1": ("Basic Synthesis", example_basic_synthesis),
        "2": ("Search and Select", example_search_then_select),
        "3": ("Batch Processing", example_multi_topic_batch),
        "4": ("Progressive Enrichment", example_progressive_enrichment),
        "5": ("Quality Filtering", example_quality_filtering),
        "6": ("System Monitoring", example_monitoring_and_stats)
    }

    print("\nAvailable Examples:")
    for key, (name, _) in examples.items():
        print(f"{key}. {name}")

    # For demonstration, run example 1
    print("\nRunning Example 1: Basic Synthesis")
    print("-" * 40)

    try:
        await example_basic_synthesis()
    except Exception as e:
        logger.error(f"Example failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())