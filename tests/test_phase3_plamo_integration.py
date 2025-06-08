"""
Phase 3: PLaMo-Embedding-1B統合テスト

Phase 3で実装されたPLaMoVectorProcessor、SearchIndexGenerator、
QueryProcessorの統合動作を包括的に検証
"""

import pytest

from sphinxcontrib.jsontable.rag.metadata_extractor import BasicMetadata
from sphinxcontrib.jsontable.rag.query_processor import (
    IntelligentQueryProcessor,
    QueryExecutionResult,
    QueryIntentClassifier,
    SearchResult,
)
from sphinxcontrib.jsontable.rag.search_index_generator import (
    ComprehensiveSearchIndex,
    FacetedSearchIndex,
    JapaneseQueryProcessor,
    SearchIndexGenerator,
    SemanticSearchIndex,
    VectorIndex,
)
from sphinxcontrib.jsontable.rag.semantic_chunker import SemanticChunk
from sphinxcontrib.jsontable.rag.vector_processor import (
    BusinessTermEnhancer,
    JapaneseTextNormalizer,
    PLaMoVectorProcessor,
    VectorChunk,
    VectorProcessingResult,
)


@pytest.fixture
def sample_japanese_business_data():
    """日本語ビジネスデータサンプル"""
    return [
        {
            "会社名": "東京エレクトロニクス株式会社",
            "年度": "2024年度",
            "売上高": "850億円",
            "従業員数": "2,800名",
            "主要事業": "半導体製造装置開発・販売",
        },
        {
            "会社名": "大阪商事株式会社",
            "年度": "2024年度",
            "売上高": "320億円",
            "従業員数": "1,200名",
            "主要事業": "総合商社・貿易業務",
        },
        {
            "会社名": "名古屋自動車工業株式会社",
            "年度": "2024年度",
            "売上高": "1,250億円",
            "従業員数": "5,600名",
            "主要事業": "自動車部品製造・開発",
        },
        {
            "会社名": "福岡ソフトウェア株式会社",
            "年度": "2024年度",
            "売上高": "180億円",
            "従業員数": "800名",
            "主要事業": "システム開発・IT企業",
        },
    ]


@pytest.fixture
def semantic_chunks_from_business_data(sample_japanese_business_data):
    """ビジネスデータからSemanticChunk生成"""
    chunks = []

    for i, company_data in enumerate(sample_japanese_business_data):
        # 会社情報チャンク
        company_content = f"{company_data['会社名']}は{company_data['年度']}に{company_data['売上高']}の売上を記録。従業員数は{company_data['従業員数']}で、{company_data['主要事業']}を主力事業としている。"

        chunk = SemanticChunk(
            chunk_id=f"company_{i}",
            content=company_content,
            chunk_type="business_summary",
            embedding_hint="japanese_business_data",
            metadata={
                "table_context": {
                    "table_name": "企業情報",
                    "row_index": i,
                    "column_context": list(company_data.keys()),
                },
                "semantic_context": {
                    "chunk_type": "business_summary",
                    "company_name": company_data["会社名"],
                    "fiscal_year": company_data["年度"],
                },
            },
            search_weight=1.0,
        )
        chunks.append(chunk)

        # 財務情報チャンク
        financial_content = f"{company_data['会社名']}の財務実績：{company_data['年度']}売上高{company_data['売上高']}、従業員一人当たり売上は優秀な水準を維持。"  # noqa: RUF001

        financial_chunk = SemanticChunk(
            chunk_id=f"financial_{i}",
            content=financial_content,
            chunk_type="financial_data",
            embedding_hint="japanese_financial_data",
            metadata={
                "table_context": {
                    "table_name": "企業情報",
                    "row_index": i,
                    "column_context": ["会社名", "年度", "売上高", "従業員数"],
                },
                "semantic_context": {
                    "chunk_type": "financial_data",
                    "company_name": company_data["会社名"],
                    "fiscal_year": company_data["年度"],
                },
            },
            search_weight=1.2,  # 財務情報はやや重要度高
        )
        chunks.append(financial_chunk)

    return chunks


