"""OpenSearch format metadata exporter.

Specialized module for generating OpenSearch/Elasticsearch mapping definitions
with Japanese language analysis support and optimized field mappings.
"""

from __future__ import annotations

from typing import Any

from ..advanced_metadata import AdvancedMetadata
from .base import BaseMetadataExporter


class OpenSearchExporter(BaseMetadataExporter):
    """OpenSearch format metadata exporter.
    
    Generates OpenSearch index configuration with Japanese analysis support
    and optimized field mappings for RAG-enhanced search functionality.
    """

    def __init__(self):
        """Initialize OpenSearch exporter."""
        super().__init__()

    def export(self, metadata: AdvancedMetadata) -> dict[str, Any]:
        """Generate OpenSearch mapping definitions.

        Args:
            metadata: Advanced metadata to generate mappings from.

        Returns:
            OpenSearch index configuration with Japanese analysis support.
        """
        mapping = {
            "settings": self._create_index_settings(),
            "mappings": {"properties": self._create_property_mappings(metadata)},
        }

        return mapping

    def _create_index_settings(self) -> dict[str, Any]:
        """Create OpenSearch index settings with Japanese analysis.

        Returns:
            Index settings with analyzers and tokenizers.
        """
        return {
            "index": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "analysis": {
                    "analyzer": {
                        "japanese_analyzer": {
                            "type": "custom",
                            "tokenizer": "kuromoji_tokenizer",
                            "filter": [
                                "kuromoji_baseform",
                                "kuromoji_part_of_speech",
                                "ja_stop",
                                "kuromoji_stemmer",
                                "lowercase",
                            ],
                        },
                        "business_analyzer": {
                            "type": "custom",
                            "tokenizer": "keyword",
                            "filter": ["lowercase", "trim"],
                        },
                    },
                    "tokenizer": {
                        "kuromoji_tokenizer": {
                            "type": "kuromoji_tokenizer",
                            "mode": "search",
                            "discard_punctuation": False,
                        }
                    },
                    "filter": {
                        "ja_stop": {
                            "type": "stop",
                            "stopwords": ["の", "に", "は", "を", "が", "で", "と"],
                        }
                    },
                },
            }
        }

    def _create_property_mappings(self, metadata: AdvancedMetadata) -> dict[str, Any]:
        """Create property mappings for all detected fields.

        Args:
            metadata: Advanced metadata containing field information.

        Returns:
            Dictionary of field mappings for OpenSearch.
        """
        properties = {}

        # 統計分析フィールドのマッピング
        statistical_analysis = metadata.statistical_analysis

        # 数値フィールド
        for field_name, stats in statistical_analysis.get("numerical_fields", {}).items():
            properties[field_name] = self._create_numerical_mapping(field_name, stats)

        # カテゴリフィールド
        for field_name, stats in statistical_analysis.get("categorical_fields", {}).items():
            properties[field_name] = self._create_categorical_mapping(field_name, stats)

        # エンティティフィールド
        properties.update(self._create_entity_mappings(metadata.entity_classification))

        # PLaMo特徴量フィールド
        properties["plamo_features"] = self._create_plamo_features_mapping()

        # データ品質メトリクス
        properties["data_quality"] = self._create_data_quality_mapping()

        # メタデータフィールド
        properties.update(self._create_metadata_mappings())

        return properties

    def _create_numerical_mapping(self, field_name: str, stats: dict) -> dict[str, Any]:
        """Create mapping for numerical fields.

        Args:
            field_name: Name of the numerical field.
            stats: Statistical information for the field.

        Returns:
            OpenSearch mapping for the numerical field.
        """
        mapping = {
            "type": "float",
            "fields": {
                "keyword": {"type": "keyword"},
            },
        }

        # 整数フィールドの検出
        if stats.get("distribution_type") == "integer":
            mapping["type"] = "integer"

        # 範囲フィールドの追加
        range_type = "integer_range" if mapping["type"] == "integer" else "float_range"
        mapping["fields"]["range"] = {"type": range_type}

        # 通貨フィールドの特別処理
        if any(keyword in field_name.lower() for keyword in ["price", "salary", "cost", "金額", "給与"]):
            mapping["meta"] = {"unit": "円", "format": "currency"}

        return mapping

    def _create_categorical_mapping(self, field_name: str, stats: dict) -> dict[str, Any]:
        """Create mapping for categorical fields.

        Args:
            field_name: Name of the categorical field.
            stats: Statistical information for the field.

        Returns:
            OpenSearch mapping for the categorical field.
        """
        # 日本語テキストの検出
        sample_values = list(stats.get("value_counts", {}).keys())[:5]
        has_japanese = any(self._contains_japanese(str(value)) for value in sample_values)

        mapping = {
            "type": "text",
            "analyzer": "japanese_analyzer" if has_japanese else "standard",
            "fields": {
                "keyword": {"type": "keyword", "ignore_above": 256},
                "raw": {"type": "keyword", "index": False},
            },
        }

        # ビジネス用語フィールドの特別処理
        if any(keyword in field_name.lower() for keyword in ["company", "organization", "dept", "会社", "部署"]):
            mapping["analyzer"] = "business_analyzer"
            mapping["fields"]["suggest"] = {
                "type": "completion",
                "analyzer": "business_analyzer",
            }

        return mapping

    def _create_entity_mappings(self, entity_classification) -> dict[str, Any]:
        """Create mappings for entity fields.

        Args:
            entity_classification: Entity classification data.

        Returns:
            Dictionary of entity field mappings.
        """
        mappings = {}

        if entity_classification.persons:
            mappings["detected_persons"] = {
                "type": "nested",
                "properties": {
                    "name": {"type": "text", "analyzer": "japanese_analyzer"},
                    "confidence": {"type": "float"},
                    "name_type": {"type": "keyword"},
                },
            }

        if entity_classification.places:
            mappings["detected_places"] = {
                "type": "nested", 
                "properties": {
                    "place": {"type": "text", "analyzer": "japanese_analyzer"},
                    "confidence": {"type": "float"},
                    "place_type": {"type": "keyword"},
                },
            }

        if entity_classification.organizations:
            mappings["detected_organizations"] = {
                "type": "nested",
                "properties": {
                    "organization": {"type": "text", "analyzer": "business_analyzer"},
                    "confidence": {"type": "float"},
                    "org_type": {"type": "keyword"},
                },
            }

        if entity_classification.business_terms:
            mappings["detected_business_terms"] = {
                "type": "nested",
                "properties": {
                    "term": {"type": "text", "analyzer": "business_analyzer"},
                    "confidence": {"type": "float"},
                    "category": {"type": "keyword"},
                },
            }

        return mappings

    def _create_plamo_features_mapping(self) -> dict[str, Any]:
        """Create mapping for PLaMo features.

        Returns:
            OpenSearch mapping for PLaMo features object.
        """
        return {
            "type": "object",
            "properties": {
                "kanji_density": {"type": "float"},
                "katakana_terms": {"type": "keyword"},
                "domain": {"type": "keyword"},
                "formality_level": {"type": "keyword"},
                "technical_level": {"type": "keyword"},
                "text_segments_count": {"type": "integer"},
                "japanese_features": {
                    "type": "object",
                    "properties": {
                        "kanji_ratio": {"type": "float"},
                        "hiragana_ratio": {"type": "float"},
                        "katakana_ratio": {"type": "float"},
                    },
                },
                "embedding_hints": {
                    "type": "object",
                    "properties": {
                        "domain": {"type": "keyword"},
                        "formality_level": {"type": "keyword"},
                        "technical_level": {"type": "keyword"},
                    },
                },
            },
        }

    def _create_data_quality_mapping(self) -> dict[str, Any]:
        """Create mapping for data quality metrics.

        Returns:
            OpenSearch mapping for data quality object.
        """
        return {
            "type": "object",
            "properties": {
                "completeness_score": {"type": "float"},
                "consistency_score": {"type": "float"},
                "validity_score": {"type": "float"},
                "accuracy_score": {"type": "float"},
                "overall_score": {"type": "float"},
                "assessment_date": {"type": "date"},
            },
        }

    def _create_metadata_mappings(self) -> dict[str, Any]:
        """Create mappings for metadata fields.

        Returns:
            Dictionary of metadata field mappings.
        """
        return {
            "dataset_name": {
                "type": "text",
                "analyzer": "japanese_analyzer",
                "fields": {"keyword": {"type": "keyword"}},
            },
            "source_info": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "keyword"},
                    "creation_date": {"type": "date"},
                    "size": {"type": "long"},
                },
            },
            "generation_metadata": {
                "type": "object",
                "properties": {
                    "rag_version": {"type": "keyword"},
                    "generation_date": {"type": "date"},
                    "processing_time": {"type": "float"},
                },
            },
            # 検索用の統合フィールド
            "_all_text": {
                "type": "text",
                "analyzer": "japanese_analyzer",
                "store": False,
                "index": True,
            },
            # 検索ブーストのためのスコアフィールド
            "_search_boost": {"type": "float", "index": False},
        }
