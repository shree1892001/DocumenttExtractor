# Universal Data Extraction System

## Overview

The Universal Data Extraction System is a **completely general** document processing solution that extracts **ALL** data from **ANY** document type without limitations. Unlike traditional document processors that focus on specific document types, this system works universally across all document formats and extracts every piece of visible information.

## Key Features

### 🌍 **Universal Compatibility**
- Works with **ANY** document type (no restrictions)
- No document-specific templates or rules required
- Handles unknown or mixed document formats
- Processes any text content regardless of structure

### 🔍 **Complete Data Extraction**
- Extracts **EVERY** piece of information visible in the document
- No data is filtered out or ignored
- Preserves all original formatting and values
- Handles unclear, partial, or incomplete information

### 🎯 **General Purpose Approach**
- No document type assumptions
- No field limitations or restrictions
- Extracts whatever is present in the document
- Adapts to any document structure automatically

### 📊 **Comprehensive Analysis**
- Pattern-based extraction for additional data discovery
- Text analysis and insights
- Complete data flattening and organization
- Advanced search capabilities across all extracted data

## Architecture

### Core Components

1. **UniversalDataExtractor** (`Services/UniversalDataExtractor.py`)
   - Main universal extraction engine
   - Uses UnifiedDocumentProcessor for AI-powered extraction
   - Implements pattern-based data discovery
   - Provides comprehensive data analysis

2. **UniversalDataController** (`Controllers/UniversalDataController.py`)
   - REST API endpoints for universal extraction
   - File upload and text processing endpoints
   - Search and summary functionality
   - Error handling and validation

3. **UnifiedDocumentProcessor** (`Services/UnifiedDocumentProcessor.py`)
   - AI-powered document processing using universal prompts
   - Handles all document types without discrimination
   - Provides consistent, high-quality extraction

## How It Works

### 1. **Universal Processing**
The system processes any document without making assumptions about its type or structure. It treats all documents equally and extracts everything it can find.

### 2. **Multi-Layer Extraction**
- **AI Extraction**: Uses advanced AI to understand and extract structured data
- **Pattern Matching**: Applies comprehensive pattern recognition for dates, numbers, emails, names, etc.
- **Text Analysis**: Extracts key-value pairs and visible data from text lines
- **Code Recognition**: Identifies codes, identifiers, and technical data

### 3. **Complete Data Flattening**
All extracted data is flattened into simple key-value pairs, making it easy to search, analyze, and use.

### 4. **Comprehensive Analysis**
The system provides detailed analysis of extracted data including field types, data distribution, and text insights.

## Supported Data Types

The system extracts **ANY** type of data found in documents:

### **Personal Information**
- Names (first, last, full, middle)
- Contact details (phone, email, address)
- Personal identifiers and relationships
- Emergency contacts and beneficiaries

### **Document Information**
- Document numbers, IDs, references
- Serial numbers, codes, identifiers
- Registration numbers, permits, licenses
- Account numbers, case numbers

### **Temporal Information**
- Dates (multiple formats)
- Times, durations, periods
- Expiry dates, issue dates
- Birth dates, employment dates

### **Financial Information**
- Amounts, balances, totals
- Currency values, percentages
- Payment terms, rates
- Financial calculations

### **Technical Information**
- File numbers, version numbers
- Barcodes, QR codes, serial numbers
- Technical specifications
- System identifiers

### **Organizational Information**
- Company names, departments
- Titles, positions, roles
- Organizational structures
- Institutional information

### **And Much More**
- Any other information visible in the document
- Unclassified or miscellaneous data
- Custom fields and special cases
- Handwritten notes, annotations

## API Endpoints

### File Processing
```
POST /api/v1/universal-extraction
```
Upload ANY document file for universal data extraction.

### Text Processing
```
POST /api/v1/universal-extraction/text
```
Process ANY text content directly for universal data extraction.

### Search Functionality
```
POST /api/v1/universal-extraction/search
```
Search through ALL extracted data for specific fields or values.

### Summary Information
```
GET /api/v1/universal-extraction/summary
```
Get a summary of universal extraction results.

### Service Information
```
GET /api/v1/universal-extraction/info
```
Get information about the universal data extractor.

## Usage Examples

### Python Usage

```python
from Services.UniversalDataExtractor import UniversalDataExtractor
from Common.constants import API_KEY

# Initialize universal extractor
extractor = UniversalDataExtractor(api_key=API_KEY)

# Extract ALL data from ANY document
result = extractor.extract_all_data(
    text="Your document text here... (any document type)",
    source_file="document.txt"
)

# Get summary
summary = extractor.get_data_summary(result)
print(f"Document Type: {summary['document_type']}")
print(f"Total Fields: {summary['total_fields_extracted']}")

# Search for specific data
search_results = extractor.search_data(result, "phone")
print(f"Found {search_results['total_matches']} phone-related fields")

# Access all extracted data
all_data = result['all_extracted_data']
for field, value in all_data.items():
    print(f"{field}: {value}")
```

### API Usage

```bash
# Upload ANY document for universal extraction
curl -X POST "http://localhost:9500/api/v1/universal-extraction" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@any_document.pdf"

# Process ANY text directly
curl -X POST "http://localhost:9500/api/v1/universal-extraction/text" \
  -H "Content-Type: application/json" \
  -d '{"text": "Any document text here..."}'

# Search through ALL extracted data
curl -X POST "http://localhost:9500/api/v1/universal-extraction/search" \
  -H "Content-Type: application/json" \
  -d '{"extraction_result": {...}, "search_term": "email"}'
```

## Response Format

