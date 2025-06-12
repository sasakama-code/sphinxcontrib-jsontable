"""Comprehensive coverage tests for JsonTableDirective.

Strategic tests targeting json_table_directive.py to boost coverage from 53.06% to 75%+.
Focuses on all methods, error paths, options, and integration scenarios.

Created: 2025-06-12
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest
from docutils import nodes
from docutils.statemachine import StringList

from sphinxcontrib.jsontable.data_loaders import JsonTableError
from sphinxcontrib.jsontable.json_table_directive import JsonTableDirective


class MockSphinxEnvironment:
    """Mock Sphinx environment for testing."""

    def __init__(self, srcdir=None):
        self.srcdir = srcdir or "/tmp/test"
        self.config = MockConfig()
        self.app = Mock()
        self.app.config = self.config


class MockConfig:
    """Mock Sphinx configuration."""

    def __init__(self):
        self.jsontable_max_rows = 1000

    def get(self, key, default=None):
        return getattr(self, key, default)


class TestJsonTableDirectiveComprehensive:
    """Comprehensive JsonTableDirective coverage tests."""

    def setup_method(self):
        """Setup test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.env = MockSphinxEnvironment(str(self.temp_dir))

        # Mock state and state_machine
        self.state = Mock()
        self.state_machine = Mock()
        self.state.document = Mock()
        self.state.document.settings = Mock()
        self.state.document.settings.env = self.env

    def teardown_method(self):
        """Cleanup test fixtures."""
        import shutil

        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def create_directive(
        self, name="jsontable", arguments=None, options=None, content=None
    ):
        """Create a JsonTableDirective instance for testing."""
        arguments = arguments or []
        options = options or {}
        content = content or StringList([])

        directive = JsonTableDirective(
            name=name,
            arguments=arguments,
            options=options,
            content=content,
            lineno=1,
            content_offset=0,
            block_text="",
            state=self.state,
            state_machine=self.state_machine,
        )

        # Set environment
        directive.env = self.env

        return directive

    def test_basic_initialization(self):
        """Test basic directive initialization."""
        directive = self.create_directive()

        assert directive.name == "jsontable"
        assert hasattr(directive, "loader")
        assert hasattr(directive, "converter")
        assert hasattr(directive, "builder")

    def test_initialization_with_custom_encoding(self):
        """Test initialization with custom encoding option."""
        directive = self.create_directive(options={"encoding": "utf-16"})

        assert directive.loader.encoding == "utf-16"

    def test_initialization_with_custom_config(self):
        """Test initialization with custom max_rows config."""
        self.env.config.jsontable_max_rows = 500
        directive = self.create_directive()

        assert directive.converter.max_rows == 500

    def test_run_with_file_argument(self):
        """Test run method with file argument."""
        # Create test JSON file
        test_data = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]
        test_file = self.temp_dir / "test.json"

        with test_file.open("w") as f:
            json.dump(test_data, f)

        directive = self.create_directive(
            arguments=["test.json"], options={"header": True}
        )

        result = directive.run()

        assert len(result) == 1
        assert isinstance(result[0], nodes.table)

    def test_run_with_inline_content(self):
        """Test run method with inline JSON content."""
        json_content = ['[{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]']

        directive = self.create_directive(
            content=StringList(json_content), options={"header": True}
        )

        result = directive.run()

        assert len(result) == 1
        assert isinstance(result[0], nodes.table)

    def test_run_without_data_source(self):
        """Test run method without data source."""
        directive = self.create_directive()

        result = directive.run()

        assert len(result) == 1
        assert isinstance(result[0], nodes.system_message)

    def test_run_with_file_not_found(self):
        """Test run method with non-existent file."""
        directive = self.create_directive(arguments=["nonexistent.json"])

        result = directive.run()

        assert len(result) == 1
        assert isinstance(result[0], nodes.system_message)

    def test_run_with_invalid_json_file(self):
        """Test run method with invalid JSON file."""
        # Create invalid JSON file
        test_file = self.temp_dir / "invalid.json"

        with test_file.open("w") as f:
            f.write("{ invalid json")

        directive = self.create_directive(arguments=["invalid.json"])

        result = directive.run()

        assert len(result) == 1
        assert isinstance(result[0], nodes.system_message)

    def test_run_with_invalid_inline_json(self):
        """Test run method with invalid inline JSON."""
        json_content = ["{ invalid json }"]

        directive = self.create_directive(content=StringList(json_content))

        result = directive.run()

        assert len(result) == 1
        assert isinstance(result[0], nodes.system_message)

    def test_header_option_enabled(self):
        """Test header option when enabled."""
        json_content = ['[{"name": "Alice"}, {"name": "Bob"}]']

        directive = self.create_directive(
            content=StringList(json_content), options={"header": True}
        )

        result = directive.run()

        assert len(result) == 1
        assert isinstance(result[0], nodes.table)

    def test_header_option_disabled(self):
        """Test header option when disabled."""
        json_content = ['[{"name": "Alice"}, {"name": "Bob"}]']

        directive = self.create_directive(
            content=StringList(json_content)
            # No header option
        )

        result = directive.run()

        assert len(result) == 1
        assert isinstance(result[0], nodes.table)

    def test_limit_option(self):
        """Test limit option functionality."""
        # Create data with more rows than limit
        test_data = [{"id": i, "value": f"data_{i}"} for i in range(10)]
        json_content = [json.dumps(test_data)]

        directive = self.create_directive(
            content=StringList(json_content), options={"limit": 3}
        )

        result = directive.run()

        assert len(result) == 1
        assert isinstance(result[0], nodes.table)

    def test_encoding_option(self):
        """Test encoding option with UTF-8 content."""
        # Create UTF-8 file with Japanese content
        test_data = [{"name": "太郎", "city": "東京"}]
        test_file = self.temp_dir / "utf8.json"

        with test_file.open("w", encoding="utf-8") as f:
            json.dump(test_data, f, ensure_ascii=False)

        directive = self.create_directive(
            arguments=["utf8.json"], options={"encoding": "utf-8"}
        )

        result = directive.run()

        assert len(result) == 1
        assert isinstance(result[0], nodes.table)

    def test_load_json_data_file_priority(self):
        """Test _load_json_data method with file priority."""
        # Create test file
        test_data = {"source": "file"}
        test_file = self.temp_dir / "priority.json"

        with test_file.open("w") as f:
            json.dump(test_data, f)

        directive = self.create_directive(
            arguments=["priority.json"], content=StringList(['{"source": "content"}'])
        )

        result = directive._load_json_data()
        assert result == test_data

    def test_load_json_data_content_fallback(self):
        """Test _load_json_data method with content fallback."""
        json_content = ['{"source": "content"}']

        directive = self.create_directive(content=StringList(json_content))

        result = directive._load_json_data()
        assert result == {"source": "content"}

    def test_load_json_data_no_source_error(self):
        """Test _load_json_data method with no source."""
        directive = self.create_directive()

        with pytest.raises(JsonTableError):
            directive._load_json_data()

    def test_create_error_node(self):
        """Test _create_error_node method."""
        directive = self.create_directive()

        error_node = directive._create_error_node("Test error message")

        assert isinstance(error_node, nodes.system_message)
        assert len(error_node.children) == 1
        assert isinstance(error_node.children[0], nodes.paragraph)

    def test_complex_json_structures(self):
        """Test with complex nested JSON structures."""
        complex_data = {
            "users": [
                {
                    "id": 1,
                    "profile": {
                        "name": "Alice",
                        "details": {"age": 25, "city": "Tokyo"},
                    },
                },
                {
                    "id": 2,
                    "profile": {"name": "Bob", "details": {"age": 30, "city": "Osaka"}},
                },
            ]
        }

        json_content = [json.dumps(complex_data)]

        directive = self.create_directive(content=StringList(json_content))

        result = directive.run()

        assert len(result) == 1
        assert isinstance(result[0], nodes.table)

    def test_array_of_primitives(self):
        """Test with array of primitive values."""
        primitive_data = ["apple", "banana", "cherry"]
        json_content = [json.dumps(primitive_data)]

        directive = self.create_directive(content=StringList(json_content))

        result = directive.run()

        assert len(result) == 1
        assert isinstance(result[0], nodes.table)

    def test_single_object(self):
        """Test with single JSON object."""
        single_object = {"name": "Test", "value": "Data"}
        json_content = [json.dumps(single_object)]

        directive = self.create_directive(content=StringList(json_content))

        result = directive.run()

        assert len(result) == 1
        assert isinstance(result[0], nodes.table)

    def test_empty_json_array(self):
        """Test with empty JSON array."""
        json_content = ["[]"]

        directive = self.create_directive(content=StringList(json_content))

        result = directive.run()

        assert len(result) == 1
        assert isinstance(result[0], nodes.table)

    def test_empty_json_object(self):
        """Test with empty JSON object."""
        json_content = ["{}"]

        directive = self.create_directive(content=StringList(json_content))

        result = directive.run()

        assert len(result) == 1
        assert isinstance(result[0], nodes.table)

    def test_mixed_data_types(self):
        """Test with mixed data types in JSON."""
        mixed_data = [
            {
                "string": "text",
                "number": 42,
                "float": 3.14,
                "boolean": True,
                "null": None,
                "array": [1, 2, 3],
                "object": {"nested": "value"},
            }
        ]

        json_content = [json.dumps(mixed_data)]

        directive = self.create_directive(content=StringList(json_content))

        result = directive.run()

        assert len(result) == 1
        assert isinstance(result[0], nodes.table)

    def test_unicode_content(self):
        """Test with Unicode content."""
        unicode_data = [
            {"japanese": "こんにちは", "emoji": "🎉"},
            {"chinese": "你好", "arabic": "مرحبا"},
        ]

        json_content = [json.dumps(unicode_data, ensure_ascii=False)]

        directive = self.create_directive(content=StringList(json_content))

        result = directive.run()

        assert len(result) == 1
        assert isinstance(result[0], nodes.table)

    def test_large_dataset(self):
        """Test with moderately large dataset."""
        large_data = [{"id": i, "value": f"item_{i}"} for i in range(100)]
        json_content = [json.dumps(large_data)]

        directive = self.create_directive(content=StringList(json_content))

        result = directive.run()

        assert len(result) == 1
        assert isinstance(result[0], nodes.table)

    def test_zero_limit_option(self):
        """Test limit option with zero (unlimited)."""
        test_data = [{"id": i} for i in range(10)]
        json_content = [json.dumps(test_data)]

        directive = self.create_directive(
            content=StringList(json_content),
            options={"limit": 0},  # Unlimited
        )

        result = directive.run()

        assert len(result) == 1
        assert isinstance(result[0], nodes.table)

    def test_multiple_options_combination(self):
        """Test combination of multiple options."""
        test_data = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]
        json_content = [json.dumps(test_data)]

        directive = self.create_directive(
            content=StringList(json_content),
            options={"header": True, "limit": 5, "encoding": "utf-8"},
        )

        result = directive.run()

        assert len(result) == 1
        assert isinstance(result[0], nodes.table)

    def test_file_with_relative_path(self):
        """Test file loading with relative path."""
        # Create subdirectory and file
        subdir = self.temp_dir / "subdir"
        subdir.mkdir()
        test_file = subdir / "nested.json"

        test_data = [{"nested": "data"}]
        with test_file.open("w") as f:
            json.dump(test_data, f)

        directive = self.create_directive(arguments=["subdir/nested.json"])

        result = directive.run()

        assert len(result) == 1
        assert isinstance(result[0], nodes.table)

    def test_error_handling_robustness(self):
        """Test robust error handling in various scenarios."""
        error_scenarios = [
            # Invalid file path
            {"arguments": ["../../../etc/passwd"]},
            # Invalid JSON syntax
            {"content": StringList(["{ invalid"])},
            # Unsupported data type
            {"content": StringList(['"just a string"'])},
        ]

        for scenario in error_scenarios:
            directive = self.create_directive(**scenario)
            result = directive.run()

            # Should return error node, not crash
            assert len(result) == 1
            assert isinstance(result[0], nodes.system_message)

    def test_directive_reusability(self):
        """Test that directive components can be reused."""
        # Create first directive and run
        directive1 = self.create_directive(content=StringList(['[{"test": 1}]']))
        result1 = directive1.run()

        # Create second directive and run
        directive2 = self.create_directive(content=StringList(['[{"test": 2}]']))
        result2 = directive2.run()

        # Both should succeed independently
        assert len(result1) == 1
        assert len(result2) == 1
        assert isinstance(result1[0], nodes.table)
        assert isinstance(result2[0], nodes.table)

    def test_option_spec_completeness(self):
        """Test that all option_spec entries are handled."""
        directive = self.create_directive()

        # Verify all expected options are in option_spec
        expected_options = {"header", "encoding", "limit"}
        actual_options = set(directive.option_spec.keys())

        assert expected_options.issubset(actual_options)

    def test_sphinx_integration_points(self):
        """Test Sphinx integration points."""
        directive = self.create_directive()

        # Verify Sphinx environment integration
        assert directive.env is not None
        assert hasattr(directive.env, "srcdir")
        assert hasattr(directive.env, "config")

    def test_content_multiline_handling(self):
        """Test handling of multiline JSON content."""
        multiline_json = [
            "{",
            '  "users": [',
            '    {"name": "Alice"},',
            '    {"name": "Bob"}',
            "  ]",
            "}",
        ]

        directive = self.create_directive(content=StringList(multiline_json))

        result = directive.run()

        assert len(result) == 1
        assert isinstance(result[0], nodes.table)

    def test_extremely_nested_json(self):
        """Test with extremely nested JSON structure."""
        nested_data = {"level": 1}
        current = nested_data

        # Create 10-level deep nesting
        for i in range(2, 11):
            current["next"] = {"level": i}
            current = current["next"]

        current["data"] = [{"final": "value"}]

        json_content = [json.dumps(nested_data)]

        directive = self.create_directive(content=StringList(json_content))

        result = directive.run()

        assert len(result) == 1
        assert isinstance(result[0], nodes.table)
