# Document Processing UI - Complete Setup Guide

## 🎯 **System Overview**

This UI system provides a complete document processing solution with:

- **Template Management**: Display and filter available document templates
- **Universal Input**: Accept any document format (PDF, DOCX, Images, Text)
- **Template Matching**: Automatically match documents with best templates
- **Document Classification**: Determine document type based on template matching
- **Data Extraction**: Extract structured data using ConfidentialProcessor
- **Privacy Protection**: Complete local processing for confidential documents
- **Results Display**: Show document type and extracted data with confidence scores

## 🏗️ **Architecture**

```
Frontend (HTML/CSS/JS) ←→ FastAPI Backend ←→ ConfidentialProcessor ←→ TemplateManager
```

### **Components**
1. **Frontend UI** (`ui/` folder)
   - `index.html` - Main interface
   - `styles.css` - Responsive styling
   - `script.js` - JavaScript functionality

2. **API Backend** (`api/` folder)
   - `document_processing_api.py` - FastAPI server

3. **Core Services** (`Services/` folder)
   - `TemplateManager.py` - Template management and matching
   - `ConfidentialProcessor.py` - Document processing with RoBERTa
   - `LocalConfidentialProcessor.py` - 100% offline processing

## 🚀 **Quick Setup**

### **1. Install Dependencies**
```bash
# Install API dependencies
pip install -r requirements_api.txt

# Install system dependencies
# Windows: Install Tesseract-OCR and Poppler
# macOS: brew install tesseract poppler
# Ubuntu: sudo apt-get install tesseract-ocr poppler-utils
```

### **2. Start the API Server**
```bash
# Navigate to project directory
cd /path/to/your/project

# Start the FastAPI server
python api/document_processing_api.py

# Server will start at: http://localhost:8000
```

### **3. Open the UI**
```bash
# Open the UI in your browser
# Method 1: Direct file access
open ui/index.html

# Method 2: Use a local web server (recommended)
cd ui
python -m http.server 3000
# Then open: http://localhost:3000
```

## 📋 **Detailed Setup Instructions**

### **Step 1: Environment Setup**

```bash
# Create virtual environment (recommended)
python -m venv document_processing_env
source document_processing_env/bin/activate  # Linux/Mac
# or
document_processing_env\Scripts\activate     # Windows

# Install Python dependencies
pip install -r requirements_api.txt
```

### **Step 2: System Dependencies**

#### **Windows**
```bash
# Install Tesseract OCR
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Add to PATH: C:\Program Files\Tesseract-OCR

# Install Poppler
# Download from: https://github.com/oschwartz10612/poppler-windows
# Add to PATH: C:\path\to\poppler\bin
```

#### **macOS**
```bash
# Install using Homebrew
brew install tesseract poppler
```

#### **Ubuntu/Debian**
```bash
# Install using apt
sudo apt-get update
sudo apt-get install tesseract-ocr poppler-utils
```

### **Step 3: Verify Installation**

```bash
# Test Tesseract
tesseract --version

# Test Poppler
pdftoppm -h

# Test Python dependencies
python -c "import fastapi, transformers, cv2; print('✅ All dependencies installed')"
```

### **Step 4: Start Services**

#### **Start API Server**
```bash
# Method 1: Direct execution
python api/document_processing_api.py

# Method 2: Using uvicorn
uvicorn api.document_processing_api:app --host 0.0.0.0 --port 8000 --reload

# API will be available at:
# - Main API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - Health Check: http://localhost:8000/health
```

#### **Serve Frontend UI**
```bash
# Method 1: Simple HTTP server
cd ui
python -m http.server 3000

# Method 2: Using Node.js (if available)
cd ui
npx serve .

# Method 3: Direct file access (may have CORS issues)
open ui/index.html
```

## 🎮 **Using the UI**

### **1. Template Management**
- **View Templates**: All available templates are displayed on load
- **Filter by Category**: Use category buttons to filter templates
- **Template Details**: Each card shows required/optional fields

### **2. Document Upload**
- **Drag & Drop**: Drag files directly onto the upload area
- **Browse Files**: Click "Browse Files" to select documents
- **Supported Formats**: PDF, DOCX, JPG, PNG, TIFF, BMP, GIF, TXT
- **Privacy Option**: Check "Use Local Processing Only" for 100% offline

