#!/usr/bin/env python3
"""
Quick test to check what endpoints are available on port 9500
"""

import requests
import json

def test_endpoint(url):
    try:
        print(f"Testing: {url}")
        response = requests.get(url, timeout=3)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)}")
            except:
                print(f"Response (text): {response.text[:200]}...")
        else:
            print(f"Error response: {response.text[:200]}...")
        print("-" * 50)
        return response.status_code == 200
    except Exception as e:
        print(f"Failed: {e}")
        print("-" * 50)
        return False

print("🔍 Testing DocumentProcessorController API on port 9500")
print("=" * 60)

endpoints = [
    "http://localhost:9500/",
    "http://localhost:9500/health", 
    "http://localhost:9500/api/v1/health",
    "http://localhost:9500/docs",
    "http://localhost:9500/api/v1/processor"
]

for endpoint in endpoints:
    test_endpoint(endpoint)

print("✅ Test complete!")
print("If any endpoint returned status 200, your API is running correctly.")
print("You can now start the UI with: cd ui && python -m http.server 3000")
