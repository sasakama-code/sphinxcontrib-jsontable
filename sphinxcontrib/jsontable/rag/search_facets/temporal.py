"""Temporal facet generation for date/time filtering.

Specialized module for generating temporal facets with date range detection,
Japanese date format support, and temporal pattern analysis.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .base import FacetConfig, generate_display_name


@dataclass
class TemporalFacet:
    """Temporal facet definition for date/time filtering.

    Args:
        field_name: Source field name from data.
        display_name: Human-readable display name.
        facet_type: Type of facet (date_range, date_histogram, etc.).
        earliest_date: Earliest date in the dataset.
        latest_date: Latest date in the dataset.
        date_ranges: List of predefined date ranges.
        temporal_patterns: Detected temporal patterns.
        ui_config: UI-specific configuration parameters.
    """

    field_name: str
    display_name: str
    facet_type: str = "date_range"
    earliest_date: str = ""
    latest_date: str = ""
    date_ranges: list[dict[str, Any]] = field(default_factory=list)
    temporal_patterns: dict[str, Any] = field(default_factory=dict)
    ui_config: dict[str, Any] = field(default_factory=dict)


class TemporalFacetGenerator:
    """Generator for temporal search facets.

    Handles creation of temporal facets with Japanese date parsing,
    intelligent date range generation, and temporal pattern detection.
    """

    def __init__(self, config: FacetConfig):
        """Initialize temporal facet generator.

        Args:
            config: Configuration for facet generation parameters.
        """
        self.config = config

    def generate_temporal_facets(
        self, statistical_analysis: dict
    ) -> list[TemporalFacet]:
        """Generate temporal facets from statistical analysis data.

        Args:
            statistical_analysis: Statistical analysis data to search for temporal patterns.

        Returns:
            List of temporal facets with date ranges and patterns.
        """
        temporal_facets = []

        # 時系列フィールドの検出
        temporal_fields = self._detect_temporal_fields(statistical_analysis)

        for field_name, temporal_info in temporal_fields.items():
            # 日付範囲生成
            date_ranges = self._generate_date_ranges(temporal_info)

            # 時系列パターン分析
            temporal_patterns = self._analyze_temporal_patterns(temporal_info)

            # 日本語表示名生成
            display_name = generate_display_name(
                field_name, self.config.japanese_display_names
            )

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

    def _detect_temporal_fields(self, statistical_analysis: dict) -> dict:
        """Detect temporal fields from statistical analysis data.

        Args:
            statistical_analysis: Statistical analysis containing field information.

        Returns:
            Dictionary mapping field names to temporal information.
        """
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
        """Determine if field contains temporal data.

        Args:
            field_name: Name of the field to check.
            stats: Statistical information for the field.

        Returns:
            True if field contains temporal/date data.
        """
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
        """Extract temporal information from field statistics.

        Args:
            stats: Statistical data for a temporal field.

        Returns:
            Dictionary with temporal info (earliest, latest, span) or None if invalid.
        """
        value_counts = stats.get("value_counts", {})
        if not value_counts:
            return None

        # 日付値の解析
        dates = []
        for value in value_counts:
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
        """Parse date string in various formats including Japanese.

        Args:
            date_string: Date string to parse.

        Returns:
            Parsed datetime object or None if parsing fails.
        """
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
        """Generate appropriate date ranges based on temporal span.

        Args:
            temporal_info: Temporal information with date span and patterns.

        Returns:
            List of date range dictionaries with from/to/label/type.
        """
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

    def _generate_daily_ranges(
        self, start_date: datetime, end_date: datetime
    ) -> list[dict]:
        """Generate daily date ranges for short time periods.

        Args:
            start_date: Starting date for range generation.
            end_date: Ending date for range generation.

        Returns:
            List of daily range dictionaries.
        """
        ranges = []
        current = start_date

        while current <= end_date:
            ranges.append(
                {
                    "from": current.isoformat(),
                    "to": current.isoformat(),
                    "label": current.strftime("%Y年%m月%d日"),
                    "type": "daily",
                }
            )
            current = current.replace(day=current.day + 1)

        return ranges

    def _generate_weekly_ranges(
        self, start_date: datetime, end_date: datetime
    ) -> list[dict]:
        """Generate weekly date ranges for medium time periods.

        Args:
            start_date: Starting date for range generation.
            end_date: Ending date for range generation.

        Returns:
            List of weekly range dictionaries.
        """
        ranges = []
        current = start_date

        week_num = 1
        while current <= end_date:
            week_end = min(current.replace(day=current.day + 6), end_date)
            ranges.append(
                {
                    "from": current.isoformat(),
                    "to": week_end.isoformat(),
                    "label": f"第{week_num}週 ({current.strftime('%m/%d')} - {week_end.strftime('%m/%d')})",
                    "type": "weekly",
                }
            )
            current = week_end.replace(day=week_end.day + 1)
            week_num += 1

        return ranges

    def _generate_monthly_ranges(
        self, start_date: datetime, end_date: datetime
    ) -> list[dict]:
        """Generate monthly date ranges for longer time periods.

        Args:
            start_date: Starting date for range generation.
            end_date: Ending date for range generation.

        Returns:
            List of monthly range dictionaries.
        """
        import calendar

        ranges = []
        current = start_date

        while current <= end_date:
            # 月末を取得
            last_day_of_month = calendar.monthrange(current.year, current.month)[1]
            month_end = current.replace(day=last_day_of_month)
            month_end = min(month_end, end_date)

            ranges.append(
                {
                    "from": current.isoformat(),
                    "to": month_end.isoformat(),
                    "label": f"{current.year}年{current.month}月",
                    "type": "monthly",
                }
            )

            # 次の月の1日に移動
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1, day=1)
            else:
                current = current.replace(month=current.month + 1, day=1)

        return ranges

    def _generate_yearly_ranges(
        self, start_date: datetime, end_date: datetime
    ) -> list[dict]:
        """Generate yearly date ranges for very long time periods.

        Args:
            start_date: Starting date for range generation.
            end_date: Ending date for range generation.

        Returns:
            List of yearly range dictionaries.
        """
        ranges = []
        current_year = start_date.year

        while current_year <= end_date.year:
            year_start = datetime(current_year, 1, 1)
            year_end = datetime(current_year, 12, 31)

            # 実際のデータ範囲に調整
            year_start = max(year_start, start_date)
            year_end = min(year_end, end_date)

            ranges.append(
                {
                    "from": year_start.isoformat(),
                    "to": year_end.isoformat(),
                    "label": f"{current_year}年",
                    "type": "yearly",
                }
            )

            current_year += 1

        return ranges

    def _analyze_temporal_patterns(self, temporal_info: dict) -> dict:
        """Analyze temporal patterns and frequency in the data.

        Args:
            temporal_info: Temporal information with date span and count.

        Returns:
            Dictionary with detected patterns (frequency, duration_type).
        """
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

    def _generate_temporal_ui_config(
        self, field_name: str, temporal_info: dict
    ) -> dict:
        """Generate UI configuration for temporal facets.

        Args:
            field_name: Name of the field this facet represents.
            temporal_info: Temporal information including date span.

        Returns:
            Dictionary with UI-specific configuration parameters.
        """
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
