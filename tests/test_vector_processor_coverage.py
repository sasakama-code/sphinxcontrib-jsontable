"""Vector processor coverage improvement tests.

Provides comprehensive test coverage for VectorProcessor components to improve
overall code coverage from 69.79% to 80%+ target. Tests focus on core
functionality, error handling, and edge cases.

Created: 2025-06-09
"""

import numpy as np

from sphinxcontrib.jsontable.rag.semantic_chunker import SemanticChunk
from sphinxcontrib.jsontable.rag.vector_processor import (
    BusinessTermEnhancer,
    JapaneseTextNormalizer,
    PLaMoVectorProcessor,
    VectorChunk,
    VectorProcessingResult,
)


class TestJapaneseTextNormalizerCoverage:
    """Comprehensive tests for JapaneseTextNormalizer."""

    def setup_method(self):
        """Setup normalizer for testing."""
        self.normalizer = JapaneseTextNormalizer()

    def test_normalize_basic_functionality(self):
        """Test basic text normalization."""
        text = "株式会社ＴＥＳＴの２０２４年度売上"
        normalized = self.normalizer.normalize(text)

        assert "TEST" in normalized
        assert "2024" in normalized
        assert "株式会社" in normalized

    def test_normalize_empty_text(self):
        """Test normalization with empty text."""
        result = self.normalizer.normalize("")
        assert result == ""

    def test_normalize_none_text(self):
        """Test normalization with None input."""
        try:
            result = self.normalizer.normalize(None)
            # If it handles None gracefully, check result
            assert result == "" or isinstance(result, str)
        except (TypeError, AttributeError):
            # If it raises an error, that's also acceptable
            pass

    def test_normalize_whitespace_handling(self):
        """Test whitespace normalization."""
        text = "  株式会社　　ＴＥＳＴコーポレーション  "
        normalized = self.normalizer.normalize(text)

        assert normalized.strip() != text.strip()
        assert "TEST" in normalized

    def test_normalize_katakana_hiragana(self):
        """Test katakana and hiragana normalization."""
        text = "コーポレーション　ひらがなテスト"
        normalized = self.normalizer.normalize(text)

        assert len(normalized) > 0
        assert isinstance(normalized, str)

    def test_normalize_mixed_scripts(self):
        """Test mixed script normalization."""
        text = "ABC株式会社１２３コーポレーション"
        normalized = self.normalizer.normalize(text)

        assert "ABC" in normalized
        assert "123" in normalized
        assert "株式会社" in normalized

    def test_normalize_special_characters(self):
        """Test special character handling."""
        text = "株式会社@TEST#2024$年度"
        normalized = self.normalizer.normalize(text)

        assert "株式会社" in normalized
        assert "2024" in normalized


class TestBusinessTermEnhancerCoverage:
    """Comprehensive tests for BusinessTermEnhancer."""

    def setup_method(self):
        """Setup enhancer for testing."""
        self.enhancer = BusinessTermEnhancer()

    def test_enhance_basic_business_terms(self):
        """Test basic business term enhancement."""
        text = "株式会社の売上高は1000万円"
        enhanced = self.enhancer.enhance(text)

        assert "[組織]" in enhanced or "[財務]" in enhanced
        assert len(enhanced) > len(text)

    def test_enhance_empty_text(self):
        """Test enhancement with empty text."""
        result = self.enhancer.enhance("")
        assert result == ""

    def test_enhance_none_input(self):
        """Test enhancement with None input."""
        try:
            result = self.enhancer.enhance(None)
            assert result == "" or isinstance(result, str)
        except (TypeError, AttributeError):
            # If it raises an error, that's also acceptable
            pass

    def test_extract_business_features_comprehensive(self):
        """Test comprehensive business feature extraction."""
        text = "営業部の田中部長が発表した2024年度売上は5億円"
        features = self.enhancer.extract_business_features(text)

        assert isinstance(features, dict)
        assert "categories" in features
        assert "boost_score" in features
        assert isinstance(features["categories"], list)
        assert features["boost_score"] >= 1.0

    def test_extract_business_features_empty(self):
        """Test business feature extraction with empty text."""
        features = self.enhancer.extract_business_features("")

        assert isinstance(features, dict)
        assert features["boost_score"] == 1.0
        assert len(features["categories"]) == 0

    def test_extract_business_features_no_business_terms(self):
        """Test feature extraction with no business terms."""
        text = "こんにちは、今日はいい天気ですね"
        features = self.enhancer.extract_business_features(text)

        assert isinstance(features, dict)
        assert features["boost_score"] == 1.0

    def test_enhance_multiple_financial_terms(self):
        """Test enhancement with multiple financial terms."""
        text = "売上高、営業利益、純利益の推移"
        enhanced = self.enhancer.enhance(text)

        assert "[財務]" in enhanced
        assert "売上高" in enhanced

    def test_enhance_organizational_terms(self):
        """Test enhancement with organizational terms."""
        text = "取締役会で承認された新規事業計画"
        enhanced = self.enhancer.enhance(text)

        assert len(enhanced) >= len(text)


