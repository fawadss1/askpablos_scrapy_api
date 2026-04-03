"""
Exception handling for AskPablos Scrapy API.

This module provides custom exceptions and error handling
utilities for the AskPablos Scrapy API middleware.
"""
from typing import Optional, Dict, Any


class AskPablosAPIError(Exception):
    """Base exception class for AskPablos API errors."""

    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.response = response

        if response and isinstance(response, dict):
            self.message = response.get('error', "An error occurred with the AskPablos API").strip()

        super().__init__(self.message)

    def __str__(self) -> str:
        """String representation of the error."""
        if self.status_code:
            return f"[{self.status_code}]: {self.message}"
        elif self.status_code:
            return f"[{self.status_code}] {self.message}"
        else:
            return self.message


class AuthenticationError(AskPablosAPIError):
    """
    Raised when API key or secret key authentication fails.
    This is a critical error that should stop the spider.
    """

    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code, response)
        self.is_critical = True  # Flag to indicate this should stop the spider


class RateLimitError(AskPablosAPIError):
    """
    Raised when the API rate limit is exceeded.
    This is a critical error that should stop the spider.
    """

    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code, response)
        self.is_critical = True

        # Extract rate limit information if available
        self.reset_time = None
        self.limit = None
        self.remaining = None

        if response and isinstance(response, dict):
            rate_info = response.get('rateLimit', {})
            self.reset_time = rate_info.get('resetAt')
            self.limit = rate_info.get('limit')
            self.remaining = rate_info.get('remaining', 0)

    def __str__(self) -> str:
        """String representation with rate limit details if available."""
        base_str = super().__str__()
        if self.reset_time:
            return f"{base_str} (Limit: {self.limit}, Remaining: {self.remaining}, Reset at: {self.reset_time})"
        return base_str


def handle_api_error(status_code: int, response_data: Optional[Dict[str, Any]] = None) -> AskPablosAPIError:
    """
    Factory function to create and return the appropriate exception based on status code.

    Args:
        status_code: HTTP status code
        response_data: API response data if available

    Returns:
        An appropriate Exception instance.
    """
    message = "An error occurred with the AskPablos API"

    if response_data and isinstance(response_data, dict):
        message = response_data.get('error', message).strip()

    if status_code == 401 or status_code == 403:
        return AuthenticationError(f"Authentication failed: {message}", status_code, response_data)
    elif status_code == 429:
        return RateLimitError(message, status_code, response_data)
    else:
        return AskPablosAPIError(message, status_code, response_data)
