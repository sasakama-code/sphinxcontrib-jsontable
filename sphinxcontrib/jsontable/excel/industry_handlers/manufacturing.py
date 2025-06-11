"""Manufacturing industry specialized Excel format handler.

This module provides specialized handling for manufacturing industry Excel formats
commonly used in Japanese business environments, including production management,
quality control, equipment management, process control, and inventory management.

Features:
- Production planning and scheduling analysis
- Quality control and inspection data processing
- Equipment management and maintenance tracking
- Process optimization and efficiency analysis
- Inventory management and materials planning
- Japanese manufacturing terminology recognition
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import pandas as pd

from .base import IndustryHandlerBase

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

        # Normalize quantity columns
        transformed_df = self._normalize_quantities(transformed_df)

        # Add format-specific enrichments
        if format_type == "production_plan":
            transformed_df = self._enrich_production_data(transformed_df)
        elif format_type == "quality_control":
            transformed_df = self._enrich_quality_data(transformed_df)
        elif format_type == "equipment_mgmt":
            transformed_df = self._enrich_equipment_data(transformed_df)

        return transformed_df

    def generate_analysis_queries(self, metadata: dict[str, Any]) -> list[str]:
        """Generate manufacturing-specific analysis queries."""
        format_type = metadata.get("format_type", "")
        queries = []

        if format_type == "production_plan":
            queries.extend([
                "生産計画の進捗率はどの程度ですか？",
                "最も生産性の高い製造ラインはどれですか？",
                "計画と実績の差異が大きい製品はありますか？",
                "工場別の生産効率を比較してください",
            ])
        elif format_type == "quality_control":
            queries.extend([
                "品質検査の合格率はどのくらいですか？",
                "最も多い不良原因は何ですか？",
                "品質指標の改善傾向はありますか？",
                "検査項目別の不合格率を分析してください",
            ])
        elif format_type == "equipment_mgmt":
            queries.extend([
                "設備の稼働率はどの程度ですか？",
                "メンテナンス頻度が高い設備はどれですか？",
                "故障による生産への影響を分析してください",
                "設備の更新計画を立てるためのデータを提供してください",
            ])

        # Add general manufacturing queries
        queries.extend([
            "製造コストの削減ポイントはどこですか？",
            "品質向上のための改善提案を生成してください",
            "生産効率を向上させる方法を提案してください",
        ])

        return queries

    def _load_domain_keywords(self) -> dict[str, list[str]]:
        """Load manufacturing-specific domain keywords."""
        return {
            "production": [
                "生産", "製造", "組立", "加工", "工程", "ライン", "工場",
                "設備", "機械", "生産性", "効率", "歩留", "サイクル時間"
            ],
            "quality": [
                "品質", "検査", "測定", "規格", "公差", "不良", "欠陥",
                "合格", "不合格", "QC", "品質管理", "改善", "是正"
            ],
            "inventory": [
                "在庫", "部品", "材料", "資材", "入庫", "出庫", "発注",
                "納期", "調達", "供給", "需要", "安全在庫"
            ],
            "maintenance": [
                "保守", "点検", "整備", "故障", "修理", "交換", "予防",
                "定期", "緊急", "稼働率", "MTTR", "MTBF"
            ]
        }

    def _get_analysis_focus(self, format_type: str) -> str:
        """Get analysis focus for the given format type."""
        focus_map = {
            "production_plan": "生産効率と計画達成度の分析",
            "quality_control": "品質管理と不良分析",
            "equipment_mgmt": "設備効率と保全管理",
            "process_control": "工程最適化と作業効率",
            "inventory_mgmt": "在庫最適化と調達管理",
        }
        return focus_map.get(format_type, "製造業データの総合分析")

    def _extract_key_metrics(self, df: pd.DataFrame, format_type: str) -> dict[str, Any]:
        """Extract key manufacturing metrics from data."""
        metrics = {}
        
        if format_type == "production_plan":
            # Look for production-related metrics
            for col in df.columns:
                col_lower = str(col).lower()
                if any(term in col_lower for term in ["数量", "quantity", "実績", "計画"]):
                    try:
                        numeric_data = pd.to_numeric(df[col], errors='coerce')
                        if not numeric_data.isna().all():
                            metrics[col] = {
                                "sum": float(numeric_data.sum()),
                                "mean": float(numeric_data.mean()),
                                "max": float(numeric_data.max()),
                                "min": float(numeric_data.min())
                            }
                    except (ValueError, TypeError):
                        continue
        
        return metrics

    def _extract_time_dimension(self, df: pd.DataFrame) -> dict[str, Any]:
        """Extract time-related information from manufacturing data."""
        time_info = {
            "has_time_data": False,
            "time_columns": [],
            "time_range": None,
        }
        
        for col in df.columns:
            col_lower = str(col).lower()
            if any(term in col_lower for term in ["日", "date", "time", "予定", "実績"]):
                time_info["time_columns"].append(col)
                time_info["has_time_data"] = True
        
        return time_info

    def _extract_production_entities(self, df: pd.DataFrame) -> dict[str, Any]:
        """Extract production-related entities from data."""
        entities = {
            "products": [],
            "lines": [],
            "facilities": [],
        }
        
        for col in df.columns:
            col_lower = str(col).lower()
            if any(term in col_lower for term in ["製品", "product", "商品"]):
                entities["products"] = df[col].dropna().unique().tolist()[:10]
            elif any(term in col_lower for term in ["ライン", "line", "工程"]):
                entities["lines"] = df[col].dropna().unique().tolist()[:10]
            elif any(term in col_lower for term in ["工場", "facility", "設備"]):
                entities["facilities"] = df[col].dropna().unique().tolist()[:10]
        
        return entities

    def _extract_quality_indicators(self, df: pd.DataFrame, format_type: str) -> dict[str, Any]:
        """Extract quality-related indicators from data."""
        quality_info = {
            "has_quality_data": False,
            "quality_metrics": [],
            "defect_types": [],
        }
        
        if format_type == "quality_control":
            for col in df.columns:
                col_lower = str(col).lower()
                if any(term in col_lower for term in ["品質", "quality", "合格", "不合格", "欠陥"]):
                    quality_info["quality_metrics"].append(col)
                    quality_info["has_quality_data"] = True
        
        return quality_info

    def _standardize_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize date formats in the DataFrame."""
        # Implementation for date standardization
        return df

    def _normalize_quantities(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize quantity and numerical values."""
        # Implementation for quantity normalization
        return df

    def _enrich_production_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add production-specific enrichments."""
        # Add production efficiency calculations
        enriched_df = df.copy()
        enriched_df['_manufacturing_timestamp'] = datetime.now().isoformat()
        return enriched_df

    def _enrich_quality_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add quality-specific enrichments."""
        # Add quality analysis enrichments
        enriched_df = df.copy()
        enriched_df['_quality_analysis_timestamp'] = datetime.now().isoformat()
        return enriched_df

    def _enrich_equipment_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add equipment-specific enrichments."""
        # Add equipment analysis enrichments
        enriched_df = df.copy()
        enriched_df['_equipment_analysis_timestamp'] = datetime.now().isoformat()
        return enriched_df