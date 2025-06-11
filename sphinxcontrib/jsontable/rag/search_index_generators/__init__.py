"""Search index generators unified API and facade.

Provides a unified interface for all search index generation capabilities
with complete backward compatibility for the original SearchIndexGenerator API.
"""

import logging
import time
from typing import Any

from .base import ComprehensiveSearchIndex
from .faceted_index import FacetedIndexGenerator
from .hybrid_index import HybridIndexGenerator
from .japanese_processor import JapaneseQueryProcessor
from .semantic_index import SemanticIndexGenerator
from .storage import IndexStorageManager
from .vector_index import VectorIndexGenerator

logger = logging.getLogger(__name__)

__all__ = [
    "SearchIndexGenerator",
    "VectorIndexGenerator",
    "SemanticIndexGenerator", 
    "FacetedIndexGenerator",
    "HybridIndexGenerator",
    "IndexStorageManager",
    "JapaneseQueryProcessor",
]


class SearchIndexGenerator:
    """Unified search index generation facade.
    
    Orchestrates the creation of vector, semantic, faceted, and hybrid search
    indices with Japanese language optimization. Provides complete backward
    compatibility with the original API while leveraging modular architecture.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize search index generator with configuration.

        Args:
            config: Optional configuration dictionary for index parameters.
        """
        self.config = config or self._get_default_config()
        
        # Initialize specialized generators
        self.vector_generator = VectorIndexGenerator(self.config)
        self.semantic_generator = SemanticIndexGenerator(self.config)
        self.faceted_generator = FacetedIndexGenerator(self.config)
        self.hybrid_generator = HybridIndexGenerator(self.config)
        
        # Initialize utilities
        self.storage_manager = IndexStorageManager()
        self.japanese_processor = JapaneseQueryProcessor()

        # Setup index strategies for backward compatibility
        self.index_strategies = {
            "vector_similarity": self._setup_vector_strategy(),
            "semantic_search": self._setup_semantic_strategy(),
            "faceted_search": self._setup_faceted_strategy(),
            "hybrid_search": self._setup_hybrid_strategy(),
        }

        logger.info("SearchIndexGenerator initialized with modular architecture")

    def _get_default_config(self) -> dict[str, Any]:
        """Get default configuration for search index generation.

        Returns:
            Default configuration dictionary with optimized settings for Japanese search.
        """
        return {
            "vector_search": {
                "dimension": 1024,
                "index_type": "FlatIP",  # Inner Product for PLaMo
                "nprobe": 10,
                "search_k": 10,
            },
            "semantic_search": {
                "min_term_frequency": 2,
                "max_features": 10000,
                "japanese_tokenization": True,
            },
            "faceted_search": {
                "max_facet_values": 100,
                "enable_numerical_ranges": True,
                "enable_temporal_facets": True,
            },
            "hybrid_search": {
                "vector_weight": 0.7,
                "semantic_weight": 0.2,
                "facet_weight": 0.1,
                "rank_fusion_k": 10,
            },
        }

    def _setup_vector_strategy(self) -> dict[str, Any]:
        """ベクトル検索戦略設定"""
        return {
            "enabled": True,
            "use_faiss": getattr(self.vector_generator, "faiss_available", False),
            "fallback_available": True,
            "optimization_targets": ["speed", "accuracy"],
        }

    def _setup_semantic_strategy(self) -> dict[str, Any]:
        """セマンティック検索戦略設定"""
        return {
            "enabled": True,
            "japanese_specific": True,
            "business_term_enhancement": True,
            "query_expansion": True,
        }

    def _setup_faceted_strategy(self) -> dict[str, Any]:
        """ファセット検索戦略設定"""
        return {
            "enabled": True,
            "categorical_facets": True,
            "numerical_facets": True,
            "temporal_facets": True,
            "entity_facets": True,
        }

    def _setup_hybrid_strategy(self) -> dict[str, Any]:
        """ハイブリッド検索戦略設定"""
        return {
            "enabled": True,
            "rank_fusion": True,
            "weight_optimization": True,
            "adaptive_weighting": False,  # 将来の拡張
        }

    def generate_comprehensive_index(
        self,
        vector_chunks: list,
        basic_metadata: Any = None,
    ) -> ComprehensiveSearchIndex:
        """包括的検索インデックス生成 - 完全後方互換API.
        
        Args:
            vector_chunks: ベクトル化されたチャンクのリスト.
            basic_metadata: 基本メタデータ（オプション）.
            
        Returns:
            包括的検索インデックス.
        """
        start_time = time.time()

        logger.info(
            f"Generating comprehensive search index for {len(vector_chunks)} chunks"
        )

        search_index = ComprehensiveSearchIndex()
        search_index.total_chunks = len(vector_chunks)

        # 1. ベクトル類似度検索インデックス
        search_index.vector_index = self.vector_generator.generate(vector_chunks)

        # 2. セマンティック検索インデックス
        search_index.semantic_index = self.semantic_generator.generate(vector_chunks)

        # 3. ファセット検索インデックス
        search_index.facet_index = self.faceted_generator.generate(
            vector_chunks, basic_metadata
        )

        # 4. ハイブリッド検索インデックス
        search_index.hybrid_index = self.hybrid_generator.generate()

        # 統計情報更新
        generation_time = time.time() - start_time
        search_index.index_statistics = {
            "generation_time_seconds": generation_time,
            "vector_index_size": len(vector_chunks),
            "semantic_terms_indexed": len(
                search_index.semantic_index.japanese_keyword_index
            ),
            "facet_categories": len(search_index.facet_index.categorical_facets),
            "faiss_available": getattr(self.vector_generator, "faiss_available", False),
            "modular_architecture": True,  # 新アーキテクチャの識別子
        }

        logger.info(f"Comprehensive search index generated in {generation_time:.2f}s")

        return search_index

    def search_similar_vectors(
        self,
        query_embedding,
        search_index: ComprehensiveSearchIndex,
        k: int = 10,
    ) -> list[tuple[int, float]]:
        """ベクトル類似検索 - 完全後方互換API.
        
        Args:
            query_embedding: クエリベクトル.
            search_index: 包括的検索インデックス.
            k: 取得する類似ベクトル数.
            
        Returns:
            (インデックス, スコア)のタプルリスト.
        """
        if search_index.vector_index is None:
            return []

        return self.vector_generator.search_similar_vectors(
            query_embedding, search_index.vector_index, k
        )

    def save_search_index(
        self, search_index: ComprehensiveSearchIndex, output_path: str
    ) -> None:
        """検索インデックス保存 - 完全後方互換API.
        
        Args:
            search_index: 保存対象の包括的検索インデックス.
            output_path: 出力先パス.
        """
        self.storage_manager.save_search_index(search_index, output_path)

    @classmethod
    def load_search_index(cls, input_path: str) -> ComprehensiveSearchIndex:
        """検索インデックス読み込み - 完全後方互換API.
        
        Args:
            input_path: 入力パス.
            
        Returns:
            読み込まれた包括的検索インデックス.
        """
        storage_manager = IndexStorageManager()
        return storage_manager.load_search_index(input_path)

    def search_by_query(
        self,
        query: str,
        search_index: ComprehensiveSearchIndex,
        search_mode: str = "hybrid",
        max_results: int = 10,
        filters: dict[str, Any] | None = None,
    ) -> list[tuple[int, float]]:
        """統合クエリ検索機能（新機能）.
        
        Args:
            query: 検索クエリ.
            search_index: 包括的検索インデックス.
            search_mode: 検索モード ("vector", "semantic", "faceted", "hybrid").
            max_results: 最大結果数.
            filters: ファセットフィルタ（オプション）.
            
        Returns:
            検索結果のリスト.
        """
        if search_mode == "vector":
            # ベクトル検索のみ（クエリベクトル化が必要）
            logger.warning("Vector-only search requires query embedding")
            return []
            
        elif search_mode == "semantic":
            # セマンティック検索のみ
            if search_index.semantic_index:
                return self.semantic_generator.search_by_keywords(
                    query, search_index.semantic_index, max_results
                )
            return []
            
        elif search_mode == "faceted":
            # ファセット検索のみ
            if search_index.facet_index and filters:
                facet_results = self.faceted_generator.filter_by_facets(
                    search_index.facet_index, filters
                )
                return [(chunk_id, 1.0) for chunk_id in facet_results[:max_results]]
            return []
            
        elif search_mode == "hybrid":
            # ハイブリッド検索
            return self._perform_hybrid_search(
                query, search_index, max_results, filters
            )
            
        else:
            raise ValueError(f"Unknown search mode: {search_mode}")

    def _perform_hybrid_search(
        self,
        query: str,
        search_index: ComprehensiveSearchIndex,
        max_results: int,
        filters: dict[str, Any] | None,
    ) -> list[tuple[int, float]]:
        """ハイブリッド検索の実行.
        
        Args:
            query: 検索クエリ.
            search_index: 包括的検索インデックス.
            max_results: 最大結果数.
            filters: ファセットフィルタ.
            
        Returns:
            ハイブリッド検索結果.
        """
        # セマンティック検索結果
        semantic_results = []
        if search_index.semantic_index:
            semantic_results = self.semantic_generator.search_by_keywords(
                query, search_index.semantic_index, max_results
            )

        # ファセット検索結果
        facet_results = []
        if search_index.facet_index and filters:
            facet_results = self.faceted_generator.filter_by_facets(
                search_index.facet_index, filters
            )

        # ベクトル検索結果（空として処理）
        vector_results = []

        # ハイブリッド融合
        if search_index.hybrid_index:
            return self.hybrid_generator.fuse_search_results(
                vector_results,
                semantic_results,
                facet_results,
                search_index.hybrid_index,
                max_results,
            )

        # フォールバック: セマンティック結果のみ
        return semantic_results

    def get_comprehensive_statistics(
        self, search_index: ComprehensiveSearchIndex
    ) -> dict[str, Any]:
        """包括的統計情報取得（新機能）.
        
        Args:
            search_index: 統計情報を取得する包括的インデックス.
            
        Returns:
            統計情報辞書.
        """
        stats = {
            "index_creation_time": search_index.creation_time,
            "total_chunks": search_index.total_chunks,
            "generation_statistics": search_index.index_statistics,
        }

        # 各インデックスの統計情報
        if search_index.vector_index:
            stats["vector_statistics"] = self.vector_generator.get_vector_statistics(
                search_index.vector_index
            )

        if search_index.semantic_index:
            stats["semantic_statistics"] = self.semantic_generator.get_semantic_statistics(
                search_index.semantic_index
            )

        if search_index.facet_index:
            stats["facet_statistics"] = self.faceted_generator.get_facet_statistics(
                search_index.facet_index
            )

        if search_index.hybrid_index:
            stats["hybrid_statistics"] = self.hybrid_generator.get_hybrid_statistics(
                search_index.hybrid_index
            )

        return stats

    def optimize_index(
        self, search_index: ComprehensiveSearchIndex
    ) -> ComprehensiveSearchIndex:
        """インデックス最適化（新機能）.
        
        Args:
            search_index: 最適化対象のインデックス.
            
        Returns:
            最適化されたインデックス.
        """
        # 各専用ジェネレーターによる最適化
        if search_index.vector_index:
            search_index.vector_index = self.vector_generator.optimize_index(
                search_index.vector_index
            )

        if search_index.semantic_index:
            search_index.semantic_index = self.semantic_generator.optimize_semantic_index(
                search_index.semantic_index
            )

        logger.info("Comprehensive search index optimized")
        return search_index
