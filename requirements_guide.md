# 📦 Requirements.txt Guide for Document Processing System

## 🎯 Overview
This document explains the comprehensive requirements.txt file created for your Document Processing System based on DocumentProcessor3.

## 🔧 Core Dependencies Analysis

### **Essential Libraries (Required)**
These libraries are directly used in your codebase and are **mandatory**:

#### **Web Framework & API**
```
fastapi>=0.104.1          # Main web framework (Main.py)
uvicorn[standard]>=0.24.0 # ASGI server
python-multipart>=0.0.6  # File upload support
```

#### **Google AI/ML**
```
google-generativeai>=0.3.0  # Gemini API (DocumentProcessor3.py)
```

#### **Document Processing**
```
PyMuPDF>=1.23.0           # PDF processing (fitz in DocumentProcessor3.py)
python-docx>=0.8.11      # DOCX processing (DocumentProcessor3.py)
```

#### **Image Processing & OCR**
```
Pillow>=10.0.0           # Image processing (PIL in DocumentProcessor3.py)
pytesseract>=0.3.10     # OCR text extraction (DocumentProcessor3.py)
```

#### **Database**
```
psycopg2-binary>=2.9.7  # PostgreSQL (utils/ApplicationConnection.py)
```

#### **Data Processing**
```
pandas>=2.1.0           # Data manipulation (if used)
numpy>=1.24.0           # Numerical operations
```

#### **HTTP & Requests**
```
requests>=2.31.0        # HTTP requests
```

#### **Built-in Libraries Used**
These are part of Python standard library but listed for reference:
- `json`, `re`, `os`, `sys`, `logging`, `tempfile`, `datetime`
- `traceback`, `functools`, `time`, `threading`, `abc`, `io`

### **Development Libraries (Recommended)**
```
pytest>=7.4.0           # Testing framework
pytest-asyncio>=0.21.0  # Async testing
black>=23.0.0           # Code formatting
flake8>=6.0.0           # Code linting
mypy>=1.6.0             # Type checking
```

### **Optional Libraries (From Original Requirements)**
```
streamlit>=1.28.0           # Web UI framework
langchain-google-genai>=1.0.0  # LangChain integration
browser-use>=0.1.0          # Browser automation
playwright>=1.40.0          # Browser automation
```

### **Extended Libraries (For Future Enhancement)**
These are included for potential future features:
- Machine Learning: `scikit-learn`, `tensorflow`, `torch`
- Data Visualization: `matplotlib`, `seaborn`, `plotly`
- Cloud Storage: `boto3`, `google-cloud-storage`
- Monitoring: `prometheus-client`, `statsd`

## 🚀 Installation Instructions

### **1. Minimal Installation (Core Features Only)**
For just the essential document processing features:

```bash
pip install fastapi uvicorn python-multipart google-generativeai PyMuPDF python-docx Pillow pytesseract psycopg2-binary requests
```

### **2. Full Installation (All Dependencies)**
For complete feature set:

```bash
pip install -r requirements.txt
```

### **3. Development Installation**
For development with testing and linting:

```bash
pip install -r requirements.txt
pip install pytest pytest-asyncio black flake8 mypy
```

## 🔍 Dependency Categories

### **🟢 Critical (Must Install)**
- FastAPI ecosystem
- Google Generative AI
- Document processing (PyMuPDF, python-docx)
- Image processing (Pillow, pytesseract)
- Database (psycopg2-binary)

### **🟡 Important (Recommended)**
- Development tools (pytest, black, flake8)
- Security libraries (cryptography)
- Environment management (python-dotenv)

### **🔵 Optional (Nice to Have)**
- Streamlit (if using web UI)
- Machine learning libraries
- Cloud storage clients
- Monitoring tools

### **⚪ Future (For Expansion)**
- Advanced ML frameworks
- Data visualization
- Task queues
- Caching systems

## 🛠 System Requirements

### **Python Version**
- **Minimum**: Python 3.8+
- **Recommended**: Python 3.9+ or 3.10+

### **System Dependencies**
Before installing Python packages, ensure these system dependencies are installed:

#### **For Tesseract OCR:**
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

#### **For PostgreSQL:**
```bash
# Ubuntu/Debian
sudo apt-get install postgresql-dev

# macOS
brew install postgresql

# Windows
# Download from: https://www.postgresql.org/download/windows/
```

## 📝 Usage Examples

### **Basic Installation Script**
```bash
#!/bin/bash
# install_requirements.sh

echo "Installing core dependencies..."
pip install --upgrade pip
pip install fastapi uvicorn python-multipart
pip install google-generativeai
pip install PyMuPDF python-docx
pip install Pillow pytesseract
pip install psycopg2-binary
pip install requests

echo "Installation complete!"
```

### **Development Setup Script**
```bash
#!/bin/bash
# setup_dev.sh

echo "Setting up development environment..."
pip install --upgrade pip
pip install -r requirements.txt
pip install pre-commit
pre-commit install

echo "Development environment ready!"
```

## 🔧 Troubleshooting

### **Common Issues:**

1. **Tesseract not found:**
   ```bash
   # Add tesseract to PATH or install system package
   export PATH="/usr/local/bin:$PATH"
   ```

2. **PostgreSQL compilation errors:**
   ```bash
   # Install development headers
   sudo apt-get install libpq-dev python3-dev
   ```

3. **Pillow installation issues:**
   ```bash
   # Install image libraries
   sudo apt-get install libjpeg-dev zlib1g-dev
   ```

## 📊 File Size & Installation Time

- **Minimal installation**: ~200MB, 2-3 minutes
- **Full installation**: ~2-3GB, 10-15 minutes
- **With ML libraries**: ~5-8GB, 20-30 minutes

## 🎯 Recommendations

### **For Production:**
```
fastapi, uvicorn, google-generativeai, PyMuPDF, 
python-docx, Pillow, pytesseract, psycopg2-binary, 
requests, python-dotenv, gunicorn
```

### **For Development:**
```
All production dependencies + pytest, black, flake8, 
mypy, pre-commit, jupyter
```

### **For Research/ML:**
```
All dependencies + scikit-learn, tensorflow, 
matplotlib, seaborn, jupyter
```

## ✅ Verification

After installation, verify key components:

```python
# test_installation.py
try:
    import fastapi
    import google.generativeai as genai
    import fitz  # PyMuPDF
    from docx import Document
    from PIL import Image
    import pytesseract
    import psycopg2
    print("✅ All core dependencies installed successfully!")
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
```

**Your requirements.txt file is now comprehensive and production-ready!** 🎉📦✨
