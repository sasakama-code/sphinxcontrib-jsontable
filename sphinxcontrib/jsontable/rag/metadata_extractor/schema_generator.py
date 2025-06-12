"""JSON Schema Generation Module for RAG Metadata Extraction.

This module provides comprehensive JSON Schema generation capabilities
optimized for OpenAPI and JSON-LD compliance. Includes advanced property
analysis and statistical processing for enterprise data analysis.

Features:
- OpenAPI-compliant JSON Schema generation
- Advanced property type inference and analysis
- Statistical data analysis and quality assessment
- JSON-LD semantic web compatibility
- Optimized for enterprise business data

Created: 2025-06-12 (split from metadata_extractor.py)
Author: Claude Code Assistant
"""

from __future__ import annotations

import logging
from typing import Any

from .japanese_patterns import JapanesePatternManager

logger = logging.getLogger(__name__)

JsonData = dict[str, Any] | list[dict[str, Any]] | list[Any]


class SchemaGenerator:
    """Advanced JSON Schema generation with business intelligence features.

    Generates OpenAPI-compliant schemas with semantic annotations
    and statistical analysis for RAG processing optimization.
    """

    def __init__(self, japanese_patterns: JapanesePatternManager) -> None:
        """Initialize schema generator with Japanese pattern support.

        Args:
            japanese_patterns: Japanese language pattern manager instance
        """
        self.japanese_patterns = japanese_patterns

    def extract_schema(self, data: JsonData) -> dict[str, Any]:
        """Generate JSON Schema from data.

        Creates structured schema compliant with OpenAPI and JSON-LD
        specifications for better interoperability.

        Args:
            data: Input JSON data to analyze.

        Returns:
            Complete JSON Schema with metadata annotations.
        """
        if isinstance(data, list):
            if not data:
                return {
                    "type": "array",
                    "items": {},
                    "description": "Empty array",
                    "x-rag-metadata": {"record_count": 0, "is_empty": True},
                }

            # Handle array of objects (most common case)
            if isinstance(data[0], dict):
                # Analyze all objects to get comprehensive schema
                all_properties = {}
                for item in data:
                    if isinstance(item, dict):
                        for key, value in item.items():
                            if key not in all_properties:
                                all_properties[key] = {
                                    "values": [],
                                    "types": set(),
                                    "null_count": 0,
                                }

                            if value is None:
                                all_properties[key]["null_count"] += 1
                            else:
                                all_properties[key]["values"].append(value)
                                all_properties[key]["types"].add(type(value).__name__)

                properties = {}
                required = []

                for key, info in all_properties.items():
                    prop_schema = self._analyze_property(key, info["values"])

                    # Add nullability information
                    if info["null_count"] > 0:
                        if info["null_count"] < len(data):
                            # Mixed null/non-null - make nullable
                            if "type" in prop_schema:
                                prop_schema["type"] = [prop_schema["type"], "null"]
                        else:
                            # All null values
                            prop_schema["type"] = "null"
                    else:
                        # No null values - mark as required
                        required.append(key)

                    properties[key] = prop_schema

                item_schema = {
                    "type": "object",
                    "properties": properties,
                    "additionalProperties": False,
                    "x-rag-metadata": {
                        "record_count": len(data),
                        "property_count": len(properties),
                        "completeness_score": self._calculate_completeness_score(
                            all_properties, len(data)
                        ),
                    },
                }

                if required:
                    item_schema["required"] = required

                return {
                    "type": "array",
                    "items": item_schema,
                    "description": f"Array of {len(data)} business records",
                    "x-rag-metadata": {
                        "record_count": len(data),
                        "data_format": "object_array",
                        "business_context": self._detect_business_context(properties),
                    },
                }

            # Handle array of primitives
            else:
                value_types = {type(item).__name__ for item in data}
                if len(value_types) == 1:
                    item_type = next(iter(value_types)).lower()
                    if item_type == "str":
                        item_type = "string"
                    elif item_type == "int" or item_type == "float":
                        item_type = "number"
                else:
                    item_type = "string"  # Mixed types, default to string

                return {
                    "type": "array",
                    "items": {"type": item_type},
                    "description": f"Array of {len(data)} {item_type} values",
                    "x-rag-metadata": {
                        "record_count": len(data),
                        "data_format": "primitive_array",
                        "value_types": list(value_types),
                    },
                }

        elif isinstance(data, dict):
            properties = {}
            required = []

            for key, value in data.items():
                if value is not None:
                    required.append(key)
                    properties[key] = self._analyze_property(key, [value])
                else:
                    properties[key] = {"type": "null"}

            schema = {
                "type": "object",
                "properties": properties,
                "additionalProperties": False,
                "description": "Single business record object",
                "x-rag-metadata": {
                    "record_count": 1,
                    "property_count": len(properties),
                    "business_context": self._detect_business_context(properties),
                },
            }

            if required:
                schema["required"] = required

            return schema

        else:
            # Single primitive value
            value_type = type(data).__name__.lower()
            if value_type == "str":
                value_type = "string"
            elif value_type in ["int", "float"]:
                value_type = "number"

            return {
                "type": value_type,
                "description": f"Single {value_type} value",
                "x-rag-metadata": {
                    "record_count": 1,
                    "data_format": "primitive_value",
                },
            }

    def _analyze_property(self, key: str, values: list[Any]) -> dict[str, Any]:
        """Analyze property to determine type and characteristics.

        Args:
            key: Property name/key.
            values: List of property values to analyze.

        Returns:
            Property schema with type information and metadata.
        """
        if not values:
            return {"type": "null", "description": f"Property: {key}"}

        # Remove None values for analysis
        non_null_values = [v for v in values if v is not None]
        if not non_null_values:
            return {"type": "null", "description": f"Property: {key}"}

        # Determine basic type
        value_types = {type(v).__name__ for v in non_null_values}

        if len(value_types) == 1:
            python_type = next(iter(value_types))

            if python_type == "str":
                return self._analyze_string_property(key, non_null_values)
            elif python_type in ["int", "float"]:
                return self._analyze_numeric_property(key, non_null_values)
            elif python_type == "bool":
                return {
                    "type": "boolean",
                    "description": f"Boolean property: {key}",
                    "x-semantic-type": "flag",
                }
            elif python_type == "list":
                return {
                    "type": "array",
                    "description": f"Array property: {key}",
                    "x-semantic-type": "collection",
                }
            elif python_type == "dict":
                return {
                    "type": "object",
                    "description": f"Object property: {key}",
                    "x-semantic-type": "nested_object",
                }

        # Mixed types - default to string with conversion info
        return {
            "type": "string",
            "description": f"Mixed-type property: {key}",
            "x-semantic-type": "mixed",
            "x-original-types": list(value_types),
        }

    def _analyze_string_property(self, key: str, values: list[str]) -> dict[str, Any]:
        """Analyze string property for semantic type and patterns.

        Args:
            key: Property name
            values: List of string values

        Returns:
            String property schema with semantic annotations
        """
        property_schema = {
            "type": "string",
            "description": self._generate_property_description(key, values),
        }

        # Basic statistics
        lengths = [len(str(v)) for v in values]
        if lengths:
            property_schema["minLength"] = min(lengths)
            property_schema["maxLength"] = max(lengths)

        # Semantic type detection using Japanese patterns
        semantic_type = self.japanese_patterns.get_entity_type_for_field(key)
        if semantic_type:
            property_schema["x-entity-type"] = semantic_type

        # Pattern analysis for sample values
        sample_values = values[:10]  # Analyze up to 10 samples
        pattern_analysis = {}

        for value in sample_values:
            if isinstance(value, str):
                detected_type, description = self.japanese_patterns.infer_semantic_type(
                    value
                )
                if detected_type:
                    if detected_type not in pattern_analysis:
                        pattern_analysis[detected_type] = {
                            "count": 0,
                            "description": description,
                        }
                    pattern_analysis[detected_type]["count"] += 1

        if pattern_analysis:
            # Use the most common pattern
            most_common = max(pattern_analysis.items(), key=lambda x: x[1]["count"])
            property_schema["x-semantic-type"] = most_common[0]
            property_schema["x-pattern-description"] = most_common[1]["description"]

        # Unique value analysis
        unique_values = list(set(values))
        if len(unique_values) <= 10:
            property_schema["enum"] = unique_values
            property_schema["x-is-categorical"] = True
        elif len(unique_values) < len(values) * 0.5:
            property_schema["x-is-categorical"] = True
            property_schema["x-unique-count"] = len(unique_values)

        return property_schema

    def _analyze_numeric_property(
        self, key: str, values: list[float | int]
    ) -> dict[str, Any]:
        """Analyze numeric property for statistical information.

        Args:
            key: Property name
            values: List of numeric values

        Returns:
            Numeric property schema with statistical metadata
        """
        numeric_values = [float(v) for v in values if isinstance(v, int | float)]

        if not numeric_values:
            return {"type": "number", "description": f"Numeric property: {key}"}

        # Calculate statistics
        stats = self._calculate_numeric_stats(numeric_values)

        property_schema = {
            "type": "number",
            "description": self._generate_property_description(key, values),
            "minimum": stats["min"],
            "maximum": stats["max"],
            "x-statistics": stats,
        }

        # Detect if it's likely an integer
        if all(float(v).is_integer() for v in numeric_values):
            property_schema["type"] = "integer"

        # Entity type detection
        entity_type = self.japanese_patterns.get_entity_type_for_field(key)
        if entity_type == "amount":
            property_schema["x-semantic-type"] = "monetary"
            property_schema["x-currency"] = "JPY"  # Default for Japanese business data
        elif "id" in key.lower() or "番号" in key:
            property_schema["x-semantic-type"] = "identifier"
        elif "count" in key.lower() or "数" in key:
            property_schema["x-semantic-type"] = "count"

        return property_schema

    def _calculate_numeric_stats(self, values: list[float]) -> dict[str, Any]:
        """Calculate comprehensive numeric statistics.

        Args:
            values: List of numeric values

        Returns:
            Dictionary containing statistical measures
        """
        if not values:
            return {}

        sorted_values = sorted(values)
        n = len(values)

        # Basic statistics
        min_val = min(values)
        max_val = max(values)
        total = sum(values)
        mean = total / n

        # Median calculation
        if n % 2 == 0:
            median = (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2
        else:
            median = sorted_values[n // 2]

        # Variance and standard deviation
        variance = sum((x - mean) ** 2 for x in values) / n
        std_dev = variance**0.5

        # Quartiles
        q1_idx = n // 4
        q3_idx = 3 * n // 4
        q1 = sorted_values[q1_idx] if q1_idx < n else sorted_values[-1]
        q3 = sorted_values[q3_idx] if q3_idx < n else sorted_values[-1]

        return {
            "count": n,
            "min": min_val,
            "max": max_val,
            "sum": total,
            "mean": round(mean, 4),
            "median": median,
            "std_dev": round(std_dev, 4),
            "variance": round(variance, 4),
            "q1": q1,
            "q3": q3,
            "range": max_val - min_val,
        }

    def _get_unique_values(self, values: list[Any], limit: int = 100) -> list[Any]:
        """Get unique values from a list with optional limit.

        Args:
            values: Input values list
            limit: Maximum number of unique values to return

        Returns:
            List of unique values (limited)
        """
        unique_values = list(set(values))
        return unique_values[:limit]

    def _generate_property_description(self, key: str, values: list[Any]) -> str:
        """Generate human-readable description for a property.

        Args:
            key: Property name
            values: Sample values

        Returns:
            Human-readable property description
        """
        # Basic entity type description
        entity_type = self.japanese_patterns.get_entity_type_for_field(key)

        if entity_type == "name":
            return f"名前情報: {key}"
        elif entity_type == "organization":
            return f"組織・会社情報: {key}"
        elif entity_type == "date":
            return f"日付・時刻情報: {key}"
        elif entity_type == "amount":
            return f"金額・数値情報: {key}"
        elif entity_type == "location":
            return f"住所・場所情報: {key}"
        else:
            # Analyze sample values for context
            sample_str = str(values[0]) if values else ""
            if self.japanese_patterns.is_japanese_text(sample_str):
                return f"日本語テキスト情報: {key}"
            else:
                return f"データ項目: {key}"

    def _calculate_completeness_score(
        self, properties: dict[str, dict], total_records: int
    ) -> float:
        """Calculate data completeness score.

        Args:
            properties: Property analysis results
            total_records: Total number of records

        Returns:
            Completeness score between 0 and 1
        """
        if not properties or total_records == 0:
            return 0.0

        total_cells = len(properties) * total_records
        filled_cells = sum(
            len(prop_info["values"]) for prop_info in properties.values()
        )

        return round(filled_cells / total_cells, 4)

    def _detect_business_context(self, properties: dict[str, dict]) -> str:
        """Detect business context from property names.

        Args:
            properties: Schema properties

        Returns:
            Detected business context string
        """
        property_names = list(properties.keys())
        name_text = " ".join(property_names).lower()

        contexts = {
            "sales": ["売上", "sales", "revenue", "顧客", "customer", "営業"],
            "hr": ["社員", "employee", "給与", "salary", "人事", "hr"],
            "finance": ["金額", "amount", "価格", "price", "財務", "finance", "会計"],
            "inventory": ["在庫", "inventory", "商品", "product", "stock"],
            "project": ["プロジェクト", "project", "タスク", "task", "進捗"],
        }

        for context, keywords in contexts.items():
            if any(keyword in name_text for keyword in keywords):
                return context

        return "general"
