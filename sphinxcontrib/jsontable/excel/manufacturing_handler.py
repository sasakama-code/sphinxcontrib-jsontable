"""Manufacturing industry-specific Excel format handler.

This module provides specialized handler for manufacturing industry Excel formats
commonly used in Japanese business environments. The handler implements domain-specific
data extraction and transformation patterns for manufacturing production management.

Key Features:
- Manufacturing production management Excel formats
- Quality control and equipment management data processing
- Process control and inventory management analysis
- Industry-specific terminology and entity recognition
- Japanese business document structure understanding
- Automated metadata enrichment for manufacturing domain analysis

Supported Manufacturing Areas:
- 生産管理 (Production Management)
- 品質管理 (Quality Control)
- 設備管理 (Equipment Management)
- 工程管理 (Process Management)
- 在庫管理 (Inventory Management)
"""

from __future__ import annotations

import logging
import re
from datetime import datetime
from typing import Any

import pandas as pd

from .base_handler import IndustryHandlerBase

logger = logging.getLogger(__name__)


class ManufacturingHandler(IndustryHandlerBase):
    """Handler for manufacturing industry Excel formats.

    Supports:
    - 生産管理 (Production Management)
    - 品質管理 (Quality Control)
    - 設備管理 (Equipment Management)
    - 工程管理 (Process Management)
    - 在庫管理 (Inventory Management)
    """

    def __init__(self):
        super().__init__("manufacturing")

    def detect_format_type(self, df: pd.DataFrame, sheet_name: str) -> str | None:
        """Detect manufacturing-specific Excel format types."""
        # Check sheet name patterns
        sheet_patterns = {
            "production_plan": [
                "生産計画",
                "製造計画",
                "production_plan",
                "生産スケジュール",
            ],
            "quality_control": [
                "品質管理",
                "QC",
                "品質検査",
                "quality_control",
                "検査結果",
            ],
            "equipment_mgmt": [
                "設備管理",
                "機械管理",
                "equipment",
                "設備点検",
                "メンテナンス",
            ],
            "process_control": [
                "工程管理",
                "プロセス",
                "process",
                "作業工程",
                "製造工程",
            ],
            "inventory_mgmt": [
                "在庫管理",
                "inventory",
                "部品管理",
                "materials",
                "資材管理",
            ],
        }

        sheet_lower = sheet_name.lower()
        for format_type, keywords in sheet_patterns.items():
            if any(keyword in sheet_lower for keyword in keywords):
                logger.info(
                    f"Detected manufacturing format: {format_type} from sheet name"
                )
                return format_type

        # Check column header patterns
        if df.empty:
            return None

        headers = [str(col).lower() for col in df.columns]
        header_text = " ".join(headers)

        # Production planning indicators
        production_indicators = [
            "製品名",
            "生産数量",
            "予定日",
            "実績",
            "進捗",
            "ライン",
            "工場",
        ]
        if (
            sum(1 for indicator in production_indicators if indicator in header_text)
            >= 3
        ):
            return "production_plan"

        # Quality control indicators
        quality_indicators = [
            "検査項目",
            "合格",
            "不合格",
            "欠陥",
            "品質",
            "測定値",
            "規格",
        ]
        if sum(1 for indicator in quality_indicators if indicator in header_text) >= 3:
            return "quality_control"

        # Equipment management indicators
        equipment_indicators = [
            "設備名",
            "機械",
            "点検日",
            "稼働率",
            "故障",
            "メンテナンス",
        ]
        if (
            sum(1 for indicator in equipment_indicators if indicator in header_text)
            >= 3
        ):
            return "equipment_mgmt"

        # Process control indicators
        process_indicators = ["工程", "作業", "時間", "効率", "歩留", "サイクル"]
        if sum(1 for indicator in process_indicators if indicator in header_text) >= 3:
            return "process_control"

        # Inventory management indicators
        inventory_indicators = ["在庫", "部品", "入庫", "出庫", "発注", "納期"]
        if (
            sum(1 for indicator in inventory_indicators if indicator in header_text)
            >= 3
        ):
            return "inventory_mgmt"

        return None

    def extract_industry_metadata(
        self, df: pd.DataFrame, format_type: str
    ) -> dict[str, Any]:
        """Extract manufacturing-specific metadata."""
        metadata = {
            "industry": "manufacturing",
            "format_type": format_type,
            "analysis_focus": self._get_analysis_focus(format_type),
            "key_metrics": self._extract_key_metrics(df, format_type),
            "time_dimension": self._extract_time_dimension(df),
            "production_entities": self._extract_production_entities(df),
            "quality_indicators": self._extract_quality_indicators(df, format_type),
        }

        return metadata

    def transform_data(self, df: pd.DataFrame, format_type: str) -> pd.DataFrame:
        """Transform manufacturing data for optimal RAG processing."""
        transformed_df = df.copy()

        # Standardize date columns
        transformed_df = self._standardize_dates(transformed_df)

        # Normalize quantity and measurement columns
        transformed_df = self._normalize_quantities(transformed_df)

        # Enrich with calculated fields based on format type
        if format_type == "production_plan":
            transformed_df = self._enrich_production_data(transformed_df)
        elif format_type == "quality_control":
            transformed_df = self._enrich_quality_data(transformed_df)
        elif format_type == "equipment_mgmt":
            transformed_df = self._enrich_equipment_data(transformed_df)

        # Add industry context columns
        transformed_df["industry_domain"] = "manufacturing"
        transformed_df["data_category"] = format_type
        transformed_df["analysis_timestamp"] = datetime.now().isoformat()

        return transformed_df

    def generate_analysis_queries(self, metadata: dict[str, Any]) -> list[str]:
        """Generate manufacturing-specific analysis queries."""
        format_type = metadata.get("format_type", "general")

        queries = {
            "production_plan": [
                "生産計画の達成率が低い製品ラインはどれですか？",
                "生産効率向上のためのボトルネック工程はどこですか？",
                "月別の生産実績トレンドと季節性パターンは？",
                "設備稼働率と生産量の相関関係を分析してください",
                "納期遅延リスクの高い注文を特定してください",
            ],
            "quality_control": [
                "品質不良率が増加傾向にある製品は？",
                "検査工程で最も発見される欠陥タイプは？",
                "品質改善効果の測定と要因分析は？",
                "顧客クレームと品質検査結果の関連性は？",
                "予防保全による品質向上効果は？",
            ],
            "equipment_mgmt": [
                "設備故障の予兆を示すパターンは？",
                "メンテナンスコストが高い設備の優先順位は？",
                "設備稼働率と生産性の最適化ポイントは？",
                "予防保全スケジュールの効果測定は？",
                "設備投資ROIの算出と判断基準は？",
            ],
            "process_control": [
                "工程改善による生産性向上の可能性は？",
                "作業時間短縮のための最適化ポイントは？",
                "工程品質のバラツキ要因分析は？",
                "標準作業時間と実績の乖離要因は？",
                "工程能力指数の改善施策は？",
            ],
            "inventory_mgmt": [
                "在庫回転率の低い部品と改善策は？",
                "発注点の最適化による在庫削減効果は？",
                "欠品リスクの高い重要部品は？",
                "在庫コスト削減のための統合発注効果は？",
                "季節変動を考慮した在庫計画は？",
            ],
        }

        return queries.get(
            format_type,
            [
                "製造業データの主要傾向と改善ポイントは？",
                "生産効率向上のための重要指標は？",
                "品質とコストのバランス最適化は？",
            ],
        )

    def _load_domain_keywords(self) -> dict[str, list[str]]:
        """Load manufacturing domain keywords."""
        return {
            "production": ["生産", "製造", "組立", "加工", "成形", "機械", "ライン"],
            "quality": [
                "品質",
                "検査",
                "試験",
                "測定",
                "規格",
                "基準",
                "合格",
                "不合格",
            ],
            "equipment": ["設備", "機械", "装置", "ツール", "治具", "金型", "プレス"],
            "process": [
                "工程",
                "プロセス",
                "作業",
                "手順",
                "フロー",
                "サイクル",
                "タクト",
            ],
            "materials": ["材料", "部品", "素材", "原料", "資材", "消耗品", "治具"],
            "metrics": ["効率", "歩留", "稼働率", "生産性", "品質率", "コスト", "時間"],
        }

    def _get_analysis_focus(self, format_type: str) -> list[str]:
        """Get analysis focus areas for each format type."""
        focus_map = {
            "production_plan": [
                "生産効率",
                "スケジュール最適化",
                "リソース配分",
                "納期管理",
            ],
            "quality_control": ["品質向上", "不良削減", "検査効率", "顧客満足度"],
            "equipment_mgmt": ["設備効率", "予防保全", "故障分析", "投資効果"],
            "process_control": ["工程改善", "作業効率", "標準化", "品質安定"],
            "inventory_mgmt": ["在庫最適化", "コスト削減", "欠品防止", "回転率向上"],
        }
        return focus_map.get(format_type, ["効率向上", "コスト削減", "品質改善"])

    def _extract_key_metrics(self, df: pd.DataFrame, format_type: str) -> list[str]:
        """Extract key performance metrics from the data."""
        metrics = []
        columns = [str(col).lower() for col in df.columns]

        # Common manufacturing metrics
        metric_patterns = {
            "efficiency": ["効率", "efficiency", "歩留", "yield"],
            "quality": ["品質", "quality", "不良率", "defect"],
            "productivity": ["生産性", "productivity", "生産量", "output"],
            "cost": ["コスト", "cost", "費用", "expense"],
            "time": ["時間", "time", "期間", "duration", "サイクル"],
        }

        for metric_type, patterns in metric_patterns.items():
            if any(pattern in " ".join(columns) for pattern in patterns):
                metrics.append(metric_type)

        return metrics

    def _extract_time_dimension(self, df: pd.DataFrame) -> dict[str, Any]:
        """Extract time-related information from the data."""
        time_info: dict[str, Any] = {
            "has_temporal_data": False,
            "time_columns": [],
            "time_range": None,
            "time_granularity": None,
        }

        # Look for date/time columns
        for col in df.columns:
            col_str = str(col).lower()
            if any(
                keyword in col_str for keyword in ["日付", "日", "date", "time", "年月"]
            ):
                time_info["time_columns"].append(str(col))
                time_info["has_temporal_data"] = True

        return time_info

    def _extract_production_entities(self, df: pd.DataFrame) -> dict[str, list[str]]:
        """Extract production-related entities from the data."""
        entities: dict[str, list[str]] = {
            "products": [],
            "equipment": [],
            "processes": [],
            "locations": [],
        }

        # This is a simplified implementation
        # In practice, would use more sophisticated NLP techniques
        for col in df.columns:
            col_str = str(col).lower()
            if "製品" in col_str or "product" in col_str:
                entities["products"].extend(
                    [str(x) for x in df[col].dropna().unique().tolist()[:10]]
                )
            elif "設備" in col_str or "equipment" in col_str:
                entities["equipment"].extend(
                    [str(x) for x in df[col].dropna().unique().tolist()[:10]]
                )

        return entities

    def _extract_quality_indicators(
        self, df: pd.DataFrame, format_type: str
    ) -> dict[str, Any]:
        """Extract quality-related indicators."""
        quality_info: dict[str, Any] = {
            "has_quality_metrics": False,
            "quality_columns": [],
            "defect_types": [],
            "pass_fail_ratio": None,
        }

        if format_type == "quality_control":
            for col in df.columns:
                col_str = str(col).lower()
                if any(
                    keyword in col_str for keyword in ["品質", "検査", "合格", "不良"]
                ):
                    quality_info["quality_columns"].append(str(col))
                    quality_info["has_quality_metrics"] = True

        return quality_info

    def _standardize_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize date columns to ISO format."""
        for col in df.columns:
            col_str = str(col).lower()
            if any(keyword in col_str for keyword in ["日付", "date", "年月日"]):
                try:
                    df[col] = pd.to_datetime(df[col], errors="coerce")
                except Exception as e:
                    logger.warning(f"Could not convert {col} to datetime: {e}")
        return df

    def _normalize_quantities(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize quantity and measurement columns."""
        for col in df.columns:
            col_str = str(col).lower()
            if any(
                keyword in col_str for keyword in ["数量", "quantity", "重量", "weight"]
            ):
                # Remove Japanese unit suffixes and convert to numeric
                try:
                    df[col] = (
                        df[col].astype(str).str.replace("[個台件万]", "", regex=True)
                    )
                    df[col] = pd.to_numeric(df[col], errors="coerce")
                except Exception as e:
                    logger.warning(f"Could not normalize {col}: {e}")
        return df

    def _enrich_production_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add calculated fields for production data."""
        # Add production efficiency calculations if possible
        if "計画数量" in df.columns and "実績数量" in df.columns:
            df["達成率"] = (df["実績数量"] / df["計画数量"] * 100).round(2)

        return df

    def _enrich_quality_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add calculated fields for quality data."""
        # Add quality metrics if possible
        pass_cols = [col for col in df.columns if "合格" in str(col).lower()]
        fail_cols = [col for col in df.columns if "不良" in str(col).lower()]

        if pass_cols and fail_cols:
            df["品質率"] = (
                df[pass_cols[0]] / (df[pass_cols[0]] + df[fail_cols[0]]) * 100
            ).round(2)

        return df

    def _enrich_equipment_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add calculated fields for equipment data."""
        # Add equipment efficiency calculations if possible
        if "稼働時間" in df.columns and "計画時間" in df.columns:
            df["稼働率"] = (df["稼働時間"] / df["計画時間"] * 100).round(2)

        return df
