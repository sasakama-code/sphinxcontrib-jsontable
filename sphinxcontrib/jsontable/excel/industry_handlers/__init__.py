"""Industry-specific Excel format handlers package.

This package provides specialized handlers for processing Excel data from
different industry domains, including manufacturing, retail, and financial
sectors. Each handler implements domain-specific data extraction, transformation,
and analysis patterns optimized for Japanese business environments.

Key Components:
- IndustryHandlerManager: Central coordination for all handlers
- ManufacturingHandler: Production, quality, and equipment management
- RetailHandler: Sales, inventory, and customer analysis
- FinancialHandler: Risk, compliance, and investment analysis
- IndustryHandlerBase: Abstract base class for all handlers

Usage:
    from sphinxcontrib.jsontable.excel.industry_handlers import IndustryHandlerManager

    manager = IndustryHandlerManager()
    industry, format_type = manager.detect_industry_and_format(df, sheet_name)
    result = manager.process_industry_data(df, industry, format_type)
"""

from .base import IndustryHandlerBase
from .manufacturing import ManufacturingHandler
from .retail import RetailHandler
from .financial import FinancialHandler
from .manager import IndustryHandlerManager

__all__ = [
    "IndustryHandlerManager",
    "IndustryHandlerBase",
    "ManufacturingHandler",
    "RetailHandler",
    "FinancialHandler",
]

# Version information
__version__ = "0.3.0"
__author__ = "sphinxcontrib-jsontable development team"
__description__ = "Industry-specific Excel format handlers for Japanese business data"
