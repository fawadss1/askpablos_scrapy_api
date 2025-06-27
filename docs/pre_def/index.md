# AskPablos Scrapy API

A professional Scrapy integration for seamlessly routing requests through AskPablos Proxy API with support for headless browser rendering and rotating IP addresses.

## Key Features

- 🔄 **Selective Proxying**: Only routes requests with `askpablos_api_map` in their meta
- 🌐 **Headless Browser Support**: Render JavaScript-heavy pages
- 🔄 **Rotating Proxies**: Access to a pool of rotating IP addresses
- 🔒 **Secure Authentication**: HMAC-SHA256 request signing
- 🔁 **Automatic Retries**: With exponential backoff
- ⚠️ **Comprehensive Error Handling**: Detailed logging and error reporting
- 🛡️ **Rate Limiting**: Built-in request rate limiting to avoid overloading the API

## Requirements

- Python 3.9+
- Scrapy 2.6+
- Valid AskPablos Proxy API credentials

## Installation

```bash
pip install askpablos-scrapy-api
```

Or install directly from GitHub:

```bash
pip install git+https://github.com/fawadss1/askpablos-scrapy-api.git
```

## Basic Setup

Add AskPablosAPIDownloaderMiddleware to your Scrapy settings:

```python
# In your settings.py
API_KEY = "your_api_key"  # Your AskPablos API key
SECRET_KEY = "your_secret_key"  # Your AskPablos secret key

# Optional settings
ASKPABLOS_TIMEOUT = 30  # Request timeout in seconds
ASKPABLOS_MAX_RETRIES = 2  # Maximum number of retries for failed requests
ASKPABLOS_RETRY_DELAY = 1.0  # Initial delay between retries in seconds

# Add the middleware
DOWNLOADER_MIDDLEWARES = {
    'askpablos_scrapy_api.middleware.AskPablosAPIDownloaderMiddleware': 950,  # Adjust priority as needed
}
```

Or use custom settings in your spider:

```python
class MySpider(scrapy.Spider):
    name = 'myspider'
    
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
    
    # ...spider implementation...
```

## Quick Example

```python
import scrapy

class MySpider(scrapy.Spider):
    name = 'myspider'
    
    def start_requests(self):
        urls = [
            'https://example.com',
            'https://api-intensive-site.com'
        ]
        
        # Regular Scrapy request - NOT using the API
        yield scrapy.Request(url=urls[0], callback=self.parse_regular)
        
        # Request using AskPablos API with a headless browser
        yield scrapy.Request(
            url=urls[1],
            callback=self.parse_api,
            meta={
                'askpablos_api_map': {
                    'browser': True,  # Use headless browser
                    'rotate_proxy': True,  # Use rotating proxies
                }
            }
        )
    
    def parse_regular(self, response):
        # Handle response from a direct request
        pass
        
    def parse_api(self, response):
        # Handle response from AskPablos API
        # (Response will be processed exactly like a normal Scrapy response)
        pass
```

## Environment Variables

Instead of putting sensitive API keys in your settings file, you can use environment variables:

```bash
# Set these environment variables before running your spider
export ASKPABLOS_API_KEY="your_api_key"
export ASKPABLOS_SECRET_KEY="your_secret_key"
```

## Documentation

- [Detailed Usage Guide](usage.md) - Complete instructions for configuring and using AskPablos Scrapy API
- [FAQ](faq.md) - Answers to common questions and troubleshooting help

## How It Works

AskPablos Scrapy API intercepts requests with the `askpablos_api_map` in their meta dictionary and routes them through the AskPablos proxy service. The service can process requests using headless browsers and/or rotating proxies as specified, before returning the HTML response.

Requests without the `askpablos_api_map` configuration bypass the processing entirely, giving you full control over which requests use the proxy service.

## Advanced Configuration

```python
# Request with all available options
yield scrapy.Request(
    url="https://example.com",
    callback=self.parse,
    meta={
        'askpablos_api_map': {
            'browser': True,  # Use headless browser
            'rotate_proxy': True,  # Use rotating proxy
            'timeout': 60  # Custom timeout for this request only
        }
    }
)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Fawad Ali ([@fawadss1](https://github.com/fawadss1))
