"""
PDF & Reference Library System - Adapted for Integration
Complete system for managing, extracting, and searching PDF medical textbooks
"""

import asyncio
import json
import logging
import re
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

# For PDF processing
import PyPDF2
import magic

logger = logging.getLogger(__name__)


# ============= Data Models =============

@dataclass
class Textbook:
    """Represents a medical textbook"""
    id: str
    name: str
    title: str
    folder_path: str
    edition: Optional[str] = None
    authors: List[str] = field(default_factory=list)
    publisher: Optional[str] = None
    publication_year: Optional[int] = None
    isbn: Optional[str] = None
    specialty: str = "neurosurgery"
    is_processed: bool = False
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    processing_error: Optional[str] = None


@dataclass
class BookChapter:
    """Represents a chapter within a textbook"""
    id: str
    textbook_id: str
    file_name: str
    file_path: str
    chapter_number: Optional[int] = None
    title: Optional[str] = None
    content_text: Optional[str] = None
    summary: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    medical_terms: List[str] = field(default_factory=list)
    citations: List[Dict] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)
    file_size_mb: Optional[float] = None
    word_count: Optional[int] = None
    reading_time_minutes: Optional[int] = None
    complexity_score: Optional[float] = None
    is_processed: bool = False
    tables: List[Dict] = field(default_factory=list)
    figures: List[Dict] = field(default_factory=list)


@dataclass
class ReferenceSearchIndex:
    """Search index entry for efficient retrieval"""
    id: str
    chapter_id: str
    text_chunk: str
    chunk_position: int
    chunk_size: int
    section_title: Optional[str] = None
    embedding: Optional[List[float]] = None


@dataclass
class ChapterSearchResult:
    """Search result with relevance scoring"""
    chapter_id: str
    title: str
    file_path: str
    chapter_number: Optional[int]
    textbook_title: str
    text_chunk: str
    chunk_position: int
    relevance_score: float


@dataclass
class ProcessingStats:
    """Statistics for processing operations"""
    textbooks_found: int = 0
    textbooks_processed: int = 0
    chapters_found: int = 0
    chapters_processed: int = 0
    chapters_failed: int = 0
    processing_time_seconds: float = 0.0
    average_extraction_accuracy: float = 0.0
    citation_extraction_rate: float = 0.0
    medical_term_coverage: float = 0.0
    total_content_size_gb: float = 0.0
    index_entry_count: int = 0
    errors: List[str] = field(default_factory=list)


# ============= Main Service =============

