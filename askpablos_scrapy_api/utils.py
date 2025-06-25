"""
Utility functions for the AskPablos Scrapy API middleware.
"""
import logging
from typing import Any, Optional
import json


def setup_logging(level: int = logging.DEBUG) -> None:
    """
    Set up logging for the AskPablos Scrapy API middleware.

    Args:
        level: The logging level to use (defaults to DEBUG)
    """
    logger = logging.getLogger('askpablos_scrapy_api')
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False


def parse_response_body(body: Any) -> Optional[str]:
    """
    Parse and validate response body.

    Args:
        body: The response body

    Returns:
        The parsed body as a string or None if invalid
    """
    if isinstance(body, dict):
        # Handle case where the API returns a JSON object instead of a string
        try:
            return json.dumps(body)
        except (TypeError, ValueError):
            return None
    elif isinstance(body, str):
        return body
    elif isinstance(body, bytes):
        try:
            return body.decode()
        except UnicodeDecodeError:
            return None
    else:
        return None
