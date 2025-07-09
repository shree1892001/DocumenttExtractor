#!/usr/bin/env python3
"""
Simple Document Extraction Test Script
Tests the improved DocumentProcessor3 with better field identification
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

def test_simple_extraction():
    """Test the simple extraction with better field identification"""
    
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
    print("SIMPLE DOCUMENT EXTRACTION TEST")
    print("Testing improved field identification without enhancement methods")
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
                    
                    # Check for meaningful vs generic field names
                    meaningful_fields = []
                    generic_fields = []
                    
                    for key, value in extracted_data.items():
                        if key.startswith('Text_') or key.startswith('text_'):
                            generic_fields.append((key, value))
                        else:
                            meaningful_fields.append((key, value))
                    
                    # Display meaningful fields first
                    if meaningful_fields:
                        print(f"\n     ✅ MEANINGFUL FIELDS ({len(meaningful_fields)}):")
                        for key, value in meaningful_fields:
                            print(f"       {key}: {value}")
                    
                    # Display generic fields if any
                    if generic_fields:
                        print(f"\n     ⚠️  GENERIC FIELDS ({len(generic_fields)}):")
                        for key, value in generic_fields:
                            print(f"       {key}: {value}")
                    
                    # Summary
                    total_fields = len(extracted_data)
                    meaningful_ratio = len(meaningful_fields) / total_fields * 100 if total_fields > 0 else 0
                    print(f"\n     📊 SUMMARY:")
                    print(f"       Total fields: {total_fields}")
                    print(f"       Meaningful fields: {len(meaningful_fields)} ({meaningful_ratio:.1f}%)")
                    print(f"       Generic fields: {len(generic_fields)} ({100-meaningful_ratio:.1f}%)")
                    
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
    print("SIMPLE EXTRACTION TEST COMPLETED")
    print("="*80)

def test_specific_file():
    """Test a specific file to see the field identification improvements"""
    
    print("\n" + "="*80)
    print("SPECIFIC FILE TEST")
    print("="*80)
    
    processor = DocumentProcessor(API_KEY)
    processor.set_unified_processing(True)
    
    # Test with a specific file
    test_file = "testdocs/ikmages/OIP.jpg"
    
    if os.path.exists(test_file):
        print(f"\n🔍 Testing specific file: {test_file}")
        
        try:
            results = processor.process_file(test_file, min_confidence=0.0)
            
            if results:
                result = results[0]
                extracted_data = result.get('extracted_data', {}).get('data', {})
                
                print(f"\n📋 Field Identification Analysis:")
                print(f"   Total fields extracted: {len(extracted_data)}")
                
                # Analyze field quality
                meaningful_count = 0
                generic_count = 0
                
                for key, value in extracted_data.items():
                    if key.startswith('Text_') or key.startswith('text_'):
                        generic_count += 1
                    else:
                        meaningful_count += 1
                
                print(f"   Meaningful field names: {meaningful_count}")
                print(f"   Generic field names: {generic_count}")
                
                if meaningful_count > 0:
                    quality_ratio = meaningful_count / (meaningful_count + generic_count) * 100
                    print(f"   Field identification quality: {quality_ratio:.1f}%")
                
                # Show all extracted data
                print(f"\n📝 All Extracted Data:")
                for key, value in extracted_data.items():
                    field_type = "✅ MEANINGFUL" if not key.startswith('Text_') else "⚠️  GENERIC"
                    print(f"   {field_type} - {key}: {value}")
                
        except Exception as e:
            print(f"❌ Error in specific file test: {str(e)}")
    else:
        print(f"⚠️  Test file not found: {test_file}")

if __name__ == "__main__":
    print("🚀 Starting Simple Document Extraction Tests...")
    
    try:
        # Test simple extraction
        test_simple_extraction()
        
        # Test specific file
        test_specific_file()
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test execution failed: {str(e)}")
        logger.error("Test execution failed", exc_info=True)
        sys.exit(1) 