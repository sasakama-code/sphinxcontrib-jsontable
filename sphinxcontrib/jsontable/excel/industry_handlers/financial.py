"""Financial industry specialized Excel format handler.

This module provides specialized handling for financial industry Excel formats
commonly used in Japanese business environments, including risk management,
financial analysis, compliance, investment analysis, and cash management.

Features:
- Risk management and assessment analysis
- Financial statement and performance analysis
- Regulatory compliance and reporting
- Investment portfolio and analysis
- Cash flow and liquidity management
- Japanese financial terminology recognition
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import pandas as pd

from .base import IndustryHandlerBase

logger = logging.getLogger(__name__)


class FinancialHandler(IndustryHandlerBase):
    """Handler for financial industry Excel formats.

    Supports:
    - リスク管理 (Risk Management)
    - 財務分析 (Financial Analysis)
    - コンプライアンス (Compliance)
    - 投資分析 (Investment Analysis)
    - 資金管理 (Cash Management)
    """

    def __init__(self):
        super().__init__("financial")

    def detect_format_type(self, df: pd.DataFrame, sheet_name: str) -> str | None:
        """Detect financial-specific Excel format types."""
        # Check sheet name patterns
        sheet_patterns = {
            "risk_management": [
                "リスク管理",
                "risk",
                "VaR",
                "信用リスク",
                "市場リスク",
                "リスク評価",
            ],
            "financial_analysis": [
                "財務分析",
                "financial_analysis",
                "PL",
                "BS",
                "損益",
                "貸借対照表",
                "財務諸表",
            ],
            "compliance": [
                "コンプライアンス",
                "compliance",
                "規制",
                "監査",
                "内部統制",
                "法令遵守",
            ],
            "investment": [
                "投資",
                "investment",
                "ポートフォリオ",
                "運用",
                "資産",
                "投資分析",
            ],
            "cash_mgmt": [
                "資金管理",
                "cash",
                "流動性",
                "キャッシュフロー",
                "資金調達",
                "資金運用",
            ],
        }

        sheet_lower = sheet_name.lower()
        for format_type, keywords in sheet_patterns.items():
            if any(keyword in sheet_lower for keyword in keywords):
                logger.info(f"Detected financial format: {format_type} from sheet name")
                return format_type

        # Check column header patterns
        if df.empty:
            return None

        headers = [str(col).lower() for col in df.columns]
        header_text = " ".join(headers)

        # Risk management indicators
        risk_indicators = ["リスク", "VaR", "信用", "格付", "損失", "exposure"]
        if sum(1 for indicator in risk_indicators if indicator in header_text) >= 2:
            return "risk_management"

        # Financial analysis indicators
        financial_indicators = ["売上", "利益", "資産", "負債", "ROE", "ROA", "EBITDA"]
        if sum(1 for indicator in financial_indicators if indicator in header_text) >= 3:
            return "financial_analysis"

        # Compliance indicators
        compliance_indicators = ["監査", "規制", "法令", "内部統制", "コンプライアンス"]
        if sum(1 for indicator in compliance_indicators if indicator in header_text) >= 2:
            return "compliance"

        # Investment indicators
        investment_indicators = ["投資", "運用", "ポートフォリオ", "資産", "収益率"]
        if sum(1 for indicator in investment_indicators if indicator in header_text) >= 2:
            return "investment"

        # Cash management indicators
        cash_indicators = ["資金", "キャッシュ", "流動性", "調達", "運用", "現金"]
        if sum(1 for indicator in cash_indicators if indicator in header_text) >= 2:
            return "cash_mgmt"

        return None

    def extract_industry_metadata(
        self, df: pd.DataFrame, format_type: str
    ) -> dict[str, Any]:
        """Extract financial-specific metadata."""
        metadata = {
            "industry": "financial",
            "format_type": format_type,
            "analysis_focus": self._get_financial_analysis_focus(format_type),
            "key_metrics": self._extract_financial_metrics(df, format_type),
            "risk_factors": self._extract_risk_factors(df),
            "regulatory_context": self._extract_regulatory_context(df, format_type),
            "time_horizons": self._extract_time_horizons(df),
        }

        return metadata

    def transform_data(self, df: pd.DataFrame, format_type: str) -> pd.DataFrame:
        """Transform financial data for optimal RAG processing."""
        transformed_df = df.copy()

        # Standardize financial values
        transformed_df = self._standardize_financial_values(transformed_df)

        # Add format-specific enrichments
        if format_type in ["financial_analysis", "investment"]:
            transformed_df = self._enrich_financial_analysis(transformed_df)
        elif format_type == "risk_management":
            transformed_df = self._enrich_risk_data(transformed_df)

        # Add financial context
        transformed_df["industry_domain"] = "financial"
        transformed_df["data_category"] = format_type
        transformed_df["analysis_timestamp"] = datetime.now().isoformat()

        return transformed_df

    def generate_analysis_queries(self, metadata: dict[str, Any]) -> list[str]:
        """Generate financial-specific analysis queries."""
        format_type = metadata.get("format_type", "general")

        queries = {
            "risk_management": [
                "主要リスクファクターの定量的評価は？",
                "VaRモデルによるリスク測定結果は？",
                "信用リスクの集中度と分散状況は？",
                "市場リスクの感応度分析結果は？",
                "ストレステストによる耐性評価は？",
                "リスク限度額の使用状況とアラートは？",
            ],
            "financial_analysis": [
                "収益性指標の改善トレンドは？",
                "財務健全性の評価と課題は？",
                "キャッシュフロー分析による資金繰りは？",
                "ROE・ROA等の効率性指標分析は？",
                "競合他社との財務比較分析は？",
                "将来の業績予測と成長戦略は？",
            ],
            "compliance": [
                "規制要求事項の遵守状況は？",
                "内部統制の有効性評価は？",
                "監査指摘事項の改善状況は？",
                "法令変更による影響評価は？",
                "コンプライアンス体制の強化は？",
            ],
            "investment": [
                "ポートフォリオのリスク・リターン分析は？",
                "資産配分の最適化提案は？",
                "投資パフォーマンスの評価は？",
                "ベンチマークとの乖離要因は？",
                "ESG投資の組み入れ効果は？",
            ],
            "cash_mgmt": [
                "流動性リスクの評価と対策は？",
                "資金調達コストの最適化は？",
                "キャッシュフロー予測の精度は？",
                "短期資金運用の効率性は？",
                "資金管理体制の改善点は？",
            ],
        }

        result_queries = queries.get(format_type, [])
        
        # Add general financial queries
        result_queries.extend([
            "金融業界のトレンドと将来展望は？",
            "デジタル化による業務効率化の効果は？",
            "金融規制の変化への対応戦略は？",
            "持続可能な金融事業のための提案は？",
        ])

        return result_queries

    def _get_financial_analysis_focus(self, format_type: str) -> str:
        """Get analysis focus for financial format types."""
        focus_map = {
            "risk_management": "リスク評価と管理体制強化",
            "financial_analysis": "財務パフォーマンス分析と改善",
            "compliance": "規制遵守と内部統制強化",
            "investment": "投資効率と収益最適化",
            "cash_mgmt": "流動性管理と資金効率化",
        }
        return focus_map.get(format_type, "金融データの総合分析")

    def _extract_financial_metrics(self, df: pd.DataFrame, format_type: str) -> dict[str, Any]:
        """Extract key financial metrics from data."""
        metrics = {}
        
        # Look for financial metrics based on format type
        financial_terms = {
            "monetary": ["金額", "amount", "value", "円", "dollar", "yen"],
            "percentage": ["率", "ratio", "percent", "%"],
            "performance": ["収益", "利益", "損失", "ROE", "ROA", "EBITDA"],
        }
        
        for col in df.columns:
            col_lower = str(col).lower()
            try:
                numeric_data = pd.to_numeric(df[col], errors='coerce')
                if not numeric_data.isna().all():
                    # Determine metric type
                    metric_type = "other"
                    for term_type, terms in financial_terms.items():
                        if any(term in col_lower for term in terms):
                            metric_type = term_type
                            break
                    
                    metrics[col] = {
                        "type": metric_type,
                        "total": float(numeric_data.sum()),
                        "average": float(numeric_data.mean()),
                        "max": float(numeric_data.max()),
                        "min": float(numeric_data.min()),
                        "std_dev": float(numeric_data.std())
                    }
            except (ValueError, TypeError):
                continue
        
        return metrics

    def _extract_risk_factors(self, df: pd.DataFrame) -> list[str]:
        """Extract risk factors from financial data."""
        risk_factors = []
        risk_terms = ["信用リスク", "市場リスク", "流動性リスク", "オペレーショナルリスク", "金利リスク"]
        
        for col in df.columns:
            col_str = str(col)
            for term in risk_terms:
                if term in col_str:
                    risk_factors.append(term)
        
        return list(set(risk_factors))

    def _extract_regulatory_context(self, df: pd.DataFrame, format_type: str) -> dict[str, Any]:
        """Extract regulatory context from financial data."""
        regulatory_info = {
            "applicable_regulations": [],
            "reporting_requirements": [],
            "compliance_status": "unknown",
        }
        
        if format_type == "compliance":
            # Look for regulatory indicators in column names
            regulatory_terms = ["バーゼル", "IFRS", "JGAAP", "金融庁", "監査"]
            for col in df.columns:
                col_str = str(col)
                for term in regulatory_terms:
                    if term in col_str:
                        regulatory_info["applicable_regulations"].append(term)
        
        return regulatory_info

    def _extract_time_horizons(self, df: pd.DataFrame) -> dict[str, Any]:
        """Extract time horizon information from financial data."""
        time_info = {
            "has_time_series": False,
            "time_columns": [],
            "analysis_period": None,
        }
        
        for col in df.columns:
            col_lower = str(col).lower()
            if any(term in col_lower for term in ["日", "月", "年", "期", "date", "time"]):
                time_info["time_columns"].append(col)
                time_info["has_time_series"] = True
        
        return time_info

    def _standardize_financial_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize financial values and units."""
        # Implementation for financial value standardization
        return df

    def _enrich_financial_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add financial analysis enrichments."""
        enriched_df = df.copy()
        enriched_df['_financial_analysis_timestamp'] = datetime.now().isoformat()
        return enriched_df

    def _enrich_risk_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add risk analysis enrichments."""
        enriched_df = df.copy()
        enriched_df['_risk_analysis_timestamp'] = datetime.now().isoformat()
        return enriched_df

    def _load_domain_keywords(self) -> dict[str, list[str]]:
        """Load financial-specific domain keywords."""
        return {
            "risk": [
                "リスク", "VaR", "信用リスク", "市場リスク", "流動性リスク",
                "オペレーショナルリスク", "格付", "デフォルト", "損失", "exposure"
            ],
            "financial_metrics": [
                "ROE", "ROA", "EBITDA", "PER", "PBR", "自己資本比率",
                "流動比率", "負債比率", "売上高", "営業利益", "純利益"
            ],
            "investment": [
                "投資", "運用", "ポートフォリオ", "資産配分", "分散投資",
                "リターン", "ベンチマーク", "アクティブ", "パッシブ", "ESG"
            ],
            "compliance": [
                "コンプライアンス", "規制", "法令", "監査", "内部統制",
                "金融庁", "バーゼル", "IFRS", "報告", "開示"
            ]
        }