@router.post("/processor")
@custom_logger.log_around
async def process_document(file: UploadFile = File(...)):
    custom_logger.info(f"Received file upload request for file: {file.filename}")
    
    try:
        # Validate file extension
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
            
        if not file.filename.lower().endswith((".pdf", ".docx", ".jpg", ".jpeg", ".png")):
            raise HTTPException(
                status_code=400, 
                detail="Invalid file format. Only PDF, DOCX, JPG, and PNG are allowed."
            )

        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            custom_logger.info(f"Created temporary file: {temp_file.name}")
            
            # Read and write file content
            content = await file.read()
            if not content:
                raise HTTPException(status_code=400, detail="Empty file provided")
                
            temp_file.write(content)
            temp_file_path = temp_file.name

        try:
            # Process the document
            processor = DocumentProcessor(api_key=API_KEY)
            results = processor.process_file(temp_file_path)

            if not results:
                return JSONResponse(
                    status_code=400,
                    content={
                        "status": "error",
                        "message": "No valid documents found",
                        "data": None
                    }
                )

            # Process the first result (assuming single document processing)
            result = results[0]
            
            # Handle error or rejected status
            if result.get("status") == "error" or result.get("status") == "rejected":
                return JSONResponse(
                    status_code=400,
                    content={
                        "status": "error",
                        "message": result.get("rejection_reason", "Document processing failed"),
                        "data": {
                            "document_type": result.get("document_type", "unknown"),
                            "verification_result": result.get("verification_result", {})
                        }
                    }
                )

            # Extract verification status
            verification_result = result.get("verification_result", {})
            verification_status = {
                "is_verified": verification_result.get("is_genuine", False),
                "confidence_score": verification_result.get("confidence_score", 0.0),
                "document_type": result.get("document_type", "unknown"),
                "verification_details": {
                    "authenticity": verification_result.get("verification_checks", {}).get("authenticity", {}),
                    "security_features": verification_result.get("verification_checks", {}).get("security_features", {}),
                    "data_validation": verification_result.get("verification_checks", {}).get("data_validation", {}),
                    "quality": verification_result.get("verification_checks", {}).get("quality", {})
                },
                "security_features_found": verification_result.get("security_features_found", []),
                "verification_summary": verification_result.get("verification_summary", ""),
                "recommendations": verification_result.get("recommendations", [])
            }

            # Get the extracted data
            extracted_data = result.get("extracted_data", {})
            if isinstance(extracted_data, dict) and "data" in extracted_data:
                extracted_data = extracted_data["data"]

            # Prepare the response data
            response_data = {
                "extracted_data": {
                    "document_type": result.get("document_type", "unknown"),
                    "processing_method": result.get("processing_method", "ocr"),
                    "data": extracted_data,
                    "verification_details": verification_result.get("verification_checks", {})
                },
                "verification": verification_status,
                "document_metadata": result.get("document_metadata", {}),
                "processing_details": {
                    "document_type": result.get("document_type"),
                    "confidence": result.get("confidence"),
                    "validation_level": result.get("validation_level"),
                    "processing_method": result.get("processing_method")
                }
            }

            # If document is not verified, return a warning status
            if not verification_status["is_verified"]:
                return JSONResponse(
                    status_code=200,
                    content={
                        "status": "warning",
                        "message": verification_result.get("rejection_reason", "Document verification failed"),
                        "data": response_data
                    }
                )

            custom_logger.info(f"Successfully processed document: {file.filename}")
            custom_logger.info(f"Document type: {result['document_type']} with confidence {verification_status['confidence_score']}")

            return JSONResponse(
                content={
                    "status": "success",
                    "message": "Document processed successfully",
                    "data": response_data
                },
                status_code=200
            )

        except ValueError as ve:
            custom_logger.warning(f"Document processing failed: {str(ve)}")
            return error_response(str(ve), status_code=400)

        except Exception as e:
            custom_logger.error(f"Error processing document: {str(e)}")
            return error_response("Internal server error during document processing")

        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                custom_logger.info(f"Cleaned up temporary file: {temp_file_path}")

    except HTTPException as he:
        custom_logger.error(f"HTTP error: {str(he)}")
        raise he
        
    except Exception as e:
        custom_logger.error(f"Error handling file upload: {str(e)}")
        return error_response("Error handling file upload") 