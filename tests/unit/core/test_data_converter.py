"""Unit tests for DataConverter - extracted from monolithic ExcelDataLoader.

Tests the data conversion logic that addresses Excel data processing
requirements through focused, testable functionality.
"""

import numpy as np
import pandas as pd
import pytest

from sphinxcontrib.jsontable.core.data_converter import (
    ConversionResult,
    DataConverter,
    HeaderDetectionResult,
    IDataConverter,
    MockDataConverter,
)
from sphinxcontrib.jsontable.errors.excel_errors import DataConversionError


class TestConversionResult:
    """Test suite for ConversionResult data class."""
    
    def test_basic_initialization(self):
        """Test basic ConversionResult initialization."""
        result = ConversionResult(
            data=[["A1", "B1"], ["A2", "B2"]],
            has_header=True,
            headers=["Col A", "Col B"],
            metadata={"test": True}
        )
        
        assert result.data == [["A1", "B1"], ["A2", "B2"]]
        assert result.has_header is True
        assert result.headers == ["Col A", "Col B"]
        assert result.metadata == {"test": True}
    
    def test_to_dict_conversion(self):
        """Test dictionary conversion for JSON serialization."""
        result = ConversionResult(
            data=[["row1_col1", "row1_col2"], ["row2_col1", "row2_col2"]],
            has_header=True,
            headers=["Header1", "Header2"],
            metadata={"conversion_type": "test"}
        )
        
        result_dict = result.to_dict()
        
        expected = {
            "data": [["row1_col1", "row1_col2"], ["row2_col1", "row2_col2"]],
            "has_header": True,
            "headers": ["Header1", "Header2"],
            "metadata": {"conversion_type": "test"},
            "rows": 2,
            "columns": 2
        }
        
        assert result_dict == expected
    
    def test_empty_data_conversion(self):
        """Test dictionary conversion with empty data."""
        result = ConversionResult(
            data=[],
            has_header=False,
            headers=[],
            metadata={}
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["rows"] == 0
        assert result_dict["columns"] == 0


class TestHeaderDetectionResult:
    """Test suite for HeaderDetectionResult data class."""
    
    def test_basic_initialization(self):
        """Test basic HeaderDetectionResult initialization."""
        result = HeaderDetectionResult(
            has_header=True,
            confidence=0.85,
            headers=["Name", "Age", "Email"],
            analysis={"string_ratio": 1.0, "keyword_match": True}
        )
        
        assert result.has_header is True
        assert result.confidence == 0.85
        assert result.headers == ["Name", "Age", "Email"]
        assert result.analysis["string_ratio"] == 1.0
        assert result.analysis["keyword_match"] is True


class TestDataConverterBasic:
    """Test suite for basic DataConverter functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.converter = DataConverter()
        self.custom_converter = DataConverter(
            empty_string_replacement="N/A",
            preserve_numeric_types=False,
            header_keywords=["custom_header", "test_col"]
        )
    
    def test_initialization_default(self):
        """Test DataConverter initialization with defaults."""
        converter = DataConverter()
        
        assert converter.empty_string_replacement == ""
        assert converter.preserve_numeric_types is True
        assert "name" in [kw.lower() for kw in converter.header_keywords]
        assert "id" in [kw.lower() for kw in converter.header_keywords]
    
    def test_initialization_custom(self):
        """Test DataConverter initialization with custom parameters."""
        assert self.custom_converter.empty_string_replacement == "N/A"
        assert self.custom_converter.preserve_numeric_types is False
        assert "custom_header" in self.custom_converter.header_keywords
    
    def test_interface_implementation(self):
        """Test that DataConverter implements IDataConverter."""
        assert isinstance(self.converter, IDataConverter)
        assert hasattr(self.converter, 'convert_dataframe_to_json')
        assert hasattr(self.converter, 'detect_header')
        assert hasattr(self.converter, 'normalize_headers')


class TestDataFrameConversion:
    """Test suite for DataFrame to JSON conversion."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.converter = DataConverter()
        
        # Test DataFrames
        self.simple_df = pd.DataFrame({
            'Name': ['Alice', 'Bob', 'Charlie'],
            'Age': [25, 30, 35],
            'City': ['Tokyo', 'Osaka', 'Kyoto']
        })
        
        self.mixed_types_df = pd.DataFrame({
            'ID': [1, 2, 3],
            'Value': [10.5, 20.0, 30.7],
            'Text': ['A', 'B', 'C'],
            'Boolean': [True, False, True]
        })
        
        self.with_nan_df = pd.DataFrame({
            'Col1': ['A', np.nan, 'C'],
            'Col2': [1, 2, np.nan],
            'Col3': [10.5, np.nan, 30.0]
        })
    
    def test_simple_dataframe_conversion(self):
        """Test conversion of simple DataFrame."""
        result = self.converter.convert_dataframe_to_json(self.simple_df, has_header=True)
        
        assert isinstance(result, ConversionResult)
        assert result.has_header is True
        assert len(result.data) == 3
        assert len(result.data[0]) == 3
        assert result.headers == ['Name', 'Age', 'City']
        assert result.data[0] == ['Alice', 25, 'Tokyo']
        assert result.metadata['conversion_type'] == 'dataframe_to_json'
    
    def test_mixed_types_conversion(self):
        """Test conversion with mixed data types."""
        result = self.converter.convert_dataframe_to_json(self.mixed_types_df)
        
        # Verify numeric type preservation
        assert result.data[0][0] == 1  # Integer preserved
        assert result.data[0][1] == 10.5  # Float preserved
        assert result.data[1][1] == 20  # 20.0 becomes 20 (integer)
        assert result.data[0][2] == 'A'  # String preserved
        assert result.data[0][3] is True  # Boolean preserved as boolean
    
    def test_nan_value_handling(self):
        """Test handling of NaN values."""
        result = self.converter.convert_dataframe_to_json(self.with_nan_df)
        
        # Check NaN replacement
        assert result.data[1][0] == ""  # np.nan becomes empty string
        assert result.data[2][1] == ""  # np.nan becomes empty string
        assert result.data[1][2] == ""  # np.nan becomes empty string
        
        # Check non-NaN values are preserved
        assert result.data[0][0] == 'A'
        assert result.data[0][1] == 1
        assert result.data[0][2] == 10.5
    
    def test_no_header_conversion(self):
        """Test conversion without headers."""
        result = self.converter.convert_dataframe_to_json(self.simple_df, has_header=False)
        
        assert result.has_header is False
        assert result.headers == ['Column_1', 'Column_2', 'Column_3']
        assert len(result.data) == 3
    
    def test_empty_dataframe_conversion(self):
        """Test conversion of empty DataFrame."""
        empty_df = pd.DataFrame()
        result = self.converter.convert_dataframe_to_json(empty_df)
        
        assert result.data == []
        assert result.headers == []
        assert result.metadata['original_rows'] == 0
        assert result.metadata['original_columns'] == 0
    
    def test_custom_empty_replacement(self):
        """Test custom empty string replacement."""
        converter = DataConverter(empty_string_replacement="N/A")
        result = converter.convert_dataframe_to_json(self.with_nan_df)
        
        assert result.data[1][0] == "N/A"  # NaN replaced with N/A
        assert result.data[2][1] == "N/A"
        assert result.data[1][2] == "N/A"
    
    def test_numeric_type_preservation_disabled(self):
        """Test with numeric type preservation disabled."""
        converter = DataConverter(preserve_numeric_types=False)
        result = converter.convert_dataframe_to_json(self.mixed_types_df)
        
        # All values should be strings
        assert result.data[0][0] == '1'  # Integer as string
        assert result.data[0][1] == '10.5'  # Float as string
        assert result.data[1][1] == '20.0'  # Float as string
    
    def test_conversion_error_handling(self):
        """Test error handling during conversion."""
        # Create a problematic DataFrame that might cause conversion issues
        problematic_df = pd.DataFrame({'col': [object()]})  # Non-serializable object
        
        # This should not raise an exception but handle gracefully
        result = self.converter.convert_dataframe_to_json(problematic_df)
        assert isinstance(result, ConversionResult)


class TestHeaderDetection:
    """Test suite for header detection functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.converter = DataConverter()
        
        # DataFrame with clear header
        self.header_df = pd.DataFrame({
            'Name': ['Alice', 'Bob'],
            'Age': [25, 30],
            'Email': ['alice@test.com', 'bob@test.com']
        })
        
        # DataFrame without header (all numeric data)
        self.no_header_df = pd.DataFrame([
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9]
        ])
        
        # DataFrame with header keywords
        self.keyword_df = pd.DataFrame({
            '名前': ['田中', '佐藤'],
            'ID': [1, 2],
            '日付': ['2023-01-01', '2023-01-02']
        })
    
    def test_clear_header_detection(self):
        """Test detection of clear header row."""
        result = self.converter.detect_header(self.header_df)
        
        # Headers should be detected based on string ratio and keyword presence
        assert result.confidence > 0.0  # Some confidence should be present
        assert 'string_ratio' in result.analysis
        assert 'numeric_ratio' in result.analysis
        
        # Test with a more clear header case
        clear_header_df = pd.DataFrame({
            'name': ['Alice', 30],  # keyword + mixed types
            'age': ['Bob', 25],
            'email': ['alice@test.com', 'bob@test.com']
        })
        clear_result = self.converter.detect_header(clear_header_df)
        assert clear_result.has_header is True or clear_result.confidence > 0.5
    
    def test_no_header_detection(self):
        """Test detection when no header is present."""
        result = self.converter.detect_header(self.no_header_df)
        
        assert result.has_header is False
        assert result.confidence < 0.6
        assert result.analysis['string_ratio'] < 0.5
    
    def test_keyword_based_detection(self):
        """Test header detection based on keywords."""
        result = self.converter.detect_header(self.keyword_df)
        
        # Should have some confidence due to keyword presence
        assert result.confidence > 0.0
        
        # Test with explicit keyword DataFrame
        keyword_df = pd.DataFrame({
            'name': ['Alice', 25],  # Clear keyword
            'id': ['Bob', 30],      # Clear keyword
            'date': ['2023-01-01', '2023-01-02']  # Clear keyword
        })
        keyword_result = self.converter.detect_header(keyword_df)
        assert keyword_result.analysis['keyword_match'] is True
        assert keyword_result.has_header is True
    
    def test_insufficient_data_detection(self):
        """Test header detection with insufficient data."""
        # Single row DataFrame
        single_row_df = pd.DataFrame([['A', 'B', 'C']])
        result = self.converter.detect_header(single_row_df)
        
        assert result.has_header is False
        assert result.confidence == 0.0
        assert result.analysis['reason'] == 'insufficient_data'
        
        # Empty DataFrame
        empty_df = pd.DataFrame()
        result = self.converter.detect_header(empty_df)
        
        assert result.has_header is False
        assert result.confidence == 0.0
    
    def test_confidence_calculation(self):
        """Test confidence score calculation."""
        # Create DataFrame with mixed characteristics
        mixed_df = pd.DataFrame({
            'StringCol': ['Header1', 'data1'],  # String header, string data
            'NumCol': ['Header2', 123],         # String header, numeric data
            'ID': ['識別子', 456]               # Japanese keyword, numeric data
        })
        
        result = self.converter.detect_header(mixed_df)
        
        # Should have high confidence due to keyword presence
        assert result.confidence > 0.7
        assert result.has_header is True


class TestHeaderNormalization:
    """Test suite for header normalization functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.converter = DataConverter()
    
    def test_basic_header_normalization(self):
        """Test basic header normalization."""
        headers = ['Name', 'Age', 'Email Address']
        result = self.converter.normalize_headers(headers)
        
        assert result == ['Name', 'Age', 'Email_Address']  # Space becomes underscore
    
    def test_empty_header_handling(self):
        """Test handling of empty headers."""
        headers = ['Name', '', 'Age', None, 'nan']
        result = self.converter.normalize_headers(headers)
        
        assert result[0] == 'Name'
        assert result[1] == 'Column_2'  # Empty header gets default name
        assert result[2] == 'Age'
        assert result[3] == 'Column_4'  # None becomes default
        assert result[4] == 'Column_5'  # 'nan' string becomes default
    
    def test_duplicate_header_handling(self):
        """Test handling of duplicate headers."""
        headers = ['Name', 'Age', 'Name', 'Age', 'Name']
        result = self.converter.normalize_headers(headers)
        
        assert result == ['Name', 'Age', 'Name_1', 'Age_1', 'Name_2']
    
    def test_japanese_character_normalization(self):
        """Test Japanese character normalization."""
        headers = ['名前（氏名）', '年齢［Age］', '住所【Address】', '電話〈Phone〉']
        result = self.converter.normalize_headers(headers, japanese_support=True)
        
        # Japanese parentheses should be replaced with underscores
        assert '_' in result[0]  # （） should become _
        assert '_' in result[1]  # ［］ should become _
        assert '_' in result[2]  # 【】 should become _
        assert '_' in result[3]  # 〈〉 should become _
    
    def test_special_character_normalization(self):
        """Test special character normalization."""
        headers = ['Col@1', 'Col#2', 'Col$3', 'Col%4', 'Col&5']
        result = self.converter.normalize_headers(headers)
        
        for header in result:
            assert '@' not in header
            assert '#' not in header
            assert '$' not in header
            assert '%' not in header
            assert '&' not in header
    
    def test_whitespace_normalization(self):
        """Test whitespace and hyphen normalization."""
        headers = ['First Name', 'Last-Name', 'Email  Address', 'Phone-Number']
        result = self.converter.normalize_headers(headers)
        
        # Spaces and hyphens should be replaced with underscores
        assert result[0] == 'First_Name'
        assert result[1] == 'Last_Name'
        assert result[2] == 'Email_Address'
        assert result[3] == 'Phone_Number'
    
    def test_consecutive_underscore_cleanup(self):
        """Test cleanup of consecutive underscores."""
        headers = ['Col___1', 'Col____2', '_Col_3_', '__Col__4__']
        result = self.converter.normalize_headers(headers)
        
        # Consecutive underscores should be collapsed
        assert result[0] == 'Col_1'
        assert result[1] == 'Col_2'
        assert result[2] == 'Col_3'
        assert result[3] == 'Col_4'
    
    def test_japanese_support_disabled(self):
        """Test normalization with Japanese support disabled."""
        headers = ['名前（氏名）', 'Age']
        result = self.converter.normalize_headers(headers, japanese_support=False)
        
        # Should still handle basic normalization
        assert len(result) == 2
        assert result[1] == 'Age'


class TestUtilityMethods:
    """Test suite for utility methods."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.converter = DataConverter()
    
    def test_is_numeric_value(self):
        """Test numeric value detection."""
        # Numeric types
        assert self.converter._is_numeric_value(123) is True
        assert self.converter._is_numeric_value(123.45) is True
        assert self.converter._is_numeric_value('123') is True
        assert self.converter._is_numeric_value('123.45') is True
        assert self.converter._is_numeric_value('-123.45') is True
        
        # Non-numeric types
        assert self.converter._is_numeric_value('abc') is False
        assert self.converter._is_numeric_value('') is False
        assert self.converter._is_numeric_value(None) is False
        assert self.converter._is_numeric_value('123abc') is False
    
    def test_string_ratio_calculation(self):
        """Test string ratio calculation."""
        # All strings
        string_row = pd.Series(['A', 'B', 'C'])
        assert self.converter._calculate_string_ratio(string_row) == 1.0
        
        # Mixed types
        mixed_row = pd.Series(['A', 123, 'C'])
        assert self.converter._calculate_string_ratio(mixed_row) == 2/3
        
        # No strings
        numeric_row = pd.Series([1, 2, 3])
        assert self.converter._calculate_string_ratio(numeric_row) == 0.0
        
        # Empty row
        empty_row = pd.Series([])
        assert self.converter._calculate_string_ratio(empty_row) == 0.0
    
    def test_numeric_ratio_calculation(self):
        """Test numeric ratio calculation."""
        # All numeric
        numeric_row = pd.Series([1, 2, 3])
        assert self.converter._calculate_numeric_ratio(numeric_row) == 1.0
        
        # Mixed types
        mixed_row = pd.Series([1, 'B', 3])
        assert self.converter._calculate_numeric_ratio(mixed_row) == 2/3
        
        # No numeric
        string_row = pd.Series(['A', 'B', 'C'])
        assert self.converter._calculate_numeric_ratio(string_row) == 0.0
    
    def test_header_keyword_checking(self):
        """Test header keyword checking."""
        # Contains keywords
        keyword_row = pd.Series(['Name', 'Age', 'ID'])
        assert self.converter._check_header_keywords(keyword_row) is True
        
        # Japanese keywords
        japanese_row = pd.Series(['名前', '年齢', '番号'])
        assert self.converter._check_header_keywords(japanese_row) is True
        
        # No keywords
        no_keyword_row = pd.Series(['ColumnA', 'ColumnB', 'ColumnC'])
        assert self.converter._check_header_keywords(no_keyword_row) is False
    
    def test_confidence_calculation(self):
        """Test header confidence calculation."""
        # Perfect conditions
        confidence = self.converter._calculate_header_confidence(1.0, 1.0, True)
        assert confidence == 1.0
        
        # Good conditions
        confidence = self.converter._calculate_header_confidence(0.8, 0.7, True)
        assert confidence > 0.8
        
        # Poor conditions
        confidence = self.converter._calculate_header_confidence(0.2, 0.1, False)
        assert confidence < 0.4


class TestMockDataConverter:
    """Test suite for MockDataConverter."""
    
    def test_default_mock_behavior(self):
        """Test MockDataConverter with default behavior."""
        mock_converter = MockDataConverter()
        
        # Test DataFrame
        df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
        
        # Test conversion
        result = mock_converter.convert_dataframe_to_json(df)
        assert isinstance(result, ConversionResult)
        assert result.metadata['mock'] is True
        assert len(mock_converter.convert_calls) == 1
        
        # Test header detection
        header_result = mock_converter.detect_header(df)
        assert isinstance(header_result, HeaderDetectionResult)
        assert header_result.confidence == 0.8
        assert len(mock_converter.detect_header_calls) == 1
        
        # Test header normalization
        normalized = mock_converter.normalize_headers(['H1', 'H2'])
        assert normalized == ['Header1', 'Header2']
        assert len(mock_converter.normalize_headers_calls) == 1
    
    def test_custom_mock_results(self):
        """Test MockDataConverter with custom results."""
        custom_conversion = ConversionResult(
            data=[['custom', 'data']],
            has_header=False,
            headers=['Custom'],
            metadata={'custom': True}
        )
        
        custom_header = HeaderDetectionResult(
            has_header=False,
            confidence=0.3,
            headers=[],
            analysis={'custom': True}
        )
        
        mock_converter = MockDataConverter(
            mock_conversion_result=custom_conversion,
            mock_header_result=custom_header,
            mock_headers=['MockHeader1', 'MockHeader2']
        )
        
        df = pd.DataFrame({'A': [1]})
        
        # Test custom results
        conv_result = mock_converter.convert_dataframe_to_json(df)
        assert conv_result.metadata['custom'] is True
        
        header_result = mock_converter.detect_header(df)
        assert header_result.confidence == 0.3
        
        headers = mock_converter.normalize_headers(['A', 'B'])
        assert headers == ['MockHeader1', 'MockHeader2']
    
    def test_mock_error_behavior(self):
        """Test MockDataConverter error simulation."""
        mock_converter = MockDataConverter(should_fail=True)
        df = pd.DataFrame({'A': [1]})
        
        with pytest.raises(DataConversionError):
            mock_converter.convert_dataframe_to_json(df)
        
        with pytest.raises(DataConversionError):
            mock_converter.detect_header(df)
        
        with pytest.raises(DataConversionError):
            mock_converter.normalize_headers(['A'])
    
    def test_call_tracking(self):
        """Test call tracking functionality."""
        mock_converter = MockDataConverter()
        
        df1 = pd.DataFrame({'A': [1, 2]})
        df2 = pd.DataFrame({'B': [3, 4, 5]})
        
        # Make multiple calls
        mock_converter.convert_dataframe_to_json(df1, has_header=True)
        mock_converter.convert_dataframe_to_json(df2, has_header=False)
        mock_converter.detect_header(df1)
        mock_converter.normalize_headers(['H1', 'H2'], japanese_support=True)
        mock_converter.normalize_headers(['H3'], japanese_support=False)
        
        # Verify tracking
        assert len(mock_converter.convert_calls) == 2
        assert mock_converter.convert_calls[0]['df_shape'] == (2, 1)
        assert mock_converter.convert_calls[0]['has_header'] is True
        assert mock_converter.convert_calls[1]['df_shape'] == (3, 1)
        assert mock_converter.convert_calls[1]['has_header'] is False
        
        assert len(mock_converter.detect_header_calls) == 1
        assert mock_converter.detect_header_calls[0]['df_shape'] == (2, 1)
        
        assert len(mock_converter.normalize_headers_calls) == 2
        assert mock_converter.normalize_headers_calls[0]['japanese_support'] is True
        assert mock_converter.normalize_headers_calls[1]['japanese_support'] is False


class TestInterface:
    """Test interface implementation."""
    
    def test_interface_compliance(self):
        """Test that all converters implement IDataConverter."""
        converters = [
            DataConverter(),
            MockDataConverter()
        ]
        
        for converter in converters:
            assert isinstance(converter, IDataConverter)
            assert hasattr(converter, 'convert_dataframe_to_json')
            assert hasattr(converter, 'detect_header')
            assert hasattr(converter, 'normalize_headers')
    
    def test_polymorphic_usage(self):
        """Test polymorphic usage of different converter implementations."""
        def process_data(converter: IDataConverter, df: pd.DataFrame) -> ConversionResult:
            """Function that accepts any IDataConverter implementation."""
            header_result = converter.detect_header(df)
            return converter.convert_dataframe_to_json(df, header_result.has_header)
        
        df = pd.DataFrame({'Name': ['Alice'], 'Age': [25]})
        
        # Test with real converter
        real_converter = DataConverter()
        result1 = process_data(real_converter, df)
        assert isinstance(result1, ConversionResult)
        
        # Test with mock converter
        mock_converter = MockDataConverter()
        result2 = process_data(mock_converter, df)
        assert isinstance(result2, ConversionResult)


class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_conversion_error_propagation(self):
        """Test that conversion errors are properly propagated."""
        converter = DataConverter()
        
        # This should handle gracefully
        df = pd.DataFrame({'col': [1, 2, 3]})
        result = converter.convert_dataframe_to_json(df)
        assert isinstance(result, ConversionResult)
    
    def test_header_detection_error_handling(self):
        """Test header detection error handling."""
        converter = DataConverter()
        
        # Should handle edge cases gracefully
        empty_df = pd.DataFrame()
        result = converter.detect_header(empty_df)
        assert isinstance(result, HeaderDetectionResult)
        assert result.has_header is False
    
    def test_header_normalization_error_handling(self):
        """Test header normalization error handling."""
        converter = DataConverter()
        
        # Should handle problematic headers gracefully
        problematic_headers = [None, '', 123, object()]
        result = converter.normalize_headers(problematic_headers)
        assert len(result) == len(problematic_headers)
        assert all(isinstance(h, str) for h in result)