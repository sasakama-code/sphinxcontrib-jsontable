"""Enhanced JSON Table Directive with RAG Integration.

Extended JsonTableDirective that provides RAG capabilities with zero impact
on existing functionality through opt-in features.

Features:
- Modular RAG integration with SOLID principle compliance
- Zero-impact opt-in RAG capabilities
- Advanced metadata generation with Japanese language support
- Semantic chunking for search optimization
- Multi-format export (JSON-LD, OpenSearch, PLaMo-ready)
- Comprehensive error handling with graceful fallbacks

Created: 2025-06-07 (Refactored: 2025-06-12)
Author: Claude Code Assistant
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.util import logging

from .directives import JsonTableDirective
from .enhanced_directive import (
    EnhancedDirectiveOptionsManager,
    RAGPipelineProcessor,
    RAGProcessingResult,
)

if TYPE_CHECKING:
    from sphinx.application import Sphinx

logger = logging.getLogger(__name__)

__all__ = ["EnhancedJsonTableDirective"]


class EnhancedJsonTableDirective(JsonTableDirective):
    """Enhanced JSON table directive with comprehensive RAG integration.

    Extends the base JsonTableDirective with optional RAG capabilities including
    advanced metadata extraction, semantic chunking, search facet generation,
    and multi-format export. Maintains full backward compatibility while adding
    powerful AI and search integration features through opt-in configuration.

    Features:
    - Zero-impact RAG integration (opt-in only)
    - Advanced metadata generation with Japanese language support
    - Semantic chunking for search optimization
    - Multi-format export (JSON-LD, OpenSearch, PLaMo-ready)
    - Comprehensive error handling with graceful fallbacks
    """

    # Extend base options with RAG-specific options
    option_spec: ClassVar[dict[str, Any]] = {
        **JsonTableDirective.option_spec,
        "rag-enabled": directives.flag,
        "semantic-chunks": directives.flag,
        "advanced-metadata": directives.flag,
        "export-formats": directives.unchanged,
        "metadata-tags": directives.unchanged,
        "chunk-strategy": directives.unchanged,
        "facet-generation": directives.flag,
    }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize enhanced directive with conditional RAG component setup.

        Args:
            *args: Positional arguments passed to parent JsonTableDirective.
            **kwargs: Keyword arguments passed to parent JsonTableDirective.
        """
        super().__init__(*args, **kwargs)
        
        # Initialize options manager for RAG components
        self.options_manager = EnhancedDirectiveOptionsManager(
            dict(self.options), self.env
        )

    def run(self) -> list[nodes.Node]:
        """Execute directive processing with optional RAG pipeline integration.

        Processes standard table generation and conditionally executes RAG
        pipeline based on directive options. Includes comprehensive error
        handling to ensure graceful fallback to standard functionality.

        Returns:
            List of docutils nodes representing the generated table.
        """
        try:
            # Execute standard table generation
            table_nodes = super().run()

            # Return standard table if RAG is not enabled
            if not self.options_manager.is_rag_enabled():
                return table_nodes

            # Get RAG processor and execute pipeline
            rag_processor = self.options_manager.get_rag_processor()
            if rag_processor:
                json_data = self._get_json_data()
                rag_result = rag_processor.process_rag_pipeline(
                    json_data,
                    dict(self.options),
                    self.options_manager.get_export_formats()
                )

                # Attach RAG metadata to table nodes
                if table_nodes and rag_result:
                    rag_processor.attach_rag_metadata(table_nodes[0], rag_result)

                # Output debug information if enabled
                if self.env.app.config.get("rag_debug_mode", False):
                    rag_processor.output_debug_info(rag_result, self.env)

            return table_nodes

        except Exception as e:
            logger.error(f"Enhanced directive RAG integration error: {e}")
            # Fallback to standard functionality on error
            return super().run()

    def _get_json_data(self) -> dict[str, Any] | list[Any]:
        """Get JSON data from file or inline content.
        
        Returns:
            Parsed JSON data from file or inline content.
            
        Raises:
            ValueError: If no JSON data source is provided.
        """
        if self.arguments:
            # File-based JSON data
            file_path = Path(self.env.srcdir) / self.arguments[0]
            if not self.options_manager.is_safe_path(file_path):
                raise ValueError(f"Unsafe file path: {self.arguments[0]}")
            
            with file_path.open(encoding="utf-8") as f:
                return json.load(f)
        elif self.content:
            # Inline JSON content
            return json.loads("\n".join(self.content))
        else:
            raise ValueError("No JSON data specified")


def setup(app: Sphinx) -> dict[str, Any]:
    """Setup function for Sphinx extension registration.
    
    Args:
        app: Sphinx application instance.
        
    Returns:
        Extension metadata dictionary.
    """
    # Register the enhanced directive
    app.add_directive("enhanced-jsontable", EnhancedJsonTableDirective)
    
    # Add configuration values for RAG features
    app.add_config_value("rag_debug_mode", False, "env", [bool])
    
    return {
        "version": "0.3.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }