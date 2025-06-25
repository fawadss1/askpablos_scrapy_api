"""
Basic tests for the AskPablos Scrapy API middleware.

To run these tests:
    pytest -v tests/test.py
"""
import pytest
from unittest.mock import MagicMock, patch

from scrapy.http import Request, Response
from scrapy import Spider

from askpablos_scrapy_api.middleware import AskPablosAPIDownloaderMiddleware


class TestAskPablosAPIDownloaderMiddleware:
    """Test cases for the AskPablosAPIDownloaderMiddleware middleware."""

    @pytest.fixture
    def mock_crawler(self):
        """Create a mock crawler with settings."""
        crawler = MagicMock()
        crawler.settings = {
            'API_KEY': 'test_api_key',
            'SECRET_KEY': 'test_secret_key',
        }
        return crawler

    @pytest.fixture
    def middleware(self, mock_crawler):
        """Create an instance of the middleware."""
        return AskPablosAPIDownloaderMiddleware.from_crawler(mock_crawler)

    @pytest.fixture
    def spider(self):
        """Create a mock spider."""
        spider = MagicMock(spec=Spider)
        spider.name = 'test_spider'
        spider.logger = MagicMock()
        spider.crawler = MagicMock()
        spider.crawler.stats = MagicMock()
        return spider

    def test_process_request_skips_non_askpablos_requests(self, middleware, spider):
        """Test that requests without askpablos_api_map are skipped."""
        request = Request('https://httpbin.org/ip')
        result = middleware.process_request(request, spider)
        assert result is None

    def test_process_request_skips_empty_askpablos_config(self, middleware, spider):
        """Test that requests with empty askpablos_api_map are skipped."""
        request = Request('https://httpbin.org/ip', meta={'askpablos_api_map': {}})
        result = middleware.process_request(request, spider)
        assert result is None

    @patch('requests.post')
    def test_process_request_with_valid_config(self, mock_post, middleware, spider):
        """Test processing a request with valid askpablos_api_map."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'body': '<html><body>Test</body></html>',
            'status': 200
        }
        mock_post.return_value = mock_response

        # Create request with askpablos config
        request = Request(
            url='https://httpbin.org/ip',
            meta={'askpablos_api_map': {'browser': True, 'rotate_proxy': True}}
        )

        # Process the request
        result = middleware.process_request(request, spider)

        # Verify the result
        assert result is not None
        assert isinstance(result, Response)
        assert result.body == b'<html><body>Test</body></html>'
        assert result.url == 'https://httpbin.org/ip'

    @patch('requests.post')
    def test_retry_on_error(self, mock_post, middleware, spider):
        """Test retrying when an error occurs."""
        # First request fails
        mock_post.side_effect = [
            Exception("Connection error"),
            MagicMock(
                status_code=200,
                json=lambda: {'body': '<html><body>Test</body></html>', 'status': 200}
            )
        ]

        request = Request(
            url='https://httpbin.org/ip',
            meta={'askpablos_api_map': {'browser': True}}
        )

        # Override retry delay for testing
        middleware.retry_delay = 0.01

        # Process the request
        result = middleware.process_request(request, spider)

        # Verify retry happened and we got a response
        assert mock_post.call_count == 2
        assert result is not None
        assert isinstance(result, Response)

    @patch('askpablos_scrapy_api.auth.sign_request')
    def test_auth_signature_creation(self, mock_sign, middleware, spider):
        """Test that authentication signature is created correctly."""
        # Setup
        expected_json = '{"url":"https://httpbin.org/ip","method":"GET","browser":true,"rotateProxy":false}'
        expected_signature = "test_signature"
        mock_sign.return_value = (expected_json, expected_signature)

        with patch('requests.post') as mock_post:
            mock_post.return_value = MagicMock(
                status_code=200,
                json=lambda: {'body': '<html></html>', 'status': 200}
            )

            # Create and process request
            request = Request(
                url='https://httpbin.org/ip',
                meta={'askpablos_api_map': {'browser': True}}
            )
            middleware.process_request(request, spider)

            # Verify
            mock_sign.assert_called_once()
            call_args = mock_post.call_args
            assert call_args[1]['headers']['X-API-Key'] == 'test_api_key'
            assert call_args[1]['headers']['X-Signature'] == expected_signature
