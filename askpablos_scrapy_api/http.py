from __future__ import annotations

import json
import logging
from base64 import b64decode

from twisted.internet.defer import succeed
from twisted.web.client import Agent, readBody, HTTPConnectionPool
from twisted.web.http_headers import Headers
from twisted.web.iweb import IBodyProducer
from zope.interface import implementer

from scrapy.http import HtmlResponse, Request
from scrapy import Spider

from .exceptions import handle_api_error

logger = logging.getLogger('askpablos_scrapy_api')


@implementer(IBodyProducer)
class _BytesProducer:
    """Minimal Twisted IBodyProducer that writes a fixed bytes payload."""

    def __init__(self, body: bytes):
        self.body = body
        self.length = len(body)

    def startProducing(self, consumer):
        consumer.write(self.body)
        return succeed(None)

    def stopProducing(self):
        pass

    def pauseProducing(self):
        pass

    def resumeProducing(self):
        pass


class AskPablosHTTPClient:
    """
    Persistent HTTP client backed by Twisted's Agent + HTTPConnectionPool.

    Using Twisted's native HTTP stack (not aiohttp) because Scrapy drives
    coroutines via _inlineCallbacks which never calls asyncio._set_running_loop(),
    so any aiohttp code that calls asyncio.get_running_loop() (timeouts, connector
    setup) raises RuntimeError: no running event loop.

    Lifecycle (tied to the Scrapy spider):
        client.open()         # spider_opened signal (synchronous)
        await client.post(…)  # called for every proxied request
        await client.close()  # spider_closed signal
    """

    def __init__(self):
        self._agent: Agent | None = None
        self._pool: HTTPConnectionPool | None = None

    def open(self):
        """Create the connection pool and agent. Synchronous — safe to call from signal handlers."""
        from twisted.internet import reactor
        self._pool = HTTPConnectionPool(reactor)
        self._agent = Agent(reactor, pool=self._pool)
        logger.debug("AskPablos HTTP client opened")

    async def close(self):
        """Drain and close all pooled connections."""
        if self._pool:
            await self._pool.closeCachedConnections()
            self._pool = None
            self._agent = None
            logger.debug("AskPablos HTTP client closed")

    async def post(self, url: str, data: str, headers: dict, timeout: int) -> dict:
        """
        POST to the AskPablos backend.

        All concurrent callers share the same connection pool so their network
        I/O overlaps — no request blocks another. Timeout is handled by Scrapy's
        DOWNLOAD_TIMEOUT at the Deferred level.
        """
        if self._agent is None:
            self.open()

        request_headers = Headers()
        for key, value in headers.items():
            request_headers.addRawHeader(
                key.encode() if isinstance(key, str) else key,
                value.encode() if isinstance(value, str) else value,
            )

        body = data.encode() if isinstance(data, str) else data

        try:
            response = await self._agent.request(
                b'POST',
                url.encode() if isinstance(url, str) else url,
                request_headers,
                _BytesProducer(body),
            )
            response_body = await readBody(response)
            response_data = json.loads(response_body)

            return {
                'status_code': response.code,
                'data': response_data,
                'headers': {
                    k.decode(): v[0].decode()
                    for k, v in response.headers.getAllRawHeaders()
                },
            }
        except Exception as e:
            msg = str(e)
            if any(w in msg.lower() for w in ('timeout', 'timed out')):
                raise TimeoutError("AskPablos API request timed out") from None
            raise ConnectionError(f"AskPablos API connection error: {msg}") from None


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
