"""Excel Processor Tests - Phase 3.1 Coverage Boost."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from sphinxcontrib.jsontable.directives.excel_processor import ExcelProcessor
from sphinxcontrib.jsontable.directives.validators import JsonTableError


class TestExcelProcessor:
    """Test suite for ExcelProcessor to boost coverage."""

    @patch(
        "sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelDataLoaderFacade"
    )
    def test_init_success(self, mock_facade_class):
        """Test successful initialization."""
        mock_facade = Mock()
        mock_facade_class.return_value = mock_facade

        base_path = Path("/test")
        processor = ExcelProcessor(base_path)

        assert processor.base_path == base_path
        assert processor.excel_loader == mock_facade
        assert processor._cache == {}

    def test_init_import_error(self):
        """Test initialization failure due to import error."""
        with patch(
            "sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelDataLoaderFacade",
            side_effect=ImportError("pandas not found"),
        ):
            with pytest.raises(JsonTableError, match="Excel support not available"):
                ExcelProcessor(Path("/test"))

    @patch(
        "sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelDataLoaderFacade"
    )
    def test_validate_file_path_none(self, mock_facade_class):
        """Test file path validation with None."""
        processor = ExcelProcessor(Path("/test"))

        with pytest.raises(JsonTableError, match="File path cannot be None"):
            processor._validate_file_path(None)

    @patch(
        "sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelDataLoaderFacade"
    )
    def test_validate_file_path_empty(self, mock_facade_class):
        """Test file path validation with empty string."""
        processor = ExcelProcessor(Path("/test"))

        with pytest.raises(JsonTableError, match="File path cannot be empty"):
            processor._validate_file_path("")

    @patch(
        "sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelDataLoaderFacade"
    )
    def test_validate_options_none(self, mock_facade_class):
        """Test options validation with None."""
        processor = ExcelProcessor(Path("/test"))

        result = processor._validate_options(None)
        assert result == {}

    @patch(
        "sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelDataLoaderFacade"
    )
    def test_validate_options_invalid_type(self, mock_facade_class):
        """Test options validation with invalid type."""
        processor = ExcelProcessor(Path("/test"))

        with pytest.raises(JsonTableError, match="Options must be a dictionary"):
            processor._validate_options("invalid")

    @patch(
        "sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelDataLoaderFacade"
    )
    def test_clear_cache(self, mock_facade_class):
        """Test cache clearing."""
        processor = ExcelProcessor(Path("/test"))

        # Add something to cache
        processor._cache["test_key"] = "test_value"
        assert len(processor._cache) == 1

        # Clear cache
        processor.clear_cache()
        assert len(processor._cache) == 0

    @patch(
        "sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelDataLoaderFacade"
    )
    def test_resolve_file_path_empty(self, mock_facade_class):
        """Test file path resolution with empty path."""
        processor = ExcelProcessor(Path("/test"))

        with pytest.raises(JsonTableError, match="File path cannot be None or empty"):
            processor._resolve_file_path("")

    @patch(
        "sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelDataLoaderFacade"
    )
    def test_resolve_file_path_traversal_attack(self, mock_facade_class):
        """Test file path resolution with path traversal."""
        processor = ExcelProcessor(Path("/test"))

        with pytest.raises(JsonTableError, match="Path traversal detected"):
            processor._resolve_file_path("../../../etc/passwd")

    @patch(
        "sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelDataLoaderFacade"
    )
    def test_load_excel_data_basic(self, mock_facade_class):
        """Test basic Excel data loading."""
        mock_facade = Mock()
        mock_facade_class.return_value = mock_facade
        mock_facade.load_from_excel.return_value = {
            "data": [["Name", "Age"], ["Alice", "30"], ["Bob", "25"]]
        }

        processor = ExcelProcessor(Path("/test"))

        result = processor.load_excel_data("test.xlsx", {})

        expected_data = [["Name", "Age"], ["Alice", "30"], ["Bob", "25"]]
        assert result == expected_data

    @patch(
        "sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelDataLoaderFacade"
    )
    def test_load_excel_data_with_cache(self, mock_facade_class):
        """Test Excel data loading with cache enabled."""
        mock_facade = Mock()
        mock_facade_class.return_value = mock_facade
        mock_facade.load_from_excel.return_value = {"data": [["Cached", "Data"]]}

        processor = ExcelProcessor(Path("/test"))

        options = {"json-cache": True}
        result = processor.load_excel_data("test.xlsx", options)

        assert result == [["Cached", "Data"]]

    @patch(
        "sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelDataLoaderFacade"
    )
    def test_load_excel_data_invalid_file_path(self, mock_facade_class):
        """Test Excel data loading with invalid file path."""
        processor = ExcelProcessor(Path("/test"))

        with pytest.raises(JsonTableError, match="File path cannot be None"):
            processor.load_excel_data(None, {})

    @patch(
        "sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelDataLoaderFacade"
    )
    def test_load_excel_data_excel_loader_error(self, mock_facade_class):
        """Test Excel data loading with excel loader error."""
        mock_facade = Mock()
        mock_facade_class.return_value = mock_facade
        mock_facade.load_from_excel.side_effect = Exception("Excel loading failed")

        processor = ExcelProcessor(Path("/test"))

        with pytest.raises(JsonTableError, match="Excel file processing failed"):
            processor.load_excel_data("test.xlsx", {})
