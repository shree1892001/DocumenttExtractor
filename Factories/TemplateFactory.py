"""
TemplateFactory - Factory for template-related operations.
Handles document type detection, template suggestions, and field extraction logic.
"""

import re
from typing import Dict, Any, List
from Logging_file.logging_file import custom_logger


class TemplateFactory:
    """Factory class for template-related operations and document analysis"""
    
    @staticmethod
    def determine_document_type(template_name: str) -> str:
        """
        Determine document type from template name
        
        Args:
            template_name: Name of the template
            
        Returns:
            Document type string
        """
        template_lower = template_name.lower()
        
        if "aadhaar" in template_lower or "aadhar" in template_lower:
            return "aadhaar_card"
        elif "pan" in template_lower:
            return "pan_card"
        elif "license" in template_lower:
            if "florida" in template_lower:
                return "florida_driving_license"
            elif "indian" in template_lower:
                return "indian_driving_license"
            else:
                return "driving_license"
        elif "passport" in template_lower:
            return "passport"
        elif "corp" in template_lower or "newmexico" in template_lower:
            return "corporate_document"
        else:
            return "unknown"
    
    @staticmethod
    def analyze_document_for_template_suggestion(document_info: Dict[str, Any], extracted_text: str) -> Dict[str, Any]:
        """
        Analyze document content to suggest template creation
        
        Args:
            document_info: Information about the document
            extracted_text: Text extracted from the document
            
        Returns:
            Dict containing template suggestion details
        """
        try:
            # Extract key information from the document
            text_lower = extracted_text.lower()

            # Suggest document type based on content analysis
            suggested_type = "other"
            suggested_name = "Custom Template"
            suggested_description = "Custom document template"
            suggested_fields = ["document_number", "name", "date"]

            # Analyze content for document type patterns
            if any(keyword in text_lower for keyword in ["aadhaar", "aadhar", "uid"]):
                suggested_type = "aadhaar_card"
                suggested_name = "Custom Aadhaar Template"
                suggested_description = "Custom Aadhaar card template"
                suggested_fields = ["name", "aadhaar_number", "date_of_birth", "address"]

            elif any(keyword in text_lower for keyword in ["pan", "permanent account", "income tax"]):
                suggested_type = "pan_card"
                suggested_name = "Custom PAN Template"
                suggested_description = "Custom PAN card template"
                suggested_fields = ["name", "fathers_name", "pan_number", "date_of_birth"]

            elif any(keyword in text_lower for keyword in ["driving", "license", "licence", "vehicle"]):
                suggested_type = "driving_license"
                suggested_name = "Custom License Template"
                suggested_description = "Custom driving license template"
                suggested_fields = ["name", "license_number", "date_of_birth", "address", "vehicle_class"]

            elif any(keyword in text_lower for keyword in ["passport", "travel", "nationality"]):
                suggested_type = "passport"
                suggested_name = "Custom Passport Template"
                suggested_description = "Custom passport template"
                suggested_fields = ["name", "passport_number", "date_of_birth", "nationality"]

            elif any(keyword in text_lower for keyword in ["company", "corporation", "business", "registration"]):
                suggested_type = "corporate_document"
                suggested_name = "Custom Corporate Template"
                suggested_description = "Custom corporate document template"
                suggested_fields = ["company_name", "registration_number", "address", "incorporation_date"]

            # Extract potential field values from the text
            extracted_fields = TemplateFactory.extract_potential_fields(extracted_text)

            return {
                "suggested_name": suggested_name,
                "suggested_type": suggested_type,
                "suggested_description": suggested_description,
                "suggested_fields": suggested_fields,
                "extracted_sample_data": extracted_fields,
                "confidence": TemplateFactory.calculate_suggestion_confidence(text_lower, suggested_type)
            }

        except Exception as e:
            custom_logger.error(f"Error analyzing document for template suggestion: {str(e)}")
            return {
                "suggested_name": "Custom Template",
                "suggested_type": "other",
                "suggested_description": "Custom document template",
                "suggested_fields": ["document_number", "name", "date"],
                "extracted_sample_data": {},
                "confidence": 0.5
            }
    
    @staticmethod
    def extract_potential_fields(text: str) -> Dict[str, List[str]]:
        """
        Extract potential field values from document text
        
        Args:
            text: Text content to analyze
            
        Returns:
            Dict containing extracted field values
        """
        fields = {}

        # Extract dates
        date_patterns = [
            r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{4})\b',
            r'\b(\d{4}[/-]\d{1,2}[/-]\d{1,2})\b',
            r'\b(\d{1,2}\s+\w+\s+\d{4})\b'
        ]

        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            if matches:
                fields["dates_found"] = matches[:3]  # First 3 dates
                break

        # Extract numbers (potential IDs)
        number_patterns = [
            r'\b([A-Z]{3,5}\d{4,10}[A-Z]?)\b',  # Alphanumeric IDs
            r'\b(\d{10,16})\b'  # Long numbers
        ]

        for pattern in number_patterns:
            matches = re.findall(pattern, text)
            if matches:
                fields["numbers_found"] = matches[:3]  # First 3 numbers
                break

        # Extract potential names (capitalized words)
        name_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        names = re.findall(name_pattern, text)
        if names:
            fields["names_found"] = [name for name in names if len(name.split()) >= 2][:3]

        return fields
    
    @staticmethod
    def calculate_suggestion_confidence(text: str, suggested_type: str) -> float:
        """
        Calculate confidence score for template suggestion
        
        Args:
            text: Text content to analyze
            suggested_type: The suggested document type
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        confidence = 0.5  # Base confidence

        # Type-specific keywords boost confidence
        type_keywords = {
            "aadhaar_card": ["aadhaar", "aadhar", "uid", "unique identification"],
            "pan_card": ["pan", "permanent account", "income tax"],
            "driving_license": ["driving", "license", "licence", "vehicle"],
            "passport": ["passport", "travel", "nationality"],
            "corporate_document": ["company", "corporation", "business", "registration"]
        }

        if suggested_type in type_keywords:
            keyword_count = sum(1 for keyword in type_keywords[suggested_type] if keyword in text)
            confidence += min(keyword_count * 0.1, 0.3)  # Max 0.3 boost

        # Length and structure boost confidence
        if len(text) > 100:
            confidence += 0.1
        if len(text) > 500:
            confidence += 0.1

        return min(confidence, 0.95)  # Cap at 95%
    
    @staticmethod
    def get_document_type_fields(doc_type: str) -> List[str]:
        """
        Get expected fields for a document type
        
        Args:
            doc_type: Document type
            
        Returns:
            List of expected field names
        """
        field_mapping = {
            "aadhaar_card": ["name", "aadhaar_number", "date_of_birth", "address", "gender"],
            "pan_card": ["name", "fathers_name", "pan_number", "date_of_birth"],
            "driving_license": ["name", "license_number", "date_of_birth", "address", "vehicle_class"],
            "passport": ["name", "passport_number", "date_of_birth", "nationality", "place_of_birth"],
            "corporate_document": ["company_name", "registration_number", "address", "incorporation_date"]
        }
        
        return field_mapping.get(doc_type, ["document_number", "name", "date"])
