"""Base class for industry-specific Excel format handlers.

This module provides the abstract base class that defines the interface for all
industry-specific Excel format handlers. Each industry handler must implement
the required methods for detecting format types, extracting metadata, transforming
data, and generating analysis queries.

Key Features:
- Abstract base class with standardized interface
- Domain keyword and entity pattern loading
- Industry-specific metadata extraction framework
- Data transformation pipeline for RAG processing
- Analysis query generation for domain expertise
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import Any

import pandas as pd


class IndustryHandlerBase(ABC):
    """Base class for industry-specific Excel format handlers."""

    def __init__(self, industry_name: str):
        """Initialize industry handler.

        Args:
            industry_name: Name of the industry (e.g., 'manufacturing', 'retail', 'financial')
        """
        self.industry_name = industry_name
        self.domain_keywords = self._load_domain_keywords()
        self.entity_patterns = self._load_entity_patterns()

    @abstractmethod
    def detect_format_type(self, df: pd.DataFrame, sheet_name: str) -> str | None:
        """Detect specific format type within the industry.

        Args:
            df: DataFrame containing Excel data
            sheet_name: Name of the Excel sheet

        Returns:
            Format type string or None if not detected
        """

    @abstractmethod
    def extract_industry_metadata(
        self, df: pd.DataFrame, format_type: str
    ) -> dict[str, Any]:
        """Extract industry-specific metadata from the data.

        Args:
            df: DataFrame containing Excel data
            format_type: Detected format type

        Returns:
            Dictionary containing industry-specific metadata
        """

    @abstractmethod
    def transform_data(self, df: pd.DataFrame, format_type: str) -> pd.DataFrame:
        """Transform data according to industry standards.

        Args:
            df: Original DataFrame
            format_type: Detected format type

        Returns:
            Transformed DataFrame optimized for RAG processing
        """

    @abstractmethod
    def generate_analysis_queries(self, metadata: dict[str, Any]) -> list[str]:
        """Generate industry-specific analysis query suggestions.

        Args:
            metadata: Industry-specific metadata

        Returns:
            List of suggested queries for this industry domain
        """

    def _load_domain_keywords(self) -> dict[str, list[str]]:
        """Load domain-specific keywords for content detection."""
        # Base implementation - to be overridden by specific handlers
        return {"general": ["データ", "分析", "レポート", "管理", "システム"]}

    def _load_entity_patterns(self) -> dict[str, re.Pattern]:
        """Load regex patterns for industry-specific entity recognition."""
        # Base implementation - to be overridden by specific handlers
        return {
            "japanese_date": re.compile(r"\d{4}年\d{1,2}月\d{1,2}日"),
            "japanese_number": re.compile(r"[\d,]+(?:\.\d+)?[万億兆]?[円個台件]?"),
        }