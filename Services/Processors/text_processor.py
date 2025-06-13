import google.generativeai as genai
import logging

logger = logging.getLogger(__name__)

class TextProcessor:
    def __init__(self, api_key: str):
        from Common.gemini_config import GeminiConfig
        self.api_key = api_key
        self.config = GeminiConfig.create_text_processor_config(api_key)
        self.model = self.config.get_model()

    def process_text(self, text: str, prompt: str) -> str:
        """Process text using Gemini without image handling"""
        try:
            response = self.model.generate_content([prompt, text])
            return response.text
        except Exception as e:
            logger.error(f"Error processing text with Gemini: {str(e)}")
            raise 