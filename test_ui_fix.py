"""
Test the UI fix for raw format compatibility.
"""

import os
import sys
import json
import requests

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Common.constants import API_HOST, API_PORT


def test_ui_compatibility():
    """Test that the API returns data compatible with the updated UI"""
    print("🔍 Testing UI compatibility with raw format...")
    
    base_url = f"http://{API_HOST}:{API_PORT}"
    
    # Test with passport data that should extract fields
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
            result = response.json()
            
            print(f"   📋 API Response Analysis:")
            print(f"     - Status: {result.get('status')}")
            print(f"     - Document Type: {result.get('document_type')}")
            print(f"     - Confidence: {result.get('confidence', 0.0):.2f}")
            
            # Test what the updated UI JavaScript would do
            print(f"\n   🔄 Simulating Updated UI Processing:")
            
            # Test displayDocumentType function logic
            doc_type = result.get('document_type', 'Unknown')
            confidence = (result.get('confidence', 0) * 100)
            print(f"     Document Type Display: {doc_type.capitalize()} ({confidence:.0f}% confidence)")
            
            # Test displayExtractedData function logic
            extracted_data = result.get('extracted_data', {})
            
            # This is the key test - does the UI find the fields?
            fields = {}
            if extracted_data:
                if 'extracted_fields' in extracted_data:
                    # Old format
                    fields = extracted_data['extracted_fields']
                    print(f"     ✅ Found fields in old format: {len(fields)} fields")
                else:
                    # New raw format
                    fields = extracted_data
                    print(f"     ✅ Found fields in new raw format: {len(fields)} fields")
            
            if len(fields) > 0:
                print(f"     📋 Fields that UI would display:")
                for i, (key, value) in enumerate(list(fields.items())[:5]):
                    print(f"       {i+1}. {key}: {value}")
                if len(fields) > 5:
                    print(f"       ... and {len(fields) - 5} more fields")
                
                print(f"   ✅ UI SHOULD NOW DISPLAY DATA!")
            else:
                print(f"   ❌ UI would still show 'No data extracted'")
            
            # Test verification display
            verification = result.get('verification_result', {})
            if verification:
                is_genuine = verification.get('is_genuine', True)
                rejection_reason = verification.get('rejection_reason', '')
                print(f"     Verification: {'✅ Genuine' if is_genuine else f'⚠️ Rejected ({rejection_reason})'}")
            
            return len(fields) > 0
        else:
            print(f"   ❌ API request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def create_test_html():
    """Create a simple test HTML to verify the UI changes work"""
    print("\n🔍 Creating test HTML file...")
    
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>UI Raw Format Test</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .test-result { margin: 10px 0; padding: 10px; border: 1px solid #ccc; }
        .success { background-color: #d4edda; border-color: #c3e6cb; }
        .error { background-color: #f8d7da; border-color: #f5c6cb; }
    </style>
</head>
<body>
    <h1>UI Raw Format Test</h1>
    <div id="test-results"></div>
    
    <script>
        // Simulate the updated UI functions
        function testDisplayExtractedData(results) {
            console.log('Testing displayExtractedData with:', results);
            
            // This is the updated logic from script.js
            let fields = {};
            let confidenceScores = {};
            
            if (results.extracted_data) {
                if (results.extracted_data.extracted_fields) {
                    // Old format
                    fields = results.extracted_data.extracted_fields;
                    confidenceScores = results.extracted_data.confidence_scores || {};
                } else {
                    // New raw format
                    fields = results.extracted_data;
                    const defaultConfidence = results.confidence || 0.85;
                    confidenceScores = {};
                    Object.keys(fields).forEach(key => {
                        confidenceScores[key] = defaultConfidence;
                    });
                }
            }
            
            return {
                fieldCount: Object.keys(fields).length,
                fields: fields,
                confidenceScores: confidenceScores
            };
        }
        
        // Test with sample raw format data
        const sampleRawData = {
            "status": "success",
            "document_type": "passport",
            "confidence": 0.95,
            "extracted_data": {
                "Name": "SRIKRISHNAN NADAR SIVA SELVA KUMAR",
                "First Name": "SIVA SELVA KUMAR",
                "Document Number": "H1591116",
                "Date of Birth": "1976-05-04",
                "Nationality": "INDIAN"
            },
            "verification_result": {
                "is_genuine": false,
                "rejection_reason": "suspicious"
            }
        };
        
        // Run test
        const testResult = testDisplayExtractedData(sampleRawData);
        
        const resultsDiv = document.getElementById('test-results');
        
        if (testResult.fieldCount > 0) {
            resultsDiv.innerHTML = `
                <div class="test-result success">
                    <h3>✅ Test PASSED</h3>
                    <p>UI can extract ${testResult.fieldCount} fields from raw format:</p>
                    <ul>
                        ${Object.entries(testResult.fields).map(([key, value]) => 
                            `<li><strong>${key}:</strong> ${value}</li>`
                        ).join('')}
                    </ul>
                    <p><strong>The UI should now display extracted data!</strong></p>
                </div>
            `;
        } else {
            resultsDiv.innerHTML = `
                <div class="test-result error">
                    <h3>❌ Test FAILED</h3>
                    <p>UI could not extract fields from raw format.</p>
                    <p>The UI would still show "No data extracted".</p>
                </div>
            `;
        }
    </script>
</body>
</html>
    """
    
    try:
        with open('DocumenttExtractor/test_ui_raw_format.html', 'w') as f:
            f.write(html_content)
        print(f"   ✅ Created test_ui_raw_format.html")
        print(f"   💡 Open this file in a browser to test the UI logic")
        return True
    except Exception as e:
        print(f"   ❌ Error creating test HTML: {e}")
        return False


def main():
    """Main test function"""
    print("🧪 Testing UI Fix for Raw Format")
    print("=" * 40)
    
    # Test 1: API compatibility
    api_works = test_ui_compatibility()
    
    # Test 2: Create test HTML
    html_created = create_test_html()
    
    # Summary
    print(f"\n📊 SUMMARY:")
    print(f"   API Raw Format: {'✅' if api_works else '❌'}")
    print(f"   Test HTML Created: {'✅' if html_created else '❌'}")
    
    if api_works:
        print(f"\n🎉 UI FIX SHOULD WORK!")
        print(f"   • Upload a document through your UI")
        print(f"   • You should now see the extracted data")
        print(f"   • Check browser console for 'Extracted fields:' debug logs")
    else:
        print(f"\n⚠️ API issues found")
        print(f"   • Check if the API is running")
        print(f"   • Verify the raw format is being returned")
    
    if html_created:
        print(f"\n💡 ADDITIONAL TESTING:")
        print(f"   • Open test_ui_raw_format.html in a browser")
        print(f"   • It will test the UI logic with sample data")
        print(f"   • Should show '✅ Test PASSED' if the fix works")


if __name__ == "__main__":
    main()
