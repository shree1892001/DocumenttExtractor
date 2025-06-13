from abc import ABC, abstractmethod
import google.generativeai as genai
import logging

logger = logging.getLogger(__name__)

class BaseTextExtractor(ABC):
    def __init__(self, api_key: str):
        from Common.gemini_config import GeminiConfig
        self.api_key = api_key
        self.config = GeminiConfig.create_vision_processor_config(api_key)
        self.model = self.config.get_model()

    @abstractmethod
    def extract_text(self, file_path: str) -> str:
        pass 