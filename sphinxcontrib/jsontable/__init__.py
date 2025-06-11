"""
Sphinx extension for rendering JSON data as tables.

This extension provides the jsontable directive that can render JSON data
from external files or inline content as HTML tables in Sphinx documentation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

# Legacy import support for backward compatibility
from .directives import JsonTableDirective as LegacyJsonTableDirective
from .enhanced_directive import EnhancedJsonTableDirective

# Import from new modular structure
from .json_table_directive import JsonTableDirective
from .table_converters import DEFAULT_MAX_ROWS

if TYPE_CHECKING:
    from sphinx.application import Sphinx

__version__ = "0.3.0"
__author__ = "sasakama-code"
__email__ = "sasakamacode@gmail.com"


def setup(app: Sphinx) -> dict[str, Any]:
    """
    Sphinx extension setup function.

    Args:
        app: Sphinx application instance

    Returns:
        Extension metadata
    """
    # Register the jsontable directive
    app.add_directive("jsontable", JsonTableDirective)

    # Register the enhanced jsontable directive (RAG-enabled)
    app.add_directive("enhanced-jsontable", EnhancedJsonTableDirective)

    # Add configuration values for performance limits
    app.add_config_value(
        "jsontable_max_rows",
        DEFAULT_MAX_ROWS,
        "env",  # Rebuild environment when changed
        [int],  # Type validation
    )

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
