from fastapi import FastAPI, File, UploadFile, Form
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

    app.state.templates = load_templates()

    app.state.document_processor = DocumentProcessor(api_key=API_KEY)

@app.on_event("startup")
async def warm_up():
    custom_logger.info("Warming up document processor")

    if app.state.templates:
        custom_logger.info("Loaded templates:")
        for template_name in app.state.templates.keys():
            custom_logger.info(f"- {template_name}")

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

@app.get("/api/v1/templates")
async def get_templates():
    """Get all available document templates"""
    try:
        templates = getattr(app.state, 'templates', {})

        # Create detailed template information
        template_info = []
        for template_name, template_path in templates.items():
            # Extract file info
            filename = os.path.basename(template_path)
            file_extension = os.path.splitext(filename)[1].lower()

            # Determine document type from filename based on actual templates
            doc_type = "unknown"
            template_lower = template_name.lower()

            if "aadhaar" in template_lower or "aadhar" in template_lower:
                doc_type = "aadhaar_card"
            elif "pan" in template_lower:
                doc_type = "pan_card"
            elif "license" in template_lower:
                if "florida" in template_lower:
                    doc_type = "florida_driving_license"
                elif "indian" in template_lower:
                    doc_type = "indian_driving_license"
                else:
                    doc_type = "driving_license"
            elif "passport" in template_lower:
                doc_type = "passport"
            elif "corp" in template_lower or "newmexico" in template_lower:
                doc_type = "corporate_document"

            # Get file size if possible
            file_size = 0
            try:
                if os.path.exists(template_path):
                    file_size = os.path.getsize(template_path)
            except:
                pass

            template_info.append({
                "name": template_name,
                "display_name": template_name.replace('_', ' ').title(),
                "filename": filename,
                "file_path": template_path,
                "file_extension": file_extension,
                "file_size": file_size,
                "document_type": doc_type,
                "supported_formats": [file_extension.replace('.', '')]
            })

        return {
            "status": "success",
            "total_templates": len(template_info),
            "templates": template_info
        }

    except Exception as e:
        custom_logger.error(f"Error getting templates: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to get templates: {str(e)}",
            "templates": []
        }

