#!/usr/bin/env python3
"""
Format Consistency Test Script
Tests the improved DocumentProcessor3 for consistent results across different formats
"""

import sys
import os
import json
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from Services.DocumentProcessor3 import DocumentProcessor
from Common.constants import API_KEY

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_format_consistency():
    """Test consistency across different document formats"""
    
    # Initialize the processor
    processor = DocumentProcessor(API_KEY)
    
    # Enable unified processing
    processor.set_unified_processing(True)
    
    # Test files in different formats (same document)
    test_files = [
        "testdocs/docs/driver_license_card.docx",
        "testdocs/pdf/driver_license_card.pdf",
        "testdocs/ikmages/driving_license.jpg"
    ]
    
    print("=" * 80)
    print("FORMAT CONSISTENCY TEST")
    print("Testing consistent results across different document formats")
    print("=" * 80)
    
    results_by_format = {}
    
    for file_path in test_files:
        if not os.path.exists(file_path):
            print(f"⚠️  File not found: {file_path}")
            continue
            
        file_format = file_path.split('.')[-1].upper()
        print(f"\n🔍 Processing {file_format} format: {file_path}")
        print("-" * 60)
        
        try:
            # Process the file
            results = processor.process_file(file_path, min_confidence=0.0)
            
            if not results:
                print("❌ No results returned")
                continue
                
            # Store results for comparison
            results_by_format[file_format] = results
            
            # Display results
            for i, result in enumerate(results):
                print(f"\n📄 Result {i+1}:")
                
                # Document analysis
                doc_analysis = result.get('document_analysis', {})
                print(f"   Document Type: {doc_analysis.get('document_type', 'Unknown')}")
                print(f"   Confidence: {doc_analysis.get('confidence_score', 0.0):.2f}")
                print(f"   Processing Method: {result.get('processing_method', 'Unknown')}")
                
                # Extracted data
                extracted_data = result.get('extracted_data', {}).get('data', {})
                if extracted_data:
                    print(f"\n   📋 EXTRACTED DATA ({len(extracted_data)} fields):")
                    
                    # Show key fields for comparison
                    key_fields = ['Full Name', 'Document Number', 'Date Of Birth', 'Issue Date', 'Expiry Date', 'Address']
                    
                    for field in key_fields:
                        if field in extracted_data:
                            print(f"     {field}: {extracted_data[field]}")
                    
                    # Show other fields
                    other_fields = [k for k in extracted_data.keys() if k not in key_fields]
                    if other_fields:
                        print(f"     Other fields: {', '.join(other_fields[:5])}")
                        if len(other_fields) > 5:
                            print(f"     ... and {len(other_fields) - 5} more")
                    
                    # Quality metrics
                    meaningful_count = sum(1 for key in extracted_data.keys() 
                                         if not key.startswith('Unclear Text') and not key.startswith('Text_'))
                    total_count = len(extracted_data)
                    meaningful_ratio = meaningful_count / total_count * 100 if total_count > 0 else 0
                    
                    print(f"\n   📊 Quality: {meaningful_count}/{total_count} meaningful fields ({meaningful_ratio:.1f}%)")
                    
                else:
                    print("   ❌ No extracted data found")
                
                print("\n" + "="*60)
                
        except Exception as e:
            print(f"❌ Error processing {file_path}: {str(e)}")
            logger.error(f"Error processing {file_path}: {str(e)}", exc_info=True)
    
    # Compare results across formats
    print("\n" + "="*80)
    print("FORMAT CONSISTENCY ANALYSIS")
    print("="*80)
    
    if len(results_by_format) > 1:
        compare_results_across_formats(results_by_format)
    else:
        print("⚠️  Need at least 2 formats to compare consistency")

