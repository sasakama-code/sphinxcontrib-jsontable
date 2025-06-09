"""Basic coverage improvement tests.

Simple tests to improve code coverage for frequently used but untested methods.
Focuses on straightforward test cases that don't require complex mocking.

Created: 2025-06-09
"""

import json
import tempfile
from pathlib import Path

import pytest

from sphinxcontrib.jsontable.directives import (
    JsonTableError,
    ensure_file_exists,
    is_safe_path,
    validate_not_empty,
)


class TestUtilityFunctions:
    """Test utility functions for improved coverage."""

    def test_ensure_file_exists_valid_file(self):
        """Test ensure_file_exists with valid file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write('{"test": "data"}')
            temp_path = Path(f.name)

        try:
            # Should not raise an exception
            ensure_file_exists(temp_path)
        finally:
            temp_path.unlink()

    def test_ensure_file_exists_missing_file(self):
        """Test ensure_file_exists with missing file."""
        missing_path = Path("/nonexistent/file.json")

        with pytest.raises(FileNotFoundError):
            ensure_file_exists(missing_path)

    def test_is_safe_path_safe_paths(self):
        """Test is_safe_path with safe paths."""
        source_dir = Path("/safe/source")

        safe_paths = [
            source_dir / "data.json",
            source_dir / "subdir" / "file.json",
            source_dir / "nested" / "deep" / "data.json",
        ]

        for path in safe_paths:
            assert is_safe_path(path, source_dir) is True

    def test_is_safe_path_unsafe_paths(self):
        """Test is_safe_path with unsafe paths."""
        source_dir = Path("/safe/source")

        unsafe_paths = [
            Path("/etc/passwd"),
            Path("../../../etc/passwd"),
            source_dir / ".." / ".." / "dangerous.json",
            Path("/root/secret.json"),
        ]

        for path in unsafe_paths:
            assert is_safe_path(path, source_dir) is False

    def test_validate_not_empty_valid_content(self):
        """Test validate_not_empty with valid content."""
        valid_contents = [
            ["line1", "line2"],
            ["single line"],
            ["", "not empty"],  # Has non-empty content
            [" ", "content"],  # Has actual content
        ]

        for content in valid_contents:
            # Should not raise an exception
            validate_not_empty(content, "test error")

    def test_validate_not_empty_invalid_content(self):
        """Test validate_not_empty with invalid content."""
        invalid_contents = [
            [],  # Empty list
            None,  # None value
            "",  # Empty string
            False,  # Boolean False
        ]

        for content in invalid_contents:
            with pytest.raises(JsonTableError):
                validate_not_empty(content, "test error")


class TestDirectiveBasicFunctionality:
    """Test basic directive functionality for coverage."""

    def test_json_table_error_creation(self):
        """Test JsonTableError creation and message."""
        error_message = "Test error message"
        error = JsonTableError(error_message)

        assert str(error) == error_message
        assert isinstance(error, Exception)

    def test_json_table_error_inheritance(self):
        """Test JsonTableError inheritance."""
        error = JsonTableError("test")

        assert isinstance(error, Exception)
        assert isinstance(error, JsonTableError)


class TestDataProcessing:
    """Test data processing functionality."""

    def test_basic_json_processing(self):
        """Test basic JSON data processing."""
        # Test valid JSON data
        valid_json_data = [
            {"name": "test1", "value": 100},
            {"name": "test2", "value": 200},
        ]

        # Convert to JSON string and parse back
        json_string = json.dumps(valid_json_data)
        parsed_data = json.loads(json_string)

        assert len(parsed_data) == 2
        assert parsed_data[0]["name"] == "test1"
        assert parsed_data[1]["value"] == 200

    def test_json_error_handling(self):
        """Test JSON parsing error handling."""
        invalid_json_strings = [
            '{"invalid": json}',  # Missing quotes
            '{"incomplete":',  # Incomplete
            "{invalid}",  # Invalid structure
            "",  # Empty string
        ]

        for invalid_json in invalid_json_strings:
            with pytest.raises(json.JSONDecodeError):
                json.loads(invalid_json)

    def test_data_type_conversion(self):
        """Test various data type conversions."""
        test_values = [
            (None, ""),
            (123, "123"),
            (45.67, "45.67"),
            (True, "True"),
            (False, "False"),
            ("string", "string"),
            ([], "[]"),
            ({}, "{}"),
        ]

        for input_value, expected_str in test_values:
            result = str(input_value) if input_value is not None else ""
            if input_value is None:
                assert result == expected_str
            else:
                assert str(input_value) == expected_str


class TestFileOperations:
    """Test file operation scenarios."""

    def test_temp_file_operations(self):
        """Test temporary file operations."""
        test_data = {"test": "data", "number": 123}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(test_data, f)
            temp_path = Path(f.name)

        try:
            # Test file exists
            assert temp_path.exists()

            # Test file reading
            with open(temp_path) as f:
                loaded_data = json.load(f)

            assert loaded_data == test_data

        finally:
            # Cleanup
            if temp_path.exists():
                temp_path.unlink()

    def test_path_operations(self):
        """Test path operations."""
        # Test path creation and manipulation
        base_path = Path("/test/base")
        relative_path = "data/file.json"

        full_path = base_path / relative_path

        assert str(full_path) == "/test/base/data/file.json"
        assert full_path.name == "file.json"
        assert full_path.suffix == ".json"
        assert full_path.parent.name == "data"

    def test_path_security_scenarios(self):
        """Test various path security scenarios."""
        base_dir = Path("/secure/base")

        # Test various relative paths
        test_cases = [
            ("data.json", True),  # Simple file
            ("subdir/data.json", True),  # Subdirectory
            ("./data.json", True),  # Current directory
            ("../outside.json", False),  # Parent directory
            ("../../etc/passwd", False),  # Multiple parent traversal
            ("/absolute/path.json", False),  # Absolute path outside
        ]

        for test_path, expected_safe in test_cases:
            full_path = base_dir / test_path
            result = is_safe_path(full_path, base_dir)
            assert result == expected_safe, f"Path {test_path} safety check failed"


class TestErrorConditions:
    """Test various error conditions."""

    def test_empty_content_validation(self):
        """Test empty content validation scenarios."""
        error_message = "Content cannot be empty"

        # Test completely empty
        with pytest.raises(JsonTableError, match=error_message):
            validate_not_empty([], error_message)

        # Test None value
        with pytest.raises(JsonTableError, match=error_message):
            validate_not_empty(None, error_message)

    def test_file_not_found_scenarios(self):
        """Test file not found scenarios."""
        nonexistent_paths = [
            Path("/nonexistent/file.json"),
            Path("/tmp/missing/data.json"),
            Path("./does_not_exist.json"),
        ]

        for path in nonexistent_paths:
            with pytest.raises(FileNotFoundError):
                ensure_file_exists(path)

    def test_json_parsing_edge_cases(self):
        """Test JSON parsing edge cases."""
        edge_cases = [
            ("null", None),  # null value
            ("true", True),  # boolean true
            ("false", False),  # boolean false
            ("0", 0),  # zero
            ('""', ""),  # empty string
            ("[]", []),  # empty array
            ("{}", {}),  # empty object
            ('"unicode: 日本語"', "unicode: 日本語"),  # Unicode
        ]

        for json_str, expected in edge_cases:
            result = json.loads(json_str)
            assert result == expected

    def test_string_conversion_edge_cases(self):
        """Test string conversion edge cases."""
        edge_values = [
            float("inf"),  # Infinity
            float("-inf"),  # Negative infinity
            0.0,  # Zero float
            -0.0,  # Negative zero
            1e10,  # Scientific notation
            1e-10,  # Small scientific notation
        ]

        for value in edge_values:
            # Should not raise an exception
            result = str(value)
            assert isinstance(result, str)
            assert len(result) > 0


class TestDataStructureValidation:
    """Test data structure validation."""

    def test_json_structure_types(self):
        """Test various JSON structure types."""
        structures = [
            # Array of objects
            [{"id": 1, "name": "test1"}, {"id": 2, "name": "test2"}],
            # Array of arrays
            [["header1", "header2"], ["value1", "value2"]],
            # Single object
            {"key1": "value1", "key2": "value2"},
            # Mixed types
            [{"str": "text", "num": 123, "bool": True, "null": None}],
            # Nested structures
            [{"nested": {"deep": {"value": "test"}}}],
            # Empty structures
            [],
            {},
        ]

        for structure in structures:
            # Test JSON serialization round-trip
            json_str = json.dumps(structure)
            parsed = json.loads(json_str)
            assert parsed == structure

    def test_data_type_consistency(self):
        """Test data type consistency in structures."""
        # Test consistent object keys
        consistent_data = [
            {"name": "Alice", "age": 30, "city": "Tokyo"},
            {"name": "Bob", "age": 25, "city": "Osaka"},
            {"name": "Charlie", "age": 35, "city": "Kyoto"},
        ]

        # Extract all keys
        all_keys = set()
        for item in consistent_data:
            all_keys.update(item.keys())

        assert all_keys == {"name", "age", "city"}

        # Test that all items have the same keys
        for item in consistent_data:
            assert set(item.keys()) == all_keys

    def test_unicode_handling(self):
        """Test Unicode character handling."""
        unicode_data = [
            {"名前": "田中太郎", "年齢": 30},
            {"名前": "佐藤花子", "年齢": 25},
            {"emoji": "🎯🚀💡", "symbols": "①②③"},
        ]

        # Test JSON round-trip with Unicode
        json_str = json.dumps(unicode_data, ensure_ascii=False)
        parsed = json.loads(json_str)

        assert parsed == unicode_data
        assert "田中太郎" in json_str
        assert "🎯" in json_str
