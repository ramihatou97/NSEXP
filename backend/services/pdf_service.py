"""
Enhanced PDF Processing Service
Extracts text, metadata, images, and tables from neurosurgical PDFs
"""
import PyPDF2
import io
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

# Advanced PDF processing
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    fitz = None

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Enhanced service for processing PDF documents with image extraction"""
    
    def __init__(self):
        self.use_advanced = PYMUPDF_AVAILABLE

    async def process_pdf(
        self, 
        pdf_path: str,
        extract_images: bool = False,
        extract_tables: bool = False
    ) -> Dict[str, Any]:
        """
        Process a PDF file and extract content including text, images, and tables
        
        Args:
            pdf_path: Path to PDF file
            extract_images: Whether to extract embedded images
            extract_tables: Whether to extract tables
            
        Returns:
            Dictionary with extracted content and metadata
        """
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        # Use advanced extraction if available
        if self.use_advanced and PYMUPDF_AVAILABLE:
            return await self._process_pdf_advanced(pdf_path, extract_images, extract_tables)
        
        # Fallback to PyPDF2
        return await self._process_pdf_basic(pdf_path)
    
    async def _process_pdf_basic(self, pdf_path: str) -> Dict[str, Any]:
        """Basic PDF processing using PyPDF2"""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)

            # Extract text from all pages
            text_content = []
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text_content.append(page.extract_text())

            # Get metadata
            metadata = pdf_reader.metadata or {}

            return {
                "text": "\n\n".join(text_content),
                "page_count": len(pdf_reader.pages),
                "title": metadata.get("/Title", ""),
                "authors": [metadata.get("/Author", "")] if metadata.get("/Author") else [],
                "metadata": {
                    "subject": metadata.get("/Subject", ""),
                    "creator": metadata.get("/Creator", ""),
                    "producer": metadata.get("/Producer", ""),
                    "creation_date": metadata.get("/CreationDate", "")
                },
                "extraction_method": "PyPDF2"
            }
    
    async def _process_pdf_advanced(
        self, 
        pdf_path: str,
        extract_images: bool = False,
        extract_tables: bool = False
    ) -> Dict[str, Any]:
        """
        Advanced PDF processing using PyMuPDF
        Better text extraction, image extraction, and structure analysis
        """
        try:
            doc = fitz.open(pdf_path)
            
            # Extract text with better formatting
            text_content = []
            page_details = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Extract text blocks with positioning
                page_text = page.get_text("text")
                text_content.append(page_text)
                
                # Get page dimensions
                page_details.append({
                    "page_number": page_num + 1,
                    "width": page.rect.width,
                    "height": page.rect.height,
                    "word_count": len(page_text.split()),
                    "has_images": len(page.get_images()) > 0
                })
            
            # Extract metadata
            metadata = doc.metadata
            
            result = {
                "text": "\n\n".join(text_content),
                "page_count": len(doc),
                "title": metadata.get("title", ""),
                "authors": [metadata.get("author", "")] if metadata.get("author") else [],
                "metadata": {
                    "subject": metadata.get("subject", ""),
                    "creator": metadata.get("creator", ""),
                    "producer": metadata.get("producer", ""),
                    "creation_date": metadata.get("creationDate", ""),
                    "keywords": metadata.get("keywords", "")
                },
                "page_details": page_details,
                "extraction_method": "PyMuPDF"
            }
            
            # Extract images if requested
            if extract_images:
                images = await self._extract_images_pymupdf(doc, pdf_path)
                result["images"] = images
                result["image_count"] = len(images)
            
            # Extract tables if requested
            if extract_tables:
                tables = await self._extract_tables_pymupdf(doc)
                result["tables"] = tables
                result["table_count"] = len(tables)
            
            doc.close()
            return result
            
        except Exception as e:
            logger.error(f"Advanced PDF processing failed: {e}, falling back to basic")
            return await self._process_pdf_basic(pdf_path)
    
    async def _extract_images_pymupdf(self, doc, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract images from PDF using PyMuPDF"""
        images = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            image_list = page.get_images(full=True)
            
            for img_index, img in enumerate(image_list):
                try:
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    
                    if base_image:
                        images.append({
                            "page": page_num + 1,
                            "index": img_index + 1,
                            "width": base_image.get("width"),
                            "height": base_image.get("height"),
                            "format": base_image.get("ext"),
                            "size_bytes": len(base_image["image"])
                        })
                except Exception as e:
                    logger.warning(f"Failed to extract image {img_index} from page {page_num}: {e}")
        
        return images
    
    async def _extract_tables_pymupdf(self, doc) -> List[Dict[str, Any]]:
        """
        Extract tables from PDF
        Uses text block analysis to identify table structures
        """
        tables = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Get text blocks with position information
            blocks = page.get_text("dict")["blocks"]
            
            # Simple heuristic: look for aligned text blocks
            # This is a basic implementation - can be enhanced
            table_candidates = []
            
            for block in blocks:
                if block.get("type") == 0:  # Text block
                    lines = block.get("lines", [])
                    if len(lines) > 2:  # Potential table row
                        table_candidates.append({
                            "page": page_num + 1,
                            "bbox": block["bbox"],
                            "lines": len(lines)
                        })
            
            if table_candidates:
                tables.append({
                    "page": page_num + 1,
                    "table_count": len(table_candidates),
                    "note": "Table detection is basic - enhancement recommended"
                })
        
        return tables

    async def process_pdf_bytes(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """Process PDF from bytes"""

        pdf_file = io.BytesIO(pdf_bytes)
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        text_content = []
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text_content.append(page.extract_text())

        metadata = pdf_reader.metadata or {}

        return {
            "text": "\n\n".join(text_content),
            "page_count": len(pdf_reader.pages),
            "title": metadata.get("/Title", ""),
            "authors": [metadata.get("/Author", "")] if metadata.get("/Author") else [],
            "metadata": {
                "subject": metadata.get("/Subject", ""),
                "creator": metadata.get("/Creator", ""),
                "producer": metadata.get("/Producer", "")
            }
        }

    def extract_sections(self, text: str) -> Dict[str, str]:
        """
        Extract common sections from neurosurgical papers
        Enhanced to capture more medical paper structures
        """
        sections = {}

        common_headers = [
            "abstract", "introduction", "background", "methods", "materials and methods",
            "results", "discussion", "conclusion", "conclusions", "references",
            "case report", "surgical technique", "complications", "outcomes",
            "literature review", "patient demographics"
        ]

        text_lower = text.lower()

        for header in common_headers:
            # Find section start
            if header in text_lower:
                start_idx = text_lower.find(header)
                
                # Try to find next section
                end_idx = start_idx + 3000  # Default end
                
                for other_header in common_headers:
                    if other_header != header:
                        next_idx = text_lower.find(other_header, start_idx + len(header))
                        if next_idx != -1 and next_idx < end_idx:
                            end_idx = next_idx
                
                sections[header] = text[start_idx:end_idx].strip()

        return sections
    
    async def chunk_pdf_content(
        self,
        pdf_path: str,
        chunk_size: int = 1000,
        overlap: int = 200
    ) -> List[Dict[str, Any]]:
        """
        Chunk PDF content for processing large documents
        Useful for AI processing with token limits
        
        Args:
            pdf_path: Path to PDF
            chunk_size: Number of characters per chunk
            overlap: Overlap between chunks
            
        Returns:
            List of text chunks with metadata
        """
        result = await self.process_pdf(pdf_path)
        text = result.get("text", "")
        
        chunks = []
        start = 0
        chunk_num = 1
        
        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]
            
            chunks.append({
                "chunk_number": chunk_num,
                "text": chunk_text,
                "start_char": start,
                "end_char": end,
                "length": len(chunk_text)
            })
            
            start += chunk_size - overlap
            chunk_num += 1
        
        return chunks