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

# Phase 1 modules (implemented)
# Phase 2 modules (implemented)
from .advanced_metadata import AdvancedMetadataGenerator
from .metadata_exporter import MetadataExporter
from .metadata_extractor import RAGMetadataExtractor
from .query_processor import IntelligentQueryProcessor
from .search_facets import SearchFacetGenerator
from .search_index_generator import SearchIndexGenerator
from .semantic_chunker import SemanticChunker

# Phase 3 modules (implemented)
from .vector_processor import PLaMoVectorProcessor

__version__ = "0.3.0"
__all__ = [
    "AdvancedMetadataGenerator",
    "IntelligentQueryProcessor",
    "MetadataExporter",
    "PLaMoVectorProcessor",
    "RAGMetadataExtractor",
    "SearchFacetGenerator",
    "SearchIndexGenerator",
    "SemanticChunker",
]
