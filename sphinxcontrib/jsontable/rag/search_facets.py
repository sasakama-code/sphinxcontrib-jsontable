"""
Search Facet Generator for Phase 2 RAG Integration

検索ファセット自動生成機能：
- カテゴリカルファセット自動生成
- 数値範囲ファセット最適化
- 時系列ファセット対応
- 日本語エンティティファセット
- UI連携用メタデータ生成
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .advanced_metadata import AdvancedMetadata, EntityClassification


@dataclass
class FacetConfig:
    """ファセット設定"""

    max_categorical_values: int = 20
    max_numerical_ranges: int = 5
    min_frequency_threshold: int = 2
    enable_entity_facets: bool = True
    japanese_display_names: bool = True
    confidence_threshold: float = 0.6


@dataclass
class CategoricalFacet:
    """カテゴリカルファセット"""

    field_name: str
    display_name: str
    facet_type: str = "terms"
    values: dict[str, int] = field(default_factory=dict)
    total_count: int = 0
    missing_count: int = 0
    ui_config: dict[str, Any] = field(default_factory=dict)


@dataclass
class NumericalFacet:
    """数値ファセット"""

    field_name: str
    display_name: str
    facet_type: str = "range"
    min_value: float = 0.0
    max_value: float = 0.0
    ranges: list[dict[str, Any]] = field(default_factory=list)
    distribution_info: dict[str, Any] = field(default_factory=dict)
    ui_config: dict[str, Any] = field(default_factory=dict)


@dataclass
class TemporalFacet:
    """時系列ファセット"""

    field_name: str
    display_name: str
    facet_type: str = "date_range"
    earliest_date: str = ""
    latest_date: str = ""
    date_ranges: list[dict[str, Any]] = field(default_factory=list)
    temporal_patterns: dict[str, Any] = field(default_factory=dict)
    ui_config: dict[str, Any] = field(default_factory=dict)


@dataclass
class EntityFacet:
    """エンティティファセット"""

    entity_type: str
    display_name: str
    facet_type: str = "entity_terms"
    entities: dict[str, dict[str, Any]] = field(default_factory=dict)
    confidence_threshold: float = 0.6
    ui_config: dict[str, Any] = field(default_factory=dict)


@dataclass
class GeneratedFacets:
    """生成されたファセット群"""

    categorical_facets: list[CategoricalFacet] = field(default_factory=list)
    numerical_facets: list[NumericalFacet] = field(default_factory=list)
    temporal_facets: list[TemporalFacet] = field(default_factory=list)
    entity_facets: list[EntityFacet] = field(default_factory=list)
    generation_metadata: dict[str, Any] = field(default_factory=dict)


class SearchFacetGenerator:
    """検索ファセットの自動生成器"""

    def __init__(self, config: FacetConfig | None = None):
        """ファセット生成器の初期化"""
        self.config = config or FacetConfig()
        self.japanese_field_names = {
            "name": "名前",
            "age": "年齢",
            "department": "部署",
            "position": "役職",
            "salary": "給与",
            "email": "メールアドレス",
            "phone": "電話番号",
            "address": "住所",
            "company": "会社",
            "project": "プロジェクト",
            "skill": "スキル",
            "experience": "経験年数",
            "date": "日付",
            "created_at": "作成日",
            "updated_at": "更新日",
            "price": "価格",
            "category": "カテゴリ",
            "status": "ステータス",
            "type": "種別",
        }

    def generate_facets(self, advanced_metadata: AdvancedMetadata) -> GeneratedFacets:
        """高度メタデータから検索ファセットを自動生成"""
        facets = GeneratedFacets()

        # カテゴリカルファセット生成
        facets.categorical_facets = self._generate_categorical_facets(
            advanced_metadata.statistical_analysis
        )

        # 数値ファセット生成
        facets.numerical_facets = self._generate_numerical_facets(
            advanced_metadata.statistical_analysis
        )

        # 時系列ファセット生成
        facets.temporal_facets = self._generate_temporal_facets(
            advanced_metadata.statistical_analysis
        )

        # エンティティファセット生成
        if self.config.enable_entity_facets:
            facets.entity_facets = self._generate_entity_facets(
                advanced_metadata.entity_classification
            )

        # 生成メタデータ
        facets.generation_metadata = self._create_generation_metadata(facets)

        return facets

    def _generate_categorical_facets(self, statistical_analysis: dict) -> list[CategoricalFacet]:
        """カテゴリカルファセットの生成"""
        categorical_facets = []

        categorical_fields = statistical_analysis.get("categorical_fields", {})

        for field_name, stats in categorical_fields.items():
            # ファセット化適正チェック
            if not self._is_suitable_for_categorical_facet(stats):
                continue

            # 頻度フィルタリング
            filtered_values = self._filter_by_frequency(
                stats["value_counts"], self.config.min_frequency_threshold
            )

            if not filtered_values:
                continue

            # 日本語表示名生成
            display_name = self._generate_display_name(field_name)

            # UIコンフィグ生成
            ui_config = self._generate_categorical_ui_config(field_name, stats)

            facet = CategoricalFacet(
                field_name=field_name,
                display_name=display_name,
                values=filtered_values,
                total_count=sum(filtered_values.values()),
                missing_count=stats.get("missing_count", 0),
                ui_config=ui_config,
            )

            categorical_facets.append(facet)

        return categorical_facets

    def _generate_numerical_facets(self, statistical_analysis: dict) -> list[NumericalFacet]:
        """数値ファセットの生成"""
        numerical_facets = []

        numerical_fields = statistical_analysis.get("numerical_fields", {})

        for field_name, stats in numerical_fields.items():
            # 数値ファセット適正チェック
            if not self._is_suitable_for_numerical_facet(stats):
                continue

            # 最適な範囲生成
            ranges = self._generate_optimal_numerical_ranges(stats)

            # 日本語表示名生成
            display_name = self._generate_display_name(field_name)

            # UIコンフィグ生成
            ui_config = self._generate_numerical_ui_config(field_name, stats)

            # 分布情報
            distribution_info = {
                "distribution_type": stats.get("distribution_type", "unknown"),
                "skewness": stats.get("skewness", 0.0),
                "has_outliers": len(stats.get("outliers", [])) > 0,
                "quartiles": stats.get("quartiles", [0, 0, 0]),
            }

            facet = NumericalFacet(
                field_name=field_name,
                display_name=display_name,
                min_value=stats["min_value"],
                max_value=stats["max_value"],
                ranges=ranges,
                distribution_info=distribution_info,
                ui_config=ui_config,
            )

            numerical_facets.append(facet)

        return numerical_facets

    def _generate_temporal_facets(self, statistical_analysis: dict) -> list[TemporalFacet]:
        """時系列ファセットの生成"""
        temporal_facets = []

        # 時系列フィールドの検出
        temporal_fields = self._detect_temporal_fields(statistical_analysis)

        for field_name, temporal_info in temporal_fields.items():
            # 日付範囲生成
            date_ranges = self._generate_date_ranges(temporal_info)

            # 時系列パターン分析
            temporal_patterns = self._analyze_temporal_patterns(temporal_info)

            # 日本語表示名生成
            display_name = self._generate_display_name(field_name)

            # UIコンフィグ生成
            ui_config = self._generate_temporal_ui_config(field_name, temporal_info)

            facet = TemporalFacet(
                field_name=field_name,
                display_name=display_name,
                earliest_date=temporal_info.get("earliest", ""),
                latest_date=temporal_info.get("latest", ""),
                date_ranges=date_ranges,
                temporal_patterns=temporal_patterns,
                ui_config=ui_config,
            )

            temporal_facets.append(facet)

        return temporal_facets

    def _generate_entity_facets(self, entity_classification: EntityClassification) -> list[EntityFacet]:
        """エンティティファセットの生成"""
        entity_facets = []

        # 人名ファセット
        if entity_classification.persons:
            person_facet = self._create_person_facet(entity_classification.persons)
            if person_facet:
                entity_facets.append(person_facet)

        # 場所ファセット
        if entity_classification.places:
            place_facet = self._create_place_facet(entity_classification.places)
            if place_facet:
                entity_facets.append(place_facet)

        # 組織ファセット
        if entity_classification.organizations:
            org_facet = self._create_organization_facet(entity_classification.organizations)
            if org_facet:
                entity_facets.append(org_facet)

        # ビジネス用語ファセット
        if entity_classification.business_terms:
            business_facet = self._create_business_facet(entity_classification.business_terms)
            if business_facet:
                entity_facets.append(business_facet)

        return entity_facets

    def _is_suitable_for_categorical_facet(self, stats: dict) -> bool:
        """カテゴリカルファセット適正判定"""
        unique_count = stats.get("unique_count", 0)
        total_values = sum(stats.get("value_counts", {}).values())

        # 適正条件
        return (
            1 < unique_count <= self.config.max_categorical_values
            and total_values >= 3  # 最小データ数（5→3に緩和）
            and (unique_count / total_values) <= 0.9  # 多様性が高すぎない（0.8→0.9に緩和）
        )

    def _is_suitable_for_numerical_facet(self, stats: dict) -> bool:
        """数値ファセット適正判定"""
        min_val = stats.get("min_value", 0)
        max_val = stats.get("max_value", 0)

        # 適正条件
        return (
            max_val > min_val  # 値の範囲がある
            and (max_val - min_val) > 1  # 意味のある範囲
            and not (min_val == 0 and max_val == 1)  # バイナリでない
        )

    def _filter_by_frequency(self, value_counts: dict, threshold: int) -> dict:
        """頻度による値のフィルタリング"""
        return {
            value: count for value, count in value_counts.items() if count >= threshold
        }

    def _generate_display_name(self, field_name: str) -> str:
        """日本語表示名の生成"""
        if self.config.japanese_display_names:
            # 日本語名マッピング
            japanese_name = self.japanese_field_names.get(field_name.lower())
            if japanese_name:
                return japanese_name

            # アンダースコアをスペースに変換し、タイトルケース化
            display_name = field_name.replace("_", " ").title()

            # 一般的な英語フィールド名を日本語に変換
            translations = {
                "Id": "ID",
                "Url": "URL",
                "Api": "API",
                "Json": "JSON",
                "Xml": "XML",
                "Html": "HTML",
                "Css": "CSS",
                "Sql": "SQL",
            }

            for eng, jp in translations.items():
                display_name = display_name.replace(eng, jp)

            return display_name
        else:
            return field_name.replace("_", " ").title()

    def _generate_optimal_numerical_ranges(self, stats: dict) -> list[dict]:
        """最適な数値範囲の生成"""
        min_val = stats["min_value"]
        max_val = stats["max_value"]
        quartiles = stats.get("quartiles", [min_val, (min_val + max_val) / 2, max_val])

        # 四分位数ベースの範囲生成（より自然な分布）
        ranges = []

        # Q1未満
        if quartiles[0] > min_val:
            ranges.append({
                "from": min_val,
                "to": quartiles[0],
                "label": f"{self._format_number(min_val)} 以下",
                "type": "below_q1",
            })

        # Q1-Q2
        ranges.append({
            "from": quartiles[0],
            "to": quartiles[1],
            "label": f"{self._format_number(quartiles[0])} - {self._format_number(quartiles[1])}",
            "type": "q1_q2",
        })

        # Q2-Q3
        ranges.append({
            "from": quartiles[1],
            "to": quartiles[2],
            "label": f"{self._format_number(quartiles[1])} - {self._format_number(quartiles[2])}",
            "type": "q2_q3",
        })

        # Q3超過
        if quartiles[2] < max_val:
            ranges.append({
                "from": quartiles[2],
                "to": max_val,
                "label": f"{self._format_number(quartiles[2])} 以上",
                "type": "above_q3",
            })

        # 外れ値が多い場合の特別範囲
        outliers = stats.get("outliers", [])
        if len(outliers) > len(stats.get("data", [])) * 0.1:  # 10%以上が外れ値
            outlier_min = min(outliers) if outliers else min_val
            outlier_max = max(outliers) if outliers else max_val
            ranges.append({
                "from": outlier_min,
                "to": outlier_max,
                "label": "外れ値範囲",
                "type": "outliers",
            })

        return ranges

    def _format_number(self, number: float) -> str:
        """数値の日本語向けフォーマット"""
        if number >= 10000:
            return f"{number/10000:.1f}万"
        elif number >= 1000:
            return f"{number/1000:.1f}千"
        elif number == int(number):
            return str(int(number))
        else:
            return f"{number:.1f}"

    def _detect_temporal_fields(self, statistical_analysis: dict) -> dict:
        """時系列フィールドの検出"""
        temporal_fields = {}

        # カテゴリカルフィールドから日付形式を検出
        categorical_fields = statistical_analysis.get("categorical_fields", {})

        for field_name, stats in categorical_fields.items():
            if self._is_temporal_field(field_name, stats):
                temporal_info = self._extract_temporal_info(stats)
                if temporal_info:
                    temporal_fields[field_name] = temporal_info

        return temporal_fields

    def _is_temporal_field(self, field_name: str, stats: dict) -> bool:
        """時系列フィールド判定"""
        # フィールド名による判定
        temporal_keywords = [
            "date",
            "time",
            "created",
            "updated",
            "modified",
            "日付",
            "時刻",
            "作成",
            "更新",
        ]

        if any(keyword in field_name.lower() for keyword in temporal_keywords):
            return True

        # 値のパターンによる判定
        value_counts = stats.get("value_counts", {})
        if not value_counts:
            return False

        # 日付パターンの検出
        date_patterns = [
            r"\d{4}-\d{2}-\d{2}",  # YYYY-MM-DD
            r"\d{4}/\d{2}/\d{2}",  # YYYY/MM/DD
            r"\d{2}/\d{2}/\d{4}",  # MM/DD/YYYY
            r"\d{4}年\d{1,2}月\d{1,2}日",  # 日本語日付
        ]

        sample_values = list(value_counts.keys())[:10]
        for value in sample_values:
            if any(re.match(pattern, str(value)) for pattern in date_patterns):
                return True

        return False

    def _extract_temporal_info(self, stats: dict) -> dict | None:
        """時系列情報の抽出"""
        value_counts = stats.get("value_counts", {})
        if not value_counts:
            return None

        # 日付値の解析
        dates = []
        for value in value_counts.keys():
            parsed_date = self._parse_date(str(value))
            if parsed_date:
                dates.append(parsed_date)

        if not dates:
            return None

        dates.sort()

        return {
            "earliest": dates[0].isoformat(),
            "latest": dates[-1].isoformat(),
            "date_count": len(dates),
            "span_days": (dates[-1] - dates[0]).days,
        }

    def _parse_date(self, date_string: str) -> datetime | None:
        """日付文字列の解析"""
        date_formats = [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%Y-%m-%d %H:%M:%S",
            "%Y/%m/%d %H:%M:%S",
        ]

        for fmt in date_formats:
            try:
                return datetime.strptime(date_string, fmt)
            except ValueError:
                continue

        # 日本語日付の解析
        japanese_pattern = r"(\d{4})年(\d{1,2})月(\d{1,2})日"
        match = re.match(japanese_pattern, date_string)
        if match:
            year, month, day = map(int, match.groups())
            try:
                return datetime(year, month, day)
            except ValueError:
                pass

        return None

    def _generate_date_ranges(self, temporal_info: dict) -> list[dict]:
        """日付範囲の生成"""
        if temporal_info["span_days"] <= 0:
            return []

        ranges = []
        start_date = datetime.fromisoformat(temporal_info["earliest"])
        end_date = datetime.fromisoformat(temporal_info["latest"])

        span_days = temporal_info["span_days"]

        # 期間に応じた適切な範囲生成
        if span_days <= 7:  # 1週間以内
            ranges = self._generate_daily_ranges(start_date, end_date)
        elif span_days <= 31:  # 1ヶ月以内
            ranges = self._generate_weekly_ranges(start_date, end_date)
        elif span_days <= 365:  # 1年以内
            ranges = self._generate_monthly_ranges(start_date, end_date)
        else:  # 1年超
            ranges = self._generate_yearly_ranges(start_date, end_date)

        return ranges

    def _generate_daily_ranges(self, start_date: datetime, end_date: datetime) -> list[dict]:
        """日別範囲生成"""
        ranges = []
        current = start_date

        while current <= end_date:
            ranges.append({
                "from": current.isoformat(),
                "to": current.isoformat(),
                "label": current.strftime("%Y年%m月%d日"),
                "type": "daily",
            })
            current = current.replace(day=current.day + 1)

        return ranges

    def _generate_weekly_ranges(self, start_date: datetime, end_date: datetime) -> list[dict]:
        """週別範囲生成"""
        ranges = []
        current = start_date

        week_num = 1
        while current <= end_date:
            week_end = min(current.replace(day=current.day + 6), end_date)
            ranges.append({
                "from": current.isoformat(),
                "to": week_end.isoformat(),
                "label": f"第{week_num}週 ({current.strftime('%m/%d')} - {week_end.strftime('%m/%d')})",
                "type": "weekly",
            })
            current = week_end.replace(day=week_end.day + 1)
            week_num += 1

        return ranges

    def _generate_monthly_ranges(self, start_date: datetime, end_date: datetime) -> list[dict]:
        """月別範囲生成"""
        import calendar
        ranges = []
        current = start_date

        while current <= end_date:
            # 月末を取得
            last_day_of_month = calendar.monthrange(current.year, current.month)[1]
            month_end = current.replace(day=last_day_of_month)
            month_end = min(month_end, end_date)

            ranges.append({
                "from": current.isoformat(),
                "to": month_end.isoformat(),
                "label": f"{current.year}年{current.month}月",
                "type": "monthly",
            })

            # 次の月の1日に移動
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1, day=1)
            else:
                current = current.replace(month=current.month + 1, day=1)

        return ranges

    def _generate_yearly_ranges(self, start_date: datetime, end_date: datetime) -> list[dict]:
        """年別範囲生成"""
        ranges = []
        current_year = start_date.year

        while current_year <= end_date.year:
            year_start = datetime(current_year, 1, 1)
            year_end = datetime(current_year, 12, 31)

            # 実際のデータ範囲に調整
            year_start = max(year_start, start_date)
            year_end = min(year_end, end_date)

            ranges.append({
                "from": year_start.isoformat(),
                "to": year_end.isoformat(),
                "label": f"{current_year}年",
                "type": "yearly",
            })

            current_year += 1

        return ranges

    def _analyze_temporal_patterns(self, temporal_info: dict) -> dict:
        """時系列パターンの分析"""
        patterns = {}

        span_days = temporal_info["span_days"]
        date_count = temporal_info["date_count"]

        # 頻度パターン
        if date_count > 0:
            avg_interval = span_days / date_count
            if avg_interval <= 1.5:
                patterns["frequency"] = "daily"
            elif avg_interval <= 7.5:
                patterns["frequency"] = "weekly"
            elif avg_interval <= 32:
                patterns["frequency"] = "monthly"
            else:
                patterns["frequency"] = "irregular"

        # 期間分類
        if span_days <= 7:
            patterns["duration_type"] = "short_term"
        elif span_days <= 90:
            patterns["duration_type"] = "medium_term"
        else:
            patterns["duration_type"] = "long_term"

        return patterns

    def _create_person_facet(self, persons) -> EntityFacet | None:
        """人名ファセットの作成"""
        if not persons:
            return None

        # 信頼度フィルタリング
        high_confidence_persons = [
            p for p in persons if p.confidence >= self.config.confidence_threshold
        ]

        if not high_confidence_persons:
            return None

        # エンティティ情報構築
        entities = {}
        for person in high_confidence_persons:
            entities[person.name] = {
                "confidence": person.confidence,
                "name_type": person.name_type,
                "count": 1,  # 実際のデータではカウントを正確に計算
            }

        ui_config = {
            "icon": "👤",
            "color": "#3498db",
            "sortBy": "confidence",
            "displayFormat": "name_with_confidence",
        }

        return EntityFacet(
            entity_type="persons",
            display_name="人名",
            entities=entities,
            confidence_threshold=self.config.confidence_threshold,
            ui_config=ui_config,
        )

    def _create_place_facet(self, places) -> EntityFacet | None:
        """場所ファセットの作成"""
        if not places:
            return None

        high_confidence_places = [
            p for p in places if p.confidence >= self.config.confidence_threshold
        ]

        if not high_confidence_places:
            return None

        entities = {}
        for place in high_confidence_places:
            entities[place.place] = {
                "confidence": place.confidence,
                "place_type": place.place_type,
                "count": 1,
            }

        ui_config = {
            "icon": "📍",
            "color": "#e74c3c",
            "sortBy": "place_type",
            "displayFormat": "place_with_type",
            "groupBy": "place_type",
        }

        return EntityFacet(
            entity_type="places",
            display_name="場所",
            entities=entities,
            confidence_threshold=self.config.confidence_threshold,
            ui_config=ui_config,
        )

    def _create_organization_facet(self, organizations) -> EntityFacet | None:
        """組織ファセットの作成"""
        if not organizations:
            return None

        high_confidence_orgs = [
            o for o in organizations if o.confidence >= self.config.confidence_threshold
        ]

        if not high_confidence_orgs:
            return None

        entities = {}
        for org in high_confidence_orgs:
            entities[org.organization] = {
                "confidence": org.confidence,
                "org_type": org.org_type,
                "count": 1,
            }

        ui_config = {
            "icon": "🏢",
            "color": "#9b59b6",
            "sortBy": "org_type",
            "displayFormat": "org_with_type",
            "groupBy": "org_type",
        }

        return EntityFacet(
            entity_type="organizations",
            display_name="組織",
            entities=entities,
            confidence_threshold=self.config.confidence_threshold,
            ui_config=ui_config,
        )

    def _create_business_facet(self, business_terms) -> EntityFacet | None:
        """ビジネス用語ファセットの作成"""
        if not business_terms:
            return None

        high_confidence_terms = [
            b for b in business_terms if b.confidence >= self.config.confidence_threshold
        ]

        if not high_confidence_terms:
            return None

        entities = {}
        for term in high_confidence_terms:
            entities[term.term] = {
                "confidence": term.confidence,
                "category": term.category,
                "count": 1,
            }

        ui_config = {
            "icon": "💼",
            "color": "#f39c12",
            "sortBy": "category",
            "displayFormat": "term_with_category",
            "groupBy": "category",
        }

        return EntityFacet(
            entity_type="business_terms",
            display_name="ビジネス用語",
            entities=entities,
            confidence_threshold=self.config.confidence_threshold,
            ui_config=ui_config,
        )

    def _generate_categorical_ui_config(self, field_name: str, stats: dict) -> dict:
        """カテゴリカルファセット用UIコンフィグ生成"""
        unique_count = stats.get("unique_count", 0)

        ui_config = {
            "widget_type": "checkbox_list" if unique_count <= 10 else "searchable_dropdown",
            "max_visible_items": min(unique_count, 8),
            "enable_search": unique_count > 5,
            "enable_select_all": unique_count > 3,
            "sort_options": ["count_desc", "name_asc", "name_desc"],
            "default_sort": "count_desc",
        }

        # フィールド特有の設定
        if "status" in field_name.lower():
            ui_config["color_coding"] = True
            ui_config["status_colors"] = {
                "active": "#2ecc71",
                "inactive": "#95a5a6",
                "pending": "#f39c12",
                "error": "#e74c3c",
            }

        return ui_config

    def _generate_numerical_ui_config(self, field_name: str, stats: dict) -> dict:
        """数値ファセット用UIコンフィグ生成"""
        ui_config = {
            "widget_type": "range_slider",
            "enable_histogram": True,
            "step_size": self._calculate_step_size(stats),
            "number_format": self._detect_number_format(field_name),
            "enable_text_input": True,
        }

        # フィールド特有の設定
        if any(keyword in field_name.lower() for keyword in ["price", "salary", "cost", "金額", "給与"]):
            ui_config["number_format"] = "currency"
            ui_config["currency_symbol"] = "¥"

        elif any(keyword in field_name.lower() for keyword in ["age", "年齢"]):
            ui_config["number_format"] = "integer"
            ui_config["suffix"] = "歳"

        elif any(keyword in field_name.lower() for keyword in ["percent", "rate", "割合"]):
            ui_config["number_format"] = "percentage"
            ui_config["suffix"] = "%"

        return ui_config

    def _generate_temporal_ui_config(self, field_name: str, temporal_info: dict) -> dict:
        """時系列ファセット用UIコンフィグ生成"""
        span_days = temporal_info.get("span_days", 0)

        ui_config = {
            "widget_type": "date_range_picker",
            "enable_presets": True,
            "date_format": "YYYY年MM月DD日",
            "enable_calendar": True,
        }

        # 期間に応じたプリセット設定
        if span_days <= 31:
            ui_config["presets"] = ["今日", "昨日", "今週", "先週", "今月"]
        elif span_days <= 365:
            ui_config["presets"] = ["今月", "先月", "今四半期", "前四半期", "今年"]
        else:
            ui_config["presets"] = ["今年", "昨年", "過去2年", "過去5年", "全期間"]

        return ui_config

    def _calculate_step_size(self, stats: dict) -> float:
        """数値ファセットのステップサイズ計算"""
        min_val = stats["min_value"]
        max_val = stats["max_value"]
        range_val = max_val - min_val

        if range_val <= 1:
            return 0.01
        elif range_val <= 10:
            return 0.1
        elif range_val <= 100:
            return 1
        elif range_val <= 1000:
            return 10
        else:
            return 100

    def _detect_number_format(self, field_name: str) -> str:
        """数値フォーマットの検出"""
        if any(keyword in field_name.lower() for keyword in ["price", "salary", "cost", "金額"]):
            return "currency"
        elif any(keyword in field_name.lower() for keyword in ["percent", "rate", "割合"]):
            return "percentage"
        elif any(keyword in field_name.lower() for keyword in ["age", "count", "number", "年齢"]):
            return "integer"
        else:
            return "decimal"

    def _create_generation_metadata(self, facets: GeneratedFacets) -> dict:
        """ファセット生成メタデータの作成"""
        return {
            "generation_timestamp": datetime.now().isoformat(),
            "facet_counts": {
                "categorical": len(facets.categorical_facets),
                "numerical": len(facets.numerical_facets),
                "temporal": len(facets.temporal_facets),
                "entity": len(facets.entity_facets),
            },
            "total_facets": (
                len(facets.categorical_facets)
                + len(facets.numerical_facets)
                + len(facets.temporal_facets)
                + len(facets.entity_facets)
            ),
            "configuration": {
                "max_categorical_values": self.config.max_categorical_values,
                "confidence_threshold": self.config.confidence_threshold,
                "japanese_display_names": self.config.japanese_display_names,
            },
        }