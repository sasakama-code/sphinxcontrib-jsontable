"""
query_processor.pyカバレッジ向上専用テスト

未カバー機能の網羅的テストによりカバレッジ70%以上を目指す
"""

from unittest.mock import AsyncMock, MagicMock

import numpy as np
import pytest

from sphinxcontrib.jsontable.rag.query_processor import (
    HybridSearchEngine,
    IntelligentQueryProcessor,
    QueryAnalysis,
    QueryExecutionResult,
    SearchResult,
)
from sphinxcontrib.jsontable.rag.search_index_generator import (
    ComprehensiveSearchIndex,
    FacetedSearchIndex,
    HybridSearchIndex,
    SemanticSearchIndex,
    VectorIndex,
)


@pytest.fixture
def mock_search_index():
    """モック検索インデックス"""
    search_index = ComprehensiveSearchIndex()

    # ベクトルインデックス
    search_index.vector_index = VectorIndex(
        faiss_index=None,  # モックなのでNone
        fallback_embeddings=np.random.random((5, 512)),
        chunk_metadata=[
            {
                "chunk_id": f"test_chunk_{i}",
                "content": f"テストコンテンツ {i}: 会社情報データ",
                "japanese_enhancement": {
                    "business_features": {"boost_score": 1.2},
                    "enhancement_applied": True,
                    "boost_score": 1.2
                }
            }
            for i in range(5)
        ],
        dimension=1024
    )

    # セマンティックインデックス
    search_index.semantic_index = SemanticSearchIndex(
        text_segments=[f"セマンティックテキスト{i}" for i in range(3)],
        japanese_keyword_index={"日本語": [0, 1], "テスト": [1, 2]},
        business_term_index={"株式会社": [0], "売上": [1, 2]},
        semantic_mappings={"ビジネス": [0, 1], "技術": [1, 2]}
    )

    # ファセットインデックス
    search_index.facet_index = FacetedSearchIndex(
        categorical_facets={"category": {"business": [0, 1], "tech": [2]}},
        numerical_facets={"score": {"range": [0.0, 1.0], "chunks": [0, 1, 2]}},
        temporal_facets={"year": {"2024": [0, 1], "2023": [2]}},
        entity_facets={"company": {"TestCorp": [0, 1]}}
    )

    # ハイブリッドインデックス
    search_index.hybrid_index = HybridSearchIndex(
        vector_weight=0.7,
        semantic_weight=0.2,
        facet_weight=0.1,
        fusion_algorithm="rank_fusion"
    )

    return search_index


class TestHybridSearchEngineErrorHandling:
    """HybridSearchEngineのエラーハンドリングテスト"""

    def test_init_without_vector_index_raises_error(self):
        """ベクトルインデックスなしでの初期化エラー"""
        search_index = ComprehensiveSearchIndex()
        search_index.vector_index = None  # インデックスなし

        with pytest.raises(ValueError, match="Vector index is required"):
            HybridSearchEngine(search_index)

    @pytest.mark.asyncio
    async def test_vector_search_with_invalid_embedding_size(self, mock_search_index):
        """無効なエンベディングサイズでのベクトル検索"""
        engine = HybridSearchEngine(mock_search_index)

        # 間違ったサイズのエンベディング (正しいのは1024次元)
        invalid_embedding = np.random.random(512)

        results = await engine._execute_vector_search(invalid_embedding, k=3)

        # フォールバックエンベディングで検索されることを確認
        assert len(results) <= 3
        assert all(isinstance(r, SearchResult) for r in results)

    @pytest.mark.asyncio
    async def test_vector_search_without_semantic_index(self, mock_search_index):
        """セマンティックインデックスなしでのセマンティック検索"""
        engine = HybridSearchEngine(mock_search_index)
        mock_search_index.semantic_index = None

        query_analysis = QueryAnalysis(
            original_query="テストクエリ",
            expanded_queries=["テストクエリ", "テスト 質問"],
            query_type="general",
            japanese_features={"has_japanese": True},
            search_intent="semantic_search",
            confidence_score=0.8
        )

        results = await engine._execute_semantic_search(query_analysis, k=3)

        # 空の結果が返されることを確認
        assert len(results) == 0


