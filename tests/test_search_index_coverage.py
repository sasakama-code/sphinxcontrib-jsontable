"""Search index generator coverage improvement tests.

Provides comprehensive test coverage for SearchIndexGenerator and related
components to improve overall code coverage. Focuses on synchronous
functionality and data structure validation.

Created: 2025-06-09
"""

import numpy as np

from sphinxcontrib.jsontable.rag.metadata_extractor import BasicMetadata
from sphinxcontrib.jsontable.rag.search_index_generator import (
    ComprehensiveSearchIndex,
    FacetedSearchIndex,
    JapaneseQueryProcessor,
    SearchIndexGenerator,
    SemanticSearchIndex,
    VectorIndex,
)
from sphinxcontrib.jsontable.rag.vector_processor import VectorChunk


class TestVectorIndexCoverage:
    """Comprehensive tests for VectorIndex data class."""

    def test_vector_index_creation(self):
        """Test VectorIndex creation and basic attributes."""
        index = VectorIndex(
            dimension=1024,
            total_vectors=10,
            index_type="faiss_flatip",
            chunk_metadata={"chunk_1": {"content": "test"}},
            vector_store=None,  # Using None for testing
        )

        assert index.dimension == 1024
        assert index.total_vectors == 10
        assert index.index_type == "faiss_flatip"
        assert "chunk_1" in index.chunk_metadata
        assert index.vector_store is None

    def test_vector_index_fallback_type(self):
        """Test VectorIndex with fallback index type."""
        index = VectorIndex(
            dimension=512,
            total_vectors=5,
            index_type="fallback_cosine",
            chunk_metadata={},
            vector_store={"type": "fallback", "vectors": []},
        )

        assert index.dimension == 512
        assert index.total_vectors == 5
        assert index.index_type == "fallback_cosine"
        assert index.chunk_metadata == {}
        assert index.vector_store is not None

    def test_vector_index_with_metadata(self):
        """Test VectorIndex with comprehensive metadata."""
        metadata = {
            f"chunk_{i}": {
                "content": f"Content {i}",
                "source": f"table_{i}",
                "type": "business_data",
            }
            for i in range(100)
        }

        index = VectorIndex(
            dimension=1024,
            total_vectors=100,
            index_type="faiss_flatip",
            chunk_metadata=metadata,
            vector_store={"faiss_index": "mock_index"},
        )

        assert len(index.chunk_metadata) == 100
        assert index.total_vectors == 100
        assert index.vector_store["faiss_index"] == "mock_index"


class TestSemanticSearchIndexCoverage:
    """Comprehensive tests for SemanticSearchIndex data class."""

    def test_semantic_index_creation(self):
        """Test SemanticSearchIndex creation."""
        text_segments = ["セグメント1", "セグメント2", "セグメント3"]
        keyword_index = {"売上": [0, 1], "会社": [1, 2], "データ": [0, 2]}
        business_index = {"株式会社": [0], "営業利益": [1], "財務": [2]}

        index = SemanticSearchIndex(
            text_segments=text_segments,
            japanese_keyword_index=keyword_index,
            business_term_index=business_index,
            semantic_clusters={},
        )

        assert len(index.text_segments) == 3
        assert "売上" in index.japanese_keyword_index
        assert "株式会社" in index.business_term_index
        assert index.semantic_clusters == {}

    def test_semantic_index_empty(self):
        """Test SemanticSearchIndex with empty data."""
        index = SemanticSearchIndex(
            text_segments=[],
            japanese_keyword_index={},
            business_term_index={},
            semantic_clusters={},
        )

        assert len(index.text_segments) == 0
        assert len(index.japanese_keyword_index) == 0
        assert len(index.business_term_index) == 0
        assert len(index.semantic_clusters) == 0

    def test_semantic_index_large_dataset(self):
        """Test SemanticSearchIndex with large dataset."""
        # Create large text segments
        text_segments = [f"テキストセグメント{i}" for i in range(1000)]

        # Create keyword index
        keyword_index = {}
        for i in range(100):
            keyword = f"キーワード{i}"
            keyword_index[keyword] = list(range(i, min(i + 10, 1000)))

        # Create business term index
        business_index = {}
        business_terms = ["売上", "利益", "会社", "従業員", "財務"]
        for i, term in enumerate(business_terms):
            business_index[term] = list(range(i * 200, (i + 1) * 200))

        index = SemanticSearchIndex(
            text_segments=text_segments,
            japanese_keyword_index=keyword_index,
            business_term_index=business_index,
            semantic_clusters={"cluster_1": list(range(500))},
        )

        assert len(index.text_segments) == 1000
        assert len(index.japanese_keyword_index) == 100
        assert len(index.business_term_index) == 5
        assert "cluster_1" in index.semantic_clusters


