"""
Debug script to test unified processing and see why data extraction is failing.
"""

import os
import sys
import json
import requests

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Services.DocumentProcessor3 import DocumentProcessor
from Common.constants import API_KEY, API_HOST, API_PORT


def test_direct_processing():
    """Test DocumentProcessor3 directly"""
    print("🔍 Testing DocumentProcessor3 directly...")
    
    try:
        processor = DocumentProcessor(api_key=API_KEY)
        
        # Test with sample resume text (similar to what was processed)
        test_text = """
        YOGI PATEL
        UI/UX Designer
        
        Email: yogi.patel@email.com
        Phone: +91 9876543210
        Location: Mumbai, India
        
        EXPERIENCE:
        Senior UI/UX Designer at TechCorp (2020-2023)
        - Designed user interfaces for mobile applications
        - Conducted user research and usability testing
        - Collaborated with development teams
        
        UI Designer at StartupXYZ (2018-2020)
        - Created wireframes and prototypes
        - Designed responsive web interfaces
        
        EDUCATION:
        Bachelor of Design, Mumbai University (2014-2018)
        
        SKILLS:
        Figma, Adobe XD, Sketch, Photoshop, HTML/CSS
        """
        
        print(f"   Processing text ({len(test_text)} characters)...")
        
        # Test text processing directly
        result = processor._process_text_content(test_text, "resume.txt", 0.0)
        
        if result:
            print(f"   ✅ Processing successful")
            print(f"   Document Type: {result.get('document_type', 'unknown')}")
            print(f"   Status: {result.get('status', 'unknown')}")
            print(f"   Confidence: {result.get('confidence', 0.0):.2f}")
            
            extracted_data = result.get('extracted_data', {}).get('data', {})
            print(f"   Extracted Data Keys: {list(extracted_data.keys())}")
            
            if extracted_data:
                print(f"   Sample Extracted Data:")
                for key, value in list(extracted_data.items())[:5]:  # Show first 5 items
                    print(f"     {key}: {value}")
            else:
                print(f"   ❌ No extracted data found")
                
                # Check the full result structure
                print(f"   Full result keys: {list(result.keys())}")
                print(f"   Extracted data structure: {result.get('extracted_data', {})}")
            
            return result
        else:
            print(f"   ❌ Processing returned None")
            return None
        
    except Exception as e:
        print(f"   ❌ Error in direct processing: {e}")
        return None


def test_api_debug_endpoint():
    """Test the debug API endpoint"""
    print("\n🔍 Testing API debug endpoint...")
    
    base_url = f"http://{API_HOST}:{API_PORT}"
    
    test_text = """
    JOHN DOE
    Software Engineer
    
    Email: john.doe@email.com
    Phone: +1 555-123-4567
    
    Experience:
    - Senior Developer at ABC Corp (2020-2023)
    - Junior Developer at XYZ Inc (2018-2020)
    
    Education:
    - BS Computer Science, University of Tech (2014-2018)
    """
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/processor/debug",
            json={"text": test_text},
            timeout=60
        )
        
        if response.status_code == 200:
            debug_info = response.json()
            print(f"   ✅ Debug endpoint successful")
            
            debug_data = debug_info.get('debug_info', {})
            print(f"   Raw response length: {debug_data.get('raw_response_length', 0)}")
            print(f"   Parse successful: {debug_data.get('parse_successful', False)}")
            print(f"   Structure valid: {debug_data.get('response_structure_valid', False)}")
            
            if debug_data.get('parse_error'):
                print(f"   Parse error: {debug_data.get('parse_error')}")
            
            if debug_data.get('raw_response_preview'):
                print(f"   Raw response preview: {debug_data.get('raw_response_preview')[:200]}...")
            
            parsed_response = debug_data.get('parsed_response')
            if parsed_response:
                print(f"   Parsed response keys: {list(parsed_response.keys())}")
                if 'extracted_data' in parsed_response:
                    extracted_data = parsed_response['extracted_data']
                    print(f"   Extracted data keys: {list(extracted_data.keys())}")
                    
                    # Check for actual data
                    for section_key, section_data in extracted_data.items():
                        if isinstance(section_data, dict) and section_data:
                            print(f"     {section_key}: {list(section_data.keys())}")
                        elif section_data:
                            print(f"     {section_key}: {type(section_data)} with content")
                        else:
                            print(f"     {section_key}: empty")
            
            return debug_info
        else:
            print(f"   ❌ Debug endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    
    except Exception as e:
        print(f"   ❌ Error testing debug endpoint: {e}")
        return None


def test_api_text_processing():
    """Test the regular text processing API endpoint"""
    print("\n🔍 Testing API text processing endpoint...")
    
    base_url = f"http://{API_HOST}:{API_PORT}"
    
    test_text = """
    ALICE SMITH
    Marketing Manager
    
    Contact: alice.smith@company.com
    Phone: +1 555-987-6543
    Location: New York, NY
    
    Professional Experience:
    Marketing Manager at BigCorp (2021-Present)
    - Led digital marketing campaigns
    - Managed team of 5 marketing specialists
    
    Marketing Coordinator at MediumCorp (2019-2021)
    - Coordinated social media campaigns
    - Analyzed marketing metrics
    
    Education:
    MBA Marketing, Business School (2017-2019)
    BA Communications, State University (2013-2017)
    """
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/processor/text",
            json={"text": test_text},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Text processing endpoint successful")
            print(f"   Status: {result.get('status', 'unknown')}")
            
            if result.get('result'):
                doc_result = result['result']
                print(f"   Document Type: {doc_result.get('document_type', 'unknown')}")
                print(f"   Confidence: {doc_result.get('confidence', 0.0):.2f}")
                
                extracted_data = doc_result.get('extracted_data', {}).get('data', {})
                print(f"   Extracted Data Keys: {list(extracted_data.keys())}")
                
                if extracted_data:
                    print(f"   Sample Extracted Data:")
                    for key, value in list(extracted_data.items())[:5]:
                        print(f"     {key}: {value}")
                else:
                    print(f"   ❌ No extracted data in API result")
                    print(f"   Full extracted_data structure: {doc_result.get('extracted_data', {})}")
            
            return result
        else:
            print(f"   ❌ Text processing endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    
    except Exception as e:
        print(f"   ❌ Error testing text processing endpoint: {e}")
        return None


def main():
    """Main debug function"""
    print("🐛 Debug Document Data Extraction")
    print("=" * 50)
    
    # Test 1: Direct processing
    direct_result = test_direct_processing()
    
    # Test 2: API debug endpoint
    debug_result = test_api_debug_endpoint()
    
    # Test 3: API text processing
    api_result = test_api_text_processing()
    
    # Summary
    print(f"\n📊 DEBUG SUMMARY:")
    print(f"   Direct Processing: {'✅' if direct_result else '❌'}")
    print(f"   API Debug Endpoint: {'✅' if debug_result else '❌'}")
    print(f"   API Text Processing: {'✅' if api_result else '❌'}")
    
    # Analysis
    if direct_result and not api_result:
        print(f"\n🔍 ANALYSIS: Direct processing works but API doesn't - check API conversion logic")
    elif not direct_result:
        print(f"\n🔍 ANALYSIS: Direct processing fails - check unified prompt or AI response")
    elif all([direct_result, debug_result, api_result]):
        print(f"\n🔍 ANALYSIS: All tests pass - extraction should be working")
    else:
        print(f"\n🔍 ANALYSIS: Mixed results - check individual test outputs above")


if __name__ == "__main__":
    main()
