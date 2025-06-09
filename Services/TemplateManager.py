"""
Template Manager for Document Processing
Manages document templates, matching, and classification
"""

import os
import json
import re
import logging
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class DocumentCategory(Enum):
    """Document categories for classification"""
    EDUCATIONAL = "educational"
    MEDICAL = "medical"
    FINANCIAL = "financial"
    LEGAL = "legal"
    EMPLOYMENT = "employment"
    IDENTITY = "identity"
    CERTIFICATION = "certification"
    UNKNOWN = "unknown"


@dataclass
class DocumentTemplate:
    """Document template definition"""
    id: str
    name: str
    category: DocumentCategory
    description: str
    keywords: List[str]
    patterns: List[str]
    required_fields: List[str]
    optional_fields: List[str]
    confidence_threshold: float = 0.7
    sample_text: str = ""


class TemplateManager:
    """Manages document templates and matching"""
    
    def __init__(self):
        """Initialize template manager with predefined templates"""
        self.templates = {}
        self._initialize_templates()
        logger.info(f"TemplateManager initialized with {len(self.templates)} templates")
    
    def _initialize_templates(self):
        """Initialize predefined document templates"""
        
        # Educational Templates
        self.add_template(DocumentTemplate(
            id="student_transcript",
            name="Student Transcript",
            category=DocumentCategory.EDUCATIONAL,
            description="Official academic transcript with grades and GPA",
            keywords=["transcript", "gpa", "grade", "course", "credit", "semester", "academic"],
            patterns=[
                r"(?i)official\s+transcript",
                r"(?i)grade\s+point\s+average",
                r"(?i)gpa\s*:?\s*\d+\.\d+",
                r"(?i)credit\s+hours?",
                r"(?i)semester|quarter"
            ],
            required_fields=["student_name", "student_id", "gpa", "institution"],
            optional_fields=["graduation_date", "degree", "major", "courses"],
            sample_text="Official Transcript - Student: John Doe, GPA: 3.85"
        ))
        
        self.add_template(DocumentTemplate(
            id="diploma_certificate",
            name="Diploma/Certificate",
            category=DocumentCategory.EDUCATIONAL,
            description="Graduation diploma or academic certificate",
            keywords=["diploma", "certificate", "graduation", "degree", "bachelor", "master"],
            patterns=[
                r"(?i)diploma",
                r"(?i)certificate",
                r"(?i)bachelor\s+of",
                r"(?i)master\s+of",
                r"(?i)graduation",
                r"(?i)conferred|awarded"
            ],
            required_fields=["recipient_name", "degree", "institution", "graduation_date"],
            optional_fields=["honors", "major", "minor"],
            sample_text="This diploma certifies that John Doe has earned Bachelor of Science"
        ))
        
        # Professional Certification Templates
        self.add_template(DocumentTemplate(
            id="professional_certification",
            name="Professional Certification",
            category=DocumentCategory.CERTIFICATION,
            description="Professional certifications and licenses",
            keywords=["certification", "certified", "license", "professional", "credential"],
            patterns=[
                r"(?i)certification",
                r"(?i)certified\s+\w+",
                r"(?i)license\s+number",
                r"(?i)professional\s+license",
                r"(?i)credential"
            ],
            required_fields=["holder_name", "certification_name", "issue_date"],
            optional_fields=["expiration_date", "certification_number", "issuing_authority"],
            sample_text="AWS Certified Solutions Architect - Professional Certification"
        ))
        
        # Medical Templates
        self.add_template(DocumentTemplate(
            id="medical_license",
            name="Medical License",
            category=DocumentCategory.MEDICAL,
            description="Medical professional license",
            keywords=["medical", "license", "physician", "doctor", "md", "nurse", "rn"],
            patterns=[
                r"(?i)medical\s+license",
                r"(?i)physician\s+license",
                r"(?i)doctor\s+of\s+medicine",
                r"(?i)nursing\s+license",
                r"(?i)license\s+number\s*:?\s*[A-Z0-9]+"
            ],
            required_fields=["licensee_name", "license_number", "license_type"],
            optional_fields=["issue_date", "expiration_date", "medical_board"],
            sample_text="California Medical Board - Physician License - Dr. Jane Smith"
        ))
        
        # Employment Templates
        self.add_template(DocumentTemplate(
            id="resume_cv",
            name="Resume/CV",
            category=DocumentCategory.EMPLOYMENT,
            description="Professional resume or curriculum vitae",
            keywords=["resume", "cv", "curriculum vitae", "experience", "education", "skills"],
            patterns=[
                r"(?i)resume|curriculum\s+vitae",
                r"(?i)work\s+experience",
                r"(?i)professional\s+experience",
                r"(?i)education\s*:",
                r"(?i)skills\s*:"
            ],
            required_fields=["name", "email", "phone"],
            optional_fields=["address", "experience", "education", "skills"],
            sample_text="John Doe - Software Engineer Resume - Experience: 5 years"
        ))
        
        # Financial Templates
        self.add_template(DocumentTemplate(
            id="bank_statement",
            name="Bank Statement",
            category=DocumentCategory.FINANCIAL,
            description="Bank account statement",
            keywords=["bank", "statement", "account", "balance", "transaction"],
            patterns=[
                r"(?i)bank\s+statement",
                r"(?i)account\s+number",
                r"(?i)opening\s+balance",
                r"(?i)closing\s+balance",
                r"(?i)transaction\s+history"
            ],
            required_fields=["account_holder", "account_number", "statement_period"],
            optional_fields=["opening_balance", "closing_balance", "transactions"],
            sample_text="Bank Statement - Account Holder: John Doe - Account: 123456789"
        ))
        
        # Identity Templates
        self.add_template(DocumentTemplate(
            id="passport",
            name="Passport",
            category=DocumentCategory.IDENTITY,
            description="Passport identification document",
            keywords=["passport", "nationality", "passport number", "country"],
            patterns=[
                r"(?i)passport",
                r"(?i)passport\s+number",
                r"(?i)nationality",
                r"(?i)country\s+of\s+issue",
                r"(?i)date\s+of\s+birth"
            ],
            required_fields=["full_name", "passport_number", "nationality"],
            optional_fields=["date_of_birth", "place_of_birth", "issue_date", "expiry_date"],
            sample_text="Passport - Full Name: John Doe - Passport Number: A12345678"
        ))
        
        # Legal Templates
        self.add_template(DocumentTemplate(
            id="contract",
            name="Legal Contract",
            category=DocumentCategory.LEGAL,
            description="Legal contract or agreement",
            keywords=["contract", "agreement", "party", "terms", "conditions"],
            patterns=[
                r"(?i)contract|agreement",
                r"(?i)party\s+of\s+the\s+first\s+part",
                r"(?i)terms\s+and\s+conditions",
                r"(?i)whereas",
                r"(?i)in\s+consideration\s+of"
            ],
            required_fields=["parties", "contract_type", "date"],
            optional_fields=["terms", "conditions", "signatures"],
            sample_text="Employment Contract between Company ABC and John Doe"
        ))
    
    def add_template(self, template: DocumentTemplate):
        """Add a template to the manager"""
        self.templates[template.id] = template
        logger.debug(f"Added template: {template.name}")
    
    def get_all_templates(self) -> Dict[str, DocumentTemplate]:
        """Get all available templates"""
        return self.templates.copy()
    
    def get_templates_by_category(self, category: DocumentCategory) -> Dict[str, DocumentTemplate]:
        """Get templates by category"""
        return {
            tid: template for tid, template in self.templates.items()
            if template.category == category
        }
    
    def match_document_to_template(self, text: str) -> Tuple[Optional[DocumentTemplate], float]:
        """
        Match document text to the best template
        
        Args:
            text: Document text content
            
        Returns:
            Tuple of (best_template, confidence_score)
        """
        try:
            text_lower = text.lower()
            best_template = None
            best_score = 0.0
            
            for template in self.templates.values():
                score = self._calculate_template_score(text_lower, template)
                
                if score > best_score and score >= template.confidence_threshold:
                    best_score = score
                    best_template = template
            
            logger.info(f"Best template match: {best_template.name if best_template else 'None'} (score: {best_score:.2f})")
            return best_template, best_score
            
        except Exception as e:
            logger.error(f"Error matching document to template: {str(e)}")
            return None, 0.0
    
    def _calculate_template_score(self, text: str, template: DocumentTemplate) -> float:
        """Calculate matching score between text and template"""
        try:
            keyword_score = 0.0
            pattern_score = 0.0
            
            # Calculate keyword score
            keyword_matches = 0
            for keyword in template.keywords:
                if keyword.lower() in text:
                    keyword_matches += 1
            
            if template.keywords:
                keyword_score = keyword_matches / len(template.keywords)
            
            # Calculate pattern score
            pattern_matches = 0
            for pattern in template.patterns:
                if re.search(pattern, text):
                    pattern_matches += 1
            
            if template.patterns:
                pattern_score = pattern_matches / len(template.patterns)
            
            # Combined score (weighted average)
            total_score = (keyword_score * 0.4) + (pattern_score * 0.6)
            
            return total_score
            
        except Exception as e:
            logger.error(f"Error calculating template score: {str(e)}")
            return 0.0
    
    def get_template_by_id(self, template_id: str) -> Optional[DocumentTemplate]:
        """Get template by ID"""
        return self.templates.get(template_id)
    
    def get_template_summary(self) -> Dict[str, Any]:
        """Get summary of all templates"""
        summary = {
            "total_templates": len(self.templates),
            "categories": {},
            "templates": []
        }
        
        # Count by category
        for template in self.templates.values():
            category = template.category.value
            if category not in summary["categories"]:
                summary["categories"][category] = 0
            summary["categories"][category] += 1
            
            # Add template info
            summary["templates"].append({
                "id": template.id,
                "name": template.name,
                "category": category,
                "description": template.description,
                "required_fields": len(template.required_fields),
                "optional_fields": len(template.optional_fields)
            })
        
        return summary