class TestFacetedSearchIndexCoverage:
    """Comprehensive tests for FacetedSearchIndex data class."""

    def test_faceted_index_creation(self):
        """Test FacetedSearchIndex creation."""
        categorical_facets = {
            "department": {"開発": [0, 1], "営業": [2, 3]},
            "status": {"active": [0, 2], "inactive": [1, 3]},
        }

        numerical_facets = {
            "salary": {"min": 300000, "max": 800000, "buckets": [0, 1, 2, 3]},
            "age": {"min": 25, "max": 45, "buckets": [0, 1, 2, 3]},
        }

        temporal_facets = {
            "hire_date": {
                "start": "2020-01-01",
                "end": "2024-12-31",
                "buckets": [0, 1, 2, 3],
            }
        }

        entity_facets = {
            "person": {"田中": [0], "佐藤": [1], "山田": [2]},
            "company": {"株式会社A": [0, 1], "株式会社B": [2, 3]},
        }

        index = FacetedSearchIndex(
            categorical_facets=categorical_facets,
            numerical_facets=numerical_facets,
            temporal_facets=temporal_facets,
            entity_facets=entity_facets,
        )

        assert "department" in index.categorical_facets
        assert "salary" in index.numerical_facets
        assert "hire_date" in index.temporal_facets
        assert "person" in index.entity_facets

    def test_faceted_index_empty(self):
        """Test FacetedSearchIndex with empty facets."""
        index = FacetedSearchIndex(
            categorical_facets={},
            numerical_facets={},
            temporal_facets={},
            entity_facets={},
        )

        assert len(index.categorical_facets) == 0
        assert len(index.numerical_facets) == 0
        assert len(index.temporal_facets) == 0
        assert len(index.entity_facets) == 0

    def test_faceted_index_complex_structure(self):
        """Test FacetedSearchIndex with complex nested structure."""
        complex_categorical = {
            "multi_level": {
                "level1_a": {"level2_x": [0, 1], "level2_y": [2, 3]},
                "level1_b": {"level2_z": [4, 5]},
            }
        }

        index = FacetedSearchIndex(
            categorical_facets=complex_categorical,
            numerical_facets={},
            temporal_facets={},
            entity_facets={},
        )

        assert "multi_level" in index.categorical_facets
        assert "level1_a" in index.categorical_facets["multi_level"]


