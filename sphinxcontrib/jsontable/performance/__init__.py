"""Performance optimization package for single-pass processing design.

This package contains optimized components for single-pass processing
architecture and performance improvements.
"""

from .single_pass_processor import (
    DataFlowOptimizationResult,
    OverallDesignEffectiveness,
    PerformanceComparisonResult,
    ProcessingStageMetrics,
    SinglePassDesignMetrics,
    SinglePassProcessingResult,
    SinglePassProcessor,
    UnifiedProcessingPipeline,
)

__all__ = [
    "SinglePassProcessor",
    "SinglePassProcessingResult",
    "SinglePassDesignMetrics",
    "ProcessingStageMetrics",
    "UnifiedProcessingPipeline",
    "DataFlowOptimizationResult",
    "PerformanceComparisonResult",
    "OverallDesignEffectiveness",
]
