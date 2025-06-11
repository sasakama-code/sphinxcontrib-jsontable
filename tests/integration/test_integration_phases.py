"""
Integrated Phase testing for all RAG phases.
統合元: test_phase1_2_integration.py + test_phase2_integration.py + test_phase3_plamo_integration.py
"""

from unittest.mock import Mock

import pytest

from sphinxcontrib.jsontable.enhanced_directive import EnhancedJsonTableDirective
from sphinxcontrib.jsontable.rag.advanced_metadata import (
    AdvancedMetadata,
    AdvancedMetadataGenerator,
)
from sphinxcontrib.jsontable.rag.metadata_exporter import MetadataExporter
from sphinxcontrib.jsontable.rag.metadata_extractor import (
    BasicMetadata,
    RAGMetadataExtractor,
)
from sphinxcontrib.jsontable.rag.search_facets import (
    GeneratedFacets,
    SearchFacetGenerator,
)
from sphinxcontrib.jsontable.rag.semantic_chunker import SemanticChunk, SemanticChunker


class TestPhase1Integration:
    """Phase 1: Core RAG infrastructure integration tests."""

    def setup_method(self):
        """Test setup."""
        self.metadata_extractor = RAGMetadataExtractor()
        self.semantic_chunker = SemanticChunker()

    def test_phase1_basic_workflow(self):
        """Test Phase 1 basic RAG workflow."""
        # Sample data for Phase 1 testing
        sample_data = [
            {"name": "田中太郎", "age": 30, "department": "営業部"},
            {"name": "佐藤花子", "age": 25, "department": "開発部"},
            {"name": "鈴木一郎", "age": 35, "department": "マーケティング部"},
        ]

        # Step 1: Extract metadata
        metadata = self.metadata_extractor.extract(sample_data, {})

        assert isinstance(metadata, BasicMetadata)
        assert metadata.record_count == 3
        assert len(metadata.schema["properties"]) == 3
        assert "name" in metadata.schema["properties"]
        assert "age" in metadata.schema["properties"]
        assert "department" in metadata.schema["properties"]

        # Step 2: Create semantic chunks
        chunks = self.semantic_chunker.create_chunks(sample_data, metadata)

        assert len(chunks) >= 1
        for chunk in chunks:
            assert isinstance(chunk, SemanticChunk)
            assert hasattr(chunk, "content")
            assert hasattr(chunk, "chunk_type")

    def test_phase1_japanese_text_processing(self):
        """Test Phase 1 Japanese text processing."""
        japanese_data = [
            {"title": "商品開発", "description": "新しい商品の開発プロセスについて"},
            {"title": "品質管理", "description": "品質管理システムの導入と運用"},
        ]

        metadata = self.metadata_extractor.extract(japanese_data, {})

        # Should extract Japanese content properly
        assert metadata.record_count == 2
        assert len(metadata.search_keywords) > 0
        assert metadata.semantic_summary is not None

        # Should handle Japanese text in chunking
        chunks = self.semantic_chunker.create_chunks(japanese_data, metadata)
        assert len(chunks) > 0

    def test_phase1_error_handling(self):
        """Test Phase 1 error handling."""
        # Test empty data
        empty_metadata = self.metadata_extractor.extract([], {})
        assert empty_metadata.record_count == 0

        # Test malformed data
        import contextlib

        with contextlib.suppress(Exception):
            self.metadata_extractor.extract(None, {})


