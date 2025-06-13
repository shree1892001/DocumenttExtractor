"""
Test script to verify the API returns data in the format expected by the UI.
"""

import os
import sys
import json
import requests

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Common.constants import API_HOST, API_PORT


def test_ui_expected_format():
    """Test that API returns data in the format expected by the UI"""
    print("🔍 Testing UI-expected API response format...")
    
    base_url = f"http://{API_HOST}:{API_PORT}"
    
    # Test with resume text that should extract data
    resume_text = """
    SARAH WILSON
    Product Manager
    
    Email: sarah.wilson@company.com
    Phone: +1 555-123-4567
    LinkedIn: linkedin.com/in/sarahwilson
    Location: San Francisco, CA
    
    EXPERIENCE:
    Senior Product Manager | Google | 2021 - Present
    • Led product strategy for Gmail with 1.5B+ users
    • Managed cross-functional team of 12 engineers and designers
    • Launched 5 major features resulting in 20% user engagement increase
    
    Product Manager | Facebook | 2019 - 2021
    • Owned messaging features for WhatsApp Business
    • Conducted user research and A/B testing
    • Improved business user retention by 35%
    
    EDUCATION:
    MBA | Stanford Graduate School of Business | 2017 - 2019
    BS Computer Science | MIT | 2013 - 2017
    
    SKILLS:
    Product Strategy, User Research, A/B Testing, SQL, Python
    Data Analysis, Agile Development, Cross-functional Leadership
    """
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/processor/text",
            json={"text": resume_text},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ API request successful")
            
            # Check the expected UI format
            print(f"   📋 Checking UI-expected format...")
            
            # Top-level structure
            required_fields = ['status', 'message', 'data']
            for field in required_fields:
                if field in result:
                    print(f"     ✅ {field}: {result[field] if field != 'data' else f'array with {len(result[field])} items'}")
                else:
                    print(f"     ❌ Missing {field}")
            
            # Check data array structure
            if 'data' in result and len(result['data']) > 0:
                doc_data = result['data'][0]
                
                print(f"   📋 Checking document data structure...")
                doc_required_fields = ['extracted_data', 'verification', 'processing_details']
                for field in doc_required_fields:
                    if field in doc_data:
                        print(f"     ✅ {field}: present")
                    else:
                        print(f"     ❌ Missing {field}")
                
                # Check extracted_data structure
                if 'extracted_data' in doc_data:
                    extracted_data = doc_data['extracted_data']
                    if 'data' in extracted_data:
                        actual_data = extracted_data['data']
                        print(f"     ✅ extracted_data.data: {len(actual_data)} fields")
                        
                        if actual_data:
                            print(f"     📋 Sample extracted fields:")
                            for key, value in list(actual_data.items())[:5]:
                                if isinstance(value, list):
                                    print(f"       {key}: [{', '.join(map(str, value[:3]))}{'...' if len(value) > 3 else ''}]")
                                else:
                                    print(f"       {key}: {value}")
                        else:
                            print(f"     ❌ extracted_data.data is empty")
                    else:
                        print(f"     ❌ extracted_data missing 'data' field")
                
                # Check processing_details
                if 'processing_details' in doc_data:
                    processing = doc_data['processing_details']
                    print(f"     ✅ processing_details:")
                    print(f"       document_type: {processing.get('document_type', 'missing')}")
                    print(f"       confidence: {processing.get('confidence', 'missing')}")
                    print(f"       processing_method: {processing.get('processing_method', 'missing')}")
                
                # Check verification
                if 'verification' in doc_data:
                    verification = doc_data['verification']
                    print(f"     ✅ verification:")
                    print(f"       is_genuine: {verification.get('is_genuine', 'missing')}")
                    print(f"       confidence_score: {verification.get('confidence_score', 'missing')}")
            
            # Test what the UI conversion function expects
            print(f"\n   🔍 Testing UI conversion compatibility...")
            try:
                # Simulate what the UI does
                data_array = result.get('data', [])
                if len(data_array) > 0:
                    first_result = data_array[0]
                    extracted_data = first_result.get('extracted_data', {})
                    extracted_fields = extracted_data.get('data', {})
                    
                    if extracted_fields:
                        print(f"     ✅ UI conversion would work - {len(extracted_fields)} fields available")
                        print(f"     📋 Fields that would display in UI:")
                        for field_name in list(extracted_fields.keys())[:5]:
                            print(f"       - {field_name}")
                    else:
                        print(f"     ❌ UI conversion would fail - no extracted fields")
                else:
                    print(f"     ❌ UI conversion would fail - no data array")
            except Exception as conversion_error:
                print(f"     ❌ UI conversion would fail: {conversion_error}")
            
            return result
        else:
            print(f"   ❌ API request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    
    except Exception as e:
        print(f"   ❌ Error testing API format: {e}")
        return None


def test_sample_result_endpoint():
    """Test the sample result endpoint for comparison"""
    print("\n🔍 Testing sample result endpoint...")
    
    base_url = f"http://{API_HOST}:{API_PORT}"
    
    try:
        response = requests.post(f"{base_url}/api/v1/processor/test-result", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Sample result endpoint successful")
            
            # Check if it matches the expected format
            if 'data' in result and len(result['data']) > 0:
                doc_data = result['data'][0]
                extracted_fields = doc_data.get('extracted_data', {}).get('data', {})
                print(f"   📋 Sample result has {len(extracted_fields)} fields:")
                for key, value in extracted_fields.items():
                    print(f"     {key}: {value}")
                
                return result
            else:
                print(f"   ❌ Sample result doesn't have expected structure")
                return None
        else:
            print(f"   ❌ Sample result endpoint failed: {response.status_code}")
            return None
    
    except Exception as e:
        print(f"   ❌ Error testing sample result: {e}")
        return None


def main():
    """Main test function"""
    print("🧪 Testing UI Response Format Compatibility")
    print("=" * 60)
    
    # Test 1: Actual API response format
    actual_result = test_ui_expected_format()
    
    # Test 2: Sample result for comparison
    sample_result = test_sample_result_endpoint()
    
    # Summary
    print(f"\n📊 SUMMARY:")
    
    if actual_result:
        data_array = actual_result.get('data', [])
        if len(data_array) > 0:
            extracted_fields = data_array[0].get('extracted_data', {}).get('data', {})
            if extracted_fields:
                print(f"   ✅ API returns UI-compatible format with {len(extracted_fields)} fields")
                print(f"   🎉 Data extraction should now work in the UI!")
            else:
                print(f"   ⚠️ API format is correct but no data extracted")
        else:
            print(f"   ❌ API format issue - no data array")
    else:
        print(f"   ❌ API request failed")
    
    if sample_result:
        print(f"   ✅ Sample result endpoint works as expected")
    else:
        print(f"   ❌ Sample result endpoint failed")
    
    print(f"\n💡 NEXT STEPS:")
    if actual_result and actual_result.get('data', []):
        extracted_fields = actual_result['data'][0].get('extracted_data', {}).get('data', {})
        if extracted_fields:
            print(f"   • Upload a document through the UI to test the complete flow")
            print(f"   • The UI should now display the extracted data properly")
        else:
            print(f"   • Check why no data is being extracted from the test document")
            print(f"   • Verify the unified processing is working correctly")
    else:
        print(f"   • Fix the API response format issues first")
        print(f"   • Check the controller conversion logic")


if __name__ == "__main__":
    main()