@pytest.fixture
def basic_metadata_sample():
    """BasicMetadataサンプル"""
    return BasicMetadata(
        table_id="test_business_table",
        schema={
            "会社名": {"type": "string", "examples": ["東京エレクトロニクス株式会社"]},
            "年度": {"type": "string", "examples": ["2024年度"]},
            "売上高": {"type": "string", "examples": ["850億円"]},
            "従業員数": {"type": "string", "examples": ["2,800名"]},
            "主要事業": {"type": "string", "examples": ["半導体製造装置開発・販売"]},
        },
        semantic_summary="日本企業の基本情報と財務データを含む企業情報テーブル",
        search_keywords=["企業情報", "売上高", "従業員数", "主要事業"],
        entity_mapping={"organization": "会社名", "financial": "売上高"},
        custom_tags=["japanese_business", "financial_data"],
        data_statistics={"total_rows": 4, "total_columns": 5},
        embedding_ready_text="日本企業の基本情報と財務データを含む企業情報テーブル。会社名、年度、売上高、従業員数、主要事業の情報を記録。",
        generation_timestamp="2025-06-07T10:00:00",
    )


class TestJapaneseTextNormalizer:
    """日本語テキスト正規化テスト"""

    def test_unicode_normalization(self):
        """Unicode正規化テスト"""
        normalizer = JapaneseTextNormalizer()

        # 全角英数字を半角に変換
        text = "株式会社ＡＢＣ１２３"
        normalized = normalizer.normalize(text)
        assert "ABC123" in normalized

    def test_business_term_normalization(self):
        """ビジネス用語正規化テスト"""
        normalizer = JapaneseTextNormalizer()

        # 株式会社表記の統一
        text = "㈱テスト会社"
        normalized = normalizer.normalize(text)
        assert "株式会社" in normalized

        # 年度表記の正規化
        text = "2024年度売上"
        normalized = normalizer.normalize(text)
        assert "2024年度" in normalized


class TestBusinessTermEnhancer:
    """ビジネス用語強化テスト"""

    def test_business_term_enhancement(self):
        """ビジネス用語強化テスト"""
        enhancer = BusinessTermEnhancer()

        text = "株式会社テスト企業の売上高は1000万円"
        enhanced = enhancer.enhance(text)

        # 組織マーカーの確認
        assert "[組織]" in enhanced
        assert "[財務]" in enhanced

    def test_business_feature_extraction(self):
        """ビジネス特徴抽出テスト"""
        enhancer = BusinessTermEnhancer()

        text = "営業部の田中部長が発表した2024年度売上は5億円"
        features = enhancer.extract_business_features(text)

        assert "organization" in features["categories"]
        assert "position" in features["categories"]
        assert "financial" in features["categories"]
        assert "temporal" in features["categories"]
        assert features["boost_score"] > 1.0


class TestPLaMoVectorProcessor:
    """PLaMoVectorProcessorテスト"""

    @pytest.mark.asyncio
    async def test_vector_processing_basic(self, semantic_chunks_from_business_data):
        """基本的なベクトル処理テスト"""
        processor = PLaMoVectorProcessor()

        chunks = semantic_chunks_from_business_data[:2]  # 最初の2つのチャンク

        result = await processor.process_chunks(chunks)

        assert isinstance(result, VectorProcessingResult)
        assert len(result.vector_chunks) == 2
        assert result.japanese_optimization_applied is True

        # ベクトルの基本検証
        for vector_chunk in result.vector_chunks:
            assert isinstance(vector_chunk, VectorChunk)
            assert vector_chunk.embedding.shape == (1024,)  # PLaMo dimension
            assert vector_chunk.search_boost > 0
            assert vector_chunk.japanese_enhancement["enhancement_applied"] is True

    @pytest.mark.asyncio
    async def test_japanese_enhancement_application(
        self, semantic_chunks_from_business_data
    ):
        """日本語強化適用テスト"""
        processor = PLaMoVectorProcessor()

        # ビジネス用語を多く含むチャンクを選択
        business_chunk = semantic_chunks_from_business_data[0]  # 会社情報チャンク

        result = await processor.process_chunks([business_chunk])
        vector_chunk = result.vector_chunks[0]

        # 日本語強化の確認
        assert vector_chunk.japanese_enhancement["enhancement_applied"] is True

        business_features = vector_chunk.japanese_enhancement["business_features"]
        assert "categories" in business_features
        assert business_features["boost_score"] > 1.0

    @pytest.mark.asyncio
    async def test_batch_processing_performance(
        self, semantic_chunks_from_business_data
    ):
        """バッチ処理性能テスト"""
        processor = PLaMoVectorProcessor()

        chunks = semantic_chunks_from_business_data  # 全8チャンク

        import time

        start_time = time.time()

        result = await processor.process_chunks(chunks)

        processing_time = time.time() - start_time

        # 性能要件確認
        assert processing_time < 10.0  # 10秒以内で完了
        assert len(result.vector_chunks) == len(chunks)
        assert result.processing_stats["success_rate"] == 1.0

    def test_processing_stats_tracking(self):
        """処理統計追跡テスト"""
        processor = PLaMoVectorProcessor()

        # 初期統計確認
        stats = processor.get_processing_stats()
        assert stats["total_processed"] == 0
        assert stats["success_rate"] == 0.0


