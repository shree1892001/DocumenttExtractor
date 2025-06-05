import os
import re
import json
import logging
from typing import Dict, Any
from Services.Processors.text_processor import TextProcessor
from Factories.DocumentFactory import TextExtractorFactory
from Common.document_constants import (
    DOCUMENT_TYPE_MAPPING,
    SUPPORTED_EXTENSIONS,
    MIN_CONFIDENCE_THRESHOLD,
    HIGH_CONFIDENCE_THRESHOLD,
    FIELD_PATTERNS
)

logger = logging.getLogger(__name__)

class TemplateMatcher:
    document_type_mapping = {
        "aadhaar": "aadhaar_card",
        "aadhaarcard": "aadhaar_card",
        "aadhar": "aadhaar_card",
        "aadharcard": "aadhaar_card",
        "pan": "pan_card",
        "pancard": "pan_card",
        "license": "license",
        "driving license": "license",
        "dl": "license"
    }

    SUPPORTED_EXTENSIONS = {'.docx', '.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.bmp'}

    MIN_CONFIDENCE_THRESHOLD = 0.4
    HIGH_CONFIDENCE_THRESHOLD = 0.8

    def __init__(self, api_key: str, templates_dir: str = "D:\\imageextractor\\identites\\Templates"):
        self.templates_dir = templates_dir
        self.api_key = api_key
        self.text_processor = TextProcessor(api_key)

        if not os.path.exists(self.templates_dir):
            logger.error(f"Templates directory does not exist: {self.templates_dir}")
            raise ValueError(f"Templates directory not found: {self.templates_dir}")

        self.templates = self._load_templates()
        if not self.templates:
            logger.error(f"No valid templates found in directory: {self.templates_dir}")
            raise ValueError(f"No valid templates found in directory: {self.templates_dir}")

    def _load_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load all templates from the templates directory"""
        templates = {}
        try:
            files = os.listdir(self.templates_dir)
            if not files:
                logger.error(f"Templates directory is empty: {self.templates_dir}")
                return templates

            logger.info(f"Found {len(files)} files in templates directory")

            for filename in files:
                file_path = os.path.join(self.templates_dir, filename)
                file_ext = os.path.splitext(filename)[1].lower()

                if file_ext not in self.SUPPORTED_EXTENSIONS:
                    logger.debug(f"Skipping unsupported file format: {filename}")
                    continue

                if os.path.isfile(file_path):
                    try:
                        doc_type = filename.replace('sample_', '').replace('.docx', '').replace('.pdf', '').replace(
                            '.jpg', '').replace('.png', '')
                        doc_type = self._standardize_document_type(doc_type)

                        logger.info(f"Processing template: {filename} as {doc_type}")

                        text_extractor = TextExtractorFactory.create_extractor(file_path, self.api_key)
                        template_text = text_extractor.extract_text(file_path)

                        if template_text:
                            templates[doc_type] = {
                                'content': template_text,
                                'fields': self._extract_fields_from_text(template_text),
                                'structure': template_text
                            }
                            logger.info(f"Successfully loaded template: {filename}")
                        else:
                            logger.warning(f"No text extracted from template: {filename}")
                    except Exception as e:
                        logger.warning(f"Error processing template file {filename}: {str(e)}")
                        continue

            if not templates:
                logger.error(f"No valid templates found in directory: {self.templates_dir}")
            else:
                logger.info(f"Successfully loaded {len(templates)} templates")

            return templates

        except Exception as e:
            logger.error(f"Error loading templates from directory {self.templates_dir}: {str(e)}")
            raise

    def _extract_fields_from_text(self, text: str) -> set:
        """Extract potential field names from text"""
        fields = set()

        field_patterns = [
            r'\{([^}]+)\}',
            r'([^:]+):',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        ]

        for pattern in field_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    field = match[0] if match[0] else match[1]
                else:
                    field = match
                fields.add(field.strip())

        return fields

    def _standardize_document_type(self, doc_type: str) -> str:
        """Standardize document type to match factory mappings"""
        doc_type = doc_type.lower().strip()
        return self.document_type_mapping.get(doc_type, doc_type)

    def _create_template_matching_prompt(self, input_text: str, template_content: str, doc_type: str) -> str:
        """Create a prompt for Gemini to match document against template"""
        return f"""
            You are a document analysis expert specializing in document verification. Your task is to analyze if the given document matches the {doc_type} template structure.

            Document Text:
            {input_text}

            Template Structure:
            {template_content}

            Please analyze the document and return a JSON response with:
            1. Whether this document matches the template (true/false)
            2. Confidence score (0-1) based on:
               - Key field presence (0.3 weight)
               - Content similarity (0.3 weight)
               - Structure match (0.2 weight)
               - Format consistency (0.2 weight)

            3. Extracted fields based on the template structure
            4. Any additional relevant information found

            Format the response as:
            {{
                "matches_template": true/false,
                "confidence_score": 0.0-1.0,
                "extracted_fields": {{
                    "field1": "value1",
                    "field2": "value2"
                }},
                "additional_info": "any additional relevant information",
                "matching_details": {{
                    "field_match": 0.0-1.0,
                    "structure_match": 0.0-1.0,
                    "format_match": 0.0-1.0,
                    "content_match": 0.0-1.0
                }}
            }}

            Important:
            - Consider partial matches if key fields are present
            - Account for variations in formatting and layout
            - Be lenient with confidence scoring if key identifiers are present
            - Consider a match if confidence score is above 0.4 and key fields are present
            - Look for document-specific security features and official elements
            - Consider regional variations in document formats
            - Account for different versions of the same document type
            """

    def match_document(self, file_path: str, section_text: str = None) -> Dict[str, Any]:
        """Match document against templates using Gemini"""
        if not self.templates:
            raise ValueError("No templates available for matching")

        best_match = {
            'document_type': None,
            'confidence': 0.0,
            'matched_fields': {},
            'additional_info': None,
            'template_id': None,
            'matching_details': {}
        }

        try:
            input_text = section_text
            if not input_text and file_path:
                text_extractor = TextExtractorFactory.create_extractor(file_path, self.api_key)
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        input_text = text_extractor.extract_text(file_path)
                        if input_text:
                            break
                    except Exception as e:
                        if attempt == max_retries - 1:
                            raise
                        logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                        continue

            if not input_text:
                raise ValueError("No text content available for matching")

            logger.info(f"Extracted text from document: {len(input_text)} characters")

            for template_id, template in self.templates.items():
                try:
                    template_doc_type = template.get('document_type', 'unknown')
                    prompt = self._create_template_matching_prompt(
                        input_text,
                        template['content'],
                        template_doc_type
                    )
                    response = self.text_processor.process_text(input_text, prompt)
                    match_result = json.loads(response.strip().replace("```json", "").replace("```", "").strip())

                    confidence = match_result.get('confidence_score', 0)
                    logger.info(f"Template match result for {template_id}: {confidence}")

                    if confidence > best_match['confidence']:
                        best_match = {
                            'document_type': match_result.get('document_type'),
                            'confidence': confidence,
                            'matched_fields': match_result.get('extracted_fields', {}),
                            'additional_info': match_result.get('additional_info'),
                            'template_id': template_id,
                            'matching_details': match_result.get('matching_details', {})
                        }
                        logger.info(f"Found better match: {template_id} with confidence {confidence}")
                        logger.info(
                            f"Matching details: {json.dumps(match_result.get('matching_details', {}), indent=2)}")
                except Exception as e:
                    logger.warning(f"Error matching template for {template_id}: {str(e)}")
                    continue

            if not best_match['document_type']:
                logger.error("No matching template found for the document")
                raise ValueError("No matching template found for the document")

            logger.info(f"Best match found: {best_match['document_type']} with confidence {best_match['confidence']}")
            return best_match

        except Exception as e:
            logger.error(f"Error matching document: {str(e)}")
            raise