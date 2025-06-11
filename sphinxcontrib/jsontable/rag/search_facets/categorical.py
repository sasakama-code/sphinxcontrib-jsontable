"""Categorical facet generation for search interfaces.

Specialized module for generating categorical facets from statistical analysis data.
Implements categorical-specific logic, validation, and UI configuration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .base import FacetConfig, filter_by_frequency, generate_display_name


@dataclass
class CategoricalFacet:
    """Categorical facet definition for search interfaces.

    Args:
        field_name: Source field name from data.
        display_name: Human-readable display name.
        facet_type: Type of facet (terms, hierarchy, etc.).
        values: Value counts for facet options.
        total_count: Total number of records.
        missing_count: Number of records with missing values.
        ui_config: UI-specific configuration parameters.
    """

    field_name: str
    display_name: str
    facet_type: str = "terms"
    values: dict[str, int] = field(default_factory=dict)
    total_count: int = 0
    missing_count: int = 0
    ui_config: dict[str, Any] = field(default_factory=dict)


class CategoricalFacetGenerator:
    """Generator for categorical search facets.

    Handles creation of categorical facets from statistical analysis data
    with Japanese language optimization and business data enhancement.
    """

    def __init__(self, config: FacetConfig):
        """Initialize categorical facet generator.

        Args:
            config: Configuration for facet generation parameters.
        """
        self.config = config

    def generate_categorical_facets(
        self, statistical_analysis: dict
    ) -> list[CategoricalFacet]:
        """Generate categorical facets from statistical analysis data.

        Args:
            statistical_analysis: Statistical analysis data containing categorical fields.

        Returns:
            List of categorical facets suitable for search interfaces.
        """
        categorical_facets = []

        categorical_fields = statistical_analysis.get("categorical_fields", {})

        for field_name, stats in categorical_fields.items():
            # ファセット化適正チェック
            if not self._is_suitable_for_categorical_facet(stats):
                continue

            # 頻度フィルタリング
            filtered_values = filter_by_frequency(
                stats["value_counts"], self.config.min_frequency_threshold
            )

            if not filtered_values:
                continue

            # 日本語表示名生成
            display_name = generate_display_name(
                field_name, self.config.japanese_display_names
            )

            # UIコンフィグ生成
            ui_config = self._generate_categorical_ui_config(field_name, stats)

            facet = CategoricalFacet(
                field_name=field_name,
                display_name=display_name,
                values=filtered_values,
                total_count=sum(filtered_values.values()),
                missing_count=stats.get("missing_count", 0),
                ui_config=ui_config,
            )

            categorical_facets.append(facet)

        return categorical_facets

    def _is_suitable_for_categorical_facet(self, stats: dict) -> bool:
        """Check if field statistics are suitable for categorical faceting.

        Args:
            stats: Statistical data for a categorical field.

        Returns:
            True if field is suitable for categorical facet generation.
        """
        unique_count = stats.get("unique_count", 0)
        total_values = sum(stats.get("value_counts", {}).values())

        # 適正条件
        return (
            1 < unique_count <= self.config.max_categorical_values
            and total_values >= 3  # 最小データ数（5→3に緩和）
            and (unique_count / total_values)
            <= 0.9  # 多様性が高すぎない（0.8→0.9に緩和）
        )

    def _generate_categorical_ui_config(self, field_name: str, stats: dict) -> dict:
        """Generate UI configuration for categorical facets.

        Args:
            field_name: Name of the field this facet represents.
            stats: Statistical data for the categorical field.

        Returns:
            Dictionary with UI-specific configuration parameters.
        """
        unique_count = stats.get("unique_count", 0)

        ui_config = {
            "widget_type": "checkbox_list"
            if unique_count <= 10
            else "searchable_dropdown",
            "max_visible_items": min(unique_count, 8),
            "enable_search": unique_count > 5,
            "enable_select_all": unique_count > 3,
            "sort_options": ["count_desc", "name_asc", "name_desc"],
            "default_sort": "count_desc",
        }

        # フィールド特有の設定
        if "status" in field_name.lower():
            ui_config["color_coding"] = True
            ui_config["status_colors"] = {
                "active": "#2ecc71",
                "inactive": "#95a5a6",
                "pending": "#f39c12",
                "error": "#e74c3c",
            }

        return ui_config
