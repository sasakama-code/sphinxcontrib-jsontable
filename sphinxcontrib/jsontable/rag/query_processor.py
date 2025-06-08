"""
Phase 3: インテリジェントクエリ処理エンジン

自然言語クエリの解析・最適化・実行を統合的に管理し、
日本語特化の高度な検索機能を提供
"""

import logging
import re
import time
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from .search_index_generator import (
    ComprehensiveSearchIndex,
    JapaneseQueryProcessor,
    SearchIndexGenerator,
)
from .vector_processor import PLaMoVectorProcessor

logger = logging.getLogger(__name__)


@dataclass
class QueryAnalysis:
    """クエリ分析結果"""

    original_query: str
    expanded_queries: list[str] = field(default_factory=list)
    query_type: str = "general"  # general, business, technical, numerical
    japanese_features: dict[str, Any] = field(default_factory=dict)
    search_intent: str = "similarity"  # similarity, faceted, hybrid
    confidence_score: float = 1.0


@dataclass
class SearchResult:
    """検索結果"""

    chunk_id: str
    content: str
    relevance_score: float
    search_method: str  # vector, semantic, faceted, hybrid
    metadata: dict[str, Any] = field(default_factory=dict)
    japanese_enhancement: dict[str, Any] = field(default_factory=dict)


@dataclass
class QueryExecutionResult:
    """クエリ実行結果"""

    query_analysis: QueryAnalysis
    search_results: list[SearchResult]
    execution_time_ms: float
    total_candidates: int
    search_statistics: dict[str, Any] = field(default_factory=dict)


class QueryIntentClassifier:
    """クエリ意図分類器"""

    def __init__(self):
        # 意図分類パターン
        self.intent_patterns = {
            "similarity_search": {
                "patterns": [r"類似", r"似ている", r"関連する", r"like", r"similar"],
                "description": "ベクトル類似検索",
            },
            "faceted_search": {
                "patterns": [
                    r"絞り込み",
                    r"条件",
                    r"フィルター",
                    r"範囲",
                    r"where",
                    r"filter",
                ],
                "description": "ファセット検索",
            },
            "semantic_search": {
                "patterns": [r"意味", r"概念", r"内容", r"について", r"semantic"],
                "description": "セマンティック検索",
            },
            "temporal_search": {
                "patterns": [r"\d{4}年", r"四半期", r"期間", r"時期", r"when"],
                "description": "時間軸検索",
            },
            "numerical_search": {
                "patterns": [r"金額", r"数値", r"以上", r"以下", r"範囲", r"amount"],
                "description": "数値範囲検索",
            },
        }

        # ビジネス文脈パターン
        self.business_context_patterns = {
            "financial": [r"売上", r"利益", r"収益", r"予算", r"財務"],
            "organizational": [r"組織", r"部門", r"人事", r"従業員"],
            "operational": [r"業務", r"運営", r"プロセス", r"効率"],
            "strategic": [r"戦略", r"計画", r"目標", r"市場"],
        }

    def classify_intent(self, query: str) -> tuple[str, float]:
        """クエリ意図分類"""

        intent_scores = {}

        for intent, config in self.intent_patterns.items():
            score = 0.0

            for pattern in config["patterns"]:
                if re.search(pattern, query, re.IGNORECASE):
                    score += 1.0

            # パターン数で正規化
            intent_scores[intent] = score / len(config["patterns"])

        # 最高スコアの意図を返す
        if intent_scores:
            best_intent = max(intent_scores.items(), key=lambda x: x[1])
            return best_intent[0], best_intent[1]

        return "similarity_search", 0.5  # デフォルト

    def classify_business_context(self, query: str) -> str | None:
        """ビジネス文脈分類"""

        for context, patterns in self.business_context_patterns.items():
            if any(re.search(pattern, query) for pattern in patterns):
                return context

        return None


