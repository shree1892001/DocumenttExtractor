"""
Constants for document processing, including document categories and patterns.
"""

# Document Categories and Types
DOCUMENT_CATEGORIES = {
    'identity': [
        'passport', 'national_id', 'drivers_license', 'residence_permit',
        'citizenship_card', 'voter_id', 'aadhaar_card', 'pan_card',
        'social_security_card', 'health_insurance_card', 'student_id',
        'employee_id', 'military_id', 'government_id', 'immigration_document',
        'alien_registration_card', 'refugee_id', 'temporary_resident_card',
        'work_permit', 'visa_document', 'border_crossing_card', 'travel_document',
        'diplomatic_id', 'consular_id', 'maritime_id', 'aviation_id',
        'professional_license', 'occupational_license', 'medical_license',
        'law_license', 'teaching_license', 'engineering_license'
    ],
    'legal': [
        'contract', 'agreement', 'deed', 'power_of_attorney',
        'court_order', 'legal_notice', 'affidavit', 'will',
        'trust_deed', 'marriage_certificate', 'divorce_decree',
        'adoption_papers', 'custody_document', 'legal_opinion',
        'regulatory_compliance', 'intellectual_property_document',
        'patent_document', 'trademark_registration', 'copyright_document',
        'legal_brief', 'court_filing', 'legal_memorandum', 'legal_contract',
        'settlement_agreement', 'arbitration_award', 'legal_judgment',
        'legal_injunction', 'legal_subpoena', 'legal_warrant',
        'legal_pleading', 'legal_motion', 'legal_appeal', 'legal_brief',
        'legal_opinion', 'legal_advice', 'legal_consultation'
    ],
    'financial': [
        'bank_statement', 'tax_return', 'invoice', 'receipt',
        'credit_card_statement', 'loan_document', 'insurance_policy',
        'investment_statement', 'mortgage_document', 'payroll_document',
        'financial_report', 'budget_document', 'expense_report',
        'financial_audit', 'accounting_document', 'balance_sheet',
        'income_statement', 'cash_flow_statement', 'financial_forecast',
        'financial_plan', 'investment_proposal', 'financial_analysis',
        'financial_review', 'financial_summary', 'financial_statement',
        'financial_record', 'financial_transaction', 'financial_receipt',
        'financial_invoice', 'financial_contract', 'financial_agreement',
        'financial_certificate', 'financial_license', 'financial_permit'
    ],
    'educational': [
        'degree_certificate', 'diploma', 'transcript', 'report_card',
        'scholarship_document', 'academic_certificate', 'enrollment_document',
        'course_completion', 'professional_certification', 'training_certificate',
        'academic_transcript', 'student_record', 'educational_assessment',
        'academic_reference', 'educational_plan', 'academic_achievement',
        'academic_award', 'academic_merit', 'academic_honor',
        'academic_qualification', 'academic_credential', 'academic_license',
        'academic_permit', 'academic_certification', 'academic_verification',
        'academic_validation', 'academic_confirmation', 'academic_approval',
        'academic_authorization', 'academic_clearance', 'academic_eligibility'
    ],
    'medical': [
        'medical_report', 'prescription', 'health_insurance',
        'vaccination_record', 'medical_certificate', 'patient_record',
        'medical_history', 'diagnostic_report', 'treatment_plan',
        'medical_referral', 'discharge_summary', 'medical_bill',
        'medical_authorization', 'medical_consent', 'medical_imaging',
        'medical_scan', 'medical_test', 'medical_lab_result',
        'medical_analysis', 'medical_evaluation', 'medical_assessment',
        'medical_diagnosis', 'medical_prognosis', 'medical_recommendation',
        'medical_advice', 'medical_consultation', 'medical_opinion',
        'medical_verification', 'medical_validation', 'medical_confirmation',
        'medical_approval', 'medical_authorization', 'medical_clearance'
    ],
    'business': [
        'business_license', 'incorporation_document', 'tax_registration',
        'commercial_invoice', 'shipping_document', 'business_plan',
        'company_policy', 'employee_handbook', 'business_contract',
        'partnership_agreement', 'board_resolution', 'annual_report',
        'business_proposal', 'marketing_document', 'business_correspondence',
        'business_agreement', 'business_certificate', 'business_license',
        'business_permit', 'business_registration', 'business_incorporation',
        'business_formation', 'business_dissolution', 'business_merger',
        'business_acquisition', 'business_sale', 'business_purchase',
        'business_transfer', 'business_assignment', 'business_delegation',
        'business_authorization', 'business_approval', 'business_clearance'
    ],
    'government': [
        'government_id', 'permit', 'license', 'registration',
        'certificate', 'official_letter', 'government_form',
        'regulatory_document', 'compliance_certificate', 'government_report',
        'official_notice', 'government_contract', 'public_record',
        'government_authorization', 'official_documentation', 'government_approval',
        'government_clearance', 'government_verification', 'government_validation',
        'government_confirmation', 'government_certification', 'government_license',
        'government_permit', 'government_registration', 'government_incorporation',
        'government_formation', 'government_dissolution', 'government_merger',
        'government_acquisition', 'government_sale', 'government_purchase',
        'government_transfer', 'government_assignment', 'government_delegation'
    ],
    'employment': [
        'employment_contract', 'payslip', 'tax_form',
        'employment_certificate', 'resume', 'job_application',
        'performance_review', 'employment_verification', 'work_permit',
        'employee_benefits', 'termination_document', 'promotion_letter',
        'employment_agreement', 'job_description', 'employment_record',
        'employment_authorization', 'employment_approval', 'employment_clearance',
        'employment_verification', 'employment_validation', 'employment_confirmation',
        'employment_certification', 'employment_license', 'employment_permit',
        'employment_registration', 'employment_incorporation', 'employment_formation',
        'employment_dissolution', 'employment_merger', 'employment_acquisition',
        'employment_sale', 'employment_purchase', 'employment_transfer'
    ],
    'property': [
        'property_deed', 'mortgage_document', 'lease_agreement',
        'property_tax_document', 'survey_document', 'title_deed',
        'property_insurance', 'property_assessment', 'property_valuation',
        'property_inspection', 'property_maintenance', 'property_transfer',
        'property_development', 'property_management', 'property_contract',
        'property_authorization', 'property_approval', 'property_clearance',
        'property_verification', 'property_validation', 'property_confirmation',
        'property_certification', 'property_license', 'property_permit',
        'property_registration', 'property_incorporation', 'property_formation',
        'property_dissolution', 'property_merger', 'property_acquisition',
        'property_sale', 'property_purchase', 'property_transfer'
    ],
    'transportation': [
        'vehicle_registration', 'vehicle_title', 'vehicle_insurance',
        'vehicle_inspection', 'vehicle_maintenance', 'vehicle_transfer',
        'vehicle_authorization', 'vehicle_approval', 'vehicle_clearance',
        'vehicle_verification', 'vehicle_validation', 'vehicle_confirmation',
        'vehicle_certification', 'vehicle_license', 'vehicle_permit',
        'vehicle_registration', 'vehicle_incorporation', 'vehicle_formation',
        'vehicle_dissolution', 'vehicle_merger', 'vehicle_acquisition',
        'vehicle_sale', 'vehicle_purchase', 'vehicle_transfer',
        'vehicle_assignment', 'vehicle_delegation', 'vehicle_authorization',
        'vehicle_approval', 'vehicle_clearance', 'vehicle_verification'
    ],
    'insurance': [
        'insurance_policy', 'insurance_certificate', 'insurance_claim',
        'insurance_verification', 'insurance_validation', 'insurance_confirmation',
        'insurance_certification', 'insurance_license', 'insurance_permit',
        'insurance_registration', 'insurance_incorporation', 'insurance_formation',
        'insurance_dissolution', 'insurance_merger', 'insurance_acquisition',
        'insurance_sale', 'insurance_purchase', 'insurance_transfer',
        'insurance_assignment', 'insurance_delegation', 'insurance_authorization',
        'insurance_approval', 'insurance_clearance', 'insurance_verification',
        'insurance_validation', 'insurance_confirmation', 'insurance_certification',
        'insurance_license', 'insurance_permit', 'insurance_registration'
    ],
    'other': []  # For uncategorized document types
}

