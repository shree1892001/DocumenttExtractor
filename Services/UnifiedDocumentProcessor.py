"""
UnifiedDocumentProcessor - Single optimized processor for all document operations.
Uses the unified prompt to handle detection, extraction, and verification in one pass.
"""

import json
import logging
from typing import Dict, Any, Optional
from Common.constants import UNIFIED_DOCUMENT_PROCESSING_PROMPT
from Common.base_text_processor import DocumentTextProcessor
from Common.gemini_config import GeminiConfig

logger = logging.getLogger(__name__)


class UnifiedDocumentProcessor:
    """
    Unified document processor that handles detection, extraction, and verification
    in a single optimized pass using the unified prompt.
    """
    
    def __init__(self, api_key: Optional[str] = None, config: Optional[GeminiConfig] = None):
        """
        Initialize the unified document processor
        
        Args:
            api_key: Google AI API key (optional if config provided)
            config: Pre-configured GeminiConfig instance (optional)
        """
        if config is None:
            config = GeminiConfig.create_text_processor_config(api_key)
            # Optimize for document processing
            config.update_generation_config(
                temperature=0.05,  # Very low for consistent extraction
                top_p=0.9,
                top_k=40,
                max_output_tokens=16384  # Larger for comprehensive output
            )
        
        self.text_processor = DocumentTextProcessor(config=config)
        logger.info("UnifiedDocumentProcessor initialized")
    
    def process_document(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process document text using the unified prompt for complete analysis
        
        Args:
            text: Document text to process
            context: Optional additional context information
            
        Returns:
            Comprehensive document analysis results
        """
        try:
            # Prepare the unified prompt with the text
            prompt = UNIFIED_DOCUMENT_PROCESSING_PROMPT.format(text=text)
            
            # Add context if provided
            if context:
                context_str = "\n\n**ADDITIONAL CONTEXT**:\n"
                for key, value in context.items():
                    context_str += f"- {key}: {value}\n"
                prompt += context_str
            
            # Process with the unified prompt
            logger.info(f"Processing document text ({len(text)} characters)")
            logger.debug(f"Prompt length: {len(prompt)} characters")

            try:
                response = self.text_processor.process_text(text, prompt)
                logger.debug(f"Received response length: {len(response) if response else 0}")
            except Exception as e:
                logger.error(f"Error calling text processor: {str(e)}")
                return self._create_error_response(
                    "text_processor_error",
                    f"Text processor failed: {str(e)}"
                )

            # Check if response is empty or None
            if not response or not response.strip():
                logger.error("Received empty response from text processor")
                return self._create_error_response(
                    "empty_response",
                    "AI model returned empty response",
                    {"prompt_length": len(prompt), "text_length": len(text)}
                )

            # Clean and parse the JSON response
            try:
                # Clean the response - remove markdown formatting and extra whitespace
                cleaned_response = self._clean_json_response(response)
                logger.debug(f"Cleaned response length: {len(cleaned_response)}")

                if not cleaned_response:
                    logger.error("Response became empty after cleaning")
                    return self._create_error_response(
                        "empty_cleaned_response",
                        "Response became empty after cleaning",
                        {"raw_response": response[:500]}
                    )

                result = json.loads(cleaned_response)

                # Validate the response structure
                if not self._validate_response_structure(result):
                    logger.warning("Response structure validation failed, attempting to fix")
                    result = self._fix_response_structure(result)

                # Add processing metadata
                if "processing_metadata" not in result:
                    result["processing_metadata"] = {}
                result["processing_metadata"]["unified_processing"] = True
                result["processing_metadata"]["prompt_version"] = "unified_v1"

                logger.info("Document processing completed successfully")
                return result

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {str(e)}")
                logger.error(f"Raw response (first 500 chars): {response[:500]}")

                # Try to extract JSON from the response if it's embedded in text
                extracted_json = self._extract_json_from_text(response)
                if extracted_json:
                    try:
                        result = json.loads(extracted_json)
                        logger.info("Successfully extracted JSON from text response")

                        # Validate and fix structure
                        if not self._validate_response_structure(result):
                            result = self._fix_response_structure(result)

                        # Add metadata
                        if "processing_metadata" not in result:
                            result["processing_metadata"] = {}
                        result["processing_metadata"]["unified_processing"] = True
                        result["processing_metadata"]["prompt_version"] = "unified_v1"
                        result["processing_metadata"]["response_extracted"] = True

                        return result
                    except json.JSONDecodeError:
                        logger.error("Failed to parse extracted JSON as well")

                # Try fallback with simpler prompt
                logger.warning("Unified prompt failed, trying fallback approach")
                fallback_result = self._process_with_fallback(text, context)
                if fallback_result:
                    return fallback_result

                return self._create_error_response(
                    "json_parse_error",
                    f"Failed to parse AI response as JSON: {str(e)}",
                    {"raw_response": response[:500], "cleaned_response": cleaned_response[:500] if 'cleaned_response' in locals() else "N/A"}
                )
        
        except Exception as e:
            logger.error(f"Error in unified document processing: {str(e)}")
            return self._create_error_response(
                "processing_error",
                f"Document processing failed: {str(e)}"
            )
    
    def extract_specific_fields(self, text: str, field_list: list, document_type: str = None) -> Dict[str, Any]:
        """
        Extract specific fields from document using targeted processing
        
        Args:
            text: Document text
            field_list: List of specific fields to extract
            document_type: Known document type (optional)
            
        Returns:
            Extracted field data
        """
        try:
            # Create focused context for specific field extraction
            context = {
                "extraction_mode": "targeted_fields",
                "target_fields": field_list,
                "focus_areas": field_list
            }
            
            if document_type:
                context["known_document_type"] = document_type
            
            result = self.process_document(text, context)
            
            # Extract only the requested fields
            extracted_data = result.get("extracted_data", {})
            specific_fields = {}
            
            for field in field_list:
                # Search through all sections for the field
                field_value = self._find_field_in_data(extracted_data, field)
                if field_value is not None:
                    specific_fields[field] = field_value
            
            return {
                "status": "success",
                "extracted_fields": specific_fields,
                "confidence": result.get("processing_metadata", {}).get("extraction_confidence", 0.0),
                "document_type": result.get("document_analysis", {}).get("document_type", "unknown")
            }
            
        except Exception as e:
            logger.error(f"Error in specific field extraction: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "extracted_fields": {}
            }
    
    def verify_document_only(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform verification on already extracted document data
        
        Args:
            extracted_data: Previously extracted document data
            
        Returns:
            Verification results
        """
        try:
            # Convert extracted data to text for verification
            data_text = json.dumps(extracted_data, indent=2)
            
            context = {
                "processing_mode": "verification_only",
                "skip_extraction": True,
                "focus_on_verification": True
            }
            
            result = self.process_document(data_text, context)
            
            # Return only verification results
            return {
                "status": "success",
                "verification_results": result.get("verification_results", {}),
                "authenticity_assessment": result.get("verification_results", {}).get("authenticity_assessment", {}),
                "quality_checks": result.get("verification_results", {}).get("quality_checks", {}),
                "flags_and_warnings": result.get("verification_results", {}).get("flags_and_warnings", []),
                "recommendations": result.get("verification_results", {}).get("recommendations", [])
            }
            
        except Exception as e:
            logger.error(f"Error in document verification: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "verification_results": {}
            }
    
    def _validate_response_structure(self, response: Dict[str, Any]) -> bool:
        """Validate that the response has the expected structure"""
        required_sections = [
            "document_analysis",
            "extracted_data", 
            "verification_results",
            "processing_metadata"
        ]
        
        return all(section in response for section in required_sections)
    
    def _fix_response_structure(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Fix incomplete response structure"""
        fixed_response = {
            "document_analysis": response.get("document_analysis", {}),
            "extracted_data": response.get("extracted_data", {}),
            "verification_results": response.get("verification_results", {}),
            "processing_metadata": response.get("processing_metadata", {})
        }
        
        # Ensure minimum required fields
        if not fixed_response["document_analysis"]:
            fixed_response["document_analysis"] = {
                "document_type": "unknown",
                "confidence_score": 0.0,
                "processing_method": "unified_prompt"
            }
        
        if not fixed_response["processing_metadata"]:
            fixed_response["processing_metadata"] = {
                "extraction_confidence": 0.0,
                "text_quality": "unknown",
                "completeness_score": 0.0
            }
        
        return fixed_response
    
    def _find_field_in_data(self, data: Dict[str, Any], field_name: str) -> Any:
        """Recursively search for a field in nested data structure"""
        if isinstance(data, dict):
            # Direct match
            if field_name in data:
                return data[field_name]
            
            # Search in nested dictionaries
            for value in data.values():
                result = self._find_field_in_data(value, field_name)
                if result is not None:
                    return result
        
        return None

    def _process_with_fallback(self, text: str, context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Fallback processing using simpler prompts when unified prompt fails

        Args:
            text: Document text to process
            context: Optional context information

        Returns:
            Processing result or None if fallback also fails
        """
        try:
            logger.info("Using fallback processing with simpler prompts")

            # Simple document detection
            detection_prompt = """
            Analyze this document text and identify the document type. Return a JSON response with:
            {
                "document_type": "detected_type",
                "confidence": 0.0-1.0,
                "category": "document_category"
            }

            Text: """ + text[:2000]  # Limit text length for fallback

            try:
                detection_response = self.text_processor.process_text("", detection_prompt)
                detection_result = json.loads(self._clean_json_response(detection_response))
            except Exception as e:
                logger.warning(f"Fallback detection failed: {str(e)}")
                detection_result = {
                    "document_type": "unknown",
                    "confidence": 0.0,
                    "category": "unknown"
                }

            # Simple data extraction
            extraction_prompt = f"""
            Extract key information from this {detection_result.get('document_type', 'document')} text. Return JSON with:
            {{
                "name": "extracted_name",
                "document_number": "extracted_number",
                "date_of_birth": "YYYY-MM-DD",
                "other_fields": {{}}
            }}

            Text: """ + text[:2000]

            try:
                extraction_response = self.text_processor.process_text("", extraction_prompt)
                extraction_result = json.loads(self._clean_json_response(extraction_response))
            except Exception as e:
                logger.warning(f"Fallback extraction failed: {str(e)}")
                extraction_result = {}

            # Create simplified unified format result
            fallback_result = {
                "document_analysis": {
                    "document_type": detection_result.get("document_type", "unknown"),
                    "document_category": detection_result.get("category", "unknown"),
                    "confidence_score": detection_result.get("confidence", 0.0),
                    "processing_method": "fallback_simplified"
                },
                "extracted_data": {
                    "personal_information": {
                        "full_name": extraction_result.get("name"),
                        "date_of_birth": extraction_result.get("date_of_birth")
                    },
                    "document_identifiers": {
                        "primary_number": extraction_result.get("document_number")
                    },
                    "document_specific_fields": extraction_result.get("other_fields", {})
                },
                "verification_results": {
                    "authenticity_assessment": {
                        "is_likely_genuine": True,  # Default to true for fallback
                        "confidence_score": 0.5,
                        "verification_status": "fallback_processing"
                    },
                    "quality_checks": {},
                    "flags_and_warnings": ["Processed using fallback method due to unified prompt failure"]
                },
                "processing_metadata": {
                    "extraction_confidence": detection_result.get("confidence", 0.0),
                    "text_quality": "unknown",
                    "completeness_score": 0.5,
                    "processing_notes": "Fallback processing used",
                    "unified_processing": False,
                    "fallback_processing": True
                }
            }

            logger.info("Fallback processing completed successfully")
            return fallback_result

        except Exception as e:
            logger.error(f"Fallback processing also failed: {str(e)}")
            return None

    def _clean_json_response(self, response: str) -> str:
        """
        Clean the response to extract valid JSON

        Args:
            response: Raw response from AI model

        Returns:
            Cleaned JSON string
        """
        if not response:
            return ""

        # Remove common markdown formatting
        cleaned = response.strip()

        # Remove markdown code blocks
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]

        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]

        # Remove any leading/trailing whitespace
        cleaned = cleaned.strip()

        # Remove any text before the first { or [
        start_idx = -1
        for i, char in enumerate(cleaned):
            if char in ['{', '[']:
                start_idx = i
                break

        if start_idx > 0:
            cleaned = cleaned[start_idx:]
        elif start_idx == -1:
            # No JSON found
            return ""

        # Remove any text after the last } or ]
        end_idx = -1
        for i in range(len(cleaned) - 1, -1, -1):
            if cleaned[i] in ['}', ']']:
                end_idx = i
                break

        if end_idx >= 0:
            cleaned = cleaned[:end_idx + 1]

        return cleaned

    def _extract_json_from_text(self, text: str) -> Optional[str]:
        """
        Try to extract JSON from text that may contain other content

        Args:
            text: Text that may contain JSON

        Returns:
            Extracted JSON string or None
        """
        import re

        if not text:
            return None

        # Try to find JSON objects using regex
        json_patterns = [
            r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',  # Simple nested objects
            r'\{.*?\}',  # Basic object pattern
            r'\[.*?\]'   # Array pattern
        ]

        for pattern in json_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                try:
                    # Test if it's valid JSON
                    json.loads(match)
                    return match
                except json.JSONDecodeError:
                    continue

        # Try to find content between specific markers
        markers = [
            (r'\{', r'\}'),
            (r'\[', r'\]')
        ]

        for start_marker, end_marker in markers:
            start_pos = text.find(start_marker)
            if start_pos != -1:
                # Find the matching closing marker
                bracket_count = 0
                for i in range(start_pos, len(text)):
                    if text[i] == start_marker:
                        bracket_count += 1
                    elif text[i] == end_marker:
                        bracket_count -= 1
                        if bracket_count == 0:
                            potential_json = text[start_pos:i+1]
                            try:
                                json.loads(potential_json)
                                return potential_json
                            except json.JSONDecodeError:
                                break

        return None

    def _create_error_response(self, error_type: str, message: str, additional_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create standardized error response"""
        error_response = {
            "status": "error",
            "error_type": error_type,
            "message": message,
            "document_analysis": {
                "document_type": "unknown",
                "confidence_score": 0.0,
                "processing_method": "unified_prompt"
            },
            "extracted_data": {},
            "verification_results": {
                "authenticity_assessment": {
                    "is_likely_genuine": False,
                    "confidence_score": 0.0,
                    "verification_status": "error"
                }
            },
            "processing_metadata": {
                "extraction_confidence": 0.0,
                "text_quality": "error",
                "completeness_score": 0.0,
                "processing_notes": message
            }
        }
        
        if additional_data:
            error_response.update(additional_data)
        
        return error_response
    
    def test_processor(self) -> Dict[str, Any]:
        """
        Test the processor with a simple document to diagnose issues

        Returns:
            Test results and diagnostics
        """
        test_text = """
        SAMPLE DOCUMENT
        Name: John Doe
        Date of Birth: 01/01/1990
        Document Number: TEST123456
        """

        try:
            logger.info("Running processor test...")

            # Test connection first
            connection_ok = self.text_processor.test_connection()

            # Test simple processing
            simple_prompt = "Analyze this text and return JSON with document type: " + test_text
            try:
                simple_response = self.text_processor.process_text("", simple_prompt)
                simple_success = bool(simple_response and len(simple_response) > 0)
            except Exception as e:
                simple_response = str(e)
                simple_success = False

            # Test unified processing
            try:
                unified_result = self.process_document(test_text)
                unified_success = unified_result.get("status") != "error"
            except Exception as e:
                unified_result = {"error": str(e)}
                unified_success = False

            return {
                "connection_test": connection_ok,
                "simple_processing": {
                    "success": simple_success,
                    "response_length": len(simple_response) if simple_response else 0,
                    "response_preview": simple_response[:200] if simple_response else "No response"
                },
                "unified_processing": {
                    "success": unified_success,
                    "result_preview": str(unified_result)[:200]
                },
                "model_info": self.text_processor.get_model_info(),
                "recommendations": self._get_troubleshooting_recommendations(connection_ok, simple_success, unified_success)
            }

        except Exception as e:
            return {
                "test_failed": True,
                "error": str(e),
                "recommendations": ["Check API key", "Verify network connection", "Check model availability"]
            }

    def _get_troubleshooting_recommendations(self, connection_ok: bool, simple_ok: bool, unified_ok: bool) -> list:
        """Get troubleshooting recommendations based on test results"""
        recommendations = []

        if not connection_ok:
            recommendations.extend([
                "Check API key validity",
                "Verify network connection",
                "Check Gemini API service status"
            ])
        elif not simple_ok:
            recommendations.extend([
                "Check model availability",
                "Verify API quotas and limits",
                "Try reducing input text length"
            ])
        elif not unified_ok:
            recommendations.extend([
                "Unified prompt may be too complex",
                "Try using fallback processing",
                "Check for prompt length limits",
                "Consider simplifying the unified prompt"
            ])
        else:
            recommendations.append("All tests passed - processor is working correctly")

        return recommendations

    def get_processor_info(self) -> Dict[str, Any]:
        """Get information about the processor configuration"""
        return {
            "processor_type": "UnifiedDocumentProcessor",
            "prompt_version": "unified_v1",
            "capabilities": [
                "document_detection",
                "data_extraction",
                "document_verification",
                "quality_assessment",
                "targeted_field_extraction",
                "fallback_processing"
            ],
            "model_info": self.text_processor.get_model_info(),
            "optimization": "single_pass_processing"
        }
