"""Excel-RAG integration package for sphinxcontrib-jsontable.

This package provides comprehensive Excel file integration with RAG (Retrieval
Augmented Generation) systems, enabling 5-minute transformation of Excel data
into AI-ready documentation and query systems.

Key Features:
- Automatic Excel format detection (pivot tables, financial statements, multi-headers)
- Intelligent Excel-to-JSON conversion with business entity recognition
- Seamless RAG system integration (OpenAI, LangChain, custom systems)
- Industry-specific optimizations (manufacturing, retail, finance)
- Japanese language entity recognition and processing
- Automatic Sphinx documentation generation

Main Classes:
- ExcelRAGConverter: Core Excel-to-RAG conversion engine
- AdvancedExcelConverter: Format-aware Excel processing
- AutoSphinxIntegration: Automatic documentation generation
- ExcelFormatHandler: Multi-format Excel support
"""

from __future__ import annotations

__version__ = "0.3.0"

# Core exports
from .converter import ExcelRAGConverter, convert_excel_to_rag, query_excel_data
from .federation import (
    CrossDepartmentRelationship,
    DepartmentConfig,
    ExcelRAGFederation,
    create_enterprise_federation,
    setup_cross_department_relationships,
)
from .format_detector import AdvancedExcelConverter, ExcelFormatHandler
from .industry_handlers import (
    FinancialHandler,
    IndustryHandlerManager,
    ManufacturingHandler,
    RetailHandler,
)
from .monitoring import (
    ExcelFileChangeEvent,
    ExcelRAGMonitor,
    UpdatePolicy,
    monitor_department_files,
    setup_enterprise_monitoring,
)
from .sphinx_integration import AutoSphinxIntegration

__all__ = [
    "AdvancedExcelConverter",
    "AutoSphinxIntegration",
    "CrossDepartmentRelationship",
    "DepartmentConfig",
    "ExcelFileChangeEvent",
    "ExcelFormatHandler",
    # Main conversion classes
    "ExcelRAGConverter",
    # Enterprise federation
    "ExcelRAGFederation",
    # Real-time monitoring
    "ExcelRAGMonitor",
    "FinancialHandler",
    # Industry-specific handlers
    "IndustryHandlerManager",
    "ManufacturingHandler",
    "RetailHandler",
    "UpdatePolicy",
    # Convenience functions
    "convert_excel_to_rag",
    "create_enterprise_federation",
    "monitor_department_files",
    "query_excel_data",
    "setup_cross_department_relationships",
    "setup_enterprise_monitoring",
]
