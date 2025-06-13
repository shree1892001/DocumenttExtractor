"""
Test script to verify the data extraction fixes.
"""

import os
import sys
import json
import requests

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Services.DocumentProcessor3 import DocumentProcessor
from Common.constants import API_KEY, API_HOST, API_PORT


def test_resume_processing():
    """Test resume processing with the fixes"""
    print("🔍 Testing resume processing with fixes...")
    
    # Sample resume text similar to what was in the logs
    resume_text = """
    YOGITA CHOUHAN
    UI/UX Designer
    
    Contact Information:
    Email: yogita.chouhan@email.com
    Phone: +91 9876543210
    Location: Indore, India
    Portfolio: https://www.behance.net/yogitachouhan
    
    PROFESSIONAL EXPERIENCE:
    
    Senior UI/UX Designer | TechCorp India | 2021 - Present
    • Led design for mobile applications with 1M+ users
    • Conducted user research and usability testing
    • Collaborated with cross-functional teams
    • Improved user engagement by 40%
    
    UI Designer | StartupXYZ | 2019 - 2021
    • Designed responsive web interfaces
    • Created wireframes and prototypes
    • Worked with development teams on implementation
    
    EDUCATION:
    Bachelor of Design (B.Des) | National Institute of Design | 2015 - 2019
    Specialization: Interaction Design
    
    SKILLS:
    Design Tools: Adobe XD, Sketch, Figma, InVision, Zeplin, Photoshop, Illustrator
    Technologies: JavaScript, HTML, CSS, React basics
    Research: User interviews, Usability testing, A/B testing
    
    PROJECTS:
    E-commerce Mobile App | 2022
    • Designed complete user journey for shopping app
    • Increased conversion rate by 25%
    
    Healthcare Dashboard | 2021
    • Created admin dashboard for healthcare providers
    • Improved workflow efficiency by 30%
    
    CERTIFICATIONS:
    • Google UX Design Certificate (2020)
    • Adobe Certified Expert (2019)
    """
    
    try:
        processor = DocumentProcessor(api_key=API_KEY)
        
        print(f"   Processing resume text ({len(resume_text)} characters)...")
        
        # Test direct text processing
        result = processor._process_text_content(resume_text, "yogita_resume.txt", 0.0)
        
        if result:
            print(f"   ✅ Processing successful")
            print(f"   Document Type: {result.get('document_type', 'unknown')}")
            print(f"   Status: {result.get('status', 'unknown')}")
            print(f"   Confidence: {result.get('confidence', 0.0):.2f}")
            
            extracted_data = result.get('extracted_data', {}).get('data', {})
            print(f"   Extracted Data Fields: {len(extracted_data)}")
            
            if extracted_data:
                print(f"   📋 Extracted Information:")
                for key, value in extracted_data.items():
                    if isinstance(value, list):
                        print(f"     {key}: {', '.join(map(str, value))}")
                    else:
                        print(f"     {key}: {value}")
                
                # Check for key resume fields
                key_fields = ['Name', 'portfolio_url', 'tools', 'languages_and_technologies']
                found_fields = [field for field in key_fields if field in extracted_data]
                print(f"   ✅ Found {len(found_fields)}/{len(key_fields)} key resume fields: {found_fields}")
                
                return True
            else:
                print(f"   ❌ No extracted data found")
                return False
        else:
            print(f"   ❌ Processing returned None")
            return False
        
    except Exception as e:
        print(f"   ❌ Error in resume processing: {e}")
        return False


