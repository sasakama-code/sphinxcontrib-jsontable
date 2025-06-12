"""RAG Metadata Extractor Package - Modular Architecture.

This package provides comprehensive metadata extraction capabilities for RAG
(Retrieval Augmented Generation) systems with advanced Japanese language support.

The package has been refactored from a single large file (25,989 bytes) into
modular components for better maintainability and extensibility while preserving
complete backward compatibility.

Architecture:
- JapanesePatternManager: Japanese language processing
- SchemaGenerator: JSON Schema generation and analysis
- RAGMetadataExtractor: Main API (backward compatible)

Created: 2025-06-12 (modularized from metadata_extractor.py)
Author: Claude Code Assistant
"""

from __future__ import annotations

import hashlib
import json
import logging
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .japanese_patterns import JapanesePatternManager
from .schema_generator import SchemaGenerator

logger = logging.getLogger(__name__)

JsonData = dict[str, Any] | list[dict[str, Any]] | list[Any]


@dataclass
class BasicMetadata:
    """Basic metadata structure for RAG processing and search optimization.

    Attributes:
        table_id: Unique identifier for the table.
        schema: JSON schema of the data structure.
        semantic_summary: Human-readable summary of table content.
        search_keywords: Keywords for search optimization.
        entity_mapping: Mapping of field names to entity types.
        custom_tags: User-defined tags for categorization.
        data_statistics: Statistical information about the data.
        embedding_ready_text: Text prepared for embedding generation.
        generation_timestamp: Timestamp when metadata was generated.
    """

    table_id: str
    schema: dict[str, Any]
    semantic_summary: str
    search_keywords: list[str]
    entity_mapping: dict[str, str]
    custom_tags: list[str]
    data_statistics: dict[str, Any]
    embedding_ready_text: str
    generation_timestamp: str

    @property
    def record_count(self) -> int:
        """レコード数取得（後方互換性）。

        Returns:
            データのレコード数
        """
        return self.data_statistics.get("record_count", 0)

    @property
    def column_count(self) -> int:
        """カラム数取得。

        Returns:
            データのカラム数
        """
        return self.data_statistics.get("column_count", 0)


