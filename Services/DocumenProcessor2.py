import fitz
import tempfile
from typing import List, Dict, Any, Optional, Tuple
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
import concurrent.futures
from tqdm import tqdm
import multiprocessing
from pathlib import Path
import time
from queue import Queue
import threading
from typing import Generator
import hashlib
from concurrent.futures import ThreadPoolExecutor
import gc
from concurrent.futures import as_completed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BATCH_SIZE = 100
MAX_WORKERS = multiprocessing.cpu_count()
CHUNK_SIZE = 1000
MAX_RETRIES = 3

@dataclass
class DocumentInfo:
    document_type: str
    confidence_score: float
    extracted_data: Dict[str, Any]
    matched_fields: Dict[str, Any]

class BaseTextExtractor:
    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def extract_text(self, file_path: str) -> str:
        """Extract text from a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error extracting text from file: {str(e)}")
            raise

    def extract_text_from_bytes(self, content: bytes) -> str:
        """Extract text from bytes content"""
        try:
            return content.decode('utf-8')
        except Exception as e:
            logger.error(f"Error extracting text from bytes: {str(e)}")
            raise

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

class DynamicDocumentTypeSystem:
    def __init__(self):
        self.document_types = {}
        self.type_patterns = {}
        self.field_patterns = {}
        self.initialize_default_patterns()

    def initialize_default_patterns(self):
        """Initialize default field patterns for common document elements"""
        self.field_patterns = {
            'passport': [
                r'(?i)(?:passport|travel\s*document)\s*(?:number|no|#)?[:#]?\s*([A-Z0-9\-]+)',
                r'(?i)(?:type|category)[:#]?\s*([A-Z0-9\-]+)',
                r'(?i)(?:country\s*code|issuing\s*country)[:#]?\s*([A-Z]{2,3})',
                r'(?i)(?:surname|last\s*name|family\s*name)[:#]?\s*([A-Za-z\s\.]+)',
                r'(?i)(?:given\s*names|first\s*name)[:#]?\s*([A-Za-z\s\.]+)',
                r'(?i)(?:nationality|citizenship)[:#]?\s*([A-Za-z\s]+)',
                r'(?i)(?:date\s*of\s*birth|dob)[:#]?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
                r'(?i)(?:place\s*of\s*birth|pob)[:#]?\s*([A-Za-z\s,]+)',
                r'(?i)(?:date\s*of\s*issue|doi)[:#]?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
                r'(?i)(?:date\s*of\s*expiry|doe)[:#]?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
                r'(?i)(?:authority|issuing\s*authority)[:#]?\s*([A-Za-z\s,\.]+)',
                r'(?i)(?:sex|gender)[:#]?\s*([MF])',
                r'(?i)(?:personal\s*number|id\s*number)[:#]?\s*([A-Z0-9\-]+)'
            ],
            'identification': [
                r'(?i)(?:id|identification|reference)\s*(?:number|no|#)?[:#]?\s*([A-Z0-9\-]+)',
                r'(?i)(?:document|doc)\s*(?:number|no|#)?[:#]?\s*([A-Z0-9\-]+)'
            ],
            'date': [
                r'(?i)(?:date|issued|valid|expiry|expiration)\s*(?:date)?[:#]?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
                r'(?i)(?:dob|birth|born)\s*(?:date)?[:#]?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})'
            ],
            'name': [
                r'(?i)(?:name|full\s*name|applicant|holder|person)[:#]?\s*([A-Za-z\s\.]+)',
                r'(?i)(?:surname|last\s*name|family\s*name)[:#]?\s*([A-Za-z\s\.]+)'
            ],
            'address': [
                r'(?i)(?:address|location|residence)[:#]?\s*([A-Za-z0-9\s,\.\-]+)',
                r'(?i)(?:street|road|avenue)[:#]?\s*([A-Za-z0-9\s,\.\-]+)'
            ],
            'contact': [
                r'(?i)(?:phone|mobile|tel|contact)[:#]?\s*([0-9\+\-\(\)\s]+)',
                r'(?i)(?:email|e-mail)[:#]?\s*([A-Za-z0-9\._%\+\-]+@[A-Za-z0-9\.\-]+\.[A-Za-z]{2,})'
            ],
            'amount': [
                r'(?i)(?:amount|total|sum|value)[:#]?\s*([0-9,\.]+)',
                r'(?i)(?:price|cost|fee)[:#]?\s*([0-9,\.]+)'
            ],
            'status': [
                r'(?i)(?:status|state|condition)[:#]?\s*([A-Za-z\s]+)',
                r'(?i)(?:valid|active|current)[:#]?\s*([A-Za-z\s]+)'
            ]
        }

    def add_document_type(self, doc_type: str, patterns: List[str], fields: List[str]) -> None:
        """Add a new document type with its patterns and expected fields"""
        self.document_types[doc_type] = {
            'patterns': patterns,
            'fields': fields,
            'created_at': time.time()
        }
        self._update_type_patterns(doc_type, patterns)

    def add_field_pattern(self, field_type: str, patterns: List[str]) -> None:
        """Add new field patterns for document analysis"""
        if field_type not in self.field_patterns:
            self.field_patterns[field_type] = []
        self.field_patterns[field_type].extend(patterns)

    def _update_type_patterns(self, doc_type: str, patterns: List[str]) -> None:
        """Update patterns for document type matching"""
        self.type_patterns[doc_type] = patterns

    def get_document_type(self, text: str) -> Dict[str, Any]:
        """Dynamically identify document type from text"""
        matches = {}

        for doc_type, info in self.document_types.items():
            score = 0
            matched_patterns = []

            for pattern in info['patterns']:
                if re.search(pattern, text, re.IGNORECASE):
                    score += 1
                    matched_patterns.append(pattern)

            if score > 0:
                matches[doc_type] = {
                    'score': score / len(info['patterns']),
                    'matched_patterns': matched_patterns,
                    'expected_fields': info['fields']
                }

        if not matches:
            return self._identify_document_type_from_content(text)

        best_match = max(matches.items(), key=lambda x: x[1]['score'])
        return {
            'document_type': best_match[0],
            'confidence': best_match[1]['score'],
            'matched_patterns': best_match[1]['matched_patterns'],
            'expected_fields': best_match[1]['expected_fields']
        }

    def _identify_document_type_from_content(self, text: str) -> Dict[str, Any]:
        """Identify document type from content analysis"""

        key_phrases = self._extract_key_phrases(text)

        passport_indicators = [
            'passport', 'travel document', 'national passport', 'diplomatic passport',
            'official passport', 'service passport', 'type', 'category', 'issuing country',
            'nationality', 'date of birth', 'place of birth', 'date of issue',
            'date of expiry', 'authority', 'personal number'
        ]

        passport_score = sum(1 for indicator in passport_indicators if indicator.lower() in text.lower())

        if passport_score >= 3:
            return {
                'document_type': 'passport',
                'confidence': min(0.5 + (passport_score * 0.1), 1.0),
                'category': 'travel_document',
                'key_phrases': key_phrases,
                'structure': self._analyze_document_structure(text)
            }

        structure = self._analyze_document_structure(text)
        category = self._identify_document_category(key_phrases, structure)
        doc_type = self._generate_document_type(category, key_phrases)

        return {
            'document_type': doc_type,
            'confidence': 0.5,
            'category': category,
            'key_phrases': key_phrases,
            'structure': structure
        }

    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases from document text"""

        sentences = re.split(r'[.!?]+', text)

        key_phrases = []
        for sentence in sentences:

            if re.search(r'(?i)(?:document|certificate|letter|form|report|statement)', sentence):
                key_phrases.append(sentence.strip())

            if re.search(r'(?i)(?:official|authorized|certified|verified|approved)', sentence):
                key_phrases.append(sentence.strip())

            if re.search(r'(?i)(?:number|no|#|id|reference)', sentence):
                key_phrases.append(sentence.strip())

        return key_phrases

    def _analyze_document_structure(self, text: str) -> Dict[str, Any]:
        """Analyze document structure and layout"""
        structure = {
            'has_header': bool(re.search(r'(?i)^.*?(?:header|title|heading)', text)),
            'has_footer': bool(re.search(r'(?i)(?:footer|bottom|end).*?$', text)),
            'has_signature': bool(re.search(r'(?i)(?:signature|signed|authorized)', text)),
            'has_stamp': bool(re.search(r'(?i)(?:stamp|seal|official)', text)),
            'has_table': bool(re.search(r'(?i)(?:table|grid|matrix)', text)),
            'has_list': bool(re.search(r'(?i)(?:list|enumeration|bullets)', text)),
            'sections': self._identify_sections(text)
        }
        return structure

    def _identify_sections(self, text: str) -> List[Dict[str, Any]]:
        """Identify document sections"""
        sections = []
        current_section = {'title': '', 'content': []}

        lines = text.split('\n')

        for line in lines:

            if re.match(r'^[A-Z][A-Za-z\s]+[:]?$', line.strip()):
                if current_section['title']:
                    sections.append(current_section)
                current_section = {'title': line.strip(), 'content': []}
            else:
                current_section['content'].append(line.strip())

        if current_section['title']:
            sections.append(current_section)

        return sections

    def _identify_document_category(self, key_phrases: List[str], structure: Dict[str, Any]) -> str:
        """Identify document category from content and structure"""

        category_indicators = {
            'legal': [
                'agreement', 'contract', 'terms', 'conditions', 'clause', 'law', 'legal', 'jurisdiction',
                'witness', 'signature', 'notary', 'attorney', 'lawyer', 'court', 'judge', 'case',
                'defendant', 'plaintiff', 'settlement', 'verdict', 'ruling', 'statute', 'regulation',
                'compliance', 'liability', 'indemnity', 'warranty', 'disclaimer'
            ],
            'financial': [
                'payment', 'amount', 'balance', 'transaction', 'account', 'invoice', 'receipt', 'bill',
                'statement', 'tax', 'revenue', 'expense', 'income', 'profit', 'loss', 'budget',
                'investment', 'interest', 'loan', 'credit', 'debit', 'currency', 'exchange', 'rate',
                'dividend', 'share', 'stock', 'bond', 'security', 'portfolio', 'asset', 'liability'
            ],
            'identity': [
                'id', 'identification', 'name', 'address', 'dob', 'passport', 'nationality', 'citizenship',
                'residence', 'visa', 'permit', 'license', 'registration', 'certificate', 'document',
                'photo', 'signature', 'biometric', 'fingerprint', 'iris', 'facial', 'recognition',
                'security', 'authentication', 'verification', 'validation'
            ],
            'medical': [
                'patient', 'diagnosis', 'treatment', 'prescription', 'health', 'medical', 'doctor',
                'physician', 'nurse', 'hospital', 'clinic', 'medicine', 'drug', 'vaccine', 'immunization',
                'symptom', 'disease', 'condition', 'allergy', 'blood', 'test', 'result', 'lab',
                'radiology', 'x-ray', 'scan', 'therapy', 'rehabilitation', 'prognosis'
            ],
            'educational': [
                'student', 'course', 'grade', 'degree', 'certificate', 'diploma', 'transcript',
                'academic', 'education', 'school', 'college', 'university', 'faculty', 'professor',
                'lecturer', 'teacher', 'instructor', 'curriculum', 'syllabus', 'assignment',
                'examination', 'test', 'quiz', 'homework', 'project', 'thesis', 'dissertation'
            ],
            'business': [
                'company', 'business', 'corporate', 'organization', 'enterprise', 'firm', 'partnership',
                'corporation', 'llc', 'inc', 'ltd', 'proprietorship', 'franchise', 'branch', 'subsidiary',
                'department', 'division', 'unit', 'team', 'staff', 'employee', 'employer', 'manager',
                'director', 'executive', 'officer', 'shareholder', 'stakeholder', 'investor'
            ],
            'government': [
                'official', 'government', 'authority', 'department', 'ministry', 'agency', 'bureau',
                'commission', 'council', 'committee', 'board', 'administration', 'public', 'civil',
                'municipal', 'state', 'federal', 'national', 'international', 'diplomatic', 'consular',
                'embassy', 'mission', 'delegation', 'representation'
            ],
            'technical': [
                'specification', 'technical', 'engineering', 'design', 'architecture', 'blueprint',
                'diagram', 'schematic', 'circuit', 'component', 'system', 'network', 'protocol',
                'interface', 'database', 'software', 'hardware', 'firmware', 'algorithm', 'code',
                'program', 'application', 'platform', 'framework', 'infrastructure'
            ],
            'research': [
                'research', 'study', 'analysis', 'investigation', 'experiment', 'trial', 'survey',
                'poll', 'census', 'data', 'statistics', 'finding', 'result', 'conclusion',
                'hypothesis', 'theory', 'methodology', 'procedure', 'protocol', 'observation',
                'measurement', 'evaluation', 'assessment', 'review', 'literature'
            ],
            'personal': [
                'personal', 'private', 'confidential', 'individual', 'person', 'family', 'household',
                'residence', 'domicile', 'marriage', 'divorce', 'birth', 'death', 'inheritance',
                'estate', 'will', 'testament', 'guardian', 'trust', 'beneficiary', 'heir'
            ],
            'travel': [
                'travel', 'trip', 'journey', 'voyage', 'tour', 'excursion', 'expedition', 'itinerary',
                'schedule', 'booking', 'reservation', 'ticket', 'pass', 'permit', 'visa', 'passport',
                'immigration', 'customs', 'border', 'checkpoint', 'destination', 'departure', 'arrival'
            ],
            'employment': [
                'employment', 'job', 'work', 'career', 'profession', 'occupation', 'position',
                'role', 'duty', 'responsibility', 'task', 'assignment', 'project', 'performance',
                'evaluation', 'appraisal', 'review', 'promotion', 'transfer', 'termination',
                'resignation', 'retirement', 'pension', 'benefit', 'compensation', 'salary', 'wage'
            ]
        }

        category_scores = {}
        for category, indicators in category_indicators.items():
            score = 0
            for indicator in indicators:
                if any(indicator.lower() in phrase.lower() for phrase in key_phrases):
                    score += 1
            category_scores[category] = score

        if category_scores:
            return max(category_scores.items(), key=lambda x: x[1])[0]
        return 'other'

    def _generate_document_type(self, category: str, key_phrases: List[str]) -> str:
        """Generate document type name from category and key phrases"""

        doc_type = 'unknown'
        for phrase in key_phrases:

            match = re.search(r'(?i)(?:document|certificate|letter|form|report|statement)\s+of\s+([A-Za-z\s]+)', phrase)
            if match:
                doc_type = match.group(1).strip().lower().replace(' ', '_')
                break

        if doc_type == 'unknown':
            doc_type = f"{category}_document"

        return doc_type

    def extract_fields(self, text: str, doc_type: str) -> Dict[str, Any]:
        """Extract fields from document text"""
        fields = {}

        field_patterns = self.document_types.get(doc_type, {}).get('fields', [])

        for field_type, patterns in self.field_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    field_name = field_type
                    field_value = match.group(1).strip()
                    fields[field_name] = field_value

        return fields

