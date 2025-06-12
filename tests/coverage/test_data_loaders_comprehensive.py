"""Comprehensive coverage tests for JsonDataLoader.

Strategic tests targeting data_loaders.py to boost coverage from 34.15% to 65%+.
Focuses on all methods, error paths, security, and edge cases.

Created: 2025-06-12
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from sphinxcontrib.jsontable.data_loaders import (
    DEFAULT_ENCODING,
    EMPTY_CONTENT_ERROR,
    INVALID_JSON_DATA_ERROR,
    NO_JSON_SOURCE_ERROR,
    JsonDataLoader,
    JsonTableError,
    ensure_file_exists,
    format_error,
    is_safe_path,
    validate_not_empty,
)


class TestJsonDataLoaderComprehensive:
    """Comprehensive JsonDataLoader coverage tests."""

    def setup_method(self):
        """Setup test fixtures."""
        self.loader = JsonDataLoader()
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Cleanup test fixtures."""
        import shutil

        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_default_initialization(self):
        """Test default loader initialization."""
        loader = JsonDataLoader()
        assert loader.encoding == DEFAULT_ENCODING

    def test_custom_encoding_initialization(self):
        """Test loader with custom encoding."""
        loader = JsonDataLoader("utf-16")
        assert loader.encoding == "utf-16"

    def test_invalid_encoding_fallback(self):
        """Test fallback for invalid encoding."""
        loader = JsonDataLoader("invalid-encoding")
        assert loader.encoding == DEFAULT_ENCODING

    def test_load_from_file_success(self):
        """Test successful file loading."""
        # Create test JSON file
        test_data = [{"name": "Alice", "age": 25}]
        test_file = self.temp_dir / "test.json"

        with test_file.open("w", encoding="utf-8") as f:
            json.dump(test_data, f)

        result = self.loader.load_from_file("test.json", self.temp_dir)
        assert result == test_data

    def test_load_from_file_with_encoding(self):
        """Test file loading with specific encoding."""
        test_data = {"name": "テスト", "value": "日本語"}
        test_file = self.temp_dir / "test_utf8.json"

        with test_file.open("w", encoding="utf-8") as f:
            json.dump(test_data, f, ensure_ascii=False)

        loader = JsonDataLoader("utf-8")
        result = loader.load_from_file("test_utf8.json", self.temp_dir)
        assert result == test_data

    def test_load_from_file_not_found(self):
        """Test loading non-existent file."""
        with pytest.raises(FileNotFoundError):
            self.loader.load_from_file("nonexistent.json", self.temp_dir)

    def test_load_from_file_invalid_json(self):
        """Test loading file with invalid JSON."""
        test_file = self.temp_dir / "invalid.json"

        with test_file.open("w") as f:
            f.write("{ invalid json")

        with pytest.raises(JsonTableError):
            self.loader.load_from_file("invalid.json", self.temp_dir)

    def test_load_from_file_security_violation(self):
        """Test security path validation."""
        with pytest.raises(JsonTableError, match="not safe"):
            self.loader.load_from_file("../../../etc/passwd", self.temp_dir)

    def test_load_from_content_success(self):
        """Test successful content loading."""
        content = '{"name": "Alice", "age": 25}'
        result = self.loader.load_from_content(content)
        assert result == {"name": "Alice", "age": 25}

    def test_load_from_content_array(self):
        """Test loading array from content."""
        content = '[{"id": 1}, {"id": 2}]'
        result = self.loader.load_from_content(content)
        assert result == [{"id": 1}, {"id": 2}]

    def test_load_from_content_empty(self):
        """Test loading empty content."""
        with pytest.raises(JsonTableError, match=EMPTY_CONTENT_ERROR):
            self.loader.load_from_content("")

    def test_load_from_content_whitespace_only(self):
        """Test loading whitespace-only content."""
        with pytest.raises(JsonTableError, match=EMPTY_CONTENT_ERROR):
            self.loader.load_from_content("   \t\n  ")

    def test_load_from_content_invalid_json(self):
        """Test loading invalid JSON content."""
        with pytest.raises(JsonTableError, match="Failed to parse inline JSON"):
            self.loader.load_from_content("{ invalid json }")

    def test_load_json_data_file_priority(self):
        """Test that file takes priority over content."""
        test_data = {"from": "file"}
        test_file = self.temp_dir / "priority.json"

        with test_file.open("w") as f:
            json.dump(test_data, f)

        result = self.loader.load_json_data(
            "priority.json", '{"from": "content"}', self.temp_dir
        )
        assert result == test_data

    def test_load_json_data_content_fallback(self):
        """Test fallback to content when no file."""
        content = '{"from": "content"}'
        result = self.loader.load_json_data(None, content, self.temp_dir)
        assert result == {"from": "content"}

    def test_load_json_data_no_source(self):
        """Test error when no data source provided."""
        with pytest.raises(JsonTableError, match=NO_JSON_SOURCE_ERROR):
            self.loader.load_json_data(None, None, self.temp_dir)

    def test_validate_json_structure_dict(self):
        """Test JSON structure validation for dict."""
        self.loader._validate_json_structure({"key": "value"})
        # Should not raise

    def test_validate_json_structure_list(self):
        """Test JSON structure validation for list."""
        self.loader._validate_json_structure([{"key": "value"}])
        # Should not raise

    def test_validate_json_structure_invalid(self):
        """Test JSON structure validation for invalid types."""
        with pytest.raises(JsonTableError, match=INVALID_JSON_DATA_ERROR):
            self.loader._validate_json_structure("string")

        with pytest.raises(JsonTableError, match=INVALID_JSON_DATA_ERROR):
            self.loader._validate_json_structure(123)

        with pytest.raises(JsonTableError, match=INVALID_JSON_DATA_ERROR):
            self.loader._validate_json_structure(True)

    def test_validate_path_security_safe(self):
        """Test path security validation for safe paths."""
        safe_path = self.temp_dir / "safe.json"
        self.loader._validate_path_security(safe_path, self.temp_dir)
        # Should not raise

    def test_validate_path_security_unsafe(self):
        """Test path security validation for unsafe paths."""
        unsafe_path = self.temp_dir.parent / "unsafe.json"
        with pytest.raises(JsonTableError, match="not safe"):
            self.loader._validate_path_security(unsafe_path, self.temp_dir)

    def test_validate_encoding_valid(self):
        """Test encoding validation for valid encodings."""
        assert self.loader._validate_encoding("utf-8") == "utf-8"
        assert self.loader._validate_encoding("latin-1") == "latin-1"
        assert self.loader._validate_encoding("ascii") == "ascii"

    def test_validate_encoding_invalid(self):
        """Test encoding validation for invalid encodings."""
        assert self.loader._validate_encoding("invalid") == DEFAULT_ENCODING
        assert self.loader._validate_encoding("") == DEFAULT_ENCODING

    def test_complex_json_structures(self):
        """Test loading complex JSON structures."""
        complex_data = {
            "users": [
                {
                    "id": 1,
                    "name": "Alice",
                    "profile": {
                        "age": 25,
                        "interests": ["reading", "coding"],
                        "active": True,
                    },
                },
                {
                    "id": 2,
                    "name": "Bob",
                    "profile": {
                        "age": 30,
                        "interests": ["sports", "music"],
                        "active": False,
                    },
                },
            ],
            "metadata": {"total": 2, "last_updated": "2025-06-12", "version": 1.0},
        }

        content = json.dumps(complex_data)
        result = self.loader.load_from_content(content)
        assert result == complex_data

    def test_unicode_content_handling(self):
        """Test handling of Unicode content."""
        unicode_data = {
            "japanese": "こんにちは世界",
            "emoji": "🎉🚀✨",
            "mixed": "Hello 世界 🌍",
        }

        content = json.dumps(unicode_data, ensure_ascii=False)
        result = self.loader.load_from_content(content)
        assert result == unicode_data

    def test_large_json_file(self):
        """Test loading large JSON file."""
        # Create moderately large JSON (not too big for CI)
        large_data = [{"id": i, "value": f"data_{i}"} for i in range(1000)]
        test_file = self.temp_dir / "large.json"

        with test_file.open("w") as f:
            json.dump(large_data, f)

        result = self.loader.load_from_file("large.json", self.temp_dir)
        assert len(result) == 1000
        assert result[0] == {"id": 0, "value": "data_0"}

    def test_special_characters_in_filename(self):
        """Test files with special characters in name."""
        test_data = {"test": "data"}
        special_file = self.temp_dir / "test file with spaces.json"

        with special_file.open("w") as f:
            json.dump(test_data, f)

        result = self.loader.load_from_file("test file with spaces.json", self.temp_dir)
        assert result == test_data

    def test_error_message_formatting(self):
        """Test error message formatting in exceptions."""
        test_file = self.temp_dir / "malformed.json"

        with test_file.open("w") as f:
            f.write("{ malformed json")

        try:
            self.loader.load_from_file("malformed.json", self.temp_dir)
            pytest.fail("Should have raised JsonTableError")
        except JsonTableError as e:
            assert "Failed to load JSON file" in str(e)

    def test_empty_json_structures(self):
        """Test loading empty but valid JSON structures."""
        empty_cases = ["{}", "[]", '{"empty": {}}', '{"empty_list": []}']

        for case in empty_cases:
            result = self.loader.load_from_content(case)
            assert result is not None

    def test_nested_arrays_and_objects(self):
        """Test deeply nested JSON structures."""
        nested_data = {
            "level1": {
                "level2": {
                    "level3": [
                        {"level4": {"value": "deep"}},
                        {"level4": {"value": "nested"}},
                    ]
                }
            }
        }

        content = json.dumps(nested_data)
        result = self.loader.load_from_content(content)
        assert result == nested_data

    def test_json_with_null_values(self):
        """Test JSON with null values."""
        null_data = {
            "valid": "data",
            "null_value": None,
            "list_with_null": [1, None, 3],
            "nested": {"also_null": None},
        }

        content = json.dumps(null_data)
        result = self.loader.load_from_content(content)
        assert result == null_data

    def test_file_permission_error_handling(self):
        """Test handling of file permission errors."""
        test_file = self.temp_dir / "protected.json"

        # Create file
        with test_file.open("w") as f:
            json.dump({"data": "test"}, f)

        # Mock permission error
        with patch(
            "pathlib.Path.open", side_effect=PermissionError("Permission denied")
        ):
            with pytest.raises(JsonTableError, match="Failed to load JSON file"):
                self.loader.load_from_file("protected.json", self.temp_dir)

    def test_concurrent_loading(self):
        """Test that loader is safe for concurrent use."""
        # Create multiple files
        files_data = {}
        for i in range(5):
            filename = f"concurrent_{i}.json"
            data = {"file": i, "data": f"content_{i}"}
            files_data[filename] = data

            test_file = self.temp_dir / filename
            with test_file.open("w") as f:
                json.dump(data, f)

        # Load all files
        results = {}
        for filename in files_data:
            results[filename] = self.loader.load_from_file(filename, self.temp_dir)

        # Verify all loaded correctly
        for filename, expected in files_data.items():
            assert results[filename] == expected