class ReferenceLibraryService:
    """Service for managing PDF textbook references with intelligent extraction"""

    def __init__(self, database_connection=None):
        self.textbooks_root = Path("textbooks")
        self.supported_formats = ['.pdf']
        self.chunk_size = 1000  # Characters per search chunk
        self.chunk_overlap = 200  # Overlap for context preservation
        self.max_file_size_mb = 100

        # In-memory storage (replace with actual database in production)
        self.textbooks: Dict[str, Textbook] = {}
        self.chapters: Dict[str, BookChapter] = {}
        self.search_index: List[ReferenceSearchIndex] = []

        # Chapter recognition patterns
        self.chapter_patterns = [
            r'^(\d+)[.\-_]\s*(.+)\.pdf$',
            r'^chapter[_\-\s]*(\d+)[.\-_]\s*(.+)\.pdf$',
            r'^ch[_\-\s]*(\d+)[.\-_]\s*(.+)\.pdf$',
            r'^([A-Z]\d+)[.\-_]\s*(.+)\.pdf$',
        ]

        # Medical term patterns
        self.medical_patterns = self._initialize_medical_patterns()

    def _initialize_medical_patterns(self) -> Dict[str, List[str]]:
        """Initialize medical term recognition patterns"""
        return {
            'anatomy': [
                r'\b(?:frontal|parietal|temporal|occipital)\s+lobe\b',
                r'\b(?:cerebr[oa]l?|spin[ae]l|neural)\s+\w+\b',
                r'\b(?:cortex|medulla|pons|midbrain|thalamus)\b'
            ],
            'procedures': [
                r'\b(?:craniotomy|laminectomy|diskectomy)\b',
                r'\b(?:stereotactic|endoscopic|microsurgical)\s+\w+\b'
            ],
            'conditions': [
                r'\b(?:glioblastoma|meningioma|astrocytoma)\b',
                r'\b(?:aneurysm|hemorrhage|hematoma)\b'
            ],
            'drugs': [
                r'\b(?:dexamethasone|mannitol|phenytoin|levetiracetam)\b',
                r'\b(?:temozolomide|bevacizumab|carmustine)\b'
            ]
        }

    async def scan_textbooks_folder(self, force_rescan: bool = False) -> ProcessingStats:
        """Scan textbooks folder and process all PDFs"""
        stats = ProcessingStats()
        start_time = datetime.now()

        if not self.textbooks_root.exists():
            logger.error(f"Textbooks root does not exist: {self.textbooks_root}")
            stats.errors.append(f"Path not found: {self.textbooks_root}")
            return stats

        # Scan for textbook folders
        for folder in self.textbooks_root.iterdir():
            if folder.is_dir():
                stats.textbooks_found += 1

                # Process textbook folder
                try:
                    textbook = await self._process_textbook_folder(folder)
                    if textbook:
                        self.textbooks[textbook.id] = textbook
                        stats.textbooks_processed += 1
                except Exception as e:
                    logger.error(f"Failed to process textbook {folder.name}: {e}")
                    stats.errors.append(f"Textbook {folder.name}: {str(e)}")

        stats.processing_time_seconds = (datetime.now() - start_time).total_seconds()
        return stats

    async def _process_textbook_folder(self, folder_path: Path) -> Optional[Textbook]:
        """Process a single textbook folder"""
        # Load metadata if available
        metadata = {}
        metadata_file = folder_path / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)

        # Create textbook record
        textbook = Textbook(
            id=self._generate_id(),
            name=folder_path.name,
            title=metadata.get('title', folder_path.name),
            folder_path=str(folder_path),
            edition=metadata.get('edition'),
            authors=metadata.get('authors', []),
            publisher=metadata.get('publisher'),
            publication_year=metadata.get('year'),
            isbn=metadata.get('isbn'),
            specialty=metadata.get('specialty', 'neurosurgery')
        )

        # Find and process PDF chapters
        pdf_files = list(folder_path.glob("*.pdf"))
        for pdf_file in pdf_files:
            try:
                chapter = await self._process_chapter_pdf(pdf_file, textbook.id)
                if chapter:
                    self.chapters[chapter.id] = chapter
            except Exception as e:
                logger.error(f"Failed to process chapter {pdf_file.name}: {e}")

        textbook.is_processed = True
        textbook.processing_completed_at = datetime.now()

        return textbook

    async def _process_chapter_pdf(self, pdf_path: Path, textbook_id: str) -> Optional[BookChapter]:
        """Process a single PDF chapter"""
        # Extract chapter info from filename
        chapter_info = self._extract_chapter_info(pdf_path.name)

        # Create chapter record
        chapter = BookChapter(
            id=self._generate_id(),
            textbook_id=textbook_id,
            file_name=pdf_path.name,
            file_path=str(pdf_path),
            chapter_number=chapter_info.get('number'),
            title=chapter_info.get('title', pdf_path.stem),
            file_size_mb=pdf_path.stat().st_size / (1024 * 1024)
        )

        # Extract content
        try:
            extracted_data = await self._extract_pdf_content(pdf_path)
            chapter.content_text = extracted_data['text']
            chapter.citations = extracted_data['citations']
            chapter.medical_terms = extracted_data['medical_terms']
            chapter.tables = extracted_data.get('tables', [])
            chapter.figures = extracted_data.get('figures', [])

            # Calculate metrics
            if chapter.content_text:
                chapter.word_count = len(chapter.content_text.split())
                chapter.reading_time_minutes = chapter.word_count // 200
                chapter.complexity_score = self._assess_content_quality(chapter.content_text)

            # Update search index
            self._update_search_index(chapter.content_text, chapter.id)

            chapter.is_processed = True

        except Exception as e:
            logger.error(f"Content extraction failed for {pdf_path}: {e}")
            chapter.processing_error = str(e)

        return chapter

    async def _extract_pdf_content(self, file_path: Path) -> Dict[str, Any]:
        """Extract content from PDF file"""
        text_content = ""

        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)

                # Extract text from all pages
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text_content += page_text + "\n"

        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            # Fallback to basic file reading or OCR could go here
            text_content = f"[PDF extraction failed: {e}]"

        # Extract structured elements
        extracted_data = {
            'text': text_content,
            'citations': self._extract_citations(text_content),
            'medical_terms': self._extract_medical_terms(text_content),
            'figures': self._extract_figure_references(text_content),
            'tables': self._extract_table_references(text_content)
        }

        return extracted_data

    def _extract_chapter_info(self, filename: str) -> Dict[str, Any]:
        """Extract chapter number and title from filename"""
        for pattern in self.chapter_patterns:
            match = re.match(pattern, filename)
            if match:
                return {
                    'number': int(match.group(1)) if match.group(1).isdigit() else 0,
                    'title': match.group(2).replace('_', ' ').replace('-', ' ').title()
                }

        # Fallback: use filename as title
        return {
            'number': None,
            'title': Path(filename).stem.replace('_', ' ').replace('-', ' ').title()
        }

    def _extract_medical_terms(self, text: str) -> List[str]:
        """Extract medical terms using pattern matching"""
        found_terms = set()

        for category, patterns in self.medical_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                found_terms.update(matches)

        return list(found_terms)

    def _extract_citations(self, text: str) -> List[Dict]:
        """Extract citations in various formats"""
        citation_patterns = {
            'vancouver': r'\[(\d+)\]\s*([^\.]+\.[^\.]+\.)',
            'apa': r'\(([A-Z][a-z]+(?:\s+et\s+al\.)?),\s*(\d{4})\)',
            'doi': r'doi:\s*(10\.\d{4,}/[-._;()/:\w]+)',
            'pmid': r'PMID:\s*(\d{7,8})'
        }

        citations = []
        for style, pattern in citation_patterns.items():
            matches = re.findall(pattern, text)
            for match in matches:
                citations.append({
                    'style': style,
                    'text': str(match),
                    'type': 'citation'
                })

        return citations

    def _extract_figure_references(self, text: str) -> List[Dict]:
        """Extract figure references from text"""
        figures = []

        # Pattern for figure references
        fig_patterns = [
            r'Figure\s+(\d+[\.\d]*)[:\.]?\s*([^\.]+)',
            r'Fig\.\s*(\d+[\.\d]*)[:\.]?\s*([^\.]+)',
            r'\(Fig\.\s*(\d+[\.\d]*)\)'
        ]

        for pattern in fig_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                figures.append({
                    'number': match.group(1) if len(match.groups()) > 0 else '',
                    'caption': match.group(2) if len(match.groups()) > 1 else '',
                    'type': 'figure_reference'
                })

        return figures

    def _extract_table_references(self, text: str) -> List[Dict]:
        """Extract table references from text"""
        tables = []

        # Pattern for table references
        table_patterns = [
            r'Table\s+(\d+[\.\d]*)[:\.]?\s*([^\.]+)',
            r'\(Table\s+(\d+[\.\d]*)\)'
        ]

        for pattern in table_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                tables.append({
                    'number': match.group(1) if len(match.groups()) > 0 else '',
                    'title': match.group(2) if len(match.groups()) > 1 else '',
                    'type': 'table_reference'
                })

        return tables

    def _update_search_index(self, content: str, chapter_id: str):
        """Generate search index with overlapping chunks"""
        if not content:
            return

        start = 0
        while start < len(content):
            end = start + self.chunk_size
            chunk = content[start:end]

            # Detect section title if present
            section_title = self._detect_section_title(chunk)

            # Create index entry
            index_entry = ReferenceSearchIndex(
                id=self._generate_id(),
                chapter_id=chapter_id,
                text_chunk=chunk,
                chunk_position=start,
                chunk_size=len(chunk),
                section_title=section_title
            )

            self.search_index.append(index_entry)

            # Move with overlap
            if end >= len(content):
                break
            start += self.chunk_size - self.chunk_overlap

    def _detect_section_title(self, chunk: str) -> Optional[str]:
        """Detect section title in chunk"""
        # Look for common section patterns
        lines = chunk.split('\n')
        for line in lines[:5]:  # Check first few lines
            # Common section indicators
            if re.match(r'^[A-Z][A-Z\s]+$', line.strip()):
                return line.strip()
            if re.match(r'^\d+\.\s+[A-Z]', line.strip()):
                return line.strip()
        return None

    async def search_chapters(
        self,
        query: str,
        textbook_id: Optional[str] = None,
        specialty: Optional[str] = None,
        limit: int = 20
    ) -> List[ChapterSearchResult]:
        """Search chapters with relevance scoring"""
        results = []
        query_lower = query.lower()

        # Search through all chapters
        for chapter_id, chapter in self.chapters.items():
            # Apply filters
            if textbook_id and chapter.textbook_id != textbook_id:
                continue

            # Calculate relevance
            relevance_score = 0.0

            # Title match (highest weight)
            if chapter.title and query_lower in chapter.title.lower():
                relevance_score += 1.0

            # Content match
            if chapter.content_text and query_lower in chapter.content_text.lower():
                # Count occurrences
                occurrences = chapter.content_text.lower().count(query_lower)
                relevance_score += min(occurrences * 0.1, 0.8)

            # Medical term match
            if any(query_lower in term.lower() for term in chapter.medical_terms):
                relevance_score += 0.3

            # Keyword match
            if any(query_lower in kw.lower() for kw in chapter.keywords):
                relevance_score += 0.2

            if relevance_score > 0:
                # Get relevant chunk
                chunk = self._get_relevant_chunk(chapter.content_text, query)

                # Get textbook info
                textbook = self.textbooks.get(chapter.textbook_id)

                results.append(ChapterSearchResult(
                    chapter_id=chapter_id,
                    title=chapter.title or "Untitled",
                    file_path=chapter.file_path,
                    chapter_number=chapter.chapter_number,
                    textbook_title=textbook.title if textbook else "Unknown",
                    text_chunk=chunk,
                    chunk_position=0,
                    relevance_score=min(relevance_score, 1.0)
                ))

        # Sort by relevance
        results.sort(key=lambda x: x.relevance_score, reverse=True)

        return results[:limit]

    def _get_relevant_chunk(self, content: str, query: str, context_size: int = 500) -> str:
        """Extract relevant chunk around query match"""
        if not content:
            return ""

        query_lower = query.lower()
        content_lower = content.lower()

        # Find query position
        pos = content_lower.find(query_lower)

        if pos == -1:
            # Return beginning if no exact match
            return content[:context_size]

        # Extract with context
        start = max(0, pos - context_size // 2)
        end = min(len(content), pos + len(query) + context_size // 2)

        chunk = content[start:end]

        # Clean up edges
        if start > 0:
            chunk = "..." + chunk
        if end < len(content):
            chunk = chunk + "..."

        return chunk

    async def get_chapter_by_id(self, chapter_id: str) -> Optional[BookChapter]:
        """Retrieve full chapter by ID"""
        return self.chapters.get(chapter_id)

    def _assess_content_quality(self, text: str) -> float:
        """Assess extracted content quality"""
        if not text:
            return 0.0

        quality_factors = {
            'text_length': len(text) > 500,
            'has_structure': bool(re.search(r'\n\n', text)),
            'has_medical_terms': len(self._extract_medical_terms(text)) > 5,
            'has_citations': len(self._extract_citations(text)) > 0,
            'complete_sentences': bool(re.search(r'\.\s+[A-Z]', text)),
            'not_gibberish': not bool(re.search(r'[^\x00-\x7F]{10,}', text))
        }

        score = sum(1 for factor in quality_factors.values() if factor)
        return score / len(quality_factors)

    def _generate_id(self) -> str:
        """Generate unique ID"""
        import uuid
        return str(uuid.uuid4())

    def _generate_sha256(self, file_path: Path) -> str:
        """Generate SHA-256 hash of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    async def get_statistics(self) -> ProcessingStats:
        """Get system statistics"""
        stats = ProcessingStats()
        stats.textbooks_found = len(self.textbooks)
        stats.textbooks_processed = sum(1 for t in self.textbooks.values() if t.is_processed)
        stats.chapters_found = len(self.chapters)
        stats.chapters_processed = sum(1 for c in self.chapters.values() if c.is_processed)
        stats.index_entry_count = len(self.search_index)

        # Calculate total content size
        total_size = sum(c.file_size_mb or 0 for c in self.chapters.values())
        stats.total_content_size_gb = total_size / 1024

        # Calculate average quality
        quality_scores = [c.complexity_score for c in self.chapters.values() if c.complexity_score]
        if quality_scores:
            stats.average_extraction_accuracy = sum(quality_scores) / len(quality_scores)

        return stats