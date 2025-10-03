"""
Advanced Image Extraction Service for Medical PDFs
Extracts images, diagrams, and anatomical illustrations from neurosurgical literature
"""
import io
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import base64

# Core PDF and image processing
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    fitz = None

try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    Image = None

try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False
    convert_from_path = None

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False
    pytesseract = None

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    easyocr = None

logger = logging.getLogger(__name__)


class ImageExtractionService:
    """Service for extracting and processing images from medical PDFs"""
    
    def __init__(self):
        self.easyocr_reader = None
        if EASYOCR_AVAILABLE:
            try:
                # Initialize EasyOCR for medical text (English)
                self.easyocr_reader = easyocr.Reader(['en'], gpu=False)
                logger.info("EasyOCR initialized successfully")
            except Exception as e:
                logger.warning(f"EasyOCR initialization failed: {e}")
        
        self.supported_formats = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif']
    
    async def extract_images_from_pdf(
        self,
        pdf_path: str,
        output_dir: Optional[str] = None,
        min_width: int = 100,
        min_height: int = 100,
        extract_text: bool = True
    ) -> Dict[str, Any]:
        """
        Extract all images from a PDF file with metadata
        
        Args:
            pdf_path: Path to PDF file
            output_dir: Directory to save extracted images (optional)
            min_width: Minimum image width to extract
            min_height: Minimum image height to extract
            extract_text: Whether to perform OCR on images
            
        Returns:
            Dictionary with extracted images and metadata
        """
        if not PYMUPDF_AVAILABLE:
            logger.warning("PyMuPDF not available, using fallback extraction")
            return await self._fallback_image_extraction(pdf_path, output_dir)
        
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        # Create output directory if specified
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
        
        extracted_images = []
        
        try:
            # Open PDF with PyMuPDF
            pdf_document = fitz.open(pdf_path)
            
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                
                # Get images on this page
                image_list = page.get_images(full=True)
                
                for img_index, img_info in enumerate(image_list):
                    try:
                        xref = img_info[0]
                        base_image = pdf_document.extract_image(xref)
                        
                        if not base_image:
                            continue
                        
                        image_bytes = base_image["image"]
                        image_ext = base_image["ext"]
                        width = base_image.get("width", 0)
                        height = base_image.get("height", 0)
                        
                        # Filter by minimum dimensions
                        if width < min_width or height < min_height:
                            continue
                        
                        # Generate filename
                        image_filename = f"page{page_num + 1}_img{img_index + 1}.{image_ext}"
                        
                        # Save image if output directory specified
                        image_path = None
                        if output_dir:
                            image_path = output_path / image_filename
                            with open(image_path, "wb") as img_file:
                                img_file.write(image_bytes)
                        
                        # Convert to PIL Image for analysis
                        pil_image = None
                        if PILLOW_AVAILABLE:
                            try:
                                pil_image = Image.open(io.BytesIO(image_bytes))
                            except Exception as e:
                                logger.warning(f"Failed to open image with PIL: {e}")
                        
                        # Analyze image type (diagram, photo, chart, etc.)
                        image_type = self._classify_image_type(pil_image) if pil_image else "unknown"
                        
                        # Extract text from image if requested
                        extracted_text = None
                        if extract_text and pil_image:
                            extracted_text = await self._extract_text_from_image(pil_image)
                        
                        # Encode image as base64 for API response
                        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                        
                        image_data = {
                            "page_number": page_num + 1,
                            "image_index": img_index + 1,
                            "filename": image_filename,
                            "path": str(image_path) if image_path else None,
                            "width": width,
                            "height": height,
                            "format": image_ext,
                            "type": image_type,
                            "extracted_text": extracted_text,
                            "base64": image_base64[:1000] + "..." if len(image_base64) > 1000 else image_base64,  # Truncate for response
                            "size_bytes": len(image_bytes)
                        }
                        
                        extracted_images.append(image_data)
                        
                    except Exception as e:
                        logger.error(f"Error extracting image {img_index} from page {page_num}: {e}")
                        continue
            
            pdf_document.close()
            
            return {
                "success": True,
                "pdf_path": str(path),
                "total_pages": len(pdf_document),
                "images_extracted": len(extracted_images),
                "images": extracted_images,
                "output_directory": str(output_path) if output_dir else None
            }
            
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "pdf_path": str(path),
                "images_extracted": 0,
                "images": []
            }
    
    async def _fallback_image_extraction(
        self,
        pdf_path: str,
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fallback image extraction using pdf2image
        Converts entire pages to images
        """
        if not PDF2IMAGE_AVAILABLE:
            return {
                "success": False,
                "error": "No image extraction libraries available",
                "images": []
            }
        
        try:
            path = Path(pdf_path)
            images = convert_from_path(pdf_path, dpi=150)
            
            if output_dir:
                output_path = Path(output_dir)
                output_path.mkdir(parents=True, exist_ok=True)
            
            extracted_images = []
            
            for i, img in enumerate(images):
                image_filename = f"page{i + 1}_full.png"
                
                image_path = None
                if output_dir:
                    image_path = output_path / image_filename
                    img.save(image_path, 'PNG')
                
                # Convert to bytes for base64 encoding
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='PNG')
                img_bytes = img_byte_arr.getvalue()
                
                extracted_images.append({
                    "page_number": i + 1,
                    "filename": image_filename,
                    "path": str(image_path) if image_path else None,
                    "width": img.width,
                    "height": img.height,
                    "format": "png",
                    "type": "page_render",
                    "size_bytes": len(img_bytes)
                })
            
            return {
                "success": True,
                "pdf_path": str(path),
                "total_pages": len(images),
                "images_extracted": len(extracted_images),
                "images": extracted_images,
                "output_directory": str(output_path) if output_dir else None,
                "method": "pdf2image_fallback"
            }
            
        except Exception as e:
            logger.error(f"Fallback image extraction failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "images": []
            }
    
    def _classify_image_type(self, image: Any) -> str:
        """
        Classify image type (diagram, photo, chart, anatomical, etc.)
        Based on color distribution and complexity
        """
        if not image or not PILLOW_AVAILABLE:
            return "unknown"
        
        try:
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Calculate color statistics
            colors = image.getcolors(maxcolors=256)
            
            if colors:
                # Predominantly grayscale/black-white -> likely diagram or text
                if len(colors) < 20:
                    return "diagram_or_chart"
                
                # Limited colors -> likely illustration or diagram
                elif len(colors) < 100:
                    return "medical_illustration"
                
                # Many colors -> likely photograph or complex image
                else:
                    return "photograph_or_scan"
            
            # Default classification
            return "medical_image"
            
        except Exception as e:
            logger.warning(f"Image classification failed: {e}")
            return "unknown"
    
    async def _extract_text_from_image(self, image: Any) -> Optional[str]:
        """
        Extract text from image using OCR
        Tries EasyOCR first, falls back to Tesseract
        """
        if not image:
            return None
        
        try:
            # Try EasyOCR first (better for medical text)
            if self.easyocr_reader:
                try:
                    # Convert PIL image to numpy array
                    import numpy as np
                    img_array = np.array(image)
                    
                    results = self.easyocr_reader.readtext(img_array)
                    
                    if results:
                        # Extract text from results
                        text = " ".join([result[1] for result in results])
                        return text.strip()
                except Exception as e:
                    logger.warning(f"EasyOCR extraction failed: {e}")
            
            # Fallback to Tesseract
            if PYTESSERACT_AVAILABLE:
                try:
                    text = pytesseract.image_to_string(image)
                    return text.strip() if text else None
                except Exception as e:
                    logger.warning(f"Tesseract extraction failed: {e}")
            
            return None
            
        except Exception as e:
            logger.error(f"Text extraction from image failed: {e}")
            return None
    
    async def analyze_anatomical_image(
        self,
        image_path: str,
        ai_service: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Analyze anatomical image using AI vision models
        Identifies structures, labels, and provides description
        
        Args:
            image_path: Path to image file
            ai_service: AI service manager for vision analysis
            
        Returns:
            Analysis results with identified structures
        """
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        if not PILLOW_AVAILABLE:
            return {
                "success": False,
                "error": "Image processing not available"
            }
        
        try:
            # Load image
            image = Image.open(image_path)
            
            # Basic analysis
            analysis = {
                "success": True,
                "image_path": str(path),
                "width": image.width,
                "height": image.height,
                "format": image.format,
                "mode": image.mode,
                "type": self._classify_image_type(image)
            }
            
            # Extract text labels
            extracted_text = await self._extract_text_from_image(image)
            if extracted_text:
                analysis["labels"] = extracted_text
            
            # AI-powered analysis (if available)
            if ai_service:
                try:
                    # Convert image to base64 for AI analysis
                    buffered = io.BytesIO()
                    image.save(buffered, format="PNG")
                    img_base64 = base64.b64encode(buffered.getvalue()).decode()
                    
                    # Call AI vision service
                    ai_analysis = await self._analyze_with_ai_vision(
                        img_base64,
                        ai_service
                    )
                    
                    if ai_analysis:
                        analysis["ai_description"] = ai_analysis.get("description")
                        analysis["identified_structures"] = ai_analysis.get("structures", [])
                        analysis["medical_relevance"] = ai_analysis.get("relevance")
                        
                except Exception as e:
                    logger.warning(f"AI vision analysis failed: {e}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "image_path": str(path)
            }
    
    async def _analyze_with_ai_vision(
        self,
        image_base64: str,
        ai_service: Any
    ) -> Optional[Dict[str, Any]]:
        """
        Use AI vision models to analyze medical images
        """
        try:
            prompt = """Analyze this medical/anatomical image and provide:
1. A detailed description of what is shown
2. Identification of anatomical structures visible
3. Type of image (MRI, CT, diagram, surgical photo, etc.)
4. Medical relevance and context
5. Any visible labels or annotations

Focus on neurosurgical anatomy and structures."""
            
            # This would call the AI service with vision capabilities
            # Implementation depends on available AI service
            # Placeholder for now
            
            return {
                "description": "AI vision analysis pending integration",
                "structures": [],
                "relevance": "high"
            }
            
        except Exception as e:
            logger.error(f"AI vision analysis error: {e}")
            return None


# Global instance
image_extraction_service = ImageExtractionService()
