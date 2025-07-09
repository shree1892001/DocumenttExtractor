#!/usr/bin/env python3
"""
Enhanced Document Extraction Test Script
Tests the improved DocumentProcessor3 with better field identification and cleaner text extraction
"""

import sys
import os
import json
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from Services.DocumentProcessor3 import DocumentProcessor
from Common.constants import API_KEY

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_enhanced_extraction():
    """Test the enhanced extraction with better field identification"""
    
    # Initialize the processor
    processor = DocumentProcessor(API_KEY)
    
    # Enable unified processing
    processor.set_unified_processing(True)
    
    # Test files to process
    test_files = [
        "testdocs/docs/NewMexicoCorp.docx",
        "testdocs/docs/OIP.docx", 
        "testdocs/docs/Specimen_Persona.docx",
        "testdocs/docs/aadhaar_card_realistic.docx",
        "testdocs/docs/driver_license_card.docx",
        "testdocs/pdf/OIP.pdf",
        "testdocs/pdf/NewMexicoCorp.pdf",
        "testdocs/pdf/Specimen_Persona.pdf",
        "testdocs/ikmages/OIP.jpg",
        "testdocs/ikmages/Specimen_Persona.jpg",
        "testdocs/ikmages/driving_license.jpg"
    ]
    
    print("=" * 80)
    print("ENHANCED DOCUMENT EXTRACTION TEST")
    print("Testing improved field identification and cleaner text extraction")
    print("=" * 80)
    
    for file_path in test_files:
        if not os.path.exists(file_path):
            print(f"⚠️  File not found: {file_path}")
            continue
            
        print(f"\n🔍 Processing: {file_path}")
        print("-" * 60)
        
        try:
            # Process the file
            results = processor.process_file(file_path, min_confidence=0.0)
            
            if not results:
                print("❌ No results returned")
                continue
                
            # Display results
            for i, result in enumerate(results):
                print(f"\n📄 Result {i+1}:")
                
                # Document analysis
                doc_analysis = result.get('document_analysis', {})
                print(f"   Document Type: {doc_analysis.get('document_type', 'Unknown')}")
                print(f"   Confidence: {doc_analysis.get('confidence_score', 0.0):.2f}")
                print(f"   Processing Method: {doc_analysis.get('processing_method', 'Unknown')}")
                
                # Extracted data
                extracted_data = result.get('extracted_data', {}).get('data', {})
                if extracted_data:
                    print(f"\n   📋 EXTRACTED DATA ({len(extracted_data)} fields):")
                    
                    # Sort fields by type for better display
                    personal_fields = []
                    document_fields = []
                    contact_fields = []
                    address_fields = []
                    date_fields = []
                    other_fields = []
                    
                    for key, value in extracted_data.items():
                        key_lower = key.lower()
                        if any(word in key_lower for word in ['name', 'birth', 'gender', 'nationality', 'age']):
                            personal_fields.append((key, value))
                        elif any(word in key_lower for word in ['document', 'number', 'id', 'license', 'passport', 'account']):
                            document_fields.append((key, value))
                        elif any(word in key_lower for word in ['phone', 'email', 'contact', 'mobile']):
                            contact_fields.append((key, value))
                        elif any(word in key_lower for word in ['address', 'city', 'state', 'country', 'postal', 'zip']):
                            address_fields.append((key, value))
                        elif any(word in key_lower for word in ['date', 'issue', 'expiry', 'valid']):
                            date_fields.append((key, value))
                        else:
                            other_fields.append((key, value))
                    
                    # Display by category
                    if personal_fields:
                        print(f"\n     👤 Personal Information:")
                        for key, value in personal_fields:
                            print(f"       {key}: {value}")
                    
                    if document_fields:
                        print(f"\n     📄 Document Information:")
                        for key, value in document_fields:
                            print(f"       {key}: {value}")
                    
                    if contact_fields:
                        print(f"\n     📞 Contact Information:")
                        for key, value in contact_fields:
                            print(f"       {key}: {value}")
                    
                    if address_fields:
                        print(f"\n     🏠 Address Information:")
                        for key, value in address_fields:
                            print(f"       {key}: {value}")
                    
                    if date_fields:
                        print(f"\n     📅 Date Information:")
                        for key, value in date_fields:
                            print(f"       {key}: {value}")
                    
                    if other_fields:
                        print(f"\n     📝 Other Information:")
                        for key, value in other_fields:
                            print(f"       {key}: {value}")
                    
                    # Check for generic field names
                    generic_count = sum(1 for key in extracted_data.keys() if key.startswith('Text_') or key.startswith('text_'))
                    if generic_count > 0:
                        print(f"\n     ⚠️  WARNING: Found {generic_count} generic field names")
                        for key, value in extracted_data.items():
                            if key.startswith('Text_') or key.startswith('text_'):
                                print(f"       {key}: {value}")
                else:
                    print("   ❌ No extracted data found")
                
                # Verification results
                verification = result.get('verification_results', {})
                if verification:
                    print(f"\n   ✅ Verification:")
                    print(f"     Genuine: {verification.get('is_genuine', 'Unknown')}")
                    print(f"     Confidence: {verification.get('confidence_score', 0.0):.2f}")
                    print(f"     Summary: {verification.get('verification_summary', 'No summary')}")
                
                # Processing metadata
                metadata = result.get('processing_metadata', {})
                if metadata:
                    print(f"\n   🔧 Processing Info:")
                    print(f"     Extraction Confidence: {metadata.get('extraction_confidence', 0.0):.2f}")
                    print(f"     Notes: {metadata.get('processing_notes', 'No notes')}")
                
                print("\n" + "="*60)
                
        except Exception as e:
            print(f"❌ Error processing {file_path}: {str(e)}")
            logger.error(f"Error processing {file_path}: {str(e)}", exc_info=True)
    
    print("\n" + "="*80)
    print("ENHANCED EXTRACTION TEST COMPLETED")
    print("="*80)

