import os
import logging
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import fitz
import tempfile
import re
import cv2
import numpy as np
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class DocumentProcessor3:
    def __init__(self, api_key: str):
        self.api_key = api_key
        # Configure pytesseract path if needed
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows path
        # Configure OCR settings
        self.ocr_config = '--oem 3 --psm 6'  # Use LSTM OCR Engine Mode with automatic page segmentation

    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess image to improve OCR accuracy"""
        try:
            # Convert to numpy array for OpenCV processing
            img_array = np.array(image)
            
            # Convert to grayscale
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array

            # Resize image if too small
            height, width = gray.shape
            if width < 1000:
                scale = 1000 / width
                gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

            # Apply bilateral filter to remove noise while preserving edges
            denoised = cv2.bilateralFilter(gray, 9, 75, 75)

            # Apply adaptive thresholding with different methods
            thresh1 = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            thresh2 = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                cv2.THRESH_BINARY, 11, 2
            )

            # Combine both thresholding results
            thresh = cv2.bitwise_or(thresh1, thresh2)

            # Apply morphological operations to clean up the image
            kernel = np.ones((1, 1), np.uint8)
            opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
            closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)

            # Convert back to PIL Image
            processed_image = Image.fromarray(closing)
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(processed_image)
            processed_image = enhancer.enhance(2.5)
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(processed_image)
            processed_image = enhancer.enhance(2.5)
            
            # Enhance brightness
            enhancer = ImageEnhance.Brightness(processed_image)
            processed_image = enhancer.enhance(1.2)

            return processed_image
        except Exception as e:
            logger.warning(f"Image preprocessing failed: {str(e)}")
            return image

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF using PyMuPDF and enhanced OCR"""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            
            for page_num, page in enumerate(doc):
                # Get text from page
                page_text = page.get_text()
                
                # If page has images or if text extraction is poor, try OCR
                if page.get_images() or len(page_text.strip()) < 50:
                    # Convert page to image with higher DPI
                    pix = page.get_pixmap(matrix=fitz.Matrix(400/72, 400/72))  # 400 DPI
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    
                    # Preprocess image
                    processed_img = self.preprocess_image(img)
                    
                    # Perform OCR with multiple configurations
                    ocr_text = ""
                    
                    # Try different PSM modes and languages
                    psm_modes = [6, 3, 4, 1]  # Added PSM 1 for automatic page segmentation with OSD
                    languages = ['eng', 'eng+fra', 'eng+deu']  # Try multiple languages
                    
                    for psm in psm_modes:
                        for lang in languages:
                            config = f'--oem 3 --psm {psm} -l {lang}'
                            try:
                                temp_text = pytesseract.image_to_string(
                                    processed_img,
                                    config=config
                                )
                                if len(temp_text.strip()) > len(ocr_text.strip()):
                                    ocr_text = temp_text
                            except Exception as e:
                                logger.warning(f"OCR failed for PSM {psm} and language {lang}: {str(e)}")
                    
                    # If OCR text is better than extracted text, use it
                    if len(ocr_text.strip()) > len(page_text.strip()):
                        page_text = ocr_text
                
                # Process images in the page
                if page.get_images():
                    for img_index, img in enumerate(page.get_images(full=True)):
                        try:
                            xref = img[0]
                            base_image = doc.extract_image(xref)
                            image_bytes = base_image["image"]
                            
                            # Save image temporarily
                            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                                temp_file.write(image_bytes)
                                temp_path = temp_file.name
                            
                            # Perform OCR on image
                            try:
                                img = Image.open(temp_path)
                                processed_img = self.preprocess_image(img)
                                
                                # Try different PSM modes and languages for image
                                for psm in psm_modes:
                                    for lang in languages:
                                        config = f'--oem 3 --psm {psm} -l {lang}'
                                        try:
                                            temp_text = pytesseract.image_to_string(
                                                processed_img,
                                                config=config
                                            )
                                            if temp_text.strip():
                                                page_text += "\n" + temp_text
                                        except Exception as e:
                                            logger.warning(f"OCR failed for image {img_index} with PSM {psm} and language {lang}: {str(e)}")
                                
                            except Exception as e:
                                logger.warning(f"OCR failed for image {img_index}: {str(e)}")
                            
                            # Clean up temp file
                            os.unlink(temp_path)
                        except Exception as e:
                            logger.warning(f"Failed to process image {img_index}: {str(e)}")
                
                text += page_text + "\n\n"
            
            doc.close()
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise

    def extract_fields_from_text(self, text: str) -> Dict[str, str]:
        """Extract all fields and their values from text using enhanced patterns"""
        fields = {}
        
        # Split text into lines and clean
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Common field patterns
        patterns = [
            # Key: Value
            (r'^([^:]+):\s*(.+)$', ':'),
            # Key - Value
            (r'^([^-]+)-\s*(.+)$', '-'),
            # Key = Value
            (r'^([^=]+)=\s*(.+)$', '='),
            # Key Value (no separator)
            (r'^([A-Za-z\s]+)\s+([A-Za-z0-9\s\-\.]+)$', ' '),
            # Key/Value
            (r'^([^/]+)/(.+)$', '/'),
            # Key|Value
            (r'^([^|]+)\|(.+)$', '|'),
            # Key.Value
            (r'^([^\.]+)\.\s*(.+)$', '.'),
            # Key_Value
            (r'^([^_]+)_(.+)$', '_'),
        ]
        
        # Process each line
        for line in lines:
            # Try each pattern
            for pattern, separator in patterns:
                match = re.match(pattern, line)
                if match:
                    key = match.group(1).strip().lower()
                    value = match.group(2).strip()
                    
                    # Clean and normalize key
                    key = re.sub(r'[^a-z0-9\s]', ' ', key)
                    key = re.sub(r'\s+', '_', key.strip())
                    
                    if key and value:
                        fields[key] = value
                    break
            
            # If no pattern matched, check for potential field names
            if not any(key in line.lower() for key in fields.keys()):
                # Look for common field indicators
                field_indicators = [
                    'name', 'date', 'address', 'id', 'number', 'code',
                    'type', 'class', 'category', 'status', 'value',
                    'amount', 'total', 'balance', 'reference', 'account',
                    'phone', 'email', 'website', 'url', 'location',
                    'city', 'state', 'country', 'zip', 'postal',
                    'issue', 'expiry', 'valid', 'authority', 'department'
                ]
                
                for indicator in field_indicators:
                    if indicator in line.lower():
                        key = line.lower().replace(' ', '_')
                        if key not in fields:
                            fields[key] = ""
                        break
        
        # Clean up fields
        cleaned_fields = {}
        for key, value in fields.items():
            # Remove special characters from keys
            key = re.sub(r'[^a-z0-9_]', '', key)
            # Remove empty values
            if value:
                # Clean up value
                value = re.sub(r'\s+', ' ', value).strip()
                cleaned_fields[key] = value
        
        return cleaned_fields

    def detect_document_type(self, text: str) -> str:
        """Detect document type based on text content"""
        text = text.lower()
        
        # Document type patterns
        patterns = {
            'license': [
                r'driving\s*license',
                r'driver\s*license',
                r'dl\s*number',
                r'license\s*number',
                r'license\s*type',
                r'license\s*class'
            ],
            'passport': [
                r'passport\s*number',
                r'passport\s*type',
                r'passport\s*authority',
                r'passport\s*office'
            ],
            'id_card': [
                r'id\s*card',
                r'identity\s*card',
                r'national\s*id',
                r'government\s*id'
            ],
            'certificate': [
                r'certificate\s*number',
                r'certificate\s*type',
                r'certificate\s*of',
                r'certified\s*by'
            ]
        }
        
        # Check each document type
        for doc_type, doc_patterns in patterns.items():
            for pattern in doc_patterns:
                if re.search(pattern, text):
                    return doc_type
        
        return "unknown"

    def process_document(self, file_path: str) -> Optional[List[Dict[str, Any]]]:
        """Process document and extract information with enhanced error handling"""
        try:
            # Extract text from document
            extracted_text = self.extract_text_from_pdf(file_path)

            if not extracted_text or len(extracted_text.strip()) < 10:
                logger.warning(f"Very little text extracted from {file_path}")
                extracted_text = f"[Minimal text extracted from {os.path.basename(file_path)}]"

            # Extract fields from text
            extracted_fields = self.extract_fields_from_text(extracted_text)

            # Detect document type
            document_type = self.detect_document_type(extracted_text)

            # Create result with processing status
            result = {
                "document_type": document_type,
                "extracted_text": extracted_text,
                "extracted_fields": extracted_fields,
                "metadata": {
                    "file_path": file_path,
                    "file_type": os.path.splitext(file_path)[1].lower().replace('.', ''),
                    "processing_status": "success",
                    "text_length": len(extracted_text),
                    "fields_count": len(extracted_fields)
                }
            }

            return [result]

        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")

            # Return a minimal result instead of failing completely
            error_result = {
                "document_type": "unknown",
                "extracted_text": f"[Error processing document: {str(e)}]",
                "extracted_fields": {},
                "metadata": {
                    "file_path": file_path,
                    "file_type": os.path.splitext(file_path)[1].lower().replace('.', ''),
                    "processing_status": "error",
                    "error_message": str(e),
                    "text_length": 0,
                    "fields_count": 0
                }
            }

            return [error_result]