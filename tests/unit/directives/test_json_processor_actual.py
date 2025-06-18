"""JSON Processor Tests - Phase 3.1 Coverage Boost.

Tests for actual json_processor.py methods to maximize coverage.
"""

import json
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from sphinxcontrib.jsontable.directives.json_processor import JsonProcessor
from sphinxcontrib.jsontable.directives.validators import JsonTableError


class TestJsonProcessorActual:
    """Test suite for JsonProcessor based on actual implementation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.base_path = Path("/test")
        self.processor = JsonProcessor(self.base_path)

    def test_init_default(self):
        """Test default initialization."""
        base_path = Path("/test")
        processor = JsonProcessor(base_path)
        assert processor.base_path == base_path
        assert processor.encoding == "utf-8"

    def test_init_with_encoding(self):
        """Test initialization with custom encoding."""
        processor = JsonProcessor(Path("/test"), encoding="utf-16")
        assert processor.encoding == "utf-16"

    def test_init_with_invalid_encoding(self):
        """Test initialization with invalid encoding falls back to utf-8."""
        processor = JsonProcessor(Path("/test"), encoding="invalid-encoding")
        assert processor.encoding == "utf-8"

    def test_validate_encoding_valid(self):
        """Test encoding validation with valid encoding."""
        result = self.processor._validate_encoding("iso-8859-1")
        assert result == "iso-8859-1"

    def test_validate_encoding_invalid(self):
        """Test encoding validation with invalid encoding."""
        with patch("sphinxcontrib.jsontable.directives.json_processor.logger"):
            result = self.processor._validate_encoding("totally-fake-encoding")
            assert result == "utf-8"

    def test_parse_inline_simple_object(self):
        """Test parsing simple JSON object."""
        content = ['{"name": "test", "value": 123}']
        result = self.processor.parse_inline(content)

        assert isinstance(result, dict)
        assert result["name"] == "test"
        assert result["value"] == 123

    def test_parse_inline_simple_array(self):
        """Test parsing simple JSON array."""
        content = ['[{"id": 1}, {"id": 2}]']
        result = self.processor.parse_inline(content)

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[1]["id"] == 2

    def test_parse_inline_multiline(self):
        """Test parsing multiline JSON."""
        content = [
            "{",
            '  "users": [',
            '    {"name": "Alice", "age": 30},',
            '    {"name": "Bob", "age": 25}',
            "  ],",
            '  "total": 2',
            "}",
        ]
        result = self.processor.parse_inline(content)

        assert "users" in result
        assert "total" in result
        assert len(result["users"]) == 2
        assert result["users"][0]["name"] == "Alice"
        assert result["total"] == 2

    def test_parse_inline_empty_content(self):
        """Test parsing empty content raises error."""
        with pytest.raises(JsonTableError):
            self.processor.parse_inline([])

    def test_parse_inline_invalid_json(self):
        """Test parsing invalid JSON raises error."""
        content = ['{"incomplete": ']
        with pytest.raises(JsonTableError):
            self.processor.parse_inline(content)

    def test_parse_inline_unicode_content(self):
        """Test parsing JSON with Unicode content."""
        content = ['{"message": "こんにちは", "name": "田中"}']
        result = self.processor.parse_inline(content)

        assert result["message"] == "こんにちは"
        assert result["name"] == "田中"

    def test_parse_inline_special_values(self):
        """Test parsing JSON with special values."""
        content = [
            "{",
            '  "null_value": null,',
            '  "bool_true": true,',
            '  "bool_false": false,',
            '  "number": 42.5,',
            '  "empty_string": "",',
            '  "empty_array": [],',
            '  "empty_object": {}',
            "}",
        ]
        result = self.processor.parse_inline(content)

        assert result["null_value"] is None
        assert result["bool_true"] is True
        assert result["bool_false"] is False
        assert result["number"] == 42.5
        assert result["empty_string"] == ""
        assert result["empty_array"] == []
        assert result["empty_object"] == {}

    @patch("sphinxcontrib.jsontable.directives.validators.ValidationUtils.is_safe_path")
    @patch(
        "sphinxcontrib.jsontable.directives.validators.ValidationUtils.ensure_file_exists"
    )
    def test_load_from_file_success(self, mock_ensure_exists, mock_is_safe):
        """Test successful file loading."""
        mock_is_safe.return_value = True
        mock_ensure_exists.return_value = None

        test_data = {"users": [{"name": "Alice"}]}
        mock_content = json.dumps(test_data)

        with patch("builtins.open", mock_open(read_data=mock_content)):
            result = self.processor.load_from_file("test.json")

        assert result == test_data
        mock_is_safe.assert_called_once()
        mock_ensure_exists.assert_called_once()

    @patch("sphinxcontrib.jsontable.directives.validators.ValidationUtils.is_safe_path")
    def test_load_from_file_unsafe_path(self, mock_is_safe):
        """Test file loading with unsafe path."""
        mock_is_safe.return_value = False

        with pytest.raises(JsonTableError):
            self.processor.load_from_file("../../../etc/passwd")

    @patch("sphinxcontrib.jsontable.directives.validators.ValidationUtils.is_safe_path")
    @patch(
        "sphinxcontrib.jsontable.directives.validators.ValidationUtils.ensure_file_exists"
    )
    def test_load_from_file_json_decode_error(self, mock_ensure_exists, mock_is_safe):
        """Test file loading with invalid JSON content."""
        mock_is_safe.return_value = True
        mock_ensure_exists.return_value = None

        invalid_json = "not valid json content"

        with patch("builtins.open", mock_open(read_data=invalid_json)):
            with pytest.raises(JsonTableError):
                self.processor.load_from_file("invalid.json")

    @patch("sphinxcontrib.jsontable.directives.validators.ValidationUtils.is_safe_path")
    @patch(
        "sphinxcontrib.jsontable.directives.validators.ValidationUtils.ensure_file_exists"
    )
    def test_load_from_file_unicode_error(self, mock_ensure_exists, mock_is_safe):
        """Test file loading with Unicode decode error."""
        mock_is_safe.return_value = True
        mock_ensure_exists.return_value = None

        with patch("builtins.open", mock_open()) as mock_file:
            mock_file.return_value.__enter__.return_value.read.side_effect = (
                UnicodeDecodeError("utf-8", b"", 0, 1, "invalid start byte")
            )
            # Mock json.load to raise UnicodeDecodeError
            with patch(
                "json.load",
                side_effect=UnicodeDecodeError(
                    "utf-8", b"", 0, 1, "invalid start byte"
                ),
            ):
                with pytest.raises(JsonTableError):
                    self.processor.load_from_file("unicode_error.json")

    def test_validate_file_path_safe(self):
        """Test file path validation with safe path."""
        with patch(
            "sphinxcontrib.jsontable.directives.validators.ValidationUtils.is_safe_path",
            return_value=True,
        ):
            result = self.processor._validate_file_path("safe.json")
            assert result == self.base_path / "safe.json"

    def test_validate_file_path_unsafe(self):
        """Test file path validation with unsafe path."""
        with patch(
            "sphinxcontrib.jsontable.directives.validators.ValidationUtils.is_safe_path",
            return_value=False,
        ):
            with pytest.raises(JsonTableError):
                self.processor._validate_file_path("../unsafe.json")

    def test_encoding_property(self):
        """Test encoding property access."""
        processor = JsonProcessor(Path("/test"), encoding="shift_jis")
        assert processor.encoding == "shift_jis"

    def test_base_path_property(self):
        """Test base_path property access."""
        base_path = Path("/custom/path")
        processor = JsonProcessor(base_path)
        assert processor.base_path == base_path

    def test_parse_inline_large_json(self):
        """Test parsing larger JSON content."""
        # Create a larger JSON structure
        large_data = {
            "items": [{"id": i, "name": f"item_{i}"} for i in range(100)],
            "metadata": {"total": 100, "page": 1},
        }
        content = [json.dumps(large_data)]

        result = self.processor.parse_inline(content)

        assert len(result["items"]) == 100
        assert result["items"][0]["id"] == 0
        assert result["items"][99]["name"] == "item_99"
        assert result["metadata"]["total"] == 100

    def test_parse_inline_nested_structures(self):
        """Test parsing deeply nested JSON."""
        content = [
            """{
            "level1": {
                "level2": {
                    "level3": {
                        "level4": {
                            "data": "deep value"
                        }
                    }
                }
            }
        }"""
        ]

        result = self.processor.parse_inline(content)
        assert result["level1"]["level2"]["level3"]["level4"]["data"] == "deep value"

    def test_parse_inline_with_logging(self):
        """Test that parsing generates appropriate log messages."""
        content = ['{"test": "data"}']

        with patch(
            "sphinxcontrib.jsontable.directives.json_processor.logger"
        ) as mock_logger:
            result = self.processor.parse_inline(content)

            # Verify that logging methods were called
            assert mock_logger.debug.called
            assert mock_logger.info.called
            assert result["test"] == "data"

    @patch("sphinxcontrib.jsontable.directives.validators.ValidationUtils.is_safe_path")
    @patch(
        "sphinxcontrib.jsontable.directives.validators.ValidationUtils.ensure_file_exists"
    )
    def test_load_from_file_with_logging(self, mock_ensure_exists, mock_is_safe):
        """Test that file loading generates appropriate log messages."""
        mock_is_safe.return_value = True
        mock_ensure_exists.return_value = None

        test_data = {"test": "data"}
        mock_content = json.dumps(test_data)

        with patch("builtins.open", mock_open(read_data=mock_content)):
            with patch(
                "sphinxcontrib.jsontable.directives.json_processor.logger"
            ) as mock_logger:
                result = self.processor.load_from_file("test.json")

                # Verify that logging methods were called
                assert mock_logger.debug.called
                assert mock_logger.info.called
                assert result["test"] == "data"

    def test_multiple_encodings(self):
        """Test processor with different encodings."""
        encodings = ["utf-8", "utf-16", "iso-8859-1", "cp1252"]

        for encoding in encodings:
            processor = JsonProcessor(Path("/test"), encoding=encoding)
            # Valid encodings should be preserved
            if encoding in ["utf-8", "utf-16", "iso-8859-1", "cp1252"]:
                assert processor.encoding in [
                    encoding,
                    "utf-8",
                ]  # May fallback for some
