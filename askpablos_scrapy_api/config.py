"""
Configuration management module for AskPablos Scrapy API.

This module provides utilities for securely loading and validating
configuration settings from environment variables and settings files.
"""
import os
from typing import Any, Dict, Optional


class Config:
    """Configuration manager for AskPablos Scrapy API."""

    # Default values
    DEFAULT_TIMEOUT = 30
    DEFAULT_RETRIES = 2

    API_URL = "http://10.10.10.178:7500/api/proxy/"

    def __init__(self):
        """Initialize an empty configuration."""
        self._settings = {}

    def load_from_settings(self, settings: Dict[str, Any]) -> None:
        """Load configuration from Scrapy settings."""
        self._settings = {
            'API_KEY': settings.get('API_KEY'),
            'SECRET_KEY': settings.get('SECRET_KEY'),
            'TIMEOUT': settings.get('TIMEOUT', self.DEFAULT_TIMEOUT),
            'RETRIES': settings.get('MAX_RETRIES', self.DEFAULT_RETRIES),
        }

    def load_from_env(self) -> None:
        """Load configuration from environment variables."""
        if 'ASKPABLOS_API_KEY' in os.environ:
            self._settings['API_KEY'] = os.environ['ASKPABLOS_API_KEY']

        if 'ASKPABLOS_SECRET_KEY' in os.environ:
            self._settings['SECRET_KEY'] = os.environ['ASKPABLOS_SECRET_KEY']

        if 'TIMEOUT' in os.environ:
            self._settings['TIMEOUT'] = int(os.environ['TIMEOUT'])

        if 'MAX_RETRIES' in os.environ:
            self._settings['RETRIES'] = int(os.environ['MAX_RETRIES'])

    def validate(self) -> None:
        """Validate that all required configuration is present."""
        if not self._settings.get('API_KEY'):
            raise ValueError("API_KEY must be defined in settings or ASKPABLOS_API_KEY environment variable")
        if not self._settings.get('SECRET_KEY'):
            raise ValueError("SECRET_KEY must be defined in settings or ASKPABLOS_SECRET_KEY environment variable")

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Get a configuration value.

        Args:
            key: The configuration key to retrieve
            default: Default value if the key is not found

        Returns:
            The configuration value or the default
        """
        return self._settings.get(key, default)
