"""Elasticsearch format metadata exporter.

Specialized module for generating Elasticsearch mapping definitions with vector search support
and optimized configurations for Elasticsearch-specific features.
"""

from __future__ import annotations

from typing import Any

from ..advanced_metadata import AdvancedMetadata
from .opensearch import OpenSearchExporter


class ElasticsearchExporter(OpenSearchExporter):
    """Elasticsearch format metadata exporter.

    Extends OpenSearch exporter with Elasticsearch-specific features
    including dense vector support and Elasticsearch-optimized analyzers.
    """

    def __init__(self):
        """Initialize Elasticsearch exporter."""
        super().__init__()

    def export(self, metadata: AdvancedMetadata) -> dict[str, Any]:
        """Generate Elasticsearch mapping definitions.

        Args:
            metadata: Advanced metadata to generate mappings from.

        Returns:
            Elasticsearch index configuration with vector search support.
        """
        # OpenSearchとほぼ同じだが、Elasticsearch特有の調整を適用
        opensearch_mapping = super().export(metadata)

        # Elasticsearch特有の調整
        elasticsearch_mapping = self._adapt_for_elasticsearch(opensearch_mapping)

        return elasticsearch_mapping

    def _adapt_for_elasticsearch(self, mapping: dict[str, Any]) -> dict[str, Any]:
        """Adapt OpenSearch mapping for Elasticsearch compatibility.

        Args:
            mapping: OpenSearch mapping to adapt.

        Returns:
            Elasticsearch-compatible mapping.
        """
        # Elasticsearchのanalyzer名調整
        if "settings" in mapping and "index" in mapping["settings"]:
            settings = (
                mapping["settings"]["index"].get("analysis", {}).get("analyzer", {})
            )
            if "japanese_analyzer" in settings:
                settings["japanese_analyzer"]["tokenizer"] = "kuromoji_tokenizer"

        # ベクトル検索フィールド（Elasticsearch 8.0以降）
        if "mappings" in mapping and "properties" in mapping["mappings"]:
            properties = mapping["mappings"]["properties"]
            properties["embedding_vector"] = {
                "type": "dense_vector",
                "dims": 1024,  # PLaMo-Embedding-1Bの次元数
                "index": True,
                "similarity": "cosine",
            }

        return mapping
