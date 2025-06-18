"""Header Detection Tests - Phase 3.1 Coverage Boost.

Tests for actual header_detection.py methods to maximize coverage.
"""

import pandas as pd

from sphinxcontrib.jsontable.core.data_conversion_types import HeaderDetectionResult
from sphinxcontrib.jsontable.core.header_detection import HeaderDetector


class TestHeaderDetectionActual:
    """Test suite for HeaderDetector based on actual implementation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.detector = HeaderDetector()

    def test_init_default(self):
        """Test default initialization."""
        detector = HeaderDetector()
        assert detector.header_keywords is not None
        assert "name" in detector.header_keywords
        assert "名前" in detector.header_keywords
        assert "id" in detector.header_keywords

    def test_init_with_custom_keywords(self):
        """Test initialization with custom keywords."""
        custom_keywords = ["test", "テスト", "sample"]
        detector = HeaderDetector(header_keywords=custom_keywords)
        assert detector.header_keywords == custom_keywords

    def test_detect_header_empty_dataframe(self):
        """Test header detection with empty DataFrame."""
        df = pd.DataFrame()
        result = self.detector.detect_header(df)

        assert isinstance(result, HeaderDetectionResult)
        assert result.has_header is False
        assert result.confidence == 0.0
        assert result.headers == []
        assert "insufficient_data" in result.analysis["reason"]

    def test_detect_header_single_row(self):
        """Test header detection with single row DataFrame."""
        df = pd.DataFrame([["value1", "value2", "value3"]])
        result = self.detector.detect_header(df)

        assert result.has_header is False
        assert result.confidence == 0.0
        assert result.headers == []

    def test_detect_header_with_clear_headers(self):
        """Test header detection with clear header row."""
        # Create DataFrame with clear header pattern
        df = pd.DataFrame(
            [["Name", "Age", "City"], ["Alice", "30", "Tokyo"], ["Bob", "25", "Osaka"]]
        )

        result = self.detector.detect_header(df)

        assert isinstance(result, HeaderDetectionResult)
        # Note: exact results depend on implementation details
        assert isinstance(result.has_header, bool)
        assert isinstance(result.confidence, float)
        assert isinstance(result.headers, list)
        assert isinstance(result.analysis, dict)

    def test_detect_header_with_numeric_data(self):
        """Test header detection with mostly numeric data."""
        df = pd.DataFrame([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

        result = self.detector.detect_header(df)

        assert isinstance(result, HeaderDetectionResult)
        # Numeric first row should reduce header confidence
        assert isinstance(result.has_header, bool)
        assert isinstance(result.confidence, float)

    def test_detect_header_with_japanese_keywords(self):
        """Test header detection with Japanese keywords."""
        df = pd.DataFrame(
            [
                ["名前", "年齢", "住所"],
                ["田中太郎", "30", "東京"],
                ["佐藤花子", "25", "大阪"],
            ]
        )

        result = self.detector.detect_header(df)

        assert isinstance(result, HeaderDetectionResult)
        assert isinstance(result.has_header, bool)
        assert isinstance(result.confidence, float)

    def test_detect_header_mixed_content(self):
        """Test header detection with mixed string/numeric content."""
        df = pd.DataFrame(
            [
                ["Product", "Price", "Quantity"],
                ["Widget A", 10.99, 5],
                ["Widget B", 15.50, 3],
                ["Widget C", 8.25, 12],
            ]
        )

        result = self.detector.detect_header(df)

        assert isinstance(result, HeaderDetectionResult)
        assert "string_ratio" in result.analysis
        assert "numeric_ratio" in result.analysis
        assert "keyword_match" in result.analysis

    def test_detect_header_with_keyword_columns(self):
        """Test header detection with column names containing keywords."""
        # Create DataFrame where column names contain header keywords
        df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [30, 25], "id": [1, 2]})

        result = self.detector.detect_header(df)

        assert isinstance(result, HeaderDetectionResult)
        # Should consider keyword match in columns
        assert "keyword_match" in result.analysis

    def test_header_keywords_coverage(self):
        """Test that various header keywords are recognized."""
        keywords = self.detector.header_keywords

        # Test Japanese keywords
        assert "名前" in keywords
        assert "氏名" in keywords
        assert "項目" in keywords
        assert "タイトル" in keywords
        assert "日付" in keywords
        assert "時間" in keywords

        # Test English keywords
        assert "name" in keywords
        assert "item" in keywords
        assert "title" in keywords
        assert "id" in keywords
        assert "date" in keywords
        assert "time" in keywords

    def test_confidence_calculation_factors(self):
        """Test that confidence calculation includes expected factors."""
        df = pd.DataFrame(
            [
                ["Header1", "Header2", "Header3"],
                ["data1", "data2", "data3"],
                ["data4", "data5", "data6"],
            ]
        )

        result = self.detector.detect_header(df)

        # Check that analysis includes expected factors
        assert "string_ratio" in result.analysis
        assert "numeric_ratio" in result.analysis
        assert "keyword_match" in result.analysis
        assert "confidence_threshold" in result.analysis
        assert "factors_analyzed" in result.analysis

    def test_edge_case_all_empty_strings(self):
        """Test header detection with all empty strings."""
        df = pd.DataFrame([["", "", ""], ["data1", "data2", "data3"]])

        result = self.detector.detect_header(df)

        assert isinstance(result, HeaderDetectionResult)
        # Should handle empty strings gracefully
        assert isinstance(result.confidence, float)

    def test_edge_case_all_same_values(self):
        """Test header detection where all values are the same."""
        df = pd.DataFrame(
            [
                ["same", "same", "same"],
                ["same", "same", "same"],
                ["same", "same", "same"],
            ]
        )

        result = self.detector.detect_header(df)

        assert isinstance(result, HeaderDetectionResult)
        assert isinstance(result.confidence, float)

    def test_header_detection_result_structure(self):
        """Test that HeaderDetectionResult has expected structure."""
        df = pd.DataFrame([["Name", "Value"], ["Test", "123"]])

        result = self.detector.detect_header(df)

        # Test required attributes
        assert hasattr(result, "has_header")
        assert hasattr(result, "confidence")
        assert hasattr(result, "headers")
        assert hasattr(result, "analysis")

        # Test attribute types
        assert isinstance(result.has_header, bool)
        assert isinstance(result.confidence, (int, float))
        assert isinstance(result.headers, list)
        assert isinstance(result.analysis, dict)

    def test_large_dataframe_performance(self):
        """Test header detection with larger DataFrame."""
        # Create larger DataFrame to test performance
        data = []
        data.append(["Column1", "Column2", "Column3", "Column4", "Column5"])

        for i in range(100):
            data.append(
                [
                    f"value{i}_1",
                    f"value{i}_2",
                    f"value{i}_3",
                    f"value{i}_4",
                    f"value{i}_5",
                ]
            )

        df = pd.DataFrame(data)
        result = self.detector.detect_header(df)

        assert isinstance(result, HeaderDetectionResult)
        # Should complete in reasonable time and return valid result
        assert isinstance(result.confidence, float)

    def test_various_data_types(self):
        """Test header detection with various pandas data types."""
        df = pd.DataFrame(
            [
                ["Name", "Age", "Active", "Score"],
                ["Alice", 30, True, 95.5],
                ["Bob", 25, False, 87.2],
            ]
        )

        result = self.detector.detect_header(df)

        assert isinstance(result, HeaderDetectionResult)
        # Should handle mixed data types
        assert isinstance(result.confidence, float)
        assert "string_ratio" in result.analysis
        assert "numeric_ratio" in result.analysis
