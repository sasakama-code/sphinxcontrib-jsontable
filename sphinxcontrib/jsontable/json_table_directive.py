"""Main JSON table directive implementation for Sphinx integration.

Provides the core JsonTableDirective that integrates JSON data loading, table
conversion, and docutils table generation for Sphinx documentation.

Features:
- File and inline JSON content support
- Security validation and performance limits
- Configurable options (header, encoding, row limits)
- Comprehensive error handling
- Integration with Sphinx environment
"""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.util import logging
from sphinx.util.docutils import SphinxDirective

from .data_loaders import (
    DEFAULT_ENCODING,
    NO_JSON_SOURCE_ERROR,
    JsonData,
    JsonDataLoader,
    JsonTableError,
    format_error,
)
from .table_builders import TableBuilder
from .table_converters import DEFAULT_MAX_ROWS, TableConverter

logger = logging.getLogger(__name__)


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
            return self.loader.load_from_content("\n".join(self.content))
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
