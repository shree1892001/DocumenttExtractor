"""
Example usage of ConfidentialDocumentProcessor for processing resumes
without sending data to external AI services like Gemini.

This example demonstrates how to use the ConfidentialDocumentProcessor
to process resume documents while maintaining privacy and confidentiality.
"""

import os
import sys
import json
import logging
from typing import List, Dict, Any

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Services.DocumentProcessor3 import ConfidentialDocumentProcessor
from Common.constants import API_KEY_3

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_resume_safely(file_path: str, api_key: str) -> List[Dict[str, Any]]:
    """
    Process a resume file using the confidential processor
    
    Args:
        file_path: Path to the resume file (PDF, DOCX, or image)
        api_key: API key (required for initialization but won't be used for confidential docs)
    
    Returns:
        List of processing results
    """
    try:
        # Initialize the confidential processor
        processor = ConfidentialDocumentProcessor(api_key=api_key)
        
        # Process the file
        results = processor.process_file(file_path, min_confidence=0.3)
        
        # Log processing method for each result
        for result in results:
            processing_method = result.get('processing_method', 'unknown')
            privacy_protected = result.get('privacy_protected', False)
            
            logger.info(f"Document processed with method: {processing_method}")
            logger.info(f"Privacy protected: {privacy_protected}")
            
            if privacy_protected:
                logger.info("✅ Resume processed locally without external AI services")
            else:
                logger.warning("⚠️ Document processed with external services")
        
        return results
        
    except Exception as e:
        logger.error(f"Error processing resume: {str(e)}")
        raise

def main():
    """
    Example usage of the confidential document processor
    """
    try:
        # Example file path - replace with your actual resume file
        resume_file = "path/to/your/resume.pdf"  # or .docx, .jpg, .png, etc.
        
        if not os.path.exists(resume_file):
            logger.error(f"Resume file not found: {resume_file}")
            logger.info("Please update the 'resume_file' variable with a valid file path")
            return
        
        # Process the resume
        logger.info(f"Processing resume: {resume_file}")
        results = process_resume_safely(resume_file, API_KEY_3)
        
        # Display results
        if results:
            logger.info(f"Successfully processed {len(results)} document(s)")
            
            for i, result in enumerate(results, 1):
                logger.info(f"\n--- Document {i} ---")
                logger.info(f"Status: {result.get('status', 'unknown')}")
                logger.info(f"Document Type: {result.get('document_type', 'unknown')}")
                logger.info(f"Confidence: {result.get('confidence', 0):.2f}")
                logger.info(f"Privacy Protected: {result.get('privacy_protected', False)}")
                
                # Show extracted data (be careful with sensitive info in logs)
                extracted_data = result.get('extracted_data', {}).get('data', {})
                if extracted_data:
                    logger.info("Extracted fields:")
                    for field, value in extracted_data.items():
                        if field in ['email', 'phone']:  # Show contact info
                            logger.info(f"  {field}: {value}")
                        elif field in ['name']:  # Show name
                            logger.info(f"  {field}: {value}")
                        else:  # For other fields, just show that they exist
                            logger.info(f"  {field}: [extracted]")
            
            # Save results to file (optional)
            output_file = "resume_processing_results.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"Results saved to: {output_file}")
            
        else:
            logger.warning("No documents were successfully processed")
            
    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
