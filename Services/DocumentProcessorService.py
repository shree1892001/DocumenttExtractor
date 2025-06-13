"""
DocumentProcessorService - Service layer for document processing operations.
Handles business logic for document processing, coordinates with various processors.
"""

import os
import tempfile
from typing import Dict, Any, List
from fastapi import UploadFile
from Services.DocumentProcessor3 import DocumentProcessor
from Common.constants import API_KEY
from Logging_file.logging_file import custom_logger


class DocumentProcessorService:
    """Service class for handling document processing business logic"""
    
    def __init__(self, api_key: str = None):
        """
        Initialize the document processor service
        
        Args:
            api_key: API key for external services (defaults to common API_KEY)
        """
        self.api_key = api_key or API_KEY
        self.document_processor = DocumentProcessor(api_key=self.api_key)
        custom_logger.info("DocumentProcessorService initialized")
    
    async def process_document(self, file: UploadFile) -> Dict[str, Any]:
        """
        Process an uploaded document file
        
        Args:
            file: The uploaded file to process
            
        Returns:
            Dict containing processing results
        """
        temp_file_path = None
        
        try:
            # Validate file
            if not file.filename:
                return {
                    "status": "error",
                    "message": "No file provided"
                }
            
            # Check file extension
            file_extension = os.path.splitext(file.filename)[1].lower()
            supported_extensions = {'.pdf', '.docx', '.jpg', '.jpeg', '.png', '.tiff', '.bmp'}
            
            if file_extension not in supported_extensions:
                return {
                    "status": "error",
                    "message": f"Unsupported file type: {file_extension}. Supported: {', '.join(supported_extensions)}"
                }
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                temp_file_path = temp_file.name
                content = await file.read()
                temp_file.write(content)
            
            custom_logger.info(f"Processing file: {file.filename} ({len(content)} bytes)")
            
            # Process the document
            results = self.document_processor.process_file(temp_file_path, min_confidence=0.0)
            
            if not results:
                return {
                    "status": "error",
                    "message": "No documents could be processed from the file"
                }
            
            # Format results
            processed_results = []
            for result in results:
                processed_result = {
                    "document_type": result.get("document_type", "unknown"),
                    "confidence": result.get("confidence", 0.0),
                    "extracted_data": result.get("extracted_data", {}),
                    "verification_status": result.get("verification_status", "unknown"),
                    "processing_method": result.get("processing_method", "unknown"),
                    "source_file": file.filename
                }
                
                # Add additional metadata if available
                if "image_number" in result:
                    processed_result["image_number"] = result["image_number"]
                
                if "page_number" in result:
                    processed_result["page_number"] = result["page_number"]
                
                processed_results.append(processed_result)
            
            custom_logger.info(f"Successfully processed {len(processed_results)} documents from {file.filename}")
            
            return {
                "status": "success",
                "message": f"Successfully processed {len(processed_results)} documents",
                "total_documents": len(processed_results),
                "results": processed_results
            }
            
        except Exception as e:
            custom_logger.error(f"Error processing document {file.filename}: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to process document: {str(e)}"
            }
        
        finally:
            # Clean up temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except Exception as e:
                    custom_logger.warning(f"Failed to delete temporary file {temp_file_path}: {str(e)}")
    
    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported file formats
        
        Returns:
            List of supported file extensions
        """
        return ['.pdf', '.docx', '.jpg', '.jpeg', '.png', '.tiff', '.bmp']
    
    def get_processor_info(self) -> Dict[str, Any]:
        """
        Get information about the document processor
        
        Returns:
            Dict containing processor information
        """
        return {
            "processor_type": "DocumentProcessor3",
            "supported_formats": self.get_supported_formats(),
            "api_key_configured": bool(self.api_key),
            "status": "ready"
        }
