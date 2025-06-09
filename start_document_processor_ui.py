"""
Startup script for Document Processing UI with DocumentProcessorController integration
This script starts the DocumentProcessorController API and serves the UI
"""

import os
import sys
import subprocess
import time
import webbrowser
import threading
from pathlib import Path

def start_document_processor_controller():
    """Start the existing DocumentProcessorController API server"""
    try:
        print("🚀 Starting DocumentProcessorController API...")

        # Try multiple ways to start DocumentProcessorController
        try:
            # Method 1: Try importing DocumentProcessorController directly
            try:
                from Controllers.DocumentProcessorController import router as document_router
                from fastapi import FastAPI
                import uvicorn

                # Create FastAPI app with your router
                app = FastAPI(title="Document Processing API")
                app.include_router(document_router, prefix="/api/v1", tags=["Document Processing"])

                print("📦 DocumentProcessorController imported successfully")

            except ImportError:
                # Method 2: Try importing from Main.py
                try:
                    from Main import app
                    import uvicorn
                    print("📦 Main.py imported successfully")

                except ImportError:
                    # Method 3: Try direct import
                    try:
                        import DocumentProcessorController
                        app = DocumentProcessorController.app
                        import uvicorn
                        print("📦 DocumentProcessorController.py imported successfully")

                    except ImportError as e:
                        print(f"❌ Could not import DocumentProcessorController: {e}")
                        print("Please ensure one of these files exists:")
                        print("   • Controllers/DocumentProcessorController.py")
                        print("   • Main.py")
                        print("   • DocumentProcessorController.py")
                        return False

            print("🔧 Initializing DocumentProcessor3 service...")

            # Start the API server in a separate thread
            def run_api():
                try:
                    uvicorn.run(
                        app,
                        host="0.0.0.0",
                        port=8000,
                        log_level="info",
                        access_log=True
                    )
                except Exception as e:
                    print(f"❌ Error starting API server: {e}")

            api_thread = threading.Thread(target=run_api, daemon=True)
            api_thread.start()

            print("✅ DocumentProcessorController API started on http://localhost:8000")
            print("📊 Available endpoints:")
            print("   • POST /api/v1/processor - Document processing")
            print("   • GET /api/v1/health - Health check")
            print("   • GET /docs - API documentation")

            return True

        except Exception as e:
            print(f"❌ Failed to start DocumentProcessorController: {e}")
            print("Please try starting manually:")
            print("   python Main.py")
            print("   # or")
            print("   python DocumentProcessorController.py")
            return False

    except Exception as e:
        print(f"❌ Failed to start DocumentProcessorController: {e}")
        return False

def start_ui_server():
    """Start a simple HTTP server for the UI"""
    try:
        print("🌐 Starting UI server...")
        
        ui_dir = Path(__file__).parent / "ui"
        if not ui_dir.exists():
            print(f"❌ UI directory not found: {ui_dir}")
            return False
        
        # Change to UI directory
        os.chdir(ui_dir)
        
        # Start HTTP server
        def run_ui_server():
            try:
                import http.server
                import socketserver
                
                PORT = 3000
                Handler = http.server.SimpleHTTPRequestHandler
                
                with socketserver.TCPServer(("", PORT), Handler) as httpd:
                    print(f"✅ UI server started on http://localhost:{PORT}")
                    httpd.serve_forever()
                    
            except Exception as e:
                print(f"❌ Failed to start UI server: {e}")
        
        ui_thread = threading.Thread(target=run_ui_server, daemon=True)
        ui_thread.start()
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to start UI server: {e}")
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'python-multipart',
        'PyMuPDF',
        'python-docx',
        'opencv-python',
        'pytesseract',
        'Pillow',
        'numpy',
        'transformers',  # For DocumentProcessor3 AI models
        'torch',         # For DocumentProcessor3 AI models
        'requests'       # For API calls
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"  ❌ {package}")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Install them with: pip install " + " ".join(missing_packages))
        return False
    
    print("✅ All dependencies are installed")
    return True

def check_system_dependencies():
    """Check system dependencies like Tesseract and Poppler"""
    print("🔍 Checking system dependencies...")
    
    # Check Tesseract
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("  ✅ Tesseract OCR")
        else:
            print("  ❌ Tesseract OCR")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("  ❌ Tesseract OCR not found")
        print("     Install: https://github.com/UB-Mannheim/tesseract/wiki")
        return False
    
    # Check Poppler (for PDF processing)
    try:
        result = subprocess.run(['pdftoppm', '-h'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0 or 'pdftoppm' in result.stderr:
            print("  ✅ Poppler (pdftoppm)")
        else:
            print("  ❌ Poppler (pdftoppm)")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("  ❌ Poppler not found")
        print("     Install: https://github.com/oschwartz10612/poppler-windows")
        return False
    
    print("✅ All system dependencies are available")
    return True

def wait_for_api():
    """Wait for the API to be ready"""
    import requests
    
    print("⏳ Waiting for API to be ready...")
    
    for i in range(30):  # Wait up to 30 seconds
        try:
            response = requests.get("http://localhost:8000/api/v1/health", timeout=2)
            if response.status_code == 200:
                print("✅ API is ready")
                return True
        except requests.exceptions.RequestException:
            pass
        
        time.sleep(1)
        print(f"   Waiting... ({i+1}/30)")
    
    print("❌ API did not start within 30 seconds")
    return False

def open_browser():
    """Open the UI in the default browser"""
    try:
        print("🌐 Opening UI in browser...")
        webbrowser.open("http://localhost:3000")
        print("✅ Browser opened")
    except Exception as e:
        print(f"❌ Failed to open browser: {e}")
        print("Please manually open: http://localhost:3000")

def main():
    """Main startup function"""
    print("DOCUMENT PROCESSING UI - STARTUP")
    print("=" * 50)
    print("🔗 Integrating with DocumentProcessorController")
    print("🎯 Template-based document processing with privacy protection")
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing Python packages and try again")
        return False
    
    if not check_system_dependencies():
        print("\n❌ Please install missing system dependencies and try again")
        return False
    
    # Start DocumentProcessorController API
    if not start_document_processor_controller():
        print("\n❌ Failed to start DocumentProcessorController")
        return False
    
    # Wait for API to be ready
    if not wait_for_api():
        print("\n❌ API failed to start properly")
        return False
    
    # Start UI server
    if not start_ui_server():
        print("\n❌ Failed to start UI server")
        return False
    
    # Wait a moment for UI server to start
    time.sleep(2)
    
    # Open browser
    open_browser()
    
    print("\n" + "=" * 50)
    print("🎉 DOCUMENT PROCESSING UI IS READY!")
    print("=" * 50)
    print("📊 API Server: http://localhost:8000")
    print("🌐 UI Interface: http://localhost:3000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("💡 Health Check: http://localhost:8000/api/v1/health")
    print("\n🔧 Features Available:")
    print("   • Template-based document classification")
    print("   • Universal input format support (PDF, DOCX, Images, Text)")
    print("   • Privacy-protected data extraction")
    print("   • DocumentProcessor3 integration")
    print("   • Real-time processing with confidence scoring")
    print("\n⏹️  Press Ctrl+C to stop the servers")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down servers...")
        print("✅ Goodbye!")
        return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n🛑 Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
