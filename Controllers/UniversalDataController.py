"""
UniversalDataController - API controller for universal data extraction from ANY document
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, Request
from fastapi.responses import JSONResponse
from Services.UniversalDataExtractor import UniversalDataExtractor
from Common.constants import API_KEY
from Logging_file.logging_file import custom_logger
import tempfile
import os
import json

router = APIRouter()

def error_response(message="Universal data extraction failed", status_code=500):
    """Reusable function for returning an error response."""
    return JSONResponse(
        status_code=status_code,
        content={"detail": message}
    )

@router.post("/universal-extraction")
@custom_logger.log_around
async def extract_universal_data(request: Request, file: UploadFile = File(...)):
    """
    Extract ALL data from ANY document file - completely general approach.
    Works with any document type and extracts everything visible.
    
    Args:
        request: FastAPI request object to access app state
        file (UploadFile): The file to process (any document type)
        
    Returns:
        JSONResponse: All extracted data from the document
    """
    custom_logger.info(f"Received universal extraction request for file: {file.filename}")
    
    try:
        # Create universal data extractor
        extractor = UniversalDataExtractor(api_key=API_KEY)
        
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            custom_logger.info(f"Processing file for universal extraction: {file.filename}")
            
            # Extract text from file first
            text = await extract_text_from_file(temp_file_path, file.filename)
            
            if not text:
                return error_response("No text could be extracted from the file", status_code=400)
            
            # Perform universal data extraction
            result = extractor.extract_all_data(text, file.filename)
            
            # Get summary for logging
            summary = extractor.get_data_summary(result)
            custom_logger.info(f"Universal extraction completed - Document: {summary.get('document_type')}, Fields: {summary.get('total_fields_extracted')}")
            
            return JSONResponse(
                content=result,
                status_code=200
            )
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
                custom_logger.info(f"Cleaned up temporary file: {temp_file_path}")
            except Exception as cleanup_error:
                custom_logger.warning(f"Failed to clean up temporary file: {cleanup_error}")
                
    except Exception as e:
        custom_logger.error(f"Error in universal data extraction: {str(e)}")
        return error_response(f"Error extracting universal data: {str(e)}", status_code=500)

@router.post("/universal-extraction/text")
@custom_logger.log_around
async def extract_universal_data_from_text(request: Request, text_data: dict):
    """
    Extract ALL data from text content - completely general approach.
    Works with any document text and extracts everything visible.
    
    Args:
        request: FastAPI request object to access app state
        text_data: Dictionary containing 'text' field with document text
        
    Returns:
        JSONResponse: All extracted data from the text
    """
    try:
        text = text_data.get('text', '')
        if not text:
            return error_response("No text provided", status_code=400)
        
        custom_logger.info(f"Received universal text extraction request ({len(text)} characters)")
        
        # Create universal data extractor
        extractor = UniversalDataExtractor(api_key=API_KEY)
        
        # Perform universal data extraction
        result = extractor.extract_all_data(text, "text_input")
        
        # Get summary for logging
        summary = extractor.get_data_summary(result)
        custom_logger.info(f"Universal text extraction completed - Document: {summary.get('document_type')}, Fields: {summary.get('total_fields_extracted')}")
        
        return JSONResponse(
            content=result,
            status_code=200
        )
        
    except Exception as e:
        custom_logger.error(f"Error in universal text extraction: {str(e)}")
        return error_response(f"Error extracting universal data from text: {str(e)}", status_code=500)

@router.post("/universal-extraction/search")
@custom_logger.log_around
async def search_universal_data(request: Request, search_request: dict):
    """
    Search through all extracted data for specific fields or values.
    
    Args:
        request: FastAPI request object to access app state
        search_request: Dictionary containing 'extraction_result' and 'search_term'
        
    Returns:
        JSONResponse: Search results
    """
    try:
        extraction_result = search_request.get('extraction_result', {})
        search_term = search_request.get('search_term', '')
        
        if not extraction_result:
            return error_response("No extraction result provided", status_code=400)
        
        if not search_term:
            return error_response("No search term provided", status_code=400)
        
        custom_logger.info(f"Received universal search request for term: {search_term}")
        
        # Create universal data extractor
        extractor = UniversalDataExtractor(api_key=API_KEY)
        
        # Perform search
        search_results = extractor.search_data(extraction_result, search_term)
        
        custom_logger.info(f"Universal search completed - Found {search_results.get('total_matches', 0)} matches")
        
        return JSONResponse(
            content=search_results,
            status_code=200
        )
        
    except Exception as e:
        custom_logger.error(f"Error in universal data search: {str(e)}")
        return error_response(f"Error searching universal data: {str(e)}", status_code=500)

@router.get("/universal-extraction/summary")
@custom_logger.log_around
async def get_universal_extraction_summary(request: Request, extraction_result: dict):
    """
    Get a summary of universal extraction results.
    
    Args:
        request: FastAPI request object to access app state
        extraction_result: The extraction result to summarize
        
    Returns:
        JSONResponse: Summary information
    """
    try:
        if not extraction_result:
            return error_response("No extraction result provided", status_code=400)
        
        custom_logger.info("Received universal extraction summary request")
        
        # Create universal data extractor
        extractor = UniversalDataExtractor(api_key=API_KEY)
        
        # Get summary
        summary = extractor.get_data_summary(extraction_result)
        
        return JSONResponse(
            content=summary,
            status_code=200
        )
        
    except Exception as e:
        custom_logger.error(f"Error getting universal extraction summary: {str(e)}")
        return error_response(f"Error getting universal extraction summary: {str(e)}", status_code=500)

@router.get("/universal-extraction/info")
@custom_logger.log_around
async def get_universal_extractor_info(request: Request):
    """
    Get information about the universal data extractor.
    
    Args:
        request: FastAPI request object to access app state
        
    Returns:
        JSONResponse: Extractor information
    """
    try:
        custom_logger.info("Received universal extractor info request")
        
        info = {
            "service": "UniversalDataExtractor",
            "version": "1.0.0",
            "description": "Extracts ALL data from ANY document type - completely general approach",
            "features": [
                "Universal document processing - works with ANY document type",
                "Extracts EVERYTHING visible in the document",
                "No document type limitations or restrictions",
                "Pattern-based extraction for additional data",
                "Comprehensive data analysis and search",
                "Complete data flattening and organization",
                "Original text preservation for reference",
                "Advanced search capabilities across all data"
            ],
            "extraction_methods": [
                "AI-powered extraction using unified prompts",
                "Pattern matching for dates, numbers, emails, names",
                "Key-value pair extraction from text lines",
                "Code and identifier pattern recognition",
                "Heading and title extraction",
                "Complete data structure flattening"
            ],
            "supported_patterns": [
                "Dates (multiple formats)",
                "Phone numbers (multiple formats)",
                "Email addresses",
                "Names (first, last, full)",
                "Addresses",
                "Amounts and currency",
                "Codes and identifiers",
                "Document numbers and IDs"
            ],
            "endpoints": {
                "file_extraction": "/api/v1/universal-extraction",
                "text_extraction": "/api/v1/universal-extraction/text",
                "search": "/api/v1/universal-extraction/search",
                "summary": "/api/v1/universal-extraction/summary",
                "info": "/api/v1/universal-extraction/info"
            },
            "use_cases": [
                "Any document type processing",
                "Complete data extraction",
                "Document analysis and insights",
                "Data mining and discovery",
                "Content indexing and search",
                "Document comparison and analysis"
            ]
        }
        
        return JSONResponse(
            content=info,
            status_code=200
        )
        
    except Exception as e:
        custom_logger.error(f"Error getting universal extractor info: {str(e)}")
        return error_response(f"Error getting universal extractor info: {str(e)}", status_code=500)

async def extract_text_from_file(file_path: str, filename: str) -> str:
    """
    Extract text from various file formats.
    
    Args:
        file_path: Path to the file
        filename: Original filename
        
    Returns:
        Extracted text content
    """
    try:
        file_extension = os.path.splitext(filename)[1].lower()
        
        if file_extension == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        elif file_extension == '.pdf':
            import fitz  # PyMuPDF
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        
        elif file_extension == '.docx':
            try:
                from docx import Document
                doc = Document(file_path)
                text = ""
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                return text
            except ImportError:
                custom_logger.warning("python-docx not available, cannot extract from DOCX")
                return ""
        
        elif file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
            # For images, we would need OCR processing
            # This is a placeholder - in a real implementation, you'd use OCR
            custom_logger.warning("Image OCR processing not implemented in this controller")
            return ""
        
        else:
            custom_logger.warning(f"Unsupported file format: {file_extension}")
            return ""
            
    except Exception as e:
        custom_logger.error(f"Error extracting text from file: {str(e)}")
        return "" 