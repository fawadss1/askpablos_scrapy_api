import json
import logging
from typing import Optional

from scrapy import signals
from scrapy.http import HtmlResponse, Request
from scrapy import Spider
from scrapy.exceptions import IgnoreRequest
from scrapy.utils.defer import deferred_from_coro

from .auth import sign_request, create_auth_headers
from .config import Config
from .operations import AskPablosAPIMapValidator, create_api_payload
from .exceptions import (
    AskPablosAPIError,
    RateLimitError,
    AuthenticationError,
)
from .http import AskPablosHTTPClient, handle_api_response

logger = logging.getLogger('askpablos_scrapy_api')


class AskPablosAPIDownloaderMiddleware:
    """
    Scrapy middleware to route selected requests through AskPablos proxy API.

    Requests are forwarded to the API in parallel: every proxied request
    immediately fires an async HTTP POST through a shared aiohttp session
    without waiting for any other in-flight request to complete first.

    This middleware activates **only** for requests that include:
        meta = {
            "askpablos_api_map": {
                "browser": True,                # Optional: Use headless browser
                "screenshot": True,             # Optional: Take screenshot (requires browser: True)
                "operations": [...],            # Optional: Browser operations (requires browser: True)
                "geoLocation": "PK",            # Optional: Target country (2-letter ISO code)
                "proxyType": "residential",     # Optional: "datacenter", "residential", or "mobile"
            }
        }

    Configuration (via settings.py or `custom_settings` in your spider):
        API_KEY = "<your API key>"
        SECRET_KEY = "<your secret key>"
    """

    def __init__(self, api_key, secret_key, config):
        self.api_key = api_key
        self.secret_key = secret_key
        self.config = config
        self._spider_closing = False
        self._http_client = AskPablosHTTPClient()

    @classmethod
    def from_crawler(cls, crawler):
        """Create a middleware instance and connect spider lifecycle signals."""
        config = Config()
        config.load_from_settings(crawler.settings)

        try:
            config.validate()
        except ValueError as e:
            error_msg = f"AskPablos API configuration validation failed: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        mw = cls(
            api_key=config.get('API_KEY'),
            secret_key=config.get('SECRET_KEY'),
            config=config,
        )

        # Open the shared HTTP session when the spider starts, close it when done.
        # The session is shared across all concurrent requests so they run in parallel.
        crawler.signals.connect(mw._spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(mw._spider_closed, signal=signals.spider_closed)

        return mw

    def _spider_opened(self, spider):
        return deferred_from_coro(self._http_client.open())

    def _spider_closed(self, spider):
        return deferred_from_coro(self._http_client.close())

    def process_request(self, request: Request, spider: Spider):
        """Fire an async request immediately — does not wait for other in-flight requests."""
        if self._spider_closing:
            raise IgnoreRequest()

        proxy_cfg = request.meta.get("askpablos_api_map")
        if not proxy_cfg or not isinstance(proxy_cfg, dict):
            return None

        # Each call returns its own Deferred; Scrapy resolves them concurrently.
        return deferred_from_coro(self._async_process_request(request, spider))

    async def _async_process_request(self, request: Request, spider: Spider) -> Optional[HtmlResponse]:
        """Build and fire the API request; runs in parallel with all other in-flight requests."""
        try:
            proxy_cfg = request.meta.get("askpablos_api_map", {})
            validated_config = AskPablosAPIMapValidator.validate_config(proxy_cfg)

            payload = create_api_payload(
                request_url=request.url,
                request_method=request.method if hasattr(request, "method") else "GET",
                config=validated_config,
            )

            if 'timeout' not in payload:
                payload['timeout'] = self.config.get('TIMEOUT')
            if 'maxRetries' not in payload:
                payload['maxRetries'] = self.config.get('RETRIES')

            if request.method != "GET" and "body" not in payload:
                req_bdy = request.body.decode()
                if isinstance(req_bdy, str):
                    payload['body'] = json.loads(req_bdy)
                elif isinstance(req_bdy, dict):
                    payload['body'] = req_bdy

            request_json, signature_b64 = sign_request(payload, self.secret_key)
            headers = create_auth_headers(self.api_key, signature_b64)

            logger.debug(f"AskPablos API: Sending request for URL: {request.url}")

            api_response = await self._http_client.post(
                url=self.config.API_URL,
                data=request_json,
                headers=headers,
                timeout=payload.get('timeout', 30),
            )

            return handle_api_response(api_response, request, spider)

        except ValueError as e:
            spider.crawler.stats.inc_value("askpablos/errors/config_validation")
            logger.error(f"AskPablos API configuration error: {e}")
            raise IgnoreRequest(f"Invalid askpablos_api_map configuration: {e}") from None

        except TimeoutError:
            spider.crawler.stats.inc_value("askpablos/errors/timeout")
            raise TimeoutError(f"AskPablos API request timed out for URL: {request.url}") from None

        except ConnectionError as e:
            spider.crawler.stats.inc_value("askpablos/errors/connection")
            raise ConnectionError(f"AskPablos API connection error for URL: {request.url} - {str(e)}") from None

        except (AuthenticationError, RateLimitError):
            if not self._spider_closing:
                self._spider_closing = True
                spider.crawler.stats.inc_value("askpablos/errors/critical")
                raise
            else:
                raise IgnoreRequest() from None

        except AskPablosAPIError:
            raise

        except Exception as e:
            spider.crawler.stats.inc_value("askpablos/errors/unexpected")
            raise RuntimeError(f"AskPablos API encountered an unexpected error: {str(e)}") from None
