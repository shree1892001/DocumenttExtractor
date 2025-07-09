#!/usr/bin/env python3
"""
Test script to demonstrate DocumentProcessor3 with field-preserving extraction
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Services.DocumentProcessor3 import DocumentProcessor
from Common.constants import API_KEY_1

def test_documentprocessor3():
    """Test DocumentProcessor3 with Korean passport text"""
    
    # Korean passport text from the user's example
    korean_passport_text = """tH Ea yal 3 i REPUBLIC OF KOREA

Be) Iy0e
Oj a PASSPORT — py

Al Surin

O16 Given sae

35 Nakanalty
REPUBLIC OF KOREA
ASW aio of brn

02 JUL 1985
Alui'sos

F

WR WhOme of ese

15 APR 2014
7121429) Date of expy

15 APR 2024

'OF ea county
KOR

Of Asia Passport We

M70689098

he,
&
418 m8 0/ Person No,

2154710

Yasar Abort
UNISTRY- OF FOREIGN FAS
wae

Olea

PMKORLEE<<SUY EONK<<<<<< <<< <<< KKK KKK KKK KKK KKK
M706890985K0R8507022F24041522154710V17627884"""

    print("Testing DocumentProcessor3 with Field-Preserving Extraction")
    print("=" * 60)
    print(f"Input text length: {len(korean_passport_text)} characters")
    print("\nInput text:")
    print("-" * 40)
    print(korean_passport_text)
    print("-" * 40)
    
    try:
        # Initialize DocumentProcessor3 with API_KEY_1 to avoid rate limits
        print(f"\n🔑 Using API Key: {API_KEY_1[:10]}...")
        processor = DocumentProcessor(api_key=API_KEY_1)
        
        # Test the field-preserving extraction directly
        print("\n🔄 Testing field-preserving intelligent extraction...")
        result = processor._extract_data_intelligently(
            korean_passport_text, 
            "korean_passport.jpg", 
            min_confidence=0.1
        )
        
        if result:
            print("\n✅ Field-preserving extraction successful!")
            print(f"📄 Document type: {result.get('document_type', 'unknown')}")
            print(f"🎯 Confidence: {result.get('confidence', 0.0):.2f}")
            print(f"🔧 Processing method: {result.get('processing_method', 'unknown')}")
            
            extracted_data = result.get('extracted_data', {}).get('data', {})
            print(f"\n📋 Extracted Data with Original Field Names ({len(extracted_data)} fields):")
            print("-" * 60)
            
            for field_name, value in extracted_data.items():
                print(f"  📝 {field_name}: {value}")
                
            # Test the full processing pipeline
            print("\n🔄 Testing full processing pipeline...")
            full_result = processor._process_text_content(
                korean_passport_text, 
                "korean_passport.jpg", 
                min_confidence=0.1
            )
            
            if full_result:
                print("\n✅ Full processing successful!")
                print(f"📄 Document type: {full_result.get('document_type', 'unknown')}")
                print(f"🎯 Confidence: {full_result.get('confidence', 0.0):.2f}")
                print(f"🔧 Processing method: {full_result.get('processing_method', 'unknown')}")
                print(f"📊 Status: {full_result.get('status', 'unknown')}")
                
                full_extracted_data = full_result.get('extracted_data', {}).get('data', {})
                print(f"\n📋 Full Pipeline Extracted Data ({len(full_extracted_data)} fields):")
                print("-" * 60)
                
                for field_name, value in full_extracted_data.items():
                    print(f"  📝 {field_name}: {value}")
            else:
                print("\n❌ Full processing failed - no result returned")
                
        else:
            print("\n❌ Field-preserving extraction failed - no result returned")
            
    except Exception as e:
        print(f"\n❌ Error during processing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_documentprocessor3() 