# AskPablos Scrapy API - Usage Guide

This guide walks you through how to configure and use AskPablosScrapyAPI in your Scrapy project.

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Basic Usage](#basic-usage)
- [Advanced Usage](#advanced-usage)
- [Configuration Options](#configuration-options)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Installation

Install the package using pip:

```bash
pip install askpablos-scrapy-api
```

Or directly from the repository:

```bash
pip install git+https://github.com/fawadss1/askpablos-scrapy-api.git
```

---

## Configuration

There are multiple ways to configure the AskPablos Scrapy API middleware:

### 1. Project-wide Settings (settings.py)

You can configure the middleware for all spiders in your project by adding it to your project's `settings.py` file:

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

### 2. Spider-specific Configuration (custom_settings)

You can also configure the middleware for specific spiders using the `custom_settings` attribute:

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

For enhanced security, you can store your API keys in environment variables:

```bash
# Set these environment variables before running your spider
export ASKPABLOS_API_KEY="your-api-key-here"
export ASKPABLOS_SECRET_KEY="your-secret-key-here"
```

---

## Basic Usage

AskPablosScrapyAPI only processes requests that include the `askpablos_api_map` in the request's `meta` dictionary. Requests without this configuration will follow the standard Scrapy processing path.

### Example Spider:

```python
import scrapy

class ExampleSpider(scrapy.Spider):
    name = "example"
    start_urls = ["https://example.com"]
    
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={
                    "askpablos_api_map": {
                        "browser": True,          # Use headless browser
                        "rotate_proxy": True      # Use rotating proxy IP
                    }
                }
            )
    
    def parse(self, response):
        # Process the response normally
        yield {
            "title": response.css("title::text").get(),
            "content": response.css("p::text").getall()
        }
```

---

---

## Configuration Options

The `askpablos_api_map` accepts the following parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `browser` | Boolean | `False` | When `True`, uses a headless browser to render JavaScript and handle complex anti-bot measures |
| `rotate_proxy` | Boolean | `False` | When `True`, routes the request through a rotating proxy to avoid IP-based rate limiting |

Required configuration settings:

| Option | Type | Description |
|--------|------|-------------|
| `API_KEY` | String | Your AskPablos API key |
| `SECRET_KEY` | String | Your AskPablos secret key |
| `DOWNLOADER_MIDDLEWARES` | Dict | Scrapy downloader middlewares configuration |

Recommended optional settings:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `ASKPABLOS_TIMEOUT` | Integer | 30 | Request timeout in seconds |
| `ASKPABLOS_MAX_RETRIES` | Integer | 2 | Maximum number of retries for failed requests |
| `ASKPABLOS_RETRY_DELAY` | Float | 1.0 | Initial delay between retries in seconds |

---

## Best Practices

1. **Resource Management**: Use the headless browser option only when necessary, as it consumes more resources
2. **Rate Limiting**: Respect website ToS by setting appropriate delays between requests
3. **Timeout Configuration**: Adjust `ASKPABLOS_TIMEOUT` based on the target website's response time
4. **Error Handling**: Add proper error handling for API unavailability scenarios

```python
def errback_handler(self, failure):
    self.logger.error(f"Request failed: {failure}")
    # Implement retry logic or fallback behavior
```

---

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Ensure your API_KEY and SECRET_KEY are correct
   - Check that your subscription is active

2. **Timeout Errors**
   - The target website might be slow to respond
   - Consider increasing the request timeout settings

3. **Empty Responses**
   - Check if the target website has anti-bot measures that require additional configuration
   - Try enabling the browser option for fully rendered pages

For more help, check the [FAQ](./faq.md) or open an issue on the [GitHub repository](https://github.com/fawadss1/askpablos-scrapy-api/issues).
