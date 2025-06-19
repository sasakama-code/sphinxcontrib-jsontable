"""Unit tests for ExcelReader - extracted from monolithic ExcelDataLoader.

Tests the file I/O logic that addresses Excel file reading requirements
through focused, testable functionality.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from sphinxcontrib.jsontable.core.excel_reader import (
    ExcelReader,
    IExcelReader,
    MockExcelReader,
    ReadResult,
    WorkbookInfo,
)
from sphinxcontrib.jsontable.errors.excel_errors import (
    ExcelFileNotFoundError,
    ExcelProcessingError,
    SecurityValidationError,
    WorksheetNotFoundError,
)


class TestWorkbookInfo:
    """Test suite for WorkbookInfo data class."""

    def test_basic_initialization(self):
        """Test basic WorkbookInfo initialization."""
        file_path = Path("/test/file.xlsx")
        info = WorkbookInfo(
            file_path=file_path,
            sheet_names=["Sheet1", "Sheet2"],
            has_macros=False,
            has_external_links=False,
            file_size=1024,
            format_type=".xlsx",
        )

        assert info.file_path == file_path
        assert info.sheet_names == ["Sheet1", "Sheet2"]
        assert info.has_macros is False
        assert info.has_external_links is False
        assert info.file_size == 1024
        assert info.format_type == ".xlsx"

    def test_to_dict_conversion(self):
        """Test dictionary conversion for JSON serialization."""
        file_path = Path("/test/workbook.xlsx")
        info = WorkbookInfo(
            file_path=file_path,
            sheet_names=["Data", "Summary", "Charts"],
            has_macros=True,
            has_external_links=True,
            file_size=2048000,
            format_type=".xlsm",
        )

        result = info.to_dict()

        expected = {
            "file_path": "/test/workbook.xlsx",
            "sheet_names": ["Data", "Summary", "Charts"],
            "has_macros": True,
            "has_external_links": True,
            "file_size": 2048000,
            "format_type": ".xlsm",
            "total_sheets": 3,
        }

        assert result == expected


class TestReadResult:
    """Test suite for ReadResult data class."""

    def test_basic_initialization(self):
        """Test basic ReadResult initialization."""
        df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
        workbook_info = WorkbookInfo(
            file_path=Path("/test.xlsx"),
            sheet_names=["Sheet1"],
            has_macros=False,
            has_external_links=False,
            file_size=1024,
            format_type=".xlsx",
        )
        metadata = {"test": True}

        result = ReadResult(
            dataframe=df,
            workbook_info=workbook_info,
            metadata=metadata,
        )

        assert result.dataframe.equals(df)
        assert result.workbook_info == workbook_info
        assert result.metadata == metadata

    def test_to_dict_conversion(self):
        """Test dictionary conversion."""
        df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        workbook_info = WorkbookInfo(
            file_path=Path("/test.xlsx"),
            sheet_names=["Sheet1"],
            has_macros=False,
            has_external_links=False,
            file_size=1024,
            format_type=".xlsx",
        )

        result = ReadResult(
            dataframe=df,
            workbook_info=workbook_info,
            metadata={"rows": 3},
        )

        result_dict = result.to_dict()

        assert result_dict["data_shape"] == (3, 2)
        assert result_dict["columns"] == ["A", "B"]
        assert result_dict["metadata"] == {"rows": 3}
        assert "workbook_info" in result_dict


class TestExcelReaderBasic:
    """Test suite for basic ExcelReader functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.reader = ExcelReader()
        self.custom_reader = ExcelReader(
            max_file_size=50 * 1024 * 1024,  # 50MB
            allowed_extensions=[".xlsx", ".xls"],
            enable_security_validation=False,
        )

    def test_initialization_default(self):
        """Test ExcelReader initialization with defaults."""
        reader = ExcelReader()

        assert reader.max_file_size == 100 * 1024 * 1024  # 100MB
        assert ".xlsx" in reader.allowed_extensions
        assert ".xls" in reader.allowed_extensions
        assert reader.enable_security_validation is True

    def test_initialization_custom(self):
        """Test ExcelReader initialization with custom parameters."""
        assert self.custom_reader.max_file_size == 50 * 1024 * 1024
        assert self.custom_reader.allowed_extensions == [".xlsx", ".xls"]
        assert self.custom_reader.enable_security_validation is False

    def test_interface_implementation(self):
        """Test that ExcelReader implements IExcelReader."""
        assert isinstance(self.reader, IExcelReader)
        assert hasattr(self.reader, "validate_file")
        assert hasattr(self.reader, "read_excel")
        assert hasattr(self.reader, "get_sheet_names")


