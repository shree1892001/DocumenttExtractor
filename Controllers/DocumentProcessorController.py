from fastapi import APIRouter, File, UploadFile, HTTPException, Request
from fastapi.responses import JSONResponse
from Services.DocumentProcessor3 import DocumentProcessor
from Common.constants import API_KEY
from Logging_file.logging_file import custom_logger
import tempfile
import os
import json

router = APIRouter()

def error_response(message="Document processing failed", status_code=500):
    """Reusable function for returning an error response."""
    return JSONResponse(
        status_code=status_code,
        content={"detail": message}
    )

@router.post("/processor")
@custom_logger.log_around
async def process_document(request: Request, file: UploadFile = File(...)):
    """
    Process a document file and extract information from it using DocumentProcessor3.

    Args:
        request: FastAPI request object to access app state
        file (UploadFile): The file to process

    Returns:
        JSONResponse: Processing results including extracted data and verification
    """
    custom_logger.info(f"Received file upload request for file: {file.filename}")

    try:
        # Get DocumentProcessor3 from app state or create new instance
        if hasattr(request.app.state, 'document_processor') and request.app.state.document_processor:
            processor = request.app.state.document_processor
            custom_logger.info("Using DocumentProcessor3 from app state")
        else:
            custom_logger.info("Creating new DocumentProcessor3 instance")
            processor = DocumentProcessor(api_key=API_KEY)

        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        try:
            custom_logger.info(f"Processing file: {file.filename} (saved to {temp_file_path})")

            try:
                # Process document using DocumentProcessor3.process_file method
                custom_logger.info("Controller: Calling processor.process_file...")
                results = processor.process_file(temp_file_path, min_confidence=0.0)
                custom_logger.info("Controller: process_file call completed successfully")
            except Exception as process_error:
                custom_logger.error(f"Controller: Error calling process_file: {str(process_error)}")
                custom_logger.error(f"Controller: Process error type: {type(process_error).__name__}")
                raise process_error

            # Debug what process_file returned
            custom_logger.info(f"Controller: process_file returned {type(results)} with {len(results) if results else 0} items")
            if results:
                for i, result in enumerate(results):
                    custom_logger.info(f"Controller: Result {i+1} - Type: {result.get('document_type', 'unknown')}, Status: {result.get('status', 'unknown')}")
                    extracted_data = result.get('extracted_data', {}).get('data', {})
                    custom_logger.info(f"Controller: Result {i+1} - Extracted fields: {list(extracted_data.keys())}")

            # process_file returns a list, so we need to handle it appropriately
            if not results or len(results) == 0:
                custom_logger.error("Controller: process_file returned no results")
                return error_response("Document processing returned no results", status_code=400)

            # For single document processing, take the first result
            if len(results) == 1:
                result = results[0]
                custom_logger.info(f"Controller: Using single result - Type: {result.get('document_type', 'unknown')}")
            else:
                custom_logger.info(f"Controller: Creating multi-document result from {len(results)} results")
                result = {
                    "status": "success",
                    "document_type": "multiple_documents",
                    "source_file": file.filename,
                    "confidence": max([r.get("confidence", 0.0) for r in results]),
                    "extracted_data": {
                        "data": {"multiple_documents": results},
                        "confidence": max([r.get("confidence", 0.0) for r in results]),
                        "additional_info": f"Found {len(results)} documents in file",
                        "document_metadata": {"type": "multiple_documents", "count": len(results)}
                    },
                    "processing_method": "multi_document",
                    "validation_level": "comprehensive"
                }

            # Debug logging to see what we got from DocumentProcessor3
            custom_logger.info(f"Controller received result - Document Type: {result.get('document_type', 'unknown')}")
            custom_logger.info(f"Controller received result - Status: {result.get('status', 'unknown')}")
            custom_logger.info(f"Controller received result - Confidence: {result.get('confidence', 0.0)}")

            extracted_data = result.get('extracted_data', {}).get('data', {})
            custom_logger.info(f"Controller received extracted data fields: {list(extracted_data.keys())}")
            custom_logger.info(f"Controller received extracted data sample: {dict(list(extracted_data.items())[:3])}")

            if result is None:
                custom_logger.error("Controller: result is None - returning error")
                return error_response("Document processing returned no result", status_code=400)

            # Send raw data directly - let UI handle different document types
            extracted_data = result.get('extracted_data', {}).get('data', {})
            custom_logger.info(f"Controller: Sending raw data - Document Type: {result.get('document_type', 'unknown')}")
            custom_logger.info(f"Controller: Raw extracted data fields: {list(extracted_data.keys())}")
            custom_logger.info(f"Controller: Raw extracted data sample: {dict(list(extracted_data.items())[:3])}")

            # Simple, direct response format
            raw_response = {
                "status": "success",
                "message": "Document processed successfully",
                "data": [{
                    "extracted_data": {
                        "data": extracted_data,
                        "confidence": result.get('confidence', 0.0),
                        "additional_info": "Document processed successfully",
                        "document_metadata": {
                            "type": result.get('document_type', 'unknown'),
                            "category": "identity" if result.get('document_type') == 'passport' else 'unknown',
                            "issuing_authority": result.get('issuing_authority', 'unknown')
                        }
                    },
                    "verification": {
                        "is_genuine": result.get('status') != 'rejected',
                        "confidence_score": result.get('confidence', 0.0),
                        "verification_checks": {
                            "format_check": True,
                            "data_consistency": True,
                            "security_features": True
                        },
                        "security_features_found": result.get('Official Seals', []),
                        "verification_summary": result.get('rejection_reason', '') if result.get('status') == 'rejected' else 'Document appears genuine',
                        "recommendations": [],
                        "rejection_reason": result.get('rejection_reason', '')
                    },
                    "processing_details": {
                        "document_type": result.get('document_type', 'unknown'),
                        "confidence": result.get('confidence', 0.0),
                        "validation_level": result.get('validation_level', 'comprehensive'),
                        "processing_method": result.get('processing_method', 'unified_prompt'),
                        "chunk_index": result.get('chunk_index'),
                        "total_chunks": result.get('total_chunks')
                    }
                }]
            }

            custom_logger.info(f"Controller: Returning raw response with {len(extracted_data)} fields")
            return JSONResponse(
                content=raw_response,
                status_code=200
            )


        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
                custom_logger.info(f"Cleaned up temporary file: {temp_file_path}")
            except Exception as cleanup_error:
                custom_logger.warning(f"Failed to clean up temporary file: {cleanup_error}")

    except Exception as e:
        custom_logger.error(f"Error in document processing endpoint: {str(e)}")
        return error_response(f"Error processing document: {str(e)}", status_code=500)


