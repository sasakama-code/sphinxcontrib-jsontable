# sphinxcontrib-jsontable

[![Tests](https://github.com/sasakama-code/sphinxcontrib-jsontable/actions/workflows/ci.yml/badge.svg)](https://github.com/sasakama-code/sphinxcontrib-jsontable/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/sasakama-code/sphinxcontrib-jsontable/graph/badge.svg)](https://codecov.io/gh/sasakama-code/sphinxcontrib-jsontable)
[![Python](https://img.shields.io/pypi/pyversions/sphinxcontrib-jsontable.svg)](https://pypi.org/project/sphinxcontrib-jsontable/)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/sasakama-code/sphinxcontrib-jsontable)

**Languages:** [English](README.md) | [日本語](README_ja.md)

A powerful Sphinx extension that renders JSON data (from files or inline content) as beautifully formatted reStructuredText tables. Perfect for documentation that needs to display structured data, API examples, configuration references, and data-driven content.

## Background / Motivation

In recent years, there has been an increasing trend of using documents as data sources for Retrieval Augmented Generation (RAG). However, tabular data within documents often loses its structural relevance during the process of being ingested by RAG systems. This presented a challenge where the original value of the structured data could not be fully leveraged.

Against this backdrop, sphinxcontrib-jsontable was developed to directly embed structured data, such as JSON, as meaningful tables in Sphinx-generated documents, with the objective to ensure that readability and the data's value as a source effectively coexist.

## Features

✨ **Flexible Data Sources**
* Load JSON from files within your Sphinx project
* Embed JSON directly inline in your documentation
* Support for relative file paths with safe path resolution

📊 **Multiple Data Formats**
* JSON objects (single or arrays)
* 2D arrays with optional headers
* Mixed data types with automatic string conversion
* Nested data structures (flattened appropriately)

🎛️ **Customizable Output**
* Optional header rows with automatic key extraction
* Row limiting for large datasets
* Custom file encoding support
* Responsive table formatting

🔒 **Robust & Safe**
* Path traversal protection
* Comprehensive error handling
* Encoding validation
* Detailed logging for debugging

⚡ **Performance Optimized**
* Automatic row limiting for large datasets (10,000 rows by default)
* Configurable performance limits
* Memory-safe processing
* User-friendly warnings for large data

## Installation

### From PyPI
```bash
pip install sphinxcontrib-jsontable
```

### From Source
```bash
git clone https://github.com/sasakama-code/sphinxcontrib-jsontable.git
cd sphinxcontrib-jsontable
pip install -e .
```

## Quick Start

### 1. Enable the Extension

Add to your `conf.py`:

```python
extensions = [
    # ... your other extensions
    'sphinxcontrib.jsontable',
]

# Optional: Configure performance limits
jsontable_max_rows = 5000  # Default: 10000
```

### 2. Create Sample Data

Create `data/users.json`:
```json
[
  {
    "id": 1,
    "name": "Alice Johnson",
    "email": "alice@example.com",
    "department": "Engineering",
    "active": true
  },
  {
    "id": 2,
    "name": "Bob Smith",
    "email": "bob@example.com", 
    "department": "Marketing",
    "active": false
  }
]
```

### 3. Add to Your Documentation

**In reStructuredText (.rst):**
```rst
User Database
=============

.. jsontable:: data/users.json
   :header:
   :limit: 10
```

**In Markdown (with myst-parser):**
````markdown
# User Database

```{jsontable} data/users.json
:header:
:limit: 10
```
````

### 4. Build Your Documentation

```bash
sphinx-build -b html docs/ build/html/
```

## Comprehensive Usage Guide

### Data Format Support

#### Array of Objects (Most Common)

Perfect for database records, API responses, configuration lists:

```json
[
  {"name": "Redis", "port": 6379, "ssl": false},
  {"name": "PostgreSQL", "port": 5432, "ssl": true},
  {"name": "MongoDB", "port": 27017, "ssl": true}
]
```

```rst
.. jsontable:: data/services.json
   :header:
```

**Output:** Automatically generates headers from object keys (name, port, ssl).

#### 2D Arrays with Headers

Great for CSV-like data, reports, matrices:

```json
[
  ["Service", "Port", "Protocol", "Status"],
  ["HTTP", 80, "TCP", "Active"],
  ["HTTPS", 443, "TCP", "Active"],
  ["SSH", 22, "TCP", "Inactive"]
]
```

```rst
.. jsontable:: data/ports.json
   :header:
```

**Output:** First row becomes the table header.

#### 2D Arrays without Headers

Simple tabular data:

```json
[
  ["Monday", "Sunny", "75°F"],
  ["Tuesday", "Cloudy", "68°F"],
  ["Wednesday", "Rainy", "62°F"]
]
```

```rst
.. jsontable:: data/weather.json
```

**Output:** All rows treated as data (no headers).

#### Single Object

Configuration objects, settings, metadata:

```json
{
  "database_host": "localhost",
  "database_port": 5432,
  "debug_mode": true,
  "max_connections": 100
}
```

```rst
.. jsontable:: data/config.json
   :header:
```

**Output:** Keys become one column, values become another.

### Directive Options Reference

| Option | Type | Default | Description | Example |
|--------|------|---------|-------------|---------|
| `header` | flag | off | Include first row as table header | `:header:` |
| `encoding` | string | `utf-8` | File encoding for JSON files | `:encoding: utf-16` |
| `limit` | positive int/0 | automatic | Maximum rows to display (0 = unlimited) | `:limit: 50` |

## Configuration Options

Configure sphinxcontrib-jsontable in your `conf.py`:

### Performance Settings

```python
# Maximum rows before automatic limiting kicks in (default: 10000)
jsontable_max_rows = 5000

# Example configurations for different use cases:

# For documentation with mostly small datasets
jsontable_max_rows = 100

# For large data-heavy documentation
jsontable_max_rows = 50000

# Disable automatic limiting entirely (not recommended for web deployment)
# jsontable_max_rows = None  # Will use unlimited by default
```

### Advanced Examples

#### Automatic Performance Protection

When no `:limit:` is specified, the extension automatically protects against large datasets:

```rst
.. jsontable:: data/huge_dataset.json
   :header:

# If dataset > 10,000 rows, automatically shows first 10,000 with warning
# User sees: "Large dataset detected (25,000 rows). Showing first 10,000 
# rows for performance. Use :limit: option to customize."
```

#### Explicit Unlimited Processing

For cases where you need to display all data regardless of size:

```rst
.. jsontable:: data/large_but_manageable.json
   :header:
   :limit: 0

# ⚠️ Shows ALL rows - use with caution for web deployment
```

#### Large Dataset with Pagination

For performance and readability with large datasets:

```rst
.. jsontable:: data/large_dataset.json
   :header:
   :limit: 100

.. note::
   This table shows the first 100 entries out of 50,000+ total records. 
   Download the complete dataset: :download:`large_dataset.json <data/large_dataset.json>`
```

#### Non-UTF8 Encoding

Working with legacy systems or specific character encodings:

```rst
.. jsontable:: data/legacy_data.json
   :encoding: iso-8859-1
   :header:
```

#### Inline JSON for Examples

Perfect for API documentation, examples, tutorials:

```rst
API Response Format
==================

The user endpoint returns data in this format:

.. jsontable::

   {
     "user_id": 12345,
     "username": "john_doe",
     "email": "john@example.com",
     "created_at": "2024-01-15T10:30:00Z",
     "is_verified": true,
     "profile": {
       "first_name": "John",
       "last_name": "Doe",
       "avatar_url": "https://example.com/avatar.jpg"
     }
   }
```

#### Complex Nested Data

For nested JSON, the extension flattens appropriately:

```rst
.. jsontable::

   [
     {
       "id": 1,
       "name": "Product A",
       "category": {"name": "Electronics", "id": 10},
       "tags": ["popular", "sale"],
       "price": 99.99
     }
   ]
```

**Note:** Objects and arrays in values are converted to string representations.

### Integration Examples

#### With Sphinx Tabs

Combine with sphinx-tabs for multi-format documentation:

```rst
.. tabs::

   .. tab:: JSON Data

      .. jsontable:: data/api_response.json
         :header:

   .. tab:: Raw JSON

      .. literalinclude:: data/api_response.json
         :language: json
```

#### With Code Blocks

Document API endpoints with request/response examples:

```rst
Get Users Endpoint
==================

**Request:**

.. code-block:: http

   GET /api/v1/users HTTP/1.1
   Host: api.example.com
   Authorization: Bearer <token>

**Response:**

.. jsontable::

   [
     {
       "id": 1,
       "username": "alice",
       "email": "alice@example.com",
       "status": "active"
     },
     {
       "id": 2, 
       "username": "bob",
       "email": "bob@example.com",
       "status": "inactive"
     }
   ]
```

#### In MyST Markdown

Full MyST Markdown support for modern documentation workflows:

````markdown
# Configuration Reference

## Database Settings

```{jsontable} config/database.json
:header:
:encoding: utf-8
```

## Feature Flags

```{jsontable}
[
  {"feature": "dark_mode", "enabled": true, "rollout": "100%"},
  {"feature": "new_dashboard", "enabled": false, "rollout": "0%"},
  {"feature": "advanced_search", "enabled": true, "rollout": "50%"}
]
```
````

### File Organization Best Practices

#### Recommended Directory Structure

```
docs/
├── conf.py
├── index.rst
├── data/
│   ├── users.json
│   ├── products.json
│   ├── config/
│   │   ├── database.json
│   │   └── features.json
│   └── examples/
│       ├── api_responses.json
│       └── error_codes.json
└── api/
    └── endpoints.rst
```

#### Naming Conventions

- Use descriptive filenames: `user_permissions.json` not `data1.json`
- Group related data in subdirectories: `config/`, `examples/`, `test_data/`
- Include version or date when appropriate: `api_v2_responses.json`

### Performance Considerations

#### Automatic Protection for Large Datasets

The extension automatically protects against performance issues:

- **Default Limit**: 10,000 rows maximum by default
- **Smart Detection**: Automatically estimates dataset size
- **User Warnings**: Clear messages when limits are applied
- **Configurable**: Adjust limits via `jsontable_max_rows` setting

#### Performance Behavior

| Dataset Size | Default Behavior | User Action Required |
|--------------|------------------|---------------------|
| ≤ 10,000 rows | ✅ Display all rows | None |
| > 10,000 rows | ⚠️ Auto-limit + warning | Use `:limit:` to customize |
| Any size with `:limit: 0` | 🚨 Display all (unlimited) | Use with caution |

#### Build Time Optimization

**Small Datasets (< 1,000 rows):**
```rst
.. jsontable:: data/small_dataset.json
   :header:
   # No limit needed - processes quickly
```

**Medium Datasets (1,000-10,000 rows):**
```rst
.. jsontable:: data/medium_dataset.json
   :header:
   # Automatic protection applies - good performance
```

**Large Datasets (> 10,000 rows):**
```rst
.. jsontable:: data/large_dataset.json
   :header:
   :limit: 100
   # Explicit limit recommended for predictable performance
```

#### Memory Considerations

**Safe Configurations:**
```python
# Conservative (good for low-memory environments)
jsontable_max_rows = 1000

# Balanced (default - good for most use cases)
jsontable_max_rows = 10000

# Aggressive (high-memory environments only)
jsontable_max_rows = 100000
```

**Memory Usage Guidelines:**
- **~1MB JSON**: ~1,000-5,000 rows (safe for all environments)
- **~10MB JSON**: ~10,000-50,000 rows (requires adequate memory)
- **>50MB JSON**: Consider data preprocessing or database solutions

#### Best Practices for Large Data

1. **Use Appropriate Limits**:
   ```rst
   .. jsontable:: data/sales_data.json
      :header:
      :limit: 50
      
   *Showing top 50 sales records. Full data available in source file.*
   ```

2. **Consider Data Preprocessing**:
   - Split large files into logical chunks
   - Create summary datasets for documentation
   - Use database views instead of static files

3. **Optimize for Build Performance**:
   ```python
   # In conf.py - faster builds for large projects
   jsontable_max_rows = 100
   ```

4. **Provide Context for Limited Data**:
   ```rst
   .. jsontable:: data/user_activity.json
      :header:
      :limit: 20
      
   .. note::
      This table shows recent activity only. For complete logs, 
      see the :doc:`admin-dashboard` or download the 
      :download:`full dataset <data/user_activity.json>`.
   ```

### Migration Guide

#### Upgrading from Previous Versions

**No Breaking Changes**: Existing documentation continues to work unchanged.

**New Features Available**:
```rst
# Before: Manual limit required for large datasets
.. jsontable:: large_data.json
   :header:
   :limit: 100

# After: Automatic protection (manual limit still supported)
.. jsontable:: large_data.json
   :header:
   # Automatically limited to 10,000 rows with user warning
```

**Recommended Configuration Update**:
```python
# Add to conf.py for customized behavior
jsontable_max_rows = 5000  # Adjust based on your needs
```

### Troubleshooting

#### Common Issues

**Error: "No JSON data source provided"**
```rst
# ❌ Missing file path or content
.. jsontable::

# ✅ Provide file path or inline content  
.. jsontable:: data/example.json
```

**Error: "JSON file not found"**
- Check file path relative to source directory
- Verify file exists and has correct permissions
- Ensure no typos in filename

**Error: "Invalid inline JSON"**
- Validate JSON syntax using online validator
- Check for trailing commas, unquoted keys
- Ensure proper escaping of special characters

**Performance Warnings**
```
WARNING: Large dataset detected (25,000 rows). Showing first 10,000 rows for performance.
```
**Solutions:**
- Add explicit `:limit:` option: `:limit: 50`
- Use `:limit: 0` for unlimited (if needed)
- Increase global limit: `jsontable_max_rows = 25000`
- Consider data preprocessing for smaller files

**Encoding Issues**
```rst
# For non-UTF8 files
.. jsontable:: data/legacy.json
   :encoding: iso-8859-1
```

**Empty Tables**
- Check if JSON file is empty or null
- Verify JSON structure (must be array or object)
- Check if automatic limiting is hiding your data

#### Debug Mode

Enable detailed logging in `conf.py`:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# For sphinx-specific logs
extensions = ['sphinxcontrib.jsontable']

# Performance monitoring
jsontable_max_rows = 1000  # Lower limit for debugging
```

#### Testing Configuration

Create a simple test file to verify setup:

```json
[{"test": "success", "status": "ok"}]
```

```rst
.. jsontable:: test.json
   :header:
```

### Security Considerations

#### Path Traversal Protection

The extension automatically prevents directory traversal attacks:

```rst
# ❌ This will be blocked
.. jsontable:: ../../etc/passwd

# ✅ Safe relative paths only
.. jsontable:: data/safe_file.json
```

#### File Access

- Only files within the Sphinx source directory are accessible
- No network URLs or absolute system paths allowed
- File permissions respected by the system

#### Performance Security

- Default limits prevent accidental resource exhaustion
- Memory usage is bounded by configurable limits
- Large dataset warnings help prevent unintentional performance impact

### Migration Guide

#### From Other Extensions

**From sphinx-jsonschema:**
- Replace `.. jsonschema::` with `.. jsontable::`
- Remove schema validation options
- Add `:header:` option if needed

**From Custom Solutions:**
- Export your data to JSON format
- Replace custom table generation with `.. jsontable::`
- Update file paths to be relative to source directory

#### Version Compatibility

- **Sphinx:** 3.0+ (recommended: 4.0+)
- **Python:** 3.10+ (recommended: 3.11+)
- **Docutils:** 0.14+

### API Reference

#### Core Classes

**`JsonTableDirective`**
- Main Sphinx directive class
- Handles option parsing and execution
- Coordinates data loading, conversion, and rendering

**`JsonDataLoader`**  
- Loads JSON from files or inline content
- Validates encoding and file paths
- Provides secure file access

**`TableConverter`**
- Transforms JSON structures into 2D table data
- Handles different data formats (objects, arrays, mixed)
- Manages header extraction and row limiting
- Applies automatic performance limits

**`TableBuilder`**
- Generates Docutils table nodes
- Creates proper table structure with headers/body
- Handles cell formatting and padding

#### Error Handling

All errors inherit from `JsonTableError`:
- File access errors
- JSON parsing errors  
- Invalid data structure errors
- Path traversal attempts

### Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup
- Code style guidelines
- Testing procedures
- Pull request process

#### Development Setup

```bash
git clone https://github.com/sasakama-code/sphinxcontrib-jsontable.git
cd sphinxcontrib-jsontable
pip install -e ".[dev]"
pytest
```

#### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=sphinxcontrib.jsontable

# Run specific test
pytest tests/test_directives.py::test_json_table_basic
```

### Examples Repository

See the [`examples/`](examples/) directory for:
- Complete Sphinx project setup
- Various data format examples  
- Integration with other extensions
- Advanced configuration examples

```bash
cd examples/
sphinx-build -b html . _build/html/
```

### Development Tools

The [`scripts/`](scripts/) directory contains development and analysis tools used during the creation of performance features:

- **`performance_benchmark.py`** - Performance measurement and analysis tool
- **`memory_analysis.py`** - Memory usage analysis for different dataset sizes
- **`competitive_analysis.py`** - Industry standard research and best practices
- **`validate_ci_tests.py`** - CI environment testing and validation
- **`test_integration.py`** - Comprehensive integration testing

These tools were instrumental in establishing the scientific foundation for performance limits and ensuring enterprise-grade reliability. They can be used for ongoing performance monitoring and analysis.

```bash
# Run performance analysis
python scripts/performance_benchmark.py

# Validate CI environment
python scripts/validate_ci_tests.py
```

### Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed version history and release notes.

### License

This project is licensed under the [MIT License](LICENSE).

### Support

- **Documentation:** [GitHub Pages](https://sasakama-code.github.io/sphinxcontrib-jsontable/)
- **Issues:** [GitHub Issues](https://github.com/sasakama-code/sphinxcontrib-jsontable/issues)
- **Discussions:** [GitHub Discussions](https://github.com/sasakama-code/sphinxcontrib-jsontable/discussions)
