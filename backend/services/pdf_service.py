"""
PDF Processing Service
Extracts text and metadata from neurosurgical PDFs
"""
import PyPDF2
import io
from typing import Dict, Any, Optional
from pathlib import Path


class PDFProcessor:
    """Service for processing PDF documents"""

    async def process_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Process a PDF file and extract content"""

        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

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
                }
            }

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
        """Extract common sections from neurosurgical papers"""
        sections = {}

        common_headers = [
            "abstract", "introduction", "methods", "results",
            "discussion", "conclusion", "references"
        ]

        text_lower = text.lower()

        for header in common_headers:
            # Simple section extraction (can be enhanced)
            if header in text_lower:
                start_idx = text_lower.find(header)
                sections[header] = text[start_idx:start_idx+2000]  # Extract snippet

        return sections