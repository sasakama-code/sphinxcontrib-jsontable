"""RAG pipeline processing logic.

Handles the complete RAG processing pipeline execution including metadata
extraction, semantic chunking, advanced analysis, and export generation.

Created: 2025-06-12
"""

from __future__ import annotations

import logging
from dataclasses import asdict
from typing import TYPE_CHECKING, Any, cast

from docutils import nodes

from ..rag.advanced_metadata import AdvancedMetadataGenerator
from ..rag.metadata_exporter import MetadataExporter
from ..rag.metadata_extractor import RAGMetadataExtractor
from ..rag.search_facets import SearchFacetGenerator
from ..rag.semantic_chunker import SemanticChunk, SemanticChunker
from .rag_processing_result import RAGProcessingResult

if TYPE_CHECKING:
    from sphinx.environment import BuildEnvironment

logger = logging.getLogger(__name__)

__all__ = ["RAGPipelineProcessor"]


class RAGPipelineProcessor:
    """RAG processing pipeline executor.

    Handles the complete execution of the RAG processing pipeline including
    all phases of metadata extraction, chunking, and export generation.
    """

    def __init__(
        self,
        metadata_extractor: RAGMetadataExtractor,
        semantic_chunker: SemanticChunker | None = None,
        advanced_generator: AdvancedMetadataGenerator | None = None,
        facet_generator: SearchFacetGenerator | None = None,
        metadata_exporter: MetadataExporter | None = None,
    ):
        """Initialize RAG pipeline processor.

        Args:
            metadata_extractor: Basic metadata extractor.
            semantic_chunker: Optional semantic chunker.
            advanced_generator: Optional advanced metadata generator.
            facet_generator: Optional search facet generator.
            metadata_exporter: Optional metadata exporter.
        """
        self.metadata_extractor = metadata_extractor
        self.semantic_chunker = semantic_chunker
        self.advanced_generator = advanced_generator
        self.facet_generator = facet_generator
        self.metadata_exporter = metadata_exporter

    def process_rag_pipeline(
        self,
        json_data: Any,
        options: dict[str, Any],
        export_formats: list[str] | None = None,
    ) -> RAGProcessingResult:
        """Execute the complete RAG processing pipeline.

        Args:
            json_data: Input JSON data to process through the pipeline.
            options: Processing options dictionary.
            export_formats: Optional list of export formats.

        Returns:
            RAGProcessingResult containing all processing outputs including
            metadata, chunks, facets, and export data.
        """
        # Phase 1: Basic metadata extraction
        basic_metadata = self.metadata_extractor.extract(json_data, options)

        # Phase 1: Semantic chunking
        semantic_chunks: list[SemanticChunk] = []
        if self.semantic_chunker and "semantic-chunks" in options:
            semantic_chunks = self.semantic_chunker.process(json_data, basic_metadata)

        # Phase 2: Advanced metadata generation
        advanced_metadata = None
        if self.advanced_generator and "advanced-metadata" in options:
            advanced_metadata = self.advanced_generator.generate_advanced_metadata(
                json_data, asdict(basic_metadata)
            )

        # Phase 2: Search facet generation
        generated_facets = None
        if self.facet_generator and advanced_metadata and "facet-generation" in options:
            generated_facets = self.facet_generator.generate_facets(advanced_metadata)

        # Phase 2: Metadata export
        export_data = None
        if (
            self.metadata_exporter
            and advanced_metadata
            and generated_facets
            and export_formats
        ):
            export_data = self.metadata_exporter.export_metadata(
                advanced_metadata, generated_facets, export_formats
            )

        return RAGProcessingResult(
            basic_metadata=basic_metadata,
            semantic_chunks=semantic_chunks,
            advanced_metadata=advanced_metadata,
            generated_facets=generated_facets,
            export_data=export_data,
        )

    def attach_rag_metadata(
        self, table_node: nodes.Node, rag_result: RAGProcessingResult
    ) -> None:
        """Attach RAG processing metadata to table node as custom attributes.

        Args:
            table_node: Docutils table node to annotate with metadata.
            rag_result: Complete RAG processing results to attach.
        """
        # Add RAG metadata as custom attributes using cast for type safety
        element_node = cast(nodes.Element, table_node)
        if not hasattr(element_node, "attributes"):
            element_node.attributes = {}

        # Basic metadata
        element_node.attributes["rag_table_id"] = rag_result.basic_metadata.table_id
        element_node.attributes["rag_semantic_summary"] = (
            rag_result.basic_metadata.semantic_summary
        )
        element_node.attributes["rag_search_keywords"] = ",".join(
            rag_result.basic_metadata.search_keywords
        )

        # Advanced metadata (if available)
        if rag_result.advanced_metadata:
            element_node.attributes["rag_row_count"] = str(
                rag_result.advanced_metadata.total_rows
            )
            element_node.attributes["rag_column_count"] = str(
                rag_result.advanced_metadata.total_columns
            )

        # Semantic chunks information
        element_node.attributes["rag_chunk_count"] = str(
            len(rag_result.semantic_chunks)
        )

        # Export information
        if rag_result.export_data:
            element_node.attributes["rag_export_formats"] = ",".join(
                rag_result.get_export_formats()
            )

    def output_debug_info(
        self, rag_result: RAGProcessingResult, env: BuildEnvironment
    ) -> None:
        """Output comprehensive debug information for RAG processing.

        Args:
            rag_result: RAG processing results to debug.
            env: Sphinx build environment for output paths.
        """
        debug_info = {
            "basic_metadata": {
                "table_id": rag_result.basic_metadata.table_id,
                "row_count": rag_result.basic_metadata.row_count,
                "column_count": rag_result.basic_metadata.column_count,
                "semantic_summary": rag_result.basic_metadata.semantic_summary,
                "search_keywords": rag_result.basic_metadata.search_keywords,
            },
            "semantic_chunks": {
                "count": len(rag_result.semantic_chunks),
                "chunks": [
                    {
                        "chunk_id": chunk.chunk_id,
                        "content_preview": chunk.content[:100] + "...",
                        "token_count": chunk.token_count,
                    }
                    for chunk in rag_result.semantic_chunks[:3]  # First 3 chunks
                ],
            },
        }

        if rag_result.advanced_metadata:
            debug_info["advanced_metadata"] = {
                "total_rows": rag_result.advanced_metadata.total_rows,
                "total_columns": rag_result.advanced_metadata.total_columns,
                "quality_score": rag_result.advanced_metadata.quality_score,
            }

        if rag_result.generated_facets:
            debug_info["generated_facets"] = {
                "facet_count": len(rag_result.generated_facets.facets),
                "facet_types": [
                    facet.facet_type for facet in rag_result.generated_facets.facets
                ],
            }

        if rag_result.export_data:
            debug_info["export_data"] = {
                "formats": list(rag_result.export_data.keys()),
                "total_size": sum(
                    len(str(data)) for data in rag_result.export_data.values()
                ),
            }

        logger.info(f"RAG Processing Debug Info: {debug_info}")
