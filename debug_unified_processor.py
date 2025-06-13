"""
Debug script for unified document processor issues.
This script helps diagnose and fix common problems.
"""

import os
import sys
import json
import logging

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Common.constants import API_KEY_1
from Services.UnifiedDocumentProcessor import UnifiedDocumentProcessor

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_basic_connection():
    """Test basic connection to Gemini API"""
    print("🔍 Testing basic connection...")
    
    try:
        processor = UnifiedDocumentProcessor(api_key=API_KEY_1)
        
        # Test connection
        connection_ok = processor.text_processor.test_connection()
        print(f"   Connection: {'✅ OK' if connection_ok else '❌ FAILED'}")
        
        if not connection_ok:
            print("   ⚠️ Check your API key and network connection")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Connection test failed: {str(e)}")
        return False


def test_simple_processing():
    """Test simple text processing"""
    print("\n🔍 Testing simple text processing...")
    
    try:
        processor = UnifiedDocumentProcessor(api_key=API_KEY_1)
        
        # Very simple test
        simple_prompt = "Return JSON with document_type: 'test'. Text: Sample document"
        response = processor.text_processor.process_text("", simple_prompt)
        
        print(f"   Response received: {'✅ YES' if response else '❌ NO'}")
        print(f"   Response length: {len(response) if response else 0}")
        print(f"   Response preview: {response[:100] if response else 'None'}...")
        
        if response:
            # Try to parse as JSON
            try:
                cleaned = processor._clean_json_response(response)
                parsed = json.loads(cleaned)
                print(f"   JSON parsing: ✅ SUCCESS")
                print(f"   Parsed content: {parsed}")
                return True
            except Exception as e:
                print(f"   JSON parsing: ❌ FAILED - {str(e)}")
                print(f"   Cleaned response: {cleaned[:200] if 'cleaned' in locals() else 'N/A'}")
                return False
        else:
            return False
            
    except Exception as e:
        print(f"   ❌ Simple processing failed: {str(e)}")
        return False


def test_unified_prompt():
    """Test the unified prompt with minimal text"""
    print("\n🔍 Testing unified prompt...")
    
    try:
        processor = UnifiedDocumentProcessor(api_key=API_KEY_1)
        
        # Minimal test document
        test_text = "Name: John Doe\nDocument: Test ID\nNumber: 123456"
        
        print(f"   Test text: {test_text}")
        
        result = processor.process_document(test_text)
        
        if result.get("status") == "error":
            print(f"   ❌ Unified processing failed: {result.get('message', 'Unknown error')}")
            
            # Show additional error details
            if "raw_response" in result:
                print(f"   Raw response: {result['raw_response'][:200]}...")
            
            return False
        else:
            print(f"   ✅ Unified processing succeeded")
            print(f"   Document type: {result.get('document_analysis', {}).get('document_type', 'unknown')}")
            print(f"   Confidence: {result.get('document_analysis', {}).get('confidence_score', 0.0)}")
            return True
            
    except Exception as e:
        print(f"   ❌ Unified prompt test failed: {str(e)}")
        return False


def test_fallback_processing():
    """Test fallback processing"""
    print("\n🔍 Testing fallback processing...")
    
    try:
        processor = UnifiedDocumentProcessor(api_key=API_KEY_1)
        
        # Test fallback directly
        test_text = "Name: Jane Smith\nLicense: ABC123\nDOB: 01/01/1990"
        
        result = processor._process_with_fallback(test_text)
        
        if result:
            print(f"   ✅ Fallback processing succeeded")
            print(f"   Document type: {result.get('document_analysis', {}).get('document_type', 'unknown')}")
            return True
        else:
            print(f"   ❌ Fallback processing failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Fallback test failed: {str(e)}")
        return False


def run_comprehensive_diagnostics():
    """Run comprehensive diagnostics"""
    print("\n🔧 Running comprehensive diagnostics...")
    
    try:
        processor = UnifiedDocumentProcessor(api_key=API_KEY_1)
        diagnostics = processor.test_processor()
        
        print(f"\n📊 DIAGNOSTIC RESULTS:")
        print(f"   Connection: {'✅' if diagnostics.get('connection_test') else '❌'}")
        
        simple_test = diagnostics.get('simple_processing', {})
        print(f"   Simple Processing: {'✅' if simple_test.get('success') else '❌'}")
        
        unified_test = diagnostics.get('unified_processing', {})
        print(f"   Unified Processing: {'✅' if unified_test.get('success') else '❌'}")
        
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in diagnostics.get('recommendations', []):
            print(f"   • {rec}")
        
        return diagnostics
        
    except Exception as e:
        print(f"   ❌ Comprehensive diagnostics failed: {str(e)}")
        return {"error": str(e)}


def main():
    """Main debug function"""
    print("🐛 Unified Document Processor Debug Tool")
    print("=" * 60)
    
    # Step 1: Basic connection
    if not test_basic_connection():
        print("\n❌ Basic connection failed. Cannot proceed with further tests.")
        return
    
    # Step 2: Simple processing
    if not test_simple_processing():
        print("\n❌ Simple processing failed. Check API configuration.")
        return
    
    # Step 3: Unified prompt
    unified_ok = test_unified_prompt()
    
    # Step 4: Fallback processing
    fallback_ok = test_fallback_processing()
    
    # Step 5: Comprehensive diagnostics
    diagnostics = run_comprehensive_diagnostics()
    
    # Summary
    print(f"\n📋 SUMMARY:")
    print(f"   Basic Connection: ✅")
    print(f"   Simple Processing: ✅")
    print(f"   Unified Processing: {'✅' if unified_ok else '❌'}")
    print(f"   Fallback Processing: {'✅' if fallback_ok else '❌'}")
    
    if unified_ok:
        print(f"\n🎉 All systems working! Unified processing is ready to use.")
    elif fallback_ok:
        print(f"\n⚠️ Unified processing has issues, but fallback is working.")
        print(f"   The system will automatically use fallback when needed.")
    else:
        print(f"\n❌ Both unified and fallback processing failed.")
        print(f"   Please check the recommendations above.")
    
    # Save diagnostics
    if diagnostics and "error" not in diagnostics:
        with open("debug_diagnostics.json", "w") as f:
            json.dump(diagnostics, f, indent=2)
        print(f"\n💾 Detailed diagnostics saved to debug_diagnostics.json")


if __name__ == "__main__":
    main()
