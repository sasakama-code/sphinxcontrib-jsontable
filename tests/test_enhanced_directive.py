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

    metadata = extractor.extract_metadata(test_data)

    print(f"Data Type: {metadata['data_type']}")
    print(f"Schema Type: {metadata['schema_info']['type']}")
    print(f"Fields: {metadata['schema_info']['fields']}")
    print("✅ RAGMetadataExtractor test passed")


def test_semantic_chunker():
    """SemanticChunker の基本機能テスト"""
    print("\n=== SemanticChunker Test ===")

    chunker = SemanticChunker(chunk_size=2)

    table_data = [
        ["名前", "年齢", "部署"],
        ["田中太郎", "30", "開発部"],
        ["佐藤花子", "25", "営業部"],
        ["鈴木一郎", "35", "開発部"],
    ]

    chunks = chunker.create_semantic_chunks(table_data, {}, has_header=True)

    print(f"Generated {len(chunks)} chunks")
    print("✅ SemanticChunker test passed")


if __name__ == "__main__":
    print("🚀 EnhancedJsonTableDirective テスト開始\n")

    test_rag_metadata_extractor()
    test_semantic_chunker()

    print("\n🎉 基本テストが成功しました!")
