# Confidential Document Processing

## Overview

The `ConfidentialDocumentProcessor` is a comprehensive document processor designed to handle **ALL types of confidential documents** without sending data to external AI services like Google Gemini. This ensures complete privacy and confidentiality for sensitive personal information.

## Problem Solved

**Issue**: The original `DocumentProcessor3` uses Google Gemini for text extraction and document analysis, which means sensitive document data is sent to external servers.

**Solution**: The `ConfidentialDocumentProcessor` automatically detects **ALL confidential documents** and processes them using only local OCR and pattern matching, ensuring no sensitive data leaves your system.

## Features

### 🔒 Privacy Protection
- **No External AI**: ALL confidential documents are processed entirely locally
- **Automatic Detection**: Automatically identifies ALL types of confidential documents
- **Fallback Safety**: Defaults to local processing if document type cannot be determined
- **Zero Data Leakage**: Sensitive information never leaves your system

### 🎯 Smart Document Detection
- **Multi-Type Detection**: Detects identity, financial, medical, employment, legal, and educational documents
- **Keyword Analysis**: Uses comprehensive keyword sets for each document category
- **Pattern Matching**: Identifies document-specific patterns and structures
- **Sensitivity Markers**: Detects explicit confidentiality markers in documents
- **Configurable Types**: Easy to add new confidential document types

### 🔧 Advanced OCR
- **Multi-mode Processing**: Uses different Tesseract PSM modes for optimal results
- **Image Preprocessing**: Advanced image enhancement for better text extraction
- **Multiple Languages**: Supports English, French, and German text recognition

### 📊 Comprehensive Local Data Extraction
- **Identity Documents**: Extracts names, document numbers, dates, addresses
- **Financial Documents**: Extracts account numbers, balances, dates (safely anonymized)
- **Medical Documents**: Extracts basic administrative info while protecting sensitive details
- **Employment Documents**: Extracts job titles, companies, dates, salaries
- **Educational Documents**: Extracts degrees, institutions, GPAs, student IDs
- **Legal Documents**: Extracts parties, dates, document types
- **Contact Information**: Extracts emails, phone numbers, and addresses
- **Structured Output**: Returns data in the same format as the original processor

## Usage

### Basic Usage

```python
from Services.DocumentProcessor3 import ConfidentialDocumentProcessor
from Common.constants import API_KEY_3

# Initialize the processor
processor = ConfidentialDocumentProcessor(api_key=API_KEY_3)

# Process a resume file
results = processor.process_file("path/to/resume.pdf", min_confidence=0.3)

# Check if privacy was protected
for result in results:
    if result.get('privacy_protected'):
        print("✅ Resume processed locally - privacy protected!")
    else:
        print("⚠️ Document processed with external services")
```

### Advanced Usage

```python
# Process multiple files
resume_files = ["resume1.pdf", "resume2.docx", "resume3.jpg"]

for file_path in resume_files:
    results = processor.process_file(file_path)
    
    for result in results:
        print(f"File: {result['source_file']}")
        print(f"Type: {result['document_type']}")
        print(f"Privacy Protected: {result.get('privacy_protected', False)}")
        
        # Access extracted data
        data = result.get('extracted_data', {}).get('data', {})
        if 'email' in data:
            print(f"Email: {data['email']}")
        if 'name' in data:
            print(f"Name: {data['name']}")
```

## Supported Confidential Document Types

The processor automatically detects and protects these document categories:

### 📋 Employment/HR Documents
- Resumes, CVs, job applications
- Employment contracts, payslips, salary slips
- Performance reviews, employee benefits
- Termination documents, promotion letters
- Work permits, employment verification

### 🆔 Personal Identity Documents
- Passports, national IDs, driver's licenses
- Residence permits, citizenship cards
- Voter IDs, Aadhaar cards, PAN cards
- Social security cards, birth certificates
- Marriage certificates

### 💰 Financial Documents (Personal)
- Bank statements, credit card statements
- Loan documents, tax returns
- Investment statements, insurance policies
- Personal financial statements