### Success Response
```json
{
  "status": "success",
  "source_file": "any_document.pdf",
  "document_analysis": {
    "document_type": "unknown",
    "confidence_score": 0.95,
    "processing_method": "universal_extraction",
    "key_indicators": []
  },
  "all_extracted_data": {
    "name_1": "John Smith",
    "email_1": "john.smith@email.com",
    "phone_1": "(555) 123-4567",
    "date_1": "2024-01-15",
    "amount_1": "1500.00",
    "document_number_1": "DOC-2024-001",
    "address_1": "123 Main Street",
    "company_1": "ABC Corporation",
    "title_1": "Software Engineer",
    "code_1": "ABC12345",
    "heading_1": "INVOICE",
    "line_1_invoice_number": "INV-2024-001",
    "line_2_date": "2024-01-15",
    "line_3_total": "$1,500.00"
  },
  "raw_extracted_data": {
    // Original AI extraction results
  },
  "original_text": "Complete original document text...",
  "verification_results": {
    "is_genuine": true,
    "confidence_score": 0.95,
    "verification_summary": "Document processed",
    "security_features_found": [],
    "warnings": []
  },
  "processing_metadata": {
    "extraction_confidence": 0.95,
    "processing_notes": "Universal extraction - all data extracted",
    "unified_processing": true,
    "prompt_version": "unified_v1",
    "total_fields_extracted": 15,
    "extraction_method": "universal_comprehensive"
  },
  "data_analysis": {
    "total_fields": 15,
    "field_types": {
      "name": 2,
      "email": 1,
      "phone": 1,
      "date": 3,
      "amount": 2,
      "text": 6
    },
    "text_analysis": {
      "total_characters": 2500,
      "total_words": 450,
      "total_lines": 25,
      "estimated_pages": 1
    }
  },
  "search_index": {
    "all_fields": ["name_1", "email_1", "phone_1", ...],
    "all_values": ["John Smith", "john.smith@email.com", ...],
    "field_value_pairs": {...},
    "searchable_text": "name_1: John Smith email_1: john.smith@email.com ..."
  }
}
```

## Pattern Recognition

The system uses advanced pattern recognition to extract additional data:

### **Date Patterns**
- MM/DD/YYYY, DD/MM/YYYY, YYYY-MM-DD
- Month names (January 15, 2024)
- Various date formats and separators

### **Number Patterns**
- Phone numbers (multiple formats)
- Document numbers and IDs
- Serial numbers and codes
- Account numbers and references

### **Contact Patterns**
- Email addresses
- Phone numbers
- Physical addresses
- Social media handles

### **Financial Patterns**
- Currency amounts
- Percentages and rates
- Financial calculations
- Payment terms

### **Name Patterns**
- Full names (first, middle, last)
- Company names
- Organization names
- Product names

## Testing

Run the universal test suite:

```bash
python test_universal_extraction.py
```

This will test the system with various document types:
- Driver License
- Invoice
- Resume
- Medical Report
- Legal Document
- Any real documents in the testdocs folder

## Integration

### With Existing System
The Universal Data Extraction System integrates seamlessly with the existing document processing infrastructure:

- Uses the same API key and configuration
- Compatible with existing file upload mechanisms
- Provides universal data extraction capabilities
- Maintains backward compatibility

### Customization
The system is highly customizable:

- Add new pattern recognition rules
- Modify data cleaning and normalization
- Extend search capabilities
- Customize output format and analysis

## Performance

### Optimization Features
- Efficient pattern matching algorithms
- Optimized data flattening
- Minimal memory footprint
- Fast processing times

### Scalability
- Handles documents of any size
- Processes any document type
- Supports concurrent requests
- Efficient resource utilization

## Error Handling

The system provides comprehensive error handling:

- Graceful degradation on processing errors
- Detailed error messages and logging
- Fallback processing mechanisms
- Validation and verification checks

## Security

- Secure API key handling
- Input validation and sanitization
- Error message sanitization
- Secure file processing

## Use Cases

### **General Document Processing**
- Process any document without knowing its type
- Extract all available information
- Handle mixed document formats
- Process unknown document structures

### **Data Mining and Discovery**
- Discover hidden information in documents
- Extract patterns and relationships
- Analyze document content comprehensively
- Find specific data across multiple documents

### **Content Indexing**
- Create searchable indexes of document content
- Extract all searchable terms and phrases
- Build comprehensive document databases
- Enable full-text search across documents

### **Document Analysis**
- Analyze document structure and content
- Extract metadata and insights
- Compare documents across different types
- Generate comprehensive document reports

### **Compliance and Auditing**
- Extract all relevant information for compliance
- Create comprehensive audit trails
- Process documents for regulatory requirements
- Ensure no data is missed in processing

## Future Enhancements

Planned improvements include:

- Machine learning-based pattern recognition
- Advanced data validation rules
- Real-time processing capabilities
- Enhanced search algorithms
- Multi-language support
- Image-based document processing
- Handwriting recognition
- Document comparison tools

## Support

For issues or questions:

1. Check the test results and logs
2. Review the API documentation
3. Examine the extraction results
4. Contact the development team

## License

This system is part of the Document Extractor project and follows the same licensing terms.

## Summary

The Universal Data Extraction System is the ultimate solution for extracting **ALL** data from **ANY** document type. It provides:

- ✅ **Universal compatibility** with any document type
- ✅ **Complete data extraction** without limitations
- ✅ **General purpose approach** with no assumptions
- ✅ **Advanced pattern recognition** for additional data discovery
- ✅ **Comprehensive analysis** and search capabilities
- ✅ **Easy integration** with existing systems
- ✅ **Scalable performance** for any workload

This system ensures that **no data is ever missed** during document processing, regardless of the document type or structure. 