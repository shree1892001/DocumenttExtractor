from DocumentProcessor3 import DocumentProcessor3
from Logging_file.logging_file import custom_logger
import os

class DocumentProcessor:
    def __init__(self):
        self.processor = DocumentProcessor3(api_key=os.getenv("API_KEY", "your_api_key"))

    def process_document(self, file_path: str):
        """
        Process a document by matching it against templates and extracting data.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Dictionary containing:
            - document_type: Type of document matched
            - template_confidence: Confidence score of template match
            - genuineness_score: Score indicating document authenticity
            - verification_score: Score for extracted information verification
            - extracted_fields: Dictionary of extracted field values
            - raw_text: Raw text extracted from document
        """
        try:
            # Process the document
            result = self.processor.process_document(file_path)
            
            # Log success
            custom_logger.info(f"Successfully processed document: {file_path}")
            custom_logger.info(f"Matched template: {result['document_type']} with confidence {result['template_confidence']}")
            
            return result
            
        except Exception as e:
            custom_logger.error(f"Error processing document: {str(e)}")
            raise 