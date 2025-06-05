from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import tempfile
import os
from DocumentProcessor3 import DocumentProcessor3
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Document Processing API",
    description="API for document template matching and data extraction",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DocumentProcessor3
processor = DocumentProcessor3(api_key="your_api_key")  # Replace with your actual API key

@app.post("/process-document/", response_model=Dict[str, Any])
async def process_document(file: UploadFile = File(...)):
    """
    Process a document by matching it against templates and extracting data.
    
    Args:
        file: The uploaded document file (supports PDF, DOCX, JPG, PNG)
        
    Returns:
        JSON response containing:
        - document_type: Type of document matched
        - template_confidence: Confidence score of template match
        - genuineness_score: Score indicating document authenticity
        - verification_score: Score for extracted information verification
        - extracted_fields: Dictionary of extracted field values
        - raw_text: Raw text extracted from document
    """
    try:
        # Create a temporary file to store the upload
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            # Write the uploaded file to the temporary file
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        try:
            # Process the document
            result = processor.process_document(temp_file_path)
            
            # Log success
            logger.info(f"Successfully processed document: {file.filename}")
            logger.info(f"Matched template: {result['document_type']} with confidence {result['template_confidence']}")
            
            return JSONResponse(
                content={
                    "status": "success",
                    "message": "Document processed successfully",
                    "data": result
                },
                status_code=200
            )
            
        except ValueError as ve:
            # Handle template matching or validation errors
            logger.warning(f"Document processing failed: {str(ve)}")
            return JSONResponse(
                content={
                    "status": "error",
                    "message": str(ve),
                    "data": None
                },
                status_code=400
            )
            
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Error processing document: {str(e)}")
            return JSONResponse(
                content={
                    "status": "error",
                    "message": "Internal server error during document processing",
                    "data": None
                },
                status_code=500
            )
            
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        logger.error(f"Error handling file upload: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error handling file upload"
        )

@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify API is running.
    """
    return {"status": "healthy", "message": "API is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 