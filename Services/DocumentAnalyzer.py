import json
import re
import logging
from typing import Dict, List, Any, Optional, Tuple, Set, Protocol, TypeVar, Generic, Union
import os
from dataclasses import dataclass
from collections import defaultdict
import google.generativeai as genai
from abc import ABC, abstractmethod
from pathlib import Path
import importlib
import inspect
import yaml
from datetime import datetime
import hashlib
from concurrent.futures import ThreadPoolExecutor
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar('T')

class DocumentElement(Generic[T]):
    """Generic document element with type safety and validation"""
    def __init__(self, 
                 name: str, 
                 value: T, 
                 confidence: float = 1.0,
                 element_type: str = "unknown",
                 validation_rules: Dict[str, Any] = None):
        self.name = name
        self.value = value
        self.confidence = confidence
        self.element_type = element_type
        self.validation_rules = validation_rules or {}
        self.metadata: Dict[str, Any] = {}
        self.validation_status: Dict[str, bool] = {}
        self.alternative_values: List[T] = []
        self.context: Dict[str, Any] = {}

    def validate(self) -> bool:
        """Validate element against rules"""
        try:
            for rule_name, rule in self.validation_rules.items():
                if not self._apply_validation_rule(rule):
                    self.validation_status[rule_name] = False
                    return False
                self.validation_status[rule_name] = True
            return True
        except Exception as e:
            logger.error(f"Validation error for {self.name}: {str(e)}")
            return False

    def _apply_validation_rule(self, rule: Any) -> bool:
        """Apply a validation rule to the element"""
        if isinstance(rule, str):
            return bool(re.match(rule, str(self.value)))
        elif callable(rule):
            return rule(self.value)
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'value': self.value,
            'confidence': self.confidence,
            'element_type': self.element_type,
            'validation_status': self.validation_status,
            'metadata': self.metadata,
            'context': self.context,
            'alternative_values': self.alternative_values
        }

class DocumentSection:
    """Generic document section with hierarchical structure"""
    def __init__(self, 
                 name: str, 
                 content: str, 
                 confidence: float = 1.0,
                 section_type: str = "unknown"):
        self.name = name
        self.content = content
        self.confidence = confidence
        self.section_type = section_type
        self.elements: List[DocumentElement] = []
        self.subsections: List[DocumentSection] = []
        self.metadata: Dict[str, Any] = {}
        self.relationships: Dict[str, List[str]] = {}
        self.position: Dict[str, Any] = {}
        self.importance: float = 0.0

    def add_element(self, element: DocumentElement):
        """Add an element to the section"""
        self.elements.append(element)
        self._update_relationships(element)

    def add_subsection(self, subsection: 'DocumentSection'):
        """Add a subsection to the section"""
        self.subsections.append(subsection)
        self._update_hierarchy()

    def _update_relationships(self, element: DocumentElement):
        """Update relationships between elements"""
        for existing in self.elements:
            if existing != element:
                # Add bidirectional relationship
                if element.name not in self.relationships:
                    self.relationships[element.name] = []
                if existing.name not in self.relationships:
                    self.relationships[existing.name] = []
                
                self.relationships[element.name].append(existing.name)
                self.relationships[existing.name].append(element.name)

    def _update_hierarchy(self):
        """Update section hierarchy"""
        for subsection in self.subsections:
            subsection.position['parent'] = self.name
            subsection.position['level'] = self.position.get('level', 0) + 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'content': self.content,
            'confidence': self.confidence,
            'section_type': self.section_type,
            'elements': [element.to_dict() for element in self.elements],
            'subsections': [subsection.to_dict() for subsection in self.subsections],
            'metadata': self.metadata,
            'relationships': self.relationships,
            'position': self.position,
            'importance': self.importance
        }

@dataclass
class DocumentFeatures:
    document_type: str
    confidence: float
    sections: List[DocumentSection]
    metadata: Dict[str, Any]
    security_features: List[str]
    additional_info: Dict[str, Any]
    document_hash: str
    analysis_timestamp: str
    version: str = "1.0"

    def to_dict(self) -> Dict[str, Any]:
        return {
            'document_type': self.document_type,
            'confidence': self.confidence,
            'sections': [section.to_dict() for section in self.sections],
            'metadata': self.metadata,
            'security_features': self.security_features,
            'additional_info': self.additional_info,
            'document_hash': self.document_hash,
            'analysis_timestamp': self.analysis_timestamp,
            'version': self.version
        }

