from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import cv2
import numpy as np
from PIL import Image
import pytesseract
import logging
import re
import os
from pdf2image import convert_from_path
from docx import Document
import tempfile
import fitz  # PyMuPDF
from Factories.OCRExtractorFactory import OCRExtractorFactory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseTextExtractor(ABC):
    """Base class for text extractors"""
    
    def __init__(self):
        self.ocr_factory = OCRExtractorFactory()
    
    @abstractmethod
    def extract_text(self, file_path: str) -> str:
        """Extract text from file"""
        pass

class ImageTextExtractor(BaseTextExtractor):
    """Extractor for image files"""
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from image file"""
        try:
            # Read image
            image = cv2.imread(file_path)
            if image is None:
                raise ValueError(f"Could not read image: {file_path}")
            
            # Create OCR extractor
            ocr_extractor = self.ocr_factory.create_extractor('document')
            
            # Extract text
            text = ocr_extractor.extract_text(image)
            
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from image: {str(e)}")
            return ""

class PDFTextExtractor(BaseTextExtractor):
    """Extractor for PDF files"""
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            text_content = []
            pdf_document = fitz.open(file_path)
            
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                
                # Try normal text extraction first
                text = page.get_text()
                
                # If no text found or text is too short, try OCR
                if not text.strip() or len(text.strip()) < 50:
                    # Convert page to high-resolution image
                    pix = page.get_pixmap(matrix=fitz.Matrix(400/72, 400/72))  # 400 DPI
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    
                    # Convert PIL Image to OpenCV format
                    image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                    
                    # Create OCR extractor
                    ocr_extractor = self.ocr_factory.create_extractor('document')
                    
                    # Extract text
                    text = ocr_extractor.extract_text(image)
                
                # Process images in the page
                if page.get_images():
                    for img_index, img in enumerate(page.get_images(full=True)):
                        try:
                            xref = img[0]
                            base_image = pdf_document.extract_image(xref)
                            image_bytes = base_image["image"]
                            
                            # Save image temporarily
                            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                                temp_file.write(image_bytes)
                                temp_path = temp_file.name
                            
                            # Extract text from image
                            try:
                                img_text = ImageTextExtractor().extract_text(temp_path)
                                if img_text.strip():
                                    text += "\n" + img_text
                            except Exception as e:
                                logger.warning(f"OCR failed for image {img_index}: {str(e)}")
                            
                            # Clean up temp file
                            os.unlink(temp_path)
                        except Exception as e:
                            logger.warning(f"Failed to process image {img_index}: {str(e)}")
                
                if text.strip():
                    text_content.append(text.strip())
            
            pdf_document.close()
            return '\n'.join(text_content)
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            return ""

class DocxTextExtractor(BaseTextExtractor):
    """Extractor for DOCX files"""
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            text_content = []
            
            # Extract text from paragraphs
            for para in doc.paragraphs:
                if para.text.strip():
                    text_content.append(para.text.strip())
            
            # Extract text from images
            for rel in doc.part.rels.values():
                if "image" in rel.target_ref:
                    try:
                        # Get image data
                        image_data = rel.target_part.blob
                        
                        # Save image temporarily
                        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                            temp_file.write(image_data)
                            temp_path = temp_file.name
                        
                        # Extract text from image
                        try:
                            img_text = ImageTextExtractor().extract_text(temp_path)
                            if img_text.strip():
                                text_content.append(img_text.strip())
                        except Exception as e:
                            logger.warning(f"OCR failed for image in DOCX: {str(e)}")
                        
                        # Clean up temp file
                        os.unlink(temp_path)
                    except Exception as e:
                        logger.warning(f"Failed to process image in DOCX: {str(e)}")
            
            return '\n'.join(text_content)
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {str(e)}")
            return ""

class TextExtractorFactory:
    """Factory class for creating text extractors"""
    
    _extractors = {
        '.jpg': ImageTextExtractor,
        '.jpeg': ImageTextExtractor,
        '.png': ImageTextExtractor,
        '.pdf': PDFTextExtractor,
        '.docx': DocxTextExtractor
    }
    
    @classmethod
    def create_extractor(cls, file_path: str) -> BaseTextExtractor:
        """Create appropriate text extractor based on file extension"""
        _, ext = os.path.splitext(file_path.lower())
        extractor_class = cls._extractors.get(ext, ImageTextExtractor)
        return extractor_class()
    
    @classmethod
    def register_extractor(cls, extension: str, extractor_class: type) -> None:
        """Register a new extractor for a file extension"""
        if not issubclass(extractor_class, BaseTextExtractor):
            raise ValueError("Extractor must inherit from BaseTextExtractor")
        cls._extractors[extension.lower()] = extractor_class 