class TemplateMatcher:
    def __init__(self, api_key: str, templates_dir: str = "D:\\imageextractor\\identites\\Templates"):
        self.templates_dir = templates_dir
        self.api_key = api_key
        self.text_processor = TextProcessor(api_key)
        self.document_system = DynamicDocumentTypeSystem()

        self.SUPPORTED_EXTENSIONS = {

            '.pdf', '.docx', '.doc', '.txt', '.rtf', '.odt', '.pages',

            '.jpg', '.jpeg', '.png', '.tiff', '.bmp', '.gif', '.webp',

            '.xlsx', '.xls', '.csv', '.ods',

            '.ppt', '.pptx', '.key',

            '.xml', '.json', '.html', '.htm'
        }

        if not os.path.exists(self.templates_dir):
            logger.warning(f"Templates directory does not exist: {self.templates_dir}. System will use dynamic analysis only.")
            self.templates = {}
        else:

            self.templates = self._load_templates()
            if not self.templates:
                logger.warning(f"No templates found in directory: {self.templates_dir}. System will use dynamic analysis.")

    def _load_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load all templates from the templates directory"""
        templates = {}
        try:
            files = os.listdir(self.templates_dir)
            if not files:
                logger.warning(f"Templates directory is empty: {self.templates_dir}")
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

                        doc_type = self._determine_document_type(filename, file_path)

                        logger.info(f"Processing template: {filename} as {doc_type}")

                        text_extractor = TextExtractorFactory.create_extractor(file_path, self.api_key)
                        template_text = text_extractor.extract_text(file_path)

                        if template_text:
                            templates[doc_type] = {
                                'content': template_text,
                                'fields': self._extract_fields_from_text(template_text),
                                'structure': template_text,
                                'metadata': {
                                    'filename': filename,
                                    'file_path': file_path,
                                    'file_type': file_ext,
                                    'created_at': time.time()
                                }
                            }
                            logger.info(f"Successfully loaded template: {filename}")
                        else:
                            logger.warning(f"No text extracted from template: {filename}")
                    except Exception as e:
                        logger.warning(f"Error processing template file {filename}: {str(e)}")
                        continue

            return templates

        except Exception as e:
            logger.error(f"Error loading templates from directory {self.templates_dir}: {str(e)}")
            return {}

    def _determine_document_type(self, filename: str, file_path: str) -> str:
        """Dynamically determine document type from filename or content"""
        try:

            base_name = os.path.splitext(filename)[0].lower()

            base_name = re.sub(r'^(template|sample|example|doc|document)_?', '', base_name)
            base_name = re.sub(r'_?(template|sample|example|doc|document)$', '', base_name)

            doc_type = re.sub(r'[^a-z0-9]+', '_', base_name).strip('_')

            if not doc_type:

                text_extractor = TextExtractorFactory.create_extractor(file_path, self.api_key)
                content = text_extractor.extract_text(file_path)

                if content:

                    doc_info = self.document_system.get_document_type(content)
                    doc_type = doc_info.get('document_type', 'unknown_document')

            return doc_type or 'unknown_document'

        except Exception as e:
            logger.error(f"Error determining document type: {str(e)}")
            return 'unknown_document'

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

    def _create_template_matching_prompt(self, input_text: str, template_content: str, doc_type: str) -> str:
        """Create a prompt for Gemini to match document against template"""

        doc_info = self.document_system.get_document_type(input_text)

        passport_instructions = ""
        if doc_type.lower() == 'passport':
            passport_instructions = """
            For passport documents, pay special attention to:
            1. Passport number format and location
            2. Type/Category of passport
            3. Country code and issuing country
            4. Personal information (name, nationality, DOB, etc.)
            5. Dates (issue, expiry)
            6. Authority information
            7. Machine readable zone (MRZ) if present
            8. Security features and official elements
            """

        return f"""
            You are a document analysis expert specializing in document verification. Your task is to analyze if the given document matches the {doc_type} template structure.

            Document Information:
            Type: {doc_info['document_type']}
            Category: {doc_info.get('category', 'unknown')}
            Confidence: {doc_info.get('confidence', 0.0)}

            Document Text:
            {input_text}

            Template Structure:
            {template_content}

            {passport_instructions}

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
                }},
                "document_info": {{
                    "type": "{doc_info['document_type']}",
                    "category": "{doc_info.get('category', 'unknown')}",
                    "confidence": {doc_info.get('confidence', 0.0)}
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

            if not self.templates:
                return self._analyze_document_dynamically(input_text)

            best_match = {
                'document_type': None,
                'confidence': 0.0,
                'matched_fields': {},
                'additional_info': None,
                'template_id': None,
                'matching_details': {}
            }

            for template_id, template in self.templates.items():
                try:
                    prompt = self._create_template_matching_prompt(
                        input_text,
                        template['content'],
                        template_id
                    )
                    response = self.text_processor.process_text(input_text, prompt)
                    match_result = json.loads(response.strip().replace("```json", "").replace("```", "").strip())

                    confidence = match_result.get('confidence_score', 0)
                    logger.info(f"Template match result for {template_id}: {confidence}")

                    if confidence > best_match['confidence']:
                        best_match = {
                            'document_type': template_id,
                            'confidence': confidence,
                            'matched_fields': match_result.get('extracted_fields', {}),
                            'additional_info': match_result.get('additional_info'),
                            'template_id': template_id,
                            'matching_details': match_result.get('matching_details', {})
                        }
                except Exception as e:
                    logger.warning(f"Error matching template for {template_id}: {str(e)}")
                    continue

            if not best_match['document_type'] or best_match['confidence'] < 0.4:
                return self._analyze_document_dynamically(input_text)

            return best_match

        except Exception as e:
            logger.error(f"Error matching document: {str(e)}")
            return self._analyze_document_dynamically(input_text)

    def _analyze_document_dynamically(self, text: str) -> Dict[str, Any]:
        """Analyze document without template matching"""
        try:

            doc_info = self.document_system.get_document_type(text)

            fields = self.document_system.extract_fields(text, doc_info['document_type'])

            return {
                'document_type': doc_info['document_type'],
                'confidence': doc_info.get('confidence', 0.0),
                'matched_fields': fields,
                'additional_info': doc_info.get('additional_info'),
                'template_id': None,
                'matching_details': {
                    'analysis_method': 'dynamic',
                    'category': doc_info.get('category', 'unknown'),
                    'key_phrases': doc_info.get('key_phrases', []),
                    'structure': doc_info.get('structure', {})
                }
            }

        except Exception as e:
            logger.error(f"Error in dynamic analysis: {str(e)}")
            return {
                'document_type': 'unknown_document',
                'confidence': 0.0,
                'matched_fields': {},
                'additional_info': None,
                'template_id': None,
                'matching_details': {
                    'analysis_method': 'fallback',
                    'error': str(e)
                }
            }

class DocumentClassifier:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.template_matcher = TemplateMatcher(api_key)

    def identify_document_type(self, file_path: str) -> DocumentInfo:
        try:

            template_match = self.template_matcher.match_document(file_path)

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

class DocumentLearningSystem:
    def __init__(self):
        self.learned_patterns = {}
        self.document_features = {}
        self.content_patterns = {}
        self.structure_patterns = {}
        self.learning_history = []

    def initialize(self):
        """Initialize the learning system"""
        self.learned_patterns = {}
        self.document_features = {}
        self.content_patterns = {}
        self.structure_patterns = {}
        self.learning_history = []

    def learn(self, text: str, features: Dict[str, Any], patterns: Dict[str, Any], content: Dict[str, Any]) -> None:
        """Learn from document"""

        self._update_patterns(patterns)

        self._update_features(features)

        self._update_content_patterns(content)

        self._update_structure_patterns(features.get('structure', {}))

        self.learning_history.append({
            'timestamp': time.time(),
            'features': features,
            'patterns': patterns,
            'content': content
        })

    def _update_patterns(self, patterns: Dict[str, Any]) -> None:
        """Update learned patterns"""
        for pattern_type, pattern_data in patterns.items():
            if pattern_type not in self.learned_patterns:
                self.learned_patterns[pattern_type] = []
            self.learned_patterns[pattern_type].append(pattern_data)

    def _update_features(self, features: Dict[str, Any]) -> None:
        """Update document features"""
        for feature_type, feature_data in features.items():
            if feature_type not in self.document_features:
                self.document_features[feature_type] = []
            self.document_features[feature_type].append(feature_data)

    def _update_content_patterns(self, content: Dict[str, Any]) -> None:
        """Update content patterns"""
        for content_type, content_data in content.items():
            if content_type not in self.content_patterns:
                self.content_patterns[content_type] = []
            self.content_patterns[content_type].append(content_data)

    def _update_structure_patterns(self, structure: Dict[str, Any]) -> None:
        """Update structure patterns"""
        for structure_type, structure_data in structure.items():
            if structure_type not in self.structure_patterns:
                self.structure_patterns[structure_type] = []
            self.structure_patterns[structure_type].append(structure_data)

    def get_learning_data(self) -> Dict[str, Any]:
        """Get learning system data"""
        return {
            'learned_patterns': self.learned_patterns,
            'document_features': self.document_features,
            'content_patterns': self.content_patterns,
            'structure_patterns': self.structure_patterns,
            'learning_history': self.learning_history
        }

class DynamicDocumentProcessor:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.text_processor = TextProcessor(api_key)
        self.learning_system = DocumentLearningSystem()
        self.pattern_analyzer = PatternAnalyzer()
        self.feature_extractor = FeatureExtractor()
        self.structure_analyzer = StructureAnalyzer()
        self.content_analyzer = ContentAnalyzer()
        self.template_matcher = TemplateMatcher(api_key)
        self.document_system = DynamicDocumentTypeSystem()

        self.text_extractors = {
            '.pdf': PdfTextExtractor(api_key),
            '.docx': DocxTextExtractor(api_key),
            '.doc': DocxTextExtractor(api_key),
            '.txt': BaseTextExtractor(api_key),
            '.jpg': ImageTextExtractor(api_key),
            '.jpeg': ImageTextExtractor(api_key),
            '.png': ImageTextExtractor(api_key),
            '.tiff': ImageTextExtractor(api_key),
            '.bmp': ImageTextExtractor(api_key)
        }

        self.templates = {
            'pan': {
                'patterns': [
                    r'(?i)(?:PAN\s*CARD|PERMANENT\s*ACCOUNT\s*NUMBER)',
                    r'(?i)(?:PAN|PERMANENT\s*ACCOUNT\s*NUMBER)\s*(?:NO|NUMBER|#)?[:#]?\s*([A-Z0-9\-]+)'
                ],
                'fields': ['pan_number', 'name', 'father_name', 'dob', 'address']
            },
            'florida_license': {
                'patterns': [
                    r'(?i)(?:FLORIDA\s*DRIVER\s*LICENSE|FLORIDA\s*DL)',
                    r'(?i)(?:LICENSE|DL)\s*(?:NO|NUMBER|#)?[:#]?\s*([A-Z0-9\-]+)'
                ],
                'fields': ['license_number', 'name', 'address', 'dob', 'expiry']
            },
            'passport': {
                'patterns': [
                    r'(?i)(?:PASSPORT|TRAVEL\s*DOCUMENT)',
                    r'(?i)(?:PASSPORT|TRAVEL\s*DOCUMENT)\s*(?:NO|NUMBER|#)?[:#]?\s*([A-Z0-9\-]+)'
                ],
                'fields': ['passport_number', 'name', 'nationality', 'dob', 'expiry']
            }
        }

        self.initialize_system()
        self.analysis_cache = {}
        self.cache_lock = threading.Lock()

    def initialize_system(self):
        """Initialize the dynamic document processing system"""
        self.learning_system.initialize()
        self.pattern_analyzer.initialize()
        self.feature_extractor.initialize()
        self.structure_analyzer.initialize()
        self.content_analyzer.initialize()

    def process_document(self, file_path: str) -> List[Dict[str, Any]]:
        """Process any document and extract information"""
        try:

            text = self._extract_text_with_retry(file_path)
            if not text:
                raise ValueError("No text could be extracted from document")

            logger.info(f"Extracted text length: {len(text)}")
            logger.debug(f"Extracted text sample: {text[:200]}...")

            if self._is_merged_document(text):
                logger.info("Detected merged document, processing multiple documents...")
                return self.process_merged_document(file_path)
            else:
                logger.info("Processing single document...")
                return [self._process_single_document(text, file_path)]

        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            raise

    def _is_merged_document(self, text: str) -> bool:
        """Check if the document contains multiple documents"""

        doc_headers = re.findall(r'(?i)(?:DOCUMENT|CERTIFICATE|IDENTIFICATION|LICENSE|PASSPORT|ID|PAN|AADHAAR|DRIVER|DL|FORM|APPLICATION)\s*(?:TYPE|NUMBER|#)?\s*[:#]?\s*\d*\s*$', text, re.MULTILINE)

        separators = re.findall(r'^\s*[-=*_#]{3,}\s*$', text, re.MULTILINE)

        page_breaks = re.findall(r'^\s*Page\s+\d+\s+of\s+\d+\s*$', text, re.MULTILINE)

        doc_numbers = re.findall(r'^\s*(?:DOCUMENT|CERTIFICATE)\s+\d+\s*$', text, re.MULTILINE)

        return (len(doc_headers) > 1 or
                len(separators) > 1 or
                len(page_breaks) > 1 or
                len(doc_numbers) > 1)

    def process_merged_document(self, file_path: str) -> List[Dict[str, Any]]:
        """Process a merged document by splitting it into individual documents"""
        try:

            text = self._extract_text_with_retry(file_path)
            if not text:
                raise ValueError("No text could be extracted from merged document")

            documents = self._split_into_documents(text)
            logger.info(f"Found {len(documents)} potential documents in merged file")

            results = []
            for i, doc_text in enumerate(documents, 1):
                logger.info(f"Processing document {i} of {len(documents)}")
                result = self._process_single_document(doc_text, file_path)
                result['document_number'] = i
                result['total_documents'] = len(documents)
                results.append(result)

            return results

        except Exception as e:
            logger.error(f"Error processing merged document: {str(e)}")
            raise

    def _process_single_document(self, text: str, file_path: str) -> Dict[str, Any]:
        """Process a single document with retry logic for API rate limits"""
        max_retries = 3
        base_delay = 5

        for attempt in range(max_retries):
            try:

                cleaned_text = self._clean_extracted_text(text)
                logger.info(f"Extracted text from document: {len(cleaned_text)} characters")

                template_match = None
                for template_attempt in range(max_retries):
                    try:
                        template_match = self.template_matcher.match_document(None, cleaned_text)
                        break
                    except Exception as e:
                        if "429" in str(e) and template_attempt < max_retries - 1:
                            delay = base_delay * (2 ** template_attempt)
                            logger.warning(f"Rate limit hit during template matching, retrying in {delay} seconds...")
                            time.sleep(delay)
                            continue
                        else:
                            logger.error(f"Error matching template: {str(e)}")
                            break

                doc_type_info = self._identify_document_type(cleaned_text)
                doc_type = doc_type_info['type']

                fields = self._extract_fields_by_type(cleaned_text, doc_type)

                metadata = self._extract_metadata(file_path)
                fields['metadata'] = metadata

                fields['document_type'] = doc_type
                fields['confidence_score'] = doc_type_info['confidence']

                return fields

            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:

                    delay = base_delay * (2 ** attempt)
                    logger.warning(f"Rate limit hit, retrying in {delay} seconds...")
                    time.sleep(delay)
                    continue
                else:
                    logger.error(f"Error processing document: {str(e)}")
                    return {
                        'error': str(e),
                        'document_type': 'unknown',
                        'confidence_score': 0.0,
                        'fields': {}
                    }

        return {
            'error': 'Max retries exceeded',
            'document_type': 'unknown',
            'confidence_score': 0.0,
            'fields': {}
        }

    def _identify_document_type(self, text: str) -> Dict[str, Any]:
        """Identify document type from text content"""
        try:

            template_match = self.template_matcher.match_document(None, text)
            if template_match and template_match['confidence'] > 0.4:
                return {
                    'type': template_match['document_type'],
                    'confidence': template_match['confidence'],
                    'matched_fields': template_match['matched_fields']
                }

            doc_info = self.document_system.get_document_type(text)

            key_phrases = self._extract_key_phrases(text)

            if 'passport' in text.lower():
                return {
                    'type': 'passport',
                    'confidence': 0.8,
                    'matched_fields': self._extract_passport_fields(text)
                }
            elif 'license' in text.lower() or 'dl' in text.lower():
                return {
                    'type': 'driver_license',
                    'confidence': 0.8,
                    'matched_fields': self._extract_license_fields(text)
                }
            elif 'id' in text.lower() or 'identification' in text.lower():
                return {
                    'type': 'id_card',
                    'confidence': 0.8,
                    'matched_fields': self._extract_id_fields(text)
                }
            elif 'pan' in text.lower() or 'permanent account number' in text.lower():
                return {
                    'type': 'pan_card',
                    'confidence': 0.8,
                    'matched_fields': self._extract_id_fields(text)
                }

            return {
                'type': doc_info['document_type'],
                'confidence': doc_info.get('confidence', 0.5),
                'matched_fields': {}
            }

        except Exception as e:
            logger.error(f"Error identifying document type: {str(e)}")
            return {
                'type': 'unknown_document',
                'confidence': 0.0,
                'matched_fields': {}
            }

    def _extract_fields_by_type(self, text: str, doc_type: str) -> Dict[str, Any]:
        """Extract fields based on document type with retry logic"""
        max_retries = 3
        base_delay = 5

        for attempt in range(max_retries):
            try:
                fields = {}

                dates = self._extract_dates(text)
                if dates:
                    fields['dates'] = dates

                if doc_type in self.templates:
                    template_fields = self.templates[doc_type].get('fields', [])
                    if isinstance(template_fields, list):

                        fields.update({field: None for field in template_fields})
                    elif isinstance(template_fields, dict):
                        fields.update(template_fields)

                if doc_type:
                    if 'passport' in doc_type.lower():
                        fields.update(self._extract_passport_fields(text))
                    elif 'id' in doc_type.lower():
                        fields.update(self._extract_id_fields(text))
                    elif 'certificate' in doc_type.lower():
                        fields.update(self._extract_certificate_fields(text))
                    elif 'license' in doc_type.lower():
                        fields.update(self._extract_license_fields(text))
                    elif 'image' in doc_type.lower() or 'photo' in doc_type.lower():
                        fields.update(self._extract_image_fields(text))

                return fields

            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:

                    delay = base_delay * (2 ** attempt)
                    logger.warning(f"Rate limit hit during field extraction, retrying in {delay} seconds...")
                    time.sleep(delay)
                    continue
                else:
                    logger.error(f"Error extracting fields: {str(e)}")
                    return {}

        return {}

    def _extract_text_with_retry(self, file_path: str, max_retries: int = 3) -> str:
        """Extract text from document with retry mechanism"""
        for attempt in range(max_retries):
            try:
                text = self._extract_text(file_path)
                if text and len(text.strip()) >= 10:
                    return text
                time.sleep(1)
            except Exception as e:
                logger.warning(f"Text extraction attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    raise
        return ""

    def _extract_text(self, file_path: str) -> str:
        """Extract text from any document type"""
        try:

            file_ext = os.path.splitext(file_path)[1].lower()
            extractor = self.text_extractors.get(file_ext)

            if not extractor:
                raise ValueError(f"Unsupported file type: {file_ext}")

            extracted_text = extractor.extract_text(file_path)

            if not extracted_text or len(extracted_text.strip()) < 10:
                logger.warning(f"Extracted text too short or empty: {extracted_text}")
                raise ValueError("Text extraction failed - insufficient content")

            cleaned_text = self._clean_extracted_text(extracted_text)

            if not cleaned_text or len(cleaned_text.strip()) < 10:
                logger.warning("Cleaned text too short or empty")
                raise ValueError("Text cleaning failed - insufficient content")

            return cleaned_text

        except Exception as e:
            logger.error(f"Error extracting text: {str(e)}")
            raise

    def _clean_extracted_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        try:

            text = text.replace('|', 'I')
            text = text.replace('l', 'I')
            text = text.replace('0', 'O')

            text = re.sub(r'\s+([.,;:!?])', r'\1', text)
            text = re.sub(r'([.,;:!?])\s+', r'\1 ', text)

            text = re.sub(r'\n\s*\n', '\n\n', text)

            text = re.sub(r'\b([A-Z])\s+([A-Z])\b', r'\1\2', text)

            text = re.sub(r'(\d{1,2})[oO](\d{1,2})', r'\1/0\2', text)

            text = re.sub(r'([A-Z])\s+(\d)', r'\1\2', text)
            text = re.sub(r'(\d)\s+([A-Z])', r'\1\2', text)

            text = re.sub(r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})', r'\1 \2 \3', text)

            text = re.sub(r'([A-Z])\s+([a-z])', r'\1\2', text)

            text = re.sub(r'([A-Z])\s*0\s*(\d)', r'\1O\2', text)

            text = re.sub(r'([A-Z])\s*0\s*([A-Z])', r'\1O\2', text)

            text = re.sub(r'([A-Z])\s*(\d{2})\s*(\d{2})\s*(\d{2})\s*(\d{2})', r'\1\2\3\4\5', text)

            text = re.sub(r'(\d{2})\s*(\d{2})\s*(\d{4})', r'\1/\2/\3', text)

            text = re.sub(r'\s+', ' ', text)

            text = re.sub(r'\n\s*', '\n', text)

            text = re.sub(r'[^\w\s.,;:!?@#$%^&*()\-_=+\[\]{}|\\<>/"\'`~]', '', text)

            return text.strip()

        except Exception as e:
            logger.error(f"Error cleaning text: {str(e)}")
            return text

    def _extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from file"""
        try:
            stat = os.stat(file_path)
            return {
                'filename': os.path.basename(file_path),
                'file_size': stat.st_size,
                'created_time': stat.st_ctime,
                'modified_time': stat.st_mtime,
                'file_extension': os.path.splitext(file_path)[1].lower()
            }
        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}")
            return {}

    def _compute_document_hash(self, file_path: str) -> str:
        try:
            stat = os.stat(file_path)
            hash_input = f"{file_path}:{stat.st_size}:{stat.st_mtime}"
            return hashlib.sha256(hash_input.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Error computing document hash: {str(e)}")
            return hashlib.sha256(file_path.encode()).hexdigest()

    def _split_into_documents(self, text: str) -> List[str]:
        """Split merged text into individual documents with enhanced boundary detection"""
        documents = []

        image_indicators = [

            r'(?i)(?:IMAGE|PHOTO|PICTURE|SCAN)\s*(?:OF|DOCUMENT)?\s*[:#]?',
            r'(?i)(?:FRONT|BACK|SIDE)\s*(?:VIEW|IMAGE|PHOTO)?\s*[:#]?',
            r'(?i)(?:DOCUMENT\s*IMAGE|DOCUMENT\s*PHOTO|DOCUMENT\s*SCAN)',

            r'(?i)(?:TOP|BOTTOM|LEFT|RIGHT)\s*(?:IMAGE|PHOTO|PICTURE)?\s*[:#]?',
            r'(?i)(?:UPPER|LOWER)\s*(?:IMAGE|PHOTO|PICTURE)?\s*[:#]?',

            r'(?i)(?:PASSPORT|LICENSE|ID|PAN|AADHAAR)\s*(?:IMAGE|PHOTO|PICTURE)?\s*[:#]?',
            r'(?i)(?:DRIVER|IDENTITY|CERTIFICATE)\s*(?:IMAGE|PHOTO|PICTURE)?\s*[:#]?',

            r'(?i)(?:IMAGE|PHOTO|PICTURE)\s*(?:1|2|3|4|5|ONE|TWO|THREE|FOUR|FIVE)\s*[:#]?',
            r'(?i)(?:FIRST|SECOND|THIRD|FOURTH|FIFTH)\s*(?:IMAGE|PHOTO|PICTURE)?\s*[:#]?'
        ]

        for indicator in image_indicators:
            parts = re.split(indicator, text, flags=re.IGNORECASE)
            if len(parts) > 1:

                for i, part in enumerate(parts):
                    if len(part.strip()) > 5:

                        if i > 0:

                            for match in re.finditer(indicator, text, re.IGNORECASE):

                                start = max(0, match.start() - 300)
                                end = min(len(text), match.end() + 300)
                                context = text[start:end]

                                doc_text = context + part.strip()
                                if self._is_valid_document(doc_text):
                                    documents.append(doc_text)

        if not documents:
            doc_indicators = [

                r'(?i)(?:PAN\s*CARD|PERMANENT\s*ACCOUNT\s*NUMBER)',
                r'(?i)(?:FLORIDA\s*DRIVER\s*LICENSE|FLORIDA\s*DL)',
                r'(?i)(?:DRIVER\s*LICENSE|DRIVER\'?S?\s*LICENSE|DL)',
                r'(?i)(?:IDENTITY\s*CARD|ID\s*CARD)',
                r'(?i)(?:PASSPORT|TRAVEL\s*DOCUMENT)',

                r'(?i)(?:DOCUMENT|CERTIFICATE|IDENTIFICATION|LICENSE|PASSPORT|ID|PAN|AADHAAR|DRIVER|DL|FORM|APPLICATION)\s*(?:TYPE|NUMBER|#)?\s*[:#]?\s*\d*\s*$',

                r'(?i)(?:PAGE|SHEET)\s+\d+\s+OF\s+\d+',
                r'(?i)(?:DOCUMENT|CERTIFICATE)\s+\d+',
                r'(?i)(?:COPY|DUPLICATE)\s+\d+',
                r'(?i)(?:ORIGINAL|COPY|DUPLICATE)',
                r'(?i)(?:ISSUED|VALID|EXPIRY)\s+DATE',
                r'(?i)(?:ISSUING\s+AUTHORITY|ISSUED\s+BY)',
                r'(?i)(?:OFFICIAL\s+USE|FOR\s+OFFICIAL\s+USE)',
                r'(?i)(?:SIGNATURE|AUTHORIZED\s+SIGNATURE)',
                r'(?i)(?:STAMP|SEAL|OFFICIAL\s+STAMP)'
            ]

            for indicator in doc_indicators:
                parts = re.split(indicator, text, flags=re.IGNORECASE)
                if len(parts) > 1:
                    for i, part in enumerate(parts):
                        if len(part.strip()) > 5:
                            if i > 0:
                                for match in re.finditer(indicator, text, re.IGNORECASE):
                                    start = max(0, match.start() - 200)
                                    end = min(len(text), match.end() + 200)
                                    context = text[start:end]
                                    doc_text = context + part.strip()
                                    if self._is_valid_document(doc_text):
                                        documents.append(doc_text)

        if not documents:
            header_patterns = [

                r'^[A-Z][A-Za-z\s]+(?:IMAGE|PHOTO|PICTURE|SCAN)[A-Za-z\s]*[:]?$',
                r'^[A-Z][A-Za-z\s]+(?:FRONT|BACK|SIDE)[A-Za-z\s]*[:]?$',

                r'^[A-Z][A-Za-z\s]+(?:DOCUMENT|CERTIFICATE|IDENTIFICATION|LICENSE|PASSPORT|ID|PAN|AADHAAR|DRIVER|DL|FORM|APPLICATION)[A-Za-z\s]*[:]?$',
                r'^[A-Z][A-Za-z\s]+(?:TYPE|CATEGORY|CLASS)[A-Za-z\s]*[:]?$',
                r'^[A-Z][A-Za-z\s]+(?:NUMBER|NO|#)[A-Za-z\s]*[:]?$',

                r'^[A-Z][A-Za-z\s]+(?:PAGE|SHEET)[A-Za-z\s]*[:]?$',
                r'^[A-Z][A-Za-z\s]+(?:COPY|DUPLICATE)[A-Za-z\s]*[:]?$',
                r'^[A-Z][A-Za-z\s]+(?:ORIGINAL|COPY|DUPLICATE)[A-Za-z\s]*[:]?$',
                r'^[A-Z][A-Za-z\s]+(?:ISSUED|VALID|EXPIRY)[A-Za-z\s]*[:]?$',
                r'^[A-Z][A-Za-z\s]+(?:ISSUING|AUTHORITY)[A-Za-z\s]*[:]?$',
                r'^[A-Z][A-Za-z\s]+(?:OFFICIAL|USE)[A-Za-z\s]*[:]?$',
                r'^[A-Z][A-Za-z\s]+(?:SIGNATURE|AUTHORIZED)[A-Za-z\s]*[:]?$',
                r'^[A-Z][A-Za-z\s]+(?:STAMP|SEAL)[A-Za-z\s]*[:]?$'
            ]

            for pattern in header_patterns:
                parts = re.split(pattern, text, flags=re.MULTILINE)
                if len(parts) > 1:
                    for i, part in enumerate(parts):
                        if len(part.strip()) > 5:
                            if i > 0:
                                for match in re.finditer(pattern, text, re.MULTILINE):
                                    start = max(0, match.start() - 200)
                                    end = min(len(text), match.end() + 200)
                                    context = text[start:end]
                                    doc_text = context + part.strip()
                                    if self._is_valid_document(doc_text):
                                        documents.append(doc_text)

        if not documents:
            parts = re.split(r'\n\s*\n\s*\n+', text)
            for part in parts:
                if len(part.strip()) > 5 and self._is_valid_document(part.strip()):
                    documents.append(part.strip())

        if not documents:
            parts = re.split(r'(?i)(?:page\s+\d+\s+of\s+\d+|page\s+\d+)', text)
            for part in parts:
                if len(part.strip()) > 5 and self._is_valid_document(part.strip()):
                    documents.append(part.strip())

        if not documents:
            parts = re.split(r'^\s*[-=*_#]{3,}\s*$', text, flags=re.MULTILINE)
            for part in parts:
                if len(part.strip()) > 5 and self._is_valid_document(part.strip()):
                    documents.append(part.strip())

        if not documents:
            parts = re.split(r'^\s*(?:DOCUMENT|CERTIFICATE)\s+\d+\s*$', text, flags=re.MULTILINE)
            for part in parts:
                if len(part.strip()) > 5 and self._is_valid_document(part.strip()):
                    documents.append(part.strip())

        if not documents:
            parts = re.split(r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}', text)
            for part in parts:
                if len(part.strip()) > 5 and self._is_valid_document(part.strip()):
                    documents.append(part.strip())

        if not documents:
            doc_type_keywords = [
                'PASSPORT', 'LICENSE', 'ID CARD', 'PAN CARD', 'AADHAAR',
                'DRIVER LICENSE', 'IDENTITY CARD', 'CERTIFICATE', 'DOCUMENT'
            ]
            for keyword in doc_type_keywords:
                parts = re.split(f'(?i){keyword}', text)
                if len(parts) > 1:
                    for i, part in enumerate(parts):
                        if len(part.strip()) > 5:
                            if i > 0:
                                doc_text = keyword + part.strip()
                                if self._is_valid_document(doc_text):
                                    documents.append(doc_text)

        unique_docs = []
        seen = set()
        for doc in documents:
            if doc not in seen:
                seen.add(doc)
                unique_docs.append(doc)

        unique_docs.sort(key=lambda x: text.find(x))

        logger.info(f"Found {len(unique_docs)} potential documents in merged file")

        return unique_docs

    def _is_valid_document(self, text: str) -> bool:
        """Check if text contains enough content to be a valid document"""

        if len(text.strip()) < 3:
            return False

        doc_type_info = self._identify_document_type(text)
        if doc_type_info['confidence'] > 0.1:
            return True

        has_dates = bool(re.search(r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}', text))
        has_numbers = bool(re.search(r'[A-Z0-9\-]{2,}', text))
        has_headers = bool(re.search(r'^[A-Z][A-Za-z\s]+[:]?$', text, re.MULTILINE))
        has_doc_indicators = bool(re.search(r'(?i)(?:document|certificate|identification|license|passport|id|pan|aadhaar|driver|dl|form|application)', text))

        has_image_indicators = bool(re.search(r'(?i)(?:image|photo|picture|scan|front|back|side|view|document\s*image|document\s*photo|document\s*scan)', text))

        has_pan = bool(re.search(r'(?i)(?:pan\s*card|permanent\s*account\s*number)', text))
        has_license = bool(re.search(r'(?i)(?:driver\s*license|driver\'?s?\s*license|dl)', text))
        has_id = bool(re.search(r'(?i)(?:identity\s*card|id\s*card)', text))

        return (has_dates or has_numbers or has_headers or has_doc_indicators or
                has_pan or has_license or has_id or has_image_indicators)

    def _extract_fields_by_type(self, text: str, doc_type: str) -> Dict[str, Any]:
        """Extract fields based on document type"""
        try:
            fields = {}

            dates = self._extract_dates(text)
            if dates:
                fields['dates'] = dates

            if doc_type in self.templates:
                template_fields = self.templates[doc_type].get('fields', [])
                if isinstance(template_fields, list):

                    fields.update({field: None for field in template_fields})
                elif isinstance(template_fields, dict):
                    fields.update(template_fields)

            if doc_type:
                if 'passport' in doc_type.lower():
                    fields.update(self._extract_passport_fields(text))
                elif 'id' in doc_type.lower():
                    fields.update(self._extract_id_fields(text))
                elif 'certificate' in doc_type.lower():
                    fields.update(self._extract_certificate_fields(text))
                elif 'license' in doc_type.lower():
                    fields.update(self._extract_license_fields(text))
                elif 'image' in doc_type.lower() or 'photo' in doc_type.lower():
                    fields.update(self._extract_image_fields(text))

            return fields

        except Exception as e:
            logger.error(f"Error extracting fields: {str(e)}")
            return {}

    def _extract_image_fields(self, text: str) -> Dict[str, Any]:
        """Extract fields from image documents"""
        fields = {}
        try:

            image_type_match = re.search(r'(?i)(?:image|photo|picture|scan)\s*(?:of|type)?\s*[:#]?\s*([A-Za-z\s]+)', text)
            if image_type_match:
                fields['image_type'] = image_type_match.group(1).strip()

            doc_type_match = re.search(r'(?i)(?:document|type)\s*(?:of|type)?\s*[:#]?\s*([A-Za-z\s]+)', text)
            if doc_type_match:
                fields['document_type'] = doc_type_match.group(1).strip()

            side_match = re.search(r'(?i)(?:front|back|side)\s*(?:view|image|photo)?\s*[:#]?\s*([A-Za-z\s]+)?', text)
            if side_match:
                fields['side'] = side_match.group(1).strip() if side_match.group(1) else side_match.group(0).strip()

            return fields

        except Exception as e:
            logger.error(f"Error extracting image fields: {str(e)}")
            return {}

    def _extract_metadata(self, text: str) -> Dict[str, Any]:
        """Extract metadata from text"""
        metadata = {
            'text_length': len(text),
            'word_count': len(text.split()),
            'line_count': len(text.split('\n')),
            'date_count': len(re.findall(r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}', text)),
            'number_count': len(re.findall(r'[A-Z0-9\-]{5,}', text)),
            'email_count': len(re.findall(r'[A-Za-z0-9\._%\+\-]+@[A-Za-z0-9\.\-]+\.[A-Za-z]{2,}', text)),
            'phone_count': len(re.findall(r'[0-9\+\-\(\)\s]{10,}', text))
        }
        return metadata

    def _identify_document_type(self, text: str) -> Dict[str, Any]:
        """Identify document type from text content"""
        try:

            template_match = self.template_matcher.match_document(None, text)
            if template_match and template_match['confidence'] > 0.4:
                return {
                    'type': template_match['document_type'],
                    'confidence': template_match['confidence'],
                    'matched_fields': template_match['matched_fields']
                }

            doc_info = self.document_system.get_document_type(text)

            key_phrases = self._extract_key_phrases(text)

            if 'passport' in text.lower():
                return {
                    'type': 'passport',
                    'confidence': 0.8,
                    'matched_fields': self._extract_passport_fields(text)
                }
            elif 'license' in text.lower() or 'dl' in text.lower():
                return {
                    'type': 'driver_license',
                    'confidence': 0.8,
                    'matched_fields': self._extract_license_fields(text)
                }
            elif 'id' in text.lower() or 'identification' in text.lower():
                return {
                    'type': 'id_card',
                    'confidence': 0.8,
                    'matched_fields': self._extract_id_fields(text)
                }
            elif 'pan' in text.lower() or 'permanent account number' in text.lower():
                return {
                    'type': 'pan_card',
                    'confidence': 0.8,
                    'matched_fields': self._extract_id_fields(text)
                }

            return {
                'type': doc_info['document_type'],
                'confidence': doc_info.get('confidence', 0.5),
                'matched_fields': {}
            }

        except Exception as e:
            logger.error(f"Error identifying document type: {str(e)}")
            return {
                'type': 'unknown_document',
                'confidence': 0.0,
                'matched_fields': {}
            }

    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases from text"""
        key_phrases = []

        doc_type_patterns = [
            r'(?i)(?:document|type)\s*(?:of|type)?\s*[:#]?\s*([A-Za-z\s]+)',
            r'(?i)(?:certificate|license|passport|id|pan)\s*(?:type|category)?\s*[:#]?\s*([A-Za-z\s]+)',
            r'(?i)(?:form|application)\s*(?:type|category)?\s*[:#]?\s*([A-Za-z\s]+)'
        ]

        for pattern in doc_type_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                if len(match.groups()) > 0:
                    key_phrases.append(match.group(1).strip())
                else:
                    key_phrases.append(match.group(0).strip())

        return key_phrases

    def _extract_dates(self, text: str) -> List[Dict[str, str]]:
        """Extract dates from text with various formats"""
        dates = []
        try:

            date_patterns = [

                r'(?:\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b)',

                r'(?:\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b)',

                r'(?:\b\d{1,2} (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}\b)',

                r'(?:\b\d{4}-\d{2}-\d{2}\b)',

                r'(?:\b\d{2}-\d{2}-\d{4}\b)'
            ]

            date_types = {
                'issue': r'(?i)(?:issue|issued|issuance|date of issue)',
                'expiry': r'(?i)(?:expiry|expiration|expires|valid until|valid till)',
                'birth': r'(?i)(?:birth|date of birth|dob|born)',
                'effective': r'(?i)(?:effective|valid from|valid since)'
            }

            for pattern in date_patterns:
                for match in re.finditer(pattern, text):
                    date_text = match.group(0)

                    start = max(0, match.start() - 50)
                    end = min(len(text), match.end() + 50)
                    context = text[start:end]

                    date_type = 'unknown'
                    for type_name, type_pattern in date_types.items():
                        if re.search(type_pattern, context):
                            date_type = type_name
                            break

                    dates.append({
                        'date': date_text,
                        'type': date_type,
                        'context': context.strip()
                    })

            return dates

        except Exception as e:
            logger.error(f"Error extracting dates: {str(e)}")
            return []

class PatternAnalyzer:
    def __init__(self):
        self.patterns = {}
        self.learned_patterns = {}
        self.pattern_cache = {}
        self.initialize()

    def initialize(self):
        """Initialize the pattern analyzer"""
        self.patterns = {
            'document_headers': [
                r'(?i)^\s*(?:DOCUMENT|CERTIFICATE|IDENTIFICATION|LICENSE|PASSPORT|ID|PAN|AADHAAR|DRIVER|DL|FORM|APPLICATION)\s*(?:TYPE|NUMBER|#)?\s*[:#]?\s*\d*\s*$',
                r'(?i)^\s*(?:DOCUMENT|CERTIFICATE|IDENTIFICATION|LICENSE|PASSPORT|ID|PAN|AADHAAR|DRIVER|DL|FORM|APPLICATION)\s*(?:NO|NUMBER|#)?\s*[:#]?\s*[A-Z0-9\-]+\s*$'
            ],
            'separators': [
                r'^\s*[-=]{3,}\s*$',
                r'^\s*_{3,}\s*$',
                r'^\s*[*]{3,}\s*$',
                r'^\s*[#]{3,}\s*$'
            ],
            'page_breaks': [
                r'^\s*Page\s+\d+\s+of\s+\d+\s*$',
                r'^\s*-\s*\d+\s*-\s*$',
                r'^\s*Page\s+\d+\s*$',
                r'^\s*P\s*\d+\s*$'
            ],
            'document_numbers': [
                r'^\s*DOCUMENT\s+\d+\s*$',
                r'^\s*CERTIFICATE\s+\d+\s*$',
                r'^\s*DOC\s*\d+\s*$',
                r'^\s*CERT\s*\d+\s*$'
            ],
            'dates': [
                r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}',
                r'\d{1,2}\s+[A-Za-z]+\s+\d{4}',
                r'[A-Za-z]+\s+\d{1,2}(?:st|nd|rd|th)?\s*,\s*\d{4}'
            ],
            'names': [
                r'(?i)(?:name|full\s*name|applicant|holder|person)[:#]?\s*([A-Za-z\s\.]+)',
                r'(?i)(?:surname|last\s*name|family\s*name)[:#]?\s*([A-Za-z\s\.]+)',
                r'(?i)(?:given\s*names|first\s*name)[:#]?\s*([A-Za-z\s\.]+)'
            ],
            'numbers': [
                r'(?i)(?:number|no|#|id|reference)[:#]?\s*([A-Z0-9\-]+)',
                r'(?i)(?:document|doc)\s*(?:number|no|#)?[:#]?\s*([A-Z0-9\-]+)'
            ],
            'addresses': [
                r'(?i)(?:address|location|residence)[:#]?\s*([A-Za-z0-9\s,\.\-]+)',
                r'(?i)(?:street|road|avenue)[:#]?\s*([A-Za-z0-9\s,\.\-]+)'
            ],
            'contact': [
                r'(?i)(?:phone|mobile|tel|contact)[:#]?\s*([0-9\+\-\(\)\s]+)',
                r'(?i)(?:email|e-mail)[:#]?\s*([A-Za-z0-9\._%\+\-]+@[A-Za-z0-9\.\-]+\.[A-Za-z]{2,})'
            ]
        }
        self.learned_patterns = {}
        self.pattern_cache = {}

    def analyze(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze text for patterns"""
        try:
            results = {
                'matches': {},
                'learned_patterns': {},
                'confidence_scores': {}
            }

            for category, patterns in self.patterns.items():
                matches = []
                for pattern in patterns:
                    found_matches = re.finditer(pattern, text, re.MULTILINE)
                    for match in found_matches:
                        matches.append({
                            'pattern': pattern,
                            'match': match.group(0),
                            'start': match.start(),
                            'end': match.end(),
                            'groups': match.groups()
                        })

                if matches:
                    results['matches'][category] = matches
                    results['confidence_scores'][category] = self._calculate_confidence(matches, text)

            self._learn_patterns(text, results['matches'])
            results['learned_patterns'] = self.learned_patterns

            return results

        except Exception as e:
            logger.error(f"Error analyzing patterns: {str(e)}")
            return {
                'matches': {},
                'learned_patterns': {},
                'confidence_scores': {},
                'error': str(e)
            }

    def _calculate_confidence(self, matches: List[Dict[str, Any]], text: str) -> float:
        """Calculate confidence score for pattern matches"""
        if not matches:
            return 0.0

        base_confidence = len(matches) / (len(text.split('\n')) + 1)

        quality_scores = []
        for match in matches:

            context_score = 1.0
            if match['groups']:
                context_score = 1.2

            length_score = min(len(match['match']) / 10, 1.0)

            position_score = 1.0
            if match['start'] == 0 or text[match['start']-1] == '\n':
                position_score = 1.2

            quality_scores.append(context_score * length_score * position_score)

        avg_quality = sum(quality_scores) / len(quality_scores)
        return min(base_confidence * avg_quality, 1.0)

    def _learn_patterns(self, text: str, matches: Dict[str, List[Dict[str, Any]]]) -> None:
        """Learn new patterns from text"""
        try:

            for category, category_matches in matches.items():
                if category not in self.learned_patterns:
                    self.learned_patterns[category] = []

                for match in category_matches:

                    start = max(0, match['start'] - 50)
                    end = min(len(text), match['end'] + 50)
                    context = text[start:end]

                    new_pattern = {
                        'pattern': match['pattern'],
                        'context': context,
                        'confidence': match.get('confidence', 0.0),
                        'timestamp': time.time()
                    }

                    if not any(p['pattern'] == new_pattern['pattern'] for p in self.learned_patterns[category]):
                        self.learned_patterns[category].append(new_pattern)

            for category, patterns in self.patterns.items():
                if category not in matches:

                    similar_patterns = self._find_similar_patterns(text, patterns)
                    if similar_patterns:
                        if category not in self.learned_patterns:
                            self.learned_patterns[category] = []
                        self.learned_patterns[category].extend(similar_patterns)

        except Exception as e:
            logger.error(f"Error learning patterns: {str(e)}")

    def _find_similar_patterns(self, text: str, patterns: List[str]) -> List[Dict[str, Any]]:
        """Find patterns similar to existing ones"""
        similar_patterns = []
        try:

            lines = text.split('\n')

            for line in lines:

                if re.search(r'[A-Z][A-Za-z\s]+[:]?$', line):
                    similar_patterns.append({
                        'pattern': f'^{re.escape(line.strip())}$',
                        'context': line,
                        'confidence': 0.5,
                        'timestamp': time.time()
                    })
                elif re.search(r'[-=*_#]{3,}', line):
                    similar_patterns.append({
                        'pattern': f'^{re.escape(line.strip())}$',
                        'context': line,
                        'confidence': 0.5,
                        'timestamp': time.time()
                    })
                elif re.search(r'\d+', line):
                    similar_patterns.append({
                        'pattern': f'^{re.escape(line.strip())}$',
                        'context': line,
                        'confidence': 0.5,
                        'timestamp': time.time()
                    })

        except Exception as e:
            logger.error(f"Error finding similar patterns: {str(e)}")

        return similar_patterns

    def get_patterns(self) -> Dict[str, List[str]]:
        """Get all patterns"""
        return self.patterns

    def get_learned_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get learned patterns"""
        return self.learned_patterns

    def clear_cache(self) -> None:
        """Clear pattern cache"""
        self.pattern_cache = {}

class FeatureExtractor:
    def __init__(self):
        self.features = {}
        self.learned_features = {}
        self.feature_cache = {}
        self.initialize()

    def initialize(self):
        """Initialize the feature extractor"""
        self.features = {
            'document_structure': {
                'has_header': False,
                'has_footer': False,
                'has_signature': False,
                'has_stamp': False,
                'has_table': False,
                'has_list': False,
                'sections': []
            },
            'content_features': {
                'date_count': 0,
                'number_count': 0,
                'name_count': 0,
                'address_count': 0,
                'contact_count': 0,
                'email_count': 0,
                'phone_count': 0
            },
            'format_features': {
                'line_count': 0,
                'word_count': 0,
                'char_count': 0,
                'avg_line_length': 0,
                'max_line_length': 0,
                'min_line_length': 0
            },
            'style_features': {
                'all_caps_count': 0,
                'mixed_case_count': 0,
                'special_chars_count': 0,
                'numeric_count': 0
            }
        }
        self.learned_features = {}
        self.feature_cache = {}

    def extract(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Extract features from text"""
        try:
            results = {
                'structure': self._extract_structure_features(text),
                'content': self._extract_content_features(text),
                'format': self._extract_format_features(text),
                'style': self._extract_style_features(text)
            }

            self._learn_features(text, results)

            return results

        except Exception as e:
            logger.error(f"Error extracting features: {str(e)}")
            return {
                'structure': {},
                'content': {},
                'format': {},
                'style': {},
                'error': str(e)
            }

    def _extract_structure_features(self, text: str) -> Dict[str, Any]:
        """Extract document structure features"""
        structure = self.features['document_structure'].copy()

        structure['has_header'] = bool(re.search(r'^[A-Z][A-Za-z\s]+[:]?$', text, re.MULTILINE))

        structure['has_footer'] = bool(re.search(r'(?i)(?:footer|bottom|end).*?$', text))

        structure['has_signature'] = bool(re.search(r'(?i)(?:signature|signed|authorized)', text))

        structure['has_stamp'] = bool(re.search(r'(?i)(?:stamp|seal|official)', text))

        structure['has_table'] = bool(re.search(r'(?i)(?:table|grid|matrix)', text))

        structure['has_list'] = bool(re.search(r'(?i)(?:list|enumeration|bullets)', text))

        structure['sections'] = self._identify_sections(text)

        return structure

    def _extract_content_features(self, text: str) -> Dict[str, Any]:
        """Extract content features"""
        content = self.features['content_features'].copy()

        content['date_count'] = len(re.findall(r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}', text))

        content['number_count'] = len(re.findall(r'[A-Z0-9\-]{5,}', text))

        content['name_count'] = len(re.findall(r'(?i)(?:name|full\s*name|applicant|holder|person)[:#]?\s*([A-Za-z\s\.]+)', text))

        content['address_count'] = len(re.findall(r'(?i)(?:address|location|residence)[:#]?\s*([A-Za-z0-9\s,\.\-]+)', text))

        content['contact_count'] = len(re.findall(r'(?i)(?:contact|phone|mobile|tel)[:#]?\s*([0-9\+\-\(\)\s]+)', text))

        content['email_count'] = len(re.findall(r'[A-Za-z0-9\._%\+\-]+@[A-Za-z0-9\.\-]+\.[A-Za-z]{2,}', text))

        content['phone_count'] = len(re.findall(r'[0-9\+\-\(\)\s]{10,}', text))

        return content

    def _extract_format_features(self, text: str) -> Dict[str, Any]:
        """Extract format features"""
        format_features = self.features['format_features'].copy()

        lines = text.split('\n')
        format_features['line_count'] = len(lines)

        words = text.split()
        format_features['word_count'] = len(words)

        format_features['char_count'] = len(text)

        line_lengths = [len(line) for line in lines if line.strip()]
        if line_lengths:
            format_features['avg_line_length'] = sum(line_lengths) / len(line_lengths)
            format_features['max_line_length'] = max(line_lengths)
            format_features['min_line_length'] = min(line_lengths)

        return format_features

    def _extract_style_features(self, text: str) -> Dict[str, Any]:
        """Extract style features"""
        style = self.features['style_features'].copy()

        style['all_caps_count'] = len(re.findall(r'^[A-Z\s]+$', text, re.MULTILINE))

        style['mixed_case_count'] = len(re.findall(r'^[A-Za-z\s]+$', text, re.MULTILINE))

        style['special_chars_count'] = len(re.findall(r'[^A-Za-z0-9\s]', text))

        style['numeric_count'] = len(re.findall(r'\d+', text))

        return style

    def _identify_sections(self, text: str) -> List[Dict[str, Any]]:
        """Identify document sections"""
        sections = []
        current_section = {'title': '', 'content': []}

        lines = text.split('\n')

        for line in lines:

            if re.match(r'^[A-Z][A-Za-z\s]+[:]?$', line.strip()):
                if current_section['title']:
                    sections.append(current_section)
                current_section = {'title': line.strip(), 'content': []}
            else:
                current_section['content'].append(line.strip())

        if current_section['title']:
            sections.append(current_section)

        return sections

    def _learn_features(self, text: str, features: Dict[str, Any]) -> None:
        """Learn from extracted features"""
        try:

            if features['structure']['has_header']:
                self._learn_structure_pattern('header', text)
            if features['structure']['has_footer']:
                self._learn_structure_pattern('footer', text)
            if features['structure']['has_signature']:
                self._learn_structure_pattern('signature', text)

            if features['content']['date_count'] > 0:
                self._learn_content_pattern('date', text)
            if features['content']['name_count'] > 0:
                self._learn_content_pattern('name', text)
            if features['content']['address_count'] > 0:
                self._learn_content_pattern('address', text)

            if features['format']['line_count'] > 0:
                self._learn_format_pattern('line', text)
            if features['format']['word_count'] > 0:
                self._learn_format_pattern('word', text)

            if features['style']['all_caps_count'] > 0:
                self._learn_style_pattern('all_caps', text)
            if features['style']['mixed_case_count'] > 0:
                self._learn_style_pattern('mixed_case', text)

        except Exception as e:
            logger.error(f"Error learning features: {str(e)}")

    def _learn_structure_pattern(self, pattern_type: str, text: str) -> None:
        """Learn structure pattern"""
        if pattern_type not in self.learned_features:
            self.learned_features[pattern_type] = []

        pattern = {
            'type': pattern_type,
            'context': text[:200],
            'timestamp': time.time()
        }

        if not any(p['type'] == pattern['type'] for p in self.learned_features[pattern_type]):
            self.learned_features[pattern_type].append(pattern)

    def _learn_content_pattern(self, pattern_type: str, text: str) -> None:
        """Learn content pattern"""
        if pattern_type not in self.learned_features:
            self.learned_features[pattern_type] = []

        pattern = {
            'type': pattern_type,
            'context': text[:200],
            'timestamp': time.time()
        }

        if not any(p['type'] == pattern['type'] for p in self.learned_features[pattern_type]):
            self.learned_features[pattern_type].append(pattern)

    def _learn_format_pattern(self, pattern_type: str, text: str) -> None:
        """Learn format pattern"""
        if pattern_type not in self.learned_features:
            self.learned_features[pattern_type] = []

        pattern = {
            'type': pattern_type,
            'context': text[:200],
            'timestamp': time.time()
        }

        if not any(p['type'] == pattern['type'] for p in self.learned_features[pattern_type]):
            self.learned_features[pattern_type].append(pattern)

    def _learn_style_pattern(self, pattern_type: str, text: str) -> None:
        """Learn style pattern"""
        if pattern_type not in self.learned_features:
            self.learned_features[pattern_type] = []

        pattern = {
            'type': pattern_type,
            'context': text[:200],
            'timestamp': time.time()
        }

        if not any(p['type'] == pattern['type'] for p in self.learned_features[pattern_type]):
            self.learned_features[pattern_type].append(pattern)

    def get_features(self) -> Dict[str, Any]:
        """Get all features"""
        return self.features

    def get_learned_features(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get learned features"""
        return self.learned_features

    def clear_cache(self) -> None:
        """Clear feature cache"""
        self.feature_cache = {}

class StructureAnalyzer:
    def __init__(self):
        self.structure_patterns = {}
        self.learned_patterns = {}
        self.structure_cache = {}
        self.initialize()

    def initialize(self):
        """Initialize the structure analyzer"""
        self.structure_patterns = {
            'headers': [
                r'^[A-Z][A-Za-z\s]+[:]?$',
                r'^(?:DOCUMENT|CERTIFICATE|IDENTIFICATION|LICENSE|PASSPORT|ID|PAN|AADHAAR|DRIVER|DL|FORM|APPLICATION)\s*(?:TYPE|NUMBER|#)?\s*[:#]?\s*\d*\s*$'
            ],
            'footers': [
                r'(?i)(?:footer|bottom|end).*?$',
                r'^\s*Page\s+\d+\s+of\s+\d+\s*$'
            ],
            'signatures': [
                r'(?i)(?:signature|signed|authorized)',
                r'(?i)(?:witness|notary|attorney)'
            ],
            'stamps': [
                r'(?i)(?:stamp|seal|official)',
                r'(?i)(?:certified|verified|approved)'
            ],
            'tables': [
                r'(?i)(?:table|grid|matrix)',
                r'^\s*[-+|]+\s*$'
            ],
            'lists': [
                r'(?i)(?:list|enumeration|bullets)',
                r'^\s*[-*•]\s+'
            ],
            'sections': [
                r'^[A-Z][A-Za-z\s]+[:]?$',
                r'^\d+\.\s+[A-Z][A-Za-z\s]+[:]?$'
            ]
        }
        self.learned_patterns = {}
        self.structure_cache = {}

    def analyze(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze document structure"""
        try:
            results = {
                'structure': self._analyze_structure(text),
                'sections': self._identify_sections(text),
                'layout': self._analyze_layout(text),
                'formatting': self._analyze_formatting(text)
            }

            self._learn_patterns(text, results)

            return results

        except Exception as e:
            logger.error(f"Error analyzing structure: {str(e)}")
            return {
                'structure': {},
                'sections': [],
                'layout': {},
                'formatting': {},
                'error': str(e)
            }

    def _analyze_structure(self, text: str) -> Dict[str, Any]:
        """Analyze document structure"""
        structure = {
            'has_header': False,
            'has_footer': False,
            'has_signature': False,
            'has_stamp': False,
            'has_table': False,
            'has_list': False,
            'section_count': 0,
            'paragraph_count': 0,
            'line_count': 0
        }

        for pattern in self.structure_patterns['headers']:
            if re.search(pattern, text, re.MULTILINE):
                structure['has_header'] = True
                break

        for pattern in self.structure_patterns['footers']:
            if re.search(pattern, text, re.MULTILINE):
                structure['has_footer'] = True
                break

        for pattern in self.structure_patterns['signatures']:
            if re.search(pattern, text, re.MULTILINE):
                structure['has_signature'] = True
                break

        for pattern in self.structure_patterns['stamps']:
            if re.search(pattern, text, re.MULTILINE):
                structure['has_stamp'] = True
                break

        for pattern in self.structure_patterns['tables']:
            if re.search(pattern, text, re.MULTILINE):
                structure['has_table'] = True
                break

        for pattern in self.structure_patterns['lists']:
            if re.search(pattern, text, re.MULTILINE):
                structure['has_list'] = True
                break

        structure['section_count'] = len(self._identify_sections(text))

        structure['paragraph_count'] = len(re.split(r'\n\s*\n', text))

        structure['line_count'] = len(text.split('\n'))

        return structure

    def _identify_sections(self, text: str) -> List[Dict[str, Any]]:
        """Identify document sections"""
        sections = []
        current_section = {'title': '', 'content': [], 'level': 0}

        lines = text.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            is_header = False
            level = 0

            if re.match(self.structure_patterns['sections'][0], line):
                is_header = True
                level = 1

            elif re.match(self.structure_patterns['sections'][1], line):
                is_header = True
                level = 2

            if is_header:

                if current_section['title']:
                    sections.append(current_section)

                current_section = {
                    'title': line,
                    'content': [],
                    'level': level
                }
            else:

                current_section['content'].append(line)

        if current_section['title']:
            sections.append(current_section)

        return sections

    def _analyze_layout(self, text: str) -> Dict[str, Any]:
        """Analyze document layout"""
        layout = {
            'alignment': self._detect_alignment(text),
            'spacing': self._analyze_spacing(text),
            'margins': self._analyze_margins(text),
            'columns': self._detect_columns(text)
        }
        return layout

    def _analyze_formatting(self, text: str) -> Dict[str, Any]:
        """Analyze document formatting"""
        formatting = {
            'font_styles': self._detect_font_styles(text),
            'text_emphasis': self._detect_text_emphasis(text),
            'special_characters': self._analyze_special_characters(text),
            'whitespace': self._analyze_whitespace(text)
        }
        return formatting

    def _detect_alignment(self, text: str) -> Dict[str, Any]:
        """Detect text alignment patterns"""
        alignment = {
            'left_aligned': 0,
            'center_aligned': 0,
            'right_aligned': 0,
            'justified': 0
        }

        lines = text.split('\n')
        for line in lines:
            if not line.strip():
                continue

            indent = len(line) - len(line.lstrip())
            if indent > 0:
                alignment['left_aligned'] += 1
            else:

                if line.strip().startswith(' ') and line.strip().endswith(' '):
                    alignment['center_aligned'] += 1

                elif line.strip().endswith(' '):
                    alignment['right_aligned'] += 1

                elif len(line) > 50 and '  ' in line:
                    alignment['justified'] += 1
                else:
                    alignment['left_aligned'] += 1

        return alignment

    def _analyze_spacing(self, text: str) -> Dict[str, Any]:
        """Analyze document spacing"""
        spacing = {
            'line_spacing': 0,
            'paragraph_spacing': 0,
            'section_spacing': 0
        }

        lines = text.split('\n')
        empty_lines = 0
        for line in lines:
            if not line.strip():
                empty_lines += 1
            else:
                if empty_lines == 1:
                    spacing['paragraph_spacing'] += 1
                elif empty_lines > 1:
                    spacing['section_spacing'] += 1
                empty_lines = 0

        return spacing

    def _analyze_margins(self, text: str) -> Dict[str, Any]:
        """Analyze document margins"""
        margins = {
            'left_margin': 0,
            'right_margin': 0,
            'top_margin': 0,
            'bottom_margin': 0
        }

        lines = text.split('\n')
        if lines:

            left_spaces = [len(line) - len(line.lstrip()) for line in lines if line.strip()]
            if left_spaces:
                margins['left_margin'] = min(left_spaces)

            right_spaces = [len(line) - len(line.rstrip()) for line in lines if line.strip()]
            if right_spaces:
                margins['right_margin'] = min(right_spaces)

            top_empty = 0
            for line in lines:
                if not line.strip():
                    top_empty += 1
                else:
                    break
            margins['top_margin'] = top_empty

            bottom_empty = 0
            for line in reversed(lines):
                if not line.strip():
                    bottom_empty += 1
                else:
                    break
            margins['bottom_margin'] = bottom_empty

        return margins

    def _detect_columns(self, text: str) -> Dict[str, Any]:
        """Detect column layout"""
        columns = {
            'single_column': True,
            'multi_column': False,
            'column_count': 1
        }

        lines = text.split('\n')
        if not lines:
            return columns

        separator_count = 0
        for line in lines:
            if re.search(r'^\s*[-+|]+\s*$', line):
                separator_count += 1

        if separator_count > 0:
            columns['single_column'] = False
            columns['multi_column'] = True
            columns['column_count'] = separator_count + 1

        return columns

    def _detect_font_styles(self, text: str) -> Dict[str, Any]:
        """Detect font styles"""
        styles = {
            'all_caps': 0,
            'mixed_case': 0,
            'numeric': 0,
            'special': 0
        }

        lines = text.split('\n')
        for line in lines:
            if not line.strip():
                continue

            if line.isupper():
                styles['all_caps'] += 1
            elif any(c.isupper() for c in line) and any(c.islower() for c in line):
                styles['mixed_case'] += 1
            elif any(c.isdigit() for c in line):
                styles['numeric'] += 1
            if any(not c.isalnum() and not c.isspace() for c in line):
                styles['special'] += 1

        return styles

    def _detect_text_emphasis(self, text: str) -> Dict[str, Any]:
        """Detect text emphasis"""
        emphasis = {
            'bold': 0,
            'italic': 0,
            'underlined': 0
        }

        lines = text.split('\n')
        for line in lines:
            if not line.strip():
                continue

            if re.search(r'\*\*.*?\*\*', line):
                emphasis['bold'] += 1

            if re.search(r'\*.*?\*', line):
                emphasis['italic'] += 1

            if re.search(r'_.*?_', line):
                emphasis['underlined'] += 1

        return emphasis

    def _analyze_special_characters(self, text: str) -> Dict[str, Any]:
        """Analyze special characters"""
        special = {
            'punctuation': 0,
            'symbols': 0,
            'whitespace': 0
        }

        for char in text:
            if char in '.,;:!?':
                special['punctuation'] += 1
            elif char in '@#$%^&*()_+-=[]{}|\\;:"\'<>,.?/~`':
                special['symbols'] += 1
            elif char.isspace():
                special['whitespace'] += 1

        return special

    def _analyze_whitespace(self, text: str) -> Dict[str, Any]:
        """Analyze whitespace usage"""
        whitespace = {
            'spaces': 0,
            'tabs': 0,
            'newlines': 0,
            'indentation': 0
        }

        for char in text:
            if char == ' ':
                whitespace['spaces'] += 1
            elif char == '\t':
                whitespace['tabs'] += 1
            elif char == '\n':
                whitespace['newlines'] += 1

        lines = text.split('\n')
        for line in lines:
            if line.startswith(' '):
                whitespace['indentation'] += 1

        return whitespace

    def _learn_patterns(self, text: str, results: Dict[str, Any]) -> None:
        """Learn from structure analysis"""
        try:

            if results['structure']['has_header']:
                self._learn_structure_pattern('header', text)
            if results['structure']['has_footer']:
                self._learn_structure_pattern('footer', text)
            if results['structure']['has_signature']:
                self._learn_structure_pattern('signature', text)
            if results['structure']['has_stamp']:
                self._learn_structure_pattern('stamp', text)
            if results['structure']['has_table']:
                self._learn_structure_pattern('table', text)
            if results['structure']['has_list']:
                self._learn_structure_pattern('list', text)

            for section in results['sections']:
                self._learn_section_pattern(section)

        except Exception as e:
            logger.error(f"Error learning patterns: {str(e)}")

    def _learn_structure_pattern(self, pattern_type: str, text: str) -> None:
        """Learn structure pattern"""
        if pattern_type not in self.learned_patterns:
            self.learned_patterns[pattern_type] = []

        pattern = {
            'type': pattern_type,
            'context': text[:200],
            'timestamp': time.time()
        }

        if not any(p['type'] == pattern['type'] for p in self.learned_patterns[pattern_type]):
            self.learned_patterns[pattern_type].append(pattern)

    def _learn_section_pattern(self, section: Dict[str, Any]) -> None:
        """Learn section pattern"""
        if 'sections' not in self.learned_patterns:
            self.learned_patterns['sections'] = []

        pattern = {
            'title': section['title'],
            'level': section['level'],
            'content_length': len(section['content']),
            'timestamp': time.time()
        }

        if not any(p['title'] == pattern['title'] for p in self.learned_patterns['sections']):
            self.learned_patterns['sections'].append(pattern)

    def get_patterns(self) -> Dict[str, List[str]]:
        """Get all patterns"""
        return self.structure_patterns

    def get_learned_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get learned patterns"""
        return self.learned_patterns

    def clear_cache(self) -> None:
        """Clear structure cache"""
        self.structure_cache = {}

class ContentAnalyzer:
    def __init__(self):
        self.content_patterns = {}
        self.learned_patterns = {}
        self.content_cache = {}
        self.initialize()

    def initialize(self):
        """Initialize the content analyzer"""
        self.content_patterns = {
            'dates': [
                r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}',
                r'\d{1,2}\s+[A-Za-z]+\s+\d{4}',
                r'[A-Za-z]+\s+\d{1,2}(?:st|nd|rd|th)?\s*,\s*\d{4}'
            ],
            'names': [
                r'(?i)(?:name|full\s*name|applicant|holder|person)[:#]?\s*([A-Za-z\s\.]+)',
                r'(?i)(?:surname|last\s*name|family\s*name)[:#]?\s*([A-Za-z\s\.]+)',
                r'(?i)(?:given\s*names|first\s*name)[:#]?\s*([A-Za-z\s\.]+)'
            ],
            'numbers': [
                r'(?i)(?:number|no|#|id|reference)[:#]?\s*([A-Z0-9\-]+)',
                r'(?i)(?:document|doc)\s*(?:number|no|#)?[:#]?\s*([A-Z0-9\-]+)'
            ],
            'addresses': [
                r'(?i)(?:address|location|residence)[:#]?\s*([A-Za-z0-9\s,\.\-]+)',
                r'(?i)(?:street|road|avenue)[:#]?\s*([A-Za-z0-9\s,\.\-]+)'
            ],
            'contact': [
                r'(?i)(?:phone|mobile|tel|contact)[:#]?\s*([0-9\+\-\(\)\s]+)',
                r'(?i)(?:email|e-mail)[:#]?\s*([A-Za-z0-9\._%\+\-]+@[A-Za-z0-9\.\-]+\.[A-Za-z]{2,})'
            ],
            'amounts': [
                r'(?i)(?:amount|total|sum|value)[:#]?\s*([0-9,\.]+)',
                r'(?i)(?:price|cost|fee)[:#]?\s*([0-9,\.]+)'
            ],
            'status': [
                r'(?i)(?:status|state|condition)[:#]?\s*([A-Za-z\s]+)',
                r'(?i)(?:valid|active|current)[:#]?\s*([A-Za-z\s]+)'
            ]
        }
        self.learned_patterns = {}
        self.content_cache = {}

    def analyze(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze document content"""
        try:
            results = {
                'content': self._analyze_content(text),
                'entities': self._extract_entities(text),
                'metadata': self._extract_metadata(text),
                'summary': self._generate_summary(text)
            }

            self._learn_patterns(text, results)

            return results

        except Exception as e:
            logger.error(f"Error analyzing content: {str(e)}")
            return {
                'content': {},
                'entities': {},
                'metadata': {},
                'summary': '',
                'error': str(e)
            }

    def _analyze_content(self, text: str) -> Dict[str, Any]:
        """Analyze document content"""
        content = {
            'dates': self._extract_dates(text),
            'names': self._extract_names(text),
            'numbers': self._extract_numbers(text),
            'addresses': self._extract_addresses(text),
            'contact': self._extract_contact_info(text),
            'amounts': self._extract_amounts(text),
            'status': self._extract_status(text)
        }
        return content

    def _extract_entities(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """Extract entities from text"""
        entities = {
            'dates': [],
            'names': [],
            'numbers': [],
            'addresses': [],
            'contact': [],
            'amounts': [],
            'status': []
        }

        for pattern in self.content_patterns['dates']:
            matches = re.finditer(pattern, text)
            for match in matches:
                entities['dates'].append({
                    'value': match.group(0),
                    'start': match.start(),
                    'end': match.end(),
                    'context': text[max(0, match.start()-20):min(len(text), match.end()+20)]
                })

        for pattern in self.content_patterns['names']:
            matches = re.finditer(pattern, text)
            for match in matches:
                entities['names'].append({
                    'value': match.group(1) if len(match.groups()) > 0 else match.group(0),
                    'start': match.start(),
                    'end': match.end(),
                    'context': text[max(0, match.start()-20):min(len(text), match.end()+20)]
                })

        for pattern in self.content_patterns['numbers']:
            matches = re.finditer(pattern, text)
            for match in matches:
                entities['numbers'].append({
                    'value': match.group(1) if len(match.groups()) > 0 else match.group(0),
                    'start': match.start(),
                    'end': match.end(),
                    'context': text[max(0, match.start()-20):min(len(text), match.end()+20)]
                })

        for pattern in self.content_patterns['addresses']:
            matches = re.finditer(pattern, text)
            for match in matches:
                entities['addresses'].append({
                    'value': match.group(1) if len(match.groups()) > 0 else match.group(0),
                    'start': match.start(),
                    'end': match.end(),
                    'context': text[max(0, match.start()-20):min(len(text), match.end()+20)]
                })

        for pattern in self.content_patterns['contact']:
            matches = re.finditer(pattern, text)
            for match in matches:
                entities['contact'].append({
                    'value': match.group(1) if len(match.groups()) > 0 else match.group(0),
                    'start': match.start(),
                    'end': match.end(),
                    'context': text[max(0, match.start()-20):min(len(text), match.end()+20)]
                })

        for pattern in self.content_patterns['amounts']:
            matches = re.finditer(pattern, text)
            for match in matches:
                entities['amounts'].append({
                    'value': match.group(1) if len(match.groups()) > 0 else match.group(0),
                    'start': match.start(),
                    'end': match.end(),
                    'context': text[max(0, match.start()-20):min(len(text), match.end()+20)]
                })

        for pattern in self.content_patterns['status']:
            matches = re.finditer(pattern, text)
            for match in matches:
                entities['status'].append({
                    'value': match.group(1) if len(match.groups()) > 0 else match.group(0),
                    'start': match.start(),
                    'end': match.end(),
                    'context': text[max(0, match.start()-20):min(len(text), match.end()+20)]
                })

        return entities

    def _extract_metadata(self, text: str) -> Dict[str, Any]:
        """Extract metadata from text"""
        metadata = {
            'text_length': len(text),
            'word_count': len(text.split()),
            'line_count': len(text.split('\n')),
            'date_count': len(re.findall(r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}', text)),
            'number_count': len(re.findall(r'[A-Z0-9\-]{5,}', text)),
            'email_count': len(re.findall(r'[A-Za-z0-9\._%\+\-]+@[A-Za-z0-9\.\-]+\.[A-Za-z]{2,}', text)),
            'phone_count': len(re.findall(r'[0-9\+\-\(\)\s]{10,}', text))
        }
        return metadata

    def _generate_summary(self, text: str) -> str:
        """Generate a summary of the document content"""

        sentences = re.split(r'[.!?]+', text)

        sentences = [s.strip() for s in sentences if s.strip()]

        summary = ' '.join(sentences[:3])

        return summary

    def _extract_dates(self, text: str) -> List[Dict[str, Any]]:
        """Extract dates from text"""
        dates = []
        for pattern in self.content_patterns['dates']:
            matches = re.finditer(pattern, text)
            for match in matches:
                dates.append({
                    'value': match.group(0),
                    'context': text[max(0, match.start()-20):min(len(text), match.end()+20)]
                })
        return dates

    def _extract_names(self, text: str) -> List[Dict[str, Any]]:
        """Extract names from text"""
        names = []
        for pattern in self.content_patterns['names']:
            matches = re.finditer(pattern, text)
            for match in matches:
                names.append({
                    'value': match.group(1) if len(match.groups()) > 0 else match.group(0),
                    'context': text[max(0, match.start()-20):min(len(text), match.end()+20)]
                })
        return names

    def _extract_numbers(self, text: str) -> List[Dict[str, Any]]:
        """Extract numbers from text"""
        numbers = []
        for pattern in self.content_patterns['numbers']:
            matches = re.finditer(pattern, text)
            for match in matches:
                numbers.append({
                    'value': match.group(1) if len(match.groups()) > 0 else match.group(0),
                    'context': text[max(0, match.start()-20):min(len(text), match.end()+20)]
                })
        return numbers

    def _extract_addresses(self, text: str) -> List[Dict[str, Any]]:
        """Extract addresses from text"""
        addresses = []
        for pattern in self.content_patterns['addresses']:
            matches = re.finditer(pattern, text)
            for match in matches:
                addresses.append({
                    'value': match.group(1) if len(match.groups()) > 0 else match.group(0),
                    'context': text[max(0, match.start()-20):min(len(text), match.end()+20)]
                })
        return addresses

    def _extract_contact_info(self, text: str) -> List[Dict[str, Any]]:
        """Extract contact information from text"""
        contact_info = []
        for pattern in self.content_patterns['contact']:
            matches = re.finditer(pattern, text)
            for match in matches:
                contact_info.append({
                    'value': match.group(1) if len(match.groups()) > 0 else match.group(0),
                    'context': text[max(0, match.start()-20):min(len(text), match.end()+20)]
                })
        return contact_info

    def _extract_amounts(self, text: str) -> List[Dict[str, Any]]:
        """Extract amounts from text"""
        amounts = []
        for pattern in self.content_patterns['amounts']:
            matches = re.finditer(pattern, text)
            for match in matches:
                amounts.append({
                    'value': match.group(1) if len(match.groups()) > 0 else match.group(0),
                    'context': text[max(0, match.start()-20):min(len(text), match.end()+20)]
                })
        return amounts

    def _extract_status(self, text: str) -> List[Dict[str, Any]]:
        """Extract status information from text"""
        status = []
        for pattern in self.content_patterns['status']:
            matches = re.finditer(pattern, text)
            for match in matches:
                status.append({
                    'value': match.group(1) if len(match.groups()) > 0 else match.group(0),
                    'context': text[max(0, match.start()-20):min(len(text), match.end()+20)]
                })
        return status

    def _learn_patterns(self, text: str, results: Dict[str, Any]) -> None:
        """Learn from content analysis"""
        try:

            for entity_type, entities in results['entities'].items():
                if entity_type not in self.learned_patterns:
                    self.learned_patterns[entity_type] = []

                for entity in entities:

                    pattern = {
                        'type': entity_type,
                        'value': entity['value'],
                        'context': entity['context'],
                        'timestamp': time.time()
                    }

                    if not any(p['value'] == pattern['value'] for p in self.learned_patterns[entity_type]):
                        self.learned_patterns[entity_type].append(pattern)

        except Exception as e:
            logger.error(f"Error learning patterns: {str(e)}")

    def get_patterns(self) -> Dict[str, List[str]]:
        """Get all patterns"""
        return self.content_patterns

    def get_learned_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get learned patterns"""
        return self.learned_patterns

    def clear_cache(self) -> None:
        """Clear content cache"""
        self.content_cache = {}

def main():
    input_path = "D:\\imageextractor\\identites\\merged_docs.docx"
    api_key = API_KEY_3

    extractor = DynamicDocumentProcessor(api_key=api_key)

    try:

        if not os.path.exists(input_path):
            raise FileNotFoundError(f"File not found: {input_path}")

        is_merged = True

        if is_merged:

            results = extractor.process_merged_document(input_path)
            print(f"\n📄 Found {len(results)} documents in merged file")
        else:

            result = extractor.process_document(input_path)
            results = [result]
            print("\n📄 Processing single document")

        with open("extracted_documents.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print("\n" + "="*80)
        print("📄 DOCUMENT EXTRACTION RESULTS")
        print("="*80)

        for i, result in enumerate(results, 1):
            print(f"\nDocument {i}:")
            print(f"Type: {result.get('document_type', 'unknown')}")
            print(f"Confidence: {result.get('confidence', 0):.2%}")
            print(f"Text Length: {result.get('metadata', {}).get('text_length', 0):,} characters")
            print(f"Word Count: {result.get('metadata', {}).get('word_count', 0):,} words")
            print(f"Line Count: {result.get('metadata', {}).get('line_count', 0):,} lines")
            print(f"Date Count: {result.get('metadata', {}).get('date_count', 0):,} dates")
            print(f"Number Count: {result.get('metadata', {}).get('number_count', 0):,} numbers")
            print("Extracted Data:")
            for key, value in result.get('extracted_fields', {}).items():
                print(f"  {key}: {value}")
            print("-"*40)

        print(f"\n✅ Extraction completed successfully!")
        print(f"Results saved to: extracted_documents.json")
        print("="*80 + "\n")

    except Exception as e:
        print("\n" + "="*80)
        print("⚠️ ERROR EXTRACTING DOCUMENTS")
        print("="*80)
        print(f"Error: {str(e)}")
        print("="*80 + "\n")

if __name__ == "__main__":
    main()