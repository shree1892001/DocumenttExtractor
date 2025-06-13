"""
Base Text Processor Module
Provides a standardized text processor using Gemini configuration.
"""

import logging
from typing import Optional, Dict, Any
from .gemini_config import GeminiConfig
import google.generativeai as genai

logger = logging.getLogger(__name__)


class BaseTextProcessor:
    """
    Base text processor class using centralized Gemini configuration
    """
    
    def __init__(self, api_key: Optional[str] = None, model_type: str = "text", config: Optional[GeminiConfig] = None):
        """
        Initialize the text processor
        
        Args:
            api_key: Google AI API key (optional if config provided)
            model_type: Type of model to use ('text', 'vision', 'pro')
            config: Pre-configured GeminiConfig instance (optional)
        """
        if config:
            self.config = config
        else:
            self.config = GeminiConfig(api_key=api_key, model_type=model_type)
        
        self.model = self.config.get_model()
        logger.info(f"BaseTextProcessor initialized with model: {self.config.model_config.name}")
    
    def process_text(self, text: str, prompt: str) -> str:
        """
        Process text using Gemini model
        
        Args:
            text: Input text to process
            prompt: Processing prompt/instructions
            
        Returns:
            Processed text response
            
        Raises:
            RuntimeError: If processing fails
        """
        try:
            # Combine prompt and text for processing
            full_prompt = f"{prompt}\n\nText to process:\n{text}"
            
            response = self.model.generate_content(full_prompt)
            
            if not response or not response.text:
                raise ValueError("Empty response from Gemini model")
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error processing text with Gemini: {str(e)}")
            raise RuntimeError(f"Text processing failed: {str(e)}")
    
    def process_with_context(self, text: str, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Process text with additional context
        
        Args:
            text: Input text to process
            prompt: Processing prompt/instructions
            context: Additional context information
            
        Returns:
            Processed text response
        """
        try:
            # Build context string if provided
            context_str = ""
            if context:
                context_str = "\n\nAdditional Context:\n"
                for key, value in context.items():
                    context_str += f"{key}: {value}\n"
            
            # Combine prompt, context, and text
            full_prompt = f"{prompt}{context_str}\n\nText to process:\n{text}"
            
            response = self.model.generate_content(full_prompt)
            
            if not response or not response.text:
                raise ValueError("Empty response from Gemini model")
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error processing text with context: {str(e)}")
            raise RuntimeError(f"Text processing with context failed: {str(e)}")
    
    def process_image_with_text(self, image_path: str, prompt: str, text: Optional[str] = None) -> str:
        """
        Process image with optional text using vision model
        
        Args:
            image_path: Path to image file
            prompt: Processing prompt/instructions
            text: Optional additional text context
            
        Returns:
            Processed response
        """
        try:
            # Ensure we're using a vision-capable model
            if self.config.model_type != "vision":
                logger.warning("Switching to vision model for image processing")
                self.config.set_model_type("vision")
                self.model = self.config.get_model()
            
            # Prepare content for vision model
            content_parts = [prompt]
            
            # Add image
            try:
                from PIL import Image
                image = Image.open(image_path)
                content_parts.append(image)
            except Exception as e:
                logger.error(f"Error loading image {image_path}: {str(e)}")
                raise ValueError(f"Failed to load image: {str(e)}")
            
            # Add text if provided
            if text:
                content_parts.append(f"\n\nAdditional text context:\n{text}")
            
            response = self.model.generate_content(content_parts)
            
            if not response or not response.text:
                raise ValueError("Empty response from Gemini vision model")
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error processing image with text: {str(e)}")
            raise RuntimeError(f"Image processing failed: {str(e)}")
    
    def update_model_settings(self, **kwargs):
        """
        Update model generation settings
        
        Args:
            **kwargs: Generation config parameters
        """
        self.config.update_generation_config(**kwargs)
        # Recreate model with new settings
        self.model = self.config.get_model()
        logger.info(f"Updated model settings: {kwargs}")
    
    def switch_model_type(self, model_type: str):
        """
        Switch to a different model type
        
        Args:
            model_type: New model type ('text', 'vision', 'pro')
        """
        self.config.set_model_type(model_type)
        self.model = self.config.get_model()
        logger.info(f"Switched to model type: {model_type}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model configuration
        
        Returns:
            Dictionary with model information
        """
        return self.config.get_model_info()
    
    def test_connection(self) -> bool:
        """
        Test the connection to Gemini API
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            test_response = self.model.generate_content("Test connection. Respond with 'OK'.")
            return test_response and test_response.text and "OK" in test_response.text.upper()
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False


class DocumentTextProcessor(BaseTextProcessor):
    """
    Specialized text processor for document processing tasks
    """
    
    def __init__(self, api_key: Optional[str] = None, config: Optional[GeminiConfig] = None):
        """
        Initialize document text processor
        
        Args:
            api_key: Google AI API key (optional if config provided)
            config: Pre-configured GeminiConfig instance (optional)
        """
        # Use text model optimized for document processing
        if config is None:
            config = GeminiConfig.create_text_processor_config(api_key)
        
        super().__init__(config=config)
        logger.info("DocumentTextProcessor initialized")
    
    def extract_document_data(self, text: str, document_type: str, extraction_prompt: str) -> str:
        """
        Extract structured data from document text
        
        Args:
            text: Document text
            document_type: Type of document
            extraction_prompt: Extraction instructions
            
        Returns:
            Extracted data as JSON string
        """
        context = {
            "document_type": document_type,
            "task": "data_extraction",
            "output_format": "JSON"
        }
        
        return self.process_with_context(text, extraction_prompt, context)
    
    def verify_document(self, document_data: str, verification_prompt: str) -> str:
        """
        Verify document authenticity
        
        Args:
            document_data: Document data to verify
            verification_prompt: Verification instructions
            
        Returns:
            Verification results as JSON string
        """
        context = {
            "task": "document_verification",
            "output_format": "JSON"
        }
        
        return self.process_with_context(document_data, verification_prompt, context)
    
    def detect_document_type(self, text: str, detection_prompt: str) -> str:
        """
        Detect document type from text
        
        Args:
            text: Document text
            detection_prompt: Detection instructions
            
        Returns:
            Detection results as JSON string
        """
        context = {
            "task": "document_type_detection",
            "output_format": "JSON"
        }
        
        return self.process_with_context(text, detection_prompt, context)


class VisionTextProcessor(BaseTextProcessor):
    """
    Specialized text processor for vision/image processing tasks
    """
    
    def __init__(self, api_key: Optional[str] = None, config: Optional[GeminiConfig] = None):
        """
        Initialize vision text processor
        
        Args:
            api_key: Google AI API key (optional if config provided)
            config: Pre-configured GeminiConfig instance (optional)
        """
        # Use vision model optimized for image processing
        if config is None:
            config = GeminiConfig.create_vision_processor_config(api_key)
        
        super().__init__(config=config)
        logger.info("VisionTextProcessor initialized")
    
    def extract_text_from_image(self, image_path: str, extraction_prompt: str = None) -> str:
        """
        Extract text from image using OCR
        
        Args:
            image_path: Path to image file
            extraction_prompt: Custom extraction prompt (optional)
            
        Returns:
            Extracted text
        """
        if extraction_prompt is None:
            from .constants import OCR_TEXT_EXTRACTION_PROMPT
            extraction_prompt = OCR_TEXT_EXTRACTION_PROMPT
        
        return self.process_image_with_text(image_path, extraction_prompt)
    
    def analyze_document_image(self, image_path: str, analysis_prompt: str) -> str:
        """
        Analyze document image for structure and content
        
        Args:
            image_path: Path to image file
            analysis_prompt: Analysis instructions
            
        Returns:
            Analysis results
        """
        return self.process_image_with_text(image_path, analysis_prompt)
