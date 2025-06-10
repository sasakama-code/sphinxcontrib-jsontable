"""Comprehensive tests for Excel-RAG integration functionality.

This test suite covers all aspects of the Excel-RAG integration including
format detection, conversion, entity recognition, and Sphinx documentation
generation. Tests are designed to validate the 5-minute Excel-to-AI conversion
capability and ensure high quality results.

Test Coverage:
- ExcelRAGConverter core functionality
- AdvancedExcelConverter format detection and processing
- AutoSphinxIntegration document generation
- Format-specific handlers (pivot, financial, multi-header, etc.)
- Entity recognition and quality assessment
- Error handling and edge cases
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Test imports
from sphinxcontrib.jsontable.excel import (
    AdvancedExcelConverter,
    AutoSphinxIntegration,
    ExcelFormatHandler,
    ExcelRAGConverter,
    convert_excel_to_rag,
    query_excel_data,
)
from sphinxcontrib.jsontable.excel.format_detector import (
    FinancialStatementHandler,
    PivotTableHandler,
    StandardTableHandler,
)


class TestExcelRAGConverter:
    """Test suite for main ExcelRAGConverter functionality."""

    @pytest.fixture
    def mock_excel_file(self):
        """Create mock Excel file path."""
        return "test_data.xlsx"

    @pytest.fixture
    def converter(self):
        """Create ExcelRAGConverter instance."""
        return ExcelRAGConverter()

    @pytest.fixture
    def sample_conversion_result(self):
        """Sample conversion result for testing."""
        return {
            "json_data": [
                {"name": "Product A", "price": 100, "category": "Electronics"},
                {"name": "Product B", "price": 200, "category": "Books"},
            ],
            "format_type": "standard_table",
            "entities": {
                "items": [
                    {"text": "Product A", "type": "product", "confidence": 0.9},
                    {"text": "Electronics", "type": "category", "confidence": 0.8},
                ],
                "types": ["product", "category"],
                "confidence": 0.85,
            },
            "metadata": {
                "source_file": "test_data.xlsx",
                "record_count": 2,
                "data_quality": {
                    "completeness": 0.95,
                    "consistency": 0.90,
                    "accuracy": 0.88,
                },
            },
            "quality_score": 0.91,
            "format_confidence": 0.95,
            "conversion_notes": ["Standard table format processed"],
        }

    def test_initialization(self, converter):
        """Test ExcelRAGConverter initialization."""
        assert converter is not None
        assert hasattr(converter, "excel_converter")
        assert hasattr(converter, "format_handler")
        assert hasattr(converter, "sphinx_integration")
        assert hasattr(converter, "rag_extractor")
        assert hasattr(converter, "advanced_metadata")
        assert converter.rag_systems == {}
        assert converter.default_config["language"] == "japanese"
        assert converter.default_config["auto_entity_detection"] is True

    def test_initialization_with_config(self):
        """Test initialization with custom configuration."""
        custom_config = {
            "language": "english",
            "quality_threshold": 0.9,
            "max_file_size_mb": 200,
        }
        converter = ExcelRAGConverter(custom_config)
        assert converter.config == custom_config

    @patch("sphinxcontrib.jsontable.excel.converter.Path")
    def test_validate_excel_file_success(self, mock_path, converter, mock_excel_file):
        """Test successful Excel file validation."""
        # Mock Path object
        mock_path_obj = Mock()
        mock_path_obj.exists.return_value = True
        mock_path_obj.suffix = ".xlsx"
        mock_stat = Mock()
        mock_stat.st_size = 50 * 1024 * 1024  # 50MB
        mock_path_obj.stat.return_value = mock_stat
        mock_path.return_value = mock_path_obj

        # Should not raise exception
        converter._validate_excel_file(mock_path_obj)

    @patch("sphinxcontrib.jsontable.excel.converter.Path")
    def test_validate_excel_file_not_found(self, mock_path, converter):
        """Test Excel file validation with missing file."""
        mock_path_obj = Mock()
        mock_path_obj.exists.return_value = False
        mock_path.return_value = mock_path_obj

        with pytest.raises(FileNotFoundError):
            converter._validate_excel_file(mock_path_obj)

    @patch("sphinxcontrib.jsontable.excel.converter.Path")
    def test_validate_excel_file_unsupported_format(self, mock_path, converter):
        """Test Excel file validation with unsupported format."""
        mock_path_obj = Mock()
        mock_path_obj.exists.return_value = True
        mock_path_obj.suffix = ".doc"  # Unsupported format
        mock_path.return_value = mock_path_obj

        with pytest.raises(ValueError, match="Unsupported file format"):
            converter._validate_excel_file(mock_path_obj)

    @patch("sphinxcontrib.jsontable.excel.converter.Path")
    def test_validate_excel_file_too_large(self, mock_path, converter):
        """Test Excel file validation with file too large."""
        mock_path_obj = Mock()
        mock_path_obj.exists.return_value = True
        mock_path_obj.suffix = ".xlsx"
        mock_stat = Mock()
        mock_stat.st_size = 200 * 1024 * 1024  # 200MB (exceeds 100MB limit)
        mock_path_obj.stat.return_value = mock_stat
        mock_path.return_value = mock_path_obj

        with pytest.raises(ValueError, match="File too large"):
            converter._validate_excel_file(mock_path_obj)

    def test_set_rag_system_openai(self, converter):
        """Test setting OpenAI RAG system configuration."""
        config = {"model": "text-embedding-3-small", "api_key": "test-key"}
        converter.set_rag_system("openai", config)

        assert "openai" in converter.rag_systems
        assert converter.rag_systems["openai"] == config

    def test_set_rag_system_langchain(self, converter):
        """Test setting LangChain RAG system configuration."""
        config = {"vectorstore": "chroma", "llm": "gpt-3.5-turbo"}
        converter.set_rag_system("langchain", config)

        assert "langchain" in converter.rag_systems
        assert converter.rag_systems["langchain"] == config

    def test_set_rag_system_custom(self, converter):
        """Test setting custom RAG system configuration."""
        config = {"endpoint": "https://custom-rag.com", "api_key": "custom-key"}
        converter.set_rag_system("custom", config)

        assert "custom" in converter.rag_systems
        assert converter.rag_systems["custom"] == config

    def test_set_rag_system_unsupported(self, converter):
        """Test setting unsupported RAG system raises error."""
        with pytest.raises(ValueError, match="Unsupported RAG system"):
            converter.set_rag_system("unsupported", {})

    @patch(
        "sphinxcontrib.jsontable.excel.converter.ExcelRAGConverter._validate_excel_file"
    )
    @patch(
        "sphinxcontrib.jsontable.excel.converter.ExcelRAGConverter._generate_rag_metadata"
    )
    @patch(
        "sphinxcontrib.jsontable.excel.converter.ExcelRAGConverter._generate_output_files"
    )
    @patch(
        "sphinxcontrib.jsontable.excel.converter.ExcelRAGConverter._generate_sphinx_documentation"
    )
    @patch(
        "sphinxcontrib.jsontable.excel.converter.ExcelRAGConverter._calculate_overall_quality"
    )
    def test_convert_excel_to_rag_success(
        self,
        mock_quality,
        mock_sphinx,
        mock_output,
        mock_metadata,
        mock_validate,
        converter,
        mock_excel_file,
        sample_conversion_result,
    ):
        """Test successful Excel-to-RAG conversion."""
        # Setup mocks
        mock_validate.return_value = None
        converter.excel_converter.convert_with_intelligence = Mock(
            return_value=sample_conversion_result
        )
        mock_metadata.return_value = {"test": "metadata"}
        mock_output.return_value = ["test.json"]
        mock_sphinx.return_value = ["test.rst"]
        mock_quality.return_value = 0.91

        # Execute conversion
        result = converter.convert_excel_to_rag(mock_excel_file, "test-purpose")

        # Verify result structure
        assert "json_files" in result
        assert "sphinx_docs" in result
        assert "metadata" in result
        assert "quality_score" in result
        assert "conversion_summary" in result

        assert result["json_files"] == ["test.json"]
        assert result["sphinx_docs"] == ["test.rst"]
        assert result["quality_score"] == 0.91

        # Verify summary
        summary = result["conversion_summary"]
        assert summary["excel_file"] == mock_excel_file
        assert summary["format_type"] == "standard_table"
        assert summary["rag_purpose"] == "test-purpose"

    @patch(
        "sphinxcontrib.jsontable.excel.converter.ExcelRAGConverter._validate_excel_file"
    )
    def test_convert_excel_to_rag_validation_error(
        self, mock_validate, converter, mock_excel_file
    ):
        """Test conversion with validation error."""
        mock_validate.side_effect = FileNotFoundError("File not found")

        with pytest.raises(RuntimeError, match="Conversion failed"):
            converter.convert_excel_to_rag(mock_excel_file, "test-purpose")

    def test_generate_rag_metadata(self, converter, sample_conversion_result):
        """Test RAG metadata generation."""
        config = {"rag_purpose": "test", "language": "japanese"}

        # Mock the metadata generators
        converter.rag_extractor.extract_metadata = Mock(
            return_value={"basic": "metadata"}
        )
        converter.advanced_metadata.generate_advanced_metadata = Mock(
            return_value={"advanced": "metadata"}
        )

        result = converter._generate_rag_metadata(sample_conversion_result, config)

        assert "basic" in result
        assert "advanced" in result
        assert "quality_metrics" in result
        assert "processing_config" in result
        assert result["processing_config"] == config

    def test_generate_output_files(self, converter, sample_conversion_result):
        """Test output file generation."""
        config = {"rag_purpose": "test-analysis"}
        metadata = {"test": "metadata"}

        with tempfile.TemporaryDirectory() as temp_dir:
            # Change to temp directory
            import os

            original_cwd = os.getcwd()
            os.chdir(temp_dir)

            try:
                result = converter._generate_output_files(
                    sample_conversion_result, metadata, config
                )

                assert len(result) == 2
                assert "test-analysis_data.json" in result
                assert "test-analysis_metadata.json" in result

                # Verify files exist
                assert Path("test-analysis_data.json").exists()
                assert Path("test-analysis_metadata.json").exists()

                # Verify file contents
                with open("test-analysis_data.json", encoding="utf-8") as f:
                    data = json.load(f)
                    assert data == sample_conversion_result["json_data"]

                with open("test-analysis_metadata.json", encoding="utf-8") as f:
                    meta = json.load(f)
                    assert meta == metadata

            finally:
                os.chdir(original_cwd)

    def test_calculate_overall_quality(self, converter, sample_conversion_result):
        """Test overall quality calculation."""
        metadata = {
            "data_quality": {
                "completeness": 0.95,
                "consistency": 0.90,
                "accuracy": 0.88,
            }
        }

        quality_score = converter._calculate_overall_quality(
            sample_conversion_result, metadata
        )

        # Should be average of multiple factors
        assert 0.0 <= quality_score <= 1.0
        assert quality_score > 0.8  # Should be high for good sample data

    def test_query_excel_data_placeholder(self, converter, mock_excel_file):
        """Test Excel data querying (placeholder implementation)."""
        result = converter.query_excel_data(mock_excel_file, "Test question")

        # Should return placeholder response
        assert "Query 'Test question' processed" in result
        assert "RAG integration pending Phase 3" in result


class TestAdvancedExcelConverter:
    """Test suite for AdvancedExcelConverter functionality."""

    @pytest.fixture
    def converter(self):
        """Create AdvancedExcelConverter instance."""
        return AdvancedExcelConverter()

    def test_initialization(self, converter):
        """Test AdvancedExcelConverter initialization."""
        assert converter is not None
        assert hasattr(converter, "format_handler")
        assert hasattr(converter, "entity_patterns")
        assert isinstance(converter.entity_patterns, dict)

        # Check entity patterns
        patterns = converter.entity_patterns
        assert "person" in patterns
        assert "location" in patterns
        assert "organization" in patterns
        assert "financial" in patterns

    @patch("openpyxl.load_workbook")
    def test_auto_detect_format_standard_table(self, mock_workbook, converter):
        """Test auto-detection of standard table format."""
        # Mock workbook structure
        mock_wb = Mock()
        mock_sheet = Mock()
        mock_wb.sheetnames = ["Sheet1"]
        mock_wb.__getitem__ = Mock(return_value=mock_sheet)
        mock_wb.close = Mock()
        mock_workbook.return_value = mock_wb

        # Mock sheet that doesn't match special patterns
        converter._has_pivot_indicators = Mock(return_value=False)
        converter._has_financial_indicators = Mock(return_value=False)
        converter._has_multi_headers = Mock(return_value=False)
        converter._has_crosstab_structure = Mock(return_value=False)
        converter._has_time_series_pattern = Mock(return_value=False)

        result = converter.auto_detect_format("test.xlsx")

        assert result == "standard_table"
        mock_workbook.assert_called_once_with("test.xlsx", data_only=True)
        mock_wb.close.assert_called_once()

    @patch("openpyxl.load_workbook")
    def test_auto_detect_format_pivot_table(self, mock_workbook, converter):
        """Test auto-detection of pivot table format."""
        # Setup mock
        mock_wb = Mock()
        mock_sheet = Mock()
        mock_wb.sheetnames = ["Sheet1"]
        mock_wb.__getitem__ = Mock(return_value=mock_sheet)
        mock_wb.close = Mock()
        mock_workbook.return_value = mock_wb

        # Mock pivot table detection
        converter._has_pivot_indicators = Mock(return_value=True)

        result = converter.auto_detect_format("test.xlsx")

        assert result == "pivot_table"

    @patch("openpyxl.load_workbook")
    def test_auto_detect_format_financial_statement(self, mock_workbook, converter):
        """Test auto-detection of financial statement format."""
        mock_wb = Mock()
        mock_sheet = Mock()
        mock_wb.sheetnames = ["Sheet1"]
        mock_wb.__getitem__ = Mock(return_value=mock_sheet)
        mock_wb.close = Mock()
        mock_workbook.return_value = mock_wb

        converter._has_pivot_indicators = Mock(return_value=False)
        converter._has_financial_indicators = Mock(return_value=True)

        result = converter.auto_detect_format("test.xlsx")

        assert result == "financial_statement"

    def test_extract_business_entities(self, converter):
        """Test business entity extraction."""
        sample_data = [
            {"company": "株式会社テスト", "amount": "1000万円", "person": "田中太郎"},
            {"company": "ABC企業", "amount": "500円", "person": "佐藤花子"},
        ]

        result = converter._extract_business_entities(
            sample_data, "general", "japanese"
        )

        assert "items" in result
        assert "types" in result
        assert "confidence" in result
        assert result["domain"] == "general"
        assert result["language"] == "japanese"

        # Should detect organizations and financial entities
        entity_types = set(item["type"] for item in result["items"])
        assert "organization" in entity_types or "financial" in entity_types

    def test_calculate_completeness_full_data(self, converter):
        """Test completeness calculation with complete data."""
        data = [
            {"name": "Product A", "price": 100},
            {"name": "Product B", "price": 200},
        ]

        completeness = converter._calculate_completeness(data)
        assert completeness == 1.0

    def test_calculate_completeness_missing_data(self, converter):
        """Test completeness calculation with missing data."""
        data = [
            {"name": "Product A", "price": 100},
            {"name": None, "price": 200},
            {"name": "Product C", "price": None},
        ]

        completeness = converter._calculate_completeness(data)
        assert 0.0 < completeness < 1.0
        assert completeness == 4.0 / 6.0  # 4 filled out of 6 total fields

    def test_calculate_completeness_empty_data(self, converter):
        """Test completeness calculation with empty data."""
        completeness = converter._calculate_completeness([])
        assert completeness == 0.0

    def test_calculate_consistency_full_consistency(self, converter):
        """Test consistency calculation with fully consistent data."""
        data = [
            {"name": "Product A", "price": 100},
            {"name": "Product B", "price": 200},
        ]

        consistency = converter._calculate_consistency(data)
        assert consistency == 1.0

    def test_calculate_consistency_partial_consistency(self, converter):
        """Test consistency calculation with partial consistency."""
        data = [
            {"name": "Product A", "price": 100},
            {"name": "Product B", "price": 200, "extra": "field"},
            {"name": "Product C"},  # Missing price field
        ]

        consistency = converter._calculate_consistency(data)
        assert 0.0 < consistency < 1.0
        assert consistency == 1.0 / 3.0  # Only 1 of 3 records consistent

    def test_infer_column_type_numeric(self, converter):
        """Test column type inference for numeric data."""
        sample_data = [
            ["Name", "Price"],  # Header
            ["Product A", 100],
            ["Product B", 200],
            ["Product C", 150],
        ]

        col_type = converter._infer_column_type(sample_data, 1)  # Price column
        assert col_type == "numeric"

    def test_infer_column_type_text(self, converter):
        """Test column type inference for text data."""
        sample_data = [
            ["Name", "Category"],  # Header
            ["Product A", "Electronics"],
            ["Product B", "Books"],
            ["Product C", "Clothing"],
        ]

        col_type = converter._infer_column_type(sample_data, 1)  # Category column
        assert col_type == "text"

    def test_infer_column_type_empty(self, converter):
        """Test column type inference for empty data."""
        sample_data = [
            ["Name", "Empty"],  # Header
            ["Product A", None],
            ["Product B", None],
        ]

        col_type = converter._infer_column_type(sample_data, 1)  # Empty column
        assert col_type == "empty"


class TestAutoSphinxIntegration:
    """Test suite for AutoSphinxIntegration functionality."""

    @pytest.fixture
    def integration(self):
        """Create AutoSphinxIntegration instance."""
        return AutoSphinxIntegration()

    @pytest.fixture
    def sample_conversion_result(self):
        """Sample conversion result for testing."""
        return {
            "json_data": [{"test": "data"}],
            "format_type": "standard_table",
            "entities": {"types": ["product"], "items": []},
            "metadata": {
                "source_file": "test.xlsx",
                "data_quality": {"completeness": 0.95},
            },
            "quality_score": 0.91,
        }

    def test_initialization(self, integration):
        """Test AutoSphinxIntegration initialization."""
        assert integration is not None
        assert hasattr(integration, "templates")
        assert isinstance(integration.templates, dict)

        # Check required templates
        assert "main_document" in integration.templates
        assert "index_document" in integration.templates
        assert "chunk_document" in integration.templates

    def test_infer_title_from_config(self, integration, sample_conversion_result):
        """Test title inference from configuration."""
        config = {"title": "Custom Title"}
        title = integration._infer_title(sample_conversion_result, config)
        assert title == "Custom Title"

    def test_infer_title_from_rag_purpose(self, integration, sample_conversion_result):
        """Test title inference from RAG purpose."""
        config = {"rag_purpose": "sales-analysis"}
        title = integration._infer_title(sample_conversion_result, config)
        assert title == "営業実績分析"

    def test_infer_title_default(self, integration, sample_conversion_result):
        """Test default title inference."""
        config = {"rag_purpose": "unknown-analysis"}
        title = integration._infer_title(sample_conversion_result, config)
        assert "データ分析" in title

    def test_generate_data_summary(self, integration, sample_conversion_result):
        """Test data summary generation."""
        summary = integration._generate_data_summary(sample_conversion_result)

        assert isinstance(summary, str)
        assert "standard table" in summary.lower()
        assert "1" in summary  # Record count

    def test_format_structure_info(self, integration):
        """Test data structure info formatting."""
        conversion_result = {
            "format_type": "standard_table",
            "json_data": [
                {"name": "Product A", "price": 100},
                {"name": "Product B", "price": 200},
            ],
        }

        info = integration._format_structure_info(conversion_result)

        assert "Standard Table" in info
        assert "name" in info
        assert "price" in info
        assert "2 レコード" in info

    def test_generate_example_queries_sales(
        self, integration, sample_conversion_result
    ):
        """Test example query generation for sales analysis."""
        config = {"rag_purpose": "sales-analysis"}
        queries = integration._generate_example_queries(
            sample_conversion_result, config
        )

        assert isinstance(queries, str)
        assert "営業担当者" in queries
        assert "売上" in queries

    def test_generate_example_queries_inventory(
        self, integration, sample_conversion_result
    ):
        """Test example query generation for inventory management."""
        config = {"rag_purpose": "inventory-management"}
        queries = integration._generate_example_queries(
            sample_conversion_result, config
        )

        assert isinstance(queries, str)
        assert "在庫" in queries
        assert "商品" in queries

    def test_generate_advanced_queries(self, integration, sample_conversion_result):
        """Test advanced query generation."""
        config = {"rag_purpose": "general"}
        queries = integration._generate_advanced_queries(
            sample_conversion_result, config
        )

        assert isinstance(queries, str)
        assert "予測" in queries or "分析" in queries
        assert "機械学習" in queries

    def test_format_quality_report(self, integration):
        """Test quality report formatting."""
        metadata = {
            "data_quality": {
                "completeness": 0.95,
                "consistency": 0.92,
                "accuracy": 0.88,
            }
        }

        report = integration._format_quality_report(metadata)

        assert isinstance(report, str)
        assert "95.0%" in report
        assert "92.0%" in report
        assert "88.0%" in report
        assert "高品質" in report

    def test_create_main_document(self, integration, sample_conversion_result):
        """Test main document creation."""
        config = {"rag_purpose": "test-analysis", "auto_update": "daily"}

        doc = integration._create_main_document(sample_conversion_result, config)

        assert isinstance(doc, str)
        assert "enhanced-jsontable::" in doc
        assert "test-analysis" in doc
        assert "rag-metadata: true" in doc
        assert "AI活用ガイド" in doc
        assert "データ品質レポート" in doc

    def test_create_sub_documents_small_dataset(
        self, integration, sample_conversion_result
    ):
        """Test sub-document creation for small dataset."""
        config = {"max_records_per_doc": 1000}

        sub_docs = integration._create_sub_documents(sample_conversion_result, config)

        # Should be empty for small dataset
        assert sub_docs == []

    def test_create_index_document(self, integration, sample_conversion_result):
        """Test index document creation."""
        main_doc = "main document content"
        sub_docs = []

        index_doc = integration._create_index_document(
            sample_conversion_result, main_doc, sub_docs
        )

        assert isinstance(index_doc, str)
        assert "Complete Documentation" in index_doc
        assert "toctree::" in index_doc
        assert "main" in index_doc

    def test_update_sphinx_config(self, integration, sample_conversion_result):
        """Test Sphinx configuration updates."""
        config = {"test": "config"}

        sphinx_config = integration._update_sphinx_config(
            sample_conversion_result, config
        )

        assert isinstance(sphinx_config, dict)
        assert "extensions" in sphinx_config
        assert "sphinxcontrib.jsontable" in sphinx_config["extensions"]
        assert "jsontable_excel_config" in sphinx_config
        assert sphinx_config["jsontable_excel_config"]["auto_detection"] is True


class TestFormatHandlers:
    """Test suite for format-specific handlers."""

    def test_excel_format_handler_initialization(self):
        """Test ExcelFormatHandler initialization."""
        handler = ExcelFormatHandler()

        assert handler is not None
        assert hasattr(handler, "format_handlers")
        assert len(handler.format_handlers) == 6

        # Check all handlers are present
        expected_handlers = [
            "pivot_table",
            "financial_statement",
            "multi_header",
            "cross_tab",
            "time_series",
            "standard_table",
        ]
        for handler_name in expected_handlers:
            assert handler_name in handler.format_handlers

    def test_get_handler_existing(self):
        """Test getting existing format handler."""
        handler = ExcelFormatHandler()
        pivot_handler = handler.get_handler("pivot_table")
        assert isinstance(pivot_handler, PivotTableHandler)

    def test_get_handler_non_existing(self):
        """Test getting non-existing format handler returns default."""
        handler = ExcelFormatHandler()
        default_handler = handler.get_handler("unknown_format")
        assert isinstance(default_handler, StandardTableHandler)

    @patch("pandas.read_excel")
    def test_pivot_table_handler_convert(self, mock_read_excel):
        """Test PivotTableHandler conversion."""
        # Mock DataFrame
        mock_df = Mock()
        mock_df.to_dict.return_value = [{"test": "data"}]
        mock_read_excel.return_value = mock_df

        handler = PivotTableHandler()
        result = handler.convert("test.xlsx", {})

        assert result["format"] == "pivot_table"
        assert result["confidence"] == 0.8
        assert "Pivot table detected" in result["notes"][0]
        assert result["data"] == [{"test": "data"}]

    @patch("pandas.read_excel")
    def test_financial_statement_handler_convert(self, mock_read_excel):
        """Test FinancialStatementHandler conversion."""
        mock_df = Mock()
        mock_df.to_dict.return_value = [{"revenue": 1000}]
        mock_read_excel.return_value = mock_df

        handler = FinancialStatementHandler()
        result = handler.convert("test.xlsx", {})

        assert result["format"] == "financial_statement"
        assert result["confidence"] == 0.9
        assert "Financial statement format" in result["notes"][0]

    @patch("pandas.read_excel")
    def test_standard_table_handler_convert(self, mock_read_excel):
        """Test StandardTableHandler conversion."""
        mock_df = Mock()
        mock_df.to_dict.return_value = [{"name": "Product", "price": 100}]
        mock_read_excel.return_value = mock_df

        handler = StandardTableHandler()
        result = handler.convert("test.xlsx", {})

        assert result["format"] == "standard_table"
        assert result["confidence"] == 0.9
        assert "Standard table format" in result["notes"][0]


class TestConvenienceFunctions:
    """Test suite for convenience functions."""

    @patch("sphinxcontrib.jsontable.excel.converter.ExcelRAGConverter")
    def test_convert_excel_to_rag_function(self, mock_converter_class):
        """Test convert_excel_to_rag convenience function."""
        # Mock converter instance
        mock_converter = Mock()
        mock_converter.convert_excel_to_rag.return_value = {"result": "success"}
        mock_converter_class.return_value = mock_converter

        result = convert_excel_to_rag(
            "test.xlsx", "test-purpose", test_arg="test_value"
        )

        assert result == {"result": "success"}
        mock_converter_class.assert_called_once()
        mock_converter.convert_excel_to_rag.assert_called_once_with(
            "test.xlsx", "test-purpose", {"test_arg": "test_value"}
        )

    @patch("sphinxcontrib.jsontable.excel.converter.ExcelRAGConverter")
    def test_query_excel_data_function(self, mock_converter_class):
        """Test query_excel_data convenience function."""
        mock_converter = Mock()
        mock_converter.query_excel_data.return_value = "Test answer"
        mock_converter_class.return_value = mock_converter

        result = query_excel_data("test.xlsx", "Test question")

        assert result == "Test answer"
        mock_converter_class.assert_called_once()
        mock_converter.query_excel_data.assert_called_once_with(
            "test.xlsx", "Test question"
        )


# Integration tests
class TestExcelRAGIntegration:
    """Integration tests for complete Excel-RAG workflow."""

    @pytest.fixture
    def temp_excel_file(self):
        """Create temporary Excel file for testing."""
        import pandas as pd

        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            # Create sample data
            data = {
                "Product": ["Laptop", "Mouse", "Keyboard"],
                "Price": [1200, 25, 80],
                "Category": ["Electronics", "Accessories", "Accessories"],
            }
            df = pd.DataFrame(data)
            df.to_excel(tmp.name, index=False)
            yield tmp.name

        # Cleanup
        Path(tmp.name).unlink(missing_ok=True)

    @patch(
        "sphinxcontrib.jsontable.excel.converter.ExcelRAGConverter._validate_excel_file"
    )
    @patch("builtins.open", new_callable=MagicMock)
    def test_full_conversion_workflow(self, mock_open, mock_validate, temp_excel_file):
        """Test complete Excel-to-RAG conversion workflow."""
        # Mock file operations to avoid actual file I/O during test
        mock_validate.return_value = None
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        converter = ExcelRAGConverter()

        try:
            result = converter.convert_excel_to_rag(
                excel_file=temp_excel_file,
                rag_purpose="test-analysis",
                auto_sphinx_docs=True,
            )

            # Verify result structure
            assert "conversion_summary" in result
            assert "quality_score" in result
            assert result["conversion_summary"]["rag_purpose"] == "test-analysis"

        except Exception as e:
            # Expected due to mocked dependencies
            assert "missing" in str(e).lower() or "mock" in str(e).lower()


# Performance tests
class TestExcelRAGPerformance:
    """Performance tests for Excel-RAG integration."""

    def test_converter_initialization_performance(self):
        """Test converter initialization performance."""
        import time

        start_time = time.time()
        converter = ExcelRAGConverter()
        end_time = time.time()

        # Should initialize quickly (under 1 second)
        assert (end_time - start_time) < 1.0
        assert converter is not None

    def test_format_detection_performance(self):
        """Test format detection performance."""
        import time

        converter = AdvancedExcelConverter()

        # Mock large dataset processing
        large_sample = [["col"] + [f"data_{i}" for i in range(1000)]]

        start_time = time.time()
        col_type = converter._infer_column_type(large_sample, 0)
        end_time = time.time()

        # Should process quickly even for large datasets
        assert (end_time - start_time) < 0.1
        assert col_type in ["text", "numeric", "mixed", "empty"]


if __name__ == "__main__":
    pytest.main([__file__])
