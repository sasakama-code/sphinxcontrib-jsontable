# User-Friendly Error Examples

## Overview

This document demonstrates the enhanced error experience in sphinxcontrib-jsontable (Phase 3 UX improvements). The system now provides user-friendly error messages with automatic resolution guidance.

## Before and After Comparison

### Traditional Error Messages (Before)
```
ERROR: FileNotFoundError: [Errno 2] No such file or directory: 'data/missing.xlsx'
```

### Enhanced Error Messages (After)
```
❌ 📁 File not found: 'data/missing.xlsx'

🔧 Quick Solutions:
   1. Check if 'data/missing.xlsx' exists with: `ls data/missing.xlsx`
   2. Use relative paths like: `data/your_file.xlsx` instead of absolute paths
   3. Place Excel files in a `data/` subdirectory for organization

📋 Step-by-step guide:
   1. 🔍 Check if the file path is correct
   2. 📂 Verify the file exists in your project directory
   3. 📝 Ensure the file path is relative to your docs source directory
   4. 🔄 Try using a different file path format

⏱️ Estimated fix time: 2-5 minutes

📚 Helpful guides:
   • File organization guide: docs/troubleshooting_guide.md#file-not-found-errors
   • Best practices: docs/README.md#file-organization-best-practices
```

## Real-World Error Scenarios

### 1. Excel File Not Found

**Directive:**
```rst
.. jsontable:: reports/quarterly_data.xlsx
   :header:
```

**Enhanced Error Message:**
```
❌ 📁 File not found: 'reports/quarterly_data.xlsx'

🔧 Quick Solutions:
   1. Check if 'reports/quarterly_data.xlsx' exists with: `ls reports/quarterly_data.xlsx`
   2. Use relative paths like: `data/your_file.xlsx` instead of absolute paths
   3. Place Excel files in a `data/` subdirectory for organization

⏱️ Estimated fix time: 2-5 minutes
```

### 2. Excel Sheet Not Found

**Directive:**
```rst
.. jsontable:: data/financial_report.xlsx
   :header:
   :sheet: "Q4 Results"
```

**Enhanced Error Message:**
```
❌ 📊 Excel sheet 'Q4 Results' not found

🔧 Quick Solutions:
   1. Available sheets: Summary, Q1 Data, Q2 Data, Q3 Data, Annual Overview
   2. Use `:sheet: 0` for first sheet (index-based)
   3. Remove `:sheet:` option to use default sheet
   4. Did you mean: 'Q3 Data'?

📋 Step-by-step guide:
   1. 📋 Check available sheet names in your Excel file
   2. ✏️ Fix the sheet name in your directive
   3. 🔢 Alternatively, use sheet index (0-based) instead
   4. 📁 Verify you're using the correct Excel file

⏱️ Estimated fix time: 1-3 minutes
```

### 3. Invalid Range Specification

**Directive:**
```rst
.. jsontable:: data/large_dataset.xlsx
   :header:
   :range: "ZZ1:AAA9999"
```

**Enhanced Error Message:**
```
❌ 📐 Invalid Excel range: 'ZZ1:AAA9999'

🔧 Quick Solutions:
   1. Try: `:range: A1:E20` for a basic range
   2. Remove `:range:` option to auto-detect data boundaries
   3. Use `:limit: 50` instead of range for large files

📋 Step-by-step guide:
   1. ✅ Check range format (should be like 'A1:D10')
   2. 📊 Verify range is within sheet boundaries
   3. 🔄 Try using a smaller range first
   4. 📱 Remove range option to auto-detect data
   5. 📏 Range extends beyond column Z - verify this is intended
   6. 📊 Large row range detected - consider using `:limit:` instead

⏱️ Estimated fix time: 2-5 minutes
```

### 4. Security Validation Error

**Directive:**
```rst
.. jsontable:: data/macro_enabled_file.xlsm
   :header:
```

**Enhanced Error Message:**
```
❌ 🔒 Security validation failed: 2 issues detected

🔧 Quick Solutions:
   1. Save Excel file as .xlsx format (removes macros)
   2. Use file from a trusted source
   3. High priority issues: 1

📋 Step-by-step guide:
   1. 🛡️ Review detected security issues
   2. 🧹 Clean or recreate the Excel file without macros
   3. 💾 Save as .xlsx format instead of .xlsm
   4. ⚙️ Adjust security settings if file is trusted

⏱️ Estimated fix time: 5-15 minutes
```