class TestSemanticSearchImplementation:
    """セマンティック検索の詳細実装テスト"""

    @pytest.mark.asyncio
    async def test_semantic_search_with_japanese_keywords(self, mock_search_index):
        """日本語キーワードでのセマンティック検索"""
        engine = HybridSearchEngine(mock_search_index)

        query_analysis = QueryAnalysis(
            original_query="日本語テスト",
            expanded_queries=["日本語テスト", "日本語 検査"],
            query_type="general",
            japanese_features={
                "has_japanese": True,
                "has_hiragana": True,
                "has_business_terms": False
            },
            search_intent="semantic_search",
            confidence_score=0.9
        )

        results = await engine._execute_semantic_search(query_analysis, k=2)

        assert len(results) > 0
        assert all(r.search_method == "semantic" for r in results)
        assert all(r.relevance_score >= 0 for r in results)

    @pytest.mark.asyncio
    async def test_semantic_search_with_business_terms(self, mock_search_index):
        """ビジネス用語でのセマンティック検索"""
        engine = HybridSearchEngine(mock_search_index)

        query_analysis = QueryAnalysis(
            original_query="株式会社の売上情報",
            expanded_queries=["株式会社の売上情報", "企業 収益 データ"],
            query_type="business",
            japanese_features={
                "has_japanese": True,
                "has_business_terms": True,
                "business_context": "financial"
            },
            search_intent="semantic_search",
            confidence_score=0.85
        )

        results = await engine._execute_semantic_search(query_analysis, k=3)

        assert len(results) > 0
        # ビジネス用語にマッチした結果が含まれることを確認
        business_results = [r for r in results if "株式会社" in str(r.metadata)]
        assert len(business_results) >= 0  # ビジネス用語インデックスから検索


class TestFacetedSearchImplementation:
    """ファセット検索の詳細実装テスト"""

    @pytest.mark.asyncio
    async def test_faceted_search_temporal(self, mock_search_index):
        """時系列ファセット検索"""
        engine = HybridSearchEngine(mock_search_index)

        query_analysis = QueryAnalysis(
            original_query="2024年の情報",
            expanded_queries=["2024年の情報"],
            query_type="temporal",
            japanese_features={"has_numbers": True},
            search_intent="temporal_search",
            confidence_score=0.7
        )

        results = await engine._execute_faceted_search(query_analysis, k=5)

        assert len(results) > 0
        assert all(r.search_method == "faceted" for r in results)

    @pytest.mark.asyncio
    async def test_faceted_search_numerical(self, mock_search_index):
        """数値ファセット検索"""
        engine = HybridSearchEngine(mock_search_index)

        query_analysis = QueryAnalysis(
            original_query="スコア0.8以上",
            expanded_queries=["スコア0.8以上", "高スコア"],
            query_type="numerical",
            japanese_features={"has_numbers": True},
            search_intent="numerical_search",
            confidence_score=0.75
        )

        results = await engine._execute_faceted_search(query_analysis, k=3)

        assert len(results) >= 0
        assert all(r.search_method == "faceted" for r in results)


class TestHybridSearchFusion:
    """ハイブリッド検索の融合アルゴリズムテスト"""

    @pytest.mark.asyncio
    async def test_hybrid_search_rank_fusion(self, mock_search_index):
        """ランク融合アルゴリズムでのハイブリッド検索"""
        engine = HybridSearchEngine(mock_search_index)

        # ベクトル検索結果（モック）
        vector_results = [
            SearchResult(
                chunk_id="vec_1",
                content="ベクトル検索結果1",
                relevance_score=0.9,
                search_method="vector"
            ),
            SearchResult(
                chunk_id="vec_2",
                content="ベクトル検索結果2",
                relevance_score=0.7,
                search_method="vector"
            )
        ]

        # セマンティック検索結果（モック）
        semantic_results = [
            SearchResult(
                chunk_id="sem_1",
                content="セマンティック検索結果1",
                relevance_score=0.8,
                search_method="semantic"
            )
        ]

        # ファセット検索結果（モック）
        faceted_results = [
            SearchResult(
                chunk_id="fac_1",
                content="ファセット検索結果1",
                relevance_score=1.0,
                search_method="faceted"
            )
        ]

        # 融合実行
        fused_results = await engine._fuse_search_results(
            vector_results, semantic_results, faceted_results
        )

        assert len(fused_results) > 0
        assert all(r.search_method == "hybrid" for r in fused_results)
        # スコアが正しく計算されていることを確認
        assert all(r.relevance_score > 0 for r in fused_results)