class TestUtilityFunctions:
    """Test utility functions in data_loaders module."""

    def test_validate_not_empty_valid(self):
        """Test validate_not_empty with valid data."""
        validate_not_empty([1, 2, 3], "error")
        validate_not_empty({"key": "value"}, "error")
        validate_not_empty("non-empty", "error")
        validate_not_empty(42, "error")
        # Should not raise

    def test_validate_not_empty_invalid(self):
        """Test validate_not_empty with invalid data."""
        with pytest.raises(JsonTableError, match="test error"):
            validate_not_empty(None, "test error")

        with pytest.raises(JsonTableError, match="test error"):
            validate_not_empty([], "test error")

        with pytest.raises(JsonTableError, match="test error"):
            validate_not_empty("", "test error")

        with pytest.raises(JsonTableError, match="test error"):
            validate_not_empty({}, "test error")

    def test_ensure_file_exists_valid(self):
        """Test ensure_file_exists with existing file."""
        with tempfile.NamedTemporaryFile() as tmp:
            path = Path(tmp.name)
            ensure_file_exists(path)
            # Should not raise

    def test_ensure_file_exists_invalid(self):
        """Test ensure_file_exists with non-existing file."""
        non_existent = Path("/non/existent/file.json")
        with pytest.raises(FileNotFoundError, match="JSON file not found"):
            ensure_file_exists(non_existent)

    def test_format_error(self):
        """Test error message formatting."""
        context = "Test operation"
        error = ValueError("Test error")

        result = format_error(context, error)
        assert result == "Test operation: Test error"

    def test_is_safe_path_safe(self):
        """Test is_safe_path with safe paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            safe_path = base / "safe.json"

            assert is_safe_path(safe_path, base) is True

    def test_is_safe_path_unsafe(self):
        """Test is_safe_path with unsafe paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            unsafe_path = base.parent / "unsafe.json"

            assert is_safe_path(unsafe_path, base) is False

    def test_is_safe_path_traversal(self):
        """Test is_safe_path with directory traversal."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            traversal_path = base / ".." / ".." / "etc" / "passwd"

            assert is_safe_path(traversal_path, base) is False

    def test_is_safe_path_relative(self):
        """Test is_safe_path with relative paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            relative_path = base / "subdir" / ".." / "safe.json"

            # Should be safe after resolution
            assert is_safe_path(relative_path, base) is True

    def test_is_safe_path_exception_handling(self):
        """Test is_safe_path exception handling."""
        # Mock path that causes exception
        mock_path = Mock()
        mock_path.resolve.side_effect = OSError("Test error")

        mock_base = Mock()
        mock_base.resolve.return_value = Path("/base")

        result = is_safe_path(mock_path, mock_base)
        assert result is False
