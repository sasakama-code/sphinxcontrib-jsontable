# Excel Advanced Features Guide

## Overview

sphinxcontrib-jsontable provides comprehensive Excel processing with 36+ advanced methods including intelligent range detection, merged cell handling, and enterprise-grade security features.

## Sheet Selection

### By Sheet Name
```rst
.. jsontable:: data/quarterly_report.xlsx
   :header:
   :sheet: "Q3 Results"
```

### By Sheet Index (0-based)
```rst
.. jsontable:: data/workbook.xlsx
   :header:
   :sheet: 0  # First sheet
```

### Multiple Sheets (Advanced)
```rst
.. jsontable:: data/annual_report.xlsx
   :header:
   :sheet: "Summary"  # Process specific summary sheet
   
.. jsontable:: data/annual_report.xlsx
   :header:
   :sheet: "Details"  # Process detailed data sheet
```

## Range Specification

### Basic Ranges
```rst
.. jsontable:: data/sales_data.xlsx
   :header:
   :range: "A1:D10"  # Cells A1 through D10
```

### Dynamic Ranges
```rst
.. jsontable:: data/report.xlsx
   :header:
   :range: "B2:F50"    # Skip column A, start from row 2
   :skip-rows: "0,1"   # Skip first two rows of the range
```

### Large Range Optimization
```rst
.. jsontable:: data/massive_sheet.xlsx
   :header:
   :range: "A1:Z100"   # Specify exact range for performance
   :limit: 50          # Display limit for readability
```

## Header Row Configuration

### Automatic Header Detection
```rst
.. jsontable:: data/auto_headers.xlsx
   :header:  # Automatically detects header row
```

### Specific Header Row
```rst
.. jsontable:: data/complex_structure.xlsx
   :header:
   :header-row: 3  # Use row 3 (0-based) as headers
```

### Custom Header Processing
```rst
.. jsontable:: data/normalized_headers.xlsx
   :header:
   :header-row: 0
   # Headers automatically normalized (spaces→underscores, etc.)
```

## Row Skipping (Advanced Patterns)

### Simple Row Skips
```rst
.. jsontable:: data/report_with_notes.xlsx
   :header:
   :skip-rows: "0,1,2"  # Skip first 3 rows
```

### Range-based Skipping
```rst
.. jsontable:: data/complex_layout.xlsx
   :header:
   :skip-rows: "0-5,10,15-20"  # Skip rows 0-5, row 10, and rows 15-20
```

### Pattern-based Skipping
```rst
.. jsontable:: data/formatted_report.xlsx
   :header:
   :skip-rows: "0-2,total,summary"  # Skip rows + rows containing keywords
```

## Merged Cell Processing

### Expand Mode (Recommended)
```rst
.. jsontable:: data/merged_cells.xlsx
   :header:
   :merge-mode: "expand"  # Duplicate merged cell value to all cells
```

**Use case**: When merged cells represent categories or groups

### First Mode
```rst
.. jsontable:: data/quarterly_data.xlsx
   :header:
   :merge-mode: "first"   # Use only the first cell's value
```

**Use case**: When merged cells are just formatting

### Skip Mode
```rst
.. jsontable:: data/report_with_merges.xlsx
   :header:
   :merge-mode: "skip"    # Skip rows containing merged cells
```

**Use case**: When merged cells contain non-data content

## Automatic Range Detection

### Smart Data Boundary Detection
```rst
.. jsontable:: data/variable_size.xlsx
   :header:
   # Automatically detects actual data boundaries
   # Ignores empty rows/columns at edges
```

### Range Detection with Hints
```rst
.. jsontable:: data/large_sheet.xlsx
   :header:
   :range-hint: "A1:Z100"  # Provides hint for faster detection
```

## Security Features

### External Link Protection
```rst
.. jsontable:: data/external_links.xlsx
   :header:
   # Automatically blocks external links for security
```

### Macro Security
```rst
.. jsontable:: data/macro_file.xlsm
   :header:
   # Safely processes macro-enabled files (macros are not executed)
```

### File Validation
```rst
.. jsontable:: data/suspicious_file.xlsx
   :header:
   # Built-in validation prevents malicious file processing
```

## Complex Real-World Examples

### Financial Reports
```rst
Quarterly Financial Summary
===========================

.. jsontable:: data/q3_financials.xlsx
   :header:
   :sheet: "P&L Statement"
   :range: "A5:H25"        # Skip header sections
   :skip-rows: "0-2"       # Skip report title rows
   :merge-mode: "expand"   # Handle merged category headers
   :limit: 15              # Show top 15 line items
```

### Survey Data with Complex Structure
```rst
Customer Survey Results
=======================

.. jsontable:: data/survey_2024.xlsx
   :header:
   :sheet: "Processed Data"
   :range: "B3:M500"          # Skip ID column, start from data
   :header-row: 0             # First row has question headers
   :skip-rows: "0,1,summary"  # Skip intro rows and summary rows
   :limit: 100                # Show first 100 responses
```