class DocumentAnalyzer:
    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.analysis_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_lock = threading.Lock()
        
        # Initialize confidence thresholds
        self.MIN_CONFIDENCE_THRESHOLD = 0.4
        self.HIGH_CONFIDENCE_THRESHOLD = 0.7

    def analyze_document(self, text: str) -> Dict[str, Any]:
        """Analyze document using AI-based approach"""
        try:
            # Check cache first
            doc_hash = self._compute_document_hash(text)
            with self.cache_lock:
                if doc_hash in self.analysis_cache:
                    return self.analysis_cache[doc_hash]

            # Extract document structure
            sections = self._extract_sections(text)
            
            # Identify document type
            doc_type, confidence = self._identify_document_type(text, sections)
            
            # Process sections in parallel
            with ThreadPoolExecutor() as executor:
                futures = []
                for section in sections:
                    futures.append(executor.submit(self._process_section, section))
                
                # Wait for all processing to complete
                for future in futures:
                    future.result()
            
            # Extract metadata
            metadata = self._extract_metadata(text)
            
            # Find security features
            security_features = self._find_security_features(text)
            
            # Create document features
            features = DocumentFeatures(
                document_type=doc_type,
                confidence=confidence,
                sections=sections,
                metadata=metadata,
                security_features=security_features,
                additional_info={
                    'analysis_timestamp': datetime.now().isoformat(),
                    'text_length': len(text),
                    'section_count': len(sections)
                },
                document_hash=doc_hash,
                analysis_timestamp=datetime.now().isoformat()
            )
            
            # Cache results
            with self.cache_lock:
                self.analysis_cache[doc_hash] = features.to_dict()
            
            return features.to_dict()
            
        except Exception as e:
            logger.error(f"Error analyzing document: {str(e)}")
            raise

    def _compute_document_hash(self, text: str) -> str:
        """Compute a unique hash for the document"""
        return hashlib.sha256(text.encode()).hexdigest()

    def _extract_sections(self, text: str) -> List[DocumentSection]:
        """Extract document sections using AI"""
        try:
            prompt = f"""
            Analyze this document and identify its sections and their relationships:

            Text:
            {text}

            Return a JSON array of sections, where each section has:
            {{
                "name": "section_name",
                "content": "section_content",
                "confidence": 0.0-1.0,
                "type": "section_type",
                "importance": 0.0-1.0,
                "metadata": {{
                    "position": "start/end/middle",
                    "importance": "high/medium/low",
                    "contains_fields": true/false,
                    "relationships": ["related_section1", "related_section2"]
                }},
                "subsections": [
                    {{
                        "name": "subsection_name",
                        "content": "subsection_content",
                        "type": "subsection_type",
                        "importance": 0.0-1.0
                    }}
                ]
            }}
            """
            
            response = self.model.generate_content([prompt, text])
            sections_data = json.loads(response.text.strip())
            
            sections = []
            for section_data in sections_data:
                section = DocumentSection(
                    name=section_data['name'],
                    content=section_data['content'],
                    confidence=section_data['confidence'],
                    section_type=section_data['type']
                )
                section.importance = section_data.get('importance', 0.0)
                section.metadata = section_data.get('metadata', {})
                
                # Process subsections
                for subsection_data in section_data.get('subsections', []):
                    subsection = DocumentSection(
                        name=subsection_data['name'],
                        content=subsection_data['content'],
                        section_type=subsection_data['type']
                    )
                    subsection.importance = subsection_data.get('importance', 0.0)
                    section.add_subsection(subsection)
                
                sections.append(section)
            
            return sections
            
        except Exception as e:
            logger.error(f"Error extracting sections: {str(e)}")
            return []

    def _process_section(self, section: DocumentSection):
        """Process a document section to extract elements"""
        try:
            prompt = f"""
            Extract elements from this document section:

            Section Name: {section.name}
            Content: {section.content}

            Return a JSON array of elements, where each element has:
            {{
                "name": "element_name",
                "value": "element_value",
                "confidence": 0.0-1.0,
                "type": "element_type",
                "validation_rules": {{
                    "rule1": "pattern1",
                    "rule2": "pattern2"
                }},
                "metadata": {{
                    "format": "element_format",
                    "importance": "high/medium/low",
                    "context": "element_context"
                }},
                "alternative_values": ["alt1", "alt2"]
            }}
            """
            
            response = self.model.generate_content([prompt, section.content])
            elements_data = json.loads(response.text.strip())
            
            for element_data in elements_data:
                element = DocumentElement(
                    name=element_data['name'],
                    value=element_data['value'],
                    confidence=element_data['confidence'],
                    element_type=element_data['type'],
                    validation_rules=element_data.get('validation_rules', {})
                )
                element.metadata = element_data.get('metadata', {})
                element.alternative_values = element_data.get('alternative_values', [])
                section.add_element(element)
            
        except Exception as e:
            logger.error(f"Error processing section {section.name}: {str(e)}")

    def _identify_document_type(self, text: str, sections: List[DocumentSection]) -> Tuple[str, float]:
        """Identify document type using AI"""
        try:
            prompt = f"""
            Analyze this document and identify its type:

            Text:
            {text}

            Sections:
            {json.dumps([section.to_dict() for section in sections], indent=2)}

            Return a JSON response with:
            {{
                "document_type": "identified_type",
                "confidence": 0.0-1.0,
                "reasoning": "explanation of why this document type was identified",
                "key_characteristics": ["characteristic1", "characteristic2", ...],
                "metadata": {{
                    "category": "document_category",
                    "format": "document_format",
                    "purpose": "document_purpose",
                    "region": "document_region",
                    "language": "document_language",
                    "version": "document_version"
                }}
            }}
            """
            
            response = self.model.generate_content([prompt, text])
            result = json.loads(response.text.strip())
            
            return result["document_type"], result["confidence"]
            
        except Exception as e:
            logger.error(f"Error identifying document type: {str(e)}")
            return "unknown", 0.0

    def _extract_metadata(self, text: str) -> Dict[str, Any]:
        """Extract document metadata"""
        try:
            prompt = f"""
            Extract metadata from this document:

            Text:
            {text}

            Return a JSON object with:
            {{
                "creation_date": "date",
                "modification_date": "date",
                "author": "author_name",
                "version": "version_number",
                "references": ["reference1", "reference2", ...],
                "language": "document_language",
                "region": "document_region",
                "purpose": "document_purpose",
                "format": "document_format",
                "security_level": "high/medium/low",
                "additional_metadata": {{
                    "key1": "value1",
                    "key2": "value2"
                }}
            }}
            """
            
            response = self.model.generate_content([prompt, text])
            metadata = json.loads(response.text.strip())
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}")
            return {}

    def _find_security_features(self, text: str) -> List[str]:
        """Find security features in document"""
        try:
            prompt = f"""
            Identify security features in this document:

            Text:
            {text}

            Return a JSON object with:
            {{
                "security_features": [
                    {{
                        "type": "feature_type",
                        "description": "feature_description",
                        "confidence": 0.0-1.0,
                        "location": "feature_location",
                        "verification_method": "verification_method",
                        "importance": "high/medium/low"
                    }}
                ],
                "security_level": "high/medium/low",
                "verification_methods": ["method1", "method2", ...],
                "risk_assessment": {{
                    "risk_level": "high/medium/low",
                    "vulnerabilities": ["vuln1", "vuln2"],
                    "recommendations": ["rec1", "rec2"]
                }}
            }}
            """
            
            response = self.model.generate_content([prompt, text])
            result = json.loads(response.text.strip())
            
            return [feature['type'] for feature in result.get('security_features', [])]
            
        except Exception as e:
            logger.error(f"Error finding security features: {str(e)}")
            return []

def main():
    api_key = "your_api_key"
    analyzer = DocumentAnalyzer(api_key)
    
    # Example usage
    text = """
    PASSPORT
    Type: P
    Country Code: USA
    Passport No: P12345678
    Surname: DOE
    Given Names: JOHN
    Nationality: USA
    Date of Birth: 01/01/1980
    Place of Birth: NEW YORK
    Date of Issue: 01/01/2020
    Date of Expiry: 01/01/2030
    Authority: US DEPARTMENT OF STATE
    """
    
    try:
        result = analyzer.analyze_document(text)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 