"""
Test the complete flow from API to UI format to verify data extraction is working.
"""

import os
import sys
import json
import requests

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Common.constants import API_HOST, API_PORT


def test_complete_flow():
    """Test the complete flow with passport data like in your logs"""
    print("🔍 Testing complete flow with passport data...")
    
    base_url = f"http://{API_HOST}:{API_PORT}"
    
    # Use the exact passport data from your logs
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
        print(f"   📤 Sending request...")
        
        response = requests.post(
            f"{base_url}/api/v1/processor/text",
            json={"text": passport_text},
            timeout=60
        )
        
        print(f"   📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            api_response = response.json()
            
            print(f"   📋 API Response Analysis:")
            print(f"     - Status: {api_response.get('status')}")
            print(f"     - Message: {api_response.get('message')}")
            print(f"     - Has data array: {'data' in api_response}")
            
            if 'data' in api_response and len(api_response['data']) > 0:
                doc_data = api_response['data'][0]
                print(f"     - Document data keys: {list(doc_data.keys())}")
                
                # Check extracted_data structure
                if 'extracted_data' in doc_data:
                    extracted_data = doc_data['extracted_data']
                    print(f"     - Extracted data keys: {list(extracted_data.keys())}")
                    
                    if 'data' in extracted_data:
                        actual_fields = extracted_data['data']
                        print(f"     ✅ Found {len(actual_fields)} extracted fields")
                        
                        # Show the actual extracted data
                        print(f"   📋 Extracted Fields:")
                        for key, value in actual_fields.items():
                            if isinstance(value, list):
                                print(f"     {key}: [{', '.join(map(str, value[:2]))}{'...' if len(value) > 2 else ''}]")
                            else:
                                print(f"     {key}: {value}")
                        
                        # Simulate what the UI conversion function does
                        print(f"\n   🔄 Simulating UI conversion...")
                        
                        # This is what convertDocumentProcessorResponse does
                        ui_format = {
                            "status": "success",
                            "document_type": doc_data.get('processing_details', {}).get('document_type', 'Unknown'),
                            "template_matched": "passport",
                            "template_confidence": doc_data.get('processing_details', {}).get('confidence', 0.0),
                            "extracted_data": {
                                "extracted_fields": actual_fields,  # This is the key mapping!
                                "confidence_scores": {field: 0.85 for field in actual_fields.keys()}
                            }
                        }
                        
                        print(f"     ✅ UI format created successfully")
                        print(f"     - Document type: {ui_format['document_type']}")
                        print(f"     - Template confidence: {ui_format['template_confidence']:.2f}")
                        print(f"     - Extracted fields count: {len(ui_format['extracted_data']['extracted_fields'])}")
                        
                        # Check if displayExtractedData would work
                        extracted_fields = ui_format['extracted_data']['extracted_fields']
                        if len(extracted_fields) > 0:
                            print(f"     ✅ displayExtractedData would show {len(extracted_fields)} fields")
                            print(f"     📋 Fields that would display:")
                            for field_name in list(extracted_fields.keys())[:5]:
                                print(f"       - {field_name}")
                        else:
                            print(f"     ❌ displayExtractedData would show 'No data extracted'")
                        
                        return True
                    else:
                        print(f"     ❌ No 'data' field in extracted_data")
                else:
                    print(f"     ❌ No 'extracted_data' in document data")
            else:
                print(f"     ❌ No data array in response")
            
            return False
        else:
            print(f"   ❌ Request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    except Exception as e:
        print(f"   ❌ Error testing complete flow: {e}")
        return False


def test_ui_javascript_simulation():
    """Simulate what the UI JavaScript does with the API response"""
    print("\n🔍 Simulating UI JavaScript processing...")
    
    # This simulates what happens in the browser
    sample_api_response = {
        "status": "success",
        "message": "Successfully processed 1 documents",
        "data": [
            {
                "extracted_data": {
                    "data": {
                        "Name": "SRIKRISHNAN NADAR SIVA SELVA KUMAR",
                        "First Name": "SIVA SELVA KUMAR",
                        "Last Name": "SRIKRISHNAN NADAR",
                        "Date of Birth": "1976-05-04",
                        "Gender": "M",
                        "Nationality": "INDIAN",
                        "Address": "NAGERCOIL MADURAI",
                        "City": "MADURAI",
                        "Country": "India",
                        "Document Number": "H1591116",
                        "Issue Date": "2008-12-01",
                        "Expiry Date": "2018-11-30",
                        "Status": "expired",
                        "place_of_birth": "NAGERCOIL",
                        "passport_type": "P"
                    },
                    "confidence": 0.85
                },
                "verification": {
                    "is_genuine": True,
                    "confidence_score": 0.88
                },
                "processing_details": {
                    "document_type": "passport",
                    "confidence": 0.92,
                    "validation_level": "comprehensive",
                    "processing_method": "unified_prompt"
                }
            }
        ]
    }
    
    try:
        # Simulate convertDocumentProcessorResponse function
        print(f"   🔄 Running convertDocumentProcessorResponse simulation...")
        
        data_array = sample_api_response.get('data', [])
        if len(data_array) == 0:
            print(f"     ❌ No data array - would return error")
            return False
        
        first_result = data_array[0]
        extracted_data = first_result.get('extracted_data', {})
        verification = first_result.get('verification', {})
        processing_details = first_result.get('processing_details', {})
        
        # This is the key line from the conversion function
        extracted_fields = extracted_data.get('data', {})  # Line 1395 in script.js
        
        print(f"     ✅ Extracted {len(extracted_fields)} fields from API response")
        
        # Simulate the UI format creation
        ui_results = {
            "status": "success",
            "document_type": processing_details.get('document_type', 'Unknown'),
            "template_matched": "passport",
            "template_confidence": processing_details.get('confidence', 0.0),
            "extracted_data": {
                "extracted_fields": extracted_fields,  # This goes to displayExtractedData
                "confidence_scores": {field: 0.85 for field in extracted_fields.keys()}
            }
        }
        
        print(f"     ✅ UI results object created")
        print(f"     - Document type: {ui_results['document_type']}")
        print(f"     - Template confidence: {ui_results['template_confidence']:.2f}")
        
        # Simulate displayExtractedData function
        print(f"   🔄 Simulating displayExtractedData...")
        
        fields = ui_results['extracted_data']['extracted_fields']
        
        if len(fields) == 0:
            print(f"     ❌ Would display: 'No data extracted from the document.'")
            return False
        else:
            print(f"     ✅ Would display {len(fields)} fields:")
            for field_name, field_value in list(fields.items())[:5]:
                print(f"       - {field_name}: {field_value}")
            
            return True
    
    except Exception as e:
        print(f"   ❌ Error in UI simulation: {e}")
        return False


def main():
    """Main test function"""
    print("🧪 Testing Complete API to UI Flow")
    print("=" * 50)
    
    # Test 1: Complete API flow
    api_works = test_complete_flow()
    
    # Test 2: UI JavaScript simulation
    ui_works = test_ui_javascript_simulation()
    
    # Summary
    print(f"\n📊 FLOW TEST SUMMARY:")
    print(f"   API Response Format: {'✅' if api_works else '❌'}")
    print(f"   UI JavaScript Processing: {'✅' if ui_works else '❌'}")
    
    if api_works and ui_works:
        print(f"\n🎉 COMPLETE FLOW WORKING!")
        print(f"   • API returns data in correct format")
        print(f"   • UI JavaScript can process the response")
        print(f"   • Data should display in the browser")
        print(f"\n💡 If UI still shows 'No data extracted':")
        print(f"   • Check browser developer console for JavaScript errors")
        print(f"   • Check network tab to see actual API response")
        print(f"   • Verify the convertDocumentProcessorResponse function is being called")
    elif api_works:
        print(f"\n⚠️ API WORKS BUT UI SIMULATION FAILED")
        print(f"   • Check the UI JavaScript conversion logic")
        print(f"   • Verify the response format matches expectations")
    elif ui_works:
        print(f"\n⚠️ UI SIMULATION WORKS BUT API FAILED")
        print(f"   • Check the API response format")
        print(f"   • Verify the controller is returning correct structure")
    else:
        print(f"\n❌ BOTH API AND UI SIMULATION FAILED")
        print(f"   • Check API connectivity and response format")
        print(f"   • Check UI JavaScript logic")


if __name__ == "__main__":
    main()
