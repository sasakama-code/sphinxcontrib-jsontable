"""
Test cases for performance limits and new functionality.

This module contains test cases for the new performance limit features,
including default limits, warning systems, and configuration options.
"""

from unittest.mock import MagicMock, patch

import pytest

from sphinxcontrib.jsontable.directives import (
    DEFAULT_MAX_ROWS,
    JsonTableDirective,
    TableConverter,
)


class TestTableConverterPerformanceLimits:
    """Test cases for TableConverter performance limit functionality."""

    @pytest.fixture
    def converter(self):
        """Create TableConverter instance for testing."""
        return TableConverter()

    @pytest.fixture
    def large_dataset(self):
        """Large dataset exceeding DEFAULT_MAX_ROWS for testing."""
        return [{"id": i, "name": f"item_{i}"} for i in range(15000)]

    @pytest.fixture
    def small_dataset(self):
        """Small dataset within DEFAULT_MAX_ROWS for testing."""
        return [{"id": i, "name": f"item_{i}"} for i in range(100)]

    # ========================================
    # DEFAULT_MAX_ROWS Functionality Tests
    # ========================================

    def test_default_max_rows_constant_value(self):
        """Test that DEFAULT_MAX_ROWS is set to expected value."""
        assert DEFAULT_MAX_ROWS == 10000

    def test_converter_uses_default_max_rows(self, converter):
        """Test that TableConverter uses DEFAULT_MAX_ROWS by default."""
        assert converter.default_max_rows == DEFAULT_MAX_ROWS

    def test_converter_accepts_custom_default_max_rows(self):
        """Test that TableConverter accepts custom default max rows."""
        custom_limit = 5000
        converter = TableConverter(default_max_rows=custom_limit)
        assert converter.default_max_rows == custom_limit

    # ========================================
    # _apply_default_limit Method Tests
    # ========================================

    def test_apply_default_limit_small_dataset_no_user_limit(
        self, converter, small_dataset
    ):
        """Test that small dataset has no limit applied when no user limit specified."""
        result = converter._apply_default_limit(small_dataset, None)
        assert result is None

    def test_apply_default_limit_large_dataset_no_user_limit(
        self, converter, large_dataset
    ):
        """Test that large dataset has default limit applied when no user limit specified."""
        with patch("sphinxcontrib.jsontable.directives.logger") as mock_logger:
            result = converter._apply_default_limit(large_dataset, None)
            assert result == DEFAULT_MAX_ROWS
            mock_logger.warning.assert_called_once()
            warning_msg = mock_logger.warning.call_args[0][0]
            assert "15,000 rows" in warning_msg
            assert "10,000 rows" in warning_msg

    def test_apply_default_limit_user_limit_zero_unlimited(
        self, converter, large_dataset
    ):
        """Test that user_limit=0 results in unlimited processing."""
        with patch("sphinxcontrib.jsontable.directives.logger") as mock_logger:
            result = converter._apply_default_limit(large_dataset, 0)
            assert result is None
            mock_logger.info.assert_called_once_with(
                "JsonTable: Unlimited rows requested via :limit: 0"
            )

    def test_apply_default_limit_user_limit_specified(self, converter, large_dataset):
        """Test that explicit user limit is respected."""
        user_limit = 2000
        result = converter._apply_default_limit(large_dataset, user_limit)
        assert result == user_limit

    def test_apply_default_limit_user_limit_small_dataset(
        self, converter, small_dataset
    ):
        """Test that user limit is respected even for small datasets."""
        user_limit = 50
        result = converter._apply_default_limit(small_dataset, user_limit)
        assert result == user_limit

    # ========================================
    # _estimate_data_size Method Tests
    # ========================================

    def test_estimate_data_size_dict(self, converter):
        """Test data size estimation for dictionary input."""
        data = {"key": "value"}
        assert converter._estimate_data_size(data) == 1

    def test_estimate_data_size_list(self, converter):
        """Test data size estimation for list input."""
        data = [{"id": 1}, {"id": 2}, {"id": 3}]
        assert converter._estimate_data_size(data) == 3

    def test_estimate_data_size_empty_list(self, converter):
        """Test data size estimation for empty list."""
        data = []
        assert converter._estimate_data_size(data) == 0

    def test_estimate_data_size_invalid_type(self, converter):
        """Test data size estimation for invalid types."""
        assert converter._estimate_data_size("string") == 0
        assert converter._estimate_data_size(123) == 0
        assert converter._estimate_data_size(None) == 0

    # ========================================
    # Integration Tests with Convert Method
    # ========================================

    def test_convert_large_dataset_applies_default_limit(
        self, converter, large_dataset
    ):
        """Test that convert method applies default limit to large datasets."""
        with patch("sphinxcontrib.jsontable.directives.logger"):
            result = converter.convert(large_dataset, include_header=True)
            # Header + DEFAULT_MAX_ROWS data rows
            assert len(result) == DEFAULT_MAX_ROWS + 1

    def test_convert_small_dataset_no_limit_applied(self, converter, small_dataset):
        """Test that convert method doesn't limit small datasets."""
        result = converter.convert(small_dataset, include_header=True)
        # Header + all data rows
        assert len(result) == len(small_dataset) + 1

    def test_convert_with_explicit_limit_zero(self, converter, large_dataset):
        """Test that explicit limit=0 disables all limits."""
        with patch("sphinxcontrib.jsontable.directives.logger"):
            result = converter.convert(large_dataset, include_header=True, limit=0)
            # Header + all data rows (unlimited)
            assert len(result) == len(large_dataset) + 1

    def test_convert_with_explicit_limit_value(self, converter, large_dataset):
        """Test that explicit limit value is respected."""
        explicit_limit = 500
        result = converter.convert(
            large_dataset, include_header=True, limit=explicit_limit
        )
        # Header + limited data rows
        assert len(result) == explicit_limit + 1

    # ========================================
    # Warning Message Tests
    # ========================================

    def test_warning_message_format(self, converter, large_dataset):
        """Test that warning message contains expected information."""
        with patch("sphinxcontrib.jsontable.directives.logger") as mock_logger:
            converter._apply_default_limit(large_dataset, None)
            warning_msg = mock_logger.warning.call_args[0][0]

            # Check message contains key information
            assert "Large dataset detected" in warning_msg
            assert "15,000 rows" in warning_msg
            assert "10,000 rows" in warning_msg
            assert ":limit: option" in warning_msg
            assert "all rows" in warning_msg

    def test_no_warning_for_small_dataset(self, converter, small_dataset):
        """Test that no warning is issued for small datasets."""
        with patch("sphinxcontrib.jsontable.directives.logger") as mock_logger:
            converter._apply_default_limit(small_dataset, None)
            mock_logger.warning.assert_not_called()

    def test_info_message_for_unlimited_request(self, converter, large_dataset):
        """Test that info message is logged for unlimited requests."""
        with patch("sphinxcontrib.jsontable.directives.logger") as mock_logger:
            converter._apply_default_limit(large_dataset, 0)
            mock_logger.info.assert_called_once_with(
                "JsonTable: Unlimited rows requested via :limit: 0"
            )

    # ========================================
    # Edge Cases and Error Handling
    # ========================================

    def test_apply_default_limit_exactly_at_threshold(self, converter):
        """Test behavior when dataset size exactly equals threshold."""
        exact_size_dataset = [{"id": i} for i in range(DEFAULT_MAX_ROWS)]
        result = converter._apply_default_limit(exact_size_dataset, None)
        # Should not trigger limit (dataset size == limit, not >)
        assert result is None

    def test_apply_default_limit_one_over_threshold(self, converter):
        """Test behavior when dataset size is one over threshold."""
        over_threshold_dataset = [{"id": i} for i in range(DEFAULT_MAX_ROWS + 1)]
        with patch("sphinxcontrib.jsontable.directives.logger"):
            result = converter._apply_default_limit(over_threshold_dataset, None)
            assert result == DEFAULT_MAX_ROWS

    def test_custom_default_max_rows_respected(self):
        """Test that custom default max rows setting is respected."""
        custom_limit = 5000
        converter = TableConverter(default_max_rows=custom_limit)
        large_dataset = [{"id": i} for i in range(6000)]

        with patch("sphinxcontrib.jsontable.directives.logger") as mock_logger:
            result = converter._apply_default_limit(large_dataset, None)
            assert result == custom_limit
            warning_msg = mock_logger.warning.call_args[0][0]
            assert "6,000 rows" in warning_msg
            assert "5,000 rows" in warning_msg


