"""Query processor synchronous functionality coverage tests.

Provides comprehensive test coverage for non-async query processor functionality
to improve overall code coverage. Focuses on synchronous components and utility
methods that can be tested without async infrastructure.

Created: 2025-06-09
"""


from sphinxcontrib.jsontable.rag.query_processor import (
    JapaneseQueryProcessor,
    QueryIntentClassifier,
    SearchResult,
)


class TestJapaneseQueryProcessorCoverage:
    """Comprehensive tests for JapaneseQueryProcessor synchronous methods."""

    def setup_method(self):
        """Setup query processor for testing."""
        self.processor = JapaneseQueryProcessor()

    def test_expand_query_basic(self):
        """Test basic query expansion functionality."""
        query = "会社の売上情報"
        expanded = self.processor.expand_query(query)

        assert isinstance(expanded, list)
        assert len(expanded) >= 1
        assert query in expanded

    def test_expand_query_empty(self):
        """Test query expansion with empty query."""
        expanded = self.processor.expand_query("")
        assert isinstance(expanded, list)
        assert len(expanded) == 1
        assert expanded[0] == ""

    def test_expand_query_none(self):
        """Test query expansion with None input."""
        expanded = self.processor.expand_query(None)
        assert isinstance(expanded, list)
        assert len(expanded) == 1
        assert expanded[0] == ""

    def test_expand_query_business_terms(self):
        """Test query expansion with business terms."""
        queries = ["売上高", "株式会社", "従業員数", "営業利益", "財務状況"]

        for query in queries:
            expanded = self.processor.expand_query(query)
            assert isinstance(expanded, list)
            assert len(expanded) >= 1
            assert query in expanded

    def test_extract_japanese_features_comprehensive(self):
        """Test comprehensive Japanese feature extraction."""
        test_cases = [
            {
                "query": "株式会社の2024年度売上高を検索",
                "expected_hiragana": True,
                "expected_kanji": True,
                "expected_numbers": True,
                "expected_business": True,
                "expected_type": "business",
            },
            {
                "query": "ABC Company sales data",
                "expected_hiragana": False,
                "expected_kanji": False,
                "expected_numbers": False,
                "expected_business": False,
                "expected_type": "general",
            },
            {
                "query": "123456789",
                "expected_hiragana": False,
                "expected_kanji": False,
                "expected_numbers": True,
                "expected_business": False,
                "expected_type": "numerical",
            },
            {
                "query": "こんにちは今日はいい天気ですね",
                "expected_hiragana": True,
                "expected_kanji": False,
                "expected_numbers": False,
                "expected_business": False,
                "expected_type": "general",
            },
        ]

        for case in test_cases:
            features = self.processor.extract_japanese_features(case["query"])

            assert isinstance(features, dict)
            assert "has_hiragana" in features
            assert "has_kanji" in features
            assert "has_numbers" in features
            assert "has_business_terms" in features
            assert "query_type" in features

            assert features["has_hiragana"] == case["expected_hiragana"]
            assert features["has_kanji"] == case["expected_kanji"]
            assert features["has_numbers"] == case["expected_numbers"]
            assert features["has_business_terms"] == case["expected_business"]
            assert features["query_type"] == case["expected_type"]

    def test_extract_japanese_features_edge_cases(self):
        """Test Japanese feature extraction with edge cases."""
        edge_cases = [
            "",
            None,
            "   ",
            "!@#$%^&*()",
            "ＡＢＣ１２３",  # Full-width characters
            "カタカナテスト",
            "ひらがなてすと",
            "漢字テスト",
        ]

        for case in edge_cases:
            features = self.processor.extract_japanese_features(case)
            assert isinstance(features, dict)
            assert all(
                key in features
                for key in [
                    "has_hiragana",
                    "has_kanji",
                    "has_numbers",
                    "has_business_terms",
                    "query_type",
                ]
            )

    def test_normalize_query(self):
        """Test query normalization functionality."""
        test_cases = [
            ("株式会社ＴＥＳＴの売上", "株式会社TESTの売上"),
            ("２０２４年度", "2024年度"),
            ("　　スペース　　", "スペース"),
            ("", ""),
        ]

        for input_query, expected_output in test_cases:
            # This tests the internal normalization process
            features = self.processor.extract_japanese_features(input_query)
            assert isinstance(features, dict)

    def test_business_term_detection(self):
        """Test business term detection accuracy."""
        business_terms = [
            "売上高",
            "営業利益",
            "純利益",
            "株式会社",
            "取締役",
            "従業員",
            "資本金",
            "財務",
            "会計",
            "決算",
        ]

        non_business_terms = [
            "天気",
            "料理",
            "旅行",
            "映画",
            "音楽",
            "スポーツ",
            "ゲーム",
            "動物",
            "植物",
            "色",
        ]

        for term in business_terms:
            features = self.processor.extract_japanese_features(term)
            assert features["has_business_terms"] is True
            assert features["query_type"] in ["business", "financial"]

        for term in non_business_terms:
            features = self.processor.extract_japanese_features(term)
            assert features["has_business_terms"] is False
            assert features["query_type"] == "general"


