"""Custom format metadata exporter.

Specialized module for exporting metadata in user-defined custom formats
with flexible transformation and formatting options.
"""

from __future__ import annotations

from typing import Any

from ..advanced_metadata import AdvancedMetadata
from .base import BaseMetadataExporter


class CustomExporter(BaseMetadataExporter):
    """Custom format metadata exporter.

    Exports metadata in user-defined custom formats with
    flexible transformation and field selection capabilities.
    """

    def __init__(self):
        """Initialize custom exporter."""
        super().__init__()

    def export(
        self, metadata: AdvancedMetadata, config: dict[str, Any]
    ) -> dict[str, Any]:
        """Export custom format based on user configuration.

        Args:
            metadata: Advanced metadata to export.
            config: Custom configuration for export format.

        Returns:
            Custom formatted metadata based on user specifications.
        """
        custom_format = config.get("format", {})
        include_sections = config.get("include_sections", ["all"])

        custom_output = {
            "metadata_format": "custom",
            "generated_at": self._get_timestamp(),
        }

        # セクション別のデータ追加
        if "all" in include_sections or "basic" in include_sections:
            custom_output["basic_metadata"] = metadata.basic_metadata

        if "all" in include_sections or "statistical" in include_sections:
            custom_output["statistical_analysis"] = metadata.statistical_analysis

        if "all" in include_sections or "entities" in include_sections:
            custom_output["entity_classification"] = self._format_entities(
                metadata.entity_classification
            )

        if "all" in include_sections or "quality" in include_sections:
            custom_output["data_quality"] = self._format_quality(metadata.data_quality)

        if "all" in include_sections or "plamo" in include_sections:
            custom_output["plamo_features"] = self._format_plamo(
                metadata.plamo_features
            )

        # カスタム変換の適用
        if "transformations" in custom_format:
            custom_output = self._apply_custom_transformations(
                custom_output, custom_format["transformations"]
            )

        return custom_output

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime

        return datetime.now().isoformat()

    def _format_entities(self, entity_classification) -> dict[str, Any]:
        """Format entity classification for custom export."""
        from dataclasses import asdict

        return {
            "persons": [asdict(p) for p in entity_classification.persons],
            "places": [asdict(p) for p in entity_classification.places],
            "organizations": [asdict(o) for o in entity_classification.organizations],
            "business_terms": [asdict(b) for b in entity_classification.business_terms],
        }

    def _format_quality(self, data_quality) -> dict[str, Any]:
        """Format data quality for custom export."""
        from dataclasses import asdict

        return asdict(data_quality)

    def _format_plamo(self, plamo_features) -> dict[str, Any]:
        """Format PLaMo features for custom export."""
        from dataclasses import asdict

        return asdict(plamo_features)