### **3. Processing**
- **Automatic Processing**: Upload triggers automatic template matching
- **Real-time Status**: Processing status shown with spinner
- **Error Handling**: Clear error messages for any issues

### **4. Results Display**
- **Document Type**: Shows matched template and confidence score
- **Extracted Data**: All extracted fields with confidence scores
- **Processing Info**: Details about file format and processing method
- **Privacy Status**: Confirmation of privacy protection level

### **5. Export Results**
- **JSON Export**: Download results as structured JSON file
- **Reset Form**: Process another document easily

## 🔧 **Configuration Options**

### **API Configuration**
Edit `api/document_processing_api.py`:

```python
# Change server settings
uvicorn.run(
    "document_processing_api:app",
    host="0.0.0.0",        # Change host
    port=8000,             # Change port
    reload=True            # Disable in production
)

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### **Frontend Configuration**
Edit `ui/script.js`:

```javascript
// Change API URL
const API_BASE_URL = 'http://localhost:8000';  // Update if API runs elsewhere
```

### **Template Configuration**
Edit `Services/TemplateManager.py` to add custom templates:

```python
# Add new template
self.add_template(DocumentTemplate(
    id="custom_template",
    name="Custom Document Type",
    category=DocumentCategory.CUSTOM,
    description="Your custom document description",
    keywords=["keyword1", "keyword2"],
    patterns=[r"(?i)pattern1", r"(?i)pattern2"],
    required_fields=["field1", "field2"],
    optional_fields=["field3", "field4"]
))
```

## 🔍 **API Endpoints**

### **Template Endpoints**
- `GET /templates` - Get all templates
- `GET /templates/categories` - Get template categories
- `GET /templates/{template_id}` - Get specific template

### **Processing Endpoints**
- `POST /process` - Process uploaded document
- `POST /match-template` - Match text to template

### **Utility Endpoints**
- `GET /` - API information
- `GET /health` - Health check

## 🛠️ **Troubleshooting**

### **Common Issues**

#### **API Server Won't Start**
```bash
# Check if port is in use
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Try different port
uvicorn api.document_processing_api:app --port 8001
```

#### **CORS Errors in Browser**
```bash
# Use local web server instead of file:// protocol
cd ui
python -m http.server 3000
```

#### **Template Loading Fails**
```bash
# Check API health
curl http://localhost:8000/health

# Check templates endpoint
curl http://localhost:8000/templates
```

#### **Document Processing Fails**
```bash
# Check system dependencies
tesseract --version
pdftoppm -h

# Check Python dependencies
python -c "import cv2, pytesseract; print('OCR dependencies OK')"
```

#### **RoBERTa Model Issues**
```bash
# Use local-only processing
# Check "Use Local Processing Only" in UI

# Or disable RoBERTa in API
# Comment out transformers/torch imports in document_processing_api.py
```

### **Performance Optimization**

#### **For Large Documents**
- Use local processing only for faster processing
- Ensure sufficient RAM (4GB+ recommended for RoBERTa)
- Consider batch processing for multiple documents

#### **For Production**
- Use production ASGI server (gunicorn + uvicorn)
- Configure proper CORS origins
- Add authentication if needed
- Use HTTPS for secure document upload

## 🎯 **Usage Examples**

### **Educational Institution**
1. Upload student transcript (PDF)
2. System matches "Student Transcript" template
3. Extracts: student name, ID, GPA, courses
4. Privacy protected (FERPA compliant)

### **Healthcare Organization**
1. Upload medical license (JPG photo)
2. System matches "Medical License" template
3. Extracts: doctor name, license number, expiry
4. Privacy protected (HIPAA compliant)

### **Corporate HR**
1. Upload resume (DOCX)
2. System matches "Resume/CV" template
3. Extracts: name, email, experience, skills
4. Privacy protected (employee data secure)

## ✅ **Success Indicators**

- ✅ API server starts without errors
- ✅ UI loads and displays templates
- ✅ File upload works with drag & drop
- ✅ Document processing completes successfully
- ✅ Results display extracted data with confidence scores
- ✅ Privacy protection status shows correctly
- ✅ Export functionality works

## 🎉 **You're Ready!**

Your Document Processing UI is now fully set up and ready to handle any document format with template-based classification and privacy-protected data extraction!

**Access your system at:**
- **UI**: http://localhost:3000 (or file:// path)
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
