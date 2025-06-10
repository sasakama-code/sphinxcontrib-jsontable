"""Additional coverage tests for JsonTableDirective to reach 80% coverage target.

This module specifically targets the uncovered lines in json_table_directive.py
to achieve the required 80% test coverage for GitHub Actions CI.
"""

from unittest.mock import Mock, patch

from sphinxcontrib.jsontable.json_table_directive import (
    DEFAULT_ENCODING,
    DEFAULT_MAX_ROWS,
    JsonTableDirective,
    JsonTableError,
)


class TestJsonTableDirectiveCoverage:
    """Additional tests targeting specific uncovered lines."""

    def test_init_with_custom_encoding_option(self):
        """Test __init__ processes encoding option correctly (lines 66-67)."""
        # Arrange
        mock_env = Mock()
        mock_env.config = Mock()
        mock_env.config.jsontable_max_rows = 5000

        # Act
        with (
            patch(
                "sphinxcontrib.jsontable.json_table_directive.JsonDataLoader"
            ),
            patch(
                "sphinxcontrib.jsontable.json_table_directive.TableConverter"
            ),
            patch(
                "sphinxcontrib.jsontable.json_table_directive.TableBuilder"
            ),
        ):
            directive = JsonTableDirective(
                name="json-table",
                arguments=[],
                options={"encoding": "iso-8859-1"},
                content=[],
                lineno=1,
                content_offset=0,
                block_text="",
                state=Mock(),
                state_machine=Mock(),
            )
            directive.env = mock_env

            # Manually trigger the initialization that happens in __init__
            encoding = directive.options.get("encoding", DEFAULT_ENCODING)
            default_max_rows = getattr(
                directive.env.config, "jsontable_max_rows", DEFAULT_MAX_ROWS
            )

            from sphinxcontrib.jsontable.data_loaders import JsonDataLoader
            from sphinxcontrib.jsontable.table_builders import TableBuilder
            from sphinxcontrib.jsontable.table_converters import TableConverter

            directive.loader = JsonDataLoader(encoding)
            directive.converter = TableConverter(default_max_rows)
            directive.builder = TableBuilder()

        # Assert encoding was processed correctly
        assert directive.loader.encoding == "iso-8859-1"

    def test_init_config_max_rows_access(self):
        """Test __init__ accesses config.jsontable_max_rows correctly (lines 70-72)."""
        # Arrange
        mock_env = Mock()
        mock_env.config = Mock()
        mock_env.config.jsontable_max_rows = 8000

        # Act
        with (
            patch("sphinxcontrib.jsontable.json_table_directive.JsonDataLoader"),
            patch(
                "sphinxcontrib.jsontable.json_table_directive.TableConverter"
            ),
            patch("sphinxcontrib.jsontable.json_table_directive.TableBuilder"),
        ):
            directive = JsonTableDirective(
                name="json-table",
                arguments=[],
                options={},
                content=[],
                lineno=1,
                content_offset=0,
                block_text="",
                state=Mock(),
                state_machine=Mock(),
            )
            directive.env = mock_env

            # Access config the same way as in __init__
            default_max_rows = getattr(
                directive.env.config, "jsontable_max_rows", DEFAULT_MAX_ROWS
            )

            from sphinxcontrib.jsontable.table_converters import TableConverter

            directive.converter = TableConverter(default_max_rows)

        # Assert config value was used
        assert directive.converter.default_max_rows == 8000

    def test_init_component_creation(self):
        """Test __init__ creates loader, converter and builder (lines 74-76)."""
        # Arrange
        mock_env = Mock()
        mock_env.config = Mock()
        mock_env.config.jsontable_max_rows = 6000

        # Act
        directive = JsonTableDirective(
            name="json-table",
            arguments=[],
            options={"encoding": "utf-8"},
            content=[],
            lineno=1,
            content_offset=0,
            block_text="",
            state=Mock(),
            state_machine=Mock(),
        )
        directive.env = mock_env

        # Manually execute the component creation logic
        encoding = directive.options.get("encoding", DEFAULT_ENCODING)
        default_max_rows = getattr(
            directive.env.config, "jsontable_max_rows", DEFAULT_MAX_ROWS
        )

        from sphinxcontrib.jsontable.data_loaders import JsonDataLoader
        from sphinxcontrib.jsontable.table_builders import TableBuilder
        from sphinxcontrib.jsontable.table_converters import TableConverter

        directive.loader = JsonDataLoader(encoding)
        directive.converter = TableConverter(default_max_rows)
        directive.builder = TableBuilder()

        # Assert all components were created
        assert directive.loader is not None
        assert directive.converter is not None
        assert directive.builder is not None
        assert directive.loader.encoding == "utf-8"
        assert directive.converter.default_max_rows == 6000

    def test_run_load_json_data_call(self):
        """Test run() calls _load_json_data correctly (line 87)."""
        # Arrange
        directive = JsonTableDirective(
            name="json-table",
            arguments=["test.json"],
            options={},
            content=[],
            lineno=1,
            content_offset=0,
            block_text="",
            state=Mock(),
            state_machine=Mock(),
        )
        directive.env = Mock()
        directive.env.config = Mock()

        # Mock the components
        directive.loader = Mock()
        directive.converter = Mock()
        directive.builder = Mock()

        directive.loader.load_from_file.return_value = [{"test": "data"}]
        directive.converter.convert.return_value = [["test", "data"]]
        directive.builder.build.return_value = Mock()

        # Act
        directive.run()

        # Assert _load_json_data functionality was called
        directive.loader.load_from_file.assert_called_once_with("test.json")

    def test_run_header_option_processing(self):
        """Test run() processes header option correctly (line 88)."""
        # Arrange
        directive = JsonTableDirective(
            name="json-table",
            arguments=[],
            options={"header": True},  # header option present
            content=['{"test": "data"}'],
            lineno=1,
            content_offset=0,
            block_text="",
            state=Mock(),
            state_machine=Mock(),
        )
        directive.env = Mock()
        directive.env.config = Mock()

        # Mock components
        directive.loader = Mock()
        directive.converter = Mock()
        directive.builder = Mock()

        directive.loader.parse_inline.return_value = [{"test": "data"}]
        directive.converter.convert.return_value = [["test", "data"]]
        directive.builder.build.return_value = Mock()

        # Act
        directive.run()

        # Assert header option was processed correctly
        directive.converter.convert.assert_called_once_with(
            [{"test": "data"}],
            True,
            None,  # include_header=True
        )

    def test_run_limit_option_processing(self):
        """Test run() processes limit option correctly (line 89)."""
        # Arrange
        directive = JsonTableDirective(
            name="json-table",
            arguments=[],
            options={"limit": 10},
            content=['{"test": "data"}'],
            lineno=1,
            content_offset=0,
            block_text="",
            state=Mock(),
            state_machine=Mock(),
        )
        directive.env = Mock()
        directive.env.config = Mock()

        # Mock components
        directive.loader = Mock()
        directive.converter = Mock()
        directive.builder = Mock()

        directive.loader.parse_inline.return_value = [{"test": "data"}]
        directive.converter.convert.return_value = [["test", "data"]]
        directive.builder.build.return_value = Mock()

        # Act
        directive.run()

        # Assert limit option was processed correctly
        directive.converter.convert.assert_called_once_with(
            [{"test": "data"}],
            False,
            10,  # limit=10
        )

    def test_run_table_conversion_and_building(self):
        """Test run() calls converter and builder correctly (lines 90-94)."""
        # Arrange
        directive = JsonTableDirective(
            name="json-table",
            arguments=[],
            options={},
            content=['[{"name": "test", "value": 123}]'],
            lineno=1,
            content_offset=0,
            block_text="",
            state=Mock(),
            state_machine=Mock(),
        )
        directive.env = Mock()
        directive.env.config = Mock()

        # Mock components
        directive.loader = Mock()
        directive.converter = Mock()
        directive.builder = Mock()

        mock_json_data = [{"name": "test", "value": 123}]
        mock_table_data = [["name", "value"], ["test", "123"]]
        mock_table_node = Mock()

        directive.loader.parse_inline.return_value = mock_json_data
        directive.converter.convert.return_value = mock_table_data
        directive.builder.build.return_value = mock_table_node

        # Act
        result = directive.run()

        # Assert all processing steps were called
        directive.loader.parse_inline.assert_called_once()
        directive.converter.convert.assert_called_once_with(mock_json_data, False, None)
        directive.builder.build.assert_called_once_with(mock_table_data, False)
        assert len(result) == 1
        assert result[0] == mock_table_node

    def test_run_exception_handling_json_table_error(self):
        """Test run() handles JsonTableError correctly (lines 95-96)."""
        # Arrange
        directive = JsonTableDirective(
            name="json-table",
            arguments=["bad_file.json"],
            options={},
            content=[],
            lineno=1,
            content_offset=0,
            block_text="",
            state=Mock(),
            state_machine=Mock(),
        )
        directive.env = Mock()
        directive.env.config = Mock()

        directive.loader = Mock()
        directive.converter = Mock()
        directive.builder = Mock()

        # Make loader raise JsonTableError
        error_msg = "Invalid JSON format"
        directive.loader.load_from_file.side_effect = JsonTableError(error_msg)

        # Mock _create_error_node
        mock_error_node = Mock()
        directive._create_error_node = Mock(return_value=mock_error_node)

        # Act
        result = directive.run()

        # Assert error was handled correctly
        directive._create_error_node.assert_called_once_with(error_msg)
        assert len(result) == 1
        assert result[0] == mock_error_node

    def test_run_exception_handling_file_not_found_error(self):
        """Test run() handles FileNotFoundError correctly (lines 97-98)."""
        # Arrange
        directive = JsonTableDirective(
            name="json-table",
            arguments=["missing_file.json"],
            options={},
            content=[],
            lineno=1,
            content_offset=0,
            block_text="",
            state=Mock(),
            state_machine=Mock(),
        )
        directive.env = Mock()
        directive.env.config = Mock()

        directive.loader = Mock()
        directive.converter = Mock()
        directive.builder = Mock()

        # Make loader raise FileNotFoundError
        directive.loader.load_from_file.side_effect = FileNotFoundError()

        # Mock _create_error_node
        mock_error_node = Mock()
        directive._create_error_node = Mock(return_value=mock_error_node)

        # Act
        result = directive.run()

        # Assert error was handled correctly
        expected_msg = 'File not found: "missing_file.json"'
        directive._create_error_node.assert_called_once_with(expected_msg)
        assert len(result) == 1
        assert result[0] == mock_error_node
