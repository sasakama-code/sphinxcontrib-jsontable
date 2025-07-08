"""Test Data Type Rendering - Comprehensive TDD tests for Issue #49.

This test module implements comprehensive test coverage for intelligent data type
detection and rendering functionality including URL links, boolean checkmarks,
date localization, and number formatting.

TDD Implementation Strategy:
- RED Phase: Create failing tests that define exact requirements
- GREEN Phase: Implement minimal functionality to pass tests
- REFACTOR Phase: Enhance to enterprise-grade quality

Test Coverage Areas:
- URL detection and link generation (with security validation)
- Boolean recognition and rendering (checkmarks, badges, text)
- Date parsing and localization
- Number formatting with thousands separators
- Currency detection and formatting
- Phone number recognition and formatting
- IP address validation and highlighting
- Security: XSS protection and input sanitization
- Performance with large datasets
- Integration with existing directive functionality

CLAUDE.md Code Excellence Compliance:
- DRY Principle: Reusable test fixtures and helpers
- Single Responsibility: Each test validates one specific behavior
- SOLID Principles: Clear test structure with separation of concerns
"""

import pytest
from unittest.mock import Mock, MagicMock

from sphinxcontrib.jsontable.directives.data_type_renderer import DataTypeRenderer
from sphinxcontrib.jsontable.directives.directive_core import JsonTableDirective
from sphinxcontrib.jsontable.directives.validators import JsonTableError


