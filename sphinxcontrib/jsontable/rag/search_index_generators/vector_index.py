"""Vector search index generation with FAISS integration.

Specialized generator for vector-based similarity search indices with
FAISS optimization and fallback implementations for comprehensive
vector search capabilities.
"""

import logging
from typing import Any

import numpy as np

from .base import BaseIndexGenerator, VectorIndex

# FAISS integration (optional)
try:
    import faiss

    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logging.warning(
        "FAISS not available. Vector search will use fallback implementation."
    )

logger = logging.getLogger(__name__)

__all__ = ["VectorIndexGenerator"]


class VectorIndexGenerator(BaseIndexGenerator):
    """Vector search index generator with FAISS integration.

    Specialized generator for creating vector-based similarity search indices
    with FAISS optimization and fallback implementations.
    """

    def __init__(self, config: dict[str, Any]):
        """Initialize vector index generator.

        Args:
            config: Configuration dictionary for vector index generation.
        """
        super().__init__(config)
        self.faiss_available = FAISS_AVAILABLE
        self.vector_config = config.get("vector_search", {})

    def generate(self, vector_chunks: list) -> VectorIndex:
        """ベクトルインデックス生成.

        Args:
            vector_chunks: ベクトル化されたチャンクのリスト.

        Returns:
            生成されたベクトルインデックス.
        """
        if not self.validate_input(vector_chunks):
            raise ValueError("Invalid vector chunks provided")

        dimension = self.vector_config.get("dimension", 1024)
        embeddings = np.array([chunk.embedding for chunk in vector_chunks])

        vector_index = VectorIndex(
            dimension=dimension,
            chunk_metadata=self._build_chunk_metadata(vector_chunks),
            search_parameters=self._build_search_parameters(),
        )

        if self.faiss_available:
            vector_index = self._build_faiss_index(vector_index, embeddings)
        else:
            vector_index = self._build_fallback_index(vector_index, embeddings)

        logger.info(f"Vector index built with {len(vector_chunks)} vectors")
        return vector_index

    def _build_chunk_metadata(self, vector_chunks: list) -> list[dict[str, Any]]:
        """チャンクメタデータ構築.

        Args:
            vector_chunks: ベクトルチャンクのリスト.

        Returns:
            チャンクメタデータのリスト.
        """
        return [
            {
                "chunk_id": chunk.chunk_id,
                "content": chunk.original_chunk.content,
                "search_boost": getattr(chunk, "search_boost", 1.0),
                "japanese_enhancement": getattr(chunk, "japanese_enhancement", {}),
            }
            for chunk in vector_chunks
        ]

    def _build_search_parameters(self) -> dict[str, Any]:
        """検索パラメータ構築.

        Returns:
            検索パラメータ辞書.
        """
        return {
            "k": self.vector_config.get("search_k", 10),
            "threshold": 0.7,
            "japanese_boost": 1.2,
            "nprobe": self.vector_config.get("nprobe", 10),
        }

    def _build_faiss_index(
        self, vector_index: VectorIndex, embeddings: np.ndarray
    ) -> VectorIndex:
        """FAISS使用によるベクトルインデックス構築.

        Args:
            vector_index: ベースとなるベクトルインデックス.
            embeddings: 埋め込みベクトル配列.

        Returns:
            FAISS統合されたベクトルインデックス.
        """
        dimension = vector_index.dimension
        index_type = self.vector_config.get("index_type", "FlatIP")

        # PLaMo用内積インデックス
        if index_type == "FlatIP":
            index = faiss.IndexFlatIP(dimension)
        elif index_type == "IVFFlat":
            # より高速な検索のためのIVFインデックス
            nlist = min(100, len(embeddings) // 10)  # クラスタ数調整
            quantizer = faiss.IndexFlatIP(dimension)
            index = faiss.IndexIVFFlat(quantizer, dimension, nlist)

            # 訓練が必要
            if len(embeddings) >= nlist:
                index.train(embeddings.astype("float32"))
        else:
            # デフォルトはFlatIP
            index = faiss.IndexFlatIP(dimension)

        index.add(embeddings.astype("float32"))

        vector_index.faiss_index = index
        vector_index.index_type = f"faiss_{index_type.lower()}"

        return vector_index

    def _build_fallback_index(
        self, vector_index: VectorIndex, embeddings: np.ndarray
    ) -> VectorIndex:
        """フォールバック実装によるベクトルインデックス構築.

        Args:
            vector_index: ベースとなるベクトルインデックス.
            embeddings: 埋め込みベクトル配列.

        Returns:
            フォールバック実装されたベクトルインデックス.
        """
        vector_index.fallback_embeddings = embeddings
        vector_index.index_type = "fallback_cosine"

        return vector_index

    def search_similar_vectors(
        self,
        query_embedding: np.ndarray,
        vector_index: VectorIndex,
        k: int = 10,
    ) -> list[tuple[int, float]]:
        """ベクトル類似検索.

        Args:
            query_embedding: クエリベクトル.
            vector_index: 検索対象のベクトルインデックス.
            k: 取得する類似ベクトル数.

        Returns:
            (インデックス, スコア)のタプルリスト.
        """
        if self.faiss_available and vector_index.faiss_index is not None:
            return self._search_with_faiss(query_embedding, vector_index, k)
        else:
            return self._search_with_fallback(query_embedding, vector_index, k)

    def _search_with_faiss(
        self,
        query_embedding: np.ndarray,
        vector_index: VectorIndex,
        k: int,
    ) -> list[tuple[int, float]]:
        """FAISS使用による類似検索.

        Args:
            query_embedding: クエリベクトル.
            vector_index: 検索対象のベクトルインデックス.
            k: 取得する類似ベクトル数.

        Returns:
            (インデックス, スコア)のタプルリスト.
        """
        # FAISS検索
        query_vector = query_embedding.reshape(1, -1).astype("float32")
        scores, indices = vector_index.faiss_index.search(query_vector, k)

        results = [
            (int(indices[0][i]), float(scores[0][i]))
            for i in range(len(indices[0]))
            if indices[0][i] != -1
        ]

        return results

    def _search_with_fallback(
        self,
        query_embedding: np.ndarray,
        vector_index: VectorIndex,
        k: int,
    ) -> list[tuple[int, float]]:
        """フォールバック実装による類似検索.

        Args:
            query_embedding: クエリベクトル.
            vector_index: 検索対象のベクトルインデックス.
            k: 取得する類似ベクトル数.

        Returns:
            (インデックス, スコア)のタプルリスト.
        """
        # フォールバック検索（コサイン類似度）
        embeddings = vector_index.fallback_embeddings

        # コサイン類似度計算
        if embeddings is not None and query_embedding is not None:
            similarities = np.dot(embeddings, query_embedding) / (
                np.linalg.norm(embeddings, axis=1) * np.linalg.norm(query_embedding)
            )
        else:
            similarities = np.array([])

        # 上位k件取得
        top_indices = np.argsort(similarities)[::-1][:k]
        results = [(int(idx), float(similarities[idx])) for idx in top_indices]

        return results

    def get_vector_statistics(self, vector_index: VectorIndex) -> dict[str, Any]:
        """ベクトルインデックス統計情報取得.

        Args:
            vector_index: 統計情報を取得するベクトルインデックス.

        Returns:
            統計情報辞書.
        """
        stats = {
            "dimension": vector_index.dimension,
            "index_type": vector_index.index_type,
            "total_vectors": len(vector_index.chunk_metadata),
            "faiss_available": self.faiss_available,
            "search_parameters": vector_index.search_parameters,
        }

        if vector_index.faiss_index is not None:
            stats["faiss_total_vectors"] = vector_index.faiss_index.ntotal
            stats["faiss_index_trained"] = getattr(
                vector_index.faiss_index, "is_trained", True
            )

        if vector_index.fallback_embeddings is not None:
            stats["fallback_shape"] = vector_index.fallback_embeddings.shape
            stats["fallback_dtype"] = str(vector_index.fallback_embeddings.dtype)

        return stats

    def optimize_index(self, vector_index: VectorIndex) -> VectorIndex:
        """ベクトルインデックス最適化.

        Args:
            vector_index: 最適化対象のベクトルインデックス.

        Returns:
            最適化されたベクトルインデックス.
        """
        if not self.faiss_available or vector_index.faiss_index is None:
            return vector_index

        # インデックスタイプに応じた最適化
        if hasattr(vector_index.faiss_index, "nprobe"):
            # IVFインデックスの場合
            optimal_nprobe = min(
                vector_index.faiss_index.nlist // 4,
                self.vector_config.get("nprobe", 10),
            )
            vector_index.faiss_index.nprobe = optimal_nprobe
            vector_index.search_parameters["nprobe"] = optimal_nprobe

        logger.info("Vector index optimized")
        return vector_index
