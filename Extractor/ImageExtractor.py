import os
import google.generativeai as genai
from IPython.display import Image as IPImage

class ImageTextExtractor:
    def __init__(self, api_key, model_name=None):
        from Common.gemini_config import GeminiConfig
        self.api_key = api_key
        self.config = GeminiConfig.create_vision_processor_config(api_key)
        self.model_name = model_name or self.config.model_config.name
        self._configure_api()

    def _configure_api(self):
        os.environ['GOOGLE_API_KEY'] = self.api_key
        # Configuration is handled by GeminiConfig

    def query_gemini_llm(self, image_path, prompt):
        ip_image = IPImage(filename=image_path)
        vision_model = self.config.get_model()
        response = vision_model.generate_content([prompt, ip_image])
        return response.text