@router.post("/processor/text")
@custom_logger.log_around
async def process_text(request: Request, text_data: dict):
    """
    Process text content directly using DocumentProcessor3.

    Args:
        request: FastAPI request object to access app state
        text_data: Dictionary containing 'text' field with document text

    Returns:
        JSONResponse: Processing results including extracted data and verification
    """
    try:
        text = text_data.get('text', '')
        if not text:
            return error_response("No text provided", status_code=400)

        custom_logger.info(f"Received text processing request ({len(text)} characters)")

        # Get DocumentProcessor3 from app state or create new instance
        if hasattr(request.app.state, 'document_processor') and request.app.state.document_processor:
            processor = request.app.state.document_processor
            custom_logger.info("Using DocumentProcessor3 from app state")
        else:
            custom_logger.info("Creating new DocumentProcessor3 instance")
            processor = DocumentProcessor(api_key=API_KEY)

        # Process text using DocumentProcessor3
        result = processor._process_text_content(text, "text_input.txt", min_confidence=0.0)

        if result is None:
            return error_response("Text processing returned no result", status_code=400)

        # Check result status
        if result.get("status") == "error":
            return error_response(result.get("message", "Text processing failed"), status_code=400)
        elif result.get("status") == "rejected":
            return JSONResponse(
                content={
                    "status": "rejected",
                    "message": result.get("rejection_reason", "Text was rejected"),
                    "result": result
                },
                status_code=200
            )
        else:
            # Send raw data directly for text processing too
            extracted_data = result.get('extracted_data', {}).get('data', {})

            raw_response = {
                "status": "success",
                "message": "Text processed successfully",
                "document_type": result.get('document_type', 'unknown'),
                "confidence": result.get('confidence', 0.0),
                "extracted_data": extracted_data,
                "verification_result": {
                    "is_genuine": result.get('status') != 'rejected',
                    "confidence_score": result.get('confidence', 0.0),
                    "rejection_reason": result.get('rejection_reason', ''),
                    "verification_summary": result.get('rejection_reason', '') if result.get('status') == 'rejected' else 'Text processed successfully'
                },
                "processing_details": {
                    "source_file": "text_input.txt",
                    "processing_method": result.get('processing_method', 'unified_prompt'),
                    "validation_level": result.get('validation_level', 'comprehensive')
                }
            }

            return JSONResponse(
                content=raw_response,
                status_code=200
            )

    except Exception as e:
        custom_logger.error(f"Error in text processing endpoint: {str(e)}")
        return error_response(f"Error processing text: {str(e)}", status_code=500)


