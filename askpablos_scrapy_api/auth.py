"""
Authentication utilities for AskPablos Scrapy API.

This module provides functions for securely signing API requests
and verifying authentication credentials.
"""
import base64
import hashlib
import hmac
import json
from typing import Dict, Any, Tuple


def sign_request(payload: Dict[str, Any], secret_key: str) -> Tuple[str, str]:
    """
    Sign a request payload with HMAC-SHA256 using the provided secret key.

    Args:
        payload: The request payload to sign
        secret_key: The secret key used for signing

    Returns:
        Tuple containing the (JSON payload string, base64-encoded signature)
    """
    # Ensure consistent serialization by specifying separators
    request_json = json.dumps(payload, separators=(',', ':'))

    # Create HMAC-SHA256 signature
    signature = hmac.new(
        secret_key.encode(),
        request_json.encode(),
        hashlib.sha256
    ).digest()

    # Convert signature to base64
    signature_b64 = base64.b64encode(signature).decode()

    return request_json, signature_b64


def create_auth_headers(api_key: str, signature: str) -> Dict[str, str]:
    """
    Create authentication headers for AskPablos API requests.

    Args:
        api_key: The API key
        signature: The base64-encoded signature

    Returns:
        Dictionary of HTTP headers
    """
    return {
        "Content-Type": "application/json",
        "X-API-Key": api_key,
        "X-Signature": signature
    }