class TestSearchIndexGenerator:
    """SearchIndexGeneratorテスト"""

    @pytest.mark.asyncio
    async def test_comprehensive_index_generation(
        self, semantic_chunks_from_business_data, basic_metadata_sample
    ):
        """包括的インデックス生成テスト"""
        # まずベクトル処理
        vector_processor = PLaMoVectorProcessor()
        vector_result = await vector_processor.process_chunks(
            semantic_chunks_from_business_data
        )

        # インデックス生成
        generator = SearchIndexGenerator()
        search_index = generator.generate_comprehensive_index(
            vector_result.vector_chunks, basic_metadata_sample
        )

        assert isinstance(search_index, ComprehensiveSearchIndex)
        assert search_index.total_chunks == len(vector_result.vector_chunks)

        # 各インデックスの確認
        assert search_index.vector_index is not None
        assert search_index.semantic_index is not None
        assert search_index.facet_index is not None
        assert search_index.hybrid_index is not None

    @pytest.mark.asyncio
    async def test_vector_index_construction(self, semantic_chunks_from_business_data):
        """ベクトルインデックス構築テスト"""
        vector_processor = PLaMoVectorProcessor()
        vector_result = await vector_processor.process_chunks(
            semantic_chunks_from_business_data
        )

        generator = SearchIndexGenerator()
        vector_index = generator._build_vector_index(vector_result.vector_chunks)

        assert isinstance(vector_index, VectorIndex)
        assert vector_index.dimension == 1024
        assert len(vector_index.chunk_metadata) == len(vector_result.vector_chunks)

        # FAISS or フォールバックインデックスの確認
        assert vector_index.index_type in ["faiss_flatip", "fallback_cosine"]

    @pytest.mark.asyncio
    async def test_semantic_index_construction(
        self, semantic_chunks_from_business_data
    ):
        """セマンティックインデックス構築テスト"""
        vector_processor = PLaMoVectorProcessor()
        vector_result = await vector_processor.process_chunks(
            semantic_chunks_from_business_data
        )

        generator = SearchIndexGenerator()
        semantic_index = generator._build_semantic_index(vector_result.vector_chunks)

        assert isinstance(semantic_index, SemanticSearchIndex)
        assert len(semantic_index.text_segments) == len(vector_result.vector_chunks)

        # 日本語キーワードインデックスの確認
        assert len(semantic_index.japanese_keyword_index) > 0

        # ビジネス用語インデックスの確認
        assert len(semantic_index.business_term_index) > 0

        # 日本語企業名が正しくインデックスされているか
        business_terms = semantic_index.business_term_index.keys()
        japanese_companies = [term for term in business_terms if "株式会社" in term]
        assert len(japanese_companies) > 0

    @pytest.mark.asyncio
    async def test_faceted_index_construction(
        self, semantic_chunks_from_business_data, basic_metadata_sample
    ):
        """ファセットインデックス構築テスト"""
        vector_processor = PLaMoVectorProcessor()
        vector_result = await vector_processor.process_chunks(
            semantic_chunks_from_business_data
        )

        generator = SearchIndexGenerator()
        facet_index = generator._build_facet_index(
            vector_result.vector_chunks, basic_metadata_sample
        )

        assert isinstance(facet_index, FacetedSearchIndex)

        # カテゴリファセットの確認
        assert "data_type" in facet_index.categorical_facets
        assert "business_category" in facet_index.categorical_facets

        # 数値ファセットの確認
        assert "amount_range" in facet_index.numerical_facets

        # 時間ファセットの確認
        assert "fiscal_year" in facet_index.temporal_facets

        # エンティティファセットの確認
        assert "organization" in facet_index.entity_facets