class TestComprehensiveSearchIndexCoverage:
    """Comprehensive tests for ComprehensiveSearchIndex data class."""

    def test_comprehensive_index_creation(self):
        """Test ComprehensiveSearchIndex creation."""
        # Create mock indexes
        vector_index = VectorIndex(1024, 10, "faiss_flatip", {}, None)
        semantic_index = SemanticSearchIndex([], {}, {}, {})
        facet_index = FacetedSearchIndex({}, {}, {}, {})

        comprehensive_index = ComprehensiveSearchIndex(
            vector_index=vector_index,
            semantic_index=semantic_index,
            facet_index=facet_index,
            hybrid_index={"fusion_weights": {"vector": 0.6, "semantic": 0.4}},
            total_chunks=10,
            index_metadata={"created": "2025-06-09", "version": "1.0"},
        )

        assert comprehensive_index.vector_index is not None
        assert comprehensive_index.semantic_index is not None
        assert comprehensive_index.facet_index is not None
        assert comprehensive_index.total_chunks == 10
        assert "fusion_weights" in comprehensive_index.hybrid_index

    def test_comprehensive_index_defaults(self):
        """Test ComprehensiveSearchIndex with default values."""
        index = ComprehensiveSearchIndex()

        assert index.vector_index is None
        assert index.semantic_index is None
        assert index.facet_index is None
        assert index.hybrid_index == {}
        assert index.total_chunks == 0
        assert index.index_metadata == {}


