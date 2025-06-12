"""Enhanced directive options and component management.

Handles initialization, configuration, and lifecycle management of RAG
processing components based on directive options.

Created: 2025-06-12
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

from ..rag.advanced_metadata import AdvancedMetadataGenerator
from ..rag.metadata_exporter import MetadataExporter
from ..rag.metadata_extractor import RAGMetadataExtractor
from ..rag.search_facets import SearchFacetGenerator
from ..rag.semantic_chunker import SemanticChunker
from .rag_pipeline_processor import RAGPipelineProcessor

if TYPE_CHECKING:
    from sphinx.environment import BuildEnvironment

logger = logging.getLogger(__name__)

__all__ = ["EnhancedDirectiveOptionsManager"]


class EnhancedDirectiveOptionsManager:
    """RAG options and component lifecycle manager.

    Manages the initialization and configuration of RAG processing components
    based on directive options, providing centralized component management.
    """

    def __init__(self, options: dict[str, Any], env: BuildEnvironment):
        """Initialize options manager with directive configuration.

        Args:
            options: Directive options dictionary.
            env: Sphinx build environment.
        """
        self.options = options
        self.env = env
        self.rag_processor: RAGPipelineProcessor | None = None

        # Initialize RAG processor if enabled
        if self.is_rag_enabled():
            self.rag_processor = self._create_rag_processor()

    def is_rag_enabled(self) -> bool:
        """Check if RAG processing is enabled.

        Returns:
            True if rag-enabled flag is present in options.
        """
        return "rag-enabled" in self.options

    def has_semantic_chunks(self) -> bool:
        """Check if semantic chunking is enabled.

        Returns:
            True if semantic-chunks flag is present in options.
        """
        return "semantic-chunks" in self.options

    def has_advanced_metadata(self) -> bool:
        """Check if advanced metadata generation is enabled.

        Returns:
            True if advanced-metadata flag is present in options.
        """
        return "advanced-metadata" in self.options

    def has_facet_generation(self) -> bool:
        """Check if facet generation is enabled.

        Returns:
            True if facet-generation flag is present in options.
        """
        return "facet-generation" in self.options

    def get_chunk_strategy(self) -> str:
        """Get chunk strategy from options.

        Returns:
            Chunk strategy name, defaults to "adaptive".
        """
        return self.options.get("chunk-strategy", "adaptive")

    def get_export_formats(self) -> list[str]:
        """Parse export format specification from directive options.

        Returns:
            List of export format names specified in options, empty list if none.
        """
        if "export-formats" not in self.options:
            return []

        formats_str = self.options["export-formats"]
        return [fmt.strip() for fmt in formats_str.split(",") if fmt.strip()]

    def get_metadata_tags(self) -> list[str]:
        """Get metadata tags from options.

        Returns:
            List of metadata tags, empty list if none specified.
        """
        if "metadata-tags" not in self.options:
            return []

        tags_str = self.options["metadata-tags"]
        return [tag.strip() for tag in tags_str.split(",") if tag.strip()]

    def is_safe_path(self, path: Path) -> bool:
        """Validate file path for security and access restrictions.

        Args:
            path: File path to validate for safety.

        Returns:
            True if path is within source directory and safe to access.
        """
        try:
            # Restrict to source directory
            resolved_path = path.resolve()
            srcdir_path = Path(self.env.srcdir).resolve()
            return str(resolved_path).startswith(str(srcdir_path))
        except Exception:
            return False

    def _create_rag_processor(self) -> RAGPipelineProcessor:
        """Create and configure RAG pipeline processor.

        Returns:
            Configured RAGPipelineProcessor instance.
        """
        # Always initialize metadata extractor
        metadata_extractor = RAGMetadataExtractor()

        # Initialize optional components based on options
        semantic_chunker = None
        if self.has_semantic_chunks():
            chunk_strategy = self.get_chunk_strategy()
            semantic_chunker = SemanticChunker(chunk_strategy=chunk_strategy)

        advanced_generator = None
        if self.has_advanced_metadata():
            advanced_generator = AdvancedMetadataGenerator()

        facet_generator = None
        if self.has_facet_generation() and advanced_generator:
            facet_generator = SearchFacetGenerator()

        metadata_exporter = None
        export_formats = self.get_export_formats()
        if export_formats and advanced_generator:
            metadata_exporter = MetadataExporter()

        return RAGPipelineProcessor(
            metadata_extractor=metadata_extractor,
            semantic_chunker=semantic_chunker,
            advanced_generator=advanced_generator,
            facet_generator=facet_generator,
            metadata_exporter=metadata_exporter,
        )

    def get_rag_processor(self) -> RAGPipelineProcessor | None:
        """Get the configured RAG processor.

        Returns:
            RAGPipelineProcessor instance if RAG is enabled, None otherwise.
        """
        return self.rag_processor
