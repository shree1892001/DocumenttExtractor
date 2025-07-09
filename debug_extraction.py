#!/usr/bin/env python3
"""
Debug script to test text extraction and processing step by step
"""

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Services.DocumentProcessor3 import DocumentProcessor

def debug_extraction():
    """Debug the extraction process step by step"""
    
    print("🔍 DEBUGGING DOCUMENT EXTRACTION PROCESS")
    print("=" * 60)
    
    # Initialize processor
    processor = DocumentProcessor(api_key="your_api_key_here")
    
    # Test with a known document
    test_file = "testdocs/docs/NewMexicoCorp.docx"
    
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return
    
    print(f"📄 Testing with: {test_file}")
    print()
    
    # Step 1: Test text extraction
    print("Step 1: Testing text extraction...")
    try:
        extracted_text = processor._extract_text_from_file(test_file)
        print(f"✅ Text extraction successful")
        print(f"   Text length: {len(extracted_text)} characters")
        print(f"   First 200 chars: {extracted_text[:200]}...")
        print()
        
        if not extracted_text.strip():
            print("❌ No text content extracted!")
            return
            
    except Exception as e:
        print(f"❌ Text extraction failed: {str(e)}")
        return
    
    # Step 2: Test dynamic content extraction
    print("Step 2: Testing dynamic content extraction...")
    try:
        extracted_data = processor._extract_all_content_dynamically(extracted_text)
        print(f"✅ Dynamic content extraction successful")
        print(f"   Content elements extracted: {len(extracted_data)}")
        
        if extracted_data:
            print("   Sample elements:")
            for i, (key, value) in enumerate(list(extracted_data.items())[:3]):
                print(f"     {i+1}. {key}")
                if isinstance(value, dict):
                    print(f"        Type: {value.get('content_type', 'Unknown')}")
                    print(f"        Confidence: {value.get('confidence', 'N/A')}")
                    print(f"        Length: {value.get('length', 'N/A')} chars")
                    print(f"        Value: {str(value.get('value', ''))[:50]}...")
                else:
                    print(f"        Value: {str(value)[:50]}...")
        else:
            print("   ❌ No content elements extracted!")
            
        print()
        
    except Exception as e:
        print(f"❌ Dynamic content extraction failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 3: Test text splitting
    print("Step 3: Testing text splitting...")
    try:
        chunks = processor._split_text_dynamically(extracted_text)
        print(f"✅ Text splitting successful")
        print(f"   Chunks created: {len(chunks)}")
        
        if chunks:
            print("   Sample chunks:")
            for i, chunk in enumerate(chunks[:5]):
                print(f"     {i+1}. Length: {len(chunk)} chars")
                print(f"        Content: {chunk[:50]}...")
        else:
            print("   ❌ No chunks created!")
            
        print()
        
    except Exception as e:
        print(f"❌ Text splitting failed: {str(e)}")
        return
    
    # Step 4: Test chunk analysis
    print("Step 4: Testing chunk analysis...")
    try:
        if chunks:
            sample_chunk = chunks[0]
            analysis = processor._analyze_chunk_dynamically(sample_chunk, 0)
            
            if analysis:
                print(f"✅ Chunk analysis successful")
                print(f"   Content type: {analysis.get('type', 'Unknown')}")
                print(f"   Confidence: {analysis.get('confidence', 'N/A')}")
                print(f"   Characteristics: {list(analysis.get('characteristics', {}).keys())}")
            else:
                print("   ❌ Chunk analysis returned None")
        else:
            print("   ⚠️  No chunks to analyze")
            
        print()
        
    except Exception as e:
        print(f"❌ Chunk analysis failed: {str(e)}")
        return
    
    # Step 5: Test full processing
    print("Step 5: Testing full processing...")
    try:
        result = processor.process_file(test_file)
        
        if result and result[0].get("status") == "success":
            print(f"✅ Full processing successful")
            extracted_data = result[0].get("extracted_data", {}).get("data", {})
            print(f"   Final content elements: {len(extracted_data)}")
            print(f"   Confidence: {result[0].get('confidence', 'N/A')}")
            print(f"   Document type: {result[0].get('document_type', 'N/A')}")
        else:
            print(f"❌ Full processing failed")
            if result:
                print(f"   Status: {result[0].get('status', 'Unknown')}")
                print(f"   Error: {result[0].get('extracted_data', {}).get('additional_info', 'No error info')}")
            
    except Exception as e:
        print(f"❌ Full processing failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_extraction() 