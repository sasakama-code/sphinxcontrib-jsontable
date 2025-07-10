"""Test Column Customization - Comprehensive TDD tests for Issue #48.

This test module implements comprehensive test coverage for column customization
functionality including visibility control, ordering, and width specifications.

TDD Implementation Strategy:
- RED Phase: Create failing tests that define exact requirements
- GREEN Phase: Implement minimal functionality to pass tests
- REFACTOR Phase: Enhance to enterprise-grade quality

Test Coverage Areas:
- Column visibility (show/hide specific columns)
- Custom column ordering with various input formats
- Column width specifications (percentage, pixels, auto)
- Error handling and validation
- Performance with large datasets
- Integration with existing directive functionality

CLAUDE.md Code Excellence Compliance:
- DRY Principle: Reusable test fixtures and helpers
- Single Responsibility: Each test validates one specific behavior
- SOLID Principles: Clear test structure with separation of concerns
"""

from unittest.mock import Mock

import pytest

from sphinxcontrib.jsontable.directives.column_customizer import ColumnCustomizer
from sphinxcontrib.jsontable.directives.directive_core import JsonTableDirective
from sphinxcontrib.jsontable.directives.validators import JsonTableError


class TestColumnCustomizer:
    """Test suite for ColumnCustomizer functionality."""

    @pytest.fixture
    def customizer(self):
        """Create ColumnCustomizer instance for testing."""
        return ColumnCustomizer()

    @pytest.fixture
    def sample_table_data(self):
        """Sample table data for testing."""
        return [
            ["name", "age", "score", "department", "active"],
            ["Alice", "25", "95", "Engineering", "true"],
            ["Bob", "30", "87", "Design", "true"],
            ["Carol", "28", "92", "Marketing", "false"],
            ["David", "35", "89", "Engineering", "true"]
        ]

    @pytest.fixture
    def large_table_data(self):
        """Large table data for performance testing."""
        headers = ["col1", "col2", "col3", "col4", "col5"]
        data = [headers]
        for i in range(1000):
            data.append([f"value{i}_{j}" for j in range(5)])
        return data

    # RED Phase Tests - These should initially fail

    def test_column_selection_basic(self, customizer, sample_table_data):
        """Test basic column selection functionality.
        
        Should select only specified columns in original order.
        """
        result, widths = customizer.customize_columns(
            sample_table_data,
            columns="name,score,active"
        )
        
        # Expected: Only selected columns, original data order preserved
        expected = [
            ["name", "score", "active"],
            ["Alice", "95", "true"],
            ["Bob", "87", "true"],
            ["Carol", "92", "false"],
            ["David", "89", "true"]
        ]
        
        assert result == expected
        assert widths == {}  # No width specifications

    def test_column_ordering_basic(self, customizer, sample_table_data):
        """Test basic column reordering functionality.
        
        Should reorder columns according to specification.
        """
        result, widths = customizer.customize_columns(
            sample_table_data,
            column_order="score,name,age"
        )
        
        # Expected: All columns reordered as specified
        expected = [
            ["score", "name", "age", "department", "active"],
            ["95", "Alice", "25", "Engineering", "true"],
            ["87", "Bob", "30", "Design", "true"],
            ["92", "Carol", "28", "Marketing", "false"],
            ["89", "David", "35", "Engineering", "true"]
        ]
        
        assert result == expected

    def test_column_width_specifications(self, customizer, sample_table_data):
        """Test column width specification functionality.
        
        Should return proper width specifications for HTML rendering.
        """
        result, widths = customizer.customize_columns(
            sample_table_data,
            columns="name,age,score",
            column_widths="40%,20%,40%"
        )
        
        # Expected: Width specifications match column order
        expected_widths = {
            "name": "40%",
            "age": "20%", 
            "score": "40%"
        }
        
        assert widths == expected_widths
        # Verify data is correctly filtered
        assert len(result[0]) == 3  # Only 3 columns
        assert result[0] == ["name", "age", "score"]

    def test_combined_column_customization(self, customizer, sample_table_data):
        """Test combined column selection, ordering, and width specification.
        
        Should apply all three customizations correctly.
        """
        result, widths = customizer.customize_columns(
            sample_table_data,
            columns="name,score,active",
            column_order="score,name,active",
            column_widths="30%,50%,20%"
        )
        
        # Expected: Selected columns in custom order with widths
        expected_data = [
            ["score", "name", "active"],
            ["95", "Alice", "true"],
            ["87", "Bob", "true"],
            ["92", "Carol", "false"],
            ["89", "David", "true"]
        ]
        
        expected_widths = {
            "score": "30%",
            "name": "50%",
            "active": "20%"
        }
        
        assert result == expected_data
        assert widths == expected_widths

    def test_wildcard_column_selection(self, customizer, sample_table_data):
        """Test wildcard pattern matching for column selection.
        
        Should support wildcard patterns like 'col*' for flexible selection.
        """
        # Add data with pattern-based headers
        pattern_data = [
            ["user_name", "user_age", "user_active", "system_id", "score"],
            ["Alice", "25", "true", "123", "95"],
            ["Bob", "30", "true", "456", "87"]
        ]
        
        result, widths = customizer.customize_columns(
            pattern_data,
            columns="user_*,score"
        )
        
        # Expected: All user_* columns plus score
        expected = [
            ["user_name", "user_age", "user_active", "score"],
            ["Alice", "25", "true", "95"],
            ["Bob", "30", "true", "87"]
        ]
        
        assert result == expected

    def test_case_insensitive_column_matching(self, customizer, sample_table_data):
        """Test case-insensitive column name matching.
        
        Should match columns regardless of case differences.
        """
        result, widths = customizer.customize_columns(
            sample_table_data,
            columns="NAME,AGE,Score"  # Mixed case
        )
        
        # Expected: Correct columns selected despite case differences
        expected = [
            ["name", "age", "score"],  # Original case preserved
            ["Alice", "25", "95"],
            ["Bob", "30", "87"],
            ["Carol", "28", "92"],
            ["David", "35", "89"]
        ]
        
        assert result == expected

    def test_partial_column_ordering(self, customizer, sample_table_data):
        """Test partial column ordering with automatic completion.
        
        Should reorder specified columns and append remaining columns.
        """
        result, widths = customizer.customize_columns(
            sample_table_data,
            column_order="score,name"  # Only specify 2 of 5 columns
        )
        
        # Expected: Specified columns first, then remaining in original order
        expected_headers = ["score", "name", "age", "department", "active"]
        
        assert result[0] == expected_headers

    def test_mixed_width_units(self, customizer, sample_table_data):
        """Test mixed width units (percentage, pixels, auto).
        
        Should support different width unit types in same specification.
        """
        result, widths = customizer.customize_columns(
            sample_table_data,
            columns="name,age,score",
            column_widths="200px,20%,auto"
        )
        
        expected_widths = {
            "name": "200px",
            "age": "20%",
            "score": "auto"
        }
        
        assert widths == expected_widths

    def test_performance_large_dataset(self, customizer, large_table_data):
        """Test performance with large dataset (1000+ rows).
        
        Should handle large datasets efficiently without performance degradation.
        """
        import time
        
        start_time = time.perf_counter()
        result, widths = customizer.customize_columns(
            large_table_data,
            columns="col1,col3,col5",
            column_order="col5,col1,col3"
        )
        end_time = time.perf_counter()
        
        # Performance requirement: < 100ms for 1000 rows
        assert (end_time - start_time) < 0.1
        
        # Verify correctness
        assert len(result) == 1001  # Header + 1000 data rows
        assert result[0] == ["col5", "col1", "col3"]

    # Error Handling Tests

    def test_empty_table_data_error(self, customizer):
        """Test error handling for empty table data."""
        with pytest.raises(JsonTableError, match="Table data cannot be empty"):
            customizer.customize_columns([])

    def test_empty_header_row_error(self, customizer):
        """Test error handling for empty header row."""
        with pytest.raises(JsonTableError, match="Header row cannot be empty"):
            customizer.customize_columns([[]])

    def test_nonexistent_column_selection_error(self, customizer, sample_table_data):
        """Test error handling for non-existent column names."""
        with pytest.raises(JsonTableError, match="Column 'nonexistent' not found"):
            customizer.customize_columns(
                sample_table_data,
                columns="name,nonexistent,score"
            )

    def test_invalid_column_order_error(self, customizer, sample_table_data):
        """Test error handling for invalid column order specification."""
        with pytest.raises(JsonTableError, match="Column 'invalid' in order specification"):
            customizer.customize_columns(
                sample_table_data,
                columns="name,age,score",
                column_order="score,invalid,name"
            )

    def test_mismatched_width_count_error(self, customizer, sample_table_data):
        """Test error handling for width count mismatch."""
        with pytest.raises(JsonTableError, match="Width specification count .* must match column count"):
            customizer.customize_columns(
                sample_table_data,
                columns="name,age,score",  # 3 columns
                column_widths="30%,40%"    # 2 widths
            )

    def test_invalid_width_format_error(self, customizer, sample_table_data):
        """Test error handling for invalid width formats."""
        with pytest.raises(JsonTableError, match="Invalid width specification"):
            customizer.customize_columns(
                sample_table_data,
                columns="name,age,score",
                column_widths="30%,invalid,40%"
            )

    def test_excessive_percentage_width_warning(self, customizer, sample_table_data, caplog):
        """Test warning for total percentage width exceeding 100%."""
        result, widths = customizer.customize_columns(
            sample_table_data,
            columns="name,age,score",
            column_widths="50%,60%,40%"  # Total: 150%
        )
        
        # Should still work but log warning
        assert "exceeds 100%" in caplog.text
        assert widths == {"name": "50%", "age": "60%", "score": "40%"}


