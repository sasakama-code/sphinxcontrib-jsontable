"""Data Converter for Excel data processing.

Extracted from monolithic ExcelDataLoader to provide focused,
testable data conversion functionality with single responsibility.
"""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import pandas as pd

from ..errors.excel_errors import DataConversionError


@dataclass
class ConversionResult:
    """Structured result of data conversion operations."""

    data: List[List[Any]]
    has_header: bool
    headers: List[str]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "data": self.data,
            "has_header": self.has_header,
            "headers": self.headers,
            "metadata": self.metadata,
            "rows": len(self.data),
            "columns": len(self.data[0]) if self.data else 0,
        }


@dataclass
class HeaderDetectionResult:
    """Result of header detection analysis."""

    has_header: bool
    confidence: float
    headers: List[str]
    analysis: Dict[str, Any]


class IDataConverter(ABC):
    """Abstract interface for data conversion functionality."""

    @abstractmethod
    def convert_dataframe_to_json(
        self, df: pd.DataFrame, has_header: bool = True
    ) -> ConversionResult:
        """Convert pandas DataFrame to JSON-compatible structure.

        Args:
            df: Pandas DataFrame to convert
            has_header: Whether DataFrame has header row

        Returns:
            ConversionResult: Structured conversion result

        Raises:
            DataConversionError: If conversion fails
        """
        pass

    @abstractmethod
    def detect_header(self, df: pd.DataFrame) -> HeaderDetectionResult:
        """Detect whether DataFrame has a header row.

        Args:
            df: Pandas DataFrame to analyze

        Returns:
            HeaderDetectionResult: Detection result with confidence
        """
        pass

    @abstractmethod
    def normalize_headers(
        self, headers: List[str], japanese_support: bool = True
    ) -> List[str]:
        """Normalize header names for consistency.

        Args:
            headers: List of raw header names
            japanese_support: Enable Japanese character processing

        Returns:
            List[str]: Normalized header names
        """
        pass


