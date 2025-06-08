"""
RAG (Retrieval-Augmented Generation) integration module for sphinxcontrib-jsontable.

This module provides functionality to convert JSON table data into RAG-compatible
formats with semantic chunking, metadata extraction, and vector processing.

Phase 1: Semantic Data Output
- EnhancedJsonTableDirective: Extended directive with RAG capabilities
- RAGMetadataExtractor: Automatic metadata extraction from JSON data
- SemanticChunker: Intelligent data chunking for search optimization

Phase 2: Advanced Metadata Generation
- AdvancedMetadataGenerator: Statistical analysis and entity classification
- SearchFacetGenerator: Automatic search facet generation
- MetadataExporter: Multi-format export (JSON-LD, OpenSearch, etc.)

Phase 3: PLaMo-Embedding-1B Integration
- VectorProcessor: PLaMo-Embedding-1B integration for Japanese text
- SearchIndexGenerator: Vector index generation for semantic search
"""

# Phase 1 modules (to be implemented)
# from .metadata_extractor import RAGMetadataExtractor
# from .semantic_chunker import SemanticChunker

# Phase 2 modules (implemented)
from .advanced_metadata import AdvancedMetadataGenerator
from .metadata_exporter import MetadataExporter
from .search_facets import SearchFacetGenerator

__version__ = "0.2.0-dev"
__all__ = [
    # Phase 2 (implemented)
    "AdvancedMetadataGenerator",
    "MetadataExporter",
    "SearchFacetGenerator",
    # Phase 1 (pending)
    # "RAGMetadataExtractor",
    # "SemanticChunker",
]
