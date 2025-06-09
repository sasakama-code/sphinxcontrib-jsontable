"""JSON to table data conversion utilities with performance optimization.

Converts various JSON data formats into 2D table structure suitable for Sphinx
table generation with comprehensive performance safeguards and memory limits.

Features:
- Multiple JSON format support (objects, arrays, mixed types)
- Performance limits and memory safety
- Header generation from object keys
- Comprehensive data validation
"""

from __future__ import annotations

from typing import Any

from sphinx.util import logging

from .data_loaders import JsonData, JsonTableError, validate_not_empty

logger = logging.getLogger(__name__)

TableData = list[list[str]]

DEFAULT_MAX_ROWS = 10000  # Conservative limit for performance and memory safety


def safe_str(value: Any) -> str:
    """
    Safely convert a value to string, returning empty string for None.

    Args:
        value: Any value to convert to string.

    Returns:
        String representation of value, or empty string if value is None.
    """
    return str(value) if value is not None else ""


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
            raise JsonTableError("JSON data must be an array or object")

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
        limit: int | None,
    ) -> TableData:
        """Convert dictionary to table format.

        Args:
            data: Dictionary data to convert.
            include_header: Whether to include header row.
            limit: Maximum number of rows to include.

        Returns:
            2D table data with optional header row.
        """
        if not data:
            return []

        keys = list(data.keys())
        values = [safe_str(data[key]) for key in keys]

        table = []
        if include_header:
            table.append(keys)

        table.append(values)
        return table

    def _convert_list(
        self,
        data: list[Any],
        include_header: bool,
        limit: int | None,
    ) -> TableData:
        """Convert list to table format with optional row limiting.

        Args:
            data: List data to convert.
            include_header: Whether to include header row.
            limit: Maximum number of rows to include.

        Returns:
            2D table data with optional header row and row limiting.
        """
        if not data:
            return []

        # Handle primitive arrays directly
        if not isinstance(data[0], dict):
            return self._convert_primitive_array(data, include_header, limit)

        # Handle array of objects
        return self._convert_object_array(data, include_header, limit)

    def _convert_primitive_array(
        self,
        data: list[Any],
        include_header: bool,
        limit: int | None,
    ) -> TableData:
        """Convert array of primitive values to table format.

        Args:
            data: List of primitive values.
            include_header: Whether to include header row.
            limit: Maximum number of rows to include.

        Returns:
            2D table data where each primitive becomes a single-column row.
        """
        table = []

        if include_header:
            table.append(["Value"])

        # Apply limit to primitive data
        limited_data = data[:limit] if limit is not None else data

        for item in limited_data:
            table.append([safe_str(item)])

        return table

    def _convert_object_array(
        self,
        data: list[dict[str, Any]],
        include_header: bool,
        limit: int | None,
    ) -> TableData:
        """Convert array of objects to table format with consistent columns.

        Args:
            data: List of dictionary objects.
            include_header: Whether to include header row.
            limit: Maximum number of rows to include.

        Returns:
            2D table data with consistent column structure.
        """
        if not data:
            return []

        # Apply limit to object array data
        limited_data = data[:limit] if limit is not None else data

        # Extract all unique keys across all objects
        all_keys = set()
        for obj in limited_data:
            if isinstance(obj, dict):
                all_keys.update(obj.keys())

        # Sort keys for consistent column ordering
        sorted_keys = sorted(all_keys)

        table = []

        if include_header:
            table.append(sorted_keys)

        # Convert each object to table row
        for obj in limited_data:
            if isinstance(obj, dict):
                row = [safe_str(obj.get(key, "")) for key in sorted_keys]
                table.append(row)
            else:
                # Handle mixed array with non-dict elements
                row = [safe_str(obj)] + [""] * (len(sorted_keys) - 1)
                table.append(row)

        return table