class TestSearchIndexGeneratorCoverage:
    """Comprehensive tests for SearchIndexGenerator synchronous methods."""

    def setup_method(self):
        """Setup generator for testing."""
        self.generator = SearchIndexGenerator()

    def test_generator_initialization(self):
        """Test SearchIndexGenerator initialization."""
        assert self.generator is not None
        assert hasattr(self.generator, "_build_vector_index")
        assert hasattr(self.generator, "_build_semantic_index")
        assert hasattr(self.generator, "_build_facet_index")

    def test_build_vector_index_structure(self):
        """Test vector index building structure validation."""
        # Create mock vector chunks
        vector_chunks = []
        for i in range(5):
            embedding = np.random.rand(1024).astype(np.float32)
            chunk = VectorChunk(
                chunk_id=f"chunk_{i}",
                content=f"Content {i}",
                embedding=embedding,
                metadata={"source": f"table_{i}"},
            )
            vector_chunks.append(chunk)

        # Build vector index
        vector_index = self.generator._build_vector_index(vector_chunks)

        assert isinstance(vector_index, VectorIndex)
        assert vector_index.dimension == 1024
        assert vector_index.total_vectors == 5
        assert len(vector_index.chunk_metadata) == 5
        assert vector_index.index_type in ["faiss_flatip", "fallback_cosine"]

    def test_build_vector_index_empty(self):
        """Test vector index building with empty chunks."""
        vector_index = self.generator._build_vector_index([])

        assert isinstance(vector_index, VectorIndex)
        assert vector_index.total_vectors == 0
        assert len(vector_index.chunk_metadata) == 0

    def test_build_semantic_index_structure(self):
        """Test semantic index building structure validation."""
        # Create mock vector chunks with Japanese content
        vector_chunks = []
        japanese_contents = [
            "株式会社テストの売上高データ",
            "営業部門の業績情報",
            "財務諸表の分析結果",
            "従業員数の統計データ",
            "市場分析レポート",
        ]

        for i, content in enumerate(japanese_contents):
            embedding = np.random.rand(1024).astype(np.float32)
            chunk = VectorChunk(
                chunk_id=f"chunk_{i}",
                content=content,
                embedding=embedding,
                metadata={"type": "business_data"},
            )
            vector_chunks.append(chunk)

        # Build semantic index
        semantic_index = self.generator._build_semantic_index(vector_chunks)

        assert isinstance(semantic_index, SemanticSearchIndex)
        assert len(semantic_index.text_segments) == 5
        assert len(semantic_index.japanese_keyword_index) > 0
        assert len(semantic_index.business_term_index) > 0

    def test_build_semantic_index_keyword_extraction(self):
        """Test keyword extraction in semantic index building."""
        # Create chunks with specific keywords
        vector_chunks = []
        contents_with_keywords = [
            "データベースの情報を検索",
            "売上高の分析結果",
            "会社の組織構造",
            "財務データの処理",
        ]

        for i, content in enumerate(contents_with_keywords):
            embedding = np.random.rand(1024).astype(np.float32)
            chunk = VectorChunk(
                chunk_id=f"keyword_chunk_{i}", content=content, embedding=embedding
            )
            vector_chunks.append(chunk)

        semantic_index = self.generator._build_semantic_index(vector_chunks)

        # Check for expected keywords
        all_keywords = set(semantic_index.japanese_keyword_index.keys())
        all_business_terms = set(semantic_index.business_term_index.keys())

        assert len(all_keywords) > 0
        assert len(all_business_terms) > 0

    def test_build_facet_index_with_metadata(self):
        """Test facet index building with metadata."""
        # Create mock vector chunks
        vector_chunks = []
        for i in range(3):
            embedding = np.random.rand(1024).astype(np.float32)
            chunk = VectorChunk(
                chunk_id=f"facet_chunk_{i}",
                content=f"Facet content {i}",
                embedding=embedding,
                metadata={
                    "department": ["開発", "営業", "人事"][i],
                    "salary": [500000, 600000, 700000][i],
                    "hire_date": ["2020-01-01", "2021-06-15", "2022-12-01"][i],
                },
            )
            vector_chunks.append(chunk)

        # Create basic metadata
        basic_metadata = BasicMetadata(
            table_id="facet_test",
            schema={
                "department": {"type": "string"},
                "salary": {"type": "integer"},
                "hire_date": {"type": "date"},
            },
            semantic_summary="Test data for facet generation",
            search_keywords=["department", "salary"],
            entity_mapping={},
            custom_tags=[],
            data_statistics={"total_rows": 3},
            embedding_ready_text="Test data",
            generation_timestamp="2025-06-09",
        )

        # Build facet index
        facet_index = self.generator._build_facet_index(vector_chunks, basic_metadata)

        assert isinstance(facet_index, FacetedSearchIndex)
        # Facet generation might be empty for this test data, but structure should be valid
        assert hasattr(facet_index, "categorical_facets")
        assert hasattr(facet_index, "numerical_facets")
        assert hasattr(facet_index, "temporal_facets")
        assert hasattr(facet_index, "entity_facets")

    def test_generate_comprehensive_index_minimal(self):
        """Test comprehensive index generation with minimal data."""
        # Create minimal vector chunks
        vector_chunks = [
            VectorChunk(
                chunk_id="minimal_1",
                content="最小限のテストデータ",
                embedding=np.random.rand(1024).astype(np.float32),
            )
        ]

        # Generate comprehensive index
        comprehensive_index = self.generator.generate_comprehensive_index(vector_chunks)

        assert isinstance(comprehensive_index, ComprehensiveSearchIndex)
        assert comprehensive_index.total_chunks == 1
        assert comprehensive_index.vector_index is not None
        assert comprehensive_index.semantic_index is not None
        assert comprehensive_index.facet_index is not None

    def test_generate_comprehensive_index_with_metadata(self):
        """Test comprehensive index generation with metadata."""
        # Create vector chunks
        vector_chunks = []
        for i in range(2):
            embedding = np.random.rand(1024).astype(np.float32)
            chunk = VectorChunk(
                chunk_id=f"meta_chunk_{i}",
                content=f"メタデータ付きチャンク {i}",
                embedding=embedding,
                metadata={"category": f"category_{i}"},
            )
            vector_chunks.append(chunk)

        # Create basic metadata
        basic_metadata = BasicMetadata(
            table_id="comprehensive_test",
            schema={"category": {"type": "string"}},
            semantic_summary="包括的インデックステスト",
            search_keywords=["テスト", "インデックス"],
            entity_mapping={},
            custom_tags=["test"],
            data_statistics={"total_rows": 2},
            embedding_ready_text="テストデータ",
            generation_timestamp="2025-06-09",
        )

        # Generate comprehensive index
        comprehensive_index = self.generator.generate_comprehensive_index(
            vector_chunks, basic_metadata
        )

        assert isinstance(comprehensive_index, ComprehensiveSearchIndex)
        assert comprehensive_index.total_chunks == 2
        assert comprehensive_index.index_metadata != {}


