"""
HybridConfidentialProcessor - Gives users choice between processing modes:

1. LOCAL_ONLY: 100% offline processing with rule-based extraction
2. ROBERTA_LOCAL: Uses pre-downloaded RoBERTa model (local after first download)
3. AUTO: Automatically chooses based on model availability

This addresses the concern about external model dependencies while providing flexibility.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from enum import Enum

# Import both processors
from Services.LocalConfidentialProcessor import LocalConfidentialProcessor
from Services.ConfidentialProcessor import ConfidentialProcessor

logger = logging.getLogger(__name__)


class ProcessingMode(Enum):
    """Processing mode options"""
    LOCAL_ONLY = "local_only"           # 100% offline, rule-based extraction
    ROBERTA_LOCAL = "roberta_local"     # RoBERTa model (local after download)
    AUTO = "auto"                       # Automatic selection based on availability


class HybridConfidentialProcessor:
    """
    Hybrid processor that allows users to choose their preferred processing mode
    based on their privacy requirements and model availability.
    """
    
    def __init__(self, mode: ProcessingMode = ProcessingMode.AUTO):
        """
        Initialize the hybrid processor
        
        Args:
            mode: Processing mode to use
        """
        self.mode = mode
        self.local_processor = None
        self.roberta_processor = None
        self.active_processor = None
        
        logger.info(f"Initializing HybridConfidentialProcessor in {mode.value} mode")
        
        # Initialize processors based on mode
        self._initialize_processors()
    
    def _initialize_processors(self):
        """Initialize the appropriate processors based on mode"""
        try:
            if self.mode == ProcessingMode.LOCAL_ONLY:
                # Only initialize local processor
                self.local_processor = LocalConfidentialProcessor()
                self.active_processor = self.local_processor
                logger.info("✅ LOCAL_ONLY mode: Using rule-based extraction (100% offline)")
                
            elif self.mode == ProcessingMode.ROBERTA_LOCAL:
                # Try to initialize RoBERTa processor
                try:
                    self.roberta_processor = ConfidentialProcessor()
                    self.active_processor = self.roberta_processor
                    logger.info("✅ ROBERTA_LOCAL mode: Using RoBERTa model (local after download)")
                except Exception as e:
                    logger.warning(f"RoBERTa processor failed to initialize: {str(e)}")
                    logger.info("Falling back to LOCAL_ONLY mode")
                    self.local_processor = LocalConfidentialProcessor()
                    self.active_processor = self.local_processor
                    
            elif self.mode == ProcessingMode.AUTO:
                # Try RoBERTa first, fallback to local
                try:
                    self.roberta_processor = ConfidentialProcessor()
                    self.active_processor = self.roberta_processor
                    logger.info("✅ AUTO mode: RoBERTa available, using advanced extraction")
                except Exception as e:
                    logger.warning(f"RoBERTa not available: {str(e)}")
                    logger.info("AUTO mode: Falling back to local rule-based extraction")
                    self.local_processor = LocalConfidentialProcessor()
                    self.active_processor = self.local_processor
            
            # Always initialize local processor as backup
            if not self.local_processor:
                self.local_processor = LocalConfidentialProcessor()
                
        except Exception as e:
            logger.error(f"Error initializing processors: {str(e)}")
            # Emergency fallback to local processor
            self.local_processor = LocalConfidentialProcessor()
            self.active_processor = self.local_processor
            logger.info("Emergency fallback to LOCAL_ONLY mode")
    
    def get_processing_info(self) -> Dict[str, Any]:
        """Get information about the current processing configuration"""
        info = {
            "mode": self.mode.value,
            "active_processor": type(self.active_processor).__name__,
            "local_processor_available": self.local_processor is not None,
            "roberta_processor_available": self.roberta_processor is not None,
            "offline_capable": True,
            "external_dependencies": self.roberta_processor is not None
        }
        
        if self.roberta_processor:
            try:
                model_info = self.roberta_processor.get_model_info()
                info["roberta_model"] = model_info.get("model_name", "Unknown")
                info["roberta_device"] = model_info.get("device", "Unknown")
            except:
                info["roberta_model"] = "Error getting model info"
        
        return info
    
    def switch_mode(self, new_mode: ProcessingMode) -> bool:
        """
        Switch to a different processing mode
        
        Args:
            new_mode: New processing mode to switch to
            
        Returns:
            True if switch was successful, False otherwise
        """
        try:
            logger.info(f"Switching from {self.mode.value} to {new_mode.value} mode")
            old_mode = self.mode
            self.mode = new_mode
            self._initialize_processors()
            
            if self.active_processor:
                logger.info(f"✅ Successfully switched to {new_mode.value} mode")
                return True
            else:
                logger.error(f"Failed to switch to {new_mode.value} mode")
                self.mode = old_mode
                self._initialize_processors()
                return False
                
        except Exception as e:
            logger.error(f"Error switching modes: {str(e)}")
            return False
    
    def process_file(self, file_path: str, force_local: bool = False) -> Dict[str, Any]:
        """
        Process a file using the active processor
        
        Args:
            file_path: Path to the file to process
            force_local: Force use of local processor regardless of mode
            
        Returns:
            Processing results
        """
        try:
            processor_to_use = self.local_processor if force_local else self.active_processor
            
            if not processor_to_use:
                raise ValueError("No processor available")
            
            result = processor_to_use.process_file(file_path)
            
            # Add hybrid processor metadata
            result["hybrid_processor_info"] = {
                "mode": self.mode.value,
                "processor_used": type(processor_to_use).__name__,
                "forced_local": force_local,
                "offline_processing": isinstance(processor_to_use, LocalConfidentialProcessor)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            return {
                "status": "error",
                "source_file": file_path,
                "error_message": str(e),
                "hybrid_processor_info": {
                    "mode": self.mode.value,
                    "error": "Processing failed"
                }
            }
    
    def process_document_text(self, text: str, source_file: str = None, force_local: bool = False) -> Dict[str, Any]:
        """
        Process document text using the active processor
        
        Args:
            text: Document text content
            source_file: Optional source file path
            force_local: Force use of local processor regardless of mode
            
        Returns:
            Processing results
        """
        try:
            processor_to_use = self.local_processor if force_local else self.active_processor
            
            if not processor_to_use:
                raise ValueError("No processor available")
            
            result = processor_to_use.process_document_text(text, source_file)
            
            # Add hybrid processor metadata
            result["hybrid_processor_info"] = {
                "mode": self.mode.value,
                "processor_used": type(processor_to_use).__name__,
                "forced_local": force_local,
                "offline_processing": isinstance(processor_to_use, LocalConfidentialProcessor)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing text: {str(e)}")
            return {
                "status": "error",
                "source_file": source_file or "text_input",
                "error_message": str(e),
                "hybrid_processor_info": {
                    "mode": self.mode.value,
                    "error": "Processing failed"
                }
            }
    
    def batch_process_files(self, file_paths: List[str], force_local: bool = False) -> List[Dict[str, Any]]:
        """
        Process multiple files using the active processor
        
        Args:
            file_paths: List of file paths to process
            force_local: Force use of local processor regardless of mode
            
        Returns:
            List of processing results
        """
        processor_to_use = self.local_processor if force_local else self.active_processor
        
        if not processor_to_use:
            return [{
                "status": "error",
                "source_file": path,
                "error_message": "No processor available",
                "hybrid_processor_info": {"mode": self.mode.value, "error": "No processor"}
            } for path in file_paths]
        
        results = processor_to_use.batch_process_files(file_paths)
        
        # Add hybrid processor metadata to each result
        for result in results:
            result["hybrid_processor_info"] = {
                "mode": self.mode.value,
                "processor_used": type(processor_to_use).__name__,
                "forced_local": force_local,
                "offline_processing": isinstance(processor_to_use, LocalConfidentialProcessor)
            }
        
        return results
    
    def is_confidential_document(self, text: str, doc_type: str = None) -> bool:
        """Check if document is confidential using the active processor"""
        processor_to_use = self.active_processor or self.local_processor
        return processor_to_use.is_confidential_document(text, doc_type)


# Utility functions for easy usage
def create_hybrid_processor(mode: ProcessingMode = ProcessingMode.AUTO) -> HybridConfidentialProcessor:
    """Create and initialize a HybridConfidentialProcessor instance"""
    return HybridConfidentialProcessor(mode)


def create_local_only_processor() -> HybridConfidentialProcessor:
    """Create a processor that uses only local rule-based extraction (100% offline)"""
    return HybridConfidentialProcessor(ProcessingMode.LOCAL_ONLY)


def create_roberta_processor() -> HybridConfidentialProcessor:
    """Create a processor that uses RoBERTa model (local after download)"""
    return HybridConfidentialProcessor(ProcessingMode.ROBERTA_LOCAL)


def process_confidential_document_hybrid(file_path: str, mode: ProcessingMode = ProcessingMode.AUTO) -> Dict[str, Any]:
    """Quick function to process a single confidential document with specified mode"""
    processor = create_hybrid_processor(mode)
    return processor.process_file(file_path)


# Example usage
if __name__ == "__main__":
    print("HYBRID CONFIDENTIAL PROCESSOR - FLEXIBLE PROCESSING MODES")
    print("=" * 70)
    
    try:
        # Test all modes
        modes_to_test = [
            ProcessingMode.LOCAL_ONLY,
            ProcessingMode.ROBERTA_LOCAL,
            ProcessingMode.AUTO
        ]
        
        for mode in modes_to_test:
            print(f"\n🧪 Testing {mode.value.upper()} mode:")
            try:
                processor = create_hybrid_processor(mode)
                info = processor.get_processing_info()
                
                print(f"   Active Processor: {info['active_processor']}")
                print(f"   Offline Capable: {info['offline_capable']}")
                print(f"   External Dependencies: {info['external_dependencies']}")
                
                if info.get('roberta_model'):
                    print(f"   RoBERTa Model: {info['roberta_model']}")
                
                print(f"   ✅ {mode.value.upper()} mode working")
                
            except Exception as e:
                print(f"   ❌ {mode.value.upper()} mode failed: {str(e)}")
        
        print("\n🎯 Usage Recommendations:")
        print("   • LOCAL_ONLY: Maximum privacy, 100% offline, rule-based extraction")
        print("   • ROBERTA_LOCAL: High accuracy, local after download, AI-powered")
        print("   • AUTO: Best of both worlds, automatic fallback")
        
        print("\n✅ HybridConfidentialProcessor provides flexible processing options!")
        
    except Exception as e:
        print(f"❌ Error in hybrid processor demo: {str(e)}")
