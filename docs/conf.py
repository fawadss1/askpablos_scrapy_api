# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
import sphinx_rtd_theme

# Add the project root directory to Python path for autodoc extension to find the module
sys.path.insert(0, os.path.abspath('..'))

# -- Project information -----------------------------------------------------
project = 'AskPablos Scrapy API'
copyright = '2025, Fawad Ali'
author = 'Fawad Ali'

# Import the version from the package - handle potential import errors gracefully
try:
    from askpablos_scrapy_api.version import __version__
    release = __version__
except ImportError:
    release = '0.2.0'  # Default to this version if import fails

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',         # Include documentation from docstrings
    'sphinx.ext.viewcode',        # Add links to the source code
    'sphinx.ext.napoleon',        # Google/NumPy style docstrings
    'sphinx.ext.intersphinx',     # Link to other projects' documentation
    'sphinx.ext.autosectionlabel',  # Allow reference sections
    'myst_parser',               # Parse Markdown files
    'sphinx_rtd_theme',          # Read the Docs theme
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The master toctree document.
master_doc = 'index'

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_theme_options = {
    'navigation_depth': 3,
    'collapse_navigation': False,
    'sticky_navigation': True,
    'includehidden': True,
    'titles_only': False,
    'logo_only': False,
    'display_version': True,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Ensure the _static directory exists to prevent build warnings
os.makedirs(os.path.join(os.path.dirname(__file__), '_static'), exist_ok=True)

# -- Options for MyST Parser -------------------------------------------------
myst_enable_extensions = [
    'tasklist',      # GitHub-style task lists
    'smartquotes',   # Smart quotes
    'replacements',  # Common text replacements
    'colon_fence',   # Alternative to code fence syntax
]

# -- Options for autodoc extension -------------------------------------------
autodoc_member_order = 'bysource'
autodoc_typehints = 'description'
autoclass_content = 'both'
autodoc_mock_imports = ['scrapy', 'requests']

# -- Intersphinx configuration ---------------------------------------
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'scrapy': ('https://docs.scrapy.org/en/latest/', None),
    'requests': ('https://requests.readthedocs.io/en/latest/', None),
}
