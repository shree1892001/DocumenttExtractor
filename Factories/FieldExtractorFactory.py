from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import re
import logging
import spacy
from Common.document_constants import (
    FIELD_PATTERNS,
    OCR_ERROR_PATTERNS,
    CHARACTER_PATTERNS
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseFieldExtractor(ABC):
    """Base class for field extractors"""
    
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
    
    def _clean_value(self, value: str) -> str:
        """Clean and validate extracted value"""
        try:
            if not value:
                return ""
            
            # Remove common OCR errors
            for pattern, replacement in OCR_ERROR_PATTERNS.items():
                value = re.sub(pattern, replacement, value)
            
            # Remove invalid characters
            for pattern in CHARACTER_PATTERNS:
                value = re.sub(pattern, "", value)
            
            # Remove extra whitespace
            value = " ".join(value.split())
            
            return value.strip()
        except Exception as e:
            logger.error(f"Error cleaning value: {str(e)}")
            return ""

    @abstractmethod
    def extract_fields(self, text: str) -> Dict[str, Any]:
        """Extract fields from text"""
        pass

class GenericFieldExtractor(BaseFieldExtractor):
    """Extractor for generic document fields"""
    
    def extract_fields(self, text: str) -> Dict[str, Any]:
        """Extract fields using pattern matching"""
        try:
            fields = {}
            doc = self.nlp(text)
            
            # Extract fields based on patterns
            for pattern in FIELD_PATTERNS:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    if isinstance(match.group(1), tuple):
                        field_name = match.group(1)[0].strip()
                        value = match.group(1)[1].strip()
                    else:
                        field_name = match.group(1).strip()
                        value = match.group(0).strip()
                    
                    if field_name and value:
                        fields[field_name] = value
            
            # Clean and validate extracted values
            cleaned_fields = {}
            for field_name, value in fields.items():
                if isinstance(value, (dict, list)):
                    value = str(value)
                cleaned_value = self._clean_value(value)
                if cleaned_value:
                    cleaned_fields[field_name] = cleaned_value
            
            # If no fields were extracted, include the raw text
            if not cleaned_fields:
                cleaned_fields = {
                    "text_content": text,
                    "document_type": "unknown",
                    "processing_method": "ocr"
                }
            
            return cleaned_fields
        except Exception as e:
            logger.error(f"Error extracting fields: {str(e)}")
            return {
                "text_content": text,
                "document_type": "unknown",
                "processing_method": "ocr"
            }

class IdentityDocumentExtractor(BaseFieldExtractor):
    """Extractor for identity documents (ID cards, passports, etc.)"""
    
    def extract_fields(self, text: str) -> Dict[str, Any]:
        """Extract fields specific to identity documents"""
        try:
            fields = {}
            doc = self.nlp(text)
            
            # Extract common identity fields
            identity_patterns = {
                'name': r'(?:name|full name)[:\s]+([A-Za-z\s]+)',
                'date_of_birth': r'(?:date of birth|dob|birth date)[:\s]+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
                'id_number': r'(?:id|identification|document) number[:\s]+([A-Z0-9-]+)',
                'expiry_date': r'(?:expiry|expiration) date[:\s]+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
                'nationality': r'nationality[:\s]+([A-Za-z\s]+)',
                'address': r'(?:address|residence)[:\s]+([A-Za-z0-9\s,.-]+)'
            }
            
            for field_name, pattern in identity_patterns.items():
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    value = match.group(1).strip()
                    if value:
                        fields[field_name] = value
                        break
            
            # Clean and validate extracted values
            cleaned_fields = {}
            for field_name, value in fields.items():
                if isinstance(value, (dict, list)):
                    value = str(value)
                cleaned_value = self._clean_value(value)
                if cleaned_value:
                    cleaned_fields[field_name] = cleaned_value
            
            # If no fields were extracted, include the raw text
            if not cleaned_fields:
                cleaned_fields = {
                    "text_content": text,
                    "document_type": "identity",
                    "processing_method": "ocr"
                }
            
            return cleaned_fields
        except Exception as e:
            logger.error(f"Error extracting identity fields: {str(e)}")
            return {
                "text_content": text,
                "document_type": "identity",
                "processing_method": "ocr"
            }

class LicenseExtractor(BaseFieldExtractor):
    """Extractor for license documents"""
    
    def extract_fields(self, text: str) -> Dict[str, Any]:
        """Extract fields specific to licenses"""
        try:
            fields = {}
            doc = self.nlp(text)
            
            # Extract license-specific fields
            license_patterns = {
                'license_number': r'(?:license|permit) number[:\s]+([A-Z0-9-]+)',
                'license_type': r'(?:license|permit) type[:\s]+([A-Za-z\s]+)',
                'issue_date': r'(?:issue|issued) date[:\s]+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
                'expiry_date': r'(?:expiry|expiration) date[:\s]+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
                'issuing_authority': r'(?:issuing|issuer) (?:authority|office)[:\s]+([A-Za-z\s]+)',
                'restrictions': r'restrictions[:\s]+([A-Za-z0-9\s,.-]+)'
            }
            
            for field_name, pattern in license_patterns.items():
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    value = match.group(1).strip()
                    if value:
                        fields[field_name] = value
                        break
            
            # Clean and validate extracted values
            cleaned_fields = {}
            for field_name, value in fields.items():
                if isinstance(value, (dict, list)):
                    value = str(value)
                cleaned_value = self._clean_value(value)
                if cleaned_value:
                    cleaned_fields[field_name] = cleaned_value
            
            # If no fields were extracted, include the raw text
            if not cleaned_fields:
                cleaned_fields = {
                    "text_content": text,
                    "document_type": "license",
                    "processing_method": "ocr"
                }
            
            return cleaned_fields
        except Exception as e:
            logger.error(f"Error extracting license fields: {str(e)}")
            return {
                "text_content": text,
                "document_type": "license",
                "processing_method": "ocr"
            }

class FieldExtractorFactory:
    """Factory class for creating field extractors"""
    
    _extractors = {
        'generic': GenericFieldExtractor,
        'identity': IdentityDocumentExtractor,
        'license': LicenseExtractor
    }
    
    @classmethod
    def create_extractor(cls, document_type: str) -> BaseFieldExtractor:
        """Create appropriate field extractor based on document type"""
        extractor_class = cls._extractors.get(document_type.lower(), GenericFieldExtractor)
        return extractor_class()
    
    @classmethod
    def register_extractor(cls, document_type: str, extractor_class: type) -> None:
        """Register a new extractor for a document type"""
        if not issubclass(extractor_class, BaseFieldExtractor):
            raise ValueError("Extractor must inherit from BaseFieldExtractor")
        cls._extractors[document_type.lower()] = extractor_class 