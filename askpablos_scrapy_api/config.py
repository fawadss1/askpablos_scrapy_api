"""
Configuration management module for AskPablos Scrapy API.

This module provides utilities for securely loading and validating
configuration settings from environment variables and settings files.
"""
from typing import Any, Dict, Optional
from urllib.parse import urljoin


class Config:
    """Configuration manager for AskPablos Scrapy API."""

    # Default values
    DEFAULT_TIMEOUT = 30
    DEFAULT_RETRIES = 2

    def __init__(self):
        """Initialize an empty configuration."""
        self._settings = {}
        self.API_URL = None

    def load_from_settings(self, settings: Dict[str, Any]) -> None:
        """Load configuration from Scrapy settings."""
        self._settings = {
            'API_KEY': settings.get('API_KEY'),
            'SECRET_KEY': settings.get('SECRET_KEY'),
            'TIMEOUT': settings.get('TIMEOUT', self.DEFAULT_TIMEOUT),
            'RETRIES': settings.get('MAX_RETRIES', self.DEFAULT_RETRIES),
        }

        base_url: str = settings.get('APCLOUDY_URL', 'http://10.10.10.24')
        self.API_URL = urljoin(base_url, '/api/proxy/')

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