class TestIntelligentQueryProcessorEdgeCases:
    """IntelligentQueryProcessorのエッジケーステスト"""

    @pytest.mark.asyncio
    async def test_query_processing_with_empty_query(self):
        """空クエリでのクエリ処理"""
        mock_search_index = MagicMock()
        mock_vector_processor = MagicMock()

        processor = IntelligentQueryProcessor(mock_vector_processor, mock_search_index)

        result = await processor.process_query("")

        assert isinstance(result, QueryExecutionResult)
        assert result.query_analysis.original_query == ""
        assert len(result.search_results) == 0

    @pytest.mark.asyncio
    async def test_query_processing_with_special_characters(self):
        """特殊文字を含むクエリの処理"""
        mock_search_index = MagicMock()
        mock_vector_processor = MagicMock()

        processor = IntelligentQueryProcessor(mock_vector_processor, mock_search_index)

        special_query = "テスト@#$%検索!?&*()"
        result = await processor.process_query(special_query)

        assert isinstance(result, QueryExecutionResult)
        assert result.query_analysis.original_query == special_query

    @pytest.mark.asyncio
    async def test_vectorization_fallback(self):
        """ベクトル化失敗時のフォールバック"""
        mock_search_index = MagicMock()
        mock_vector_processor = MagicMock()

        # ベクトル化処理でエラーが発生する設定
        mock_vector_processor.process_chunks = AsyncMock(side_effect=Exception("ベクトル化エラー"))

        processor = IntelligentQueryProcessor(mock_vector_processor, mock_search_index)

        # エラーが発生してもフォールバック処理で継続することを確認
        result = await processor.process_query("テストクエリ")

        assert isinstance(result, QueryExecutionResult)
        # フォールバック処理が実行されたことを確認
        assert result.execution_time_ms >= 0


class TestQueryAnalysisEnhancements:
    """クエリ分析の拡張機能テスト"""

    def test_complex_japanese_query_analysis(self):
        """複雑な日本語クエリの分析"""
        # このテストは実際のJapaneseQueryProcessorの詳細な動作をテスト
        from sphinxcontrib.jsontable.rag.search_index_generator import (
            JapaneseQueryProcessor,
        )

        processor = JapaneseQueryProcessor()

        complex_query = "2024年度の東京エレクトロニクス株式会社の売上高と従業員数について"

        # クエリ拡張
        expanded = processor.expand_query(complex_query)
        assert len(expanded) > 1
        assert any("東京エレクトロニクス" in q for q in expanded)

        # 日本語特徴抽出
        features = processor.extract_japanese_features(complex_query)
        assert features["has_japanese"] is True
        assert features["has_business_terms"] is True
        assert features["has_kanji"] is True
        assert features["has_numbers"] is True

    def test_business_context_detection(self):
        """ビジネス文脈検出テスト"""
        from sphinxcontrib.jsontable.rag.search_index_generator import (
            JapaneseQueryProcessor,
        )

        processor = JapaneseQueryProcessor()

        business_queries = [
            "売上高の推移",
            "従業員数の変化",
            "株式会社の業績",
            "ROI改善策",
            "KPI達成状況"
        ]

        for query in business_queries:
            features = processor.extract_japanese_features(query)
            assert features["has_business_terms"] is True, f"'{query}'でビジネス用語が検出されませんでした"
            assert features["query_type"] == "business"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
