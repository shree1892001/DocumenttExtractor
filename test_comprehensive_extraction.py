"""
Test script for comprehensive data extraction functionality
"""

import json
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Services.ComprehensiveDataExtractor import ComprehensiveDataExtractor
from Common.constants import API_KEY

def test_comprehensive_extraction():
    """Test the comprehensive data extraction functionality"""
    
    print("=== Testing Comprehensive Data Extraction ===")
    
    # Sample document text for testing
    sample_text = """
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
    
    RESTRICTIONS: NONE
    ENDORSEMENTS: NONE
    
    EMERGENCY CONTACT:
    Name: MARY SMITH
    Relationship: SPOUSE
    Phone: (555) 123-4567
    
    ORGAN DONOR: YES
    
    SIGNATURE: _________________
    
    OFFICIAL SEAL: [DMV SEAL]
    WATERMARK: CALIFORNIA STATE SEAL
    """
    
    try:
        # Create comprehensive data extractor
        print("1. Initializing ComprehensiveDataExtractor...")
        extractor = ComprehensiveDataExtractor(api_key=API_KEY)
        print("   ✓ Extractor initialized successfully")
        
        # Extract comprehensive data
        print("\n2. Performing comprehensive data extraction...")
        result = extractor.extract_all_data(sample_text, "sample_driver_license.txt")
        print("   ✓ Extraction completed")
        
        # Get summary
        print("\n3. Getting extraction summary...")
        summary = extractor.get_extraction_summary(result)
        print(f"   ✓ Summary: Document Type: {summary.get('document_type')}")
        print(f"   ✓ Total Fields: {summary.get('total_fields')}")
        print(f"   ✓ Sections: {summary.get('sections_identified')}")
        
        # Test search functionality
        print("\n4. Testing search functionality...")
        search_results = extractor.search_fields(result, "name")
        print(f"   ✓ Found {search_results.get('total_matches')} matches for 'name'")
        
        search_results = extractor.search_fields(result, "phone")
        print(f"   ✓ Found {search_results.get('total_matches')} matches for 'phone'")
        
        # Display structured data
        print("\n5. Structured Data Sections:")
        structured_data = result.get('structured_data', {})
        for section, fields in structured_data.items():
            print(f"   {section}: {len(fields)} fields")
            for field, value in list(fields.items())[:3]:  # Show first 3 fields
                print(f"     - {field}: {value}")
            if len(fields) > 3:
                print(f"     ... and {len(fields) - 3} more fields")
        
        # Display summary statistics
        print("\n6. Summary Statistics:")
        stats = result.get('summary_statistics', {})
        print(f"   Total Sections: {stats.get('total_sections')}")
        print(f"   Total Fields: {stats.get('total_fields')}")
        print(f"   Sections with Data: {stats.get('sections_with_data')}")
        
        # Display data completeness
        print("\n7. Data Completeness:")
        completeness = stats.get('data_completeness', {})
        for section, info in completeness.items():
            print(f"   {section}: {info.get('completeness_percentage')}% complete "
                  f"({info.get('non_empty_fields')}/{info.get('total_fields')} fields)")
        
        # Save results to file
        print("\n8. Saving results to file...")
        with open('comprehensive_extraction_results.json', 'w') as f:
            json.dump(result, f, indent=2)
        print("   ✓ Results saved to 'comprehensive_extraction_results.json'")
        
        print("\n=== Test Completed Successfully ===")
        return True
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
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
        extractor = ComprehensiveDataExtractor(api_key=API_KEY)
        
        # Extract data
        print("   Performing comprehensive extraction...")
        result = extractor.extract_all_data(text_content, os.path.basename(test_file))
        
        # Get summary
        summary = extractor.get_extraction_summary(result)
        print(f"   ✓ Document Type: {summary.get('document_type')}")
        print(f"   ✓ Total Fields: {summary.get('total_fields')}")
        print(f"   ✓ Sections: {summary.get('sections_identified')}")
        
        # Save results
        output_file = f"real_document_extraction_{os.path.splitext(os.path.basename(test_file))[0]}.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"   ✓ Results saved to '{output_file}'")
        
        print("   ✓ Real document test completed successfully")
        return True
        
    except Exception as e:
        print(f"   ❌ Error testing with real document: {str(e)}")
        return False

if __name__ == "__main__":
    print("Comprehensive Data Extraction Test Suite")
    print("=" * 50)
    
    # Test with sample text
    success1 = test_comprehensive_extraction()
    
    # Test with real document
    success2 = test_with_real_document()
    
    if success1 and success2:
        print("\n🎉 All tests passed successfully!")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
    
    print("\nTest files generated:")
    print("- comprehensive_extraction_results.json")
    print("- real_document_extraction_*.json (if real document test ran)") 