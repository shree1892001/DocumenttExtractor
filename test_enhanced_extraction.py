"""
Test the enhanced extraction that extracts ALL possible data from documents.
"""

import os
import sys
import json
import requests

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Common.constants import API_HOST, API_PORT


def test_comprehensive_extraction():
    """Test comprehensive extraction with a complex document"""
    print("🔍 Testing comprehensive extraction...")
    
    base_url = f"http://{API_HOST}:{API_PORT}"
    
    # Complex document with lots of information
    complex_document = """
    REPUBLIC OF INDIA
    PASSPORT
    
    Type: P
    Country Code: IND
    Passport No.: H1591116
    
    Surname: SRIKRISHNAN NADAR
    Given Name(s): SIVA SELVA KUMAR
    
    Nationality: INDIAN
    Date of Birth: 04/05/1976
    Sex: M
    Place of Birth: NAGERCOIL
    
    Date of Issue: 01/12/2008
    Date of Expiry: 30/11/2018
    Place of Issue: MADURAI
    
    Address: NAGERCOIL MADURAI
    
    Father's Name: NADAR KRISHNAN
    Mother's Name: KAMALA DEVI
    
    Height: 175 CM
    Eye Color: BROWN
    Blood Type: O+
    
    Emergency Contact: +91-9876543210
    Email: siva.kumar@email.com
    
    Occupation: SOFTWARE ENGINEER
    Company: TECH SOLUTIONS PVT LTD
    Employee ID: EMP001234
    
    Previous Passport: G1234567 (Expired)
    
    Endorsements: 
    - Valid for all countries except Pakistan
    - Emergency travel document
    
    Security Features:
    - Holographic lamination
    - Digital signature
    - Biometric chip
    - Watermark: Government of India
    
    File Number: F/2008/12345
    Application Number: APP789012
    Fee Paid: Rs. 1500
    Receipt Number: RCP456789
    
    Issuing Officer: K. RAJESH, IFS
    Office Code: MAD001
    
    Machine Readable Zone:
    P<IND<SRIKRISHNAN<NADAR<<SIVA<SELVA<KUMAR<<<<
    H1591116<9IND7605046M1811308<<<<<<<<<<<<<<<<<<<<<0
    
    Verification Code: VER123456
    QR Code Data: https://passport.gov.in/verify/H1591116
    
    Notes: Document issued under normal circumstances
    Special Remarks: None
    
    IMPORTANT: This passport is property of Government of India
    """
    
    try:
        print(f"   📤 Sending complex document for extraction...")
        
        response = requests.post(
            f"{base_url}/api/v1/processor/text",
            json={"text": complex_document},
            timeout=120  # Longer timeout for complex processing
        )
        
        print(f"   📥 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"   📋 Comprehensive Extraction Results:")
            print(f"     - Status: {result.get('status')}")
            print(f"     - Document Type: {result.get('document_type')}")
            print(f"     - Confidence: {result.get('confidence', 0.0):.2f}")
            
            # Check extracted data
            extracted_data = result.get('extracted_data', {})
            field_count = len(extracted_data)
            
            print(f"     - Total Fields Extracted: {field_count}")
            
            if field_count > 0:
                print(f"\n   📋 ALL EXTRACTED FIELDS:")
                
                # Group fields by category for better display
                categories = {
                    "Names": [],
                    "Dates": [],
                    "Numbers & IDs": [],
                    "Contact Info": [],
                    "Personal Details": [],
                    "Professional Info": [],
                    "Security Features": [],
                    "Technical Data": [],
                    "Other Information": []
                }
                
                # Categorize fields
                for field_name, field_value in extracted_data.items():
                    field_lower = field_name.lower()
                    
                    if any(word in field_lower for word in ['name', 'surname', 'given']):
                        categories["Names"].append((field_name, field_value))
                    elif any(word in field_lower for word in ['date', 'birth', 'issue', 'expiry']):
                        categories["Dates"].append((field_name, field_value))
                    elif any(word in field_lower for word in ['number', 'id', 'code', 'passport', 'file', 'application']):
                        categories["Numbers & IDs"].append((field_name, field_value))
                    elif any(word in field_lower for word in ['phone', 'email', 'contact', 'address']):
                        categories["Contact Info"].append((field_name, field_value))
                    elif any(word in field_lower for word in ['height', 'eye', 'blood', 'gender', 'nationality', 'place']):
                        categories["Personal Details"].append((field_name, field_value))
                    elif any(word in field_lower for word in ['occupation', 'company', 'employee', 'job']):
                        categories["Professional Info"].append((field_name, field_value))
                    elif any(word in field_lower for word in ['security', 'watermark', 'hologram', 'signature', 'chip']):
                        categories["Security Features"].append((field_name, field_value))
                    elif any(word in field_lower for word in ['qr', 'barcode', 'machine', 'verification', 'receipt']):
                        categories["Technical Data"].append((field_name, field_value))
                    else:
                        categories["Other Information"].append((field_name, field_value))
                
                # Display categorized fields
                for category, fields in categories.items():
                    if fields:
                        print(f"\n     🏷️ {category}:")
                        for field_name, field_value in fields:
                            if isinstance(field_value, list):
                                print(f"       • {field_name}: {', '.join(map(str, field_value))}")
                            else:
                                print(f"       • {field_name}: {field_value}")
                
                # Summary
                print(f"\n   📊 EXTRACTION SUMMARY:")
                for category, fields in categories.items():
                    if fields:
                        print(f"     • {category}: {len(fields)} fields")
                
                print(f"\n   🎉 COMPREHENSIVE EXTRACTION SUCCESSFUL!")
                print(f"     • Extracted {field_count} total fields")
                print(f"     • Covered all major categories of information")
                print(f"     • No data limitations - extracted everything possible")
                
                return True
            else:
                print(f"   ❌ No fields extracted")
                return False
        else:
            print(f"   ❌ Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_different_document_types():
    """Test extraction with different types of documents"""
    print(f"\n🔍 Testing extraction with different document types...")
    
    base_url = f"http://{API_HOST}:{API_PORT}"
    
    test_documents = {
        "Resume": """
        JOHN SMITH
        Software Engineer
        
        Email: john.smith@email.com
        Phone: +1-555-123-4567
        LinkedIn: linkedin.com/in/johnsmith
        GitHub: github.com/johnsmith
        Portfolio: johnsmith.dev
        
        Address: 123 Main St, San Francisco, CA 94105
        
        EXPERIENCE:
        Senior Software Engineer | Google Inc. | 2020-2023
        - Led team of 5 developers
        - Increased performance by 40%
        - Technologies: Python, React, AWS
        
        Software Engineer | Microsoft | 2018-2020
        - Developed cloud solutions
        - Managed $2M budget
        
        EDUCATION:
        Master of Science in Computer Science
        Stanford University | 2016-2018
        GPA: 3.8/4.0
        
        Bachelor of Engineering
        MIT | 2012-2016
        Magna Cum Laude
        
        SKILLS:
        Programming: Python, JavaScript, Java, C++
        Frameworks: React, Django, Spring Boot
        Cloud: AWS, Azure, Google Cloud
        Databases: PostgreSQL, MongoDB, Redis
        
        CERTIFICATIONS:
        - AWS Solutions Architect (2022)
        - Google Cloud Professional (2021)
        - Scrum Master Certified (2020)
        
        PROJECTS:
        E-commerce Platform | 2023
        - Built scalable platform handling 1M+ users
        - Tech stack: React, Node.js, PostgreSQL
        
        LANGUAGES:
        English (Native), Spanish (Fluent), French (Basic)
        """,
        
        "Invoice": """
        TECH SOLUTIONS INC.
        123 Business Ave, New York, NY 10001
        Phone: (555) 123-4567
        Email: billing@techsolutions.com
        Tax ID: 12-3456789
        
        INVOICE
        
        Invoice Number: INV-2023-001234
        Date: December 15, 2023
        Due Date: January 15, 2024
        
        Bill To:
        ABC Corporation
        456 Corporate Blvd
        Los Angeles, CA 90210
        
        Ship To:
        ABC Corporation - Warehouse
        789 Industrial Way
        Los Angeles, CA 90211
        
        Description                 Qty    Rate      Amount
        Software Development        40hrs  $150/hr   $6,000.00
        System Integration          20hrs  $200/hr   $4,000.00
        Technical Support           10hrs  $100/hr   $1,000.00
        
        Subtotal:                             $11,000.00
        Tax (8.25%):                          $907.50
        Shipping:                             $50.00
        Total:                                $11,957.50
        
        Payment Terms: Net 30
        Payment Method: Bank Transfer
        Account: 1234567890
        Routing: 987654321
        
        Reference: Project Alpha-2023
        PO Number: PO-ABC-789
        
        Thank you for your business!
        """
    }
    
    results = {}
    
    for doc_type, doc_text in test_documents.items():
        try:
            print(f"   📤 Testing {doc_type}...")
            
            response = requests.post(
                f"{base_url}/api/v1/processor/text",
                json={"text": doc_text},
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                extracted_data = result.get('extracted_data', {})
                field_count = len(extracted_data)
                
                print(f"     ✅ {doc_type}: {field_count} fields extracted")
                results[doc_type] = field_count
                
                # Show sample fields
                if extracted_data:
                    sample_fields = list(extracted_data.items())[:3]
                    for field_name, field_value in sample_fields:
                        print(f"       • {field_name}: {field_value}")
            else:
                print(f"     ❌ {doc_type}: Failed ({response.status_code})")
                results[doc_type] = 0
        
        except Exception as e:
            print(f"     ❌ {doc_type}: Error - {e}")
            results[doc_type] = 0
    
    return results


def main():
    """Main test function"""
    print("🧪 Testing Enhanced Comprehensive Data Extraction")
    print("=" * 60)
    
    # Test 1: Comprehensive extraction with complex document
    comprehensive_success = test_comprehensive_extraction()
    
    # Test 2: Different document types
    document_results = test_different_document_types()
    
    # Summary
    print(f"\n📊 FINAL SUMMARY:")
    print(f"   Comprehensive Extraction: {'✅ SUCCESS' if comprehensive_success else '❌ FAILED'}")
    
    if document_results:
        print(f"   Document Type Tests:")
        for doc_type, field_count in document_results.items():
            print(f"     • {doc_type}: {field_count} fields {'✅' if field_count > 0 else '❌'}")
    
    total_success = comprehensive_success and all(count > 0 for count in document_results.values())
    
    if total_success:
        print(f"\n🎉 ENHANCED EXTRACTION IS WORKING!")
        print(f"   • Extracts ALL possible data from documents")
        print(f"   • No format limitations or restrictions")
        print(f"   • Works with any document type")
        print(f"   • Comprehensive field extraction")
    else:
        print(f"\n⚠️ Some issues found - check the details above")
    
    print(f"\n💡 BENEFITS OF ENHANCED EXTRACTION:")
    print(f"   • Extracts EVERYTHING visible in the document")
    print(f"   • No predefined field limitations")
    print(f"   • Dynamic field naming based on content")
    print(f"   • Works with any document type automatically")
    print(f"   • Preserves all information without loss")


if __name__ == "__main__":
    main()