class DataConverter(IDataConverter):
    """Production implementation of data conversion functionality.

    Implements data conversion logic extracted from excel_data_loader.py
    lines 660-689 (data_type_conversion), 565-659 (header_detection),
    and related header normalization methods.
    """

    def __init__(
        self,
        empty_string_replacement: str = "",
        preserve_numeric_types: bool = True,
        header_keywords: Optional[List[str]] = None,
    ):
        """Initialize data converter with configuration.

        Args:
            empty_string_replacement: String to replace empty/NaN values
            preserve_numeric_types: Whether to preserve numeric type info
            header_keywords: Keywords that indicate header presence
        """
        self.empty_string_replacement = empty_string_replacement
        self.preserve_numeric_types = preserve_numeric_types
        self.header_keywords = header_keywords or [
            "名前",
            "name",
            "氏名",
            "項目",
            "item",
            "title",
            "タイトル",
            "id",
            "識別子",
            "番号",
            "no",
            "number",
            "date",
            "日付",
            "時間",
            "time",
        ]

        # Japanese character mappings for header normalization
        self._japanese_char_map = {
            "（": "_",
            "）": "_",
            "［": "_",
            "］": "_",
            "【": "_",
            "】": "_",
            "〈": "_",
            "〉": "_",
            "《": "_",
            "》": "_",
            "「": "_",
            "」": "_",
            "『": "_",
            "』": "_",
        }

    def convert_dataframe_to_json(
        self, df: pd.DataFrame, has_header: bool = True
    ) -> ConversionResult:
        """Convert pandas DataFrame to JSON-compatible structure.

        Implements the logic from excel_data_loader.py lines 660-689.
        """
        try:
            # Extract headers if present
            if has_header and not df.empty:
                headers = [str(col) for col in df.columns]
                data_df = df
            else:
                headers = [f"Column_{i + 1}" for i in range(len(df.columns))]
                data_df = df

            # Convert DataFrame to 2D array with proper type handling
            data_array = self._convert_dataframe_values(data_df)

            # Normalize headers if needed
            if has_header:
                headers = self.normalize_headers(headers)

            # Build metadata
            metadata = {
                "conversion_type": "dataframe_to_json",
                "preserve_numeric_types": self.preserve_numeric_types,
                "empty_replacement": self.empty_string_replacement,
                "original_columns": len(df.columns),
                "original_rows": len(df),
                "processed_rows": len(data_array),
            }

            return ConversionResult(
                data=data_array,
                has_header=has_header,
                headers=headers,
                metadata=metadata,
            )

        except Exception as e:
            raise DataConversionError(
                "dataframe_to_json",
                message=f"Failed to convert DataFrame to JSON: {e}",
                original_error=e,
            ) from e

    def detect_header(self, df: pd.DataFrame) -> HeaderDetectionResult:
        """Detect whether DataFrame has a header row.

        Implements logic from excel_data_loader.py lines 565-659.
        """
        if df.empty or len(df) < 2:
            return HeaderDetectionResult(
                has_header=False,
                confidence=0.0,
                headers=[],
                analysis={"reason": "insufficient_data", "rows": len(df)},
            )

        try:
            # Analyze first row (potential header)
            first_row = df.iloc[0]
            string_ratio = self._calculate_string_ratio(first_row)

            # Analyze second row (potential data)
            second_row = df.iloc[1]
            numeric_ratio = self._calculate_numeric_ratio(second_row)

            # Check for header keywords in column names
            keyword_match = self._check_header_keywords_in_columns(df.columns)

            # Calculate confidence based on multiple factors
            confidence = self._calculate_header_confidence(
                string_ratio, numeric_ratio, keyword_match
            )

            has_header = confidence >= 0.6  # Threshold for header detection

            headers = [str(val) for val in first_row] if has_header else []

            analysis = {
                "string_ratio": string_ratio,
                "numeric_ratio": numeric_ratio,
                "keyword_match": keyword_match,
                "confidence_threshold": 0.6,
                "factors_analyzed": [
                    "string_ratio",
                    "numeric_ratio",
                    "keyword_presence",
                ],
            }

            return HeaderDetectionResult(
                has_header=has_header,
                confidence=confidence,
                headers=headers,
                analysis=analysis,
            )

        except Exception as e:
            raise DataConversionError(
                "header_detection",
                message=f"Failed to detect headers: {e}",
                original_error=e,
            ) from e

    def normalize_headers(
        self, headers: List[str], japanese_support: bool = True
    ) -> List[str]:
        """Normalize header names for consistency.

        Implements logic from excel_data_loader.py lines 1426-1456 and 3405-3432.
        """
        try:
            normalized = []
            seen_headers = set()

            for i, header in enumerate(headers):
                # Basic normalization
                normalized_header = str(header).strip()

                # Handle empty headers
                if not normalized_header or normalized_header.lower() in [
                    "nan",
                    "none",
                    "null",
                ]:
                    normalized_header = f"Column_{i + 1}"

                # Apply Japanese-specific normalization if enabled
                if japanese_support:
                    normalized_header = self._normalize_japanese_header(
                        normalized_header
                    )

                # Handle duplicates
                original_header = normalized_header
                counter = 1
                while normalized_header in seen_headers:
                    normalized_header = f"{original_header}_{counter}"
                    counter += 1

                seen_headers.add(normalized_header)
                normalized.append(normalized_header)

            return normalized

        except Exception as e:
            raise DataConversionError(
                "header_normalization",
                message=f"Failed to normalize headers: {e}",
                original_error=e,
            ) from e

    def _convert_dataframe_values(self, df: pd.DataFrame) -> List[List[Any]]:
        """Convert DataFrame values with proper type handling.

        Implements core conversion logic from lines 660-689.
        """
        data_array = []

        for _, row in df.iterrows():
            row_data = []
            for value in row:
                # Handle NaN/None values
                if pd.isna(value):
                    row_data.append(self.empty_string_replacement)
                    continue

                # Handle numeric values with type preservation
                if self.preserve_numeric_types and self._is_numeric_value(value):
                    # Convert to int if it's a whole number, otherwise keep as float
                    if isinstance(value, float) and value.is_integer():
                        row_data.append(int(value))
                    else:
                        row_data.append(value)
                else:
                    # Convert to string for consistency
                    row_data.append(str(value))

            data_array.append(row_data)

        return data_array

    def _is_numeric_value(self, value: Any) -> bool:
        """Check if value is numeric (implements logic from lines 587-596)."""
        if isinstance(value, (int, float)):
            return True

        if isinstance(value, str):
            try:
                float(value)
                return True
            except (ValueError, TypeError):
                return False

        return False

    def _calculate_string_ratio(self, row: pd.Series) -> float:
        """Calculate ratio of string values in a row."""
        if len(row) == 0:
            return 0.0

        string_count = sum(1 for val in row if isinstance(val, str) and val.strip())
        return string_count / len(row)

    def _calculate_numeric_ratio(self, row: pd.Series) -> float:
        """Calculate ratio of numeric values in a row."""
        if len(row) == 0:
            return 0.0

        numeric_count = sum(1 for val in row if self._is_numeric_value(val))
        return numeric_count / len(row)

    def _check_header_keywords(self, row: pd.Series) -> bool:
        """Check if row contains header-indicating keywords."""
        row_text = " ".join(str(val).lower() for val in row)
        return any(keyword.lower() in row_text for keyword in self.header_keywords)

    def _check_header_keywords_in_columns(self, columns) -> bool:
        """Check if column names contain header-indicating keywords."""
        column_text = " ".join(str(col).lower() for col in columns)
        return any(keyword.lower() in column_text for keyword in self.header_keywords)

    def _calculate_header_confidence(
        self, string_ratio: float, numeric_ratio: float, keyword_match: bool
    ) -> float:
        """Calculate confidence score for header detection."""
        confidence = 0.0

        # High string ratio in first row suggests header
        confidence += string_ratio * 0.4

        # High numeric ratio in second row suggests data
        confidence += numeric_ratio * 0.4

        # Keyword presence strongly suggests header
        if keyword_match:
            confidence += 0.3

        return min(confidence, 1.0)

    def _normalize_japanese_header(self, header: str) -> str:
        """Normalize header with Japanese character support.

        Implements logic from lines 3405-3432.
        """
        # Process Japanese parentheses and brackets
        for jp_char, replacement in self._japanese_char_map.items():
            header = header.replace(jp_char, replacement)

        # Replace other special characters with underscores
        header = re.sub(r"[^\w\s\-]", "_", header)

        # Replace spaces and hyphens with underscores
        header = re.sub(r"[\s\-]+", "_", header)

        # Clean consecutive underscores
        header = re.sub(r"_+", "_", header)

        # Remove leading/trailing underscores
        header = header.strip("_")

        return header


