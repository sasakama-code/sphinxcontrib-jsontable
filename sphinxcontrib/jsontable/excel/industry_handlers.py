"""Industry-specific Excel format handlers for specialized business data processing.

This module provides the main manager class for industry-specific Excel format handlers.
The actual handler implementations are located in the industry_handlers/ subdirectory
for better modularity and maintainability.

Key Features:
- Centralized industry detection and routing
- Modular handler architecture  
- Unified interface for all industry formats
- Japanese business document structure understanding
- Automated metadata enrichment for domain analysis

Supported Industries:
- 製造業 (Manufacturing): 生産管理、品質管理、設備管理
- 小売業 (Retail): 販売実績、在庫管理、顧客分析  
- 金融業 (Financial): リスク管理、財務分析、コンプライアンス
"""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd

# Import handlers from modular structure
from .industry_handlers.manufacturing import ManufacturingHandler
from .industry_handlers.retail import RetailHandler
from .industry_handlers.financial import FinancialHandler

logger = logging.getLogger(__name__)


class IndustryHandlerManager:
    """Manager class for industry-specific Excel format handlers."""

    def __init__(self):
        """Initialize the industry handler manager."""
        self.handlers = {
            "manufacturing": ManufacturingHandler(),
            "retail": RetailHandler(),
            "financial": FinancialHandler(),
        }
        logger.info(f"Initialized industry handlers: {list(self.handlers.keys())}")

    def detect_industry_and_format(
        self, df: pd.DataFrame, sheet_name: str, file_path: str | None = None
    ) -> tuple[str | None, str | None]:
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
                logger.info(
                    f"Detected industry: {industry_name}, format: {format_type}"
                )
                return industry_name, format_type

        logger.info("No specific industry format detected")
        return None, None

    def process_industry_data(
        self, df: pd.DataFrame, industry: str, format_type: str
    ) -> dict[str, Any]:
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
            "original_data": df,
        }

    def get_available_industries(self) -> list[str]:
        """Get list of available industry handlers."""
        return list(self.handlers.keys())

    def get_industry_formats(self, industry: str) -> list[str]:
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
            "manufacturing": [
                "production_plan",
                "quality_control",
                "equipment_mgmt",
                "process_control",
                "inventory_mgmt",
            ],
            "retail": [
                "sales_performance",
                "inventory",
                "customer_analysis",
                "store_operations",
                "marketing",
            ],
            "financial": [
                "risk_management",
                "financial_analysis",
                "compliance",
                "investment",
                "cash_mgmt",
            ],
        }

        return format_map.get(industry, [])
