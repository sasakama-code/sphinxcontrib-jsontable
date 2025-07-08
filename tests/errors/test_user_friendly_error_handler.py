"""Test User-Friendly Error Handler - UX Phase 3 validation.

Tests for enhanced user experience error handling with automatic resolution guidance.

CLAUDE.md Test Excellence Compliance:
- Comprehensive test coverage for UX improvements
- Real-world error scenarios testing
- User experience validation
"""

from pathlib import Path

import pytest

from sphinxcontrib.jsontable.errors.excel_errors import (
    DataConversionError,
    FileAccessError,
    RangeValidationError,
    SecurityValidationError,
    WorksheetNotFoundError,
)
from sphinxcontrib.jsontable.errors.user_friendly_error_handler import (
    UserFriendlyErrorHandler,
)


class TestUserFriendlyErrorHandler:
    """Test suite for user-friendly error handling functionality."""
    
    @pytest.fixture
    def ux_handler(self):
        """Create user-friendly error handler instance."""
        return UserFriendlyErrorHandler()
    
    def test_file_access_error_not_found(self, ux_handler):
        """Test user-friendly handling of file not found errors."""
        error = FileAccessError(
            "/Users/test/missing_file.xlsx",
            "File not found: /Users/test/missing_file.xlsx"
        )
        
        response = ux_handler.create_user_friendly_response(
            error, context="Excel processing", file_path="/Users/test/missing_file.xlsx"
        )
        
        # Verify user-friendly components
        assert "📁 File not found" in response["user_friendly_message"]
        assert "2-5 minutes" == response["estimated_fix_time"]
        assert len(response["resolution_steps"]) >= 3
        assert len(response["quick_fixes"]) >= 2
        assert "file path is correct" in response["resolution_steps"][0].lower()
        
        # Verify documentation links
        assert len(response["documentation_links"]) > 0
        assert "troubleshooting_guide.md" in response["documentation_links"][0]
    
    def test_file_access_error_permission_denied(self, ux_handler):
        """Test user-friendly handling of permission denied errors."""
        error = FileAccessError(
            "/restricted/file.xlsx",
            "Permission denied: cannot read file"
        )
        
        response = ux_handler.create_user_friendly_response(
            error, context="Excel processing", file_path="/restricted/file.xlsx"
        )
        
        assert "🔒 Permission denied" in response["user_friendly_message"]
        assert "1-2 minutes" == response["estimated_fix_time"]
        assert any("chmod 644" in fix for fix in response["quick_fixes"])
    
    def test_worksheet_not_found_error(self, ux_handler):
        """Test user-friendly handling of worksheet not found errors."""
        error = WorksheetNotFoundError(
            "Results",
            ["Sheet1", "Summary", "Data", "Charts"],
            "Worksheet 'Results' not found. Available sheets: Sheet1, Summary, Data, Charts"
        )
        
        response = ux_handler.create_user_friendly_response(
            error, context="Excel processing"
        )
        
        assert "📊 Excel sheet 'Results' not found" in response["user_friendly_message"]
        assert "1-3 minutes" == response["estimated_fix_time"]
        assert "Available sheets: Sheet1, Summary, Data, Charts" in response["quick_fixes"][0]
        assert any(":sheet: 0" in fix for fix in response["quick_fixes"])
    
    def test_worksheet_close_match_suggestions(self, ux_handler):
        """Test that close sheet name matches are suggested."""
        error = WorksheetNotFoundError(
            "summary",  # lowercase
            ["Sheet1", "Summary", "Data"],  # Mixed case
            "Worksheet 'summary' not found"
        )
        
        response = ux_handler.create_user_friendly_response(error, context="Excel processing")
        
        # Should suggest "Summary" as a close match
        suggestions = [fix for fix in response["quick_fixes"] if "Did you mean" in fix]
        assert len(suggestions) > 0
        assert "Summary" in suggestions[0]
    
    def test_range_validation_error(self, ux_handler):
        """Test user-friendly handling of range validation errors."""
        error = RangeValidationError(
            "ZZ1:AAA9999",
            "Invalid range specification: ZZ1:AAA9999"
        )
        
        response = ux_handler.create_user_friendly_response(
            error, context="Excel processing"
        )
        
        assert "📐 Invalid Excel range" in response["user_friendly_message"]
        assert "2-5 minutes" == response["estimated_fix_time"]
        assert any("A1:E20" in fix for fix in response["quick_fixes"])
        assert any("auto-detect" in fix.lower() for fix in response["quick_fixes"])
    
    def test_security_validation_error(self, ux_handler):
        """Test user-friendly handling of security validation errors."""
        security_issues = [
            {"type": "macro", "severity": "high", "description": "Macro detected"},
            {"type": "external_links", "severity": "medium", "description": "External links found"}
        ]
        
        error = SecurityValidationError(
            security_issues,
            "Security validation failed: 2 security issues detected"
        )
        
        response = ux_handler.create_user_friendly_response(
            error, context="Excel processing"
        )
        
        assert "🔒 Security validation failed: 2 issues detected" in response["user_friendly_message"]
        assert "5-15 minutes" == response["estimated_fix_time"]
        assert any(".xlsx format" in fix for fix in response["quick_fixes"])
    
    def test_data_conversion_error(self, ux_handler):
        """Test user-friendly handling of data conversion errors."""
        error = DataConversionError(
            "merged_cell_processing",
            "Data conversion failed at stage: merged_cell_processing"
        )
        
        response = ux_handler.create_user_friendly_response(
            error, context="Excel processing"
        )
        
        assert "🔄 Data conversion failed at: merged_cell_processing" in response["user_friendly_message"]
        assert "5-10 minutes" == response["estimated_fix_time"]
        assert any("merge-cells: expand" in fix for fix in response["quick_fixes"])
    
    def test_value_error_skip_rows(self, ux_handler):
        """Test user-friendly handling of skip rows value errors."""
        error = ValueError("Skip row 15 is out of range")
        
        response = ux_handler.create_user_friendly_response(
            error, context="Excel processing"
        )
        
        assert "📍 Skip row specification is out of range" in response["user_friendly_message"]
        assert "2-5 minutes" == response["estimated_fix_time"]
        assert any("skip-rows: 0,1,2" in fix for fix in response["quick_fixes"])
    
    def test_value_error_header_row(self, ux_handler):
        """Test user-friendly handling of header row value errors."""
        error = ValueError("Header row 10 is invalid")
        
        response = ux_handler.create_user_friendly_response(
            error, context="Excel processing"
        )
        
        assert "📋 Header row specification issue" in response["user_friendly_message"]
        assert "1-3 minutes" == response["estimated_fix_time"]
        assert any("header-row: 0" in fix for fix in response["quick_fixes"])
    
    def test_type_error_handling(self, ux_handler):
        """Test user-friendly handling of type errors."""
        error = TypeError("Expected string, got int")
        
        response = ux_handler.create_user_friendly_response(
            error, context="Excel processing"
        )
        
        assert "🔧 Data type mismatch in processing" in response["user_friendly_message"]
        assert "3-8 minutes" == response["estimated_fix_time"]
        assert any("string values" in fix for fix in response["quick_fixes"])
    
    def test_generic_error_handling(self, ux_handler):
        """Test user-friendly handling of generic errors."""
        error = RuntimeError("Unexpected error occurred")
        
        response = ux_handler.create_user_friendly_response(
            error, context="Excel processing"
        )
        
        assert "⚠️ Unexpected error in Excel processing" in response["user_friendly_message"]
        assert "5-15 minutes" == response["estimated_fix_time"]
        assert any(":header:" in fix for fix in response["quick_fixes"])
    
    def test_range_analysis_invalid_format(self, ux_handler):
        """Test range analysis for invalid formats."""
        # Test with invalid range format
        analysis = ux_handler._analyze_range_specification("R1C1:R10C4")
        
        assert len(analysis["steps"]) > 0
        assert len(analysis["fixes"]) > 0
        assert any("Excel format" in step for step in analysis["steps"])
        assert any("A1:E20" in fix for fix in analysis["fixes"])
    
    def test_range_analysis_large_range(self, ux_handler):
        """Test range analysis for large ranges."""
        analysis = ux_handler._analyze_range_specification("A1:ZZ2000")
        
        assert any("column Z" in step for step in analysis["steps"])
        assert any("large row range" in step.lower() for step in analysis["steps"])
    
    def test_sheet_name_matching(self, ux_handler):
        """Test fuzzy matching for sheet names."""
        # Exact match (case insensitive)
        matches = ux_handler._find_close_sheet_matches("data", ["Data", "Summary", "Charts"])
        assert "Data" in matches
        
        # Substring match
        matches = ux_handler._find_close_sheet_matches("sum", ["Summary", "Data", "Results"])
        assert "Summary" in matches
        
        # Word match
        matches = ux_handler._find_close_sheet_matches("sales data", ["Q1 Sales", "Data Analysis"])
        assert len(matches) >= 1
    
    def test_file_context_analysis(self, ux_handler):
        """Test file context analysis."""
        # Test with non-existent file
        context = ux_handler._analyze_file_context("/fake/path/file.xlsx")
        assert not context.get("exists", True)
        
        # Test with real file (create temporary)
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            # Write some data to make it non-empty
            tmp.write(b"fake excel data")
            tmp.flush()
            
            context = ux_handler._analyze_file_context(tmp.name)
            assert context["exists"]
            assert context["extension"] == ".xlsx"
            assert context["size"] > 0
            
            # Clean up
            Path(tmp.name).unlink()
    
    def test_response_structure_completeness(self, ux_handler):
        """Test that error responses contain all required fields."""
        error = FileAccessError("test.xlsx", "Test error")
        
        response = ux_handler.create_user_friendly_response(
            error, context="test", file_path="test.xlsx"
        )
        
        # Verify all required fields are present
        required_fields = [
            "error", "error_type", "technical_message", "user_friendly_message",
            "resolution_steps", "quick_fixes", "prevention_tips", "documentation_links",
            "context", "severity", "estimated_fix_time"
        ]
        
        for field in required_fields:
            assert field in response, f"Missing required field: {field}"
        
        # Verify field types
        assert isinstance(response["error"], bool)
        assert isinstance(response["resolution_steps"], list)
        assert isinstance(response["quick_fixes"], list)
        assert isinstance(response["prevention_tips"], list)
        assert isinstance(response["documentation_links"], list)


