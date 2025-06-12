"""RAG processing result data container.

Provides the main data structure for storing and organizing results
from the complete RAG processing pipeline execution.

Created: 2025-06-12
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..rag.advanced_metadata import AdvancedMetadata
from ..rag.metadata_extractor import BasicMetadata
from ..rag.search_facets import GeneratedFacets
from ..rag.semantic_chunker import SemanticChunk

__all__ = ["RAGProcessingResult"]


@dataclass
class RAGProcessingResult:
    """Comprehensive result container for RAG processing pipeline execution.

    Attributes:
        basic_metadata: Basic metadata extracted from JSON data.
        semantic_chunks: List of semantic chunks created from content.
        advanced_metadata: Advanced statistical analysis results (optional).
        generated_facets: Generated search facets (optional).
        export_data: Exported metadata in various formats (optional).
    """

    basic_metadata: BasicMetadata
    semantic_chunks: list[SemanticChunk]
    advanced_metadata: AdvancedMetadata | None = None
    generated_facets: GeneratedFacets | None = None
    export_data: dict[str, Any] | None = None

    def has_advanced_features(self) -> bool:
        """Check if advanced RAG features are available.
        
        Returns:
            True if advanced metadata or facets are generated.
        """
        return self.advanced_metadata is not None or self.generated_facets is not None

    def get_export_formats(self) -> list[str]:
        """Get list of available export formats.
        
        Returns:
            List of format names if export data is available, empty list otherwise.
        """
        if self.export_data:
            return list(self.export_data.keys())
        return []

    def get_chunk_count(self) -> int:
        """Get total number of semantic chunks.
        
        Returns:
            Number of semantic chunks generated.
        """
        return len(self.semantic_chunks)