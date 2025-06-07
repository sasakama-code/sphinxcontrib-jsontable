"""
Metadata Exporter for Phase 2 RAG Integration

メタデータ多形式出力機能：
- JSON-LD形式出力
- OpenSearch/Elasticsearch マッピング生成
- PLaMo-Embedding-1B用特殊形式
- 検索エンジン用インデックス設定
- カスタム形式対応
"""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from typing import Any

from .advanced_metadata import AdvancedMetadata
from .search_facets import GeneratedFacets


class MetadataExporter:
    """多形式メタデータ出力器"""

    def __init__(self):
        """メタデータ出力器の初期化"""
        self.supported_formats = [
            "json-ld",
            "opensearch",
            "elasticsearch",
            "plamo-ready",
            "search-config",
            "facet-config",
            "custom",
        ]

    def export_metadata(
        self,
        advanced_metadata: AdvancedMetadata,
        generated_facets: GeneratedFacets,
        formats: list[str],
        custom_config: dict | None = None,
    ) -> dict[str, Any]:
        """指定形式でメタデータを出力"""
        exports = {}

        for format_type in formats:
            if format_type not in self.supported_formats:
                continue

            try:
                if format_type == "json-ld":
                    exports["json-ld"] = self._export_json_ld(advanced_metadata)
                elif format_type == "opensearch":
                    exports["opensearch"] = self._export_opensearch(advanced_metadata)
                elif format_type == "elasticsearch":
                    exports["elasticsearch"] = self._export_elasticsearch(advanced_metadata)
                elif format_type == "plamo-ready":
                    exports["plamo-ready"] = self._export_plamo_ready(advanced_metadata)
                elif format_type == "search-config":
                    exports["search-config"] = self._export_search_config(
                        advanced_metadata, generated_facets
                    )
                elif format_type == "facet-config":
                    exports["facet-config"] = self._export_facet_config(generated_facets)
                elif format_type == "custom":
                    exports["custom"] = self._export_custom(
                        advanced_metadata, custom_config or {}
                    )
            except Exception as e:
                exports[f"{format_type}_error"] = str(e)

        return exports

    def _export_json_ld(self, metadata: AdvancedMetadata) -> dict:
        """JSON-LD形式でのメタデータ出力"""
        # JSON-LD コンテキスト定義
        context = {
            "@vocab": "http://schema.org/",
            "rag": "http://example.com/rag-schema/",
            "jsontable": "http://example.com/jsontable-schema/",
            # データ型定義
            "statisticalAnalysis": {"@type": "rag:StatisticalAnalysis"},
            "entityClassification": {"@type": "rag:EntityClassification"},
            "dataQuality": {"@type": "rag:DataQualityReport"},
            "searchFacets": {"@type": "rag:SearchFacets"},
            "plamoFeatures": {"@type": "rag:PLaMoFeatures"},
        }

        # メインデータ構造
        json_ld = {
            "@context": context,
            "@type": "Dataset",
            "@id": f"rag:dataset-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "name": self._extract_dataset_name(metadata),
            "description": self._generate_dataset_description(metadata),
            "dateCreated": datetime.now().isoformat(),
            "creator": {
                "@type": "SoftwareApplication",
                "name": "sphinxcontrib-jsontable-rag",
                "version": metadata.basic_metadata.get("rag_version", "1.0.0"),
            },
            # RAG特有のメタデータ
            "rag:statisticalAnalysis": self._format_statistical_analysis_for_jsonld(
                metadata.statistical_analysis
            ),
            "rag:entityClassification": self._format_entity_classification_for_jsonld(
                metadata.entity_classification
            ),
            "rag:dataQuality": self._format_data_quality_for_jsonld(metadata.data_quality),
            "rag:plamoFeatures": self._format_plamo_features_for_jsonld(
                metadata.plamo_features
            ),
            # データセット詳細
            "distribution": {
                "@type": "DataDownload",
                "encodingFormat": "application/json",
                "contentSize": self._estimate_content_size(metadata),
            },
            "keywords": self._extract_keywords(metadata),
            "variableMeasured": self._extract_variables(metadata),
        }

        return json_ld

    def _export_opensearch(self, metadata: AdvancedMetadata) -> dict:
        """OpenSearch用マッピング定義生成"""
        mapping = {
            "settings": {
                "index": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0,
                    "analysis": {
                        "analyzer": {
                            "japanese_analyzer": {
                                "type": "custom",
                                "tokenizer": "kuromoji_tokenizer",
                                "filter": [
                                    "kuromoji_baseform",
                                    "kuromoji_part_of_speech",
                                    "ja_stop",
                                    "kuromoji_stemmer",
                                    "lowercase",
                                ],
                            }
                        }
                    },
                }
            },
            "mappings": {"properties": {}},
        }

        # フィールドマッピングの生成
        properties = mapping["mappings"]["properties"]

        # 統計分析フィールドのマッピング
        statistical_analysis = metadata.statistical_analysis

        # 数値フィールド
        for field_name, stats in statistical_analysis.get("numerical_fields", {}).items():
            properties[field_name] = {
                "type": "float",
                "fields": {
                    "keyword": {"type": "keyword"},
                    "range": {
                        "type": "integer_range"
                        if stats.get("distribution_type") == "integer"
                        else "float_range"
                    },
                },
            }

        # カテゴリフィールド
        for field_name, stats in statistical_analysis.get("categorical_fields", {}).items():
            field_mapping = {
                "type": "text",
                "analyzer": "japanese_analyzer",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
            }

            # 日本語テキストの検出
            sample_values = list(stats.get("value_counts", {}).keys())[:5]
            if any(self._contains_japanese(str(value)) for value in sample_values):
                field_mapping["analyzer"] = "japanese_analyzer"

            properties[field_name] = field_mapping

        # エンティティフィールド
        entity_classification = metadata.entity_classification

        if entity_classification.persons:
            properties["detected_persons"] = {
                "type": "nested",
                "properties": {
                    "name": {"type": "text", "analyzer": "japanese_analyzer"},
                    "confidence": {"type": "float"},
                    "name_type": {"type": "keyword"},
                },
            }

        if entity_classification.places:
            properties["detected_places"] = {
                "type": "nested",
                "properties": {
                    "place": {"type": "text", "analyzer": "japanese_analyzer"},
                    "confidence": {"type": "float"},
                    "place_type": {"type": "keyword"},
                },
            }

        if entity_classification.organizations:
            properties["detected_organizations"] = {
                "type": "nested",
                "properties": {
                    "organization": {"type": "text", "analyzer": "japanese_analyzer"},
                    "confidence": {"type": "float"},
                    "org_type": {"type": "keyword"},
                },
            }

        # PLaMo特徴量フィールド
        properties["plamo_features"] = {
            "type": "object",
            "properties": {
                "kanji_density": {"type": "float"},
                "katakana_terms": {"type": "keyword"},
                "domain": {"type": "keyword"},
                "formality_level": {"type": "keyword"},
                "technical_level": {"type": "keyword"},
            },
        }

        # データ品質メトリクス
        properties["data_quality"] = {
            "type": "object",
            "properties": {
                "completeness_score": {"type": "float"},
                "consistency_score": {"type": "float"},
                "validity_score": {"type": "float"},
                "overall_score": {"type": "float"},
            },
        }

        return mapping

    def _export_elasticsearch(self, metadata: AdvancedMetadata) -> dict:
        """Elasticsearch用マッピング定義生成"""
        # OpenSearchとほぼ同じだが、一部Elasticsearchの違いを反映
        opensearch_mapping = self._export_opensearch(metadata)

        # Elasticsearch特有の調整
        elasticsearch_mapping = opensearch_mapping.copy()

        # Elasticsearchのanalyzer名調整
        settings = elasticsearch_mapping["settings"]["index"]["analysis"]["analyzer"]
        settings["japanese_analyzer"]["tokenizer"] = "kuromoji_tokenizer"

        # Elasticsearch特有のフィールド設定
        properties = elasticsearch_mapping["mappings"]["properties"]

        # ベクトル検索フィールド（Elasticsearch 8.0以降）
        properties["embedding_vector"] = {
            "type": "dense_vector",
            "dims": 1024,  # PLaMo-Embedding-1Bの次元数
            "index": True,
            "similarity": "cosine",
        }

        return elasticsearch_mapping

    def _export_plamo_ready(self, metadata: AdvancedMetadata) -> dict:
        """PLaMo-Embedding-1B用特殊形式出力"""
        plamo_features = metadata.plamo_features

        plamo_config = {
            "model_config": {
                "model_name": "PLaMo-Embedding-1B",
                "embedding_dimension": 1024,
                "max_sequence_length": 512,
                "batch_size": 32,
            },
            "preprocessing_config": {
                "text_segmentation": {
                    "strategy": plamo_features.vector_optimization.get(
                        "chunk_strategy", "semantic_boundary"
                    ),
                    "max_chunk_length": plamo_features.vector_optimization.get(
                        "max_chunk_length", 512
                    ),
                    "overlap_ratio": plamo_features.vector_optimization.get("overlap_ratio", 0.1),
                    "prioritize_entities": plamo_features.vector_optimization.get(
                        "prioritize_entities", True
                    ),
                },
                "japanese_optimization": {
                    "enable_kuromoji": True,
                    "normalize_kanji": True,
                    "handle_katakana": True,
                    "preserve_honorifics": True,
                },
            },
            "text_segments": plamo_features.text_segments,
            "japanese_features": plamo_features.japanese_features,
            "embedding_hints": plamo_features.embedding_hints,
            "entity_enhancement": {
                "persons": [asdict(p) for p in metadata.entity_classification.persons],
                "places": [asdict(p) for p in metadata.entity_classification.places],
                "organizations": [
                    asdict(o) for o in metadata.entity_classification.organizations
                ],
                "business_terms": [
                    asdict(b) for b in metadata.entity_classification.business_terms
                ],
            },
            "quality_metrics": {
                "overall_score": metadata.data_quality.overall_score,
                "text_quality_indicators": {
                    "formality_level": plamo_features.embedding_hints.get("formality_level"),
                    "technical_level": plamo_features.embedding_hints.get("technical_level"),
                    "domain": plamo_features.embedding_hints.get("domain"),
                },
            },
        }

        return plamo_config

    def _export_search_config(
        self, metadata: AdvancedMetadata, facets: GeneratedFacets
    ) -> dict:
        """検索エンジン用設定出力"""
        search_config = {
            "search_settings": {
                "default_operator": "AND",
                "minimum_should_match": "75%",
                "boost_config": self._generate_boost_config(metadata),
                "highlight_config": {
                    "fields": self._get_highlightable_fields(metadata),
                    "pre_tags": ["<mark>"],
                    "post_tags": ["</mark>"],
                },
            },
            "facet_settings": {
                "categorical_facets": [asdict(f) for f in facets.categorical_facets],
                "numerical_facets": [asdict(f) for f in facets.numerical_facets],
                "temporal_facets": [asdict(f) for f in facets.temporal_facets],
                "entity_facets": [asdict(f) for f in facets.entity_facets],
            },
            "aggregation_config": self._generate_aggregation_config(facets),
            "suggestion_config": {
                "enable_autocomplete": True,
                "suggestion_fields": self._get_suggestion_fields(metadata),
                "fuzzy_matching": True,
                "japanese_reading_support": True,
            },
        }

        return search_config

    def _export_facet_config(self, facets: GeneratedFacets) -> dict:
        """ファセット設定専用出力"""
        facet_config = {
            "ui_configuration": {
                "layout": "sidebar",
                "collapsible_sections": True,
                "max_visible_facets": 8,
                "enable_facet_search": True,
            },
            "facet_groups": self._organize_facets_into_groups(facets),
            "interaction_config": {
                "multiple_selection": True,
                "clear_all_button": True,
                "facet_counting": True,
                "dynamic_filtering": True,
            },
            "display_config": {
                "show_facet_counts": True,
                "show_zero_counts": False,
                "facet_sorting": "count_desc",
                "localization": "ja_JP",
            },
        }

        return facet_config

    def _export_custom(self, metadata: AdvancedMetadata, config: dict) -> dict:
        """カスタム形式出力"""
        custom_format = config.get("format", {})
        include_sections = config.get("include_sections", ["all"])

        custom_output = {"metadata_format": "custom", "generated_at": datetime.now().isoformat()}

        if "all" in include_sections or "basic" in include_sections:
            custom_output["basic_metadata"] = metadata.basic_metadata

        if "all" in include_sections or "statistical" in include_sections:
            custom_output["statistical_analysis"] = metadata.statistical_analysis

        if "all" in include_sections or "entities" in include_sections:
            custom_output["entity_classification"] = {
                "persons": [asdict(p) for p in metadata.entity_classification.persons],
                "places": [asdict(p) for p in metadata.entity_classification.places],
                "organizations": [
                    asdict(o) for o in metadata.entity_classification.organizations
                ],
                "business_terms": [
                    asdict(b) for b in metadata.entity_classification.business_terms
                ],
            }

        if "all" in include_sections or "quality" in include_sections:
            custom_output["data_quality"] = asdict(metadata.data_quality)

        if "all" in include_sections or "plamo" in include_sections:
            custom_output["plamo_features"] = asdict(metadata.plamo_features)

        # カスタム変換の適用
        if "transformations" in custom_format:
            custom_output = self._apply_custom_transformations(
                custom_output, custom_format["transformations"]
            )

        return custom_output

    # ヘルパーメソッド群

    def _extract_dataset_name(self, metadata: AdvancedMetadata) -> str:
        """データセット名の抽出"""
        source_info = metadata.basic_metadata.get("source_info", {})
        file_path = source_info.get("file_path")

        if file_path:
            return f"JSON Table Dataset: {file_path}"
        else:
            return "JSON Table Dataset (Inline)"

    def _generate_dataset_description(self, metadata: AdvancedMetadata) -> str:
        """データセット説明の生成"""
        stats = metadata.statistical_analysis
        entity_count = (
            len(metadata.entity_classification.persons)
            + len(metadata.entity_classification.places)
            + len(metadata.entity_classification.organizations)
            + len(metadata.entity_classification.business_terms)
        )

        numerical_fields = len(stats.get("numerical_fields", {}))
        categorical_fields = len(stats.get("categorical_fields", {}))

        description = f"JSONテーブルデータセット。"
        description += f"数値フィールド{numerical_fields}個、"
        description += f"カテゴリフィールド{categorical_fields}個を含む。"

        if entity_count > 0:
            description += f"日本語エンティティ{entity_count}個を検出。"

        quality_score = metadata.data_quality.overall_score
        description += f"データ品質スコア: {quality_score:.2f}"

        return description

    def _format_statistical_analysis_for_jsonld(self, analysis: dict) -> dict:
        """統計分析をJSON-LD形式でフォーマット"""
        formatted = {"@type": "rag:StatisticalAnalysis"}

        if "numerical_fields" in analysis:
            formatted["numericalFields"] = {}
            for field, stats in analysis["numerical_fields"].items():
                formatted["numericalFields"][field] = {
                    "@type": "rag:NumericalStats",
                    "mean": stats.get("mean"),
                    "median": stats.get("median"),
                    "standardDeviation": stats.get("std_dev"),
                    "range": {
                        "min": stats.get("min_value"),
                        "max": stats.get("max_value"),
                    },
                    "distributionType": stats.get("distribution_type"),
                }

        if "categorical_fields" in analysis:
            formatted["categoricalFields"] = {}
            for field, stats in analysis["categorical_fields"].items():
                formatted["categoricalFields"][field] = {
                    "@type": "rag:CategoricalStats",
                    "uniqueCount": stats.get("unique_count"),
                    "entropy": stats.get("entropy"),
                    "diversityIndex": stats.get("diversity_index"),
                }

        return formatted

    def _format_entity_classification_for_jsonld(self, entities) -> dict:
        """エンティティ分類をJSON-LD形式でフォーマット"""
        return {
            "@type": "rag:EntityClassification",
            "persons": [
                {
                    "@type": "rag:PersonEntity",
                    "name": p.name,
                    "confidence": p.confidence,
                    "nameType": p.name_type,
                }
                for p in entities.persons
            ],
            "places": [
                {
                    "@type": "rag:PlaceEntity",
                    "place": p.place,
                    "confidence": p.confidence,
                    "placeType": p.place_type,
                }
                for p in entities.places
            ],
            "organizations": [
                {
                    "@type": "rag:OrganizationEntity",
                    "organization": o.organization,
                    "confidence": o.confidence,
                    "organizationType": o.org_type,
                }
                for o in entities.organizations
            ],
        }

    def _format_data_quality_for_jsonld(self, quality) -> dict:
        """データ品質をJSON-LD形式でフォーマット"""
        return {
            "@type": "rag:DataQualityReport",
            "completenessScore": quality.completeness_score,
            "consistencyScore": quality.consistency_score,
            "validityScore": quality.validity_score,
            "accuracyScore": quality.accuracy_score,
            "overallScore": quality.overall_score,
        }

    def _format_plamo_features_for_jsonld(self, features) -> dict:
        """PLaMo特徴量をJSON-LD形式でフォーマット"""
        return {
            "@type": "rag:PLaMoFeatures",
            "japaneseFeatures": features.japanese_features,
            "embeddingHints": features.embedding_hints,
            "vectorOptimization": features.vector_optimization,
        }

    def _estimate_content_size(self, metadata: AdvancedMetadata) -> str:
        """コンテンツサイズの推定"""
        # 基本的な推定ロジック
        json_str = json.dumps(asdict(metadata), ensure_ascii=False)
        size_bytes = len(json_str.encode("utf-8"))

        if size_bytes < 1024:
            return f"{size_bytes} bytes"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"

    def _extract_keywords(self, metadata: AdvancedMetadata) -> list[str]:
        """キーワードの抽出"""
        keywords = ["JSON", "table", "RAG", "日本語"]

        # エンティティからキーワード抽出
        entities = metadata.entity_classification
        if entities.places:
            keywords.append("地理データ")
        if entities.persons:
            keywords.append("人名データ")
        if entities.organizations:
            keywords.append("組織データ")

        # ドメイン情報
        domain = metadata.plamo_features.embedding_hints.get("domain")
        if domain:
            keywords.append(domain)

        return list(set(keywords))

    def _extract_variables(self, metadata: AdvancedMetadata) -> list[dict]:
        """変数の抽出"""
        variables = []

        # 数値変数
        for field_name, stats in metadata.statistical_analysis.get("numerical_fields", {}).items():
            variables.append({
                "@type": "PropertyValue",
                "name": field_name,
                "description": f"数値フィールド: {field_name}",
                "minValue": stats.get("min_value"),
                "maxValue": stats.get("max_value"),
                "unitText": self._guess_unit(field_name),
            })

        # カテゴリ変数
        for field_name, stats in metadata.statistical_analysis.get("categorical_fields", {}).items():
            variables.append({
                "@type": "PropertyValue",
                "name": field_name,
                "description": f"カテゴリフィールド: {field_name}",
                "valueReference": list(stats.get("value_counts", {}).keys())[:10],
            })

        return variables

    def _guess_unit(self, field_name: str) -> str:
        """フィールド名から単位を推測"""
        field_lower = field_name.lower()

        if any(keyword in field_lower for keyword in ["age", "年齢"]):
            return "歳"
        elif any(keyword in field_lower for keyword in ["price", "salary", "cost", "金額", "給与"]):
            return "円"
        elif any(keyword in field_lower for keyword in ["percent", "rate", "割合"]):
            return "%"
        elif any(keyword in field_lower for keyword in ["count", "number", "件数"]):
            return "件"
        else:
            return ""

    def _contains_japanese(self, text: str) -> bool:
        """日本語文字を含むかチェック"""
        import re

        return bool(re.search(r"[ひらがなカタカナ一-龯]", text))

    def _generate_boost_config(self, metadata: AdvancedMetadata) -> dict:
        """検索ブースト設定の生成"""
        boost_config = {}

        # エンティティフィールドのブースト
        if metadata.entity_classification.persons:
            boost_config["detected_persons.name"] = 2.0

        if metadata.entity_classification.organizations:
            boost_config["detected_organizations.organization"] = 1.5

        # 重要フィールドの推定とブースト
        for field_name in metadata.statistical_analysis.get("categorical_fields", {}):
            if any(
                keyword in field_name.lower()
                for keyword in ["name", "title", "主", "名前", "タイトル"]
            ):
                boost_config[field_name] = 2.5

        return boost_config

    def _get_highlightable_fields(self, metadata: AdvancedMetadata) -> list[str]:
        """ハイライト対象フィールドの取得"""
        fields = []

        # テキストフィールド
        for field_name in metadata.statistical_analysis.get("categorical_fields", {}):
            fields.append(field_name)

        # エンティティフィールド
        if metadata.entity_classification.persons:
            fields.append("detected_persons.name")
        if metadata.entity_classification.places:
            fields.append("detected_places.place")
        if metadata.entity_classification.organizations:
            fields.append("detected_organizations.organization")

        return fields

    def _generate_aggregation_config(self, facets: GeneratedFacets) -> dict:
        """集計設定の生成"""
        aggregations = {}

        # カテゴリ集計
        for facet in facets.categorical_facets:
            aggregations[f"{facet.field_name}_terms"] = {
                "terms": {"field": f"{facet.field_name}.keyword", "size": 20}
            }

        # 数値範囲集計
        for facet in facets.numerical_facets:
            aggregations[f"{facet.field_name}_range"] = {
                "range": {
                    "field": facet.field_name,
                    "ranges": [
                        {"from": r["from"], "to": r["to"], "key": r["label"]}
                        for r in facet.ranges
                    ],
                }
            }

        # 統計集計
        for facet in facets.numerical_facets:
            aggregations[f"{facet.field_name}_stats"] = {"stats": {"field": facet.field_name}}

        return aggregations

    def _get_suggestion_fields(self, metadata: AdvancedMetadata) -> list[str]:
        """サジェスト対象フィールドの取得"""
        suggestion_fields = []

        # 高い多様性を持つカテゴリフィールド
        for field_name, stats in metadata.statistical_analysis.get("categorical_fields", {}).items():
            diversity = stats.get("diversity_index", 0)
            if diversity > 0.5:  # 多様性が高い
                suggestion_fields.append(field_name)

        return suggestion_fields

    def _organize_facets_into_groups(self, facets: GeneratedFacets) -> list[dict]:
        """ファセットをグループ化"""
        groups = []

        if facets.categorical_facets:
            groups.append({
                "group_name": "カテゴリ",
                "group_id": "categorical",
                "facets": [f.field_name for f in facets.categorical_facets],
                "collapsed": False,
            })

        if facets.numerical_facets:
            groups.append({
                "group_name": "数値範囲",
                "group_id": "numerical",
                "facets": [f.field_name for f in facets.numerical_facets],
                "collapsed": False,
            })

        if facets.temporal_facets:
            groups.append({
                "group_name": "日付・時間",
                "group_id": "temporal",
                "facets": [f.field_name for f in facets.temporal_facets],
                "collapsed": True,
            })

        if facets.entity_facets:
            groups.append({
                "group_name": "エンティティ",
                "group_id": "entities",
                "facets": [f.entity_type for f in facets.entity_facets],
                "collapsed": True,
            })

        return groups

    def _apply_custom_transformations(self, data: dict, transformations: list) -> dict:
        """カスタム変換の適用"""
        result = data.copy()

        for transformation in transformations:
            transform_type = transformation.get("type")
            params = transformation.get("parameters", {})

            if transform_type == "rename_fields":
                field_mappings = params.get("mappings", {})
                for old_name, new_name in field_mappings.items():
                    if old_name in result:
                        result[new_name] = result.pop(old_name)

            elif transform_type == "filter_fields":
                allowed_fields = params.get("allowed_fields", [])
                if allowed_fields:
                    result = {k: v for k, v in result.items() if k in allowed_fields}

            elif transform_type == "flatten":
                # ネストした構造をフラット化
                result = self._flatten_dict(result, params.get("separator", "_"))

        return result

    def _flatten_dict(self, nested_dict: dict, separator: str = "_") -> dict:
        """辞書のフラット化"""
        flattened = {}

        def _flatten(obj, parent_key=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_key = f"{parent_key}{separator}{key}" if parent_key else key
                    _flatten(value, new_key)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    new_key = f"{parent_key}{separator}{i}" if parent_key else str(i)
                    _flatten(item, new_key)
            else:
                flattened[parent_key] = obj

        _flatten(nested_dict)
        return flattened