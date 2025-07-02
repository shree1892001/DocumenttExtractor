import sys
import traceback
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import warnings
from Controllers.DocumentProcessorController import router as document_router
from Controllers.TemplateController import router as template_router
from Services.TemplateService import TemplateService
from Services.DocumentProcessor3 import DocumentProcessor
from Common.constants import API_HOST, API_PORT, API_KEY
from Logging_file.logging_file import custom_logger

warnings.filterwarnings("ignore")

# Add debug logging
custom_logger.info("Starting Main.py execution")
custom_logger.info(f"Python version: {sys.version}")
custom_logger.info(f"API configuration - Host: {API_HOST}, Port: {API_PORT}")

try:
    custom_logger.info("Creating FastAPI application...")
    app = FastAPI(
        title="Document Processing API",
        description="API for processing and extracting information from documents",
        version="1.0.0"
    )
    custom_logger.info("FastAPI application created successfully")

    custom_logger.info("Adding CORS middleware...")
    origins = ['*']
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    custom_logger.info("CORS middleware added successfully")

except Exception as e:
    custom_logger.error(f"Failed to create FastAPI application: {str(e)}")
    custom_logger.error(f"Traceback: {traceback.format_exc()}")
    sys.exit(1)

@app.on_event("startup")
async def startup_event():
    """Initialize application services on startup"""
    try:
        custom_logger.info("Initializing Document Processing API")

        # Initialize services
        custom_logger.info("Initializing TemplateService...")
        template_service = TemplateService()
        app.state.templates = template_service.load_templates()
        custom_logger.info(f"Loaded {len(app.state.templates)} templates")

        custom_logger.info("Initializing DocumentProcessor...")
        app.state.document_processor = DocumentProcessor(api_key=API_KEY)
        custom_logger.info("DocumentProcessor initialized successfully")

    except Exception as e:
        custom_logger.error(f"Failed to initialize services: {str(e)}")

        app.state.templates = {}
        app.state.document_processor = None
        custom_logger.warning("API started with limited functionality due to initialization errors")

@app.on_event("startup")
async def warm_up():
    """Warm up and log application state"""
    try:
        custom_logger.info("Warming up document processor")

        if hasattr(app.state, 'templates') and app.state.templates:
            custom_logger.info("Loaded templates:")
            for template_name in app.state.templates.keys():
                custom_logger.info(f"- {template_name}")
        else:
            custom_logger.warning("No templates loaded")

        if hasattr(app.state, 'document_processor') and app.state.document_processor:
            custom_logger.info("Document processor is ready")
        else:
            custom_logger.warning("Document processor not initialized")

        custom_logger.info("API startup completed successfully")

    except Exception as e:
        custom_logger.error(f"Error during warm up: {str(e)}")

# Add health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Document Processing API is running",
        "version": "1.0.0",
        "templates_loaded": len(app.state.templates) if hasattr(app.state, 'templates') else 0,
        "processor_initialized": hasattr(app.state, 'document_processor')
    }

@app.get("/api/v1/health")
async def api_health_check():
    """API v1 health check endpoint"""
    return {
        "status": "healthy",
        "message": "DocumentProcessorController API is running",
        "version": "1.0.0",
        "endpoints": {
            "processor": "/api/v1/processor",
            "health": "/api/v1/health",
            "templates": "/api/v1/templates"
        },
        "templates_loaded": len(app.state.templates) if hasattr(app.state, 'templates') else 0,
        "processor_initialized": hasattr(app.state, 'document_processor')
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Document Processing API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "api_health": "/api/v1/health",
            "processor": "/api/v1/processor",
            "templates": "/api/v1/templates",
            "docs": "/docs"
        }
    }

try:
    custom_logger.info("Including document router...")
    app.include_router(
        document_router,
        prefix="/api/v1",
        tags=["Document Processing"]
    )
    custom_logger.info("Document router included successfully")

    custom_logger.info("Including template router...")
    app.include_router(
        template_router,
        prefix="/api/v1",
        tags=["Template Management"]
    )
    custom_logger.info("Template router included successfully")

except Exception as e:
    custom_logger.error(f"Failed to include routers: {str(e)}")
    custom_logger.error(f"Traceback: {traceback.format_exc()}")
    sys.exit(1)

if __name__ == "__main__":
    try:
        custom_logger.info(f"Starting Document Processing API on {API_HOST}:{API_PORT}")

        # Start the FastAPI server
        uvicorn.run(
            app,
            host=API_HOST,
            port=API_PORT,
            log_level="info",
            access_log=True
        )

    except Exception as e:
        custom_logger.error(f"Failed to start API server: {str(e)}")
        raise
