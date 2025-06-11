"""Search configuration exporter.

Specialized module for exporting search engine configuration with facets,
boost settings, and Japanese language optimization.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from ..advanced_metadata import AdvancedMetadata
from ..search_facets import GeneratedFacets
from .base import BaseMetadataExporter


class SearchConfigExporter(BaseMetadataExporter):
    """Search configuration exporter.
    
    Exports comprehensive search engine configuration including facets,
    boost settings, aggregations, and Japanese language support.
    """

    def __init__(self):
        """Initialize search config exporter."""
        super().__init__()

    def export(self, metadata: AdvancedMetadata, facets: GeneratedFacets) -> dict[str, Any]:
        """Export search engine configuration.

        Args:
            metadata: Advanced metadata for search optimization.
            facets: Generated facets for search interface.

        Returns:
            Search engine configuration with facets and boost settings.
        """
        return {
            "search_settings": self._create_search_settings(metadata),
            "facet_settings": self._create_facet_settings(facets),
            "aggregation_config": self._create_aggregation_config(facets),
            "suggestion_config": self._create_suggestion_config(metadata),
            "boost_config": self._create_boost_config(metadata),
            "highlight_config": self._create_highlight_config(metadata),
        }

    def _create_search_settings(self, metadata: AdvancedMetadata) -> dict[str, Any]:
        """Create basic search settings."""
        return {
            "default_operator": "AND",
            "minimum_should_match": "75%",
            "japanese_analysis": True,
            "fuzzy_matching": True,
            "phrase_matching": True,
        }

    def _create_facet_settings(self, facets: GeneratedFacets) -> dict[str, Any]:
        """Create facet settings from generated facets."""
        return {
            "categorical_facets": [asdict(f) for f in facets.categorical_facets],
            "numerical_facets": [asdict(f) for f in facets.numerical_facets],
            "temporal_facets": [asdict(f) for f in facets.temporal_facets],
            "entity_facets": [asdict(f) for f in facets.entity_facets],
        }

    def _create_aggregation_config(self, facets: GeneratedFacets) -> dict[str, Any]:
        """Create aggregation configuration."""
        aggregations = {}

        for facet in facets.categorical_facets:
            aggregations[f"{facet.field_name}_terms"] = {
                "terms": {"field": f"{facet.field_name}.keyword", "size": 20}
            }

        for facet in facets.numerical_facets:
            aggregations[f"{facet.field_name}_stats"] = {
                "stats": {"field": facet.field_name}
            }

        return aggregations

    def _create_suggestion_config(self, metadata: AdvancedMetadata) -> dict[str, Any]:
        """Create suggestion configuration."""
        return {
            "enable_autocomplete": True,
            "suggestion_fields": self._get_suggestion_fields(metadata),
            "fuzzy_matching": True,
            "japanese_reading_support": True,
        }

    def _create_boost_config(self, metadata: AdvancedMetadata) -> dict[str, Any]:
        """Create boost configuration."""
        boost_config = {}

        if metadata.entity_classification.persons:
            boost_config["detected_persons.name"] = 2.0
        if metadata.entity_classification.organizations:
            boost_config["detected_organizations.organization"] = 1.5

        return boost_config

    def _create_highlight_config(self, metadata: AdvancedMetadata) -> dict[str, Any]:
        """Create highlight configuration."""
        return {
            "fields": self._get_highlightable_fields(metadata),
            "pre_tags": ["<mark>"],
            "post_tags": ["</mark>"],
        }
