"""Numerical analytics module for advanced statistical analysis.

Provides sophisticated numerical statistical analysis capabilities including
distribution analysis, outlier detection, and comprehensive statistical measures
with Japanese language optimization for financial and business data.

Features:
- Advanced numerical distribution analysis
- Outlier detection using IQR method
- Skewness and kurtosis calculation
- Distribution type classification
- Temporal data statistical analysis
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass
class NumericalStats:
    """Comprehensive statistical analysis results for numerical data.

    Attributes:
        mean: Arithmetic mean of the values.
        median: Middle value when sorted.
        std_dev: Standard deviation.
        min_value: Minimum value in dataset.
        max_value: Maximum value in dataset.
        quartiles: Q1, Q2, Q3 quartile values.
        outliers: Values identified as outliers.
        distribution_type: Statistical distribution type.
        skewness: Measure of asymmetry.
        kurtosis: Measure of tail heaviness.
    """

    mean: float
    median: float
    std_dev: float
    min_value: float
    max_value: float
    quartiles: tuple[float, float, float]
    outliers: list[float]
    distribution_type: str
    skewness: float
    kurtosis: float


@dataclass
class TemporalStats:
    """Statistical analysis results for temporal data with trend detection.

    Attributes:
        time_range: Start and end time range.
        duration: Total duration of the time series.
        frequency_pattern: Detected frequency pattern.
        seasonal_indicators: Seasonal pattern indicators.
        trend_direction: Overall trend direction.
    """

    time_range: tuple[str, str]
    duration: str
    frequency_pattern: str
    seasonal_indicators: dict[str, Any]
    trend_direction: str


class StatisticalAnalyzer:
    """Advanced statistical analysis processor for numerical data analysis.

    Provides sophisticated statistical analysis capabilities including numerical
    distribution analysis, outlier identification, and comprehensive statistical
    measures with optimized performance for Japanese business data.
    """

    def analyze_numerical_data(self, data: list[float]) -> NumericalStats:
        """Perform comprehensive statistical analysis on numerical data.

        Args:
            data: List of numerical values to analyze.

        Returns:
            NumericalStats containing detailed statistical analysis results.
        """
        if not data:
            return self._empty_numerical_stats()

        # 基本統計量
        mean_val = statistics.mean(data)
        median_val = statistics.median(data)
        try:
            std_dev = statistics.stdev(data) if len(data) > 1 else 0.0
        except statistics.StatisticsError:
            std_dev = 0.0

        min_val = min(data)
        max_val = max(data)

        # 四分位数
        q1 = np.percentile(data, 25)
        q2 = median_val
        q3 = np.percentile(data, 75)

        # 外れ値検出 (IQR method)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outliers = [x for x in data if x < lower_bound or x > upper_bound]

        # 分布の形状
        skewness = self._calculate_skewness(data, mean_val, std_dev)
        kurtosis = self._calculate_kurtosis(data, mean_val, std_dev)
        distribution_type = self._classify_distribution(skewness, kurtosis)

        return NumericalStats(
            mean=mean_val,
            median=median_val,
            std_dev=std_dev,
            min_value=min_val,
            max_value=max_val,
            quartiles=(float(q1), float(q2), float(q3)),
            outliers=outliers,
            distribution_type=distribution_type,
            skewness=skewness,
            kurtosis=kurtosis,
        )

    def _calculate_skewness(
        self, data: list[float], mean: float, std_dev: float
    ) -> float:
        """歪度の計算"""
        if std_dev == 0:
            return 0.0
        n = len(data)
        if n < 3:  # 歪度計算には最低3つのデータポイントが必要
            return 0.0
        try:
            return (n / ((n - 1) * (n - 2))) * sum(
                ((x - mean) / std_dev) ** 3 for x in data
            )
        except ZeroDivisionError:
            return 0.0

    def _calculate_kurtosis(
        self, data: list[float], mean: float, std_dev: float
    ) -> float:
        """尖度の計算"""
        if std_dev == 0:
            return 0.0
        n = len(data)
        if n < 4:  # Kurtosis calculation requires at least 4 data points
            return 0.0
        try:
            return (n * (n + 1) / ((n - 1) * (n - 2) * (n - 3))) * sum(
                ((x - mean) / std_dev) ** 4 for x in data
            ) - (3 * (n - 1) ** 2 / ((n - 2) * (n - 3)))
        except ZeroDivisionError:
            return 0.0

    def _classify_distribution(self, skewness: float, kurtosis: float) -> str:
        """
        Classify distribution type based on skewness and kurtosis values.

        Args:
            skewness: Skewness value of the distribution.
            kurtosis: Kurtosis value of the distribution.

        Returns:
            String classification of distribution type.
        """
        if abs(skewness) < 0.5 and abs(kurtosis) < 3:
            return "normal"
        elif skewness > 1:
            return "right_skewed"
        elif skewness < -1:
            return "left_skewed"
        elif kurtosis > 3:
            return "leptokurtic"
        elif kurtosis < 3:
            return "platykurtic"
        else:
            return "unknown"

    def _empty_numerical_stats(self) -> NumericalStats:
        """
        Create empty numerical statistics structure.

        Returns:
            NumericalStats with zero/empty values for empty datasets.
        """
        return NumericalStats(
            mean=0.0,
            median=0.0,
            std_dev=0.0,
            min_value=0.0,
            max_value=0.0,
            quartiles=(0.0, 0.0, 0.0),
            outliers=[],
            distribution_type="empty",
            skewness=0.0,
            kurtosis=0.0,
        )
