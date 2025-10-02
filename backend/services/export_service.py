"""
Export Service - Handle exporting chapters in various formats
Supports JSON, Markdown, PDF, HTML, and DOCX
"""

import json
from typing import Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


async def export_chapter_content(chapter_id: str, format: str = "json") -> Dict[str, Any]:
    """
    Export chapter in specified format

    Args:
        chapter_id: Chapter ID to export
        format: Export format (json, markdown, pdf, html, docx)

    Returns:
        Dictionary containing export data and metadata
    """
    try:
        # Import here to avoid circular imports
        from services.chapter_service import get_chapter_by_id

        # Get chapter data
        chapter_response = await get_chapter_by_id(chapter_id)

        if not chapter_response.get("success"):
            return {
                "success": False,
                "error": "Chapter not found"
            }

        chapter = chapter_response.get("data")

        # Export based on format
        if format.lower() == "json":
            return export_as_json(chapter)
        elif format.lower() == "markdown" or format.lower() == "md":
            return export_as_markdown(chapter)
        elif format.lower() == "html":
            return export_as_html(chapter)
        elif format.lower() == "pdf":
            return export_as_pdf(chapter)
        elif format.lower() == "docx":
            return export_as_docx(chapter)
        else:
            return {
                "success": False,
                "error": f"Unsupported format: {format}"
            }

    except Exception as e:
        logger.error(f"Export failed for chapter {chapter_id}: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def export_as_json(chapter: Dict[str, Any]) -> Dict[str, Any]:
    """Export chapter as JSON"""
    try:
        content = json.dumps(chapter, indent=2, ensure_ascii=False)

        return {
            "success": True,
            "format": "json",
            "content": content,
            "filename": f"{chapter.get('title', 'chapter').replace(' ', '_').lower()}.json",
            "mime_type": "application/json"
        }
    except Exception as e:
        logger.error(f"JSON export failed: {e}")
        return {"success": False, "error": str(e)}


def export_as_markdown(chapter: Dict[str, Any]) -> Dict[str, Any]:
    """Export chapter as Markdown"""
    try:
        lines = []

        # Title
        lines.append(f"# {chapter.get('title', 'Untitled')}\n")

        # Metadata
        lines.append(f"**Specialty:** {chapter.get('specialty', 'N/A')}")
        lines.append(f"**Status:** {chapter.get('status', 'N/A')}")
        lines.append(f"**Version:** {chapter.get('version', 1)}")
        lines.append(f"**Created:** {chapter.get('created_at', 'N/A')}")
        lines.append(f"**Updated:** {chapter.get('updated_at', 'N/A')}")
        lines.append("")

        # Tags
        metadata = chapter.get('metadata', {})
        if metadata and metadata.get('tags'):
            lines.append(f"**Tags:** {', '.join(metadata['tags'])}")
            lines.append("")

        # Summary
        content = chapter.get('content', {})
        if content and content.get('summary'):
            lines.append("## Summary\n")
            lines.append(content['summary'])
            lines.append("")

        # Sections
        sections = content.get('sections', []) if content else []
        if sections:
            lines.append("## Content\n")
            for i, section in enumerate(sections, 1):
                lines.append(f"### {i}. {section.get('title', 'Untitled Section')}\n")
                lines.append(section.get('content', ''))
                lines.append("")

                # Subsections
                subsections = section.get('subsections', [])
                for j, subsection in enumerate(subsections, 1):
                    lines.append(f"#### {i}.{j} {subsection.get('title', 'Untitled Subsection')}\n")
                    lines.append(subsection.get('content', ''))
                    lines.append("")

        # References
        references = chapter.get('references', [])
        if references:
            lines.append("## References\n")
            for i, ref_id in enumerate(references, 1):
                lines.append(f"{i}. Reference ID: {ref_id}")
            lines.append("")

        content = "\n".join(lines)

        return {
            "success": True,
            "format": "markdown",
            "content": content,
            "filename": f"{chapter.get('title', 'chapter').replace(' ', '_').lower()}.md",
            "mime_type": "text/markdown"
        }
    except Exception as e:
        logger.error(f"Markdown export failed: {e}")
        return {"success": False, "error": str(e)}


def export_as_html(chapter: Dict[str, Any]) -> Dict[str, Any]:
    """Export chapter as HTML"""
    try:
        html_parts = []

        # HTML header
        html_parts.append("<!DOCTYPE html>")
        html_parts.append("<html lang='en'>")
        html_parts.append("<head>")
        html_parts.append("    <meta charset='UTF-8'>")
        html_parts.append("    <meta name='viewport' content='width=device-width, initial-scale=1.0'>")
        html_parts.append(f"    <title>{chapter.get('title', 'Chapter')}</title>")
        html_parts.append("    <style>")
        html_parts.append("        body { font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }")
        html_parts.append("        h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }")
        html_parts.append("        h2 { color: #34495e; margin-top: 30px; }")
        html_parts.append("        h3 { color: #7f8c8d; }")
        html_parts.append("        .metadata { background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0; }")
        html_parts.append("        .metadata p { margin: 5px 0; }")
        html_parts.append("        .tags { margin: 10px 0; }")
        html_parts.append("        .tag { background: #3498db; color: white; padding: 3px 8px; border-radius: 3px; margin-right: 5px; font-size: 0.9em; }")
        html_parts.append("        .summary { background: #e8f4f8; padding: 15px; border-left: 4px solid #3498db; margin: 20px 0; }")
        html_parts.append("        pre { background: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }")
        html_parts.append("    </style>")
        html_parts.append("</head>")
        html_parts.append("<body>")

        # Title
        html_parts.append(f"    <h1>{chapter.get('title', 'Untitled')}</h1>")

        # Metadata
        html_parts.append("    <div class='metadata'>")
        html_parts.append(f"        <p><strong>Specialty:</strong> {chapter.get('specialty', 'N/A')}</p>")
        html_parts.append(f"        <p><strong>Status:</strong> {chapter.get('status', 'N/A')}</p>")
        html_parts.append(f"        <p><strong>Version:</strong> {chapter.get('version', 1)}</p>")
        html_parts.append(f"        <p><strong>Created:</strong> {chapter.get('created_at', 'N/A')}</p>")
        html_parts.append(f"        <p><strong>Updated:</strong> {chapter.get('updated_at', 'N/A')}</p>")

        # Tags
        metadata = chapter.get('metadata', {})
        if metadata and metadata.get('tags'):
            html_parts.append("        <div class='tags'>")
            for tag in metadata['tags']:
                html_parts.append(f"            <span class='tag'>{tag}</span>")
            html_parts.append("        </div>")

        html_parts.append("    </div>")

        # Summary
        content = chapter.get('content', {})
        if content and content.get('summary'):
            html_parts.append("    <div class='summary'>")
            html_parts.append("        <h2>Summary</h2>")
            html_parts.append(f"        <p>{content['summary']}</p>")
            html_parts.append("    </div>")

        # Sections
        sections = content.get('sections', []) if content else []
        if sections:
            html_parts.append("    <h2>Content</h2>")
            for i, section in enumerate(sections, 1):
                html_parts.append(f"    <h3>{i}. {section.get('title', 'Untitled Section')}</h3>")
                section_content = section.get('content', '').replace('\n', '<br>')
                html_parts.append(f"    <p>{section_content}</p>")

                # Subsections
                subsections = section.get('subsections', [])
                for j, subsection in enumerate(subsections, 1):
                    html_parts.append(f"    <h4>{i}.{j} {subsection.get('title', 'Untitled Subsection')}</h4>")
                    subsection_content = subsection.get('content', '').replace('\n', '<br>')
                    html_parts.append(f"    <p>{subsection_content}</p>")

        # References
        references = chapter.get('references', [])
        if references:
            html_parts.append("    <h2>References</h2>")
            html_parts.append("    <ol>")
            for ref_id in references:
                html_parts.append(f"        <li>Reference ID: {ref_id}</li>")
            html_parts.append("    </ol>")

        # HTML footer
        html_parts.append("</body>")
        html_parts.append("</html>")

        content = "\n".join(html_parts)

        return {
            "success": True,
            "format": "html",
            "content": content,
            "filename": f"{chapter.get('title', 'chapter').replace(' ', '_').lower()}.html",
            "mime_type": "text/html"
        }
    except Exception as e:
        logger.error(f"HTML export failed: {e}")
        return {"success": False, "error": str(e)}


def export_as_pdf(chapter: Dict[str, Any]) -> Dict[str, Any]:
    """Export chapter as PDF (placeholder - requires additional library)"""
    # Note: PDF generation requires libraries like reportlab or weasyprint
    # This is a placeholder that returns HTML which can be converted to PDF client-side
    return {
        "success": False,
        "error": "PDF export requires additional setup. Use HTML export and convert using browser print-to-PDF.",
        "alternative": "html"
    }


def export_as_docx(chapter: Dict[str, Any]) -> Dict[str, Any]:
    """Export chapter as DOCX (placeholder - requires additional library)"""
    # Note: DOCX generation requires python-docx library
    # This is a placeholder
    return {
        "success": False,
        "error": "DOCX export requires additional setup. Use Markdown or HTML export as alternative.",
        "alternative": "markdown"
    }
