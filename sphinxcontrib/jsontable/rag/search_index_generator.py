"""
Phase 3: 高度検索インデックス生成エンジン

PLaMo-Embedding-1Bと統合されたベクトル検索インデックスの
包括的な構築・管理機能を提供
"""

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

# FAISS統合（オプション）
try:
    import faiss

    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logging.warning(
        "FAISS not available. Vector search will use fallback implementation."
    )

from .metadata_extractor import BasicMetadata
from .vector_processor import VectorChunk

logger = logging.getLogger(__name__)


@dataclass
class VectorIndex:
    """ベクトル検索インデックス"""

    faiss_index: Any | None = None  # FAISSインデックス
    fallback_embeddings: np.ndarray | None = None  # フォールバック用埋め込み
    chunk_metadata: list[dict[str, Any]] = field(default_factory=list)
    search_parameters: dict[str, Any] = field(default_factory=dict)
    dimension: int = 1024
    index_type: str = "faiss_flatip"  # or "fallback_cosine"


@dataclass
class SemanticSearchIndex:
    """セマンティック検索インデックス"""

    text_segments: list[str] = field(default_factory=list)
    semantic_mappings: dict[str, list[int]] = field(default_factory=dict)
    japanese_keyword_index: dict[str, list[int]] = field(default_factory=dict)
    business_term_index: dict[str, list[int]] = field(default_factory=dict)


@dataclass
class FacetedSearchIndex:
    """ファセット検索インデックス"""

    categorical_facets: dict[str, dict[str, list[int]]] = field(default_factory=dict)
    numerical_facets: dict[str, dict[str, list[int]]] = field(default_factory=dict)
    temporal_facets: dict[str, dict[str, list[int]]] = field(default_factory=dict)
    entity_facets: dict[str, dict[str, list[int]]] = field(default_factory=dict)


@dataclass
class HybridSearchIndex:
    """ハイブリッド検索インデックス"""

    vector_weight: float = 0.7
    semantic_weight: float = 0.2
    facet_weight: float = 0.1
    fusion_algorithm: str = "rank_fusion"


@dataclass
class ComprehensiveSearchIndex:
    """包括的検索インデックス"""

    vector_index: VectorIndex | None = None
    semantic_index: SemanticSearchIndex | None = None
    facet_index: FacetedSearchIndex | None = None
    hybrid_index: HybridSearchIndex | None = None

    creation_time: str = field(
        default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S")
    )
    total_chunks: int = 0
    index_statistics: dict[str, Any] = field(default_factory=dict)


class JapaneseQueryProcessor:
    """日本語クエリ処理・最適化"""

    def __init__(self):
        # 日本語クエリ拡張辞書
        self.synonym_dict = {
            "会社": ["企業", "法人", "組織", "株式会社"],
            "売上": ["売上高", "収益", "売り上げ", "販売実績"],
            "利益": ["収益", "プロフィット", "純利益", "営業利益"],
            "従業員": ["社員", "職員", "スタッフ", "人員"],
            "年度": ["会計年度", "FY", "事業年度"],
            "四半期": ["Q1", "Q2", "Q3", "Q4", "クォーター"],
        }

        # ビジネス用語マッピング
        self.business_term_mapping = {
            "ROI": ["投資収益率", "リターン"],
            "KPI": ["重要業績評価指標", "主要指標"],
            "EBITDA": ["利払い前・税引き前・減価償却前利益"],
            "B2B": ["企業間取引"],
            "B2C": ["企業・消費者間取引"],
        }

    def expand_query(self, query: str) -> list[str]:
        """クエリ拡張処理"""

        expanded_queries = [query]  # 元のクエリ

        # 同義語展開
        for term, synonyms in self.synonym_dict.items():
            if term in query:
                for synonym in synonyms:
                    expanded_queries.append(query.replace(term, synonym))

        # ビジネス用語展開
        for term, variations in self.business_term_mapping.items():
            if term.lower() in query.lower():
                for variation in variations:
                    expanded_queries.append(query + " " + variation)

        return list(set(expanded_queries))  # 重複除去

    def extract_japanese_features(self, query: str) -> dict[str, Any]:
        """日本語クエリ特徴抽出"""

        import re

        features = {
            "has_hiragana": bool(re.search(r"[ひ-ん]", query)),
            "has_katakana": bool(re.search(r"[ア-ン]", query)),
            "has_kanji": bool(re.search(r"[一-龯]", query)),
            "has_numbers": bool(re.search(r"\d+", query)),
            "has_business_terms": False,
            "query_type": "general",
        }

        # ビジネス用語チェック
        business_keywords = [
            "会社",
            "売上",
            "利益",
            "従業員",
            "年度",
            "ROI",
            "KPI",
            "株式会社",
            "企業",
            "業績",
            "売上高",
            "製造業",
            "情報",
        ]
        if any(keyword in query for keyword in business_keywords):
            features["has_business_terms"] = True
            features["query_type"] = "business"

        return features


