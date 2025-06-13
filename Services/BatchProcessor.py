import os
import json
import time
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import concurrent.futures
from tqdm import tqdm
import multiprocessing
from queue import Queue
import threading
from Services.DocumenProcessor2 import DocumentProcessor
from Common.constants import API_KEY_1
import shutil
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import constants from central constants file
from Common.constants import (
    BATCH_SIZE, MAX_WORKERS, CHUNK_SIZE, MAX_RETRIES,
    TEMPLATE_SIMILARITY_THRESHOLD, SUPPORTED_EXTENSIONS
)

@dataclass
class ProcessingResult:
    file_path: str
    status: str
    document_type: Optional[str] = None
    confidence_score: Optional[float] = None
    extracted_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time: Optional[float] = None
    template_used: Optional[str] = None
    template_similarity: Optional[float] = None

class DynamicTemplateManager:
    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = templates_dir
        self.templates = {}
        self.template_hashes = {}
        self.load_templates()

    def load_templates(self):
        """Load all templates from the templates directory"""
        os.makedirs(self.templates_dir, exist_ok=True)
        
        for file_path in Path(self.templates_dir).rglob("*"):
            if file_path.is_file():
                try:
                    # Calculate file hash
                    file_hash = self._calculate_file_hash(file_path)
                    
                    # Store template
                    self.templates[str(file_path)] = {
                        "path": str(file_path),
                        "hash": file_hash,
                        "type": self._infer_document_type(file_path),
                        "last_used": 0,
                        "success_count": 0,
                        "failure_count": 0
                    }
                    self.template_hashes[file_hash] = str(file_path)
                    
                except Exception as e:
                    logger.error(f"Error loading template {file_path}: {str(e)}")

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate hash of file content"""
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(CHUNK_SIZE), b''):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _infer_document_type(self, file_path: Path) -> str:
        """Infer document type from filename and content"""
        # Extract base name without extension
        base_name = file_path.stem.lower()
        
        # Remove common prefixes and suffixes
        base_name = base_name.replace('sample_', '').replace('template_', '')
        
        # Remove file extension
        base_name = base_name.split('.')[0]
        
        return base_name

    def add_template(self, file_path: str, document_type: Optional[str] = None) -> bool:
        """Add a new template"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return False

            # Calculate hash
            file_hash = self._calculate_file_hash(file_path)
            
            # If template already exists, update it
            if file_hash in self.template_hashes:
                existing_path = self.template_hashes[file_hash]
                self.templates[existing_path]["last_used"] = time.time()
                return True

            # Copy template to templates directory
            template_path = Path(self.templates_dir) / file_path.name
            shutil.copy2(file_path, template_path)

            # Store template info
            doc_type = document_type or self._infer_document_type(file_path)
            self.templates[str(template_path)] = {
                "path": str(template_path),
                "hash": file_hash,
                "type": doc_type,
                "last_used": time.time(),
                "success_count": 0,
                "failure_count": 0
            }
            self.template_hashes[file_hash] = str(template_path)
            
            return True

        except Exception as e:
            logger.error(f"Error adding template {file_path}: {str(e)}")
            return False

    def get_best_template(self, document_path: str) -> Optional[Dict[str, Any]]:
        """Get the best matching template for a document"""
        try:
            doc_hash = self._calculate_file_hash(Path(document_path))
            
            # First try exact hash match
            if doc_hash in self.template_hashes:
                template_path = self.template_hashes[doc_hash]
                return self.templates[template_path]

            # If no exact match, try similarity matching
            best_match = None
            best_score = 0

            for template in self.templates.values():
                similarity = self._calculate_similarity(document_path, template["path"])
                if similarity > best_score and similarity >= TEMPLATE_SIMILARITY_THRESHOLD:
                    best_score = similarity
                    best_match = template

            return best_match

        except Exception as e:
            logger.error(f"Error finding template for {document_path}: {str(e)}")
            return None

    def _calculate_similarity(self, doc_path: str, template_path: str) -> float:
        """Calculate similarity between document and template"""
        try:
            # Use the DocumentProcessor to compare documents
            processor = DocumentProcessor(API_KEY_1)
            doc_result = processor.process_file(doc_path)
            template_result = processor.process_file(template_path)

            if not doc_result or not template_result:
                return 0.0

            # Compare document structures and content
            doc_structure = self._extract_structure(doc_result[0])
            template_structure = self._extract_structure(template_result[0])

            # Calculate similarity score
            structure_similarity = self._compare_structures(doc_structure, template_structure)
            content_similarity = self._compare_content(doc_result[0], template_result[0])

            # Weighted average of structure and content similarity
            return 0.6 * structure_similarity + 0.4 * content_similarity

        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0

    def _extract_structure(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract document structure from processing result"""
        structure = {
            "document_type": result.get("document_type"),
            "fields": set(result.get("extracted_data", {}).keys()),
            "confidence": result.get("confidence", 0)
        }
        return structure

    def _compare_structures(self, doc_structure: Dict[str, Any], template_structure: Dict[str, Any]) -> float:
        """Compare document structures"""
        if doc_structure["document_type"] != template_structure["document_type"]:
            return 0.0

        # Compare field sets
        doc_fields = doc_structure["fields"]
        template_fields = template_structure["fields"]
        
        if not doc_fields or not template_fields:
            return 0.0

        # Calculate Jaccard similarity
        intersection = len(doc_fields.intersection(template_fields))
        union = len(doc_fields.union(template_fields))
        
        return intersection / union if union > 0 else 0.0

    def _compare_content(self, doc_result: Dict[str, Any], template_result: Dict[str, Any]) -> float:
        """Compare document content"""
        doc_data = doc_result.get("extracted_data", {})
        template_data = template_result.get("extracted_data", {})
        
        if not doc_data or not template_data:
            return 0.0

        # Compare common fields
        common_fields = set(doc_data.keys()).intersection(set(template_data.keys()))
        if not common_fields:
            return 0.0

        # Calculate average similarity for common fields
        similarities = []
        for field in common_fields:
            doc_value = str(doc_data[field]).lower()
            template_value = str(template_data[field]).lower()
            
            # Calculate Levenshtein similarity
            similarity = self._levenshtein_similarity(doc_value, template_value)
            similarities.append(similarity)

        return sum(similarities) / len(similarities) if similarities else 0.0

    def _levenshtein_similarity(self, s1: str, s2: str) -> float:
        """Calculate Levenshtein similarity between two strings"""
        if not s1 or not s2:
            return 0.0

        # Calculate Levenshtein distance
        m, n = len(s1), len(s2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
            
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if s1[i-1] == s2[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]) + 1

        # Convert distance to similarity
        max_len = max(m, n)
        if max_len == 0:
            return 1.0
        return 1 - (dp[m][n] / max_len)

    def update_template_stats(self, template_path: str, success: bool):
        """Update template usage statistics"""
        if template_path in self.templates:
            if success:
                self.templates[template_path]["success_count"] += 1
            else:
                self.templates[template_path]["failure_count"] += 1
            self.templates[template_path]["last_used"] = time.time()

class BatchProcessor:
    def __init__(self, api_key: str = API_KEY_1, output_dir: str = "results"):
        self.api_key = api_key
        self.output_dir = output_dir
        self.processor = DocumentProcessor(api_key)
        self.template_manager = DynamicTemplateManager()
        self.results_queue = Queue()
        self.progress_bar = None
        self.total_documents = 0
        self.processed_documents = 0
        self.failed_documents = 0
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize results storage
        self.results = {
            "successful": [],
            "failed": [],
            "skipped": []
        }

    def process_directory(self, input_dir: str, file_patterns: List[str] = None) -> Dict[str, Any]:
        """Process all documents in a directory"""
        try:
            # Get list of all files
            all_files = self._get_files(input_dir, file_patterns)
            self.total_documents = len(all_files)
            
            if self.total_documents == 0:
                logger.warning(f"No files found in directory: {input_dir}")
                return self.results

            # Initialize progress bar
            self.progress_bar = tqdm(total=self.total_documents, desc="Processing documents")
            
            # Process files in batches
            for i in range(0, len(all_files), BATCH_SIZE):
                batch = all_files[i:i + BATCH_SIZE]
                self._process_batch(batch)
                
                # Save intermediate results
                self._save_results()
                
                # Clear memory
                self._clear_memory()

            # Final save of results
            self._save_results()
            
            return self.results

        except Exception as e:
            logger.error(f"Error processing directory: {str(e)}")
            return self.results

    def _get_files(self, input_dir: str, file_patterns: List[str] = None) -> List[str]:
        """Get list of files to process"""
        files = []
        if file_patterns is None:
            file_patterns = list(SUPPORTED_EXTENSIONS)
            
        for pattern in file_patterns:
            files.extend(list(Path(input_dir).rglob(f"*{pattern}")))
            
        return [str(f) for f in files]

    def _process_batch(self, batch: List[str]) -> None:
        """Process a batch of documents in parallel"""
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(self._process_single_file, file_path): file_path 
                for file_path in batch
            }
            
            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    self._handle_result(result)
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {str(e)}")
                    self._handle_result(ProcessingResult(
                        file_path=file_path,
                        status="error",
                        error=str(e)
                    ))

    def _process_single_file(self, file_path: str) -> ProcessingResult:
        """Process a single file with retries"""
        start_time = time.time()
        
        for attempt in range(MAX_RETRIES):
            try:
                # Find best matching template
                template = self.template_manager.get_best_template(file_path)
                
                if template:
                    # Process with template
                    results = self.processor.process_file(file_path)
                    
                    if not results:
                        return ProcessingResult(
                            file_path=file_path,
                            status="skipped",
                            processing_time=time.time() - start_time
                        )
                    
                    # Get the best result
                    best_result = max(results, key=lambda x: x.get("confidence", 0))
                    
                    # Update template statistics
                    self.template_manager.update_template_stats(
                        template["path"],
                        best_result.get("confidence", 0) >= 0.7
                    )
                    
                    return ProcessingResult(
                        file_path=file_path,
                        status="success",
                        document_type=best_result.get("document_type"),
                        confidence_score=best_result.get("confidence"),
                        extracted_data=best_result.get("extracted_data"),
                        processing_time=time.time() - start_time,
                        template_used=template["path"],
                        template_similarity=template.get("similarity", 0)
                    )
                else:
                    # If no template found, try to process as new document type
                    results = self.processor.process_file(file_path)
                    
                    if results and results[0].get("confidence", 0) >= 0.7:
                        # Add as new template
                        self.template_manager.add_template(file_path)
                        
                        return ProcessingResult(
                            file_path=file_path,
                            status="success",
                            document_type=results[0].get("document_type"),
                            confidence_score=results[0].get("confidence"),
                            extracted_data=results[0].get("extracted_data"),
                            processing_time=time.time() - start_time
                        )
                    else:
                        return ProcessingResult(
                            file_path=file_path,
                            status="skipped",
                            processing_time=time.time() - start_time
                        )
                    
            except Exception as e:
                if attempt == MAX_RETRIES - 1:
                    return ProcessingResult(
                        file_path=file_path,
                        status="error",
                        error=str(e),
                        processing_time=time.time() - start_time
                    )
                time.sleep(1)  # Wait before retry

    def _handle_result(self, result: ProcessingResult) -> None:
        """Handle processing result"""
        if result.status == "success":
            self.results["successful"].append(result)
            self.processed_documents += 1
        elif result.status == "error":
            self.results["failed"].append(result)
            self.failed_documents += 1
        else:
            self.results["skipped"].append(result)
            
        # Update progress bar
        if self.progress_bar:
            self.progress_bar.update(1)
            
        # Log progress
        logger.info(f"Processed {self.processed_documents}/{self.total_documents} documents "
                   f"({self.failed_documents} failed)")

    def _save_results(self) -> None:
        """Save processing results to files"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        # Save successful results
        if self.results["successful"]:
            success_file = os.path.join(self.output_dir, f"successful_{timestamp}.json")
            with open(success_file, 'w', encoding='utf-8') as f:
                json.dump([vars(r) for r in self.results["successful"]], f, indent=2)
                
        # Save failed results
        if self.results["failed"]:
            failed_file = os.path.join(self.output_dir, f"failed_{timestamp}.json")
            with open(failed_file, 'w', encoding='utf-8') as f:
                json.dump([vars(r) for r in self.results["failed"]], f, indent=2)
                
        # Save skipped results
        if self.results["skipped"]:
            skipped_file = os.path.join(self.output_dir, f"skipped_{timestamp}.json")
            with open(skipped_file, 'w', encoding='utf-8') as f:
                json.dump([vars(r) for r in self.results["skipped"]], f, indent=2)

    def _clear_memory(self) -> None:
        """Clear memory after batch processing"""
        import gc
        gc.collect()

def main():
    # Example usage
    input_dir = "D:\\imageextractor\\identites\\documents"  # Directory containing documents
    output_dir = "D:\\imageextractor\\identites\\results"   # Directory for results
    
    # Initialize batch processor
    processor = BatchProcessor(api_key=API_KEY_1, output_dir=output_dir)
    
    # Process all documents
    results = processor.process_directory(input_dir)
    
    # Print summary
    print("\nProcessing Summary:")
    print(f"Total documents: {processor.total_documents}")
    print(f"Successfully processed: {processor.processed_documents}")
    print(f"Failed: {processor.failed_documents}")
    print(f"Skipped: {len(results['skipped'])}")
    
    # Print error summary if any
    if results["failed"]:
        print("\nError Summary:")
        error_types = {}
        for result in results["failed"]:
            error_type = result.error.split(":")[0] if result.error else "Unknown"
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        for error_type, count in error_types.items():
            print(f"{error_type}: {count}")

if __name__ == "__main__":
    main() 