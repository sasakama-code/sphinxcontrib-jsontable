"""Metadata Exporter for Phase 2 RAG Integration.

Modular metadata export functionality with complete backward compatibility.
Provides the same API as the original monolithic MetadataExporter while
internally using specialized exporters for improved maintainability.

Features:
- JSON-LD format output
- OpenSearch/Elasticsearch mapping generation  
- PLaMo-Embedding-1B specialized format
- Search engine index configuration
- Custom format support
"""

from __future__ import annotations

from typing import Any

from ..advanced_metadata import AdvancedMetadata
from ..search_facets import GeneratedFacets

# Import all specialized exporters
from .base import BaseMetadataExporter
from .custom import CustomExporter
from .elasticsearch import ElasticsearchExporter
from .facet_config import FacetConfigExporter
from .json_ld import JsonLdExporter
from .opensearch import OpenSearchExporter
from .plamo_ready import PlamoReadyExporter
from .search_config import SearchConfigExporter

# Public API exports for backward compatibility
__all__ = [
    "MetadataExporter",
    "BaseMetadataExporter",
    "JsonLdExporter",
    "OpenSearchExporter", 
    "ElasticsearchExporter",
    "PlamoReadyExporter",
    "SearchConfigExporter",
    "FacetConfigExporter",
    "CustomExporter",
]


class MetadataExporter:
    """Multi-format metadata export processor.

    Provides comprehensive metadata export capabilities for various search engines
    and embedding systems with Japanese language optimization.
    
    This is a facade that internally coordinates specialized exporters for
    improved maintainability while preserving the original API.
    """

    def __init__(self):
        """Initialize metadata exporter with supported format configurations."""
        self.supported_formats = [
            "json-ld",
            "opensearch",
            "elasticsearch",
            "plamo-ready",
            "search-config",
            "facet-config",
            "custom",
        ]
        
        # Initialize specialized exporters
        self.json_ld_exporter = JsonLdExporter()
        self.opensearch_exporter = OpenSearchExporter()
        self.elasticsearch_exporter = ElasticsearchExporter()
        self.plamo_ready_exporter = PlamoReadyExporter()
        self.search_config_exporter = SearchConfigExporter()
        self.facet_config_exporter = FacetConfigExporter()
        self.custom_exporter = CustomExporter()

    def export_metadata(
        self,
        advanced_metadata: AdvancedMetadata,
        generated_facets: GeneratedFacets,
        formats: list[str],
        custom_config: dict | None = None,
    ) -> dict[str, Any]:
        """Export metadata in specified formats.

        Args:
            advanced_metadata: Advanced metadata from Phase 2 analysis.
            generated_facets: Search facets generated for the dataset.
            formats: List of export formats to generate.
            custom_config: Optional custom configuration for export.

        Returns:
            Dictionary containing exported metadata in requested formats.
        """
        exports = {}

        for format_type in formats:
            if format_type not in self.supported_formats:
                continue

            try:
                if format_type == "json-ld":
                    exports["json-ld"] = self.json_ld_exporter.export(advanced_metadata)
                elif format_type == "opensearch":
                    exports["opensearch"] = self.opensearch_exporter.export(advanced_metadata)
                elif format_type == "elasticsearch":
                    exports["elasticsearch"] = self.elasticsearch_exporter.export(advanced_metadata)
                elif format_type == "plamo-ready":
                    exports["plamo-ready"] = self.plamo_ready_exporter.export(advanced_metadata)
                elif format_type == "search-config":
                    exports["search-config"] = self.search_config_exporter.export(
                        advanced_metadata, generated_facets
                    )
                elif format_type == "facet-config":
                    exports["facet-config"] = self.facet_config_exporter.export(generated_facets)
                elif format_type == "custom":
                    exports["custom"] = self.custom_exporter.export(
                        advanced_metadata, custom_config or {}
                    )
            except Exception as e:
                exports[f"{format_type}_error"] = {"error": str(e)}

        return exports

    # Legacy method aliases for backward compatibility
    def _export_json_ld(self, metadata: AdvancedMetadata) -> dict:
        """Legacy method for JSON-LD export."""
        return self.json_ld_exporter.export(metadata)

    def _export_opensearch(self, metadata: AdvancedMetadata) -> dict:
        """Legacy method for OpenSearch export."""
        return self.opensearch_exporter.export(metadata)

    def _export_elasticsearch(self, metadata: AdvancedMetadata) -> dict:
        """Legacy method for Elasticsearch export."""
        return self.elasticsearch_exporter.export(metadata)

    def _export_plamo_ready(self, metadata: AdvancedMetadata) -> dict:
        """Legacy method for PLaMo-ready export."""
        return self.plamo_ready_exporter.export(metadata)

    def _export_search_config(self, metadata: AdvancedMetadata, facets: GeneratedFacets) -> dict:
        """Legacy method for search config export."""
        return self.search_config_exporter.export(metadata, facets)

    def _export_facet_config(self, facets: GeneratedFacets) -> dict:
        """Legacy method for facet config export."""
        return self.facet_config_exporter.export(facets)

    def _export_custom(self, metadata: AdvancedMetadata, config: dict) -> dict:
        """Legacy method for custom export."""
        return self.custom_exporter.export(metadata, config)
