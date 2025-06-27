"""
Utility functions for the AskPablos Scrapy API middleware.
"""
import json
import logging
import requests
from typing import Dict, Any

# Configure logger
logger = logging.getLogger('askpablos_scrapy_api')


def extract_response_data(response: requests.Response) -> Dict[str, Any]:
    """
    Safely extract JSON data from response or return empty dict.

    Args:
        response: The requests Response object to extract JSON from

    Returns:
        Dict containing the JSON data or an empty dict if parsing fails
    """
    try:
        return response.json()
    except (ValueError, json.JSONDecodeError):
        logger.warning(f"Failed to parse JSON response with status {response.status_code}")
        return {}
