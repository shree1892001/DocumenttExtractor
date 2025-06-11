#!/usr/bin/env python3
"""
Test script to verify DocumentProcessorController API endpoints are working
"""

import requests
import json
import sys

def test_endpoint(url, description):
    """Test a single endpoint"""
    try:
        print(f"🔍 Testing {description}: {url}")
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {description} - SUCCESS")
            print(f"   Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ {description} - FAILED (Status: {response.status_code})")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ {description} - CONNECTION FAILED")
        print(f"   Cannot connect to {url}")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ {description} - TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {str(e)}")
        return False

def main():
    """Test all API endpoints"""
    print("🚀 Testing DocumentProcessorController API Endpoints")
    print("=" * 60)
    
    base_url = "http://localhost:9500"
    
    endpoints = [
        (f"{base_url}/", "Root Endpoint"),
        (f"{base_url}/health", "Health Check"),
        (f"{base_url}/api/v1/health", "API v1 Health Check"),
        (f"{base_url}/docs", "API Documentation"),
        (f"{base_url}/openapi.json", "OpenAPI Schema")
    ]
    
    results = []
    
    for url, description in endpoints:
        success = test_endpoint(url, description)
        results.append((description, success))
        print("-" * 60)
    
    # Summary
    print("\n📊 SUMMARY")
    print("=" * 60)
    
    successful = 0
    total = len(results)
    
    for description, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {description}")
        if success:
            successful += 1
    
    print(f"\nResults: {successful}/{total} endpoints working")
    
    if successful > 0:
        print("\n🎉 API is accessible! You can now start the UI.")
        print("To start the UI:")
        print("   cd ui")
        print("   python -m http.server 3000")
        print("   # Then open: http://localhost:3000")
        return True
    else:
        print("\n❌ API is not accessible. Please check:")
        print("   1. Is Main.py running?")
        print("   2. Is it running on port 9500?")
        print("   3. Are there any error messages in the Main.py console?")
        return False

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