# Document Type Mappings
DOCUMENT_TYPE_MAPPING = {
    "aadhaar": "aadhaar_card",
    "aadhaarcard": "aadhaar_card",
    "aadhar": "aadhaar_card",
    "aadharcard": "aadhaar_card",
    "pan": "pan_card",
    "pancard": "pan_card",
    "license": "license",
    "driving license": "license",
    "dl": "license",
    "passport": "passport",
    "travel document": "passport",
    "national passport": "passport",
    "diplomatic passport": "passport",
    "official passport": "passport",
    "service passport": "passport"
}

# Document Type Indicators
DOCUMENT_INDICATORS = {
    "aadhaar_card": [
        "- 12-digit Aadhaar number",
        "- Name of the holder",
        "- Date of birth",
        "- Gender",
        "- Address",
        "- UIDAI logo or text",
        "- QR code or barcode"
    ],
    "license": [
        "- License number",
        "- Name of the holder",
        "- Date of birth",
        "- Address",
        "- License type/class",
        "- Issue and expiry dates",
        "- Issuing authority"
    ],
    "pan_card": [
        "- 10-character PAN number",
        "- Name of the holder",
        "- Father's name",
        "- Date of birth",
        "- PAN card number format",
        "- Income Tax Department text"
    ]
}

# Document Processing Constants
MIN_CONFIDENCE_THRESHOLD = 0.4
HIGH_CONFIDENCE_THRESHOLD = 0.8
MIN_GENUINENESS_SCORE = 0.6
VERIFICATION_THRESHOLD = 0.5

