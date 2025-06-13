"""
Test script for DocumentProcessor3 with integrated unified processing.
"""

import os
import sys
import json
import logging

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Common.constants import API_KEY_1
from Services.DocumentProcessor3 import DocumentProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_unified_processing_in_documentprocessor3():
    """Test the unified processing integrated into DocumentProcessor3"""
    
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
        """
    }
    
    try:
        # Initialize DocumentProcessor3
        logger.info("Initializing DocumentProcessor3...")
        processor = DocumentProcessor(api_key=API_KEY_1)
        
        # Ensure unified processing is enabled
        processor.set_unified_processing(True)
        
        results = {}
        
        for doc_name, doc_text in test_documents.items():
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing: {doc_name}")
            logger.info(f"{'='*60}")
            
            try:
                # Test unified processing
                logger.info("Testing Unified Processing in DocumentProcessor3...")
                result = processor._process_text_content(doc_text, f"{doc_name}.txt", 0.0)
                results[doc_name] = result
                
                if result:
                    # Print summary
                    print(f"\n📄 UNIFIED PROCESSING RESULTS for {doc_name}:")
                    print(f"   Status: {result.get('status', 'unknown')}")
                    print(f"   Document Type: {result.get('document_type', 'unknown')}")
                    print(f"   Confidence: {result.get('confidence', 0.0):.2f}")
                    print(f"   Processing Method: {result.get('processing_method', 'unknown')}")
                    
                    # Show key extracted fields
                    extracted_data = result.get('extracted_data', {}).get('data', {})
                    if extracted_data:
                        print(f"   Name: {extracted_data.get('Name', 'N/A')}")
                        print(f"   Document Number: {extracted_data.get('Document Number', 'N/A')}")
                        print(f"   DOB: {extracted_data.get('Date of Birth', 'N/A')}")
                    
                    # Verification status
                    verification = result.get('verification_result', {})
                    if verification:
                        print(f"   Authenticity: {verification.get('is_genuine', False)}")
                        print(f"   Verification Score: {verification.get('confidence_score', 0.0):.2f}")
                    
                    if result.get('status') == 'rejected':
                        print(f"   Rejection Reason: {result.get('rejection_reason', 'Unknown')}")
                else:
                    print(f"\n❌ No result returned for {doc_name}")
                
            except Exception as e:
                logger.error(f"Processing failed for {doc_name}: {str(e)}")
                results[doc_name] = {"error": str(e)}
                print(f"\n❌ ERROR processing {doc_name}: {str(e)}")
        
        # Save detailed results
        output_file = "documentprocessor3_unified_test_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n✅ Test completed! Detailed results saved to {output_file}")
        
        # Print summary
        print(f"\n{'='*80}")
        print("PROCESSING SUMMARY")
        print(f"{'='*80}")
        
        successful = 0
        failed = 0
        
        for doc_name, result in results.items():
            if isinstance(result, dict) and "error" not in result:
                status = result.get('status', 'unknown')
                if status == 'success':
                    successful += 1
                    print(f"✅ {doc_name}: SUCCESS - {result.get('document_type', 'unknown')}")
                elif status == 'rejected':
                    print(f"⚠️ {doc_name}: REJECTED - {result.get('rejection_reason', 'Unknown reason')}")
                else:
                    failed += 1
                    print(f"❌ {doc_name}: FAILED - {status}")
            else:
                failed += 1
                print(f"❌ {doc_name}: ERROR - {result.get('error', 'Unknown error')}")
        
        print(f"\nSUMMARY: {successful} successful, {failed} failed out of {len(test_documents)} documents")
        
        return results
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        return {"error": str(e)}


def test_fallback_processing():
    """Test fallback processing when unified prompt fails"""
    
    try:
        processor = DocumentProcessor(api_key=API_KEY_1)
        
        # Test with problematic text that might cause JSON parsing issues
        problematic_text = """
        This is a test document with some unusual formatting.
        Name: Test User
        ID: 123456
        Some random text that might confuse the AI...
        """
        
        logger.info("Testing fallback processing...")
        
        # Try the fallback method directly
        result = processor._process_with_fallback_prompt(problematic_text, "test.txt", 0.0)
        
        if result:
            print(f"\n🔄 FALLBACK PROCESSING RESULTS:")
            print(f"   Status: {result.get('status', 'unknown')}")
            print(f"   Document Type: {result.get('document_type', 'unknown')}")
            print(f"   Confidence: {result.get('confidence', 0.0):.2f}")
            print(f"   Processing Method: {result.get('processing_method', 'unknown')}")
            return True
        else:
            print(f"\n❌ Fallback processing failed")
            return False
            
    except Exception as e:
        logger.error(f"Fallback test failed: {str(e)}")
        print(f"\n❌ Fallback test error: {str(e)}")
        return False


def test_legacy_vs_unified():
    """Compare legacy vs unified processing"""
    
    try:
        processor = DocumentProcessor(api_key=API_KEY_1)
        
        test_text = """
        DRIVING LICENSE
        License Number: DL123456789
        Name: John Doe
        Date of Birth: 01/01/1990
        """
        
        print(f"\n🔄 COMPARING LEGACY VS UNIFIED PROCESSING:")
        
        # Test unified processing
        processor.set_unified_processing(True)
        unified_result = processor._process_text_content(test_text, "test.txt", 0.0)
        
        # Test legacy processing
        processor.set_unified_processing(False)
        legacy_result = processor._process_text_content(test_text, "test.txt", 0.0)
        
        print(f"   Unified: {unified_result.get('document_type', 'unknown') if unified_result else 'FAILED'}")
        print(f"   Legacy:  {legacy_result.get('document_type', 'unknown') if legacy_result else 'FAILED'}")
        
        return unified_result, legacy_result
        
    except Exception as e:
        logger.error(f"Comparison test failed: {str(e)}")
        return None, None


def main():
    """Main test function"""
    try:
        print("🚀 Starting DocumentProcessor3 Unified Processing Tests")
        print("=" * 80)
        
        # Test 1: Unified processing
        print("\n📋 TEST 1: Unified Processing in DocumentProcessor3")
        unified_results = test_unified_processing_in_documentprocessor3()
        
        # Test 2: Fallback processing
        print("\n📋 TEST 2: Fallback Processing")
        fallback_ok = test_fallback_processing()
        
        # Test 3: Legacy vs Unified comparison
        print("\n📋 TEST 3: Legacy vs Unified Comparison")
        unified_result, legacy_result = test_legacy_vs_unified()
        
        print("\n✅ All tests completed!")
        
        # Summary
        print(f"\n📊 FINAL SUMMARY:")
        print(f"   Unified Processing: {'✅ WORKING' if unified_results and not unified_results.get('error') else '❌ FAILED'}")
        print(f"   Fallback Processing: {'✅ WORKING' if fallback_ok else '❌ FAILED'}")
        print(f"   Legacy Processing: {'✅ WORKING' if legacy_result else '❌ FAILED'}")
        
    except Exception as e:
        logger.error(f"Main test failed: {str(e)}")
        print(f"❌ Test failed: {str(e)}")


if __name__ == "__main__":
    main()
