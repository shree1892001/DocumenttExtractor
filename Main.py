from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import warnings
import os
from Controllers.DocumentProcessorController import router as document_router
from Services.DocumentProcessor3 import DocumentProcessor
from Common.constants import API_HOST, API_PORT, TEMPLATES_DIR, API_KEY
from Logging_file.logging_file import custom_logger
import cv2
import numpy as np
from pdf2image import convert_from_path
from docx import Document
import tempfile

warnings.filterwarnings("ignore")

app = FastAPI(
    title="Document Processing API",
    description="API for processing and extracting information from documents",
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

def load_templates():
    """Load all document templates from the templates directory"""
    templates = {}
    try:
        if not os.path.exists(TEMPLATES_DIR):
            custom_logger.warning(f"Templates directory not found: {TEMPLATES_DIR}")
            return templates

        custom_logger.info(f"Found {len(os.listdir(TEMPLATES_DIR))} files in templates directory")

        for filename in os.listdir(TEMPLATES_DIR):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.pdf', '.docx')):
                template_path = os.path.join(TEMPLATES_DIR, filename)
                template_name = os.path.splitext(filename)[0].lower()
                
                # Simply store the file path
                templates[template_name] = template_path
                custom_logger.info(f"Loaded template: {filename}")

        custom_logger.info(f"Successfully loaded {len(templates)} templates")
        return templates

    except Exception as e:
        custom_logger.error(f"Error loading templates: {str(e)}")
        return templates

@app.on_event("startup")
async def startup_event():
    custom_logger.info("Initializing Document Processing API")

    # Load templates at startup
    app.state.templates = load_templates()
    
    # Initialize document processor with loaded templates and API key
    app.state.document_processor = DocumentProcessor(api_key=API_KEY)

@app.on_event("startup")
async def warm_up():
    custom_logger.info("Warming up document processor")
    
    # Log loaded templates
    if app.state.templates:
        custom_logger.info("Loaded templates:")
        for template_name in app.state.templates.keys():
            custom_logger.info(f"- {template_name}")

# Include routers with explicit prefix
app.include_router(
    document_router,
    prefix="/api/v1",
    tags=["Document Processing"]
)

if __name__ == "__main__":
    custom_logger.info(f"Starting Document Processing API on {API_HOST}:{API_PORT}")
    uvicorn.run(app, host=API_HOST, port=API_PORT)