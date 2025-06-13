"""
Quick test to see what the API is actually returning.
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
    """Test text processing with passport data"""
    print("🔍 Testing text processing...")
    
    base_url = f"http://{API_HOST}:{API_PORT}"
    
    # Use passport data similar to your logs
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
        print(f"   📤 Sending to: {base_url}/api/v1/processor/text")
        
        response = requests.post(
            f"{base_url}/api/v1/processor/text",
            json={"text": passport_text},
            timeout=60
        )
        
        print(f"   📥 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"   📋 Response keys: {list(result.keys())}")
            print(f"   📋 Status: {result.get('status')}")
            print(f"   📋 Message: {result.get('message')}")
            
            if 'data' in result:
                print(f"   📋 Data array length: {len(result['data'])}")
                if len(result['data']) > 0:
                    doc = result['data'][0]
                    print(f"   📋 Document keys: {list(doc.keys())}")
                    
                    if 'extracted_data' in doc:
                        extracted = doc['extracted_data']
                        print(f"   📋 Extracted data keys: {list(extracted.keys())}")
                        
                        if 'data' in extracted:
                            fields = extracted['data']
                            print(f"   ✅ Found {len(fields)} extracted fields:")
                            for key, value in list(fields.items())[:5]:
                                print(f"     {key}: {value}")
                        else:
                            print(f"   ❌ No 'data' in extracted_data")
                    else:
                        print(f"   ❌ No 'extracted_data' in document")
                else:
                    print(f"   ❌ Data array is empty")
            else:
                print(f"   ❌ No 'data' in response")
                
                # Check if it's old format
                if 'result' in result:
                    print(f"   ⚠️ Found 'result' (old format)")
                    old_result = result['result']
                    if 'extracted_data' in old_result:
                        old_data = old_result['extracted_data'].get('data', {})
                        print(f"   Old format has {len(old_data)} fields")
            
            return result
        else:
            print(f"   ❌ Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None


def test_file_upload():
    """Test file upload"""
    print("\n🔍 Testing file upload...")
    
    base_url = f"http://{API_HOST}:{API_PORT}"
    
    # Create a temporary file with passport content
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
        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write(passport_content)
            temp_file_path = temp_file.name
        
        print(f"   📤 Uploading to: {base_url}/api/v1/processor")
        
        try:
            with open(temp_file_path, 'rb') as f:
                files = {'file': ('passport.txt', f, 'text/plain')}
                response = requests.post(
                    f"{base_url}/api/v1/processor",
                    files=files,
                    timeout=60
                )
            
            print(f"   📥 Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"   📋 Response keys: {list(result.keys())}")
                print(f"   📋 Status: {result.get('status')}")
                
                if 'data' in result and len(result['data']) > 0:
                    doc = result['data'][0]
                    extracted_fields = doc.get('extracted_data', {}).get('data', {})
                    print(f"   ✅ File upload extracted {len(extracted_fields)} fields")
                    
                    if extracted_fields:
                        print(f"   📋 Sample fields:")
                        for key, value in list(extracted_fields.items())[:3]:
                            print(f"     {key}: {value}")
                else:
                    print(f"   ❌ File upload: No data in response")
                
                return result
            else:
                print(f"   ❌ Failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
        
        finally:
            # Clean up
            try:
                os.unlink(temp_file_path)
            except:
                pass
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None


def main():
    """Main test"""
    print("🧪 Quick API Debug Test")
    print("=" * 30)
    
    # Test text processing
    text_result = test_text_processing()
    
    # Test file upload
    file_result = test_file_upload()
    
    # Summary
    print(f"\n📊 SUMMARY:")
    
    if text_result:
        text_has_data = 'data' in text_result and len(text_result['data']) > 0
        if text_has_data:
            text_fields = text_result['data'][0].get('extracted_data', {}).get('data', {})
            print(f"   ✅ Text processing: {len(text_fields)} fields extracted")
        else:
            print(f"   ❌ Text processing: No data in response")
    else:
        print(f"   ❌ Text processing: Failed")
    
    if file_result:
        file_has_data = 'data' in file_result and len(file_result['data']) > 0
        if file_has_data:
            file_fields = file_result['data'][0].get('extracted_data', {}).get('data', {})
            print(f"   ✅ File upload: {len(file_fields)} fields extracted")
        else:
            print(f"   ❌ File upload: No data in response")
    else:
        print(f"   ❌ File upload: Failed")
    
    # Recommendations
    print(f"\n💡 NEXT STEPS:")
    if text_result and file_result:
        text_fields = text_result['data'][0].get('extracted_data', {}).get('data', {}) if 'data' in text_result else {}
        file_fields = file_result['data'][0].get('extracted_data', {}).get('data', {}) if 'data' in file_result else {}
        
        if text_fields and file_fields:
            print(f"   • API is working correctly!")
            print(f"   • Check browser developer tools for UI issues")
            print(f"   • Look for JavaScript errors in browser console")
        else:
            print(f"   • API format conversion is not working")
            print(f"   • Check the controller logs for debug messages")
    else:
        print(f"   • API connectivity issues")
        print(f"   • Check if the API server is running")


if __name__ == "__main__":
    main()
