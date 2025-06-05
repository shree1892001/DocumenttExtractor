import json
import logging
from typing import Dict, Any
from Services.Processors.text_processor import TextProcessor
from Common.document_constants import (
    DOCUMENT_PROMPTS,
    MIN_GENUINENESS_SCORE,
    VERIFICATION_THRESHOLD,
    NON_GENUINE_INDICATORS
)

logger = logging.getLogger(__name__)

class DocumentVerifier:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.text_processor = TextProcessor(api_key)
        self.MIN_GENUINENESS_SCORE = MIN_GENUINENESS_SCORE
        self.VERIFICATION_THRESHOLD = VERIFICATION_THRESHOLD

    def verify_document(self, extracted_data: Dict[str, Any], doc_type: str) -> Dict[str, Any]:
        """Verify document authenticity and data validity"""
        try:
            verification_prompt = DOCUMENT_PROMPTS["verification"].format(
                doc_type=doc_type,
                data=json.dumps(extracted_data, indent=2)
            )

            response = self.text_processor.process_text(json.dumps(extracted_data), verification_prompt)
            verification_result = json.loads(response.strip().replace("```json", "").replace("```", "").strip())

            checks = verification_result.get("verification_checks", {})
            confidence_scores = [
                checks.get("authenticity", {}).get("confidence", 0),
                checks.get("security_features", {}).get("confidence", 0),
                checks.get("data_validation", {}).get("confidence", 0),
                checks.get("quality", {}).get("confidence", 0)
            ]
            overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0

            verification_result["confidence_score"] = overall_confidence
            verification_result["is_genuine"] = overall_confidence >= self.VERIFICATION_THRESHOLD

            logger.info(f"Document verification results: {json.dumps(verification_result, indent=2)}")

            return verification_result

        except Exception as e:
            logger.exception(f"Error verifying document genuineness: {str(e)}")
            return {
                "is_genuine": False,
                "confidence_score": 0.0,
                "rejection_reason": f"Error during verification: {str(e)}",
                "verification_checks": {
                    "authenticity": {"passed": False, "details": f"Error during verification: {str(e)}", "confidence": 0.0},
                    "security_features": {"passed": False, "details": "Verification failed", "confidence": 0.0},
                    "data_validation": {"passed": False, "details": "Verification failed", "confidence": 0.0},
                    "quality": {"passed": False, "details": "Verification failed", "confidence": 0.0}
                },
                "security_features_found": [],
                "verification_summary": f"Document verification failed due to error: {str(e)}",
                "recommendations": ["Verification process failed due to technical error"]
            }

    def verify_document_genuineness(self, text: str) -> Dict[str, Any]:
        """Verify if the document is genuine before extraction"""
        verification_result = {
            "is_genuine": False,
            "confidence_score": 0.0,
            "rejection_reason": "",
            "verification_checks": [],
            "security_features_found": []
        }

        try:
            verification_prompt = DOCUMENT_PROMPTS["genuineness_check"].format(text=text)

            response = self.text_processor.process_text(text, verification_prompt)
            verification_data = json.loads(response.strip().replace("```json", "").replace("```", "").strip())

            verification_result["is_genuine"] = verification_data.get("is_genuine", False)
            verification_result["confidence_score"] = verification_data.get("confidence_score", 0.0)
            verification_result["rejection_reason"] = verification_data.get("rejection_reason", "")
            verification_result["verification_checks"] = verification_data.get("verification_checks", [])
            verification_result["security_features_found"] = verification_data.get("security_features_found", [])

            if any(indicator in text.lower() for indicator in NON_GENUINE_INDICATORS):
                verification_result["is_genuine"] = False
                verification_result["rejection_reason"] = "Document contains indicators of being non-genuine"

            if verification_result["confidence_score"] < self.MIN_GENUINENESS_SCORE:
                verification_result["is_genuine"] = False
                verification_result["rejection_reason"] = f"Low genuineness confidence: {verification_result['confidence_score']}"

            if not verification_result["security_features_found"]:
                verification_result["is_genuine"] = False
                verification_result["rejection_reason"] = "No security features found"

            return verification_result

        except Exception as e:
            logger.error(f"Error in document genuineness verification: {str(e)}")
            verification_result["rejection_reason"] = f"Verification error: {str(e)}"
            return verification_result 