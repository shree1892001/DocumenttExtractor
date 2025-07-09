"""
UniversalDataExtractor - Extracts ALL data from ANY document type
General purpose document data extraction without document-specific limitations
"""

import json
import logging
from typing import Dict, Any, Optional, List, Union
from Services.UnifiedDocumentProcessor import UnifiedDocumentProcessor
from Common.gemini_config import GeminiConfig
from Common.constants import API_KEY
import re
import os

logger = logging.getLogger(__name__)


class UniversalDataExtractor:
    """
    Universal data extractor that extracts EVERYTHING from ANY document
    No document type limitations - extracts all visible data
    """
    
    def __init__(self, api_key: Optional[str] = None, config: Optional[GeminiConfig] = None):
        """
        Initialize the universal data extractor
        
        Args:
            api_key: Google AI API key (optional if config provided)
            config: Pre-configured GeminiConfig instance (optional)
        """
        self.unified_processor = UnifiedDocumentProcessor(api_key=api_key, config=config)
        logger.info("UniversalDataExtractor initialized")
    
    def extract_all_data(self, text: str, source_file: str = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Extract ALL data from ANY document text - completely general approach
        
        Args:
            text: Document text to process (any document type)
            source_file: Source file path (optional)
            context: Additional context information (optional)
            
        Returns:
            Complete extracted data from the document
        """
        try:
            logger.info(f"Starting universal data extraction from {len(text)} characters")
            
            # Add universal extraction context
            if context is None:
                context = {}
            context.update({
                "source_file": source_file,
                "extraction_mode": "universal_all_data",
                "document_type": "any",
                "focus": "extract_everything"
            })
            
            # Process with unified processor using universal approach
            result = self.unified_processor.process_document(text, context)
            
            # Extract and structure ALL data without limitations
            universal_result = self._extract_universal_data(result, source_file, text)
            
            logger.info(f"Universal extraction completed - {len(universal_result.get('all_extracted_data', {}))} total fields")
            return universal_result
            
        except Exception as e:
            logger.error(f"Error in universal data extraction: {str(e)}")
            return self._create_error_result(str(e), source_file)
    
    def _extract_universal_data(self, unified_result: Dict[str, Any], source_file: str, original_text: str) -> Dict[str, Any]:
        """
        Extract ALL data from unified result without any document type limitations
        
        Args:
            unified_result: Result from unified processor
            source_file: Source file path
            original_text: Original document text
            
        Returns:
            Complete universal data extraction results
        """
        try:
            # Extract base information
            doc_analysis = unified_result.get("document_analysis", {})
            extracted_data = unified_result.get("extracted_data", {})
            verification = unified_result.get("verification_results", {})
            metadata = unified_result.get("processing_metadata", {})
            
            # Extract ALL data without categorization limitations
            all_extracted_data = self._extract_everything(extracted_data, original_text)
            
            # Create comprehensive result
            result = {
                "status": "success",
                "source_file": source_file,
                "document_analysis": {
                    "document_type": doc_analysis.get("document_type", "unknown"),
                    "confidence_score": doc_analysis.get("confidence_score", 0.0),
                    "processing_method": "universal_extraction",
                    "key_indicators": doc_analysis.get("key_indicators", [])
                },
                "all_extracted_data": all_extracted_data,  # ALL data without categorization
                "raw_extracted_data": extracted_data,  # Original AI extraction
                "original_text": original_text,  # Keep original text for reference
                "verification_results": {
                    "is_genuine": verification.get("is_genuine", True),
                    "confidence_score": verification.get("confidence_score", 0.0),
                    "verification_summary": verification.get("verification_summary", "Document processed"),
                    "security_features_found": verification.get("security_features_found", []),
                    "warnings": verification.get("warnings", [])
                },
                "processing_metadata": {
                    "extraction_confidence": metadata.get("extraction_confidence", 0.0),
                    "processing_notes": "Universal extraction - all data extracted",
                    "unified_processing": True,
                    "prompt_version": "unified_v1",
                    "total_fields_extracted": len(all_extracted_data),
                    "extraction_method": "universal_comprehensive"
                },
                "data_analysis": self._analyze_extracted_data(all_extracted_data, original_text),
                "search_index": self._create_search_index(all_extracted_data)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting universal data: {str(e)}")
            return self._create_error_result(f"Universal data extraction failed: {str(e)}", source_file)
    
    def _extract_everything(self, extracted_data: Dict[str, Any], original_text: str) -> Dict[str, Any]:
        """
        Extract EVERYTHING from the data without any limitations or categorization
        
        Args:
            extracted_data: Data from AI processor
            original_text: Original document text
            
        Returns:
            All extracted data as flat key-value pairs
        """
        all_data = {}
        
        # Extract from AI processed data
        if extracted_data:
            all_data.update(self._flatten_data_structure(extracted_data))
        
        # Extract additional data from original text using pattern matching
        text_extractions = self._extract_from_text_patterns(original_text)
        all_data.update(text_extractions)
        
        # Extract any remaining visible data
        visible_extractions = self._extract_visible_data(original_text)
        all_data.update(visible_extractions)
        
        # Clean and deduplicate
        cleaned_data = {}
        for key, value in all_data.items():
            if value is not None and value != "" and str(value).strip():
                # Clean the key name
                clean_key = self._clean_field_name(key)
                if clean_key and clean_key not in cleaned_data:
                    cleaned_data[clean_key] = value
                elif clean_key and clean_key in cleaned_data:
                    # Handle duplicates by appending number
                    counter = 1
                    while f"{clean_key}_{counter}" in cleaned_data:
                        counter += 1
                    cleaned_data[f"{clean_key}_{counter}"] = value
        
        return cleaned_data
    
    def _flatten_data_structure(self, data: Any, prefix: str = "") -> Dict[str, Any]:
        """
        Flatten any data structure into key-value pairs
        
        Args:
            data: Any data structure
            prefix: Prefix for nested keys
            
        Returns:
            Flattened key-value pairs
        """
        flattened = {}
        
        if isinstance(data, dict):
            for key, value in data.items():
                new_key = f"{prefix}_{key}" if prefix else key
                if isinstance(value, (dict, list)):
                    flattened.update(self._flatten_data_structure(value, new_key))
                else:
                    flattened[new_key] = value
        elif isinstance(data, list):
            for i, item in enumerate(data):
                new_key = f"{prefix}_item_{i+1}" if prefix else f"item_{i+1}"
                if isinstance(item, (dict, list)):
                    flattened.update(self._flatten_data_structure(item, new_key))
                else:
                    flattened[new_key] = item
        else:
            if prefix:
                flattened[prefix] = data
        
        return flattened
    
    def _extract_from_text_patterns(self, text: str) -> Dict[str, Any]:
        """
        Extract data using pattern matching from original text
        
        Args:
            text: Original document text
            
        Returns:
            Extracted data from patterns
        """
        extractions = {}
        
        # Date patterns
        date_patterns = [
            (r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{4})\b', 'date'),
            (r'\b(\d{4}[/-]\d{1,2}[/-]\d{1,2})\b', 'date'),
            (r'\b(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})\b', 'date'),
            (r'\b(\d{1,2}\s+\d{1,2}\s+\d{4})\b', 'date'),
        ]
        
        for pattern, field_type in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for i, match in enumerate(matches):
                extractions[f"{field_type}_{i+1}"] = match
        
        # Number patterns
        number_patterns = [
            (r'\b(\d{10,16})\b', 'number'),
            (r'\b([A-Z]{2,5}\d{4,10}[A-Z]?)\b', 'identifier'),
            (r'\b(\d{3}-\d{3}-\d{4})\b', 'phone'),
            (r'\b(\d{3}\.\d{3}\.\d{4})\b', 'phone'),
            (r'\b(\d{10})\b', 'phone'),
        ]
        
        for pattern, field_type in number_patterns:
            matches = re.findall(pattern, text)
            for i, match in enumerate(matches):
                extractions[f"{field_type}_{i+1}"] = match
        
        # Email patterns
        email_matches = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        for i, email in enumerate(email_matches):
            extractions[f"email_{i+1}"] = email
        
        # Name patterns
        name_patterns = [
            (r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b', 'name'),
            (r'\b([A-Z][A-Z\s]+)\b', 'name_uppercase'),
        ]
        
        for pattern, field_type in name_patterns:
            matches = re.findall(pattern, text)
            for i, match in enumerate(matches):
                if len(match.split()) >= 2:  # At least first and last name
                    extractions[f"{field_type}_{i+1}"] = match
        
        # Address patterns
        address_patterns = [
            (r'\b(\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr))\b', 'address'),
            (r'\b([A-Za-z\s]+,\s*[A-Z]{2}\s*\d{5})\b', 'address'),
        ]
        
        for pattern, field_type in address_patterns:
            matches = re.findall(pattern, text)
            for i, match in enumerate(matches):
                extractions[f"{field_type}_{i+1}"] = match
        
        # Amount patterns
        amount_patterns = [
            (r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', 'amount_dollar'),
            (r'\b(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:dollars?|USD)\b', 'amount_dollar'),
            (r'\b(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\b', 'amount'),
        ]
        
        for pattern, field_type in amount_patterns:
            matches = re.findall(pattern, text)
            for i, match in enumerate(matches):
                extractions[f"{field_type}_{i+1}"] = match
        
        return extractions
    
    def _extract_visible_data(self, text: str) -> Dict[str, Any]:
        """
        Extract any other visible data from text
        
        Args:
            text: Original document text
            
        Returns:
            Additional extracted data
        """
        extractions = {}
        
        # Extract lines that look like key-value pairs
        lines = text.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if ':' in line and len(line) > 5:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    if key and value and len(key) < 50 and len(value) < 200:
                        clean_key = self._clean_field_name(key)
                        if clean_key:
                            extractions[f"line_{i+1}_{clean_key}"] = value
        
        # Extract any words that look like codes or identifiers
        code_patterns = [
            r'\b[A-Z]{2,8}\d{2,8}\b',  # Like ABC12345
            r'\b[A-Z]{3,5}-\d{3,8}\b',  # Like ABC-12345
            r'\b\d{3,8}-[A-Z]{2,5}\b',  # Like 12345-ABC
        ]
        
        for pattern in code_patterns:
            matches = re.findall(pattern, text)
            for i, match in enumerate(matches):
                extractions[f"code_{i+1}"] = match
        
        # Extract any text that looks like a title or heading
        lines = text.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if (line.isupper() and len(line) > 5 and len(line) < 100 and 
                not line.isdigit() and not re.match(r'^\d+$', line)):
                extractions[f"heading_{i+1}"] = line
        
        return extractions
    
    def _clean_field_name(self, field_name: str) -> str:
        """
        Clean field name for consistent naming
        
        Args:
            field_name: Raw field name
            
        Returns:
            Cleaned field name
        """
        if not field_name:
            return ""
        
        # Remove special characters and normalize
        cleaned = re.sub(r'[^\w\s]', '', field_name)
        cleaned = re.sub(r'\s+', '_', cleaned.strip())
        cleaned = cleaned.lower()
        
        # Remove common prefixes/suffixes
        cleaned = re.sub(r'^(the_|a_|an_)', '', cleaned)
        cleaned = re.sub(r'(_the_|_a_|_an_)$', '', cleaned)
        
        return cleaned
    
    def _analyze_extracted_data(self, extracted_data: Dict[str, Any], original_text: str) -> Dict[str, Any]:
        """
        Analyze the extracted data for insights
        
        Args:
            extracted_data: All extracted data
            original_text: Original document text
            
        Returns:
            Analysis results
        """
        analysis = {
            "total_fields": len(extracted_data),
            "field_types": {},
            "data_distribution": {},
            "text_analysis": {}
        }
        
        # Analyze field types
        for key, value in extracted_data.items():
            if isinstance(value, str):
                if '@' in value:
                    analysis["field_types"]["email"] = analysis["field_types"].get("email", 0) + 1
                elif re.match(r'\d{1,2}[/-]\d{1,2}[/-]\d{4}', value):
                    analysis["field_types"]["date"] = analysis["field_types"].get("date", 0) + 1
                elif re.match(r'\d{10,16}', value):
                    analysis["field_types"]["number"] = analysis["field_types"].get("number", 0) + 1
                elif re.match(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+', value):
                    analysis["field_types"]["name"] = analysis["field_types"].get("name", 0) + 1
                else:
                    analysis["field_types"]["text"] = analysis["field_types"].get("text", 0) + 1
        
        # Analyze text
        analysis["text_analysis"] = {
            "total_characters": len(original_text),
            "total_words": len(original_text.split()),
            "total_lines": len(original_text.split('\n')),
            "estimated_pages": len(original_text) // 2000 + 1
        }
        
        return analysis
    
    def _create_search_index(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create search index for all extracted data
        
        Args:
            extracted_data: All extracted data
            
        Returns:
            Search index
        """
        search_index = {
            "all_fields": list(extracted_data.keys()),
            "all_values": list(extracted_data.values()),
            "field_value_pairs": extracted_data,
            "searchable_text": " ".join([f"{k}: {v}" for k, v in extracted_data.items() if v])
        }
        
        return search_index
    
    def _create_error_result(self, error_message: str, source_file: str = None) -> Dict[str, Any]:
        """
        Create error result structure
        
        Args:
            error_message: Error message
            source_file: Source file path
            
        Returns:
            Error result structure
        """
        return {
            "status": "error",
            "source_file": source_file,
            "error": {
                "message": error_message,
                "type": "extraction_error"
            },
            "all_extracted_data": {},
            "raw_extracted_data": {},
            "original_text": "",
            "verification_results": {},
            "processing_metadata": {
                "extraction_confidence": 0.0,
                "processing_notes": f"Extraction failed: {error_message}",
                "unified_processing": False
            },
            "data_analysis": {},
            "search_index": {}
        }
    
    def search_data(self, result: Dict[str, Any], search_term: str) -> Dict[str, Any]:
        """
        Search through all extracted data
        
        Args:
            result: Extraction result
            search_term: Search term
            
        Returns:
            Search results
        """
        if result.get("status") == "error":
            return {"matches": [], "search_term": search_term}
        
        all_data = result.get("all_extracted_data", {})
        matches = []
        search_term_lower = search_term.lower()
        
        for field, value in all_data.items():
            if (search_term_lower in field.lower() or 
                search_term_lower in str(value).lower()):
                matches.append({
                    "field": field,
                    "value": value,
                    "match_type": "field" if search_term_lower in field.lower() else "value"
                })
        
        return {
            "matches": matches,
            "search_term": search_term,
            "total_matches": len(matches)
        }
    
    def get_data_summary(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get summary of all extracted data
        
        Args:
            result: Extraction result
            
        Returns:
            Summary information
        """
        if result.get("status") == "error":
            return {
                "status": "error",
                "message": result.get("error", {}).get("message", "Unknown error"),
                "source_file": result.get("source_file")
            }
        
        all_data = result.get("all_extracted_data", {})
        analysis = result.get("data_analysis", {})
        
        return {
            "status": "success",
            "source_file": result.get("source_file"),
            "document_type": result.get("document_analysis", {}).get("document_type", "unknown"),
            "confidence_score": result.get("document_analysis", {}).get("confidence_score", 0.0),
            "total_fields_extracted": len(all_data),
            "field_types_found": analysis.get("field_types", {}),
            "text_analysis": analysis.get("text_analysis", {}),
            "verification_status": result.get("verification_results", {}).get("is_genuine", True),
            "extraction_confidence": result.get("processing_metadata", {}).get("extraction_confidence", 0.0)
        } 