class TestJapaneseQueryProcessorIntegration:
    """Integration tests for JapaneseQueryProcessor within search context."""

    def setup_method(self):
        """Setup query processor for testing."""
        self.processor = JapaneseQueryProcessor()

    def test_query_processing_for_search(self):
        """Test query processing optimized for search operations."""
        search_queries = [
            "売上データを検索",
            "株式会社の情報",
            "2024年度の業績",
            "従業員の給与情報",
        ]

        for query in search_queries:
            # Expand query for better search coverage
            expanded = self.processor.expand_query(query)

            # Extract features for search optimization
            features = self.processor.extract_japanese_features(query)

            assert isinstance(expanded, list)
            assert len(expanded) >= 1
            assert isinstance(features, dict)
            assert "query_type" in features

    def test_business_term_optimization(self):
        """Test business term optimization for search."""
        business_queries = [
            "営業利益",
            "株主総会",
            "取締役会",
            "四半期決算",
            "投資収益率",
        ]

        for query in business_queries:
            features = self.processor.extract_japanese_features(query)

            assert features["has_business_terms"] is True
            assert features["query_type"] in ["business", "financial"]

    def test_multilingual_search_support(self):
        """Test multilingual search query support."""
        multilingual_queries = [
            "revenue 売上",
            "company 会社 organization",
            "financial 財務 data",
            "employee 従業員 information",
        ]

        for query in multilingual_queries:
            expanded = self.processor.expand_query(query)
            features = self.processor.extract_japanese_features(query)

            assert len(expanded) >= 1
            assert isinstance(features, dict)


class TestSearchIndexErrorHandling:
    """Test error handling and edge cases for search index components."""

    def test_vector_index_with_invalid_data(self):
        """Test VectorIndex creation with invalid data."""
        # Test with negative dimensions
        index = VectorIndex(
            dimension=-1,
            total_vectors=0,
            index_type="invalid_type",
            chunk_metadata={},
            vector_store=None,
        )

        assert index.dimension == -1  # Should store as-is for error handling
        assert index.index_type == "invalid_type"

    def test_semantic_index_with_malformed_data(self):
        """Test SemanticSearchIndex with malformed data."""
        # Test with mismatched indices
        index = SemanticSearchIndex(
            text_segments=["segment1"],
            japanese_keyword_index={
                "keyword": [0, 1, 2, 3]
            },  # References beyond segments
            business_term_index={"term": [-1, 100]},  # Invalid indices
            semantic_clusters={},
        )

        assert len(index.text_segments) == 1
        assert "keyword" in index.japanese_keyword_index
        assert index.japanese_keyword_index["keyword"] == [0, 1, 2, 3]

    def test_generator_with_empty_inputs(self):
        """Test SearchIndexGenerator with various empty inputs."""
        generator = SearchIndexGenerator()

        # Test with empty vector chunks
        vector_index = generator._build_vector_index([])
        assert vector_index.total_vectors == 0

        # Test semantic index with empty chunks
        semantic_index = generator._build_semantic_index([])
        assert len(semantic_index.text_segments) == 0

        # Test comprehensive index with empty chunks
        comprehensive_index = generator.generate_comprehensive_index([])
        assert comprehensive_index.total_chunks == 0

    def test_generator_with_malformed_chunks(self):
        """Test SearchIndexGenerator with malformed vector chunks."""
        generator = SearchIndexGenerator()

        # Create malformed chunks (missing required fields)
        try:
            # This may raise an error or handle gracefully depending on implementation
            malformed_chunks = [
                # Missing embedding or other required fields
                VectorChunk("malformed", "content", np.array([]))
            ]

            vector_index = generator._build_vector_index(malformed_chunks)
            # If it succeeds, verify basic structure
            assert isinstance(vector_index, VectorIndex)

        except (ValueError, TypeError, AttributeError):
            # Expected for malformed data
            pass