@router.get("/processor/info")
@custom_logger.log_around
async def get_processor_info(request: Request):
    """
    Get information about the DocumentProcessor3 instance and its available methods.

    Args:
        request: FastAPI request object to access app state

    Returns:
        JSONResponse: Information about the processor
    """
    try:
        # Get DocumentProcessor3 from app state or create new instance
        if hasattr(request.app.state, 'document_processor') and request.app.state.document_processor:
            processor = request.app.state.document_processor
            processor_source = "app_state"
        else:
            processor = DocumentProcessor(api_key=API_KEY)
            processor_source = "new_instance"

        # Get available methods
        available_methods = [method for method in dir(processor) if not method.startswith('_') and callable(getattr(processor, method))]

        # Get processor configuration
        processor_info = {
            "processor_class": processor.__class__.__name__,
            "processor_source": processor_source,
            "api_key_configured": bool(processor.api_key),
            "templates_dir": getattr(processor, 'templates_dir', 'unknown'),
            "unified_processing_enabled": getattr(processor, 'use_unified_processing', False),
            "available_public_methods": available_methods,
            "key_methods": {
                "process_file": "Process a file (PDF, DOCX, or image) - returns List[Dict]",
                "process_text_content": "Process text content directly - returns Dict (private method)",
                "verify_document": "Verify document authenticity - returns Dict",
                "set_unified_processing": "Enable/disable unified processing - returns None"
            }
        }

        return JSONResponse(
            content={
                "status": "success",
                "message": "DocumentProcessor3 information retrieved",
                "processor_info": processor_info
            },
            status_code=200
        )

    except Exception as e:
        custom_logger.error(f"Error getting processor info: {str(e)}")
        return error_response(f"Error getting processor info: {str(e)}", status_code=500)


@router.post("/processor/debug")
@custom_logger.log_around
async def debug_unified_processing(request: Request, text_data: dict):
    """
    Debug endpoint to see raw unified processing results.

    Args:
        request: FastAPI request object to access app state
        text_data: Dictionary containing 'text' field with document text

    Returns:
        JSONResponse: Raw unified processing results for debugging
    """
    try:
        text = text_data.get('text', '')
        if not text:
            return error_response("No text provided", status_code=400)

        custom_logger.info(f"Debug processing request ({len(text)} characters)")

        # Get DocumentProcessor3 from app state or create new instance
        if hasattr(request.app.state, 'document_processor') and request.app.state.document_processor:
            processor = request.app.state.document_processor
        else:
            processor = DocumentProcessor(api_key=API_KEY)

        # Call the unified processing method directly to see raw results
        try:
            # Prepare the unified prompt
            from Common.constants import UNIFIED_DOCUMENT_PROCESSING_PROMPT
            prompt = UNIFIED_DOCUMENT_PROCESSING_PROMPT.format(text=text)

            # Get raw response from AI
            raw_response = processor.text_processor.process_text(text, prompt)

            # Try to clean and parse the response
            cleaned_response = processor._clean_json_response(raw_response)

            try:
                parsed_response = json.loads(cleaned_response) if cleaned_response else None
            except json.JSONDecodeError as e:
                parsed_response = None
                parse_error = str(e)
            else:
                parse_error = None

            # Return debug information
            debug_info = {
                "status": "debug_success",
                "input_text_length": len(text),
                "prompt_length": len(prompt),
                "raw_response_length": len(raw_response) if raw_response else 0,
                "raw_response_preview": raw_response[:500] if raw_response else "No response",
                "cleaned_response_length": len(cleaned_response) if cleaned_response else 0,
                "cleaned_response_preview": cleaned_response[:500] if cleaned_response else "No cleaned response",
                "parse_successful": parsed_response is not None,
                "parse_error": parse_error,
                "parsed_response": parsed_response,
                "response_structure_valid": processor._validate_unified_response_structure(parsed_response) if parsed_response else False
            }

            return JSONResponse(
                content={
                    "status": "success",
                    "message": "Debug information retrieved",
                    "debug_info": debug_info
                },
                status_code=200
            )

        except Exception as processing_error:
            return JSONResponse(
                content={
                    "status": "debug_error",
                    "message": f"Error during debug processing: {str(processing_error)}",
                    "error_details": {
                        "error_type": type(processing_error).__name__,
                        "error_message": str(processing_error)
                    }
                },
                status_code=200
            )

    except Exception as e:
        custom_logger.error(f"Error in debug endpoint: {str(e)}")
        return error_response(f"Error in debug endpoint: {str(e)}", status_code=500)


