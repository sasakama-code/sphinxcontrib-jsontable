"""Legacy Sphinx directive for backward compatibility (DEPRECATED).

⚠️  DEPRECATION WARNING: This module is deprecated and maintained only for backward
    compatibility. New code should use the recommended 'json_table_directive' module.

Migration path:
    from sphinxcontrib.jsontable.directives import JsonTableDirective  # OLD
    from sphinxcontrib.jsontable.json_table_directive import JsonTableDirective  # NEW

This legacy implementation will be removed in a future version.
"""

from __future__ import annotations

import warnings
from typing import Any, ClassVar

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.util import logging
from sphinx.util.docutils import SphinxDirective

# Import from the proper modular implementation
from .data_loaders import (
    DEFAULT_ENCODING,
    NO_JSON_SOURCE_ERROR,
    JsonDataLoader,
    JsonTableError,
    format_error,
)
from .table_builders import TableBuilder
from .table_converters import DEFAULT_MAX_ROWS, TableConverter

logger = logging.getLogger(__name__)

# Deprecation warning for legacy usage
warnings.warn(
    "sphinxcontrib.jsontable.directives is deprecated. "
    "Use sphinxcontrib.jsontable.json_table_directive instead. "
    "This module will be removed in a future version.",
    DeprecationWarning,
    stacklevel=2,
)


class JsonTableDirective(SphinxDirective):
    """
    Legacy JSON table directive (DEPRECATED).

    ⚠️  This implementation is deprecated. Use the new JsonTableDirective from
        json_table_directive module instead.

    This class is maintained only for backward compatibility and will be removed
    in a future version. New projects should use the recommended implementation.
    """

    has_content: ClassVar[bool] = True
    required_arguments: ClassVar[int] = 0
    optional_arguments: ClassVar[int] = 1
    final_argument_whitespace: ClassVar[bool] = False
    option_spec: ClassVar[dict[str, Any]] = {
        "header": directives.flag,
        "encoding": directives.unchanged,
        "limit": directives.positive_int,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Issue deprecation warning when directive is instantiated
        logger.warning(
            "JsonTableDirective from directives.py is deprecated. "
            "Use the new implementation from json_table_directive.py"
        )

    def run(self) -> list[nodes.Node]:
        """Execute the legacy directive with deprecation handling."""
        try:
            # Get configuration
            encoding = self.options.get("encoding", DEFAULT_ENCODING)
            include_header = "header" in self.options
            row_limit = self.options.get("limit", DEFAULT_MAX_ROWS)

            # Load JSON data
            loader = JsonDataLoader(encoding)

            if self.arguments:
                # File-based JSON
                source_path = self.arguments[0]
                json_data = loader.load_from_file(source_path, self.env.srcdir)
            elif self.content:
                # Inline JSON
                json_data = loader.load_from_content("\n".join(self.content))
            else:
                raise JsonTableError(NO_JSON_SOURCE_ERROR)

            # Convert and build table
            converter = TableConverter()
            table_data = converter.convert(json_data, include_header)

            # Apply row limit if specified
            if row_limit > 0:
                table_data = table_data[: row_limit + (1 if include_header else 0)]

            builder = TableBuilder()
            return [builder.build(table_data, include_header)]

        except Exception as e:
            error_msg = format_error("Legacy JsonTableDirective error", e)
            logger.error(error_msg)
            error_node = nodes.error("", nodes.paragraph("", error_msg))
            return [error_node]
