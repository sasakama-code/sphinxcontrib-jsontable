#!/usr/bin/env python3
"""
Manual test script for column customization features.

This script tests the new column customization functionality without requiring
the full pytest setup.
"""

import sys
import os

# Add the package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'sphinxcontrib'))

def test_column_config_extraction():
    """Test column configuration extraction."""
    print("Testing column configuration extraction...")
    
    from sphinxcontrib.jsontable.directives.directive_core import JsonTableDirective
    from unittest.mock import Mock
    
    # Create a minimal directive instance
    directive = JsonTableDirective.__new__(JsonTableDirective)
    directive.options = {
        "columns": "name,age,city",
        "column-order": "city,name,age",
        "column-widths": "2,1,3",
        "hide-columns": "id,timestamp"
    }
    
    try:
        config = directive._extract_column_config()
        print(f"✓ Column config extracted: {config}")
        
        # Verify expected values
        assert config["visible_columns"] == ["name", "age", "city"]
        assert config["column_order"] == ["city", "name", "age"]
        assert config["column_widths"] == [2, 1, 3]
        assert config["hidden_columns"] == ["id", "timestamp"]
        print("✓ All config values correct")
        
    except Exception as e:
        print(f"✗ Column config extraction failed: {e}")
        return False
    
    return True

def test_table_converter_column_config():
    """Test table converter column configuration."""
    print("\nTesting table converter column configuration...")
    
    from sphinxcontrib.jsontable.directives.table_converter import TableConverter
    
    try:
        converter = TableConverter()
        
        # Test apply_column_config
        keys = ["name", "age", "city", "country"]
        config = {
            "visible_columns": ["name", "city", "country"],
            "hidden_columns": ["age"],
            "column_order": ["country", "name"]
        }
        
        result = converter._apply_column_config(keys, config)
        expected = ["country", "name", "city"]  # country first, then name, then remaining
        print(f"✓ Column config applied: {keys} -> {result}")
        
        assert result == expected, f"Expected {expected}, got {result}"
        print("✓ Column ordering correct")
        
    except Exception as e:
        print(f"✗ Table converter column config failed: {e}")
        return False
    
    return True

def test_table_builder_column_widths():
    """Test table builder column widths."""
    print("\nTesting table builder column widths...")
    
    from sphinxcontrib.jsontable.directives.table_builder import TableBuilder
    
    try:
        builder = TableBuilder()
        
        # Test default widths
        colspecs = builder._create_colspec_nodes(3)
        assert len(colspecs) == 3
        assert all(colspec.attributes["colwidth"] == 1 for colspec in colspecs)
        print("✓ Default column widths correct")
        
        # Test custom widths
        colspecs = builder._create_colspec_nodes(3, [2, 1, 3])
        assert len(colspecs) == 3
        assert colspecs[0].attributes["colwidth"] == 2
        assert colspecs[1].attributes["colwidth"] == 1
        assert colspecs[2].attributes["colwidth"] == 3
        print("✓ Custom column widths correct")
        
    except Exception as e:
        print(f"✗ Table builder column widths failed: {e}")
        return False
    
    return True

def test_object_array_conversion():
    """Test object array conversion with column config."""
    print("\nTesting object array conversion with column config...")
    
    from sphinxcontrib.jsontable.directives.table_converter import TableConverter
    
    try:
        converter = TableConverter()
        
        # Test data
        data = [
            {"name": "Alice", "age": 25, "city": "Tokyo", "country": "Japan"},
            {"name": "Bob", "age": 30, "city": "NYC", "country": "USA"}
        ]
        
        # Test with column config
        column_config = {
            "visible_columns": ["name", "city", "country"],
            "column_order": ["country", "city", "name"]
        }
        
        result = converter.convert(data, column_config=column_config)
        
        # Expected: header row + 2 data rows
        assert len(result) == 3
        assert result[0] == ["country", "city", "name"]  # header in specified order
        assert result[1] == ["Japan", "Tokyo", "Alice"]
        assert result[2] == ["USA", "NYC", "Bob"]
        
        print("✓ Object array conversion with column config successful")
        print(f"  Header: {result[0]}")
        print(f"  Row 1: {result[1]}")
        print(f"  Row 2: {result[2]}")
        
    except Exception as e:
        print(f"✗ Object array conversion failed: {e}")
        return False
    
    return True

def main():
    """Run all tests."""
    print("Column Customization Feature Test Suite")
    print("=" * 50)
    
    tests = [
        test_column_config_extraction,
        test_table_converter_column_config,
        test_table_builder_column_widths,
        test_object_array_conversion
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())