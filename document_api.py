from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import warnings
import os
from pydantic import BaseModel
from typing import Optional
from Services.document_processor import DocumentProcessor
from Logging_file.logging_file import custom_logger
from constants import API_HOST, API_PORT, API_KEY

# Ignore warnings
warnings.filterwarnings("ignore")

# Initialize FastAPI app
app = FastAPI(
    title="Document Processing API",
    description="API for document template matching and data extraction",
    version="1.0.0"
)

# Configure CORS
origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup events
@app.on_event("startup")
async def startup_event():
    custom_logger.info("Initializing Document Processing API")
    app.state.document_processor = DocumentProcessor()

@app.on_event("startup")
async def warm_up():
    custom_logger.info("Warming up document processor")
    processor = app.state.document_processor
    # Add any warm-up tasks here

# Request models
class DocumentRequest(BaseModel):
    file_path: str
    document_type: Optional[str] = None

class ProcessResult(BaseModel):
    document_type: str
    template_confidence: float
    genuineness_score: float
    verification_score: float
    extracted_fields: dict
    raw_text: str

# API Endpoints
@app.post("/process-document", response_model=ProcessResult)
async def process_document(
    file: UploadFile = File(...),
    document_type: Optional[str] = Form(None)
):
    """
    Process a document by matching it against templates and extracting data.
    """
    try:
        # Save uploaded file temporarily
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Process the document
        processor = app.state.document_processor
        result = processor.process_document(temp_file_path)

        # Clean up temporary file
        os.remove(temp_file_path)

        return result

    except Exception as e:
        custom_logger.error(f"Error processing document: {str(e)}")
        raise

@app.post("/process-document-path")
async def process_document_path(request: DocumentRequest):
    """
    Process a document from a file path.
    """
    try:
        processor = app.state.document_processor
        result = processor.process_document(request.file_path)
        return result
    except Exception as e:
        custom_logger.error(f"Error processing document: {str(e)}")
        raise

@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify API is running.
    """
    return {
        "status": "healthy",
        "message": "Document Processing API is running",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    custom_logger.info(f"Starting Document Processing API on {API_HOST}:{API_PORT}")
    uvicorn.run(app, host=API_HOST, port=API_PORT) 