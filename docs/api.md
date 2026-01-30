# API Reference

This section contains the detailed API reference for all public modules and classes in AskPablos Scrapy API.

## Middleware Module

The middleware module is responsible for integrating with Scrapy's downloader middleware system to route requests through AskPablos Proxy API.

### Configuration Options

The middleware accepts the following configuration in request meta:

```python
meta = {
    "askpablos_api_map": {
        "browser": True,          # Optional: Use headless browser
        "screenshot": True,       # Optional: Take screenshot (requires browser: True)
        "operations": [...]       # Optional: Browser operations for SPA interaction (requires browser: True)
    }
}
```

### HTTP Method Support

The middleware automatically supports both GET and POST HTTP methods:

- **GET requests**: Standard Scrapy requests are processed as GET by default
- **POST requests**: When using Scrapy FormRequest or setting `method='POST'`, the request body is automatically included in the API payload

### Settings Configuration

Global settings must be configured in `settings.py`:

```python
# Required settings
API_KEY = "your_api_key_here"
SECRET_KEY = "your_secret_key_here"

# Optional settings
APCLOUDY_URL = "https://domain.com"  # Base URL for AskPablos API
TIMEOUT = 30          # Request timeout in seconds
MAX_RETRIES = 2       # Maximum number of retries for failed requests
```

```{eval-rst}
.. automodule:: askpablos_scrapy_api.middleware
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
```

## Operations Module

The operations module handles configuration validation and API payload creation for enhanced features.

### Browser Operations for SPA Interaction

The `operations` parameter allows you to define advanced browser interactions for Single Page Applications:

```python
"operations": [
    {
        "task": "waitForElement",
        "match": {
            "on": "xpath",      # or "css"
            "rule": "visible",  # or "attached", "hidden", "detached"
            "value": "//*[@id='element']"
        },
        "maxWait": 30,          # Optional: seconds to wait (default: 30)
        "onFailure": "return"   # Optional: "continue", "return", or "throw"
    }
]
```

**Supported Tasks:**
- `waitForElement` - Wait for an element to match the specified condition

**Match Options:**
- `on`: Selector type - `"xpath"` or `"css"`
- `rule`: Element state - `"visible"`, `"attached"`, `"hidden"`, or `"detached"`
- `value`: The selector string (XPath or CSS selector)

**Optional Parameters:**
- `maxWait`: Maximum time to wait in seconds (must be > 0)
- `onFailure`: Action on failure - `"continue"` (ignore and continue), `"return"` (stop and return), or `"throw"` (raise error)

```{eval-rst}
.. automodule:: askpablos_scrapy_api.operations
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
```

## Authentication Module

The authentication module handles secure API authentication using HMAC-SHA256 request signing.

```{eval-rst}
.. automodule:: askpablos_scrapy_api.auth
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
```

## Configuration Module

The configuration module manages settings and configuration options for the AskPablos API integration.

```{eval-rst}
.. automodule:: askpablos_scrapy_api.config
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
```

## Endpoints Module

The endpoints module provides access to different API endpoints offered by the AskPablos service.

```{eval-rst}
.. automodule:: askpablos_scrapy_api.endpoints
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
```

## Exceptions Module

The exceptions module defines custom exceptions for error handling within the AskPablos Scrapy API.

```{eval-rst}
.. automodule:: askpablos_scrapy_api.exceptions
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
```

## Utilities Module

The utilities module provides helper functions for working with the AskPablos Scrapy API.

```{eval-rst}
.. automodule:: askpablos_scrapy_api.utils
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
```
