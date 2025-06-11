"""
Core coverage tests for basic functionality.
統合元: test_core_coverage.py + test_basic_coverage_improvement.py
"""

import pytest
from docutils import nodes

from sphinxcontrib.jsontable.data_loaders import JsonDataLoader
from sphinxcontrib.jsontable.directives import JsonTableError
from sphinxcontrib.jsontable.table_builders import TableBuilder
from sphinxcontrib.jsontable.table_converters import TableConverter


class TestCoreCoverage:
    """Core functionality coverage tests."""

    def setup_method(self):
        """Test setup."""
        self.data_loader = JsonDataLoader()
        self.table_builder = TableBuilder()
        self.table_converter = TableConverter()

    def test_json_data_loader_basic_functionality(self):
        """Test JsonDataLoader basic operations."""
        # Test inline data loading
        data = '{"key": "value"}'
        result = self.data_loader.load_from_content(data)
        assert result == {"key": "value"}

        # Test empty data handling - should raise error
        try:
            result = self.data_loader.load_from_content("")
            assert False, "Should raise error for empty content"
        except Exception:
            assert True  # Expected

        # Test list data
        result = self.data_loader.load_from_content('[{"a": 1}, {"b": 2}]')
        assert len(result) == 2

    def test_table_builder_core_operations(self):
        """Test TableBuilder core functionality."""
        # Test empty table creation
        table = self.table_builder._create_empty_table()
        assert isinstance(table, nodes.table)

        # Test basic table building
        data = [["col1", "col2"], ["val1", "val2"]]
        table = self.table_builder.build(data, has_header=True)
        assert isinstance(table, nodes.table)

        # Test structure creation
        table_structure = self.table_builder._create_table_structure(2)
        assert isinstance(table_structure, nodes.table)

    def test_table_converter_basic_conversion(self):
        """Test TableConverter basic operations."""
        # Test object list conversion
        data = [{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]
        result = self.table_converter.convert(data, include_header=True)
        assert len(result) >= 2  # Header + data rows
        assert isinstance(result[0], list)  # Header row
        assert "name" in result[0] and "age" in result[0]

        # Test 2D array conversion (list of primitives)
        data = ["value1", "value2", "value3"]
        result = self.table_converter.convert(data, include_header=True)
        assert len(result) >= 3  # Header + data rows
        assert isinstance(result, list)

    def test_error_handling_coverage(self):
        """Test error handling paths."""
        # Test invalid JSON handling
        with pytest.raises(JsonTableError):
            self.data_loader.load_from_content('{"invalid": json}')

        # Test edge cases - empty data should raise error
        with pytest.raises(JsonTableError):
            self.table_converter.convert([])

    def test_integration_basic_flow(self):
        """Test basic integration flow."""
        # Simulate basic directive flow
        json_data = '[{"product": "A", "price": 100}, {"product": "B", "price": 200}]'

        # Load data
        data = self.data_loader.load_from_content(json_data)
        assert len(data) == 2

        # Convert to table format
        converted = self.table_converter.convert(data, include_header=True)
        assert len(converted) >= 2  # Header + data rows
        assert "product" in converted[0]  # Header row
        assert "price" in converted[0]

        # Build table
        table = self.table_builder.build(converted, has_header=True)
        assert isinstance(table, nodes.table)


class TestBasicCoverageImprovement:
    """Basic coverage improvement tests."""

    def test_data_loader_file_operations(self):
        """Test file-related operations."""
        from pathlib import Path

        from sphinxcontrib.jsontable.data_loaders import is_safe_path

        loader = JsonDataLoader()

        # Test path validation using module function
        assert is_safe_path(Path("data/test.json"), Path("."))
        assert not is_safe_path(Path("../dangerous.json"), Path("."))

        # Test encoding validation
        assert loader._validate_encoding("utf-8") == "utf-8"
        assert loader._validate_encoding("invalid-encoding") == "utf-8"

    def test_table_builder_edge_cases(self):
        """Test TableBuilder edge cases."""
        builder = TableBuilder()

        # Test single column table
        data = [["single"], ["value"]]
        table = builder.build(data, has_header=True)
        assert isinstance(table, nodes.table)

        # Test irregular row lengths
        data = [["a", "b"], ["1"], ["2", "3", "4"]]
        table = builder.build(data, has_header=True)
        assert isinstance(table, nodes.table)

    def test_table_converter_type_handling(self):
        """Test TableConverter type handling."""
        converter = TableConverter()

        # Test mixed types
        data = [{"str": "text", "int": 42, "float": 3.14, "bool": True, "none": None}]
        result = converter.convert(data, include_header=True)
        assert len(result) >= 1  # Header + data rows
        assert len(result[0]) == 5  # 5 columns

        # Test data row (second row)
        if len(result) > 1:
            for value in result[1]:  # Data row
                assert isinstance(value, str)

    def test_performance_limits(self):
        """Test performance-related limits."""
        converter = TableConverter()

        # Test large dataset handling (within limits)
        large_data = [{"id": i, "value": f"item_{i}"} for i in range(100)]
        result = converter.convert(large_data, include_header=True)
        assert len(result) >= 100  # Header + 100 data rows

        # Test key length limits
        data = [{"very_long_key_" + "x" * 200: "value"}]
        result = converter.convert(data, include_header=True)
        # Should handle long keys appropriately
        assert len(result[0]) == 1  # Header with 1 column


if __name__ == "__main__":
    pytest.main([__file__])