class TestFileValidation:
    """Test suite for file validation functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.reader = ExcelReader()

    def test_validate_file_existence_nonexistent(self):
        """Test validation of non-existent file."""
        with pytest.raises(ExcelFileNotFoundError):
            self.reader._validate_file_existence(Path("/nonexistent/file.xlsx"))

    def test_validate_file_extension_valid(self):
        """Test validation of valid file extensions."""
        # Should not raise for valid extensions
        self.reader._validate_file_extension(Path("test.xlsx"))
        self.reader._validate_file_extension(Path("test.xls"))
        self.reader._validate_file_extension(Path("test.xlsm"))
        self.reader._validate_file_extension(Path("test.xltm"))

    def test_validate_file_extension_invalid(self):
        """Test validation of invalid file extensions."""
        with pytest.raises(ExcelProcessingError, match="Unsupported file extension"):
            self.reader._validate_file_extension(Path("test.txt"))

        with pytest.raises(ExcelProcessingError, match="Unsupported file extension"):
            self.reader._validate_file_extension(Path("test.pdf"))

    def test_validate_file_size_within_limit(self):
        """Test file size validation within limits."""
        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
            tmp_file.write(b"test content")
            tmp_path = Path(tmp_file.name)

        try:
            # Should not raise for small file
            self.reader._validate_file_size(tmp_path)
        finally:
            tmp_path.unlink()

    def test_validate_file_size_exceeds_limit(self):
        """Test file size validation when exceeding limits."""
        # Create reader with very small limit for testing
        reader = ExcelReader(max_file_size=10)  # 10 bytes

        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
            tmp_file.write(b"this content exceeds 10 bytes")
            tmp_path = Path(tmp_file.name)

        try:
            with pytest.raises(ExcelProcessingError, match="File too large"):
                reader._validate_file_size(tmp_path)
        finally:
            tmp_path.unlink()

    def test_validate_path_security(self):
        """Test path security validation."""
        # Should not raise for normal paths
        self.reader._validate_path_security(Path("normal/path/file.xlsx"))
        self.reader._validate_path_security(Path("./relative/path.xlsx"))


class TestSheetOperations:
    """Test suite for sheet-related operations."""

    def setup_method(self):
        """Set up test fixtures."""
        self.reader = ExcelReader()

    def test_determine_target_sheet_default(self):
        """Test default sheet selection (first sheet)."""
        sheet_names = ["Data", "Summary", "Charts"]
        result = self.reader._determine_target_sheet(sheet_names)
        assert result == "Data"

    def test_determine_target_sheet_by_name(self):
        """Test sheet selection by name."""
        sheet_names = ["Data", "Summary", "Charts"]
        result = self.reader._determine_target_sheet(sheet_names, sheet_name="Summary")
        assert result == "Summary"

    def test_determine_target_sheet_by_index(self):
        """Test sheet selection by index."""
        sheet_names = ["Data", "Summary", "Charts"]
        result = self.reader._determine_target_sheet(sheet_names, sheet_index=2)
        assert result == "Charts"

    def test_determine_target_sheet_invalid_name(self):
        """Test sheet selection with invalid name."""
        sheet_names = ["Data", "Summary", "Charts"]
        with pytest.raises(WorksheetNotFoundError):
            self.reader._determine_target_sheet(sheet_names, sheet_name="NonExistent")

    def test_determine_target_sheet_invalid_index(self):
        """Test sheet selection with invalid index."""
        sheet_names = ["Data", "Summary", "Charts"]
        with pytest.raises(WorksheetNotFoundError):
            self.reader._determine_target_sheet(sheet_names, sheet_index=5)

    def test_determine_target_sheet_no_sheets(self):
        """Test sheet selection with no sheets available."""
        with pytest.raises(WorksheetNotFoundError, match="No worksheets found"):
            self.reader._determine_target_sheet([])


class TestSecurityValidation:
    """Test suite for security validation functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.reader = ExcelReader()

    @patch("sphinxcontrib.jsontable.core.excel_reader.load_workbook")
    def test_validate_security_no_threats(self, mock_load_workbook):
        """Test security validation with no threats."""
        # Mock workbook without macros or external links
        mock_workbook = Mock()
        mock_workbook.vba_archive = None
        mock_worksheet = Mock()
        mock_cell = Mock()
        mock_cell.value = "Normal text"
        mock_worksheet.iter_rows.return_value = [[mock_cell]]
        mock_workbook.worksheets = [mock_worksheet]

        result = self.reader._validate_security(mock_workbook)

        assert result["has_macros"] is False
        assert result["has_external_links"] is False

    @patch("sphinxcontrib.jsontable.core.excel_reader.load_workbook")
    def test_validate_security_with_macros(self, mock_load_workbook):
        """Test security validation with macros."""
        # Mock workbook with VBA
        mock_workbook = Mock()
        mock_workbook.vba_archive = Mock()  # Non-None indicates VBA presence
        mock_worksheet = Mock()
        mock_cell = Mock()
        mock_cell.value = "Normal text"
        mock_worksheet.iter_rows.return_value = [[mock_cell]]
        mock_workbook.worksheets = [mock_worksheet]

        with pytest.raises(SecurityValidationError) as exc_info:
            self.reader._validate_security(mock_workbook)

        assert "macro_detected" in str(exc_info.value.security_issues)

    @patch("sphinxcontrib.jsontable.core.excel_reader.load_workbook")
    def test_validate_security_with_external_links(self, mock_load_workbook):
        """Test security validation with external links."""
        # Mock workbook with external links
        mock_workbook = Mock()
        mock_workbook.vba_archive = None
        mock_worksheet = Mock()
        mock_cell = Mock()
        mock_cell.value = "=HYPERLINK('http://external-site.com')"
        mock_worksheet.iter_rows.return_value = [[mock_cell]]
        mock_workbook.worksheets = [mock_worksheet]

        with pytest.raises(SecurityValidationError) as exc_info:
            self.reader._validate_security(mock_workbook)

        assert "external_links" in str(exc_info.value.security_issues)


