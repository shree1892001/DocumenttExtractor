"""
Test script to verify API startup and basic functionality.
"""

import os
import sys
import time
import requests
import subprocess
import threading
import logging

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Common.constants import API_HOST, API_PORT

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        from fastapi import FastAPI
        print("   ✅ FastAPI imported successfully")
    except ImportError as e:
        print(f"   ❌ FastAPI import failed: {e}")
        return False
    
    try:
        import uvicorn
        print("   ✅ Uvicorn imported successfully")
    except ImportError as e:
        print(f"   ❌ Uvicorn import failed: {e}")
        return False
    
    try:
        from Controllers.DocumentProcessorController import router as document_router
        print("   ✅ DocumentProcessorController imported successfully")
    except ImportError as e:
        print(f"   ❌ DocumentProcessorController import failed: {e}")
        return False
    
    try:
        from Controllers.TemplateController import router as template_router
        print("   ✅ TemplateController imported successfully")
    except ImportError as e:
        print(f"   ❌ TemplateController import failed: {e}")
        return False
    
    try:
        from Services.TemplateService import TemplateService
        print("   ✅ TemplateService imported successfully")
    except ImportError as e:
        print(f"   ❌ TemplateService import failed: {e}")
        return False
    
    try:
        from Services.DocumentProcessor3 import DocumentProcessor
        print("   ✅ DocumentProcessor3 imported successfully")
    except ImportError as e:
        print(f"   ❌ DocumentProcessor3 import failed: {e}")
        return False
    
    try:
        from Common.constants import API_HOST, API_PORT, API_KEY
        print(f"   ✅ Constants imported successfully (Host: {API_HOST}, Port: {API_PORT})")
    except ImportError as e:
        print(f"   ❌ Constants import failed: {e}")
        return False
    
    return True


def test_service_initialization():
    """Test if services can be initialized"""
    print("\n🔍 Testing service initialization...")
    
    try:
        from Services.TemplateService import TemplateService
        template_service = TemplateService()
        print("   ✅ TemplateService initialized successfully")
    except Exception as e:
        print(f"   ❌ TemplateService initialization failed: {e}")
        return False
    
    try:
        from Services.DocumentProcessor3 import DocumentProcessor
        from Common.constants import API_KEY
        processor = DocumentProcessor(api_key=API_KEY)
        print("   ✅ DocumentProcessor initialized successfully")
    except Exception as e:
        print(f"   ❌ DocumentProcessor initialization failed: {e}")
        return False
    
    return True


def test_fastapi_app():
    """Test if FastAPI app can be created"""
    print("\n🔍 Testing FastAPI app creation...")
    
    try:
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        
        app = FastAPI(
            title="Test Document Processing API",
            description="Test API",
            version="1.0.0"
        )
        
        app.add_middleware(
            CORSMiddleware,
            allow_origins=['*'],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        @app.get("/test")
        async def test_endpoint():
            return {"status": "ok"}
        
        print("   ✅ FastAPI app created successfully")
        return True
        
    except Exception as e:
        print(f"   ❌ FastAPI app creation failed: {e}")
        return False


def start_api_server():
    """Start the API server in a subprocess"""
    print(f"\n🚀 Starting API server on {API_HOST}:{API_PORT}...")
    
    try:
        # Start the server
        process = subprocess.Popen(
            [sys.executable, "Main.py"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a bit for the server to start
        time.sleep(5)
        
        # Check if process is still running
        if process.poll() is None:
            print("   ✅ API server started successfully")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"   ❌ API server failed to start")
            print(f"   STDOUT: {stdout}")
            print(f"   STDERR: {stderr}")
            return None
            
    except Exception as e:
        print(f"   ❌ Failed to start API server: {e}")
        return None


def test_api_endpoints(max_retries=5):
    """Test API endpoints"""
    print(f"\n🔍 Testing API endpoints...")
    
    base_url = f"http://{API_HOST}:{API_PORT}"
    
    endpoints_to_test = [
        "/",
        "/health",
        "/api/v1/health"
    ]
    
    for retry in range(max_retries):
        print(f"   Attempt {retry + 1}/{max_retries}")
        
        all_passed = True
        for endpoint in endpoints_to_test:
            try:
                url = f"{base_url}{endpoint}"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    print(f"   ✅ {endpoint}: {response.status_code}")
                else:
                    print(f"   ❌ {endpoint}: {response.status_code}")
                    all_passed = False
                    
            except requests.exceptions.ConnectionError:
                print(f"   ⏳ {endpoint}: Connection refused (server may still be starting)")
                all_passed = False
            except Exception as e:
                print(f"   ❌ {endpoint}: {e}")
                all_passed = False
        
        if all_passed:
            print("   ✅ All endpoints responding correctly")
            return True
        
        if retry < max_retries - 1:
            print("   ⏳ Waiting 3 seconds before retry...")
            time.sleep(3)
    
    print("   ❌ Some endpoints failed after all retries")
    return False


def main():
    """Main test function"""
    print("🧪 API Startup Test Suite")
    print("=" * 50)
    
    # Test 1: Imports
    if not test_imports():
        print("\n❌ Import test failed. Cannot proceed.")
        return False
    
    # Test 2: Service initialization
    if not test_service_initialization():
        print("\n❌ Service initialization test failed. Cannot proceed.")
        return False
    
    # Test 3: FastAPI app creation
    if not test_fastapi_app():
        print("\n❌ FastAPI app test failed. Cannot proceed.")
        return False
    
    # Test 4: Start API server
    server_process = start_api_server()
    if not server_process:
        print("\n❌ Failed to start API server.")
        return False
    
    try:
        # Test 5: Test endpoints
        endpoints_ok = test_api_endpoints()
        
        if endpoints_ok:
            print("\n🎉 All tests passed! API is working correctly.")
            result = True
        else:
            print("\n⚠️ API started but some endpoints are not responding correctly.")
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
        print("\n✅ API startup test completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ API startup test failed!")
        sys.exit(1)
