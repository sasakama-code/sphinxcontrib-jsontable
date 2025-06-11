"""Faceted search index generation for filtered retrieval.

Specialized generator for faceted search indices supporting categorical,
numerical, temporal, and entity-based filtering with Japanese optimization.
"""

import logging
import re
from typing import Any

from .base import BaseIndexGenerator, FacetedSearchIndex
from .japanese_processor import JapaneseQueryProcessor

logger = logging.getLogger(__name__)

__all__ = ["FacetedIndexGenerator"]


class FacetedIndexGenerator(BaseIndexGenerator):
    """Faceted search index generator.
    
    Specialized generator for creating faceted search indices supporting
    categorical, numerical, temporal, and entity-based filtering.
    """

    def __init__(self, config: dict[str, Any]):
        """Initialize faceted index generator.
        
        Args:
            config: Configuration dictionary for faceted index generation.
        """
        super().__init__(config)
        self.faceted_config = config.get("faceted_search", {})
        self.japanese_processor = JapaneseQueryProcessor()

    def generate(
        self, vector_chunks: list, basic_metadata: Any = None
    ) -> FacetedSearchIndex:
        """ファセット検索インデックス生成.
        
        Args:
            vector_chunks: ベクトル化されたチャンクのリスト.
            basic_metadata: 基本メタデータ（オプション）.
            
        Returns:
            生成されたファセット検索インデックス.
        """
        if not self.validate_input(vector_chunks):
            raise ValueError("Invalid vector chunks provided")

        facet_index = FacetedSearchIndex()

        # カテゴリファセット構築
        facet_index.categorical_facets = self._build_categorical_facets(
            vector_chunks, basic_metadata
        )

        # 数値ファセット構築
        facet_index.numerical_facets = self._build_numerical_facets(
            vector_chunks, basic_metadata
        )

        # 時間ファセット構築
        facet_index.temporal_facets = self._build_temporal_facets(vector_chunks)

        # エンティティファセット構築
        facet_index.entity_facets = self._build_entity_facets(vector_chunks)

        logger.info(
            f"Faceted index built with {len(facet_index.categorical_facets)} categorical facets"
        )

        return facet_index

    def _build_categorical_facets(
        self, vector_chunks: list, basic_metadata: Any
    ) -> dict[str, dict[str, list[int]]]:
        """カテゴリファセット構築.
        
        Args:
            vector_chunks: ベクトルチャンクのリスト.
            basic_metadata: 基本メタデータ.
            
        Returns:
            カテゴリファセット辞書.
        """
        categorical_facets: dict[str, dict[str, list[int]]] = {}

        # データ型ファセット
        categorical_facets["data_type"] = {}

        for i, chunk in enumerate(vector_chunks):
            # チャンクタイプによる分類
            chunk_type = getattr(chunk.original_chunk, "chunk_type", "unknown")

            if chunk_type not in categorical_facets["data_type"]:
                categorical_facets["data_type"][chunk_type] = []
            categorical_facets["data_type"][chunk_type].append(i)

        # ビジネスカテゴリファセット
        categorical_facets["business_category"] = {}
        business_categories = [
            "financial",
            "organizational",
            "operational",
            "strategic",
        ]

        for category in business_categories:
            categorical_facets["business_category"][category] = []

            for i, chunk in enumerate(vector_chunks):
                if self.japanese_processor.categorize_business_content(
                    chunk.original_chunk.content, category
                ):
                    categorical_facets["business_category"][category].append(i)

        # 言語タイプファセット
        categorical_facets["language_type"] = self._build_language_type_facets(
            vector_chunks
        )

        return categorical_facets

    def _build_language_type_facets(
        self, vector_chunks: list
    ) -> dict[str, list[int]]:
        """言語タイプファセット構築.
        
        Args:
            vector_chunks: ベクトルチャンクのリスト.
            
        Returns:
            言語タイプファセット辞書.
        """
        language_facets = {
            "japanese_rich": [],  # 日本語豊富
            "mixed_language": [],  # 日英混在
            "english_dominant": [],  # 英語中心
            "numerical_focus": [],  # 数値中心
        }

        for i, chunk in enumerate(vector_chunks):
            content = chunk.original_chunk.content
            features = self.japanese_processor.extract_japanese_features(content)

            # 言語タイプ分類
            if features["has_kanji"] and features["has_hiragana"]:
                language_facets["japanese_rich"].append(i)
            elif features["has_kanji"] or features["has_katakana"]:
                language_facets["mixed_language"].append(i)
            elif re.search(r"[A-Za-z]", content):
                language_facets["english_dominant"].append(i)

            if features["has_numbers"]:
                language_facets["numerical_focus"].append(i)

        return language_facets

    def _build_numerical_facets(
        self, vector_chunks: list, basic_metadata: Any
    ) -> dict[str, dict[str, list[int]]]:
        """数値ファセット構築.
        
        Args:
            vector_chunks: ベクトルチャンクのリスト.
            basic_metadata: 基本メタデータ.
            
        Returns:
            数値ファセット辞書.
        """
        numerical_facets: dict[str, dict[str, list[int]]] = {}

        # 金額範囲ファセット
        numerical_facets["amount_range"] = {
            "small": [],  # ~100万円
            "medium": [],  # 100万円~1億円
            "large": [],  # 1億円~
            "unknown": [],
        }

        # 数値密度ファセット
        numerical_facets["number_density"] = {
            "low": [],  # 数値少ない
            "medium": [],  # 数値普通
            "high": [],  # 数値多い
        }

        for i, chunk in enumerate(vector_chunks):
            content = chunk.original_chunk.content

            # 金額分析
            amounts = re.findall(r"(\d+(?:,\d{3})*(?:万|億)?円)", content)

            if amounts:
                max_amount = max(
                    self.japanese_processor.parse_japanese_amount(amount)
                    for amount in amounts
                )

                if max_amount < 1000000:  # 100万円未満
                    numerical_facets["amount_range"]["small"].append(i)
                elif max_amount < 100000000:  # 1億円未満
                    numerical_facets["amount_range"]["medium"].append(i)
                else:
                    numerical_facets["amount_range"]["large"].append(i)
            else:
                numerical_facets["amount_range"]["unknown"].append(i)

            # 数値密度分析
            numbers = re.findall(r"\d+", content)
            number_density = len(numbers) / max(len(content.split()), 1)

            if number_density < 0.1:
                numerical_facets["number_density"]["low"].append(i)
            elif number_density < 0.3:
                numerical_facets["number_density"]["medium"].append(i)
            else:
                numerical_facets["number_density"]["high"].append(i)

        return numerical_facets

    def _build_temporal_facets(
        self, vector_chunks: list
    ) -> dict[str, dict[str, list[int]]]:
        """時間ファセット構築.
        
        Args:
            vector_chunks: ベクトルチャンクのリスト.
            
        Returns:
            時間ファセット辞書.
        """
        temporal_facets: dict[str, dict[str, list[int]]] = {}

        # 年度ファセット
        temporal_facets["fiscal_year"] = {}

        for i, chunk in enumerate(vector_chunks):
            content = chunk.original_chunk.content

            # 年度抽出
            years = re.findall(r"(\d{4})年度?", content)

            for year in years:
                if year not in temporal_facets["fiscal_year"]:
                    temporal_facets["fiscal_year"][year] = []
                temporal_facets["fiscal_year"][year].append(i)

        # 四半期ファセット
        temporal_facets["quarter"] = {}
        quarters = [
            "Q1",
            "Q2",
            "Q3",
            "Q4",
            "第1四半期",
            "第2四半期",
            "第3四半期",
            "第4四半期",
        ]

        for quarter in quarters:
            temporal_facets["quarter"][quarter] = []

            for i, chunk in enumerate(vector_chunks):
                if quarter in chunk.original_chunk.content:
                    temporal_facets["quarter"][quarter].append(i)

        # 時期ファセット
        temporal_facets["time_period"] = self._build_time_period_facets(vector_chunks)

        return temporal_facets

    def _build_time_period_facets(
        self, vector_chunks: list
    ) -> dict[str, list[int]]:
        """時期ファセット構築.
        
        Args:
            vector_chunks: ベクトルチャンクのリスト.
            
        Returns:
            時期ファセット辞書.
        """
        time_periods = {
            "daily": [],
            "monthly": [],
            "quarterly": [],
            "yearly": [],
        }

        time_patterns = {
            "daily": [r"\d+日", r"\d{4}/\d{1,2}/\d{1,2}", r"\d{1,2}/\d{1,2}"],
            "monthly": [r"\d+月", r"\d{4}/\d{1,2}", r"月次"],
            "quarterly": [r"四半期", r"Q[1-4]", r"クォーター"],
            "yearly": [r"\d{4}年", r"年次", r"年度"],
        }

        for i, chunk in enumerate(vector_chunks):
            content = chunk.original_chunk.content

            for period, patterns in time_patterns.items():
                if any(re.search(pattern, content) for pattern in patterns):
                    time_periods[period].append(i)

        return time_periods

    def _build_entity_facets(
        self, vector_chunks: list
    ) -> dict[str, dict[str, list[int]]]:
        """エンティティファセット構築.
        
        Args:
            vector_chunks: ベクトルチャンクのリスト.
            
        Returns:
            エンティティファセット辞書.
        """
        entity_facets: dict[str, dict[str, list[int]]] = {}

        # 組織エンティティファセット
        entity_facets["organization"] = {}

        for i, chunk in enumerate(vector_chunks):
            content = chunk.original_chunk.content

            # 会社名抽出
            companies = re.findall(r"株式会社[一-龯]+|[一-龯]+株式会社", content)

            for company in companies:
                if company not in entity_facets["organization"]:
                    entity_facets["organization"][company] = []
                entity_facets["organization"][company].append(i)

        # 人名エンティティファセット
        entity_facets["person"] = {}

        for i, chunk in enumerate(vector_chunks):
            content = chunk.original_chunk.content

            # 人名抽出（簡易版）
            persons = re.findall(r"[一-龯]{2,4}(?:社長|部長|課長|主任|取締役)", content)

            for person in persons:
                person_name = re.sub(r"(社長|部長|課長|主任|取締役)$", "", person)
                if person_name not in entity_facets["person"]:
                    entity_facets["person"][person_name] = []
                entity_facets["person"][person_name].append(i)

        # 部門エンティティファセット
        entity_facets["department"] = self._build_department_facets(vector_chunks)

        return entity_facets

    def _build_department_facets(
        self, vector_chunks: list
    ) -> dict[str, list[int]]:
        """部門ファセット構築.
        
        Args:
            vector_chunks: ベクトルチャンクのリスト.
            
        Returns:
            部門ファセット辞書.
        """
        department_facets = {}

        department_patterns = [
            r"[一-龯]+部",
            r"[一-龯]+課",
            r"[一-龯]+室",
            r"[一-龯]+センター",
        ]

        for i, chunk in enumerate(vector_chunks):
            content = chunk.original_chunk.content

            for pattern in department_patterns:
                departments = re.findall(pattern, content)

                for dept in departments:
                    if dept not in department_facets:
                        department_facets[dept] = []
                    department_facets[dept].append(i)

        return department_facets

    def filter_by_facets(
        self,
        facet_index: FacetedSearchIndex,
        filters: dict[str, Any],
    ) -> list[int]:
        """ファセットによるフィルタリング.
        
        Args:
            facet_index: ファセット検索インデックス.
            filters: フィルタ条件辞書.
            
        Returns:
            フィルタ条件に合致するチャンクインデックスのリスト.
        """
        result_indices = set()

        # カテゴリファセットでフィルタ
        if "categorical" in filters:
            categorical_results = self._filter_categorical(
                facet_index.categorical_facets, filters["categorical"]
            )
            if result_indices:
                result_indices &= categorical_results
            else:
                result_indices = categorical_results

        # 数値ファセットでフィルタ
        if "numerical" in filters:
            numerical_results = self._filter_numerical(
                facet_index.numerical_facets, filters["numerical"]
            )
            if result_indices:
                result_indices &= numerical_results
            else:
                result_indices = numerical_results

        # 時間ファセットでフィルタ
        if "temporal" in filters:
            temporal_results = self._filter_temporal(
                facet_index.temporal_facets, filters["temporal"]
            )
            if result_indices:
                result_indices &= temporal_results
            else:
                result_indices = temporal_results

        # エンティティファセットでフィルタ
        if "entity" in filters:
            entity_results = self._filter_entity(
                facet_index.entity_facets, filters["entity"]
            )
            if result_indices:
                result_indices &= entity_results
            else:
                result_indices = entity_results

        return list(result_indices)

    def _filter_categorical(
        self, categorical_facets: dict, filters: dict
    ) -> set[int]:
        """カテゴリファセットフィルタリング."""
        result_indices = set()

        for facet_name, facet_values in filters.items():
            if facet_name in categorical_facets:
                facet_data = categorical_facets[facet_name]

                for value in facet_values:
                    if value in facet_data:
                        result_indices.update(facet_data[value])

        return result_indices

    def _filter_numerical(
        self, numerical_facets: dict, filters: dict
    ) -> set[int]:
        """数値ファセットフィルタリング."""
        result_indices = set()

        for facet_name, facet_values in filters.items():
            if facet_name in numerical_facets:
                facet_data = numerical_facets[facet_name]

                for value in facet_values:
                    if value in facet_data:
                        result_indices.update(facet_data[value])

        return result_indices

    def _filter_temporal(
        self, temporal_facets: dict, filters: dict
    ) -> set[int]:
        """時間ファセットフィルタリング."""
        result_indices = set()

        for facet_name, facet_values in filters.items():
            if facet_name in temporal_facets:
                facet_data = temporal_facets[facet_name]

                for value in facet_values:
                    if value in facet_data:
                        result_indices.update(facet_data[value])

        return result_indices

    def _filter_entity(
        self, entity_facets: dict, filters: dict
    ) -> set[int]:
        """エンティティファセットフィルタリング."""
        result_indices = set()

        for facet_name, facet_values in filters.items():
            if facet_name in entity_facets:
                facet_data = entity_facets[facet_name]

                for value in facet_values:
                    if value in facet_data:
                        result_indices.update(facet_data[value])

        return result_indices

    def get_facet_statistics(
        self, facet_index: FacetedSearchIndex
    ) -> dict[str, Any]:
        """ファセットインデックス統計情報取得.
        
        Args:
            facet_index: 統計情報を取得するファセットインデックス.
            
        Returns:
            統計情報辞書.
        """
        return {
            "categorical_facet_count": len(facet_index.categorical_facets),
            "numerical_facet_count": len(facet_index.numerical_facets),
            "temporal_facet_count": len(facet_index.temporal_facets),
            "entity_facet_count": len(facet_index.entity_facets),
            "total_facet_values": (
                sum(
                    len(values)
                    for facet in facet_index.categorical_facets.values()
                    for values in facet.values()
                )
                + sum(
                    len(values)
                    for facet in facet_index.numerical_facets.values()
                    for values in facet.values()
                )
                + sum(
                    len(values)
                    for facet in facet_index.temporal_facets.values()
                    for values in facet.values()
                )
                + sum(
                    len(values)
                    for facet in facet_index.entity_facets.values()
                    for values in facet.values()
                )
            ),
        }
