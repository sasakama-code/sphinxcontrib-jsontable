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


class TableConverter:
    """JSON to tabular data converter with performance optimization.

    Converts various JSON data formats into 2D table structure suitable for
    Sphinx table generation. Includes comprehensive performance safeguards,
    memory limits, and support for multiple JSON formats including objects,
    arrays, and mixed data types.

    Attributes:
        default_max_rows: Maximum number of rows to process for performance.
    """

    def __init__(self, default_max_rows: int | None = None):
        """Initialize table converter with optional row limit configuration.

        Args:
            default_max_rows: Maximum rows to process (None uses DEFAULT_MAX_ROWS).
        """
        self.default_max_rows = default_max_rows or DEFAULT_MAX_ROWS

    def convert(
        self,
        data: JsonData,
        include_header: bool = False,
        limit: int | None = None,
    ) -> TableData:
        """Convert JSON data to 2D table format with optional headers and limits.

        Args:
            data: JSON data as dictionary, list, or primitive value.
            include_header: Whether to prepend header row from object keys.
            limit: Maximum number of data rows to include.

        Returns:
            2D list where each row is a list of string values.

        Raises:
            JsonTableError: If data is not dict or list, or if empty.
        """
        validate_not_empty(data, "No JSON data to process")

        # Apply default limit if no explicit limit provided
        effective_limit = self._apply_default_limit(data, limit)

        if isinstance(data, dict):
            return self._convert_dict(data, include_header, effective_limit)
        elif isinstance(data, list):
            return self._convert_list(data, include_header, effective_limit)
        else:
            raise JsonTableError(INVALID_JSON_DATA_ERROR)

    def _apply_default_limit(
        self, data: JsonData, user_limit: int | None
    ) -> int | None:
        """
        Apply default limit logic with user-friendly warnings.

        Args:
            data: The JSON data to process.
            user_limit: User-specified limit (None, 0, or positive int).

        Returns:
            Effective limit to use (None for unlimited, positive int for limit).
        """
        # If user explicitly sets limit=0, disable all limits
        if user_limit == 0:
            logger.info("JsonTable: Unlimited rows requested via :limit: 0")
            return None

        # If user provides explicit limit, use it
        if user_limit is not None:
            return user_limit

        # Estimate data size for default limit logic
        estimated_size = self._estimate_data_size(data)

        # Apply default limit if data is large
        if estimated_size > self.default_max_rows:
            logger.warning(
                f"Large dataset detected ({estimated_size:,} rows). "
                f"Showing first {self.default_max_rows:,} rows for performance. "
                f"Use :limit: option to customize (e.g., :limit: 0 for all rows)."
            )
            return self.default_max_rows

        # Data is small enough, no limit needed
        return None

    def _estimate_data_size(self, data: JsonData) -> int:
        """
        Estimate the number of rows that will be generated from JSON data.

        Args:
            data: JSON data to estimate.

        Returns:
            Estimated number of rows.
        """
        if isinstance(data, dict):
            return 1  # Single object = 1 row
        elif isinstance(data, list):
            return len(data)  # Array length = row count
        else:
            return 0

    def _convert_dict(
        self,
        data: dict[str, Any],
        include_header: bool,
        limit: int | None = None,
    ) -> TableData:
        """
        Convert a single JSON object into table rows, considering limit.

        Args:
            data: JSON object as dict.
            include_header: Whether to include a header row.
            limit: Row limit (None or positive integer).

        Returns:
            TableData rows for the object.
        """
        if limit is not None and limit <= 0:
            return []
        return self._convert_object_list([data], include_header, limit)

    def _convert_list(
        self,
        data: list[Any],
        include_header: bool,
        limit: int | None = None,
    ) -> TableData:
        """
        Convert a JSON array into table rows, dispatching by element type.

        Args:
            data: JSON array as list.
            include_header: Whether to include headers for objects.
            limit: Row limit.

        Returns:
            TableData rows for the array.

        Raises:
            JsonTableError: If first element is null or unsupported type.
        """
        if not data:
            return []
        limited_data = data[:limit] if limit is not None else data
        first_item = limited_data[0]
        if first_item is None:
            raise JsonTableError("Invalid array data: null first element")

        if isinstance(first_item, dict):
            return self._convert_object_list(limited_data, include_header, limit)
        elif isinstance(first_item, list):
            return self._convert_array_list(limited_data, limit)
        else:
            raise JsonTableError("Array items must be objects or arrays")

    def _convert_object_list(
        self,
        objects: list[dict[str, Any]],
        include_header: bool,
        limit: int | None = None,
    ) -> TableData:
        """
        Convert a list of JSON objects into rows, extracting headers.

        Args:
            objects: List of dicts.
            include_header: Whether to prepend header row.
            limit: Row limit.

        Returns:
            TableData with optional header and rows.
        """
        if not objects:
            return []
        headers = self._extract_headers(objects)
        limited_objects = objects[:limit] if limit is not None else objects
        rows = [self._object_to_row(obj, headers) for obj in limited_objects]
        return [headers, *rows] if include_header else rows

    def _convert_array_list(
        self,
        arrays: list[list[Any]],
        limit: int | None = None,
    ) -> TableData:
        """
        Convert a list of arrays (lists) directly into rows.

        Args:
            arrays: List of lists representing rows.
            limit: Row limit.

        Returns:
            TableData rows with all elements stringified.
        """
        limited_arrays = arrays[:limit] if limit is not None else arrays
        return [[safe_str(cell) for cell in row] for row in limited_arrays]

    def _extract_headers(self, objects: list[dict[str, Any]]) -> list[str]:
        """
        Extract header names from JSON objects with key order preservation.

        The key order from the first object is preserved, and any additional keys
        from subsequent objects are appended in the order they are encountered.
        Includes performance optimizations and security constraints.

        Args:
            objects: List of dictionary objects to extract headers from.
                    Each object should be a dict with string keys.
                    Non-dict objects are automatically skipped.
                    Processing limited to first 10,000 objects.

        Returns:
            List of unique header keys in preserved order.
            Maximum 1,000 keys returned.
            String keys only, with length limit of 255 characters.
            Empty list if no valid objects provided.
        """
        if not objects:
            return []

        ordered_keys = []
        seen_keys = set()

        # Realistic limits for performance and security
        MAX_KEYS = 1000
        MAX_OBJECTS = min(len(objects), 10000)
        MAX_KEY_LENGTH = 255

        for i in range(MAX_OBJECTS):
            obj = objects[i]
            if not isinstance(obj, dict):
                continue

            for key in obj:
                if len(ordered_keys) >= MAX_KEYS:
                    return ordered_keys

                if (
                    key not in seen_keys
                    and isinstance(key, str)
                    and key != ""
                    and len(key) <= MAX_KEY_LENGTH
                ):
                    ordered_keys.append(key)
                    seen_keys.add(key)

        return ordered_keys

    def _object_to_row(self, obj: dict[str, Any], headers: list[str]) -> list[str]:
        """
        Convert a JSON object to a row based on provided headers.

        Args:
            obj: JSON object dict.
            headers: List of header names to use as columns.

        Returns:
            List of stringified values corresponding to headers.
        """
        return [safe_str(obj.get(key, "")) for key in headers]