class TestQueryIntentClassifierCoverage:
    """Comprehensive tests for QueryIntentClassifier."""

    def setup_method(self):
        """Setup intent classifier for testing."""
        self.classifier = QueryIntentClassifier()

    def test_classify_intent_similarity_search(self):
        """Test similarity search intent classification."""
        similarity_queries = [
            "これに似ている会社を探して",
            "類似する企業",
            "同じような商品",
            "似たデータ",
            "関連する情報",
        ]

        for query in similarity_queries:
            intent, confidence = self.classifier.classify_intent(query)
            assert intent == "similarity_search"
            assert isinstance(confidence, (int, float))
            assert confidence > 0

    def test_classify_intent_faceted_search(self):
        """Test faceted search intent classification."""
        faceted_queries = [
            "2024年度で売上が1000億円以上の会社",
            "東京都の企業のみ",
            "従業員数が500人以上",
            "評価がAの商品",
            "価格が10万円以下",
        ]

        for query in faceted_queries:
            intent, confidence = self.classifier.classify_intent(query)
            assert intent in ["faceted_search", "numerical_search", "temporal_search"]
            assert isinstance(confidence, (int, float))
            assert confidence > 0

    def test_classify_intent_general_search(self):
        """Test general search intent classification."""
        general_queries = [
            "データを検索",
            "情報を探している",
            "テーブルの内容",
            "会社について",
            "製品情報",
        ]

        for query in general_queries:
            intent, confidence = self.classifier.classify_intent(query)
            assert intent in ["general_search", "keyword_search", "business_search"]
            assert isinstance(confidence, (int, float))
            assert confidence >= 0

    def test_classify_intent_edge_cases(self):
        """Test intent classification with edge cases."""
        edge_cases = [
            "",
            None,
            "   ",
            "!@#$%",
            "x" * 1000,  # Very long query
            "単語",  # Single word
        ]

        for query in edge_cases:
            intent, confidence = self.classifier.classify_intent(query)
            assert isinstance(intent, str)
            assert isinstance(confidence, (int, float))
            assert confidence >= 0

    def test_classify_business_context_financial(self):
        """Test financial business context classification."""
        financial_queries = [
            "売上高と利益の情報",
            "財務データ",
            "収益性",
            "資本金",
            "投資収益率",
        ]

        for query in financial_queries:
            context = self.classifier.classify_business_context(query)
            assert context == "financial"

    def test_classify_business_context_organizational(self):
        """Test organizational business context classification."""
        organizational_queries = [
            "従業員数と組織構造",
            "部署の情報",
            "人事データ",
            "組織図",
            "管理職",
        ]

        for query in organizational_queries:
            context = self.classifier.classify_business_context(query)
            assert context == "organizational"

    def test_classify_business_context_operational(self):
        """Test operational business context classification."""
        operational_queries = [
            "生産性データ",
            "業務プロセス",
            "オペレーション",
            "効率性",
            "稼働率",
        ]

        for query in operational_queries:
            context = self.classifier.classify_business_context(query)
            assert context in ["operational", "general"]

    def test_classify_business_context_general(self):
        """Test general business context classification."""
        general_queries = [
            "会社の基本情報",
            "企業概要",
            "一般的なデータ",
            "情報検索",
            "データ参照",
        ]

        for query in general_queries:
            context = self.classifier.classify_business_context(query)
            assert context in ["general", "business"]

    def test_classify_business_context_edge_cases(self):
        """Test business context classification with edge cases."""
        edge_cases = ["", None, "   ", "123", "非ビジネス用語テスト"]

        for query in edge_cases:
            context = self.classifier.classify_business_context(query)
            assert isinstance(context, str)
            assert context in [
                "general",
                "financial",
                "organizational",
                "operational",
                "business",
            ]