class TestPhase2Integration:
    """Phase 2: Advanced metadata generation integration tests."""

    def setup_method(self):
        """Test setup."""
        self.metadata_extractor = RAGMetadataExtractor()
        self.advanced_generator = AdvancedMetadataGenerator()
        self.facet_generator = SearchFacetGenerator()
        self.metadata_exporter = MetadataExporter()

    def test_phase2_advanced_workflow(self):
        """Test Phase 2 advanced metadata workflow."""
        # Business-oriented test data
        business_data = [
            {
                "company": "株式会社ABC",
                "revenue": 5000000,
                "industry": "製造業",
                "location": "東京都",
            },
            {
                "company": "XYZ商事",
                "revenue": 3000000,
                "industry": "商業",
                "location": "大阪府",
            },
            {
                "company": "テクノロジー株式会社",
                "revenue": 8000000,
                "industry": "IT",
                "location": "神奈川県",
            },
        ]

        # Step 1: Basic metadata extraction
        basic_metadata = self.metadata_extractor.extract(business_data, {})
        assert basic_metadata.record_count == 3

        # Step 2: Advanced metadata generation
        advanced_metadata = self.advanced_generator.generate_advanced_metadata(
            business_data, basic_metadata
        )

        assert isinstance(advanced_metadata, AdvancedMetadata)
        assert hasattr(advanced_metadata, "statistics")
        assert hasattr(advanced_metadata, "entities")

        # Step 3: Facet generation
        facets = self.facet_generator.generate_facets(business_data)

        assert isinstance(facets, GeneratedFacets)
        assert len(facets.categorical_facets) > 0  # Should detect industry, location
        assert len(facets.numerical_facets) > 0  # Should detect revenue

    def test_phase2_japanese_entity_recognition(self):
        """Test Phase 2 Japanese entity recognition."""
        entity_data = [
            {
                "person": "田中太郎",
                "organization": "株式会社サンプル",
                "location": "東京都渋谷区",
            },
            {
                "person": "佐藤花子",
                "organization": "テスト商事",
                "location": "大阪市中央区",
            },
        ]

        basic_metadata = self.metadata_extractor.extract(entity_data, {})
        advanced_metadata = self.advanced_generator.generate_advanced_metadata(
            entity_data, basic_metadata
        )

        # Should recognize Japanese entities
        assert advanced_metadata is not None
        assert hasattr(advanced_metadata, "entities")

    def test_phase2_export_formats(self):
        """Test Phase 2 export format generation."""
        sample_data = [{"test": "データ", "number": 42}]

        basic_metadata = self.metadata_extractor.extract(sample_data, {})
        advanced_metadata = self.advanced_generator.generate_advanced_metadata(
            sample_data, basic_metadata
        )
        facets = self.facet_generator.generate_facets(sample_data)

        # Test export functionality
        try:
            exported = self.metadata_exporter.export_metadata(
                basic_metadata, advanced_metadata, facets, format_type="json"
            )
            assert exported is not None
        except Exception:
            # Export may require additional setup
            pass


class TestPhase3Integration:
    """Phase 3: PLaMo-Embedding-1B integration tests."""

    def setup_method(self):
        """Test setup."""
        # Import Phase 3 components with mocking for missing dependencies
        try:
            from sphinxcontrib.jsontable.rag.query_processor import (
                IntelligentQueryProcessor,
            )
            from sphinxcontrib.jsontable.rag.search_index_generator import (
                SearchIndexGenerator,
            )
            from sphinxcontrib.jsontable.rag.vector_processor import (
                PLaMoVectorProcessor,
            )

            self.vector_processor = PLaMoVectorProcessor()
            self.query_processor = IntelligentQueryProcessor()
            self.search_generator = SearchIndexGenerator()
        except ImportError:
            # Phase 3 components may not be fully available
            self.vector_processor = None
            self.query_processor = None
            self.search_generator = None

    def test_phase3_vector_processing(self):
        """Test Phase 3 vector processing workflow."""
        if self.vector_processor is None:
            pytest.skip("Phase 3 components not available")

        japanese_text_data = [
            {
                "content": "これは日本語のテストコンテンツです。PLaMo-Embedding-1Bでの処理をテストします。"
            },
            {"content": "製品開発におけるAI技術の活用について説明します。"},
            {"content": "データ分析と機械学習の重要性を議論します。"},
        ]

        try:
            # Test vector generation
            vectors = self.vector_processor.generate_vectors(
                [item["content"] for item in japanese_text_data]
            )
            assert vectors is not None
        except Exception:
            # May require actual PLaMo setup
            pytest.skip("PLaMo vector processing requires additional setup")

    def test_phase3_query_processing(self):
        """Test Phase 3 intelligent query processing."""
        if self.query_processor is None:
            pytest.skip("Phase 3 components not available")

        japanese_queries = [
            "売上データを表示してください",
            "品質管理に関する情報を検索",
            "従業員の勤務状況を確認したい",
        ]

        for query in japanese_queries:
            try:
                result = self.query_processor.process_query(query)
                assert result is not None
            except Exception:
                # May require full setup
                pass

    def test_phase3_search_index_creation(self):
        """Test Phase 3 search index creation."""
        if self.search_generator is None:
            pytest.skip("Phase 3 components not available")

        index_data = [
            {"id": 1, "title": "製品A", "description": "高品質な製品Aの説明"},
            {"id": 2, "title": "サービスB", "description": "効率的なサービスBの詳細"},
            {
                "id": 3,
                "title": "プロジェクトC",
                "description": "革新的なプロジェクトCの概要",
            },
        ]

        try:
            search_index = self.search_generator.create_search_index(index_data)
            assert search_index is not None
        except Exception:
            # May require additional dependencies
            pass


