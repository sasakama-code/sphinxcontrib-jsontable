"""Sphinx directive for rendering JSON data as ReStructuredText tables.

Provides comprehensive JSON table rendering capabilities including file and inline
content processing, security validation, performance optimization, and integration
with Sphinx documentation generation workflow.

Supported Features:
- JSON file and inline content processing
- Security validation with path traversal protection
- Performance limits and memory safety
- Multiple JSON format support (objects, arrays, mixed types)
- Comprehensive error handling and validation
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, ClassVar

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.util import logging
from sphinx.util.docutils import SphinxDirective

from .table_builders import TableBuilder
from .table_converters import TableConverter

logger = logging.getLogger(__name__)

JsonData = list[Any] | dict[str, Any]
TableData = list[list[str]]

DEFAULT_ENCODING = "utf-8"
DEFAULT_MAX_ROWS = 10000  # Conservative limit for performance and memory safety
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
        data: Data to validate, may be None or an empty sequence.
        error_msg: Error message to use in exception when data is empty.

    Raises:
        JsonTableError: If data is None, empty, or evaluates to False.
    """
    if not data:
        raise JsonTableError(error_msg)


def safe_str(value: Any) -> str:
    """
    Safely convert a value to string, returning empty string for None.

    Args:
        value: Any value to convert to string.

    Returns:
        String representation of value, or empty string if value is None.
    """
    return str(value) if value is not None else ""


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
        """Validate character encoding and return safe encoding name.

        Args:
            encoding: Character encoding name to validate.

        Returns:
            Validated encoding name, or DEFAULT_ENCODING if invalid.
        """
        try:
            "test".encode(encoding)
            return encoding
        except LookupError:
            logger.warning(f"Invalid encoding '{encoding}', using {DEFAULT_ENCODING}")
            return DEFAULT_ENCODING

    def _validate_file_path(self, source: str, srcdir: Path) -> Path:
        """Validate and resolve JSON file path to prevent security issues.

        Args:
            source: Relative path string to JSON file.
            srcdir: Base directory for path resolution.

        Returns:
            Resolved and validated Path object for JSON file.

        Raises:
            JsonTableError: If path contains directory traversal attempts.
        """
        file_path = srcdir / source
        if not is_safe_path(file_path, srcdir):
            raise JsonTableError(f"Invalid file path: {source}")
        return file_path

    def load_from_file(self, source: str, srcdir: Path) -> JsonData:
        """Load and parse JSON data from file with security validation.

        Args:
            source: Relative file path to JSON data.
            srcdir: Sphinx project source directory path.

        Returns:
            Parsed JSON data as dict, list, or primitive value.

        Raises:
            JsonTableError: If path validation or JSON parsing fails.
            FileNotFoundError: If specified file does not exist.
        """
        file_path = self._validate_file_path(source, srcdir)
        ensure_file_exists(file_path)

        try:
            with open(file_path, encoding=self.encoding) as f:
                return json.load(f)
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            raise JsonTableError(format_error(f"Failed to load {source}", e)) from e

    def parse_inline(self, content: list[str]) -> JsonData:
        """Parse inline JSON content from directive content lines.

        Args:
            content: List of strings representing JSON content lines.

        Returns:
            Parsed JSON data as dict, list, or primitive value.

        Raises:
            JsonTableError: If content is empty or contains invalid JSON.
        """
        validate_not_empty(content, EMPTY_CONTENT_ERROR)

        try:
            return json.loads("\n".join(content))
        except json.JSONDecodeError as e:
            raise JsonTableError(f"Invalid inline JSON: {e.msg}") from e


class JsonTableDirective(SphinxDirective):
    """
    Sphinx directive to render JSON data as reStructuredText tables.

    Processes JSON data from files or inline content and renders it as
    formatted tables in Sphinx documentation. Supports various JSON formats
    including objects, arrays, and nested structures with comprehensive
    security and performance safeguards.

    Options:
        header: Include first row of JSON objects as table header.
        encoding: Character encoding for JSON file reading (default: utf-8).
        limit: Maximum number of rows to display (0 for unlimited).
    """

    has_content = True
    required_arguments = 0
    optional_arguments = 1
    option_spec: ClassVar[dict] = {
        "header": directives.flag,
        "encoding": directives.unchanged,
        "limit": directives.nonnegative_int,  # Accept 0 or positive integers
    }

    def __init__(self, *args, **kwargs):
        """
        Initialize directive with JSON loader, converter, and builder.
        """
        super().__init__(*args, **kwargs)
        encoding = self.options.get("encoding", DEFAULT_ENCODING)

        # Get custom max rows from Sphinx config if available
        default_max_rows = getattr(
            self.env.config, "jsontable_max_rows", DEFAULT_MAX_ROWS
        )

        self.loader = JsonDataLoader(encoding)
        self.converter = TableConverter(default_max_rows)
        self.builder = TableBuilder()

    def run(self) -> list[nodes.Node]:
        """
        Execute the directive: load JSON, convert to table_data,
        build table node, and return it.

        Returns:
            List of docutils.nodes.Node (table or error node).
        """
        try:
            json_data = self._load_json_data()
            include_header = "header" in self.options
            limit = self.options.get("limit")  # None, 0, or positive integer

            table_data = self.converter.convert(json_data, include_header, limit)
            table_node = self.builder.build(table_data, include_header)
            return [table_node]

        except (JsonTableError, FileNotFoundError) as e:
            error_msg = format_error("JsonTable directive error", e)
            logger.error(error_msg)
            return [self._create_error_node(error_msg)]

    def _load_json_data(self) -> JsonData:
        """
        Determine JSON source: file (argument) or inline content.

        Returns:
            Parsed JSON data (object or list).

        Raises:
            JsonTableError: If no JSON source provided.
        """
        if self.arguments:
            return self.loader.load_from_file(
                self.arguments[0],
                Path(self.env.srcdir),
            )
        elif self.content:
            return self.loader.parse_inline(list(self.content))
        else:
            raise JsonTableError(NO_JSON_SOURCE_ERROR)

    def _create_error_node(self, message: str) -> nodes.Node:
        """
        Create a docutils.error node with the given message.

        Args:
            message: Error message to display in the documentation.

        Returns:
            nodes.error containing a paragraph with the message.
        """
        error_node = nodes.error()
        error_node += nodes.paragraph(text=message)
        return error_node
