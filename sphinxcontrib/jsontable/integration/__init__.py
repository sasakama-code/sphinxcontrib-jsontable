"""Integration package for unified processing components.

This package contains unified components that integrate multiple
pipeline processing modules to eliminate duplication and improve efficiency.
"""

from .pipeline_performance_analyzer import (
    ComprehensivePerformanceReport,
    DuplicationEliminationReport,
    IntegratedPipelineMetrics,
    MemoryUsageComparison,
    PerformanceComparisonResult,
    PipelinePerformanceAnalyzer,
    ProcessingStageComparison,
)
from .pipeline_regression_validator import (
    BackwardCompatibilityVerification,
    ComprehensiveRegressionReport,
    EdgeCasePreservationVerification,
    ErrorHandlingConsistencyCheck,
    FunctionalityComparisonResult,
    OutputConsistencyAnalysis,
    PerformanceRegressionCheck,
    PipelineRegressionValidator,
    RegressionTestResult,
)
from .unified_data_conversion import (
    ConversionOptimizationResult,
    UnifiedConversionResult,
    UnifiedDataConversionEngine,
)
from .unified_error_handler import (
    PipelineErrorClassification,
    UnifiedErrorMonitor,
    UnifiedPipelineErrorHandler,
)

__all__ = [
    # Pipeline Performance Analyzer
    "ComprehensivePerformanceReport",
    "DuplicationEliminationReport", 
    "IntegratedPipelineMetrics",
    "MemoryUsageComparison",
    "PerformanceComparisonResult",
    "PipelinePerformanceAnalyzer",
    "ProcessingStageComparison",
    # Pipeline Regression Validator
    "BackwardCompatibilityVerification",
    "ComprehensiveRegressionReport",
    "EdgeCasePreservationVerification",
    "ErrorHandlingConsistencyCheck",
    "FunctionalityComparisonResult",
    "OutputConsistencyAnalysis",
    "PerformanceRegressionCheck",
    "PipelineRegressionValidator",
    "RegressionTestResult",
    # Unified Data Conversion
    "ConversionOptimizationResult",
    "UnifiedConversionResult",
    "UnifiedDataConversionEngine",
    # Unified Error Handler
    "PipelineErrorClassification",
    "UnifiedErrorMonitor",
    "UnifiedPipelineErrorHandler",
]
