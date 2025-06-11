"""Search index storage and persistence management.

Handles saving and loading of comprehensive search indices with support
for multiple formats including FAISS, JSON, and NumPy arrays.
"""

import json
import logging
from pathlib import Path
from typing import Any

import numpy as np

from .base import (
    ComprehensiveSearchIndex,
    FacetedSearchIndex,
    HybridSearchIndex,
    SemanticSearchIndex,
    VectorIndex,
)

# FAISS integration (optional)
try:
    import faiss

    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

logger = logging.getLogger(__name__)

__all__ = ["IndexStorageManager"]


class IndexStorageManager:
    """Index storage and persistence manager.
    
    Handles saving and loading of comprehensive search indices with support
    for multiple formats and fallback implementations.
    """

    def __init__(self):
        """Initialize storage manager."""
        self.faiss_available = FAISS_AVAILABLE

    def save_search_index(
        self, search_index: ComprehensiveSearchIndex, output_path: str
    ) -> None:
        """検索インデックス保存.
        
        Args:
            search_index: 保存対象の包括的検索インデックス.
            output_path: 出力先パス.
        """
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)

        # FAISSインデックス保存
        if (
            self.faiss_available
            and search_index.vector_index
            and search_index.vector_index.faiss_index
        ):
            faiss_path = output_dir / "vector_index.faiss"
            faiss.write_index(search_index.vector_index.faiss_index, str(faiss_path))

        # その他のインデックス情報をJSON保存
        index_data = self._serialize_index_data(search_index)

        # フォールバック埋め込み保存
        if (
            search_index.vector_index
            and search_index.vector_index.fallback_embeddings is not None
        ):
            embeddings_path = output_dir / "fallback_embeddings.npy"
            np.save(embeddings_path, search_index.vector_index.fallback_embeddings)

        # メタデータJSON保存
        metadata_path = output_dir / "search_index_metadata.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)

        logger.info(f"Search index saved to {output_path}")

    def load_search_index(self, input_path: str) -> ComprehensiveSearchIndex:
        """検索インデックス読み込み.
        
        Args:
            input_path: 入力パス.
            
        Returns:
            読み込まれた包括的検索インデックス.
        """
        input_dir = Path(input_path)

        # メタデータ読み込み
        metadata_path = input_dir / "search_index_metadata.json"
        with open(metadata_path, encoding="utf-8") as f:
            index_data = json.load(f)

        # 検索インデックス再構築
        search_index = self._deserialize_index_data(index_data)

        # FAISSインデックス読み込み
        faiss_path = input_dir / "vector_index.faiss"
        if self.faiss_available and faiss_path.exists() and search_index.vector_index:
            search_index.vector_index.faiss_index = faiss.read_index(str(faiss_path))

        # フォールバック埋め込み読み込み
        embeddings_path = input_dir / "fallback_embeddings.npy"
        if embeddings_path.exists() and search_index.vector_index:
            search_index.vector_index.fallback_embeddings = np.load(embeddings_path)

        logger.info(f"Search index loaded from {input_path}")

        return search_index

    def _serialize_index_data(
        self, search_index: ComprehensiveSearchIndex
    ) -> dict[str, Any]:
        """インデックスデータのシリアライゼーション.
        
        Args:
            search_index: シリアライズ対象のインデックス.
            
        Returns:
            シリアライズされたデータ辞書.
        """
        return {
            "creation_time": search_index.creation_time,
            "total_chunks": search_index.total_chunks,
            "index_statistics": search_index.index_statistics,
            "vector_index_metadata": self._serialize_vector_index(
                search_index.vector_index
            ),
            "semantic_index": self._serialize_semantic_index(
                search_index.semantic_index
            ),
            "facet_index": self._serialize_facet_index(search_index.facet_index),
            "hybrid_index": self._serialize_hybrid_index(search_index.hybrid_index),
        }

    def _serialize_vector_index(self, vector_index: VectorIndex | None) -> dict[str, Any]:
        """ベクトルインデックスのシリアライゼーション."""
        if vector_index is None:
            return {}

        return {
            "chunk_metadata": vector_index.chunk_metadata,
            "search_parameters": vector_index.search_parameters,
            "dimension": vector_index.dimension,
            "index_type": vector_index.index_type,
        }

    def _serialize_semantic_index(
        self, semantic_index: SemanticSearchIndex | None
    ) -> dict[str, Any]:
        """セマンティックインデックスのシリアライゼーション."""
        if semantic_index is None:
            return {}

        return {
            "text_segments": semantic_index.text_segments,
            "japanese_keyword_index": semantic_index.japanese_keyword_index,
            "business_term_index": semantic_index.business_term_index,
            "semantic_mappings": semantic_index.semantic_mappings,
        }

    def _serialize_facet_index(
        self, facet_index: FacetedSearchIndex | None
    ) -> dict[str, Any]:
        """ファセットインデックスのシリアライゼーション."""
        if facet_index is None:
            return {}

        return {
            "categorical_facets": facet_index.categorical_facets,
            "numerical_facets": facet_index.numerical_facets,
            "temporal_facets": facet_index.temporal_facets,
            "entity_facets": facet_index.entity_facets,
        }

    def _serialize_hybrid_index(
        self, hybrid_index: HybridSearchIndex | None
    ) -> dict[str, Any]:
        """ハイブリッドインデックスのシリアライゼーション."""
        if hybrid_index is None:
            return {}

        return {
            "vector_weight": hybrid_index.vector_weight,
            "semantic_weight": hybrid_index.semantic_weight,
            "facet_weight": hybrid_index.facet_weight,
            "fusion_algorithm": hybrid_index.fusion_algorithm,
        }

    def _deserialize_index_data(self, index_data: dict[str, Any]) -> ComprehensiveSearchIndex:
        """インデックスデータのデシリアライゼーション.
        
        Args:
            index_data: デシリアライズ対象のデータ辞書.
            
        Returns:
            復元された包括的検索インデックス.
        """
        search_index = ComprehensiveSearchIndex(
            creation_time=index_data["creation_time"],
            total_chunks=index_data["total_chunks"],
            index_statistics=index_data["index_statistics"],
        )

        # ベクトルインデックス復元
        vector_metadata = index_data["vector_index_metadata"]
        if vector_metadata:
            search_index.vector_index = VectorIndex(
                chunk_metadata=vector_metadata["chunk_metadata"],
                search_parameters=vector_metadata["search_parameters"],
                dimension=vector_metadata["dimension"],
                index_type=vector_metadata["index_type"],
            )

        # セマンティックインデックス復元
        semantic_data = index_data["semantic_index"]
        if semantic_data:
            search_index.semantic_index = SemanticSearchIndex(
                text_segments=semantic_data["text_segments"],
                japanese_keyword_index=semantic_data["japanese_keyword_index"],
                business_term_index=semantic_data["business_term_index"],
                semantic_mappings=semantic_data["semantic_mappings"],
            )

        # ファセットインデックス復元
        facet_data = index_data["facet_index"]
        if facet_data:
            search_index.facet_index = FacetedSearchIndex(
                categorical_facets=facet_data["categorical_facets"],
                numerical_facets=facet_data["numerical_facets"],
                temporal_facets=facet_data["temporal_facets"],
                entity_facets=facet_data["entity_facets"],
            )

        # ハイブリッドインデックス復元
        hybrid_data = index_data["hybrid_index"]
        if hybrid_data:
            search_index.hybrid_index = HybridSearchIndex(
                vector_weight=hybrid_data["vector_weight"],
                semantic_weight=hybrid_data["semantic_weight"],
                facet_weight=hybrid_data["facet_weight"],
                fusion_algorithm=hybrid_data["fusion_algorithm"],
            )

        return search_index
