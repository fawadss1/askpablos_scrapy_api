"""
Operations handler for AskPablos Scrapy API.

This module defines and validates configuration that can be used
with the AskPablos API service.
"""
from typing import Dict, Any
import logging

from .utils import (
    validate_browser,
    validate_rotate_proxy,
    validate_wait_for_load,
    validate_js_strategy,
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
        validate_rotate_proxy(config, validated_config)
        validate_wait_for_load(config, validated_config, browser_enabled)
        validate_js_strategy(config, validated_config, browser_enabled)
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
        "rotateProxy": config.get("rotate_proxy", False),
    }

    # Add optional fields if present
    optional_fields = [
        'wait_for_load', 'js_strategy', 'screenshot', 'operations'
    ]

    for field in optional_fields:
        if field in config:
            # Convert snake_case to camelCase for API
            api_field = field
            if field == 'wait_for_load':
                api_field = 'waitForLoad'
            elif field == 'js_strategy':
                api_field = 'jsStrategy'
            elif field == 'screenshot':
                api_field = 'screenshot'
            elif field == 'operations':
                api_field = 'operations'

            payload[api_field] = config[field]

    return payload
