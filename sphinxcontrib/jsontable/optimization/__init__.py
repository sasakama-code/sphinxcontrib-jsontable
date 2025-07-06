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
from .duplicate_detector_optimized import (
    DuplicateDetectorOptimized,
    DuplicateDetectionResult,
    HashTableMetrics,
    OptimizationMetrics,
)
from .range_parser_optimized import (
    RangeParserOptimized,
    RangeParsingResult,
    CacheMetrics,
    RegexOptimizationMetrics,
    PerformanceMetrics,
)

__all__ = [
    "OptimizedHeaderProcessor",
    "HeaderProcessingResult",
    "DuplicationEliminationMetrics",
    "SinglePassHeaderResult",
    "MemoryOptimizationResult",
    "BenchmarkComparisonResult",
    "LinearScalabilityTestResult",
    "DuplicateDetectorOptimized",
    "DuplicateDetectionResult",
    "HashTableMetrics",
    "OptimizationMetrics",
    "RangeParserOptimized",
    "RangeParsingResult",
    "CacheMetrics",
    "RegexOptimizationMetrics",
    "PerformanceMetrics",
]
