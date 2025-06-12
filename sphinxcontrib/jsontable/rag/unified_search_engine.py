"""Unified Search Engine with Multi-Modal Search Capabilities.

Advanced search engine that integrates vector processing, semantic indexing,
and hybrid search with Japanese optimization and intelligent fallback.

Features:
- Multi-modal search: vector similarity + keyword matching + faceted filtering
- Japanese language optimization with business term recognition
- Intelligent query processing and intent classification
- Performance optimization with caching and parallel processing
- Flexible configuration and fallback mechanisms
- Real-time search result ranking and relevance scoring

Created: 2025-06-12
Author: Claude Code Assistant
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from .enhanced_vector_processor import EnhancedVectorProcessor
from .search_index_generators.faceted_index import FacetedIndexGenerator
from .search_index_generators.hybrid_index import HybridIndexGenerator
from .search_index_generators.japanese_processor import JapaneseQueryProcessor
from .search_index_generators.semantic_index import SemanticIndexGenerator
from .search_index_generators.vector_index import VectorIndexGenerator
from .semantic_chunker import SemanticChunk
from .vector_config import VectorConfig

logger = logging.getLogger(__name__)


@dataclass
class SearchQuery:
    """Unified search query structure."""

    query_text: str
    query_type: str = "hybrid"  # hybrid, semantic, vector, faceted
    filters: dict[str, Any] = field(default_factory=dict)
    max_results: int = 10
    min_score: float = 0.0
    boost_factors: dict[str, float] = field(default_factory=dict)
    language: str = "ja"  # Japanese by default
    include_metadata: bool = True


@dataclass
class SearchResult:
    """Search result structure with comprehensive metadata."""

    chunk_id: str
    content: str
    relevance_score: float
    search_type: str
    metadata: dict[str, Any] = field(default_factory=dict)
    highlighting: dict[str, list[str]] = field(default_factory=dict)
    explanation: dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchEngineMetrics:
    """Search engine performance metrics."""

    total_queries: int = 0
    avg_query_time: float = 0.0
    cache_hit_rate: float = 0.0
    index_size: int = 0
    active_indices: list[str] = field(default_factory=list)
    search_accuracy: float = 0.0


class UnifiedSearchEngine:
    """Unified search engine with multi-modal capabilities.

    Integrates vector processing, semantic indexing, and hybrid search
    with intelligent query processing and performance optimization.
    """

    def __init__(
        self,
        vector_config: VectorConfig | None = None,
        search_config: dict[str, Any] | None = None,
    ):
        """Initialize unified search engine.

        Args:
            vector_config: Vector processing configuration.
            search_config: Search engine configuration.
        """
        self.vector_config = vector_config or VectorConfig.get_default_config()
        self.search_config = search_config or self._get_default_search_config()

        # Initialize core components
        self.vector_processor = EnhancedVectorProcessor(self.vector_config)
        self.japanese_processor = JapaneseQueryProcessor()

        # Initialize search index generators
        self.semantic_generator = SemanticIndexGenerator(self.search_config)
        self.hybrid_generator = HybridIndexGenerator(self.search_config)
        self.vector_generator = VectorIndexGenerator(self.search_config)
        self.faceted_generator = FacetedIndexGenerator(self.search_config)

        # Search indices
        self._semantic_index = None
        self._vector_index = None
        self._hybrid_index = None
        self._faceted_index = None

        # Performance tracking
        self.metrics = SearchEngineMetrics()
        self._query_cache: dict[str, list[SearchResult]] = {}

        logger.info("UnifiedSearchEngine initialized with multi-modal capabilities")

    async def index_data(
        self,
        semantic_chunks: list[SemanticChunk],
        progress_callback: callable | None = None,
    ) -> None:
        """Index data for search operations.

        Args:
            semantic_chunks: Semantic chunks to index.
            progress_callback: Optional progress callback.
        """
        logger.info(f"Indexing {len(semantic_chunks)} semantic chunks")
        start_time = time.time()

        # Step 1: Generate vector embeddings
        if progress_callback:
            progress_callback(0.1, "Generating vector embeddings...")

        vector_result = await self.vector_processor.process_chunks(
            semantic_chunks,
            lambda p: progress_callback(0.1 + p * 0.4, "Processing vectors...")
            if progress_callback
            else None,
        )

        # Step 2: Build search indices
        if progress_callback:
            progress_callback(0.5, "Building search indices...")

        # Build semantic index
        self._semantic_index = self.semantic_generator.generate(
            vector_result.vector_chunks
        )

        # Build vector index
        self._vector_index = self.vector_generator.generate(vector_result.vector_chunks)

        # Build faceted index
        self._faceted_index = self.faceted_generator.generate(
            vector_result.vector_chunks
        )

        # Build hybrid index
        self._hybrid_index = self.hybrid_generator.generate()

        if progress_callback:
            progress_callback(0.9, "Optimizing indices...")

        # Update metrics
        self.metrics.index_size = len(semantic_chunks)
        self.metrics.active_indices = ["semantic", "vector", "faceted", "hybrid"]

        index_time = time.time() - start_time
        logger.info(f"Indexing completed in {index_time:.2f}s")

        if progress_callback:
            progress_callback(1.0, "Indexing complete")

    async def search(
        self, query: str | SearchQuery, **kwargs
    ) -> list[SearchResult]:
        """Execute unified search query.

        Args:
            query: Search query string or SearchQuery object.
            **kwargs: Additional search parameters.

        Returns:
            List of search results sorted by relevance.
        """
        # Normalize query
        if isinstance(query, str):
            search_query = SearchQuery(query_text=query, **kwargs)
        else:
            search_query = query

        start_time = time.time()

        # Check cache first
        cache_key = self._generate_cache_key(search_query)
        if cache_key in self._query_cache:
            self.metrics.cache_hit_rate = (
                self.metrics.cache_hit_rate * self.metrics.total_queries + 1
            ) / (self.metrics.total_queries + 1)
            return self._query_cache[cache_key]

        # Process query based on type
        if search_query.query_type == "hybrid":
            results = await self._hybrid_search(search_query)
        elif search_query.query_type == "semantic":
            results = await self._semantic_search(search_query)
        elif search_query.query_type == "vector":
            results = await self._vector_search(search_query)
        elif search_query.query_type == "faceted":
            results = await self._faceted_search(search_query)
        else:
            logger.warning(
                f"Unknown query type: {search_query.query_type}, using hybrid"
            )
            results = await self._hybrid_search(search_query)

        # Apply post-processing
        results = self._post_process_results(results, search_query)

        # Cache results
        self._query_cache[cache_key] = results

        # Update metrics
        query_time = time.time() - start_time
        self.metrics.total_queries += 1
        self.metrics.avg_query_time = (
            self.metrics.avg_query_time * (self.metrics.total_queries - 1) + query_time
        ) / self.metrics.total_queries

        logger.info(
            f"Search completed in {query_time:.3f}s, returned {len(results)} results"
        )

        return results

    async def _hybrid_search(self, query: SearchQuery) -> list[SearchResult]:
        """Execute hybrid search combining multiple modalities."""
        if not self._hybrid_index:
            raise ValueError("Hybrid index not available")

        # Execute parallel searches
        vector_task = self._vector_search(
            SearchQuery(
                query_text=query.query_text,
                query_type="vector",
                max_results=query.max_results * 2,
            )
        )

        semantic_task = self._semantic_search(
            SearchQuery(
                query_text=query.query_text,
                query_type="semantic",
                max_results=query.max_results * 2,
            )
        )

        faceted_task = (
            self._faceted_search(
                SearchQuery(
                    query_text=query.query_text,
                    query_type="faceted",
                    filters=query.filters,
                )
            )
            if query.filters
            else asyncio.create_task(self._empty_results())
        )

        # Wait for all searches to complete
        vector_results, semantic_results, faceted_results = await asyncio.gather(
            vector_task, semantic_task, faceted_task
        )

        # Fuse results using hybrid generator
        vector_tuples = [(r.chunk_id, r.relevance_score) for r in vector_results]
        semantic_tuples = [(r.chunk_id, r.relevance_score) for r in semantic_results]
        faceted_ids = [r.chunk_id for r in faceted_results]

        fused_scores = self.hybrid_generator.fuse_search_results(
            vector_tuples,
            semantic_tuples,
            faceted_ids,
            self._hybrid_index,
            query.max_results,
        )

        # Convert to SearchResult objects
        results = []
        for chunk_id, score in fused_scores[: query.max_results]:
            if score >= query.min_score:
                result = SearchResult(
                    chunk_id=chunk_id,
                    content=self._get_chunk_content(chunk_id),
                    relevance_score=score,
                    search_type="hybrid",
                    metadata=self._get_chunk_metadata(chunk_id),
                    explanation={
                        "vector_score": self._get_vector_score(
                            chunk_id, vector_results
                        ),
                        "semantic_score": self._get_semantic_score(
                            chunk_id, semantic_results
                        ),
                        "faceted_match": chunk_id
                        in [r.chunk_id for r in faceted_results],
                        "fusion_algorithm": self._hybrid_index.fusion_algorithm,
                    },
                )
                results.append(result)

        return results

    async def _semantic_search(self, query: SearchQuery) -> list[SearchResult]:
        """Execute semantic keyword search."""
        if not self._semantic_index:
            raise ValueError("Semantic index not available")

        # Process Japanese query
        processed_query = self.japanese_processor.process_query(query.query_text)

        # Search in semantic index using generator
        matches = self.semantic_generator.search_by_keywords(
            processed_query.normalized_text,
            self._semantic_index,
            max_results=query.max_results,
        )

        results = []
        for chunk_id, score in matches:
            if score >= query.min_score:
                result = SearchResult(
                    chunk_id=chunk_id,
                    content=self._get_chunk_content(chunk_id),
                    relevance_score=score,
                    search_type="semantic",
                    metadata=self._get_chunk_metadata(chunk_id),
                    highlighting=self._generate_highlighting(
                        chunk_id, processed_query.keywords
                    ),
                )
                results.append(result)

        return results

    async def _vector_search(self, query: SearchQuery) -> list[SearchResult]:
        """Execute vector similarity search."""
        if not self._vector_index:
            raise ValueError("Vector index not available")

        # Generate query embedding
        query_embedding = await self._generate_query_embedding(query.query_text)
        if query_embedding is None:
            logger.warning(
                "Failed to generate query embedding, falling back to semantic search"
            )
            return await self._semantic_search(query)

        # Search in vector index using generator
        similarities = self.vector_generator.search_similar_vectors(
            query_embedding, self._vector_index, k=query.max_results
        )

        results = []
        for chunk_id, score in similarities:
            if score >= query.min_score:
                result = SearchResult(
                    chunk_id=chunk_id,
                    content=self._get_chunk_content(chunk_id),
                    relevance_score=score,
                    search_type="vector",
                    metadata=self._get_chunk_metadata(chunk_id),
                )
                results.append(result)

        return results

    async def _faceted_search(self, query: SearchQuery) -> list[SearchResult]:
        """Execute faceted filtering search."""
        if not self._faceted_index:
            raise ValueError("Faceted index not available")

        # Apply filters using generator
        matches = self.faceted_generator.filter_by_facets(
            self._faceted_index, query.filters
        )

        results = []
        for chunk_id in matches[: query.max_results]:
            result = SearchResult(
                chunk_id=chunk_id,
                content=self._get_chunk_content(chunk_id),
                relevance_score=1.0,  # Binary match
                search_type="faceted",
                metadata=self._get_chunk_metadata(chunk_id),
            )
            results.append(result)

        return results

    async def _empty_results(self) -> list[SearchResult]:
        """Return empty results for conditional searches."""
        return []

    async def _generate_query_embedding(self, query_text: str) -> np.ndarray | None:
        """Generate embedding for query text."""
        try:
            # Create temporary semantic chunk for query
            query_chunk = SemanticChunk(
                chunk_id="query",
                chunk_type="query",
                content=query_text,
                metadata={},
                search_weight=1.0,
                embedding_hint="search_query",
            )

            # Process through vector processor
            result = await self.vector_processor.process_chunks([query_chunk])

            if result.vector_chunks:
                return result.vector_chunks[0].embedding
            else:
                return None

        except Exception as e:
            logger.error(f"Failed to generate query embedding: {e}")
            return None

    def _fuse_search_scores(
        self,
        vector_results: list[SearchResult],
        semantic_results: list[SearchResult],
        faceted_results: list[SearchResult],
        query: SearchQuery,
    ) -> list[tuple[str, float]]:
        """Fuse scores from different search modalities."""
        if not self._hybrid_index:
            return []

        # Convert results to score dictionaries
        vector_scores = {r.chunk_id: r.relevance_score for r in vector_results}
        semantic_scores = {r.chunk_id: r.relevance_score for r in semantic_results}
        faceted_ids = {r.chunk_id for r in faceted_results}

        # Get all unique chunk IDs
        all_chunk_ids = (
            set(vector_scores.keys()) | set(semantic_scores.keys()) | faceted_ids
        )

        # Apply fusion algorithm
        fused_scores = []
        for chunk_id in all_chunk_ids:
            vector_score = vector_scores.get(chunk_id, 0.0)
            semantic_score = semantic_scores.get(chunk_id, 0.0)
            faceted_match = 1.0 if chunk_id in faceted_ids else 0.0

            # Weighted combination
            fused_score = (
                vector_score * self._hybrid_index.vector_weight
                + semantic_score * self._hybrid_index.semantic_weight
                + faceted_match * self._hybrid_index.facet_weight
            )

            # Apply boost factors
            for boost_key, boost_value in query.boost_factors.items():
                if boost_key in self._get_chunk_metadata(chunk_id):
                    fused_score *= boost_value

            fused_scores.append((chunk_id, fused_score))

        # Sort by score descending
        fused_scores.sort(key=lambda x: x[1], reverse=True)

        return fused_scores

    def _post_process_results(
        self, results: list[SearchResult], query: SearchQuery
    ) -> list[SearchResult]:
        """Apply post-processing to search results."""
        # Remove duplicates
        seen_ids = set()
        unique_results = []
        for result in results:
            if result.chunk_id not in seen_ids:
                unique_results.append(result)
                seen_ids.add(result.chunk_id)

        # Apply minimum score filter
        filtered_results = [
            r for r in unique_results if r.relevance_score >= query.min_score
        ]

        # Limit results
        return filtered_results[: query.max_results]

    def _generate_cache_key(self, query: SearchQuery) -> str:
        """Generate cache key for query."""
        import hashlib

        query_str = f"{query.query_text}_{query.query_type}_{query.max_results}_{query.min_score}"
        return hashlib.md5(query_str.encode("utf-8")).hexdigest()

    def _get_chunk_content(self, chunk_id: str) -> str:
        """Get content for chunk ID."""
        # Implementation depends on index structure
        return f"Content for {chunk_id}"

    def _get_chunk_metadata(self, chunk_id: str) -> dict[str, Any]:
        """Get metadata for chunk ID."""
        # Implementation depends on index structure
        return {"chunk_id": chunk_id}

    def _get_vector_score(self, chunk_id: str, results: list[SearchResult]) -> float:
        """Get vector score for chunk ID."""
        for result in results:
            if result.chunk_id == chunk_id:
                return result.relevance_score
        return 0.0

    def _get_semantic_score(self, chunk_id: str, results: list[SearchResult]) -> float:
        """Get semantic score for chunk ID."""
        for result in results:
            if result.chunk_id == chunk_id:
                return result.relevance_score
        return 0.0

    def _generate_highlighting(
        self, chunk_id: str, keywords: list[str]
    ) -> dict[str, list[str]]:
        """Generate search term highlighting."""
        return {"content": keywords}

    def _get_default_search_config(self) -> dict[str, Any]:
        """Get default search configuration."""
        return {
            "semantic_search": {
                "japanese_optimization": True,
                "business_terms": True,
                "fuzzy_matching": True,
            },
            "hybrid_search": {
                "vector_weight": 0.6,
                "semantic_weight": 0.3,
                "facet_weight": 0.1,
                "fusion_algorithm": "weighted_sum",
            },
            "vector_search": {"similarity_threshold": 0.7, "max_distance": 2.0},
            "faceted_search": {
                "enable_range_queries": True,
                "enable_text_search": True,
            },
            "performance": {
                "cache_size": 1000,
                "parallel_searches": True,
                "index_optimization": True,
            },
        }

    def get_metrics(self) -> SearchEngineMetrics:
        """Get current search engine metrics."""
        return self.metrics

    def clear_cache(self) -> None:
        """Clear search result cache."""
        self._query_cache.clear()
        logger.info("Search cache cleared")

    def is_ready(self) -> bool:
        """Check if search engine is ready for queries."""
        return (
            self._semantic_index is not None
            and self._vector_index is not None
            and self._hybrid_index is not None
            and self._faceted_index is not None
        )

    def get_index_status(self) -> dict[str, bool]:
        """Get status of all search indices."""
        return {
            "semantic": self._semantic_index is not None,
            "vector": self._vector_index is not None,
            "hybrid": self._hybrid_index is not None,
            "faceted": self._faceted_index is not None,
        }
