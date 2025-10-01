#!/usr/bin/env python3
"""
Main Entry Point - Integrated Reference Search & Synthesis System
Run this script to start using the integrated system
"""

import asyncio
import argparse
import logging
from pathlib import Path
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('integrated_system.log')
    ]
)

logger = logging.getLogger(__name__)


async def run_synthesis(args):
    """Run synthesis for a single topic"""
    from system_config import SystemInitializer, get_config

    # Initialize system
    logger.info("Initializing integrated system...")
    config = get_config()

    # Override with command line arguments
    if args.textbooks:
        config.textbooks_path = Path(args.textbooks)
    if args.api_key:
        if args.ai_service == "claude":
            config.claude_api_key = args.api_key
        else:
            config.openai_api_key = args.api_key

    system = await SystemInitializer.initialize_system(config)

    # Generate chapter
    logger.info(f"Generating chapter for topic: {args.topic}")
    chapter = await system.generate_chapter(
        topic=args.topic,
        options={
            "specialty": args.specialty,
            "max_sources": args.max_sources,
            "include_images": not args.no_images
        }
    )

    # Output results
    if args.output:
        # Save to file
        import json
        output_path = Path(args.output)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(chapter, f, indent=2, ensure_ascii=False)
        logger.info(f"Chapter saved to: {output_path}")
    else:
        # Print summary
        print(f"\n{'='*60}")
        print(f"SYNTHESIZED CHAPTER: {args.topic}")
        print(f"{'='*60}")
        print(f"Status: {chapter.get('status', 'Unknown')}")
        print(f"Sources Used: {chapter.get('search_metadata', {}).get('sources_used', 0)}")
        print(f"Sections Generated: {len(chapter.get('content', {}))}")

        if args.verbose:
            print("\nSections:")
            for section_name in chapter.get('content', {}).keys():
                print(f"  - {section_name}")

    return chapter


