"""JSON data loading utilities with security validation and encoding support.

Provides secure JSON data loading capabilities for both file-based and inline content
processing with comprehensive error handling and security validation.

Features:
- Secure file path validation with traversal protection
- Encoding validation and fallback support
- Inline JSON content processing
- Comprehensive error handling
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sphinx.util import logging

logger = logging.getLogger(__name__)

JsonData = list[Any] | dict[str, Any]

DEFAULT_ENCODING = "utf-8"
NO_JSON_SOURCE_ERROR = "No JSON data source provided"
INVALID_JSON_DATA_ERROR = "JSON data must be an array or object"
EMPTY_CONTENT_ERROR = "No inline JSON content provided"


class JsonTableError(Exception):
    """
    Exception raised for errors during JSON to table conversion.

    This exception is raised when JSON data cannot be processed, converted,
    or rendered as a table due to format issues, validation failures, or
    other processing errors.
    """


def validate_not_empty(data: Any, error_msg: str) -> None:
    """Validate data is not None or empty, raising JsonTableError if invalid.

    Args:
        data: Data to validate for non-empty state.
        error_msg: Error message to use if validation fails.

    Raises:
        JsonTableError: If data is None, empty, or evaluates to False.
    """
    if not data:
        raise JsonTableError(error_msg)


def ensure_file_exists(path: Path) -> None:
    """Verify file path exists and raise FileNotFoundError if missing.

    Args:
        path: Path object representing the file to verify.

    Raises:
        FileNotFoundError: If the file does not exist at the specified path.
    """
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")


def format_error(context: str, error: Exception) -> str:
    """Format error message by combining context description with exception details.

    Args:
        context: Description of operation or location where error occurred.
        error: Exception instance containing error details.

    Returns:
        Formatted error string in format "{context}: {error}".
    """
    return f"{context}: {error}"


def is_safe_path(path: Path, base: Path) -> bool:
    """Validate path is within base directory to prevent directory traversal attacks.

    Args:
        path: Path to validate for safety.
        base: Base directory that should contain the path.

    Returns:
        True if path is safely within base directory, False otherwise.
    """
    try:
        return path.resolve().is_relative_to(base.resolve())
    except AttributeError:
        try:
            path.resolve().relative_to(base.resolve())
            return True
        except Exception:
            return False


class JsonDataLoader:
    """JSON data loader with support for file and inline content processing.

    Provides secure JSON data loading capabilities with encoding validation,
    path security checks, and comprehensive error handling for both file-based
    and inline JSON content processing.

    Attributes:
        encoding: Character encoding used for file reading operations.
    """

    def __init__(self, encoding: str = DEFAULT_ENCODING):
        self.encoding = self._validate_encoding(encoding)

    def _validate_encoding(self, encoding: str) -> str:
        """Validate encoding and return with fallback to UTF-8 if invalid.

        Args:
            encoding: Character encoding to validate.

        Returns:
            Valid encoding string, defaulting to UTF-8 if validation fails.
        """
        try:
            "test".encode(encoding)
            return encoding
        except (LookupError, TypeError):
            logger.warning(f"Invalid encoding '{encoding}', falling back to UTF-8")
            return DEFAULT_ENCODING

    def _validate_path_security(self, json_path: Path, base_path: Path) -> None:
        """Validate path security to prevent directory traversal attacks.

        Args:
            json_path: Path to JSON file to validate.
            base_path: Base directory path for security validation.

        Raises:
            JsonTableError: If path is not safe (directory traversal detected).
        """
        if not is_safe_path(json_path, base_path):
            raise JsonTableError(
                f"Path '{json_path}' is not safe (directory traversal detected)"
            )

    def _validate_json_structure(self, data: JsonData) -> None:
        """Validate JSON data structure is supported (array or object).

        Args:
            data: JSON data to validate.

        Raises:
            JsonTableError: If data is not an array or object type.
        """
        if not isinstance(data, list | dict):
            raise JsonTableError(INVALID_JSON_DATA_ERROR)

    def load_from_file(self, file_path: str, base_path: Path) -> JsonData:
        """Load JSON data from file with security validation.

        Args:
            file_path: Path to JSON file relative to base path.
            base_path: Base directory path for security validation.

        Returns:
            Parsed JSON data as list or dict.

        Raises:
            JsonTableError: If file access, parsing, or validation fails.
            FileNotFoundError: If the specified file does not exist.
        """
        try:
            json_path = base_path / file_path
            ensure_file_exists(json_path)
            self._validate_path_security(json_path, base_path)

            with json_path.open(encoding=self.encoding) as f:
                data = json.load(f)

            self._validate_json_structure(data)
            return data

        except (OSError, json.JSONDecodeError) as e:
            raise JsonTableError(format_error("Failed to load JSON file", e)) from e

    def load_from_content(self, content: str) -> JsonData:
        """Load JSON data from inline string content.

        Args:
            content: JSON string content to parse.

        Returns:
            Parsed JSON data as list or dict.

        Raises:
            JsonTableError: If content is empty or JSON parsing fails.
        """
        validate_not_empty(content.strip(), EMPTY_CONTENT_ERROR)

        try:
            data = json.loads(content)
            self._validate_json_structure(data)
            return data
        except json.JSONDecodeError as e:
            raise JsonTableError(format_error("Failed to parse inline JSON", e)) from e

    def load_json_data(
        self, file_path: str | None, content: str | None, base_path: Path
    ) -> JsonData:
        """Load JSON data from file or inline content with validation.

        Args:
            file_path: Optional path to JSON file.
            content: Optional inline JSON content.
            base_path: Base directory path for file operations.

        Returns:
            Parsed JSON data as list or dict.

        Raises:
            JsonTableError: If no data source provided or data loading fails.
        """
        if file_path:
            return self.load_from_file(file_path, base_path)
        elif content:
            return self.load_from_content(content)
        else:
            raise JsonTableError(NO_JSON_SOURCE_ERROR)
