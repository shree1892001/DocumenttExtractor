#!/usr/bin/env python3
"""
Test script to verify that extracted data is always included in the response
"""

import requests
import json
import sys

def test_document_processing():
    """Test document processing to ensure extracted data is always returned"""
    
    print("🔍 Testing DocumentProcessor API - Extracted Data Fix")
    print("=" * 60)
    
    # Test with a sample image file
    api_url = "http://localhost:9500/api/v1/processor"
    
    # You can replace this with an actual test file path
    test_file_path = "test_document.jpg"  # Replace with your test file
    
    try:
        # Test with a file upload
        with open(test_file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(api_url, files=files, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ API Response received successfully")
            print(f"Status: {result.get('status')}")
            print(f"Message: {result.get('message')}")
            
            # Check if data is present
            data = result.get('data', [])
            if data:
                print(f"📊 Found {len(data)} document(s) in response")
                
                for i, doc in enumerate(data):
                    print(f"\n📄 Document {i+1}:")
                    
                    # Check extracted_data
                    extracted_data = doc.get('extracted_data', {})
                    data_content = extracted_data.get('data', {})
                    
                    print(f"   Extracted Data Present: {'✅ Yes' if data_content else '❌ No'}")
                    print(f"   Data Fields: {len(data_content)} fields")
                    print(f"   Confidence: {extracted_data.get('confidence', 0.0)}")
                    
                    # Check verification
                    verification = doc.get('verification', {})
                    print(f"   Document Genuine: {'✅ Yes' if verification.get('is_genuine') else '❌ No'}")
                    print(f"   Verification Confidence: {verification.get('confidence_score', 0.0)}")
                    
                    # Check processing details
                    processing = doc.get('processing_details', {})
                    print(f"   Document Type: {processing.get('document_type', 'unknown')}")
                    print(f"   Processing Method: {processing.get('processing_method', 'unknown')}")
                    
                    # Show actual extracted data if present
                    if data_content:
                        print(f"   📋 Extracted Fields:")
                        for key, value in data_content.items():
                            print(f"      • {key}: {value}")
                    
                    print("-" * 40)
                
                # Summary
                docs_with_data = sum(1 for doc in data if doc.get('extracted_data', {}).get('data'))
                print(f"\n📈 Summary:")
                print(f"   Total Documents: {len(data)}")
                print(f"   Documents with Extracted Data: {docs_with_data}")
                print(f"   Success Rate: {(docs_with_data/len(data)*100):.1f}%")
                
                if docs_with_data == len(data):
                    print("🎉 SUCCESS: All documents have extracted data!")
                    return True
                else:
                    print("⚠️  WARNING: Some documents missing extracted data")
                    return False
            else:
                print("❌ No data found in response")
                return False
                
        else:
            print(f"❌ API request failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except FileNotFoundError:
        print(f"❌ Test file not found: {test_file_path}")
        print("Please provide a valid test document file")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure Main.py is running on port 9500")
        return False
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 DocumentProcessor Extracted Data Test")
    print("This test verifies that extracted data is always included in responses")
    print("even when documents are rejected due to verification failures.")
    print()
    
    success = test_document_processing()
    
    if success:
        print("\n✅ TEST PASSED: Extracted data fix is working correctly!")
    else:
        print("\n❌ TEST FAILED: Extracted data is still missing in some cases")
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n🛑 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
