"""
Simple test to verify API startup with DocumentProcessor3.
"""

import os
import sys
import time
import requests
import subprocess
import logging

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Common.constants import API_HOST, API_PORT

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_basic_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing basic imports...")
    
    try:
        from Services.DocumentProcessor3 import DocumentProcessor
        from Common.constants import API_KEY
        print("   ✅ DocumentProcessor3 imported successfully")
        
        # Test initialization
        processor = DocumentProcessor(api_key=API_KEY)
        print("   ✅ DocumentProcessor3 initialized successfully")
        return True
        
    except Exception as e:
        print(f"   ❌ Import/initialization failed: {e}")
        return False


def test_controller_imports():
    """Test if controllers can be imported"""
    print("\n🔍 Testing controller imports...")
    
    try:
        from Controllers.DocumentProcessorController import router as document_router
        print("   ✅ DocumentProcessorController imported successfully")
        
        from Controllers.TemplateController import router as template_router
        print("   ✅ TemplateController imported successfully")
        return True
        
    except Exception as e:
        print(f"   ❌ Controller import failed: {e}")
        return False


def start_api_in_background():
    """Start the API server in background"""
    print(f"\n🚀 Starting API server on {API_HOST}:{API_PORT}...")
    
    try:
        # Start the server
        process = subprocess.Popen(
            [sys.executable, "Main.py"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Monitor output for a few seconds
        start_time = time.time()
        output_lines = []
        
        while time.time() - start_time < 10:  # Wait up to 10 seconds
            if process.poll() is not None:
                # Process has terminated
                stdout, _ = process.communicate()
                print(f"   ❌ API server terminated early")
                print(f"   Output: {stdout}")
                return None
            
            # Check if server is responding
            try:
                response = requests.get(f"http://{API_HOST}:{API_PORT}/health", timeout=2)
                if response.status_code == 200:
                    print("   ✅ API server started and responding")
                    return process
            except requests.exceptions.ConnectionError:
                pass  # Server not ready yet
            except Exception as e:
                print(f"   ⚠️ Error checking server: {e}")
            
            time.sleep(1)
        
        # If we get here, server didn't respond in time
        if process.poll() is None:
            print("   ⚠️ Server started but not responding to health checks")
            return process
        else:
            print("   ❌ Server failed to start")
            return None
            
    except Exception as e:
        print(f"   ❌ Failed to start server: {e}")
        return None


def test_api_endpoints(max_wait=30):
    """Test API endpoints"""
    print(f"\n🔍 Testing API endpoints...")
    
    base_url = f"http://{API_HOST}:{API_PORT}"
    
    endpoints = [
        ("/", "Root endpoint"),
        ("/health", "Health check"),
        ("/api/v1/health", "API health check"),
        ("/docs", "API documentation")
    ]
    
    # Wait for server to be ready
    start_time = time.time()
    server_ready = False
    
    while time.time() - start_time < max_wait:
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                server_ready = True
                break
        except:
            pass
        time.sleep(2)
    
    if not server_ready:
        print("   ❌ Server not ready after waiting")
        return False
    
    # Test endpoints
    all_passed = True
    for endpoint, description in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ {description}: {response.status_code}")
            else:
                print(f"   ❌ {description}: {response.status_code}")
                all_passed = False
                
        except Exception as e:
            print(f"   ❌ {description}: {e}")
            all_passed = False
    
    return all_passed


def test_document_processing_endpoint():
    """Test the document processing endpoint with text"""
    print(f"\n🔍 Testing document processing endpoint...")
    
    base_url = f"http://{API_HOST}:{API_PORT}"
    
    # Test text processing endpoint
    try:
        url = f"{base_url}/api/v1/processor/text"
        test_data = {
            "text": "Name: John Doe\nDocument Number: 123456\nDate of Birth: 01/01/1990"
        }
        
        response = requests.post(url, json=test_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Text processing endpoint: {response.status_code}")
            print(f"   Status: {result.get('status', 'unknown')}")
            if result.get('result'):
                doc_type = result['result'].get('document_type', 'unknown')
                confidence = result['result'].get('confidence', 0.0)
                print(f"   Document Type: {doc_type}, Confidence: {confidence:.2f}")
            return True
        else:
            print(f"   ❌ Text processing endpoint: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Text processing endpoint error: {e}")
        return False


def main():
    """Main test function"""
    print("🧪 Simple API Test with DocumentProcessor3")
    print("=" * 50)
    
    # Test 1: Basic imports
    if not test_basic_imports():
        print("\n❌ Basic imports failed. Cannot proceed.")
        return False
    
    # Test 2: Controller imports
    if not test_controller_imports():
        print("\n❌ Controller imports failed. Cannot proceed.")
        return False
    
    # Test 3: Start API server
    server_process = start_api_in_background()
    if not server_process:
        print("\n❌ Failed to start API server.")
        return False
    
    try:
        # Test 4: Test endpoints
        endpoints_ok = test_api_endpoints()
        
        # Test 5: Test document processing
        processing_ok = test_document_processing_endpoint()
        
        if endpoints_ok and processing_ok:
            print("\n🎉 All tests passed! API is working correctly with DocumentProcessor3.")
            result = True
        else:
            print("\n⚠️ Some tests failed, but API is running.")
            result = False
    
    finally:
        # Clean up: terminate the server process
        if server_process:
            print(f"\n🛑 Stopping API server...")
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
                print("   ✅ API server stopped")
            except subprocess.TimeoutExpired:
                server_process.kill()
                print("   ⚠️ API server force killed")
    
    return result


if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ API test completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ API test had issues!")
        sys.exit(1)
