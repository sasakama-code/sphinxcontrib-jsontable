"""User-Friendly Error Handler - Enhanced user experience error handling.

Implements user-friendly error messages and automatic resolution guidance
for Phase 3 of user experience improvement initiative.

CLAUDE.md Code Excellence Compliance:
- Single Responsibility: User experience error handling only
- DRY Principle: Reuses existing error infrastructure
- SOLID Principles: Extends existing interfaces with UX focus
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from .error_handler_core import ErrorHandlerCore
from .error_types import RecoveryStrategy
from .excel_errors import (
    DataConversionError,
    FileAccessError,
    RangeValidationError,
    SecurityValidationError,
    WorksheetNotFoundError,
)


class UserFriendlyErrorHandler(ErrorHandlerCore):
    """Enhanced error handler with user-friendly messages and automatic resolution guidance.
    
    Provides comprehensive user experience improvements including:
    - Plain language error explanations
    - Step-by-step resolution guidance
    - Context-aware suggestions
    - Performance optimization hints
    """

    def __init__(
        self,
        default_strategy: RecoveryStrategy = RecoveryStrategy.GRACEFUL_DEGRADATION,
        enable_logging: bool = True,
        logger_name: str = "sphinxcontrib.jsontable.errors.ux",
    ):
        """Initialize user-friendly error handler."""
        super().__init__(default_strategy, enable_logging, logger_name)
        
        # User-friendly error message templates
        self.user_messages = {
            FileAccessError: self._handle_file_access_error,
            WorksheetNotFoundError: self._handle_worksheet_not_found_error,
            RangeValidationError: self._handle_range_validation_error,
            SecurityValidationError: self._handle_security_validation_error,
            DataConversionError: self._handle_data_conversion_error,
            ValueError: self._handle_value_error,
            TypeError: self._handle_type_error,
            Exception: self._handle_generic_error,
        }

    def create_user_friendly_response(
        self, error: Exception, context: Optional[str] = None, file_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create user-friendly error response with resolution guidance."""
        # Get handler for this error type
        handler = self._get_error_handler(error)
        
        # Generate user-friendly content
        user_content = handler(error, context, file_path)
        
        # Create enhanced response
        response = {
            "error": True,
            "error_type": type(error).__name__,
            "technical_message": str(error),
            "user_friendly_message": user_content["message"],
            "resolution_steps": user_content["steps"],
            "quick_fixes": user_content["quick_fixes"],
            "prevention_tips": user_content["prevention"],
            "documentation_links": user_content["docs"],
            "context": context or "Excel processing",
            "severity": self._determine_severity(error).value,
            "estimated_fix_time": user_content["fix_time"],
        }
        
        if file_path:
            response["file_path"] = file_path
            response["file_context"] = self._analyze_file_context(file_path)
        
        return response

    def _get_error_handler(self, error: Exception):
        """Get appropriate error handler for the error type."""
        error_type = type(error)
        
        # Check exact match first
        if error_type in self.user_messages:
            return self.user_messages[error_type]
        
        # Check inheritance hierarchy
        for mapped_type, handler in self.user_messages.items():
            if isinstance(error, mapped_type):
                return handler
        
        # Default to generic handler
        return self.user_messages[Exception]

    def _handle_file_access_error(
        self, error: Exception, context: Optional[str], file_path: Optional[str]
    ) -> Dict[str, Any]:
        """Handle file access errors with user-friendly guidance."""
        if hasattr(error, 'file_path'):
            problem_file = error.file_path
        else:
            problem_file = file_path or "unknown file"
        
        # Analyze the specific issue
        if "not found" in str(error).lower() or "no such file" in str(error).lower():
            return {
                "message": f"📁 File not found: '{problem_file}'",
                "steps": [
                    "1. 🔍 Check if the file path is correct",
                    "2. 📂 Verify the file exists in your project directory",
                    "3. 📝 Ensure the file path is relative to your docs source directory",
                    "4. 🔄 Try using a different file path format",
                ],
                "quick_fixes": [
                    f"Check if '{problem_file}' exists with: `ls {problem_file}`",
                    "Use relative paths like: `data/your_file.xlsx` instead of absolute paths",
                    "Place Excel files in a `data/` subdirectory for organization",
                ],
                "prevention": [
                    "Always use relative paths from your Sphinx source directory",
                    "Organize data files in a consistent directory structure",
                    "Use descriptive filenames to avoid confusion",
                ],
                "docs": [
                    "File organization guide: docs/troubleshooting_guide.md#file-not-found-errors",
                    "Best practices: docs/README.md#file-organization-best-practices",
                ],
                "fix_time": "2-5 minutes",
            }
        elif "permission" in str(error).lower():
            return {
                "message": f"🔒 Permission denied accessing file: '{problem_file}'",
                "steps": [
                    "1. 🔐 Check file permissions with: `ls -la {problem_file}`",
                    "2. 🛠️ Fix permissions with: `chmod 644 {problem_file}`",
                    "3. 👤 Ensure you have read access to the file",
                    "4. 📁 Check parent directory permissions",
                ],
                "quick_fixes": [
                    f"Fix permissions: `chmod 644 {problem_file}`",
                    "Ensure file is readable by your user account",
                ],
                "prevention": [
                    "Set appropriate file permissions when adding new files",
                    "Avoid using files from restricted directories",
                ],
                "docs": [
                    "File permissions guide: docs/troubleshooting_guide.md#file-permissions",
                ],
                "fix_time": "1-2 minutes",
            }
        else:
            return {
                "message": f"⚠️ Cannot access file: '{problem_file}'",
                "steps": [
                    "1. 🔍 Verify the file exists and is readable",
                    "2. 📂 Check file path and permissions",
                    "3. 🔄 Try copying the file to your docs directory",
                    "4. 📝 Ensure the file isn't corrupted",
                ],
                "quick_fixes": [
                    "Try a different file path format",
                    "Copy file to docs/data/ directory",
                ],
                "prevention": [
                    "Test file access before adding to documentation",
                    "Use consistent file organization",
                ],
                "docs": [
                    "Troubleshooting guide: docs/troubleshooting_guide.md",
                ],
                "fix_time": "3-10 minutes",
            }

    def _handle_worksheet_not_found_error(
        self, error: Exception, context: Optional[str], file_path: Optional[str]
    ) -> Dict[str, Any]:
        """Handle worksheet not found errors."""
        sheet_name = getattr(error, 'sheet_name', 'unknown')
        available_sheets = getattr(error, 'available_sheets', [])
        
        # Generate suggestions based on available sheets
        suggestions = []
        if available_sheets:
            # Find close matches
            close_matches = self._find_close_sheet_matches(sheet_name, available_sheets)
            if close_matches:
                suggestions.extend([f"Did you mean: '{match}'?" for match in close_matches])
        
        return {
            "message": f"📊 Excel sheet '{sheet_name}' not found",
            "steps": [
                "1. 📋 Check available sheet names in your Excel file",
                "2. ✏️ Fix the sheet name in your directive",
                "3. 🔢 Alternatively, use sheet index (0-based) instead",
                "4. 📁 Verify you're using the correct Excel file",
            ],
            "quick_fixes": [
                f"Available sheets: {', '.join(available_sheets)}" if available_sheets else "Check Excel file sheets",
                "Use `:sheet: 0` for first sheet (index-based)",
                "Remove `:sheet:` option to use default sheet",
            ] + suggestions,
            "prevention": [
                "Use sheet names exactly as they appear in Excel",
                "Consider using sheet index (0-based) for reliability",
                "Double-check sheet names for typos and extra spaces",
            ],
            "docs": [
                "Sheet selection guide: docs/excel_advanced_features.md#sheet-selection",
                "Troubleshooting: docs/troubleshooting_guide.md#sheet-not-found",
            ],
            "fix_time": "1-3 minutes",
        }

    def _handle_range_validation_error(
        self, error: Exception, context: Optional[str], file_path: Optional[str]
    ) -> Dict[str, Any]:
        """Handle range validation errors."""
        range_spec = getattr(error, 'range_spec', 'unknown range')
        
        # Analyze range specification issues
        range_issues = self._analyze_range_specification(range_spec)
        
        return {
            "message": f"📐 Invalid Excel range: '{range_spec}'",
            "steps": [
                "1. ✅ Check range format (should be like 'A1:D10')",
                "2. 📊 Verify range is within sheet boundaries",
                "3. 🔄 Try using a smaller range first",
                "4. 📱 Remove range option to auto-detect data",
            ] + range_issues["steps"],
            "quick_fixes": [
                "Try: `:range: A1:E20` for a basic range",
                "Remove `:range:` option to auto-detect data boundaries",
                "Use `:limit: 50` instead of range for large files",
            ] + range_issues["fixes"],
            "prevention": [
                "Test ranges with small data first",
                "Use Excel format (A1:D10) not RC format",
                "Consider auto-detection for variable data sizes",
            ],
            "docs": [
                "Range specification guide: docs/excel_advanced_features.md#range-specification",
                "Troubleshooting: docs/troubleshooting_guide.md#range-outside-bounds",
            ],
            "fix_time": "2-5 minutes",
        }

    def _handle_security_validation_error(
        self, error: Exception, context: Optional[str], file_path: Optional[str]
    ) -> Dict[str, Any]:
        """Handle security validation errors."""
        security_issues = getattr(error, 'security_issues', [])
        high_severity = getattr(error, 'get_high_severity_issues', lambda: [])()
        
        return {
            "message": f"🔒 Security validation failed: {len(security_issues)} issues detected",
            "steps": [
                "1. 🛡️ Review detected security issues",
                "2. 🧹 Clean or recreate the Excel file without macros",
                "3. 💾 Save as .xlsx format instead of .xlsm",
                "4. ⚙️ Adjust security settings if file is trusted",
            ],
            "quick_fixes": [
                "Save Excel file as .xlsx format (removes macros)",
                "Use file from a trusted source",
                f"High priority issues: {len(high_severity)}" if high_severity else "Review all security issues",
            ],
            "prevention": [
                "Use .xlsx format instead of macro-enabled formats",
                "Verify Excel files from external sources",
                "Keep security settings at recommended levels",
            ],
            "docs": [
                "Security guide: docs/excel_advanced_features.md#security-features",
                "File validation: docs/troubleshooting_guide.md#security-considerations",
            ],
            "fix_time": "5-15 minutes",
        }

    def _handle_data_conversion_error(
        self, error: Exception, context: Optional[str], file_path: Optional[str]
    ) -> Dict[str, Any]:
        """Handle data conversion errors."""
        conversion_stage = getattr(error, 'conversion_stage', 'unknown stage')
        
        return {
            "message": f"🔄 Data conversion failed at: {conversion_stage}",
            "steps": [
                "1. 📊 Check for merged cells in your Excel data",
                "2. 🧹 Clean up data formatting in Excel",
                "3. ⚙️ Try different merge cell handling options",
                "4. 📱 Use a smaller data range for testing",
            ],
            "quick_fixes": [
                "Add `:merge-cells: expand` to handle merged cells",
                "Try `:limit: 20` to process smaller amount of data",
                "Use `:range: A1:E20` to focus on specific data area",
            ],
            "prevention": [
                "Ensure consistent data formatting in Excel",
                "Avoid complex merged cell structures",
                "Test with small data samples first",
            ],
            "docs": [
                "Data handling: docs/excel_advanced_features.md#merged-cell-processing",
                "Troubleshooting: docs/troubleshooting_guide.md#merged-cells-causing-issues",
            ],
            "fix_time": "5-10 minutes",
        }

    def _handle_value_error(
        self, error: Exception, context: Optional[str], file_path: Optional[str]
    ) -> Dict[str, Any]:
        """Handle generic value errors with context-specific guidance."""
        error_msg = str(error).lower()
        
        if "skip row" in error_msg and "out of range" in error_msg:
            return {
                "message": "📍 Skip row specification is out of range",
                "steps": [
                    "1. 🔢 Check your `:skip-rows:` values",
                    "2. 📊 Verify row numbers are within data range",
                    "3. 📱 Use smaller row numbers for testing",
                    "4. 🔄 Try without skip-rows first",
                ],
                "quick_fixes": [
                    "Reduce skip-rows numbers (e.g., `:skip-rows: 0,1,2`)",
                    "Remove `:skip-rows:` option temporarily",
                    "Check file has enough rows for your skip specification",
                ],
                "prevention": [
                    "Verify data size before specifying skip rows",
                    "Use conservative row skip values",
                    "Test with small datasets first",
                ],
                "docs": [
                    "Row skipping guide: docs/excel_advanced_features.md#row-skipping-advanced-patterns",
                ],
                "fix_time": "2-5 minutes",
            }
        elif "header row" in error_msg:
            return {
                "message": "📋 Header row specification issue",
                "steps": [
                    "1. 🔢 Check `:header-row:` value is correct",
                    "2. 📊 Verify header row exists in your data",
                    "3. 🔄 Try auto-detection by removing option",
                    "4. 📱 Test with `:header-row: 0` for first row",
                ],
                "quick_fixes": [
                    "Use `:header-row: 0` for first row",
                    "Remove `:header-row:` to auto-detect",
                    "Check if your file actually has headers",
                ],
                "prevention": [
                    "Verify header row exists before specifying",
                    "Use 0-based row indexing",
                    "Let auto-detection work when possible",
                ],
                "docs": [
                    "Header configuration: docs/excel_advanced_features.md#header-row-configuration",
                ],
                "fix_time": "1-3 minutes",
            }
        else:
            return self._handle_generic_error(error, context, file_path)

    def _handle_type_error(
        self, error: Exception, context: Optional[str], file_path: Optional[str]
    ) -> Dict[str, Any]:
        """Handle type errors with user-friendly explanations."""
        return {
            "message": "🔧 Data type mismatch in processing",
            "steps": [
                "1. 📊 Check data format in your Excel file",
                "2. 🧹 Ensure consistent data types in columns",
                "3. ⚙️ Verify directive options are correct format",
                "4. 📱 Try with simpler data first",
            ],
            "quick_fixes": [
                "Use string values for directive options",
                "Check option format (e.g., `:limit: 50` not `:limit: \"50\"`)",
                "Ensure Excel data has consistent formatting",
            ],
            "prevention": [
                "Use consistent data formats in Excel",
                "Follow directive option format guidelines",
                "Test with simple data structures first",
            ],
            "docs": [
                "Option reference: docs/excel_advanced_features.md#excel-options-reference",
                "Troubleshooting: docs/troubleshooting_guide.md",
            ],
            "fix_time": "3-8 minutes",
        }

    def _handle_generic_error(
        self, error: Exception, context: Optional[str], file_path: Optional[str]
    ) -> Dict[str, Any]:
        """Handle generic errors with general guidance."""
        return {
            "message": f"⚠️ Unexpected error in {context or 'Excel processing'}",
            "steps": [
                "1. 🔍 Check the technical error message below",
                "2. 📊 Verify your Excel file is not corrupted",
                "3. 📱 Try with a simpler example first",
                "4. 🔄 Check all directive options are valid",
            ],
            "quick_fixes": [
                "Try with `:header:` option only (remove other options)",
                "Test with a small, simple Excel file",
                "Check file is not corrupted or password-protected",
            ],
            "prevention": [
                "Test with simple files before complex ones",
                "Use recommended directive option combinations",
                "Keep Excel files in standard formats",
            ],
            "docs": [
                "Getting started: docs/getting_started.md",
                "Troubleshooting guide: docs/troubleshooting_guide.md",
                "Examples: docs/quick_examples.py",
            ],
            "fix_time": "5-15 minutes",
        }

    def _find_close_sheet_matches(self, target: str, available: List[str]) -> List[str]:
        """Find close matches for sheet names using fuzzy matching."""
        if not available:
            return []
        
        # Simple fuzzy matching based on edit distance and common patterns
        matches = []
        target_lower = target.lower()
        
        for sheet in available:
            sheet_lower = sheet.lower()
            
            # Exact match (case insensitive)
            if target_lower == sheet_lower:
                matches.append(sheet)
                continue
            
            # Substring match
            if target_lower in sheet_lower or sheet_lower in target_lower:
                matches.append(sheet)
                continue
            
            # Common word match
            target_words = set(re.findall(r'\w+', target_lower))
            sheet_words = set(re.findall(r'\w+', sheet_lower))
            if target_words & sheet_words:  # Intersection
                matches.append(sheet)
        
        return matches[:3]  # Return top 3 matches

    def _analyze_range_specification(self, range_spec: str) -> Dict[str, Any]:
        """Analyze range specification for common issues."""
        steps = []
        fixes = []
        
        if not re.match(r'^[A-Z]+\d+:[A-Z]+\d+$', range_spec.upper()):
            steps.append("5. ✅ Use Excel format: 'A1:D10' not 'R1C1:R10C4'")
            fixes.append("Example: `:range: A1:E20`")
        
        # Check for obviously large ranges
        if ':' in range_spec:
            try:
                start, end = range_spec.split(':')
                end_col = re.findall(r'[A-Z]+', end.upper())
                end_row = re.findall(r'\d+', end)
                
                if end_col and ord(end_col[0][0]) - ord('A') > 25:  # Beyond Z
                    steps.append("6. 📏 Range extends beyond column Z - verify this is intended")
                    fixes.append("Try smaller range like `:range: A1:K50`")
                
                if end_row and int(end_row[0]) > 1000:
                    steps.append("7. 📊 Large row range detected - consider using `:limit:` instead")
                    fixes.append("Use `:limit: 100` instead of large range")
            except:
                steps.append("8. 🔍 Range format appears incorrect")
                fixes.append("Use format like `:range: A1:E20`")
        
        return {"steps": steps, "fixes": fixes}

    def _analyze_file_context(self, file_path: str) -> Dict[str, Any]:
        """Analyze file context for better error guidance."""
        try:
            path = Path(file_path)
            
            context = {
                "exists": path.exists(),
                "size": path.stat().st_size if path.exists() else 0,
                "extension": path.suffix.lower(),
                "directory": str(path.parent),
            }
            
            # Add size-based recommendations
            if context["size"] > 10 * 1024 * 1024:  # > 10MB
                context["recommendations"] = [
                    "Large file detected - consider using `:limit:` option",
                    "Use `:range:` to process specific sections",
                ]
            elif context["size"] == 0:
                context["recommendations"] = [
                    "File appears empty - verify correct file",
                ]
            
            return context
        except:
            return {"analysis_failed": True}