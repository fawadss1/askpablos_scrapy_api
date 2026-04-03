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


async def async_post_request(url: str, data: str, headers: dict, timeout: int):
    """
    Make an async POST request to AskPablos API.

    Allows multiple requests to execute in parallel without blocking threads.
    """
    try:
        timeout_obj = aiohttp.ClientTimeout(total=timeout)
        async with aiohttp.ClientSession(timeout=timeout_obj) as session:
            async with session.post(url, data=data, headers=headers) as response:
                response_data = await response.json()
                return {
                    'status_code': response.status,
                    'data': response_data,
                    'headers': dict(response.headers),
                }
    except aiohttp.ClientError as e:
        raise ConnectionError(f"AskPablos API connection error: {str(e)}") from None
    except asyncio.TimeoutError:
        raise TimeoutError(f"AskPablos API request timed out") from None


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
