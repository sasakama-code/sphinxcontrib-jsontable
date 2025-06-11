"""Categorical analytics module for advanced pattern analysis.

Provides sophisticated categorical data analysis capabilities including pattern
detection, entropy calculation, diversity assessment, and Japanese language
pattern recognition for business and enterprise data.

Features:
- Categorical data pattern detection
- Shannon entropy calculation
- Simpson diversity index analysis
- Japanese business pattern recognition
- Value frequency analysis
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass
class CategoricalStats:
    """Statistical analysis results for categorical data with pattern detection.

    Attributes:
        unique_count: Number of unique values.
        value_counts: Frequency count for each value.
        entropy: Shannon entropy measure.
        diversity_index: Simpson diversity index.
        most_common: Most frequently occurring values.
        patterns: Detected patterns in the data.
    """

    unique_count: int
    value_counts: dict[str, int]
    entropy: float
    diversity_index: float
    most_common: list[tuple[str, int]]
    patterns: list[str]


class CategoricalAnalyzer:
    """Advanced categorical data analysis processor.

    Provides sophisticated categorical analysis capabilities including pattern
    detection, entropy calculation, and diversity assessment with specialized
    recognition for Japanese business patterns and data structures.
    """

    def analyze_categorical_data(self, data: list[str]) -> CategoricalStats:
        """カテゴリデータの詳細分析"""
        if not data:
            return self._empty_categorical_stats()

        # 頻度計算
        value_counts = Counter(data)
        unique_count = len(value_counts)

        # エントロピー計算
        total = len(data)
        entropy = -sum(
            (count / total) * np.log2(count / total) for count in value_counts.values()
        )

        # 多様性指数 (Simpson's Diversity Index)
        diversity_index = 1 - sum(
            (count / total) ** 2 for count in value_counts.values()
        )

        # 最頻値
        most_common = value_counts.most_common(10)

        # パターン検出
        patterns = self._detect_categorical_patterns(data)

        return CategoricalStats(
            unique_count=unique_count,
            value_counts=dict(value_counts),
            entropy=entropy,
            diversity_index=diversity_index,
            most_common=most_common,
            patterns=patterns,
        )

    def _detect_categorical_patterns(self, data: list[str]) -> list[str]:
        """
        Detect common patterns in categorical data.

        Args:
            data: List of categorical string values to analyze.

        Returns:
            List of detected pattern types found in the data.
        """
        patterns = []

        # Detect common patterns
        if any("株式会社" in item for item in data):
            patterns.append("company_names")
        if any(re.match(r"[一-龯]{1,4}[一-龯]{1,3}", item) for item in data):
            patterns.append("japanese_names")
        if any(re.match(r"\d{4}-\d{2}-\d{2}", item) for item in data):
            patterns.append("date_format")
        if any("@" in item for item in data):
            patterns.append("email_addresses")

        return patterns

    def _empty_categorical_stats(self) -> CategoricalStats:
        """
        Create empty categorical statistics structure.

        Returns:
            CategoricalStats with zero/empty values for empty datasets.
        """
        return CategoricalStats(
            unique_count=0,
            value_counts={},
            entropy=0.0,
            diversity_index=0.0,
            most_common=[],
            patterns=[],
        )
