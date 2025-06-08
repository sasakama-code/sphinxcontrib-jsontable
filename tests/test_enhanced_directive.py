#!/usr/bin/env python3
"""
EnhancedJsonTableDirective の基本動作テスト
"""

from sphinxcontrib.jsontable.enhanced_directive import (
    RAGMetadataExtractor,
    SemanticChunker,
)


def test_rag_metadata_extractor():
    """RAGMetadataExtractor の基本機能テスト"""
    print("=== RAGMetadataExtractor Test ===")

    extractor = RAGMetadataExtractor()

    test_data = [
        {"name": "田中太郎", "age": 30, "department": "開発部"},
        {"name": "佐藤花子", "age": 25, "department": "営業部"},
    ]

    metadata = extractor.extract(test_data, {})

    print(f"Table ID: {metadata.table_id}")
    print(f"Schema: {metadata.schema}")
    print(f"Keywords: {metadata.search_keywords}")
    print("✅ RAGMetadataExtractor test passed")


def test_semantic_chunker():
    """SemanticChunker の基本機能テスト"""
    print("\n=== SemanticChunker Test ===")

    chunker = SemanticChunker(chunk_strategy="row_based", max_chunk_size=1000)

    # RAGMetadataExtractorを使って基本メタデータを生成
    extractor = RAGMetadataExtractor()
    test_data = [
        {"name": "田中太郎", "age": 30, "department": "開発部"},
        {"name": "佐藤花子", "age": 25, "department": "営業部"},
    ]
    
    basic_metadata = extractor.extract(test_data, {})
    chunks = chunker.process(test_data, basic_metadata)

    print(f"Generated {len(chunks)} chunks")
    print("✅ SemanticChunker test passed")


if __name__ == "__main__":
    print("🚀 EnhancedJsonTableDirective テスト開始\n")

    test_rag_metadata_extractor()
    test_semantic_chunker()

    print("\n🎉 基本テストが成功しました!")
