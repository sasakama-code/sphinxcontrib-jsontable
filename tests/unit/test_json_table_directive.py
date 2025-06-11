"""Comprehensive unit tests for JsonTableDirective class.

Provides exhaustive test coverage for all JsonTableDirective methods including
initiation, configuration parsing, JSON data processing, and table generation.
Tests cover both successful operations and error conditions with proper mocking
for component isolation and reliable test execution.

Test Structure:
- Initialization and configuration tests
- JSON data loading and validation tests
- Table conversion and rendering tests
- Error handling and edge case validation
"""

from pathlib import Path
from unittest.mock import MagicMock, Mock, PropertyMock, patch

import pytest

# Import the class under test and related exceptions
from sphinxcontrib.jsontable.directives import (
    DEFAULT_ENCODING,
    NO_JSON_SOURCE_ERROR,
    JsonTableDirective,
    JsonTableError,
)


class TestJsonTableDirective:
    """Comprehensive test suite for JsonTableDirective functionality.

    Tests all aspects of JsonTableDirective including initialization,
    configuration processing, data loading, table generation, and error
    handling with comprehensive mocking for component isolation.
    """

    @pytest.fixture
    def mock_state(self):
        """Create mock Sphinx state with document and environment configuration.

        Returns:
            Mock object configured to simulate Sphinx directive state.
        """
        state = Mock()
        state.document = Mock()
        state.document.settings = Mock()
        state.document.settings.env = Mock()
        state.document.settings.env.srcdir = "/mock/source/dir"
        return state

    @pytest.fixture
    def directive_instance(self, mock_state):
        """Create JsonTableDirective instance with fully mocked dependencies.

        Args:
            mock_state: Mocked Sphinx state fixture.

        Returns:
            JsonTableDirective instance with mocked loader, converter, and builder.
        """
        with (
            patch("sphinxcontrib.jsontable.directives.SphinxDirective.__init__"),
            patch(
                "sphinxcontrib.jsontable.directives.JsonDataLoader"
            ) as mock_loader_class,
            patch(
                "sphinxcontrib.jsontable.directives.TableConverter"
            ) as mock_converter_class,
            patch(
                "sphinxcontrib.jsontable.directives.TableBuilder"
            ) as mock_builder_class,
        ):
            # Create instance without calling parent __init__
            directive = JsonTableDirective.__new__(JsonTableDirective)

            # Set up basic attributes
            directive.state = mock_state
            directive.arguments = []
            directive.content = []
            directive.options = {}

            # Set up mock instances
            directive.loader = mock_loader_class.return_value
            directive.converter = mock_converter_class.return_value
            directive.builder = mock_builder_class.return_value

            # Store mock classes for verification
            directive._mock_loader_class = mock_loader_class
            directive._mock_converter_class = mock_converter_class
            directive._mock_builder_class = mock_builder_class

            return directive

    # Tests for __init__ method

    @patch("sphinxcontrib.jsontable.directives.JsonDataLoader")
    @patch("sphinxcontrib.jsontable.directives.TableConverter")
    @patch("sphinxcontrib.jsontable.directives.TableBuilder")
    def test_init_with_default_encoding(
        self, mock_builder, mock_converter, mock_loader
    ):
        """Test initialization uses default encoding when no encoding option provided."""
        # Arrange
        mock_state = Mock()
        mock_state_machine = Mock()
        args = (
            "json-table",
            [],
            {},
            [],
            1,
            0,
            "block text",
            mock_state,
            mock_state_machine,
        )

        # Act
        directive = JsonTableDirective(*args)  # noqa

        # Assert
        mock_loader.assert_called_once_with(DEFAULT_ENCODING)

    @patch("sphinxcontrib.jsontable.directives.JsonDataLoader")
    @patch("sphinxcontrib.jsontable.directives.TableConverter")
    @patch("sphinxcontrib.jsontable.directives.TableBuilder")
    def test_init_with_custom_encoding(self, mock_builder, mock_converter, mock_loader):
        """Test initialization uses custom encoding when encoding option provided."""
        # Arrange
        custom_encoding = "latin-1"
        mock_state = Mock()
        mock_state_machine = Mock()
        args = (
            "json-table",
            [],
            {"encoding": custom_encoding},
            [],
            1,
            0,
            "block text",
            mock_state,
            mock_state_machine,
        )

        # Act
        directive = JsonTableDirective(*args)  # noqa

        # Assert
        mock_loader.assert_called_once_with(custom_encoding)

    @patch("sphinxcontrib.jsontable.directives.JsonDataLoader")
    @patch("sphinxcontrib.jsontable.directives.TableConverter")
    @patch("sphinxcontrib.jsontable.directives.TableBuilder")
    def test_init_creates_required_components(
        self, mock_builder, mock_converter, mock_loader
    ):
        """Test initialization creates loader, converter, and builder instances."""
        # Arrange
        mock_state = Mock()
        mock_state_machine = Mock()
        args = (
            "json-table",
            [],
            {},
            [],
            1,
            0,
            "block text",
            mock_state,
            mock_state_machine,
        )

        # Act
        directive = JsonTableDirective(*args)

        # Assert
        assert hasattr(directive, "loader")
        assert hasattr(directive, "converter")
        assert hasattr(directive, "builder")

    # Tests for run method

    @patch("sphinxcontrib.jsontable.directives.logger")
    def test_run_with_file_argument_no_options(self, mock_logger, directive_instance):
        """Test run method with file argument and no options."""
        # Arrange
        directive_instance.arguments = ["test.json"]
        directive_instance.options = {}

        mock_json_data = {"key": "value"}
        mock_table_data = [["row1"]]
        mock_table_node = Mock()

        directive_instance.loader.load_from_file.return_value = mock_json_data
        directive_instance.converter.convert.return_value = mock_table_data
        directive_instance.builder.build.return_value = mock_table_node

        # Act
        result = directive_instance.run()

        # Assert
        assert result == [mock_table_node]

    @patch("sphinxcontrib.jsontable.directives.logger")
    def test_run_with_file_argument_and_header_option(
        self, mock_logger, directive_instance
    ):
        """Test run method with file argument and header option."""
        # Arrange
        directive_instance.arguments = ["test.json"]
        directive_instance.options = {"header": True}

        mock_json_data = [{"name": "test"}]
        directive_instance.loader.load_from_file.return_value = mock_json_data
        directive_instance.converter.convert.return_value = [["name"], ["test"]]
        directive_instance.builder.build.return_value = Mock()

        # Act
        directive_instance.run()

        # Assert
        directive_instance.converter.convert.assert_called_once_with(
            mock_json_data, True, None
        )

    @patch("sphinxcontrib.jsontable.directives.logger")
    def test_run_with_file_argument_and_limit_option(
        self, mock_logger, directive_instance
    ):
        """Test run method with file argument and limit option."""
        # Arrange
        directive_instance.arguments = ["test.json"]
        directive_instance.options = {"limit": 10}

        mock_json_data = [{"name": "test"}]
        directive_instance.loader.load_from_file.return_value = mock_json_data
        directive_instance.converter.convert.return_value = [["test"]]
        directive_instance.builder.build.return_value = Mock()

        # Act
        directive_instance.run()

        # Assert
        directive_instance.converter.convert.assert_called_once_with(
            mock_json_data, False, 10
        )

    @patch("sphinxcontrib.jsontable.directives.logger")
    def test_run_with_inline_content_no_options(self, mock_logger, directive_instance):
        """Test run method with inline content and no options."""
        # Arrange
        directive_instance.arguments = []
        directive_instance.content = ['{"key": "value"}']
        directive_instance.options = {}

        mock_json_data = {"key": "value"}
        directive_instance.loader.parse_inline.return_value = mock_json_data
        directive_instance.converter.convert.return_value = [["row1"]]
        directive_instance.builder.build.return_value = Mock()

        # Act
        result = directive_instance.run()

        # Assert
        assert len(result) == 1

    @patch("sphinxcontrib.jsontable.directives.logger")
    def test_run_with_inline_content_and_header_option(
        self, mock_logger, directive_instance
    ):
        """Test run method with inline content and header option."""
        # Arrange
        directive_instance.arguments = []
        directive_instance.content = ['[{"name": "test"}]']
        directive_instance.options = {"header": True}

        mock_json_data = [{"name": "test"}]
        directive_instance.loader.parse_inline.return_value = mock_json_data
        directive_instance.converter.convert.return_value = [["name"], ["test"]]
        directive_instance.builder.build.return_value = Mock()

        # Act
        directive_instance.run()

        # Assert
        directive_instance.builder.build.assert_called_once_with(
            [["name"], ["test"]], True
        )

    @patch("sphinxcontrib.jsontable.directives.logger")
    def test_run_with_all_options(self, mock_logger, directive_instance):
        """Test run method with all options provided."""
        # Arrange
        directive_instance.arguments = ["test.json"]
        directive_instance.options = {"header": True, "limit": 5, "encoding": "utf-8"}

        mock_json_data = [{"name": "test"}]
        directive_instance.loader.load_from_file.return_value = mock_json_data
        directive_instance.converter.convert.return_value = [["name"], ["test"]]
        directive_instance.builder.build.return_value = Mock()

        # Act
        directive_instance.run()

        # Assert
        directive_instance.converter.convert.assert_called_once_with(
            mock_json_data, True, 5
        )

    @patch("sphinxcontrib.jsontable.directives.logger")
    def test_run_handles_json_table_error(self, mock_logger, directive_instance):
        """Test run method handles JsonTableError and returns error node."""
        # Arrange
        directive_instance.arguments = ["test.json"]
        directive_instance.loader.load_from_file.side_effect = JsonTableError(
            "Test error"
        )

        with patch.object(
            directive_instance, "_create_error_node"
        ) as mock_create_error:
            mock_error_node = Mock()
            mock_create_error.return_value = mock_error_node

            # Act
            result = directive_instance.run()

            # Assert
            assert result == [mock_error_node]

    @patch("sphinxcontrib.jsontable.directives.logger")
    def test_run_handles_file_not_found_error(self, mock_logger, directive_instance):
        """Test run method handles FileNotFoundError and returns error node."""
        # Arrange
        directive_instance.arguments = ["nonexistent.json"]
        directive_instance.loader.load_from_file.side_effect = FileNotFoundError(
            "File not found"
        )

        with patch.object(
            directive_instance, "_create_error_node"
        ) as mock_create_error:
            mock_error_node = Mock()
            mock_create_error.return_value = mock_error_node

            # Act
            result = directive_instance.run()

            # Assert
            assert result == [mock_error_node]

    # Tests for _load_json_data method

    def test_load_json_data_from_file(self, directive_instance):
        """Test _load_json_data loads from file when arguments provided."""
        # Arrange
        directive_instance.arguments = ["test.json"]
        directive_instance.content = []

        mock_json_data = {"key": "value"}
        directive_instance.loader.load_from_file.return_value = mock_json_data

        # Mock the env property access
        with patch.object(
            type(directive_instance), "env", new_callable=PropertyMock
        ) as mock_env:
            mock_env.return_value.srcdir = "/source/dir"

            # Act
            result = directive_instance._load_json_data()

            # Assert
            assert result == mock_json_data

    def test_load_json_data_from_inline_content(self, directive_instance):
        """Test _load_json_data loads from inline content when no arguments."""
        # Arrange
        directive_instance.arguments = []
        directive_instance.content = ['{"key": "value"}']

        mock_json_data = {"key": "value"}
        directive_instance.loader.parse_inline.return_value = mock_json_data

        # Act
        result = directive_instance._load_json_data()

        # Assert
        assert result == mock_json_data

    def test_load_json_data_no_source_raises_error(self, directive_instance):
        """Test _load_json_data raises JsonTableError when no source provided."""
        # Arrange
        directive_instance.arguments = []
        directive_instance.content = []

        # Act & Assert
        with pytest.raises(JsonTableError) as exc_info:
            directive_instance._load_json_data()

        assert str(exc_info.value) == NO_JSON_SOURCE_ERROR

    # Tests for _create_error_node method

    def test_create_error_node_structure(self, directive_instance):
        """Test _create_error_node creates correct node structure."""
        # Arrange
        error_message = "Test error message"

        with patch("sphinxcontrib.jsontable.directives.nodes") as mock_nodes:
            # Use MagicMock which supports magic methods like __iadd__
            mock_error_node = MagicMock()
            mock_paragraph = MagicMock()

            # Ensure __iadd__ returns the same object
            mock_error_node.__iadd__.return_value = mock_error_node

            # Configure nodes module mocks
            mock_nodes.error.return_value = mock_error_node
            mock_nodes.paragraph.return_value = mock_paragraph

            # Act
            result = directive_instance._create_error_node(error_message)

            # Assert
            assert result == mock_error_node
            mock_nodes.error.assert_called_once()
            mock_nodes.paragraph.assert_called_once_with(text=error_message)

    def test_create_error_node_message_content(self, directive_instance):
        """Test _create_error_node includes message in paragraph node."""
        # Arrange
        error_message = "Test error message"

        with patch("sphinxcontrib.jsontable.directives.nodes") as mock_nodes:
            # Use MagicMock which supports magic methods like __iadd__
            mock_error_node = MagicMock()
            mock_paragraph = MagicMock()

            # Configure nodes module mocks
            mock_nodes.error.return_value = mock_error_node
            mock_nodes.paragraph.return_value = mock_paragraph

            # Act
            directive_instance._create_error_node(error_message)

            # Assert
            mock_nodes.paragraph.assert_called_once_with(text=error_message)

    # Additional edge case tests

    @patch("sphinxcontrib.jsontable.directives.logger")
    def test_run_processes_limit_option_correctly(
        self, mock_logger, directive_instance
    ):
        """Test run method processes limit option correctly without specific logging."""
        # Arrange
        directive_instance.arguments = ["test.json"]
        directive_instance.options = {"limit": 10}

        mock_json_data = [{"name": "test"}]
        directive_instance.loader.load_from_file.return_value = mock_json_data
        directive_instance.converter.convert.return_value = [["test"]]
        directive_instance.builder.build.return_value = Mock()

        # Act
        result = directive_instance.run()

        # Assert
        # Verify that the limit was passed to converter.convert
        directive_instance.converter.convert.assert_called_once_with(
            mock_json_data, False, 10
        )
        # Verify successful execution
        assert len(result) == 1

    def test_load_json_data_calls_loader_with_correct_path(self, directive_instance):
        """Test _load_json_data calls loader with correct source directory path."""
        # Arrange
        directive_instance.arguments = ["data/test.json"]
        directive_instance.content = []

        mock_json_data = {"key": "value"}
        directive_instance.loader.load_from_file.return_value = mock_json_data

        # Mock the env property access
        with patch.object(
            type(directive_instance), "env", new_callable=PropertyMock
        ) as mock_env:
            mock_source_dir = Path("/project/source")
            mock_env.return_value.srcdir = str(mock_source_dir)

            # Act
            directive_instance._load_json_data()

            # Assert
            directive_instance.loader.load_from_file.assert_called_once_with(
                "data/test.json",
                mock_source_dir,
            )

    # Real instance tests to improve coverage of actual implementation

    @patch("builtins.getattr")
    @patch("sphinxcontrib.jsontable.json_table_directive.TableBuilder")
    @patch("sphinxcontrib.jsontable.json_table_directive.TableConverter")
    @patch("sphinxcontrib.jsontable.json_table_directive.JsonDataLoader")
    def test_real_init_with_default_settings(
        self, mock_loader_class, mock_converter_class, mock_builder_class, mock_getattr
    ):
        """Test real __init__ method with default settings to cover lines 66-76."""
        # Mock getattr to return DEFAULT_MAX_ROWS
        from sphinxcontrib.jsontable.table_converters import DEFAULT_MAX_ROWS

        mock_getattr.return_value = DEFAULT_MAX_ROWS

        # Create minimal mock state
        mock_state = Mock()
        mock_state_machine = Mock()
        mock_env = Mock()
        mock_config = Mock()
        mock_env.config = mock_config

        # Create instance arguments for real initialization
        args = (
            "json-table",
            [],
            {},  # no options
            [],
            1,
            0,
            "block text",
            mock_state,
            mock_state_machine,
        )

        # Patch SphinxDirective.__init__ to set up env
        with patch(
            "sphinxcontrib.jsontable.json_table_directive.SphinxDirective.__init__"
        ) as mock_super_init:

            def setup_env(self, *args, **kwargs):
                self.env = mock_env
                self.options = {}

            mock_super_init.side_effect = setup_env

            # Act - create real instance to test lines 66-76
            directive = JsonTableDirective(*args)

            # Assert initialization
            mock_loader_class.assert_called_once_with(DEFAULT_ENCODING)
            mock_converter_class.assert_called_once_with(DEFAULT_MAX_ROWS)
            mock_builder_class.assert_called_once_with()
            assert hasattr(directive, "loader")
            assert hasattr(directive, "converter")
            assert hasattr(directive, "builder")

    @patch("builtins.getattr")
    @patch("sphinxcontrib.jsontable.json_table_directive.TableBuilder")
    @patch("sphinxcontrib.jsontable.json_table_directive.TableConverter")
    @patch("sphinxcontrib.jsontable.json_table_directive.JsonDataLoader")
    def test_real_init_with_custom_encoding(
        self, mock_loader_class, mock_converter_class, mock_builder_class, mock_getattr
    ):
        """Test real __init__ method with custom encoding option."""
        # Mock getattr to return DEFAULT_MAX_ROWS
        from sphinxcontrib.jsontable.table_converters import DEFAULT_MAX_ROWS

        mock_getattr.return_value = DEFAULT_MAX_ROWS

        # Create minimal mock state
        mock_state = Mock()
        mock_state_machine = Mock()
        mock_env = Mock()
        mock_config = Mock()
        mock_env.config = mock_config

        custom_encoding = "latin-1"
        args = (
            "json-table",
            [],
            {"encoding": custom_encoding},
            [],
            1,
            0,
            "block text",
            mock_state,
            mock_state_machine,
        )

        # Patch SphinxDirective.__init__ to set up env
        with patch(
            "sphinxcontrib.jsontable.json_table_directive.SphinxDirective.__init__"
        ) as mock_super_init:

            def setup_env(self, *args, **kwargs):
                self.env = mock_env
                self.options = {"encoding": custom_encoding}

            mock_super_init.side_effect = setup_env

            # Act
            JsonTableDirective(*args)

            # Assert
            mock_loader_class.assert_called_once_with(custom_encoding)

    @patch("builtins.getattr")
    @patch("sphinxcontrib.jsontable.json_table_directive.TableBuilder")
    @patch("sphinxcontrib.jsontable.json_table_directive.TableConverter")
    @patch("sphinxcontrib.jsontable.json_table_directive.JsonDataLoader")
    def test_real_init_with_custom_max_rows(
        self, mock_loader_class, mock_converter_class, mock_builder_class, mock_getattr
    ):
        """Test real __init__ method with custom max rows config."""
        # Mock getattr to return custom value
        custom_max_rows = 500
        mock_getattr.return_value = custom_max_rows

        # Create minimal mock state
        mock_state = Mock()
        mock_state_machine = Mock()
        mock_env = Mock()
        mock_config = Mock()
        mock_env.config = mock_config

        args = (
            "json-table",
            [],
            {},
            [],
            1,
            0,
            "block text",
            mock_state,
            mock_state_machine,
        )

        # Patch SphinxDirective.__init__ to set up env
        with patch(
            "sphinxcontrib.jsontable.json_table_directive.SphinxDirective.__init__"
        ) as mock_super_init:

            def setup_env(self, *args, **kwargs):
                self.env = mock_env
                self.options = {}

            mock_super_init.side_effect = setup_env

            # Act
            JsonTableDirective(*args)

            # Assert
            from sphinxcontrib.jsontable.table_converters import DEFAULT_MAX_ROWS

            mock_getattr.assert_called_once_with(
                mock_config, "jsontable_max_rows", DEFAULT_MAX_ROWS
            )
            mock_converter_class.assert_called_once_with(custom_max_rows)

    def test_real_run_success_with_file_and_options(self):
        """Test real run method execution with file argument and options to cover lines 86-93."""
        # Create real directive instance
        mock_state = Mock()
        mock_state_machine = Mock()
        mock_env = Mock()
        mock_env.config = Mock()
        mock_env.srcdir = "/mock/source"

        args = (
            "json-table",
            ["test.json"],
            {"header": True, "limit": 10},
            [],
            1,
            0,
            "block text",
            mock_state,
            mock_state_machine,
        )

        with (
            patch(
                "sphinxcontrib.jsontable.json_table_directive.SphinxDirective.__init__"
            ) as mock_super_init,
            patch(
                "sphinxcontrib.jsontable.json_table_directive.JsonDataLoader"
            ) as mock_loader_class,
            patch(
                "sphinxcontrib.jsontable.json_table_directive.TableConverter"
            ) as mock_converter_class,
            patch(
                "sphinxcontrib.jsontable.json_table_directive.TableBuilder"
            ) as mock_builder_class,
            patch("builtins.getattr") as mock_getattr,
        ):
            # Setup environment
            def setup_env(self, *args, **kwargs):
                self.env = mock_env
                self.arguments = ["test.json"]
                self.options = {"header": True, "limit": 10}

            mock_super_init.side_effect = setup_env
            mock_getattr.return_value = 1000

            # Setup mock instances
            mock_loader = mock_loader_class.return_value
            mock_converter = mock_converter_class.return_value
            mock_builder = mock_builder_class.return_value

            mock_json_data = [{"name": "test", "value": 123}]
            mock_table_data = [["name", "value"], ["test", "123"]]
            mock_table_node = Mock()

            mock_loader.load_from_file.return_value = mock_json_data
            mock_converter.convert.return_value = mock_table_data
            mock_builder.build.return_value = mock_table_node

            # Act
            directive = JsonTableDirective(*args)
            result = directive.run()

            # Assert - covers lines 87-93
            assert result == [mock_table_node]
            mock_converter.convert.assert_called_once_with(mock_json_data, True, 10)
            mock_builder.build.assert_called_once_with(mock_table_data, True)

    def test_real_run_success_with_content(self):
        """Test real run method execution with inline content to cover load_from_content path."""
        # Create real directive instance
        mock_state = Mock()
        mock_state_machine = Mock()
        mock_env = Mock()
        mock_env.config = Mock()

        args = (
            "json-table",
            [],
            {},
            ['{"name": "test", "value": 123}'],
            1,
            0,
            "block text",
            mock_state,
            mock_state_machine,
        )

        with (
            patch(
                "sphinxcontrib.jsontable.json_table_directive.SphinxDirective.__init__"
            ) as mock_super_init,
            patch(
                "sphinxcontrib.jsontable.json_table_directive.JsonDataLoader"
            ) as mock_loader_class,
            patch(
                "sphinxcontrib.jsontable.json_table_directive.TableConverter"
            ) as mock_converter_class,
            patch(
                "sphinxcontrib.jsontable.json_table_directive.TableBuilder"
            ) as mock_builder_class,
            patch(
                "sphinxcontrib.jsontable.json_table_directive.getattr"
            ) as mock_getattr,
        ):
            # Setup environment
            def setup_env(self, *args, **kwargs):
                self.env = mock_env
                self.arguments = []
                self.content = ['{"name": "test", "value": 123}']
                self.options = {}

            mock_super_init.side_effect = setup_env
            mock_getattr.return_value = 1000

            # Setup mock instances
            mock_loader = mock_loader_class.return_value
            mock_converter = mock_converter_class.return_value
            mock_builder = mock_builder_class.return_value

            mock_json_data = {"name": "test", "value": 123}
            mock_table_data = [["test", "123"]]
            mock_table_node = Mock()

            mock_loader.load_from_content.return_value = mock_json_data
            mock_converter.convert.return_value = mock_table_data
            mock_builder.build.return_value = mock_table_node

            # Act
            directive = JsonTableDirective(*args)
            result = directive.run()

            # Assert - covers lines 115-116
            assert result == [mock_table_node]
            mock_loader.load_from_content.assert_called_once_with(
                '{"name": "test", "value": 123}'
            )

    @patch("sphinxcontrib.jsontable.json_table_directive.logger")
    @patch("sphinxcontrib.jsontable.json_table_directive.format_error")
    def test_real_run_error_handling(self, mock_format_error, mock_logger):
        """Test real run method error handling to cover lines 95-98."""
        # Create real directive instance
        mock_state = Mock()
        mock_state_machine = Mock()
        mock_env = Mock()
        mock_env.config = Mock()

        args = (
            "json-table",
            ["nonexistent.json"],
            {},
            [],
            1,
            0,
            "block text",
            mock_state,
            mock_state_machine,
        )

        with (
            patch(
                "sphinxcontrib.jsontable.json_table_directive.SphinxDirective.__init__"
            ) as mock_super_init,
            patch(
                "sphinxcontrib.jsontable.json_table_directive.JsonDataLoader"
            ) as mock_loader_class,
            patch("sphinxcontrib.jsontable.json_table_directive.TableConverter"),
            patch("sphinxcontrib.jsontable.json_table_directive.TableBuilder"),
            patch(
                "sphinxcontrib.jsontable.json_table_directive.getattr"
            ) as mock_getattr,
            patch("sphinxcontrib.jsontable.json_table_directive.nodes") as mock_nodes,
        ):
            # Setup environment
            def setup_env(self, *args, **kwargs):
                self.env = mock_env
                self.arguments = ["nonexistent.json"]
                self.options = {}

            mock_super_init.side_effect = setup_env
            mock_getattr.return_value = 1000

            # Setup mock instances
            mock_loader = mock_loader_class.return_value
            test_error = JsonTableError("Test error")
            mock_loader.load_from_file.side_effect = test_error

            # Setup error node creation
            mock_error_node = Mock()
            mock_paragraph_node = Mock()
            mock_nodes.error.return_value = mock_error_node
            mock_nodes.paragraph.return_value = mock_paragraph_node
            mock_error_node.__iadd__ = Mock(return_value=mock_error_node)

            mock_format_error.return_value = "Formatted error message"

            # Act
            directive = JsonTableDirective(*args)
            result = directive.run()

            # Assert - covers lines 95-98 and 130-132
            assert result == [mock_error_node]
            mock_format_error.assert_called_once_with(
                "JsonTable directive error", test_error
            )
            mock_logger.error.assert_called_once_with("Formatted error message")
            mock_nodes.error.assert_called_once()
            mock_nodes.paragraph.assert_called_once_with(text="Formatted error message")

    def test_real_load_json_data_no_source_error(self):
        """Test real _load_json_data method when no source provided to cover line 118."""
        # Create real directive instance
        mock_state = Mock()
        mock_state_machine = Mock()
        mock_env = Mock()
        mock_env.config = Mock()

        args = (
            "json-table",
            [],
            {},
            [],
            1,
            0,
            "block text",
            mock_state,
            mock_state_machine,
        )

        with (
            patch(
                "sphinxcontrib.jsontable.json_table_directive.SphinxDirective.__init__"
            ) as mock_super_init,
            patch("sphinxcontrib.jsontable.json_table_directive.JsonDataLoader"),
            patch("sphinxcontrib.jsontable.json_table_directive.TableConverter"),
            patch("sphinxcontrib.jsontable.json_table_directive.TableBuilder"),
            patch(
                "sphinxcontrib.jsontable.json_table_directive.getattr"
            ) as mock_getattr,
        ):
            # Setup environment - no arguments, no content
            def setup_env(self, *args, **kwargs):
                self.env = mock_env
                self.arguments = []
                self.content = []
                self.options = {}

            mock_super_init.side_effect = setup_env
            mock_getattr.return_value = 1000

            # Act
            directive = JsonTableDirective(*args)

            # Assert - covers line 118
            with pytest.raises(JsonTableError) as exc_info:
                directive._load_json_data()
            assert str(exc_info.value) == NO_JSON_SOURCE_ERROR