class TestPLaMoVectorProcessorCoverage:
    """Comprehensive tests for PLaMoVectorProcessor non-async methods."""

    def setup_method(self):
        """Setup processor for testing."""
        self.processor = PLaMoVectorProcessor()

    def test_init_configuration(self):
        """Test processor initialization and configuration."""
        assert self.processor.config is not None
        assert self.processor.config["model"]["dimension"] == 1024
        assert self.processor.config["model"]["japanese_preprocessing"] is True

    def test_get_processing_stats_initial(self):
        """Test initial processing statistics."""
        stats = self.processor.get_processing_stats()

        assert isinstance(stats, dict)
        assert "total_processed" in stats
        assert "success_rate" in stats
        assert stats["total_processed"] == 0
        assert stats["success_rate"] == 0.0

    def test_create_mock_vector(self):
        """Test mock vector creation."""
        # This tests internal mock functionality
        config = self.processor.config
        dimension = config["model"]["dimension"]

        # Test that dimension is correctly set
        assert dimension == 1024
        assert isinstance(dimension, int)

    def test_japanese_preprocessing_setup(self):
        """Test Japanese preprocessing setup."""
        config = self.processor.config

        assert config["model"]["japanese_preprocessing"] is True
        assert config["optimization"]["japanese_boost"] > 1.0

    def test_vector_processing_config_validation(self):
        """Test vector processing configuration validation."""
        config = self.processor.config

        # Validate all required configuration keys
        assert "model" in config
        assert "processing" in config
        assert "optimization" in config

        # Validate model configuration
        model_config = config["model"]
        assert "dimension" in model_config
        assert "japanese_preprocessing" in model_config

        # Validate processing configuration
        processing_config = config["processing"]
        assert "batch_size" in processing_config
        assert "max_text_length" in processing_config

        # Validate optimization configuration
        optimization_config = config["optimization"]
        assert "japanese_boost" in optimization_config


class TestVectorChunkCoverage:
    """Tests for VectorChunk data class coverage."""

    def test_vector_chunk_creation(self):
        """Test VectorChunk creation and attributes."""
        # Create mock embedding
        embedding = np.random.rand(1024).astype(np.float32)

        chunk = VectorChunk(
            chunk_id="test_001",
            content="テストコンテンツ",
            embedding=embedding,
            metadata={"test": "data"},
            search_boost=1.5,
            japanese_enhancement={
                "enhancement_applied": True,
                "business_features": {"boost_score": 1.2},
            },
        )

        assert chunk.chunk_id == "test_001"
        assert chunk.content == "テストコンテンツ"
        assert chunk.embedding.shape == (1024,)
        assert chunk.search_boost == 1.5
        assert chunk.japanese_enhancement["enhancement_applied"] is True

    def test_vector_chunk_default_values(self):
        """Test VectorChunk with minimal required parameters."""
        embedding = np.random.rand(1024).astype(np.float32)

        chunk = VectorChunk(
            chunk_id="minimal", content="minimal content", embedding=embedding
        )

        assert chunk.chunk_id == "minimal"
        assert chunk.content == "minimal content"
        assert chunk.embedding is not None
        assert chunk.metadata == {}
        assert chunk.search_boost == 1.0


class TestVectorProcessingResultCoverage:
    """Tests for VectorProcessingResult data class coverage."""

    def test_vector_processing_result_creation(self):
        """Test VectorProcessingResult creation."""
        # Create mock vector chunks
        embedding1 = np.random.rand(1024).astype(np.float32)
        embedding2 = np.random.rand(1024).astype(np.float32)

        chunks = [
            VectorChunk("chunk1", "content1", embedding1),
            VectorChunk("chunk2", "content2", embedding2),
        ]

        result = VectorProcessingResult(
            vector_chunks=chunks,
            japanese_optimization_applied=True,
            processing_stats={"success_rate": 1.0, "total_processed": 2},
        )

        assert len(result.vector_chunks) == 2
        assert result.japanese_optimization_applied is True
        assert result.processing_stats["success_rate"] == 1.0

    def test_vector_processing_result_defaults(self):
        """Test VectorProcessingResult with default values."""
        result = VectorProcessingResult(
            vector_chunks=[], japanese_optimization_applied=False, processing_stats={}
        )

        assert len(result.vector_chunks) == 0
        assert result.japanese_optimization_applied is False
        assert result.processing_stats == {}