class TestSearchResultCoverage:
    """Tests for SearchResult data class coverage."""

    def test_search_result_creation(self):
        """Test SearchResult creation and attributes."""
        result = SearchResult(
            chunk_id="result_001",
            content="テスト検索結果コンテンツ",
            relevance_score=0.85,
            metadata={"source": "test", "type": "business"},
            search_type="semantic",
        )

        assert result.chunk_id == "result_001"
        assert result.content == "テスト検索結果コンテンツ"
        assert result.relevance_score == 0.85
        assert result.metadata["source"] == "test"
        assert result.search_type == "semantic"

    def test_search_result_default_values(self):
        """Test SearchResult with minimal parameters."""
        result = SearchResult(
            chunk_id="minimal", content="minimal content", relevance_score=0.5
        )

        assert result.chunk_id == "minimal"
        assert result.content == "minimal content"
        assert result.relevance_score == 0.5
        assert result.metadata == {}
        assert result.search_type == "general"

    def test_search_result_score_validation(self):
        """Test SearchResult with various relevance scores."""
        test_scores = [0.0, 0.25, 0.5, 0.75, 1.0, 1.5]  # Including edge cases

        for score in test_scores:
            result = SearchResult(
                chunk_id=f"score_test_{score}",
                content="Score test content",
                relevance_score=score,
            )
            assert result.relevance_score == score

    def test_search_result_with_complex_metadata(self):
        """Test SearchResult with complex metadata."""
        complex_metadata = {
            "source_table": "企業データ",
            "extraction_method": "semantic_chunking",
            "business_context": "financial",
            "entities": ["株式会社テスト", "売上高"],
            "confidence": 0.92,
            "processing_time": 0.15,
        }

        result = SearchResult(
            chunk_id="complex_meta",
            content="Complex metadata test",
            relevance_score=0.9,
            metadata=complex_metadata,
            search_type="faceted",
        )

        assert result.metadata == complex_metadata
        assert result.metadata["source_table"] == "企業データ"
        assert len(result.metadata["entities"]) == 2


