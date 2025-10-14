import logging
from base64 import b64decode
from typing import Optional
import asyncio

import aiohttp
from scrapy.http import HtmlResponse, Request
from scrapy import Spider
from scrapy.exceptions import IgnoreRequest
from scrapy.utils.defer import deferred_from_coro
import json

from .auth import sign_request, create_auth_headers
from .config import Config
from .endpoints import API_URL
from .version import __version__
from .utils import extract_response_data
from .operations import AskPablosAPIMapValidator, create_api_payload
from .exceptions import (
    AskPablosAPIError, RateLimitError, AuthenticationError,
    BrowserRenderingError, handle_api_error
)

# Configure logger
logger = logging.getLogger('askpablos_scrapy_api')


async def _async_post_request(url: str, data: str, headers: dict, timeout: int):
    """
    Make async POST request to AskPablos API.

    This replaces the synchronous requests.post() call with async aiohttp.
    Allows multiple requests to execute in parallel without blocking threads.
    """
    try:
        timeout_obj = aiohttp.ClientTimeout(total=timeout)
        async with aiohttp.ClientSession(timeout=timeout_obj) as session:
            async with session.post(url, data=data, headers=headers) as response:
                response_data = await response.json()
                return {
                    'status_code': response.status,
                    'data': response_data
                }
    except aiohttp.ClientError as e:
        raise ConnectionError(f"AskPablos API connection error: {str(e)}")
    except asyncio.TimeoutError:
        raise TimeoutError(f"AskPablos API request timed out")


