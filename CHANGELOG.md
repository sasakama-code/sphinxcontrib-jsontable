# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Automatic Performance Protection**: Default row limit of 10,000 rows to prevent performance issues with large datasets (#29)
- **Sphinx Configuration Option**: `jsontable_max_rows` setting in `conf.py` to customize default row limits (#29)
- **Unlimited Mode**: Support for `:limit: 0` to disable all row restrictions when needed (#29)
- **Smart Data Detection**: Automatic estimation of dataset size for intelligent limit application (#29)
- **User-Friendly Warnings**: Clear messages when automatic limits are applied to large datasets (#29)
- **Enhanced Documentation**: Comprehensive performance guidelines and best practices in README (#29)
- **Configuration Examples**: Multiple `conf.py` examples for different environment needs (#29)

### Changed
- **Improved Performance Behavior**: Large datasets (>10,000 rows) are now automatically limited with user warnings instead of potential memory issues (#29)
- **Enhanced TableConverter**: Added `_apply_default_limit()` method for intelligent limit management (#29)
- **Better User Experience**: Clear feedback when automatic performance protections are applied (#29)

### Performance
- **Memory Safety**: Automatic protection against accidentally processing extremely large datasets
- **Configurable Limits**: Users can adjust performance thresholds based on their environment
- **Build Optimization**: Faster documentation builds with predictable resource usage for large data

### Security
- **Resource Protection**: Default limits prevent potential denial-of-service through large data processing

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

### Security
- Implemented path traversal protection
- File access restricted to Sphinx source directory
- Input validation for all directive options
- Safe JSON parsing with error handling

### Performance
- Efficient JSON loading and parsing
- Memory-conscious handling of large datasets
- Optional row limiting for performance optimization

### Changed
- **BREAKING**: Minimum Python version raised to 3.10+
- **BREAKING**: Dropped support for Python 3.9 and earlier versions
- Updated build system to use modern Python packaging standards
- Improved code quality with ruff and mypy integration

---

## Release Notes

### Upcoming v0.2.0 - Performance & Usability Enhancements

**Coming Soon:** Major performance improvements and enhanced user experience for handling large datasets.

**Key Features:**
- 🚀 **Automatic Performance Protection**: Smart detection and handling of large datasets
- ⚙️ **Configurable Limits**: Customize performance thresholds via `conf.py`
- 🛡️ **Memory Safety**: Built-in protection against resource exhaustion
- 📊 **Enhanced Documentation**: Comprehensive performance guidelines and best practices
- 🔧 **Better User Experience**: Clear warnings and guidance for large data handling

**Performance Improvements:**
- Default 10,000 row limit for automatic protection
- Intelligent data size estimation
- User-friendly warnings for limit application
- Configurable behavior via `jsontable_max_rows` setting

**Compatibility:**
- No breaking changes - all existing documentation continues to work
- New features are opt-in and backwards compatible
- Enhanced performance for existing projects

### v0.1.0 - Initial Release

This is the first stable release of sphinxcontrib-jsontable, providing a robust solution for embedding JSON data as tables in Sphinx documentation.

**Key Features:**
- 🚀 Easy integration with existing Sphinx projects
- 📊 Multiple data format support
- 🛡️ Security-first design with path protection
- 📝 Comprehensive documentation and examples
- 🔧 Flexible customization options

**Compatibility:**
- Python 3.10+ (3.10, 3.11, 3.12)
- Sphinx 3.0+
- Docutils 0.18+

**Installation:**
```bash
pip install sphinxcontrib-jsontable
```

**Quick Start:**
```rst
.. jsontable:: data/example.json
   :header:
   :limit: 10
```

For detailed usage instructions, see [README.md](README.md).

---

## Migration Guide

### Upgrading to v0.2.0 (Performance Enhancements)

**No Breaking Changes**: All existing documentation will continue to work without modification.

**New Features Available:**

1. **Automatic Protection**: Large datasets are now automatically limited to 10,000 rows with clear user warnings
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

2. **Custom Configuration**: Add to your `conf.py` for personalized behavior
   ```python
   # Recommended addition to conf.py
   jsontable_max_rows = 5000  # Adjust based on your needs
   ```

3. **Unlimited Mode**: Use `:limit: 0` when you need to display all data
   ```rst
   .. jsontable:: large_but_needed.json
      :header:
      :limit: 0  # Show all rows regardless of size
   ```

**Recommended Actions:**
- Review your documentation for large datasets that could benefit from explicit limits
- Consider adding `jsontable_max_rows` configuration for consistent behavior
- Update documentation to mention performance features for users

### Python Version Requirements

**Important:** This package requires Python 3.10 or later. If you're using an older Python version:

1. **Upgrade Python**: Install Python 3.10+ on your system
2. **Virtual Environment**: Create a new virtual environment with the supported Python version
3. **Dependencies**: Ensure all your project dependencies are compatible with Python 3.10+

### From Custom Solutions

If you're currently using custom scripts or other methods to generate tables from JSON:

1. **Export your data to JSON format** if not already in JSON
2. **Replace custom table generation** with `.. jsontable::` directive
3. **Update file paths** to be relative to your Sphinx source directory
4. **Add appropriate options** (`:header:`, `:limit:`, etc.) based on your needs
5. **Consider performance settings** for large datasets

### From Other Extensions

**From sphinx-jsonschema:**
- Replace `.. jsonschema::` with `.. jsontable::`
- Remove schema validation options (not applicable)
- Add `:header:` option if you want column headers
- Benefit from automatic performance protection

**From manual table creation:**
- Replace manual reStructuredText tables with `.. jsontable::` directive
- Move your data to JSON files for easier maintenance
- Leverage automatic header extraction for object arrays
- Use performance features for large datasets

---

## Best Practices for Large Data

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