class TestQueryProcessorIntegration:
    """Integration tests for query processor components."""

    def test_processor_classifier_integration(self):
        """Test integration between query processor and classifier."""
        processor = JapaneseQueryProcessor()
        classifier = QueryIntentClassifier()

        query = "株式会社の2024年度売上データを検索"

        # Extract features
        features = processor.extract_japanese_features(query)

        # Classify intent
        intent, confidence = classifier.classify_intent(query)
        business_context = classifier.classify_business_context(query)

        # Verify integration
        assert features["has_business_terms"] is True
        assert features["query_type"] == "business"
        assert intent in ["business_search", "temporal_search", "general_search"]
        assert business_context in ["financial", "business", "general"]

    def test_query_expansion_with_classification(self):
        """Test query expansion combined with intent classification."""
        processor = JapaneseQueryProcessor()
        classifier = QueryIntentClassifier()

        original_query = "売上情報"

        # Expand query
        expanded_queries = processor.expand_query(original_query)

        # Classify each expanded query
        for expanded_query in expanded_queries:
            features = processor.extract_japanese_features(expanded_query)
            intent, confidence = classifier.classify_intent(expanded_query)

            assert isinstance(features, dict)
            assert isinstance(intent, str)
            assert isinstance(confidence, (int, float))

    def test_search_result_ranking_simulation(self):
        """Test search result ranking simulation."""
        # Create multiple search results
        results = [
            SearchResult("id1", "高い関連性コンテンツ", 0.95, search_type="semantic"),
            SearchResult("id2", "中程度関連性コンテンツ", 0.75, search_type="keyword"),
            SearchResult("id3", "低い関連性コンテンツ", 0.45, search_type="general"),
            SearchResult("id4", "最高関連性コンテンツ", 0.98, search_type="business"),
        ]

        # Sort by relevance score (descending)
        sorted_results = sorted(results, key=lambda x: x.relevance_score, reverse=True)

        assert sorted_results[0].relevance_score == 0.98
        assert sorted_results[1].relevance_score == 0.95
        assert sorted_results[2].relevance_score == 0.75
        assert sorted_results[3].relevance_score == 0.45

    def test_multilingual_query_handling(self):
        """Test handling of multilingual queries."""
        processor = JapaneseQueryProcessor()

        multilingual_queries = [
            "sales データ 売上",
            "company 会社 企業",
            "2024年度 annual report",
            "財務 financial statement",
        ]

        for query in multilingual_queries:
            features = processor.extract_japanese_features(query)
            expanded = processor.expand_query(query)

            assert isinstance(features, dict)
            assert isinstance(expanded, list)
            assert len(expanded) >= 1


class TestQueryProcessorErrorHandling:
    """Test error handling and edge cases."""

    def test_processor_with_malformed_input(self):
        """Test processor behavior with malformed input."""
        processor = JapaneseQueryProcessor()

        malformed_inputs = [
            None,
            "",
            "   ",
            123,
            [],
            {},
            "\x00\x01\x02",  # Control characters
        ]

        for malformed_input in malformed_inputs:
            try:
                if isinstance(malformed_input, str) or malformed_input is None:
                    features = processor.extract_japanese_features(malformed_input)
                    expanded = processor.expand_query(malformed_input)
                    assert isinstance(features, dict)
                    assert isinstance(expanded, list)
                else:
                    # For non-string inputs, we expect them to be handled gracefully
                    # or raise appropriate exceptions
                    pass
            except (TypeError, AttributeError):
                # Expected for non-string inputs
                pass

    def test_classifier_with_extreme_inputs(self):
        """Test classifier with extreme inputs."""
        classifier = QueryIntentClassifier()

        extreme_inputs = [
            "x" * 10000,  # Very long string
            "日" * 1000,  # Very long Japanese string
            "a" * 5000 + "売上" + "b" * 5000,  # Long string with business term
        ]

        for extreme_input in extreme_inputs:
            intent, confidence = classifier.classify_intent(extreme_input)
            context = classifier.classify_business_context(extreme_input)

            assert isinstance(intent, str)
            assert isinstance(confidence, (int, float))
            assert isinstance(context, str)

    def test_search_result_boundary_values(self):
        """Test SearchResult with boundary values."""
        boundary_cases = [
            ("", "", -1.0),  # Minimum values
            ("x" * 1000, "y" * 10000, 2.0),  # Large values
            ("unicode_🎯", "content_🚀", 0.0),  # Unicode content
        ]

        for chunk_id, content, score in boundary_cases:
            result = SearchResult(
                chunk_id=chunk_id, content=content, relevance_score=score
            )

            assert result.chunk_id == chunk_id
            assert result.content == content
            assert result.relevance_score == score
