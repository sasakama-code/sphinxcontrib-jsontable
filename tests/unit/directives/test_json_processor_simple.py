"""Simple JSON Processor Tests - Phase 3.1 Coverage Boost.

Tests for actual methods in json_processor.py to boost coverage effectively.
"""

import json
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from sphinxcontrib.jsontable.directives.json_processor import JsonProcessor


class TestJsonProcessorSimple:
    """Simple JSON processor tests that actually boost coverage."""

    def setup_method(self):
        """Set up test fixtures."""
        self.processor = JsonProcessor()

    def test_init(self):
        """Test initialization."""
        processor = JsonProcessor()
        assert processor is not None

    def test_process_inline_json_simple(self):
        """Test processing simple inline JSON."""
        json_data = '{"name": "test", "value": 123}'
        result = self.processor.process_inline_json(json_data)

        assert isinstance(result, dict)
        assert result["name"] == "test"
        assert result["value"] == 123

    def test_process_inline_json_array(self):
        """Test processing JSON array."""
        json_data = '[{"id": 1}, {"id": 2}]'
        result = self.processor.process_inline_json(json_data)

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["id"] == 1

    def test_process_inline_json_unicode(self):
        """Test processing JSON with Unicode."""
        json_data = '{"message": "こんにちは", "emoji": "🚀"}'
        result = self.processor.process_inline_json(json_data)

        assert result["message"] == "こんにちは"
        assert result["emoji"] == "🚀"

    def test_process_inline_json_invalid(self):
        """Test processing invalid JSON."""
        with pytest.raises((json.JSONDecodeError, ValueError)):
            self.processor.process_inline_json('{"invalid": }')

    def test_process_file_json_valid(self):
        """Test processing valid JSON file."""
        test_data = {"test": "data"}
        mock_content = json.dumps(test_data)

        with patch("builtins.open", mock_open(read_data=mock_content)):
            with patch("pathlib.Path.exists", return_value=True):
                result = self.processor.process_file_json(Path("test.json"))

        assert result == test_data

    def test_process_file_json_not_found(self):
        """Test processing non-existent file."""
        with patch("pathlib.Path.exists", return_value=False):
            with pytest.raises(Exception):  # Any exception is fine
                self.processor.process_file_json(Path("missing.json"))

    def test_process_nested_json(self):
        """Test processing nested JSON structure."""
        json_data = """
        {
            "users": [{"name": "Alice"}, {"name": "Bob"}],
            "meta": {"count": 2}
        }
        """
        result = self.processor.process_inline_json(json_data)

        assert "users" in result
        assert len(result["users"]) == 2
        assert result["meta"]["count"] == 2

    def test_process_empty_structures(self):
        """Test processing empty JSON structures."""
        # Empty object
        result = self.processor.process_inline_json("{}")
        assert result == {}

        # Empty array
        result = self.processor.process_inline_json("[]")
        assert result == []

    def test_process_null_values(self):
        """Test processing null values."""
        json_data = '{"value": null, "array": [null, 1]}'
        result = self.processor.process_inline_json(json_data)

        assert result["value"] is None
        assert result["array"][0] is None
        assert result["array"][1] == 1

    def test_process_boolean_values(self):
        """Test processing boolean values."""
        json_data = '{"is_valid": true, "is_complete": false}'
        result = self.processor.process_inline_json(json_data)

        assert result["is_valid"] is True
        assert result["is_complete"] is False
