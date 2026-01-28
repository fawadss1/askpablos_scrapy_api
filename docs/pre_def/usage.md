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
APCLOUDY_URL = "https://domain.com"  # Base URL for AskPablos API (optional)
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
        "operations": [...]       # Browser operations for SPA interaction (requires browser: True)
    }
}
```

---

## Basic Usage

### Simple GET Request with Browser Rendering

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

### POST Request Support

```python
import scrapy
import json

class MySpider(scrapy.Spider):
    name = 'example'

    def start_requests(self):
        # Using FormRequest for POST requests
        yield scrapy.FormRequest(
            url='https://api.example.com/endpoint',
            formdata={'key': 'value'},
            meta={
                "askpablos_api_map": {
                    "browser": True,
                    "rotate_proxy": True
                }
            },
            callback=self.parse
        )

        # Or using Request with method='POST' and JSON body
        yield scrapy.Request(
            url='https://api.example.com/endpoint',
            method='POST',
            body=json.dumps({'key': 'value'}),
            headers={'Content-Type': 'application/json'},
            meta={
                "askpablos_api_map": {
                    "rotate_proxy": True
                }
            },
            callback=self.parse
        )

    def parse(self, response):
        # Process the response
        data = response.json()
        yield {'result': data}
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

#### Basic SPA Support

```python
meta = {
    "askpablos_api_map": {
        "browser": True,
        "wait_for_load": True,
        "js_strategy": "DEFAULT"
    }
}
```

#### Advanced SPA Interaction with Operations

For more complex SPAs that require waiting for specific elements or performing actions:

```python
def start_requests(self):
    yield scrapy.Request(
        url='https://spa-example.com',
        meta={
            "askpablos_api_map": {
                "browser": True,
                "js_strategy": "DEFAULT",
                "operations": [
                    {
                        "task": "waitForElement",
                        "match": {
                            "on": "xpath",
                            "rule": "visible",
                            "value": "//*[@id='content-loaded']"
                        },
                        "maxWait": 10,
                        "onFailure": "return"
                    }
                ]
            }
        },
        callback=self.parse_spa
    )

def parse_spa(self, response):
    # The page has waited for the element to be visible
    data = response.css('.dynamic-content::text').getall()
    yield {'data': data}
```

**Operations Parameters:**

- **task**: Action to perform
  - `waitForElement` - Wait for element to match condition

- **match**: Element matching criteria
  - `on`: `"xpath"` or `"css"` - Selector type
  - `rule`: Element state to wait for
    - `"visible"` - Element is visible on page
    - `"attached"` - Element exists in DOM
    - `"hidden"` - Element exists but is hidden
    - `"detached"` - Element is removed from DOM
  - `value`: Selector string (XPath or CSS selector)

- **maxWait** (optional): Maximum seconds to wait (must be > 0)
- **onFailure** (optional): Action when operation fails
  - `"continue"` - Ignore failure and continue
  - `"return"` - Stop operations and return page
  - `"throw"` - Raise an error

#### Multiple Operations Example

You can chain multiple operations:

```python
meta = {
    "askpablos_api_map": {
        "browser": True,
        "operations": [
            {
                "task": "waitForElement",
                "match": {
                    "on": "css",
                    "rule": "visible",
                    "value": "#login-form"
                },
                "maxWait": 5,
                "onFailure": "throw"
            },
            {
                "task": "waitForElement",
                "match": {
                    "on": "xpath",
                    "rule": "visible",
                    "value": "//div[@class='content-loaded']"
                },
                "maxWait": 15,
                "onFailure": "return"
            }
        ]
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
| `operations`    | list     | Browser operations for SPA interaction (requires browser: True) |

**Important Note:** The options `wait_for_load`, `screenshot`, `js_strategy`, and `operations` only work when `browser: True` is set. If browser rendering is disabled, these options will be ignored.

### Settings.py Configuration

| Setting         | Type | Default                               | Description                               |
|-----------------|------|---------------------------------------|-------------------------------------------|
| `API_KEY`       | str  | Required                              | Your AskPablos API key                    |
| `SECRET_KEY`    | str  | Required                              | Your AskPablos secret key                 |
| `APCLOUDY_URL`  | str  | https://appcloudy.askpablos.com       | Base URL for AskPablos API                |
| `TIMEOUT`       | int  | 30                                    | Request timeout in seconds                |
| `MAX_RETRIES`   | int  | 2                                     | Maximum retry attempts                    |

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