# Supported File Extensions
SUPPORTED_EXTENSIONS = {'.docx', '.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.bmp'}

# Document Field Patterns
FIELD_PATTERNS = [
    r'\{([^}]+)\}',
    r'([^:]+):',
    r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
]

# Document Separators
DOCUMENT_SEPARATORS = [
    r'\n\s*\n\s*\n',  # Multiple blank lines
    r'[-=]{3,}',      # Lines of dashes or equals
    r'_{3,}',         # Lines of underscores
    r'\*{3,}',        # Lines of asterisks
    r'Page \d+',      # Page numbers
    r'Document \d+',  # Document numbers
    r'Copy \d+',      # Copy numbers
    r'Original',      # Original document marker
    r'Duplicate',     # Duplicate document marker
    r'COPY',          # COPY marker
    r'ORIGINAL'       # ORIGINAL marker
]

# OCR Error Patterns
OCR_ERROR_PATTERNS = [
    r'[|]{2,}',
    r'[l1]{3,}',
    r'[o0]{3,}',
    r'[rn]{3,}',
    r'\s{3,}'
]

# Character-by-Character Patterns
CHARACTER_PATTERNS = [
    r'[A-Z]\s+[A-Z]\s+[A-Z]',
    r'[a-z]\s+[a-z]\s+[a-z]',
    r'[0-9]\s+[0-9]\s+[0-9]',
    r'[A-Za-z]\s+[A-Za-z]\s+[A-Za-z]'
]

# Meaningful Content Indicators
CONTENT_INDICATORS = [
    r'[A-Z]{2,}',
    r'\d{4,}',
    r'[A-Za-z]+\s+[A-Za-z]+',
    r'[A-Za-z]+\s+\d+',
    r'\d+\s+[A-Za-z]+'
]

# Document Indicator Keywords
DOCUMENT_INDICATOR_KEYWORDS = [
    "name", "date", "address", "signature", "photo",
    "passport", "license", "id", "number", "issued"
]

# Non-Genuine Document Indicators
NON_GENUINE_INDICATORS = [
    "sample", "template", "example", "dummy", "test",
    "not for official use", "for demonstration",
    "training", "practice", "mock",
    "photocopy", "scan", "digital copy",
    "this is a", "this document is",
    "for testing", "for practice",
    "do not use", "invalid",
    "unofficial", "non-official"
]

