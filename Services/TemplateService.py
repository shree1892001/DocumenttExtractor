"""
TemplateService - Service layer for template management operations.
Handles business logic for template loading, uploading, and management.
"""

import os
from typing import Dict, Any, List
from fastapi import UploadFile
from Common.constants import TEMPLATES_DIR
from Logging_file.logging_file import custom_logger


class TemplateService:
    """Service class for handling template management business logic"""
    
    def __init__(self, templates_dir: str = None):
        """
        Initialize the template service
        
        Args:
            templates_dir: Directory containing templates (defaults to TEMPLATES_DIR)
        """
        self.templates_dir = templates_dir or TEMPLATES_DIR
        custom_logger.info(f"TemplateService initialized with directory: {self.templates_dir}")
    
    def load_templates(self) -> Dict[str, str]:
        """
        Load all document templates from the templates directory
        
        Returns:
            Dict mapping template names to file paths
        """
        templates = {}
        try:
            if not os.path.exists(self.templates_dir):
                custom_logger.warning(f"Templates directory not found: {self.templates_dir}")
                return templates

            custom_logger.info(f"Found {len(os.listdir(self.templates_dir))} files in templates directory")

            for filename in os.listdir(self.templates_dir):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.pdf', '.docx')):
                    template_path = os.path.join(self.templates_dir, filename)
                    template_name = os.path.splitext(filename)[0].lower()

                    templates[template_name] = template_path
                    custom_logger.info(f"Loaded template: {filename}")

            custom_logger.info(f"Successfully loaded {len(templates)} templates")
            return templates

        except Exception as e:
            custom_logger.error(f"Error loading templates: {str(e)}")
            return templates
    
    def get_template_info(self, templates: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Get detailed information about templates
        
        Args:
            templates: Dict of template names to paths
            
        Returns:
            List of template information dictionaries
        """
        template_info = []
        
        for template_name, template_path in templates.items():
            # Extract file info
            filename = os.path.basename(template_path)
            file_extension = os.path.splitext(filename)[1].lower()

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
                "supported_formats": [file_extension.replace('.', '')]
            })

        return template_info
    
    async def upload_template(
        self,
        file: UploadFile,
        template_name: str,
        document_type: str,
        description: str = None
    ) -> Dict[str, Any]:
        """
        Upload a new template file
        
        Args:
            file: The uploaded template file
            template_name: Name for the template
            document_type: Type of document this template represents
            description: Optional description
            
        Returns:
            Dict containing upload result
        """
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
            template_path = os.path.join(self.templates_dir, safe_filename)

            # Check if template already exists
            if os.path.exists(template_path):
                return {
                    "status": "error",
                    "message": f"Template '{safe_filename}' already exists"
                }

            # Ensure templates directory exists
            os.makedirs(self.templates_dir, exist_ok=True)

            # Save the uploaded file
            content = await file.read()
            with open(template_path, "wb") as buffer:
                buffer.write(content)

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
    
    def get_templates_count(self) -> int:
        """
        Get the count of available templates
        
        Returns:
            Number of templates
        """
        templates = self.load_templates()
        return len(templates)
    
    def template_exists(self, template_name: str) -> bool:
        """
        Check if a template exists
        
        Args:
            template_name: Name of the template to check
            
        Returns:
            True if template exists, False otherwise
        """
        templates = self.load_templates()
        return template_name.lower() in templates
    
    def get_template_path(self, template_name: str) -> str:
        """
        Get the file path for a specific template
        
        Args:
            template_name: Name of the template
            
        Returns:
            File path of the template, or None if not found
        """
        templates = self.load_templates()
        return templates.get(template_name.lower())