class SearchIndexGenerator:
    """検索インデックス生成エンジン"""

    def __init__(self, config: dict[str, Any] | None = None):
        """初期化"""

        self.config = config or self._get_default_config()
        self.japanese_processor = JapaneseQueryProcessor()

        # インデックス戦略設定
        self.index_strategies = {
            "vector_similarity": self._setup_vector_strategy(),
            "semantic_search": self._setup_semantic_strategy(),
            "faceted_search": self._setup_faceted_strategy(),
            "hybrid_search": self._setup_hybrid_strategy(),
        }

        logger.info("SearchIndexGenerator initialized")

    def _get_default_config(self) -> dict[str, Any]:
        """デフォルト設定"""

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
            "use_faiss": FAISS_AVAILABLE,
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
        vector_chunks: list[VectorChunk],
        basic_metadata: BasicMetadata | None = None,
    ) -> ComprehensiveSearchIndex:
        """包括的検索インデックス生成"""

        start_time = time.time()

        logger.info(
            f"Generating comprehensive search index for {len(vector_chunks)} chunks"
        )

        search_index = ComprehensiveSearchIndex()
        search_index.total_chunks = len(vector_chunks)

        # 1. ベクトル類似度検索インデックス
        search_index.vector_index = self._build_vector_index(vector_chunks)

        # 2. セマンティック検索インデックス
        search_index.semantic_index = self._build_semantic_index(vector_chunks)

        # 3. ファセット検索インデックス
        search_index.facet_index = self._build_facet_index(
            vector_chunks, basic_metadata
        )

        # 4. ハイブリッド検索インデックス
        search_index.hybrid_index = self._build_hybrid_index()

        # 統計情報更新
        generation_time = time.time() - start_time
        search_index.index_statistics = {
            "generation_time_seconds": generation_time,
            "vector_index_size": len(vector_chunks),
            "semantic_terms_indexed": len(
                search_index.semantic_index.japanese_keyword_index
            ),
            "facet_categories": len(search_index.facet_index.categorical_facets),
            "faiss_available": FAISS_AVAILABLE,
        }

        logger.info(f"Comprehensive search index generated in {generation_time:.2f}s")

        return search_index

    def _build_vector_index(self, vector_chunks: list[VectorChunk]) -> VectorIndex:
        """ベクトルインデックス構築"""

        dimension = self.config["vector_search"]["dimension"]
        embeddings = np.array([chunk.embedding for chunk in vector_chunks])

        vector_index = VectorIndex(
            dimension=dimension,
            chunk_metadata=[
                {
                    "chunk_id": chunk.chunk_id,
                    "content": chunk.original_chunk.content,
                    "search_boost": chunk.search_boost,
                    "japanese_enhancement": chunk.japanese_enhancement,
                }
                for chunk in vector_chunks
            ],
            search_parameters={
                "k": self.config["vector_search"]["search_k"],
                "threshold": 0.7,
                "japanese_boost": 1.2,
            },
        )

        if FAISS_AVAILABLE:
            # FAISS使用による高速ベクトル検索
            index = faiss.IndexFlatIP(dimension)  # PLaMo用内積インデックス
            index.add(embeddings.astype("float32"))

            vector_index.faiss_index = index
            vector_index.index_type = "faiss_flatip"

            logger.info(f"FAISS vector index built with {len(vector_chunks)} vectors")

        else:
            # フォールバック実装
            vector_index.fallback_embeddings = embeddings
            vector_index.index_type = "fallback_cosine"

            logger.info(
                f"Fallback vector index built with {len(vector_chunks)} vectors"
            )

        return vector_index

    def _build_semantic_index(
        self, vector_chunks: list[VectorChunk]
    ) -> SemanticSearchIndex:
        """セマンティック検索インデックス構築"""

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
        self, vector_chunks: list[VectorChunk]
    ) -> dict[str, list[int]]:
        """日本語キーワードインデックス構築"""

        import re

        keyword_index = {}

        for i, chunk in enumerate(vector_chunks):
            content = chunk.original_chunk.content

            # 日本語キーワード抽出
            japanese_words = re.findall(r"[一-龯ひ-んア-ン]+", content)

            # 英数字キーワード抽出
            alphanumeric_words = re.findall(r"[A-Za-z0-9]+", content)

            all_keywords = japanese_words + alphanumeric_words

            for keyword in all_keywords:
                if len(keyword) >= 2:  # 最小キーワード長
                    if keyword not in keyword_index:
                        keyword_index[keyword] = []
                    keyword_index[keyword].append(i)

        return keyword_index

    def _build_business_term_index(
        self, vector_chunks: list[VectorChunk]
    ) -> dict[str, list[int]]:
        """ビジネス用語インデックス構築"""

        import re

        business_term_index = {}

        # ビジネス用語パターン
        business_patterns = [
            r"[一-龯\w]+株式会社",  # 会社名 + 株式会社
            r"株式会社[一-龯]+",  # 株式会社 + 名前
            r"[一-龯]+部",
            r"[一-龯]+課",
            r"\d+(?:,\d{3})*円",
            r"\d+億円",
            r"\d+万円",
            r"\d{4}年度",
            r"第\d+四半期",
            r"売上",
            r"利益",
            r"収益",
            r"従業員",
            r"ROI",
            r"KPI",
            r"EBITDA",
        ]

        for i, chunk in enumerate(vector_chunks):
            content = chunk.original_chunk.content

            for pattern in business_patterns:
                matches = re.findall(pattern, content)

                for match in matches:
                    if match not in business_term_index:
                        business_term_index[match] = []
                    business_term_index[match].append(i)

        return business_term_index

    def _build_semantic_mappings(
        self, vector_chunks: list[VectorChunk]
    ) -> dict[str, list[int]]:
        """セマンティックマッピング構築"""

        semantic_mappings = {}

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

    def _build_facet_index(
        self, vector_chunks: list[VectorChunk], basic_metadata: BasicMetadata | None
    ) -> FacetedSearchIndex:
        """ファセット検索インデックス構築"""

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
        self, vector_chunks: list[VectorChunk], basic_metadata: BasicMetadata | None
    ) -> dict[str, dict[str, list[int]]]:
        """カテゴリファセット構築"""

        categorical_facets = {}

        # データ型ファセット
        categorical_facets["data_type"] = {}

        for i, chunk in enumerate(vector_chunks):
            # チャンクタイプによる分類
            chunk_type = chunk.original_chunk.chunk_type

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
                if self._categorize_business_content(
                    chunk.original_chunk.content, category
                ):
                    categorical_facets["business_category"][category].append(i)

        return categorical_facets

    def _build_numerical_facets(
        self, vector_chunks: list[VectorChunk], basic_metadata: BasicMetadata | None
    ) -> dict[str, dict[str, list[int]]]:
        """数値ファセット構築"""

        import re

        numerical_facets = {}

        # 金額範囲ファセット
        numerical_facets["amount_range"] = {
            "small": [],  # ~100万円
            "medium": [],  # 100万円~1億円
            "large": [],  # 1億円~
            "unknown": [],
        }

        for i, chunk in enumerate(vector_chunks):
            content = chunk.original_chunk.content

            # 金額抽出
            amounts = re.findall(r"(\d+(?:,\d{3})*(?:万|億)?円)", content)

            if amounts:
                max_amount = self._parse_japanese_amount(amounts[0])

                if max_amount < 1000000:  # 100万円未満
                    numerical_facets["amount_range"]["small"].append(i)
                elif max_amount < 100000000:  # 1億円未満
                    numerical_facets["amount_range"]["medium"].append(i)
                else:
                    numerical_facets["amount_range"]["large"].append(i)
            else:
                numerical_facets["amount_range"]["unknown"].append(i)

        return numerical_facets

    def _build_temporal_facets(
        self, vector_chunks: list[VectorChunk]
    ) -> dict[str, dict[str, list[int]]]:
        """時間ファセット構築"""

        import re

        temporal_facets = {}

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

        return temporal_facets

    def _build_entity_facets(
        self, vector_chunks: list[VectorChunk]
    ) -> dict[str, dict[str, list[int]]]:
        """エンティティファセット構築"""

        import re

        entity_facets = {}

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

        return entity_facets

    def _build_hybrid_index(self) -> HybridSearchIndex:
        """ハイブリッド検索インデックス構築"""

        hybrid_config = self.config["hybrid_search"]

        return HybridSearchIndex(
            vector_weight=hybrid_config["vector_weight"],
            semantic_weight=hybrid_config["semantic_weight"],
            facet_weight=hybrid_config["facet_weight"],
            fusion_algorithm="rank_fusion",
        )

    def _categorize_business_content(self, content: str, category: str) -> bool:
        """ビジネスコンテンツ分類"""

        category_keywords = {
            "financial": [
                "売上",
                "利益",
                "収益",
                "売上高",
                "純利益",
                "営業利益",
                "財務",
                "予算",
            ],
            "organizational": [
                "組織",
                "部門",
                "人事",
                "従業員",
                "社員",
                "採用",
                "研修",
            ],
            "operational": ["業務", "運営", "プロセス", "効率", "品質", "生産"],
            "strategic": ["戦略", "計画", "方針", "目標", "市場", "競合", "成長"],
        }

        keywords = category_keywords.get(category, [])
        return any(keyword in content for keyword in keywords)

    def _parse_japanese_amount(self, amount_str: str) -> int:
        """日本語金額パース"""

        import re

        # 数値抽出
        numbers = re.findall(r"\d+(?:,\d{3})*", amount_str)
        if not numbers:
            return 0

        base_amount = int(numbers[0].replace(",", ""))

        # 単位変換
        if "万円" in amount_str:
            return base_amount * 10000
        elif "億円" in amount_str:
            return base_amount * 100000000
        else:
            return base_amount

    def search_similar_vectors(
        self,
        query_embedding: np.ndarray,
        search_index: ComprehensiveSearchIndex,
        k: int = 10,
    ) -> list[tuple[int, float]]:
        """ベクトル類似検索"""

        if search_index.vector_index is None:
            return []

        vector_index = search_index.vector_index

        if FAISS_AVAILABLE and vector_index.faiss_index is not None:
            # FAISS検索
            query_vector = query_embedding.reshape(1, -1).astype("float32")
            scores, indices = vector_index.faiss_index.search(query_vector, k)

            results = [
                (int(indices[0][i]), float(scores[0][i]))
                for i in range(len(indices[0]))
                if indices[0][i] != -1
            ]

        else:
            # フォールバック検索（コサイン類似度）
            embeddings = vector_index.fallback_embeddings

            # コサイン類似度計算
            similarities = np.dot(embeddings, query_embedding) / (
                np.linalg.norm(embeddings, axis=1) * np.linalg.norm(query_embedding)
            )

            # 上位k件取得
            top_indices = np.argsort(similarities)[::-1][:k]
            results = [(int(idx), float(similarities[idx])) for idx in top_indices]

        return results

    def save_search_index(
        self, search_index: ComprehensiveSearchIndex, output_path: str
    ):
        """検索インデックス保存"""

        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)

        # FAISSインデックス保存
        if (
            FAISS_AVAILABLE
            and search_index.vector_index
            and search_index.vector_index.faiss_index
        ):
            faiss_path = output_dir / "vector_index.faiss"
            faiss.write_index(search_index.vector_index.faiss_index, str(faiss_path))

        # その他のインデックス情報をJSON保存
        index_data = {
            "creation_time": search_index.creation_time,
            "total_chunks": search_index.total_chunks,
            "index_statistics": search_index.index_statistics,
            "vector_index_metadata": {
                "chunk_metadata": search_index.vector_index.chunk_metadata
                if search_index.vector_index
                else [],
                "search_parameters": search_index.vector_index.search_parameters
                if search_index.vector_index
                else {},
                "dimension": search_index.vector_index.dimension
                if search_index.vector_index
                else 1024,
                "index_type": search_index.vector_index.index_type
                if search_index.vector_index
                else "unknown",
            },
            "semantic_index": {
                "text_segments": search_index.semantic_index.text_segments
                if search_index.semantic_index
                else [],
                "japanese_keyword_index": search_index.semantic_index.japanese_keyword_index
                if search_index.semantic_index
                else {},
                "business_term_index": search_index.semantic_index.business_term_index
                if search_index.semantic_index
                else {},
                "semantic_mappings": search_index.semantic_index.semantic_mappings
                if search_index.semantic_index
                else {},
            },
            "facet_index": {
                "categorical_facets": search_index.facet_index.categorical_facets
                if search_index.facet_index
                else {},
                "numerical_facets": search_index.facet_index.numerical_facets
                if search_index.facet_index
                else {},
                "temporal_facets": search_index.facet_index.temporal_facets
                if search_index.facet_index
                else {},
                "entity_facets": search_index.facet_index.entity_facets
                if search_index.facet_index
                else {},
            },
            "hybrid_index": {
                "vector_weight": search_index.hybrid_index.vector_weight
                if search_index.hybrid_index
                else 0.7,
                "semantic_weight": search_index.hybrid_index.semantic_weight
                if search_index.hybrid_index
                else 0.2,
                "facet_weight": search_index.hybrid_index.facet_weight
                if search_index.hybrid_index
                else 0.1,
                "fusion_algorithm": search_index.hybrid_index.fusion_algorithm
                if search_index.hybrid_index
                else "rank_fusion",
            },
        }

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

    @classmethod
    def load_search_index(cls, input_path: str) -> ComprehensiveSearchIndex:
        """検索インデックス読み込み"""

        input_dir = Path(input_path)

        # メタデータ読み込み
        metadata_path = input_dir / "search_index_metadata.json"
        with open(metadata_path, encoding="utf-8") as f:
            index_data = json.load(f)

        # 検索インデックス再構築
        search_index = ComprehensiveSearchIndex(
            creation_time=index_data["creation_time"],
            total_chunks=index_data["total_chunks"],
            index_statistics=index_data["index_statistics"],
        )

        # ベクトルインデックス復元
        vector_metadata = index_data["vector_index_metadata"]
        search_index.vector_index = VectorIndex(
            chunk_metadata=vector_metadata["chunk_metadata"],
            search_parameters=vector_metadata["search_parameters"],
            dimension=vector_metadata["dimension"],
            index_type=vector_metadata["index_type"],
        )

        # FAISSインデックス読み込み
        faiss_path = input_dir / "vector_index.faiss"
        if FAISS_AVAILABLE and faiss_path.exists():
            search_index.vector_index.faiss_index = faiss.read_index(str(faiss_path))

        # フォールバック埋め込み読み込み
        embeddings_path = input_dir / "fallback_embeddings.npy"
        if embeddings_path.exists():
            search_index.vector_index.fallback_embeddings = np.load(embeddings_path)

        # その他のインデックス復元
        search_index.semantic_index = SemanticSearchIndex(
            text_segments=index_data["semantic_index"]["text_segments"],
            japanese_keyword_index=index_data["semantic_index"][
                "japanese_keyword_index"
            ],
            business_term_index=index_data["semantic_index"]["business_term_index"],
            semantic_mappings=index_data["semantic_index"]["semantic_mappings"],
        )

        search_index.facet_index = FacetedSearchIndex(
            categorical_facets=index_data["facet_index"]["categorical_facets"],
            numerical_facets=index_data["facet_index"]["numerical_facets"],
            temporal_facets=index_data["facet_index"]["temporal_facets"],
            entity_facets=index_data["facet_index"]["entity_facets"],
        )

        search_index.hybrid_index = HybridSearchIndex(
            vector_weight=index_data["hybrid_index"]["vector_weight"],
            semantic_weight=index_data["hybrid_index"]["semantic_weight"],
            facet_weight=index_data["hybrid_index"]["facet_weight"],
            fusion_algorithm=index_data["hybrid_index"]["fusion_algorithm"],
        )

        logger.info(f"Search index loaded from {input_path}")

        return search_index
