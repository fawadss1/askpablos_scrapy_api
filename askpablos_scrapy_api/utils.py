"""
Utility functions for validating AskPablos API configuration.

This module contains separate validation methods for each configuration option.
"""
from typing import Dict, Any
import logging

logger = logging.getLogger('askpablos_scrapy_api')


def validate_browser(config: Dict[str, Any], validated_config: Dict[str, Any]) -> bool:
    """
    Validate browser configuration.

    Args:
        config: Raw configuration dictionary
        validated_config: Dictionary to store validated config

    Returns:
        bool: True if browser is enabled, False otherwise

    Raises:
        ValueError: If browser value is invalid
    """
    browser_enabled = False
    if 'browser' in config:
        browser = config['browser']
        if not isinstance(browser, bool):
            raise ValueError("'browser' must be a boolean")
        validated_config['browser'] = browser
        browser_enabled = browser
    return browser_enabled


def validate_screenshot(config: Dict[str, Any], validated_config: Dict[str, Any], browser_enabled: bool) -> None:
    """
    Validate screenshot configuration.

    Args:
        config: Raw configuration dictionary
        validated_config: Dictionary to store validated config
        browser_enabled: Whether browser mode is enabled

    Raises:
        ValueError: If screenshot value is invalid
    """
    if 'screenshot' in config:
        screenshot = config['screenshot']
        if not isinstance(screenshot, bool):
            raise ValueError("'screenshot' must be a boolean")
        validated_config['screenshot'] = screenshot

        if screenshot and not browser_enabled:
            logger.error(
                "CONFIGURATION ERROR: 'screenshot': True requires 'browser': True to function properly. "
                "This attribute will be ignored without browser mode enabled."
            )


def validate_geo_location(config: Dict[str, Any], validated_config: Dict[str, Any]) -> None:
    """
    Validate geoLocation configuration.

    Args:
        config: Raw configuration dictionary
        validated_config: Dictionary to store validated config

    Raises:
        ValueError: If geoLocation value is invalid
    """
    if 'geoLocation' in config:
        geo = config['geoLocation']
        if not isinstance(geo, str):
            raise ValueError("'geoLocation' must be a string")
        geo = geo.strip().lower()
        if len(geo) != 2 or not geo.isalpha():
            raise ValueError(
                f"'geoLocation' must be a 2-letter ISO country code (e.g. 'US', 'PK', 'GB'), got '{config['geoLocation']}'"
            )
        validated_config['geoLocation'] = geo


def validate_proxy_type(config: Dict[str, Any], validated_config: Dict[str, Any]) -> None:
    """
    Validate proxyType configuration.

    Args:
        config: Raw configuration dictionary
        validated_config: Dictionary to store validated config

    Raises:
        ValueError: If proxyType value is invalid
    """
    if 'proxyType' in config:
        proxy_type = config['proxyType']
        valid_proxy_types = ['datacenter', 'residential', 'mobile']
        if not isinstance(proxy_type, str):
            raise ValueError("'proxyType' must be a string")
        if proxy_type not in valid_proxy_types:
            raise ValueError(
                f"'proxyType' must be one of {valid_proxy_types}, got '{proxy_type}'"
            )
        validated_config['proxyType'] = proxy_type


