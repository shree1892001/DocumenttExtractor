"""
Test script for the unified document processing system.
Demonstrates the single optimized prompt approach.
"""

import os
import sys
import json
import logging
from typing import Dict, Any

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Common.constants import API_KEY_1
from Services.UnifiedDocumentProcessor import UnifiedDocumentProcessor
from Services.DocumentProcessor3 import DocumentProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_unified_processing():
    """Test the unified document processing with sample documents"""
    
    # Sample document texts for testing
    test_documents = {
        "aadhaar_sample": """
        GOVERNMENT OF INDIA
        Unique Identification Authority of India
        
        Name: RAJESH KUMAR SHARMA
        Date of Birth: 15/08/1985
        Gender: Male
        Aadhaar Number: 1234 5678 9012
        Address: 123 Main Street, New Delhi, Delhi - 110001
        
        This is to certify that the above details have been verified.
        """,
        
        "license_sample": """
        DRIVING LICENSE
        Government of Delhi
        Transport Department
        
        License Number: DL-1420110012345
        Name: PRIYA SINGH
        Date of Birth: 22/03/1990
        Address: 456 Park Avenue, Delhi - 110002
        Valid From: 15/01/2020
        Valid Until: 14/01/2040
        Vehicle Class: LMV
        
        Issued by: Regional Transport Office, Delhi
        """,
        
        "pan_sample": """
        INCOME TAX DEPARTMENT
        GOVERNMENT OF INDIA
        
        Permanent Account Number Card
        
        Name: AMIT KUMAR GUPTA
        Father's Name: RAJESH GUPTA
        Date of Birth: 10/12/1988
        PAN: ABCDE1234F
        
        This is a computer generated document.
        """,
        
        "passport_sample": """
        REPUBLIC OF INDIA
        PASSPORT
        
        Type: P
        Country Code: IND
        Passport No.: A1234567
        
        Surname: SHARMA
        Given Names: ANITA
        Nationality: INDIAN
        Date of Birth: 05/07/1992
        Place of Birth: MUMBAI
        Gender: F
        
        Date of Issue: 10/01/2020
        Date of Expiry: 09/01/2030
        Place of Issue: MUMBAI
        """
    }
    
    try:
        # Initialize unified processor
        logger.info("Initializing Unified Document Processor...")
        unified_processor = UnifiedDocumentProcessor(api_key=API_KEY_1)
        
        # Initialize legacy processor for comparison
        logger.info("Initializing Legacy Document Processor...")
        legacy_processor = DocumentProcessor(api_key=API_KEY_1)
        
        results = {}
        
        for doc_name, doc_text in test_documents.items():
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing: {doc_name}")
            logger.info(f"{'='*60}")
            
            # Test unified processing
            logger.info("Testing Unified Processing...")
            try:
                unified_result = unified_processor.process_document(doc_text)
                results[f"{doc_name}_unified"] = unified_result
                
                # Print summary
                doc_analysis = unified_result.get("document_analysis", {})
                extracted_data = unified_result.get("extracted_data", {})
                verification = unified_result.get("verification_results", {})
                
                print(f"\n📄 UNIFIED PROCESSING RESULTS for {doc_name}:")
                print(f"   Document Type: {doc_analysis.get('document_type', 'unknown')}")
                print(f"   Confidence: {doc_analysis.get('confidence_score', 0.0):.2f}")
                print(f"   Category: {doc_analysis.get('document_category', 'unknown')}")
                print(f"   Issuing Authority: {doc_analysis.get('issuing_authority', 'unknown')}")
                
                # Show key extracted fields
                personal_info = extracted_data.get("personal_information", {})
                if personal_info:
                    print(f"   Name: {personal_info.get('full_name', 'N/A')}")
                    print(f"   DOB: {personal_info.get('date_of_birth', 'N/A')}")
                
                doc_ids = extracted_data.get("document_identifiers", {})
                if doc_ids:
                    print(f"   Document Number: {doc_ids.get('primary_number', 'N/A')}")
                
                # Verification status
                auth_assessment = verification.get("authenticity_assessment", {})
                print(f"   Authenticity: {auth_assessment.get('is_likely_genuine', False)}")
                print(f"   Verification Score: {auth_assessment.get('confidence_score', 0.0):.2f}")
                
            except Exception as e:
                logger.error(f"Unified processing failed for {doc_name}: {str(e)}")
                results[f"{doc_name}_unified"] = {"error": str(e)}
            
            # Test legacy processing for comparison
            logger.info("Testing Legacy Processing...")
            try:
                # Force legacy processing
                legacy_processor.set_unified_processing(False)
                legacy_result = legacy_processor._process_text_content(doc_text, f"{doc_name}.txt", 0.0)
                results[f"{doc_name}_legacy"] = legacy_result
                
                if legacy_result:
                    print(f"\n📄 LEGACY PROCESSING RESULTS for {doc_name}:")
                    print(f"   Document Type: {legacy_result.get('document_type', 'unknown')}")
                    print(f"   Confidence: {legacy_result.get('confidence', 0.0):.2f}")
                    print(f"   Status: {legacy_result.get('status', 'unknown')}")
                    
                    extracted = legacy_result.get('extracted_data', {}).get('data', {})
                    if extracted:
                        print(f"   Name: {extracted.get('Name', 'N/A')}")
                        print(f"   DOB: {extracted.get('Date of Birth', 'N/A')}")
                
            except Exception as e:
                logger.error(f"Legacy processing failed for {doc_name}: {str(e)}")
                results[f"{doc_name}_legacy"] = {"error": str(e)}
        
        # Save detailed results
        output_file = "unified_processing_test_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n✅ Test completed! Detailed results saved to {output_file}")
        
        # Print summary comparison
        print(f"\n{'='*80}")
        print("PROCESSING COMPARISON SUMMARY")
        print(f"{'='*80}")
        
        for doc_name in test_documents.keys():
            unified_key = f"{doc_name}_unified"
            legacy_key = f"{doc_name}_legacy"
            
            print(f"\n📋 {doc_name.upper()}:")
            
            # Unified results
            if unified_key in results and "error" not in results[unified_key]:
                unified_doc_type = results[unified_key].get("document_analysis", {}).get("document_type", "unknown")
                unified_confidence = results[unified_key].get("document_analysis", {}).get("confidence_score", 0.0)
                print(f"   Unified:  {unified_doc_type} (confidence: {unified_confidence:.2f})")
            else:
                print(f"   Unified:  ERROR")
            
            # Legacy results
            if legacy_key in results and "error" not in results[legacy_key]:
                legacy_doc_type = results[legacy_key].get("document_type", "unknown")
                legacy_confidence = results[legacy_key].get("confidence", 0.0)
                print(f"   Legacy:   {legacy_doc_type} (confidence: {legacy_confidence:.2f})")
            else:
                print(f"   Legacy:   ERROR")
        
        return results
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        return {"error": str(e)}


