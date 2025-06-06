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

from .metadata_extractor import RAGMetadataExtractor
from .semantic_chunker import SemanticChunker

__version__ = "0.1.0-dev"
__all__ = [
    "RAGMetadataExtractor",
    "SemanticChunker",
]