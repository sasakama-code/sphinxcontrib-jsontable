"""
Additional integration tests for performance limits with existing test infrastructure.

This module adds new functionality tests to the existing test suite to ensure
proper integration of performance limits with all existing features.
"""

from unittest.mock import MagicMock, patch

import pytest

from sphinxcontrib.jsontable.directives import (
    DEFAULT_MAX_ROWS,
    JsonTableDirective,
    JsonTableError,
    TableConverter,
)


class TestTableConverterPerformanceLimitsIntegration:
    """Integration tests for performance limits with existing converter functionality."""

    @pytest.fixture
    def converter(self):
        """Create TableConverter instance for testing."""
        return TableConverter()

    @pytest.fixture
    def converter_custom_limit(self):
        """Create TableConverter with custom default limit."""
        return TableConverter(default_max_rows=5000)

    @pytest.fixture
    def large_object_list(self):
        """Large list of objects exceeding default limit."""
        return [{"id": i, "value": f"item_{i}"} for i in range(15000)]

    @pytest.fixture
    def large_array_list(self):
        """Large list of arrays exceeding default limit."""
        return [[i, f"value_{i}"] for i in range(12000)]

    # ========================================
    # Integration with existing convert method
    # ========================================

    def test_convert_applies_default_limit_to_large_object_list(
        self, converter, large_object_list
    ):
        """Test that convert method applies default limit to large object lists."""
        with patch('sphinxcontrib.jsontable.directives.logger') as mock_logger:
            result = converter.convert(large_object_list, include_header=True)

            # Should be limited to DEFAULT_MAX_ROWS + header
            assert len(result) == DEFAULT_MAX_ROWS + 1
            mock_logger.warning.assert_called_once()

    def test_convert_applies_default_limit_to_large_array_list(
        self, converter, large_array_list
    ):
        """Test that convert method applies default limit to large array lists."""
        with patch('sphinxcontrib.jsontable.directives.logger') as mock_logger:
            result = converter.convert(large_array_list, include_header=False)

            # Should be limited to DEFAULT_MAX_ROWS
            assert len(result) == DEFAULT_MAX_ROWS
            mock_logger.warning.assert_called_once()

    def test_convert_respects_custom_default_limit(
        self, converter_custom_limit, large_object_list
    ):
        """Test that convert method respects custom default limit."""
        with patch('sphinxcontrib.jsontable.directives.logger') as mock_logger:
            result = converter_custom_limit.convert(large_object_list, include_header=True)

            # Should be limited to custom limit + header
            assert len(result) == 5000 + 1
            mock_logger.warning.assert_called_once()

    def test_convert_unlimited_override_works_with_large_data(
        self, converter, large_object_list
    ):
        """Test that :limit: 0 override works with large datasets."""
        with patch('sphinxcontrib.jsontable.directives.logger') as mock_logger:
            result = converter.convert(large_object_list, include_header=True, limit=0)

            # Should process all data
            assert len(result) == len(large_object_list) + 1
            mock_logger.info.assert_called_once()

    def test_convert_explicit_limit_overrides_default(
        self, converter, large_object_list
    ):
        """Test that explicit limit overrides default limit."""
        custom_limit = 3000
        result = converter.convert(large_object_list, include_header=True, limit=custom_limit)

        # Should be limited to explicit limit + header
        assert len(result) == custom_limit + 1

    # ========================================
    # Integration with different data types
    # ========================================

    def test_single_dict_not_affected_by_default_limit(self, converter):
        """Test that single dictionary is not affected by default limit."""
        single_dict = {"key": "value"}
        result = converter.convert(single_dict, include_header=True)

        # Should process normally without limit
        assert len(result) == 2  # Header + 1 row

    def test_small_dataset_not_affected_by_default_limit(self, converter):
        """Test that small datasets are not affected by default limit."""
        small_data = [{"id": i} for i in range(100)]

        with patch('sphinxcontrib.jsontable.directives.logger') as mock_logger:
            result = converter.convert(small_data, include_header=True)

            # Should process all data without warning
            assert len(result) == 101  # Header + 100 rows
            mock_logger.warning.assert_not_called()

    def test_exactly_at_limit_threshold(self, converter):
        """Test behavior when dataset size exactly equals the limit."""
        exact_limit_data = [{"id": i} for i in range(DEFAULT_MAX_ROWS)]

        with patch('sphinxcontrib.jsontable.directives.logger') as mock_logger:
            result = converter.convert(exact_limit_data, include_header=True)

            # Should process all data (size == limit, not >)
            assert len(result) == DEFAULT_MAX_ROWS + 1
            mock_logger.warning.assert_not_called()

    def test_one_over_limit_threshold(self, converter):
        """Test behavior when dataset size is one over the limit."""
        over_limit_data = [{"id": i} for i in range(DEFAULT_MAX_ROWS + 1)]

        with patch('sphinxcontrib.jsontable.directives.logger') as mock_logger:
            result = converter.convert(over_limit_data, include_header=True)

            # Should be limited
            assert len(result) == DEFAULT_MAX_ROWS + 1
            mock_logger.warning.assert_called_once()

    # ========================================
    # Error handling integration
    # ========================================

    def test_error_handling_not_affected_by_limits(self, converter):
        """Test that error handling works normally with limit functionality."""
        # Test with invalid data types
        with pytest.raises(JsonTableError):
            converter.convert("invalid_string")

        with pytest.raises(JsonTableError):
            converter.convert(123)

        with pytest.raises(JsonTableError):
            converter.convert(None)

    def test_empty_data_handling_with_limits(self, converter):
        """Test that empty data handling works with limit functionality."""
        with pytest.raises(JsonTableError):
            converter.convert([])


