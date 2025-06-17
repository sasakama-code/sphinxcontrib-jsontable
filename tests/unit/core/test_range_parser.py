"""Unit tests for RangeParser - extracted from monolithic ExcelDataLoader.

Tests the functional composition-based range parsing that addresses
the 814-853 line complexity problem through small, testable functions.
"""

import pytest

from sphinxcontrib.jsontable.core.range_parser import (
    IRangeParser,
    MockRangeParser,
    RangeInfo,
    RangeParser,
)
from sphinxcontrib.jsontable.errors.excel_errors import (
    RangeSpecificationError,
    RangeValidationError,
)


class TestRangeInfo:
    """Test suite for RangeInfo data class."""
    
    def test_basic_properties(self):
        """Test basic RangeInfo properties calculation."""
        range_info = RangeInfo(
            start_row=1,
            start_col=1,
            end_row=10,
            end_col=5,
            original_spec="A1:E10",
            normalized_spec="A1:E10"
        )
        
        assert range_info.row_count == 10
        assert range_info.col_count == 5
        assert range_info.cell_count == 50
    
    def test_single_cell_properties(self):
        """Test properties for single cell range."""
        range_info = RangeInfo(
            start_row=5,
            start_col=3,
            end_row=5,
            end_col=3,
            original_spec="C5",
            normalized_spec="C5"
        )
        
        assert range_info.row_count == 1
        assert range_info.col_count == 1
        assert range_info.cell_count == 1
    
    def test_to_dict_conversion(self):
        """Test dictionary conversion for serialization."""
        range_info = RangeInfo(
            start_row=2,
            start_col=4,
            end_row=8,
            end_col=7,
            original_spec="d2:g8",
            normalized_spec="D2:G8"
        )
        
        result = range_info.to_dict()
        
        expected = {
            "start_row": 2,
            "start_col": 4,
            "end_row": 8,
            "end_col": 7,
            "original_spec": "d2:g8",
            "normalized_spec": "D2:G8",
            "row_count": 7,
            "col_count": 4,
            "cell_count": 28,
        }
        
        assert result == expected


