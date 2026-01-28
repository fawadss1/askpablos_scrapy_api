# AskPablos Scrapy API
[![PyPI Version](https://img.shields.io/pypi/v/askpablos-scrapy-api.svg)](https://pypi.python.org/pypi/askpablos-scrapy-api)
[![Supported Python Versions](https://img.shields.io/pypi/pyversions/askpablos-scrapy-api.svg)](https://pypi.python.org/pypi/askpablos-scrapy-api)

A professional Scrapy integration for seamlessly routing requests through AskPablos Proxy API with support for headless browser rendering and rotating IP addresses.

## Documentation

Full documentation is available at: [https://askpablos-scrapy-api.readthedocs.io/en/latest/index.html](https://askpablos-scrapy-api.readthedocs.io/en/latest/index.html)

## Key Features

- 🔄 **Selective Proxying**: Only routes requests with `askpablos_api_map` in their meta
- 🌐 **Headless Browser Support**: Render JavaScript-heavy pages
- 🔄 **Rotating Proxies**: Access to a pool of rotating IP addresses
- 🧠 **JavaScript Strategies**: Three modes for different scraping scenarios
- 📸 **Screenshot Capture**: Take screenshots
- 📮 **POST Request Support**: Seamlessly handle both GET and POST requests with automatic body inclusion
- 🔒 **Secure Authentication**: HMAC-SHA256 request signing
- 🔁 **Automatic Retries**: Configurable retry logic
- ⚠️ **Comprehensive Error Handling**: Detailed logging and error reporting

## Quick Installation

```bash
pip install askpablos-scrapy-api
```

## License

MIT License - See LICENSE file for details.
