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

            # Prepare response data
            response_data = {
                "extracted_data": {
                    "data": extracted_data.get("data", {}),
                    "confidence": extracted_data.get("confidence", 0.0),
                    "additional_info": extracted_data.get("additional_info", ""),
                    "document_metadata": extracted_data.get("document_metadata", {})
                },
                "verification": verification_result,
                "processing_details": {
                    "document_type": result.get("document_type", "unknown"),
                    "confidence": result.get("confidence", 0.0),
                    "validation_level": result.get("validation_level", "standard"),
                    "processing_method": result.get("processing_method", "unknown"),
                    "chunk_index": result.get("chunk_index"),
                    "total_chunks": result.get("total_chunks")
                }
            }

            # Only return if we have meaningful data
            if (response_data["extracted_data"]["data"] or 
                response_data["processing_details"]["document_type"] != "unknown" or
                verification_result.get("is_genuine") is True or
                response_data["extracted_data"]["confidence"] > 0.0):
                return response_data

            return None

        except Exception as e:
            custom_logger.error(f"Error processing result: {str(e)}")
            return None

    def _cleanup_temp_file(self, file_path: str) -> None:
        """Clean up temporary file"""
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
                custom_logger.info(f"Cleaned up temporary file: {file_path}")
        except Exception as e:
            custom_logger.error(f"Error cleaning up temporary file: {str(e)}") 