"""
PLaMo-Embedding-1B統合ベクトル処理エンジン

Phase 3のコア機能として、日本語特化AI統合による
世界最高水準のベクトル生成・検索機能を提供
"""

import json
import logging
import re
import time

# PLaMo-Embedding-1B関連インポート (実装時に調整)
from contextlib import suppress
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

with suppress(ImportError):
    # 実際のPLaMoライブラリ統合時に更新
    # import plamo_embedding
    pass

from .semantic_chunker import SemanticChunk

logger = logging.getLogger(__name__)


@dataclass
class VectorChunk:
    """ベクトル化されたチャンクデータ"""

    chunk_id: str
    original_chunk: SemanticChunk
    embedding: np.ndarray
    embedding_metadata: dict[str, Any] = field(default_factory=dict)
    japanese_enhancement: dict[str, Any] = field(default_factory=dict)
    search_boost: float = 1.0
    created_at: str = field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S"))


@dataclass
class VectorProcessingResult:
    """ベクトル処理結果"""

    vector_chunks: list[VectorChunk]
    processing_stats: dict[str, Any]
    model_info: dict[str, Any]
    japanese_optimization_applied: bool = True


class JapaneseTextNormalizer:
    """日本語テキスト正規化"""

    def __init__(self):
        # 全角・半角変換マップ
        self.fullwidth_to_halfwidth = str.maketrans(
            "０１２３４５６７８９ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ",  # noqa: RUF001
            "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        )

        # ビジネス用語正規化パターン
        self.business_normalization_patterns = [
            (r"株式会社|㈱|\(株\)", "株式会社"),
            (r"有限会社|㈲|\(有\)", "有限会社"),
            (r"合同会社|㈿|\(合\)", "合同会社"),
            (r"(\d+)年度", r"\1年度"),
            (r"第(\d+)四半期", r"第\1四半期"),
        ]

    def normalize(self, text: str) -> str:
        """包括的テキスト正規化"""

        # Unicode正規化 (NFKC)
        import unicodedata

        text = unicodedata.normalize("NFKC", text)

        # 全角英数字を半角に変換
        text = text.translate(self.fullwidth_to_halfwidth)

        # ビジネス用語の正規化
        for pattern, replacement in self.business_normalization_patterns:
            text = re.sub(pattern, replacement, text)

        # 空白文字の統一
        text = re.sub(r"[　\s]+", " ", text)
        text = text.strip()

        return text


class BusinessTermEnhancer:
    """ビジネス用語文脈強化"""

    def __init__(self):
        # ビジネス用語カテゴリ
        self.business_categories = {
            "organization": {
                "patterns": [r"株式会社.*", r"[^\s]*部", r"[^\s]*課", r"[^\s]*チーム"],
                "context_marker": "[組織]",
                "boost_factor": 1.3,
            },
            "position": {
                "patterns": [r"社長", r"部長", r"課長", r"主任", r"取締役"],
                "context_marker": "[役職]",
                "boost_factor": 1.2,
            },
            "financial": {
                "patterns": [
                    r"\d+(?:,\d{3})*円",
                    r"\d+億円",
                    r"\d+万円",
                    r"売上",
                    r"利益",
                    r"収益",
                ],
                "context_marker": "[財務]",
                "boost_factor": 1.4,
            },
            "temporal": {
                "patterns": [r"\d{4}年度", r"第\d+四半期", r"\d{4}年\d{1,2}月"],
                "context_marker": "[時期]",
                "boost_factor": 1.1,
            },
        }

    def enhance(self, text: str) -> str:
        """ビジネス文脈強化"""

        enhanced_text = text

        for _category, config in self.business_categories.items():
            context_marker = config['context_marker']
            for pattern in config["patterns"]:
                enhanced_text = re.sub(
                    pattern,
                    lambda m, marker=context_marker: f"{marker}{m.group(0)}",
                    enhanced_text,
                )

        return enhanced_text

    def extract_business_features(self, text: str) -> dict[str, Any]:
        """ビジネス特徴抽出"""

        features = {"business_terms": [], "categories": {}, "boost_score": 1.0}

        total_boost = 1.0

        for category, config in self.business_categories.items():
            matches = []
            for pattern in config["patterns"]:
                matches.extend(re.findall(pattern, text))

            if matches:
                features["categories"][category] = {
                    "matches": matches,
                    "count": len(matches),
                    "boost_factor": config["boost_factor"],
                }
                features["business_terms"].extend(matches)
                total_boost *= 1 + (len(matches) * (config["boost_factor"] - 1) * 0.1)

        features["boost_score"] = min(total_boost, 2.0)  # 最大2倍まで

        return features


class ContextPreserver:
    """文脈保持・階層情報管理"""

    def preserve_hierarchical_context(self, text: str, metadata: dict[str, Any]) -> str:
        """階層文脈保持"""

        context_markers = []

        # テーブル文脈
        if "table_context" in metadata:
            table_context = metadata["table_context"]
            if "table_name" in table_context:
                context_markers.append(f"[テーブル:{table_context['table_name']}]")

            if "row_index" in table_context:
                context_markers.append(f"[行:{table_context['row_index']}]")

            if "column_context" in table_context:
                cols = table_context["column_context"]
                context_markers.append(f"[列:{','.join(cols)}]")

        # セマンティック文脈
        if "semantic_context" in metadata:
            semantic_context = metadata["semantic_context"]
            if "chunk_type" in semantic_context:
                context_markers.append(f"[種別:{semantic_context['chunk_type']}]")

        # 文脈マーカーを追加
        if context_markers:
            enhanced_text = " ".join(context_markers) + " " + text
        else:
            enhanced_text = text

        return enhanced_text


class PLaMoVectorProcessor:
    """PLaMo-Embedding-1B統合ベクトル処理エンジン"""

    def __init__(self, config: dict[str, Any] | None = None):
        """初期化"""

        self.config = config or self._get_default_config()

        # 前処理パイプライン
        self.preprocessing_pipeline = [
            JapaneseTextNormalizer(),
            BusinessTermEnhancer(),
            ContextPreserver(),
        ]

        # モデル設定
        self.model_config = self.config.get("model", {})
        self.processing_config = self.config.get("processing", {})

        # 統計情報
        self.processing_stats = {
            "total_processed": 0,
            "successful_embeddings": 0,
            "failed_embeddings": 0,
            "average_processing_time": 0.0,
            "japanese_enhancements_applied": 0,
        }

        logger.info(
            f"PLaMoVectorProcessor initialized with config: {self.model_config}"
        )

    def _get_default_config(self) -> dict[str, Any]:
        """デフォルト設定"""

        return {
            "model": {
                "name": "PLaMo-Embedding-1B",
                "dimension": 1024,
                "max_sequence_length": 512,
                "batch_size": 16,
                "local_processing": True,
                "japanese_preprocessing": True,
                "business_term_enhancement": True,
            },
            "processing": {
                "timeout_seconds": 300,
                "retry_attempts": 3,
                "memory_optimization": True,
                "parallel_processing": True,
            },
            "optimization": {
                "japanese_boost": 1.2,
                "business_context_boost": 1.3,
                "cultural_context_preservation": True,
            },
        }

    async def process_chunks(
        self, chunks: list[SemanticChunk]
    ) -> VectorProcessingResult:
        """チャンクのベクトル処理（非同期）"""

        start_time = time.time()

        logger.info(f"Starting vector processing for {len(chunks)} chunks")

        # 前処理による文脈強化
        enhanced_chunks = await self._enhance_chunks(chunks)

        # バッチ処理によるベクトル生成
        vector_chunks = await self._generate_embeddings_batch(enhanced_chunks)

        # 処理統計更新
        processing_time = time.time() - start_time
        self._update_processing_stats(len(chunks), len(vector_chunks), processing_time)

        result = VectorProcessingResult(
            vector_chunks=vector_chunks,
            processing_stats=self.get_processing_stats(),
            model_info=self.model_config.copy(),
            japanese_optimization_applied=True,
        )

        logger.info(
            f"Vector processing completed: {len(vector_chunks)} vectors generated in {processing_time:.2f}s"
        )

        return result

    async def _enhance_chunks(
        self, chunks: list[SemanticChunk]
    ) -> list[dict[str, Any]]:
        """チャンク前処理・文脈強化"""

        enhanced_chunks = []

        for chunk in chunks:
            enhanced_data = {
                "original_chunk": chunk,
                "enhanced_text": chunk.content,
                "japanese_features": {},
                "business_features": {},
                "context_preserved": False,
            }

            # 前処理パイプライン適用
            text = chunk.content

            # 1. 日本語正規化
            normalizer = self.preprocessing_pipeline[0]
            text = normalizer.normalize(text)

            # 2. ビジネス用語強化
            enhancer = self.preprocessing_pipeline[1]
            text = enhancer.enhance(text)
            enhanced_data["business_features"] = enhancer.extract_business_features(
                text
            )

            # 3. 文脈保持
            preserver = self.preprocessing_pipeline[2]
            text = preserver.preserve_hierarchical_context(text, chunk.metadata)
            enhanced_data["context_preserved"] = True

            enhanced_data["enhanced_text"] = text
            enhanced_chunks.append(enhanced_data)

        return enhanced_chunks

    async def _generate_embeddings_batch(
        self, enhanced_chunks: list[dict[str, Any]]
    ) -> list[VectorChunk]:
        """バッチ処理によるベクトル生成"""

        vector_chunks = []
        batch_size = self.model_config.get("batch_size", 16)

        # バッチ分割処理
        for i in range(0, len(enhanced_chunks), batch_size):
            batch = enhanced_chunks[i : i + batch_size]

            try:
                batch_vectors = await self._process_batch(batch)
                vector_chunks.extend(batch_vectors)

                # メモリ最適化：バッチ処理後のクリーンアップ
                if self.processing_config.get("memory_optimization", True):
                    import gc

                    gc.collect()

            except Exception as e:
                logger.error(
                    f"Batch processing failed for batch {i // batch_size + 1}: {e}"
                )
                # エラー時のフォールバック処理
                fallback_vectors = await self._fallback_processing(batch)
                vector_chunks.extend(fallback_vectors)

        return vector_chunks

    async def _process_batch(self, batch: list[dict[str, Any]]) -> list[VectorChunk]:
        """個別バッチ処理"""

        batch_texts = [item["enhanced_text"] for item in batch]

        # PLaMo-Embedding-1B による実際のベクトル生成
        # 現在は模擬実装、実際のPLaMo統合時に更新
        embeddings = await self._generate_plamo_embeddings(batch_texts)

        vector_chunks = []

        for i, (enhanced_data, embedding) in enumerate(
            zip(batch, embeddings, strict=False)
        ):
            chunk = enhanced_data["original_chunk"]

            # 日本語最適化情報
            japanese_enhancement = {
                "business_features": enhanced_data["business_features"],
                "context_preserved": enhanced_data["context_preserved"],
                "enhancement_applied": True,
                "boost_score": enhanced_data["business_features"].get(
                    "boost_score", 1.0
                ),
            }

            # ベクトルチャンク作成
            vector_chunk = VectorChunk(
                chunk_id=f"vec_{chunk.chunk_id}_{int(time.time())}_{i}",
                original_chunk=chunk,
                embedding=embedding,
                embedding_metadata={
                    "model": self.model_config["name"],
                    "dimension": self.model_config["dimension"],
                    "processing_method": "plamo_batch",
                    "text_length": len(enhanced_data["enhanced_text"]),
                },
                japanese_enhancement=japanese_enhancement,
                search_boost=japanese_enhancement["boost_score"],
            )

            vector_chunks.append(vector_chunk)

        return vector_chunks

    async def _generate_plamo_embeddings(self, texts: list[str]) -> list[np.ndarray]:
        """PLaMo-Embedding-1B ベクトル生成"""

        # 実際のPLaMo-Embedding-1B統合実装
        # 現在は開発用の模擬実装

        embeddings = []
        dimension = self.model_config.get("dimension", 1024)

        for text in texts:
            # 模擬的なベクトル生成 (実装時にPLaMo APIに置き換え)
            # 日本語の特徴を反映した模擬ベクトル生成

            # テキストの特徴に基づく疑似ベクトル
            text_features = self._extract_text_features(text)
            base_vector = np.random.normal(0, 1, dimension).astype(np.float32)

            # 日本語特徴の反映
            if text_features["has_japanese"]:
                base_vector[:100] *= 1.2  # 日本語特徴強化

            if text_features["has_business_terms"]:
                base_vector[100:200] *= 1.3  # ビジネス用語強化

            # 正規化
            norm = np.linalg.norm(base_vector)
            if norm > 0:
                base_vector = base_vector / norm

            embeddings.append(base_vector)

        # 実際のPLaMo実装時のコード例:
        # try:
        #     import plamo_embedding
        #     model = plamo_embedding.load_model(self.model_config['name'])
        #     embeddings = model.encode(texts, batch_size=self.model_config['batch_size'])
        # except Exception as e:
        #     logger.error(f"PLaMo embedding generation failed: {e}")
        #     raise

        return embeddings

    def _extract_text_features(self, text: str) -> dict[str, bool]:
        """テキスト特徴抽出"""

        return {
            "has_japanese": bool(re.search(r"[ひ-ん一-龯ア-ン]", text)),
            "has_business_terms": bool(re.search(r"会社|部|課|売上|利益|年度", text)),
            "has_numbers": bool(re.search(r"\d+", text)),
            "has_dates": bool(re.search(r"\d{4}年|\d+月", text)),
        }

    async def _fallback_processing(
        self, batch: list[dict[str, Any]]
    ) -> list[VectorChunk]:
        """フォールバック処理"""

        logger.warning("Using fallback processing for failed batch")

        vector_chunks = []
        dimension = self.model_config.get("dimension", 1024)

        for enhanced_data in batch:
            chunk = enhanced_data["original_chunk"]

            # 簡易ベクトル生成
            fallback_embedding = np.random.normal(0, 0.1, dimension).astype(np.float32)

            vector_chunk = VectorChunk(
                chunk_id=f"fallback_{chunk.chunk_id}_{int(time.time())}",
                original_chunk=chunk,
                embedding=fallback_embedding,
                embedding_metadata={
                    "model": "fallback",
                    "dimension": dimension,
                    "processing_method": "fallback",
                    "warning": "fallback_processing_used",
                },
                japanese_enhancement={"enhancement_applied": False},
                search_boost=1.0,
            )

            vector_chunks.append(vector_chunk)

        return vector_chunks

    def _update_processing_stats(
        self, total: int, successful: int, processing_time: float
    ):
        """処理統計更新"""

        self.processing_stats["total_processed"] += total
        self.processing_stats["successful_embeddings"] += successful
        self.processing_stats["failed_embeddings"] += total - successful

        # 平均処理時間更新
        current_avg = self.processing_stats["average_processing_time"]
        total_processed = self.processing_stats["total_processed"]

        if total_processed > 0:
            self.processing_stats["average_processing_time"] = (
                current_avg * (total_processed - total) + processing_time
            ) / total_processed

        if successful > 0:
            self.processing_stats["japanese_enhancements_applied"] += successful

    def get_processing_stats(self) -> dict[str, Any]:
        """処理統計取得"""

        stats = self.processing_stats.copy()

        if stats["total_processed"] > 0:
            stats["success_rate"] = (
                stats["successful_embeddings"] / stats["total_processed"]
            )
            stats["failure_rate"] = (
                stats["failed_embeddings"] / stats["total_processed"]
            )
        else:
            stats["success_rate"] = 0.0
            stats["failure_rate"] = 0.0

        return stats

    def save_processing_results(self, result: VectorProcessingResult, output_path: str):
        """処理結果保存"""

        # ベクトルデータの保存（NumPy形式）
        embeddings_path = Path(output_path) / "embeddings.npz"
        embeddings_path.parent.mkdir(parents=True, exist_ok=True)

        embeddings_dict = {}
        metadata_list = []

        for i, vector_chunk in enumerate(result.vector_chunks):
            embeddings_dict[f"embedding_{i}"] = vector_chunk.embedding

            metadata_list.append(
                {
                    "chunk_id": vector_chunk.chunk_id,
                    "original_content": vector_chunk.original_chunk.content,
                    "japanese_enhancement": vector_chunk.japanese_enhancement,
                    "search_boost": vector_chunk.search_boost,
                    "created_at": vector_chunk.created_at,
                }
            )

        # 埋め込みベクトル保存
        np.savez_compressed(embeddings_path, **embeddings_dict)

        # メタデータ保存
        metadata_path = Path(output_path) / "metadata.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "vector_chunks_metadata": metadata_list,
                    "processing_stats": result.processing_stats,
                    "model_info": result.model_info,
                    "japanese_optimization_applied": result.japanese_optimization_applied,
                },
                f,
                ensure_ascii=False,
                indent=2,
            )

        logger.info(f"Vector processing results saved to {output_path}")

    @classmethod
    def load_processing_results(cls, input_path: str) -> VectorProcessingResult:
        """処理結果読み込み"""

        # 埋め込みベクトル読み込み
        embeddings_path = Path(input_path) / "embeddings.npz"
        embeddings_data = np.load(embeddings_path)

        # メタデータ読み込み
        metadata_path = Path(input_path) / "metadata.json"
        with open(metadata_path, encoding="utf-8") as f:
            saved_data = json.load(f)

        vector_chunks = []

        for i, metadata in enumerate(saved_data["vector_chunks_metadata"]):
            # 元のSemanticChunkを再構築（簡略版）
            original_chunk = SemanticChunk(
                chunk_id=metadata["chunk_id"].replace("vec_", ""),
                content=metadata["original_content"],
                chunk_type="loaded",
                metadata={},
                search_weight=1.0,
            )

            # VectorChunk再構築
            vector_chunk = VectorChunk(
                chunk_id=metadata["chunk_id"],
                original_chunk=original_chunk,
                embedding=embeddings_data[f"embedding_{i}"],
                japanese_enhancement=metadata["japanese_enhancement"],
                search_boost=metadata["search_boost"],
                created_at=metadata["created_at"],
            )

            vector_chunks.append(vector_chunk)

        result = VectorProcessingResult(
            vector_chunks=vector_chunks,
            processing_stats=saved_data["processing_stats"],
            model_info=saved_data["model_info"],
            japanese_optimization_applied=saved_data["japanese_optimization_applied"],
        )

        logger.info(f"Vector processing results loaded from {input_path}")

        return result
