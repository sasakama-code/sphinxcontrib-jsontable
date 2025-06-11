"""Numerical facet generation for range-based filtering.

Specialized module for generating numerical facets with optimized ranges,
statistical distribution analysis, and Japanese number formatting.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .base import FacetConfig, generate_display_name


@dataclass
class NumericalFacet:
    """Numerical facet definition for range-based filtering.

    Args:
        field_name: Source field name from data.
        display_name: Human-readable display name.
        facet_type: Type of facet (range, histogram, etc.).
        min_value: Minimum value in the dataset.
        max_value: Maximum value in the dataset.
        ranges: List of predefined ranges with counts.
        distribution_info: Statistical distribution information.
        ui_config: UI-specific configuration parameters.
    """

    field_name: str
    display_name: str
    facet_type: str = "range"
    min_value: float = 0.0
    max_value: float = 0.0
    ranges: list[dict[str, Any]] = field(default_factory=list)
    distribution_info: dict[str, Any] = field(default_factory=dict)
    ui_config: dict[str, Any] = field(default_factory=dict)


class NumericalFacetGenerator:
    """Generator for numerical search facets.
    
    Handles creation of numerical facets with optimized ranges based on 
    statistical distribution and Japanese number formatting.
    """

    def __init__(self, config: FacetConfig):
        """Initialize numerical facet generator.

        Args:
            config: Configuration for facet generation parameters.
        """
        self.config = config

    def generate_numerical_facets(
        self, statistical_analysis: dict
    ) -> list[NumericalFacet]:
        """Generate numerical facets from statistical analysis data.

        Args:
            statistical_analysis: Statistical analysis data containing numerical fields.

        Returns:
            List of numerical facets with optimized ranges.
        """
        numerical_facets = []

        numerical_fields = statistical_analysis.get("numerical_fields", {})

        for field_name, stats in numerical_fields.items():
            # 数値ファセット適正チェック
            if not self._is_suitable_for_numerical_facet(stats):
                continue

            # 最適な範囲生成
            ranges = self._generate_optimal_numerical_ranges(stats)

            # 日本語表示名生成
            display_name = generate_display_name(
                field_name, self.config.japanese_display_names
            )

            # UIコンフィグ生成
            ui_config = self._generate_numerical_ui_config(field_name, stats)

            # 分布情報
            distribution_info = {
                "distribution_type": stats.get("distribution_type", "unknown"),
                "skewness": stats.get("skewness", 0.0),
                "has_outliers": len(stats.get("outliers", [])) > 0,
                "quartiles": stats.get("quartiles", [0, 0, 0]),
            }

            facet = NumericalFacet(
                field_name=field_name,
                display_name=display_name,
                min_value=stats["min_value"],
                max_value=stats["max_value"],
                ranges=ranges,
                distribution_info=distribution_info,
                ui_config=ui_config,
            )

            numerical_facets.append(facet)

        return numerical_facets

    def _is_suitable_for_numerical_facet(self, stats: dict) -> bool:
        """Check if field statistics are suitable for numerical faceting.

        Args:
            stats: Statistical data for a numerical field.

        Returns:
            True if field is suitable for numerical facet generation.
        """
        min_val = stats.get("min_value", 0)
        max_val = stats.get("max_value", 0)

        # 適正条件
        return (
            max_val > min_val  # 値の範囲がある
            and (max_val - min_val) > 1  # 意味のある範囲
            and not (min_val == 0 and max_val == 1)  # バイナリでない
        )

    def _generate_optimal_numerical_ranges(self, stats: dict) -> list[dict]:
        """Generate optimal numerical ranges based on statistical distribution.

        Args:
            stats: Statistical analysis data for numerical field.

        Returns:
            List of range dictionaries with from/to values and labels.
        """
        min_val = stats["min_value"]
        max_val = stats["max_value"]
        quartiles = stats.get("quartiles", [min_val, (min_val + max_val) / 2, max_val])

        # 四分位数ベースの範囲生成（より自然な分布）
        ranges = []

        # Q1未満
        if quartiles[0] > min_val:
            ranges.append(
                {
                    "from": min_val,
                    "to": quartiles[0],
                    "label": f"{self._format_number(min_val)} 以下",
                    "type": "below_q1",
                }
            )

        # Q1-Q2
        ranges.append(
            {
                "from": quartiles[0],
                "to": quartiles[1],
                "label": f"{self._format_number(quartiles[0])} - {self._format_number(quartiles[1])}",
                "type": "q1_q2",
            }
        )

        # Q2-Q3
        ranges.append(
            {
                "from": quartiles[1],
                "to": quartiles[2],
                "label": f"{self._format_number(quartiles[1])} - {self._format_number(quartiles[2])}",
                "type": "q2_q3",
            }
        )

        # Q3超過
        if quartiles[2] < max_val:
            ranges.append(
                {
                    "from": quartiles[2],
                    "to": max_val,
                    "label": f"{self._format_number(quartiles[2])} 以上",
                    "type": "above_q3",
                }
            )

        # 外れ値が多い場合の特別範囲
        outliers = stats.get("outliers", [])
        if len(outliers) > len(stats.get("data", [])) * 0.1:  # 10%以上が外れ値
            outlier_min = min(outliers) if outliers else min_val
            outlier_max = max(outliers) if outliers else max_val
            ranges.append(
                {
                    "from": outlier_min,
                    "to": outlier_max,
                    "label": "外れ値範囲",
                    "type": "outliers",
                }
            )

        return ranges

    def _format_number(self, number: float) -> str:
        """Format numbers in Japanese style with appropriate units.

        Args:
            number: Numeric value to format.

        Returns:
            Formatted string with Japanese numerical units (万, 千).
        """
        if number >= 10000:
            return f"{number / 10000:.1f}万"
        elif number >= 1000:
            return f"{number / 1000:.1f}千"
        elif number == int(number):
            return str(int(number))
        else:
            return f"{number:.1f}"

    def _generate_numerical_ui_config(self, field_name: str, stats: dict) -> dict:
        """Generate UI configuration for numerical facets.

        Args:
            field_name: Name of the field this facet represents.
            stats: Statistical data for the numerical field.

        Returns:
            Dictionary with UI-specific configuration parameters.
        """
        ui_config = {
            "widget_type": "range_slider",
            "enable_histogram": True,
            "step_size": self._calculate_step_size(stats),
            "number_format": self._detect_number_format(field_name),
            "enable_text_input": True,
        }

        # フィールド特有の設定
        if any(
            keyword in field_name.lower()
            for keyword in ["price", "salary", "cost", "金額", "給与"]
        ):
            ui_config["number_format"] = "currency"
            ui_config["currency_symbol"] = "¥"

        elif any(keyword in field_name.lower() for keyword in ["age", "年齢"]):
            ui_config["number_format"] = "integer"
            ui_config["suffix"] = "歳"

        elif any(
            keyword in field_name.lower() for keyword in ["percent", "rate", "割合"]
        ):
            ui_config["number_format"] = "percentage"
            ui_config["suffix"] = "%"

        return ui_config

    def _calculate_step_size(self, stats: dict) -> float:
        """Calculate appropriate step size for numerical facet sliders.

        Args:
            stats: Statistical data containing min/max values.

        Returns:
            Step size value for UI slider components.
        """
        min_val = stats["min_value"]
        max_val = stats["max_value"]
        range_val = max_val - min_val

        if range_val <= 1:
            return 0.01
        elif range_val <= 10:
            return 0.1
        elif range_val <= 100:
            return 1
        elif range_val <= 1000:
            return 10
        else:
            return 100

    def _detect_number_format(self, field_name: str) -> str:
        """Detect appropriate number format based on field name.

        Args:
            field_name: Name of the numerical field.

        Returns:
            Format type string (currency, percentage, integer, decimal).
        """
        if any(
            keyword in field_name.lower()
            for keyword in ["price", "salary", "cost", "金額"]
        ):
            return "currency"
        elif any(
            keyword in field_name.lower() for keyword in ["percent", "rate", "割合"]
        ):
            return "percentage"
        elif any(
            keyword in field_name.lower()
            for keyword in ["age", "count", "number", "年齢"]
        ):
            return "integer"
        else:
            return "decimal"
