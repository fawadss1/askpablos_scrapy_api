"""
AskPablos Scrapy API - A professional Scrapy integration for seamless proxy-based web scraping

This package provides a Scrapy middleware for routing requests through AskPablos proxy API,
offering headless browser rendering and rotating proxies for improved scraping capabilities.

Usage:
    from askpablos_scrapy_api import AskPablosAPIDownloaderMiddleware

    # In your Scrapy settings:
    DOWNLOADER_MIDDLEWARES = {
        'askpablos_scrapy_api.middleware.AskPablosAPIDownloaderMiddleware': 543,
    }

    # Or import directly:
    from askpablos_scrapy_api import AskPablosAPIDownloaderMiddleware
"""

from .middleware import AskPablosAPIDownloaderMiddleware
from .exceptions import (
    AskPablosAPIError,
    RateLimitError,
    BrowserRenderingError,
    handle_api_error,
)

__version__ = "0.4.3"

# Define package exports explicitly
__all__ = [
    'AskPablosAPIDownloaderMiddleware',
    '__version__',
    'AskPablosAPIError',
    'RateLimitError',
    'BrowserRenderingError',
    'handle_api_error'
]
