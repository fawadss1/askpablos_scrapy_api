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
        "rotate_proxy": True,     # Optional: Use rotating proxy IP
        "wait_for_load": True,    # Optional: Wait for page load (requires browser: True)
        "screenshot": True,       # Optional: Take screenshot (requires browser: True)
        "js_strategy": "DEFAULT", # Optional: JavaScript strategy (requires browser: True)
    }
}
```

### Settings Configuration

Global settings must be configured in `settings.py`:

```python
# Required settings
API_KEY = "your_api_key_here"
SECRET_KEY = "your_secret_key_here"

# Optional settings
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

### JavaScript Strategy Options

- `True` - Runs stealth script & runs minimal JS
- `False` - No stealth injection and not rendering JS of current page
- `"DEFAULT"` - Behave normal site as in browser

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
