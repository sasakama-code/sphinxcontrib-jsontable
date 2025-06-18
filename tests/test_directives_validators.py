"""
Comprehensive unit tests for directives.validators module.

This test suite provides complete coverage for ValidationUtils class methods,
following TDD approach and AAA (Arrange-Act-Assert) pattern.
Tests cover normal operation, edge cases, and error scenarios.
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Import the classes and functions to be tested
from sphinxcontrib.jsontable.directives.validators import (
    JsonTableError,
    ValidationUtils,
)


class TestJsonTableError:
    """
    Test suite for JsonTableError exception class.

    Validates that JsonTableError behaves correctly as a custom exception
    with proper inheritance and message handling.
    """

    def test_json_table_error_inherits_from_exception(self):
        """Test that JsonTableError properly inherits from Exception."""
        # Arrange & Act
        error = JsonTableError("test message")

        # Assert
        assert isinstance(error, Exception)

    def test_json_table_error_can_be_instantiated_with_message(self):
        """Test that JsonTableError can be instantiated with a message."""
        # Arrange
        message = "Test error message"

        # Act
        error = JsonTableError(message)

        # Assert
        assert str(error) == message

    def test_json_table_error_can_be_raised_and_caught(self):
        """Test that JsonTableError can be raised and caught properly."""
        # Arrange
        message = "Test error for raising"

        # Act & Assert
        with pytest.raises(JsonTableError) as exc_info:
            raise JsonTableError(message)
        assert str(exc_info.value) == message


class TestValidationUtils:
    """Test suite for ValidationUtils static methods."""

    class TestValidateNotEmpty:
        """Test suite for validate_not_empty method."""

        def test_validate_not_empty_with_none_raises_json_table_error(self):
            """Test that validate_not_empty raises JsonTableError when data is None."""
            # Arrange
            data = None
            error_msg = "Data cannot be None"

            # Act & Assert
            with pytest.raises(JsonTableError) as exc_info:
                ValidationUtils.validate_not_empty(data, error_msg)
            assert str(exc_info.value) == error_msg

        def test_validate_not_empty_with_empty_list_raises_json_table_error(self):
            """Test that validate_not_empty raises JsonTableError when data is empty list."""
            # Arrange
            data = []
            error_msg = "Data cannot be empty list"

            # Act & Assert
            with pytest.raises(JsonTableError) as exc_info:
                ValidationUtils.validate_not_empty(data, error_msg)
            assert str(exc_info.value) == error_msg

        def test_validate_not_empty_with_empty_string_raises_json_table_error(self):
            """Test that validate_not_empty raises JsonTableError when data is empty string."""
            # Arrange
            data = ""
            error_msg = "Data cannot be empty string"

            # Act & Assert
            with pytest.raises(JsonTableError) as exc_info:
                ValidationUtils.validate_not_empty(data, error_msg)
            assert str(exc_info.value) == error_msg

        def test_validate_not_empty_with_empty_dict_raises_json_table_error(self):
            """Test that validate_not_empty raises JsonTableError when data is empty dict."""
            # Arrange
            data = {}
            error_msg = "Data cannot be empty dict"

            # Act & Assert
            with pytest.raises(JsonTableError) as exc_info:
                ValidationUtils.validate_not_empty(data, error_msg)
            assert str(exc_info.value) == error_msg

        def test_validate_not_empty_with_zero_raises_json_table_error(self):
            """Test that validate_not_empty raises JsonTableError when data is zero."""
            # Arrange
            data = 0
            error_msg = "Data cannot be zero"

            # Act & Assert
            with pytest.raises(JsonTableError) as exc_info:
                ValidationUtils.validate_not_empty(data, error_msg)
            assert str(exc_info.value) == error_msg

        def test_validate_not_empty_with_false_raises_json_table_error(self):
            """Test that validate_not_empty raises JsonTableError when data is False."""
            # Arrange
            data = False
            error_msg = "Data cannot be False"

            # Act & Assert
            with pytest.raises(JsonTableError) as exc_info:
                ValidationUtils.validate_not_empty(data, error_msg)
            assert str(exc_info.value) == error_msg

        def test_validate_not_empty_with_non_empty_list_does_not_raise(self):
            """Test that validate_not_empty does not raise when data is non-empty list."""
            # Arrange
            data = [1, 2, 3]
            error_msg = "This should not be raised"

            # Act & Assert
            try:
                ValidationUtils.validate_not_empty(data, error_msg)
            except JsonTableError:
                pytest.fail("validate_not_empty raised JsonTableError unexpectedly")

        def test_validate_not_empty_with_non_empty_string_does_not_raise(self):
            """Test that validate_not_empty does not raise when data is non-empty string."""
            # Arrange
            data = "non-empty"
            error_msg = "This should not be raised"

            # Act & Assert
            try:
                ValidationUtils.validate_not_empty(data, error_msg)
            except JsonTableError:
                pytest.fail("validate_not_empty raised JsonTableError unexpectedly")

        def test_validate_not_empty_with_non_empty_dict_does_not_raise(self):
            """Test that validate_not_empty does not raise when data is non-empty dict."""
            # Arrange
            data = {"key": "value"}
            error_msg = "This should not be raised"

            # Act & Assert
            try:
                ValidationUtils.validate_not_empty(data, error_msg)
            except JsonTableError:
                pytest.fail("validate_not_empty raised JsonTableError unexpectedly")

        def test_validate_not_empty_with_positive_number_does_not_raise(self):
            """Test that validate_not_empty does not raise when data is positive number."""
            # Arrange
            data = 42
            error_msg = "This should not be raised"

            # Act & Assert
            try:
                ValidationUtils.validate_not_empty(data, error_msg)
            except JsonTableError:
                pytest.fail("validate_not_empty raised JsonTableError unexpectedly")

    class TestSafeStr:
        """Test suite for safe_str method."""

        def test_safe_str_with_none_returns_empty_string(self):
            """Test that safe_str returns empty string when value is None."""
            # Arrange
            value = None

            # Act
            result = ValidationUtils.safe_str(value)

            # Assert
            assert result == ""

        def test_safe_str_with_string_returns_same_string(self):
            """Test that safe_str returns the same string when value is string."""
            # Arrange
            value = "test string"

            # Act
            result = ValidationUtils.safe_str(value)

            # Assert
            assert result == "test string"

        def test_safe_str_with_integer_returns_string_representation(self):
            """Test that safe_str returns string representation when value is integer."""
            # Arrange
            value = 123

            # Act
            result = ValidationUtils.safe_str(value)

            # Assert
            assert result == "123"

        def test_safe_str_with_float_returns_string_representation(self):
            """Test that safe_str returns string representation when value is float."""
            # Arrange
            value = 123.45

            # Act
            result = ValidationUtils.safe_str(value)

            # Assert
            assert result == "123.45"

        def test_safe_str_with_boolean_true_returns_true_string(self):
            """Test that safe_str returns 'True' when value is boolean True."""
            # Arrange
            value = True

            # Act
            result = ValidationUtils.safe_str(value)

            # Assert
            assert result == "True"

        def test_safe_str_with_boolean_false_returns_false_string(self):
            """Test that safe_str returns 'False' when value is boolean False."""
            # Arrange
            value = False

            # Act
            result = ValidationUtils.safe_str(value)

            # Assert
            assert result == "False"

        def test_safe_str_with_list_returns_string_representation(self):
            """Test that safe_str returns string representation when value is list."""
            # Arrange
            value = [1, 2, 3]

            # Act
            result = ValidationUtils.safe_str(value)

            # Assert
            assert result == "[1, 2, 3]"

        def test_safe_str_with_dict_returns_string_representation(self):
            """Test that safe_str returns string representation when value is dict."""
            # Arrange
            value = {"key": "value"}

            # Act
            result = ValidationUtils.safe_str(value)

            # Assert
            assert result == "{'key': 'value'}"

        def test_safe_str_with_custom_object_calls_str_method(self):
            """Test that safe_str calls __str__ method on custom objects."""

            # Arrange
            class CustomObject:
                def __str__(self):
                    return "custom object string"

            value = CustomObject()

            # Act
            result = ValidationUtils.safe_str(value)

            # Assert
            assert result == "custom object string"

        def test_safe_str_with_zero_returns_zero_string(self):
            """Test that safe_str returns '0' when value is zero."""
            # Arrange
            value = 0

            # Act
            result = ValidationUtils.safe_str(value)

            # Assert
            assert result == "0"

    class TestEnsureFileExists:
        """Test suite for ensure_file_exists method."""

        @patch("pathlib.Path.exists")
        def test_ensure_file_exists_with_existing_file_does_not_raise(
            self, mock_exists
        ):
            """Test that ensure_file_exists does not raise when file exists."""
            # Arrange
            mock_exists.return_value = True
            file_path = Path("/mock/path/to/file.json")

            # Act & Assert
            try:
                ValidationUtils.ensure_file_exists(file_path)
            except FileNotFoundError:
                pytest.fail("ensure_file_exists raised FileNotFoundError unexpectedly")

        @patch("pathlib.Path.exists")
        def test_ensure_file_exists_with_non_existing_file_raises_file_not_found_error(
            self, mock_exists
        ):
            """Test that ensure_file_exists raises FileNotFoundError when file does not exist."""
            # Arrange
            mock_exists.return_value = False
            file_path = Path("/mock/path/to/nonexistent.json")

            # Act & Assert
            with pytest.raises(FileNotFoundError):
                ValidationUtils.ensure_file_exists(file_path)

        @patch("pathlib.Path.exists")
        def test_ensure_file_exists_error_message_contains_file_path(self, mock_exists):
            """Test that ensure_file_exists error message contains the file path."""
            # Arrange
            mock_exists.return_value = False
            file_path = Path("/mock/path/to/test.json")

            # Act & Assert
            with pytest.raises(FileNotFoundError) as exc_info:
                ValidationUtils.ensure_file_exists(file_path)
            assert str(file_path) in str(exc_info.value)

        @patch("pathlib.Path.exists")
        def test_ensure_file_exists_error_message_format(self, mock_exists):
            """Test that ensure_file_exists error message has correct format."""
            # Arrange
            mock_exists.return_value = False
            file_path = Path("/mock/path/to/test.json")
            expected_message = f"JSON file not found: {file_path}"

            # Act & Assert
            with pytest.raises(FileNotFoundError) as exc_info:
                ValidationUtils.ensure_file_exists(file_path)
            assert str(exc_info.value) == expected_message

        @patch("pathlib.Path.exists")
        def test_ensure_file_exists_calls_path_exists_method(self, mock_exists):
            """Test that ensure_file_exists calls the exists method on the path."""
            # Arrange
            mock_exists.return_value = True
            file_path = Path("/mock/path/to/file.json")

            # Act
            ValidationUtils.ensure_file_exists(file_path)

            # Assert
            mock_exists.assert_called_once()

    class TestFormatError:
        """Test suite for format_error method."""

        def test_format_error_combines_context_and_exception_message(self):
            """Test that format_error combines context and exception message correctly."""
            # Arrange
            context = "Loading JSON file"
            error = ValueError("Invalid JSON format")

            # Act
            result = ValidationUtils.format_error(context, error)

            # Assert
            assert result == "Loading JSON file: Invalid JSON format"

        def test_format_error_with_different_exception_types(self):
            """Test that format_error works with different exception types."""
            # Arrange
            context = "Processing data"
            error = KeyError("missing key")

            # Act
            result = ValidationUtils.format_error(context, error)

            # Assert
            assert result == "Processing data: 'missing key'"

        def test_format_error_with_empty_context_string(self):
            """Test that format_error handles empty context string."""
            # Arrange
            context = ""
            error = RuntimeError("Something went wrong")

            # Act
            result = ValidationUtils.format_error(context, error)

            # Assert
            assert result == ": Something went wrong"

        def test_format_error_with_exception_without_message(self):
            """Test that format_error handles exception without message."""
            # Arrange
            context = "Operation failed"
            error = Exception()

            # Act
            result = ValidationUtils.format_error(context, error)

            # Assert
            assert result == "Operation failed: "

        def test_format_error_with_file_not_found_error(self):
            """Test that format_error works with FileNotFoundError."""
            # Arrange
            context = "Reading file"
            error = FileNotFoundError("File not found")

            # Act
            result = ValidationUtils.format_error(context, error)

            # Assert
            assert result == "Reading file: File not found"

        def test_format_error_returns_string_type(self):
            """Test that format_error returns a string type."""
            # Arrange
            context = "Test context"
            error = Exception("Test error")

            # Act
            result = ValidationUtils.format_error(context, error)

            # Assert
            assert isinstance(result, str)

    class TestIsSafePath:
        """Test suite for is_safe_path method."""

        @patch("pathlib.Path.resolve")
        def test_is_safe_path_with_safe_subdirectory_returns_true(self, mock_resolve):
            """Test that is_safe_path returns True for safe subdirectory paths."""
            # Arrange
            base_path = Path("/safe/base/dir")
            safe_path = Path("/safe/base/dir/subdir/file.json")

            mock_resolve.side_effect = (
                lambda: safe_path if mock_resolve.call_count == 1 else base_path
            )

            # Act
            result = ValidationUtils.is_safe_path(safe_path, base_path)

            # Assert
            assert result is True

        @patch("pathlib.Path.resolve")
        def test_is_safe_path_with_directory_traversal_returns_false(
            self, mock_resolve
        ):
            """Test that is_safe_path returns False for directory traversal attempts."""
            # Arrange
            base_path = Path("/safe/base/dir")
            unsafe_path = Path("/unsafe/dir")

            mock_resolve.side_effect = (
                lambda: unsafe_path if mock_resolve.call_count == 1 else base_path
            )

            # Act
            result = ValidationUtils.is_safe_path(unsafe_path, base_path)

            # Assert
            assert result is False

        @patch("pathlib.Path.resolve")
        def test_is_safe_path_with_absolute_path_outside_base_returns_false(
            self, mock_resolve
        ):
            """Test that is_safe_path returns False for absolute paths outside base."""
            # Arrange
            base_path = Path("/safe/base/dir")
            outside_path = Path("/completely/different/path")

            mock_resolve.side_effect = (
                lambda: outside_path if mock_resolve.call_count == 1 else base_path
            )

            # Act
            result = ValidationUtils.is_safe_path(outside_path, base_path)

            # Assert
            assert result is False

        @patch("pathlib.Path.resolve")
        def test_is_safe_path_with_same_directory_returns_true(self, mock_resolve):
            """Test that is_safe_path returns True for same directory path."""
            # Arrange
            base_path = Path("/safe/base/dir")
            same_path = Path("/safe/base/dir")

            mock_resolve.return_value = base_path

            # Act
            result = ValidationUtils.is_safe_path(same_path, base_path)

            # Assert
            assert result is True

        @patch("pathlib.Path.resolve")
        def test_is_safe_path_handles_attribute_error_falls_back_to_relative_to(
            self, mock_resolve
        ):
            """Test that is_safe_path handles AttributeError and falls back to relative_to method."""
            # Arrange
            test_path = Path("/test/subdir")
            base_path = Path("/test")

            # Create mock resolved paths
            resolved_test = Mock()
            resolved_base = Mock()

            # is_relative_to doesn't exist (Python < 3.9), so AttributeError is raised
            resolved_test.is_relative_to.side_effect = AttributeError(
                "No is_relative_to method"
            )
            resolved_test.relative_to.return_value = Path(
                "subdir"
            )  # Success case - relative path

            # Mock resolve to return our mock objects
            mock_resolve.side_effect = [
                resolved_test,
                resolved_base,
                resolved_test,
                resolved_base,
            ]

            # Act
            result = ValidationUtils.is_safe_path(test_path, base_path)

            # Assert
            assert result is True

        @patch("pathlib.Path.relative_to")
        @patch("pathlib.Path.resolve")
        def test_is_safe_path_handles_exception_in_fallback_returns_false(
            self, mock_resolve, mock_relative_to
        ):
            """Test that is_safe_path returns False when exception occurs in fallback."""
            # Arrange
            test_path = Path("/test/path")
            base_path = Path("/base/path")
            mock_resolve.side_effect = AttributeError("No is_relative_to method")
            mock_relative_to.side_effect = ValueError("Path not relative")

            # Act
            result = ValidationUtils.is_safe_path(test_path, base_path)

            # Assert
            assert result is False

        @patch("pathlib.Path.resolve")
        def test_is_safe_path_calls_resolve_on_both_paths(self, mock_resolve):
            """Test that is_safe_path calls resolve on both input paths."""
            # Arrange
            test_path = Path("/test/path")
            base_path = Path("/base/path")
            mock_resolve.return_value = Path("/resolved/path")

            # Act
            ValidationUtils.is_safe_path(test_path, base_path)

            # Assert
            assert mock_resolve.call_count == 2

        def test_is_safe_path_returns_boolean_type(self):
            """Test that is_safe_path always returns a boolean value."""
            # Arrange
            test_path = Path("/test/path")
            base_path = Path("/base/path")

            # Act
            result = ValidationUtils.is_safe_path(test_path, base_path)

            # Assert
            assert isinstance(result, bool)