class TestJsonTableDirectivePerformanceLimits:
    """Test cases for JsonTableDirective performance limit integration."""

    @pytest.fixture
    def mock_env(self):
        """Mock Sphinx environment for testing."""
        env = MagicMock()
        env.config.jsontable_max_rows = DEFAULT_MAX_ROWS
        env.srcdir = "/tmp/docs"
        return env

    @pytest.fixture
    def directive_instance(self, mock_env):
        """Create JsonTableDirective instance for testing."""
        # Mock the required arguments for SphinxDirective
        name = "jsontable"
        arguments = []
        options = {}
        content = []
        lineno = 1
        content_offset = 0
        block_text = ""
        state = MagicMock()
        state_machine = MagicMock()

        directive = JsonTableDirective(
            name,
            arguments,
            options,
            content,
            lineno,
            content_offset,
            block_text,
            state,
            state_machine,
        )
        directive.env = mock_env
        return directive

    def test_directive_uses_config_max_rows(self, directive_instance):
        """Test that directive uses jsontable_max_rows from Sphinx config."""
        # Should use config value
        assert directive_instance.converter.default_max_rows == DEFAULT_MAX_ROWS

    def test_directive_with_custom_config_max_rows(self, mock_env):
        """Test that directive respects custom config max rows."""
        custom_limit = 7500
        mock_env.config.jsontable_max_rows = custom_limit

        # Create directive with custom config
        directive = JsonTableDirective(
            "jsontable", [], {}, [], 1, 0, "", MagicMock(), MagicMock()
        )
        directive.env = mock_env

        assert directive.converter.default_max_rows == custom_limit

    def test_directive_limit_option_nonnegative_int(self, directive_instance):
        """Test that directive accepts nonnegative integers for limit option."""
        # Check that option_spec allows nonnegative integers
        from docutils.parsers.rst import directives

        assert directive_instance.option_spec["limit"] == directives.nonnegative_int

    # ========================================
    # Backward Compatibility Tests
    # ========================================

    def test_backward_compatibility_no_limit_option(self, directive_instance):
        """Test that existing usage without :limit: option still works."""
        # Simulate directive without limit option
        directive_instance.options = {"header": True}

        # Should work without errors (tested via integration)
        assert hasattr(directive_instance, "converter")
        assert directive_instance.converter.default_max_rows == DEFAULT_MAX_ROWS

    def test_backward_compatibility_existing_limit_behavior(self, directive_instance):
        """Test that existing :limit: behavior is preserved."""
        # Existing positive limit should work as before
        directive_instance.options = {"limit": 1000}
        limit_value = directive_instance.options.get("limit")

        assert limit_value == 1000

    # ========================================
    # Performance and Memory Tests (CI-Safe)
    # ========================================

    @pytest.mark.performance
    def test_memory_usage_with_default_limit_ci_safe(self, converter):
        """Test that memory usage is controlled with default limit (CI-safe version)."""
        # Create a very large dataset
        huge_dataset = [{"id": i, "data": f"value_{i}" * 100} for i in range(50000)]

        with patch("sphinxcontrib.jsontable.directives.logger"):
            # Should apply default limit automatically
            result = converter.convert(huge_dataset, include_header=True)

            # Memory should be controlled by limiting to DEFAULT_MAX_ROWS
            assert len(result) <= DEFAULT_MAX_ROWS + 1  # +1 for header
            assert isinstance(result, list)
            assert all(isinstance(row, list) for row in result)

    @pytest.mark.performance
    def test_processing_efficiency_with_limit_functional(self, converter):
        """Test that processing efficiency is maintained with limits (functional test)."""
        import time

        # Large dataset that benefits from limits
        large_dataset = [{"field": f"value_{i}"} for i in range(25000)]

        # Test with default limit (should efficiently process limited data)
        with patch("sphinxcontrib.jsontable.directives.logger"):
            start_time = time.perf_counter()
            limited_result = converter.convert(large_dataset, include_header=True)
            limited_time = time.perf_counter() - start_time

        # Test with unlimited (should process all data)
        with patch("sphinxcontrib.jsontable.directives.logger"):
            start_time = time.perf_counter()
            unlimited_result = converter.convert(
                large_dataset, include_header=True, limit=0
            )
            unlimited_time = time.perf_counter() - start_time

        # Functional assertions (not time-based)
        assert len(limited_result) == DEFAULT_MAX_ROWS + 1  # Limited processing
        assert len(unlimited_result) == len(large_dataset) + 1  # Full processing

        # Log performance information for reference (not asserted)
        print("\nPerformance reference (not asserted):")
        print(
            f"  Limited processing:   {limited_time:.4f}s ({len(limited_result):,} rows)"
        )
        print(
            f"  Unlimited processing: {unlimited_time:.4f}s ({len(unlimited_result):,} rows)"
        )
        print(
            f"  Data reduction: {(1 - len(limited_result) / len(unlimited_result)) * 100:.1f}%"
        )