class MockDataConverter(IDataConverter):
    """Mock implementation for testing purposes."""

    def __init__(
        self,
        mock_conversion_result: Optional[ConversionResult] = None,
        mock_header_result: Optional[HeaderDetectionResult] = None,
        mock_headers: Optional[List[str]] = None,
        should_fail: bool = False,
        error_to_raise: Optional[Exception] = None,
    ):
        """Initialize mock converter.

        Args:
            mock_conversion_result: Fixed result for convert_dataframe_to_json
            mock_header_result: Fixed result for detect_header
            mock_headers: Fixed result for normalize_headers
            should_fail: Whether to raise errors
            error_to_raise: Specific error to raise
        """
        self.mock_conversion_result = mock_conversion_result
        self.mock_header_result = mock_header_result
        self.mock_headers = mock_headers or ["Header1", "Header2", "Header3"]
        self.should_fail = should_fail
        self.error_to_raise = error_to_raise or DataConversionError(
            "mock_operation", message="Mock error"
        )

        # Call tracking
        self.convert_calls = []
        self.detect_header_calls = []
        self.normalize_headers_calls = []

    def convert_dataframe_to_json(
        self, df: pd.DataFrame, has_header: bool = True
    ) -> ConversionResult:
        """Mock convert implementation with call tracking."""
        self.convert_calls.append({"df_shape": df.shape, "has_header": has_header})

        if self.should_fail:
            raise self.error_to_raise

        if self.mock_conversion_result:
            return self.mock_conversion_result

        # Default mock result
        return ConversionResult(
            data=[["row1_col1", "row1_col2"], ["row2_col1", "row2_col2"]],
            has_header=has_header,
            headers=["Col1", "Col2"] if has_header else ["Column_1", "Column_2"],
            metadata={"mock": True},
        )

    def detect_header(self, df: pd.DataFrame) -> HeaderDetectionResult:
        """Mock header detection with call tracking."""
        self.detect_header_calls.append({"df_shape": df.shape})

        if self.should_fail:
            raise self.error_to_raise

        if self.mock_header_result:
            return self.mock_header_result

        # Default mock result
        return HeaderDetectionResult(
            has_header=True,
            confidence=0.8,
            headers=["Header1", "Header2"],
            analysis={"mock": True},
        )

    def normalize_headers(
        self, headers: List[str], japanese_support: bool = True
    ) -> List[str]:
        """Mock header normalization with call tracking."""
        self.normalize_headers_calls.append(
            {"headers": headers, "japanese_support": japanese_support}
        )

        if self.should_fail:
            raise self.error_to_raise

        if self.mock_headers:
            return self.mock_headers[: len(headers)]

        # Default mock result
        return [f"normalized_{header}" for header in headers]
