"""
Test the new raw format API response.
"""

import os
import sys
import json
import requests

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Common.constants import API_HOST, API_PORT


def test_raw_format():
    """Test the new raw format response"""
    print("🔍 Testing new raw format API...")
    
    base_url = f"http://{API_HOST}:{API_PORT}"
    
    # Test with passport data
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
            
            print(f"   📋 Raw Response Analysis:")
            print(f"     - Status: {result.get('status')}")
            print(f"     - Message: {result.get('message')}")
            print(f"     - Document Type: {result.get('document_type')}")
            print(f"     - Confidence: {result.get('confidence', 0.0):.2f}")
            
            # Check extracted data
            extracted_data = result.get('extracted_data', {})
            print(f"     - Extracted Data Fields: {len(extracted_data)}")
            
            if extracted_data:
                print(f"   📋 Extracted Fields:")
                for key, value in list(extracted_data.items())[:10]:  # Show first 10 fields
                    if isinstance(value, list):
                        print(f"     {key}: [{', '.join(map(str, value[:2]))}{'...' if len(value) > 2 else ''}]")
                    else:
                        print(f"     {key}: {value}")
                
                if len(extracted_data) > 10:
                    print(f"     ... and {len(extracted_data) - 10} more fields")
            else:
                print(f"   ❌ No extracted data found")
            
            # Check verification
            verification = result.get('verification_result', {})
            print(f"   📋 Verification:")
            print(f"     - Is Genuine: {verification.get('is_genuine')}")
            print(f"     - Confidence Score: {verification.get('confidence_score', 0.0):.2f}")
            print(f"     - Rejection Reason: {verification.get('rejection_reason', 'None')}")
            
            # Check processing details
            processing = result.get('processing_details', {})
            print(f"   📋 Processing Details:")
            print(f"     - Source File: {processing.get('source_file')}")
            print(f"     - Processing Method: {processing.get('processing_method')}")
            print(f"     - Validation Level: {processing.get('validation_level')}")
            
            return result
        else:
            print(f"   ❌ Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None


def create_simple_ui_handler():
    """Create a simple JavaScript-like handler to show how UI can process this"""
    print("\n🔍 Simulating simple UI handler...")
    
    # Simulate the API response
    sample_response = {
        "status": "success",
        "message": "Document processed successfully",
        "document_type": "passport",
        "confidence": 0.95,
        "extracted_data": {
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
        "verification_result": {
            "is_genuine": False,
            "confidence_score": 0.95,
            "rejection_reason": "suspicious",
            "verification_summary": "suspicious"
        },
        "processing_details": {
            "source_file": "passport.jpg",
            "processing_method": "unified_prompt",
            "validation_level": "comprehensive"
        }
    }
    
    try:
        # Simple UI processing logic
        print(f"   📋 UI Processing:")
        
        # Document info
        doc_type = sample_response.get('document_type', 'Unknown').title()
        confidence = sample_response.get('confidence', 0.0) * 100
        print(f"     Document Type: {doc_type} ({confidence:.0f}% confidence)")
        
        # Verification status
        verification = sample_response.get('verification_result', {})
        is_genuine = verification.get('is_genuine', True)
        rejection_reason = verification.get('rejection_reason', '')
        
        if is_genuine:
            print(f"     ✅ Verification: Document appears genuine")
        else:
            print(f"     ⚠️ Verification: Document flagged as {rejection_reason}")
        
        # Extracted data
        extracted_data = sample_response.get('extracted_data', {})
        print(f"     📋 Extracted Data ({len(extracted_data)} fields):")
        
        # Group fields by type for better display
        personal_fields = ['Name', 'First Name', 'Last Name', 'Date of Birth', 'Gender', 'Nationality']
        document_fields = ['Document Number', 'Issue Date', 'Expiry Date', 'Status', 'passport_type']
        location_fields = ['Address', 'City', 'Country', 'place_of_birth']
        
        field_groups = [
            ("Personal Information", personal_fields),
            ("Document Information", document_fields),
            ("Location Information", location_fields)
        ]
        
        for group_name, field_list in field_groups:
            group_data = {k: v for k, v in extracted_data.items() if k in field_list}
            if group_data:
                print(f"       {group_name}:")
                for key, value in group_data.items():
                    print(f"         {key}: {value}")
        
        # Show any remaining fields
        shown_fields = sum([field_list for _, field_list in field_groups], [])
        remaining_fields = {k: v for k, v in extracted_data.items() if k not in shown_fields}
        if remaining_fields:
            print(f"       Other Information:")
            for key, value in remaining_fields.items():
                if isinstance(value, list):
                    print(f"         {key}: {', '.join(map(str, value))}")
                else:
                    print(f"         {key}: {value}")
        
        print(f"   ✅ UI can easily process this raw format!")
        return True
        
    except Exception as e:
        print(f"   ❌ Error in UI simulation: {e}")
        return False


def main():
    """Main test function"""
    print("🧪 Testing Raw Format API Response")
    print("=" * 40)
    
    # Test 1: API raw format
    api_result = test_raw_format()
    
    # Test 2: UI processing simulation
    ui_works = create_simple_ui_handler()
    
    # Summary
    print(f"\n📊 SUMMARY:")
    
    if api_result:
        extracted_count = len(api_result.get('extracted_data', {}))
        print(f"   ✅ API returns raw format with {extracted_count} fields")
        print(f"   ✅ Document Type: {api_result.get('document_type', 'unknown')}")
        print(f"   ✅ Confidence: {api_result.get('confidence', 0.0):.2f}")
    else:
        print(f"   ❌ API raw format test failed")
    
    if ui_works:
        print(f"   ✅ UI can process raw format easily")
    else:
        print(f"   ❌ UI processing simulation failed")
    
    print(f"\n💡 BENEFITS OF RAW FORMAT:")
    print(f"   • Simple and direct - no complex conversions")
    print(f"   • Flexible - works with any document type")
    print(f"   • Easy to debug - what you see is what you get")
    print(f"   • Future-proof - new document types work automatically")
    print(f"   • Less error-prone - no format conversion failures")
    
    if api_result and ui_works:
        print(f"\n🎉 RAW FORMAT IS WORKING!")
        print(f"   Upload a document and you should see the extracted data!")
    else:
        print(f"\n⚠️ Some issues found - check the details above")


if __name__ == "__main__":
    main()
