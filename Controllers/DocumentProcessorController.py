from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from Services.DocumentProcessorService import DocumentProcessorService
from Logging_file.logging_file import custom_logger

router = APIRouter()

def error_response(message="Document processing failed", status_code=500):
    """Reusable function for returning an error response."""
    return JSONResponse(
        status_code=status_code,
        content={"detail": message}
    )

@router.post("/processor")
@custom_logger.log_around
async def process_document(file: UploadFile = File(...)):
    """
    Process a document file and extract information from it.
    
    Args:
        file (UploadFile): The file to process
        
    Returns:
        JSONResponse: Processing results including extracted data and verification
    """
    custom_logger.info(f"Received file upload request for file: {file.filename}")

    try:
        # Initialize service
        document_service = DocumentProcessorService()
        
        # Process document
        result = await document_service.process_document(file)
        
        if result["status"] == "error":
            return error_response(result["message"], status_code=400)
            
        return JSONResponse(content=result, status_code=200)

    except Exception as e:
        custom_logger.error(f"Error in document processing endpoint: {str(e)}")
        return error_response("Error processing document", status_code=500)