class TableBuilder:
    """
    Build docutils table nodes from structured table data.

    Converts 2D string arrays into properly formatted docutils table nodes
    suitable for Sphinx documentation generation with support for headers,
    multi-column layouts, and proper content escaping.
    """

    def build(self, table_data: TableData, has_header: bool = False) -> nodes.table:
        """
        Build a docutils.nodes.table from 2D list of strings.

        Args:
            table_data: 2D list representing table content.
            has_header: Whether the first row is a header (default False).

        Returns:
            nodes.table node ready for inclusion in document.
        """
        if not table_data:
            return self._create_empty_table()

        max_cols = max(len(row) for row in table_data)
        table = self._create_table_structure(max_cols)

        if has_header:
            self._add_header(table, table_data[0])
            body_data = table_data[1:]
        else:
            body_data = table_data

        self._add_body(table, body_data, max_cols)
        return table

    def _create_empty_table(self) -> nodes.table:
        """
        Create an empty table node with one column.

        Returns:
            nodes.table with a single colspec.
        """
        table = nodes.table()
        tgroup = nodes.tgroup(cols=1)
        table += tgroup
        return table

    def _create_table_structure(self, cols: int) -> nodes.table:
        """
        Create a table structure with given number of columns.

        Args:
            cols: Number of columns for the table.

        Returns:
            nodes.table with tgroup and colspec elements.
        """
        table = nodes.table()
        tgroup = nodes.tgroup(cols=cols)
        table += tgroup

        for _ in range(cols):
            tgroup += nodes.colspec(colwidth=1)

        return table

    def _add_header(self, table: nodes.table, header_data: list[str]) -> None:
        """
        Add a header row to an existing table node.

        Args:
            table: nodes.table to modify.
            header_data: List of header cell strings.
        """
        thead = nodes.thead()
        header_row = self._create_row(header_data)
        thead += header_row
        table[0] += thead

    def _add_body(
        self,
        table: nodes.table,
        body_data: TableData,
        max_cols: int,
    ) -> None:
        """
        Add body rows to an existing table node.

        Args:
            table: nodes.table to modify.
            body_data: 2D list for body rows.
            max_cols: Maximum number of columns for padding.
        """
        tbody = nodes.tbody()

        for row_data in body_data:
            padded_row = row_data + [""] * (max_cols - len(row_data))
            tbody += self._create_row(padded_row)

        table[0] += tbody

    def _create_row(self, row_data: list[str]) -> nodes.row:
        """
        Create a docutils row node from a list of cell strings.

        Args:
            row_data: List of strings for each cell in the row.

        Returns:
            nodes.row containing entry and paragraph nodes.
        """
        row = nodes.row()
        for cell_data in row_data:
            entry = nodes.entry()
            entry += nodes.paragraph(text=cell_data)
            row += entry
        return row


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
            return self.loader.parse_inline(self.content)
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