def validate_operations(config: Dict[str, Any], validated_config: Dict[str, Any], browser_enabled: bool) -> None:
    """
    Validate operations configuration.

    Args:
        config: Raw configuration dictionary
        validated_config: Dictionary to store validated config
        browser_enabled: Whether browser mode is enabled

    Raises:
        ValueError: If operations structure is invalid
    """
    if 'operations' in config:
        operations = config['operations']
        if not isinstance(operations, list):
            raise ValueError("'operations' must be a list")

        # Valid values for operation fields
        valid_tasks = ['waitForElement']
        valid_match_on = ['xpath', 'css']
        valid_match_rules = ['visible', 'attached', 'hidden', 'detached']
        valid_on_failure = ['continue', 'return', 'throw']

        # Validate each operation in the list
        for idx, operation in enumerate(operations):
            if not isinstance(operation, dict):
                raise ValueError(f"Operation at index {idx} must be a dictionary")

            # Required field: task
            if 'task' not in operation:
                raise ValueError(f"Operation at index {idx} missing required field 'task'")

            task = operation['task']
            if task not in valid_tasks:
                raise ValueError(
                    f"Operation at index {idx}: 'task' must be one of {valid_tasks}, got '{task}'"
                )

            # Required field: match
            if 'match' not in operation:
                raise ValueError(f"Operation at index {idx} missing required field 'match'")

            # Validate match structure
            match = operation['match']
            if not isinstance(match, dict):
                raise ValueError(f"Operation at index {idx}: 'match' must be a dictionary")

            # Validate match.on
            if 'on' not in match:
                raise ValueError(f"Operation at index {idx}: 'match' missing required field 'on'")
            if match['on'] not in valid_match_on:
                raise ValueError(
                    f"Operation at index {idx}: 'match.on' must be one of {valid_match_on}, got '{match['on']}'"
                )

            # Validate match.rule
            if 'rule' not in match:
                raise ValueError(f"Operation at index {idx}: 'match' missing required field 'rule'")
            if match['rule'] not in valid_match_rules:
                raise ValueError(
                    f"Operation at index {idx}: 'match.rule' must be one of {valid_match_rules}, got '{match['rule']}'"
                )

            # Validate match.value
            if 'value' not in match:
                raise ValueError(f"Operation at index {idx}: 'match' missing required field 'value'")
            if not isinstance(match['value'], str):
                raise ValueError(f"Operation at index {idx}: 'match.value' must be a string")

            selector_value = match['value'].strip()
            selector_type = match['on']

            if selector_type == 'xpath':
                if selector_value.startswith('#') or selector_value.startswith('.'):
                    raise ValueError(
                        f"Operation at index {idx}: 'match.value' appears to be a CSS selector "
                        f"but 'match.on' is set to 'xpath'. Please use 'on': 'css' or provide a valid XPath expression."
                    )
                if ' > ' in selector_value or ' + ' in selector_value or ' ~ ' in selector_value:
                    logger.warning(
                        f"Operation at index {idx}: 'match.value' contains CSS combinator symbols but 'match.on' is 'xpath'. "
                        f"If this is a CSS selector, please change 'on' to 'css'."
                    )
                if not (selector_value.startswith('/') or selector_value.startswith('(') or
                        any(xpath_func in selector_value for xpath_func in ['contains(', 'text()', 'following::', 'ancestor::'])):
                    logger.warning(
                        f"Operation at index {idx}: 'match.value' does not appear to be a valid XPath expression. "
                        f"XPath typically starts with '/' or '//' or contains XPath functions."
                    )

            elif selector_type == 'css':
                if selector_value.startswith('/'):
                    raise ValueError(
                        f"Operation at index {idx}: 'match.value' appears to be an XPath selector "
                        f"but 'match.on' is set to 'css'. Please use 'on': 'xpath' or provide a valid CSS selector."
                    )
                if any(xpath_pattern in selector_value for xpath_pattern in ['[@', 'text()', 'following::', 'ancestor::', 'parent::']):
                    raise ValueError(
                        f"Operation at index {idx}: 'match.value' contains XPath syntax but 'match.on' is set to 'css'. "
                        f"Please use 'on': 'xpath' or provide a valid CSS selector."
                    )

            if 'maxWait' in operation:
                if not isinstance(operation['maxWait'], (int, float)):
                    raise ValueError(f"Operation at index {idx}: 'maxWait' must be a number")
                if operation['maxWait'] <= 0:
                    raise ValueError(f"Operation at index {idx}: 'maxWait' must be greater than 0")

            # Validate optional field: onFailure
            if 'onFailure' in operation:
                if not isinstance(operation['onFailure'], str):
                    raise ValueError(f"Operation at index {idx}: 'onFailure' must be a string")
                if operation['onFailure'] not in valid_on_failure:
                    raise ValueError(
                        f"Operation at index {idx}: 'onFailure' must be one of {valid_on_failure}, got '{operation['onFailure']}'"
                    )

        validated_config['operations'] = operations

        if not browser_enabled:
            logger.error(
                "CONFIGURATION ERROR: 'operations' requires 'browser': True to function properly. "
                "This attribute will be ignored without browser mode enabled."
            )