@app.post("/api/v1/templates/upload")
async def upload_template(
    file: UploadFile = File(...),
    template_name: str = Form(...),
    document_type: str = Form(...),
    description: str = Form(None)
):
    """Upload a new template file"""
    try:
        # Validate file type
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.pdf', '.docx'}
        file_extension = os.path.splitext(file.filename)[1].lower()

        if file_extension not in allowed_extensions:
            return {
                "status": "error",
                "message": f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            }

        # Create safe filename
        safe_template_name = template_name.lower().replace(' ', '_').replace('-', '_')
        safe_filename = f"{safe_template_name}{file_extension}"
        template_path = os.path.join(TEMPLATES_DIR, safe_filename)

        # Check if template already exists
        if os.path.exists(template_path):
            return {
                "status": "error",
                "message": f"Template '{safe_filename}' already exists"
            }

        # Save the uploaded file
        with open(template_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Add to templates dictionary
        app.state.templates[safe_template_name] = template_path

        # Log the new template
        custom_logger.info(f"New template uploaded: {safe_filename} ({len(content)} bytes)")

        return {
            "status": "success",
            "message": f"Template '{safe_filename}' uploaded successfully",
            "template": {
                "name": safe_template_name,
                "filename": safe_filename,
                "file_path": template_path,
                "file_size": len(content),
                "document_type": document_type,
                "description": description or f"{document_type} template"
            }
        }

    except Exception as e:
        custom_logger.error(f"Error uploading template: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to upload template: {str(e)}"
        }

@app.post("/api/v1/templates/suggest")
async def suggest_template_creation(request: dict):
    """Suggest creating a new template based on unmatched document"""
    try:
        document_info = request.get("document_info", {})
        extracted_text = request.get("extracted_text", "")

        # Analyze the document to suggest template details
        suggested_template = analyze_document_for_template_suggestion(document_info, extracted_text)

        return {
            "status": "success",
            "suggestion": suggested_template,
            "message": "Template suggestion generated successfully"
        }

    except Exception as e:
        custom_logger.error(f"Error suggesting template: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to suggest template: {str(e)}"
        }

def analyze_document_for_template_suggestion(document_info: dict, extracted_text: str) -> dict:
    """Analyze document content to suggest template creation"""
    try:
        # Extract key information from the document
        text_lower = extracted_text.lower()

        # Suggest document type based on content analysis
        suggested_type = "other"
        suggested_name = "Custom Template"
        suggested_description = "Custom document template"
        suggested_fields = ["document_number", "name", "date"]

        # Analyze content for document type patterns
        if any(keyword in text_lower for keyword in ["aadhaar", "aadhar", "uid"]):
            suggested_type = "aadhaar_card"
            suggested_name = "Custom Aadhaar Template"
            suggested_description = "Custom Aadhaar card template"
            suggested_fields = ["name", "aadhaar_number", "date_of_birth", "address"]

        elif any(keyword in text_lower for keyword in ["pan", "permanent account", "income tax"]):
            suggested_type = "pan_card"
            suggested_name = "Custom PAN Template"
            suggested_description = "Custom PAN card template"
            suggested_fields = ["name", "fathers_name", "pan_number", "date_of_birth"]

        elif any(keyword in text_lower for keyword in ["driving", "license", "licence", "vehicle"]):
            suggested_type = "driving_license"
            suggested_name = "Custom License Template"
            suggested_description = "Custom driving license template"
            suggested_fields = ["name", "license_number", "date_of_birth", "address", "vehicle_class"]

        elif any(keyword in text_lower for keyword in ["passport", "travel", "nationality"]):
            suggested_type = "passport"
            suggested_name = "Custom Passport Template"
            suggested_description = "Custom passport template"
            suggested_fields = ["name", "passport_number", "date_of_birth", "nationality"]

        elif any(keyword in text_lower for keyword in ["company", "corporation", "business", "registration"]):
            suggested_type = "corporate_document"
            suggested_name = "Custom Corporate Template"
            suggested_description = "Custom corporate document template"
            suggested_fields = ["company_name", "registration_number", "address", "incorporation_date"]

        # Extract potential field values from the text
        extracted_fields = extract_potential_fields(extracted_text)

        return {
            "suggested_name": suggested_name,
            "suggested_type": suggested_type,
            "suggested_description": suggested_description,
            "suggested_fields": suggested_fields,
            "extracted_sample_data": extracted_fields,
            "confidence": calculate_suggestion_confidence(text_lower, suggested_type)
        }

    except Exception as e:
        custom_logger.error(f"Error analyzing document for template suggestion: {str(e)}")
        return {
            "suggested_name": "Custom Template",
            "suggested_type": "other",
            "suggested_description": "Custom document template",
            "suggested_fields": ["document_number", "name", "date"],
            "extracted_sample_data": {},
            "confidence": 0.5
        }

def extract_potential_fields(text: str) -> dict:
    """Extract potential field values from document text"""
    import re

    fields = {}

    # Extract dates
    date_patterns = [
        r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{4})\b',
        r'\b(\d{4}[/-]\d{1,2}[/-]\d{1,2})\b',
        r'\b(\d{1,2}\s+\w+\s+\d{4})\b'
    ]

    for pattern in date_patterns:
        matches = re.findall(pattern, text)
        if matches:
            fields["dates_found"] = matches[:3]  # First 3 dates
            break

    # Extract numbers (potential IDs)
    number_patterns = [
        r'\b([A-Z]{3,5}\d{4,10}[A-Z]?)\b',  # Alphanumeric IDs
        r'\b(\d{10,16})\b'  # Long numbers
    ]

    for pattern in number_patterns:
        matches = re.findall(pattern, text)
        if matches:
            fields["numbers_found"] = matches[:3]  # First 3 numbers
            break

    # Extract potential names (capitalized words)
    name_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
    names = re.findall(name_pattern, text)
    if names:
        fields["names_found"] = [name for name in names if len(name.split()) >= 2][:3]

    return fields

def calculate_suggestion_confidence(text: str, suggested_type: str) -> float:
    """Calculate confidence score for template suggestion"""
    confidence = 0.5  # Base confidence

    # Type-specific keywords boost confidence
    type_keywords = {
        "aadhaar_card": ["aadhaar", "aadhar", "uid", "unique identification"],
        "pan_card": ["pan", "permanent account", "income tax"],
        "driving_license": ["driving", "license", "licence", "vehicle"],
        "passport": ["passport", "travel", "nationality"],
        "corporate_document": ["company", "corporation", "business", "registration"]
    }

    if suggested_type in type_keywords:
        keyword_count = sum(1 for keyword in type_keywords[suggested_type] if keyword in text)
        confidence += min(keyword_count * 0.1, 0.3)  # Max 0.3 boost

    # Length and structure boost confidence
    if len(text) > 100:
        confidence += 0.1
    if len(text) > 500:
        confidence += 0.1

    return min(confidence, 0.95)  # Cap at 95%

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
            "docs": "/docs"
        }
    }

app.include_router(
    document_router,
    prefix="/api/v1",
    tags=["Document Processing"]
)

if __name__ == "__main__":
    custom_logger.info(f"Starting Document Processing API on {API_HOST}:{API_PORT}")
    uvicorn.run(app, host=API_HOST, port=API_PORT)