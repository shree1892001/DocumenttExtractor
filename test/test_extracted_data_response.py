#!/usr/bin/env python3
"""
Test script to verify extracted data is included in API responses
"""

import json

def test_extracted_data_structure():
    """Test the extracted data structure that should be returned"""
    
    # Sample extracted data structure from DocumentProcessor3
    sample_extracted_data = {
        "data": {
            "document_identifier": "HOKPP6906M",
            "name": "ASHWINI VYANKOJI PAWAR",
            "fathers_name": "VYANKOJI PAWAR",
            "date_of_birth": "2002-01-18",
            "date_on_card": "2023-05-19",
            "issuing_authority": "INCOME TAX DEPARTMENT GOVT. OF INDIA"
        },
        "confidence": 0.95,
        "additional_info": "The document appears to be a PAN card...",
        "document_metadata": {
            "type": "permanent account number (pan) card",
            "category": "Government document",
            "issuing_authority": "INCOME TAX DEPARTMENT GOVT. OF INDIA",
            "key_indicators": [
                "'Permanent Account Number Card' explicitly stated",
                "Unique PAN number (HOKPP6906M)",
                "Issuing authority: INCOME TAX DEPARTMENT GOVT. OF INDIA"
            ]
        }
    }
    
    # Expected API response structure
    expected_response = {
        "status": "success",
        "message": "Successfully processed 1 documents",
        "data": [
            {
                "extracted_data": sample_extracted_data,  # Should contain the full structure
                "verification": {
                    "is_genuine": False,
                    "confidence_score": 0.45,
                    "rejection_reason": "Low image quality...",
                    # ... verification details
                },
                "processing_details": {
                    "document_type": "permanent account number (pan) card",
                    "confidence": 0.95,
                    "validation_level": "strict",
                    "processing_method": "ocr"
                }
            }
        ]
    }
    
    print("🎯 Expected API Response Structure:")
    print("=" * 50)
    print(json.dumps(expected_response, indent=2))
    
    print("\n✅ Key Points:")
    print("1. extracted_data should contain the full nested structure")
    print("2. extracted_data.data should have all the extracted fields")
    print("3. This should work for both successful and rejected documents")
    print("4. The structure should be consistent regardless of verification status")
    
    return expected_response

def main():
    """Main test function"""
    print("🔧 DocumentProcessor3 Extracted Data Fix Test")
    print("This shows the expected structure after the fix")
    print()
    
    test_extracted_data_structure()
    
    print("\n🚀 To test:")
    print("1. Restart your Main.py API")
    print("2. Upload a document via Postman")
    print("3. Check that extracted_data.data contains the actual extracted fields")
    print("4. Verify this works for both genuine and rejected documents")

if __name__ == "__main__":
    main()