class TestJsonTableDirectivePerformanceLimitsIntegration:
    """Integration tests for JsonTableDirective with performance limits."""

    @pytest.fixture
    def mock_env(self):
        """Mock Sphinx environment."""
        env = MagicMock()
        env.config.jsontable_max_rows = DEFAULT_MAX_ROWS
        env.srcdir = "/tmp/test"
        return env

    @pytest.fixture
    def directive_with_custom_config(self):
        """Create directive with custom configuration."""
        env = MagicMock()
        env.config.jsontable_max_rows = 7500
        env.srcdir = "/tmp/test"

        directive = JsonTableDirective(
            "jsontable", [], {}, [], 1, 0, "", MagicMock(), MagicMock()
        )
        directive.env = env
        return directive

    def test_directive_uses_default_config_value(self, mock_env):
        """Test that directive uses default config value."""
        directive = JsonTableDirective(
            "jsontable", [], {}, [], 1, 0, "", MagicMock(), MagicMock()
        )
        directive.env = mock_env

        assert directive.converter.default_max_rows == DEFAULT_MAX_ROWS

    def test_directive_uses_custom_config_value(self, directive_with_custom_config):
        """Test that directive uses custom config value."""
        assert directive_with_custom_config.converter.default_max_rows == 7500

    def test_directive_option_spec_includes_nonnegative_int(self):
        """Test that directive option_spec includes nonnegative_int for limit."""
        from docutils.parsers.rst import directives
        assert JsonTableDirective.option_spec["limit"] == directives.nonnegative_int

    def test_directive_limit_option_parsing(self, mock_env):
        """Test that directive correctly parses limit options."""
        # Test with limit option
        directive = JsonTableDirective(
            "jsontable", [], {"limit": 5000}, [], 1, 0, "", MagicMock(), MagicMock()
        )
        directive.env = mock_env

        assert directive.options.get("limit") == 5000

    def test_directive_limit_zero_parsing(self, mock_env):
        """Test that directive correctly parses limit: 0."""
        # Test with limit: 0
        directive = JsonTableDirective(
            "jsontable", [], {"limit": 0}, [], 1, 0, "", MagicMock(), MagicMock()
        )
        directive.env = mock_env

        assert directive.options.get("limit") == 0


