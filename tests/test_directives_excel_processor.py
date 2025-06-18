"""
Comprehensive unit tests for directives.excel_processor module.

This test suite provides complete coverage for ExcelProcessor class methods,
following TDD approach and AAA (Arrange-Act-Assert) pattern.
Tests cover normal operation, edge cases, and error scenarios.
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Import the classes and functions to be tested
from sphinxcontrib.jsontable.directives.validators import JsonTableError


class TestExcelProcessor:
    """Test suite for ExcelProcessor class methods."""

    @pytest.fixture
    def mock_excel_loader(self):
        """Create a mock ExcelDataLoaderFacade for testing."""
        mock_loader = Mock()
        # デフォルトの成功レスポンス
        mock_loader.load_from_excel.return_value = {
            "data": [["Name", "Age"], ["Alice", 25], ["Bob", 30]],
            "has_header": True,
            "headers": ["Name", "Age"],
        }
        return mock_loader

    class TestInit:
        """Test suite for ExcelProcessor.__init__ method."""

        @patch(
            "sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelDataLoaderFacade"
        )
        def test_init_with_base_path(self, mock_facade_class):
            """Test initialization with base path."""
            # Import here to avoid import time issues
            from sphinxcontrib.jsontable.directives.excel_processor import (
                ExcelProcessor,
            )

            # Arrange
            base_path = Path("/test/path")
            mock_loader = Mock()
            mock_facade_class.return_value = mock_loader

            # Act
            processor = ExcelProcessor(base_path=base_path)

            # Assert
            assert processor.base_path == base_path
            assert processor.excel_loader == mock_loader
            mock_facade_class.assert_called_once_with(base_path)

        def test_init_excel_support_not_available_raises_error(self):
            """Test initialization when Excel support is not available."""
            # Import here to avoid import time issues
            from sphinxcontrib.jsontable.directives.excel_processor import (
                ExcelProcessor,
            )

            # Arrange & Act & Assert
            # Import error simulation by mocking the module itself
            with patch.dict(
                "sys.modules",
                {"sphinxcontrib.jsontable.facade.excel_data_loader_facade": None},
            ):
                with pytest.raises(JsonTableError) as exc_info:
                    ExcelProcessor(base_path=Path("/test"))
                assert "Excel support not available" in str(exc_info.value)

    class TestJsonConversion:
        """Test suite for JSON conversion functionality."""

        @patch(
            "sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelDataLoaderFacade"
        )
        def test_convert_to_json_with_headers(self, mock_facade_class):
            """Test conversion to JSON format with headers."""
            # Import here to avoid import time issues
            from sphinxcontrib.jsontable.directives.excel_processor import (
                ExcelProcessor,
            )

            # Arrange
            mock_facade_class.return_value = Mock()
            processor = ExcelProcessor(base_path=Path("/test"))
            excel_data = {
                "data": [["Alice", 25], ["Bob", 30]],
                "has_header": True,
                "headers": ["Name", "Age"],
            }

            # Act
            result = processor._convert_to_json(excel_data)

            # Assert
            expected = [{"Name": "Alice", "Age": 25}, {"Name": "Bob", "Age": 30}]
            assert result == expected

        @patch(
            "sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelDataLoaderFacade"
        )
        def test_convert_to_json_without_headers(self, mock_facade_class):
            """Test conversion to JSON format without headers."""
            # Import here to avoid import time issues
            from sphinxcontrib.jsontable.directives.excel_processor import (
                ExcelProcessor,
            )

            # Arrange
            mock_facade_class.return_value = Mock()
            processor = ExcelProcessor(base_path=Path("/test"))
            excel_data = {"data": [["Alice", 25], ["Bob", 30]], "has_header": False}

            # Act
            result = processor._convert_to_json(excel_data)

            # Assert
            expected = [["Alice", 25], ["Bob", 30]]
            assert result == expected

        @patch(
            "sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelDataLoaderFacade"
        )
        def test_convert_to_json_empty_data(self, mock_facade_class):
            """Test conversion with empty data."""
            # Import here to avoid import time issues
            from sphinxcontrib.jsontable.directives.excel_processor import (
                ExcelProcessor,
            )

            # Arrange
            mock_facade_class.return_value = Mock()
            processor = ExcelProcessor(base_path=Path("/test"))
            excel_data = {"data": [], "has_header": False}

            # Act
            result = processor._convert_to_json(excel_data)

            # Assert
            assert result == []

    class TestLoadExcelData:
        """Test suite for load_excel_data method."""

        @patch(
            "sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelDataLoaderFacade"
        )
        def test_load_excel_data_basic_success(self, mock_facade_class):
            """Test basic successful Excel data loading."""
            # Import here to avoid import time issues
            from sphinxcontrib.jsontable.directives.excel_processor import (
                ExcelProcessor,
            )

            # Arrange
            mock_excel_loader = Mock()
            mock_excel_loader.load_from_excel.return_value = {
                "data": [["Alice", 25], ["Bob", 30]],
                "has_header": True,
                "headers": ["Name", "Age"],
            }
            mock_facade_class.return_value = mock_excel_loader

            processor = ExcelProcessor(base_path=Path("/test"))
            file_path = "data/test.xlsx"
            options = {}

            # Act
            result = processor.load_excel_data(file_path, options)

            # Assert
            expected = [{"Name": "Alice", "Age": 25}, {"Name": "Bob", "Age": 30}]
            assert result == expected

        @patch(
            "sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelDataLoaderFacade"
        )
        def test_load_excel_data_with_excel_loader_error(self, mock_facade_class):
            """Test Excel data loading when excel_loader raises an error."""
            # Import here to avoid import time issues
            from sphinxcontrib.jsontable.directives.excel_processor import (
                ExcelProcessor,
            )

            # Arrange
            mock_excel_loader = Mock()
            mock_excel_loader.load_from_excel.side_effect = Exception(
                "Excel file corrupted"
            )
            mock_facade_class.return_value = mock_excel_loader

            processor = ExcelProcessor(base_path=Path("/test"))
            file_path = "data/invalid.xlsx"
            options = {}

            # Act & Assert
            with pytest.raises(JsonTableError) as exc_info:
                processor.load_excel_data(file_path, options)
            assert "Failed to load Excel file" in str(exc_info.value)

    class TestResolveSheetName:
        """Test suite for _resolve_sheet_name method."""

        @patch(
            "sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelDataLoaderFacade"
        )
        def test_resolve_sheet_name_with_sheet_name_priority(self, mock_facade_class):
            """Test _resolve_sheet_name with sheet_name taking priority."""
            # Import here to avoid import time issues
            from sphinxcontrib.jsontable.directives.excel_processor import (
                ExcelProcessor,
            )

            # Arrange
            mock_facade_class.return_value = Mock()
            processor = ExcelProcessor(base_path=Path("/test"))
            file_path = "/test/file.xlsx"
            sheet_name = "Sheet1"
            sheet_index = 2

            # Act
            result = processor._resolve_sheet_name(file_path, sheet_name, sheet_index)

            # Assert
            assert result == sheet_name

        @patch(
            "sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelDataLoaderFacade"
        )
        def test_resolve_sheet_name_with_defaults(self, mock_facade_class):
            """Test _resolve_sheet_name with no options returns None."""
            # Import here to avoid import time issues
            from sphinxcontrib.jsontable.directives.excel_processor import (
                ExcelProcessor,
            )

            # Arrange
            mock_facade_class.return_value = Mock()
            processor = ExcelProcessor(base_path=Path("/test"))
            file_path = "/test/file.xlsx"

            # Act
            result = processor._resolve_sheet_name(file_path, None, None)

            # Assert
            assert result is None

    class TestIntegration:
        """Integration tests for ExcelProcessor."""

        @patch(
            "sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelDataLoaderFacade"
        )
        def test_full_excel_processing_workflow(self, mock_facade_class):
            """Test complete Excel processing workflow."""
            # Import here to avoid import time issues
            from sphinxcontrib.jsontable.directives.excel_processor import (
                ExcelProcessor,
            )

            # Arrange
            mock_excel_loader = Mock()
            mock_excel_loader.load_from_excel_with_header_row_and_range.return_value = {
                "data": [
                    ["Alice Johnson", 28, "Software Engineer"],
                    ["Bob Smith", 32, "Product Manager"],
                    ["Carol Davis", 26, "UX Designer"],
                ],
                "has_header": True,
                "headers": ["Name", "Age", "Position"],
            }
            mock_facade_class.return_value = mock_excel_loader

            processor = ExcelProcessor(base_path=Path("/test"))
            file_path = "data/employees.xlsx"
            options = {"sheet": "Employees", "header-row": 1, "range": "A1:C100"}

            # Act
            result = processor.load_excel_data(file_path, options)

            # Assert
            assert len(result) == 3
            assert result[0]["Name"] == "Alice Johnson"
            assert result[0]["Age"] == 28
            assert result[0]["Position"] == "Software Engineer"
            assert result[1]["Name"] == "Bob Smith"
            assert result[2]["Name"] == "Carol Davis"
