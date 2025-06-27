# AskPablos Scrapy API

This directory contains the documentation for AskPablos Scrapy API.

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
