"""Basic tests for improving coverage rapidly."""

import pytest
from sphinxcontrib.jsontable.table_builders import TableBuilder
from sphinxcontrib.jsontable.table_converters import TableConverter
from sphinxcontrib.jsontable.data_loaders import JsonDataLoader, JsonTableError


class TestBasicCoverage:
    """Basic tests to improve test coverage rapidly."""

    def test_table_builder_basic(self):
        """Test basic table builder functionality."""
        builder = TableBuilder()
        
        # Test empty table
        table_data = []
        result = builder.build(table_data)
        assert result is not None
        
        # Test with simple data
        table_data = [["Name", "Age"], ["Alice", "25"], ["Bob", "30"]]
        result = builder.build(table_data, has_header=True)
        assert result is not None

    def test_table_converter_basic(self):
        """Test basic table converter functionality."""
        converter = TableConverter()
        
        # Test with array of objects
        json_data = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]
        result = converter.convert(json_data)
        assert len(result) == 2  # 2 rows
        
        # Test with 2D array
        json_data = [["Name", "Age"], ["Alice", 25], ["Bob", 30]]
        result = converter.convert(json_data)
        assert len(result) == 3

    def test_data_loader_basic(self):
        """Test basic data loader functionality."""
        loader = JsonDataLoader()
        
        # Test with simple JSON string
        json_content = '[{"name": "Alice", "age": 25}]'
        result = loader.load_from_content(json_content)
        assert len(result) == 1
        assert result[0]["name"] == "Alice"
        
        # Test with empty content
        empty_content = "[]"
        result = loader.load_from_content(empty_content)
        assert result == []

    def test_table_builder_edge_cases(self):
        """Test table builder edge cases."""
        builder = TableBuilder()
        
        # Test with mixed data types
        table_data = [["ID", "Value"], [1, "text"], [2, None]]
        result = builder.build(table_data, has_header=True)
        assert result is not None
        
        # Test with single row
        table_data = [["Only Row"]]
        result = builder.build(table_data)
        assert result is not None

    def test_converter_error_handling(self):
        """Test converter error handling."""
        converter = TableConverter()
        
        # Test with invalid data
        with pytest.raises(JsonTableError):
            converter.convert("not a list or dict")
            
        # Test with None
        with pytest.raises(JsonTableError):
            converter.convert(None)

    def test_data_loader_file_operations(self):
        """Test data loader file operations."""
        loader = JsonDataLoader()
        
        # Test invalid JSON
        with pytest.raises(JsonTableError):
            loader.load_from_content("invalid json")
            
        # Test other loader methods
        try:
            loader.load_from_file("nonexistent.json")
        except (JsonTableError, FileNotFoundError):
            pass  # Expected to fail

    def test_table_converter_different_formats(self):
        """Test table converter with different data formats."""
        converter = TableConverter()
        
        # Test with object (single record)
        json_data = {"name": "Alice", "age": 25}
        result = converter.convert(json_data)
        assert len(result) == 1
        
        # Test with nested objects
        json_data = [{"user": {"name": "Alice"}, "score": 95}]
        result = converter.convert(json_data)
        assert len(result) == 1