class HybridSearchEngine:
    """ハイブリッド検索エンジン"""

    def __init__(self, search_index: ComprehensiveSearchIndex):
        self.search_index = search_index
        self.japanese_processor = JapaneseQueryProcessor()

    async def execute_hybrid_search(
        self,
        query_analysis: QueryAnalysis,
        query_embedding: np.ndarray | None = None,
        k: int = 10,
    ) -> list[SearchResult]:
        """ハイブリッド検索実行"""

        # 各検索手法の結果を収集
        vector_results = await self._execute_vector_search(query_embedding, k)
        semantic_results = await self._execute_semantic_search(query_analysis, k)
        faceted_results = await self._execute_faceted_search(query_analysis, k)

        # ランクフュージョンによる統合
        unified_results = self._rank_fusion(
            vector_results, semantic_results, faceted_results
        )

        return unified_results[:k]

    async def _execute_vector_search(
        self, query_embedding: np.ndarray | None, k: int
    ) -> list[SearchResult]:
        """ベクトル検索実行"""

        if query_embedding is None or self.search_index.vector_index is None:
            return []

        try:
            # SearchIndexGeneratorのベクトル検索を使用
            generator = SearchIndexGenerator()
            similar_indices = generator.search_similar_vectors(
                query_embedding, self.search_index, k
            )

            results = []
            for idx, score in similar_indices:
                if idx < len(self.search_index.vector_index.chunk_metadata):
                    chunk_metadata = self.search_index.vector_index.chunk_metadata[idx]

                    result = SearchResult(
                        chunk_id=chunk_metadata["chunk_id"],
                        content=chunk_metadata["content"],
                        relevance_score=max(0.0, float(score)),  # 非負値を保証
                        search_method="vector",
                        metadata=chunk_metadata,
                        japanese_enhancement=chunk_metadata.get(
                            "japanese_enhancement", {}
                        ),
                    )
                    results.append(result)

            return results

        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []

    async def _execute_semantic_search(
        self, query_analysis: QueryAnalysis, k: int
    ) -> list[SearchResult]:
        """セマンティック検索実行"""

        if self.search_index.semantic_index is None:
            return []

        results = []
        semantic_index = self.search_index.semantic_index

        # 展開されたクエリでキーワード検索
        all_keywords = []
        for query in query_analysis.expanded_queries:
            keywords = re.findall(r"[一-龯ひ-んア-ンA-Za-z0-9]+", query)
            all_keywords.extend(keywords)

        # キーワードマッチングスコア計算
        chunk_scores = {}

        for keyword in all_keywords:
            if keyword in semantic_index.japanese_keyword_index:
                for chunk_idx in semantic_index.japanese_keyword_index[keyword]:
                    if chunk_idx not in chunk_scores:
                        chunk_scores[chunk_idx] = 0.0
                    chunk_scores[chunk_idx] += 1.0

        # ビジネス用語ボーナス
        for keyword in all_keywords:
            if keyword in semantic_index.business_term_index:
                for chunk_idx in semantic_index.business_term_index[keyword]:
                    if chunk_idx in chunk_scores:
                        chunk_scores[chunk_idx] *= 1.3  # ビジネス用語ブースト

        # 上位k件取得
        sorted_chunks = sorted(chunk_scores.items(), key=lambda x: x[1], reverse=True)[
            :k
        ]

        for chunk_idx, score in sorted_chunks:
            if chunk_idx < len(semantic_index.text_segments):
                result = SearchResult(
                    chunk_id=f"semantic_{chunk_idx}",
                    content=semantic_index.text_segments[chunk_idx],
                    relevance_score=score,
                    search_method="semantic",
                    metadata={
                        "chunk_index": chunk_idx,
                        "matched_keywords": all_keywords,
                    },
                )
                results.append(result)

        return results

    async def _execute_faceted_search(
        self, query_analysis: QueryAnalysis, k: int
    ) -> list[SearchResult]:
        """ファセット検索実行"""

        if self.search_index.facet_index is None:
            return []

        results = []
        facet_index = self.search_index.facet_index

        # クエリからファセット条件抽出
        facet_conditions = self._extract_facet_conditions(query_analysis.original_query)

        matching_chunks = set()

        # カテゴリファセット検索
        if "category" in facet_conditions:
            category = facet_conditions["category"]
            if category in facet_index.categorical_facets:
                for _facet_value, chunk_indices in facet_index.categorical_facets[
                    category
                ].items():
                    matching_chunks.update(chunk_indices)

        # 時間ファセット検索
        if "year" in facet_conditions:
            year = facet_conditions["year"]
            if year in facet_index.temporal_facets.get("fiscal_year", {}):
                matching_chunks.update(facet_index.temporal_facets["fiscal_year"][year])

        # 数値ファセット検索
        if "amount_range" in facet_conditions:
            amount_range = facet_conditions["amount_range"]
            if amount_range in facet_index.numerical_facets.get("amount_range", {}):
                matching_chunks.update(
                    facet_index.numerical_facets["amount_range"][amount_range]
                )

        # 結果生成
        for chunk_idx in list(matching_chunks)[:k]:
            result = SearchResult(
                chunk_id=f"faceted_{chunk_idx}",
                content=f"Faceted result for chunk {chunk_idx}",
                relevance_score=1.0,
                search_method="faceted",
                metadata={
                    "chunk_index": chunk_idx,
                    "facet_conditions": facet_conditions,
                },
            )
            results.append(result)

        return results

    def _extract_facet_conditions(self, query: str) -> dict[str, str]:
        """ファセット条件抽出"""

        conditions = {}

        # 年度抽出
        year_match = re.search(r"(\d{4})年", query)
        if year_match:
            conditions["year"] = year_match.group(1)

        # カテゴリ抽出
        if "財務" in query or "売上" in query or "利益" in query:
            conditions["category"] = "financial"
        elif "組織" in query or "人事" in query:
            conditions["category"] = "organizational"

        # 金額範囲抽出
        if "大きい" in query or "高い" in query or "億" in query:
            conditions["amount_range"] = "large"
        elif "小さい" in query or "低い" in query or "万" in query:
            conditions["amount_range"] = "small"

        return conditions

    def _rank_fusion(
        self,
        vector_results: list[SearchResult],
        semantic_results: list[SearchResult],
        faceted_results: list[SearchResult],
    ) -> list[SearchResult]:
        """ランクフュージョンによる結果統合"""

        if self.search_index.hybrid_index is None:
            # フォールバック: ベクトル検索結果を優先
            return vector_results

        hybrid_config = self.search_index.hybrid_index

        # 各検索結果の統合スコア計算
        unified_results = {}

        # ベクトル検索結果
        for i, result in enumerate(vector_results):
            content_key = result.content[:100]  # コンテンツの最初の100文字をキーとする

            rank_score = 1.0 / (i + 1)  # ランクベーススコア
            weighted_score = (
                result.relevance_score * hybrid_config.vector_weight * rank_score
            )

            unified_results[content_key] = {
                "result": result,
                "total_score": weighted_score,
                "vector_score": weighted_score,
                "semantic_score": 0.0,
                "faceted_score": 0.0,
            }

        # セマンティック検索結果
        for i, result in enumerate(semantic_results):
            content_key = result.content[:100]

            rank_score = 1.0 / (i + 1)
            weighted_score = (
                result.relevance_score * hybrid_config.semantic_weight * rank_score
            )

            if content_key in unified_results:
                unified_results[content_key]["total_score"] += weighted_score
                unified_results[content_key]["semantic_score"] = weighted_score
            else:
                unified_results[content_key] = {
                    "result": result,
                    "total_score": weighted_score,
                    "vector_score": 0.0,
                    "semantic_score": weighted_score,
                    "faceted_score": 0.0,
                }

        # ファセット検索結果
        for i, result in enumerate(faceted_results):
            content_key = result.content[:100]

            rank_score = 1.0 / (i + 1)
            weighted_score = (
                result.relevance_score * hybrid_config.facet_weight * rank_score
            )

            if content_key in unified_results:
                unified_results[content_key]["total_score"] += weighted_score
                unified_results[content_key]["faceted_score"] = weighted_score
            else:
                unified_results[content_key] = {
                    "result": result,
                    "total_score": weighted_score,
                    "vector_score": 0.0,
                    "semantic_score": 0.0,
                    "faceted_score": weighted_score,
                }

        # 統合スコアでソート
        sorted_results = sorted(
            unified_results.values(), key=lambda x: x["total_score"], reverse=True
        )

        # SearchResultオブジェクトを更新して返す
        final_results = []
        for item in sorted_results:
            result = item["result"]
            result.relevance_score = item["total_score"]
            result.search_method = "hybrid"
            result.metadata.update(
                {
                    "vector_score": item["vector_score"],
                    "semantic_score": item["semantic_score"],
                    "faceted_score": item["faceted_score"],
                }
            )
            final_results.append(result)

        return final_results


