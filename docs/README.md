# AskPablos Scrapy API Documentation

This directory contains the documentation for AskPablos Scrapy API.

## Quick Start

The AskPablos Scrapy API provides enhanced web scraping capabilities with browser automation and JavaScript strategies.

### Basic Configuration

```python
# In your spider
meta = {
    "askpablos_api_map": {
        "browser": True,
        "rotate_proxy": True,
        "js_strategy": "DEFAULT"
    }
}
```

### Settings Configuration

Configure global settings in your `settings.py`:

```python
# Required
API_KEY = "your_api_key_here"
SECRET_KEY = "your_secret_key_here"

# Optional
TIMEOUT = 30          # Request timeout
MAX_RETRIES = 2       # Maximum retries
```

## Building the documentation

### Setup

Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Building HTML documentation

```bash
# On Windows
make.bat html

# On Unix/Linux/Mac
make html
```

The generated HTML will be in the `_build/html` directory.

### Building other formats

```bash
# PDF
make latexpdf

# ePub
make epub
```

## Documentation Structure

- `index.md`: Main landing page
- `usage.md`: Usage instructions and examples
- `faq.md`: Frequently Asked Questions
- `api.md`: API reference documentation