class AskPablosAPIDownloaderMiddleware:
    """
    Scrapy middleware to route selected requests through AskPablos proxy API.

    This middleware activates **only** for requests that include:
        meta = {
            "askpablos_api_map": {
                "browser": True,          # Optional: Use headless browser
                "rotate_proxy": True,     # Optional: Use rotating proxy IP
                "wait_for_load": True,    # Optional: Wait for page load (requires browser: True)
                "screenshot": True,       # Optional: Take screenshot (requires browser: True)
                "js_strategy": "DEFAULT", # Optional: JavaScript strategy (requires browser: True)
            }
        }

    It will bypass any request that does not include the `askpablos_api_map` key or has it as an empty dict.

    Configuration (via settings.py or `custom_settings` in your spider):
        API_KEY      = "<your API key>"
        SECRET_KEY   = "<your secret key>"

    Optional settings:
        TIMEOUT = 30  # Request timeout in seconds
        MAX_RETRIES = 2  # Maximum number of retries for failed requests
    """

    def __init__(self, api_key, secret_key, config):
        """
        Initialize the middleware.

        Args:
            api_key: API key for authentication
            secret_key: Secret key for request signing
            config: Configuration object containing settings
        """
        self.api_key = api_key
        self.secret_key = secret_key
        self.config = config
        logger.debug(f"AskPablos Scrapy API initialized (version: {__version__})")

    @classmethod
    def from_crawler(cls, crawler):
        """Create a middleware instance from Scrapy crawler.

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
            error_msg = f"AskPablos API configuration validation failed: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        return cls(
            api_key=config.get('API_KEY'),
            secret_key=config.get('SECRET_KEY'),
            config=config
        )

    def process_request(self, request: Request, spider: Spider):
        """Process a Scrapy request using an async/await pattern."""
        proxy_cfg = request.meta.get("askpablos_api_map")

        if not proxy_cfg or not isinstance(proxy_cfg, dict) or not proxy_cfg:
            return None  # Skip proxying

        # Return a Twisted Deferred that wraps the async coroutine
        return deferred_from_coro(self._async_process_request(request, spider))

    async def _async_process_request(self, request: Request, spider: Spider) -> Optional[HtmlResponse]:
        """Async implementation of request processing."""
        try:
            # Validate and normalize the configuration
            proxy_cfg = request.meta.get("askpablos_api_map")
            validated_config = AskPablosAPIMapValidator.validate_config(proxy_cfg)

            # Create API payload with all the configuration
            payload = create_api_payload(
                request_url=request.url,
                request_method=request.method if hasattr(request, "method") else "GET",
                config=validated_config
            )

            # Override with default values if not specified
            if 'timeout' not in payload:
                payload['timeout'] = self.config.get('TIMEOUT')
            if 'maxRetries' not in payload:
                payload['maxRetries'] = self.config.get('RETRIES')

            # Sign the request using auth module
            request_json, signature_b64 = sign_request(payload, self.secret_key)
            headers = create_auth_headers(self.api_key, signature_b64)

            # Log sanitized payload for debugging
            logger.debug(f"AskPablos API: Sending request for URL: {request.url}")

            # Make async API request
            api_response = await _async_post_request(
                url=API_URL,
                data=request_json,
                headers=headers,
                timeout=payload.get('timeout', self.config.get('TIMEOUT'))
            )

            # Handle the response
            return self._handle_api_response(api_response, request, spider, validated_config)

        except json.JSONDecodeError:
            raise
        except ValueError as e:
            # Configuration validation error
            spider.crawler.stats.inc_value("askpablos/errors/config_validation")
            logger.error(f"AskPablos API configuration error: {e}")
            raise IgnoreRequest(f"Invalid askpablos_api_map configuration: {e}")

        except asyncio.TimeoutError:
            spider.crawler.stats.inc_value("askpablos/errors/timeout")
            raise TimeoutError(f"AskPablos API request timed out for URL: {request.url}")

        except aiohttp.ClientError as e:
            spider.crawler.stats.inc_value("askpablos/errors/connection")
            raise ConnectionError(f"AskPablos API connection error for URL: {request.url} - {str(e)}")

        except AuthenticationError as e:
            # Critical authentication error - stop the spider immediately
            spider.crawler.stats.inc_value("askpablos/errors/authentication")
            error_msg = f"Authentication failed with AskPablos API: {str(e)}."
            logger.error(error_msg)

            # Use crawler's signal system to close the spider
            await spider.crawler.engine.close_spider(spider, error_msg)

            # Raise IgnoreRequest to prevent this request from being processed further
            raise IgnoreRequest(error_msg)

        except (RateLimitError, BrowserRenderingError, AskPablosAPIError):
            raise

        except Exception as e:
            logger.error(e)
            spider.crawler.stats.inc_value("askpablos/errors/unexpected")
            raise RuntimeError(f"AskPablos API encountered an unexpected error: {str(e)}")

    @staticmethod
    def _handle_api_response(api_response: dict, request: Request, spider: Spider, validated_config: dict):
        """
        Handle successful API response.
        
        This processes the response and creates HtmlResponse object.
        """
        status_code = api_response['status_code']
        response_data = api_response['data']

        # Handle HTTP errors
        if status_code != 200:
            # Use factory function to create appropriate exception
            error = handle_api_error(status_code, response_data)
            spider.crawler.stats.inc_value(f"askpablos/errors/{error.__class__.__name__}")
            raise error

        # Parse response
        try:
            proxy_response = response_data
        except (ValueError, json.JSONDecodeError):
            spider.crawler.stats.inc_value("askpablos/errors/json_decode")
            raise json.JSONDecodeError(f"AskPablos API returned invalid JSON response for {request.url}", "", 0)

        # Validate response content
        html_body = proxy_response.get("responseBody", "")
        if not html_body:
            spider.crawler.stats.inc_value("askpablos/errors/empty_response")
            raise ValueError(f"AskPablos API response missing required 'responseBody' field")

        # Handle browser rendering errors
        if validated_config.get("browser") and proxy_response.get("error"):
            error_msg = proxy_response.get("error", "Unknown browser rendering error")
            spider.crawler.stats.inc_value("askpablos/errors/browser_rendering")
            raise BrowserRenderingError(error_msg, response=proxy_response)

        body = b64decode(html_body).decode()

        updated_meta = request.meta.copy()
        updated_meta['raw_api_response'] = proxy_response

        # Add additional response data to meta
        if proxy_response.get("screenshot"):
            updated_meta['screenshot'] = b64decode(proxy_response["screenshot"])

        return HtmlResponse(
            url=request.url,
            body=body,
            encoding="utf-8",
            request=request.replace(meta=updated_meta),
            status=proxy_response.get("statusCode", 200),
            flags=["askpablos-api"]
        )
