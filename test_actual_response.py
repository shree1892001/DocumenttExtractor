"""
Test script to check what the API actually returns when processing documents.
"""

import os
import sys
import json
import requests
import tempfile

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Common.constants import API_HOST, API_PORT


def test_text_processing():
    """Test text processing to see the actual API response"""
    print("🔍 Testing text processing API response...")
    
    base_url = f"http://{API_HOST}:{API_PORT}"
    
    # Use passport-like text similar to what was in your logs
    passport_text = """
    REPUBLIC OF INDIA
    PASSPORT
    
    Type: P
    Country Code: IND
    Passport No.: H1591116
    
    Surname: SRIKRISHNAN NADAR
    Given Name(s): SIVA SELVA KUMAR
    
    Nationality: INDIAN
    Date of Birth: 04/05/1976
    Sex: M
    Place of Birth: NAGERCOIL
    
    Date of Issue: 01/12/2008
    Date of Expiry: 30/11/2018
    Place of Issue: MADURAI
    
    Address: NAGERCOIL MADURAI
    """
    
    try:
        print(f"   📤 Sending request to: {base_url}/api/v1/processor/text")
        
        response = requests.post(
            f"{base_url}/api/v1/processor/text",
            json={"text": passport_text},
            timeout=60
        )
        
        print(f"   📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"   📋 Response structure analysis:")
            print(f"     - Top-level keys: {list(result.keys())}")
            
            # Check if it has the UI-expected format
            if 'data' in result:
                print(f"     ✅ Has 'data' array: {len(result['data'])} items")
                
                if len(result['data']) > 0:
                    doc_data = result['data'][0]
                    print(f"     - Document data keys: {list(doc_data.keys())}")
                    
                    if 'extracted_data' in doc_data:
                        extracted_data = doc_data['extracted_data']
                        print(f"     - Extracted data keys: {list(extracted_data.keys())}")
                        
                        if 'data' in extracted_data:
                            actual_fields = extracted_data['data']
                            print(f"     ✅ Has extracted fields: {len(actual_fields)} fields")
                            print(f"     📋 Field names: {list(actual_fields.keys())}")
                            
                            # Show sample data
                            print(f"     📋 Sample extracted data:")
                            for key, value in list(actual_fields.items())[:5]:
                                if isinstance(value, list):
                                    print(f"       {key}: [{', '.join(map(str, value[:2]))}{'...' if len(value) > 2 else ''}]")
                                else:
                                    print(f"       {key}: {value}")
                        else:
                            print(f"     ❌ No 'data' field in extracted_data")
                    else:
                        print(f"     ❌ No 'extracted_data' in document data")
                else:
                    print(f"     ❌ Data array is empty")
            else:
                print(f"     ❌ No 'data' field in response")
                
                # Check if it's the old format
                if 'result' in result:
                    print(f"     ⚠️ Found 'result' field (old format)")
                    old_result = result['result']
                    if 'extracted_data' in old_result:
                        old_extracted = old_result['extracted_data'].get('data', {})
                        print(f"     - Old format has {len(old_extracted)} fields")
            
            # Show full response structure (truncated)
            print(f"\n   📄 Full response (first 1000 chars):")
            response_str = json.dumps(result, indent=2)
            print(response_str[:1000] + ("..." if len(response_str) > 1000 else ""))
            
            return result
        else:
            print(f"   ❌ Request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    
    except Exception as e:
        print(f"   ❌ Error testing text processing: {e}")
        return None


def test_file_upload():
    """Test file upload to see the actual API response"""
    print("\n🔍 Testing file upload API response...")
    
    base_url = f"http://{API_HOST}:{API_PORT}"
    
    # Create a temporary text file with passport-like content
    passport_content = """REPUBLIC OF INDIA
PASSPORT

Type: P
Country Code: IND
Passport No.: H1591116

Surname: SRIKRISHNAN NADAR
Given Name(s): SIVA SELVA KUMAR

Nationality: INDIAN
Date of Birth: 04/05/1976
Sex: M
Place of Birth: NAGERCOIL

Date of Issue: 01/12/2008
Date of Expiry: 30/11/2018
Place of Issue: MADURAI

Address: NAGERCOIL MADURAI"""
    
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write(passport_content)
            temp_file_path = temp_file.name
        
        print(f"   📤 Uploading file to: {base_url}/api/v1/processor")
        
        try:
            # Upload file
            with open(temp_file_path, 'rb') as f:
                files = {'file': ('test_passport.txt', f, 'text/plain')}
                response = requests.post(
                    f"{base_url}/api/v1/processor",
                    files=files,
                    timeout=60
                )
            
            print(f"   📥 Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"   📋 File upload response structure:")
                print(f"     - Top-level keys: {list(result.keys())}")
                
                # Check format
                if 'data' in result and len(result['data']) > 0:
                    doc_data = result['data'][0]
                    extracted_fields = doc_data.get('extracted_data', {}).get('data', {})
                    print(f"     ✅ File upload has UI-compatible format with {len(extracted_fields)} fields")
                    
                    if extracted_fields:
                        print(f"     📋 Extracted fields from file upload:")
                        for key, value in list(extracted_fields.items())[:5]:
                            print(f"       {key}: {value}")
                else:
                    print(f"     ❌ File upload response not in UI-compatible format")
                
                return result
            else:
                print(f"   ❌ File upload failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
        
        finally:
            # Clean up
            try:
                os.unlink(temp_file_path)
            except:
                pass
    
    except Exception as e:
        print(f"   ❌ Error testing file upload: {e}")
        return None


def compare_responses(text_result, file_result):
    """Compare text and file processing responses"""
    print("\n🔍 Comparing text vs file processing responses...")
    
    if not text_result or not file_result:
        print("   ❌ Cannot compare - one or both responses missing")
        return
    
    # Check if both have UI-compatible format
    text_has_data = 'data' in text_result and len(text_result['data']) > 0
    file_has_data = 'data' in file_result and len(file_result['data']) > 0
    
    print(f"   📊 Format comparison:")
    print(f"     Text processing has UI format: {'✅' if text_has_data else '❌'}")
    print(f"     File processing has UI format: {'✅' if file_has_data else '❌'}")
    
    if text_has_data and file_has_data:
        text_fields = text_result['data'][0].get('extracted_data', {}).get('data', {})
        file_fields = file_result['data'][0].get('extracted_data', {}).get('data', {})
        
        print(f"   📊 Data comparison:")
        print(f"     Text processing extracted fields: {len(text_fields)}")
        print(f"     File processing extracted fields: {len(file_fields)}")
        
        if len(text_fields) > 0 and len(file_fields) > 0:
            print(f"   ✅ Both methods extract data successfully")
        elif len(text_fields) > 0:
            print(f"   ⚠️ Only text processing extracts data")
        elif len(file_fields) > 0:
            print(f"   ⚠️ Only file processing extracts data")
        else:
            print(f"   ❌ Neither method extracts data")


def main():
    """Main test function"""
    print("🧪 Testing Actual API Response Format")
    print("=" * 50)
    
    # Test 1: Text processing
    text_result = test_text_processing()
    
    # Test 2: File upload
    file_result = test_file_upload()
    
    # Test 3: Compare responses
    compare_responses(text_result, file_result)
    
    # Summary
    print(f"\n📊 SUMMARY:")
    
    if text_result:
        text_has_ui_format = 'data' in text_result and len(text_result['data']) > 0
        if text_has_ui_format:
            text_fields = text_result['data'][0].get('extracted_data', {}).get('data', {})
            print(f"   ✅ Text processing: UI-compatible format with {len(text_fields)} fields")
        else:
            print(f"   ❌ Text processing: Not in UI-compatible format")
    else:
        print(f"   ❌ Text processing: Failed")
    
    if file_result:
        file_has_ui_format = 'data' in file_result and len(file_result['data']) > 0
        if file_has_ui_format:
            file_fields = file_result['data'][0].get('extracted_data', {}).get('data', {})
            print(f"   ✅ File processing: UI-compatible format with {len(file_fields)} fields")
        else:
            print(f"   ❌ File processing: Not in UI-compatible format")
    else:
        print(f"   ❌ File processing: Failed")
    
    print(f"\n💡 RECOMMENDATIONS:")
    if text_result and file_result:
        text_has_data = 'data' in text_result and text_result['data'][0].get('extracted_data', {}).get('data', {})
        file_has_data = 'data' in file_result and file_result['data'][0].get('extracted_data', {}).get('data', {})
        
        if text_has_data and file_has_data:
            print(f"   • API is working correctly and returning UI-compatible format")
            print(f"   • Check browser developer tools to see if UI is receiving the data")
            print(f"   • Check browser console for JavaScript errors")
        else:
            print(f"   • API format conversion is not working properly")
            print(f"   • Check the controller conversion logic")
    else:
        print(f"   • Fix API connectivity issues first")


if __name__ == "__main__":
    main()
