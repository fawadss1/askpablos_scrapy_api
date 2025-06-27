# AskPablos Scrapy API - Frequently Asked Questions

This document addresses common questions and scenarios you may encounter when using AskPablosScrapyAPI.

## General Questions

### What is AskPablosScrapyAPI?

AskPablosScrapyAPI is a Scrapy integration that routes selected requests through the AskPablos proxy API. It allows you to seamlessly use features like headless browsers and rotating proxies in your Scrapy spiders.

### How does AskPablosScrapyAPI work?

The integration intercepts requests that have the `askpablos_api_map` key in their `meta` dictionary. It then forwards these requests through the AskPablos API service, which can process them using headless browsers and/or rotating proxies as specified, before returning the response.

### Does it work with all websites?

AskPablosScrapyAPI works with most websites, but success depends on several factors:
- The complexity of the target website's anti-bot measures
- The configuration options you've selected
- Current proxy availability
- API rate limits on your plan

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

Set `browser: True` in the `askpablos_api_map` to use a headless browser that will fully render JavaScript before returning the response:

```python
meta={
    "askpablos_api_map": {
        "browser": True
    }
}
```

### Does this integrate with Scrapy's download handlers?

Yes, AskPablosScrapyAPI integrates seamlessly with Scrapy's download handlers. It processes the request before any handlers are called and returns a standard HtmlResponse object that other components can process normally.

### Can I modify headers for proxied requests?

The current version doesn't support direct header modification for proxy requests. This feature may be added in future releases.

## Troubleshooting

### I'm getting authentication errors

If you're seeing authentication errors, verify:
1. Your API_KEY and SECRET_KEY are correctly set in settings.py
2. Your API subscription is active
3. You have sufficient credits remaining in your account

### My requests are timing out

If your requests are timing out:
1. The target website may be slow to respond
2. Consider increasing the `DOWNLOAD_TIMEOUT` setting in Scrapy
3. Check if the website has heavy JavaScript that takes longer to render

### I'm getting empty content in responses

This can happen if:
1. The website has sophisticated anti-bot measures
2. You need to enable the `browser: True` option for JavaScript rendering
3. The website is blocking the proxy IP addresses

### Rate limiting issues

If you're being rate-limited:
1. Enable `rotate_proxy: True` to cycle through different IP addresses
2. Add delays between requests using Scrapy's `DOWNLOAD_DELAY` setting
3. Consider using a higher tier API plan with more allowances

## Billing and Subscription

### How am I charged for usage?

Usage is typically charged based on:
- Number of requests
- Usage of headless browsers (more resource-intensive)
- Proxy rotation frequency

Refer to your AskPablos API service subscription for specific details.

### Can I set usage limits?

Currently, AskPablosScrapyAPI doesn't include built-in usage limitations. You can:
1. Use Scrapy's `CLOSESPIDER_PAGECOUNT` or `CLOSESPIDER_ITEMCOUNT` settings
2. Implement custom extensions to track and limit requests
3. Monitor your usage through the AskPablos dashboard

### My subscription credits are depleted, but my spider is still running

AskPablosScrapyAPI will return errors when API requests fail due to depleted credits. To handle this:

1. Implement error handling in your spider
2. Set up alerts based on response statuses
3. Use the `errback` parameter in requests for graceful fallbacks:

```python
yield scrapy.Request(
    url="https://example.com", 
    callback=self.parse,
    errback=self.error_handler,
    meta={"askpablos_api_map": {"browser": True}}
)

def error_handler(self, failure):
    self.logger.error(f"Request failed: {failure}")
    # Implement custom handling for API failures
```

## Advanced Usage

### Can I use AskPablosScrapyAPI selectively in my project?

Yes! AskPablosScrapyAPI only activates for requests that explicitly include the `askpablos_api_map` in their `meta`. All other requests will follow the standard Scrapy processing path.

### Is there a way to retry failed requests with different settings?

Yes, you can implement custom retry logic:

```python
def errback_handler(self, failure):
    request = failure.request
    if "askpablos_api_map" in request.meta:
        # Try again with different settings
        new_meta = request.meta.copy()
        new_meta["askpablos_api_map"] = {"browser": True, "rotate_proxy": True}
        
        yield scrapy.Request(
            url=request.url,
            callback=request.callback,
            meta=new_meta,
            dont_filter=True  # Allow duplicate requests
        )
```

### Can I combine this with other Scrapy components?

Absolutely. AskPablosScrapyAPI works well with other Scrapy components. Just be mindful of the order in which they're executed, which is controlled by the number assigned to each middleware in the `DOWNLOADER_MIDDLEWARES` setting.

If you have any questions not covered here, please open an issue on the [GitHub repository](https://github.com/fawadss1/askpablos-scrapy-api/issues).