def test_text_quality_improvement():
    """Test specific text quality improvements"""
    
    print("\n" + "="*80)
    print("TEXT QUALITY IMPROVEMENT TEST")
    print("="*80)
    
    processor = DocumentProcessor(API_KEY)
    processor.set_unified_processing(True)
    
    # Test with a specific file that had OCR issues
    test_file = "testdocs/ikmages/OIP.jpg"
    
    if os.path.exists(test_file):
        print(f"\n🔍 Testing text quality improvement on: {test_file}")
        
        try:
            results = processor.process_file(test_file, min_confidence=0.0)
            
            if results:
                result = results[0]
                extracted_data = result.get('extracted_data', {}).get('data', {})
                
                print(f"\n📋 Text Quality Analysis:")
                print(f"   Total fields extracted: {len(extracted_data)}")
                
                # Analyze text quality
                clean_text_count = 0
                unclear_text_count = 0
                
                for key, value in extracted_data.items():
                    if isinstance(value, str):
                        # Check for common OCR artifacts
                        if any(char in value for char in ['@', '#', '$', '%', '&', '*', '(', ')', '_', '+', '=']):
                            unclear_text_count += 1
                        elif len(value.strip()) > 0:
                            clean_text_count += 1
                
                print(f"   Clean text fields: {clean_text_count}")
                print(f"   Unclear text fields: {unclear_text_count}")
                print(f"   Text quality ratio: {clean_text_count/(clean_text_count+unclear_text_count)*100:.1f}%")
                
                # Show sample of extracted data
                print(f"\n📝 Sample Extracted Data:")
                for i, (key, value) in enumerate(list(extracted_data.items())[:10]):
                    print(f"   {key}: {value}")
                
        except Exception as e:
            print(f"❌ Error in text quality test: {str(e)}")
    else:
        print(f"⚠️  Test file not found: {test_file}")

if __name__ == "__main__":
    print("🚀 Starting Enhanced Document Extraction Tests...")
    
    try:
        # Test enhanced extraction
        test_enhanced_extraction()
        
        # Test text quality improvements
        test_text_quality_improvement()
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test execution failed: {str(e)}")
        logger.error("Test execution failed", exc_info=True)
        sys.exit(1) 