class TestMockExcelReader:
    """Test suite for MockExcelReader."""

    def test_default_mock_behavior(self):
        """Test MockExcelReader with default behavior."""
        mock_reader = MockExcelReader()

        # Test validate_file
        workbook_info = mock_reader.validate_file("/test/file.xlsx")
        assert isinstance(workbook_info, WorkbookInfo)
        assert workbook_info.file_path == Path("/test/file.xlsx")
        assert len(mock_reader.validate_file_calls) == 1

        # Test read_excel
        read_result = mock_reader.read_excel("/test/file.xlsx")
        assert isinstance(read_result, ReadResult)
        assert isinstance(read_result.dataframe, pd.DataFrame)
        assert len(mock_reader.read_excel_calls) == 1

        # Test get_sheet_names
        sheet_names = mock_reader.get_sheet_names("/test/file.xlsx")
        assert sheet_names == ["Sheet1", "Sheet2"]
        assert len(mock_reader.get_sheet_names_calls) == 1

    def test_custom_mock_results(self):
        """Test MockExcelReader with custom results."""
        custom_workbook_info = WorkbookInfo(
            file_path=Path("/custom/file.xlsx"),
            sheet_names=["CustomSheet"],
            has_macros=True,
            has_external_links=False,
            file_size=2048,
            format_type=".xlsm",
        )

        custom_df = pd.DataFrame({"Custom": [1, 2, 3]})
        custom_read_result = ReadResult(
            dataframe=custom_df,
            workbook_info=custom_workbook_info,
            sheet_name="CustomSheet",
            metadata={"custom": True},
        )

        mock_reader = MockExcelReader(
            mock_workbook_info=custom_workbook_info,
            mock_read_result=custom_read_result,
            mock_sheet_names=["CustomSheet", "OtherSheet"],
        )

        # Test custom results
        workbook_info = mock_reader.validate_file("/test.xlsx")
        assert workbook_info.has_macros is True
        assert workbook_info.sheet_names == ["CustomSheet"]

        read_result = mock_reader.read_excel("/test.xlsx")
        assert read_result.metadata["custom"] is True

        sheet_names = mock_reader.get_sheet_names("/test.xlsx")
        assert sheet_names == ["CustomSheet", "OtherSheet"]

    def test_mock_error_behavior(self):
        """Test MockExcelReader error simulation."""
        mock_reader = MockExcelReader(should_fail=True)

        with pytest.raises(ExcelProcessingError):
            mock_reader.validate_file("/test.xlsx")

        with pytest.raises(ExcelProcessingError):
            mock_reader.read_excel("/test.xlsx")

        with pytest.raises(ExcelProcessingError):
            mock_reader.get_sheet_names("/test.xlsx")

    def test_call_tracking(self):
        """Test call tracking functionality."""
        mock_reader = MockExcelReader()

        # Make multiple calls
        mock_reader.validate_file("/file1.xlsx")
        mock_reader.validate_file("/file2.xlsx")
        mock_reader.read_excel("/file1.xlsx", sheet_name="Sheet1")
        mock_reader.read_excel("/file2.xlsx", sheet_index=1)
        mock_reader.get_sheet_names("/file1.xlsx")

        # Verify tracking (read_excel calls validate_file internally, so total calls = 2 + 2 = 4)
        assert len(mock_reader.validate_file_calls) == 4  # 2 direct + 2 from read_excel
        assert mock_reader.validate_file_calls[0]["file_path"] == "/file1.xlsx"
        assert mock_reader.validate_file_calls[1]["file_path"] == "/file2.xlsx"

        assert len(mock_reader.read_excel_calls) == 2
        assert mock_reader.read_excel_calls[0]["sheet_name"] == "Sheet1"
        assert mock_reader.read_excel_calls[1]["sheet_index"] == 1

        assert len(mock_reader.get_sheet_names_calls) == 1


