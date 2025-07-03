"""
Operations handler for AskPablos Scrapy API.

This module defines and validates configuration that can be used
with the AskPablos API service.
"""
from typing import Dict, List, Any, Optional, Union
import logging

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

        # Browser option
        if 'browser' in config:
            browser = config['browser']
            if not isinstance(browser, bool):
                raise ValueError("'browser' must be a boolean")
            validated_config['browser'] = browser

        # Rotate proxy option
        if 'rotate_proxy' in config:
            rotate_proxy = config['rotate_proxy']
            if not isinstance(rotate_proxy, bool):
                raise ValueError("'rotate_proxy' must be a boolean")
            validated_config['rotate_proxy'] = rotate_proxy

        # Wait for page load
        if 'wait_for_load' in config:
            wait_for_load = config['wait_for_load']
            if not isinstance(wait_for_load, bool):
                raise ValueError("'wait_for_load' must be a boolean")
            validated_config['wait_for_load'] = wait_for_load

        # JavaScript strategy
        if 'js_strategy' in config:
            js_strategy = config['js_strategy']
            valid_strategies = [True, False, "DEFAULT"]
            if js_strategy not in valid_strategies:
                raise ValueError(f"'js_strategy' must be one of {valid_strategies}")
            validated_config['js_strategy'] = js_strategy

        # Screenshot options
        if 'screenshot' in config:
            screenshot = config['screenshot']
            if not isinstance(screenshot, bool):
                raise ValueError("'screenshot' must be a boolean")
            validated_config['screenshot'] = screenshot

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
        'wait_for_load', 'js_strategy', 'screenshot'
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

            payload[api_field] = config[field]

    return payload