class TestJapaneseQueryProcessor:
    """日本語クエリ処理テスト"""

    def test_query_expansion(self):
        """クエリ拡張テスト"""
        processor = JapaneseQueryProcessor()

        query = "会社の売上情報"
        expanded = processor.expand_query(query)

        assert len(expanded) > 1
        assert query in expanded  # 元のクエリも含まれる

        # 同義語展開の確認
        expanded_text = " ".join(expanded)
        assert "企業" in expanded_text or "法人" in expanded_text
        assert "収益" in expanded_text or "売上高" in expanded_text

    def test_japanese_feature_extraction(self):
        """日本語特徴抽出テスト"""
        processor = JapaneseQueryProcessor()

        # 日本語ビジネスクエリ
        query = "株式会社の2024年度売上高を検索"
        features = processor.extract_japanese_features(query)

        assert features["has_hiragana"] is True
        assert features["has_kanji"] is True
        assert features["has_numbers"] is True
        assert features["has_business_terms"] is True
        assert features["query_type"] == "business"


class TestQueryIntentClassifier:
    """クエリ意図分類テスト"""

    def test_intent_classification(self):
        """意図分類テスト"""
        classifier = QueryIntentClassifier()

        # 類似検索意図
        similarity_query = "これに似ている会社を探して"
        intent, confidence = classifier.classify_intent(similarity_query)
        assert intent == "similarity_search"
        assert confidence > 0

        # ファセット検索意図
        faceted_query = "2024年度で売上が1000億円以上の会社"
        intent, confidence = classifier.classify_intent(faceted_query)
        assert intent in ["faceted_search", "numerical_search", "temporal_search"]

    def test_business_context_classification(self):
        """ビジネス文脈分類テスト"""
        classifier = QueryIntentClassifier()

        # 財務文脈
        financial_query = "売上高と利益の情報"
        context = classifier.classify_business_context(financial_query)
        assert context == "financial"

        # 組織文脈
        organizational_query = "従業員数と組織構造"
        context = classifier.classify_business_context(organizational_query)
        assert context == "organizational"


