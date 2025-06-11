"""Ultra coverage tests designed to reach 80% coverage target."""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest

# Import all modules for maximum coverage
import sphinxcontrib.jsontable
from sphinxcontrib.jsontable.data_loaders import JsonTableError, is_safe_path
from sphinxcontrib.jsontable.directives import (
    JsonDataLoader,
    JsonTableDirective,
    TableBuilder,
    TableConverter,
)
from sphinxcontrib.jsontable.json_table_directive import (
    JsonTableDirective as SimpleJsonTableDirective,
)


class TestUltraCoverage80:
    """Ultra comprehensive tests to reach 80% coverage."""

    def test_package_initialization(self):
        """Test package level imports and initialization."""
        # Test version import
        assert hasattr(sphinxcontrib.jsontable, "__version__")
        version = sphinxcontrib.jsontable.__version__
        assert version is not None

        # Test package level setup
        assert sphinxcontrib.jsontable is not None

    def test_all_json_data_loader_methods(self):
        """Test all JsonDataLoader methods comprehensively."""
        loader = JsonDataLoader()

        # Test load_from_content with all edge cases
        valid_json_cases = [
            '{"name": "Alice", "age": 25, "city": "NYC"}',
            "[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]",
            '{"nested": {"deep": {"very_deep": "value"}}}',
            "[]",
            "{}",
            "null",
            "true",
            "false",
            "42",
            '"string value"',
            "3.14159",
            '{"unicode": "テスト", "emoji": "🎉"}',
            '[{"a": 1}, {"b": 2}, {"c": 3}]',
        ]

        for json_str in valid_json_cases:
            result = loader.load_from_content(json_str)
            assert result is not None

        # Test load_from_file with multiple temporary files
        test_data_sets = [
            {"simple": "data"},
            [{"name": "Alice"}, {"name": "Bob"}],
            {"complex": {"nested": {"array": [1, 2, 3]}}},
            [],
            {},
            {"numbers": [1, 2, 3], "strings": ["a", "b", "c"]},
        ]

        for _i, data in enumerate(test_data_sets):
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".json", delete=False
            ) as f:
                json.dump(data, f, ensure_ascii=False)
                temp_path = f.name

            try:
                result = loader.load_from_file(temp_path)
                assert result == data
            finally:
                Path(temp_path).unlink()

        # Test error cases comprehensively
        invalid_json_cases = [
            '{"invalid": json}',
            '{missing_quotes: "value"}',
            '{"incomplete":',
            "[1, 2, 3,]",
            '{"key": undefined}',
            '{key: "value"}',  # Missing quotes on key
        ]

        for invalid_json in invalid_json_cases:
            with pytest.raises(JsonTableError):
                loader.load_from_content(invalid_json)

    def test_all_table_converter_paths(self):
        """Test all TableConverter code paths."""
        converter = TableConverter()

        # Test convert method with all supported types
        test_cases = [
            # Array of objects (most common)
            ([{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}], 2),
            # 2D array
            ([["Name", "Age"], ["Alice", 25], ["Bob", 30]], 3),
            # Single object
            ({"key1": "value1", "key2": "value2"}, 1),
            # Empty array
            ([], 0),
            # Single object converted to single row
            ({"single": "object"}, 1),
            # Array with nested objects
            ([{"user": {"name": "Alice"}, "id": 1}], 1),
            # Array with mixed types
            ([{"id": 1, "active": True, "score": 95.5}], 1),
            # Array with null values
            ([{"a": 1, "b": None}, {"a": None, "b": 2}], 2),
        ]

        for data, expected_rows in test_cases:
            result = converter.convert(data)
            assert len(result) == expected_rows

        # Test all error cases
        invalid_types = [
            "string_not_json",
            123,
            3.14,
            True,
            False,
            None,
            {1, 2, 3},
            frozenset([1, 2, 3]),
            complex(1, 2),
            lambda x: x,
        ]

        for invalid_type in invalid_types:
            with pytest.raises(JsonTableError):
                converter.convert(invalid_type)

    def test_all_table_builder_paths(self):
        """Test all TableBuilder code paths."""
        builder = TableBuilder()

        # Test build method with various configurations
        test_cases = [
            # Standard cases
            ([["Name", "Age"], ["Alice", 25]], True),
            ([["Alice", 25], ["Bob", 30]], False),
            # Edge cases
            ([], False),  # Empty data
            ([["Single"]], True),  # Single column with header
            ([["Data"]], False),  # Single column without header
            # Irregular data
            ([["A", "B", "C"], ["1", "2"], ["X", "Y", "Z", "Extra"]], True),
            ([["Short"], ["Much", "Longer", "Row"]], False),
            # Mixed types
            ([[1, "text", True], [None, 3.14, False]], False),
            # Unicode
            ([["名前", "年齢"], ["田中", 25]], True),
        ]

        for table_data, has_header in test_cases:
            result = builder.build(table_data, has_header=has_header)
            assert result is not None

    def test_directive_comprehensive(self):
        """Test directive with comprehensive scenarios."""
        # Mock Sphinx environment
        mock_state = Mock()
        mock_state_machine = Mock()
        mock_state_machine.reporter = Mock()
        mock_document = Mock()
        mock_state.document = mock_document

        # Test with file argument
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            test_data = [
                {"name": "Alice", "age": 25, "department": "Engineering"},
                {"name": "Bob", "age": 30, "department": "Sales"},
                {"name": "Charlie", "age": 35, "department": "Marketing"},
            ]
            json.dump(test_data, f)
            temp_path = f.name

        try:
            # Test various option combinations
            option_combinations = [
                {},
                {"header": True},
                {"limit": 2},
                {"header": True, "limit": 1},
            ]

            for options in option_combinations:
                directive = JsonTableDirective(
                    name="json-table",
                    arguments=[temp_path],
                    options=options,
                    content=[],
                    lineno=1,
                    content_offset=0,
                    block_text="",
                    state=mock_state,
                    state_machine=mock_state_machine,
                )

                assert directive.name == "json-table"
                assert len(directive.arguments) == 1

        finally:
            Path(temp_path).unlink()

        # Test with inline content
        inline_content_cases = [
            ['{"name": "Alice", "age": 25}'],
            ["[1, 2, 3, 4, 5]"],
            ['{"complex": {"nested": "data"}}'],
            ["[]"],
            ["{}"],
        ]

        for content in inline_content_cases:
            directive = JsonTableDirective(
                name="json-table",
                arguments=[],
                options={},
                content=content,
                lineno=1,
                content_offset=0,
                block_text="",
                state=mock_state,
                state_machine=mock_state_machine,
            )

            assert directive.name == "json-table"
            assert len(directive.content) == 1

    def test_is_safe_path_exhaustive(self):
        """Test is_safe_path function exhaustively."""
        # Safe paths - should return True
        safe_paths = [
            "file.json",
            "data/file.json",
            "data/subdir/file.json",
            "folder/nested/deep/file.json",
            "simple_file.json",
            "file-with-dashes.json",
            "file_with_underscores.json",
            "123numeric_start.json",
            "ファイル名.json",  # Unicode filename
            "file.with.dots.json",
        ]

        for path in safe_paths:
            assert is_safe_path(path), f"Should be safe: {path}"

        # Unsafe paths - should return False
        unsafe_paths = [
            "../parent.json",
            "../../grandparent.json",
            "../../../etc/passwd",
            "..\\windows\\path",
            "/absolute/path.json",
            "\\absolute\\windows\\path.json",
            "dir/../escape.json",
            "dir/../../double_escape.json",
            "~user/file.json",
            "$HOME/file.json",
            "${VARIABLE}/file.json",
            "%USERPROFILE%/file.json",
        ]

        for path in unsafe_paths:
            assert not is_safe_path(path), f"Should be unsafe: {path}"

    def test_simple_directive_comprehensive(self):
        """Test simple directive comprehensively."""
        mock_state = Mock()
        mock_state_machine = Mock()
        mock_state_machine.reporter = Mock()

        # Test with various content types
        content_cases = [
            ['{"name": "test"}'],
            ["[1, 2, 3]"],
            ['{"complex": {"data": [1, 2, 3]}}'],
            ["null"],
            ["true"],
            ['"string"'],
        ]

        for content in content_cases:
            directive = SimpleJsonTableDirective(
                name="json-table",
                arguments=[],
                options={},
                content=content,
                lineno=1,
                content_offset=0,
                block_text="",
                state=mock_state,
                state_machine=mock_state_machine,
            )

            assert directive.name == "json-table"
            assert len(directive.content) == 1

    def test_full_pipeline_integration(self):
        """Test complete data processing pipeline."""
        loader = JsonDataLoader()
        converter = TableConverter()
        builder = TableBuilder()

        # Complex real-world-like data
        complex_json = """
        {
            "employees": [
                {"id": 1, "name": "Alice Johnson", "department": "Engineering", "salary": 75000, "active": true},
                {"id": 2, "name": "Bob Smith", "department": "Sales", "salary": 65000, "active": true},
                {"id": 3, "name": "Charlie Brown", "department": "Marketing", "salary": 58000, "active": false}
            ]
        }
        """

        # Full pipeline test
        data = loader.load_from_content(complex_json)
        assert "employees" in data

        employees = data["employees"]
        table_data = converter.convert(employees)
        assert len(table_data) == 3

        # Test both header and non-header builds
        table_with_header = builder.build(table_data, has_header=True)
        assert table_with_header is not None

        table_without_header = builder.build(table_data, has_header=False)
        assert table_without_header is not None

    def test_error_scenarios_comprehensive(self):
        """Test all error scenarios comprehensively."""
        loader = JsonDataLoader()
        converter = TableConverter()

        # File not found errors
        with pytest.raises((JsonTableError, FileNotFoundError)):
            loader.load_from_file("definitely_not_existing_file.json")

        with pytest.raises((JsonTableError, FileNotFoundError)):
            loader.load_from_file("/path/that/does/not/exist.json")

        # JSON parsing errors
        malformed_json_cases = [
            "{",
            "}",
            '{"key":}',
            '{"key": value}',
            "[1, 2, 3,]",
            '{"incomplete"',
            "not json at all",
            '{"key": "value"} extra text',
        ]

        for bad_json in malformed_json_cases:
            with pytest.raises(JsonTableError):
                loader.load_from_content(bad_json)

        # Type conversion errors
        bad_types = [
            object(),
            type,
            b"binary",
            bytearray(b"mutable binary"),
            memoryview(b"memory"),
        ]

        for bad_type in bad_types:
            with pytest.raises(JsonTableError):
                converter.convert(bad_type)

    def test_unicode_and_encoding(self):
        """Test Unicode and encoding handling."""
        loader = JsonDataLoader()
        converter = TableConverter()

        # Unicode test data
        unicode_data = {
            "japanese": "こんにちは世界",
            "chinese": "你好世界",
            "arabic": "مرحبا بالعالم",
            "emoji": "🌍🎉🚀",
            "mixed": "Hello 世界 🌍",
        }

        # Test as JSON string
        unicode_json = json.dumps(unicode_data, ensure_ascii=False)
        result = loader.load_from_content(unicode_json)
        assert result == unicode_data

        # Test conversion
        table_data = converter.convert([unicode_data])
        assert len(table_data) == 1

        # Test with file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(unicode_data, f, ensure_ascii=False)
            temp_path = f.name

        try:
            result = loader.load_from_file(temp_path)
            assert result == unicode_data
        finally:
            Path(temp_path).unlink()

    def test_large_data_handling(self):
        """Test handling of large datasets."""
        converter = TableConverter()
        builder = TableBuilder()

        # Generate large dataset
        large_data = [
            {"id": i, "name": f"User_{i}", "value": i * 1.5, "active": i % 2 == 0}
            for i in range(100)
        ]

        # Test conversion
        table_data = converter.convert(large_data)
        assert len(table_data) == 100

        # Test table building
        table = builder.build(table_data[:10])  # First 10 rows
        assert table is not None

    def test_edge_case_combinations(self):
        """Test edge case combinations."""
        loader = JsonDataLoader()
        converter = TableConverter()
        builder = TableBuilder()

        edge_cases = [
            # Empty structures
            {},
            [],
            [{}],
            {"empty_array": []},
            {"empty_object": {}},
            # Null and boolean values
            {"null_value": None, "true_value": True, "false_value": False},
            [None, True, False],
            # Numeric edge cases
            {"zero": 0, "negative": -1, "float": 3.14159, "large": 1e10},
            # String edge cases
            {"empty_string": "", "whitespace": "   ", "special_chars": "!@#$%^&*()"},
        ]

        for edge_case in edge_cases:
            # Test through full pipeline
            json_str = json.dumps(edge_case)
            data = loader.load_from_content(json_str)

            if (isinstance(data, list) and data) or isinstance(data, dict):
                table_data = converter.convert(data)
                table = builder.build(table_data)
                assert table is not None
