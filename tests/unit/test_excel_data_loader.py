"""Excel Data Loader Tests - Phase 3.2 Coverage Boost.

Tests for excel_data_loader.py to boost coverage from 0% to 40%+.
"""

from pathlib import Path
from unittest.mock import Mock, patch

from sphinxcontrib.jsontable.excel_data_loader import ExcelDataLoader


class TestExcelDataLoader:
    """Test suite for ExcelDataLoader legacy API."""

    def test_init_default(self):
        """Test default initialization."""
        with patch("sphinxcontrib.jsontable.excel_data_loader.ExcelDataLoaderFacade"):
            loader = ExcelDataLoader()
            assert loader.base_path == Path.cwd()
            assert loader._facade is None  # Lazy initialization
            assert loader.encoding == "utf-8"
            assert loader.MAX_FILE_SIZE == 100 * 1024 * 1024
            assert loader.SUPPORTED_EXTENSIONS == {".xlsx", ".xls", ".xlsm", ".xltm"}

    def test_init_with_base_path_string(self):
        """Test initialization with string base path."""
        with patch("sphinxcontrib.jsontable.excel_data_loader.ExcelDataLoaderFacade"):
            base_path = "/test/path"
            loader = ExcelDataLoader(base_path=base_path)
            assert loader.base_path == Path(base_path)

    def test_init_with_base_path_pathlib(self):
        """Test initialization with Path base path."""
        with patch("sphinxcontrib.jsontable.excel_data_loader.ExcelDataLoaderFacade"):
            base_path = Path("/test/path")
            loader = ExcelDataLoader(base_path=base_path)
            assert loader.base_path == base_path

    def test_init_with_empty_base_path(self):
        """Test initialization with empty base path."""
        with patch("sphinxcontrib.jsontable.excel_data_loader.ExcelDataLoaderFacade"):
            loader = ExcelDataLoader(base_path="")
            assert loader.base_path == Path.cwd()

    def test_init_with_lazy_init_false(self):
        """Test initialization without lazy loading."""
        with patch(
            "sphinxcontrib.jsontable.excel_data_loader.ExcelDataLoaderFacade"
        ) as mock_facade:
            mock_instance = Mock()
            mock_facade.return_value = mock_instance

            loader = ExcelDataLoader(lazy_init=False)
            assert loader._facade == mock_instance
            mock_facade.assert_called_once_with(
                enable_security=True, enable_error_handling=True
            )

    def test_init_with_lazy_init_true(self):
        """Test initialization with lazy loading (default)."""
        with patch("sphinxcontrib.jsontable.excel_data_loader.ExcelDataLoaderFacade"):
            loader = ExcelDataLoader(lazy_init=True)
            assert loader._facade is None

    def test_initialize_facade(self):
        """Test facade initialization."""
        with patch(
            "sphinxcontrib.jsontable.excel_data_loader.ExcelDataLoaderFacade"
        ) as mock_facade:
            mock_instance = Mock()
            mock_facade.return_value = mock_instance

            loader = ExcelDataLoader()
            loader._initialize_facade()

            assert loader._facade == mock_instance
            mock_facade.assert_called_once_with(
                enable_security=True, enable_error_handling=True
            )

    def test_initialize_facade_already_initialized(self):
        """Test facade initialization when already initialized."""
        with patch(
            "sphinxcontrib.jsontable.excel_data_loader.ExcelDataLoaderFacade"
        ) as mock_facade:
            loader = ExcelDataLoader()
            loader._facade = Mock()  # Pre-set facade

            loader._initialize_facade()

            # Should not create new facade
            mock_facade.assert_not_called()

    def test_facade_property_lazy_initialization(self):
        """Test facade property with lazy initialization."""
        with patch(
            "sphinxcontrib.jsontable.excel_data_loader.ExcelDataLoaderFacade"
        ) as mock_facade:
            mock_instance = Mock()
            mock_facade.return_value = mock_instance

            loader = ExcelDataLoader()
            assert loader._facade is None

            # First access should initialize
            facade = loader.facade
            assert facade == mock_instance
            assert loader._facade == mock_instance
            mock_facade.assert_called_once()

    def test_facade_property_already_initialized(self):
        """Test facade property when already initialized."""
        with patch("sphinxcontrib.jsontable.excel_data_loader.ExcelDataLoaderFacade"):
            loader = ExcelDataLoader()
            mock_facade_instance = Mock()
            loader._facade = mock_facade_instance

            facade = loader.facade
            assert facade == mock_facade_instance

    def test_resolve_path_absolute(self):
        """Test path resolution with absolute path."""
        with patch("sphinxcontrib.jsontable.excel_data_loader.ExcelDataLoaderFacade"):
            loader = ExcelDataLoader(base_path="/base")

            absolute_path = "/absolute/path/file.xlsx"
            result = loader._resolve_path(absolute_path)

            assert result == Path(absolute_path)
            assert result.is_absolute()

    def test_resolve_path_relative_string(self):
        """Test path resolution with relative string path."""
        with patch("sphinxcontrib.jsontable.excel_data_loader.ExcelDataLoaderFacade"):
            base_path = Path("/base")
            loader = ExcelDataLoader(base_path=base_path)

            relative_path = "relative/file.xlsx"
            result = loader._resolve_path(relative_path)

            expected = base_path / relative_path
            assert result == expected

    def test_resolve_path_relative_pathlib(self):
        """Test path resolution with relative Path object."""
        with patch("sphinxcontrib.jsontable.excel_data_loader.ExcelDataLoaderFacade"):
            base_path = Path("/base")
            loader = ExcelDataLoader(base_path=base_path)

            relative_path = Path("relative/file.xlsx")
            result = loader._resolve_path(relative_path)

            expected = base_path / relative_path
            assert result == expected

    def test_load_from_excel(self):
        """Test load_from_excel method."""
        with patch(
            "sphinxcontrib.jsontable.excel_data_loader.ExcelDataLoaderFacade"
        ) as mock_facade_class:
            mock_facade = Mock()
            mock_facade_class.return_value = mock_facade
            mock_facade.load_from_excel.return_value = {"data": [["test"]]}

            loader = ExcelDataLoader(base_path="/base")
            result = loader.load_from_excel("test.xlsx", sheet="Sheet1")

            expected_path = Path("/base/test.xlsx")
            mock_facade.load_from_excel.assert_called_once_with(
                expected_path, sheet="Sheet1"
            )
            assert result == {"data": [["test"]]}

    def test_load_from_excel_with_detect_range(self):
        """Test load_from_excel_with_detect_range method."""
        with patch(
            "sphinxcontrib.jsontable.excel_data_loader.ExcelDataLoaderFacade"
        ) as mock_facade_class:
            mock_facade = Mock()
            mock_facade_class.return_value = mock_facade
            mock_facade.load_from_excel_with_detect_range.return_value = {
                "data": [["test"]]
            }

            loader = ExcelDataLoader(base_path="/base")
            result = loader.load_from_excel_with_detect_range(
                "test.xlsx", detect_range="A1:C10"
            )

            expected_path = Path("/base/test.xlsx")
            mock_facade.load_from_excel_with_detect_range.assert_called_once_with(
                expected_path, "A1:C10"
            )
            assert result == {"data": [["test"]]}

    def test_load_from_excel_with_skip_rows_range_and_header(self):
        """Test load_from_excel_with_skip_rows_range_and_header method."""
        with patch(
            "sphinxcontrib.jsontable.excel_data_loader.ExcelDataLoaderFacade"
        ) as mock_facade_class:
            mock_facade = Mock()
            mock_facade_class.return_value = mock_facade
            mock_facade.load_from_excel_with_skip_rows_range_and_header.return_value = {
                "data": [["test"]]
            }

            loader = ExcelDataLoader(base_path="/base")
            result = loader.load_from_excel_with_skip_rows_range_and_header(
                "test.xlsx", skip_rows=2, range_spec="A1:C10", header_row=0
            )

            expected_path = Path("/base/test.xlsx")
            mock_facade.load_from_excel_with_skip_rows_range_and_header.assert_called_once_with(
                expected_path, 2, "A1:C10", 0
            )
            assert result == {"data": [["test"]]}

    def test_load_from_excel_with_header_row(self):
        """Test load_from_excel_with_header_row method."""
        with patch(
            "sphinxcontrib.jsontable.excel_data_loader.ExcelDataLoaderFacade"
        ) as mock_facade_class:
            mock_facade = Mock()
            mock_facade_class.return_value = mock_facade
            mock_facade.load_from_excel_with_header_row.return_value = {
                "data": [["test"]]
            }

            loader = ExcelDataLoader(base_path="/base")
            result = loader.load_from_excel_with_header_row("test.xlsx", header_row=1)

            expected_path = Path("/base/test.xlsx")
            mock_facade.load_from_excel_with_header_row.assert_called_once_with(
                expected_path, 1
            )
            assert result == {"data": [["test"]]}

    def test_load_from_excel_with_range(self):
        """Test load_from_excel_with_range method."""
        with patch(
            "sphinxcontrib.jsontable.excel_data_loader.ExcelDataLoaderFacade"
        ) as mock_facade_class:
            mock_facade = Mock()
            mock_facade_class.return_value = mock_facade
            mock_facade.load_from_excel_with_range.return_value = {"data": [["test"]]}

            loader = ExcelDataLoader(base_path="/base")
            result = loader.load_from_excel_with_range("test.xlsx", range_spec="B2:D20")

            expected_path = Path("/base/test.xlsx")
            mock_facade.load_from_excel_with_range.assert_called_once_with(
                expected_path, "B2:D20"
            )
            assert result == {"data": [["test"]]}

    def test_load_from_excel_with_skip_rows(self):
        """Test load_from_excel_with_skip_rows method."""
        with patch(
            "sphinxcontrib.jsontable.excel_data_loader.ExcelDataLoaderFacade"
        ) as mock_facade_class:
            mock_facade = Mock()
            mock_facade_class.return_value = mock_facade
            mock_facade.load_from_excel_with_skip_rows.return_value = {
                "data": [["test"]]
            }

            loader = ExcelDataLoader(base_path="/base")
            result = loader.load_from_excel_with_skip_rows("test.xlsx", skip_rows=3)

            expected_path = Path("/base/test.xlsx")
            mock_facade.load_from_excel_with_skip_rows.assert_called_once_with(
                expected_path, 3
            )
            assert result == {"data": [["test"]]}

    def test_get_sheet_names(self):
        """Test get_sheet_names method."""
        with patch(
            "sphinxcontrib.jsontable.excel_data_loader.ExcelDataLoaderFacade"
        ) as mock_facade_class:
            mock_facade = Mock()
            mock_facade_class.return_value = mock_facade
            mock_facade.get_sheet_names.return_value = ["Sheet1", "Sheet2", "Data"]

            loader = ExcelDataLoader(base_path="/base")
            result = loader.get_sheet_names("test.xlsx")

            expected_path = Path("/base/test.xlsx")
            mock_facade.get_sheet_names.assert_called_once_with(expected_path)
            assert result == ["Sheet1", "Sheet2", "Data"]

    def test_get_workbook_info(self):
        """Test get_workbook_info method."""
        with patch(
            "sphinxcontrib.jsontable.excel_data_loader.ExcelDataLoaderFacade"
        ) as mock_facade_class:
            mock_facade = Mock()
            mock_facade_class.return_value = mock_facade
            mock_facade.get_workbook_info.return_value = {
                "sheets": 3,
                "file_size": 1024,
            }

            loader = ExcelDataLoader(base_path="/base")
            result = loader.get_workbook_info("test.xlsx")

            expected_path = Path("/base/test.xlsx")
            mock_facade.get_workbook_info.assert_called_once_with(expected_path)
            assert result == {"sheets": 3, "file_size": 1024}

    def test_load_excel_legacy_alias(self):
        """Test load_excel legacy method alias."""
        with patch(
            "sphinxcontrib.jsontable.excel_data_loader.ExcelDataLoaderFacade"
        ) as mock_facade_class:
            mock_facade = Mock()
            mock_facade_class.return_value = mock_facade
            mock_facade.load_from_excel.return_value = {"data": [["legacy"]]}

            loader = ExcelDataLoader(base_path="/base")
            result = loader.load_excel("test.xlsx", option="value")

            expected_path = Path("/base/test.xlsx")
            mock_facade.load_from_excel.assert_called_once_with(
                expected_path, option="value"
            )
            assert result == {"data": [["legacy"]]}

    def test_read_excel_legacy_alias(self):
        """Test read_excel legacy method alias."""
        with patch(
            "sphinxcontrib.jsontable.excel_data_loader.ExcelDataLoaderFacade"
        ) as mock_facade_class:
            mock_facade = Mock()
            mock_facade_class.return_value = mock_facade
            mock_facade.load_from_excel.return_value = {"data": [["legacy"]]}

            loader = ExcelDataLoader(base_path="/base")
            result = loader.read_excel("test.xlsx", legacy_param="test")

            expected_path = Path("/base/test.xlsx")
            mock_facade.load_from_excel.assert_called_once_with(
                expected_path, legacy_param="test"
            )
            assert result == {"data": [["legacy"]]}

    def test_constants_values(self):
        """Test that constants have expected values."""
        with patch("sphinxcontrib.jsontable.excel_data_loader.ExcelDataLoaderFacade"):
            loader = ExcelDataLoader()

            assert loader.encoding == "utf-8"
            assert loader.MAX_FILE_SIZE == 100 * 1024 * 1024  # 100MB
            assert loader.SUPPORTED_EXTENSIONS == {".xlsx", ".xls", ".xlsm", ".xltm"}

    def test_multiple_facade_property_access(self):
        """Test multiple facade property accesses use same instance."""
        with patch(
            "sphinxcontrib.jsontable.excel_data_loader.ExcelDataLoaderFacade"
        ) as mock_facade_class:
            mock_instance = Mock()
            mock_facade_class.return_value = mock_instance

            loader = ExcelDataLoader()

            facade1 = loader.facade
            facade2 = loader.facade

            assert facade1 == facade2 == mock_instance
            # Should only be called once due to lazy initialization
            mock_facade_class.assert_called_once()

    def test_path_resolution_with_various_inputs(self):
        """Test path resolution with various input types."""
        with patch("sphinxcontrib.jsontable.excel_data_loader.ExcelDataLoaderFacade"):
            loader = ExcelDataLoader(base_path="/base")

            # Test different input types
            test_cases = [
                ("file.xlsx", "/base/file.xlsx"),
                ("subdir/file.xlsx", "/base/subdir/file.xlsx"),
                (Path("file.xlsx"), "/base/file.xlsx"),
                ("/absolute/file.xlsx", "/absolute/file.xlsx"),
                (Path("/absolute/file.xlsx"), "/absolute/file.xlsx"),
            ]

            for input_path, expected_str in test_cases:
                result = loader._resolve_path(input_path)
                assert str(result) == expected_str
