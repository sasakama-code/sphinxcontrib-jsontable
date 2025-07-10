"""
Sphinx configuration template for sphinxcontrib-jsontable.

This template provides a complete configuration example for integrating
sphinxcontrib-jsontable into your Sphinx documentation project.
"""

import os
import sys

# Add the project root to sys.path to ensure imports work correctly
sys.path.insert(0, os.path.abspath(".."))

# -- Project information -----------------------------------------------------

project = "sphinxcontrib-jsontable Configuration Example"
copyright = "2024, sasakama-code"
author = "sasakama-code"

# The full version, including alpha/beta/rc tags
release = "0.4.0"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinxcontrib.jsontable",  # Enable the jsontable extension
    "myst_parser",  # For MyST Markdown support (optional)
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# -- Options for MyST Markdown support ---------------------------------------

# MyST configuration (optional, only if using MyST Markdown)
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "html_image",
]

# Source file suffixes
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# =============================================================================
# sphinxcontrib-jsontable Configuration
# =============================================================================

# Performance configuration for JSON table rendering
# This is the ONLY supported configuration option for sphinxcontrib-jsontable
# Set the default maximum number of rows to display before applying automatic limits
jsontable_max_rows = 10000  # Safe default for most use cases

# Configuration examples for different use cases:

# For documentation with mostly small datasets:
# jsontable_max_rows = 100

# For large data-heavy documentation:
# jsontable_max_rows = 50000

# To disable automatic limiting entirely (not recommended for web deployment):
# jsontable_max_rows = None

# =============================================================================
# IMPORTANT NOTES:
# =============================================================================
# 
# The following configuration options are NOT supported by sphinxcontrib-jsontable
# and should NOT be used in your conf.py file:
#
# ❌ jsontable_enable_caching = True       # NOT SUPPORTED
# ❌ jsontable_cache_ttl = 3600            # NOT SUPPORTED  
# ❌ jsontable_memory_optimization = True  # NOT SUPPORTED
# ❌ jsontable_streaming_threshold = 5000  # NOT SUPPORTED
#
# These settings may appear in examples or suggestions elsewhere, but they are
# not implemented in the current version of sphinxcontrib-jsontable.
#
# The extension has internal caching and performance optimizations that are
# automatically applied and do not require user configuration.
#
# For the most up-to-date configuration information, please refer to:
# https://github.com/sasakama-code/sphinxcontrib-jsontable

# =============================================================================
# Additional Configuration Examples
# =============================================================================

# Environment-specific configuration example:
# if os.getenv('SPHINX_ENV') == 'development':
#     jsontable_max_rows = 100  # Fast builds during development
# elif os.getenv('SPHINX_ENV') == 'production':
#     jsontable_max_rows = 10000  # Full functionality for users
# else:
#     jsontable_max_rows = 5000  # Default for most cases

# Memory-based configuration example:
# try:
#     import psutil
#     memory_gb = psutil.virtual_memory().total / (1024**3)
#     if memory_gb < 4:
#         jsontable_max_rows = 1000    # Conservative for low-memory systems
#     elif memory_gb < 8:
#         jsontable_max_rows = 5000    # Moderate for typical systems
#     else:
#         jsontable_max_rows = 25000   # Aggressive for high-memory systems
# except ImportError:
#     jsontable_max_rows = 10000  # Default fallback

# Note: Users can still override the global setting with explicit :limit: options
# in individual jsontable directives