class TestInterface:
    """Test interface implementation."""

    def test_interface_compliance(self):
        """Test that all readers implement IExcelReader."""
        readers = [ExcelReader(), MockExcelReader()]

        for reader in readers:
            assert isinstance(reader, IExcelReader)
            assert hasattr(reader, "validate_file")
            assert hasattr(reader, "read_excel")
            assert hasattr(reader, "get_sheet_names")

    def test_polymorphic_usage(self):
        """Test polymorphic usage of different reader implementations."""

        def process_excel(reader: IExcelReader, file_path: str) -> ReadResult:
            """Function that accepts any IExcelReader implementation."""
            reader.validate_file(file_path)  # Just validate, don't store result
            sheet_names = reader.get_sheet_names(file_path)
            return reader.read_excel(file_path, sheet_name=sheet_names[0])

        # Test with mock reader (real reader would need actual files)
        mock_reader = MockExcelReader()
        result = process_excel(mock_reader, "/test.xlsx")
        assert isinstance(result, ReadResult)


class TestIntegration:
    """Integration tests with temporary files."""

    def test_with_temporary_excel_file(self):
        """Test with actual temporary Excel file."""
        # Create a simple DataFrame and save as Excel
        df = pd.DataFrame(
            {
                "Name": ["Alice", "Bob", "Charlie"],
                "Age": [25, 30, 35],
                "City": ["Tokyo", "Osaka", "Kyoto"],
            }
        )

        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)
            df.to_excel(tmp_path, index=False, sheet_name="TestSheet")

        try:
            reader = ExcelReader(enable_security_validation=False)

            # Test validation
            workbook_info = reader.validate_file(tmp_path)
            assert workbook_info.format_type == ".xlsx"
            assert "TestSheet" in workbook_info.sheet_names

            # Test sheet names
            sheet_names = reader.get_sheet_names(tmp_path)
            assert "TestSheet" in sheet_names

            # Test reading
            read_result = reader.read_excel(tmp_path, sheet_name="TestSheet")
            assert isinstance(read_result.dataframe, pd.DataFrame)
            assert read_result.sheet_name == "TestSheet"

        finally:
            tmp_path.unlink()

    def test_error_handling_with_invalid_file(self):
        """Test error handling with invalid file."""
        reader = ExcelReader()

        # Test with non-existent file
        with pytest.raises(ExcelFileNotFoundError):
            reader.validate_file("/nonexistent/file.xlsx")

        # Test with text file instead of Excel
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)
            tmp_file.write(b"Not an Excel file")

        try:
            with pytest.raises(ExcelProcessingError):
                reader.validate_file(tmp_path)
        finally:
            tmp_path.unlink()


class TestErrorScenarios:
    """Test various error scenarios."""

    def setup_method(self):
        """Set up test fixtures."""
        self.reader = ExcelReader()

    @patch("sphinxcontrib.jsontable.core.excel_reader.load_workbook")
    def test_workbook_loading_error(self, mock_load_workbook):
        """Test error handling when workbook loading fails."""
        mock_load_workbook.side_effect = Exception("Corrupted file")

        # Create a valid file for path validation
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)

        try:
            with pytest.raises(ExcelProcessingError, match="Failed to load workbook"):
                self.reader.validate_file(tmp_path)
        finally:
            tmp_path.unlink()

    @patch("pandas.read_excel")
    def test_pandas_reading_error(self, mock_read_excel):
        """Test error handling when pandas reading fails."""
        mock_read_excel.side_effect = Exception("Pandas read error")

        # Mock successful validation
        mock_reader = MockExcelReader()
        reader = ExcelReader()
        reader.validate_file = mock_reader.validate_file

        with pytest.raises(ExcelProcessingError, match="Failed to read Excel data"):
            reader.read_excel("/test.xlsx")

    @patch("pandas.ExcelFile")
    def test_sheet_names_error(self, mock_excel_file):
        """Test error handling when getting sheet names fails."""
        mock_excel_file.side_effect = Exception("Cannot read file structure")

        with pytest.raises(ExcelProcessingError, match="Failed to get sheet names"):
            self.reader.get_sheet_names("/test.xlsx")
