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
        self.error_code = None

        # Extract error code from response if present
        if response and isinstance(response, dict):
            self.error_code = response.get('error', {}).get('code')

            # If the API provides a more detailed error message, use it
            if response.get('error', {}).get('message'):
                self.message = response['error']['message']

        super().__init__(self.message)

    def __str__(self) -> str:
        """String representation of the error."""
        if self.status_code and self.error_code:
            return f"[{self.status_code}] {self.error_code}: {self.message}"
        elif self.status_code:
            return f"[{self.status_code}] {self.message}"
        else:
            return self.message


class AuthenticationError(AskPablosAPIError):
    """
    Raised when authentication with the AskPablos API fails.

    This typically happens when:
    - The API key is invalid or expired
    - The signature is incorrect or malformed
    - The credentials have been revoked
    """
    pass


class RateLimitError(AskPablosAPIError):
    """
    Raised when the API rate limit is exceeded.

    This typically happens when:
    - Too many requests are made in a short period
    - The account's quota has been reached
    - The API usage exceeds the current plan limits
    """

    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code, response)

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


class ProxyError(AskPablosAPIError):
    """
    Raised when there is an error with the proxy service.

    This typically happens when:
    - The target URL is invalid or unreachable
    - The proxy server encountered an error
    - The requested proxy location is unavailable
    """
    pass


class InvalidResponseError(AskPablosAPIError):
    """
    Raised when the API returns an invalid or malformed response.

    This typically happens when:
    - The API response is not valid JSON
    - The response structure doesn't match expectations
    - There are missing required fields in the response
    """
    pass


class TimeoutError(AskPablosAPIError):
    """
    Raised when a request times out.

    This typically happens when:
    - The target site takes too long to respond
    - The proxy server is overloaded
    - The network connection is slow or unstable
    """
    pass


class BrowserRenderingError(AskPablosAPIError):
    """
    Raised when there's an error with headless browser rendering.

    This typically happens when:
    - The page JavaScript execution fails
    - The page has anti-bot measures that block the browser
    - The page structure is incompatible with headless rendering
    """
    pass


class ConfigurationError(AskPablosAPIError):
    """
    Raised when there's an error in the middleware configuration.

    This typically happens when:
    - Required API keys are missing or invalid
    - Configuration settings are incompatible
    - Environment variables are improperly set
    """
    pass


def handle_api_error(status_code: int, response_data: Optional[Dict[str, Any]] = None) -> AskPablosAPIError:
    """
    Factory function to create the appropriate exception based on status code.

    Args:
        status_code: HTTP status code
        response_data: API response data if available

    Returns:
        An appropriate AskPablosAPIError subclass instance
    """
    message = "An error occurred with the AskPablos API"

    if response_data and isinstance(response_data, dict):
        error_msg = response_data.get('error', {}).get('message')
        if error_msg:
            message = error_msg

    # Map status codes to exception types
    if status_code == 401:
        return AuthenticationError(message, status_code, response_data)
    elif status_code == 429:
        return RateLimitError(message, status_code, response_data)
    elif status_code == 408:
        return TimeoutError(message, status_code, response_data)
    elif 400 <= status_code < 500:
        # Client errors
        return AskPablosAPIError(message, status_code, response_data)
    elif 500 <= status_code < 600:
        # Server errors
        return ProxyError(message, status_code, response_data)
    else:
        # Unknown status code
        return AskPablosAPIError(message, status_code, response_data)
