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

AskPablos Scrapy API requires Python 3.9 or higher and Scrapy 2.6.0 or higher.

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

### Global Settings (settings.py)

Configure the middleware globally in your project's `settings.py` file:

```python
# Required settings
API_KEY = "your_api_key"          # Your AskPablos API key
SECRET_KEY = "your_secret_key"    # Your AskPablos secret key

# Optional global settings
TIMEOUT = 30          # Request timeout in seconds
MAX_RETRIES = 2       # Maximum number of retries for failed requests

# Add the middleware
DOWNLOADER_MIDDLEWARES = {
    'askpablos_scrapy_api.middleware.AskPablosAPIDownloaderMiddleware': 585,
}
```

### Per-Request Configuration

Configure individual requests using the `askpablos_api_map` in request meta:

```python
meta = {
    "askpablos_api_map": {
        "browser": True,          # Use headless browser
        "rotate_proxy": True,     # Rotate proxy IPs  
        "wait_for_load": True,    # Wait for page load (requires browser: True)
        "screenshot": True,       # Take screenshot (requires browser: True)
        "js_strategy": "DEFAULT", # JavaScript strategy (requires browser: True)
    }
}
```

---

## Basic Usage

### Simple Browser Rendering

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
                    "rotate_proxy": True
                }
            },
            callback=self.parse
        )
    
    def parse(self, response):
        # Process the response normally
        for item in response.css('.item'):
            yield {
                'title': item.css('h2::text').get(),
                'description': item.css('p::text').get()
            }
```

---

## Advanced Usage

### JavaScript Strategy Options

The `js_strategy` parameter controls JavaScript execution:

```python
# Stealth mode - runs stealth script & minimal JS
meta = {"askpablos_api_map": {"js_strategy": True}}

# No JavaScript - faster for static content
meta = {"askpablos_api_map": {"js_strategy": False}}

# Default browser behavior
meta = {"askpablos_api_map": {"js_strategy": "DEFAULT"}}
```

### Screenshot Capture

```python
def start_requests(self):
    yield scrapy.Request(
        url='https://example.com',
        meta={
            "askpablos_api_map": {
                "browser": True,
                "screenshot": True,
                "js_strategy": "DEFAULT"
            }
        },
        callback=self.parse_with_screenshot
    )

def parse_with_screenshot(self, response):
    # Access screenshot data
    screenshot = response.meta.get('screenshot')
    if screenshot:
        with open('page_screenshot.png', 'wb') as f:
            f.write(screenshot)
```

### SPA (Single Page Application) Handling

```python
meta = {
    "askpablos_api_map": {
        "browser": True,
        "wait_for_load": True,
        "js_strategy": "DEFAULT"
    }
}
```

---

## Configuration Options

### Meta Configuration Options

| Option          | Type     | Description                                            |
|-----------------|----------|--------------------------------------------------------|
| `browser`       | bool     | Use headless browser rendering                         |
| `rotate_proxy`  | bool     | Use rotating proxy IP addresses                        |
| `wait_for_load` | bool     | Wait for page to fully load (requires browser: True)   |
| `screenshot`    | bool     | Take screenshot of the page (requires browser: True)   |
| `js_strategy`   | bool/str | JavaScript execution strategy (requires browser: True) |

**Important Note:** The options `wait_for_load`, `screenshot`, and `js_strategy` only work when `browser: True` is set. If browser rendering is disabled, these options will be ignored.

### Settings.py Configuration

| Setting       | Type | Default  | Description                |
|---------------|------|----------|----------------------------|
| `API_KEY`     | str  | Required | Your AskPablos API key     |
| `SECRET_KEY`  | str  | Required | Your AskPablos secret key  |
| `TIMEOUT`     | int  | 30       | Request timeout in seconds |
| `MAX_RETRIES` | int  | 2        | Maximum retry attempts     |

---

## Best Practices

1. **Use appropriate JavaScript strategies**:
   - Use `"DEFAULT"` for normal websites
   - Use `True` for stealth mode on protected sites
   - Use `False` for static content to improve performance

2. **Configure timeouts appropriately**:
   - Set reasonable `TIMEOUT` values in settings.py
   - Consider page complexity when setting timeouts

3. **Use screenshots for debugging**:
   - Enable screenshots when troubleshooting
   - Disable in production unless necessary

4. **Optimize retry settings**:
   - Configure `MAX_RETRIES` globally in settings.py

---

## Troubleshooting

### Common Issues

1. **Authentication Errors**: Verify your API_KEY and SECRET_KEY
2. **Timeout Issues**: Increase TIMEOUT in settings.py
3. **JavaScript Problems**: Try different js_strategy values
4. **Rate Limiting**: Reduce concurrent requests in your spider
