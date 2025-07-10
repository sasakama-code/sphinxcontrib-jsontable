"""
Test cases for column customization features (Issue #48).

This module tests the new column customization functionality including:
- columns: Specify visible columns
- column-order: Define column order  
- column-widths: Set column widths
- hide-columns: Hide specific columns
"""

import pytest
from unittest.mock import Mock, patch

from sphinxcontrib.jsontable.directives import JsonTableDirective


class TestColumnCustomization:
    """Test suite for column customization features."""

    @pytest.fixture
    def mock_state(self):
        """Create a mock state with document and environment."""
        state = Mock()
        state.document = Mock()
        state.document.settings = Mock()
        state.document.settings.env = Mock()
        state.document.settings.env.srcdir = "/mock/source/dir"
        return state

    @pytest.fixture
    def directive_instance(self, mock_state):
        """Create a JsonTableDirective instance for testing."""
        with patch("sphinx.util.docutils.SphinxDirective.__init__"), patch(
            "sphinxcontrib.jsontable.directives.JsonDataLoader"
        ), patch(
            "sphinxcontrib.jsontable.directives.TableConverter"
        ), patch(
            "sphinxcontrib.jsontable.directives.TableBuilder"
        ):
            directive = JsonTableDirective.__new__(JsonTableDirective)
            directive.state = mock_state
            directive.arguments = []
            directive.content = []
            directive.options = {}
            directive.env = mock_state.document.settings.env
            return directive

    def test_extract_column_config_empty(self, directive_instance):
        """Test column config extraction with no options."""
        directive_instance.options = {}
        config = directive_instance._extract_column_config()
        assert config == {}

    def test_extract_column_config_columns(self, directive_instance):
        """Test column config extraction with columns option."""
        directive_instance.options = {"columns": "name,age,city"}
        config = directive_instance._extract_column_config()
        assert config["visible_columns"] == ["name", "age", "city"]

    def test_extract_column_config_column_order(self, directive_instance):
        """Test column config extraction with column-order option."""
        directive_instance.options = {"column-order": "city,name,age"}
        config = directive_instance._extract_column_config()
        assert config["column_order"] == ["city", "name", "age"]

    def test_extract_column_config_column_widths(self, directive_instance):
        """Test column config extraction with column-widths option."""
        directive_instance.options = {"column-widths": "2,1,3"}
        config = directive_instance._extract_column_config()
        assert config["column_widths"] == [2, 1, 3]

    def test_extract_column_config_hide_columns(self, directive_instance):
        """Test column config extraction with hide-columns option."""
        directive_instance.options = {"hide-columns": "id,timestamp"}
        config = directive_instance._extract_column_config()
        assert config["hidden_columns"] == ["id", "timestamp"]

    def test_extract_column_config_invalid_widths(self, directive_instance):
        """Test column config extraction with invalid column-widths."""
        directive_instance.options = {"column-widths": "2,invalid,3"}
        config = directive_instance._extract_column_config()
        # Should not include column_widths due to ValueError
        assert "column_widths" not in config

    def test_extract_column_config_with_spaces(self, directive_instance):
        """Test column config extraction with spaces in values."""
        directive_instance.options = {
            "columns": " name , age , city ",
            "column-order": " city , name , age "
        }
        config = directive_instance._extract_column_config()
        assert config["visible_columns"] == ["name", "age", "city"]
        assert config["column_order"] == ["city", "name", "age"]

    def test_extract_column_config_all_options(self, directive_instance):
        """Test column config extraction with all options."""
        directive_instance.options = {
            "columns": "name,age,city,country",
            "column-order": "country,city,name",
            "column-widths": "2,3,1",
            "hide-columns": "age"
        }
        config = directive_instance._extract_column_config()
        assert config["visible_columns"] == ["name", "age", "city", "country"]
        assert config["column_order"] == ["country", "city", "name"]
        assert config["column_widths"] == [2, 3, 1]
        assert config["hidden_columns"] == ["age"]


class TestTableConverterColumnConfig:
    """Test suite for TableConverter column configuration methods."""
    
    def test_apply_column_config_visible_columns(self):
        """Test apply_column_config with visible_columns filter."""
        from sphinxcontrib.jsontable.directives.table_converter import TableConverter
        
        converter = TableConverter()
        keys = ["name", "age", "city", "country"]
        config = {"visible_columns": ["name", "city"]}
        
        result = converter._apply_column_config(keys, config)
        assert result == ["name", "city"]

    def test_apply_column_config_hidden_columns(self):
        """Test apply_column_config with hidden_columns filter."""
        from sphinxcontrib.jsontable.directives.table_converter import TableConverter
        
        converter = TableConverter()
        keys = ["name", "age", "city", "country"]
        config = {"hidden_columns": ["age", "country"]}
        
        result = converter._apply_column_config(keys, config)
        assert result == ["city", "name"]  # remaining columns, sorted

    def test_apply_column_config_column_order(self):
        """Test apply_column_config with column_order."""
        from sphinxcontrib.jsontable.directives.table_converter import TableConverter
        
        converter = TableConverter()
        keys = ["name", "age", "city", "country"]
        config = {"column_order": ["country", "name", "city"]}
        
        result = converter._apply_column_config(keys, config)
        assert result == ["country", "name", "city", "age"]  # ordered + remaining

    def test_apply_column_config_combined(self):
        """Test apply_column_config with multiple filters."""
        from sphinxcontrib.jsontable.directives.table_converter import TableConverter
        
        converter = TableConverter()
        keys = ["name", "age", "city", "country", "id"]
        config = {
            "visible_columns": ["name", "age", "city", "country"],
            "hidden_columns": ["age"],
            "column_order": ["country", "name"]
        }
        
        result = converter._apply_column_config(keys, config)
        # Should have: visible(name,age,city,country) - hidden(age) = name,city,country
        # Ordered as: country, name, city
        assert result == ["country", "name", "city"]


class TestTableBuilderColumnWidths:
    """Test suite for TableBuilder column width functionality."""
    
    def test_create_colspec_nodes_default_widths(self):
        """Test colspec creation with default widths."""
        from sphinxcontrib.jsontable.directives.table_builder import TableBuilder
        
        builder = TableBuilder()
        colspecs = builder._create_colspec_nodes(3)
        
        assert len(colspecs) == 3
        assert all(colspec.attributes["colwidth"] == 1 for colspec in colspecs)

    def test_create_colspec_nodes_custom_widths(self):
        """Test colspec creation with custom widths."""
        from sphinxcontrib.jsontable.directives.table_builder import TableBuilder
        
        builder = TableBuilder()
        colspecs = builder._create_colspec_nodes(3, [2, 1, 3])
        
        assert len(colspecs) == 3
        assert colspecs[0].attributes["colwidth"] == 2
        assert colspecs[1].attributes["colwidth"] == 1
        assert colspecs[2].attributes["colwidth"] == 3

    def test_create_colspec_nodes_partial_widths(self):
        """Test colspec creation with fewer widths than columns."""
        from sphinxcontrib.jsontable.directives.table_builder import TableBuilder
        
        builder = TableBuilder()
        colspecs = builder._create_colspec_nodes(4, [2, 3])
        
        assert len(colspecs) == 4
        assert colspecs[0].attributes["colwidth"] == 2
        assert colspecs[1].attributes["colwidth"] == 3
        assert colspecs[2].attributes["colwidth"] == 1  # default
        assert colspecs[3].attributes["colwidth"] == 1  # default