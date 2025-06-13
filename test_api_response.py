"""
Test script to check what the API is actually returning vs what the UI expects.
"""

import os
import sys
import json
import requests

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Common.constants import API_HOST, API_PORT


def test_sample_result():
    """Test the sample result endpoint"""
    print("🔍 Testing sample result endpoint...")
    
    base_url = f"http://{API_HOST}:{API_PORT}"
    
    try:
        response = requests.post(f"{base_url}/api/v1/processor/test-result", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Sample result endpoint successful")
            
            # Check the structure
            print(f"   Response structure:")
            print(f"     - status: {result.get('status')}")
            print(f"     - message: {result.get('message')}")
            
            if 'result' in result:
                doc_result = result['result']
                print(f"     - result.status: {doc_result.get('status')}")
                print(f"     - result.document_type: {doc_result.get('document_type')}")
                print(f"     - result.confidence: {doc_result.get('confidence')}")
                
                if 'extracted_data' in doc_result:
                    extracted_data = doc_result['extracted_data']
                    print(f"     - result.extracted_data.data: {extracted_data.get('data', {})}")
                    print(f"     - result.extracted_data.confidence: {extracted_data.get('confidence')}")
                
                print(f"\n   📋 Full sample result structure:")
                print(json.dumps(result, indent=2))
                
            return result
        else:
            print(f"   ❌ Sample result endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    
    except Exception as e:
        print(f"   ❌ Error testing sample result: {e}")
        return None


def test_text_processing_with_resume():
    """Test text processing with resume data"""
    print("\n🔍 Testing text processing with resume...")
    
    base_url = f"http://{API_HOST}:{API_PORT}"
    
    # Simple resume text that should extract well
    resume_text = """
    ALICE JOHNSON
    Software Engineer
    
    Email: alice.johnson@tech.com
    Phone: +1 555-987-6543
    Location: Seattle, WA
    LinkedIn: linkedin.com/in/alicejohnson
    
    EXPERIENCE:
    Senior Software Engineer | Microsoft | 2020 - Present
    • Developed cloud services using Python and Azure
    • Led team of 4 engineers
    • Improved system performance by 40%
    
    Software Engineer | Amazon | 2018 - 2020
    • Built e-commerce features using Java and AWS
    • Implemented microservices architecture
    
    EDUCATION:
    MS Computer Science | University of Washington | 2016 - 2018
    BS Computer Science | UC Berkeley | 2012 - 2016
    
    SKILLS:
    Languages: Python, Java, JavaScript, C++
    Frameworks: Django, Spring Boot, React
    Cloud: AWS, Azure, Docker, Kubernetes
    """
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/processor/text",
            json={"text": resume_text},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Text processing successful")
            
            # Check the structure
            print(f"   Response structure:")
            print(f"     - status: {result.get('status')}")
            print(f"     - message: {result.get('message')}")
            
            if 'result' in result:
                doc_result = result['result']
                print(f"     - result.status: {doc_result.get('status')}")
                print(f"     - result.document_type: {doc_result.get('document_type')}")
                print(f"     - result.confidence: {doc_result.get('confidence')}")
                
                if 'extracted_data' in doc_result:
                    extracted_data = doc_result['extracted_data']
                    data = extracted_data.get('data', {})
                    print(f"     - result.extracted_data.data fields: {list(data.keys())}")
                    print(f"     - result.extracted_data.confidence: {extracted_data.get('confidence')}")
                    
                    if data:
                        print(f"\n   📋 Extracted data:")
                        for key, value in data.items():
                            if isinstance(value, list):
                                print(f"     {key}: {', '.join(map(str, value))}")
                            else:
                                print(f"     {key}: {value}")
                    else:
                        print(f"   ❌ No data in extracted_data.data")
                else:
                    print(f"   ❌ No extracted_data in result")
                
                # Show the full result structure for debugging
                print(f"\n   📋 Full result structure (first 1000 chars):")
                result_str = json.dumps(result, indent=2)
                print(result_str[:1000] + ("..." if len(result_str) > 1000 else ""))
                
            return result
        else:
            print(f"   ❌ Text processing failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    
    except Exception as e:
        print(f"   ❌ Error testing text processing: {e}")
        return None


def compare_results(sample_result, actual_result):
    """Compare the sample result with actual result to find differences"""
    print("\n🔍 Comparing sample vs actual results...")
    
    if not sample_result or not actual_result:
        print("   ❌ Cannot compare - one or both results are missing")
        return
    
    # Extract the result objects
    sample_doc = sample_result.get('result', {})
    actual_doc = actual_result.get('result', {})
    
    # Compare key fields
    comparisons = [
        ("status", sample_doc.get('status'), actual_doc.get('status')),
        ("document_type", sample_doc.get('document_type'), actual_doc.get('document_type')),
        ("confidence", sample_doc.get('confidence'), actual_doc.get('confidence')),
    ]
    
    print("   📊 Field comparison:")
    for field, sample_val, actual_val in comparisons:
        match = "✅" if sample_val == actual_val else "❌"
        print(f"     {match} {field}: sample='{sample_val}' vs actual='{actual_val}'")
    
    # Compare extracted data structure
    sample_data = sample_doc.get('extracted_data', {}).get('data', {})
    actual_data = actual_doc.get('extracted_data', {}).get('data', {})
    
    print(f"   📋 Extracted data comparison:")
    print(f"     Sample data fields: {list(sample_data.keys())}")
    print(f"     Actual data fields: {list(actual_data.keys())}")
    print(f"     Sample data count: {len(sample_data)}")
    print(f"     Actual data count: {len(actual_data)}")
    
    if len(actual_data) == 0:
        print(f"   ❌ ISSUE: Actual result has no extracted data!")
        print(f"   🔍 Check if the processing is working but data is not being formatted correctly")
    elif len(actual_data) > 0:
        print(f"   ✅ Actual result has extracted data - UI issue might be elsewhere")


def main():
    """Main test function"""
    print("🧪 Testing API Response Format")
    print("=" * 50)
    
    # Test 1: Sample result (what should work)
    sample_result = test_sample_result()
    
    # Test 2: Actual text processing
    actual_result = test_text_processing_with_resume()
    
    # Test 3: Compare results
    compare_results(sample_result, actual_result)
    
    # Summary
    print(f"\n📊 SUMMARY:")
    if sample_result:
        print(f"   ✅ Sample result endpoint works")
    else:
        print(f"   ❌ Sample result endpoint failed")
    
    if actual_result:
        actual_data = actual_result.get('result', {}).get('extracted_data', {}).get('data', {})
        if actual_data:
            print(f"   ✅ Actual processing extracts data ({len(actual_data)} fields)")
        else:
            print(f"   ❌ Actual processing extracts no data")
    else:
        print(f"   ❌ Actual processing failed")
    
    print(f"\n💡 RECOMMENDATIONS:")
    if sample_result and actual_result:
        actual_data = actual_result.get('result', {}).get('extracted_data', {}).get('data', {})
        if actual_data:
            print(f"   • API is working and extracting data correctly")
            print(f"   • Issue might be in the UI parsing the response")
            print(f"   • Check if UI expects different field names or structure")
        else:
            print(f"   • API response format is correct but no data is extracted")
            print(f"   • Check the document processing logic")
    else:
        print(f"   • Fix API endpoints first before debugging UI issues")


if __name__ == "__main__":
    main()
