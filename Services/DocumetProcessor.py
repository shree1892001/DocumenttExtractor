import fitz
import tempfile
from typing import List, Dict, Any, Optional
import os
import json
import re
from docx import Document
from Common.constants import *
from dataclasses import dataclass
from Extractor.ImageExtractor import ImageTextExtractor
from Extractor.Paddle import flatten_json
from Factories.DocumentFactory import (
    DocumentExtractorFactory,
    DocumentExtractor,
    TextExtractorFactory,
    BaseTextExtractor,
    DocxTextExtractor,
    PdfTextExtractor,
    ImageTextExtractor,
    TextExtractor
)
import logging
import google.generativeai as genai
from abc import ABC, abstractmethod
import pytesseract
from PIL import Image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DocumentInfo:
    document_type: str
    confidence_score: float
    extracted_data: Dict[str, Any]
    matched_fields: Dict[str, Any]


class BaseTextExtractor(ABC):
    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    @abstractmethod
    def extract_text(self, file_path: str) -> str:
        pass


class TextProcessor:
    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def process_text(self, text: str, prompt: str) -> str:
        """Process text using Gemini without image handling"""
        try:
            response = self.model.generate_content([prompt, text])
            return response.text
        except Exception as e:
            logger.error(f"Error processing text with Gemini: {str(e)}")
            raise


