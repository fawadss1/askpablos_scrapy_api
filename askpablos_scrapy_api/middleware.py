import logging
import requests
from scrapy.http import HtmlResponse, Request
from scrapy import Spider
from typing import Optional

from .auth import sign_request, create_auth_headers
from .config import Config
from .endpoints import API_URL
from .version import __version__
from .exceptions import (
    AskPablosAPIError, InvalidResponseError, ProxyError,
    TimeoutError, BrowserRenderingError,
    ConfigurationError, handle_api_error
)
from .utils import setup_logging

# Configure logger
logger = logging.getLogger('askpablos_scrapy_api')


class AskPablosAPIDownloaderMiddleware:
    """
    Scrapy middleware to route selected requests through AskPablos proxy API.

    This middleware activates **only** for requests that include:
        meta = {
            "askpablos_api_map": {
                "browser": True,          # Optional: Use headless browser
                "rotate_proxy": True      # Optional: Use rotating proxy IP
            }
        }

    It will bypass any request that does not include the `askpablos_api_map` key or has it as an empty dict.

    Configuration (via settings.py or `custom_settings` in your spider):
        API_KEY      = "<your API key>"
        SECRET_KEY   = "<your secret key>"

    Optional settings:
        ASKPABLOS_TIMEOUT = 30  # Request timeout in seconds
        ASKPABLOS_MAX_RETRIES = 2  # Maximum number of retries for failed requests
        ASKPABLOS_RETRY_DELAY = 1.0  # Initial delay between retries in seconds

    Example configuration in a spider:
        custom_settings = {
            "DOWNLOADER_MIDDLEWARES": {
                "askpablos_scrapy_api.middleware.AskPablosAPIDownloaderMiddleware": 543,
            },
            "API_KEY": "your-api-key-here",
            "SECRET_KEY": "your-secret-key-here",
            "ASKPABLOS_TIMEOUT": 30,
            "ASKPABLOS_MAX_RETRIES": 2,
            "ASKPABLOS_RETRY_DELAY": 1.0
        }
    """

    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key
        setup_logging()
        logger.debug(f"AskPablos Scrapy API initialized (version: {__version__})")

    @classmethod
    def from_crawler(cls, crawler):
        """Create middleware instance from Scrapy crawler.

        Loads configuration from:
        1. Spider's custom_settings (if available)
        2. Project settings.py
        3. Environment variables
        """
        # Load configuration
        config = Config()
        config.load_from_settings(crawler.settings)
        config.load_from_env()

        try:
            config.validate()
        except ValueError as e:
            error_msg = f"Configuration error: {e}"
            logger.error(error_msg)
            raise ConfigurationError(error_msg)

        return cls(
            api_key=config.get('API_KEY'),
            secret_key=config.get('SECRET_KEY')
        )

    def process_request(self, request: Request, spider: Spider) -> Optional[HtmlResponse]:
        """Process a Scrapy request."""
        proxy_cfg = request.meta.get("askpablos_api_map")

        if not proxy_cfg or not isinstance(proxy_cfg, dict) or not proxy_cfg:
            return None  # Skip proxying

        browser = proxy_cfg.get("browser", False)
        rotate_proxy = proxy_cfg.get("rotate_proxy", False)

        payload = {
            "url": request.url,
            "method": request.method if hasattr(request, "method") else "GET",
            "browser": browser,
            "rotateProxy": rotate_proxy
        }

        try:
            # Sign the request using auth module
            request_json, signature_b64 = sign_request(payload, self.secret_key)
            headers = create_auth_headers(self.api_key, signature_b64)

            # Log sanitized payload for debugging
            logger.debug(f"Sending request to AskPablos API for {request.url}")

            # Make API request using the URL from constants
            response = requests.post(API_URL, data=request_json, headers=headers, timeout=30)

            # Handle HTTP error status codes
            if response.status_code != 200:
                try:
                    response_data = response.json()
                except ValueError:
                    response_data = None

                # Use factory function to create appropriate exception
                error = handle_api_error(response.status_code, response_data)
                raise error

            # Parse response
            try:
                proxy_response = response.json()
            except ValueError:
                raise InvalidResponseError("Invalid JSON response from API")

            # Validate response content
            html_body = proxy_response.get("data")
            if not html_body:
                raise ProxyError(f"No 'body' in response for {request.url}")

            # Handle browser rendering errors
            if browser and proxy_response.get("error"):
                error_msg = proxy_response.get("error", "Unknown browser rendering error")
                raise BrowserRenderingError(error_msg, response=proxy_response)

            return HtmlResponse(
                url=request.url,
                body=html_body.encode() if isinstance(html_body, str) else html_body,
                encoding="utf-8",
                request=request,
                status=response.status_code
            )

        except requests.exceptions.Timeout:
            logger.error(f"Request timeout for {request.url}")
            raise TimeoutError(f"Request to {request.url} timed out after 30 seconds")

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            raise AskPablosAPIError(f"Request failed: {str(e)}")

        except AskPablosAPIError as e:
            # Log the error - this captures all our custom exceptions
            logger.error(f"[AskPablos API] {str(e)}")
            spider.crawler.stats.inc_value(f"askpablos/errors/{e.__class__.__name__}")
            raise  # Re-raise the exception for downstream handling

        except Exception as e:
            # Catch-all for unexpected errors
            logger.error(f"[AskPablos API] Unexpected error processing {request.url}: {str(e)}")
            spider.crawler.stats.inc_value("askpablos/errors/unexpected")
            raise AskPablosAPIError(f"Unexpected error: {str(e)}")
