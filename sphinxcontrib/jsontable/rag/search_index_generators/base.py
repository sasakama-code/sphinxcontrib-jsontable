"""Common base classes and data structures for search index generators.

Provides shared data structures, base classes, and utilities used across
all search index generation modules.
"""

import time
from dataclasses import dataclass, field
from typing import Any

import numpy as np

__all__ = [
    "VectorIndex",
    "SemanticSearchIndex",
    "FacetedSearchIndex",
    "HybridSearchIndex",
    "ComprehensiveSearchIndex",
    "BaseIndexGenerator",
]


@dataclass
class VectorIndex:
    """Vector search index container.

    Args:
        faiss_index: Optional FAISS index for vector similarity search.
        fallback_embeddings: NumPy array fallback for vector storage.
        chunk_metadata: Metadata for each indexed chunk.
        search_parameters: Configuration parameters for search optimization.
        dimension: Vector dimension (default 1024 for PLaMo-Embedding-1B).
        index_type: Type of index implementation used.
    """

    faiss_index: Any | None = None  # FAISS index for vector search
    fallback_embeddings: np.ndarray | None = None  # Fallback embedding storage
    chunk_metadata: list[dict[str, Any]] = field(default_factory=list)
    search_parameters: dict[str, Any] = field(default_factory=dict)
    dimension: int = 1024
    index_type: str = "faiss_flatip"  # or "fallback_cosine"


@dataclass
class SemanticSearchIndex:
    """Semantic search index for keyword-based retrieval.

    Args:
        text_segments: List of text content segments for search.
        semantic_mappings: Mappings between semantic concepts and chunk indices.
        japanese_keyword_index: Japanese keyword to chunk index mappings.
        business_term_index: Business terminology to chunk index mappings.
    """

    text_segments: list[str] = field(default_factory=list)
    semantic_mappings: dict[str, list[int]] = field(default_factory=dict)
    japanese_keyword_index: dict[str, list[int]] = field(default_factory=dict)
    business_term_index: dict[str, list[int]] = field(default_factory=dict)


@dataclass
class FacetedSearchIndex:
    """Faceted search index for filtered retrieval.

    Args:
        categorical_facets: Categorical facet values mapped to chunk indices.
        numerical_facets: Numerical range facets mapped to chunk indices.
        temporal_facets: Temporal facets for date/time filtering.
        entity_facets: Entity-based facets for semantic filtering.
    """

    categorical_facets: dict[str, dict[str, list[int]]] = field(default_factory=dict)
    numerical_facets: dict[str, dict[str, list[int]]] = field(default_factory=dict)
    temporal_facets: dict[str, dict[str, list[int]]] = field(default_factory=dict)
    entity_facets: dict[str, dict[str, list[int]]] = field(default_factory=dict)


@dataclass
class HybridSearchIndex:
    """Hybrid search index configuration.

    Args:
        vector_weight: Weight for vector similarity scores in fusion.
        semantic_weight: Weight for semantic keyword scores in fusion.
        facet_weight: Weight for faceted search scores in fusion.
        fusion_algorithm: Algorithm used for score fusion.
    """

    vector_weight: float = 0.7
    semantic_weight: float = 0.2
    facet_weight: float = 0.1
    fusion_algorithm: str = "rank_fusion"


@dataclass
class ComprehensiveSearchIndex:
    """Comprehensive search index containing all search capabilities.

    Args:
        vector_index: Vector-based similarity search index.
        semantic_index: Keyword-based semantic search index.
        facet_index: Faceted search and filtering index.
        hybrid_index: Hybrid search fusion configuration.
        creation_time: Timestamp when index was created.
        total_chunks: Total number of chunks indexed.
        index_statistics: Statistics about index performance and content.
    """

    vector_index: VectorIndex | None = None
    semantic_index: SemanticSearchIndex | None = None
    facet_index: FacetedSearchIndex | None = None
    hybrid_index: HybridSearchIndex | None = None

    creation_time: str = field(
        default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S")
    )
    total_chunks: int = 0
    index_statistics: dict[str, Any] = field(default_factory=dict)


class BaseIndexGenerator:
    """Base class for all index generators.

    Provides common functionality and configuration management
    shared across all specialized index generators.
    """

    def __init__(self, config: dict[str, Any]):
        """Initialize base index generator.

        Args:
            config: Configuration dictionary for index generation.
        """
        self.config = config

    def validate_input(self, vector_chunks: list) -> bool:
        """Validate input vector chunks.

        Args:
            vector_chunks: List of vector chunks to validate.

        Returns:
            True if input is valid, False otherwise.
        """
        if not vector_chunks:
            return False

        if not isinstance(vector_chunks, list):
            return False

        # Check if all chunks have required attributes
        for chunk in vector_chunks:
            if not hasattr(chunk, "embedding"):
                return False
            if not hasattr(chunk, "original_chunk"):
                return False

        return True

    def get_default_config(self) -> dict[str, Any]:
        """Get default configuration for search index generation.

        Returns:
            Default configuration dictionary with optimized settings for Japanese search.
        """
        return {
            "vector_search": {
                "dimension": 1024,
                "index_type": "FlatIP",  # Inner Product for PLaMo
                "nprobe": 10,
                "search_k": 10,
            },
            "semantic_search": {
                "min_term_frequency": 2,
                "max_features": 10000,
                "japanese_tokenization": True,
            },
            "faceted_search": {
                "max_facet_values": 100,
                "enable_numerical_ranges": True,
                "enable_temporal_facets": True,
            },
            "hybrid_search": {
                "vector_weight": 0.7,
                "semantic_weight": 0.2,
                "facet_weight": 0.1,
                "rank_fusion_k": 10,
            },
        }
