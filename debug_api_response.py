"""
Debug what the API is actually returning to understand why UI isn't working.
"""

import os
import sys
import json
import requests

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Common.constants import API_HOST, API_PORT


def test_actual_api_response():
    """Test what the API actually returns"""
    print("🔍 Testing actual API response...")
    
    base_url = f"http://{API_HOST}:{API_PORT}"
    
    # Simple passport text
    passport_text = """
    REPUBLIC OF INDIA
    PASSPORT
    
    Type: P
    Passport No.: H1591116
    
    Surname: SRIKRISHNAN NADAR
    Given Name(s): SIVA SELVA KUMAR
    
    Nationality: INDIAN
    Date of Birth: 04/05/1976
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
            
            # Print the EXACT response structure
            print(f"\n   📋 EXACT API RESPONSE:")
            print(f"   {json.dumps(result, indent=2)}")
            
            # Test what the UI JavaScript would see
            print(f"\n   🔄 UI JavaScript Analysis:")
            
            # Check top-level keys
            print(f"     Top-level keys: {list(result.keys())}")
            
            # Check extracted_data specifically
            if 'extracted_data' in result:
                extracted_data = result['extracted_data']
                print(f"     extracted_data type: {type(extracted_data)}")
                print(f"     extracted_data keys: {list(extracted_data.keys()) if isinstance(extracted_data, dict) else 'Not a dict'}")
                
                # This is what the UI looks for
                if isinstance(extracted_data, dict):
                    if 'extracted_fields' in extracted_data:
                        fields = extracted_data['extracted_fields']
                        print(f"     ✅ Found extracted_fields with {len(fields)} fields")
                    else:
                        # Raw format - extracted_data IS the fields
                        fields = extracted_data
                        print(f"     ✅ Using extracted_data as fields: {len(fields)} fields")
                        
                        # Show first few fields
                        if fields:
                            print(f"     📋 Sample fields:")
                            for i, (key, value) in enumerate(list(fields.items())[:3]):
                                print(f"       {key}: {value}")
                else:
                    print(f"     ❌ extracted_data is not a dict: {extracted_data}")
            else:
                print(f"     ❌ No 'extracted_data' key in response")
            
            return result
        else:
            print(f"   ❌ Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None


def create_ui_test_page():
    """Create a test page that shows exactly what the UI sees"""
    print(f"\n🔍 Creating UI test page...")
    
    html_content = '''
<!DOCTYPE html>
<html>
<head>
    <title>UI Debug Test</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .section { margin: 20px 0; padding: 15px; border: 1px solid #ccc; }
        .success { background-color: #d4edda; }
        .error { background-color: #f8d7da; }
        .info { background-color: #d1ecf1; }
        pre { background: #f8f9fa; padding: 10px; overflow-x: auto; }
        button { padding: 10px 20px; margin: 10px 0; }
    </style>
</head>
<body>
    <h1>UI Debug Test</h1>
    
    <div class="section info">
        <h3>Test API Response</h3>
        <button onclick="testAPI()">Test API Call</button>
        <div id="api-result"></div>
    </div>
    
    <div class="section">
        <h3>UI Processing Test</h3>
        <div id="ui-test-result"></div>
    </div>
    
    <script>
        const API_BASE = 'http://localhost:8000';  // Adjust if needed
        
        async function testAPI() {
            const resultDiv = document.getElementById('api-result');
            const uiTestDiv = document.getElementById('ui-test-result');
            
            try {
                resultDiv.innerHTML = '<p>🔄 Testing API...</p>';
                
                const response = await fetch(`${API_BASE}/api/v1/processor/text`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        text: `REPUBLIC OF INDIA
PASSPORT

Type: P
Passport No.: H1591116

Surname: SRIKRISHNAN NADAR
Given Name(s): SIVA SELVA KUMAR

Nationality: INDIAN
Date of Birth: 04/05/1976`
                    })
                });
                
                if (response.ok) {
                    const result = await response.json();
                    
                    // Show raw response
                    resultDiv.innerHTML = `
                        <div class="success">
                            <h4>✅ API Response Received</h4>
                            <pre>${JSON.stringify(result, null, 2)}</pre>
                        </div>
                    `;
                    
                    // Test UI processing
                    testUIProcessing(result, uiTestDiv);
                    
                } else {
                    resultDiv.innerHTML = `
                        <div class="error">
                            <h4>❌ API Error</h4>
                            <p>Status: ${response.status}</p>
                            <p>Response: ${await response.text()}</p>
                        </div>
                    `;
                }
                
            } catch (error) {
                resultDiv.innerHTML = `
                    <div class="error">
                        <h4>❌ Network Error</h4>
                        <p>${error.message}</p>
                    </div>
                `;
            }
        }
        
        function testUIProcessing(results, outputDiv) {
            console.log('Testing UI processing with:', results);
            
            let testResults = [];
            
            // Test 1: Document Type
            const docType = results.document_type || 'Unknown';
            const confidence = (results.confidence || results.template_confidence || 0) * 100;
            testResults.push(`Document Type: ${docType} (${confidence.toFixed(0)}% confidence)`);
            
            // Test 2: Extracted Data - This is the critical test
            let fields = {};
            let fieldSource = '';
            
            if (results.extracted_data) {
                if (results.extracted_data.extracted_fields) {
                    // Old format
                    fields = results.extracted_data.extracted_fields;
                    fieldSource = 'Old format (extracted_data.extracted_fields)';
                } else {
                    // New raw format
                    fields = results.extracted_data;
                    fieldSource = 'New raw format (extracted_data directly)';
                }
            }
            
            const fieldCount = Object.keys(fields).length;
            testResults.push(`Fields found: ${fieldCount} (${fieldSource})`);
            
            if (fieldCount > 0) {
                testResults.push('✅ UI SHOULD DISPLAY DATA');
                testResults.push('Sample fields:');
                Object.entries(fields).slice(0, 5).forEach(([key, value]) => {
                    testResults.push(`  • ${key}: ${value}`);
                });
            } else {
                testResults.push('❌ UI WOULD SHOW "No data extracted"');
            }
            
            // Test 3: Verification
            const verification = results.verification_result || {};
            if (verification.rejection_reason) {
                testResults.push(`Verification: Rejected (${verification.rejection_reason})`);
            } else {
                testResults.push('Verification: OK');
            }
            
            // Display results
            const resultClass = fieldCount > 0 ? 'success' : 'error';
            outputDiv.innerHTML = `
                <div class="${resultClass}">
                    <h4>${fieldCount > 0 ? '✅' : '❌'} UI Processing Test</h4>
                    ${testResults.map(result => `<p>${result}</p>`).join('')}
                </div>
            `;
        }
        
        // Auto-test on page load
        window.onload = function() {
            // Test with sample data first
            const sampleData = {
                "status": "success",
                "document_type": "passport",
                "confidence": 0.95,
                "extracted_data": {
                    "Name": "SRIKRISHNAN NADAR SIVA SELVA KUMAR",
                    "Document Number": "H1591116"
                }
            };
            
            const uiTestDiv = document.getElementById('ui-test-result');
            uiTestDiv.innerHTML = '<h4>Sample Data Test:</h4>';
            testUIProcessing(sampleData, uiTestDiv);
        };
    </script>
</body>
</html>
    '''
    
    try:
        with open('DocumenttExtractor/ui_debug_test.html', 'w') as f:
            f.write(html_content)
        print(f"   ✅ Created ui_debug_test.html")
        return True
    except Exception as e:
        print(f"   ❌ Error creating test page: {e}")
        return False


def main():
    """Main debug function"""
    print("🐛 Debugging API Response for UI")
    print("=" * 40)
    
    # Test 1: Check actual API response
    api_result = test_actual_api_response()
    
    # Test 2: Create debug page
    debug_page_created = create_ui_test_page()
    
    print(f"\n📊 DEBUG SUMMARY:")
    if api_result:
        print(f"   ✅ API is responding")
        
        # Check if extracted_data exists and has fields
        extracted_data = api_result.get('extracted_data', {})
        if isinstance(extracted_data, dict) and len(extracted_data) > 0:
            print(f"   ✅ API returns {len(extracted_data)} extracted fields")
            print(f"   🎯 The issue might be in the UI JavaScript")
        else:
            print(f"   ❌ API returns no extracted fields")
            print(f"   🎯 The issue is in the API response format")
    else:
        print(f"   ❌ API is not responding correctly")
    
    if debug_page_created:
        print(f"   ✅ Debug page created")
    
    print(f"\n💡 NEXT STEPS:")
    print(f"   1. Check the EXACT API RESPONSE above")
    print(f"   2. Open ui_debug_test.html in your browser")
    print(f"   3. Click 'Test API Call' to see what the UI receives")
    print(f"   4. Check browser console for any JavaScript errors")
    print(f"   5. Compare the API response structure with what the UI expects")


if __name__ == "__main__":
    main()
