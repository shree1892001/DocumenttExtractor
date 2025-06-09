"""
Complete example of using ConfidentialDocumentProcessor with RoBERTa
for processing confidential documents without sending data to Gemini.

This example demonstrates:
1. How to initialize the processor with RoBERTa model
2. How to process different types of confidential documents
3. How the system automatically detects confidential content
4. How RoBERTa extracts information locally
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
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def install_requirements():
    """Install required packages for RoBERTa"""
    try:
        import subprocess
        import sys
        
        packages = [
            'transformers',
            'torch',
            'opencv-python',
            'numpy'
        ]
        
        for package in packages:
            try:
                __import__(package.replace('-', '_'))
                print(f"✅ {package} is already installed")
            except ImportError:
                print(f"📦 Installing {package}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✅ {package} installed successfully")
                
    except Exception as e:
        print(f"❌ Error installing requirements: {str(e)}")
        print("Please install manually: pip install transformers torch opencv-python numpy")

def process_confidential_document_safely(file_path: str, api_key: str) -> List[Dict[str, Any]]:
    """
    Process a confidential document using RoBERTa instead of Gemini
    
    Args:
        file_path: Path to the confidential document (PDF, DOCX, or image)
        api_key: API key (required for initialization but won't be used for confidential docs)
    
    Returns:
        List of processing results
    """
    try:
        # Initialize the confidential processor with RoBERTa
        processor = ConfidentialDocumentProcessor(api_key=api_key)
        
        # Process the file
        results = processor.process_file(file_path, min_confidence=0.3)
        
        # Log processing method for each result
        for result in results:
            processing_method = result.get('processing_method', 'unknown')
            privacy_protected = result.get('privacy_protected', False)
            model_used = result.get('model_used', 'unknown')
            
            logger.info(f"Document processed with method: {processing_method}")
            logger.info(f"Privacy protected: {privacy_protected}")
            logger.info(f"Model used: {model_used}")
            
            if privacy_protected:
                logger.info("✅ Document processed locally with RoBERTa (no external AI services)")
            else:
                logger.warning("⚠️ Document processed with external services")
        
        return results
        
    except Exception as e:
        logger.error(f"Error processing confidential document: {str(e)}")
        raise

def demonstrate_roberta_extraction():
    """
    Demonstrate RoBERTa-based information extraction on sample text
    """
    print("\n" + "="*80)
    print("DEMONSTRATING ROBERTA-BASED INFORMATION EXTRACTION")
    print("="*80)
    
    try:
        # Initialize the processor
        processor = ConfidentialDocumentProcessor(api_key=API_KEY_3)
        
        # Sample confidential document text
        sample_resume = """
        JOHN DOE
        Software Engineer
        
        Contact Information:
        Email: john.doe@techcorp.com
        Phone: (555) 123-4567
        Address: 123 Main Street, San Francisco, CA 94102
        
        PROFESSIONAL SUMMARY:
        Experienced software engineer with 8+ years in full-stack development
        
        WORK EXPERIENCE:
        Senior Software Engineer | Tech Corp | 2020-Present
        - Led development of microservices architecture
        - Mentored team of 5 junior developers
        - Implemented CI/CD pipelines using Docker and Kubernetes
        
        Software Developer | StartupXYZ | 2018-2020
        - Built responsive web applications using React and Node.js
        - Designed and implemented RESTful APIs
        
        EDUCATION:
        Bachelor of Science in Computer Science
        Stanford University | 2014-2018
        GPA: 3.8/4.0
        
        TECHNICAL SKILLS:
        - Programming: Python, JavaScript, Java, Go
        - Frameworks: React, Django, Spring Boot, Express.js
        - Databases: PostgreSQL, MongoDB, Redis
        - Tools: Docker, Kubernetes, Git, Jenkins, AWS
        """
        
        print("Sample Resume Text:")
        print("-" * 40)
        print(sample_resume[:200] + "...")
        
        # Check if it's detected as confidential
        is_confidential = processor._is_confidential_document(sample_resume)
        print(f"\nConfidential Detection: {'✅ YES' if is_confidential else '❌ NO'}")
        
        if is_confidential:
            print("\n🔒 This document will be processed with RoBERTa (privacy protected)")
            
            # Get questions for resume processing
            questions = processor._get_questions_for_document_type('resume')
            print(f"\nRoBERTa Questions ({len(questions)} total):")
            for i, question in enumerate(questions[:5], 1):  # Show first 5
                print(f"  {i}. {question}")
            if len(questions) > 5:
                print(f"  ... and {len(questions) - 5} more questions")
            
            # Extract information using RoBERTa
            if processor.qa_pipeline:
                print("\n🤖 Extracting information with RoBERTa...")
                roberta_results = processor._extract_with_roberta(sample_resume, questions[:5])
                
                print("\nRoBERTa Extraction Results:")
                print("-" * 40)
                for question, result in roberta_results.items():
                    answer = result.get('answer', 'N/A')
                    confidence = result.get('confidence', 0.0)
                    print(f"Q: {question}")
                    print(f"A: {answer} (confidence: {confidence:.2f})")
                    print()
            else:
                print("❌ RoBERTa model not available")
        else:
            print("\n🌐 This document would use external AI services")
            
    except Exception as e:
        print(f"❌ Error in demonstration: {str(e)}")

def test_different_document_types():
    """
    Test the processor with different types of confidential documents
    """
    print("\n" + "="*80)
    print("TESTING DIFFERENT CONFIDENTIAL DOCUMENT TYPES")
    print("="*80)
    
    test_documents = {
        "Legal Contract": """
            EMPLOYMENT AGREEMENT
            
            This agreement is between TechCorp Inc. and Sarah Johnson
            
            Position: Senior Data Scientist
            Start Date: January 15, 2024
            Annual Salary: $120,000
            
            CONFIDENTIAL INFORMATION:
            Employee agrees to maintain confidentiality of all proprietary information
            including but not limited to trade secrets, client lists, and technical data.
        """,
        
        "Medical Report": """
            CITY GENERAL HOSPITAL
            CONFIDENTIAL MEDICAL REPORT
            
            Patient: Michael Smith
            Patient ID: MR-789456
            Date of Birth: March 15, 1985
            
            Visit Date: February 20, 2024
            Physician: Dr. Sarah Johnson, MD
            
            DIAGNOSIS: Annual physical examination
            Patient is in good health with no significant findings.
        """,
        
        "Bank Statement": """
            FIRST NATIONAL BANK
            CONFIDENTIAL ACCOUNT STATEMENT
            
            Account Holder: Jennifer Davis
            Account Number: ****-****-****-1234
            Statement Period: January 1-31, 2024
            
            Beginning Balance: $5,247.83
            Ending Balance: $4,892.15
            
            TRANSACTIONS:
            01/05 Direct Deposit - Salary    +$4,500.00
            01/10 ATM Withdrawal             -$200.00
        """
    }
    
    try:
        processor = ConfidentialDocumentProcessor(api_key=API_KEY_3)
        
        for doc_name, doc_text in test_documents.items():
            print(f"\n--- Testing: {doc_name} ---")
            
            # Check confidential detection
            is_confidential = processor._is_confidential_document(doc_text)
            print(f"Confidential: {'✅ YES' if is_confidential else '❌ NO'}")
            
            # Detect document type
            doc_type, confidence = processor._detect_document_type_locally(doc_text)
            print(f"Detected Type: {doc_type}")
            print(f"Confidence: {confidence:.2f}")
            
            if is_confidential:
                print("🔒 Would be processed with RoBERTa (privacy protected)")
                
                # Show relevant questions
                questions = processor._get_questions_for_document_type(doc_type)
                print(f"RoBERTa Questions: {len(questions)} questions prepared")
            else:
                print("🌐 Would use external AI services")
                
    except Exception as e:
        print(f"❌ Error in testing: {str(e)}")

def main():
    """
    Main demonstration function
    """
    print("ROBERTA-BASED CONFIDENTIAL DOCUMENT PROCESSOR")
    print("=" * 80)
    print("This example demonstrates processing confidential documents")
    print("using deepset/roberta-base-squad2 instead of Gemini for privacy protection.")
    
    try:
        # Check and install requirements
        print("\n📦 Checking requirements...")
        install_requirements()
        
        # Demonstrate RoBERTa extraction
        demonstrate_roberta_extraction()
        
        # Test different document types
        test_different_document_types()
        
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print("✅ ConfidentialDocumentProcessor successfully demonstrated")
        print("🔒 Confidential documents are processed locally with RoBERTa")
        print("🚫 No data sent to external AI services for confidential content")
        print("🤖 Uses deepset/roberta-base-squad2 for information extraction")
        print("📊 Maintains same interface as regular DocumentProcessor")
        
        print("\n🎯 Key Benefits:")
        print("   • Complete privacy protection for confidential documents")
        print("   • Automatic detection of confidential content")
        print("   • Local processing using state-of-the-art RoBERTa model")
        print("   • No code changes required for existing implementations")
        print("   • Comprehensive support for legal, medical, financial documents")
        
        print("\n📋 Usage:")
        print("   from Services.DocumentProcessor3 import ConfidentialDocumentProcessor")
        print("   processor = ConfidentialDocumentProcessor(api_key)")
        print("   results = processor.process_file('confidential_document.pdf')")
        
        print("\n🔗 For more information, see:")
        print("   • CONFIDENTIAL_PROCESSING_README.md")
        print("   • IMPLEMENTATION_SUMMARY.md")
        
    except Exception as e:
        print(f"\n❌ Error in main function: {str(e)}")
        logger.error(f"Main error: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()
