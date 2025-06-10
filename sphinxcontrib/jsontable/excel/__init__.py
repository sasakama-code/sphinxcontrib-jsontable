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
from .format_detector import AdvancedExcelConverter, ExcelFormatHandler
from .industry_handlers import (
    IndustryHandlerManager,
    ManufacturingHandler, 
    RetailHandler,
    FinancialHandler
)
from .sphinx_integration import AutoSphinxIntegration
from .federation import (
    ExcelRAGFederation,
    DepartmentConfig,
    CrossDepartmentRelationship,
    create_enterprise_federation,
    setup_cross_department_relationships
)
from .monitoring import (
    ExcelRAGMonitor,
    ExcelFileChangeEvent,
    UpdatePolicy,
    setup_enterprise_monitoring,
    monitor_department_files
)

__all__ = [
    # Main conversion classes
    "ExcelRAGConverter", 
    "AdvancedExcelConverter",
    "ExcelFormatHandler",
    "AutoSphinxIntegration",
    
    # Industry-specific handlers
    "IndustryHandlerManager",
    "ManufacturingHandler",
    "RetailHandler", 
    "FinancialHandler",
    
    # Enterprise federation
    "ExcelRAGFederation",
    "DepartmentConfig",
    "CrossDepartmentRelationship",
    
    # Real-time monitoring
    "ExcelRAGMonitor",
    "ExcelFileChangeEvent",
    "UpdatePolicy",
    
    # Convenience functions
    "convert_excel_to_rag",
    "query_excel_data",
    "create_enterprise_federation",
    "setup_cross_department_relationships",
    "setup_enterprise_monitoring",
    "monitor_department_files",
]