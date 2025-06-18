"""Excel Data Loader Facade Tests - Phase 3.1 Coverage Boost.

Tests for excel_data_loader_facade.py to boost coverage in facade module.
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from sphinxcontrib.jsontable.facade.excel_data_loader_facade import (
    ExcelDataLoaderFacade,
)


class TestExcelDataLoaderFacadeFixed:
    """Test suite for ExcelDataLoaderFacade to boost coverage."""

    def test_init_default(self):
        """Test default initialization."""
        with patch(
            "sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelProcessingPipeline"
        ), patch(
            "sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelUtilities"
        ):
            facade = ExcelDataLoaderFacade()
            assert facade is not None

    def test_init_with_options(self):
        """Test initialization with options."""
        with patch(
            "sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelProcessingPipeline"
        ), patch(
            "sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelUtilities"
        ):
            facade = ExcelDataLoaderFacade(
                enable_security=True, enable_error_handling=True
            )
            assert facade is not None
            assert facade.enable_security is True
            assert facade.enable_error_handling is True

    def test_load_from_excel_basic(self):
        """Test basic Excel loading."""
        with patch(
            "sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelProcessingPipeline"
        ) as mock_pipeline_class, patch(
            "sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelUtilities"
        ):
            mock_pipeline = Mock()
            mock_pipeline_class.return_value = mock_pipeline
            mock_pipeline.process_excel_file.return_value = {
                "success": True,
                "data": [{"col1": "value1"}],
                "metadata": {"rows": 1},
            }

            facade = ExcelDataLoaderFacade()
            file_path = Path("test.xlsx")
            result = facade.load_from_excel(file_path)

            assert isinstance(result, dict)
            assert result.get("success") is True
            mock_pipeline.process_excel_file.assert_called_once_with(
                file_path=file_path,
                sheet_name=None,
                sheet_index=None,
                range_spec=None,
                header_row=None,
            )

    def test_load_from_excel_with_sheet_name(self):
        """Test Excel loading with sheet name."""
        with patch(
            "sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelProcessingPipeline"
        ) as mock_pipeline_class, patch(
            "sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelUtilities"
        ):
            mock_pipeline = Mock()
            mock_pipeline_class.return_value = mock_pipeline
            mock_pipeline.process_excel_file.return_value = {
                "success": True,
                "data": [],
            }

            facade = ExcelDataLoaderFacade()
            file_path = Path("test.xlsx")
            result = facade.load_from_excel(file_path, sheet_name="Sheet2")

            mock_pipeline.process_excel_file.assert_called_with(
                file_path=file_path,
                sheet_name="Sheet2",
                sheet_index=None,
                range_spec=None,
                header_row=None,
            )

    def test_load_from_excel_with_range(self):
        """Test Excel loading with range specification."""
        with patch(
            "sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelProcessingPipeline"
        ) as mock_pipeline_class, patch(
            "sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelUtilities"
        ):
            mock_pipeline = Mock()
            mock_pipeline_class.return_value = mock_pipeline
            mock_pipeline.process_excel_file.return_value = {
                "success": True,
                "data": [],
            }

            facade = ExcelDataLoaderFacade()
            file_path = Path("test.xlsx")
            result = facade.load_from_excel(file_path, range_spec="A1:C10")

            mock_pipeline.process_excel_file.assert_called_with(
                file_path=file_path,
                sheet_name=None,
                sheet_index=None,
                range_spec="A1:C10",
                header_row=None,
            )

    def test_utility_methods(self):
        """Test utility methods."""
        with patch(
            "sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelProcessingPipeline"
        ), patch(
            "sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelUtilities"
        ) as mock_utilities_class:
            mock_utilities = Mock()
            mock_utilities_class.return_value = mock_utilities
            mock_utilities.validate_excel_file.return_value = {"valid": True}
            mock_utilities.get_sheet_names.return_value = ["Sheet1", "Sheet2"]
            mock_utilities.get_workbook_info.return_value = {"sheets": 2}
            mock_utilities.is_safe_path.return_value = True

            facade = ExcelDataLoaderFacade()
            file_path = Path("test.xlsx")

            # Test validate_excel_file
            result = facade.validate_excel_file(file_path)
            assert result == {"valid": True}
            mock_utilities.validate_excel_file.assert_called_with(file_path)

            # Test get_sheet_names
            result = facade.get_sheet_names(file_path)
            assert result == ["Sheet1", "Sheet2"]
            mock_utilities.get_sheet_names.assert_called_with(file_path)

            # Test get_workbook_info
            result = facade.get_workbook_info(file_path)
            assert result == {"sheets": 2}
            mock_utilities.get_workbook_info.assert_called_with(file_path)

            # Test is_safe_path
            result = facade.is_safe_path(file_path)
            assert result is True
            mock_utilities.is_safe_path.assert_called_with(file_path)

    def test_get_components_info(self):
        """Test components info retrieval."""
        with patch(
            "sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelProcessingPipeline"
        ), patch(
            "sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelUtilities"
        ):
            facade = ExcelDataLoaderFacade()
            result = facade.get_components_info()

            assert isinstance(result, dict)
            assert "excel_reader" in result
            assert "data_converter" in result
            assert "range_parser" in result
            assert "security_enabled" in result
            assert "error_handling_enabled" in result

    def test_last_workbook_info_tracking(self):
        """Test last workbook info tracking."""
        with patch(
            "sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelProcessingPipeline"
        ) as mock_pipeline_class, patch(
            "sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelUtilities"
        ):
            mock_pipeline = Mock()
            mock_pipeline_class.return_value = mock_pipeline
            workbook_info = {"file": "test.xlsx", "sheets": 2}
            mock_pipeline.process_excel_file.return_value = {
                "success": True,
                "data": [],
                "metadata": {"workbook_info": workbook_info},
            }

            facade = ExcelDataLoaderFacade()
            file_path = Path("test.xlsx")

            # Initially no workbook info
            assert facade.get_last_workbook_info() is None

            # Load Excel file
            facade.load_from_excel(file_path)

            # Now should have workbook info
            result = facade.get_last_workbook_info()
            assert result == workbook_info

    def test_error_handling(self):
        """Test error handling."""
        with patch(
            "sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelProcessingPipeline"
        ) as mock_pipeline_class, patch(
            "sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelUtilities"
        ):
            mock_pipeline = Mock()
            mock_pipeline_class.return_value = mock_pipeline
            mock_pipeline.process_excel_file.side_effect = Exception("Test error")

            facade = ExcelDataLoaderFacade()
            file_path = Path("test.xlsx")

            with pytest.raises(Exception):
                facade.load_from_excel(file_path)

    def test_detect_headers_method(self):
        """Test detect headers method."""
        with patch(
            "sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelProcessingPipeline"
        ), patch(
            "sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelUtilities"
        ) as mock_utilities_class:
            mock_utilities = Mock()
            mock_utilities_class.return_value = mock_utilities
            mock_utilities.detect_headers.return_value = {"headers": ["col1", "col2"]}

            facade = ExcelDataLoaderFacade()
            mock_dataframe = Mock()

            result = facade.detect_headers(mock_dataframe)
            assert result == {"headers": ["col1", "col2"]}
            mock_utilities.detect_headers.assert_called_with(mock_dataframe)