class TestJsonTableDirectiveIntegration:
    """Test integration of column customization with JsonTableDirective."""

    @pytest.fixture
    def mock_directive(self):
        """Create mock JsonTableDirective for testing."""
        directive = Mock(spec=JsonTableDirective)
        directive.options = {}
        directive.env = Mock()
        directive.env.config = Mock()
        directive.env.srcdir = "/test/src"
        return directive

    def test_directive_option_parsing(self, mock_directive):
        """Test parsing of column customization options in directive.
        
        Should parse new options and pass them to ColumnCustomizer.
        """
        # This test will fail until we add option parsing to directive_core.py
        mock_directive.options = {
            "columns": "name,age,score",
            "column-order": "score,name,age", 
            "column-widths": "30%,40%,30%"
        }
        
        # TODO: This will be implemented in GREEN phase
        # expected_columns = ["name", "age", "score"]
        # expected_order = ["score", "name", "age"]
        # expected_widths = {"score": "30%", "name": "40%", "age": "30%"}
        
        pytest.skip("Integration test - will be implemented in GREEN phase")

    def test_backward_compatibility(self, mock_directive):
        """Test that existing functionality remains unchanged.
        
        Should work exactly as before when new options are not specified.
        """
        # This test ensures we don't break existing behavior
        mock_directive.options = {
            "header": True,
            "limit": 10
        }
        
        # TODO: Verify existing behavior unchanged
        pytest.skip("Backward compatibility test - will be implemented in GREEN phase")

    def test_new_option_spec_validation(self):
        """Test that new options are properly defined in option_spec.
        
        Should include new column customization options with correct types.
        """
        # TODO: Verify option_spec includes new options
        # expected_new_options = [
        #     "columns",
        #     "column-order", 
        #     "column-widths"
        # ]
        
        pytest.skip("Option spec validation - will be implemented in GREEN phase")


