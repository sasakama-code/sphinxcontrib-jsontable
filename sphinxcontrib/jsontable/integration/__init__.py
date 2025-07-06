"""Integration package for unified processing components.

This package contains unified components that integrate multiple
pipeline processing modules to eliminate duplication and improve efficiency.
"""

from .pipeline_performance_analyzer import (
    PipelinePerformanceAnalyzer,
    PerformanceComparisonResult,
    ProcessingStageComparison,
    MemoryUsageComparison,
    DuplicationEliminationReport,
    IntegratedPipelineMetrics,
    ComprehensivePerformanceReport,
)

from .unified_data_conversion import (
    UnifiedDataConversionEngine,
    ConversionOptimizationResult,
    UnifiedConversionResult,
)

from .unified_error_handler import (
    UnifiedPipelineErrorHandler,
    PipelineErrorClassification,
    UnifiedErrorMonitor,
)

from .pipeline_regression_validator import (
    PipelineRegressionValidator,
    RegressionTestResult,
    FunctionalityComparisonResult,
    BackwardCompatibilityVerification,
    OutputConsistencyAnalysis,
    ErrorHandlingConsistencyCheck,
    EdgeCasePreservationVerification,
    PerformanceRegressionCheck,
    ComprehensiveRegressionReport,
)