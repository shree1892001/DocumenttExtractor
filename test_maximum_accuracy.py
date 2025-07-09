#!/usr/bin/env python3
"""
Maximum Accuracy Document Extraction Test Script
Tests the enhanced DocumentProcessor3 with maximum accuracy extraction
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

def test_maximum_accuracy_extraction():
    """Test the maximum accuracy extraction with enhanced field identification"""
    
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
    print("MAXIMUM ACCURACY DOCUMENT EXTRACTION TEST")
    print("Testing enhanced extraction with maximum accuracy and comprehensive field identification")
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
                print(f"   Document Category: {doc_analysis.get('document_category', 'Unknown')}")
                
                # Extracted data
                extracted_data = result.get('extracted_data', {}).get('data', {})
                if extracted_data:
                    print(f"\n   📋 EXTRACTED DATA ({len(extracted_data)} fields):")
                    
                    # Categorize fields for better display
                    personal_fields = []
                    document_fields = []
                    contact_fields = []
                    address_fields = []
                    date_fields = []
                    organizational_fields = []
                    financial_fields = []
                    security_fields = []
                    other_fields = []
                    
                    for key, value in extracted_data.items():
                        key_lower = key.lower()
                        if any(word in key_lower for word in ['name', 'birth', 'gender', 'nationality', 'age', 'blood', 'height', 'weight', 'eye', 'hair']):
                            personal_fields.append((key, value))
                        elif any(word in key_lower for word in ['document', 'number', 'id', 'license', 'passport', 'account', 'issue', 'expiry', 'valid']):
                            document_fields.append((key, value))
                        elif any(word in key_lower for word in ['phone', 'email', 'contact', 'mobile', 'fax', 'website']):
                            contact_fields.append((key, value))
                        elif any(word in key_lower for word in ['address', 'city', 'state', 'country', 'postal', 'zip', 'street']):
                            address_fields.append((key, value))
                        elif any(word in key_lower for word in ['date', 'issue', 'expiry', 'valid', 'birth', 'renewal']):
                            date_fields.append((key, value))
                        elif any(word in key_lower for word in ['company', 'organization', 'department', 'job', 'position', 'employee']):
                            organizational_fields.append((key, value))
                        elif any(word in key_lower for word in ['amount', 'balance', 'salary', 'income', 'fee', 'cost', 'currency']):
                            financial_fields.append((key, value))
                        elif any(word in key_lower for word in ['security', 'signature', 'hologram', 'watermark', 'mrz', 'barcode']):
                            security_fields.append((key, value))
                        else:
                            other_fields.append((key, value))
                    
                    # Display by category
                    if personal_fields:
                        print(f"\n     👤 Personal Information ({len(personal_fields)} fields):")
                        for key, value in personal_fields:
                            print(f"       {key}: {value}")
                    
                    if document_fields:
                        print(f"\n     📄 Document Information ({len(document_fields)} fields):")
                        for key, value in document_fields:
                            print(f"       {key}: {value}")
                    
                    if contact_fields:
                        print(f"\n     📞 Contact Information ({len(contact_fields)} fields):")
                        for key, value in contact_fields:
                            print(f"       {key}: {value}")
                    
                    if address_fields:
                        print(f"\n     🏠 Address Information ({len(address_fields)} fields):")
                        for key, value in address_fields:
                            print(f"       {key}: {value}")
                    
                    if date_fields:
                        print(f"\n     📅 Date Information ({len(date_fields)} fields):")
                        for key, value in date_fields:
                            print(f"       {key}: {value}")
                    
                    if organizational_fields:
                        print(f"\n     🏢 Organizational Information ({len(organizational_fields)} fields):")
                        for key, value in organizational_fields:
                            print(f"       {key}: {value}")
                    
                    if financial_fields:
                        print(f"\n     💰 Financial Information ({len(financial_fields)} fields):")
                        for key, value in financial_fields:
                            print(f"       {key}: {value}")
                    
                    if security_fields:
                        print(f"\n     🔒 Security Features ({len(security_fields)} fields):")
                        for key, value in security_fields:
                            print(f"       {key}: {value}")
                    
                    if other_fields:
                        print(f"\n     📝 Other Information ({len(other_fields)} fields):")
                        for key, value in other_fields:
                            print(f"       {key}: {value}")
                    
                    # Quality analysis
                    generic_count = sum(1 for key in extracted_data.keys() if key.startswith('Text_') or key.startswith('text_'))
                    meaningful_count = len(extracted_data) - generic_count
                    meaningful_ratio = meaningful_count / len(extracted_data) * 100 if len(extracted_data) > 0 else 0
                    
                    print(f"\n     📊 EXTRACTION QUALITY ANALYSIS:")
                    print(f"       Total fields extracted: {len(extracted_data)}")
                    print(f"       Meaningful field names: {meaningful_count} ({meaningful_ratio:.1f}%)")
                    print(f"       Generic field names: {generic_count} ({100-meaningful_ratio:.1f}%)")
                    
                    if meaningful_ratio >= 80:
                        print(f"       ✅ EXCELLENT: High quality field identification")
                    elif meaningful_ratio >= 60:
                        print(f"       ✅ GOOD: Good quality field identification")
                    elif meaningful_ratio >= 40:
                        print(f"       ⚠️  FAIR: Moderate quality field identification")
                    else:
                        print(f"       ❌ POOR: Low quality field identification")
                    
                else:
                    print("   ❌ No extracted data found")
                
                # Verification results
                verification = result.get('verification_results', {})
                if verification:
                    print(f"\n   ✅ Verification:")
                    print(f"     Genuine: {verification.get('is_genuine', 'Unknown')}")
                    print(f"     Confidence: {verification.get('confidence_score', 0.0):.2f}")
                    print(f"     Summary: {verification.get('verification_summary', 'No summary')}")
                    
                    security_features = verification.get('security_features_found', [])
                    if security_features:
                        print(f"     Security Features: {', '.join(security_features)}")
                
                # Processing metadata
                metadata = result.get('processing_metadata', {})
                if metadata:
                    print(f"\n   🔧 Processing Info:")
                    print(f"     Extraction Confidence: {metadata.get('extraction_confidence', 0.0):.2f}")
                    print(f"     OCR Quality: {metadata.get('ocr_quality', 'Unknown')}")
                    print(f"     Notes: {metadata.get('processing_notes', 'No notes')}")
                    
                    missing_info = metadata.get('missing_information', '')
                    if missing_info:
                        print(f"     Missing Information: {missing_info}")
                
                print("\n" + "="*60)
                
        except Exception as e:
            print(f"❌ Error processing {file_path}: {str(e)}")
            logger.error(f"Error processing {file_path}: {str(e)}", exc_info=True)
    
    print("\n" + "="*80)
    print("MAXIMUM ACCURACY EXTRACTION TEST COMPLETED")
    print("="*80)

def test_specific_accuracy_improvements():
    """Test specific accuracy improvements on known problematic files"""
    
    print("\n" + "="*80)
    print("SPECIFIC ACCURACY IMPROVEMENT TEST")
    print("="*80)
    
    processor = DocumentProcessor(API_KEY)
    processor.set_unified_processing(True)
    
    # Test with files that had issues before
    test_files = [
        "testdocs/ikmages/OIP.jpg",
        "testdocs/ikmages/driving_license.jpg"
    ]
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"\n🔍 Testing accuracy improvements on: {test_file}")
            
            try:
                results = processor.process_file(test_file, min_confidence=0.0)
                
                if results:
                    result = results[0]
                    extracted_data = result.get('extracted_data', {}).get('data', {})
                    
                    print(f"\n📋 Accuracy Analysis:")
                    print(f"   Total fields extracted: {len(extracted_data)}")
                    
                    # Analyze field quality
                    meaningful_fields = []
                    generic_fields = []
                    
                    for key, value in extracted_data.items():
                        if key.startswith('Text_') or key.startswith('text_'):
                            generic_fields.append((key, value))
                        else:
                            meaningful_fields.append((key, value))
                    
                    print(f"   Meaningful field names: {len(meaningful_fields)}")
                    print(f"   Generic field names: {len(generic_fields)}")
                    
                    if len(meaningful_fields) > 0:
                        quality_ratio = len(meaningful_fields) / (len(meaningful_fields) + len(generic_fields)) * 100
                        print(f"   Field identification quality: {quality_ratio:.1f}%")
                        
                        if quality_ratio >= 80:
                            print(f"   ✅ EXCELLENT accuracy achieved!")
                        elif quality_ratio >= 60:
                            print(f"   ✅ GOOD accuracy achieved!")
                        else:
                            print(f"   ⚠️  Accuracy needs improvement")
                    
                    # Show sample of meaningful fields
                    if meaningful_fields:
                        print(f"\n📝 Sample Meaningful Fields:")
                        for key, value in list(meaningful_fields)[:10]:
                            print(f"   ✅ {key}: {value}")
                    
                    # Show generic fields if any
                    if generic_fields:
                        print(f"\n⚠️  Generic Fields (needs improvement):")
                        for key, value in generic_fields:
                            print(f"   ❌ {key}: {value}")
                
            except Exception as e:
                print(f"❌ Error in accuracy test: {str(e)}")
        else:
            print(f"⚠️  Test file not found: {test_file}")

if __name__ == "__main__":
    print("🚀 Starting Maximum Accuracy Document Extraction Tests...")
    
    try:
        # Test maximum accuracy extraction
        test_maximum_accuracy_extraction()
        
        # Test specific accuracy improvements
        test_specific_accuracy_improvements()
        
        print("\n✅ All maximum accuracy tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test execution failed: {str(e)}")
        logger.error("Test execution failed", exc_info=True)
        sys.exit(1) 