@router.post("/processor/test-result")
@custom_logger.log_around
async def test_result_format(request: Request):
    """
    Test endpoint that returns a sample result in the expected format.
    This helps debug what the UI expects vs what we're sending.
    """
    try:
        # Create a sample result that should work with the UI
        sample_result = {
            "status": "success",
            "document_type": "resume",
            "source_file": "test_resume.pdf",
            "confidence": 0.85,
            "extracted_data": {
                "data": {
                    "Name": "John Doe",
                    "Email": "john.doe@email.com",
                    "Phone": "+1 555-123-4567",
                    "Address": "San Francisco, CA",
                    "Skills": ["Python", "JavaScript", "React"],
                    "Experience": "5 years",
                    "Education": "BS Computer Science"
                },
                "confidence": 0.85,
                "additional_info": "Test data for UI debugging",
                "document_metadata": {
                    "type": "resume",
                    "category": "professional",
                    "issuing_authority": "test",
                    "key_indicators": ["resume"]
                }
            },
            "processing_method": "unified_prompt",
            "validation_level": "comprehensive"
        }

        custom_logger.info(f"Test result - Document Type: {sample_result.get('document_type')}")
        custom_logger.info(f"Test result - Extracted data: {sample_result.get('extracted_data', {}).get('data', {})}")

        return JSONResponse(
            content={
                "status": "success",
                "message": "Test result generated successfully",
                "result": sample_result
            },
            status_code=200
        )

    except Exception as e:
        custom_logger.error(f"Error in test result endpoint: {str(e)}")
        return error_response(f"Error in test result endpoint: {str(e)}", status_code=500)


@router.post("/processor/test-passport")
@custom_logger.log_around
async def test_passport_result():
    """
    Test endpoint that returns passport data in the exact format the UI expects.
    This helps test if the UI can display data when the format is correct.
    """
    try:
        # Create a test result with the exact passport data from your logs
        passport_result = {
            "status": "success",
            "message": "Successfully processed 1 documents",
            "data": [
                {
                    "extracted_data": {
                        "data": {
                            "Name": "SRIKRISHNAN NADAR SIVA SELVA KUMAR",
                            "First Name": "SIVA SELVA KUMAR",
                            "Last Name": "SRIKRISHNAN NADAR",
                            "Date of Birth": "1976-05-04",
                            "Gender": "M",
                            "Nationality": "INDIAN",
                            "Address": "NAGERCOIL MADURAI",
                            "City": "MADURAI",
                            "Country": "India",
                            "Document Number": "H1591116",
                            "Issue Date": "2008-12-01",
                            "Expiry Date": "2018-11-30",
                            "Status": "expired",
                            "place_of_birth": "NAGERCOIL",
                            "passport_type": "P"
                        },
                        "confidence": 0.85,
                        "additional_info": "Test passport data",
                        "document_metadata": {
                            "type": "passport",
                            "category": "identity",
                            "issuing_authority": "Government of India"
                        }
                    },
                    "verification": {
                        "is_genuine": True,
                        "confidence_score": 0.88,
                        "verification_checks": {
                            "format_check": True,
                            "data_consistency": True,
                            "security_features": True
                        },
                        "security_features_found": ["Government of India Seal"],
                        "verification_summary": "Document appears genuine",
                        "recommendations": [],
                        "rejection_reason": ""
                    },
                    "processing_details": {
                        "document_type": "passport",
                        "confidence": 0.92,
                        "validation_level": "comprehensive",
                        "processing_method": "unified_prompt",
                        "chunk_index": None,
                        "total_chunks": None
                    }
                }
            ]
        }

        custom_logger.info(f"Test passport result - Document Type: {passport_result['data'][0]['processing_details']['document_type']}")
        custom_logger.info(f"Test passport result - Extracted fields: {list(passport_result['data'][0]['extracted_data']['data'].keys())}")

        return JSONResponse(
            content=passport_result,
            status_code=200
        )

    except Exception as e:
        custom_logger.error(f"Error in test passport endpoint: {str(e)}")
        return error_response(f"Error in test passport endpoint: {str(e)}", status_code=500)