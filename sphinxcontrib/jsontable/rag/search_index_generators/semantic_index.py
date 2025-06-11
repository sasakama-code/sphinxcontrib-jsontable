"""Semantic search index generation with Japanese optimization.

Specialized generator for keyword-based semantic search indices with
Japanese language processing and business term recognition.
"""

import logging
from typing import Any

from .base import BaseIndexGenerator, SemanticSearchIndex
from .japanese_processor import JapaneseQueryProcessor

logger = logging.getLogger(__name__)

__all__ = ["SemanticIndexGenerator"]


class SemanticIndexGenerator(BaseIndexGenerator):
    """Semantic search index generator with Japanese optimization.

    Specialized generator for creating keyword-based semantic search indices
    with Japanese language processing and business term recognition.
    """

    def __init__(self, config: dict[str, Any]):
        """Initialize semantic index generator.

        Args:
            config: Configuration dictionary for semantic index generation.
        """
        super().__init__(config)
        self.semantic_config = config.get("semantic_search", {})
        self.japanese_processor = JapaneseQueryProcessor()

    def generate(self, vector_chunks: list) -> SemanticSearchIndex:
        """セマンティック検索インデックス生成.

        Args:
            vector_chunks: ベクトル化されたチャンクのリスト.

        Returns:
            生成されたセマンティック検索インデックス.
        """
        if not self.validate_input(vector_chunks):
            raise ValueError("Invalid vector chunks provided")

        semantic_index = SemanticSearchIndex()

        # テキストセグメント抽出
        semantic_index.text_segments = [
            chunk.original_chunk.content for chunk in vector_chunks
        ]

        # 日本語キーワードインデックス構築
        semantic_index.japanese_keyword_index = self._build_japanese_keyword_index(
            vector_chunks
        )

        # ビジネス用語インデックス構築
        semantic_index.business_term_index = self._build_business_term_index(
            vector_chunks
        )

        # セマンティックマッピング構築
        semantic_index.semantic_mappings = self._build_semantic_mappings(vector_chunks)

        logger.info(
            f"Semantic index built with {len(semantic_index.japanese_keyword_index)} keywords"
        )

        return semantic_index

    def _build_japanese_keyword_index(
        self, vector_chunks: list
    ) -> dict[str, list[int]]:
        """日本語キーワードインデックス構築.

        Args:
            vector_chunks: ベクトルチャンクのリスト.

        Returns:
            キーワードからチャンクインデックスへのマッピング.
        """
        keyword_index: dict[str, list[int]] = {}

        for i, chunk in enumerate(vector_chunks):
            content = chunk.original_chunk.content

            # 日本語プロセッサーを使用してキーワード抽出
            keywords = self.japanese_processor.extract_keywords(content)

            for keyword in keywords:
                if self._is_valid_keyword(keyword):
                    if keyword not in keyword_index:
                        keyword_index[keyword] = []
                    keyword_index[keyword].append(i)

        # 頻度フィルタリング
        min_frequency = self.semantic_config.get("min_term_frequency", 2)
        keyword_index = {
            keyword: indices
            for keyword, indices in keyword_index.items()
            if len(indices) >= min_frequency
        }

        return keyword_index

    def _build_business_term_index(self, vector_chunks: list) -> dict[str, list[int]]:
        """ビジネス用語インデックス構築.

        Args:
            vector_chunks: ベクトルチャンクのリスト.

        Returns:
            ビジネス用語からチャンクインデックスへのマッピング.
        """
        business_term_index: dict[str, list[int]] = {}

        for i, chunk in enumerate(vector_chunks):
            content = chunk.original_chunk.content

            # 日本語プロセッサーを使用してビジネス用語抽出
            business_terms = self.japanese_processor.extract_business_terms(content)

            for term in business_terms:
                if term not in business_term_index:
                    business_term_index[term] = []
                business_term_index[term].append(i)

        return business_term_index

    def _build_semantic_mappings(self, vector_chunks: list) -> dict[str, list[int]]:
        """セマンティックマッピング構築.

        Args:
            vector_chunks: ベクトルチャンクのリスト.

        Returns:
            セマンティックカテゴリからチャンクインデックスへのマッピング.
        """
        semantic_mappings: dict[str, list[int]] = {}

        # カテゴリ別セマンティックマッピング
        semantic_categories = {
            "financial": ["売上", "利益", "収益", "売上高", "純利益", "営業利益"],
            "organizational": ["会社", "企業", "部", "課", "従業員", "社員"],
            "temporal": ["年度", "四半期", "月", "期間"],
            "numerical": ["金額", "数量", "率", "パーセント"],
        }

        for category, terms in semantic_categories.items():
            semantic_mappings[category] = []

            for i, chunk in enumerate(vector_chunks):
                content = chunk.original_chunk.content

                if any(term in content for term in terms):
                    semantic_mappings[category].append(i)

        return semantic_mappings

    def _is_valid_keyword(self, keyword: str) -> bool:
        """キーワードの有効性チェック.

        Args:
            keyword: チェック対象のキーワード.

        Returns:
            有効な場合True.
        """
        # 最小長チェック
        if len(keyword) < 2:
            return False

        # 数字のみの場合は除外
        if keyword.isdigit():
            return False

        # 単一文字の記号は除外
        if len(keyword) == 1 and not keyword.isalnum():
            return False

        return True

    def search_by_keywords(
        self,
        query: str,
        semantic_index: SemanticSearchIndex,
        max_results: int = 10,
    ) -> list[tuple[int, float]]:
        """キーワードによるセマンティック検索.

        Args:
            query: 検索クエリ.
            semantic_index: セマンティック検索インデックス.
            max_results: 最大結果数.

        Returns:
            (チャンクインデックス, スコア)のタプルリスト.
        """
        # クエリ拡張
        expanded_queries = self.japanese_processor.expand_query(query)

        # 候補チャンクとスコアの収集
        candidate_scores: dict[int, float] = {}

        for expanded_query in expanded_queries:
            # 日本語キーワード検索
            for keyword in self.japanese_processor.extract_keywords(expanded_query):
                if keyword in semantic_index.japanese_keyword_index:
                    chunk_indices = semantic_index.japanese_keyword_index[keyword]
                    for chunk_idx in chunk_indices:
                        candidate_scores[chunk_idx] = (
                            candidate_scores.get(chunk_idx, 0) + 1.0
                        )

            # ビジネス用語検索
            business_terms = self.japanese_processor.extract_business_terms(
                expanded_query
            )
            for term in business_terms:
                if term in semantic_index.business_term_index:
                    chunk_indices = semantic_index.business_term_index[term]
                    for chunk_idx in chunk_indices:
                        candidate_scores[chunk_idx] = (
                            candidate_scores.get(chunk_idx, 0) + 2.0
                        )  # ビジネス用語は高重み

        # スコア正規化
        if candidate_scores:
            max_score = max(candidate_scores.values())
            for chunk_idx in candidate_scores:
                candidate_scores[chunk_idx] /= max_score

        # 結果をスコア順にソート
        sorted_results = sorted(
            candidate_scores.items(), key=lambda x: x[1], reverse=True
        )

        return sorted_results[:max_results]

    def search_by_semantic_category(
        self,
        category: str,
        semantic_index: SemanticSearchIndex,
        max_results: int = 10,
    ) -> list[int]:
        """セマンティックカテゴリによる検索.

        Args:
            category: 検索カテゴリ.
            semantic_index: セマンティック検索インデックス.
            max_results: 最大結果数.

        Returns:
            該当するチャンクインデックスのリスト.
        """
        if category in semantic_index.semantic_mappings:
            chunk_indices = semantic_index.semantic_mappings[category]
            return chunk_indices[:max_results]
        else:
            return []

    def get_semantic_statistics(
        self, semantic_index: SemanticSearchIndex
    ) -> dict[str, Any]:
        """セマンティックインデックス統計情報取得.

        Args:
            semantic_index: 統計情報を取得するセマンティックインデックス.

        Returns:
            統計情報辞書.
        """
        return {
            "total_text_segments": len(semantic_index.text_segments),
            "japanese_keywords_count": len(semantic_index.japanese_keyword_index),
            "business_terms_count": len(semantic_index.business_term_index),
            "semantic_categories": list(semantic_index.semantic_mappings.keys()),
            "avg_keywords_per_chunk": (
                sum(
                    len(indices)
                    for indices in semantic_index.japanese_keyword_index.values()
                )
                / max(len(semantic_index.japanese_keyword_index), 1)
            ),
            "avg_business_terms_per_chunk": (
                sum(
                    len(indices)
                    for indices in semantic_index.business_term_index.values()
                )
                / max(len(semantic_index.business_term_index), 1)
            ),
        }

    def optimize_semantic_index(
        self, semantic_index: SemanticSearchIndex
    ) -> SemanticSearchIndex:
        """セマンティックインデックス最適化.

        Args:
            semantic_index: 最適化対象のセマンティックインデックス.

        Returns:
            最適化されたセマンティックインデックス.
        """
        # 低頻度キーワードの除去
        min_frequency = self.semantic_config.get("min_term_frequency", 2)

        optimized_keyword_index = {
            keyword: indices
            for keyword, indices in semantic_index.japanese_keyword_index.items()
            if len(indices) >= min_frequency
        }

        semantic_index.japanese_keyword_index = optimized_keyword_index

        # 最大特徴数制限
        max_features = self.semantic_config.get("max_features", 10000)

        if len(semantic_index.japanese_keyword_index) > max_features:
            # 頻度順でソートして上位のみ保持
            sorted_keywords = sorted(
                semantic_index.japanese_keyword_index.items(),
                key=lambda x: len(x[1]),
                reverse=True,
            )

            semantic_index.japanese_keyword_index = dict(sorted_keywords[:max_features])

        logger.info("Semantic index optimized")
        return semantic_index