class TestRangeParserBasic:
    """Test suite for basic RangeParser functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = RangeParser()
    
    def test_initialization(self):
        """Test RangeParser initialization."""
        # Default initialization
        parser = RangeParser()
        assert parser.max_rows == 1048576
        assert parser.max_cols == 16384
        
        # Custom initialization
        custom_parser = RangeParser(max_rows=1000, max_cols=100)
        assert custom_parser.max_rows == 1000
        assert custom_parser.max_cols == 100
    
    def test_interface_implementation(self):
        """Test that RangeParser implements IRangeParser."""
        assert isinstance(self.parser, IRangeParser)
        assert hasattr(self.parser, 'parse')
        assert callable(self.parser.parse)
    
    def test_simple_range_parsing(self):
        """Test parsing of simple range specifications."""
        result = self.parser.parse("A1:B10")
        
        assert result.start_row == 1
        assert result.start_col == 1
        assert result.end_row == 10
        assert result.end_col == 2
        assert result.original_spec == "A1:B10"
        assert result.normalized_spec == "A1:B10"
    
    def test_single_cell_parsing(self):
        """Test parsing of single cell specifications."""
        result = self.parser.parse("C5")
        
        assert result.start_row == 5
        assert result.start_col == 3
        assert result.end_row == 5
        assert result.end_col == 3
        assert result.original_spec == "C5"
        assert result.normalized_spec == "C5"
    
    def test_case_insensitive_parsing(self):
        """Test that parsing is case-insensitive."""
        result = self.parser.parse("a1:z26")
        
        assert result.start_row == 1
        assert result.start_col == 1
        assert result.end_row == 26
        assert result.end_col == 26
        assert result.original_spec == "a1:z26"
        assert result.normalized_spec == "A1:Z26"
    
    def test_whitespace_handling(self):
        """Test handling of whitespace in specifications."""
        result = self.parser.parse("  A1:B10  ")
        
        assert result.start_row == 1
        assert result.start_col == 1
        assert result.end_row == 10
        assert result.end_col == 2
        assert result.original_spec == "  A1:B10  "
        assert result.normalized_spec == "A1:B10"


class TestRangeParserFunctionalComposition:
    """Test suite for functional composition stages."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = RangeParser()
    
    def test_stage_1_type_validation(self):
        """Test Stage 1: Type validation (addresses lines 814-817)."""
        # Valid string input
        result = self.parser._validate_type("A1:B10")
        assert result == "A1:B10"
        
        # Invalid inputs
        with pytest.raises(TypeError, match="Range specification must be a string"):
            self.parser._validate_type(123)
        
        with pytest.raises(TypeError, match="Range specification must be a string"):
            self.parser._validate_type(None)
        
        with pytest.raises(TypeError, match="Range specification must be a string"):
            self.parser._validate_type(['A1', 'B10'])
    
    def test_stage_2_empty_validation(self):
        """Test Stage 2: Empty validation (addresses lines 819-823)."""
        # Valid non-empty input
        result = self.parser._validate_empty("A1:B10")
        assert result == "A1:B10"
        
        # Whitespace-only trimming
        result = self.parser._validate_empty("  A1:B10  ")
        assert result == "A1:B10"
        
        # Empty inputs
        with pytest.raises(RangeSpecificationError, match="Range specification cannot be empty"):
            self.parser._validate_empty("")
        
        with pytest.raises(RangeSpecificationError, match="Range specification cannot be empty"):
            self.parser._validate_empty("   ")
    
    def test_stage_3_normalization(self):
        """Test Stage 3: Specification normalization."""
        assert self.parser._normalize_spec("a1:b10") == "A1:B10"
        assert self.parser._normalize_spec("A1:B10") == "A1:B10"
        assert self.parser._normalize_spec("zZ123") == "ZZ123"
    
    def test_stage_4_format_parsing(self):
        """Test Stage 4: Format parsing (addresses lines 828-835)."""
        # Set up original input for testing
        self.parser.original_input = "A1:B10"
        
        # Valid range format
        start, end, normalized, original = self.parser._parse_format("A1:B10")
        assert start == "A1"
        assert end == "B10"
        assert normalized == "A1:B10"
        assert original == "A1:B10"
        
        # Single cell format (auto-expand)
        self.parser.original_input = "C5"
        start, end, normalized, original = self.parser._parse_format("C5")
        assert start == "C5"
        assert end == "C5"
        assert normalized == "C5"
        assert original == "C5"
        
        # Invalid formats
        with pytest.raises(RangeSpecificationError, match="Invalid range format"):
            self.parser._parse_format("A1-B10")  # Wrong separator
        
        with pytest.raises(RangeSpecificationError, match="Invalid range format"):
            self.parser._parse_format("1A:2B")   # Numbers first
        
        with pytest.raises(RangeSpecificationError, match="Invalid range format"):
            self.parser._parse_format("A:B")     # Missing row numbers
    
    def test_stage_5_bounds_validation(self):
        """Test Stage 5: Bounds validation (addresses lines 847-851)."""
        # Valid bounds
        result = self.parser._validate_bounds(("A1", "B10", "A1:B10", "A1:B10"))
        assert isinstance(result, RangeInfo)
        assert result.start_row == 1
        assert result.start_col == 1
        assert result.end_row == 10
        assert result.end_col == 2
        
        # Negative bounds - this becomes a RangeSpecificationError during cell parsing
        with pytest.raises(RangeSpecificationError, match="Invalid row number"):
            self.parser._validate_bounds(("A0", "B10", "A0:B10", "A0:B10"))
        
        # Reversed bounds
        with pytest.raises(RangeValidationError, match="Start row .* cannot be greater than end row"):
            self.parser._validate_bounds(("A10", "A1", "A10:A1", "A10:A1"))
        
        with pytest.raises(RangeValidationError, match="Start column .* cannot be greater than end column"):
            self.parser._validate_bounds(("B1", "A1", "B1:A1", "B1:A1"))


