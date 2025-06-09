# 🚀 Manual UI Startup Guide

## ❌ **Problem: API Not Running Error**

If you're getting "API is not running in the background" error, follow these steps:

## 🔧 **Solution: Start API First, Then UI**

### **Step 1: Start DocumentProcessorController API**

#### **Option A: Using Main.py (Recommended)**
```bash
# Navigate to your project directory
cd /path/to/your/project

# Start the main application
python Main.py
```

#### **Option B: Using DocumentProcessorController directly**
```bash
# If you have DocumentProcessorController.py in root
python DocumentProcessorController.py
```

#### **Option C: Using Controllers directory**
```bash
# If DocumentProcessorController is in Controllers folder
python -m Controllers.DocumentProcessorController
```

### **Step 2: Verify API is Running**

#### **Check in Browser**
Open your browser and go to:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

#### **Check with curl**
```bash
# Test health endpoint
curl http://localhost:8000/api/v1/health

# Expected response:
{
    "status": "healthy",
    "message": "DocumentProcessor is running"
}
```

#### **Check with Python**
```bash
python -c "
import requests
try:
    response = requests.get('http://localhost:8000/api/v1/health')
    print('✅ API is running:', response.json())
except:
    print('❌ API is not running')
"
```

### **Step 3: Start UI Server**

#### **Open New Terminal**
```bash
# Navigate to UI directory
cd ui

# Start HTTP server
python -m http.server 3000
```

#### **Alternative UI Servers**
```bash
# Option 1: Python 3
python -m http.server 3000

# Option 2: Python 2 (if needed)
python -m SimpleHTTPServer 3000

# Option 3: PHP (if available)
php -S localhost:3000

# Option 4: Node.js (if available)
npx serve . -p 3000
```

### **Step 4: Open UI in Browser**
```bash
# Open your browser to:
http://localhost:3000
```

---

## 🔍 **Troubleshooting Common Issues**

### **Issue 1: "Module not found" when starting API**

#### **Check File Structure**
```bash
# Verify your files exist
ls -la DocumentProcessorController.py
ls -la Main.py
ls -la Controllers/DocumentProcessorController.py
```

#### **Check Python Path**
```bash
# Add current directory to Python path
export PYTHONPATH=$PYTHONPATH:.

# Then try starting again
python Main.py
```

### **Issue 2: "Port already in use"**

#### **Check What's Using Port 8000**
```bash
# Windows
netstat -an | findstr :8000

# macOS/Linux
lsof -i :8000
```

#### **Kill Process Using Port**
```bash
# Windows
taskkill /F /PID <process_id>

# macOS/Linux
kill -9 <process_id>
```

#### **Use Different Port**
```bash
# Start API on different port (if your code supports it)
python Main.py --port 8001

# Update UI to use new port
# Edit ui/script.js and change API_BASE_URL to http://localhost:8001
```

### **Issue 3: "Dependencies missing"**

#### **Install Required Packages**
```bash
# Install FastAPI and dependencies
pip install fastapi uvicorn python-multipart

# Install DocumentProcessor3 dependencies
pip install PyMuPDF python-docx opencv-python pytesseract Pillow numpy

# Install AI model dependencies (if needed)
pip install transformers torch requests
```

### **Issue 4: UI shows "Cannot connect to API"**

#### **Check API URL in UI**
Edit `ui/script.js` and verify the API URL:
```javascript
// Make sure this matches your API server
const API_BASE_URL = 'http://localhost:8000';
const DOCUMENT_PROCESSOR_API = 'http://localhost:8000/api/v1';
```

#### **Check CORS Settings**
Your API might need CORS enabled. Add this to your DocumentProcessorController:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🎯 **Quick Test Commands**

### **Test 1: API Health**
```bash
curl -X GET http://localhost:8000/api/v1/health
```

### **Test 2: API Documentation**
```bash
# Open in browser
open http://localhost:8000/docs
```

### **Test 3: UI Access**
```bash
# Open in browser
open http://localhost:3000
```

### **Test 4: Full Integration**
1. Upload a test document in the UI
2. Check if processing works
3. Verify results display

---

## 📝 **Step-by-Step Checklist**

- [ ] **Step 1**: Start DocumentProcessorController API
  ```bash
  python Main.py
  ```

- [ ] **Step 2**: Verify API is running
  ```bash
  curl http://localhost:8000/api/v1/health
  ```

- [ ] **Step 3**: Start UI server
  ```bash
  cd ui && python -m http.server 3000
  ```

- [ ] **Step 4**: Open UI in browser
  ```bash
  open http://localhost:3000
  ```

- [ ] **Step 5**: Test document upload
  - Upload a test document
  - Verify processing works
  - Check results display

---

## 🚀 **Alternative: One-Command Startup**

Create a simple batch/shell script:

### **Windows (start_all.bat)**
```batch
@echo off
echo Starting DocumentProcessorController...
start /B python Main.py
timeout /t 5
echo Starting UI server...
cd ui
start /B python -m http.server 3000
echo Opening browser...
start http://localhost:3000
```

### **macOS/Linux (start_all.sh)**
```bash
#!/bin/bash
echo "Starting DocumentProcessorController..."
python Main.py &
sleep 5
echo "Starting UI server..."
cd ui
python -m http.server 3000 &
sleep 2
echo "Opening browser..."
open http://localhost:3000
```

---

## ✅ **Success Indicators**

When everything is working correctly:

1. **Terminal 1**: Shows DocumentProcessorController running
   ```
   INFO:     Started server process
   INFO:     Waiting for application startup.
   INFO:     Application startup complete.
   INFO:     Uvicorn running on http://0.0.0.0:8000
   ```

2. **Terminal 2**: Shows UI server running
   ```
   Serving HTTP on 0.0.0.0 port 3000 (http://0.0.0.0:3000/) ...
   ```

3. **Browser**: Shows professional document processing interface

4. **API Health**: Returns healthy status
   ```json
   {
     "status": "healthy",
     "message": "DocumentProcessor is running"
   }
   ```

---

## 🎉 **You're Ready!**

Once both servers are running:
- **UI**: http://localhost:3000
- **API**: http://localhost:8000/api/v1
- **Docs**: http://localhost:8000/docs

**Your DocumentProcessor3 system is now running with the UI!** 🎯📄✨