### 5. Skip Rows Out of Range

**Directive:**
```rst
.. jsontable:: data/small_file.xlsx
   :header:
   :skip-rows: "0,1,2,15,20"
```

**Enhanced Error Message:**
```
❌ 📍 Skip row specification is out of range

🔧 Quick Solutions:
   1. Reduce skip-rows numbers (e.g., `:skip-rows: 0,1,2`)
   2. Remove `:skip-rows:` option temporarily
   3. Check file has enough rows for your skip specification

📋 Step-by-step guide:
   1. 🔢 Check your `:skip-rows:` values
   2. 📊 Verify row numbers are within data range
   3. 📱 Use smaller row numbers for testing
   4. 🔄 Try without skip-rows first

⏱️ Estimated fix time: 2-5 minutes
```

### 6. Permission Denied

**Directive:**
```rst
.. jsontable:: /restricted/confidential.xlsx
   :header:
```

**Enhanced Error Message:**
```
❌ 🔒 Permission denied accessing file: '/restricted/confidential.xlsx'

🔧 Quick Solutions:
   1. Fix permissions: `chmod 644 /restricted/confidential.xlsx`
   2. Ensure file is readable by your user account

📋 Step-by-step guide:
   1. 🔐 Check file permissions with: `ls -la /restricted/confidential.xlsx`
   2. 🛠️ Fix permissions with: `chmod 644 /restricted/confidential.xlsx`
   3. 👤 Ensure you have read access to the file
   4. 📁 Check parent directory permissions

⏱️ Estimated fix time: 1-2 minutes
```

## Features of Enhanced Error Experience

### 🎯 User-Friendly Messages
- Clear, non-technical language
- Emoji indicators for quick visual scanning
- Context-aware explanations

### 🔧 Automatic Resolution Guidance
- Immediate quick fixes
- Step-by-step resolution guides
- Estimated fix times

### 📚 Smart Documentation Links
- Context-relevant documentation references
- Direct links to troubleshooting guides
- Best practice recommendations

### 🔍 Intelligent Error Analysis
- Fuzzy matching for sheet names
- Range specification validation
- File context analysis

### ⏱️ Time Estimates
- Realistic fix time estimates
- Complexity-based categorization
- User planning assistance

## Error Categories and Response Times

| Error Type | Typical Fix Time | Complexity |
|------------|-----------------|------------|
| File not found | 2-5 minutes | Low |
| Permission issues | 1-2 minutes | Low |
| Sheet name errors | 1-3 minutes | Low |
| Range specification | 2-5 minutes | Medium |
| Data conversion | 5-10 minutes | Medium |
| Security validation | 5-15 minutes | High |
| Generic errors | 5-15 minutes | Variable |

## Implementation Details

The enhanced error experience is implemented through:

1. **UserFriendlyErrorHandler**: Core class providing user-friendly error processing
2. **Enhanced DirectiveCore**: Integration with existing directive error handling
3. **Context-Aware Analysis**: File and configuration analysis for better guidance
4. **Fallback Compatibility**: Maintains backward compatibility with legacy error handling

## Benefits for Users

### 📈 Improved Productivity
- Faster problem resolution
- Reduced documentation reading time
- Clear next steps

### 🎓 Learning Experience
- Educational error messages
- Best practice guidance
- Prevention tips

### 😊 Better User Experience
- Less frustration with clear explanations
- Confidence in problem-solving
- Professional error presentation

## Configuration Options

Users can customize the error experience through configuration:

```python
# conf.py
jsontable_ux_enhanced_errors = True  # Enable enhanced errors (default)
jsontable_ux_show_fix_times = True   # Show estimated fix times
jsontable_ux_show_docs_links = True  # Include documentation links
jsontable_ux_error_detail_level = "standard"  # "minimal", "standard", "detailed"
```

---

> **💡 Note**: This enhanced error experience represents Phase 3 of the User Experience improvement initiative, focusing specifically on making error handling more user-friendly and educational.