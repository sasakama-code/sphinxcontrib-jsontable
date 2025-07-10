"""Type-Aware Rendering Tests for Data Type Detection and Rendering."""

import pytest

from sphinxcontrib.jsontable.directives.table_converter import TableConverter
from sphinxcontrib.jsontable.directives.table_builder import TableBuilder
from sphinxcontrib.jsontable.directives.validators import JsonTableError


class TestDataTypeDetection:
    """Test suite for data type detection functionality."""

    def test_init_with_type_awareness(self):
        """Test initialization with type awareness enabled."""
        converter = TableConverter(enable_type_awareness=True)
        assert converter.enable_type_awareness is True

    def test_detect_data_type_url(self):
        """Test detection of URL data type."""
        converter = TableConverter(enable_type_awareness=True)
        assert converter._detect_data_type("https://example.com") == "url"
        assert converter._detect_data_type("http://test.com") == "url"
        assert converter._detect_data_type("ftp://files.com") == "url"

    def test_detect_data_type_email(self):
        """Test detection of email data type."""
        converter = TableConverter(enable_type_awareness=True)
        assert converter._detect_data_type("test@example.com") == "email"
        assert converter._detect_data_type("user.name@domain.co.jp") == "email"

    def test_detect_data_type_boolean(self):
        """Test detection of boolean data type."""
        converter = TableConverter(enable_type_awareness=True)
        assert converter._detect_data_type(True) == "boolean"
        assert converter._detect_data_type(False) == "boolean"

    def test_detect_data_type_numeric(self):
        """Test detection of numeric data types."""
        converter = TableConverter(enable_type_awareness=True)
        assert converter._detect_data_type(42) == "integer"
        assert converter._detect_data_type(3.14) == "float"
        assert converter._detect_data_type("123") == "number"
        assert converter._detect_data_type("-45.67") == "number"

    def test_detect_data_type_date(self):
        """Test detection of date data type."""
        converter = TableConverter(enable_type_awareness=True)
        assert converter._detect_data_type("2024-01-15") == "date"
        assert converter._detect_data_type("2024-01-15T10:30:00") == "date"
        assert converter._detect_data_type("01/15/2024") == "date"

    def test_detect_data_type_phone(self):
        """Test detection of phone number data type."""
        converter = TableConverter(enable_type_awareness=True)
        assert converter._detect_data_type("+1-555-123-4567") == "phone"
        assert converter._detect_data_type("(555) 123-4567") == "phone"

    def test_detect_data_type_currency(self):
        """Test detection of currency data type."""
        converter = TableConverter(enable_type_awareness=True)
        assert converter._detect_data_type("$99.99") == "currency"
        assert converter._detect_data_type("€1,234.56") == "currency"

    def test_detect_data_type_null(self):
        """Test detection of null data type."""
        converter = TableConverter(enable_type_awareness=True)
        assert converter._detect_data_type(None) == "null"

    def test_detect_data_type_object(self):
        """Test detection of object data type."""
        converter = TableConverter(enable_type_awareness=True)
        assert converter._detect_data_type({"key": "value"}) == "object"
        assert converter._detect_data_type([1, 2, 3]) == "object"

    def test_detect_data_type_string(self):
        """Test detection of string data type."""
        converter = TableConverter(enable_type_awareness=True)
        assert converter._detect_data_type("Hello World") == "string"
        assert converter._detect_data_type("") == "string"
        assert converter._detect_data_type("   ") == "string"

    def test_convert_with_type_info(self):
        """Test conversion with type information preservation."""
        converter = TableConverter(enable_type_awareness=True)
        result = converter._convert_with_type_info("https://example.com")
        assert result == ("https://example.com", "url")

        result = converter._convert_with_type_info(True)
        assert result == ("True", "boolean")

        result = converter._convert_with_type_info(None)
        assert result == ("", "null")