class TestIntelligentQueryProcessor:
    """IntelligentQueryProcessor統合テスト"""

    @pytest.mark.asyncio
    async def test_complete_query_processing_pipeline(
        self, semantic_chunks_from_business_data, basic_metadata_sample
    ):
        """完全なクエリ処理パイプラインテスト"""
        # Phase 3コンポーネント統合
        vector_processor = PLaMoVectorProcessor()
        vector_result = await vector_processor.process_chunks(
            semantic_chunks_from_business_data
        )

        generator = SearchIndexGenerator()
        search_index = generator.generate_comprehensive_index(
            vector_result.vector_chunks, basic_metadata_sample
        )

        query_processor = IntelligentQueryProcessor(vector_processor, search_index)

        # 日本語ビジネスクエリで検索
        query = "東京エレクトロニクス株式会社に類似する会社"
        result = await query_processor.process_query(query)

        assert isinstance(result, QueryExecutionResult)
        assert len(result.search_results) > 0
        assert result.execution_time_ms > 0

        # クエリ分析結果の確認
        assert result.query_analysis.query_type == "business"
        assert result.query_analysis.japanese_features["has_business_terms"] is True

        # 検索結果の確認
        for search_result in result.search_results:
            assert isinstance(search_result, SearchResult)
            assert search_result.relevance_score > 0
            assert len(search_result.content) > 0

    @pytest.mark.asyncio
    async def test_japanese_business_query_optimization(
        self, semantic_chunks_from_business_data, basic_metadata_sample
    ):
        """日本語ビジネスクエリ最適化テスト"""
        vector_processor = PLaMoVectorProcessor()
        vector_result = await vector_processor.process_chunks(
            semantic_chunks_from_business_data
        )

        generator = SearchIndexGenerator()
        search_index = generator.generate_comprehensive_index(
            vector_result.vector_chunks, basic_metadata_sample
        )

        query_processor = IntelligentQueryProcessor(vector_processor, search_index)

        # 複数の日本語ビジネスクエリでテスト
        test_queries = [
            "売上高が高い会社",
            "2024年度の業績情報",
            "株式会社の従業員数",
            "製造業の企業情報",
        ]

        for query in test_queries:
            result = await query_processor.process_query(query)

            # 基本的な結果確認
            assert len(result.search_results) > 0
            assert result.query_analysis.japanese_features["has_business_terms"] is True

            # 実行時間確認（10秒以内）
            assert result.execution_time_ms < 10000

    def test_search_suggestions(
        self, semantic_chunks_from_business_data, basic_metadata_sample
    ):
        """検索サジェストテスト"""
        # 簡易インデックス作成
        search_index = ComprehensiveSearchIndex()
        search_index.semantic_index = SemanticSearchIndex()
        search_index.semantic_index.japanese_keyword_index = {
            "売上高": [0, 1],
            "株式会社": [0, 1, 2],
            "従業員": [0, 1, 2],
        }

        vector_processor = PLaMoVectorProcessor()
        query_processor = IntelligentQueryProcessor(vector_processor, search_index)

        # 部分クエリでサジェスト取得
        suggestions = query_processor.get_search_suggestions("売")
        assert "売上高" in suggestions

        suggestions = query_processor.get_search_suggestions("株")
        assert "株式会社" in suggestions