# Performance Benchmark Tests
class TestColumnCustomizationPerformance:
    """Performance benchmark tests for column customization."""

    @pytest.fixture
    def massive_table_data(self):
        """Create massive table for performance testing."""
        headers = [f"column_{i}" for i in range(20)]
        data = [headers]
        for i in range(10000):
            data.append([f"value_{i}_{j}" for j in range(20)])
        return data

    @pytest.mark.performance
    def test_column_selection_performance(self, massive_table_data):
        """Test column selection performance with massive dataset."""
        customizer = ColumnCustomizer()
        
        import time
        start_time = time.perf_counter()
        
        result, widths = customizer.customize_columns(
            massive_table_data,
            columns="column_0,column_5,column_10,column_15,column_19"
        )
        
        end_time = time.perf_counter()
        
        # Performance requirement: < 500ms for 10K rows x 20 columns
        processing_time = end_time - start_time
        assert processing_time < 0.5, f"Processing took {processing_time:.3f}s, expected < 0.5s"
        
        # Verify correctness
        assert len(result) == 10001  # Header + 10K rows
        assert len(result[0]) == 5   # 5 selected columns

    @pytest.mark.performance
    def test_column_ordering_performance(self, massive_table_data):
        """Test column ordering performance with massive dataset."""
        customizer = ColumnCustomizer()
        
        import time
        start_time = time.perf_counter()
        
        # Reverse order of all columns
        reverse_order = [f"column_{i}" for i in range(19, -1, -1)]
        
        result, widths = customizer.customize_columns(
            massive_table_data,
            column_order=",".join(reverse_order)
        )
        
        end_time = time.perf_counter()
        
        # Performance requirement: < 1s for 10K rows x 20 columns reordering
        processing_time = end_time - start_time
        assert processing_time < 1.0, f"Processing took {processing_time:.3f}s, expected < 1.0s"
        
        # Verify correctness
        assert result[0] == reverse_order

    @pytest.mark.memory
    def test_memory_efficiency(self, massive_table_data):
        """Test memory efficiency of column customization."""
        import tracemalloc
        
        customizer = ColumnCustomizer()
        
        tracemalloc.start()
        
        result, widths = customizer.customize_columns(
            massive_table_data,
            columns="column_0,column_10"
        )
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Memory requirement: Peak memory < 50MB for 10K x 20 dataset
        peak_mb = peak / 1024 / 1024
        assert peak_mb < 50, f"Peak memory usage {peak_mb:.2f}MB, expected < 50MB"