### Multi-Sheet Data Consolidation
```rst
Regional Sales Performance
==========================

**North Region:**

.. jsontable:: data/regional_sales.xlsx
   :header:
   :sheet: "North"
   :range: "A1:F20"
   :limit: 10

**South Region:**

.. jsontable:: data/regional_sales.xlsx
   :header:
   :sheet: "South" 
   :range: "A1:F20"
   :limit: 10

**Consolidated Summary:**

.. jsontable:: data/regional_sales.xlsx
   :header:
   :sheet: "Summary"
   :merge-mode: "expand"
```

## Performance Optimization for Excel

### Large Excel Files (>10MB)
```rst
.. jsontable:: data/huge_dataset.xlsx
   :header:
   :sheet: "Summary"           # Use summary sheets when available
   :range: "A1:K100"          # Limit range for performance
   :limit: 50                 # Cap displayed rows
   :merge-mode: "first"       # Fastest merge processing
```

### Memory-Efficient Processing
```rst
.. jsontable:: data/memory_intensive.xlsx
   :header:
   :range: "A1:E50"           # Process in smaller chunks
   :skip-rows: "0-5"          # Skip unnecessary data
   :limit: 25                 # Small display limit
```

### Cache-Friendly Configuration
```rst
.. jsontable:: data/frequently_accessed.xlsx
   :header:
   :sheet: "Data"
   # This file will be cached automatically for repeat access
   # Subsequent builds will be much faster
```

## Error Handling and Troubleshooting

### Common Issues and Solutions

#### "Sheet not found"
```rst
# Problem: Sheet name doesn't exist
.. jsontable:: data/report.xlsx
   :sheet: "NonExistent"

# Solution: Check available sheet names or use index
.. jsontable:: data/report.xlsx
   :sheet: 0  # Use first sheet instead
```

#### "Range outside worksheet bounds"
```rst
# Problem: Range too large for actual data
.. jsontable:: data/small_file.xlsx
   :range: "A1:Z1000"  # File only has 50 rows

# Solution: Use auto-detection or smaller range
.. jsontable:: data/small_file.xlsx
   :header:  # Let auto-detection find the right range
```

#### "Merged cells causing issues"
```rst
# Problem: Complex merged cell structure
.. jsontable:: data/complex_merges.xlsx
   :header:

# Solution: Try different merge modes
.. jsontable:: data/complex_merges.xlsx
   :header:
   :merge-mode: "skip"  # Skip problematic merged areas
```

### Performance Warnings

#### "Large dataset detected"
```
WARNING: Large dataset detected (15,000 rows). Showing first 1,000 rows for performance.
```

**Solutions:**
1. Add explicit limit: `:limit: 200`
2. Use range specification: `:range: "A1:E100"`
3. Process summary sheets instead of raw data

#### "Complex merged cell structure"
```
INFO: Complex merged cells detected. Using 'expand' mode for best results.
```

**Action**: The system automatically optimizes. Consider `:merge-mode: "first"` for faster processing if data permits.

## Integration Examples

### With Sphinx Cross-References
```rst
Sales Data Analysis
===================

The following table shows data from our :download:`Q3 sales report <data/q3_sales.xlsx>`:

.. jsontable:: data/q3_sales.xlsx
   :header:
   :sheet: "Monthly Summary"
   :limit: 12

For detailed methodology, see :ref:`analysis-methods`.
```

### With Conditional Content
```rst
.. only:: html

   Interactive Sales Dashboard
   ===========================
   
   .. jsontable:: data/dashboard_data.xlsx
      :header:
      :limit: 25

.. only:: latex

   Sales Summary (Print Version)
   =============================
   
   .. jsontable:: data/dashboard_data.xlsx
      :header:
      :limit: 10
      :range: "A1:E15"  # Smaller range for print
```

## Best Practices Summary

### ✅ Recommended Patterns
- Start with `:header:` and auto-detection
- Use `:sheet:` names rather than indices when possible
- Apply `:limit:` for large datasets
- Specify `:range:` for performance on large files
- Use `:merge-mode: "expand"` for categorized data

### ⚠️ Use with Caution
- Very large ranges without limits
- `:merge-mode: "skip"` (may remove important data)
- Processing all sheets from large multi-sheet files
- `:limit: 0` on unknown data size

### 🚀 Performance Tips
- Use summary sheets for large workbooks
- Cache frequently accessed files
- Combine `:range:` and `:limit:` for optimal performance
- Monitor processing times and adjust accordingly

---

> **💡 Pro Tip**: The advanced Excel features are designed to handle real-world business files. Start simple with `:header:` and add options as needed. The built-in optimizations will handle the heavy lifting!