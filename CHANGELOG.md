# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-06-06

### Added
- **JSON Key Order Preservation**: Headers now maintain the original key order from JSON objects instead of alphabetical sorting (#27)
- **Automatic Performance Protection**: Default row limit of 10,000 rows to prevent performance issues with large datasets (#29)
- **Sphinx Configuration Option**: `jsontable_max_rows` setting in `conf.py` to customize default row limits (#29)
- **Unlimited Mode**: Support for `:limit: 0` to disable all row restrictions when needed (#29)
- **Smart Data Detection**: Automatic estimation of dataset size for intelligent limit application (#29)
- **User-Friendly Warnings**: Clear messages when automatic limits are applied to large datasets (#29)
- **Enhanced Security Constraints**: Added limits for maximum keys (1,000), objects (10,000), and key length (255 characters) in header extraction (#27)
- **Enhanced Documentation**: Comprehensive performance guidelines and best practices in README (#29)
- **Configuration Examples**: Multiple `conf.py` examples for different environment needs (#29)

### Changed
- **Improved Header Extraction**: `_extract_headers()` method now preserves JSON key order while maintaining performance and security (#27)
- **Enhanced Performance Behavior**: Large datasets (>10,000 rows) are now automatically limited with user warnings instead of potential memory issues (#29)
- **Better TableConverter**: Added `_apply_default_limit()` method for intelligent limit management (#29)
- **Improved User Experience**: Clear feedback when automatic performance protections are applied (#29)

### Fixed
- **Key Order Consistency**: JSON object keys now appear in tables in their original order, improving readability for configuration files and structured data (#27)

### Performance
- **Memory Safety**: Automatic protection against accidentally processing extremely large datasets
- **Configurable Limits**: Users can adjust performance thresholds based on their environment
- **Build Optimization**: Faster documentation builds with predictable resource usage for large data
- **Efficient Header Processing**: Optimized header extraction with realistic performance constraints

### Security
- **Resource Protection**: Default limits prevent potential denial-of-service through large data processing
- **Header Extraction Limits**: Maximum key count, object count, and key length constraints prevent resource exhaustion
- **Input Validation**: Enhanced validation for JSON key processing

## [0.1.0] - 2025-06-02

### Added
- Initial release of sphinxcontrib-jsontable
- Support for JSON files and inline content rendering as tables
- `header` option to include first row as table header
- `encoding` option for custom file encoding (default: utf-8)
- `limit` option to restrict number of rows displayed
- Support for multiple JSON data formats:
  - Arrays of objects (with automatic header extraction from keys)
  - 2D arrays (with optional header row)
  - Single objects (key-value pairs)
  - Mixed data types with safe string conversion
- Comprehensive error handling and validation
- Path traversal protection for security
- Safe file access within Sphinx source directory only
- Detailed logging for debugging
- Full integration with both reStructuredText and MyST Markdown
- Complete documentation with examples and best practices

### Changed
- **BREAKING**: Minimum Python version raised to 3.10+
- **BREAKING**: Dropped support for Python 3.9 and earlier versions
- Updated build system to use modern Python packaging standards
- Improved code quality with ruff and mypy integration

### Security
- Implemented path traversal protection
- File access restricted to Sphinx source directory
- Input validation for all directive options
- Safe JSON parsing with error handling

### Performance
- Efficient JSON loading and parsing
- Memory-conscious handling of large datasets
- Optional row limiting for performance optimization

---

## Migration Guide

### Upgrading to v0.2.0

**No Breaking Changes**: All existing documentation will continue to work without modification.

**New Features Available:**

1. **Enhanced JSON Key Order**: Tables now display JSON object keys in their original order
   ```rst
   # Before: Keys were alphabetically sorted
   # After: Keys maintain their original order from JSON
   .. jsontable:: config.json
      :header:
   ```

2. **Automatic Performance Protection**: Large datasets are now automatically limited to 10,000 rows with clear user warnings
   ```rst
   # Before: Manual limit required for large datasets
   .. jsontable:: large_data.json
      :header:
      :limit: 100

   # After: Automatic protection (manual limit still supported)
   .. jsontable:: large_data.json
      :header:
      # Automatically limited with user warning if >10,000 rows
   ```

3. **Custom Configuration**: Add to your `conf.py` for personalized behavior
   ```python
   # Recommended addition to conf.py
   jsontable_max_rows = 5000  # Adjust based on your needs
   ```

4. **Unlimited Mode**: Use `:limit: 0` when you need to display all data
   ```rst
   .. jsontable:: large_but_needed.json
      :header:
      :limit: 0  # Show all rows regardless of size
   ```

**Recommended Actions:**
- Review your documentation for large datasets that could benefit from explicit limits
- Consider adding `jsontable_max_rows` configuration for consistent behavior
- Update documentation to mention performance features for users
- No action needed for key order preservation - it works automatically

### Upgrading from v0.1.0

**JSON Key Order**: If you were relying on alphabetical key sorting, note that tables now preserve the original JSON key order. This generally improves readability but may affect visual consistency in some cases.

**Performance**: Large datasets are now automatically protected. If you have very large datasets and want to display all rows, use `:limit: 0`.

### Python Version Requirements

**Important:** This package requires Python 3.10 or later. If you're using an older Python version:

1. **Upgrade Python**: Install Python 3.10+ on your system
2. **Virtual Environment**: Create a new virtual environment with the supported Python version
3. **Dependencies**: Ensure all your project dependencies are compatible with Python 3.10+

### From Other Extensions

**From sphinx-jsonschema:**
- Replace `.. jsonschema::` with `.. jsontable::`
- Remove schema validation options (not applicable)
- Add `:header:` option if you want column headers
- Benefit from automatic performance protection and key order preservation

**From manual table creation:**
- Replace manual reStructuredText tables with `.. jsontable::` directive
- Move your data to JSON files for easier maintenance
- Leverage automatic header extraction for object arrays
- Use performance features for large datasets

---

## Best Practices

### Performance Configuration Examples

**Conservative (Low-memory environments):**
```python
# conf.py
jsontable_max_rows = 1000
```

**Balanced (Most use cases):**
```python
# conf.py  
jsontable_max_rows = 10000  # Default
```

**Aggressive (High-memory environments):**
```python
# conf.py
jsontable_max_rows = 50000
```

### Data Size Guidelines

| Data Size | Recommended Approach | Configuration |
|-----------|---------------------|---------------|
| < 1,000 rows | No configuration needed | Default settings |
| 1,000-10,000 rows | Default automatic protection | `jsontable_max_rows = 10000` |
| > 10,000 rows | Explicit limits recommended | Custom limits + `:limit:` option |
| > 100,000 rows | Consider data preprocessing | Split files or database approach |

### JSON Key Order Best Practices

- **Configuration Files**: Key order preservation improves readability for YAML-to-JSON converted configs
- **API Documentation**: Logical key ordering enhances understanding of data structures
- **Structured Data**: Original key order often reflects data hierarchy and importance

---

## Contributing to Changelog

When contributing to this project, please:

1. **Add entries to the Unreleased section** for new features, changes, or fixes
2. **Follow the format** specified in Keep a Changelog
3. **Include appropriate subsections** (Added, Changed, Deprecated, Removed, Fixed, Security)
4. **Be descriptive** but concise in your entries
5. **Include issue/PR references** where applicable

Example entry format:
```markdown
### Added
- New `custom-option` directive option for advanced formatting (#123)
- Support for YAML input in addition to JSON (#145)

### Fixed
- Resolved encoding issue with non-ASCII characters in file paths (#134)
```

---

*For the latest updates and detailed release information, see the [GitHub Releases](https://github.com/sasakama-code/sphinxcontrib-jsontable/releases) page.*