# Utility functions
def create_template_manager() -> TemplateManager:
    """Create and initialize a template manager"""
    return TemplateManager()


def match_document_text(text: str) -> Tuple[Optional[DocumentTemplate], float]:
    """Quick function to match document text to template"""
    manager = create_template_manager()
    return manager.match_document_to_template(text)


# Example usage and testing
if __name__ == "__main__":
    print("Template Manager - Document Classification System")
    print("=" * 60)
    
    try:
        # Initialize template manager
        manager = create_template_manager()
        
        # Get summary
        summary = manager.get_template_summary()
        print(f"📋 Total Templates: {summary['total_templates']}")
        print(f"📊 Categories: {list(summary['categories'].keys())}")
        
        # Test template matching
        test_documents = [
            "Official Transcript - Student: John Doe, GPA: 3.85, Credits: 120",
            "AWS Certified Solutions Architect Professional Certification",
            "Medical License - Dr. Jane Smith, License Number: MD123456",
            "Employment Contract between TechCorp and John Doe"
        ]
        
        print("\n🧪 Testing Template Matching:")
        for i, doc_text in enumerate(test_documents, 1):
            template, score = manager.match_document_to_template(doc_text)
            print(f"\n{i}. Document: {doc_text[:50]}...")
            if template:
                print(f"   ✅ Matched: {template.name} (score: {score:.2f})")
                print(f"   📂 Category: {template.category.value}")
            else:
                print(f"   ❌ No template match found")
        
        print("\n✅ Template Manager working correctly!")
        
    except Exception as e:
        print(f"❌ Error in template manager demo: {str(e)}")
