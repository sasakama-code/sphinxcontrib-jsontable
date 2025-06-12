"""Legacy search index generator - backwards compatibility layer.

This file provides complete backward compatibility for the original
search_index_generator.py API while redirecting to the new modular architecture.

All existing functionality is preserved while leveraging the improved
modular design under the hood.
"""

import logging
import warnings
from typing import Any

from .search_index_generators import (
    ComprehensiveSearchIndex,
    FacetedSearchIndex,
    JapaneseQueryProcessor,
)

# Import the new modular implementation
from .search_index_generators import (
    SearchIndexGenerator as ModularSearchIndexGenerator,
)

# Import additional index types from base module
from .search_index_generators.base import (
    HybridSearchIndex,
    SemanticSearchIndex,
    VectorIndex,
)

logger = logging.getLogger(__name__)

# Legacy imports for backward compatibility
__all__ = [
    "ComprehensiveSearchIndex",
    "FacetedSearchIndex",
    "HybridSearchIndex",
    "JapaneseQueryProcessor",
    "SearchIndexGenerator",
    "SemanticSearchIndex",
    "VectorIndex",
]


class SearchIndexGenerator:
    """Legacy SearchIndexGenerator with complete backward compatibility.

    This class provides a compatibility layer that redirects all calls to
    the new modular architecture while maintaining the exact same API.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize search index generator with configuration.

        Args:
            config: Optional configuration dictionary for index parameters.
        """
        # Issue a deprecation notice for developers
        warnings.warn(
            "Using the legacy search_index_generator module. "
            "Consider migrating to the new modular architecture in "
            "search_index_generators/ for better performance and maintainability.",
            DeprecationWarning,
            stacklevel=2,
        )

        # Delegate to the new modular implementation
        self._generator = ModularSearchIndexGenerator(config)

        # Expose internal components for backward compatibility
        self.config = self._generator.config
        self.japanese_processor = self._generator.japanese_processor
        self.index_strategies = self._generator.index_strategies

    def _get_default_config(self) -> dict[str, Any]:
        """Get default configuration - legacy method."""
        return self._generator._get_default_config()

    def _setup_vector_strategy(self) -> dict[str, Any]:
        """Setup vector strategy - legacy method."""
        return self._generator._setup_vector_strategy()

    def _setup_semantic_strategy(self) -> dict[str, Any]:
        """Setup semantic strategy - legacy method."""
        return self._generator._setup_semantic_strategy()

    def _setup_faceted_strategy(self) -> dict[str, Any]:
        """Setup faceted strategy - legacy method."""
        return self._generator._setup_faceted_strategy()

    def _setup_hybrid_strategy(self) -> dict[str, Any]:
        """Setup hybrid strategy - legacy method."""
        return self._generator._setup_hybrid_strategy()

    def generate_comprehensive_index(
        self,
        vector_chunks: list,
        basic_metadata: Any = None,
    ) -> ComprehensiveSearchIndex:
        """Generate comprehensive search index - legacy API."""
        return self._generator.generate_comprehensive_index(
            vector_chunks, basic_metadata
        )

    def search_similar_vectors(
        self,
        query_embedding,
        search_index: ComprehensiveSearchIndex,
        k: int = 10,
    ) -> list[tuple[int, float]]:
        """Vector similarity search - legacy API."""
        return self._generator.search_similar_vectors(query_embedding, search_index, k)

    def save_search_index(
        self, search_index: ComprehensiveSearchIndex, output_path: str
    ) -> None:
        """Save search index - legacy API."""
        self._generator.save_search_index(search_index, output_path)

    @classmethod
    def load_search_index(cls, input_path: str) -> ComprehensiveSearchIndex:
        """Load search index - legacy API."""
        return ModularSearchIndexGenerator.load_search_index(input_path)

    # Additional legacy methods that may have been used
    def _build_vector_index(self, vector_chunks: list):
        """Legacy method - redirected to modular implementation."""
        return self._generator.vector_generator.generate(vector_chunks)

    def _build_semantic_index(self, vector_chunks: list):
        """Legacy method - redirected to modular implementation."""
        return self._generator.semantic_generator.generate(vector_chunks)

    def _build_facet_index(self, vector_chunks: list, basic_metadata=None):
        """Legacy method - redirected to modular implementation."""
        return self._generator.faceted_generator.generate(vector_chunks, basic_metadata)

    def _build_hybrid_index(self):
        """Legacy method - redirected to modular implementation."""
        return self._generator.hybrid_generator.generate()


# Log the compatibility layer usage
logger.info("Using legacy search_index_generator compatibility layer")