def compare_results_across_formats(results_by_format):
    """Compare results across different formats"""
    
    print(f"\n📊 Comparing results across {len(results_by_format)} formats:")
    
    # Extract key fields for comparison
    key_fields = ['Full Name', 'Document Number', 'Date Of Birth', 'Issue Date', 'Expiry Date', 'Address']
    format_data = {}
    
    for format_type, results in results_by_format.items():
        if results:
            result = results[0]  # Take first result
            extracted_data = result.get('extracted_data', {}).get('data', {})
            
            format_data[format_type] = {}
            for field in key_fields:
                format_data[format_type][field] = extracted_data.get(field, 'NOT FOUND')
    
    # Display comparison table
    print(f"\n{'Field':<20}", end="")
    for format_type in format_data.keys():
        print(f"{format_type:>15}", end="")
    print()
    
    print("-" * (20 + 15 * len(format_data)))
    
    for field in key_fields:
        print(f"{field:<20}", end="")
        for format_type in format_data.keys():
            value = format_data[format_type].get(field, 'NOT FOUND')
            if len(value) > 12:
                value = value[:10] + ".."
            print(f"{value:>15}", end="")
        print()
    
    # Calculate consistency score
    print(f"\n📈 CONSISTENCY ANALYSIS:")
    
    total_fields = len(key_fields)
    consistent_fields = 0
    
    for field in key_fields:
        values = set()
        for format_type in format_data.keys():
            value = format_data[format_type].get(field, 'NOT FOUND')
            if value != 'NOT FOUND':
                values.add(value)
        
        if len(values) <= 1:  # All formats have same value or all missing
            consistent_fields += 1
        else:
            print(f"   ⚠️  Inconsistent {field}: {values}")
    
    consistency_score = consistent_fields / total_fields * 100
    print(f"\n   Overall Consistency: {consistent_fields}/{total_fields} fields ({consistency_score:.1f}%)")
    
    if consistency_score >= 80:
        print("   ✅ EXCELLENT consistency across formats")
    elif consistency_score >= 60:
        print("   ✅ GOOD consistency across formats")
    elif consistency_score >= 40:
        print("   ⚠️  FAIR consistency across formats")
    else:
        print("   ❌ POOR consistency across formats")

def test_specific_consistency_issue():
    """Test the specific consistency issue mentioned by the user"""
    
    print("\n" + "="*80)
    print("SPECIFIC CONSISTENCY ISSUE TEST")
    print("Testing the driving license consistency issue")
    print("="*80)
    
    processor = DocumentProcessor(API_KEY)
    processor.set_unified_processing(True)
    
    # Test files that should be the same document
    test_files = [
        "testdocs/docs/driver_license_card.docx",
        "testdocs/pdf/driver_license_card.pdf"
    ]
    
    results = {}
    
    for file_path in test_files:
        if os.path.exists(file_path):
            file_format = file_path.split('.')[-1].upper()
            print(f"\n🔍 Testing {file_format}: {file_path}")
            
            try:
                file_results = processor.process_file(file_path, min_confidence=0.0)
                if file_results:
                    results[file_format] = file_results[0]  # Take first result
                    
                    extracted_data = file_results[0].get('extracted_data', {}).get('data', {})
                    print(f"   Full Name: {extracted_data.get('Full Name', 'NOT FOUND')}")
                    print(f"   Document Number: {extracted_data.get('Document Number', 'NOT FOUND')}")
                    print(f"   Issue Date: {extracted_data.get('Issue Date', 'NOT FOUND')}")
                    print(f"   Expiry Date: {extracted_data.get('Expiry Date', 'NOT FOUND')}")
                    print(f"   Address: {extracted_data.get('Address', 'NOT FOUND')}")
                    
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
        else:
            print(f"⚠️  File not found: {file_path}")
    
    # Compare the specific fields that were different
    if len(results) >= 2:
        print(f"\n📊 SPECIFIC FIELD COMPARISON:")
        
        fields_to_compare = ['Full Name', 'Document Number', 'Issue Date', 'Expiry Date', 'Address']
        
        for field in fields_to_compare:
            values = {}
            for format_type, result in results.items():
                extracted_data = result.get('extracted_data', {}).get('data', {})
                values[format_type] = extracted_data.get(field, 'NOT FOUND')
            
            print(f"\n   {field}:")
            for format_type, value in values.items():
                print(f"     {format_type}: {value}")
            
            # Check if values are consistent
            unique_values = set(v for v in values.values() if v != 'NOT FOUND')
            if len(unique_values) <= 1:
                print(f"     ✅ CONSISTENT")
            else:
                print(f"     ❌ INCONSISTENT - Different values detected")

if __name__ == "__main__":
    print("🚀 Starting Format Consistency Tests...")
    
    try:
        # Test format consistency
        test_format_consistency()
        
        # Test specific consistency issue
        test_specific_consistency_issue()
        
        print("\n✅ All format consistency tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test execution failed: {str(e)}")
        logger.error("Test execution failed", exc_info=True)
        sys.exit(1) 