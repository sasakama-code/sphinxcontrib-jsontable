"""Comprehensive coverage tests for TableBuilder.

Strategic tests targeting table_builders.py to boost coverage from 13.75% to 60%+.
Focuses on all methods, error paths, and edge cases.

Created: 2025-06-12
"""

import pytest
from docutils import nodes

from sphinxcontrib.jsontable.table_builders import TableBuilder


class TestTableBuilderComprehensive:
    """Comprehensive TableBuilder coverage tests."""

    def setup_method(self):
        """Setup test fixtures."""
        self.builder = TableBuilder()

    def test_basic_table_build(self):
        """Test basic table building functionality."""
        table_data = [
            ["Name", "Age", "City"],
            ["Alice", "25", "Tokyo"],
            ["Bob", "30", "Osaka"],
        ]

        result = self.builder.build(table_data, has_header=True)

        assert isinstance(result, nodes.table)
        assert len(result.children) == 1  # tgroup

        tgroup = result.children[0]
        assert isinstance(tgroup, nodes.tgroup)
        assert tgroup.attributes["cols"] == 3

    def test_table_without_header(self):
        """Test table building without header."""
        table_data = [
            ["Alice", "25", "Tokyo"],
            ["Bob", "30", "Osaka"],
        ]

        result = self.builder.build(table_data, has_header=False)

        assert isinstance(result, nodes.table)
        tgroup = result.children[0]
        assert tgroup.attributes["cols"] == 3

        # Should have tbody but no thead
        tbody = None
        thead = None
        for child in tgroup.children:
            if isinstance(child, nodes.tbody):
                tbody = child
            elif isinstance(child, nodes.thead):
                thead = child

        assert tbody is not None
        assert thead is None

    def test_empty_table_data(self):
        """Test handling of empty table data."""
        result = self.builder.build([], has_header=False)

        assert isinstance(result, nodes.table)
        tgroup = result.children[0]
        assert tgroup.attributes["cols"] == 1

    def test_single_row_table(self):
        """Test table with single row."""
        table_data = [["Single", "Row", "Data"]]

        result = self.builder.build(table_data, has_header=True)

        assert isinstance(result, nodes.table)
        tgroup = result.children[0]
        assert tgroup.attributes["cols"] == 3

    def test_single_column_table(self):
        """Test table with single column."""
        table_data = [
            ["Header"],
            ["Row1"],
            ["Row2"],
        ]

        result = self.builder.build(table_data, has_header=True)

        assert isinstance(result, nodes.table)
        tgroup = result.children[0]
        assert tgroup.attributes["cols"] == 1

    def test_irregular_row_lengths(self):
        """Test table with irregular row lengths."""
        table_data = [
            ["Col1", "Col2", "Col3"],
            ["Data1", "Data2"],  # Shorter row
            ["Data3", "Data4", "Data5", "Data6"],  # Longer row
        ]

        result = self.builder.build(table_data, has_header=True)

        assert isinstance(result, nodes.table)
        tgroup = result.children[0]
        # Should handle max column count
        assert tgroup.attributes["cols"] >= 3

    def test_special_characters_in_content(self):
        """Test table with special characters."""
        table_data = [
            ["Name", "Description", "Symbols"],
            ["Test", "Special chars: <>&\"'", "←→↑↓"],
            ["Unicode", "日本語テスト", "♠♣♥♦"],
        ]

        result = self.builder.build(table_data, has_header=True)

        assert isinstance(result, nodes.table)
        # Content should be properly escaped/handled

    def test_very_long_content(self):
        """Test table with very long content."""
        long_text = "A" * 1000
        table_data = [
            ["Short", "Very Long"],
            ["Test", long_text],
        ]

        result = self.builder.build(table_data, has_header=True)

        assert isinstance(result, nodes.table)

    def test_none_values_in_data(self):
        """Test table with None values."""
        table_data = [
            ["Name", "Value", "Description"],
            ["Test", None, "None value"],
            [None, "Data", None],
        ]

        result = self.builder.build(table_data, has_header=True)

        assert isinstance(result, nodes.table)

    def test_numeric_string_data(self):
        """Test table with numeric string data."""
        table_data = [
            ["ID", "Price", "Quantity"],
            ["001", "19.99", "100"],
            ["002", "29.99", "50"],
        ]

        result = self.builder.build(table_data, has_header=True)

        assert isinstance(result, nodes.table)

    def test_mixed_content_types(self):
        """Test table with mixed content that gets stringified."""
        table_data = [
            ["String", "Number", "Boolean"],
            ["Text", "123", "True"],
            ["More", "456", "False"],
        ]

        result = self.builder.build(table_data, has_header=True)

        assert isinstance(result, nodes.table)

    def test_whitespace_handling(self):
        """Test table with various whitespace scenarios."""
        table_data = [
            ["Normal", "Spaces", "Tabs"],
            ["  Leading", "Trailing  ", "\tTab\t"],
            ["", "   ", "\n\n"],
        ]

        result = self.builder.build(table_data, has_header=True)

        assert isinstance(result, nodes.table)

    def test_create_table_structure_method(self):
        """Test _create_table_structure method directly."""
        # This tests internal method behavior
        result = self.builder._create_table_structure(3)

        assert isinstance(result, nodes.table)
        tgroup = result.children[0]
        assert tgroup.attributes["cols"] == 3
        colspecs = [
            child for child in tgroup.children if isinstance(child, nodes.colspec)
        ]
        assert len(colspecs) == 3

    def test_add_header_method(self):
        """Test _add_header method directly."""
        table = self.builder._create_table_structure(3)
        header_row = ["Col1", "Col2", "Col3"]

        self.builder._add_header(table, header_row)

        tgroup = table.children[0]
        thead = [child for child in tgroup.children if isinstance(child, nodes.thead)]
        assert len(thead) == 1

    def test_add_body_method(self):
        """Test _add_body method directly."""
        table = self.builder._create_table_structure(2)
        body_rows = [["Data1", "Data2"], ["Data3", "Data4"]]

        self.builder._add_body(table, body_rows, 2)

        tgroup = table.children[0]
        tbody = [child for child in tgroup.children if isinstance(child, nodes.tbody)]
        assert len(tbody) == 1

    def test_create_row_method(self):
        """Test _create_row method directly."""
        row_data = ["Cell1", "Cell2", "Cell3"]

        result = self.builder._create_row(row_data)

        assert isinstance(result, nodes.row)
        assert len(result.children) == 3

    def test_create_empty_table_method(self):
        """Test _create_empty_table method directly."""
        result = self.builder._create_empty_table()

        assert isinstance(result, nodes.table)
        tgroup = result.children[0]
        assert tgroup.attributes["cols"] == 1
        assert len(tgroup.children) > 1  # colspec + tbody

    def test_large_table_performance(self):
        """Test performance with large table."""
        # Create moderately large table (not too big for CI)
        table_data = [["Col1", "Col2", "Col3"]]
        for i in range(100):
            table_data.append([f"Data{i}1", f"Data{i}2", f"Data{i}3"])

        result = self.builder.build(table_data, has_header=True)

        assert isinstance(result, nodes.table)
        tgroup = result.children[0]
        assert tgroup.attributes["cols"] == 3

    def test_table_with_only_header(self):
        """Test table with only header row."""
        table_data = [["Header1", "Header2", "Header3"]]

        result = self.builder.build(table_data, has_header=True)

        assert isinstance(result, nodes.table)

    def test_table_attributes_verification(self):
        """Test that table attributes are properly set."""
        table_data = [
            ["Name", "Age"],
            ["Alice", "25"],
        ]

        result = self.builder.build(table_data, has_header=True)

        assert isinstance(result, nodes.table)
        assert hasattr(result, "attributes")

        tgroup = result.children[0]
        assert isinstance(tgroup, nodes.tgroup)
        assert tgroup.attributes["cols"] == 2

    def test_nested_content_handling(self):
        """Test handling of content that might need special processing."""
        table_data = [
            ["Type", "Content"],
            ["JSON", '{"key": "value"}'],
            ["HTML", "<p>Test</p>"],
            ["Code", "function() { return true; }"],
        ]

        result = self.builder.build(table_data, has_header=True)

        assert isinstance(result, nodes.table)

    def test_error_resilience(self):
        """Test error resilience with problematic data."""
        # Test with potentially problematic inputs
        problematic_data = [
            ["Normal", "Empty"],
            ["", ""],
            ["Test", None],
        ]

        try:
            result = self.builder.build(problematic_data, has_header=True)
            assert isinstance(result, nodes.table)
        except Exception:
            # Should handle gracefully
            pytest.fail("TableBuilder should handle problematic data gracefully")

    def test_builder_reusability(self):
        """Test that builder can be reused for multiple tables."""
        builder = TableBuilder()

        # Build first table
        table1_data = [["A", "B"], ["1", "2"]]
        result1 = builder.build(table1_data, has_header=True)

        # Build second table
        table2_data = [["X", "Y", "Z"], ["3", "4", "5"]]
        result2 = builder.build(table2_data, has_header=True)

        # Both should be valid and different
        assert isinstance(result1, nodes.table)
        assert isinstance(result2, nodes.table)
        assert result1 is not result2

    def test_edge_case_combinations(self):
        """Test various edge case combinations."""
        edge_cases = [
            # Empty table
            [],
            # Single cell
            [["Single"]],
            # Only empty strings
            [["", ""], ["", ""]],
            # Mixed empty and content
            [["Header", ""], ["", "Content"]],
        ]

        for table_data in edge_cases:
            result = self.builder.build(table_data, has_header=False)
            assert isinstance(result, nodes.table)
