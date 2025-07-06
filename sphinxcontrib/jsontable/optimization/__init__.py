"""Optimization package for performance improvements.

This package contains optimized components for various performance
bottlenecks identified in the sphinxcontrib-jsontable processing pipeline.
"""

from .optimized_header_processor import (
    BenchmarkComparisonResult,
    DuplicationEliminationMetrics,
    HeaderProcessingResult,
    LinearScalabilityTestResult,
    MemoryOptimizationResult,
    OptimizedHeaderProcessor,
    SinglePassHeaderResult,
)

__all__ = [
    "OptimizedHeaderProcessor",
    "HeaderProcessingResult",
    "DuplicationEliminationMetrics",
    "SinglePassHeaderResult",
    "MemoryOptimizationResult",
    "BenchmarkComparisonResult",
    "LinearScalabilityTestResult",
]
