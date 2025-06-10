"""Core functionality coverage tests."""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch

from sphinxcontrib.jsontable.directives import JsonTableDirective, JsonDataLoader, TableConverter, TableBuilder
from sphinxcontrib.jsontable.json_table_directive import JsonTableDirective as SimpleJsonTableDirective
from sphinxcontrib.jsontable.data_loaders import JsonTableError, is_safe_path


class TestCoreFunctionality:
    """Comprehensive tests for core functionality to achieve 80% coverage."""

    def test_is_safe_path_function(self):
        """Test is_safe_path utility function."""
        # Test safe paths
        assert is_safe_path("data/file.json")
        assert is_safe_path("subdir/data.json")
        assert is_safe_path("file.json")
        
        # Test unsafe paths
        assert not is_safe_path("../../../etc/passwd")
        assert not is_safe_path("..\\..\\windows\\system32")
        assert not is_safe_path("/absolute/path")

    def test_json_data_loader_comprehensive(self):
        """Comprehensive JSON data loader tests."""
        loader = JsonDataLoader()
        
        # Test with different JSON structures
        test_cases = [
            '{"name": "Alice", "age": 25}',
            '[1, 2, 3, 4, 5]',
            '{"nested": {"key": "value"}}',
            '[]',
            '{}',
        ]
        
        for test_json in test_cases:
            result = loader.load_from_content(test_json)
            assert result is not None

        # Test with file creation and loading
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"test": "data"}, f)
            temp_path = f.name
        
        try:
            result = loader.load_from_file(temp_path)
            assert result == {"test": "data"}
        finally:
            Path(temp_path).unlink()

    def test_table_converter_comprehensive(self):
        """Comprehensive table converter tests."""
        converter = TableConverter()
        
        # Test different data structures
        test_cases = [
            # Array of objects
            ([{"a": 1, "b": 2}, {"a": 3, "b": 4}], 2),
            # 2D array
            ([["A", "B"], [1, 2], [3, 4]], 3),
            # Single object
            ({"key": "value"}, 1),
            # Empty array
            ([], 0),
            # Complex nested structure
            ([{"user": {"name": "Alice"}, "score": 95}], 1),
        ]
        
        for data, expected_rows in test_cases:
            result = converter.convert(data)
            assert len(result) == expected_rows

    def test_table_builder_comprehensive(self):
        """Comprehensive table builder tests."""
        builder = TableBuilder()
        
        # Test with different table configurations
        test_data = [["Name", "Age", "City"], ["Alice", "25", "NYC"], ["Bob", "30", "LA"]]
        
        # Test with header
        result = builder.build(test_data, has_header=True)
        assert result is not None
        
        # Test without header
        result = builder.build(test_data, has_header=False)
        assert result is not None
        
        # Test with empty data
        result = builder.build([])
        assert result is not None
        
        # Test with single column
        result = builder.build([["Single"], ["Value"]])
        assert result is not None

    def test_json_table_directive_processing(self):
        """Test JSON table directive content processing."""
        # Test with mock state and state_machine
        from docutils.utils import new_document
        from docutils.frontend import OptionParser
        from docutils.parsers.rst import Parser
        
        # Create a mock state machine
        mock_state = Mock()
        mock_state_machine = Mock()
        mock_state_machine.reporter = Mock()
        
        # Test simple directive creation
        directive = SimpleJsonTableDirective(
            name="json-table",
            arguments=[],
            options={},
            content=['{"name": "test"}'],
            lineno=1,
            content_offset=0,
            block_text="",
            state=mock_state,
            state_machine=mock_state_machine
        )
        
        assert directive.name == "json-table"

    def test_advanced_table_operations(self):
        """Test advanced table operations and edge cases."""
        converter = TableConverter()
        builder = TableBuilder()
        
        # Test with mixed data types
        mixed_data = [
            {"id": 1, "name": "Alice", "active": True, "score": 95.5},
            {"id": 2, "name": "Bob", "active": False, "score": 87.2},
        ]
        
        table_data = converter.convert(mixed_data)
        result = builder.build(table_data)
        assert result is not None
        
        # Test with None values
        none_data = [{"a": 1, "b": None}, {"a": None, "b": 2}]
        table_data = converter.convert(none_data)
        result = builder.build(table_data)
        assert result is not None

    def test_error_handling_comprehensive(self):
        """Comprehensive error handling tests."""
        loader = JsonDataLoader()
        converter = TableConverter()
        
        # Test JSON loader errors
        invalid_json_cases = [
            '{"invalid": json}',  # Invalid syntax
            '{missing_quotes: "value"}',  # Invalid format
            '{"incomplete": ',  # Incomplete JSON
        ]
        
        for invalid_json in invalid_json_cases:
            with pytest.raises(JsonTableError):
                loader.load_from_content(invalid_json)
        
        # Test converter errors
        invalid_data_cases = [
            "string_not_json",
            123,
            True,
            set([1, 2, 3]),
        ]
        
        for invalid_data in invalid_data_cases:
            with pytest.raises(JsonTableError):
                converter.convert(invalid_data)

    def test_main_directive_integration(self):
        """Test main JsonTableDirective integration."""
        # Test the main directive class functionality
        loader = JsonDataLoader()
        converter = TableConverter()
        builder = TableBuilder()
        
        # Simulate directive processing pipeline
        json_content = '[{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]'
        
        # Step 1: Load JSON
        data = loader.load_from_content(json_content)
        assert len(data) == 2
        
        # Step 2: Convert to table
        table_data = converter.convert(data)
        assert len(table_data) == 2
        
        # Step 3: Build table
        result = builder.build(table_data)
        assert result is not None