class TemplateMatcher:
    # Define document type mapping as a class variable
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

    # Define supported file extensions
    SUPPORTED_EXTENSIONS = {'.docx', '.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.bmp', '.txt'}

    # Define confidence thresholds
    MIN_CONFIDENCE_THRESHOLD = 0.4
    HIGH_CONFIDENCE_THRESHOLD = 0.8

    def __init__(self, api_key: str, templates_dir: str = "D:\\imageextractor\\identites\\Templates"):
        self.templates_dir = templates_dir
        self.api_key = api_key
        self.text_processor = TextProcessor(api_key)

        # Validate templates directory
        if not os.path.exists(self.templates_dir):
            logger.error(f"Templates directory does not exist: {self.templates_dir}")
            raise ValueError(f"Templates directory not found: {self.templates_dir}")

        # Load templates
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

                # Skip unsupported file formats
                if file_ext not in self.SUPPORTED_EXTENSIONS:
                    logger.debug(f"Skipping unsupported file format: {filename}")
                    continue

                if os.path.isfile(file_path):
                    try:
                        # Extract document type from filename
                        doc_type = filename.replace('sample_', '').replace('.docx', '').replace('.pdf', '').replace(
                            '.jpg', '').replace('.png', '')
                        doc_type = self._standardize_document_type(doc_type)

                        logger.info(f"Processing template: {filename} as {doc_type}")

                        # Use TextExtractorFactory to get appropriate extractor
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
        # Look for text between brackets or after colons
        field_patterns = [
            r'\{([^}]+)\}',  # {field_name}
            r'([^:]+):',  # field_name:
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'  # Capitalized words
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
        mapping = {
            "aadhaar": "aadhaar_card",
            "aadhaarcard": "aadhaar_card",
            "aadhar": "aadhaar_card",
            "aadharcard": "aadhaar_card",
            "pan": "pan_card",
            "pancard": "pan_card",
            "license": "license",
            "driving license": "license",
            "dl": "license",
            "indian_license": "license",
            "florida_license": "license",
            "passport": "passport"
        }
        return mapping.get(doc_type, doc_type)

    def _create_template_matching_prompt(self, input_text: str, template_content: str, doc_type: str) -> str:
        """Create a prompt for Gemini to match document against template"""
        return f"""
                    You are a document analysis expert specializing in identity document verification. Your task is to analyze if the given document matches the {doc_type} template structure.

                    Document Text:
                    {input_text}

                    Template Structure:
                    {template_content}

                    Please analyze the document and return a JSON response with:
                    1. Whether this document matches the {doc_type} template (true/false)
                    2. Confidence score (0-1) based on:
                       - Key field presence (0.3 weight): Check if essential fields like name, ID number, etc. are present
                       - Content similarity (0.3 weight): Compare the actual content with template
                       - Structure match (0.2 weight): Layout and organization similarity
                       - Format consistency (0.2 weight): Consistent formatting and style

                    For {doc_type} specifically, look for these key indicators:
                    {self._get_document_specific_indicators(doc_type)}

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
                        "additional_info": "any additional relevant information"
                    }}

                    Important:
                    - Consider partial matches if key fields are present
                    - Account for variations in formatting and layout
                    - Be lenient with confidence scoring if key identifiers are present
                    - Consider a match if confidence score is above 0.4 and key fields are present
                    """

    def _get_document_specific_indicators(self, doc_type: str) -> str:
        """Get document-specific indicators for matching"""
        indicators = {
            "aadhaar_card": """
                        - 12-digit Aadhaar number
                        - Name of the holder
                        - Date of birth
                        - Gender
                        - Address
                        - UIDAI logo or text
                        - QR code or barcode
                        """,
            "license": """
                        - License number
                        - Name of the holder
                        - Date of birth
                        - Address
                        - License type/class
                        - Issue and expiry dates
                        - Issuing authority
                        """,
            "pan_card": """
                        - 10-character PAN number
                        - Name of the holder
                        - Father's name
                        - Date of birth
                        - PAN card number format
                        - Income Tax Department text
                        """
        }
        return indicators.get(doc_type, "Look for standard identity document fields and structure.")

    def match_document(self, file_path: str) -> Dict[str, Any]:
        """Match document against templates using Gemini"""
        if not os.path.exists(file_path):
            raise ValueError(f"Document file not found: {file_path}")

        if not self.templates:
            raise ValueError("No templates available for matching")

        best_match = {
            'document_type': None,
            'confidence': 0.0,
            'matched_fields': {},
            'additional_info': None
        }

        try:
            # For .txt files, read the content directly
            if file_path.lower().endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    input_text = f.read()
            else:
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
                raise ValueError(f"Could not extract text from document: {file_path}")

            logger.info(f"Extracted text from document: {len(input_text)} characters")

            # Try to match against each template
            for doc_type, template in self.templates.items():
                try:
                    prompt = self._create_template_matching_prompt(input_text, template['content'], doc_type)
                    response = self.text_processor.process_text(input_text, prompt)
                    match_result = json.loads(response.strip().replace("```json", "").replace("```", "").strip())

                    confidence = match_result.get('confidence_score', 0)
                    logger.info(f"Template match result for {doc_type}: {confidence}")

                    # Update best match if this is better
                    if confidence > best_match['confidence']:
                        best_match = {
                            'document_type': doc_type,
                            'confidence': confidence,
                            'matched_fields': match_result.get('extracted_fields', {}),
                            'additional_info': match_result.get('additional_info')
                        }
                        logger.info(f"Found better match: {doc_type} with confidence {confidence}")
                except Exception as e:
                    logger.warning(f"Error matching template for {doc_type}: {str(e)}")
                    continue

            if not best_match['document_type']:
                logger.error("No matching template found for the document")
                raise ValueError("No matching template found for the document")

            logger.info(f"Best match found: {best_match['document_type']} with confidence {best_match['confidence']}")
            return best_match

        except Exception as e:
            logger.error(f"Error matching document: {str(e)}")
            raise


class DocumentClassifier:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.template_matcher = TemplateMatcher(api_key)

    def identify_document_type(self, file_path: str) -> DocumentInfo:
        try:
            # Match against templates using Gemini
            template_match = self.template_matcher.match_document(file_path)

            # Use the best match even if below threshold
            if template_match['document_type']:
                return DocumentInfo(
                    document_type=template_match['document_type'],
                    confidence_score=template_match['confidence'],
                    extracted_data=template_match['matched_fields'],
                    matched_fields=template_match['matched_fields']
                )
            else:
                raise ValueError("Document type not identified")

        except Exception as e:
            logger.exception("Failed to classify document")
            raise ValueError(f"Failed to classify document: {str(e)}")


class DocumentLearner:
    def __init__(self, api_key: str, templates_dir: str):
        self.api_key = api_key
        self.templates_dir = templates_dir
        self.text_processor = TextProcessor(api_key)
        self.learning_data = self._load_learning_data()

    def _load_learning_data(self) -> Dict[str, Any]:
        """Load or initialize learning data"""
        try:
            data_path = os.path.join(os.path.dirname(self.templates_dir), 'data', 'learning_data.json')
            if os.path.exists(data_path):
                with open(data_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load learning data: {str(e)}")

        return {
            "document_types": {},
            "field_patterns": {},
            "common_phrases": {},
            "structure_patterns": {}
        }

    def _save_learning_data(self):
        """Save learning data"""
        try:
            data_path = os.path.join(os.path.dirname(self.templates_dir), 'data', 'learning_data.json')
            os.makedirs(os.path.dirname(data_path), exist_ok=True)
            with open(data_path, 'w', encoding='utf-8') as f:
                json.dump(self.learning_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving learning data: {str(e)}")

    def identify_document_type(self, text: str) -> Dict[str, Any]:
        """Identify document type using learned patterns and AI"""
        try:
            # Use Gemini to analyze document
            prompt = f"""
            Analyze this document and determine its type.
            Consider the content, structure, and purpose.
            If it matches a known document type, identify it.
            If it's a new type, suggest a classification.

            Text:
            {text}

            Return a JSON object with:
            {{
                "document_type": "identified or suggested type",
                "confidence": 0-1,
                "reasoning": "explanation",
                "is_new_type": true/false,
                "key_characteristics": ["list of characteristics"],
                "suggested_fields": ["list of fields to extract"]
            }}

            Important:
            - Always include document_type and confidence
            - If is_new_type is true, include key_characteristics
            - If is_new_type is true, document_type should be the suggested type
            - Return ONLY the JSON object, no additional text
            """
            response = self.text_processor.process_text(text, prompt)
            
            # Clean the response to ensure it's valid JSON
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            try:
                result = json.loads(response)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON response: {response}")
                return {
                    "document_type": "unknown",
                    "confidence": 0.0,
                    "reasoning": "Invalid response format",
                    "is_new_type": True,
                    "key_characteristics": [],
                    "suggested_fields": []
                }

            # Ensure required fields are present
            if "document_type" not in result:
                result["document_type"] = "unknown"
            if "confidence" not in result:
                result["confidence"] = 0.0
            if "is_new_type" not in result:
                result["is_new_type"] = True
            if "key_characteristics" not in result:
                result["key_characteristics"] = []
            if "suggested_fields" not in result:
                result["suggested_fields"] = []

            # If it's a known type, enhance with learned patterns
            if not result["is_new_type"] and result["document_type"] in self.learning_data["document_types"]:
                known_type = self.learning_data["document_types"][result["document_type"]]
                result["confidence"] *= (1 + len(known_type["common_phrases"]) / 100)
                result["suggested_fields"].extend(known_type.get("common_fields", []))

            return result

        except Exception as e:
            logger.error(f"Error identifying document type: {str(e)}")
            return {
                "document_type": "unknown",
                "confidence": 0.0,
                "reasoning": f"Error during identification: {str(e)}",
                "is_new_type": True,
                "key_characteristics": [],
                "suggested_fields": []
            }

    def learn_new_document_type(self, doc_type: str, text: str, characteristics: List[str]) -> None:
        """Learn from a new document type"""
        try:
            if doc_type not in self.learning_data["document_types"]:
                self.learning_data["document_types"][doc_type] = {
                    "samples": [],
                    "common_phrases": set(),
                    "common_fields": set(),
                    "structure_patterns": []
                }

            # Extract common phrases
            prompt = f"""
            Extract key phrases from this document that are characteristic of its type.
            Focus on official terms, headers, and unique identifiers.

            Text:
            {text}

            Return a JSON array of phrases.
            """
            response = self.text_processor.process_text(text, prompt)
            phrases = json.loads(response.strip())
            self.learning_data["document_types"][doc_type]["common_phrases"].update(phrases)

            # Learn document structure
            prompt = f"""
            Analyze the structure of this document and identify key structural elements.
            Focus on layout, sections, and organization.

            Text:
            {text}

            Return a JSON object describing the document structure.
            """
            response = self.text_processor.process_text(text, prompt)
            structure = json.loads(response.strip())
            self.learning_data["document_types"][doc_type]["structure_patterns"].append(structure)

            # Save updated learning data
            self._save_learning_data()
            logger.info(f"Learned new document type: {doc_type}")

        except Exception as e:
            logger.error(f"Error learning new document type: {str(e)}")

    def extract_fields(self, text: str, doc_type: str) -> Dict[str, Any]:
        """Extract fields using learned patterns and AI"""
        try:
            # Get learned patterns for this document type
            patterns = self.learning_data["document_types"].get(doc_type, {})
            
            # Use Gemini to extract fields
            prompt = f"""
            Extract fields from this document.
            Consider these known characteristics:
            {json.dumps(patterns, indent=2)}

            Text:
            {text}

            Return a JSON object with extracted fields.
            For example:
            {{
                "name": "John Doe",
                "id_number": "123456789",
                "date_of_birth": "1990-01-01",
                "address": "123 Main St",
                "issue_date": "2020-01-01",
                "expiry_date": "2030-01-01"
            }}

            Important:
            - Extract ALL visible information from the document
            - If a field is not found, use null as the value
            - For dates, use YYYY-MM-DD format
            - For numbers, extract them exactly as shown
            - For names and addresses, preserve the exact spelling and formatting
            - Return ONLY the JSON object, no additional text
            """
            response = self.text_processor.process_text(text, prompt)
            
            # Clean the response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            try:
                extracted_fields = json.loads(response)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON response from field extraction: {response}")
                # Try to extract fields using a simpler approach
                return self._extract_fields_fallback(text, doc_type)

            # Learn from this extraction
            self._learn_from_extraction(doc_type, text, extracted_fields)

            return extracted_fields

        except Exception as e:
            logger.error(f"Error extracting fields: {str(e)}")
            # Try fallback extraction
            return self._extract_fields_fallback(text, doc_type)

    def _extract_fields_fallback(self, text: str, doc_type: str) -> Dict[str, Any]:
        """Fallback method for field extraction when primary method fails"""
        try:
            prompt = f"""
            Extract basic information from this document.
            Look for common fields like name, ID number, dates, and addresses.

            Text:
            {text}

            Return a JSON object with these fields:
            {{
                "name": "full name if found",
                "id_number": "identification number if found",
                "date_of_birth": "birth date if found (YYYY-MM-DD)",
                "address": "full address if found",
                "issue_date": "document issue date if found (YYYY-MM-DD)",
                "expiry_date": "document expiry date if found (YYYY-MM-DD)"
            }}

            Important:
            - Use null for any field not found
            - Return ONLY the JSON object
            """
            response = self.text_processor.process_text(text, prompt)
            
            # Clean the response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                logger.error("Fallback field extraction also failed")
                return {
                    "name": None,
                    "id_number": None,
                    "date_of_birth": None,
                    "address": None,
                    "issue_date": None,
                    "expiry_date": None
                }
        except Exception as e:
            logger.error(f"Error in fallback field extraction: {str(e)}")
            return {
                "name": None,
                "id_number": None,
                "date_of_birth": None,
                "address": None,
                "issue_date": None,
                "expiry_date": None
            }

    def _learn_from_extraction(self, doc_type: str, text: str, fields: Dict[str, Any]) -> None:
        """Learn from successful field extraction"""
        try:
            if doc_type not in self.learning_data["document_types"]:
                return

            # Convert sets to lists for JSON serialization
            if "common_fields" in self.learning_data["document_types"][doc_type]:
                self.learning_data["document_types"][doc_type]["common_fields"] = list(
                    self.learning_data["document_types"][doc_type]["common_fields"]
                )
            if "common_phrases" in self.learning_data["document_types"][doc_type]:
                self.learning_data["document_types"][doc_type]["common_phrases"] = list(
                    self.learning_data["document_types"][doc_type]["common_phrases"]
                )

            # Update common fields
            self.learning_data["document_types"][doc_type]["common_fields"] = list(
                set(self.learning_data["document_types"][doc_type]["common_fields"]).union(set(fields.keys()))
            )

            # Learn field patterns
            for field_name, field_value in fields.items():
                if field_value:
                    prompt = f"""
                    Find the pattern in the text that indicates the field "{field_name}" with value "{field_value}".
                    Return a JSON object with the pattern and context.

                    Text:
                    {text}

                    Return ONLY the JSON object, no additional text.
                    """
                    response = self.text_processor.process_text(text, prompt)
                    
                    # Clean the response
                    response = response.strip()
                    if response.startswith("```json"):
                        response = response[7:]
                    if response.endswith("```"):
                        response = response[:-3]
                    response = response.strip()
                    
                    try:
                        pattern = json.loads(response)
                    except json.JSONDecodeError:
                        continue

                    if "field_patterns" not in self.learning_data:
                        self.learning_data["field_patterns"] = {}
                    if doc_type not in self.learning_data["field_patterns"]:
                        self.learning_data["field_patterns"][doc_type] = {}
                    if field_name not in self.learning_data["field_patterns"][doc_type]:
                        self.learning_data["field_patterns"][doc_type][field_name] = []

                    self.learning_data["field_patterns"][doc_type][field_name].append(pattern)

            # Save updated learning data
            self._save_learning_data()

        except Exception as e:
            logger.warning(f"Error learning from extraction: {str(e)}")


class DocumentProcessor:
    def __init__(self, api_key: str, templates_dir: str = "D:\\imageextractor\\identites\\Templates"):
        self.api_key = api_key
        self.templates_dir = templates_dir
        self.classifier = DocumentClassifier(api_key)
        self.text_extractor = TextExtractor(api_key)
        self.text_processor = TextProcessor(api_key)
        self.document_learner = DocumentLearner(api_key, templates_dir)
        self.template_matcher = TemplateMatcher(api_key, templates_dir)

        # Load document mappings from configuration
        self.document_mappings = self._load_document_mappings()
        
        # Define basic thresholds
        self.MIN_CONFIDENCE_THRESHOLD = 0.4  # Lowered threshold for better matching
        self.MIN_GENUINENESS_SCORE = 0.6     # Lowered threshold for genuineness check

    def _load_document_mappings(self) -> Dict[str, Any]:
        """Load document mappings from configuration file"""
        try:
            config_path = os.path.join(os.path.dirname(self.templates_dir), 'config', 'document_mappings.json')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)

            # If config file doesn't exist, create default mappings
            default_mappings = {
                "document_types": {
                    "identity_documents": {
                        "aadhaar_card": {
                            "patterns": [
                                r"(?i)aadhaar|aadhar|uidai|unique\s*id",
                                r"(?i)आधार|यूआईडीएआई"
                            ],
                            "fields": [
                                "aadhaar_number",
                                "name",
                                "date_of_birth",
                                "gender",
                                "address"
                            ]
                        },
                        "pan_card": {
                            "patterns": [
                                r"(?i)pan|permanent\s*account|income\s*tax",
                                r"(?i)tax\s*id|tax\s*number"
                            ],
                            "fields": [
                                "pan_number",
                                "name",
                                "father_name",
                                "date_of_birth"
                            ]
                        },
                        "license": {
                            "patterns": [
                                r"(?i)license|dl|driving|permit|rto|dmv",
                                r"(?i)vehicle|motor|transport"
                            ],
                            "fields": [
                                "license_number",
                                "name",
                                "date_of_birth",
                                "address",
                                "valid_from",
                                "valid_until"
                            ]
                        }
                    },
                    "business_documents": {
                        "incorporation_certificate": {
                            "patterns": [
                                r"(?i)incorporation|certificate\s*of\s*formation",
                                r"(?i)articles\s*of\s*incorporation"
                            ],
                            "fields": [
                                "company_name",
                                "incorporation_date",
                                "registration_number",
                                "state",
                                "registered_agent"
                            ]
                        },
                        "business_license": {
                            "patterns": [
                                r"(?i)business\s*license|permit",
                                r"(?i)commercial\s*license"
                            ],
                            "fields": [
                                "business_name",
                                "license_number",
                                "issue_date",
                                "expiry_date",
                                "business_type"
                            ]
                        },
                        "download": {
                            "patterns": [
                                r"(?i)download|specimen|persona",
                                r"(?i)document|form|template"
                            ],
                            "fields": [
                                "document_type",
                                "document_number",
                                "issue_date",
                                "expiry_date",
                                "holder_name",
                                "address",
                                "identification_number",
                                "issuing_authority",
                                "status",
                                "additional_info"
                            ]
                        }
                    },
                    "financial_documents": {
                        "bank_statement": {
                            "patterns": [
                                r"(?i)bank\s*statement|account\s*statement",
                                r"(?i)transaction\s*history"
                            ],
                            "fields": [
                                "account_number",
                                "account_holder",
                                "statement_period",
                                "transactions"
                            ]
                        },
                        "tax_return": {
                            "patterns": [
                                r"(?i)tax\s*return|income\s*tax\s*return",
                                r"(?i)form\s*1040|form\s*16"
                            ],
                            "fields": [
                                "tax_year",
                                "taxpayer_name",
                                "tax_id",
                                "total_income",
                                "tax_liability"
                            ]
                        }
                    }
                },
                "field_patterns": {
                    "dates": [
                        r"\d{1,2}[-/]\d{1,2}[-/]\d{2,4}",
                        r"\d{4}[-/]\d{1,2}[-/]\d{1,2}"
                    ],
                    "numbers": [
                        r"\b\d{10,12}\b",
                        r"\b[A-Z]{2}\d{7}\b"
                    ],
                    "names": [
                        r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b"
                    ]
                }
            }

            # Create config directory if it doesn't exist
            os.makedirs(os.path.dirname(config_path), exist_ok=True)

            # Save default mappings
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_mappings, f, indent=2)

            return default_mappings

        except Exception as e:
            logger.error(f"Error loading document mappings: {str(e)}")
            return {}

    def _standardize_document_type(self, doc_type: str) -> str:
        """Standardize document type using loaded mappings"""
        try:
            doc_type = doc_type.lower().strip()

            # Check each category and document type
            for category, types in self.document_mappings.get("document_types", {}).items():
                for type_name, type_info in types.items():
                    # Check patterns
                    for pattern in type_info.get("patterns", []):
                        if re.search(pattern, doc_type):
                            return type_name

            # If no match found, try to extract base type
            base_type = self._extract_base_type(doc_type)
            if base_type:
                return base_type

            # If all else fails, return the original type
            logger.warning(f"No pattern match found for document type: {doc_type}")
            return doc_type

        except Exception as e:
            logger.error(f"Error standardizing document type: {str(e)}")
            return doc_type

    def _extract_base_type(self, doc_type: str) -> Optional[str]:
        """Extract base document type from filename or text"""
        try:
            # Remove common prefixes and suffixes
            doc_type = re.sub(r'(?i)sample_|template_|example_', '', doc_type)
            doc_type = re.sub(r'\.(docx|pdf|jpg|png|jpeg)$', '', doc_type)

            # Remove location/country prefixes
            doc_type = re.sub(r'^(indian|florida|california|texas|new_york|uk|us|canada)_', '', doc_type)

            # Remove version numbers
            doc_type = re.sub(r'_v\d+', '', doc_type)

            # Remove dates
            doc_type = re.sub(r'_\d{4}(_\d{2}){0,2}', '', doc_type)

            # Clean up any remaining special characters
            doc_type = re.sub(r'[^a-z0-9]', '_', doc_type.lower())
            doc_type = re.sub(r'_+', '_', doc_type)  # Replace multiple underscores with single
            doc_type = doc_type.strip('_')

            # Check if the cleaned type matches any of our patterns
            for standardized_type, patterns in self.document_mappings.get("document_types", {}).items():
                for pattern in patterns.get("patterns", []):
                    if pattern.search(doc_type):
                        return standardized_type

            return None

        except Exception as e:
            logger.error(f"Error extracting base type: {str(e)}")
            return None

    def _get_document_specific_fields(self, doc_type: str) -> List[str]:
        """Get document-specific fields from mappings"""
        try:
            # Check each category and document type
            for category, types in self.document_mappings.get("document_types", {}).items():
                if doc_type in types:
                    return types[doc_type].get("fields", [])

            return []

        except Exception as e:
            logger.error(f"Error getting document fields: {str(e)}")
            return []

    def add_document_type(self, category: str, doc_type: str, patterns: List[str], fields: List[str]) -> None:
        """Add a new document type to the mappings"""
        try:
            if "document_types" not in self.document_mappings:
                self.document_mappings["document_types"] = {}

            if category not in self.document_mappings["document_types"]:
                self.document_mappings["document_types"][category] = {}

            self.document_mappings["document_types"][category][doc_type] = {
                "patterns": patterns,
                "fields": fields
            }

            # Save updated mappings
            config_path = os.path.join(os.path.dirname(self.templates_dir), 'config', 'document_mappings.json')
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.document_mappings, f, indent=2)

            logger.info(f"Added new document type: {doc_type} to category: {category}")

        except Exception as e:
            logger.error(f"Error adding document type: {str(e)}")

    def _extract_text_from_docx_images(self, file_path: str) -> List[str]:
        """Extract text from images embedded in a DOCX file"""
        image_texts = []
        try:
            # Create a temporary directory for extracted images
            with tempfile.TemporaryDirectory() as temp_dir:
                # Extract images from the DOCX file
                doc = Document(file_path)
                image_count = 0

                # Process each paragraph for inline images
                for rel in doc.part.rels.values():
                    if "image" in rel.target_ref:
                        image_count += 1
                        image_path = os.path.join(temp_dir, f"image_{image_count}.png")

                        # Save the image
                        with open(image_path, 'wb') as f:
                            f.write(rel.target_part.blob)

                        # Extract text from the image
                        try:
                            image = Image.open(image_path)
                            text = pytesseract.image_to_string(image)
                            if text.strip():
                                image_texts.append(text.strip())
                        except Exception as e:
                            logger.warning(f"Error extracting text from image {image_count}: {str(e)}")

                logger.info(f"Extracted text from {len(image_texts)} images in DOCX file")
                return image_texts

        except Exception as e:
            logger.error(f"Error extracting images from DOCX: {str(e)}")
            return []

    def _extract_fields_from_text(self, text: str, doc_type: str) -> Dict[str, Any]:
        """Extract fields from text based on document type"""
        try:
            # Get fields to extract for this document type
            fields_to_extract = self._get_document_specific_fields(doc_type)

            # Create extraction prompt
            prompt = f"""
            Extract the following fields from this document text:
            {', '.join(fields_to_extract)}

            Document Text:
            {text}

            Return a JSON object with the extracted fields. For example:
            {{
                "field1": "value1",
                "field2": "value2"
            }}

            Important:
            - Extract ALL visible information from the document
            - If a field is not found, use null as the value
            - For dates, use YYYY-MM-DD format
            - For numbers, extract them exactly as shown
            - For names and addresses, preserve the exact spelling and formatting
            - Return ONLY the JSON object, no additional text
            - Be thorough in extracting all possible information
            - Look for information in headers, footers, and any visible text
            """

            # Process with Gemini
            response = self.text_processor.process_text(text, prompt)

            # Clean the response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()

            try:
                extracted_fields = json.loads(response)
                logger.info(f"Extracted fields: {json.dumps(extracted_fields, indent=2)}")
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing extracted fields: {str(e)}")
                return {}

            return extracted_fields

        except Exception as e:
            logger.error(f"Error extracting fields: {str(e)}")
            return {}

    def process_file(self, file_path: str, min_confidence: float = 0.0) -> List[Dict[str, Any]]:
        """Process a file that may contain multiple documents"""
        try:
            if file_path.lower().endswith('.docx'):
                return self._process_docx(file_path, min_confidence)
            else:
                # First, try to match the document against templates
                try:
                    template_match = self.template_matcher.match_document(file_path)
                    if not template_match:
                        return [{
                            "status": "rejected",
                            "document_type": "unknown",
                            "source_file": file_path,
                            "rejection_reason": "No template match found"
                        }]

                    # Use the matched document type even if confidence is low
                    doc_type = template_match['document_type']
                    logger.info(f"Document matched template: {doc_type} with confidence {template_match['confidence']}")

                    # Extract text from the document
                    input_text = self.text_extractor.extract_text(file_path)
                    if not input_text.strip():
                        logger.error("No text could be extracted from the document")
                        return [{
                            "status": "rejected",
                            "document_type": doc_type,
                            "source_file": file_path,
                            "rejection_reason": "No text could be extracted"
                        }]

                    # Extract fields using learned patterns
                    extracted_fields = self._extract_fields_from_text(input_text, doc_type)

                    # Merge template-matched fields with extracted fields
                    if template_match.get('matched_fields'):
                        extracted_fields.update(template_match['matched_fields'])

                    # Verify document authenticity with lower threshold
                    verification_result = self.verify_document(extracted_fields, doc_type)

                    # Return result even if verification fails, but mark it appropriately
                    return [{
                        "extracted_data": extracted_fields,
                        "status": "success" if verification_result["is_genuine"] else "warning",
                        "confidence": template_match['confidence'],
                        "document_type": doc_type,
                        "source_file": file_path,
                        "validation_level": "lenient",
                        "verification_result": verification_result,
                        "template_match": {
                            "confidence": template_match['confidence'],
                            "matched_fields": template_match.get('matched_fields', {}),
                            "additional_info": template_match.get('additional_info')
                        }
                    }]

                except Exception as e:
                    logger.error(f"Error matching template: {str(e)}")
                    return [{
                        "status": "rejected",
                        "document_type": "unknown",
                        "source_file": file_path,
                        "rejection_reason": f"Error matching template: {str(e)}"
                    }]

        except Exception as e:
            logger.exception(f"Error processing file {file_path}")
            return [{
                "status": "error",
                "document_type": "unknown",
                "source_file": file_path,
                "rejection_reason": f"Error processing document: {str(e)}"
            }]

    def _process_docx(self, file_path: str, min_confidence: float) -> List[Dict[str, Any]]:
        """Process a DOCX file that may contain multiple documents"""
        results = []
        try:
            # Extract text from paragraphs and tables
            doc = Document(file_path)
            text_content = []
            
            # Extract text from paragraphs
            for para in doc.paragraphs:
                if para.text.strip():
                    text_content.append(para.text.strip())
            
            # Extract text from tables
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if cell.text.strip():
                            text_content.append(cell.text.strip())
            
            # Combine all text
            text = '\n'.join(text_content)
            
            # Extract images from the document
            image_texts = self._extract_text_from_docx_images(file_path)
            
            # Combine text from document and images
            all_text = text
            if image_texts:
                all_text += '\n' + '\n'.join(str(img_text) for img_text in image_texts if img_text)
            
            if not all_text.strip():
                logger.warning(f"No text content found in DOCX file: {file_path}")
                return [{
                    "status": "rejected",
                    "document_type": "unknown",
                    "source_file": file_path,
                    "rejection_reason": "No text content found in document"
                }]
            
            # Try to match the combined text against templates
            try:
                # Create a temporary file with the extracted text for template matching
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as temp_file:
                    temp_file.write(all_text)
                    temp_file_path = temp_file.name

                template_match = self.template_matcher.match_document(temp_file_path)
                
                # Clean up the temporary file
                try:
                    os.unlink(temp_file_path)
                except Exception as e:
                    logger.warning(f"Error deleting temporary file: {str(e)}")

                if not template_match or template_match['confidence'] < self.MIN_CONFIDENCE_THRESHOLD:
                    return [{
                        "status": "rejected",
                        "document_type": "unknown",
                        "source_file": file_path,
                        "rejection_reason": f"Document does not match any known template (confidence: {template_match['confidence'] if template_match else 0})"
                    }]
                
                logger.info(f"Document matched template: {template_match['document_type']} with confidence {template_match['confidence']}")
            except Exception as e:
                logger.error(f"Error matching template: {str(e)}")
                return [{
                    "status": "rejected",
                    "document_type": "unknown",
                    "source_file": file_path,
                    "rejection_reason": f"Error matching template: {str(e)}"
                }]
            
            # Extract fields using learned patterns
            extracted_fields = self.document_learner.extract_fields(
                all_text,
                template_match['document_type']
            )
            
            # Merge template-matched fields with extracted fields
            if template_match.get('matched_fields'):
                extracted_fields.update(template_match['matched_fields'])
            
            # Verify document authenticity
            verification_result = self.verify_document(extracted_fields, template_match['document_type'])
            
            if not verification_result["is_genuine"]:
                return [{
                    "status": "rejected",
                    "document_type": template_match['document_type'],
                    "source_file": file_path,
                    "rejection_reason": verification_result["rejection_reason"],
                    "verification_result": verification_result
                }]
            
            # Return successful result
            return [{
                "extracted_data": extracted_fields,
                "status": "success",
                "confidence": template_match['confidence'],
                "document_type": template_match['document_type'],
                "source_file": file_path,
                "validation_level": "strict",
                "verification_result": verification_result,
                "template_match": {
                    "confidence": template_match['confidence'],
                    "matched_fields": template_match.get('matched_fields', {}),
                    "additional_info": template_match.get('additional_info')
                }
            }]
            
        except Exception as e:
            logger.error(f"Error processing DOCX file: {str(e)}")
            return [{
                "status": "error",
                "document_type": "unknown",
                "source_file": file_path,
                "rejection_reason": f"Error processing document: {str(e)}"
            }]

    def verify_document(self, extracted_data: Dict[str, Any], doc_type: str) -> Dict[str, Any]:
        """Verify document authenticity and data validity"""
        try:
            # Create a comprehensive verification prompt
            verification_prompt = f"""
            You are a document verification expert. Analyze this document text and determine if it is genuine.
            Provide a detailed verification report with specific checks and findings.

            Document Text:
            {json.dumps(extracted_data, indent=2)}

            Perform the following checks:

            1. Document Authenticity:
               - Check for official text and formatting
               - Verify presence of official logos and seals
               - Validate document structure and layout
               - Check for security features
               - Verify document quality and printing standards
               - Look for official headers and footers
               - Check for any official stamps or marks

            2. Security Feature Analysis:
               - Look for official seals and stamps
               - Check for watermarks or holograms
               - Verify presence of security patterns
               - Look for QR codes or barcodes
               - Check for any digital signatures
               - Verify any security numbers or codes
               - Look for any anti-counterfeit measures

            3. Red Flag Detection:
               - Look for signs of tampering
               - Check for inconsistencies in formatting
               - Verify document quality
               - Look for any suspicious elements
               - Check for any signs of forgery
               - Look for any anomalies in text
               - Check for any signs of photocopying

            4. Document Quality:
               - Check printing quality
               - Verify text alignment
               - Check for any smudges or marks
               - Verify color consistency
               - Check for any signs of poor quality
               - Verify professional formatting
               - Check for any signs of manipulation

            Return a JSON response with:
            {{
                "is_genuine": true/false,
                "confidence_score": 0.0-1.0,
                "rejection_reason": "reason if not genuine",
                "verification_checks": {{
                    "authenticity": {{
                        "passed": true/false,
                        "details": "explanation"
                    }},
                    "security_features": {{
                        "passed": true/false,
                        "details": "explanation"
                    }},
                    "red_flags": {{
                        "passed": true/false,
                        "details": "explanation"
                    }},
                    "quality": {{
                        "passed": true/false,
                        "details": "explanation"
                    }}
                }},
                "security_features_found": ["list of security features"],
                "verification_summary": "Overall verification summary"
            }}

            Important:
            - Be thorough in your analysis
            - Consider all aspects of document authenticity
            - Provide detailed explanations for your decisions
            - Look for any signs of forgery or tampering
            - Consider document-specific security features
            - Check for any inconsistencies or anomalies
            - Pay attention to document quality and formatting
            """

            # Process with Gemini
            response = self.text_processor.process_text(json.dumps(extracted_data), verification_prompt)
            verification_result = json.loads(response.strip().replace("```json", "").replace("```", "").strip())

            # Log verification results
            logger.info(f"Document genuineness verification results: {json.dumps(verification_result, indent=2)}")

            return verification_result

        except Exception as e:
            logger.exception(f"Error verifying document genuineness: {str(e)}")
            return {
                "is_genuine": False,
                "confidence_score": 0.0,
                "rejection_reason": f"Error during verification: {str(e)}",
                "verification_checks": {
                    "authenticity": {"passed": False, "details": f"Error during verification: {str(e)}"},
                    "security_features": {"passed": False, "details": "Verification failed"},
                    "red_flags": {"passed": False, "details": "Verification failed"},
                    "quality": {"passed": False, "details": "Verification failed"}
                },
                "security_features_found": [],
                "verification_summary": f"Document verification failed due to error: {str(e)}"
            }

    def _validate_with_leniency(self, extracted_data: Dict[str, Any], doc_type: str) -> bool:
        """Validate extracted data with lenient rules for low confidence matches"""
        try:
            data = extracted_data.get("data", {})

            # Check if we have at least some basic information
            if not data:
                return False

            # Document type specific lenient validation
            if doc_type == "license":
                # For license, require at least one of these fields
                required_fields = ["license_number", "name", "date_of_birth"]
                return any(field in data for field in required_fields)
            elif doc_type == "aadhaar_card":
                # For Aadhaar, require at least one of these fields
                required_fields = ["aadhaar_number", "name", "date_of_birth"]
                return any(field in data for field in required_fields)
            elif doc_type == "pan_card":
                # For PAN, require at least one of these fields
                required_fields = ["pan_number", "name", "date_of_birth"]
                return any(field in data for field in required_fields)
            else:
                # For other document types, require at least one field
                return len(data) > 0

        except Exception as e:
            logger.error(f"Error in lenient validation: {str(e)}")
            return False

    def _verify_document_genuineness(self, text: str) -> Dict[str, Any]:
        """Verify if the document is genuine based on text content"""
        try:
            # Create a comprehensive verification prompt
            verification_prompt = f"""
            You are a document verification expert. Analyze this document text and determine if it is genuine.
            Provide a detailed verification report with specific checks and findings.

            Document Text:
            {text}

            Perform the following checks:

            1. Document Authenticity:
               - Check for official text and formatting
               - Verify presence of official logos and seals
               - Validate document structure and layout
               - Check for security features
               - Verify document quality and printing standards
               - Look for official headers and footers
               - Check for any official stamps or marks

            2. Security Feature Analysis:
               - Look for official seals and stamps
               - Check for watermarks or holograms
               - Verify presence of security patterns
               - Look for QR codes or barcodes
               - Check for any digital signatures
               - Verify any security numbers or codes
               - Look for any anti-counterfeit measures

            3. Red Flag Detection:
               - Look for signs of tampering
               - Check for inconsistencies in formatting
               - Verify document quality
               - Look for any suspicious elements
               - Check for any signs of forgery
               - Look for any anomalies in text
               - Check for any signs of photocopying

            4. Document Quality:
               - Check printing quality
               - Verify text alignment
               - Check for any smudges or marks
               - Verify color consistency
               - Check for any signs of poor quality
               - Verify professional formatting
               - Check for any signs of manipulation

            Return a JSON response with:
            {{
                "is_genuine": true/false,
                "confidence_score": 0.0-1.0,
                "rejection_reason": "reason if not genuine",
                "verification_checks": {{
                    "authenticity": {{
                        "passed": true/false,
                        "details": "explanation"
                    }},
                    "security_features": {{
                        "passed": true/false,
                        "details": "explanation"
                    }},
                    "red_flags": {{
                        "passed": true/false,
                        "details": "explanation"
                    }},
                    "quality": {{
                        "passed": true/false,
                        "details": "explanation"
                    }}
                }},
                "security_features_found": ["list of security features"],
                "verification_summary": "Overall verification summary"
            }}

            Important:
            - Be thorough in your analysis
            - Consider all aspects of document authenticity
            - Provide detailed explanations for your decisions
            - Look for any signs of forgery or tampering
            - Consider document-specific security features
            - Check for any inconsistencies or anomalies
            - Pay attention to document quality and formatting
            """

            # Process with Gemini
            response = self.text_processor.process_text(text, verification_prompt)
            verification_result = json.loads(response.strip().replace("```json", "").replace("```", "").strip())

            # Log verification results
            logger.info(f"Document genuineness verification results: {json.dumps(verification_result, indent=2)}")

            return verification_result

        except Exception as e:
            logger.exception(f"Error verifying document genuineness: {str(e)}")
            return {
                "is_genuine": False,
                "confidence_score": 0.0,
                "rejection_reason": f"Error during verification: {str(e)}",
                "verification_checks": {
                    "authenticity": {"passed": False, "details": f"Error during verification: {str(e)}"},
                    "security_features": {"passed": False, "details": "Verification failed"},
                    "red_flags": {"passed": False, "details": "Verification failed"},
                    "quality": {"passed": False, "details": "Verification failed"}
                },
                "security_features_found": [],
                "verification_summary": f"Document verification failed due to error: {str(e)}"
            }


def main():
    input_path = "D:\\imageextractor\\identites\\NewMexicoCorp.docx"
    api_key = API_KEY

    processor = DocumentProcessor(api_key=api_key)

    results = processor.process_file(file_path=input_path)

    if results:
        # Group results by document type
        grouped_results = {}
        for result in results:
            doc_type = result["document_type"]
            if doc_type not in grouped_results:
                grouped_results[doc_type] = []
            grouped_results[doc_type].append(result)

        # Save results to JSON
        with open("results.json", "w", encoding="utf-8") as f:
            json.dump({
                "total_documents": len(results),
                "document_types": list(grouped_results.keys()),
                "results": grouped_results
            }, f, indent=2, ensure_ascii=False)
        print(f"✅ Processed {len(results)} documents and saved to results.json")
    else:
        print("⚠️ No valid documents detected")


if __name__ == "__main__":
    main()