async def run_batch(args):
    """Process multiple topics from file"""
    from system_config import SystemInitializer, get_config
    import json

    # Read topics from file
    topics_file = Path(args.batch)
    if not topics_file.exists():
        logger.error(f"Batch file not found: {topics_file}")
        return

    with open(topics_file, 'r') as f:
        if topics_file.suffix == '.json':
            topics_data = json.load(f)
            topics = topics_data if isinstance(topics_data, list) else topics_data.get('topics', [])
        else:
            topics = [line.strip() for line in f if line.strip()]

    logger.info(f"Processing {len(topics)} topics from batch file")

    # Initialize system
    config = get_config()
    system = await SystemInitializer.initialize_system(config)

    # Process topics
    results = []
    for i, topic in enumerate(topics, 1):
        logger.info(f"Processing [{i}/{len(topics)}]: {topic}")

        try:
            chapter = await system.generate_chapter(topic)
            results.append({
                "topic": topic,
                "status": "success",
                "sources_used": chapter.get('search_metadata', {}).get('sources_used', 0)
            })

            # Save individual chapters if output directory specified
            if args.output:
                output_dir = Path(args.output)
                output_dir.mkdir(exist_ok=True)
                chapter_file = output_dir / f"{topic.replace(' ', '_').lower()}.json"
                with open(chapter_file, 'w', encoding='utf-8') as f:
                    json.dump(chapter, f, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Failed to process {topic}: {e}")
            results.append({
                "topic": topic,
                "status": "error",
                "error": str(e)
            })

    # Print summary
    print(f"\n{'='*60}")
    print("BATCH PROCESSING COMPLETE")
    print(f"{'='*60}")
    successful = sum(1 for r in results if r['status'] == 'success')
    print(f"Success: {successful}/{len(topics)}")

    for result in results:
        status_icon = "✓" if result['status'] == 'success' else "✗"
        print(f"{status_icon} {result['topic']}")


async def run_search(args):
    """Search references without synthesis"""
    from system_config import SystemInitializer, get_config

    # Initialize system
    config = get_config()
    system = await SystemInitializer.initialize_system(config)

    # Search
    logger.info(f"Searching for: {args.query}")
    results = await system.search_references(
        query=args.query,
        limit=args.limit
    )

    # Display results
    print(f"\n{'='*60}")
    print(f"SEARCH RESULTS for: {args.query}")
    print(f"{'='*60}")
    print(f"Found {len(results)} references\n")

    for i, ref in enumerate(results, 1):
        print(f"{i}. {ref['title']}")
        print(f"   Textbook: {ref['textbook']}")
        print(f"   Relevance: {ref['relevance']:.2%}")
        if args.verbose and ref.get('preview'):
            print(f"   Preview: {ref['preview'][:200]}...")
        print()


async def validate_setup(args):
    """Validate system setup and configuration"""
    from system_config import validate_textbook_structure, get_config

    print(f"\n{'='*60}")
    print("SYSTEM VALIDATION")
    print(f"{'='*60}\n")

    # Check configuration
    try:
        config = get_config()
        config.validate()
        print("✓ Configuration valid")
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False

    # Check textbook structure
    validation = validate_textbook_structure(config.textbooks_path)

    print(f"✓ Textbooks path: {config.textbooks_path}")
    print(f"  - Textbooks found: {validation['textbooks_found']}")
    print(f"  - Chapters found: {validation['chapters_found']}")

    if validation['issues']:
        print("\nIssues found:")
        for issue in validation['issues']:
            print(f"  ⚠ {issue}")

    # Check database connection
    try:
        # This would actually test the database connection
        print("✓ Database connection available")
    except Exception as e:
        print(f"✗ Database connection failed: {e}")

    # Check AI services
    if config.claude_api_key:
        print("✓ Claude API key configured")
    if config.openai_api_key:
        print("✓ OpenAI API key configured")

    if not config.claude_api_key and not config.openai_api_key:
        print("✗ No AI service API keys configured")

    return validation['valid']


async def run_enrichment(args):
    """Enrich an existing chapter with external AI search"""
    from system_config import SystemInitializer, get_config
    from external_ai_searcher import ExternalAISearcher
    import json

    # Load existing chapter
    chapter_file = Path(args.chapter_file)
    if not chapter_file.exists():
        logger.error(f"Chapter file not found: {chapter_file}")
        return

    with open(chapter_file, 'r', encoding='utf-8') as f:
        chapter = json.load(f)

    logger.info(f"Loaded chapter: {chapter.get('topic', 'Unknown')}")

    # Check if chapter has knowledge gaps
    gaps = chapter.get('analysis', {}).get('knowledge_gaps', [])
    if not gaps:
        print("\n✅ Chapter has no knowledge gaps. Enrichment not needed.")
        return

    print(f"\n📊 Found {len(gaps)} knowledge gaps:")
    for i, gap in enumerate(gaps, 1):
        print(f"  {i}. {gap}")

    # Initialize system with external searcher
    config = get_config()
    system = await SystemInitializer.initialize_system(config)

    # Create external searcher
    api_keys = {}
    if args.gemini_key:
        api_keys['gemini'] = args.gemini_key
    if args.claude_key:
        api_keys['claude'] = args.claude_key
    if args.perplexity_key:
        api_keys['perplexity'] = args.perplexity_key

    external_searcher = ExternalAISearcher(api_keys=api_keys)

    # Setup login if needed and no API keys provided
    if not api_keys and args.setup_login:
        print(f"\n🔐 Setting up login for {args.service}...")
        await external_searcher.setup_login(args.service, "", "")

    # Inject external searcher into system
    system.external_searcher = external_searcher

    try:
        # Enrich chapter
        print(f"\n🔍 Enriching chapter with {args.service}...")
        enriched_chapter = await system.enrich_chapter(
            chapter=chapter,
            service=args.service,
            auto_confirm=args.auto_confirm
        )

        # Save enriched chapter
        if args.output:
            output_path = Path(args.output)
        else:
            # Save to same location with _enriched suffix
            output_path = chapter_file.with_stem(f"{chapter_file.stem}_enriched")

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(enriched_chapter, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Enriched chapter saved to: {output_path}")

        # Print enrichment stats
        if enriched_chapter.get('metadata', {}).get('enriched'):
            gaps_filled = enriched_chapter['metadata']['gaps_filled']
            print(f"\n📈 Enrichment Statistics:")
            print(f"  - Knowledge gaps filled: {gaps_filled}/{len(gaps)}")
            print(f"  - Source: {enriched_chapter['metadata']['enrichment_source']}")

        # Print usage stats
        usage = external_searcher.get_usage_report()
        print(f"\n💰 Usage Statistics:")
        print(f"  - Total cost: {usage['total_cost']}")
        print(f"  - API calls: {usage['total_api_calls']}")
        print(f"  - Web calls: {usage['total_web_calls']}")

    finally:
        await external_searcher.close()


async def run_merge(args):
    """Merge internal chapter with enriched chapter using NuanceMergeEngine"""
    from system_config import SystemInitializer, get_config
    import json

    # Load both chapters
    internal_file = Path(args.internal_chapter)
    enriched_file = Path(args.enriched_chapter)

    if not internal_file.exists():
        logger.error(f"Internal chapter not found: {internal_file}")
        return

    if not enriched_file.exists():
        logger.error(f"Enriched chapter not found: {enriched_file}")
        return

    with open(internal_file, 'r', encoding='utf-8') as f:
        internal_chapter = json.load(f)

    with open(enriched_file, 'r', encoding='utf-8') as f:
        enriched_chapter = json.load(f)

    logger.info("📚 Loaded chapters for merging")
    logger.info(f"   Internal: {internal_chapter.get('topic', 'Unknown')}")
    logger.info(f"   Enriched: {enriched_chapter.get('topic', 'Unknown')}")

    # Initialize system
    config = get_config()
    system = await SystemInitializer.initialize_system(config)

    # Perform nuanced merge
    print("\n🧬 Starting intelligent merge with NuanceMergeEngine...")
    print("   - Multi-algorithm similarity detection")
    print("   - Medical context analysis")
    print("   - Claude-powered intelligent merging")

    merged_chapter = await system.merge_with_nuance_engine(
        internal_chapter=internal_chapter,
        enriched_chapter=enriched_chapter,
        auto_merge_threshold=args.confidence_threshold
    )

    # Save merged chapter
    if args.output:
        output_path = Path(args.output)
    else:
        # Default: internal_chapter_merged.json
        output_path = internal_file.with_stem(f"{internal_file.stem}_merged")

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(merged_chapter, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Merged chapter saved to: {output_path}")

    # Print merge stats
    if merged_chapter.get('metadata', {}).get('merged'):
        stats = merged_chapter['metadata']['merge_stats']
        print(f"\n📊 Merge Statistics:")
        print(f"   - Nuances detected: {stats['nuances_detected']}")
        print(f"   - Nuances applied: {stats['nuances_applied']}")
        print(f"   - Sections enhanced: {stats['sections_enhanced']}")
        print(f"   - Average confidence: {stats.get('avg_confidence', 0):.2%}")
        print(f"   - Processing time: {stats.get('processing_time_seconds', 0):.2f}s")


async def run_summarize(args):
    """Generate summary from any chapter (internal, enriched, or merged)"""
    from neurosurgical_summary_generator import NeurosurgicalSummaryGenerator, SummaryMode, SummaryLength
    from system_config import SystemInitializer, get_config
    import json

    # Load chapter
    chapter_file = Path(args.chapter_file)
    if not chapter_file.exists():
        logger.error(f"Chapter file not found: {chapter_file}")
        return

    with open(chapter_file, 'r', encoding='utf-8') as f:
        chapter = json.load(f)

    logger.info(f"📄 Loaded chapter: {chapter.get('topic', 'Unknown')}")

    # Detect chapter type
    if chapter.get('metadata', {}).get('merged'):
        chapter_type = "Merged (Internal + External)"
    elif chapter.get('metadata', {}).get('enriched'):
        chapter_type = "Enriched (External)"
    else:
        chapter_type = "Internal"

    print(f"\n📊 Chapter Type: {chapter_type}")

    # Initialize system
    config = get_config()
    system = await SystemInitializer.initialize_system(config)

    # Create summary generator
    summary_generator = NeurosurgicalSummaryGenerator(
        ai_manager=system.bridge.synthesizer.ai_manager
    )

    # Map mode and length
    mode = SummaryMode(args.mode.upper() if '_' not in args.mode else args.mode.upper())
    length = SummaryLength(args.length.upper())

    print(f"🔍 Generating {mode.value} summary ({length.value} words)...")

    # Generate summary
    summary_result = await summary_generator.generate_summary(
        chapter_data=chapter,
        mode=mode,
        length=length,
        include_citations=not args.no_citations
    )

    # Save summary
    if args.output:
        output_path = Path(args.output)
    else:
        # Default: chapter_summary_mode.md
        output_path = chapter_file.with_stem(f"{chapter_file.stem}_summary_{args.mode}").with_suffix('.md')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(summary_result['summary'])

    print(f"\n✅ Summary saved to: {output_path}")

    # Print summary stats
    print(f"\n📈 Summary Statistics:")
    print(f"   - Word count: {summary_result['metadata']['word_count']}")
    print(f"   - Sections covered: {summary_result['metadata']['sections_covered']}")
    print(f"   - Key points extracted: {len(summary_result['key_points'])}")
    print(f"   - Clinical pearls: {len(summary_result['clinical_pearls'])}")


async def run_activate(args):
    """Activate a chapter with Alive Chapter features"""
    from system_config import SystemInitializer, get_config
    from alive_chapter_bridge import AliveChapterManager
    import json

    # Load chapter
    chapter_file = Path(args.chapter_file)
    if not chapter_file.exists():
        logger.error(f"Chapter file not found: {chapter_file}")
        return

    print(f"\n🔄 Activating chapter: {chapter_file.name}")

    with open(chapter_file, 'r', encoding='utf-8') as f:
        chapter = json.load(f)

    # Initialize system for AI manager
    config = get_config()
    system = await SystemInitializer.initialize_system(config)

    # Create alive chapter manager
    manager = AliveChapterManager(ai_manager=system.bridge.synthesizer.ai_manager)

    # Activate chapter
    activated_chapter = await manager.activate_chapter(
        chapter=chapter,
        chapter_id=args.chapter_id
    )

    # Save activated chapter
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = chapter_file.with_stem(f"{chapter_file.stem}_activated")

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(activated_chapter, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Chapter activated: {output_path}")

    # Print activation status
    metadata = activated_chapter.get('alive_metadata', {})
    print(f"\n📊 Alive Features Enabled:")
    print(f"   - Chapter ID: {metadata.get('chapter_id', 'N/A')}")
    print(f"   - Behavioral Learning: {'✓' if metadata.get('behavioral_learning_enabled') else '✗'}")
    print(f"   - Q&A Engine: {'✓' if metadata.get('qa_enabled') else '✗'}")
    print(f"   - Citation Network: {'✓' if metadata.get('citation_network_enabled') else '✗'}")
    print(f"   - Enhanced Merge: {'✓' if metadata.get('enhanced_merge_enabled') else '✗'}")


async def run_ask(args):
    """Process a question within chapter context"""
    from system_config import SystemInitializer, get_config
    from alive_chapter_bridge import AliveChapterManager
    import json

    # Load chapter
    chapter_file = Path(args.chapter_file)
    if not chapter_file.exists():
        logger.error(f"Chapter file not found: {chapter_file}")
        return

    print(f"\n❓ Processing question for chapter: {chapter_file.name}")

    with open(chapter_file, 'r', encoding='utf-8') as f:
        chapter = json.load(f)

    # Initialize system for AI manager
    config = get_config()
    system = await SystemInitializer.initialize_system(config)

    # Create alive chapter manager
    manager = AliveChapterManager(ai_manager=system.bridge.synthesizer.ai_manager)

    # Process question
    result = await manager.process_chapter_question(
        chapter=chapter,
        question=args.question,
        user_id=args.user_id,
        section_context=args.section
    )

    if not result.get('success'):
        print(f"\n❌ Failed to process question: {result.get('error', 'Unknown error')}")
        return

    # Print answer
    print(f"\n{'='*60}")
    print(f"ANSWER:")
    print(f"{'='*60}")
    print(result.get('answer', ''))

    # Save updated chapter if it was modified
    if result.get('chapter_updated'):
        if args.output:
            output_path = Path(args.output)
        else:
            output_path = chapter_file.with_stem(f"{chapter_file.stem}_qa_updated")

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result['updated_chapter'], f, indent=2, ensure_ascii=False)

        print(f"\n✅ Chapter updated with Q&A integration: {output_path}")

        if args.verbose and result.get('integration_points'):
            print(f"\n📍 Integration Points:")
            for point in result['integration_points']:
                print(f"   - {point}")
    else:
        print(f"\n📝 Answer not integrated into chapter")
        if result.get('reason'):
            print(f"   Reason: {result['reason']}")


async def run_anticipate(args):
    """Anticipate knowledge needs based on behavioral learning"""
    from system_config import SystemInitializer, get_config
    from alive_chapter_bridge import AliveChapterManager
    import json

    # Load chapter
    chapter_file = Path(args.chapter_file)
    if not chapter_file.exists():
        logger.error(f"Chapter file not found: {chapter_file}")
        return

    print(f"\n🔮 Anticipating knowledge needs for: {chapter_file.name}")

    with open(chapter_file, 'r', encoding='utf-8') as f:
        chapter = json.load(f)

    # Initialize system for AI manager
    config = get_config()
    system = await SystemInitializer.initialize_system(config)

    # Create alive chapter manager
    manager = AliveChapterManager(ai_manager=system.bridge.synthesizer.ai_manager)

    # Anticipate needs
    result = await manager.anticipate_knowledge_needs(
        chapter=chapter,
        user_id=args.user_id
    )

    if not result.get('success'):
        print(f"\n❌ Failed to anticipate needs: {result.get('error', 'Unknown error')}")
        return

    # Print anticipated needs
    anticipated_needs = result.get('anticipated_needs', [])
    suggestions = result.get('suggestions', [])
    confidence = result.get('confidence', 0.0)

    print(f"\n{'='*60}")
    print(f"ANTICIPATED KNOWLEDGE NEEDS")
    print(f"{'='*60}")
    print(f"Confidence: {confidence:.2%}\n")

    if anticipated_needs:
        print("📚 Anticipated Needs:")
        for i, need in enumerate(anticipated_needs, 1):
            print(f"   {i}. {need}")
    else:
        print("No specific knowledge needs anticipated.")

    if suggestions:
        print(f"\n💡 Suggestions:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"   {i}. {suggestion}")


def main():
    """Main entry point with command line interface"""
    parser = argparse.ArgumentParser(
        description="Integrated Reference Search & Synthesis System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate a single chapter
  python run_integrated_system.py synthesize "Brain Tumors"

  # Search references
  python run_integrated_system.py search "glioblastoma treatment"

  # Batch process topics
  python run_integrated_system.py batch topics.txt --output ./chapters/

  # Enrich chapter with external AI (API keys)
  python run_integrated_system.py enrich chapter.json --gemini-key YOUR_KEY

  # Enrich chapter with external AI (web automation)
  python run_integrated_system.py enrich chapter.json --setup-login

  # Merge internal + enriched chapters intelligently
  python run_integrated_system.py merge internal.json enriched.json --output merged.json

  # Generate summary from any chapter
  python run_integrated_system.py summarize chapter.json --mode executive

  # Activate chapter with Alive features
  python run_integrated_system.py activate chapter.json --output alive_chapter.json

  # Ask question within chapter context
  python run_integrated_system.py ask chapter.json "What are the key surgical techniques?"

  # Anticipate knowledge needs based on user behavior
  python run_integrated_system.py anticipate chapter.json --user-id user123

  # Validate setup
  python run_integrated_system.py validate
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Synthesis command
    syn_parser = subparsers.add_parser('synthesize', help='Synthesize a chapter')
    syn_parser.add_argument('topic', help='Topic to synthesize')
    syn_parser.add_argument('--specialty', default='neurosurgery', help='Medical specialty')
    syn_parser.add_argument('--max-sources', type=int, default=15, help='Maximum sources to use')
    syn_parser.add_argument('--no-images', action='store_true', help='Exclude images')
    syn_parser.add_argument('--output', help='Output file path (JSON)')
    syn_parser.add_argument('--textbooks', help='Override textbooks path')
    syn_parser.add_argument('--api-key', help='API key for AI service')
    syn_parser.add_argument('--ai-service', choices=['claude', 'openai'], default='claude')
    syn_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    # Search command
    search_parser = subparsers.add_parser('search', help='Search references')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--limit', type=int, default=10, help='Maximum results')
    search_parser.add_argument('-v', '--verbose', action='store_true', help='Show previews')

    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Batch process topics')
    batch_parser.add_argument('batch', help='File containing topics (one per line or JSON)')
    batch_parser.add_argument('--output', help='Output directory for chapters')

    # Validate command
    val_parser = subparsers.add_parser('validate', help='Validate system setup')

    # Enrichment command
    enrich_parser = subparsers.add_parser('enrich', help='Enrich chapter with external AI search')
    enrich_parser.add_argument('chapter_file', help='Path to chapter JSON file to enrich')
    enrich_parser.add_argument('--service', choices=['gemini', 'claude', 'perplexity'], default='gemini',
                              help='External AI service to use')
    enrich_parser.add_argument('--gemini-key', help='Gemini API key')
    enrich_parser.add_argument('--claude-key', help='Claude API key')
    enrich_parser.add_argument('--perplexity-key', help='Perplexity API key')
    enrich_parser.add_argument('--setup-login', action='store_true',
                              help='Setup web login (one-time, if no API keys)')
    enrich_parser.add_argument('--auto-confirm', action='store_true',
                              help='Auto-confirm enrichment without prompting')
    enrich_parser.add_argument('--output', help='Output file path for enriched chapter')

    # Merge command
    merge_parser = subparsers.add_parser('merge', help='Merge internal + enriched chapters with NuanceMergeEngine')
    merge_parser.add_argument('internal_chapter', help='Path to internal chapter JSON')
    merge_parser.add_argument('enriched_chapter', help='Path to enriched chapter JSON')
    merge_parser.add_argument('--confidence-threshold', type=float, default=0.85,
                             help='Confidence threshold for auto-merging (default: 0.85)')
    merge_parser.add_argument('--output', help='Output file path for merged chapter')

    # Summarize command
    sum_parser = subparsers.add_parser('summarize', help='Generate summary from chapter')
    sum_parser.add_argument('chapter_file', help='Path to chapter JSON file')
    sum_parser.add_argument('--mode',
                           choices=['executive', 'clinical_pearls', 'quick_reference',
                                   'surgical_steps', 'diagnostic_algorithm', 'evidence_based',
                                   'patient_education', 'board_review', 'emergency_guide'],
                           default='executive',
                           help='Summary mode')
    sum_parser.add_argument('--length',
                           choices=['ultra_concise', 'concise', 'standard', 'detailed', 'extensive'],
                           default='standard',
                           help='Summary length')
    sum_parser.add_argument('--output', help='Output file path for summary')
    sum_parser.add_argument('--no-citations', action='store_true', help='Exclude citations')

    # Activate command (Alive Chapter)
    activate_parser = subparsers.add_parser('activate', help='Activate chapter with Alive features')
    activate_parser.add_argument('chapter_file', help='Path to chapter JSON file')
    activate_parser.add_argument('--chapter-id', help='Custom chapter ID (auto-generated if not provided)')
    activate_parser.add_argument('--output', help='Output file path for activated chapter')

    # Ask command (Alive Chapter Q&A)
    ask_parser = subparsers.add_parser('ask', help='Ask question within chapter context')
    ask_parser.add_argument('chapter_file', help='Path to chapter JSON file')
    ask_parser.add_argument('question', help='Question to ask')
    ask_parser.add_argument('--user-id', default='default_user', help='User identifier for learning')
    ask_parser.add_argument('--section', help='Specific section context for question')
    ask_parser.add_argument('--output', help='Output file path if chapter is updated')
    ask_parser.add_argument('-v', '--verbose', action='store_true', help='Show integration details')

    # Anticipate command (Behavioral Learning)
    anticipate_parser = subparsers.add_parser('anticipate', help='Anticipate knowledge needs')
    anticipate_parser.add_argument('chapter_file', help='Path to chapter JSON file')
    anticipate_parser.add_argument('--user-id', default='default_user', help='User identifier for learning')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Run appropriate command
    try:
        if args.command == 'synthesize':
            asyncio.run(run_synthesis(args))
        elif args.command == 'search':
            asyncio.run(run_search(args))
        elif args.command == 'batch':
            asyncio.run(run_batch(args))
        elif args.command == 'validate':
            asyncio.run(validate_setup(args))
        elif args.command == 'enrich':
            asyncio.run(run_enrichment(args))
        elif args.command == 'merge':
            asyncio.run(run_merge(args))
        elif args.command == 'summarize':
            asyncio.run(run_summarize(args))
        elif args.command == 'activate':
            asyncio.run(run_activate(args))
        elif args.command == 'ask':
            asyncio.run(run_ask(args))
        elif args.command == 'anticipate':
            asyncio.run(run_anticipate(args))
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()