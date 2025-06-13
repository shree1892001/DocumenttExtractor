"""
Test script to verify DocumentProcessor3 methods and API endpoints.
"""

import os
import sys
import tempfile
import requests

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Services.DocumentProcessor3 import DocumentProcessor
from Common.constants import API_KEY, API_HOST, API_PORT


def test_documentprocessor3_methods():
    """Test DocumentProcessor3 methods directly"""
    print("🔍 Testing DocumentProcessor3 methods...")
    
    try:
        # Initialize processor
        processor = DocumentProcessor(api_key=API_KEY)
        print("   ✅ DocumentProcessor3 initialized successfully")
        
        # Check available methods
        methods = [method for method in dir(processor) if not method.startswith('_') and callable(getattr(processor, method))]
        print(f"   📋 Available public methods: {len(methods)}")
        for method in methods:
            print(f"      - {method}")
        
        # Test key methods exist
        key_methods = ['process_file', 'verify_document', 'set_unified_processing']
        for method in key_methods:
            if hasattr(processor, method):
                print(f"   ✅ {method} method exists")
            else:
                print(f"   ❌ {method} method missing")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error testing DocumentProcessor3: {e}")
        return False


def test_text_processing():
    """Test text processing directly"""
    print("\n🔍 Testing text processing...")
    
    try:
        processor = DocumentProcessor(api_key=API_KEY)
        
        # Test text processing
        test_text = "Name: John Doe\nDocument Number: 123456\nDate of Birth: 01/01/1990"
        result = processor._process_text_content(test_text, "test.txt", 0.0)
        
        if result:
            print(f"   ✅ Text processing successful")
            print(f"   Document Type: {result.get('document_type', 'unknown')}")
            print(f"   Status: {result.get('status', 'unknown')}")
            print(f"   Confidence: {result.get('confidence', 0.0):.2f}")
            return True
        else:
            print(f"   ❌ Text processing returned None")
            return False
        
    except Exception as e:
        print(f"   ❌ Error in text processing: {e}")
        return False


def test_file_processing():
    """Test file processing with a temporary file"""
    print("\n🔍 Testing file processing...")
    
    try:
        processor = DocumentProcessor(api_key=API_KEY)
        
        # Create a temporary text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write("DRIVING LICENSE\nName: Jane Smith\nLicense Number: DL123456\nDate of Birth: 15/05/1985")
            temp_file_path = temp_file.name
        
        try:
            # Test file processing
            results = processor.process_file(temp_file_path, min_confidence=0.0)
            
            if results and len(results) > 0:
                print(f"   ✅ File processing successful")
                print(f"   Number of results: {len(results)}")
                result = results[0]
                print(f"   Document Type: {result.get('document_type', 'unknown')}")
                print(f"   Status: {result.get('status', 'unknown')}")
                print(f"   Confidence: {result.get('confidence', 0.0):.2f}")
                return True
            else:
                print(f"   ❌ File processing returned no results")
                return False
        
        finally:
            # Clean up
            try:
                os.unlink(temp_file_path)
            except:
                pass
        
    except Exception as e:
        print(f"   ❌ Error in file processing: {e}")
        return False


def test_api_endpoints():
    """Test API endpoints"""
    print("\n🔍 Testing API endpoints...")
    
    base_url = f"http://{API_HOST}:{API_PORT}"
    
    # Test processor info endpoint
    try:
        response = requests.get(f"{base_url}/api/v1/processor/info", timeout=10)
        if response.status_code == 200:
            info = response.json()
            print(f"   ✅ Processor info endpoint: {response.status_code}")
            print(f"   Processor class: {info.get('processor_info', {}).get('processor_class', 'unknown')}")
            print(f"   Unified processing: {info.get('processor_info', {}).get('unified_processing_enabled', False)}")
        else:
            print(f"   ❌ Processor info endpoint: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Processor info endpoint error: {e}")
        return False
    
    # Test text processing endpoint
    try:
        response = requests.post(
            f"{base_url}/api/v1/processor/text",
            json={"text": "Name: Test User\nID: 789012"},
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Text processing endpoint: {response.status_code}")
            print(f"   Status: {result.get('status', 'unknown')}")
        else:
            print(f"   ❌ Text processing endpoint: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Text processing endpoint error: {e}")
        return False
    
    return True


def test_file_upload_endpoint():
    """Test file upload endpoint"""
    print("\n🔍 Testing file upload endpoint...")
    
    base_url = f"http://{API_HOST}:{API_PORT}"
    
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write("PASSPORT\nName: Alice Johnson\nPassport Number: P123456789\nNationality: USA")
            temp_file_path = temp_file.name
        
        try:
            # Upload file
            with open(temp_file_path, 'rb') as f:
                files = {'file': ('test_document.txt', f, 'text/plain')}
                response = requests.post(
                    f"{base_url}/api/v1/processor",
                    files=files,
                    timeout=60
                )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ File upload endpoint: {response.status_code}")
                print(f"   Status: {result.get('status', 'unknown')}")
                if result.get('result'):
                    doc_type = result['result'].get('document_type', 'unknown')
                    confidence = result['result'].get('confidence', 0.0)
                    print(f"   Document Type: {doc_type}, Confidence: {confidence:.2f}")
                return True
            else:
                print(f"   ❌ File upload endpoint: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        
        finally:
            # Clean up
            try:
                os.unlink(temp_file_path)
            except:
                pass
    
    except Exception as e:
        print(f"   ❌ File upload endpoint error: {e}")
        return False


def main():
    """Main test function"""
    print("🧪 DocumentProcessor3 Methods and API Test")
    print("=" * 50)
    
    # Test 1: DocumentProcessor3 methods
    methods_ok = test_documentprocessor3_methods()
    
    # Test 2: Text processing
    text_ok = test_text_processing()
    
    # Test 3: File processing
    file_ok = test_file_processing()
    
    # Test 4: API endpoints
    api_ok = test_api_endpoints()
    
    # Test 5: File upload endpoint
    upload_ok = test_file_upload_endpoint()
    
    # Summary
    print(f"\n📊 TEST SUMMARY:")
    print(f"   DocumentProcessor3 Methods: {'✅' if methods_ok else '❌'}")
    print(f"   Text Processing: {'✅' if text_ok else '❌'}")
    print(f"   File Processing: {'✅' if file_ok else '❌'}")
    print(f"   API Endpoints: {'✅' if api_ok else '❌'}")
    print(f"   File Upload: {'✅' if upload_ok else '❌'}")
    
    all_passed = all([methods_ok, text_ok, file_ok, api_ok, upload_ok])
    
    if all_passed:
        print(f"\n🎉 All tests passed! DocumentProcessor3 is working correctly.")
    else:
        print(f"\n⚠️ Some tests failed. Check the details above.")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