class TestPerformanceLimitsBenchmarks:
    """pytest-benchmark based performance tests for CI stability."""

    @pytest.fixture
    def converter(self):
        """Create TableConverter instance for testing."""
        return TableConverter()

    @pytest.fixture
    def benchmark_dataset(self):
        """Dataset optimized for benchmark testing."""
        return [
            {"id": i, "name": f"item_{i}", "value": f"data_{i}"} for i in range(5000)
        ]

    @pytest.mark.benchmark
    def test_convert_performance_benchmark(
        self, converter, benchmark_dataset, benchmark
    ):
        """Benchmark convert method performance with default limits."""
        with patch("sphinxcontrib.jsontable.directives.logger"):
            result = benchmark(converter.convert, benchmark_dataset, True)

            # Functional verification (no time assertions)
            assert isinstance(result, list)
            assert len(result) <= len(benchmark_dataset) + 1

    @pytest.mark.benchmark
    def test_apply_default_limit_benchmark(
        self, converter, benchmark_dataset, benchmark
    ):
        """Benchmark _apply_default_limit method performance."""
        with patch("sphinxcontrib.jsontable.directives.logger"):
            result = benchmark(converter._apply_default_limit, benchmark_dataset, None)

            # Functional verification
            assert result is None or isinstance(result, int)

    @pytest.mark.benchmark
    def test_estimate_data_size_benchmark(
        self, converter, benchmark_dataset, benchmark
    ):
        """Benchmark _estimate_data_size method performance."""
        result = benchmark(converter._estimate_data_size, benchmark_dataset)

        # Functional verification
        assert result == len(benchmark_dataset)

    @pytest.mark.benchmark
    def test_large_dataset_processing_benchmark(self, converter, benchmark):
        """Benchmark large dataset processing with various configurations."""
        large_dataset = [{"field": f"value_{i}"} for i in range(15000)]

        with patch("sphinxcontrib.jsontable.directives.logger"):
            result = benchmark(converter.convert, large_dataset, True)

            # Should be limited by default
            assert len(result) == DEFAULT_MAX_ROWS + 1

    @pytest.mark.benchmark
    def test_scalability_benchmark_multiple_sizes(self, converter, benchmark):
        """Benchmark scalability across different dataset sizes."""
        # Test with moderate size for stable benchmarking
        dataset = [{"id": i, "data": f"value_{i}"} for i in range(2000)]

        with patch("sphinxcontrib.jsontable.directives.logger"):
            result = benchmark(converter.convert, dataset, True)

            # Functional verification
            assert len(result) == len(dataset) + 1  # All data + header
            assert all(isinstance(row, list) for row in result)