def test_specific_field_extraction():
    """Test targeted field extraction"""
    
    sample_text = """
    DRIVING LICENSE
    License Number: DL-1420110012345
    Name: RAJESH KUMAR
    Date of Birth: 15/08/1985
    Address: 123 Main Street, Delhi
    Valid From: 01/01/2020
    Valid Until: 31/12/2039
    """
    
    try:
        processor = UnifiedDocumentProcessor(api_key=API_KEY_1)
        
        # Test specific field extraction
        target_fields = ["Name", "License Number", "Date of Birth", "Valid Until"]
        
        logger.info("Testing specific field extraction...")
        result = processor.extract_specific_fields(sample_text, target_fields, "license")
        
        print(f"\n🎯 SPECIFIC FIELD EXTRACTION RESULTS:")
        print(f"   Status: {result.get('status', 'unknown')}")
        print(f"   Document Type: {result.get('document_type', 'unknown')}")
        print(f"   Confidence: {result.get('confidence', 0.0):.2f}")
        
        extracted_fields = result.get('extracted_fields', {})
        print(f"   Extracted Fields:")
        for field, value in extracted_fields.items():
            print(f"     {field}: {value}")
        
        return result
        
    except Exception as e:
        logger.error(f"Specific field extraction test failed: {str(e)}")
        return {"error": str(e)}


def test_processor_diagnostics():
    """Test processor diagnostics and troubleshooting"""
    try:
        processor = UnifiedDocumentProcessor(api_key=API_KEY_1)

        logger.info("Running processor diagnostics...")
        test_results = processor.test_processor()

        print(f"\n🔧 PROCESSOR DIAGNOSTICS:")
        print(f"   Connection Test: {'✅ PASS' if test_results.get('connection_test') else '❌ FAIL'}")

        simple_test = test_results.get('simple_processing', {})
        print(f"   Simple Processing: {'✅ PASS' if simple_test.get('success') else '❌ FAIL'}")
        if not simple_test.get('success'):
            print(f"     Response Preview: {simple_test.get('response_preview', 'N/A')}")

        unified_test = test_results.get('unified_processing', {})
        print(f"   Unified Processing: {'✅ PASS' if unified_test.get('success') else '❌ FAIL'}")

        recommendations = test_results.get('recommendations', [])
        if recommendations:
            print(f"   Recommendations:")
            for rec in recommendations:
                print(f"     • {rec}")

        return test_results

    except Exception as e:
        logger.error(f"Diagnostics test failed: {str(e)}")
        return {"error": str(e)}


def main():
    """Main test function"""
    try:
        print("🚀 Starting Unified Document Processing Tests")
        print("=" * 80)

        # Test 0: Processor diagnostics
        print("\n🔧 TEST 0: Processor Diagnostics")
        diagnostics_results = test_processor_diagnostics()

        # Only continue if basic tests pass
        if diagnostics_results.get('connection_test') and diagnostics_results.get('simple_processing', {}).get('success'):
            # Test 1: Full document processing
            print("\n📋 TEST 1: Full Document Processing")
            full_results = test_unified_processing()

            # Test 2: Specific field extraction
            print("\n📋 TEST 2: Specific Field Extraction")
            field_results = test_specific_field_extraction()

            print("\n✅ All tests completed!")
        else:
            print("\n⚠️ Basic diagnostics failed. Please check the recommendations above before running full tests.")
        
        # Show processor info
        try:
            processor = UnifiedDocumentProcessor(api_key=API_KEY_1)
            info = processor.get_processor_info()
            
            print(f"\n🔧 PROCESSOR INFORMATION:")
            print(f"   Type: {info.get('processor_type', 'unknown')}")
            print(f"   Prompt Version: {info.get('prompt_version', 'unknown')}")
            print(f"   Capabilities: {', '.join(info.get('capabilities', []))}")
            print(f"   Optimization: {info.get('optimization', 'unknown')}")
            
        except Exception as e:
            logger.warning(f"Could not get processor info: {str(e)}")
        
    except Exception as e:
        logger.error(f"Main test failed: {str(e)}")
        print(f"❌ Test failed: {str(e)}")


if __name__ == "__main__":
    main()
