import logging
import functools
import time
from typing import Callable, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

class CustomLogger:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def info(self, message: str):
        self.logger.info(message)

    def error(self, message: str):
        self.logger.error(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def debug(self, message: str):
        self.logger.debug(message)

    def log_around(self, func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            self.logger.info(f"Starting {func.__name__}")
            
            try:
                result = await func(*args, **kwargs)
                end_time = time.time()
                self.logger.info(f"Completed {func.__name__} in {end_time - start_time:.2f} seconds")
                return result
            except Exception as e:
                self.logger.error(f"Error in {func.__name__}: {str(e)}")
                raise
                
        return wrapper

# Create a singleton instance
custom_logger = CustomLogger() 