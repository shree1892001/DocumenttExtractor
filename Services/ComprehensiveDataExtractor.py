"""
ComprehensiveDataExtractor - Enhanced service for extracting ALL data from documents
in a structured format using the UnifiedDocumentProcessor.
"""

import json
import logging
from typing import Dict, Any, Optional, List, Union
from Services.UnifiedDocumentProcessor import UnifiedDocumentProcessor
from Common.gemini_config import GeminiConfig
from Common.constants import API_KEY

logger = logging.getLogger(__name__)


class ComprehensiveDataExtractor:
    """
    Comprehensive data extractor that extracts ALL information from documents
    and structures it in a comprehensive, searchable format.
    """
    
    def __init__(self, api_key: Optional[str] = None, config: Optional[GeminiConfig] = None):
        """
        Initialize the comprehensive data extractor
        
        Args:
            api_key: Google AI API key (optional if config provided)
            config: Pre-configured GeminiConfig instance (optional)
        """
        self.unified_processor = UnifiedDocumentProcessor(api_key=api_key, config=config)
        logger.info("ComprehensiveDataExtractor initialized")
    
    def extract_all_data(self, text: str, source_file: str = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Extract ALL data from document text in a comprehensive structured format
        
        Args:
            text: Document text to process
            source_file: Source file path (optional)
            context: Additional context information (optional)
            
        Returns:
            Comprehensive structured data extraction results
        """
        try:
            logger.info(f"Starting comprehensive data extraction from {len(text)} characters")
            
            # Add source file context if provided
            if source_file:
                if context is None:
                    context = {}
                context["source_file"] = source_file
                context["extraction_mode"] = "comprehensive_all_data"
            
            # Process with unified processor
            result = self.unified_processor.process_document(text, context)
            
            # Structure and enhance the extracted data
            structured_result = self._structure_extracted_data(result, source_file)
            
            logger.info(f"Comprehensive extraction completed - {len(structured_result.get('structured_data', {}))} structured fields")
            return structured_result
            
        except Exception as e:
            logger.error(f"Error in comprehensive data extraction: {str(e)}")
            return self._create_error_result(str(e), source_file)
    
    def _structure_extracted_data(self, unified_result: Dict[str, Any], source_file: str = None) -> Dict[str, Any]:
        """
        Structure the extracted data into a comprehensive, organized format
        
        Args:
            unified_result: Result from unified processor
            source_file: Source file path
            
        Returns:
            Structured data with comprehensive organization
        """
        try:
            # Extract base information
            doc_analysis = unified_result.get("document_analysis", {})
            extracted_data = unified_result.get("extracted_data", {})
            verification = unified_result.get("verification_results", {})
            metadata = unified_result.get("processing_metadata", {})
            
            # Create comprehensive structured data
            structured_data = self._create_structured_sections(extracted_data)
            
            # Create the comprehensive result
            result = {
                "status": "success",
                "source_file": source_file,
                "document_analysis": {
                    "document_type": doc_analysis.get("document_type", "unknown"),
                    "confidence_score": doc_analysis.get("confidence_score", 0.0),
                    "processing_method": doc_analysis.get("processing_method", "comprehensive_extraction"),
                    "key_indicators": doc_analysis.get("key_indicators", [])
                },
                "structured_data": structured_data,
                "raw_extracted_data": extracted_data,  # Keep original for reference
                "verification_results": {
                    "is_genuine": verification.get("is_genuine", True),
                    "confidence_score": verification.get("confidence_score", 0.0),
                    "verification_summary": verification.get("verification_summary", "Document appears genuine"),
                    "security_features_found": verification.get("security_features_found", []),
                    "warnings": verification.get("warnings", [])
                },
                "processing_metadata": {
                    "extraction_confidence": metadata.get("extraction_confidence", 0.0),
                    "processing_notes": metadata.get("processing_notes", "Comprehensive extraction completed"),
                    "unified_processing": True,
                    "prompt_version": "unified_v1",
                    "total_fields_extracted": len(structured_data),
                    "sections_identified": list(structured_data.keys())
                },
                "searchable_data": self._create_searchable_data(structured_data),
                "summary_statistics": self._create_summary_statistics(structured_data)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error structuring extracted data: {str(e)}")
            return self._create_error_result(f"Data structuring failed: {str(e)}", source_file)
    
    def _create_structured_sections(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create organized sections from extracted data
        
        Args:
            extracted_data: Raw extracted data
            
        Returns:
            Organized data sections
        """
        structured = {
            "personal_information": {},
            "document_identifiers": {},
            "contact_information": {},
            "address_information": {},
            "employment_information": {},
            "educational_information": {},
            "financial_information": {},
            "medical_information": {},
            "vehicle_information": {},
            "legal_information": {},
            "government_information": {},
            "security_features": {},
            "dates_and_timelines": {},
            "organizational_information": {},
            "technical_information": {},
            "additional_information": {}
        }
        
        # Categorize all extracted fields
        for key, value in extracted_data.items():
            if value is None or value == "" or str(value).lower() in ['null', 'not_present', 'n/a', 'none', 'unknown']:
                continue
                
            category = self._categorize_field(key, value)
            if category in structured:
                structured[category][key] = value
            else:
                structured["additional_information"][key] = value
        
        # Remove empty sections
        structured = {k: v for k, v in structured.items() if v}
        
        return structured
    
    def _categorize_field(self, key: str, value: Any) -> str:
        """
        Categorize a field based on its key and value
        
        Args:
            key: Field key
            value: Field value
            
        Returns:
            Category name
        """
        key_lower = key.lower()
        value_str = str(value).lower()
        
        # Personal Information
        if any(term in key_lower for term in ['name', 'first', 'last', 'middle', 'full', 'father', 'mother', 'spouse', 'guardian', 'next of kin', 'beneficiary']):
            return "personal_information"
        
        # Document Identifiers
        if any(term in key_lower for term in ['id', 'number', 'license', 'passport', 'account', 'reference', 'serial', 'certificate', 'registration', 'permit']):
            return "document_identifiers"
        
        # Contact Information
        if any(term in key_lower for term in ['phone', 'mobile', 'email', 'fax', 'website', 'social', 'contact']):
            return "contact_information"
        
        # Address Information
        if any(term in key_lower for term in ['address', 'street', 'city', 'state', 'country', 'postal', 'zip', 'location', 'place']):
            return "address_information"
        
        # Employment Information
        if any(term in key_lower for term in ['job', 'title', 'position', 'company', 'employer', 'work', 'salary', 'employee', 'department', 'designation']):
            return "employment_information"
        
        # Educational Information
        if any(term in key_lower for term in ['school', 'college', 'university', 'degree', 'grade', 'education', 'academic', 'student', 'transcript', 'diploma']):
            return "educational_information"
        
        # Financial Information
        if any(term in key_lower for term in ['amount', 'balance', 'income', 'tax', 'financial', 'bank', 'credit', 'loan', 'payment', 'salary', 'wage']):
            return "financial_information"
        
        # Medical Information
        if any(term in key_lower for term in ['medical', 'health', 'patient', 'doctor', 'hospital', 'blood', 'allergy', 'medication', 'diagnosis', 'treatment']):
            return "medical_information"
        
        # Vehicle Information
        if any(term in key_lower for term in ['vehicle', 'car', 'truck', 'motorcycle', 'engine', 'chassis', 'model', 'make', 'year', 'plate', 'registration']):
            return "vehicle_information"
        
        # Legal Information
        if any(term in key_lower for term in ['legal', 'case', 'court', 'judge', 'lawyer', 'attorney', 'law', 'legal status', 'jurisdiction']):
            return "legal_information"
        
        # Government Information
        if any(term in key_lower for term in ['government', 'official', 'authority', 'department', 'agency', 'ministry', 'office', 'bureau']):
            return "government_information"
        
        # Security Features
        if any(term in key_lower for term in ['security', 'watermark', 'seal', 'signature', 'stamp', 'hologram', 'security feature']):
            return "security_features"
        
        # Dates and Timelines
        if any(term in key_lower for term in ['date', 'time', 'year', 'month', 'day', 'expiry', 'valid', 'issue', 'birth', 'employment', 'graduation']):
            return "dates_and_timelines"
        
        # Organizational Information
        if any(term in key_lower for term in ['organization', 'institution', 'association', 'society', 'club', 'committee', 'board', 'council']):
            return "organizational_information"
        
        # Technical Information
        if any(term in key_lower for term in ['technical', 'file', 'version', 'code', 'barcode', 'qr', 'serial', 'model', 'technical specification']):
            return "technical_information"
        
        return "additional_information"
    
    def _create_searchable_data(self, structured_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create searchable data structure for easy querying
        
        Args:
            structured_data: Structured data sections
            
        Returns:
            Searchable data structure
        """
        searchable = {
            "all_fields": {},
            "field_types": {
                "names": [],
                "numbers": [],
                "dates": [],
                "addresses": [],
                "emails": [],
                "phones": [],
                "amounts": [],
                "identifiers": []
            },
            "section_index": {}
        }
        
        # Flatten all fields for search
        for section, fields in structured_data.items():
            searchable["section_index"][section] = list(fields.keys())
            
            for field, value in fields.items():
                searchable["all_fields"][field] = value
                
                # Categorize by type
                if self._is_name_field(field, value):
                    searchable["field_types"]["names"].append(field)
                elif self._is_number_field(field, value):
                    searchable["field_types"]["numbers"].append(field)
                elif self._is_date_field(field, value):
                    searchable["field_types"]["dates"].append(field)
                elif self._is_address_field(field, value):
                    searchable["field_types"]["addresses"].append(field)
                elif self._is_email_field(field, value):
                    searchable["field_types"]["emails"].append(field)
                elif self._is_phone_field(field, value):
                    searchable["field_types"]["phones"].append(field)
                elif self._is_amount_field(field, value):
                    searchable["field_types"]["amounts"].append(field)
                elif self._is_identifier_field(field, value):
                    searchable["field_types"]["identifiers"].append(field)
        
        return searchable
    
    def _is_name_field(self, field: str, value: Any) -> bool:
        """Check if field contains name information"""
        name_indicators = ['name', 'first', 'last', 'middle', 'full', 'father', 'mother', 'spouse', 'guardian']
        return any(indicator in field.lower() for indicator in name_indicators)
    
    def _is_number_field(self, field: str, value: Any) -> bool:
        """Check if field contains numeric information"""
        number_indicators = ['number', 'id', 'code', 'serial', 'reference']
        return any(indicator in field.lower() for indicator in number_indicators)
    
    def _is_date_field(self, field: str, value: Any) -> bool:
        """Check if field contains date information"""
        date_indicators = ['date', 'time', 'year', 'month', 'day', 'expiry', 'valid', 'issue', 'birth']
        return any(indicator in field.lower() for indicator in date_indicators)
    
    def _is_address_field(self, field: str, value: Any) -> bool:
        """Check if field contains address information"""
        address_indicators = ['address', 'street', 'city', 'state', 'country', 'postal', 'zip', 'location']
        return any(indicator in field.lower() for indicator in address_indicators)
    
    def _is_email_field(self, field: str, value: Any) -> bool:
        """Check if field contains email information"""
        return '@' in str(value) or 'email' in field.lower()
    
    def _is_phone_field(self, field: str, value: Any) -> bool:
        """Check if field contains phone information"""
        phone_indicators = ['phone', 'mobile', 'tel', 'fax']
        return any(indicator in field.lower() for indicator in phone_indicators)
    
    def _is_amount_field(self, field: str, value: Any) -> bool:
        """Check if field contains amount information"""
        amount_indicators = ['amount', 'balance', 'income', 'salary', 'payment', 'cost', 'price']
        return any(indicator in field.lower() for indicator in amount_indicators)
    
    def _is_identifier_field(self, field: str, value: Any) -> bool:
        """Check if field contains identifier information"""
        identifier_indicators = ['license', 'passport', 'account', 'certificate', 'registration', 'permit']
        return any(indicator in field.lower() for indicator in identifier_indicators)
    
    def _create_summary_statistics(self, structured_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create summary statistics for the extracted data
        
        Args:
            structured_data: Structured data sections
            
        Returns:
            Summary statistics
        """
        stats = {
            "total_sections": len(structured_data),
            "total_fields": sum(len(fields) for fields in structured_data.values()),
            "sections_with_data": len([s for s in structured_data.values() if s]),
            "field_distribution": {section: len(fields) for section, fields in structured_data.items()},
            "data_completeness": {}
        }
        
        # Calculate completeness for each section
        for section, fields in structured_data.items():
            if fields:
                non_empty_fields = len([f for f in fields.values() if f and str(f).strip()])
                stats["data_completeness"][section] = {
                    "total_fields": len(fields),
                    "non_empty_fields": non_empty_fields,
                    "completeness_percentage": round((non_empty_fields / len(fields)) * 100, 2) if fields else 0
                }
        
        return stats
    
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
            "structured_data": {},
            "raw_extracted_data": {},
            "verification_results": {},
            "processing_metadata": {
                "extraction_confidence": 0.0,
                "processing_notes": f"Extraction failed: {error_message}",
                "unified_processing": False
            },
            "searchable_data": {},
            "summary_statistics": {
                "total_sections": 0,
                "total_fields": 0,
                "sections_with_data": 0,
                "field_distribution": {},
                "data_completeness": {}
            }
        }
    
    def get_extraction_summary(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get a summary of the extraction results
        
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
        
        structured_data = result.get("structured_data", {})
        stats = result.get("summary_statistics", {})
        
        return {
            "status": "success",
            "source_file": result.get("source_file"),
            "document_type": result.get("document_analysis", {}).get("document_type", "unknown"),
            "confidence_score": result.get("document_analysis", {}).get("confidence_score", 0.0),
            "total_sections": stats.get("total_sections", 0),
            "total_fields": stats.get("total_fields", 0),
            "sections_identified": list(structured_data.keys()),
            "verification_status": result.get("verification_results", {}).get("is_genuine", True),
            "extraction_confidence": result.get("processing_metadata", {}).get("extraction_confidence", 0.0)
        }
    
    def search_fields(self, result: Dict[str, Any], search_term: str) -> Dict[str, Any]:
        """
        Search for specific fields in the extracted data
        
        Args:
            result: Extraction result
            search_term: Search term
            
        Returns:
            Matching fields
        """
        if result.get("status") == "error":
            return {"matches": [], "search_term": search_term}
        
        searchable_data = result.get("searchable_data", {})
        all_fields = searchable_data.get("all_fields", {})
        
        matches = []
        search_term_lower = search_term.lower()
        
        for field, value in all_fields.items():
            if (search_term_lower in field.lower() or 
                search_term_lower in str(value).lower()):
                matches.append({
                    "field": field,
                    "value": value,
                    "section": self._find_field_section(field, result.get("structured_data", {}))
                })
        
        return {
            "matches": matches,
            "search_term": search_term,
            "total_matches": len(matches)
        }
    
    def _find_field_section(self, field: str, structured_data: Dict[str, Any]) -> str:
        """Find which section a field belongs to"""
        for section, fields in structured_data.items():
            if field in fields:
                return section
        return "unknown" 