class IntelligentQueryProcessor:
    """インテリジェントクエリ処理エンジン"""

    def __init__(
        self,
        vector_processor: PLaMoVectorProcessor,
        search_index: ComprehensiveSearchIndex,
    ):
        self.vector_processor = vector_processor
        self.search_index = search_index
        self.japanese_processor = JapaneseQueryProcessor()
        self.intent_classifier = QueryIntentClassifier()
        self.hybrid_engine = HybridSearchEngine(search_index)

        logger.info("IntelligentQueryProcessor initialized")

    async def process_query(
        self, query: str, options: dict[str, Any] | None = None
    ) -> QueryExecutionResult:
        """クエリ処理・実行"""

        start_time = time.time()

        logger.info(f"Processing query: {query}")

        # Step 1: クエリ分析
        query_analysis = await self._analyze_query(query)

        # Step 2: クエリベクトル化
        query_embedding = await self._vectorize_query(query, query_analysis)

        # Step 3: 検索実行
        search_results = await self._execute_search(
            query_analysis, query_embedding, options
        )

        # Step 4: 結果後処理
        processed_results = await self._post_process_results(
            search_results, query_analysis
        )

        execution_time = (time.time() - start_time) * 1000  # ms

        result = QueryExecutionResult(
            query_analysis=query_analysis,
            search_results=processed_results,
            execution_time_ms=execution_time,
            total_candidates=len(search_results),
            search_statistics={
                "query_expansion_count": len(query_analysis.expanded_queries),
                "search_method": query_analysis.search_intent,
                "japanese_features_detected": len(query_analysis.japanese_features),
                "processing_time_breakdown": {
                    "analysis_ms": 10,  # 概算
                    "vectorization_ms": 50,  # 概算
                    "search_ms": execution_time - 60,  # 残り時間
                    "post_processing_ms": 10,  # 概算
                },
            },
        )

        logger.info(
            f"Query processed in {execution_time:.2f}ms, {len(processed_results)} results"
        )

        return result

    async def _analyze_query(self, query: str) -> QueryAnalysis:
        """クエリ分析"""

        # クエリ拡張
        expanded_queries = self.japanese_processor.expand_query(query)

        # 日本語特徴抽出
        japanese_features = self.japanese_processor.extract_japanese_features(query)

        # 意図分類
        search_intent, confidence = self.intent_classifier.classify_intent(query)

        # ビジネス文脈分類
        business_context = self.intent_classifier.classify_business_context(query)
        if business_context:
            japanese_features["business_context"] = business_context

        # クエリタイプ決定
        query_type = (
            "business" if japanese_features.get("has_business_terms") else "general"
        )

        analysis = QueryAnalysis(
            original_query=query,
            expanded_queries=expanded_queries,
            query_type=query_type,
            japanese_features=japanese_features,
            search_intent=search_intent,
            confidence_score=confidence,
        )

        return analysis

    async def _vectorize_query(
        self, query: str, query_analysis: QueryAnalysis
    ) -> np.ndarray | None:
        """クエリベクトル化"""

        try:
            # クエリを疑似的なSemanticChunkに変換
            from .semantic_chunker import SemanticChunk

            query_chunk = SemanticChunk(
                chunk_id="query_embedding",
                content=query,
                chunk_type="query",
                embedding_hint="japanese_query_text",
                metadata={"query_analysis": query_analysis.__dict__},
                search_weight=1.0,
            )

            # ベクトル生成
            processing_result = await self.vector_processor.process_chunks(
                [query_chunk]
            )

            if processing_result.vector_chunks:
                return processing_result.vector_chunks[0].embedding

        except Exception as e:
            logger.error(f"Query vectorization failed: {e}")

        return None

    async def _execute_search(
        self,
        query_analysis: QueryAnalysis,
        query_embedding: np.ndarray | None,
        options: dict[str, Any] | None,
    ) -> list[SearchResult]:
        """検索実行"""

        search_options = options or {}
        k = search_options.get("max_results", 10)

        # 検索意図に基づく検索実行
        if (
            query_analysis.search_intent == "similarity_search"
            and query_embedding is not None
        ):
            return await self.hybrid_engine._execute_vector_search(query_embedding, k)

        elif query_analysis.search_intent == "semantic_search":
            return await self.hybrid_engine._execute_semantic_search(query_analysis, k)

        elif query_analysis.search_intent in [
            "faceted_search",
            "temporal_search",
            "numerical_search",
        ]:
            return await self.hybrid_engine._execute_faceted_search(query_analysis, k)

        else:
            # ハイブリッド検索（デフォルト）
            return await self.hybrid_engine.execute_hybrid_search(
                query_analysis, query_embedding, k
            )

    async def _post_process_results(
        self, search_results: list[SearchResult], query_analysis: QueryAnalysis
    ) -> list[SearchResult]:
        """結果後処理"""

        processed_results = []

        for result in search_results:
            # 日本語ブーストの適用
            if query_analysis.japanese_features.get(
                "has_japanese", False
            ) and result.japanese_enhancement.get("enhancement_applied", False):
                boost_score = result.japanese_enhancement.get("boost_score", 1.0)
                result.relevance_score *= boost_score

            # ビジネス文脈ブーストの適用
            if query_analysis.japanese_features.get("has_business_terms", False):
                business_features = result.japanese_enhancement.get(
                    "business_features", {}
                )
                if business_features:
                    business_boost = business_features.get("boost_score", 1.0)
                    result.relevance_score *= business_boost

            # コンテンツの切り詰め（表示用）
            if len(result.content) > 500:
                result.content = result.content[:500] + "..."

            processed_results.append(result)

        # 最終スコアでソート
        processed_results.sort(key=lambda x: x.relevance_score, reverse=True)

        return processed_results

    def get_search_suggestions(self, partial_query: str) -> list[str]:
        """検索サジェスト生成"""

        suggestions = []

        # 日本語キーワードサジェスト
        if self.search_index.semantic_index:
            keyword_index = self.search_index.semantic_index.japanese_keyword_index

            for keyword in keyword_index:
                if keyword.startswith(partial_query) and len(keyword) > len(
                    partial_query
                ):
                    suggestions.append(keyword)

        # ビジネス用語サジェスト
        business_terms = [
            "売上高",
            "純利益",
            "営業利益",
            "株式会社",
            "従業員数",
            "年度",
            "四半期",
            "ROI",
            "KPI",
            "EBITDA",
        ]

        for term in business_terms:
            if term.startswith(partial_query):
                suggestions.append(term)

        # 最大10件まで
        return suggestions[:10]

    def get_query_statistics(self) -> dict[str, Any]:
        """クエリ処理統計取得"""

        return {
            "total_indexed_chunks": self.search_index.total_chunks,
            "vector_index_available": self.search_index.vector_index is not None,
            "semantic_index_available": self.search_index.semantic_index is not None,
            "facet_index_available": self.search_index.facet_index is not None,
            "hybrid_search_enabled": self.search_index.hybrid_index is not None,
            "japanese_optimization_enabled": True,
            "supported_search_methods": [
                "vector_similarity",
                "semantic_search",
                "faceted_search",
                "hybrid_search",
            ],
        }