class RAGMetadataExtractor:
    """Extract RAG metadata from JSON table data.

    Modular implementation preserving complete backward compatibility.
    Delegates functionality to specialized modules while maintaining
    the same public API.
    """

    def __init__(self) -> None:
        """Initialize metadata extractor with modular components."""
        # Initialize modular components
        self.japanese_patterns = JapanesePatternManager()
        self.schema_generator = SchemaGenerator(self.japanese_patterns)

        # Legacy compatibility attributes
        self.japanese_patterns_dict = self.japanese_patterns.entity_patterns
        self.type_inference_patterns = self.japanese_patterns.type_patterns

    def extract(self, json_data: JsonData, options: dict[str, Any]) -> BasicMetadata:
        """Extract basic RAG metadata from JSON data.

        Args:
            json_data: JSON data to process (dict, list of dicts, or list).
            options: Options passed from directive.

        Returns:
            BasicMetadata containing extracted metadata information.

        Raises:
            ValueError: If data format is invalid or processing fails.
        """
        try:
            # Validate data
            if json_data is None:
                raise ValueError("Data is null")

            # Generate basic information using modular components
            table_id = self._generate_table_id(json_data, options)
            schema = self.schema_generator.extract_schema(json_data)
            semantic_summary = self._generate_semantic_summary(json_data, schema)
            search_keywords = self._extract_search_keywords(json_data, schema)
            entity_mapping = self._map_entities(json_data, schema)
            custom_tags = self._parse_custom_tags(options.get("metadata-tags", ""))
            data_statistics = self._calculate_basic_statistics(json_data)
            embedding_ready_text = self._prepare_embedding_text(json_data, schema)

            return BasicMetadata(
                table_id=table_id,
                schema=schema,
                semantic_summary=semantic_summary,
                search_keywords=search_keywords,
                entity_mapping=entity_mapping,
                custom_tags=custom_tags,
                data_statistics=data_statistics,
                embedding_ready_text=embedding_ready_text,
                generation_timestamp=datetime.now().isoformat(),
            )

        except Exception as e:
            logger.error(f"Metadata extraction error: {e}")
            raise ValueError(f"Failed to extract metadata: {e}") from e

    def _generate_table_id(self, json_data: JsonData, options: dict[str, Any]) -> str:
        """Generate unique table identifier.

        Args:
            json_data: Input JSON data.
            options: Processing options.

        Returns:
            Unique table identifier string.
        """
        # Generate hash based on data content
        data_str = json.dumps(json_data, ensure_ascii=False, sort_keys=True)
        data_hash = hashlib.md5(data_str.encode("utf-8")).hexdigest()[:8]

        # Add timestamp element
        timestamp = datetime.now().strftime("%Y%m%d")

        return f"table_{timestamp}_{data_hash}"

    def _generate_semantic_summary(self, data: JsonData, schema: dict[str, Any]) -> str:
        """Generate semantic summary of the data.

        Args:
            data: Input JSON data
            schema: Generated schema

        Returns:
            Human-readable semantic summary
        """
        if isinstance(data, list):
            record_count = len(data)
            if record_count == 0:
                return "空のデータセット"

            # Analyze business context from schema
            business_context = schema.get("x-rag-metadata", {}).get(
                "business_context", "general"
            )
            context_descriptions = {
                "sales": "営業・販売",
                "hr": "人事・労務",
                "finance": "財務・会計",
                "inventory": "在庫・商品",
                "project": "プロジェクト管理",
                "general": "一般",
            }

            context_desc = context_descriptions.get(business_context, "一般")

            if isinstance(data[0], dict):
                column_count = len(data[0].keys()) if data else 0
                return f"{context_desc}関連の{record_count}件のレコード（{column_count}項目）を含むデータテーブル"
            else:
                return f"{context_desc}関連の{record_count}件の値を含むデータリスト"

        elif isinstance(data, dict):
            item_count = len(data.keys())
            return f"{item_count}項目を含む単一データレコード"
        else:
            return "単一データ値"

    def _extract_search_keywords(
        self, data: JsonData, schema: dict[str, Any]
    ) -> list[str]:
        """Extract search keywords from data and schema.

        Args:
            data: Input JSON data
            schema: Generated schema

        Returns:
            List of search keywords
        """
        keywords = set()

        # Extract from schema properties
        if isinstance(data, list) and data and isinstance(data[0], dict):
            properties = schema.get("items", {}).get("properties", {})

            # Add property names as keywords
            for prop_name, prop_info in properties.items():
                keywords.add(prop_name.lower())

                # Add entity types as keywords
                entity_type = prop_info.get("x-entity-type")
                if entity_type:
                    keywords.add(entity_type)

                # Add semantic types as keywords
                semantic_type = prop_info.get("x-semantic-type")
                if semantic_type:
                    keywords.add(semantic_type)

        # Extract business terms from sample data
        sample_texts = []
        if isinstance(data, list) and data:
            for item in data[:5]:  # Sample first 5 items
                if isinstance(item, dict):
                    for value in item.values():
                        if isinstance(value, str) and len(value.strip()) > 0:
                            sample_texts.append(value)
        elif isinstance(data, dict):
            for value in data.values():
                if isinstance(value, str) and len(value.strip()) > 0:
                    sample_texts.append(value)

        # Extract Japanese business terms
        for text in sample_texts:
            business_terms = self.japanese_patterns.extract_business_terms(text)
            keywords.update(business_terms)

        # Business context keywords
        business_context = schema.get("x-rag-metadata", {}).get("business_context")
        if business_context:
            keywords.add(business_context)

        return sorted(keywords)

    def _map_entities(self, data: JsonData, schema: dict[str, Any]) -> dict[str, str]:
        """Map field names to detected entity types.

        Args:
            data: Input JSON data
            schema: Generated schema

        Returns:
            Dictionary mapping field names to entity types
        """
        entity_mapping = {}

        if isinstance(data, list) and data and isinstance(data[0], dict):
            properties = schema.get("items", {}).get("properties", {})

            for field_name, prop_info in properties.items():
                entity_type = prop_info.get("x-entity-type")
                if entity_type:
                    entity_mapping[field_name] = entity_type
                else:
                    # Fallback to semantic type
                    semantic_type = prop_info.get("x-semantic-type")
                    if semantic_type:
                        entity_mapping[field_name] = semantic_type

        elif isinstance(data, dict):
            for field_name in data:
                entity_type = self.japanese_patterns.get_entity_type_for_field(
                    field_name
                )
                if entity_type:
                    entity_mapping[field_name] = entity_type

        return entity_mapping

    def _parse_custom_tags(self, tags_str: str) -> list[str]:
        """Parse custom tags from comma-separated string.

        Args:
            tags_str: Comma-separated tags string

        Returns:
            List of parsed tags
        """
        if not tags_str or not isinstance(tags_str, str):
            return []

        tags = [tag.strip() for tag in tags_str.split(",")]
        return [tag for tag in tags if tag]  # Remove empty strings

    def _calculate_basic_statistics(self, data: JsonData) -> dict[str, Any]:
        """Calculate basic statistics about the data.

        Args:
            data: Input JSON data

        Returns:
            Dictionary containing basic statistics
        """
        stats = {}

        if isinstance(data, list):
            stats["record_count"] = len(data)
            stats["data_type"] = "array"

            if data and isinstance(data[0], dict):
                stats["column_count"] = len(data[0].keys()) if data else 0
                stats["item_type"] = "object"

                # Calculate completeness
                if data:
                    total_cells = len(data) * len(data[0].keys())
                    filled_cells = 0

                    for item in data:
                        if isinstance(item, dict):
                            for value in item.values():
                                if value is not None and value != "":
                                    filled_cells += 1

                    stats["completeness"] = (
                        round(filled_cells / total_cells, 4) if total_cells > 0 else 0
                    )
            else:
                stats["item_type"] = "primitive"
                stats["completeness"] = 1.0

        elif isinstance(data, dict):
            stats["record_count"] = 1
            stats["column_count"] = len(data.keys())
            stats["data_type"] = "object"
            stats["completeness"] = 1.0
        else:
            stats["record_count"] = 1
            stats["column_count"] = 1
            stats["data_type"] = "primitive"
            stats["completeness"] = 1.0

        return stats

    def _prepare_embedding_text(self, data: JsonData, schema: dict[str, Any]) -> str:
        """Prepare text optimized for PLaMo-Embedding-1B.

        Args:
            data: Input JSON data
            schema: Generated schema

        Returns:
            Text optimized for embedding generation
        """
        text_parts = []

        # Add business context
        business_context = schema.get("x-rag-metadata", {}).get(
            "business_context", "general"
        )
        if business_context != "general":
            text_parts.append(f"ビジネス分野: {business_context}")

        # Add data summary
        if isinstance(data, list) and data:
            text_parts.append(f"データ件数: {len(data)}件")

            if isinstance(data[0], dict):
                # Add field descriptions
                properties = schema.get("items", {}).get("properties", {})
                field_descriptions = []

                for field_name, prop_info in properties.items():
                    desc = prop_info.get("description", field_name)
                    field_descriptions.append(f"{field_name}({desc})")

                if field_descriptions:
                    text_parts.append("データ項目: " + ", ".join(field_descriptions))

                # Add sample values for context
                sample_values = []
                for item in data[:3]:  # Use first 3 items for sample
                    if isinstance(item, dict):
                        for key, value in item.items():
                            if isinstance(
                                value, str
                            ) and self.japanese_patterns.is_japanese_text(value):
                                sample_values.append(f"{key}: {value}")
                                break  # One sample per record

                if sample_values:
                    text_parts.append("サンプル: " + "; ".join(sample_values))

        return " | ".join(text_parts)

    # Legacy compatibility methods (delegating to modular components)
    def _init_japanese_patterns(self) -> dict[str, list[str]]:
        """Legacy compatibility method."""
        return self.japanese_patterns.entity_patterns

    def _init_type_patterns(self) -> dict[str, Any]:
        """Legacy compatibility method."""
        return self.japanese_patterns.type_patterns

    def _extract_schema(self, data: JsonData) -> dict[str, Any]:
        """Legacy compatibility method."""
        return self.schema_generator.extract_schema(data)


# Public API exports (maintaining backward compatibility)
__all__ = [
    "BasicMetadata",
    "JapanesePatternManager",
    "RAGMetadataExtractor",
    "SchemaGenerator",
]
