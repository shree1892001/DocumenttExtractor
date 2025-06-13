from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
import cv2
import numpy as np
from PIL import Image
import pytesseract
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseOCRExtractor(ABC):
    """Base class for OCR extractors"""
    
    def preprocess_image(self, image: np.ndarray) -> List[np.ndarray]:
        """Apply various preprocessing techniques to improve OCR accuracy"""
        processed_images = []
        
        # Original image
        processed_images.append(image.copy())
        
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        processed_images.append(gray)
        
        # Apply thresholding
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        processed_images.append(thresh)
        
        # Apply adaptive thresholding
        adaptive_thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                              cv2.THRESH_BINARY, 11, 2)
        processed_images.append(adaptive_thresh)
        
        # Apply noise reduction
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        processed_images.append(denoised)
        
        # Apply sharpening
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(gray, -1, kernel)
        processed_images.append(sharpened)
        
        return processed_images

    def detect_text_regions(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Detect regions containing text"""
        try:
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # Apply thresholding
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Find contours
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter contours based on area and aspect ratio
            text_regions = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / float(h)
                area = w * h
                
                # Filter based on size and aspect ratio
                if 10 < area < 100000 and 0.1 < aspect_ratio < 10:
                    text_regions.append((x, y, w, h))
            
            return text_regions
        except Exception as e:
            logger.error(f"Error detecting text regions: {str(e)}")
            return []

    def extract_text_from_region(self, image: np.ndarray, region: Tuple[int, int, int, int], 
                               psm_mode: int = 6) -> str:
        """Extract text from a specific region"""
        try:
            x, y, w, h = region
            roi = image[y:y+h, x:x+w]
            
            # Preprocess ROI
            processed_images = self.preprocess_image(roi)
            
            # Try different PSM modes and languages
            best_text = ""
            languages = ['eng', 'eng+fra', 'eng+deu', 'eng+osd']
            psm_modes = [psm_mode, 3, 4, 6, 7, 11, 12]  # Try multiple PSM modes
            
            for processed_img in processed_images:
                for lang in languages:
                    for psm in psm_modes:
                        config = f'--oem 3 --psm {psm} -l {lang}'
                        try:
                            text = pytesseract.image_to_string(
                                processed_img,
                                config=config
                            )
                            # Score the text quality based on length and content
                            score = self._score_text_quality(text)
                            current_score = self._score_text_quality(best_text)
                            
                            if score > current_score:
                                best_text = text
                        except Exception as e:
                            logger.warning(f"OCR failed for PSM {psm} and language {lang}: {str(e)}")
            
            return best_text
        except Exception as e:
            logger.error(f"Error extracting text from region: {str(e)}")
            return ""

    @abstractmethod
    def extract_text(self, image: np.ndarray) -> str:
        """Extract text from image"""
        pass

class DocumentOCRExtractor(BaseOCRExtractor):
    """Extractor for document images"""
    
    def extract_text(self, image: np.ndarray) -> str:
        """Extract text from document image"""
        try:
            # Detect text regions
            text_regions = self.detect_text_regions(image)
            
            # Sort regions from top to bottom, left to right
            text_regions.sort(key=lambda x: (x[1], x[0]))
            
            # Extract text from each region
            extracted_text = []
            for region in text_regions:
                text = self.extract_text_from_region(image, region)
                if text:
                    extracted_text.append(text)
            
            return '\n'.join(extracted_text)
        except Exception as e:
            logger.error(f"Error extracting text from document: {str(e)}")
            return ""

class TableOCRExtractor(BaseOCRExtractor):
    """Extractor for table images"""
    
    def extract_text(self, image: np.ndarray) -> str:
        """Extract text from table image"""
        try:
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # Detect table structure
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
            
            # Extract cells
            cells = self._extract_cells(gray, lines)
            
            # Extract text from each cell
            table_text = []
            for cell in cells:
                text = self.extract_text_from_region(gray, cell, psm_mode=7)  # PSM 7 for single line
                if text:
                    table_text.append(text)
            
            return '\n'.join(table_text)
        except Exception as e:
            logger.error(f"Error extracting text from table: {str(e)}")
            return ""

    def _extract_cells(self, image: np.ndarray, lines: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Extract table cells from image"""
        try:
            # Find horizontal and vertical lines
            horizontal_lines = []
            vertical_lines = []
            
            for line in lines:
                x1, y1, x2, y2 = line[0]
                if abs(x2 - x1) > abs(y2 - y1):  # Horizontal line
                    horizontal_lines.append((y1, x1, x2))
                else:  # Vertical line
                    vertical_lines.append((x1, y1, y2))
            
            # Sort lines
            horizontal_lines.sort(key=lambda x: x[0])
            vertical_lines.sort(key=lambda x: x[0])
            
            # Find cell intersections
            cells = []
            for i in range(len(horizontal_lines) - 1):
                for j in range(len(vertical_lines) - 1):
                    y1 = horizontal_lines[i][0]
                    y2 = horizontal_lines[i + 1][0]
                    x1 = vertical_lines[j][0]
                    x2 = vertical_lines[j + 1][0]
                    
                    # Add padding
                    padding = 5
                    cells.append((
                        max(0, x1 - padding),
                        max(0, y1 - padding),
                        min(image.shape[1] - x1, x2 - x1 + 2 * padding),
                        min(image.shape[0] - y1, y2 - y1 + 2 * padding)
                    ))
            
            return cells
        except Exception as e:
            logger.error(f"Error extracting cells: {str(e)}")
            return []

class OCRExtractorFactory:
    """Factory class for creating OCR extractors"""
    
    _extractors = {
        'document': DocumentOCRExtractor,
        'table': TableOCRExtractor
    }
    
    @classmethod
    def create_extractor(cls, image_type: str) -> BaseOCRExtractor:
        """Create appropriate OCR extractor based on image type"""
        extractor_class = cls._extractors.get(image_type.lower(), DocumentOCRExtractor)
        return extractor_class()
    
    @classmethod
    def register_extractor(cls, image_type: str, extractor_class: type) -> None:
        """Register a new extractor for an image type"""
        if not issubclass(extractor_class, BaseOCRExtractor):
            raise ValueError("Extractor must inherit from BaseOCRExtractor")
        cls._extractors[image_type.lower()] = extractor_class 
