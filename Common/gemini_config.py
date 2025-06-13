"""
Gemini Configuration Module
Centralized configuration for Google Gemini AI models and settings.
"""

import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
import google.generativeai as genai

logger = logging.getLogger(__name__)


@dataclass
class GeminiModelConfig:
    """Configuration for a specific Gemini model"""
    name: str
    display_name: str
    description: str
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None


@dataclass
class GeminiSafetySettings:
    """Safety settings for Gemini models"""
    harassment: str = "BLOCK_MEDIUM_AND_ABOVE"
    hate_speech: str = "BLOCK_MEDIUM_AND_ABOVE"
    sexually_explicit: str = "BLOCK_MEDIUM_AND_ABOVE"
    dangerous_content: str = "BLOCK_MEDIUM_AND_ABOVE"


@dataclass
class GeminiDocumentSafetySettings:
    """More permissive safety settings for document processing"""
    harassment: str = "BLOCK_ONLY_HIGH"
    hate_speech: str = "BLOCK_ONLY_HIGH"
    sexually_explicit: str = "BLOCK_MEDIUM_AND_ABOVE"
    dangerous_content: str = "BLOCK_ONLY_HIGH"  # More permissive for document content


class GeminiConfig:
    """Centralized configuration class for Gemini AI models"""
    
    # Default model configurations
    MODELS = {
        "text": GeminiModelConfig(
            name="gemini-1.5-flash",
            display_name="Gemini 1.5 Flash",
            description="Fast text processing model for document analysis",
            max_tokens=8192,
            temperature=0.1,
            top_p=0.8,
            top_k=40
        ),
        "vision": GeminiModelConfig(
            name="gemini-1.5-flash",
            display_name="Gemini 1.5 Flash Vision",
            description="Vision model for image and document processing",
            max_tokens=8192,
            temperature=0.1,
            top_p=0.8,
            top_k=40
        ),
        "pro": GeminiModelConfig(
            name="gemini-1.5-pro",
            display_name="Gemini 1.5 Pro",
            description="Advanced model for complex document processing",
            max_tokens=32768,
            temperature=0.1,
            top_p=0.9,
            top_k=50
        )
    }
    
    # Default safety settings
    DEFAULT_SAFETY_SETTINGS = GeminiSafetySettings()
    
    # Generation configuration
    DEFAULT_GENERATION_CONFIG = {
        "temperature": 0.1,
        "top_p": 0.8,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain"
    }
    
    def __init__(self, api_key: Optional[str] = None, model_type: str = "text"):
        """
        Initialize Gemini configuration
        
        Args:
            api_key: Google AI API key (if None, will try to get from environment)
            model_type: Type of model to use ('text', 'vision', 'pro')
        """
        self.api_key = api_key or self._get_api_key_from_env()
        self.model_type = model_type
        self.model_config = self.MODELS.get(model_type, self.MODELS["text"])
        self.safety_settings = self.DEFAULT_SAFETY_SETTINGS
        self.generation_config = self.DEFAULT_GENERATION_CONFIG.copy()
        
        # Configure Gemini
        self._configure_gemini()
        
        logger.info(f"Gemini configuration initialized with model: {self.model_config.name}")
    
    def _get_api_key_from_env(self) -> str:
        """Get API key from environment variables"""
        api_key = (
            os.getenv('GOOGLE_API_KEY') or 
            os.getenv('GEMINI_API_KEY') or 
            os.getenv('GOOGLE_AI_API_KEY')
        )
        
        if not api_key:
            raise ValueError(
                "No API key provided. Please set GOOGLE_API_KEY environment variable "
                "or pass api_key parameter"
            )
        
        return api_key
    
    def _configure_gemini(self):
        """Configure Gemini with the API key"""
        try:
            genai.configure(api_key=self.api_key)
            logger.info("Gemini API configured successfully")
        except Exception as e:
            logger.error(f"Failed to configure Gemini API: {str(e)}")
            raise RuntimeError(f"Gemini configuration failed: {str(e)}")
    
    def get_model(self) -> genai.GenerativeModel:
        """
        Get configured Gemini model instance
        
        Returns:
            Configured GenerativeModel instance
        """
        try:
            # Convert safety settings to Gemini format
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": self.safety_settings.harassment
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": self.safety_settings.hate_speech
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": self.safety_settings.sexually_explicit
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": self.safety_settings.dangerous_content
                }
            ]
            
            model = genai.GenerativeModel(
                model_name=self.model_config.name,
                generation_config=self.generation_config,
                safety_settings=safety_settings
            )
            
            logger.debug(f"Created Gemini model: {self.model_config.name}")
            return model
            
        except Exception as e:
            logger.error(f"Failed to create Gemini model: {str(e)}")
            raise RuntimeError(f"Model creation failed: {str(e)}")
    
    def update_generation_config(self, **kwargs):
        """
        Update generation configuration
        
        Args:
            **kwargs: Generation config parameters (temperature, top_p, top_k, etc.)
        """
        self.generation_config.update(kwargs)
        logger.info(f"Updated generation config: {kwargs}")
    
    def update_safety_settings(self, **kwargs):
        """
        Update safety settings
        
        Args:
            **kwargs: Safety setting parameters
        """
        for key, value in kwargs.items():
            if hasattr(self.safety_settings, key):
                setattr(self.safety_settings, key, value)
        logger.info(f"Updated safety settings: {kwargs}")
    
    def set_model_type(self, model_type: str):
        """
        Change the model type
        
        Args:
            model_type: New model type ('text', 'vision', 'pro')
        """
        if model_type not in self.MODELS:
            raise ValueError(f"Unknown model type: {model_type}. Available: {list(self.MODELS.keys())}")
        
        self.model_type = model_type
        self.model_config = self.MODELS[model_type]
        
        # Update generation config with model-specific settings
        if self.model_config.temperature is not None:
            self.generation_config["temperature"] = self.model_config.temperature
        if self.model_config.top_p is not None:
            self.generation_config["top_p"] = self.model_config.top_p
        if self.model_config.top_k is not None:
            self.generation_config["top_k"] = self.model_config.top_k
        if self.model_config.max_tokens is not None:
            self.generation_config["max_output_tokens"] = self.model_config.max_tokens
        
        logger.info(f"Switched to model type: {model_type} ({self.model_config.name})")
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model configuration
        
        Returns:
            Dictionary with model information
        """
        return {
            "model_type": self.model_type,
            "model_name": self.model_config.name,
            "display_name": self.model_config.display_name,
            "description": self.model_config.description,
            "generation_config": self.generation_config,
            "safety_settings": {
                "harassment": self.safety_settings.harassment,
                "hate_speech": self.safety_settings.hate_speech,
                "sexually_explicit": self.safety_settings.sexually_explicit,
                "dangerous_content": self.safety_settings.dangerous_content
            }
        }
    
    @classmethod
    def create_text_processor_config(cls, api_key: Optional[str] = None) -> 'GeminiConfig':
        """
        Create configuration optimized for text processing
        
        Args:
            api_key: API key (optional)
            
        Returns:
            GeminiConfig instance for text processing
        """
        config = cls(api_key=api_key, model_type="text")
        config.update_generation_config(
            temperature=0.1,
            top_p=0.8,
            max_output_tokens=8192
        )
        return config
    
    @classmethod
    def create_vision_processor_config(cls, api_key: Optional[str] = None) -> 'GeminiConfig':
        """
        Create configuration optimized for vision/image processing

        Args:
            api_key: API key (optional)

        Returns:
            GeminiConfig instance for vision processing
        """
        config = cls(api_key=api_key, model_type="vision")
        config.update_generation_config(
            temperature=0.1,
            top_p=0.8,
            max_output_tokens=8192
        )
        return config

    @classmethod
    def create_document_processor_config(cls, api_key: Optional[str] = None) -> 'GeminiConfig':
        """
        Create configuration optimized for document processing with more permissive safety settings

        Args:
            api_key: API key (optional)

        Returns:
            GeminiConfig instance for document processing
        """
        config = cls(api_key=api_key, model_type="text")

        # Use more permissive safety settings for document processing
        config.safety_settings = GeminiDocumentSafetySettings()

        config.update_generation_config(
            temperature=0.1,
            top_p=0.8,
            max_output_tokens=8192
        )
        return config


# Singleton instance for global access
_global_config: Optional[GeminiConfig] = None


def get_global_config() -> GeminiConfig:
    """
    Get the global Gemini configuration instance
    
    Returns:
        Global GeminiConfig instance
    """
    global _global_config
    if _global_config is None:
        raise RuntimeError("Global Gemini config not initialized. Call initialize_global_config() first.")
    return _global_config


def initialize_global_config(api_key: Optional[str] = None, model_type: str = "text") -> GeminiConfig:
    """
    Initialize the global Gemini configuration
    
    Args:
        api_key: API key (optional)
        model_type: Model type to use
        
    Returns:
        Initialized GeminiConfig instance
    """
    global _global_config
    _global_config = GeminiConfig(api_key=api_key, model_type=model_type)
    return _global_config


def is_global_config_initialized() -> bool:
    """
    Check if global configuration is initialized
    
    Returns:
        True if initialized, False otherwise
    """
    return _global_config is not None
