"""JSON-LD format metadata exporter.

Specialized module for exporting metadata in JSON-LD format with schema.org compliance
and support for custom RAG vocabulary extensions.
"""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from typing import Any

from ..advanced_metadata import AdvancedMetadata
from .base import BaseMetadataExporter


class JsonLdExporter(BaseMetadataExporter):
    """JSON-LD format metadata exporter.

    Exports metadata in JSON-LD format with schema.org compliance
    and custom RAG vocabulary for enhanced semantic interoperability.
    """

    def __init__(self):
        """Initialize JSON-LD exporter."""
        super().__init__()

    def export(self, metadata: AdvancedMetadata) -> dict[str, Any]:
        """Export metadata in JSON-LD format.

        Args:
            metadata: Advanced metadata to export.

        Returns:
            JSON-LD structured data with schema.org compliance.
        """
        # JSON-LD コンテキスト定義
        context = self._create_context()

        # メインデータ構造
        json_ld = {
            "@context": context,
            "@type": "Dataset",
            "@id": f"rag:dataset-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "name": self._extract_dataset_name(metadata),
            "description": self._generate_dataset_description(metadata),
            "dateCreated": datetime.now().isoformat(),
            "creator": self._create_creator_info(metadata),
            # RAG特有のメタデータ
            "rag:statisticalAnalysis": self._format_statistical_analysis_for_jsonld(
                metadata.statistical_analysis
            ),
            "rag:entityClassification": self._format_entity_classification_for_jsonld(
                metadata.entity_classification
            ),
            "rag:dataQuality": self._format_data_quality_for_jsonld(
                metadata.data_quality
            ),
            "rag:plamoFeatures": self._format_plamo_features_for_jsonld(
                metadata.plamo_features
            ),
            # データセット詳細
            "distribution": self._create_distribution_info(metadata),
            "keywords": self._extract_keywords(metadata),
            "variableMeasured": self._extract_variables(metadata),
        }

        return json_ld

    def _create_context(self) -> dict[str, Any]:
        """Create JSON-LD context definition.

        Returns:
            JSON-LD context with schema.org and custom vocabularies.
        """
        return {
            "@vocab": "http://schema.org/",
            "rag": "http://example.com/rag-schema/",
            "jsontable": "http://example.com/jsontable-schema/",
            # データ型定義
            "statisticalAnalysis": {"@type": "rag:StatisticalAnalysis"},
            "entityClassification": {"@type": "rag:EntityClassification"},
            "dataQuality": {"@type": "rag:DataQualityReport"},
            "searchFacets": {"@type": "rag:SearchFacets"},
            "plamoFeatures": {"@type": "rag:PLaMoFeatures"},
        }

    def _create_creator_info(self, metadata: AdvancedMetadata) -> dict[str, Any]:
        """Create creator information for JSON-LD.

        Args:
            metadata: Advanced metadata containing version info.

        Returns:
            Creator information dictionary.
        """
        return {
            "@type": "SoftwareApplication",
            "name": "sphinxcontrib-jsontable-rag",
            "version": metadata.basic_metadata.get("rag_version", "1.0.0"),
            "applicationCategory": "DocumentationTool",
            "operatingSystem": "Cross-platform",
        }

    def _create_distribution_info(self, metadata: AdvancedMetadata) -> dict[str, Any]:
        """Create distribution information for JSON-LD.

        Args:
            metadata: Advanced metadata to analyze.

        Returns:
            Distribution information dictionary.
        """
        return {
            "@type": "DataDownload",
            "encodingFormat": "application/json",
            "contentSize": self._estimate_content_size(metadata),
            "dateModified": datetime.now().isoformat(),
        }

    def _generate_dataset_description(self, metadata: AdvancedMetadata) -> str:
        """Generate dataset description in Japanese.

        Args:
            metadata: Advanced metadata to describe.

        Returns:
            Human-readable dataset description.
        """
        stats = metadata.statistical_analysis
        entity_count = (
            len(metadata.entity_classification.persons)
            + len(metadata.entity_classification.places)
            + len(metadata.entity_classification.organizations)
            + len(metadata.entity_classification.business_terms)
        )

        numerical_fields = len(stats.get("numerical_fields", {}))
        categorical_fields = len(stats.get("categorical_fields", {}))

        description = "JSONテーブルデータセット。"
        description += f"数値フィールド{numerical_fields}個、"
        description += f"カテゴリフィールド{categorical_fields}個を含む。"

        if entity_count > 0:
            description += f"日本語エンティティ{entity_count}個を検出。"

        quality_score = metadata.data_quality.overall_score
        description += f"データ品質スコア: {quality_score:.2f}"

        return description

    def _format_statistical_analysis_for_jsonld(self, analysis: dict) -> dict:
        """Format statistical analysis for JSON-LD structure.

        Args:
            analysis: Statistical analysis data.

        Returns:
            JSON-LD formatted statistical analysis.
        """
        formatted: dict[str, Any] = {"@type": "rag:StatisticalAnalysis"}

        if "numerical_fields" in analysis:
            formatted["numericalFields"] = {}
            for field, stats in analysis["numerical_fields"].items():
                formatted["numericalFields"][field] = {
                    "@type": "rag:NumericalStats",
                    "mean": stats.get("mean"),
                    "median": stats.get("median"),
                    "standardDeviation": stats.get("std_dev"),
                    "range": {
                        "min": stats.get("min_value"),
                        "max": stats.get("max_value"),
                    },
                    "distributionType": stats.get("distribution_type"),
                }

        if "categorical_fields" in analysis:
            formatted["categoricalFields"] = {}
            for field, stats in analysis["categorical_fields"].items():
                formatted["categoricalFields"][field] = {
                    "@type": "rag:CategoricalStats",
                    "uniqueCount": stats.get("unique_count"),
                    "entropy": stats.get("entropy"),
                    "diversityIndex": stats.get("diversity_index"),
                }

        return formatted

    def _format_entity_classification_for_jsonld(self, entities) -> dict:
        """Format entity classification for JSON-LD structure.

        Args:
            entities: Entity classification data.

        Returns:
            JSON-LD formatted entity classification.
        """
        return {
            "@type": "rag:EntityClassification",
            "persons": [
                {
                    "@type": "rag:PersonEntity",
                    "name": p.name,
                    "confidence": p.confidence,
                    "nameType": p.name_type,
                }
                for p in entities.persons
            ],
            "places": [
                {
                    "@type": "rag:PlaceEntity",
                    "place": p.place,
                    "confidence": p.confidence,
                    "placeType": p.place_type,
                }
                for p in entities.places
            ],
            "organizations": [
                {
                    "@type": "rag:OrganizationEntity",
                    "organization": o.organization,
                    "confidence": o.confidence,
                    "organizationType": o.org_type,
                }
                for o in entities.organizations
            ],
            "businessTerms": [
                {
                    "@type": "rag:BusinessTermEntity",
                    "term": b.term,
                    "confidence": b.confidence,
                    "category": b.category,
                }
                for b in entities.business_terms
            ],
        }

    def _format_data_quality_for_jsonld(self, quality) -> dict:
        """Format data quality for JSON-LD structure.

        Args:
            quality: Data quality metrics.

        Returns:
            JSON-LD formatted data quality report.
        """
        return {
            "@type": "rag:DataQualityReport",
            "completenessScore": quality.completeness_score,
            "consistencyScore": quality.consistency_score,
            "validityScore": quality.validity_score,
            "accuracyScore": quality.accuracy_score,
            "overallScore": quality.overall_score,
            "assessmentDate": datetime.now().isoformat(),
        }

    def _format_plamo_features_for_jsonld(self, features) -> dict:
        """Format PLaMo features for JSON-LD structure.

        Args:
            features: PLaMo-specific features.

        Returns:
            JSON-LD formatted PLaMo features.
        """
        return {
            "@type": "rag:PLaMoFeatures",
            "japaneseFeatures": features.japanese_features,
            "embeddingHints": features.embedding_hints,
            "vectorOptimization": features.vector_optimization,
            "textSegments": len(features.text_segments),
            "optimizationLevel": features.embedding_hints.get(
                "technical_level", "standard"
            ),
        }

    def _extract_variables(self, metadata: AdvancedMetadata) -> list[dict]:
        """Extract variables in PropertyValue format for JSON-LD.

        Args:
            metadata: Advanced metadata to analyze.

        Returns:
            List of PropertyValue objects describing dataset variables.
        """
        variables = []

        # 数値変数
        for field_name, stats in metadata.statistical_analysis.get(
            "numerical_fields", {}
        ).items():
            variables.append(
                {
                    "@type": "PropertyValue",
                    "name": field_name,
                    "description": f"数値フィールド: {field_name}",
                    "minValue": stats.get("min_value"),
                    "maxValue": stats.get("max_value"),
                    "unitText": self._guess_unit(field_name),
                    "measurementTechnique": "StatisticalAnalysis",
                }
            )

        # カテゴリ変数
        for field_name, stats in metadata.statistical_analysis.get(
            "categorical_fields", {}
        ).items():
            variables.append(
                {
                    "@type": "PropertyValue",
                    "name": field_name,
                    "description": f"カテゴリフィールド: {field_name}",
                    "valueReference": list(stats.get("value_counts", {}).keys())[:10],
                    "measurementTechnique": "CategoricalAnalysis",
                }
            )

        return variables