class TestBackwardCompatibilityWithLimits:
    """Ensure that all existing functionality continues to work with limits."""

    @pytest.fixture
    def converter(self):
        """Create TableConverter instance for testing."""
        return TableConverter()

    def test_existing_usage_patterns_unchanged(self, converter):
        """Test that existing usage patterns work unchanged."""
        # Original usage without any limit specification
        small_data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]

        result = converter.convert(small_data, include_header=True)

        # Should work exactly as before
        assert len(result) == 3  # Header + 2 rows
        assert result[0] == ["name", "age"]
        assert result[1] == ["Alice", "30"]
        assert result[2] == ["Bob", "25"]

    def test_existing_limit_option_behavior_preserved(self, converter):
        """Test that existing :limit: option behavior is preserved."""
        data = [{"id": i} for i in range(1000)]

        # Existing limit usage should work exactly as before
        result = converter.convert(data, include_header=True, limit=50)

        assert len(result) == 51  # Header + 50 limited rows

    def test_header_functionality_preserved(self, converter):
        """Test that header functionality works with limits."""
        large_data = [{"field": f"value_{i}"} for i in range(15000)]

        # With header
        with patch('sphinxcontrib.jsontable.directives.logger'):
            result_with_header = converter.convert(large_data, include_header=True)
            assert result_with_header[0] == ["field"]  # Header row
            assert len(result_with_header) == DEFAULT_MAX_ROWS + 1

        # Without header
        with patch('sphinxcontrib.jsontable.directives.logger'):
            result_without_header = converter.convert(large_data, include_header=False)
            assert len(result_without_header) == DEFAULT_MAX_ROWS

    def test_encoding_option_unaffected(self, mock_env):
        """Test that encoding option continues to work with limits."""
        directive = JsonTableDirective(
            "jsontable", [], {"encoding": "utf-16"}, [], 1, 0, "", MagicMock(), MagicMock()
        )
        directive.env = mock_env

        # Should still respect encoding option
        assert directive.loader.encoding == "utf-16"

    def test_error_conditions_unchanged(self, converter):
        """Test that error conditions continue to work as expected."""
        # Invalid data should still raise appropriate errors
        with pytest.raises(JsonTableError):
            converter.convert("invalid")

        with pytest.raises(JsonTableError):
            converter.convert([None])  # Invalid first element


class TestPerformanceLimitsWithComplexData:
    """Test performance limits with complex real-world data structures."""

    @pytest.fixture
    def converter(self):
        """Create TableConverter instance for testing."""
        return TableConverter()

    def test_complex_nested_data_with_limits(self, converter):
        """Test that complex nested data works with limits."""
        complex_data = []
        for i in range(12000):
            obj = {
                "id": i,
                "user": {"name": f"User_{i}", "email": f"user{i}@example.com"},
                "settings": {"theme": "dark", "notifications": True},
                "data": [1, 2, 3, 4, 5]
            }
            complex_data.append(obj)

        with patch('sphinxcontrib.jsontable.directives.logger') as mock_logger:
            result = converter.convert(complex_data, include_header=True)

            # Should be limited and flattened appropriately
            assert len(result) == DEFAULT_MAX_ROWS + 1
            mock_logger.warning.assert_called_once()

            # Check that nested data is converted to strings
            assert isinstance(result[1][1], str)  # user field should be string

    def test_mixed_data_types_with_limits(self, converter):
        """Test that mixed data types work with limits."""
        mixed_data = []
        for i in range(11000):
            obj = {
                "id": i,
                "name": f"Item_{i}",
                "price": 99.99 + i,
                "available": i % 2 == 0,
                "tags": ["tag1", "tag2"],
                "metadata": None if i % 100 == 0 else {"created": "2023-01-01"}
            }
            mixed_data.append(obj)

        with patch('sphinxcontrib.jsontable.directives.logger'):
            result = converter.convert(mixed_data, include_header=True)

            # Should handle mixed types and be limited
            assert len(result) == DEFAULT_MAX_ROWS + 1
            assert all(isinstance(cell, str) for row in result for cell in row)

    def test_very_wide_data_with_limits(self, converter):
        """Test that very wide data (many columns) works with limits."""
        wide_data = []
        for i in range(8000):
            obj = {f"field_{j}": f"value_{i}_{j}" for j in range(50)}
            wide_data.append(obj)

        with patch('sphinxcontrib.jsontable.directives.logger'):
            result = converter.convert(wide_data, include_header=True)

            # Should be limited in rows but preserve all columns
            assert len(result) == DEFAULT_MAX_ROWS + 1
            assert len(result[0]) == 50  # All columns preserved

    @pytest.fixture
    def mock_env(self):
        """Mock Sphinx environment for directive tests."""
        env = MagicMock()
        env.config.jsontable_max_rows = DEFAULT_MAX_ROWS
        env.srcdir = "/tmp/test"
        return env