class TestUserFriendlyErrorIntegration:
    """Integration tests for user-friendly error handling."""
    
    def test_error_handler_initialization(self):
        """Test that error handler initializes correctly."""
        handler = UserFriendlyErrorHandler()
        
        assert handler.default_strategy is not None
        assert handler.user_messages is not None
        assert len(handler.user_messages) > 0
    
    def test_error_handler_inheritance(self):
        """Test that UserFriendlyErrorHandler extends ErrorHandlerCore correctly."""
        from sphinxcontrib.jsontable.errors.error_handler_core import ErrorHandlerCore
        
        handler = UserFriendlyErrorHandler()
        assert isinstance(handler, ErrorHandlerCore)
        
        # Test that core methods are available
        assert hasattr(handler, 'handle_error')
        assert hasattr(handler, 'create_error_response')
    
    def test_backward_compatibility(self, ux_handler):
        """Test that user-friendly handler maintains backward compatibility."""
        error = ValueError("Test error")
        
        # Test that original methods still work
        result = ux_handler.handle_error(error, "test context")
        assert result is not None
        assert hasattr(result, 'success')
        
        response = ux_handler.create_error_response(error, "test context")
        assert response is not None
        assert "error" in response


if __name__ == "__main__":
    pytest.main([__file__, "-v"])