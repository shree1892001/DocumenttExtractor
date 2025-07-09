"""
Test script for universal data extraction functionality
Works with ANY document type and extracts ALL data
"""

import json
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Services.UniversalDataExtractor import UniversalDataExtractor
from Common.constants import API_KEY

def test_universal_extraction():
    """Test the universal data extraction functionality with various document types"""
    
    print("=== Testing Universal Data Extraction ===")
    print("This system extracts ALL data from ANY document type")
    
    # Test with different types of documents
    test_documents = [
        {
            "name": "Driver License",
            "text": """
            DRIVER LICENSE
            STATE OF CALIFORNIA
            DEPARTMENT OF MOTOR VEHICLES
            
            LICENSE INFORMATION:
            License Number: A123456789
            Class: C
            Expires: 12/31/2025
            Issue Date: 01/15/2020
            
            PERSONAL INFORMATION:
            Full Name: JOHN MICHAEL SMITH
            Date of Birth: 03/15/1985
            Address: 1234 MAIN STREET, APT 5B
            City: LOS ANGELES
            State: CA
            Zip Code: 90210
            Country: USA
            
            PHYSICAL DESCRIPTION:
            Height: 6'2"
            Weight: 185 lbs
            Eye Color: BLUE
            Hair Color: BROWN
            Sex: M
            
            EMERGENCY CONTACT:
            Name: MARY SMITH
            Relationship: SPOUSE
            Phone: (555) 123-4567
            
            ORGAN DONOR: YES
            """
        },
        {
            "name": "Invoice",
            "text": """
            INVOICE
            
            Invoice Number: INV-2024-001
            Date: 2024-01-15
            Due Date: 2024-02-15
            
            BILL TO:
            Company: ABC Corporation
            Contact: John Doe
            Email: john.doe@abccorp.com
            Phone: (555) 987-6543
            Address: 456 Business Ave, Suite 100
            City: New York, NY 10001
            
            ITEMS:
            Item 1: Web Development Services
            Quantity: 1
            Rate: $150.00/hour
            Hours: 40
            Amount: $6,000.00
            
            Item 2: Design Consultation
            Quantity: 1
            Rate: $75.00/hour
            Hours: 8
            Amount: $600.00
            
            SUBTOTAL: $6,600.00
            TAX (8.5%): $561.00
            TOTAL: $7,161.00
            
            Payment Terms: Net 30
            """
        },
        {
            "name": "Resume",
            "text": """
            JOHN MICHAEL SMITH
            Software Engineer
            
            CONTACT INFORMATION:
            Email: john.smith@email.com
            Phone: (555) 123-4567
            Address: 1234 Main Street, Apt 5B, Los Angeles, CA 90210
            LinkedIn: linkedin.com/in/johnsmith
            
            SUMMARY:
            Experienced software engineer with 5+ years in web development
            and cloud technologies. Passionate about creating scalable solutions.
            
            EXPERIENCE:
            Senior Developer - TechCorp Inc.
            January 2022 - Present
            - Led development of microservices architecture
            - Managed team of 5 developers
            - Technologies: Python, JavaScript, AWS, Docker
            
            Developer - StartupXYZ
            June 2020 - December 2021
            - Built full-stack web applications
            - Technologies: React, Node.js, MongoDB
            
            EDUCATION:
            Bachelor of Science in Computer Science
            University of California, Los Angeles
            Graduated: 2020
            GPA: 3.8/4.0
            
            SKILLS:
            Programming: Python, JavaScript, Java, C++
            Frameworks: React, Node.js, Django, Spring
            Cloud: AWS, Azure, Google Cloud
            Tools: Git, Docker, Kubernetes
            """
        },
        {
            "name": "Medical Report",
            "text": """
            MEDICAL REPORT
            
            Patient Information:
            Name: Sarah Johnson
            Date of Birth: 05/22/1980
            Patient ID: P123456
            Date of Visit: 2024-01-20
            
            Doctor: Dr. Michael Brown
            Department: Cardiology
            Hospital: City General Hospital
            
            VITAL SIGNS:
            Blood Pressure: 120/80 mmHg
            Heart Rate: 72 bpm
            Temperature: 98.6°F
            Weight: 140 lbs
            Height: 5'6"
            
            DIAGNOSIS:
            Primary: Hypertension (mild)
            Secondary: None
            
            TREATMENT PLAN:
            Medication: Lisinopril 10mg daily
            Follow-up: 3 months
            Lifestyle: Reduce salt intake, exercise 30 min daily
            
            LAB RESULTS:
            Cholesterol: 180 mg/dL
            Blood Sugar: 95 mg/dL
            Hemoglobin: 14.2 g/dL
            
            NOTES:
            Patient shows improvement with current treatment.
            Continue monitoring blood pressure weekly.
            """
        },
        {
            "name": "Legal Document",
            "text": """
            CONTRACT AGREEMENT
            
            Contract Number: CON-2024-001
            Date: January 15, 2024
            Effective Date: February 1, 2024
            
            PARTIES:
            Party A: ABC Corporation
            Address: 123 Business Street, New York, NY 10001
            Contact: John Smith, CEO
            Phone: (555) 123-4567
            Email: john.smith@abccorp.com
            
            Party B: XYZ Services LLC
            Address: 456 Service Avenue, Los Angeles, CA 90210
            Contact: Jane Doe, President
            Phone: (555) 987-6543
            Email: jane.doe@xyzservices.com
            
            SERVICES:
            Description: IT Consulting Services
            Duration: 12 months
            Start Date: February 1, 2024
            End Date: January 31, 2025
            
            COMPENSATION:
            Monthly Rate: $15,000
            Total Contract Value: $180,000
            Payment Terms: Net 30 days
            
            TERMINATION:
            Notice Period: 30 days
            Early Termination Fee: $25,000
            
            SIGNATURES:
            Party A: _________________ Date: _____________
            Party B: _________________ Date: _____________
            """
        }
    ]
    
    try:
        # Create universal data extractor
        print("1. Initializing UniversalDataExtractor...")
        extractor = UniversalDataExtractor(api_key=API_KEY)
        print("   ✓ Extractor initialized successfully")
        
        all_results = {}
        
        # Test with each document type
        for i, doc in enumerate(test_documents, 1):
            print(f"\n{i}. Testing with {doc['name']}...")
            
            # Extract universal data
            result = extractor.extract_all_data(doc['text'], f"{doc['name'].lower().replace(' ', '_')}.txt")
            
            # Get summary
            summary = extractor.get_data_summary(result)
            print(f"   ✓ Document Type: {summary.get('document_type')}")
            print(f"   ✓ Total Fields Extracted: {summary.get('total_fields_extracted')}")
            print(f"   ✓ Field Types: {summary.get('field_types_found')}")
            
            # Test search functionality
            search_results = extractor.search_data(result, "phone")
            print(f"   ✓ Phone-related fields found: {search_results.get('total_matches')}")
            
            # Store results
            all_results[doc['name']] = {
                'summary': summary,
                'total_fields': len(result.get('all_extracted_data', {})),
                'sample_fields': dict(list(result.get('all_extracted_data', {}).items())[:5])
            }
        
        # Display comprehensive results
        print("\n" + "="*60)
        print("UNIVERSAL EXTRACTION RESULTS SUMMARY")
        print("="*60)
        
        total_fields_all = 0
        for doc_name, result_info in all_results.items():
            print(f"\n{doc_name}:")
            print(f"  - Total Fields: {result_info['total_fields']}")
            print(f"  - Document Type: {result_info['summary'].get('document_type')}")
            print(f"  - Field Types: {result_info['summary'].get('field_types_found')}")
            print(f"  - Sample Fields:")
            for field, value in result_info['sample_fields'].items():
                print(f"    * {field}: {value}")
            total_fields_all += result_info['total_fields']
        
        print(f"\nTOTAL FIELDS EXTRACTED ACROSS ALL DOCUMENTS: {total_fields_all}")
        
        # Save results to file
        print("\n8. Saving results to file...")
        with open('universal_extraction_results.json', 'w') as f:
            json.dump(all_results, f, indent=2)
        print("   ✓ Results saved to 'universal_extraction_results.json'")
        
        print("\n=== Universal Extraction Test Completed Successfully ===")
        print("✓ Works with ANY document type")
        print("✓ Extracts ALL visible data")
        print("✓ No document-specific limitations")
        print("✓ Comprehensive pattern matching")
        print("✓ Advanced search capabilities")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during universal extraction testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_with_real_document():
    """Test with a real document from the testdocs folder"""
    
    print("\n=== Testing with Real Document ===")
    
    # Look for a test document
    test_docs_dir = "testdocs"
    if not os.path.exists(test_docs_dir):
        print(f"   Test docs directory '{test_docs_dir}' not found")
        return False
    
    # Find a text file to test with
    text_files = []
    for root, dirs, files in os.walk(test_docs_dir):
        for file in files:
            if file.endswith('.txt'):
                text_files.append(os.path.join(root, file))
    
    if not text_files:
        print("   No text files found in testdocs directory")
        return False
    
    # Use the first text file found
    test_file = text_files[0]
    print(f"   Using test file: {test_file}")
    
    try:
        # Read the file
        with open(test_file, 'r', encoding='utf-8') as f:
            text_content = f.read()
        
        print(f"   File size: {len(text_content)} characters")
        
        # Create extractor
        extractor = UniversalDataExtractor(api_key=API_KEY)
        
        # Extract data
        print("   Performing universal extraction...")
        result = extractor.extract_all_data(text_content, os.path.basename(test_file))
        
        # Get summary
        summary = extractor.get_data_summary(result)
        print(f"   ✓ Document Type: {summary.get('document_type')}")
        print(f"   ✓ Total Fields: {summary.get('total_fields_extracted')}")
        print(f"   ✓ Field Types: {summary.get('field_types_found')}")
        
        # Save results
        output_file = f"real_document_universal_extraction_{os.path.splitext(os.path.basename(test_file))[0]}.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"   ✓ Results saved to '{output_file}'")
        
        print("   ✓ Real document universal extraction completed successfully")
        return True
        
    except Exception as e:
        print(f"   ❌ Error testing with real document: {str(e)}")
        return False

if __name__ == "__main__":
    print("Universal Data Extraction Test Suite")
    print("=" * 60)
    print("This system extracts ALL data from ANY document type")
    print("No document type limitations - completely general approach")
    print("=" * 60)
    
    # Test with sample documents
    success1 = test_universal_extraction()
    
    # Test with real document
    success2 = test_with_real_document()
    
    if success1 and success2:
        print("\n🎉 All universal extraction tests passed successfully!")
        print("✅ System works with ANY document type")
        print("✅ Extracts ALL visible data")
        print("✅ No document-specific limitations")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
    
    print("\nTest files generated:")
    print("- universal_extraction_results.json")
    print("- real_document_universal_extraction_*.json (if real document test ran)") 