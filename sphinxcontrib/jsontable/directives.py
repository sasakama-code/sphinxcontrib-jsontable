"""
json_table_directive.py

Sphinx directive for rendering JSON (file or inline) as ReStructuredText tables.
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
    Exception raised for errors that occur during JSON to table conversion.

    Attributes:
        message -- explanation of the error
    """


def validate_not_empty(data: Any, error_msg: str) -> None:
    """
    Raise JsonTableError with the given message if data is None or empty.

    Args:
        data: The data to validate, may be None or an empty sequence.
        error_msg: Error message for exception when data is empty.
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
    """
    Check that the given file path exists; raise FileNotFoundError if not.

    Args:
        path: Path object representing the file path to check.

    Raises:
        FileNotFoundError: If the file does not exist at the given path.
    """
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")


def format_error(context: str, error: Exception) -> str:
    """
    Format an error message combining a context string with exception details.

    Args:
        context: Description of the operation or location where the error occurred.
        error: Exception instance containing details about the error.

    Returns:
        A formatted string "{context}: {error}".
    """
    return f"{context}: {error}"


def is_safe_path(path: Path, base: Path) -> bool:
    """
    Determine if a given path is a subpath of a base directory to prevent directory traversal.

    Args:
        path: The Path to validate.
        base: The base directory Path against which to validate.

    Returns:
        True if path is within base directory, False otherwise.
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
    """
    Loader class for reading JSON data from files or inline content.

    Args:
        encoding: Character encoding to use when reading files (default: "utf-8").
    """

    def __init__(self, encoding: str = DEFAULT_ENCODING):
        self.encoding = self._validate_encoding(encoding)

    def _validate_encoding(self, encoding: str) -> str:
        """
        Validate provided encoding; return default if invalid.

        Args:
            encoding: Encoding name to validate.

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
        """
        Validate and resolve a JSON file path relative to a source directory.

        Args:
            source: Relative path string to the JSON file.
            srcdir: Base directory Path for resolving the source.

        Returns:
            Resolved Path object for the JSON file.

        Raises:
            JsonTableError: If the path is unsafe (directory traversal).
        """
        file_path = srcdir / source
        if not is_safe_path(file_path, srcdir):
            raise JsonTableError(f"Invalid file path: {source}")
        return file_path

    def load_from_file(self, source: str, srcdir: Path) -> JsonData:
        """
        Load JSON data from a file within the Sphinx source directory.

        Args:
            source: Relative file path to JSON.
            srcdir: Path of the Sphinx project source directory.

        Returns:
            Parsed JSON data (object or array).

        Raises:
            JsonTableError: If path validation fails or JSON decoding fails.
            FileNotFoundError: If the file does not exist.
        """
        file_path = self._validate_file_path(source, srcdir)
        ensure_file_exists(file_path)

        try:
            with open(file_path, encoding=self.encoding) as f:
                return json.load(f)
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            raise JsonTableError(format_error(f"Failed to load {source}", e)) from e

    def parse_inline(self, content: list[str]) -> JsonData:
        """
        Parse inline JSON content provided as lines of text.

        Args:
            content: List of strings representing lines of JSON.

        Returns:
            Parsed JSON data (object or array).

        Raises:
            JsonTableError: If content is empty or invalid JSON.
        """
        validate_not_empty(content, EMPTY_CONTENT_ERROR)

        try:
            return json.loads("\n".join(content))
        except json.JSONDecodeError as e:
            raise JsonTableError(f"Invalid inline JSON: {e.msg}") from e


class TableConverter:
    """
    Convert JSON data into a 2D list (TableData) suitable for table building.

    This class handles the conversion of JSON data (objects or arrays) into
    tabular format while applying performance safeguards and memory limits.
    """

    def __init__(self, default_max_rows: int | None = None):
        """
        Initialize TableConverter with optional custom default limit.

        Args:
            default_max_rows: Custom default row limit (None uses DEFAULT_MAX_ROWS).
        """
        self.default_max_rows = default_max_rows or DEFAULT_MAX_ROWS

    def convert(
        self,
        data: JsonData,
        include_header: bool = False,
        limit: int | None = None,
    ) -> TableData:
        """
        Convert JSON data to a list of rows, optionally including headers and limiting rows.

        Args:
            data: JSON data as dict or list.
            include_header: Whether to include header row (default False).
            limit: Maximum number of rows to include (None for default limit).

        Returns:
            TableData: A list of rows, each row itself a list of strings.

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
    Build docutils.table nodes from TableData for Sphinx documentation.

    Methods:
        build: Create and populate table nodes with header/body.
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
    Sphinx directive to render JSON data as a reStructuredText table.

    Options:
        header: Flag to include the first row of JSON objects as table header.
        encoding: Character encoding for JSON file reading.
        limit: Positive integer to limit the number of rows, or 0 for unlimited.
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
