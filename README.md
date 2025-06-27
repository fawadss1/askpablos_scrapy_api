# AskPablos Scrapy API

A professional Scrapy integration for seamlessly routing requests through AskPablos Proxy API with support for headless browser rendering and rotating IP addresses.

## Documentation

Full documentation is available at: [https://askpablos-scrapy-api.readthedocs.io/en/latest/index.html](https://askpablos-scrapy-api.readthedocs.io/en/latest/index.html)

## Key Features

- 🔄 **Selective Proxying**: Only routes requests with `askpablos_api_map` in their meta
- 🌐 **Headless Browser Support**: Render JavaScript-heavy pages
- 🔄 **Rotating Proxies**: Access to a pool of rotating IP addresses
- 🔒 **Secure Authentication**: HMAC-SHA256 request signing
- 🔁 **Automatic Retries**: With exponential backoff
- ⚠️ **Comprehensive Error Handling**: Detailed logging and error reporting
- 🛡️ **Rate Limiting**: Built-in request rate limiting to avoid overloading the API

## Quick Installation

```bash
pip install askpablos-scrapy-api
```

## License

MIT License - See LICENSE file for details.
