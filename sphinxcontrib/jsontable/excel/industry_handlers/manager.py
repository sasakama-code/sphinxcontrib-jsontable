"""Industry handler manager for coordinating industry-specific Excel processing.

This module provides the central management system for coordinating different
industry-specific handlers, automatically detecting the appropriate handler
for given Excel data, and orchestrating the processing workflow.

Features:
- Automatic industry and format detection
- Handler lifecycle management
- Unified processing interface
- Industry capability discovery
- Format compatibility checking
"""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd

from .manufacturing import ManufacturingHandler
from .retail import RetailHandler
from .financial import FinancialHandler

logger = logging.getLogger(__name__)


class IndustryHandlerManager:
    """Manager for coordinating industry-specific Excel format handlers.
    
    This class provides a unified interface for processing Excel data across
    different industries, automatically detecting the appropriate handler
    and format type for optimal data processing and analysis.
    """

    def __init__(self):
        """Initialize the industry handler manager with all available handlers."""
        self.handlers = {
            "manufacturing": ManufacturingHandler(),
            "retail": RetailHandler(),
            "financial": FinancialHandler(),
        }
        logger.info(f"Initialized IndustryHandlerManager with {len(self.handlers)} handlers")

    def detect_industry_and_format(
        self, df: pd.DataFrame, sheet_name: str, file_path: str | None = None
    ) -> tuple[str | None, str | None]:
        """Detect the most appropriate industry and format type for the data.
        
        Args:
            df: DataFrame containing Excel data
            sheet_name: Name of the Excel sheet
            file_path: Optional file path for additional context
            
        Returns:
            Tuple of (industry, format_type) or (None, None) if not detected
        """
        detection_results = []
        
        for industry_name, handler in self.handlers.items():
            try:
                format_type = handler.detect_format_type(df, sheet_name)
                if format_type:
                    detection_results.append((industry_name, format_type))
                    logger.info(
                        f"Handler {industry_name} detected format: {format_type}"
                    )
            except Exception as e:
                logger.warning(
                    f"Error in {industry_name} handler detection: {e}"
                )
                continue
        
        if not detection_results:
            logger.info("No industry handler could detect the format")
            return None, None
        
        # Return the first successful detection
        # In future versions, could implement confidence scoring
        industry, format_type = detection_results[0]
        logger.info(f"Selected industry: {industry}, format: {format_type}")
        
        return industry, format_type

    def process_industry_data(
        self, df: pd.DataFrame, industry: str, format_type: str
    ) -> dict[str, Any]:
        """Process data using the specified industry handler.
        
        Args:
            df: DataFrame containing Excel data
            industry: Industry type (manufacturing, retail, financial)
            format_type: Specific format type within the industry
            
        Returns:
            Dictionary containing processed data and metadata
        """
        if industry not in self.handlers:
            raise ValueError(f"Unknown industry: {industry}")
        
        handler = self.handlers[industry]
        
        try:
            # Extract industry-specific metadata
            metadata = handler.extract_industry_metadata(df, format_type)
            
            # Transform data for optimal processing
            transformed_data = handler.transform_data(df, format_type)
            
            # Generate analysis queries
            suggested_queries = handler.generate_analysis_queries(metadata)
            
            result = {
                "industry": industry,
                "format_type": format_type,
                "metadata": metadata,
                "transformed_data": transformed_data,
                "suggested_queries": suggested_queries,
                "processing_timestamp": pd.Timestamp.now().isoformat(),
                "data_shape": {
                    "rows": len(transformed_data),
                    "columns": len(transformed_data.columns),
                },
            }
            
            logger.info(
                f"Successfully processed {industry} data with format {format_type}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing {industry} data: {e}")
            raise

    def get_available_industries(self) -> list[str]:
        """Get list of available industry handlers.
        
        Returns:
            List of available industry names
        """
        return list(self.handlers.keys())

    def get_industry_formats(self, industry: str) -> dict[str, Any]:
        """Get supported formats and capabilities for a specific industry.
        
        Args:
            industry: Industry name
            
        Returns:
            Dictionary containing industry capabilities and supported formats
        """
        if industry not in self.handlers:
            return {"error": f"Unknown industry: {industry}"}
        
        handler = self.handlers[industry]
        
        # Extract format information from handler
        capabilities = {
            "industry_name": industry,
            "handler_class": handler.__class__.__name__,
            "domain_keywords": handler.domain_keywords,
            "supported_formats": [],
            "analysis_capabilities": [],
        }
        
        # Add format-specific information based on industry
        if industry == "manufacturing":
            capabilities["supported_formats"] = [
                "production_plan",
                "quality_control", 
                "equipment_mgmt",
                "process_control",
                "inventory_mgmt"
            ]
            capabilities["analysis_capabilities"] = [
                "生産効率分析",
                "品質管理分析", 
                "設備稼働分析",
                "工程最適化",
                "在庫最適化"
            ]
        elif industry == "retail":
            capabilities["supported_formats"] = [
                "sales_performance",
                "inventory",
                "customer_analysis", 
                "store_operations",
                "marketing"
            ]
            capabilities["analysis_capabilities"] = [
                "売上分析",
                "在庫分析",
                "顧客分析",
                "店舗運営分析",
                "マーケティング分析"
            ]
        elif industry == "financial":
            capabilities["supported_formats"] = [
                "risk_management",
                "financial_analysis",
                "compliance",
                "investment",
                "cash_mgmt"
            ]
            capabilities["analysis_capabilities"] = [
                "リスク分析",
                "財務分析",
                "コンプライアンス分析",
                "投資分析",
                "資金管理分析"
            ]
        
        return capabilities

    def get_handler_statistics(self) -> dict[str, Any]:
        """Get statistics about handler usage and capabilities.
        
        Returns:
            Dictionary containing handler statistics
        """
        stats = {
            "total_handlers": len(self.handlers),
            "handler_details": {},
            "total_supported_formats": 0,
        }
        
        for industry, handler in self.handlers.items():
            formats = self.get_industry_formats(industry)["supported_formats"]
            stats["handler_details"][industry] = {
                "handler_class": handler.__class__.__name__,
                "format_count": len(formats),
                "formats": formats,
            }
            stats["total_supported_formats"] += len(formats)
        
        return stats