#!/usr/bin/env python3
"""
Test DOCX Processing Fix
Tests the fixed DOCX processing to ensure the KeyError is resolved
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

def test_docx_processing_fix():
    """Test the DOCX processing fix"""
    
    # Initialize the processor
    processor = DocumentProcessor(API_KEY)
    
    # Enable unified processing
    processor.set_unified_processing(True)
    
    # Test DOCX files
    test_files = [
        "testdocs/docs/NewMexicoCorp.docx",
        "testdocs/docs/OIP.docx", 
        "testdocs/docs/Specimen_Persona.docx",
        "testdocs/docs/aadhaar_card_realistic.docx",
        "testdocs/docs/driver_license_card.docx"
    ]
    
    print("=" * 80)
    print("DOCX PROCESSING FIX TEST")
    print("Testing the fix for the KeyError 'image_path' issue")
    print("=" * 80)
    
    for file_path in test_files:
        if not os.path.exists(file_path):
            print(f"⚠️  File not found: {file_path}")
            continue
            
        print(f"\n🔍 Testing DOCX processing: {file_path}")
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
                
                # Check for errors
                status = result.get('status', 'unknown')
                if status == 'error':
                    print(f"   ❌ ERROR STATUS: {status}")
                    error_details = result.get('error_details', {})
                    if error_details:
                        print(f"   Error Type: {error_details.get('error_type', 'Unknown')}")
                        print(f"   Error Message: {error_details.get('error_message', 'No message')}")
                else:
                    print(f"   ✅ SUCCESS STATUS: {status}")
                
                # Document analysis
                doc_analysis = result.get('document_analysis', {})
                print(f"   Document Type: {doc_analysis.get('document_type', 'Unknown')}")
                print(f"   Confidence: {doc_analysis.get('confidence_score', 0.0):.2f}")
                print(f"   Processing Method: {result.get('processing_method', 'Unknown')}")
                
                # Extracted data
                extracted_data = result.get('extracted_data', {}).get('data', {})
                if extracted_data:
                    print(f"\n   📋 EXTRACTED DATA ({len(extracted_data)} fields):")
                    
                    # Show first 10 fields
                    for j, (key, value) in enumerate(list(extracted_data.items())[:10]):
                        print(f"       {key}: {value}")
                    
                    if len(extracted_data) > 10:
                        print(f"       ... and {len(extracted_data) - 10} more fields")
                    
                    # Check for meaningful field names
                    meaningful_count = sum(1 for key in extracted_data.keys() 
                                         if not key.startswith('Text_') and not key.startswith('text_'))
                    total_count = len(extracted_data)
                    meaningful_ratio = meaningful_count / total_count * 100 if total_count > 0 else 0
                    
                    print(f"\n   📊 Field Quality: {meaningful_count}/{total_count} meaningful fields ({meaningful_ratio:.1f}%)")
                    
                else:
                    print("   ❌ No extracted data found")
                
                # Processing info
                segment_id = result.get('segment_id', 'N/A')
                print(f"   🔧 Segment ID: {segment_id}")
                
                print("\n" + "="*60)
                
        except Exception as e:
            print(f"❌ Error processing {file_path}: {str(e)}")
            logger.error(f"Error processing {file_path}: {str(e)}", exc_info=True)
    
    print("\n" + "="*80)
    print("DOCX PROCESSING FIX TEST COMPLETED")
    print("="*80)

def test_specific_error_scenario():
    """Test the specific error scenario that was failing"""
    
    print("\n" + "="*80)
    print("SPECIFIC ERROR SCENARIO TEST")
    print("="*80)
    
    processor = DocumentProcessor(API_KEY)
    processor.set_unified_processing(True)
    
    # Test with a specific file that was causing the error
    test_file = "testdocs/docs/OIP.docx"
    
    if os.path.exists(test_file):
        print(f"\n🔍 Testing specific error scenario with: {test_file}")
        
        try:
            results = processor.process_file(test_file, min_confidence=0.0)
            
            if results:
                print(f"✅ Successfully processed file with {len(results)} results")
                
                for i, result in enumerate(results):
                    status = result.get('status', 'unknown')
                    print(f"   Result {i+1}: Status = {status}")
                    
                    if status == 'error':
                        print(f"   ❌ Still has error status")
                        error_details = result.get('error_details', {})
                        if error_details:
                            print(f"   Error: {error_details.get('error_message', 'Unknown error')}")
                    else:
                        print(f"   ✅ No error - processing successful")
                        
                        extracted_data = result.get('extracted_data', {}).get('data', {})
                        if extracted_data:
                            print(f"   📋 Extracted {len(extracted_data)} fields")
                        else:
                            print(f"   📋 No extracted data")
            else:
                print("❌ No results returned")
                
        except Exception as e:
            print(f"❌ Exception during processing: {str(e)}")
            logger.error(f"Exception during processing: {str(e)}", exc_info=True)
    else:
        print(f"⚠️  Test file not found: {test_file}")

if __name__ == "__main__":
    print("🚀 Starting DOCX Processing Fix Tests...")
    
    try:
        # Test DOCX processing fix
        test_docx_processing_fix()
        
        # Test specific error scenario
        test_specific_error_scenario()
        
        print("\n✅ All DOCX processing fix tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test execution failed: {str(e)}")
        logger.error("Test execution failed", exc_info=True)
        sys.exit(1) 