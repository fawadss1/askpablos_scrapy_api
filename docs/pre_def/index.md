# AskPablos Scrapy API

A professional Scrapy integration for seamlessly routing requests through AskPablos Proxy API with support for headless browser rendering and JavaScript strategies.

## Key Features

- 🔄 **Selective Proxying**: Only routes requests with `askpablos_api_map` in their meta
- 🌐 **Headless Browser Support**: Render JavaScript-heavy pages
- 🔄 **Rotating Proxies**: Access to a pool of rotating IP addresses
- 🧠 **JavaScript Strategies**: Three modes for different scraping scenarios
- 📸 **Screenshot Capture**: Take screenshots
- 🔒 **Secure Authentication**: HMAC-SHA256 request signing
- 🔁 **Automatic Retries**: Configurable retry logic
- ⚠️ **Comprehensive Error Handling**: Detailed logging and error reporting

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

## Quick Start

### 1. Configure Settings

Add to your `settings.py`:

```python
# Required settings
API_KEY = "your_api_key"          # Your AskPablos API key
SECRET_KEY = "your_secret_key"    # Your AskPablos secret key

# Optional global settings
TIMEOUT = 30          # Request timeout in seconds
MAX_RETRIES = 2       # Maximum number of retries

# Add the middleware
DOWNLOADER_MIDDLEWARES = {
    'askpablos_scrapy_api.middleware.AskPablosAPIDownloaderMiddleware': 585,
}
```

### 2. Use in Your Spider

```python
import scrapy

class MySpider(scrapy.Spider):
    name = 'example'
    
    def start_requests(self):
        yield scrapy.Request(
            url='https://example.com',
            meta={
                "askpablos_api_map": {
                    "browser": True,
                    "rotate_proxy": True,
                    "js_strategy": "DEFAULT"
                }
            }
        )
```

## Configuration Options

### Meta Configuration

| Option          | Type     | Description                                            |
|-----------------|----------|--------------------------------------------------------|
| `browser`       | bool     | Use headless browser rendering                         |
| `rotate_proxy`  | bool     | Use rotating proxy IP addresses                        |
| `wait_for_load` | bool     | Wait for page to fully load (requires browser: True)   |
| `screenshot`    | bool     | Take screenshot of the page (requires browser: True)   |
| `js_strategy`   | bool/str | JavaScript execution strategy (requires browser: True) |

**Important Note:** The options `wait_for_load`, `screenshot`, and `js_strategy` only work when `browser: True` is set.

### JavaScript Strategies

- `True` - Runs stealth script & minimal JS
- `False` - No stealth injection, no JS rendering
- `"DEFAULT"` - Normal browser behavior

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
