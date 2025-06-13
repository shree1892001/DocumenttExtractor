"""
TemplateController - Controller for template-related endpoints.
Handles routing for template operations, delegates business logic to services.
"""

from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any
from Services.TemplateService import TemplateService
from Factories.TemplateFactory import TemplateFactory
from Logging_file.logging_file import custom_logger

router = APIRouter()

# Initialize services
template_service = TemplateService()
template_factory = TemplateFactory()


@router.get("/templates")
async def get_templates():
    """Get all available document templates"""
    try:
        # Load templates using service
        templates = template_service.load_templates()
        
        # Get detailed template information
        template_info = template_service.get_template_info(templates)
        
        # Add document type information using factory
        for template in template_info:
            template["document_type"] = template_factory.determine_document_type(template["name"])

        return {
            "status": "success",
            "total_templates": len(template_info),
            "templates": template_info
        }

    except Exception as e:
        custom_logger.error(f"Error getting templates: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to get templates: {str(e)}",
                "templates": []
            }
        )


@router.post("/templates/upload")
async def upload_template(
    file: UploadFile = File(...),
    template_name: str = Form(...),
    document_type: str = Form(...),
    description: str = Form(None)
):
    """Upload a new template file"""
    try:
        # Use service to handle upload
        result = await template_service.upload_template(
            file=file,
            template_name=template_name,
            document_type=document_type,
            description=description
        )
        
        if result["status"] == "error":
            return JSONResponse(
                status_code=400,
                content=result
            )
        
        return JSONResponse(
            status_code=201,
            content=result
        )

    except Exception as e:
        custom_logger.error(f"Error uploading template: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to upload template: {str(e)}"
            }
        )


@router.post("/templates/suggest")
async def suggest_template_creation(request: Dict[str, Any]):
    """Suggest creating a new template based on unmatched document"""
    try:
        document_info = request.get("document_info", {})
        extracted_text = request.get("extracted_text", "")
        
        if not extracted_text:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "extracted_text is required for template suggestion"
                }
            )

        # Use factory to analyze document and suggest template
        suggested_template = template_factory.analyze_document_for_template_suggestion(
            document_info, extracted_text
        )

        return {
            "status": "success",
            "suggestion": suggested_template,
            "message": "Template suggestion generated successfully"
        }

    except Exception as e:
        custom_logger.error(f"Error suggesting template: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to suggest template: {str(e)}"
            }
        )


@router.get("/templates/{template_name}")
async def get_template(template_name: str):
    """Get information about a specific template"""
    try:
        if not template_service.template_exists(template_name):
            return JSONResponse(
                status_code=404,
                content={
                    "status": "error",
                    "message": f"Template '{template_name}' not found"
                }
            )
        
        template_path = template_service.get_template_path(template_name)
        document_type = template_factory.determine_document_type(template_name)
        expected_fields = template_factory.get_document_type_fields(document_type)
        
        return {
            "status": "success",
            "template": {
                "name": template_name,
                "path": template_path,
                "document_type": document_type,
                "expected_fields": expected_fields
            }
        }

    except Exception as e:
        custom_logger.error(f"Error getting template {template_name}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to get template: {str(e)}"
            }
        )


@router.get("/templates/count")
async def get_templates_count():
    """Get the count of available templates"""
    try:
        count = template_service.get_templates_count()
        return {
            "status": "success",
            "count": count
        }

    except Exception as e:
        custom_logger.error(f"Error getting templates count: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to get templates count: {str(e)}"
            }
        )
