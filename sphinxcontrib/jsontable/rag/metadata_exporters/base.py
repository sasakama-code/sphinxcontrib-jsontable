"""Base classes and utilities for metadata export functionality.

Common base classes, data structures, and utility functions used across
all metadata export formats. Provides the foundation for format-specific exporters.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from typing import Any

from ..advanced_metadata import AdvancedMetadata
from ..search_facets import GeneratedFacets


class BaseMetadataExporter:
    """Base class for all metadata exporters.

    Provides common functionality and utilities used by format-specific exporters.
    """

    def __init__(self):
        """Initialize base metadata exporter."""
        pass

    def _estimate_content_size(self, metadata: AdvancedMetadata) -> str:
        """Estimate content size for metadata.

        Args:
            metadata: Advanced metadata containing source information.

        Returns:
            Human-readable size string.
        """
        json_str = json.dumps(asdict(metadata), ensure_ascii=False)
        size_bytes = len(json_str.encode("utf-8"))

        if size_bytes < 1024:
            return f"{size_bytes} bytes"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"

    def _extract_dataset_name(self, metadata: AdvancedMetadata) -> str:
        """Extract dataset name from metadata.

        Args:
            metadata: Advanced metadata containing source information.

        Returns:
            Human-readable dataset name string.
        """
        source_info = metadata.basic_metadata.get("source_info", {})
        file_path = source_info.get("file_path")

        if file_path:
            return f"JSON Table Dataset: {file_path}"
        else:
            return "JSON Table Dataset (Inline)"

    def _contains_japanese(self, text: str) -> bool:
        """Check if text contains Japanese characters.

        Args:
            text: Text to check for Japanese content.

        Returns:
            True if text contains Japanese characters.
        """
        import re

        return bool(re.search(r"[ひらがなカタカナ一-龯]", text))

    def _guess_unit(self, field_name: str) -> str:
        """Guess appropriate unit for field based on name.

        Args:
            field_name: Name of the field to analyze.

        Returns:
            Appropriate unit string for the field.
        """
        field_lower = field_name.lower()

        if any(keyword in field_lower for keyword in ["age", "年齢"]):
            return "歳"
        elif any(
            keyword in field_lower
            for keyword in ["price", "salary", "cost", "金額", "給与"]
        ):
            return "円"
        elif any(keyword in field_lower for keyword in ["percent", "rate", "割合"]):
            return "%"
        elif any(keyword in field_lower for keyword in ["count", "number", "件数"]):
            return "件"
        else:
            return ""

    def _extract_keywords(self, metadata: AdvancedMetadata) -> list[str]:
        """Extract keywords from metadata for discovery.

        Args:
            metadata: Advanced metadata to extract keywords from.

        Returns:
            List of relevant keywords for the dataset.
        """
        keywords = ["JSON", "table", "RAG", "日本語"]

        # エンティティからキーワード抽出
        entities = metadata.entity_classification
        if entities.places:
            keywords.append("地理データ")
        if entities.persons:
            keywords.append("人名データ")
        if entities.organizations:
            keywords.append("組織データ")

        # ドメイン情報
        domain = metadata.plamo_features.embedding_hints.get("domain")
        if domain:
            keywords.append(domain)

        return list(set(keywords))

    def _get_highlightable_fields(self, metadata: AdvancedMetadata) -> list[str]:
        """Get fields suitable for search highlighting.

        Args:
            metadata: Advanced metadata to analyze.

        Returns:
            List of field names suitable for highlighting.
        """
        fields = []

        # テキストフィールド
        for field_name in metadata.statistical_analysis.get("categorical_fields", {}):
            fields.append(field_name)

        # エンティティフィールド
        if metadata.entity_classification.persons:
            fields.append("detected_persons.name")
        if metadata.entity_classification.places:
            fields.append("detected_places.place")
        if metadata.entity_classification.organizations:
            fields.append("detected_organizations.organization")

        return fields

    def _get_suggestion_fields(self, metadata: AdvancedMetadata) -> list[str]:
        """Get fields suitable for search suggestions.

        Args:
            metadata: Advanced metadata to analyze.

        Returns:
            List of field names suitable for autocomplete suggestions.
        """
        suggestion_fields = []

        # 高い多様性を持つカテゴリフィールド
        for field_name, stats in metadata.statistical_analysis.get(
            "categorical_fields", {}
        ).items():
            diversity = stats.get("diversity_index", 0)
            if diversity > 0.5:  # 多様性が高い
                suggestion_fields.append(field_name)

        return suggestion_fields

    def _organize_facets_into_groups(self, facets: GeneratedFacets) -> list[dict]:
        """Organize facets into logical groups for UI presentation.

        Args:
            facets: Generated facets to organize.

        Returns:
            List of facet groups with display order and metadata.
        """
        groups = []

        if facets.categorical_facets:
            groups.append(
                {
                    "group_name": "カテゴリ",
                    "group_id": "categorical",
                    "facets": [f.field_name for f in facets.categorical_facets],
                    "collapsed": False,
                }
            )

        if facets.numerical_facets:
            groups.append(
                {
                    "group_name": "数値範囲",
                    "group_id": "numerical",
                    "facets": [f.field_name for f in facets.numerical_facets],
                    "collapsed": False,
                }
            )

        if facets.temporal_facets:
            groups.append(
                {
                    "group_name": "日付・時間",
                    "group_id": "temporal",
                    "facets": [f.field_name for f in facets.temporal_facets],
                    "collapsed": True,
                }
            )

        if facets.entity_facets:
            groups.append(
                {
                    "group_name": "エンティティ",
                    "group_id": "entities",
                    "facets": [f.entity_type for f in facets.entity_facets],
                    "collapsed": True,
                }
            )

        return groups

    def _apply_custom_transformations(self, data: dict, transformations: list) -> dict:
        """Apply custom transformations to export data.

        Args:
            data: Data to transform.
            transformations: List of transformation specifications.

        Returns:
            Transformed data dictionary.
        """
        result = data.copy()

        for transformation in transformations:
            transform_type = transformation.get("type")
            params = transformation.get("parameters", {})

            if transform_type == "rename_fields":
                field_mappings = params.get("mappings", {})
                for old_name, new_name in field_mappings.items():
                    if old_name in result:
                        result[new_name] = result.pop(old_name)

            elif transform_type == "filter_fields":
                allowed_fields = params.get("allowed_fields", [])
                if allowed_fields:
                    result = {k: v for k, v in result.items() if k in allowed_fields}

            elif transform_type == "flatten":
                # ネストした構造をフラット化
                result = self._flatten_dict(result, params.get("separator", "_"))

        return result

    def _flatten_dict(self, nested_dict: dict, separator: str = "_") -> dict:
        """Flatten nested dictionary structure.

        Args:
            nested_dict: Dictionary to flatten.
            separator: Separator for flattened keys.

        Returns:
            Flattened dictionary.
        """
        flattened = {}

        def _flatten(obj, parent_key=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_key = f"{parent_key}{separator}{key}" if parent_key else key
                    _flatten(value, new_key)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    new_key = f"{parent_key}{separator}{i}" if parent_key else str(i)
                    _flatten(item, new_key)
            else:
                flattened[parent_key] = obj

        _flatten(nested_dict)
        return flattened