# Document Processing Prompts
DOCUMENT_PROMPTS = {
    "detection": """
        Analyze this text and determine what type of document it is (license, aadhaar_card, pan_card, or passport).
        Look for these indicators:
        - Aadhaar: "Aadhaar", "UIDAI", "आधार", "Unique Identification"
        - PAN: "PAN", "Permanent Account Number", "Income Tax"
        - License: "License", "Driving License", "DL", "RTO"
        - Passport: "Passport", "Passport Number", "Nationality"

        Text:
        {text}

        Return a JSON response with:
        {{
            "document_type": "detected_type",
            "confidence": 0.0-1.0,
            "reasoning": "explanation"
        }}

        Important:
        - Only return document_type as one of: "license", "aadhaar_card", "pan_card", "passport"
        - If you cannot confidently determine the type, return "unknown"
        - Be strict in your confidence scoring
        - Consider a document type only if you see clear indicators
    """,

    "extraction": """
        You are a document analysis expert. Extract all relevant information from this {doc_type} document.

        Document Text:
        {text}

        For a {doc_type}, look for and extract these specific fields:
        {fields}

        Important:
        1. Extract ALL visible information from the document
        2. If a field is not found, use "None" as the value
        3. For dates, use YYYY-MM-DD format
        4. For numbers, extract them exactly as shown
        5. For names and addresses, preserve the exact spelling and formatting

        Return the extracted information in JSON format with this structure:
        {{
            "data": {{
                // All extracted fields
            }},
            "confidence": 0.0-1.0,
            "additional_info": "Any additional relevant information"
        }}
    """,

    "verification": """
        You are a document verification expert specializing in {doc_type} verification. 
        Analyze this document data and determine if it is genuine.
        Provide a detailed verification report with specific checks and findings.

        Document Data:
        {data}

        Document Type: {doc_type}

        Perform the following checks:

        1. Document Authenticity:
           - Verify presence of required fields for {doc_type}
           - Check for official text and formatting
           - Validate document structure and layout
           - Check for security features specific to {doc_type}
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

        3. Data Validation:
           - Verify all identification numbers and their formats
           - Check date formats and their logical consistency
           - Validate name and address formatting
           - Look for any data inconsistencies
           - Verify field relationships and dependencies
           - Check for logical data patterns
           - Validate any reference numbers

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
                    "details": "explanation",
                    "confidence": 0.0-1.0
                }},
                "security_features": {{
                    "passed": true/false,
                    "details": "explanation",
                    "confidence": 0.0-1.0
                }},
                "data_validation": {{
                    "passed": true/false,
                    "details": "explanation",
                    "confidence": 0.0-1.0
                }},
                "quality": {{
                    "passed": true/false,
                    "details": "explanation",
                    "confidence": 0.0-1.0
                }}
            }},
            "security_features_found": ["list of security features"],
            "verification_summary": "Overall verification summary",
            "recommendations": ["list of recommendations for improvement"]
        }}

        Important:
        - Be thorough but fair in your analysis
        - Consider document-specific requirements for {doc_type}
        - Account for variations in official document formats
        - Consider both digital and physical security features
        - Look for logical consistency in the data
        - Consider the document's intended use
        - Be lenient with minor formatting variations
        - Focus on key security features and data validity
        - Consider official document standards
        - Account for regional variations in document formats
    """,

    "genuineness_check": """
        You are an expert document verification AI. Your task is to determine if this document is genuine BEFORE any data extraction.

        Document Text:
        {text}

        Perform a thorough genuineness check:

        1. Document Authenticity:
           - Verify if this is a genuine official document
           - Check for official government/issuing authority text and formatting
           - Look for security features and anti-counterfeit measures
           - Validate document structure and layout
           - Check for official logos and seals

        2. Security Feature Analysis:
           - Check for official seals, watermarks, or holograms
           - Look for security patterns or microtext
           - Verify presence of QR codes or barcodes
           - Check for official government/issuing authority text
           - Look for security threads or special paper

        3. Red Flag Detection:
           - Look for signs of forgery or tampering
           - Check for missing security features
           - Identify suspicious patterns
           - Look for inconsistencies in formatting
           - Check for sample/template indicators
           - Look for "not for official use" or similar disclaimers

        4. Document Quality:
           - Check for professional printing quality
           - Verify proper alignment and formatting
           - Look for official document design elements
           - Check for proper spacing and typography

        Return a JSON response with:
        {{
            "is_genuine": true/false,
            "confidence_score": 0.0-1.0,
            "rejection_reason": "detailed explanation if not genuine",
            "verification_checks": [
                {{
                    "check_type": "type of check",
                    "status": "passed/failed",
                    "details": "explanation"
                }}
            ],
            "security_features_found": ["list of found features"],
            "verification_summary": "detailed explanation"
        }}

        Important:
        - Be extremely thorough in your analysis
        - Reject any document that shows signs of being:
          * A sample or template
          * A photocopy or scan
          * A digital copy
          * A test document
          * A demonstration document
          * A training document
        - Look for any signs of forgery or tampering
        - Provide detailed explanations for your decisions
        - If in doubt, reject the document
        - Only accept documents that are clearly genuine official documents
    """
}

# Document Field Extraction Templates
DOCUMENT_FIELD_TEMPLATES = {
    "license": """
        - License Number (look for DL number, license number, etc.)
        - Name (full name of the license holder)
        - Date of Birth (DOB, birth date)
        - Address (current address)
        - Valid From (issue date, date of issue)
        - Valid Until (expiry date, valid till)
        - Vehicle Categories (classes of vehicles allowed)
        - Issuing Authority (RTO, DMV, etc.)
    """,
    "aadhaar_card": """
        - Aadhaar Number (12-digit number)
        - Name (full name)
        - Gender
        - Date of Birth
        - Address
        - Father's Name
        - Photo
    """,
    "pan_card": """
        - PAN Number (10-character alphanumeric)
        - Name
        - Father's Name
        - Date of Birth
        - Photo
    """,
    "passport": """
        - Passport Number (look for P, A, C, S prefixes)
        - Type/Category (Regular, Diplomatic, Official, Service)
        - Country Code (3-letter code)
        - Surname/Last Name
        - Given Names
        - Nationality
        - Date of Birth
        - Place of Birth
        - Gender
        - Date of Issue
        - Date of Expiry
        - Authority/Issuing Country
        - Personal Number (if present)
        - Machine Readable Zone (MRZ)
        - Photo
        - Signature
        - Security Features
    """
} 