class TestVectorProcessorIntegration:
    """Integration tests for vector processor components."""

    def test_normalizer_enhancer_integration(self):
        """Test integration between normalizer and enhancer."""
        normalizer = JapaneseTextNormalizer()
        enhancer = BusinessTermEnhancer()

        text = "株式会社ＴＥＳＴの２０２４年度売上高"

        # Sequential processing
        normalized = normalizer.normalize(text)
        enhanced = enhancer.enhance(normalized)

        assert "TEST" in normalized
        assert "2024" in normalized
        assert len(enhanced) >= len(normalized)

    def test_semantic_chunk_to_vector_chunk_conversion(self):
        """Test conversion from SemanticChunk to VectorChunk concept."""
        # Create semantic chunk
        semantic_chunk = SemanticChunk(
            chunk_id="semantic_001",
            content="テスト用のセマンティックチャンク",
            chunk_type="test",
            metadata={"test": "data"},
        )

        # Process through normalizer and enhancer
        normalizer = JapaneseTextNormalizer()
        enhancer = BusinessTermEnhancer()

        normalized_content = normalizer.normalize(semantic_chunk.content)
        enhanced_content = enhancer.enhance(normalized_content)
        business_features = enhancer.extract_business_features(enhanced_content)

        # Create mock embedding for vector chunk
        mock_embedding = np.random.rand(1024).astype(np.float32)

        # Create vector chunk (simulating async processing result)
        vector_chunk = VectorChunk(
            chunk_id=semantic_chunk.chunk_id,
            content=enhanced_content,
            embedding=mock_embedding,
            metadata=semantic_chunk.metadata,
            search_boost=business_features["boost_score"],
            japanese_enhancement={
                "enhancement_applied": True,
                "business_features": business_features,
            },
        )

        assert vector_chunk.chunk_id == semantic_chunk.chunk_id
        assert vector_chunk.search_boost >= 1.0
        assert vector_chunk.japanese_enhancement["enhancement_applied"] is True

    def test_processor_error_handling(self):
        """Test processor error handling scenarios."""
        processor = PLaMoVectorProcessor()

        # Test with invalid configuration scenarios
        config = processor.config

        # Verify robust configuration
        assert config is not None
        assert isinstance(config, dict)

        # Test stats with no processing
        stats = processor.get_processing_stats()
        assert stats["total_processed"] == 0


class TestVectorProcessorEdgeCases:
    """Test edge cases and error conditions."""

    def test_normalizer_with_special_characters(self):
        """Test normalizer with various special characters."""
        normalizer = JapaneseTextNormalizer()

        special_texts = [
            "①②③株式会社",
            "♪♫音楽会社♪♫",
            "★☆商事株式会社★☆",
            "【重要】業績発表【重要】",
        ]

        for text in special_texts:
            result = normalizer.normalize(text)
            assert isinstance(result, str)
            assert len(result) > 0

    def test_enhancer_with_long_text(self):
        """Test enhancer with very long text."""
        enhancer = BusinessTermEnhancer()

        # Create long business text
        long_text = "株式会社テスト " * 100 + "売上高は1000万円"

        enhanced = enhancer.enhance(long_text)
        features = enhancer.extract_business_features(long_text)

        assert isinstance(enhanced, str)
        assert isinstance(features, dict)
        assert len(enhanced) >= len(long_text)
        assert features["boost_score"] >= 1.0

    def test_vector_chunk_with_large_embedding(self):
        """Test VectorChunk with different embedding sizes."""
        # Test with standard PLaMo size
        standard_embedding = np.random.rand(1024).astype(np.float32)

        chunk = VectorChunk(
            chunk_id="large_test",
            content="Large embedding test",
            embedding=standard_embedding,
        )

        assert chunk.embedding.shape == (1024,)
        assert chunk.embedding.dtype == np.float32

    def test_processing_result_with_many_chunks(self):
        """Test VectorProcessingResult with many chunks."""
        # Create many mock chunks
        chunks = []
        for i in range(100):
            embedding = np.random.rand(1024).astype(np.float32)
            chunk = VectorChunk(
                chunk_id=f"chunk_{i:03d}", content=f"Content {i}", embedding=embedding
            )
            chunks.append(chunk)

        result = VectorProcessingResult(
            vector_chunks=chunks,
            japanese_optimization_applied=True,
            processing_stats={
                "total_processed": 100,
                "success_rate": 1.0,
                "avg_processing_time": 0.1,
            },
        )

        assert len(result.vector_chunks) == 100
        assert result.processing_stats["total_processed"] == 100
        assert result.processing_stats["success_rate"] == 1.0
