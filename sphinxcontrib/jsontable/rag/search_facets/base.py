"""Base classes and configurations for search facet generation.

Common data classes and configuration objects used across all facet types.
Provides the foundation for categorical, numerical, temporal, and entity facets.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FacetConfig:
    """Configuration settings for facet generation.

    Args:
        max_categorical_values: Maximum number of values for categorical facets.
        max_numerical_ranges: Maximum number of ranges for numerical facets.
        min_frequency_threshold: Minimum frequency for facet value inclusion.
        enable_entity_facets: Whether to generate entity-based facets.
        japanese_display_names: Use Japanese display names when available.
        confidence_threshold: Minimum confidence score for entity inclusion.
    """

    max_categorical_values: int = 20
    max_numerical_ranges: int = 5
    min_frequency_threshold: int = 2
    enable_entity_facets: bool = True
    japanese_display_names: bool = True
    confidence_threshold: float = 0.6


@dataclass
class GeneratedFacets:
    """Container for all generated search facets.

    Args:
        categorical_facets: List of categorical facets for discrete values.
        numerical_facets: List of numerical facets for range-based filtering.
        temporal_facets: List of temporal facets for date/time filtering.
        entity_facets: List of entity-based facets for semantic filtering.
        generation_metadata: Metadata about the facet generation process.
    """

    categorical_facets: list[Any] = field(default_factory=list)
    numerical_facets: list[Any] = field(default_factory=list)
    temporal_facets: list[Any] = field(default_factory=list)
    entity_facets: list[Any] = field(default_factory=list)
    generation_metadata: dict[str, Any] = field(default_factory=dict)


def get_japanese_field_names() -> dict[str, str]:
    """Get Japanese field name mappings.
    
    Returns:
        Dictionary mapping English field names to Japanese equivalents.
    """
    return {
        "name": "名前",
        "age": "年齢",
        "department": "部署",
        "position": "役職",
        "salary": "給与",
        "email": "メールアドレス",
        "phone": "電話番号",
        "address": "住所",
        "company": "会社",
        "project": "プロジェクト",
        "skill": "スキル",
        "experience": "経験年数",
        "date": "日付",
        "created_at": "作成日",
        "updated_at": "更新日",
        "price": "価格",
        "category": "カテゴリ",
        "status": "ステータス",
        "type": "種別",
    }


def generate_display_name(field_name: str, use_japanese: bool = True) -> str:
    """Generate human-readable display name for field.

    Args:
        field_name: Technical field name from data.
        use_japanese: Whether to prefer Japanese names when available.

    Returns:
        Human-readable display name, preferring Japanese when configured.
    """
    if use_japanese:
        # 日本語名マッピング
        japanese_field_names = get_japanese_field_names()
        japanese_name = japanese_field_names.get(field_name.lower())
        if japanese_name:
            return japanese_name

        # アンダースコアをスペースに変換し、タイトルケース化
        display_name = field_name.replace("_", " ").title()

        # 一般的な英語フィールド名を日本語に変換
        translations = {
            "Id": "ID",
            "Url": "URL",
            "Api": "API",
            "Json": "JSON",
            "Xml": "XML",
            "Html": "HTML",
            "Css": "CSS",
            "Sql": "SQL",
        }

        for eng, jp in translations.items():
            display_name = display_name.replace(eng, jp)

        return display_name
    else:
        return field_name.replace("_", " ").title()


def filter_by_frequency(value_counts: dict, threshold: int) -> dict:
    """Filter values by frequency threshold.

    Args:
        value_counts: Dictionary mapping values to their frequency counts.
        threshold: Minimum frequency threshold for inclusion.

    Returns:
        Filtered dictionary containing only values meeting threshold.
    """
    return {
        value: count for value, count in value_counts.items() if count >= threshold
    }