class TestDataTypeRenderer:
    """Test suite for DataTypeRenderer functionality."""

    @pytest.fixture
    def renderer(self):
        """Create DataTypeRenderer instance for testing."""
        return DataTypeRenderer()

    @pytest.fixture
    def custom_renderer(self):
        """Create DataTypeRenderer with custom settings."""
        return DataTypeRenderer(
            auto_format=True,
            boolean_style="badge",
            date_format="short", 
            number_format="scientific",
            url_target="_self"
        )

    @pytest.fixture
    def sample_table_data(self):
        """Sample table data with various data types."""
        return [
            ["url", "active", "created", "price", "phone", "ip"],
            ["https://example.com", "true", "2024-01-15", "$1,234.56", "+1-555-123-4567", "192.168.1.1"],
            ["http://test.org", "false", "2023-12-01", "€999.99", "(555) 987-6543", "10.0.0.1"],
            ["https://secure.net", "yes", "2024/02/14", "¥50,000", "555.123.4567", "::1"],
            ["invalid-url", "no", "invalid-date", "not-currency", "invalid-phone", "invalid-ip"]
        ]

    @pytest.fixture
    def large_table_data(self):
        """Large table data for performance testing."""
        headers = ["url", "status", "date", "amount"]
        data = [headers]
        for i in range(1000):
            data.append([
                f"https://example{i}.com",
                "true" if i % 2 == 0 else "false",
                "2024-01-15",
                f"${i * 10}.00"
            ])
        return data

    # RED Phase Tests - These should initially fail

    def test_url_detection_and_rendering(self, renderer, sample_table_data):
        """Test URL detection and conversion to clickable links.
        
        Should detect valid URLs and render as HTML anchor tags with security attributes.
        """
        result = renderer.render_table_data(sample_table_data)
        
        # Expected: URLs converted to links with security attributes
        assert '<a href="https://example.com" target="_blank" rel="noopener noreferrer">https://example.com</a>' in result[1][0]
        assert '<a href="http://test.org" target="_blank" rel="noopener noreferrer">http://test.org</a>' in result[2][0]
        assert '<a href="https://secure.net" target="_blank" rel="noopener noreferrer">https://secure.net</a>' in result[3][0]
        
        # Invalid URLs should remain as escaped text
        assert "invalid-url" in result[4][0]
        assert "<a href=" not in result[4][0]

    def test_boolean_detection_and_checkmark_rendering(self, renderer, sample_table_data):
        """Test boolean detection and checkmark rendering.
        
        Should detect various boolean representations and render as checkmarks.
        """
        result = renderer.render_table_data(sample_table_data)
        
        # Expected: Boolean values rendered as checkmarks
        assert result[1][1] == "✓"  # "true"
        assert result[2][1] == "✗"  # "false" 
        assert result[3][1] == "✓"  # "yes"
        assert result[4][1] == "✗"  # "no"

    def test_boolean_badge_style_rendering(self, custom_renderer, sample_table_data):
        """Test boolean rendering with badge style.
        
        Should render booleans as HTML badges with appropriate classes.
        """
        result = custom_renderer.render_table_data(sample_table_data)
        
        # Expected: Boolean values rendered as badges
        assert '<span class="badge badge-success">Yes</span>' in result[1][1]
        assert '<span class="badge badge-secondary">No</span>' in result[2][1]

    def test_date_detection_and_formatting(self, renderer, sample_table_data):
        """Test date detection and localized formatting.
        
        Should detect various date formats and render in localized format.
        """
        result = renderer.render_table_data(sample_table_data)
        
        # Expected: Dates formatted to localized format
        assert "January 15, 2024" in result[1][2]  # 2024-01-15
        assert "December 01, 2023" in result[2][2]  # 2023-12-01
        assert "February 14, 2024" in result[3][2]  # 2024/02/14
        
        # Invalid dates should remain as escaped text
        assert "invalid-date" in result[4][2]

    def test_date_short_format_rendering(self, custom_renderer, sample_table_data):
        """Test date rendering with short format.
        
        Should render dates in MM/DD/YYYY format.
        """
        result = custom_renderer.render_table_data(sample_table_data)
        
        # Expected: Dates in short format
        assert "01/15/2024" in result[1][2]  # 2024-01-15
        assert "12/01/2023" in result[2][2]  # 2023-12-01

    def test_currency_detection_and_formatting(self, renderer, sample_table_data):
        """Test currency detection and enhanced formatting.
        
        Should detect currency values and wrap in appropriate HTML.
        """
        result = renderer.render_table_data(sample_table_data)
        
        # Expected: Currency values wrapped in spans
        assert '<span class="currency">$1,234.56</span>' in result[1][3]
        assert '<span class="currency">€999.99</span>' in result[2][3]
        assert '<span class="currency">¥50,000</span>' in result[3][3]
        
        # Non-currency should remain as text
        assert "not-currency" in result[4][3]
        assert '<span class="currency">' not in result[4][3]

    def test_phone_number_detection_and_formatting(self, renderer, sample_table_data):
        """Test phone number detection and formatting.
        
        Should detect phone numbers and wrap in appropriate HTML.
        """
        result = renderer.render_table_data(sample_table_data)
        
        # Expected: Phone numbers wrapped in spans
        assert '<span class="phone">+1-555-123-4567</span>' in result[1][4]
        assert '<span class="phone">(555) 987-6543</span>' in result[2][4]
        assert '<span class="phone">555.123.4567</span>' in result[3][4]
        
        # Invalid phone should remain as text
        assert "invalid-phone" in result[4][4]
        assert '<span class="phone">' not in result[4][4]

    def test_ip_address_detection_and_highlighting(self, renderer, sample_table_data):
        """Test IP address detection and highlighting.
        
        Should detect IP addresses and highlight with code styling.
        """
        result = renderer.render_table_data(sample_table_data)
        
        # Expected: IP addresses wrapped in code tags
        assert '<code class="ip-address">192.168.1.1</code>' in result[1][5]
        assert '<code class="ip-address">10.0.0.1</code>' in result[2][5]
        assert '<code class="ip-address">::1</code>' in result[3][5]
        
        # Invalid IP should remain as text
        assert "invalid-ip" in result[4][5]
        assert '<code class="ip-address">' not in result[4][5]

    def test_number_formatting_with_separators(self, renderer):
        """Test number detection and formatting with thousands separators.
        
        Should format numbers with appropriate separators and decimal precision.
        """
        test_data = [
            ["numbers"],
            ["1234567"],
            ["1234.56"],
            ["123"],
            ["-987654.321"]
        ]
        
        result = renderer.render_table_data(test_data)
        
        # Expected: Numbers formatted with separators
        assert "1,234,567" in result[1][0]
        assert "1,234.56" in result[2][0]
        assert "123" in result[3][0]  # Small numbers unchanged
        assert "-987,654.32" in result[4][0]

    def test_scientific_notation_rendering(self, custom_renderer):
        """Test number rendering in scientific notation.
        
        Should render numbers in scientific notation when specified.
        """
        test_data = [
            ["numbers"],
            ["1234567"],
            ["0.000123"]
        ]
        
        result = custom_renderer.render_table_data(test_data)
        
        # Expected: Numbers in scientific notation
        assert "1.23e+06" in result[1][0]
        assert "1.23e-04" in result[2][0]

    def test_email_detection_and_mailto_links(self, renderer):
        """Test email detection and mailto link generation.
        
        Should detect email addresses and convert to mailto links.
        """
        test_data = [
            ["contact"],
            ["user@example.com"],
            ["admin@test.org"],
            ["invalid-email"]
        ]
        
        result = renderer.render_table_data(test_data)
        
        # Expected: Email addresses converted to mailto links
        assert '<a href="mailto:user@example.com">user@example.com</a>' in result[1][0]
        assert '<a href="mailto:admin@test.org">admin@test.org</a>' in result[2][0]
        
        # Invalid email should remain as text
        assert "invalid-email" in result[3][0]
        assert "mailto:" not in result[3][0]

    def test_mixed_data_types_in_single_table(self, renderer):
        """Test handling of mixed data types within a single table.
        
        Should correctly identify and render different data types in the same table.
        """
        mixed_data = [
            ["url", "email", "active", "count", "price"],
            ["https://example.com", "user@test.com", "true", "1,234", "$56.78"],
            ["not-url", "not-email", "maybe", "not-number", "not-price"]
        ]
        
        result = renderer.render_table_data(mixed_data)
        
        # First row: All types should be detected and rendered
        assert '<a href="https://example.com"' in result[1][0]
        assert 'mailto:user@test.com' in result[1][1]
        assert result[1][2] == "✓"
        assert "1,234" in result[1][3]
        assert '<span class="currency">$56.78</span>' in result[1][4]
        
        # Second row: No types detected, should be escaped text
        assert "not-url" in result[2][0]
        assert "not-email" in result[2][1]
        assert "maybe" in result[2][2]
        assert "not-number" in result[2][3]
        assert "not-price" in result[2][4]

    def test_data_format_override_raw(self, renderer, sample_table_data):
        """Test data format override to disable formatting.
        
        Should return raw escaped text when format is set to 'raw'.
        """
        result = renderer.render_table_data(sample_table_data, data_format="raw")
        
        # Expected: No formatting applied, just escaped text
        assert "https://example.com" in result[1][0]
        assert "<a href=" not in result[1][0]
        assert "true" in result[1][1]
        assert "✓" not in result[1][1]

    def test_data_format_override_enhanced(self, renderer, sample_table_data):
        """Test data format override to enhanced formatting.
        
        Should apply all available formatting when format is set to 'enhanced'.
        """
        result = renderer.render_table_data(sample_table_data, data_format="enhanced")
        
        # Expected: All formatting applied
        assert '<a href="https://example.com"' in result[1][0]
        assert result[1][1] == "✓"

    # Security Tests

    def test_xss_protection_in_urls(self, renderer):
        """Test XSS protection in URL processing.
        
        Should properly escape malicious content in URLs.
        """
        malicious_data = [
            ["urls"],
            ['javascript:alert("xss")'],
            ['http://evil.com"><script>alert("xss")</script>'],
            ['https://example.com?param=<script>alert("xss")</script>']
        ]
        
        result = renderer.render_table_data(malicious_data)
        
        # Expected: Malicious content escaped or rejected
        for i, row in enumerate(result[1:], 1):
            for j, cell in enumerate(row):
                # No raw script tags should be present
                assert "<script>" not in cell
                
                # javascript: should not be rendered as clickable link
                if "javascript:" in cell:
                    assert "<a href=" not in cell
                
                # For URLs with script content, ensure proper escaping
                if i >= 2:  # Rows with actual script content
                    # Should have escaped angle brackets
                    if "script" in cell.lower():
                        assert "&lt;" in cell and "&gt;" in cell

    def test_html_injection_protection(self, renderer):
        """Test protection against HTML injection in data values.
        
        Should escape HTML special characters in all data types.
        """
        injection_data = [
            ["data"],
            ['<img src="x" onerror="alert(1)">'],
            ['</script><script>alert("xss")</script>'],
            ['"onmouseover="alert(1)"']
        ]
        
        result = renderer.render_table_data(injection_data)
        
        # Expected: HTML characters properly escaped
        for i, row in enumerate(result[1:]):
            for cell in row:
                # No raw HTML tags should be present
                assert "<img" not in cell
                assert "<script>" not in cell
                
                # Check specific escaping based on original content
                original = injection_data[i + 1][0]
                if "<" in original:
                    # HTML brackets should be escaped
                    assert "&lt;" in cell
                if '"' in original:
                    # Quotes should be escaped  
                    assert "&quot;" in cell

    def test_input_length_limits(self, renderer):
        """Test input length limits for security.
        
        Should truncate overly long inputs to prevent DoS attacks.
        """
        long_input = "a" * 2000  # Exceeds 1000 character limit
        test_data = [
            ["data"],
            [long_input]
        ]
        
        result = renderer.render_table_data(test_data)
        
        # Expected: Input truncated with ellipsis
        assert len(result[1][0]) < len(long_input)
        assert "..." in result[1][0]

    # Performance Tests

    def test_performance_large_dataset(self, renderer, large_table_data):
        """Test performance with large dataset (1000+ rows).
        
        Should handle large datasets efficiently without performance degradation.
        """
        import time
        
        start_time = time.perf_counter()
        result = renderer.render_table_data(large_table_data)
        end_time = time.perf_counter()
        
        # Performance requirement: < 500ms for 1000 rows
        processing_time = end_time - start_time
        assert processing_time < 0.5, f"Processing took {processing_time:.3f}s, expected < 0.5s"
        
        # Verify correctness
        assert len(result) == 1001  # Header + 1000 data rows
        # Verify some URLs were processed
        url_count = sum(1 for row in result[1:] if '<a href=' in row[0])
        assert url_count > 900  # Most URLs should be processed

    def test_memory_efficiency_large_dataset(self, renderer, large_table_data):
        """Test memory efficiency with large dataset.
        
        Should maintain reasonable memory usage during processing.
        """
        import tracemalloc
        
        tracemalloc.start()
        
        result = renderer.render_table_data(large_table_data)
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Memory requirement: Peak memory < 20MB for 1000 x 4 dataset
        peak_mb = peak / 1024 / 1024
        assert peak_mb < 20, f"Peak memory usage {peak_mb:.2f}MB, expected < 20MB"

    def test_regex_compilation_efficiency(self, renderer):
        """Test that regex patterns are compiled efficiently.
        
        Should use pre-compiled patterns for performance.
        """
        # Verify patterns are compiled (should have 'pattern' attribute)
        assert hasattr(renderer.URL_PATTERN, 'pattern')
        assert hasattr(renderer.EMAIL_PATTERN, 'pattern')
        assert hasattr(renderer.BOOLEAN_PATTERNS['true'], 'pattern')

    # Error Handling Tests

    def test_empty_table_data_error(self, renderer):
        """Test error handling for empty table data."""
        with pytest.raises(JsonTableError, match="Table data cannot be empty"):
            renderer.render_table_data([])

    def test_malformed_table_data_handling(self, renderer):
        """Test handling of malformed table data.
        
        Should gracefully handle inconsistent row lengths and missing data.
        """
        malformed_data = [
            ["col1", "col2", "col3"],
            ["data1"],  # Missing columns
            ["data1", "data2"],  # Missing one column
            ["data1", "data2", "data3", "extra"]  # Extra column
        ]
        
        result = renderer.render_table_data(malformed_data)
        
        # Expected: Should not crash and handle gracefully
        assert len(result) == 4
        assert len(result[0]) == 3  # Header preserved
        
        # Missing data should be handled gracefully
        for row in result[1:]:
            assert isinstance(row, list)

    def test_none_and_empty_cell_handling(self, renderer):
        """Test handling of None and empty cells.
        
        Should handle None values and empty strings gracefully.
        """
        test_data = [
            ["data"],
            [None],
            [""],
            [" "],  # Whitespace only
        ]
        
        result = renderer.render_table_data(test_data)
        
        # Expected: None and empty values handled without errors
        assert len(result) == 4
        for row in result:
            assert isinstance(row, list)
            for cell in row:
                assert isinstance(cell, str)

    def test_unicode_and_special_characters(self, renderer):
        """Test handling of Unicode and special characters.
        
        Should properly handle international characters and symbols.
        """
        unicode_data = [
            ["data"],
            ["日本語テスト"],
            ["émoji test 🎉"],
            ["Ελληνικά"],
            ["中文测试"]
        ]
        
        result = renderer.render_table_data(unicode_data)
        
        # Expected: Unicode characters preserved and properly escaped
        assert "日本語テスト" in result[1][0]
        assert "🎉" in result[2][0]
        assert "Ελληνικά" in result[3][0]
        assert "中文测试" in result[4][0]

    # Integration Tests

    def test_header_row_preservation(self, renderer, sample_table_data):
        """Test that header row is preserved unchanged.
        
        Should not apply formatting to header row.
        """
        result = renderer.render_table_data(sample_table_data)
        
        # Expected: Header row identical to input
        assert result[0] == sample_table_data[0]
        
        # Data rows should be processed
        assert result[1] != sample_table_data[1]  # Should be different due to formatting

    def test_custom_renderer_configuration(self):
        """Test custom renderer configuration options.
        
        Should respect all configuration options during initialization.
        """
        custom_renderer = DataTypeRenderer(
            auto_format=False,
            boolean_style="text",
            date_format="iso",
            number_format="raw",
            url_target="_parent"
        )
        
        # Verify configuration
        assert custom_renderer.auto_format is False
        assert custom_renderer.boolean_style == "text"
        assert custom_renderer.date_format == "iso"
        assert custom_renderer.number_format == "raw"
        assert custom_renderer.url_target == "_parent"

    def test_type_detection_priority_order(self, renderer):
        """Test that type detection follows correct priority order.
        
        Should detect more specific types before general ones.
        """
        # Test data that could match multiple patterns
        test_data = [
            ["ambiguous"],
            ["1234"],  # Could be number or text
            ["$123"],  # Currency (should take priority over number)
            ["true"],  # Boolean
        ]
        
        result = renderer.render_table_data(test_data)
        
        # Expected: More specific types detected first
        assert "1,234" in result[1][0]  # Detected as number
        assert '<span class="currency">$123</span>' in result[2][0]  # Currency priority
        assert result[3][0] == "✓"  # Boolean detected


