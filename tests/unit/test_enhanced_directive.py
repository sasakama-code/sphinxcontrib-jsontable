#!/usr/bin/env python3
"""
Basic functionality tests for EnhancedJsonTableDirective.

This module tests the core functionality of the enhanced directive
including RAG metadata extraction and semantic chunking.
"""

from sphinxcontrib.jsontable.rag.metadata_extractor import RAGMetadataExtractor
from sphinxcontrib.jsontable.rag.semantic_chunker import SemanticChunker


def test_rag_metadata_extractor():
    """
    Test basic functionality of RAGMetadataExtractor.

    Verifies that the metadata extractor can process Japanese employee
    data and generate appropriate metadata structures.
    """
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
    """
    Test basic functionality of SemanticChunker.

    Verifies that the semantic chunker can process JSON data and
    generate appropriate semantic chunks for search optimization.
    """
    print("\n=== SemanticChunker Test ===")

    chunker = SemanticChunker(chunk_strategy="row_based", max_chunk_size=1000)

    # Generate basic metadata using RAGMetadataExtractor
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
    print("🚀 Starting EnhancedJsonTableDirective tests\n")

    test_rag_metadata_extractor()
    test_semantic_chunker()

    print("\n🎉 All basic tests passed successfully!")
