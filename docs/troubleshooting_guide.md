# Troubleshooting Guide

## Quick Diagnosis

### Is your issue here?

| Problem | Quick Solution | Details |
|---------|----------------|---------|
| Tables not showing | Add `:header:` option | [Headers](#headers-not-showing) |
| "File not found" | Check file path | [File paths](#file-not-found-errors) |
| Slow performance | Add `:limit:` option | [Performance](#performance-issues) |
| Excel sheets not loading | Specify `:sheet:` name | [Excel issues](#excel-specific-issues) |
| Large dataset warnings | Use `:limit:` or increase `max_rows` | [Large data](#large-dataset-warnings) |

## Common Issues

### Headers Not Showing

**Problem**: Table displays data but no column headers

```rst
.. jsontable:: data/users.json
   # Headers missing!
```

**Solution**: Add the `:header:` option

```rst
.. jsontable:: data/users.json
   :header:  # ← Add this line
```

**Why this happens**: Headers are optional. The `:header:` option tells the extension to extract and display column names.

### File Not Found Errors

**Problem**: `FileNotFoundError` or "File does not exist"

```
ERROR: File 'data/report.xlsx' not found
```

**Solutions**:

1. **Check the file path** (most common):
   ```bash
   # From your Sphinx source directory:
   ls data/report.xlsx  # Should show the file
   ```

2. **Use relative paths**:
   ```rst
   # ✅ Correct (relative to source directory)
   .. jsontable:: data/report.xlsx
   
   # ❌ Incorrect (absolute paths usually don't work)
   .. jsontable:: /Users/me/Documents/report.xlsx
   ```

3. **Check file permissions**:
   ```bash
   # Ensure the file is readable
   chmod 644 data/report.xlsx
   ```

### Performance Issues

**Problem**: Sphinx build taking too long or hanging

**Symptoms**:
```
Building... (hanging at jsontable processing)
```

**Solutions**:

1. **Add row limits** (immediate fix):
   ```rst
   .. jsontable:: slow_file.xlsx
      :header:
      :limit: 100  # Start with small limits
   ```

2. **Use range specification**:
   ```rst
   .. jsontable:: big_file.xlsx
      :header:
      :range: "A1:J50"  # Process only needed cells
   ```

3. **Check file size**:
   ```bash
   ls -lh data/your_file.xlsx
   # If > 10MB, definitely use limits and ranges
   ```

### Large Dataset Warnings

**Problem**: Getting warnings about large datasets

```
WARNING: Large dataset detected (15,000 rows). Showing first 1,000 rows for performance.
```

**Solutions**:

1. **Accept the automatic limit** (recommended):
   ```rst
   .. jsontable:: large_data.json
      :header:
      # Warning is shown, but table works fine
   ```

2. **Set explicit limit**:
   ```rst
   .. jsontable:: large_data.json
      :header:
      :limit: 500  # Customize the limit
   ```

3. **Increase global limit**:
   ```python
   # conf.py
   jsontable_max_rows = 25000  # Allow larger datasets
   ```

4. **Use unlimited mode** (use carefully):
   ```rst
   .. jsontable:: large_data.json
      :header:
      :limit: 0  # Show all data (may impact performance)
   ```

## Excel-Specific Issues

### Sheet Not Found

**Problem**: "Sheet 'SheetName' not found"

```
ERROR: Sheet 'Results' not found in workbook
```

**Solutions**:

1. **Check available sheet names**:
   ```python
   # Quick Python script to check sheets:
   import openpyxl
   wb = openpyxl.load_workbook('data/your_file.xlsx')
   print("Available sheets:", wb.sheetnames)
   ```

2. **Use sheet index instead**:
   ```rst
   .. jsontable:: data/workbook.xlsx
      :header:
      :sheet: 0  # First sheet (0-based)
   ```

3. **Check for extra spaces**:
   ```rst
   # ❌ May have trailing spaces
   :sheet: "Results "
   
   # ✅ Clean sheet name  
   :sheet: "Results"
   ```

### Range Outside Bounds

**Problem**: "Range A1:Z1000 exceeds worksheet dimensions"

**Solutions**:

1. **Use auto-detection**:
   ```rst
   .. jsontable:: data/small_file.xlsx
      :header:
      # Let the system detect the right range
   ```

2. **Check actual file size**:
   ```rst
   .. jsontable:: data/file.xlsx
      :header:
      :range: "A1:E20"  # Start with smaller range
   ```

### Merged Cell Issues

**Problem**: Strange data layout with merged cells

**Solutions**:

1. **Try different merge modes**:
   ```rst
   # Expand merged cell values
   .. jsontable:: data/merged.xlsx
      :header:
      :merge-mode: "expand"
   
   # Use only first cell
   .. jsontable:: data/merged.xlsx
      :header:
      :merge-mode: "first"
   
   # Skip merged cell rows
   .. jsontable:: data/merged.xlsx
      :header:
      :merge-mode: "skip"
   ```

## JSON-Specific Issues

### Invalid JSON Format

**Problem**: "JSONDecodeError" or malformed JSON

```
ERROR: Invalid JSON format in data/broken.json
```

**Solutions**:

1. **Validate your JSON**:
   ```bash
   # Check JSON syntax
   python -m json.tool data/your_file.json
   ```

2. **Common JSON fixes**:
   ```json
   // ❌ Common mistakes:
   {
     "name": "value",  // No trailing commas
     "key": 'value'    // Use double quotes
   }
   
   // ✅ Correct format:
   {
     "name": "value",
     "key": "value"
   }
   ```

### Encoding Issues

**Problem**: Strange characters or encoding errors

**Solutions**:

1. **Specify encoding**:
   ```python
   # conf.py
   jsontable_default_encoding = 'utf-8'
   ```

2. **Convert file encoding**:
   ```bash
   # Convert to UTF-8
   iconv -f ISO-8859-1 -t UTF-8 data/file.json > data/file_utf8.json
   ```

## Configuration Issues

### Extension Not Loading

**Problem**: Directive not recognized

```
WARNING: Unknown directive type "jsontable"
```

**Solution**: Check Sphinx configuration

```python
# conf.py
extensions = [
    'sphinxcontrib.jsontable',  # ← Make sure this is present
    # ... other extensions
]
```

### Cache Problems

**Problem**: Changes not showing up in builds

**Solutions**:

1. **Clear Sphinx cache**:
   ```bash
   # Remove build cache
   rm -rf _build/
   rm -rf .doctrees/
   
   # Rebuild
   sphinx-build -b html . _build/html
   ```

2. **Disable caching temporarily**:
   ```python
   # conf.py
   jsontable_enable_caching = False
   ```

## Error Message Decoder

### Understanding Common Errors

| Error Message | What It Means | Quick Fix |
|---------------|---------------|-----------|
| `FileNotFoundError` | File path is wrong | Check file location |
| `JSONDecodeError` | Invalid JSON syntax | Validate JSON format |
| `PermissionError` | Can't read file | Check file permissions |
| `KeyError: 'sheet'` | Excel sheet not found | Use `:sheet:` option |
| `MemoryError` | File too large | Add `:limit:` option |
| `UnicodeDecodeError` | Encoding problem | Set correct encoding |

### Debug Mode

**Enable detailed error messages**:

```python
# conf.py
jsontable_debug_mode = True
jsontable_verbose_errors = True
```

**This provides**:
- Detailed file processing information
- Performance timing data
- Cache hit/miss information
- Memory usage statistics

## Getting Help

### Before Asking for Help

1. **Check this troubleshooting guide** ✓
2. **Try with a smaller/simpler file** to isolate the issue
3. **Check Sphinx build output** for specific error messages
4. **Verify file paths and permissions**

### Information to Include

When reporting issues, please include:

```markdown
**System Information:**
- Operating System: (Windows/macOS/Linux)
- Python version: `python --version`
- Sphinx version: `sphinx-build --version`
- sphinxcontrib-jsontable version: `pip show sphinxcontrib-jsontable`

**File Information:**
- File type: (JSON/Excel .xlsx/.xls)
- File size: `ls -lh your_file.xlsx`
- Sample directive that's failing

**Error Message:**
(Exact error message from Sphinx build)
```

### Where to Get Help

- **GitHub Issues**: [Report bugs or ask questions](https://github.com/sasakama-code/sphinxcontrib-jsontable/issues)
- **Documentation**: [Complete guide](../README.md)
- **Examples**: [Working samples](../examples/index.rst)

## Prevention Tips

### Best Practices to Avoid Issues

1. **Always use `:header:`** unless you specifically don't want headers
2. **Start with small limits** (`:limit: 50`) and increase as needed
3. **Use relative file paths** from your Sphinx source directory
4. **Test with small files first** before processing large datasets
5. **Check file formats** - ensure JSON is valid and Excel files aren't corrupted
6. **Monitor build times** - if builds suddenly slow down, check recent file additions

### File Organization

```
docs/
├── conf.py
├── index.rst
└── data/
    ├── small_samples/     # Test files < 1MB
    ├── medium_data/       # Files 1-10MB  
    ├── large_datasets/    # Files > 10MB (use with limits)
    └── processed/         # Pre-processed smaller versions
```

---

> **💡 Pro Tip**: Most issues are solved by adding `:header:` and `:limit:` options. When in doubt, start simple and add complexity gradually!