class TestJsonTableDirectiveIntegration:
    """Test integration of data type rendering with JsonTableDirective."""

    @pytest.fixture
    def mock_directive(self):
        """Create mock JsonTableDirective for testing."""
        directive = Mock(spec=JsonTableDirective)
        directive.options = {}
        directive.env = Mock()
        directive.env.config = Mock()
        directive.env.srcdir = "/test/src"
        return directive

    def test_auto_format_option_integration(self, mock_directive):
        """Test auto-format option integration with directive.
        
        Should enable/disable automatic formatting based on directive option.
        """
        # This test will be implemented in GREEN phase
        mock_directive.options = {
            "auto-format": True,
            "data-format": "enhanced"
        }
        
        pytest.skip("Integration test - will be implemented in GREEN phase")

    def test_boolean_style_option_integration(self, mock_directive):
        """Test boolean style option integration.
        
        Should apply correct boolean style based on directive option.
        """
        mock_directive.options = {
            "boolean-style": "badge",
            "auto-format": True
        }
        
        pytest.skip("Integration test - will be implemented in GREEN phase")

    def test_date_format_option_integration(self, mock_directive):
        """Test date format option integration.
        
        Should apply correct date format based on directive option.
        """
        mock_directive.options = {
            "date-format": "short",
            "auto-format": True
        }
        
        pytest.skip("Integration test - will be implemented in GREEN phase")

    def test_backward_compatibility_no_auto_format(self, mock_directive):
        """Test backward compatibility when auto-format is not specified.
        
        Should work exactly as before when new options are not specified.
        """
        mock_directive.options = {
            "header": True,
            "limit": 10
        }
        
        pytest.skip("Backward compatibility test - will be implemented in GREEN phase")


