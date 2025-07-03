# AskPablos Scrapy API - Frequently Asked Questions

This document addresses common questions and scenarios you may encounter when using AskPablosScrapyAPI.

## General Questions

### What is AskPablosScrapyAPI?

AskPablosScrapyAPI is a Scrapy integration that routes selected requests through the AskPablos proxy API. It allows you to seamlessly use features like headless browsers, rotating proxies, and JavaScript strategies in your Scrapy spiders.

### How does AskPablosScrapyAPI work?

The integration intercepts requests that have the `askpablos_api_map` key in their `meta` dictionary. It then forwards these requests through the AskPablos API service, which can process them using headless browsers and/or rotating proxies as specified, before returning the response.

### Does it work with all websites?

AskPablosScrapyAPI works with most websites, but success depends on several factors:
- The complexity of the target website's anti-bot measures
- The JavaScript strategy you've selected
- Current proxy availability
- API rate limits on your plan

## Configuration Questions

### Where do I configure timeout and retry settings?

Timeout and retry settings are configured globally in your `settings.py` file:

```python
# In settings.py
TIMEOUT = 30          # Request timeout in seconds
MAX_RETRIES = 2       # Maximum number of retries
```

These cannot be overridden in individual request meta.

### Do all options work without browser rendering?

No, several options require `browser: True` to function:

- `wait_for_load` - Only works with browser rendering
- `screenshot` - Only works with browser rendering  
- `js_strategy` - Only works with browser rendering

If you set these options without `browser: True`, they will be ignored.

### What's the difference between the JavaScript strategies?

- `True` - Runs stealth script & minimal JS (good for protected sites)
- `False` - No stealth injection, no JS rendering (fastest for static content)
- `"DEFAULT"` - Normal browser behavior (best for most sites)

**Note:** All JavaScript strategies require `browser: True` to work.

### Can I take screenshots for debugging?

Yes, set `screenshot: True` in your request meta, but **you must also set `browser: True`**:

```python
meta = {
    "askpablos_api_map": {
        "browser": True,        # Required for screenshot functionality
        "screenshot": True
    }
}
```

Access the screenshot in your callback:

```python
def parse(self, response):
    screenshot = response.meta.get('screenshot')
    if screenshot:
        with open('debug.png', 'wb') as f:
            f.write(screenshot)
```

## Technical Questions

### Can I use it with Scrapy's CrawlSpider?

Yes, you can use AskPablosScrapyAPI with any Scrapy spider class, including CrawlSpider. Just make sure to set the `meta` with `askpablos_api_map` for the requests you want to proxy.

```python
def start_requests(self):
    yield scrapy.Request(
        url="https://example.com",
        callback=self.parse,
        meta={"askpablos_api_map": {"browser": True}}
    )
```

### How do I handle JavaScript-rendered content?

Set `browser: True` and choose an appropriate `js_strategy`:

```python
meta = {
    "askpablos_api_map": {
        "browser": True,
        "js_strategy": "DEFAULT",
        "wait_for_load": True
    }
}
```

### Does this integrate with Scrapy's download handlers?

Yes, AskPablosScrapyAPI works as a downloader middleware, which integrates seamlessly with Scrapy's request/response cycle without interfering with other components.

### Can I override retry delay for specific requests?

No, retry delays are handled automatically by the AskPablos service and cannot be configured.

## Troubleshooting

### Why am I getting authentication errors?

1. Verify your API_KEY and SECRET_KEY in settings.py
2. Check if you're using environment variables correctly
3. Ensure your API credentials are active

### My requests are timing out

1. Increase the TIMEOUT value in settings.py
2. Check if the target website is slow to respond
3. Consider using different JavaScript strategies

### JavaScript isn't working properly

1. Try different `js_strategy` values:
   - Use `"DEFAULT"` for normal sites
   - Use `True` for stealth mode
   - Use `False` for static content
2. Enable `wait_for_load: True` for SPAs
3. Take screenshots to debug what the browser sees

### I'm being rate limited

1. Reduce concurrent requests in your spider
2. Consider using fewer requests per second

### Screenshots aren't working

1. Ensure `browser: True` is set
2. Check that `screenshot: True` is in your meta
3. Verify the response contains screenshot data

## Best Practices

### When should I use browser rendering?

Use `browser: True` when:
- The site heavily relies on JavaScript
- Content is loaded dynamically
- You need to interact with the page
- The site uses SPA (Single Page Application) architecture

### How to optimize performance?

1. Use `js_strategy: False` for static content
2. Disable screenshots in production
3. Set appropriate timeout values
4. Reduce request frequency to avoid rate limiting

### How to debug issues?

1. Enable screenshots: `screenshot: True`
2. Check the raw API response: `response.meta.get('raw_api_response')`
3. Use appropriate log levels
4. Test with different JavaScript strategies

## Error Codes

### Common HTTP Status Codes

- **401**: Authentication failed - check your API credentials
- **429**: Rate limited - reduce request frequency
- **500**: Server error - contact AskPablos support
- **503**: Service unavailable - try again later

### Scrapy Integration Errors

- **IgnoreRequest**: Configuration validation failed
- **TimeoutError**: Request exceeded timeout limit
- **ConnectionError**: Network connectivity issues