class TestRangeParserColumnConversion:
    """Test suite for Excel column letter conversion."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = RangeParser()
    
    def test_single_letter_columns(self):
        """Test conversion of single letter columns."""
        assert self.parser._column_letters_to_number("A") == 1
        assert self.parser._column_letters_to_number("B") == 2
        assert self.parser._column_letters_to_number("Z") == 26
    
    def test_double_letter_columns(self):
        """Test conversion of double letter columns."""
        assert self.parser._column_letters_to_number("AA") == 27
        assert self.parser._column_letters_to_number("AB") == 28
        assert self.parser._column_letters_to_number("AZ") == 52
        assert self.parser._column_letters_to_number("BA") == 53
        assert self.parser._column_letters_to_number("ZZ") == 702
    
    def test_triple_letter_columns(self):
        """Test conversion of triple letter columns."""
        assert self.parser._column_letters_to_number("AAA") == 703
        assert self.parser._column_letters_to_number("ABC") == 731
    
    def test_cell_address_parsing(self):
        """Test parsing of cell addresses."""
        # Simple cases
        row, col = self.parser._parse_cell_address("A1")
        assert row == 1 and col == 1
        
        row, col = self.parser._parse_cell_address("Z26")
        assert row == 26 and col == 26
        
        # Complex cases  
        row, col = self.parser._parse_cell_address("AA100")
        assert row == 100 and col == 27
        
        row, col = self.parser._parse_cell_address("ABC12345")
        assert row == 12345 and col == 731
        
        # Invalid cases
        with pytest.raises(RangeSpecificationError, match="Invalid cell address format"):
            self.parser._parse_cell_address("1A")
        
        with pytest.raises(RangeSpecificationError, match="Invalid cell address format"):
            self.parser._parse_cell_address("A")
        
        with pytest.raises(RangeSpecificationError, match="Invalid row number"):
            self.parser._parse_cell_address("A0")


class TestRangeParserBoundsValidation:
    """Test suite for range bounds validation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = RangeParser(max_rows=1000, max_cols=100)  # Custom limits for testing
    
    def test_valid_bounds(self):
        """Test validation of valid bounds."""
        # Normal range
        self.parser._check_bounds(1, 1, 10, 10, "A1:J10")  # Should not raise
        
        # Single cell
        self.parser._check_bounds(5, 5, 5, 5, "E5")  # Should not raise
        
        # Maximum bounds
        self.parser._check_bounds(1, 1, 1000, 100, "A1:CV1000")  # Should not raise
    
    def test_excel_limits_exceeded(self):
        """Test validation when Excel limits are exceeded."""
        # Row limit exceeded
        with pytest.raises(RangeValidationError, match="Row index exceeds Excel limit"):
            self.parser._check_bounds(1, 1, 1001, 10, "A1:J1001")
        
        # Column limit exceeded  
        with pytest.raises(RangeValidationError, match="Column index exceeds Excel limit"):
            self.parser._check_bounds(1, 1, 10, 101, "A1:CW10")
    
    def test_negative_indices(self):
        """Test validation with negative indices."""
        with pytest.raises(RangeValidationError, match="Row and column indices must be positive"):
            self.parser._check_bounds(0, 1, 10, 10, "A0:J10")
        
        with pytest.raises(RangeValidationError, match="Row and column indices must be positive"):
            self.parser._check_bounds(1, 0, 10, 10, "?1:J10")
    
    def test_reversed_bounds(self):
        """Test validation with reversed bounds."""
        with pytest.raises(RangeValidationError, match="Start row .* cannot be greater than end row"):
            self.parser._check_bounds(10, 1, 5, 10, "A10:J5")
        
        with pytest.raises(RangeValidationError, match="Start column .* cannot be greater than end column"):
            self.parser._check_bounds(1, 10, 10, 5, "J1:E10")


