"""
Operations handler for AskPablos Scrapy API.

This module defines and validates configuration that can be used
with the AskPablos API service.
"""
from typing import Dict, Any
import logging

from .utils import (
    validate_browser,
    validate_screenshot,
    validate_operations
)

logger = logging.getLogger('askpablos_scrapy_api')


class AskPablosAPIMapValidator:
    """Validates the askpablos_api_map configuration."""

    @classmethod
    def validate_config(cls, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize askpablos_api_map configuration.

        Args:
            config: Configuration dictionary

        Returns:
            Validated and normalized configuration

        Raises:
            ValueError: If configuration is invalid
        """
        if not isinstance(config, dict):
            raise ValueError("askpablos_api_map must be a dictionary")

        validated_config = {}

        # Validate browser option first (required by other options)
        browser_enabled = validate_browser(config, validated_config)

        # Validate all other options
        validate_screenshot(config, validated_config, browser_enabled)
        validate_operations(config, validated_config, browser_enabled)

        return validated_config


def create_api_payload(request_url: str, request_method: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create API payload from validated configuration.

    Args:
        request_url: The URL to request
        request_method: HTTP method
        config: Validated configuration

    Returns:
        API payload dictionary
    """
    payload = {
        "url": request_url,
        "method": request_method,
        "browser": config.get("browser", False),
    }

    # Add optional fields if present
    optional_fields = [
        'screenshot', 'operations'
    ]

    for field in optional_fields:
        if field in config:
            payload[field] = config[field]

    return payload
