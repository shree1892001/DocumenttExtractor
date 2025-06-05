from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import warnings
import os
from controllers.document_controller import router as document_router
from Logging_file.logging_file import custom_logger
from pydantic import BaseModel
from typing import Optional

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

# Startup event
@app.on_event("startup")
async def startup_event():
    custom_logger.info("Starting Document Processing API")
    # Initialize any required services or connections here

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify API is running.
    """
    return {"status": "healthy", "message": "API is running"}

# Include routers
app.include_router(document_router, prefix="/api/v1", tags=["Document Processing"])

if __name__ == "__main__":
    # Get host and port from environment variables or use defaults
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    # Start the server
    uvicorn.run(app, host=host, port=port) 