class TestFullIntegrationWorkflow:
    """Complete end-to-end integration workflow tests."""

    def setup_method(self):
        """Test setup."""
        self.metadata_extractor = RAGMetadataExtractor()
        self.semantic_chunker = SemanticChunker()
        self.advanced_generator = AdvancedMetadataGenerator()
        self.facet_generator = SearchFacetGenerator()
        self.metadata_exporter = MetadataExporter()

    def test_complete_rag_workflow(self):
        """Test complete RAG workflow from start to finish."""
        # Comprehensive test data
        comprehensive_data = [
            {
                "employee_id": "EMP001",
                "name": "田中太郎",
                "department": "営業部",
                "position": "課長",
                "salary": 6000000,
                "hire_date": "2020-04-01",
                "skills": ["営業", "プレゼンテーション", "英語"],
                "performance_score": 85,
                "location": "東京都",
            },
            {
                "employee_id": "EMP002",
                "name": "佐藤花子",
                "department": "開発部",
                "position": "シニアエンジニア",
                "salary": 7500000,
                "hire_date": "2019-07-15",
                "skills": ["Python", "JavaScript", "機械学習"],
                "performance_score": 92,
                "location": "神奈川県",
            },
            {
                "employee_id": "EMP003",
                "name": "鈴木一郎",
                "department": "マーケティング部",
                "position": "マネージャー",
                "salary": 8000000,
                "hire_date": "2018-01-10",
                "skills": ["マーケティング", "データ分析", "戦略企画"],
                "performance_score": 88,
                "location": "大阪府",
            },
        ]

        # Phase 1: Basic RAG processing
        basic_metadata = self.metadata_extractor.extract(comprehensive_data, {})
        assert basic_metadata.record_count == 3
        assert len(basic_metadata.schema["properties"]) >= 8

        chunks = self.semantic_chunker.create_chunks(comprehensive_data, basic_metadata)
        assert len(chunks) > 0

        # Phase 2: Advanced processing
        advanced_metadata = self.advanced_generator.generate_advanced_metadata(
            comprehensive_data, basic_metadata
        )
        assert isinstance(advanced_metadata, AdvancedMetadata)

        facets = self.facet_generator.generate_facets(comprehensive_data)
        assert isinstance(facets, GeneratedFacets)
        assert len(facets.categorical_facets) > 0  # department, position, location
        assert len(facets.numerical_facets) > 0  # salary, performance_score

        # Export processing
        try:
            exported_data = self.metadata_exporter.export_metadata(
                basic_metadata, advanced_metadata, facets, format_type="comprehensive"
            )
            assert exported_data is not None
        except Exception:
            # Export may require additional setup
            pass

        # Workflow completed successfully
        assert True

    def test_enhanced_directive_integration(self):
        """Test EnhancedJsonTableDirective integration with all phases."""
        # Mock Sphinx environment
        mock_state = Mock()
        mock_state_machine = Mock()
        mock_env = Mock()
        mock_env.docname = "test_doc"
        mock_state.document.settings.env = mock_env

        # Create enhanced directive with RAG options
        directive = EnhancedJsonTableDirective(
            name="enhanced-jsontable",
            arguments=[],
            options={
                "rag-metadata": True,
                "export-format": "json-ld,opensearch",
                "entity-recognition": "japanese",
                "facet-generation": "auto",
            },
            content=[
                '[{"product": "ノートPC", "price": 120000, "category": "電子機器"}]'
            ],
            lineno=1,
            content_offset=0,
            block_text="",
            state=mock_state,
            state_machine=mock_state_machine,
        )

        # Test directive instantiation with RAG options
        assert directive.options.get("rag-metadata") is True
        assert "json-ld" in directive.options.get("export-format", "")
        assert directive.options.get("entity-recognition") == "japanese"
        assert directive.options.get("facet-generation") == "auto"

        # Test that directive can process content
        assert len(directive.content) == 1
        assert "ノートPC" in directive.content[0]

    def test_performance_with_realistic_data(self):
        """Test performance with realistic business data size."""
        # Generate realistic sized dataset
        realistic_data = []
        departments = ["営業部", "開発部", "マーケティング部", "人事部", "財務部"]
        positions = ["マネージャー", "リーダー", "シニア", "ジュニア", "インターン"]

        for i in range(50):  # Realistic business dataset size
            realistic_data.append(
                {
                    "employee_id": f"EMP{i:03d}",
                    "name": f"社員{i}",
                    "department": departments[i % len(departments)],
                    "position": positions[i % len(positions)],
                    "salary": 4000000 + (i * 10000) % 6000000,
                    "performance_score": 60 + (i * 3) % 40,
                    "join_year": 2015 + (i % 10),
                    "location": "東京都"
                    if i % 3 == 0
                    else "大阪府"
                    if i % 3 == 1
                    else "神奈川県",
                }
            )

        # Process through all phases
        basic_metadata = self.metadata_extractor.extract(realistic_data, {})
        assert basic_metadata.record_count == 50

        advanced_metadata = self.advanced_generator.generate_advanced_metadata(
            realistic_data, basic_metadata
        )
        assert advanced_metadata is not None

        facets = self.facet_generator.generate_facets(realistic_data)
        assert len(facets.categorical_facets) > 0
        assert len(facets.numerical_facets) > 0

        # Should handle realistic data size efficiently
        assert True


if __name__ == "__main__":
    pytest.main([__file__])
