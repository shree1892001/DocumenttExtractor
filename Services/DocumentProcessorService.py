from typing import List, Dict, Any, Optional
from fastapi import UploadFile
import tempfile
import os
from Services.DocumentProcessor3 import DocumentProcessor
from Common.constants import API_KEY_1
from Logging_file.logging_file import custom_logger

class DocumentProcessorService:
    def __init__(self):
        self.api_key = API_KEY_1
        self.supported_extensions = {'.pdf', '.docx', '.jpg', '.jpeg', '.png', '.tiff', '.bmp'}
        self.processor = DocumentProcessor(api_key=self.api_key)

    async def process_document(self, file: UploadFile) -> Dict[str, Any]:
        """
        Process a document file and extract information from it.
        
        Args:
            file (UploadFile): The uploaded file to process
            
        Returns:
            Dict[str, Any]: Processing results including extracted data and verification
        """
        try:
            # Validate file
            validation_result = self._validate_file(file)
            if validation_result:
                return validation_result

            # Process file
            temp_file_path = await self._save_temp_file(file)
            try:
                return await self._process_file(temp_file_path)
            finally:
                # Clean up temp file
                self._cleanup_temp_file(temp_file_path)

        except Exception as e:
            custom_logger.error(f"Error in document processing service: {str(e)}")
            return {
                "status": "error",
                "message": "Document processing failed",
                "error": str(e)
            }

    def _validate_file(self, file: UploadFile) -> Optional[Dict[str, Any]]:
        """Validate the uploaded file"""
        try:
            if not file.filename:
                return {
                    "status": "error",
                    "message": "No file provided",
                    "error": "Missing filename"
                }

            if not file.filename.lower().endswith(tuple(self.supported_extensions)):
                return {
                    "status": "error",
                    "message": "Invalid file format",
                    "error": "Only PDF, DOCX, JPG, and PNG are allowed"
                }

            return None

        except Exception as e:
            custom_logger.error(f"Error validating file: {str(e)}")
            return {
                "status": "error",
                "message": "File validation failed",
                "error": str(e)
            }

    async def _save_temp_file(self, file: UploadFile) -> str:
        """Save uploaded file to temporary location"""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
                content = await file.read()
                if not content:
                    raise ValueError("Empty file provided")
                
                temp_file.write(content)
                return temp_file.name

        except Exception as e:
            custom_logger.error(f"Error saving temporary file: {str(e)}")
            raise

    async def _process_file(self, file_path: str) -> Dict[str, Any]:
        """Process the file and extract information"""
        try:
            # Get processing results
            results = self.processor.process_file(file_path)
            
            if not results:
                return {
                    "status": "error",
                    "message": "No valid documents detected",
                    "data": []
                }

            # Process results
            processed_results = []
            for result in results:
                processed_result = self._process_result(result)
                if processed_result:
                    processed_results.append(processed_result)
                else:
                    # If processing failed, still include basic result structure
                    processed_results.append({
                        "extracted_data": {
                            "data": {},
                            "confidence": 0.0,
                            "additional_info": "Processing failed",
                            "document_metadata": {}
                        },
                        "verification": {
                            "is_genuine": False,
                            "confidence_score": 0.0,
                            "rejection_reason": "Processing failed",
                            "verification_checks": {},
                            "security_features_found": [],
                            "verification_summary": "Processing failed",
                            "recommendations": []
                        },
                        "processing_details": {
                            "document_type": result.get("document_type", "unknown"),
                            "confidence": 0.0,
                            "validation_level": "standard",
                            "processing_method": "unknown",
                            "chunk_index": None,
                            "total_chunks": None
                        }
                    })

            if not processed_results:
                return {
                    "status": "error",
                    "message": "No documents could be processed",
                    "data": []
                }

            return {
                "status": "success",
                "message": f"Successfully processed {len(processed_results)} documents",
                "data": processed_results
            }

        except Exception as e:
            custom_logger.error(f"Error processing file: {str(e)}")
            return {
                "status": "error",
                "message": "Document processing failed",
                "error": str(e)
            }

    def _process_result(self, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual result and format response"""
        try:
            # Get the extracted data
            extracted_data = result.get("extracted_data", {})
            
            # Get verification status
            verification_result = result.get("verification_result", {
                "is_genuine": False,
                "confidence_score": 0.0,
                "rejection_reason": "No verification performed",
                "verification_checks": {
                    "authenticity": {"passed": False, "details": "", "confidence": 0.0},
                    "security_features": {"passed": False, "details": "", "confidence": 0.0},
                    "data_validation": {"passed": False, "details": "", "confidence": 0.0},
                    "quality": {"passed": False, "details": "", "confidence": 0.0}
                },
                "security_features_found": [],
                "verification_summary": "",
                "recommendations": []
            })

            # Prepare response data - ensure extracted_data is always properly structured
            if isinstance(extracted_data, dict):
                # If extracted_data is already structured correctly
                if "data" in extracted_data:
                    data_content = extracted_data.get("data", {})
                    confidence = extracted_data.get("confidence", 0.0)
                    additional_info = extracted_data.get("additional_info", "")
                    document_metadata = extracted_data.get("document_metadata", {})
                else:
                    # If extracted_data contains the actual data directly
                    data_content = extracted_data
                    confidence = result.get("confidence", 0.0)
                    additional_info = result.get("additional_info", "")
                    document_metadata = result.get("document_metadata", {})
            else:
                # Fallback for any other structure
                data_content = {}
                confidence = result.get("confidence", 0.0)
                additional_info = str(extracted_data) if extracted_data else ""
                document_metadata = {}

            # Check if we should suggest creating a new template
            document_type = result.get("document_type", "unknown")
            template_suggestion = None

            if document_type == "unknown" or result.get("confidence", 0.0) < 0.5:
                # Generate template suggestion for unknown or low-confidence documents
                template_suggestion = self._generate_template_suggestion(result, extracted_data)

            response_data = {
                "extracted_data": {
                    "data": data_content,
                    "confidence": confidence,
                    "additional_info": additional_info,
                    "document_metadata": document_metadata
                },
                "verification": verification_result,
                "processing_details": {
                    "document_type": document_type,
                    "confidence": result.get("confidence", 0.0),
                    "validation_level": result.get("validation_level", "standard"),
                    "processing_method": result.get("processing_method", "unknown"),
                    "chunk_index": result.get("chunk_index"),
                    "total_chunks": result.get("total_chunks")
                }
            }

            # Add template suggestion if available
            if template_suggestion:
                response_data["template_suggestion"] = template_suggestion

            # Always return the response data, even if document is rejected
            # This ensures extracted data is always included in the response
            return response_data

        except Exception as e:
            custom_logger.error(f"Error processing result: {str(e)}")
            return None

    def _generate_template_suggestion(self, result: Dict[str, Any], extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a template creation suggestion for unknown document types"""
        try:
            # Get extracted text for analysis
            raw_text = ""
            if isinstance(extracted_data, dict):
                if "data" in extracted_data:
                    data_content = extracted_data["data"]
                    if isinstance(data_content, dict):
                        # Combine all text fields
                        text_parts = []
                        for key, value in data_content.items():
                            if isinstance(value, str):
                                text_parts.append(value)
                            elif isinstance(value, dict):
                                for sub_key, sub_value in value.items():
                                    if isinstance(sub_value, str):
                                        text_parts.append(sub_value)
                        raw_text = " ".join(text_parts)

                # Also check additional_info
                additional_info = extracted_data.get("additional_info", "")
                if additional_info:
                    raw_text += " " + additional_info

            # Analyze content for template suggestion
            suggestion = self._analyze_content_for_template(raw_text, result)

            return {
                "should_create_template": True,
                "reason": "Document type not recognized or low confidence match",
                "suggested_template": suggestion,
                "confidence": result.get("confidence", 0.0),
                "extracted_content_sample": raw_text[:200] + "..." if len(raw_text) > 200 else raw_text
            }

        except Exception as e:
            custom_logger.error(f"Error generating template suggestion: {str(e)}")
            return {
                "should_create_template": True,
                "reason": "Document type not recognized",
                "suggested_template": {
                    "name": "Custom Template",
                    "type": "other",
                    "description": "Custom document template"
                },
                "confidence": 0.0,
                "extracted_content_sample": ""
            }

    def _analyze_content_for_template(self, text: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze document content to suggest template details"""
        text_lower = text.lower()

        # Default suggestion
        suggestion = {
            "name": "Custom Template",
            "type": "other",
            "description": "Custom document template based on uploaded document",
            "suggested_fields": ["document_number", "name", "date"]
        }

        # Analyze content patterns
        if any(keyword in text_lower for keyword in ["aadhaar", "aadhar", "uid", "unique identification"]):
            suggestion.update({
                "name": "Custom Aadhaar Template",
                "type": "aadhaar_card",
                "description": "Custom Aadhaar card template",
                "suggested_fields": ["name", "aadhaar_number", "date_of_birth", "address"]
            })
        elif any(keyword in text_lower for keyword in ["pan", "permanent account", "income tax"]):
            suggestion.update({
                "name": "Custom PAN Template",
                "type": "pan_card",
                "description": "Custom PAN card template",
                "suggested_fields": ["name", "fathers_name", "pan_number", "date_of_birth"]
            })
        elif any(keyword in text_lower for keyword in ["driving", "license", "licence", "vehicle"]):
            suggestion.update({
                "name": "Custom License Template",
                "type": "driving_license",
                "description": "Custom driving license template",
                "suggested_fields": ["name", "license_number", "date_of_birth", "address", "vehicle_class"]
            })
        elif any(keyword in text_lower for keyword in ["passport", "travel", "nationality"]):
            suggestion.update({
                "name": "Custom Passport Template",
                "type": "passport",
                "description": "Custom passport template",
                "suggested_fields": ["name", "passport_number", "date_of_birth", "nationality"]
            })
        elif any(keyword in text_lower for keyword in ["company", "corporation", "business", "registration"]):
            suggestion.update({
                "name": "Custom Corporate Template",
                "type": "corporate_document",
                "description": "Custom corporate document template",
                "suggested_fields": ["company_name", "registration_number", "address", "incorporation_date"]
            })

        return suggestion

    def _cleanup_temp_file(self, file_path: str) -> None:
        """Clean up temporary file"""
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
                custom_logger.info(f"Cleaned up temporary file: {file_path}")
        except Exception as e:
            custom_logger.error(f"Error cleaning up temporary file: {str(e)}") 