class TestTypeAwareConversion:
    """Test suite for type-aware data conversion."""

    def test_convert_with_types_simple_object(self):
        """Test type-aware conversion with simple object."""
        converter = TableConverter(enable_type_awareness=True)
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "website": "https://johndoe.com",
            "active": True,
            "age": 30
        }

        result = converter.convert_with_types(data)

        # Check structure
        assert len(result) == 2  # header + data row
        assert len(result[0]) == 5  # 5 columns

        # Check header types (all should be "string")
        for value, data_type in result[0]:
            assert data_type == "string"

        # Check data types in first row
        data_row = dict(zip([h[0] for h in result[0]], result[1]))
        assert data_row["name"] == ("John Doe", "string")
        assert data_row["email"] == ("john@example.com", "email")
        assert data_row["website"] == ("https://johndoe.com", "url")
        assert data_row["active"] == ("True", "boolean")
        assert data_row["age"] == ("30", "integer")

    def test_convert_with_types_object_array(self):
        """Test type-aware conversion with object array."""
        converter = TableConverter(enable_type_awareness=True)
        data = [
            {"name": "Alice", "email": "alice@example.com", "active": True},
            {"name": "Bob", "email": "bob@example.com", "active": False}
        ]

        result = converter.convert_with_types(data)

        # Check structure
        assert len(result) == 3  # header + 2 data rows
        assert len(result[0]) == 3  # 3 columns

        # Check data types in first data row
        data_row = dict(zip([h[0] for h in result[0]], result[1]))
        assert data_row["name"] == ("Alice", "string")
        assert data_row["email"] == ("alice@example.com", "email")
        assert data_row["active"] == ("True", "boolean")

    def test_convert_with_types_2d_array(self):
        """Test type-aware conversion with 2D array."""
        converter = TableConverter(enable_type_awareness=True)
        data = [
            ["Name", "Email", "Website"],
            ["John", "john@example.com", "https://johndoe.com"],
            ["Jane", "jane@example.com", "https://janesmith.com"]
        ]

        result = converter.convert_with_types(data)

        # Check structure
        assert len(result) == 3  # 3 rows
        assert len(result[0]) == 3  # 3 columns

        # Check data types in second row
        assert result[1][0] == ("John", "string")
        assert result[1][1] == ("john@example.com", "email")
        assert result[1][2] == ("https://johndoe.com", "url")

    def test_convert_with_types_empty_data(self):
        """Test type-aware conversion with empty data."""
        converter = TableConverter(enable_type_awareness=True)

        with pytest.raises(JsonTableError, match="No JSON data to process"):
            converter.convert_with_types([])

    def test_convert_with_types_none_data(self):
        """Test type-aware conversion with None data."""
        converter = TableConverter(enable_type_awareness=True)

        with pytest.raises(JsonTableError, match="Data cannot be None"):
            converter.convert_with_types(None)