# Performance Benchmark Tests
class TestDataTypeRenderingPerformance:
    """Performance benchmark tests for data type rendering."""

    @pytest.fixture
    def massive_table_data(self):
        """Create massive table for performance testing."""
        headers = ["url", "email", "active", "date", "price"]
        data = [headers]
        for i in range(5000):
            data.append([
                f"https://example{i}.com",
                f"user{i}@test.com", 
                "true" if i % 2 == 0 else "false",
                "2024-01-15",
                f"${i * 10}.00"
            ])
        return data

    @pytest.mark.performance
    def test_rendering_performance_massive_dataset(self, massive_table_data):
        """Test rendering performance with massive dataset."""
        renderer = DataTypeRenderer()
        
        import time
        start_time = time.perf_counter()
        
        result = renderer.render_table_data(massive_table_data)
        
        end_time = time.perf_counter()
        
        # Performance requirement: < 2s for 5K rows x 5 columns
        processing_time = end_time - start_time
        assert processing_time < 2.0, f"Processing took {processing_time:.3f}s, expected < 2.0s"
        
        # Verify correctness
        assert len(result) == 5001  # Header + 5K rows
        
        # Verify type detection worked
        url_count = sum(1 for row in result[1:] if '<a href=' in row[0])
        email_count = sum(1 for row in result[1:] if 'mailto:' in row[1])
        assert url_count > 4900  # Most URLs should be processed
        assert email_count > 4900  # Most emails should be processed

    @pytest.mark.performance
    def test_type_detection_performance(self):
        """Test individual type detection performance."""
        renderer = DataTypeRenderer()
        
        test_values = [
            "https://example.com",
            "user@test.com",
            "true",
            "2024-01-15",
            "$1,234.56"
        ] * 1000  # 5000 values
        
        import time
        start_time = time.perf_counter()
        
        for value in test_values:
            renderer._detect_and_render(value)
        
        end_time = time.perf_counter()
        
        # Performance requirement: < 100ms for 5000 type detections
        processing_time = end_time - start_time
        assert processing_time < 0.1, f"Type detection took {processing_time:.3f}s, expected < 0.1s"

    @pytest.mark.memory
    def test_memory_efficiency_type_detection(self):
        """Test memory efficiency of type detection."""
        import tracemalloc
        
        renderer = DataTypeRenderer()
        test_data = [
            ["url", "email", "status"],
            ["https://example.com", "user@test.com", "true"]
        ] * 1000  # Large dataset
        
        tracemalloc.start()
        
        result = renderer.render_table_data(test_data)
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Memory requirement: Peak memory < 30MB for large dataset
        peak_mb = peak / 1024 / 1024
        assert peak_mb < 30, f"Peak memory usage {peak_mb:.2f}MB, expected < 30MB"