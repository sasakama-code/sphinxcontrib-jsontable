"""Search Facet Generator for Phase 2 RAG Integration.

Modular search facet generation capabilities with complete backward compatibility.
Provides the same API as the original monolithic SearchFacetGenerator while
internally using specialized modules for improved maintainability.

Features:
- Categorical facet automatic generation
- Numerical range facet optimization
- Temporal facet support
- Japanese entity facets
- UI integration metadata generation
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from ..advanced_metadata import AdvancedMetadata, EntityClassification

# Import all components from modular structure
from .base import FacetConfig, GeneratedFacets
from .categorical import CategoricalFacet, CategoricalFacetGenerator
from .entity import EntityFacet, EntityFacetGenerator
from .numerical import NumericalFacet, NumericalFacetGenerator
from .temporal import TemporalFacet, TemporalFacetGenerator
from .ui_configs import UIConfigGenerator

# Public API exports for backward compatibility
__all__ = [
    # Data classes
    "CategoricalFacet",
    "EntityFacet",
    # Configuration
    "FacetConfig",
    "GeneratedFacets",
    "NumericalFacet",
    # Main generator
    "SearchFacetGenerator",
    "TemporalFacet",
]


class SearchFacetGenerator:
    """Automatic search facet generator for advanced metadata.

    Generates various types of search facets from statistical analysis and
    entity classification data, optimized for Japanese content and business data.

    This is a facade that internally coordinates specialized generators for
    improved maintainability while preserving the original API.
    """

    def __init__(self, config: FacetConfig | None = None):
        """Initialize search facet generator.

        Args:
            config: Optional facet generation configuration.
        """
        self.config = config or FacetConfig()

        # Initialize specialized generators
        self.categorical_generator = CategoricalFacetGenerator(self.config)
        self.numerical_generator = NumericalFacetGenerator(self.config)
        self.temporal_generator = TemporalFacetGenerator(self.config)
        self.entity_generator = EntityFacetGenerator(self.config)
        self.ui_generator = UIConfigGenerator()

    def generate_facets(self, advanced_metadata: AdvancedMetadata) -> GeneratedFacets:
        """Generate search facets from advanced metadata analysis.

        Args:
            advanced_metadata: Advanced metadata containing statistical analysis and entity data.

        Returns:
            GeneratedFacets containing all types of search facets.
        """
        facets = GeneratedFacets()

        # カテゴリカルファセット生成
        facets.categorical_facets = (
            self.categorical_generator.generate_categorical_facets(
                advanced_metadata.statistical_analysis
            )
        )

        # 数値ファセット生成
        facets.numerical_facets = self.numerical_generator.generate_numerical_facets(
            advanced_metadata.statistical_analysis
        )

        # 時系列ファセット生成
        facets.temporal_facets = self.temporal_generator.generate_temporal_facets(
            advanced_metadata.statistical_analysis
        )

        # エンティティファセット生成
        if self.config.enable_entity_facets:
            facets.entity_facets = self.entity_generator.generate_entity_facets(
                advanced_metadata.entity_classification
            )

        # 生成メタデータ
        facets.generation_metadata = self.ui_generator.create_generation_metadata(
            facets
        )

        return facets

    def generate_search_interface_config(
        self, facets: GeneratedFacets
    ) -> dict[str, Any]:
        """Generate complete search interface configuration.

        Args:
            facets: Generated facets for UI configuration.

        Returns:
            Comprehensive UI configuration for search interface implementation.
        """
        return self.ui_generator.generate_search_interface_config(facets)

    # Legacy method aliases for backward compatibility
    def _generate_categorical_facets(
        self, statistical_analysis: dict
    ) -> list[CategoricalFacet]:
        """Legacy method for categorical facet generation."""
        return self.categorical_generator.generate_categorical_facets(
            statistical_analysis
        )

    def _generate_numerical_facets(
        self, statistical_analysis: dict
    ) -> list[NumericalFacet]:
        """Legacy method for numerical facet generation."""
        return self.numerical_generator.generate_numerical_facets(statistical_analysis)

    def _generate_temporal_facets(
        self, statistical_analysis: dict
    ) -> list[TemporalFacet]:
        """Legacy method for temporal facet generation."""
        return self.temporal_generator.generate_temporal_facets(statistical_analysis)

    def _generate_entity_facets(
        self, entity_classification: EntityClassification
    ) -> list[EntityFacet]:
        """Legacy method for entity facet generation."""
        return self.entity_generator.generate_entity_facets(entity_classification)

    def _create_generation_metadata(self, facets: GeneratedFacets) -> dict[str, Any]:
        """Legacy method for generation metadata creation."""
        return self.ui_generator.create_generation_metadata(facets)
