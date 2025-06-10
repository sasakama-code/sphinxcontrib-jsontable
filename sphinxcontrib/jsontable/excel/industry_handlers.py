"""Industry-specific Excel format handlers for specialized business data processing.

This module provides specialized handlers for industry-specific Excel formats commonly
used in Japanese business environments, including manufacturing, retail, and financial
sectors. Each handler implements domain-specific data extraction and transformation
patterns.

Key Features:
- Manufacturing production management Excel formats
- Retail sales and inventory tracking Excel formats  
- Financial risk management and reporting Excel formats
- Industry-specific terminology and entity recognition
- Japanese business document structure understanding
- Automated metadata enrichment for domain analysis

Supported Industries:
- 製造業 (Manufacturing): 生産管理、品質管理、設備管理
- 小売業 (Retail): 販売実績、在庫管理、顧客分析  
- 金融業 (Financial): リスク管理、財務分析、コンプライアンス
"""

from __future__ import annotations

import logging
import re
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd

logger = logging.getLogger(__name__)


class IndustryHandlerBase(ABC):
    """Base class for industry-specific Excel format handlers."""
    
    def __init__(self, industry_name: str):
        """Initialize industry handler.
        
        Args:
            industry_name: Name of the industry (e.g., 'manufacturing', 'retail', 'financial')
        """
        self.industry_name = industry_name
        self.domain_keywords = self._load_domain_keywords()
        self.entity_patterns = self._load_entity_patterns()
        logger.info(f"Initialized {industry_name} industry handler")
    
    @abstractmethod
    def detect_format_type(self, df: pd.DataFrame, sheet_name: str) -> Optional[str]:
        """Detect specific format type within the industry.
        
        Args:
            df: DataFrame containing Excel data
            sheet_name: Name of the Excel sheet
            
        Returns:
            Format type string or None if not detected
        """
        pass
    
    @abstractmethod
    def extract_industry_metadata(self, df: pd.DataFrame, format_type: str) -> Dict[str, Any]:
        """Extract industry-specific metadata from the data.
        
        Args:
            df: DataFrame containing Excel data
            format_type: Detected format type
            
        Returns:
            Dictionary containing industry-specific metadata
        """
        pass
    
    @abstractmethod
    def transform_data(self, df: pd.DataFrame, format_type: str) -> pd.DataFrame:
        """Transform data according to industry standards.
        
        Args:
            df: Original DataFrame
            format_type: Detected format type
            
        Returns:
            Transformed DataFrame optimized for RAG processing
        """
        pass
    
    @abstractmethod
    def generate_analysis_queries(self, metadata: Dict[str, Any]) -> List[str]:
        """Generate industry-specific analysis query suggestions.
        
        Args:
            metadata: Industry-specific metadata
            
        Returns:
            List of suggested queries for this industry domain
        """
        pass
    
    def _load_domain_keywords(self) -> Dict[str, List[str]]:
        """Load domain-specific keywords for content detection."""
        # Base implementation - to be overridden by specific handlers
        return {
            "general": ["データ", "分析", "レポート", "管理", "システム"]
        }
    
    def _load_entity_patterns(self) -> Dict[str, re.Pattern]:
        """Load regex patterns for industry-specific entity recognition."""
        # Base implementation - to be overridden by specific handlers
        return {
            "japanese_date": re.compile(r"\d{4}年\d{1,2}月\d{1,2}日"),
            "japanese_number": re.compile(r"[\d,]+(?:\.\d+)?[万億兆]?[円個台件]?")
        }


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
    
    def detect_format_type(self, df: pd.DataFrame, sheet_name: str) -> Optional[str]:
        """Detect manufacturing-specific Excel format types."""
        # Check sheet name patterns
        sheet_patterns = {
            "production_plan": ["生産計画", "製造計画", "production_plan", "生産スケジュール"],
            "quality_control": ["品質管理", "QC", "品質検査", "quality_control", "検査結果"],
            "equipment_mgmt": ["設備管理", "機械管理", "equipment", "設備点検", "メンテナンス"],
            "process_control": ["工程管理", "プロセス", "process", "作業工程", "製造工程"],
            "inventory_mgmt": ["在庫管理", "inventory", "部品管理", "materials", "資材管理"]
        }
        
        sheet_lower = sheet_name.lower()
        for format_type, keywords in sheet_patterns.items():
            if any(keyword in sheet_lower for keyword in keywords):
                logger.info(f"Detected manufacturing format: {format_type} from sheet name")
                return format_type
        
        # Check column header patterns
        if df.empty:
            return None
            
        headers = [str(col).lower() for col in df.columns]
        header_text = " ".join(headers)
        
        # Production planning indicators
        production_indicators = ["製品名", "生産数量", "予定日", "実績", "進捗", "ライン", "工場"]
        if sum(1 for indicator in production_indicators if indicator in header_text) >= 3:
            return "production_plan"
        
        # Quality control indicators  
        quality_indicators = ["検査項目", "合格", "不合格", "欠陥", "品質", "測定値", "規格"]
        if sum(1 for indicator in quality_indicators if indicator in header_text) >= 3:
            return "quality_control"
        
        # Equipment management indicators
        equipment_indicators = ["設備名", "機械", "点検日", "稼働率", "故障", "メンテナンス"]
        if sum(1 for indicator in equipment_indicators if indicator in header_text) >= 3:
            return "equipment_mgmt"
        
        # Process control indicators
        process_indicators = ["工程", "作業", "時間", "効率", "歩留", "サイクル"]
        if sum(1 for indicator in process_indicators if indicator in header_text) >= 3:
            return "process_control"
        
        # Inventory management indicators
        inventory_indicators = ["在庫", "部品", "入庫", "出庫", "発注", "納期"]
        if sum(1 for indicator in inventory_indicators if indicator in header_text) >= 3:
            return "inventory_mgmt"
        
        return None
    
    def extract_industry_metadata(self, df: pd.DataFrame, format_type: str) -> Dict[str, Any]:
        """Extract manufacturing-specific metadata."""
        metadata = {
            "industry": "manufacturing",
            "format_type": format_type,
            "analysis_focus": self._get_analysis_focus(format_type),
            "key_metrics": self._extract_key_metrics(df, format_type),
            "time_dimension": self._extract_time_dimension(df),
            "production_entities": self._extract_production_entities(df),
            "quality_indicators": self._extract_quality_indicators(df, format_type)
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
    
    def generate_analysis_queries(self, metadata: Dict[str, Any]) -> List[str]:
        """Generate manufacturing-specific analysis queries."""
        format_type = metadata.get("format_type", "general")
        
        queries = {
            "production_plan": [
                "生産計画の達成率が低い製品ラインはどれですか？",
                "生産効率向上のためのボトルネック工程はどこですか？",
                "月別の生産実績トレンドと季節性パターンは？",
                "設備稼働率と生産量の相関関係を分析してください",
                "納期遅延リスクの高い注文を特定してください"
            ],
            "quality_control": [
                "品質不良率が増加傾向にある製品は？",
                "検査工程で最も発見される欠陥タイプは？",
                "品質改善効果の測定と要因分析は？",
                "顧客クレームと品質検査結果の関連性は？",
                "予防保全による品質向上効果は？"
            ],
            "equipment_mgmt": [
                "設備故障の予兆を示すパターンは？",
                "メンテナンスコストが高い設備の優先順位は？",
                "設備稼働率と生産性の最適化ポイントは？",
                "予防保全スケジュールの効果測定は？",
                "設備投資ROIの算出と判断基準は？"
            ],
            "process_control": [
                "工程改善による生産性向上の可能性は？",
                "作業時間短縮のための最適化ポイントは？",
                "工程品質のバラツキ要因分析は？",
                "標準作業時間と実績の乖離要因は？",
                "工程能力指数の改善施策は？"
            ],
            "inventory_mgmt": [
                "在庫回転率の低い部品と改善策は？",
                "発注点の最適化による在庫削減効果は？",
                "欠品リスクの高い重要部品は？",
                "在庫コスト削減のための統合発注効果は？",
                "季節変動を考慮した在庫計画は？"
            ]
        }
        
        return queries.get(format_type, [
            "製造業データの主要傾向と改善ポイントは？",
            "生産効率向上のための重要指標は？",
            "品質とコストのバランス最適化は？"
        ])
    
    def _load_domain_keywords(self) -> Dict[str, List[str]]:
        """Load manufacturing domain keywords."""
        return {
            "production": ["生産", "製造", "組立", "加工", "成形", "機械", "ライン"],
            "quality": ["品質", "検査", "試験", "測定", "規格", "基準", "合格", "不合格"],
            "equipment": ["設備", "機械", "装置", "ツール", "治具", "金型", "プレス"],
            "process": ["工程", "プロセス", "作業", "手順", "フロー", "サイクル", "タクト"],
            "materials": ["材料", "部品", "素材", "原料", "資材", "消耗品", "治具"],
            "metrics": ["効率", "歩留", "稼働率", "生産性", "品質率", "コスト", "時間"]
        }
    
    def _get_analysis_focus(self, format_type: str) -> List[str]:
        """Get analysis focus areas for each format type."""
        focus_map = {
            "production_plan": ["生産効率", "スケジュール最適化", "リソース配分", "納期管理"],
            "quality_control": ["品質向上", "不良削減", "検査効率", "顧客満足度"],
            "equipment_mgmt": ["設備効率", "予防保全", "故障分析", "投資効果"],
            "process_control": ["工程改善", "作業効率", "標準化", "品質安定"],
            "inventory_mgmt": ["在庫最適化", "コスト削減", "欠品防止", "回転率向上"]
        }
        return focus_map.get(format_type, ["効率向上", "コスト削減", "品質改善"])
    
    def _extract_key_metrics(self, df: pd.DataFrame, format_type: str) -> List[str]:
        """Extract key performance metrics from the data."""
        metrics = []
        columns = [str(col).lower() for col in df.columns]
        
        # Common manufacturing metrics
        metric_patterns = {
            "efficiency": ["効率", "efficiency", "歩留", "yield"],
            "quality": ["品質", "quality", "不良率", "defect"],
            "productivity": ["生産性", "productivity", "生産量", "output"],
            "cost": ["コスト", "cost", "費用", "expense"],
            "time": ["時間", "time", "期間", "duration", "サイクル"]
        }
        
        for metric_type, patterns in metric_patterns.items():
            if any(pattern in " ".join(columns) for pattern in patterns):
                metrics.append(metric_type)
        
        return metrics
    
    def _extract_time_dimension(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Extract time-related information from the data."""
        time_info = {
            "has_temporal_data": False,
            "time_columns": [],
            "time_range": None,
            "time_granularity": None
        }
        
        # Look for date/time columns
        for col in df.columns:
            col_str = str(col).lower()
            if any(keyword in col_str for keyword in ["日付", "日", "date", "time", "年月"]):
                time_info["time_columns"].append(str(col))
                time_info["has_temporal_data"] = True
        
        return time_info
    
    def _extract_production_entities(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """Extract production-related entities from the data."""
        entities: Dict[str, List[str]] = {
            "products": [],
            "equipment": [],
            "processes": [],
            "locations": []
        }
        
        # This is a simplified implementation
        # In practice, would use more sophisticated NLP techniques
        for col in df.columns:
            col_str = str(col).lower()
            if "製品" in col_str or "product" in col_str:
                entities["products"].extend([str(x) for x in df[col].dropna().unique().tolist()[:10]])
            elif "設備" in col_str or "equipment" in col_str:
                entities["equipment"].extend([str(x) for x in df[col].dropna().unique().tolist()[:10]])
        
        return entities
    
    def _extract_quality_indicators(self, df: pd.DataFrame, format_type: str) -> Dict[str, Any]:
        """Extract quality-related indicators."""
        quality_info = {
            "has_quality_metrics": False,
            "quality_columns": [],
            "defect_types": [],
            "pass_fail_ratio": None
        }
        
        if format_type == "quality_control":
            for col in df.columns:
                col_str = str(col).lower()
                if any(keyword in col_str for keyword in ["品質", "検査", "合格", "不良"]):
                    quality_info["quality_columns"].append(str(col))
                    quality_info["has_quality_metrics"] = True
        
        return quality_info
    
    def _standardize_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize date columns to ISO format."""
        for col in df.columns:
            col_str = str(col).lower()
            if any(keyword in col_str for keyword in ["日付", "date", "年月日"]):
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                except Exception as e:
                    logger.warning(f"Could not convert {col} to datetime: {e}")
        return df
    
    def _normalize_quantities(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize quantity and measurement columns."""
        for col in df.columns:
            col_str = str(col).lower()
            if any(keyword in col_str for keyword in ["数量", "quantity", "重量", "weight"]):
                # Remove Japanese unit suffixes and convert to numeric
                try:
                    df[col] = df[col].astype(str).str.replace('[個台件万]', '', regex=True)
                    df[col] = pd.to_numeric(df[col], errors='coerce')
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
            df["品質率"] = (df[pass_cols[0]] / (df[pass_cols[0]] + df[fail_cols[0]]) * 100).round(2)
        
        return df
    
    def _enrich_equipment_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add calculated fields for equipment data."""
        # Add equipment efficiency calculations if possible
        if "稼働時間" in df.columns and "計画時間" in df.columns:
            df["稼働率"] = (df["稼働時間"] / df["計画時間"] * 100).round(2)
        
        return df


class RetailHandler(IndustryHandlerBase):
    """Handler for retail industry Excel formats.
    
    Supports:
    - 販売実績 (Sales Performance)
    - 在庫管理 (Inventory Management)
    - 顧客分析 (Customer Analysis)
    - 店舗運営 (Store Operations)
    - マーケティング (Marketing Analytics)
    """
    
    def __init__(self):
        super().__init__("retail")
    
    def detect_format_type(self, df: pd.DataFrame, sheet_name: str) -> Optional[str]:
        """Detect retail-specific Excel format types."""
        # Sheet name pattern detection
        sheet_patterns = {
            "sales_performance": ["売上", "販売実績", "sales", "revenue", "セールス"],
            "inventory": ["在庫", "inventory", "stock", "商品管理"],
            "customer_analysis": ["顧客", "customer", "会員", "member", "購買"],
            "store_operations": ["店舗", "store", "運営", "operations", "ショップ"],
            "marketing": ["マーケティング", "marketing", "広告", "promotion", "キャンペーン"]
        }
        
        sheet_lower = sheet_name.lower()
        for format_type, keywords in sheet_patterns.items():
            if any(keyword in sheet_lower for keyword in keywords):
                return format_type
        
        # Column header analysis
        if df.empty:
            return None
            
        headers = [str(col).lower() for col in df.columns]
        header_text = " ".join(headers)
        
        # Sales performance indicators
        sales_indicators = ["売上", "販売", "revenue", "price", "金額", "数量"]
        if sum(1 for indicator in sales_indicators if indicator in header_text) >= 2:
            return "sales_performance"
        
        # Inventory indicators
        inventory_indicators = ["在庫", "stock", "入荷", "出荷", "商品"]
        if sum(1 for indicator in inventory_indicators if indicator in header_text) >= 2:
            return "inventory"
        
        # Customer analysis indicators
        customer_indicators = ["顧客", "customer", "会員", "購入", "購買"]
        if sum(1 for indicator in customer_indicators if indicator in header_text) >= 2:
            return "customer_analysis"
        
        return None
    
    def extract_industry_metadata(self, df: pd.DataFrame, format_type: str) -> Dict[str, Any]:
        """Extract retail-specific metadata."""
        metadata = {
            "industry": "retail",
            "format_type": format_type,
            "analysis_focus": self._get_retail_analysis_focus(format_type),
            "key_metrics": self._extract_retail_metrics(df, format_type),
            "product_categories": self._extract_product_categories(df),
            "sales_channels": self._extract_sales_channels(df),
            "geographic_dimension": self._extract_geographic_info(df)
        }
        
        return metadata
    
    def transform_data(self, df: pd.DataFrame, format_type: str) -> pd.DataFrame:
        """Transform retail data for optimal RAG processing."""
        transformed_df = df.copy()
        
        # Standardize monetary values
        transformed_df = self._standardize_monetary_values(transformed_df)
        
        # Normalize product information
        transformed_df = self._normalize_product_info(transformed_df)
        
        # Add retail-specific calculated fields
        if format_type == "sales_performance":
            transformed_df = self._enrich_sales_data(transformed_df)
        elif format_type == "customer_analysis":
            transformed_df = self._enrich_customer_data(transformed_df)
        
        # Add retail context
        transformed_df["industry_domain"] = "retail"
        transformed_df["data_category"] = format_type
        
        return transformed_df
    
    def generate_analysis_queries(self, metadata: Dict[str, Any]) -> List[str]:
        """Generate retail-specific analysis queries."""
        format_type = metadata.get("format_type", "general")
        
        queries = {
            "sales_performance": [
                "売上高上位の商品カテゴリと成長トレンドは？",
                "季節性による売上変動パターンの分析は？",
                "店舗別売上効率と改善ポイントは？",
                "商品別粗利率と収益性分析は？",
                "売上予測と在庫最適化の連携は？"
            ],
            "customer_analysis": [
                "顧客セグメント別の購買パターンは？",
                "リピート率向上のための施策は？",
                "顧客生涯価値（LTV）の高い顧客特徴は？",
                "新規顧客獲得とリテンション戦略は？",
                "購買頻度と客単価の関係分析は？"
            ],
            "inventory": [
                "在庫回転率の改善が必要な商品は？",
                "欠品による機会損失の定量化は？",
                "季節商品の仕入れ最適化は？",
                "デッドストック削減のための対策は？",
                "ABC分析による重点管理商品は？"
            ]
        }
        
        return queries.get(format_type, [
            "小売業績向上のための重要指標は？",
            "顧客満足度と売上の相関関係は？",
            "競合優位性確保のための分析は？"
        ])
    
    def _get_retail_analysis_focus(self, format_type: str) -> List[str]:
        """Get retail analysis focus areas."""
        focus_map = {
            "sales_performance": ["売上向上", "収益性改善", "商品戦略", "価格最適化"],
            "customer_analysis": ["顧客満足度", "リテンション", "セグメンテーション", "LTV向上"],
            "inventory": ["在庫最適化", "回転率改善", "欠品防止", "コスト削減"],
            "store_operations": ["店舗効率", "人員最適化", "オペレーション改善"],
            "marketing": ["マーケティングROI", "顧客獲得", "ブランド認知", "プロモーション効果"]
        }
        return focus_map.get(format_type, ["売上向上", "顧客満足", "効率改善"])
    
    def _extract_retail_metrics(self, df: pd.DataFrame, format_type: str) -> List[str]:
        """Extract retail-specific metrics."""
        metrics = []
        columns = [str(col).lower() for col in df.columns]
        
        metric_patterns = {
            "revenue": ["売上", "revenue", "金額", "価格"],
            "quantity": ["数量", "quantity", "個数", "販売数"],
            "margin": ["利益", "margin", "粗利", "マージン"],
            "customer": ["顧客", "customer", "会員", "購入者"],
            "conversion": ["転換", "conversion", "購入率", "成約率"]
        }
        
        for metric_type, patterns in metric_patterns.items():
            if any(pattern in " ".join(columns) for pattern in patterns):
                metrics.append(metric_type)
        
        return metrics
    
    def _extract_product_categories(self, df: pd.DataFrame) -> List[str]:
        """Extract product category information."""
        categories = []
        for col in df.columns:
            col_str = str(col).lower()
            if any(keyword in col_str for keyword in ["カテゴリ", "category", "分類", "商品群"]):
                try:
                    categories.extend(df[col].dropna().unique().tolist()[:20])
                except Exception:
                    pass
        return list(set(categories))[:10]  # Limit to top 10
    
    def _extract_sales_channels(self, df: pd.DataFrame) -> List[str]:
        """Extract sales channel information."""
        channels = []
        for col in df.columns:
            col_str = str(col).lower()
            if any(keyword in col_str for keyword in ["チャネル", "channel", "店舗", "オンライン"]):
                try:
                    channels.extend(df[col].dropna().unique().tolist())
                except Exception:
                    pass
        return list(set(channels))[:5]  # Limit to top 5
    
    def _extract_geographic_info(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """Extract geographic dimension information."""
        geo_info: Dict[str, List[str]] = {
            "regions": [],
            "stores": [],
            "cities": []
        }
        
        for col in df.columns:
            col_str = str(col).lower()
            if "地域" in col_str or "region" in col_str:
                try:
                    geo_info["regions"].extend(df[col].dropna().unique().tolist()[:10])
                except Exception:
                    pass
            elif "店舗" in col_str or "store" in col_str:
                try:
                    geo_info["stores"].extend(df[col].dropna().unique().tolist()[:20])
                except Exception:
                    pass
        
        return geo_info
    
    def _standardize_monetary_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize monetary value columns."""
        for col in df.columns:
            col_str = str(col).lower()
            if any(keyword in col_str for keyword in ["金額", "価格", "売上", "revenue"]):
                try:
                    # Remove currency symbols and convert to numeric
                    df[col] = df[col].astype(str).str.replace('[円¥,]', '', regex=True)
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                except Exception as e:
                    logger.warning(f"Could not standardize monetary values in {col}: {e}")
        return df
    
    def _normalize_product_info(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize product information columns."""
        # Standardize product names and categories
        for col in df.columns:
            col_str = str(col).lower()
            if any(keyword in col_str for keyword in ["商品", "product", "アイテム"]):
                try:
                    # Basic normalization: strip whitespace, standardize case
                    df[col] = df[col].astype(str).str.strip().str.title()
                except Exception as e:
                    logger.warning(f"Could not normalize product info in {col}: {e}")
        return df
    
    def _enrich_sales_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add calculated fields for sales data."""
        # Calculate revenue if price and quantity are available
        price_cols = [col for col in df.columns if any(keyword in str(col).lower() 
                     for keyword in ["価格", "単価", "price"])]
        qty_cols = [col for col in df.columns if any(keyword in str(col).lower() 
                   for keyword in ["数量", "quantity", "個数"])]
        
        if price_cols and qty_cols:
            try:
                df["計算売上"] = df[price_cols[0]] * df[qty_cols[0]]
            except Exception as e:
                logger.warning(f"Could not calculate revenue: {e}")
        
        return df
    
    def _enrich_customer_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add calculated fields for customer data."""
        # Add customer value calculations if possible
        # This is a simplified implementation
        return df


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
    
    def detect_format_type(self, df: pd.DataFrame, sheet_name: str) -> Optional[str]:
        """Detect financial-specific Excel format types."""
        sheet_patterns = {
            "risk_management": ["リスク", "risk", "VaR", "credit", "信用"],
            "financial_analysis": ["財務", "financial", "損益", "P&L", "貸借"],
            "compliance": ["コンプライアンス", "compliance", "監査", "audit", "規制"],
            "investment": ["投資", "investment", "ポートフォリオ", "portfolio", "運用"],
            "cash_mgmt": ["資金", "cash", "流動性", "liquidity", "キャッシュフロー"]
        }
        
        sheet_lower = sheet_name.lower()
        for format_type, keywords in sheet_patterns.items():
            if any(keyword in sheet_lower for keyword in keywords):
                return format_type
        
        # Column analysis for financial data
        if df.empty:
            return None
            
        headers = [str(col).lower() for col in df.columns]
        header_text = " ".join(headers)
        
        # Risk management indicators
        risk_indicators = ["リスク", "risk", "exposure", "var", "信用", "デフォルト"]
        if sum(1 for indicator in risk_indicators if indicator in header_text) >= 2:
            return "risk_management"
        
        # Financial analysis indicators
        financial_indicators = ["財務", "損益", "profit", "loss", "資産", "負債"]
        if sum(1 for indicator in financial_indicators if indicator in header_text) >= 2:
            return "financial_analysis"
        
        return None
    
    def extract_industry_metadata(self, df: pd.DataFrame, format_type: str) -> Dict[str, Any]:
        """Extract financial-specific metadata."""
        metadata = {
            "industry": "financial",
            "format_type": format_type,
            "analysis_focus": self._get_financial_analysis_focus(format_type),
            "key_metrics": self._extract_financial_metrics(df, format_type),
            "risk_factors": self._extract_risk_factors(df),
            "regulatory_context": self._extract_regulatory_context(df, format_type),
            "time_horizons": self._extract_time_horizons(df)
        }
        
        return metadata
    
    def transform_data(self, df: pd.DataFrame, format_type: str) -> pd.DataFrame:
        """Transform financial data for optimal RAG processing."""
        transformed_df = df.copy()
        
        # Standardize financial values
        transformed_df = self._standardize_financial_values(transformed_df)
        
        # Add financial ratios and calculations
        if format_type == "financial_analysis":
            transformed_df = self._enrich_financial_analysis(transformed_df)
        elif format_type == "risk_management":
            transformed_df = self._enrich_risk_data(transformed_df)
        
        # Add financial context
        transformed_df["industry_domain"] = "financial"
        transformed_df["data_category"] = format_type
        
        return transformed_df
    
    def generate_analysis_queries(self, metadata: Dict[str, Any]) -> List[str]:
        """Generate financial-specific analysis queries."""
        format_type = metadata.get("format_type", "general")
        
        queries = {
            "risk_management": [
                "ポートフォリオのリスク集中度と分散効果は？",
                "市場リスクの主要要因と対策は？",
                "信用リスクの早期警戒指標は？",
                "VaRモデルの有効性と改善点は？",
                "リスク調整後リターンの最適化は？"
            ],
            "financial_analysis": [
                "収益性指標の業界比較と改善点は？",
                "キャッシュフロー分析と資金繰り予測は？",
                "財務レバレッジと資本効率の最適化は？",
                "投資効率とROI向上の施策は？",
                "コスト構造分析と削減ポテンシャルは？"
            ],
            "investment": [
                "ポートフォリオの最適配分と期待リターンは？",
                "投資パフォーマンスのベンチマーク比較は？",
                "リスク・リターン効率の改善は？",
                "資産クラス別の投資機会は？",
                "ESG投資の財務インパクトは？"
            ]
        }
        
        return queries.get(format_type, [
            "財務健全性の総合評価は？",
            "リスク管理体制の有効性は？",
            "投資戦略の最適化方向は？"
        ])
    
    def _get_financial_analysis_focus(self, format_type: str) -> List[str]:
        """Get financial analysis focus areas."""
        focus_map = {
            "risk_management": ["リスク評価", "リスク軽減", "VaR分析", "ストレステスト"],
            "financial_analysis": ["収益性分析", "流動性分析", "効率性分析", "安全性分析"],
            "compliance": ["規制遵守", "内部統制", "監査対応", "リスク管理"],
            "investment": ["ポートフォリオ最適化", "パフォーマンス分析", "リスク調整", "資産配分"],
            "cash_mgmt": ["流動性管理", "資金調達", "資金運用", "キャッシュフロー予測"]
        }
        return focus_map.get(format_type, ["財務分析", "リスク管理", "投資効率"])
    
    def _extract_financial_metrics(self, df: pd.DataFrame, format_type: str) -> List[str]:
        """Extract financial-specific metrics."""
        metrics = []
        columns = [str(col).lower() for col in df.columns]
        
        metric_patterns = {
            "profitability": ["利益", "profit", "収益", "revenue", "ROA", "ROE"],
            "liquidity": ["流動性", "liquidity", "現金", "cash", "短期"],
            "leverage": ["レバレッジ", "leverage", "負債", "debt", "資本"],
            "efficiency": ["効率", "efficiency", "回転", "turnover", "運用"],
            "risk": ["リスク", "risk", "VaR", "volatility", "標準偏差"]
        }
        
        for metric_type, patterns in metric_patterns.items():
            if any(pattern in " ".join(columns) for pattern in patterns):
                metrics.append(metric_type)
        
        return metrics
    
    def _extract_risk_factors(self, df: pd.DataFrame) -> List[str]:
        """Extract risk factor information."""
        risk_factors = []
        for col in df.columns:
            col_str = str(col).lower()
            if any(keyword in col_str for keyword in ["リスク", "risk", "損失", "loss"]):
                risk_factors.append(col)
        return risk_factors[:10]
    
    def _extract_regulatory_context(self, df: pd.DataFrame, format_type: str) -> Dict[str, Any]:
        """Extract regulatory context information."""
        return {
            "has_regulatory_data": format_type in ["compliance", "risk_management"],
            "regulatory_columns": [],
            "compliance_indicators": []
        }
    
    def _extract_time_horizons(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Extract time horizon information for financial analysis."""
        return {
            "short_term": False,
            "medium_term": False,
            "long_term": False,
            "time_series_available": False
        }
    
    def _standardize_financial_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize financial value columns."""
        for col in df.columns:
            col_str = str(col).lower()
            if any(keyword in col_str for keyword in ["金額", "価格", "価値", "value", "amount"]):
                try:
                    # Handle financial notation (thousands, millions, etc.)
                    df[col] = df[col].astype(str).str.replace('[円¥,$,%万億兆]', '', regex=True)
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                except Exception as e:
                    logger.warning(f"Could not standardize financial values in {col}: {e}")
        return df
    
    def _enrich_financial_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add calculated fields for financial analysis."""
        # Add financial ratios if possible
        # This would require more sophisticated analysis based on actual data structure
        return df
    
    def _enrich_risk_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add calculated fields for risk data."""
        # Add risk metrics and calculations
        return df


class IndustryHandlerManager:
    """Manager class for industry-specific Excel format handlers."""
    
    def __init__(self):
        """Initialize the industry handler manager."""
        self.handlers = {
            "manufacturing": ManufacturingHandler(),
            "retail": RetailHandler(), 
            "financial": FinancialHandler()
        }
        logger.info(f"Initialized industry handlers: {list(self.handlers.keys())}")
    
    def detect_industry_and_format(
        self, 
        df: pd.DataFrame, 
        sheet_name: str, 
        file_path: Optional[str] = None
    ) -> Tuple[Optional[str], Optional[str]]:
        """Detect industry and format type from Excel data.
        
        Args:
            df: DataFrame containing Excel data
            sheet_name: Name of the Excel sheet
            file_path: Optional path to the Excel file
            
        Returns:
            Tuple of (industry_name, format_type) or (None, None) if not detected
        """
        for industry_name, handler in self.handlers.items():
            format_type = handler.detect_format_type(df, sheet_name)
            if format_type:
                logger.info(f"Detected industry: {industry_name}, format: {format_type}")
                return industry_name, format_type
        
        logger.info("No specific industry format detected")
        return None, None
    
    def process_industry_data(
        self, 
        df: pd.DataFrame, 
        industry: str, 
        format_type: str
    ) -> Dict[str, Any]:
        """Process Excel data with industry-specific handler.
        
        Args:
            df: DataFrame containing Excel data
            industry: Industry name
            format_type: Format type within the industry
            
        Returns:
            Dictionary containing processed data and metadata
        """
        if industry not in self.handlers:
            raise ValueError(f"Unsupported industry: {industry}")
        
        handler = self.handlers[industry]
        
        # Extract industry-specific metadata
        metadata = handler.extract_industry_metadata(df, format_type)
        
        # Transform data for RAG processing
        transformed_data = handler.transform_data(df, format_type)
        
        # Generate analysis queries
        suggested_queries = handler.generate_analysis_queries(metadata)
        
        return {
            "industry": industry,
            "format_type": format_type,
            "metadata": metadata,
            "transformed_data": transformed_data,
            "suggested_queries": suggested_queries,
            "original_data": df
        }
    
    def get_available_industries(self) -> List[str]:
        """Get list of available industry handlers."""
        return list(self.handlers.keys())
    
    def get_industry_formats(self, industry: str) -> List[str]:
        """Get available format types for a specific industry.
        
        Args:
            industry: Industry name
            
        Returns:
            List of available format types
        """
        if industry not in self.handlers:
            return []
        
        # This would return format types supported by the handler
        # For now, return some common ones
        format_map = {
            "manufacturing": ["production_plan", "quality_control", "equipment_mgmt", 
                            "process_control", "inventory_mgmt"],
            "retail": ["sales_performance", "inventory", "customer_analysis", 
                      "store_operations", "marketing"],
            "financial": ["risk_management", "financial_analysis", "compliance", 
                         "investment", "cash_mgmt"]
        }
        
        return format_map.get(industry, [])