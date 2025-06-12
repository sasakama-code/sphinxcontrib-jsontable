"""Advanced metadata generator with Japanese language specialization.

Provides comprehensive metadata generation capabilities including deep
statistical analysis, Japanese entity classification, data quality assessment,
and PLaMo-Embedding-1B integration preparation for enhanced RAG processing.

Features:
- Advanced statistical analysis with distribution classification
- Japanese-specialized entity recognition and classification
- Comprehensive data quality assessment and reporting
- PLaMo-Embedding-1B optimized feature preparation
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from .categorical_analytics import CategoricalAnalyzer

# Import分割された分析モジュール
from .numerical_analytics import StatisticalAnalyzer
from .temporal_analytics import (
    EntityClassification,
    JapaneseEntityClassifier,
)


@dataclass
class DataQualityReport:
    """Comprehensive data quality assessment with multi-dimensional scoring.

    Attributes:
        completeness_score: Completeness score (0.0-1.0).
        consistency_score: Consistency score (0.0-1.0).
        validity_score: Validity score (0.0-1.0).
        accuracy_score: Accuracy score (0.0-1.0).
        overall_score: Overall quality score (0.0-1.0).
        detailed_issues: Detailed list of issues by category.
    """

    completeness_score: float
    consistency_score: float
    validity_score: float
    accuracy_score: float
    overall_score: float
    detailed_issues: dict[str, list[str]] = field(default_factory=dict)


@dataclass
class SearchFacets:
    """Search facet configuration definitions for multi-dimensional filtering.

    Attributes:
        categorical: Categorical facet configurations.
        numerical: Numerical facet configurations.
        temporal: Temporal facet configurations.
        entities: Entity-based facet configurations.
    """

    categorical: dict[str, Any] = field(default_factory=dict)
    numerical: dict[str, Any] = field(default_factory=dict)
    temporal: dict[str, Any] = field(default_factory=dict)
    entities: dict[str, Any] = field(default_factory=dict)


@dataclass
class PLaMoFeatures:
    """Optimized features prepared for PLaMo-Embedding-1B processing.

    Attributes:
        text_segments: Text segments processed for embedding generation.
        japanese_features: Japanese language-specific feature enhancements.
        embedding_hints: Optimization hints for embedding processing.
        vector_optimization: Vector generation optimization parameters.
    """

    text_segments: list[str]
    japanese_features: dict[str, Any]
    embedding_hints: dict[str, Any]
    vector_optimization: dict[str, Any]


@dataclass
class AdvancedMetadata:
    """Comprehensive advanced metadata structure for Phase 2 RAG integration.

    Attributes:
        basic_metadata: Basic metadata from Phase 1 processing.
        statistical_analysis: Comprehensive statistical analysis results.
        entity_classification: Classified entity extraction results.
        data_quality: Data quality assessment report.
        search_facets: Generated search facet configurations.
        plamo_features: PLaMo-Embedding-1B optimized features.
    """

    basic_metadata: dict
    statistical_analysis: dict[str, Any]
    entity_classification: EntityClassification
    data_quality: DataQualityReport
    search_facets: SearchFacets
    plamo_features: PLaMoFeatures


class DataQualityAssessor:
    """データ品質の多角的評価"""

    def assess_data_quality(self, data: Any) -> DataQualityReport:
        """包括的なデータ品質評価"""
        completeness = self._assess_completeness(data)
        consistency = self._assess_consistency(data)
        validity = self._assess_validity(data)
        accuracy = self._assess_accuracy(data)

        # 総合スコア計算（重み付き平均）
        overall_score = (
            completeness * 0.3 + consistency * 0.25 + validity * 0.25 + accuracy * 0.2
        )

        return DataQualityReport(
            completeness_score=completeness,
            consistency_score=consistency,
            validity_score=validity,
            accuracy_score=accuracy,
            overall_score=overall_score,
            detailed_issues=self._collect_detailed_issues(data),
        )

    def _assess_completeness(self, data: Any) -> float:
        """データ完全性の評価"""
        if isinstance(data, list):
            if not data:
                return 0.0

            total_fields = 0
            missing_fields = 0

            for item in data:
                if isinstance(item, dict):
                    for value in item.values():
                        total_fields += 1
                        if value is None or value == "" or value == []:
                            missing_fields += 1
                else:
                    total_fields += 1
                    if item is None or item == "":
                        missing_fields += 1

            if total_fields == 0:
                return 1.0

            return 1.0 - (missing_fields / total_fields)

        return 1.0

    def _assess_consistency(self, data: Any) -> float:
        """データ一貫性の評価"""
        if isinstance(data, list) and data:
            consistency_score = 1.0

            # データ型の一貫性チェック
            if isinstance(data[0], dict):
                # オブジェクト配列の場合
                expected_keys = set(data[0].keys())
                for item in data[1:]:
                    if isinstance(item, dict):
                        if set(item.keys()) != expected_keys:
                            consistency_score -= 0.1
                    else:
                        consistency_score -= 0.2

            # フォーマットの一貫性チェック（簡単な例）
            formats: dict[str, int] = {}
            for item in data:
                if isinstance(item, str):
                    # 日付フォーマットのチェック
                    if re.match(r"\d{4}-\d{2}-\d{2}", item):
                        formats.setdefault("date", 0)
                        formats["date"] += 1
                    # メールフォーマットのチェック
                    elif "@" in item:
                        formats.setdefault("email", 0)
                        formats["email"] += 1

            return max(0.0, consistency_score)

        return 1.0

    def _assess_validity(self, data: Any) -> float:
        """データ妥当性の評価"""
        if isinstance(data, list):
            valid_count = 0
            total_count = 0

            for item in data:
                total_count += 1
                if self._is_valid_item(item):
                    valid_count += 1

            if total_count == 0:
                return 1.0

            return valid_count / total_count

        return 1.0

    def _assess_accuracy(self, data: Any) -> float:
        """データ正確性の評価（基本的な推定）"""
        # 実際の正確性評価は外部データとの比較が必要
        # ここでは基本的なヒューリスティクスを使用
        if isinstance(data, list):
            accuracy_indicators = []

            for item in data:
                if isinstance(item, dict):
                    # 数値の範囲チェック
                    for key, value in item.items():
                        if isinstance(value, int | float):
                            # 年齢などの合理的な範囲チェック
                            if "age" in key.lower() and not (0 <= value <= 150):
                                accuracy_indicators.append(0.0)
                            else:
                                accuracy_indicators.append(1.0)

            if accuracy_indicators:
                return sum(accuracy_indicators) / len(accuracy_indicators)

        return 0.8  # デフォルト推定値

    def _is_valid_item(self, item: Any) -> bool:
        """個別アイテムの妥当性チェック"""
        if item is None:
            return False

        if isinstance(item, str):
            # 空文字列や空白のみは無効
            if not item.strip():
                return False
            # 明らかに無効な値
            if item.lower() in ["null", "undefined", "n/a", "none"]:
                return False

        # NaNや無限大は無効
        return not (
            isinstance(item, int | float) and (np.isnan(item) or np.isinf(item))
        )

    def _collect_detailed_issues(self, data: Any) -> dict[str, list[str]]:
        """詳細な問題点の収集"""
        issues: dict[str, list[str]] = {
            "missing_data": [],
            "format_issues": [],
            "consistency_issues": [],
        }

        if isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, dict):
                    for key, value in item.items():
                        if value is None or value == "":
                            issues["missing_data"].append(
                                f"Row {i}, field '{key}': missing value"
                            )

                        # フォーマット問題の検出
                        if (
                            isinstance(value, str)
                            and "email" in key.lower()
                            and "@" not in value
                        ):
                            issues["format_issues"].append(
                                f"Row {i}, field '{key}': invalid email format"
                            )

        return issues


class AdvancedMetadataGenerator:
    """
    Phase 2: 高度なメタデータ生成機能

    Phase 1のRAGMetadataExtractorを拡張し、以下を追加:
    - 高度統計分析 (分布、相関、外れ値検出)
    - 日本語エンティティ分類 (人名、地名、組織名)
    - データ品質評価 (完全性、一貫性、妥当性)
    - PLaMo-Embedding-1B連携準備
    """

    def __init__(self):
        """高度メタデータ生成器の初期化"""
        self.statistical_analyzer = StatisticalAnalyzer()
        self.categorical_analyzer = CategoricalAnalyzer()
        self.japanese_entity_classifier = JapaneseEntityClassifier()
        self.data_quality_assessor = DataQualityAssessor()

    def generate_advanced_metadata(
        self, json_data: Any, basic_metadata: dict
    ) -> AdvancedMetadata:
        """高度メタデータの生成メイン処理"""

        # 統計分析
        statistical_analysis = self._perform_statistical_analysis(json_data)

        # エンティティ分類
        entity_classification = self._perform_entity_classification(json_data)

        # データ品質評価
        data_quality = self.data_quality_assessor.assess_data_quality(json_data)

        # 検索ファセット生成
        search_facets = self._generate_search_facets(
            statistical_analysis, entity_classification
        )

        # PLaMo特徴量準備
        plamo_features = self._prepare_plamo_features(json_data, entity_classification)

        return AdvancedMetadata(
            basic_metadata=basic_metadata,
            statistical_analysis=statistical_analysis,
            entity_classification=entity_classification,
            data_quality=data_quality,
            search_facets=search_facets,
            plamo_features=plamo_features,
        )

    def _perform_statistical_analysis(self, data: Any) -> dict[str, Any]:
        """統計分析の実行"""
        analysis: dict[str, Any] = {
            "numerical_fields": {},
            "categorical_fields": {},
            "temporal_fields": {},
        }

        if isinstance(data, list) and data and isinstance(data[0], dict):
            # オブジェクト配列の場合
            for key in data[0]:
                field_values = [
                    item.get(key)
                    for item in data
                    if isinstance(item, dict) and key in item
                ]

                # 数値フィールドの分析
                if field_values and isinstance(field_values[0], int | float):
                    numerical_values = [
                        v for v in field_values if isinstance(v, int | float)
                    ]
                    if numerical_values:
                        analysis["numerical_fields"][key] = (
                            self.statistical_analyzer.analyze_numerical_data(
                                numerical_values
                            ).__dict__
                        )

                # カテゴリフィールドの分析
                elif field_values and isinstance(field_values[0], str):
                    string_values = [v for v in field_values if isinstance(v, str)]
                    if string_values:
                        analysis["categorical_fields"][key] = (
                            self.categorical_analyzer.analyze_categorical_data(
                                string_values
                            ).__dict__
                        )

        return analysis

    def _perform_entity_classification(self, data: Any) -> EntityClassification:
        """エンティティ分類の実行"""
        text_data = []

        # テキストデータの抽出
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    for value in item.values():
                        if isinstance(value, str):
                            text_data.append(value)
                elif isinstance(item, str):
                    text_data.append(item)

        return self.japanese_entity_classifier.classify_entities(text_data)

    def _generate_search_facets(
        self, statistical_analysis: dict, entity_classification: EntityClassification
    ) -> SearchFacets:
        """検索ファセットの生成"""
        facets = SearchFacets()

        # カテゴリカルファセット
        for field_name, stats in statistical_analysis.get(
            "categorical_fields", {}
        ).items():
            if stats["unique_count"] <= 20:  # ファセット化に適した値数
                facets.categorical[field_name] = {
                    "type": "terms",
                    "values": stats["value_counts"],
                    "display_name": field_name.replace("_", " ").title(),
                }

        # 数値範囲ファセット
        for field_name, stats in statistical_analysis.get(
            "numerical_fields", {}
        ).items():
            min_val = stats["min_value"]
            max_val = stats["max_value"]
            if max_val > min_val:
                facets.numerical[field_name] = {
                    "type": "range",
                    "min": min_val,
                    "max": max_val,
                    "ranges": self._generate_optimal_ranges(min_val, max_val),
                    "display_name": field_name.replace("_", " ").title(),
                }

        # エンティティファセット
        if entity_classification.persons:
            facets.entities["persons"] = {
                "type": "terms",
                "values": {p.name: 1 for p in entity_classification.persons},
                "display_name": "人名",
            }

        if entity_classification.places:
            facets.entities["places"] = {
                "type": "terms",
                "values": {p.place: 1 for p in entity_classification.places},
                "display_name": "場所",
            }

        return facets

    def _generate_optimal_ranges(self, min_val: float, max_val: float) -> list[dict]:
        """最適な数値範囲の生成"""
        range_count = min(5, max(2, int((max_val - min_val) / 10)))  # 2-5の範囲
        step = (max_val - min_val) / range_count

        ranges = []
        for i in range(range_count):
            start = min_val + (i * step)
            end = min_val + ((i + 1) * step)
            ranges.append(
                {
                    "from": round(start, 2),
                    "to": round(end, 2),
                    "label": f"{round(start, 0)}-{round(end, 0)}",
                }
            )

        return ranges

    def _prepare_plamo_features(
        self, data: Any, entity_classification: EntityClassification
    ) -> PLaMoFeatures:
        """PLaMo-Embedding-1B用特徴量の準備"""
        text_segments = []
        japanese_features = {}

        # テキストセグメントの抽出
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    # オブジェクトを自然な日本語文に変換
                    segments = self._convert_object_to_japanese_text(item)
                    text_segments.extend(segments)

        # 日本語特有の特徴量
        japanese_features = {
            "kanji_density": self._calculate_kanji_density(text_segments),
            "katakana_terms": self._extract_katakana_terms(text_segments),
            "business_context": self._analyze_business_context(entity_classification),
            "entity_richness": self._calculate_entity_richness(entity_classification),
        }

        # 埋め込みヒント
        embedding_hints = {
            "domain": self._detect_domain(text_segments, entity_classification),
            "formality_level": self._assess_formality(text_segments),
            "technical_level": self._assess_technical_level(text_segments),
        }

        # ベクトル最適化設定
        vector_optimization = {
            "chunk_strategy": "semantic_boundary",
            "overlap_ratio": 0.1,
            "max_chunk_length": 512,  # PLaMo-Embedding-1Bに最適
            "prioritize_entities": True,
        }

        return PLaMoFeatures(
            text_segments=text_segments,
            japanese_features=japanese_features,
            embedding_hints=embedding_hints,
            vector_optimization=vector_optimization,
        )

    def _convert_object_to_japanese_text(self, obj: dict) -> list[str]:
        """オブジェクトを自然な日本語文に変換"""
        segments = []

        # キーと値のペアを自然な文に変換
        for key, value in obj.items():
            if isinstance(value, str) and value.strip():
                if key.lower() in ["name", "名前"]:
                    segments.append(f"名前は{value}です。")
                elif key.lower() in ["age", "年齢"]:
                    segments.append(f"年齢は{value}歳です。")
                elif key.lower() in ["department", "部署"]:
                    segments.append(f"所属部署は{value}です。")
                else:
                    segments.append(f"{key}は{value}です。")

        return segments

    def _calculate_kanji_density(self, text_segments: list[str]) -> float:
        """漢字密度の計算"""
        if not text_segments:
            return 0.0

        total_chars = 0
        kanji_chars = 0

        for segment in text_segments:
            total_chars += len(segment)
            kanji_chars += len(re.findall(r"[一-龯]", segment))

        return kanji_chars / total_chars if total_chars > 0 else 0.0

    def _extract_katakana_terms(self, text_segments: list[str]) -> list[str]:
        """カタカナ用語の抽出"""
        katakana_terms = set()

        for segment in text_segments:
            matches = re.findall(r"[ア-ン]{3,}", segment)
            katakana_terms.update(matches)

        return list(katakana_terms)

    def _analyze_business_context(
        self, entity_classification: EntityClassification
    ) -> dict:
        """ビジネスコンテキストの分析"""
        context = {
            "has_company_entities": len(entity_classification.organizations) > 0,
            "has_job_titles": any(
                "job_title" in term.category
                for term in entity_classification.business_terms
            ),
            "formality_indicators": [],
        }

        # 敬語・丁寧語の検出
        formal_patterns = ["です", "ます", "であります", "いたします"]
        context["formality_indicators"] = formal_patterns  # 簡略化

        return context

    def _calculate_entity_richness(
        self, entity_classification: EntityClassification
    ) -> float:
        """エンティティの豊富さを計算"""
        total_entities = (
            len(entity_classification.persons)
            + len(entity_classification.places)
            + len(entity_classification.organizations)
            + len(entity_classification.business_terms)
        )

        # エンティティタイプの多様性を考慮
        entity_types = 0
        if entity_classification.persons:
            entity_types += 1
        if entity_classification.places:
            entity_types += 1
        if entity_classification.organizations:
            entity_types += 1
        if entity_classification.business_terms:
            entity_types += 1

        return (total_entities * entity_types) / 100.0  # 正規化

    def _detect_domain(
        self, _text_segments: list[str], entity_classification: EntityClassification
    ) -> str:
        """ドメインの検出"""
        # ビジネス関連エンティティが多い場合
        if entity_classification.business_terms or entity_classification.organizations:
            return "business"

        # 地名が多い場合
        if len(entity_classification.places) > len(entity_classification.persons):
            return "geography"

        # 人名が多い場合
        if entity_classification.persons:
            return "social"

        return "general"

    def _assess_formality(self, text_segments: list[str]) -> str:
        """文体の丁寧さレベル評価"""
        formal_count = 0
        total_segments = len(text_segments)

        if total_segments == 0:
            return "neutral"

        for segment in text_segments:
            if any(pattern in segment for pattern in ["です", "ます", "であります"]):
                formal_count += 1

        formal_ratio = formal_count / total_segments

        if formal_ratio > 0.7:
            return "formal"
        elif formal_ratio > 0.3:
            return "polite"
        else:
            return "casual"

    def _assess_technical_level(self, text_segments: list[str]) -> str:
        """技術レベルの評価"""
        technical_terms = [
            "システム",
            "データ",
            "プログラム",
            "API",
            "データベース",
            "サーバー",
            "ネットワーク",
        ]

        technical_count = 0
        total_segments = len(text_segments)

        if total_segments == 0:
            return "non_technical"

        for segment in text_segments:
            if any(term in segment for term in technical_terms):
                technical_count += 1

        technical_ratio = technical_count / total_segments

        if technical_ratio > 0.5:
            return "highly_technical"
        elif technical_ratio > 0.2:
            return "moderately_technical"
        else:
            return "non_technical"