class TestTypeAwareTableBuilder:
    """Test suite for type-aware table building."""

    def test_build_table_with_types_basic(self):
        """Test basic type-aware table building."""
        builder = TableBuilder()
        type_aware_data = [
            [("Name", "string"), ("Email", "string"), ("Active", "string")],
            [("John", "string"), ("john@example.com", "email"), ("True", "boolean")],
            [("Jane", "string"), ("jane@example.com", "email"), ("False", "boolean")]
        ]

        result = builder.build_table_with_types(type_aware_data)

        assert len(result) == 1
        assert hasattr(result[0], 'tagname')

    def test_build_table_with_types_with_options(self):
        """Test type-aware table building with render options."""
        builder = TableBuilder()
        type_aware_data = [
            [("Name", "string"), ("Active", "string")],
            [("John", "string"), ("True", "boolean")],
            [("Jane", "string"), ("False", "boolean")]
        ]

        type_render_options = {
            "boolean_style": "yes-no",
            "date_format": "localized"
        }

        result = builder.build_table_with_types(
            type_aware_data, 
            has_header=True, 
            type_render_options=type_render_options
        )

        assert len(result) == 1
        assert hasattr(result[0], 'tagname')

    def test_build_table_with_types_empty_data(self):
        """Test type-aware table building with empty data."""
        builder = TableBuilder()

        with pytest.raises(ValueError, match="table_data cannot be empty"):
            builder.build_table_with_types([])

    def test_build_table_with_types_none_data(self):
        """Test type-aware table building with None data."""
        builder = TableBuilder()

        with pytest.raises(ValueError, match="table_data cannot be None"):
            builder.build_table_with_types(None)

    def test_create_type_aware_cell_url(self):
        """Test creation of URL cell."""
        builder = TableBuilder()
        entry = builder._create_type_aware_cell("https://example.com", "url")

        assert entry['classes'] == ['jsontable-url']

    def test_create_type_aware_cell_email(self):
        """Test creation of email cell."""
        builder = TableBuilder()
        entry = builder._create_type_aware_cell("test@example.com", "email")

        assert entry['classes'] == ['jsontable-email']

    def test_create_type_aware_cell_boolean_symbols(self):
        """Test creation of boolean cell with symbols style."""
        builder = TableBuilder()
        type_render_options = {"boolean_style": "symbols"}

        entry_true = builder._create_type_aware_cell("True", "boolean", type_render_options)
        entry_false = builder._create_type_aware_cell("False", "boolean", type_render_options)

        assert entry_true['classes'] == ['jsontable-boolean']
        assert entry_false['classes'] == ['jsontable-boolean']

    def test_create_type_aware_cell_boolean_yes_no(self):
        """Test creation of boolean cell with yes-no style."""
        builder = TableBuilder()
        type_render_options = {"boolean_style": "yes-no"}

        entry_true = builder._create_type_aware_cell("True", "boolean", type_render_options)
        entry_false = builder._create_type_aware_cell("False", "boolean", type_render_options)

        assert entry_true['classes'] == ['jsontable-boolean']
        assert entry_false['classes'] == ['jsontable-boolean']

    def test_create_type_aware_cell_number(self):
        """Test creation of number cells."""
        builder = TableBuilder()

        entry_int = builder._create_type_aware_cell("42", "integer")
        entry_float = builder._create_type_aware_cell("3.14", "float")

        assert 'jsontable-integer' in entry_int['classes']
        assert 'jsontable-number' in entry_int['classes']
        assert 'jsontable-float' in entry_float['classes']
        assert 'jsontable-number' in entry_float['classes']

    def test_create_type_aware_cell_date(self):
        """Test creation of date cell."""
        builder = TableBuilder()
        entry = builder._create_type_aware_cell("2024-01-15", "date")

        assert 'jsontable-date' in entry['classes']

    def test_create_type_aware_cell_string(self):
        """Test creation of string cell."""
        builder = TableBuilder()
        entry = builder._create_type_aware_cell("Hello World", "string")

        assert entry['classes'] == ['jsontable-string']

    def test_create_type_aware_cell_null(self):
        """Test creation of null cell."""
        builder = TableBuilder()
        entry = builder._create_type_aware_cell(None, "null")

        # Should handle None gracefully and create empty cell


class TestTypeAwareIntegration:
    """Integration tests for type-aware rendering pipeline."""

    def test_full_pipeline_mixed_data_types(self):
        """Test full pipeline with mixed data types."""
        converter = TableConverter(enable_type_awareness=True)
        builder = TableBuilder()

        # Create test data with various types
        data = [
            {
                "name": "John Doe",
                "email": "john@example.com",
                "website": "https://johndoe.com",
                "active": True,
                "age": 30,
                "salary": "$50,000",
                "phone": "+1-555-123-4567",
                "joined": "2024-01-15"
            },
            {
                "name": "Jane Smith",
                "email": "jane@example.com", 
                "website": "https://janesmith.com",
                "active": False,
                "age": 28,
                "salary": "$55,000",
                "phone": "+1-555-987-6543",
                "joined": "2024-02-01"
            }
        ]

        # Convert with type awareness
        type_aware_data = converter.convert_with_types(data)

        # Build table with type awareness
        type_render_options = {
            "boolean_style": "symbols",
            "date_format": "original"
        }
        table_nodes = builder.build_table_with_types(
            type_aware_data, 
            has_header=True, 
            type_render_options=type_render_options
        )

        # Verify successful completion
        assert len(table_nodes) == 1
        assert hasattr(table_nodes[0], 'tagname')

    def test_backward_compatibility_no_type_awareness(self):
        """Test that regular conversion still works when type awareness is disabled."""
        converter = TableConverter(enable_type_awareness=False)
        builder = TableBuilder()

        data = [
            {"name": "John", "email": "john@example.com", "active": True},
            {"name": "Jane", "email": "jane@example.com", "active": False}
        ]

        # Regular conversion should still work
        table_data = converter.convert(data)
        table_nodes = builder.build_table(table_data)

        assert len(table_nodes) == 1
        assert hasattr(table_nodes[0], 'tagname')