from __future__ import annotations

import asyncio
import json
import logging
from base64 import b64decode

import aiohttp
from scrapy.http import HtmlResponse, Request
from scrapy import Spider

from .exceptions import (
    handle_api_error,
)

logger = logging.getLogger('askpablos_scrapy_api')


class AskPablosHTTPClient:
    """
    Persistent HTTP client backed by a single shared aiohttp.ClientSession.

    A new TCP connection is opened for each concurrent request up to the
    connector limit, then reused via the pool — so every in-flight request
    runs in parallel without waiting for the previous one to finish.

    Lifecycle (tied to the Scrapy spider):
        await client.open()   # spider_opened signal
        await client.post(…)  # called for every proxied request
        await client.close()  # spider_closed signal
    """

    def __init__(self):
        self._session: aiohttp.ClientSession | None = None

    async def open(self):
        """Create the shared session. Must be called before any post()."""
        # limit=0 disables the per-host cap; Scrapy's CONCURRENT_REQUESTS
        # setting already governs how many requests are in flight at once.
        connector = aiohttp.TCPConnector(limit=0)
        self._session = aiohttp.ClientSession(connector=connector)
        logger.debug("AskPablos HTTP client session opened")

    async def close(self):
        """Close the shared session and release all connections."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
            logger.debug("AskPablos HTTP client session closed")

    async def post(self, url: str, data: str, headers: dict, timeout: int) -> dict:
        """
        POST to the AskPablos backend using the shared session.

        All concurrent callers share the same session and connection pool,
        so their network I/O overlaps — no request blocks another.
        """
        if self._session is None or self._session.closed:
            raise RuntimeError("AskPablosHTTPClient is not open. Call open() first.")

        try:
            timeout_obj = aiohttp.ClientTimeout(total=timeout)
            async with self._session.post(url, data=data, headers=headers, timeout=timeout_obj) as response:
                response_data = await response.json()
                return {
                    'status_code': response.status,
                    'data': response_data,
                    'headers': dict(response.headers),
                }
        except aiohttp.ClientError as e:
            raise ConnectionError(f"AskPablos API connection error: {str(e)}") from None
        except asyncio.TimeoutError:
            raise TimeoutError("AskPablos API request timed out") from None


def handle_api_response(api_response: dict, request: Request, spider: Spider):
    """
    Process an API response and return a Scrapy HtmlResponse.

    Raises the appropriate exception on HTTP errors or invalid response content.
    """
    status_code = api_response['status_code']
    proxy_response = api_response['data']

    if status_code != 200:
        error = handle_api_error(status_code, proxy_response)
        spider.crawler.stats.inc_value(f"askpablos/errors/{error.__class__.__name__}")
        raise error

    html_body = proxy_response.get("responseBody", "")
    if not html_body:
        spider.crawler.stats.inc_value("askpablos/errors/empty_response")
        raise ValueError("AskPablos API response missing required 'responseBody' field")

    body = b64decode(html_body).decode()

    updated_meta = request.meta.copy()
    updated_meta['raw_api_response'] = proxy_response

    if proxy_response.get("screenshot"):
        updated_meta['screenshot'] = b64decode(proxy_response["screenshot"])

    return HtmlResponse(
        url=request.url,
        headers=api_response.get("headers"),
        body=body,
        encoding="utf-8",
        request=request.replace(meta=updated_meta),
        status=status_code,
        flags=["askpablos-api"]
    )