def test_api_with_resume():
    """Test API endpoint with resume data"""
    print("\n🔍 Testing API with resume data...")
    
    base_url = f"http://{API_HOST}:{API_PORT}"
    
    resume_text = """
    JOHN SMITH
    Software Engineer
    
    Email: john.smith@tech.com
    Phone: +1 555-123-4567
    LinkedIn: linkedin.com/in/johnsmith
    GitHub: github.com/johnsmith
    
    EXPERIENCE:
    Senior Software Engineer | Google | 2020 - Present
    • Developed scalable microservices using Python and Go
    • Led team of 5 engineers
    • Improved system performance by 50%
    
    Software Engineer | Microsoft | 2018 - 2020
    • Built web applications using React and Node.js
    • Implemented CI/CD pipelines
    
    EDUCATION:
    MS Computer Science | Stanford University | 2016 - 2018
    BS Computer Science | UC Berkeley | 2012 - 2016
    
    SKILLS:
    Languages: Python, JavaScript, Go, Java, C++
    Frameworks: React, Node.js, Django, Flask
    Tools: Docker, Kubernetes, AWS, Git
    """
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/processor/text",
            json={"text": resume_text},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ API processing successful")
            print(f"   Status: {result.get('status', 'unknown')}")
            
            if result.get('result'):
                doc_result = result['result']
                print(f"   Document Type: {doc_result.get('document_type', 'unknown')}")
                print(f"   Confidence: {doc_result.get('confidence', 0.0):.2f}")
                
                extracted_data = doc_result.get('extracted_data', {}).get('data', {})
                print(f"   Extracted Data Fields: {len(extracted_data)}")
                
                if extracted_data:
                    print(f"   📋 Key Extracted Information:")
                    # Show most relevant fields
                    important_fields = ['Name', 'Email', 'Phone', 'LinkedIn', 'GitHub', 'Languages', 'Frameworks', 'Tools']
                    for field in important_fields:
                        if field in extracted_data:
                            value = extracted_data[field]
                            if isinstance(value, list):
                                print(f"     {field}: {', '.join(map(str, value))}")
                            else:
                                print(f"     {field}: {value}")
                    
                    return True
                else:
                    print(f"   ❌ No extracted data in API result")
                    return False
            else:
                print(f"   ❌ No result in API response")
                return False
        else:
            print(f"   ❌ API request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    except Exception as e:
        print(f"   ❌ Error testing API: {e}")
        return False


def test_multi_chunk_processing():
    """Test multi-chunk processing and merging"""
    print("\n🔍 Testing multi-chunk processing...")
    
    # Create a longer resume that will be split into chunks
    long_resume = """
    ALICE JOHNSON
    Senior Product Manager
    
    Contact: alice.johnson@company.com | +1 555-987-6543 | San Francisco, CA
    LinkedIn: linkedin.com/in/alicejohnson | Portfolio: alicejohnson.com
    
    PROFESSIONAL SUMMARY
    Experienced Product Manager with 8+ years in tech industry, specializing in B2B SaaS products.
    Led cross-functional teams to deliver products used by 10M+ users globally.
    
    
    
    PROFESSIONAL EXPERIENCE
    
    Senior Product Manager | Salesforce | 2020 - Present
    • Led product strategy for CRM platform serving 150K+ businesses
    • Managed roadmap for team of 15 engineers and 5 designers
    • Increased user engagement by 45% through data-driven feature development
    • Launched 3 major product features generating $50M+ ARR
    
    Product Manager | Slack | 2018 - 2020
    • Owned messaging platform features used by 12M+ daily active users
    • Collaborated with engineering, design, and data science teams
    • Reduced customer churn by 20% through improved onboarding flow
    
    Associate Product Manager | Uber | 2016 - 2018
    • Managed rider experience features for mobile application
    • Conducted user research and A/B testing for feature validation
    • Improved ride completion rate by 15%
    
    
    
    EDUCATION
    
    MBA | Stanford Graduate School of Business | 2014 - 2016
    Concentration: Technology and Innovation
    
    BS Computer Science | UC Berkeley | 2010 - 2014
    Magna Cum Laude, Phi Beta Kappa
    
    
    
    SKILLS & CERTIFICATIONS
    
    Technical Skills: SQL, Python, Tableau, Figma, Jira, Confluence
    Product Skills: User Research, A/B Testing, Analytics, Roadmap Planning
    Certifications: Certified Scrum Product Owner (CSPO), Google Analytics
    """
    
    try:
        processor = DocumentProcessor(api_key=API_KEY)
        
        print(f"   Processing long resume ({len(long_resume)} characters)...")
        
        # This should trigger multi-chunk processing
        results = processor._process_multiple_documents(long_resume, "alice_resume.txt", 0.0)
        
        if results:
            print(f"   ✅ Multi-chunk processing successful")
            print(f"   Number of results: {len(results)}")
            
            for i, result in enumerate(results):
                print(f"   Result {i+1}:")
                print(f"     Document Type: {result.get('document_type', 'unknown')}")
                print(f"     Confidence: {result.get('confidence', 0.0):.2f}")
                
                extracted_data = result.get('extracted_data', {}).get('data', {})
                print(f"     Extracted Fields: {len(extracted_data)}")
                
                if result.get('chunk_info'):
                    chunk_info = result['chunk_info']
                    print(f"     Chunk Info: {chunk_info.get('total_chunks', 0)} chunks, {chunk_info.get('chunks_with_data', 0)} with data")
            
            return True
        else:
            print(f"   ❌ Multi-chunk processing returned no results")
            return False
        
    except Exception as e:
        print(f"   ❌ Error in multi-chunk processing: {e}")
        return False


def main():
    """Main test function"""
    print("🧪 Testing Data Extraction Fixes")
    print("=" * 50)
    
    # Test 1: Direct resume processing
    direct_ok = test_resume_processing()
    
    # Test 2: API with resume
    api_ok = test_api_with_resume()
    
    # Test 3: Multi-chunk processing
    multi_chunk_ok = test_multi_chunk_processing()
    
    # Summary
    print(f"\n📊 TEST SUMMARY:")
    print(f"   Direct Resume Processing: {'✅' if direct_ok else '❌'}")
    print(f"   API Resume Processing: {'✅' if api_ok else '❌'}")
    print(f"   Multi-chunk Processing: {'✅' if multi_chunk_ok else '❌'}")
    
    all_passed = all([direct_ok, api_ok, multi_chunk_ok])
    
    if all_passed:
        print(f"\n🎉 All tests passed! Data extraction fixes are working.")
    else:
        print(f"\n⚠️ Some tests failed. Check the details above.")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
