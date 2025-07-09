#!/usr/bin/env python3
"""
Test script to demonstrate the new generic intelligent extraction system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Services.DocumentProcessor3 import DocumentProcessor

def test_generic_extraction():
    """Test the generic extraction with Korean passport text"""
    
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

    print("Testing Generic Intelligent Extraction System")
    print("=" * 50)
    print(f"Input text length: {len(korean_passport_text)} characters")
    print("\nInput text:")
    print("-" * 30)
    print(korean_passport_text)
    print("-" * 30)
    
    try:
        # Initialize the document processor
        processor = DocumentProcessor(api_key="test_key")
        
        # Test the generic extraction
        print("\nProcessing with generic intelligent extraction...")
        result = processor._extract_data_intelligently(
            korean_passport_text, 
            "korean_passport.jpg", 
            min_confidence=0.1
        )
        
        if result:
            print("\n✅ Extraction successful!")
            print(f"Document type: {result.get('document_type', 'unknown')}")
            print(f"Confidence: {result.get('confidence', 0.0):.2f}")
            print(f"Processing method: {result.get('processing_method', 'unknown')}")
            
            extracted_data = result.get('extracted_data', {}).get('data', {})
            print(f"\n📋 Extracted Data ({len(extracted_data)} fields):")
            print("-" * 40)
            
            for field_name, value in extracted_data.items():
                print(f"{field_name}: {value}")
                
        else:
            print("\n❌ Extraction failed - no result returned")
            
    except Exception as e:
        print(f"\n❌ Error during extraction: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_generic_extraction() 