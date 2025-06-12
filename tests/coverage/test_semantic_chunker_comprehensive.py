"""Comprehensive coverage tests for SemanticChunker.

Strategic tests targeting semantic_chunker.py to boost coverage from 48.33% to 70%+.
Focuses on chunking strategies, Japanese text processing, and edge cases.

Created: 2025-06-12
"""

import pytest

from sphinxcontrib.jsontable.rag.metadata_extractor import BasicMetadata
from sphinxcontrib.jsontable.rag.semantic_chunker import (
    SemanticChunk,
    SemanticChunker,
)


class TestSemanticChunkerComprehensive:
    """Comprehensive SemanticChunker coverage tests."""

    def setup_method(self):
        """Setup test fixtures."""
        self.chunker = SemanticChunker()
        self.basic_metadata = BasicMetadata(
            table_id="test-table",
            schema={"properties": {"name": {"type": "string"}}},
            semantic_summary="Test data",
            search_keywords=["test"],
            entity_mapping={},
            custom_tags=[],
            data_statistics={"record_count": 2},
            embedding_ready_text="Test embedding text",
            generation_timestamp="2025-06-12T00:00:00",
        )

    def test_default_initialization(self):
        """Test default chunker initialization."""
        chunker = SemanticChunker()
        assert chunker.chunk_strategy == "adaptive"
        assert chunker.max_chunk_size == 1000

    def test_custom_strategy_initialization(self):
        """Test chunker with custom strategy."""
        strategies = ["row_based", "adaptive", "semantic_blocks"]

        for strategy in strategies:
            chunker = SemanticChunker(chunk_strategy=strategy)
            assert chunker.chunk_strategy == strategy

    def test_custom_chunk_size(self):
        """Test chunker with custom chunk size."""
        chunker = SemanticChunker(max_chunk_size=200)
        assert chunker.max_chunk_size == 200

    def test_process_with_simple_data(self):
        """Test process method with simple data."""
        json_data = [
            {"name": "Alice", "description": "Software engineer"},
            {"name": "Bob", "description": "Data scientist"},
        ]

        result = self.chunker.process(json_data, self.basic_metadata)

        assert isinstance(result, list)
        assert len(result) > 0
        for chunk in result:
            assert isinstance(chunk, SemanticChunk)

    def test_process_with_japanese_data(self):
        """Test process method with Japanese data."""
        japanese_data = [
            {
                "名前": "太郎",
                "職業": "エンジニア",
                "説明": "ソフトウェア開発に従事しています。",
            },
            {
                "名前": "花子",
                "職業": "デザイナー",
                "説明": "UI/UXデザインを専門としています。",
            },
        ]

        result = self.chunker.process(japanese_data, self.basic_metadata)

        assert isinstance(result, list)
        assert len(result) > 0
        for chunk in result:
            assert isinstance(chunk, SemanticChunk)

    def test_row_based_strategy_chunking(self):
        """Test row_based strategy chunking."""
        chunker = SemanticChunker(chunk_strategy="row_based")
        data = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]

        result = chunker.process(data, self.basic_metadata)

        assert isinstance(result, list)
        assert len(result) >= 2  # At least schema + data chunks

    def test_adaptive_strategy_chunking(self):
        """Test adaptive strategy chunking."""
        chunker = SemanticChunker(chunk_strategy="adaptive")
        data = [{"name": f"User{i}", "value": f"data_{i}"} for i in range(5)]

        result = chunker.process(data, self.basic_metadata)

        assert isinstance(result, list)
        assert len(result) > 0

    def test_semantic_blocks_strategy_chunking(self):
        """Test semantic_blocks strategy chunking."""
        chunker = SemanticChunker(chunk_strategy="semantic_blocks")
        data = [
            {"category": "A", "name": "Item1"},
            {"category": "A", "name": "Item2"},
            {"category": "B", "name": "Item3"},
        ]

        result = chunker.process(data, self.basic_metadata)

        assert isinstance(result, list)
        assert len(result) > 0

    def test_chunk_by_rows_method(self):
        """Test _chunk_by_rows method directly."""
        data = [
            {"id": 1, "content": "First record"},
            {"id": 2, "content": "Second record"},
        ]

        result = self.chunker._chunk_by_rows(data, self.basic_metadata)

        assert isinstance(result, list)
        assert len(result) >= 2  # Schema + data rows

    def test_chunk_by_semantic_blocks_method(self):
        """Test _chunk_by_semantic_blocks method directly."""
        data = [
            {"category": "test", "value": "data1"},
            {"category": "test", "value": "data2"},
        ]

        result = self.chunker._chunk_by_semantic_blocks(data, self.basic_metadata)

        assert isinstance(result, list)
        assert len(result) > 0

    def test_chunk_adaptive_method(self):
        """Test _chunk_adaptive method directly."""
        data = [{"item": i} for i in range(50)]  # Medium dataset

        result = self.chunker._chunk_adaptive(data, self.basic_metadata)

        assert isinstance(result, list)
        assert len(result) > 0

    def test_create_schema_chunk(self):
        """Test _create_schema_chunk method."""
        data = [{"name": "Alice", "age": 25}]

        result = self.chunker._create_schema_chunk(data, self.basic_metadata)

        assert isinstance(result, SemanticChunk)
        assert result.chunk_type == "schema"
        assert "schema" in result.chunk_id

    def test_create_row_chunk(self):
        """Test _create_row_chunk method."""
        row = {"name": "Alice", "age": 25}

        result = self.chunker._create_row_chunk(row, 0, self.basic_metadata)

        assert isinstance(result, SemanticChunk)
        assert result.chunk_type == "data_row"
        assert "row_0" in result.chunk_id

    def test_create_primitive_chunk(self):
        """Test _create_primitive_chunk method."""
        value = "test string"

        result = self.chunker._create_primitive_chunk(value, 0, self.basic_metadata)

        assert isinstance(result, SemanticChunk)
        assert result.chunk_type == "primitive_value"
        assert "value_0" in result.chunk_id

    def test_create_object_chunk(self):
        """Test _create_object_chunk method."""
        obj = {"key": "value", "data": "test"}

        result = self.chunker._create_object_chunk(obj, self.basic_metadata)

        assert isinstance(result, SemanticChunk)
        assert result.chunk_type == "object_data"
        assert "object" in result.chunk_id

    def test_format_schema_for_search(self):
        """Test _format_schema_for_search method."""
        data = [{"name": "Alice", "age": 25}]

        result = self.chunker._format_schema_for_search(data, self.basic_metadata)

        assert isinstance(result, str)
        assert "テーブル" in result

    def test_format_row_as_text(self):
        """Test _format_row_as_text method."""
        row = {"name": "Alice", "age": 25}

        result = self.chunker._format_row_as_text(row, self.basic_metadata)

        assert isinstance(result, str)
        assert "Alice" in result

    def test_get_human_readable_column_name(self):
        """Test _get_human_readable_column_name method."""
        assert self.chunker._get_human_readable_column_name("name") == "名前"
        assert self.chunker._get_human_readable_column_name("age") == "年齢"
        assert self.chunker._get_human_readable_column_name("unknown") == "unknown"

    def test_format_value_for_search(self):
        """Test _format_value_for_search method."""
        # String value
        result = self.chunker._format_value_for_search(
            "test", "name", self.basic_metadata
        )
        assert result == "test"

        # Numeric value
        result = self.chunker._format_value_for_search(25, "age", self.basic_metadata)
        assert "25" in result

        # Boolean value
        result = self.chunker._format_value_for_search(
            True, "active", self.basic_metadata
        )
        assert result == "はい"

    def test_identify_important_fields(self):
        """Test _identify_important_fields method."""
        row = {"id": 1, "name": "Alice", "description": "test", "other": "data"}

        result = self.chunker._identify_important_fields(row, self.basic_metadata)

        assert isinstance(result, list)
        assert "name" in result  # Should prioritize name fields

    def test_calculate_row_importance(self):
        """Test _calculate_row_importance method."""
        row = {"name": "Alice", "age": 25, "description": "test"}

        result = self.chunker._calculate_row_importance(row, self.basic_metadata)

        assert isinstance(result, float)
        assert result >= 1.0

    def test_extract_row_entities(self):
        """Test _extract_row_entities method."""
        row = {"name": "田中太郎", "company": "テスト株式会社"}

        result = self.chunker._extract_row_entities(row, self.basic_metadata)

        assert isinstance(result, dict)

    def test_group_by_semantic_similarity(self):
        """Test _group_by_semantic_similarity method."""
        data = [
            {"category": "A", "name": "Item1"},
            {"category": "A", "name": "Item2"},
            {"category": "B", "name": "Item3"},
        ]

        result = self.chunker._group_by_semantic_similarity(data, self.basic_metadata)

        assert isinstance(result, list)
        assert len(result) > 0

    def test_identify_categorical_fields(self):
        """Test _identify_categorical_fields method."""
        data = [
            {"category": "A", "status": "active"},
            {"category": "B", "status": "inactive"},
            {"category": "A", "status": "active"},
        ]

        result = self.chunker._identify_categorical_fields(data, self.basic_metadata)

        assert isinstance(result, list)

    def test_group_by_category(self):
        """Test _group_by_category method."""
        data = [
            {"category": "A", "name": "Item1"},
            {"category": "A", "name": "Item2"},
            {"category": "B", "name": "Item3"},
        ]

        result = self.chunker._group_by_category(data, "category")

        assert isinstance(result, dict)
        assert "A" in result
        assert "B" in result

    def test_create_group_chunk(self):
        """Test _create_group_chunk method."""
        items = [{"name": "Item1"}, {"name": "Item2"}]

        result = self.chunker._create_group_chunk(
            "TestCategory", items, self.basic_metadata
        )

        assert isinstance(result, SemanticChunk)
        assert result.chunk_type == "category_group"

    def test_chunk_large_dataset(self):
        """Test _chunk_large_dataset method."""
        data = [{"id": i, "value": f"data_{i}"} for i in range(150)]

        result = self.chunker._chunk_large_dataset(data, self.basic_metadata)

        assert isinstance(result, list)
        assert len(result) > 0

    def test_create_statistical_summary_chunk(self):
        """Test _create_statistical_summary_chunk method."""
        data = [{"id": i} for i in range(100)]

        result = self.chunker._create_statistical_summary_chunk(
            data, self.basic_metadata
        )

        assert isinstance(result, SemanticChunk)
        assert result.chunk_type == "statistical_summary"

    def test_get_base_chunk_metadata(self):
        """Test _get_base_chunk_metadata method."""
        result = self.chunker._get_base_chunk_metadata(self.basic_metadata)

        assert isinstance(result, dict)
        assert "table_id" in result
        assert result["table_id"] == "test-table"

    def test_semantic_chunk_properties(self):
        """Test SemanticChunk properties."""
        chunk = SemanticChunk(
            chunk_id="test-chunk-1",
            chunk_type="data_row",
            content="Test content for semantic chunk",
            metadata={"chunk_size": 50},
            search_weight=1.0,
            embedding_hint="test hint",
        )

        assert chunk.chunk_id == "test-chunk-1"
        assert chunk.content == "Test content for semantic chunk"
        assert chunk.chunk_type == "data_row"
        assert chunk.search_weight == 1.0

    def test_empty_data_handling(self):
        """Test handling of empty data."""
        result = self.chunker.process([], self.basic_metadata)
        assert isinstance(result, list)

    def test_single_record_processing(self):
        """Test processing of single record."""
        data = [{"single": "record content"}]

        result = self.chunker.process(data, self.basic_metadata)

        assert isinstance(result, list)
        assert len(result) > 0

    def test_large_content_chunking(self):
        """Test chunking of large content."""
        large_content = "Large content text. " * 100
        data = [{"content": large_content}]

        result = self.chunker.process(data, self.basic_metadata)

        assert isinstance(result, list)
        assert len(result) > 0

    def test_mixed_content_types(self):
        """Test processing mixed content types."""
        mixed_data = [
            {"type": "text", "content": "Text content here"},
            {"type": "number", "value": 42},
            {"type": "object", "data": {"nested": "value"}},
        ]

        result = self.chunker.process(mixed_data, self.basic_metadata)

        assert isinstance(result, list)
        assert len(result) > 0

    def test_unicode_content_processing(self):
        """Test processing of Unicode content."""
        unicode_data = [
            {"emoji": "🎉🚀✨", "chinese": "你好世界", "arabic": "مرحبا بالعالم"},
            {
                "japanese": "こんにちは世界",
                "korean": "안녕하세요",
                "russian": "Привет мир",
            },
        ]

        result = self.chunker.process(unicode_data, self.basic_metadata)

        assert isinstance(result, list)
        assert len(result) > 0

    def test_deeply_nested_data(self):
        """Test processing deeply nested data."""
        nested_data = [
            {
                "level1": {
                    "level2": {"level3": {"level4": {"content": "Deep nested content"}}}
                }
            }
        ]

        result = self.chunker.process(nested_data, self.basic_metadata)

        assert isinstance(result, list)
        assert len(result) > 0

    def test_japanese_text_optimization(self):
        """Test Japanese text processing optimization."""
        japanese_chunker = SemanticChunker(chunk_strategy="adaptive")
        japanese_data = [
            {"説明": "これは日本語のテキストです。文章の分割をテストしています。"},
            {"内容": "複数の文が含まれています。適切に処理されることを期待します。"},
        ]

        result = japanese_chunker.process(japanese_data, self.basic_metadata)

        assert isinstance(result, list)
        assert len(result) > 0

    def test_special_characters_handling(self):
        """Test handling of special characters."""
        special_data = [
            {"content": "Text with special chars: <>&\"'`~!@#$%^&*()_+-=[]{}|;:,.<>?"}
        ]

        result = self.chunker.process(special_data, self.basic_metadata)

        assert isinstance(result, list)
        assert len(result) > 0

    def test_whitespace_handling(self):
        """Test handling of various whitespace scenarios."""
        whitespace_data = [
            {"content": "  Leading spaces"},
            {"content": "Trailing spaces  "},
            {"content": "\tTabs\t"},
            {"content": "\n\nNewlines\n\n"},
        ]

        result = self.chunker.process(whitespace_data, self.basic_metadata)

        assert isinstance(result, list)

    def test_error_resilience(self):
        """Test error resilience with problematic data."""
        problematic_data = [
            {"none_value": None},
            {"empty_string": ""},
            {"only_spaces": "   "},
        ]

        try:
            result = self.chunker.process(problematic_data, self.basic_metadata)
            assert isinstance(result, list)
        except Exception:
            # Should handle gracefully
            pytest.fail("SemanticChunker should handle problematic data gracefully")

    def test_chunker_reusability(self):
        """Test that chunker can be reused for multiple operations."""
        chunker = SemanticChunker()

        # First processing
        data1 = [{"content": "First dataset content"}]
        result1 = chunker.process(data1, self.basic_metadata)

        # Second processing
        data2 = [{"content": "Second dataset content"}]
        result2 = chunker.process(data2, self.basic_metadata)

        # Both should succeed
        assert isinstance(result1, list)
        assert isinstance(result2, list)

    def test_performance_with_large_dataset(self):
        """Test performance with moderately large dataset."""
        large_dataset = []
        for i in range(100):
            large_dataset.append(
                {
                    "id": i,
                    "content": f"Content for record {i}. This is test data for performance testing.",
                    "description": f"Description {i} with additional text content.",
                }
            )

        result = self.chunker.process(large_dataset, self.basic_metadata)

        assert isinstance(result, list)
        assert len(result) > 0

    def test_strategy_switching(self):
        """Test switching between different chunking strategies."""
        strategies = ["row_based", "adaptive", "semantic_blocks"]
        data = [{"name": "Test", "value": "data"} for _ in range(5)]

        results = {}
        for strategy in strategies:
            chunker = SemanticChunker(chunk_strategy=strategy)
            results[strategy] = chunker.process(data, self.basic_metadata)
            assert isinstance(results[strategy], list)

        # Results may vary between strategies
        assert len(results) == len(strategies)

    def test_invalid_strategy_error(self):
        """Test error handling for invalid chunking strategy."""
        chunker = SemanticChunker(chunk_strategy="invalid_strategy")
        data = [{"test": "data"}]

        with pytest.raises(ValueError, match="Unsupported chunking strategy"):
            chunker.process(data, self.basic_metadata)

    def test_single_object_processing(self):
        """Test processing single object (not in list)."""
        single_object = {"name": "Test", "value": "Data"}

        result = self.chunker.process(single_object, self.basic_metadata)

        assert isinstance(result, list)
        assert len(result) > 0

    def test_adaptive_strategy_size_thresholds(self):
        """Test adaptive strategy behavior at different data sizes."""
        chunker = SemanticChunker(chunk_strategy="adaptive")

        # Small dataset (<=10) - should use row_based
        small_data = [{"id": i} for i in range(5)]
        small_result = chunker.process(small_data, self.basic_metadata)

        # Medium dataset (<=100) - should use semantic_blocks
        medium_data = [{"id": i} for i in range(50)]
        medium_result = chunker.process(medium_data, self.basic_metadata)

        # Large dataset (>100) - should use large_dataset method
        large_data = [{"id": i} for i in range(150)]
        large_result = chunker.process(large_data, self.basic_metadata)

        assert isinstance(small_result, list)
        assert isinstance(medium_result, list)
        assert isinstance(large_result, list)