class TestPhase3Integration:
    """Phase 3完全統合テスト"""

    @pytest.mark.asyncio
    async def test_end_to_end_japanese_rag_pipeline(
        self, sample_japanese_business_data
    ):
        """エンドツーエンド日本語RAGパイプラインテスト"""

        # Step 1: データからSemanticChunk生成
        chunks = []
        for i, company in enumerate(sample_japanese_business_data):
            content = f"{company['会社名']}（{company['年度']}）: 売上{company['売上高']}、従業員{company['従業員数']}、事業：{company['主要事業']}"  # noqa: RUF001

            chunk = SemanticChunk(
                chunk_id=f"company_{i}",
                content=content,
                chunk_type="business_info",
                metadata={"company": company},
                search_weight=1.0,
                embedding_hint="structured_data_record",
            )
            chunks.append(chunk)

        # Step 2: ベクトル処理
        vector_processor = PLaMoVectorProcessor()
        vector_result = await vector_processor.process_chunks(chunks)

        # Step 3: 検索インデックス構築
        generator = SearchIndexGenerator()
        search_index = generator.generate_comprehensive_index(
            vector_result.vector_chunks
        )

        # Step 4: クエリ処理エンジン初期化
        query_processor = IntelligentQueryProcessor(vector_processor, search_index)

        # Step 5: 複数クエリでの総合テスト
        test_scenarios = [
            {
                "query": "半導体関連企業",
                "expected_match": "東京エレクトロニクス",
                "search_type": "semantic",
            },
            {
                "query": "売上1000億円以上の会社",
                "expected_match": "名古屋自動車工業",
                "search_type": "numerical",
            },
            {
                "query": "IT企業の情報",
                "expected_match": "福岡ソフトウェア",
                "search_type": "business_category",
            },
        ]

        results_summary = []

        for scenario in test_scenarios:
            result = await query_processor.process_query(scenario["query"])

            # 基本検証
            assert len(result.search_results) > 0
            assert result.execution_time_ms < 5000  # 5秒以内

            # 期待する結果の確認
            found_expected = any(
                scenario["expected_match"] in search_result.content
                for search_result in result.search_results
            )

            results_summary.append(
                {
                    "query": scenario["query"],
                    "found_expected": found_expected,
                    "result_count": len(result.search_results),
                    "execution_time": result.execution_time_ms,
                }
            )

        # 全体結果検証
        successful_queries = sum(1 for r in results_summary if r["found_expected"])
        assert successful_queries >= 2  # 少なくとも2/3のクエリで期待結果取得

        # パフォーマンス検証
        avg_execution_time = sum(r["execution_time"] for r in results_summary) / len(
            results_summary
        )
        assert avg_execution_time < 3000  # 平均3秒以内

    @pytest.mark.asyncio
    async def test_phase3_performance_benchmarks(
        self, semantic_chunks_from_business_data
    ):
        """Phase 3パフォーマンスベンチマーク"""

        # 大規模データセット生成（元データを拡張）
        extended_chunks = []
        for i in range(100):  # 800チャンク生成（8 × 100）
            for j, chunk in enumerate(semantic_chunks_from_business_data):
                new_chunk = SemanticChunk(
                    chunk_id=f"extended_{i}_{j}",
                    content=chunk.content + f" (拡張データ{i})",
                    chunk_type=chunk.chunk_type,
                    embedding_hint=chunk.embedding_hint,
                    metadata=chunk.metadata.copy(),
                    search_weight=chunk.search_weight,
                )
                extended_chunks.append(new_chunk)

        # パフォーマンステスト実行
        import time

        # ベクトル処理性能
        vector_processor = PLaMoVectorProcessor()

        start_time = time.time()
        vector_result = await vector_processor.process_chunks(extended_chunks)
        vector_processing_time = time.time() - start_time

        # インデックス構築性能
        generator = SearchIndexGenerator()

        start_time = time.time()
        search_index = generator.generate_comprehensive_index(
            vector_result.vector_chunks
        )
        index_generation_time = time.time() - start_time

        # クエリ処理性能
        query_processor = IntelligentQueryProcessor(vector_processor, search_index)

        query_times = []
        test_queries = [
            "株式会社の情報",
            "売上高データ",
            "従業員数統計",
            "2024年度業績",
        ]

        for query in test_queries:
            start_time = time.time()
            await query_processor.process_query(query)
            query_time = time.time() - start_time
            query_times.append(query_time)

        # パフォーマンス基準検証
        assert vector_processing_time < 300  # 5分以内（800チャンク）
        assert index_generation_time < 30  # 30秒以内
        assert max(query_times) < 2.0  # 最大2秒以内
        assert sum(query_times) / len(query_times) < 1.0  # 平均1秒以内

        # 成功率検証（get_processing_stats()メソッドで計算された値を使用）
        stats = vector_processor.get_processing_stats()
        assert stats["success_rate"] == 1.0
        assert len(search_index.vector_index.chunk_metadata) == len(extended_chunks)

    def test_phase3_quality_assurance(self):
        """Phase 3品質保証テスト"""

        # 各コンポーネントの初期化成功確認
        vector_processor = PLaMoVectorProcessor()
        assert vector_processor is not None

        generator = SearchIndexGenerator()
        assert generator is not None

        japanese_processor = JapaneseQueryProcessor()
        assert japanese_processor is not None

        intent_classifier = QueryIntentClassifier()
        assert intent_classifier is not None

        # 設定の整合性確認
        config = vector_processor.config
        assert config["model"]["dimension"] == 1024  # PLaMo仕様
        assert config["model"]["japanese_preprocessing"] is True
        assert config["optimization"]["japanese_boost"] > 1.0

        # 日本語処理機能の確認
        normalizer = JapaneseTextNormalizer()
        enhancer = BusinessTermEnhancer()

        test_text = "株式会社ＴＥＳＴの2024年度売上高は１００億円"  # noqa: RUF001
        normalized = normalizer.normalize(test_text)
        enhanced = enhancer.enhance(normalized)

        assert "TEST" in normalized  # 全角→半角変換
        assert "100億円" in normalized  # 全角数字→半角変換
        assert "[組織]" in enhanced or "[財務]" in enhanced  # ビジネス用語マーカー