### 🏥 Medical Documents
- Medical reports, prescriptions
- Health insurance documents
- Vaccination records, medical certificates
- Patient records, medical history
- Lab reports, diagnostic reports

### ⚖️ Legal Documents (Personal)
- Wills, testaments, power of attorney
- Legal notices, court orders
- Affidavits, personal contracts, deeds

### 🎓 Educational Documents (Personal)
- Transcripts, report cards
- Degree certificates, diplomas
- Academic certificates, student records
- Scholarship documents

### 🔒 General Confidential Content
- Any document marked as "confidential", "private", "restricted"
- Documents containing SSNs, account numbers, personal IDs
- Documents with sensitive personal information

## Configuration

### Adding New Confidential Document Types

The processor uses comprehensive detection logic, but you can add specific types:

### Adding New Confidential Types

To add new confidential document types, modify the `CONFIDENTIAL_DOCUMENT_TYPES` set in `DocumentProcessor3.py`:

```python
CONFIDENTIAL_DOCUMENT_TYPES.add('your_new_confidential_type')
```

## How It Works

### 1. Document Detection
- Analyzes text for resume-specific keywords and patterns
- Checks for common resume sections (experience, education, skills)
- Identifies contact information patterns (email, phone)

### 2. Local Processing Pipeline
```
Input Document → OCR (Tesseract only) → Pattern Matching → Data Extraction → Local Validation → Results
```

### 3. Privacy Safeguards
- **No Network Calls**: Confidential documents never leave your system
- **Local Validation**: Uses pattern matching instead of AI for validation
- **Transparent Logging**: Clearly indicates when privacy protection is active

## Supported File Types

- **PDF**: Multi-page PDF documents
- **DOCX**: Microsoft Word documents with text and images
- **Images**: JPG, PNG, TIFF, BMP formats

## Output Format

The processor returns the same format as the original processor, with additional privacy indicators:

```json
{
  "status": "success",
  "document_type": "resume",
  "confidence": 0.85,
  "privacy_protected": true,
  "processing_method": "confidential_local_only",
  "extracted_data": {
    "data": {
      "name": "John Doe",
      "email": "john.doe@email.com",
      "phone": "555-123-4567",
      "experience": "...",
      "education": "...",
      "skills": "..."
    }
  },
  "verification_result": {
    "is_genuine": true,
    "privacy_protected": true
  }
}
```

## Migration from DocumentProcessor3

The `ConfidentialDocumentProcessor` is a drop-in replacement:

```python
# Old code
from Services.DocumentProcessor3 import DocumentProcessor
processor = DocumentProcessor(api_key)

# New code - just change the class name
from Services.DocumentProcessor3 import ConfidentialDocumentProcessor
processor = ConfidentialDocumentProcessor(api_key)

# All other code remains the same
results = processor.process_file(file_path)
```

## Performance Considerations

- **Speed**: Local processing is typically faster than API calls
- **Accuracy**: OCR-only processing may have slightly lower accuracy than AI-enhanced extraction
- **Resource Usage**: Uses local CPU for OCR processing instead of network bandwidth

## Troubleshooting

### Common Issues

1. **Poor OCR Results**: Ensure images are high quality and well-lit
2. **Missing Data**: Check that the document contains clear, readable text
3. **False Negatives**: Document not detected as confidential - check keyword patterns

### Logging

Enable detailed logging to see processing decisions:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

Look for messages like:
- "Confidential document detected - using OCR-only processing"
- "Document identified as confidential (resume-like) with X matching keywords"

## Security Notes

- **Data Never Leaves System**: Confidential documents are processed entirely locally
- **No API Calls**: No network requests are made for confidential document processing
- **Audit Trail**: All processing decisions are logged for compliance
- **Fallback Safety**: When in doubt, the system defaults to local processing

## Example Files

- `Services/confidential_processor_example.py`: Complete usage example
- See the example file for a working demonstration of the confidential processor
