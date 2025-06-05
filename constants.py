import os

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# Document Processing Configuration
SUPPORTED_EXTENSIONS = ['.pdf', '.docx', '.jpg', '.jpeg', '.png']
MIN_CONFIDENCE_THRESHOLD = 0.7
MIN_GENUINENESS_SCORE = 0.6
VERIFICATION_THRESHOLD = 0.8

# File Paths
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')
LOG_FILE = 'app.log'

# API Keys
API_KEY = os.getenv("API_KEY", "your_api_key") 