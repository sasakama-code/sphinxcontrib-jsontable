"""Hybrid search index generation with score fusion capabilities.

Specialized generator for hybrid search indices that combine vector similarity,
semantic keyword matching, and faceted filtering with advanced score fusion algorithms.
"""

import logging
from typing import Any

from .base import BaseIndexGenerator, HybridSearchIndex

logger = logging.getLogger(__name__)

__all__ = ["HybridIndexGenerator"]


class HybridIndexGenerator(BaseIndexGenerator):
    """Hybrid search index generator with score fusion.
    
    Specialized generator for creating hybrid search indices that combine
    multiple search modalities with configurable score fusion algorithms.
    """

    def __init__(self, config: dict[str, Any]):
        """Initialize hybrid index generator.
        
        Args:
            config: Configuration dictionary for hybrid index generation.
        """
        super().__init__(config)
        self.hybrid_config = config.get("hybrid_search", {})

    def generate(self) -> HybridSearchIndex:
        """ハイブリッド検索インデックス生成.
        
        Returns:
            生成されたハイブリッド検索インデックス.
        """
        hybrid_index = HybridSearchIndex(
            vector_weight=self.hybrid_config.get("vector_weight", 0.7),
            semantic_weight=self.hybrid_config.get("semantic_weight", 0.2),
            facet_weight=self.hybrid_config.get("facet_weight", 0.1),
            fusion_algorithm=self.hybrid_config.get("fusion_algorithm", "rank_fusion"),
        )

        logger.info(f"Hybrid index generated with {hybrid_index.fusion_algorithm} algorithm")
        return hybrid_index

    def fuse_search_results(
        self,
        vector_results: list[tuple[int, float]],
        semantic_results: list[tuple[int, float]],
        facet_results: list[int],
        hybrid_index: HybridSearchIndex,
        max_results: int = 10,
    ) -> list[tuple[int, float]]:
        """検索結果の融合処理.
        
        Args:
            vector_results: ベクトル検索結果 (chunk_id, score).
            semantic_results: セマンティック検索結果 (chunk_id, score).
            facet_results: ファセット検索結果 (chunk_id).
            hybrid_index: ハイブリッド検索インデックス.
            max_results: 最大結果数.
            
        Returns:
            融合された検索結果 (chunk_id, fused_score).
        """
        if hybrid_index.fusion_algorithm == "rank_fusion":
            return self._rank_fusion(
                vector_results, semantic_results, facet_results, hybrid_index, max_results
            )
        elif hybrid_index.fusion_algorithm == "score_fusion":
            return self._score_fusion(
                vector_results, semantic_results, facet_results, hybrid_index, max_results
            )
        elif hybrid_index.fusion_algorithm == "weighted_sum":
            return self._weighted_sum_fusion(
                vector_results, semantic_results, facet_results, hybrid_index, max_results
            )
        else:
            # デフォルトはrank_fusion
            return self._rank_fusion(
                vector_results, semantic_results, facet_results, hybrid_index, max_results
            )

    def _rank_fusion(
        self,
        vector_results: list[tuple[int, float]],
        semantic_results: list[tuple[int, float]],
        facet_results: list[int],
        hybrid_index: HybridSearchIndex,
        max_results: int,
    ) -> list[tuple[int, float]]:
        """ランク融合アルゴリズム.
        
        Args:
            vector_results: ベクトル検索結果.
            semantic_results: セマンティック検索結果.
            facet_results: ファセット検索結果.
            hybrid_index: ハイブリッド検索インデックス.
            max_results: 最大結果数.
            
        Returns:
            ランク融合された検索結果.
        """
        k = self.hybrid_config.get("rank_fusion_k", 10)
        
        # 各結果のランクを計算
        rank_scores: dict[int, float] = {}

        # ベクトル検索のランクスコア
        for rank, (chunk_id, score) in enumerate(vector_results):
            rank_scores[chunk_id] = rank_scores.get(chunk_id, 0) + (
                hybrid_index.vector_weight / (k + rank + 1)
            )

        # セマンティック検索のランクスコア
        for rank, (chunk_id, score) in enumerate(semantic_results):
            rank_scores[chunk_id] = rank_scores.get(chunk_id, 0) + (
                hybrid_index.semantic_weight / (k + rank + 1)
            )

        # ファセット検索のブーストスコア
        for chunk_id in facet_results:
            rank_scores[chunk_id] = rank_scores.get(chunk_id, 0) + hybrid_index.facet_weight

        # ランクスコア順でソート
        sorted_results = sorted(
            rank_scores.items(), key=lambda x: x[1], reverse=True
        )

        return sorted_results[:max_results]

    def _score_fusion(
        self,
        vector_results: list[tuple[int, float]],
        semantic_results: list[tuple[int, float]],
        facet_results: list[int],
        hybrid_index: HybridSearchIndex,
        max_results: int,
    ) -> list[tuple[int, float]]:
        """スコア融合アルゴリズム.
        
        Args:
            vector_results: ベクトル検索結果.
            semantic_results: セマンティック検索結果.
            facet_results: ファセット検索結果.
            hybrid_index: ハイブリッド検索インデックス.
            max_results: 最大結果数.
            
        Returns:
            スコア融合された検索結果.
        """
        # 正規化されたスコアを計算
        fused_scores: dict[int, float] = {}

        # ベクトル検索スコアの正規化と重み適用
        vector_scores = dict(vector_results)
        if vector_scores:
            max_vector_score = max(vector_scores.values())
            for chunk_id, score in vector_scores.items():
                normalized_score = score / max_vector_score
                fused_scores[chunk_id] = fused_scores.get(chunk_id, 0) + (
                    hybrid_index.vector_weight * normalized_score
                )

        # セマンティック検索スコアの正規化と重み適用
        semantic_scores = dict(semantic_results)
        if semantic_scores:
            max_semantic_score = max(semantic_scores.values())
            for chunk_id, score in semantic_scores.items():
                normalized_score = score / max_semantic_score
                fused_scores[chunk_id] = fused_scores.get(chunk_id, 0) + (
                    hybrid_index.semantic_weight * normalized_score
                )

        # ファセット検索のブーストスコア
        for chunk_id in facet_results:
            fused_scores[chunk_id] = fused_scores.get(chunk_id, 0) + hybrid_index.facet_weight

        # 融合スコア順でソート
        sorted_results = sorted(
            fused_scores.items(), key=lambda x: x[1], reverse=True
        )

        return sorted_results[:max_results]

    def _weighted_sum_fusion(
        self,
        vector_results: list[tuple[int, float]],
        semantic_results: list[tuple[int, float]],
        facet_results: list[int],
        hybrid_index: HybridSearchIndex,
        max_results: int,
    ) -> list[tuple[int, float]]:
        """重み付き和融合アルゴリズム.
        
        Args:
            vector_results: ベクトル検索結果.
            semantic_results: セマンティック検索結果.
            facet_results: ファセット検索結果.
            hybrid_index: ハイブリッド検索インデックス.
            max_results: 最大結果数.
            
        Returns:
            重み付き和融合された検索結果.
        """
        weighted_scores: dict[int, float] = {}

        # ベクトル検索の重み付きスコア
        for chunk_id, score in vector_results:
            weighted_scores[chunk_id] = weighted_scores.get(chunk_id, 0) + (
                hybrid_index.vector_weight * score
            )

        # セマンティック検索の重み付きスコア
        for chunk_id, score in semantic_results:
            weighted_scores[chunk_id] = weighted_scores.get(chunk_id, 0) + (
                hybrid_index.semantic_weight * score
            )

        # ファセット検索のブーストスコア
        for chunk_id in facet_results:
            weighted_scores[chunk_id] = weighted_scores.get(chunk_id, 0) + hybrid_index.facet_weight

        # 重み付きスコア順でソート
        sorted_results = sorted(
            weighted_scores.items(), key=lambda x: x[1], reverse=True
        )

        return sorted_results[:max_results]

    def adaptive_weight_adjustment(
        self,
        query_features: dict[str, Any],
        hybrid_index: HybridSearchIndex,
    ) -> HybridSearchIndex:
        """クエリ特徴に基づく適応的重み調整.
        
        Args:
            query_features: クエリの特徴辞書.
            hybrid_index: 調整対象のハイブリッド検索インデックス.
            
        Returns:
            調整されたハイブリッド検索インデックス.
        """
        # クエリタイプに基づく重み調整
        if query_features.get("query_type") == "business":
            # ビジネスクエリの場合、セマンティック検索の重みを増加
            hybrid_index.semantic_weight += 0.1
            hybrid_index.vector_weight -= 0.05
            hybrid_index.facet_weight -= 0.05
        
        elif query_features.get("has_numbers", False):
            # 数値を含むクエリの場合、ファセット検索の重みを増加
            hybrid_index.facet_weight += 0.1
            hybrid_index.vector_weight -= 0.05
            hybrid_index.semantic_weight -= 0.05

        # 重みの正規化
        total_weight = (
            hybrid_index.vector_weight + 
            hybrid_index.semantic_weight + 
            hybrid_index.facet_weight
        )
        
        if total_weight > 0:
            hybrid_index.vector_weight /= total_weight
            hybrid_index.semantic_weight /= total_weight
            hybrid_index.facet_weight /= total_weight

        return hybrid_index

    def evaluate_fusion_quality(
        self,
        fused_results: list[tuple[int, float]],
        ground_truth: list[int] | None = None,
    ) -> dict[str, float]:
        """融合結果の品質評価.
        
        Args:
            fused_results: 融合された検索結果.
            ground_truth: 正解データ（オプション）.
            
        Returns:
            評価メトリクス辞書.
        """
        metrics = {
            "result_count": len(fused_results),
            "score_distribution_std": 0.0,
            "score_range": 0.0,
        }

        if fused_results:
            scores = [score for _, score in fused_results]
            
            # スコア分布の標準偏差
            if len(scores) > 1:
                mean_score = sum(scores) / len(scores)
                variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
                metrics["score_distribution_std"] = variance ** 0.5

            # スコア範囲
            metrics["score_range"] = max(scores) - min(scores)

        # 正解データがある場合の追加評価
        if ground_truth is not None:
            retrieved_ids = [chunk_id for chunk_id, _ in fused_results]
            
            # 精度 (Precision)
            relevant_retrieved = len(set(retrieved_ids) & set(ground_truth))
            metrics["precision"] = (
                relevant_retrieved / len(retrieved_ids) if retrieved_ids else 0.0
            )
            
            # 再現率 (Recall)
            metrics["recall"] = (
                relevant_retrieved / len(ground_truth) if ground_truth else 0.0
            )
            
            # F1スコア
            precision = metrics["precision"]
            recall = metrics["recall"]
            metrics["f1_score"] = (
                2 * precision * recall / (precision + recall)
                if (precision + recall) > 0
                else 0.0
            )

        return metrics

    def optimize_fusion_parameters(
        self,
        historical_queries: list[dict[str, Any]],
        hybrid_index: HybridSearchIndex,
    ) -> HybridSearchIndex:
        """履歴データに基づく融合パラメータ最適化.
        
        Args:
            historical_queries: 過去のクエリデータ.
            hybrid_index: 最適化対象のハイブリッド検索インデックス.
            
        Returns:
            最適化されたハイブリッド検索インデックス.
        """
        if not historical_queries:
            return hybrid_index

        # クエリタイプ別の最適重みを計算
        business_queries = [
            q for q in historical_queries 
            if q.get("query_features", {}).get("query_type") == "business"
        ]
        
        numerical_queries = [
            q for q in historical_queries 
            if q.get("query_features", {}).get("has_numbers", False)
        ]

        # ビジネスクエリが多い場合
        if len(business_queries) / len(historical_queries) > 0.5:
            hybrid_index.semantic_weight = min(0.4, hybrid_index.semantic_weight + 0.1)
            hybrid_index.vector_weight = max(0.5, hybrid_index.vector_weight - 0.1)

        # 数値クエリが多い場合
        if len(numerical_queries) / len(historical_queries) > 0.3:
            hybrid_index.facet_weight = min(0.3, hybrid_index.facet_weight + 0.1)
            hybrid_index.vector_weight = max(0.5, hybrid_index.vector_weight - 0.1)

        # 重みの正規化
        total_weight = (
            hybrid_index.vector_weight + 
            hybrid_index.semantic_weight + 
            hybrid_index.facet_weight
        )
        
        if total_weight > 0:
            hybrid_index.vector_weight /= total_weight
            hybrid_index.semantic_weight /= total_weight
            hybrid_index.facet_weight /= total_weight

        logger.info("Hybrid fusion parameters optimized based on historical data")
        return hybrid_index

    def get_hybrid_statistics(
        self, hybrid_index: HybridSearchIndex
    ) -> dict[str, Any]:
        """ハイブリッドインデックス統計情報取得.
        
        Args:
            hybrid_index: 統計情報を取得するハイブリッドインデックス.
            
        Returns:
            統計情報辞書.
        """
        return {
            "vector_weight": hybrid_index.vector_weight,
            "semantic_weight": hybrid_index.semantic_weight,
            "facet_weight": hybrid_index.facet_weight,
            "fusion_algorithm": hybrid_index.fusion_algorithm,
            "total_weight": (
                hybrid_index.vector_weight + 
                hybrid_index.semantic_weight + 
                hybrid_index.facet_weight
            ),
            "weight_distribution": {
                "vector_percentage": round(hybrid_index.vector_weight * 100, 1),
                "semantic_percentage": round(hybrid_index.semantic_weight * 100, 1),
                "facet_percentage": round(hybrid_index.facet_weight * 100, 1),
            },
        }