class TestRangeParserIntegration:
    """Integration tests for complete range parsing scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = RangeParser()
    
    def test_complex_range_parsing(self):
        """Test parsing of complex range specifications."""
        # Large range
        result = self.parser.parse("AA1:ZZ1000")
        assert result.start_row == 1
        assert result.start_col == 27  # AA
        assert result.end_row == 1000
        assert result.end_col == 702   # ZZ
        assert result.row_count == 1000
        assert result.col_count == 676
        assert result.cell_count == 676000
    
    def test_edge_case_ranges(self):
        """Test edge case range specifications."""
        # Single row range
        result = self.parser.parse("A5:Z5")
        assert result.row_count == 1
        assert result.col_count == 26
        
        # Single column range
        result = self.parser.parse("C1:C100")
        assert result.row_count == 100
        assert result.col_count == 1
    
    def test_error_propagation(self):
        """Test that errors are properly propagated through composition."""
        # Type error should propagate
        with pytest.raises(TypeError):
            self.parser.parse(123)
        
        # Empty specification error should propagate
        with pytest.raises(RangeSpecificationError, match="cannot be empty"):
            self.parser.parse("")
        
        # Format error should propagate
        with pytest.raises(RangeSpecificationError, match="Invalid range format"):
            self.parser.parse("invalid_format")
        
        # Bounds error should propagate
        with pytest.raises(RangeValidationError):
            self.parser.parse("A10:A1")  # Reversed bounds


class TestMockRangeParser:
    """Test suite for MockRangeParser."""
    
    def test_default_mock_behavior(self):
        """Test MockRangeParser with default behavior."""
        mock_parser = MockRangeParser()
        
        result = mock_parser.parse("A1:B10")
        
        assert isinstance(result, RangeInfo)
        assert result.start_row == 1
        assert result.start_col == 1
        assert result.end_row == 10
        assert result.end_col == 2
        assert result.original_spec == "A1:B10"
        assert result.normalized_spec == "A1:B10"
        
        # Verify call tracking
        assert len(mock_parser.parse_calls) == 1
        assert mock_parser.parse_calls[0]["range_spec"] == "A1:B10"
    
    def test_custom_mock_result(self):
        """Test MockRangeParser with custom result."""
        custom_result = RangeInfo(
            start_row=5,
            start_col=10,
            end_row=15,
            end_col=20,
            original_spec="custom",
            normalized_spec="CUSTOM"
        )
        
        mock_parser = MockRangeParser(mock_result=custom_result)
        result = mock_parser.parse("any_input")
        
        assert result is custom_result
        assert result.start_row == 5
        assert result.start_col == 10
    
    def test_mock_error_behavior(self):
        """Test MockRangeParser error simulation."""
        custom_error = RangeValidationError("TEST:ERROR", message="Mock validation error")
        mock_parser = MockRangeParser(should_fail=True, error_to_raise=custom_error)
        
        with pytest.raises(RangeValidationError, match="Mock validation error"):
            mock_parser.parse("A1:B10")
        
        # Call should still be tracked even when error occurs
        assert len(mock_parser.parse_calls) == 1
    
    def test_mock_default_error(self):
        """Test MockRangeParser with default error."""
        mock_parser = MockRangeParser(should_fail=True)
        
        with pytest.raises(RangeSpecificationError, match="Mock error"):
            mock_parser.parse("test_input")
    
    def test_call_tracking_multiple_calls(self):
        """Test call tracking for multiple invocations."""
        mock_parser = MockRangeParser()
        
        mock_parser.parse("A1:B10")
        mock_parser.parse("C1:D20")
        mock_parser.parse("E1")
        
        assert len(mock_parser.parse_calls) == 3
        assert mock_parser.parse_calls[0]["range_spec"] == "A1:B10"
        assert mock_parser.parse_calls[1]["range_spec"] == "C1:D20"
        assert mock_parser.parse_calls[2]["range_spec"] == "E1"


class TestRangeParserInterface:
    """Test interface compliance and polymorphism."""
    
    def test_interface_compliance(self):
        """Test that all parsers implement the interface correctly."""
        parsers = [
            RangeParser(),
            MockRangeParser()
        ]
        
        for parser in parsers:
            assert isinstance(parser, IRangeParser)
            assert hasattr(parser, 'parse')
            assert callable(parser.parse)
    
    def test_polymorphic_usage(self):
        """Test polymorphic usage of different parser implementations."""
        def process_range(parser: IRangeParser, spec: str) -> RangeInfo:
            """Function that accepts any IRangeParser implementation."""
            return parser.parse(spec)
        
        # Test with real parser
        real_parser = RangeParser()
        result1 = process_range(real_parser, "A1:B10")
        assert result1.start_row == 1
        assert result1.end_row == 10
        
        # Test with mock parser
        mock_parser = MockRangeParser()
        result2 = process_range(mock_parser, "A1:B10")
        assert result2.start_row == 1
        assert result2.end_row == 10
        
        # Both should return valid RangeInfo objects
        assert isinstance(result1, RangeInfo)
        assert isinstance(result2, RangeInfo)


# Performance and stress testing
class TestRangeParserPerformance:
    """Performance and stress tests for RangeParser."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = RangeParser()
    
    def test_large_range_parsing(self):
        """Test parsing of very large ranges."""
        # Test maximum Excel range
        result = self.parser.parse("A1:XFD1048576")
        
        assert result.start_row == 1
        assert result.start_col == 1
        assert result.end_row == 1048576
        assert result.end_col == 16384  # XFD = 16384
        assert result.cell_count == 1048576 * 16384
    
    def test_multiple_parsing_calls(self):
        """Test multiple sequential parsing calls."""
        test_specs = [
            "A1:B10",
            "C5:F20",
            "AA1:ZZ100",
            "A1",
            "XFD1048576"
        ]
        
        results = []
        for spec in test_specs:
            result = self.parser.parse(spec)
            results.append(result)
            assert isinstance(result, RangeInfo)
        
        # Verify all results are independent
        assert len(results) == len(test_specs)
        assert all(isinstance(r, RangeInfo) for r in results)