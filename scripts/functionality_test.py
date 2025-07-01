#!/usr/bin/env python3
"""
Functionality test script for v0.4.0 API compatibility.

This script validates that the core functionality works correctly with the new
v0.4.0 API architecture. It replaces the inline test code used in CI environments.
"""

import tempfile
import os
import json
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_functionality():
    """Test core functionality with v0.4.0 API."""
    print("🧪 Running functionality test...")
    
    # Create test data
    test_data_dict = {"name": "test", "value": 123}
    test_data = json.dumps(test_data_dict)
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write(test_data)
        test_file = f.name
    
    try:
        # Import components with new v0.4.0 API
        from sphinxcontrib.jsontable.directives import JsonDataLoader, TableConverter, TableBuilder
        
        # Test JSON loading
        loader = JsonDataLoader()
        data = loader.parse_inline([test_data])
        print("✅ JSON loading successful")
        
        # Test table conversion with new v0.4.0 API
        converter = TableConverter()
        table_data = converter.convert(data)  # No include_header parameter in v0.4.0
        print("✅ Table conversion successful")
        
        # Test table building with new v0.4.0 API
        builder = TableBuilder()
        table_nodes = builder.build_table(table_data)  # build_table() method, returns list
        table_node = table_nodes[0]  # Get first table node
        print("✅ Table building successful")
        
        print("🎉 All functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Clean up temporary file
        try:
            os.unlink(test_file)
        except OSError:
            pass

def test_excel_functionality():
    """Test Excel functionality if available."""
    try:
        # Check if Excel support is available
        from sphinxcontrib.jsontable.directives import EXCEL_SUPPORT
        
        if not EXCEL_SUPPORT:
            print("ℹ️  Excel support not available - skipping Excel tests")
            return True
            
        print("🧪 Running Excel functionality test...")
        
        # Import Excel components
        from sphinxcontrib.jsontable.facade.excel_data_loader_facade import ExcelDataLoaderFacade
        from sphinxcontrib.jsontable.security.security_scanner import SecurityScanner
        
        # Test Excel facade initialization
        security_scanner = SecurityScanner()
        facade = ExcelDataLoaderFacade(security_validator=security_scanner)
        print("✅ Excel facade initialization successful")
        
        print("🎉 Excel functionality tests passed!")
        return True
        
    except ImportError as e:
        print(f"ℹ️  Excel functionality not available: {e}")
        return True  # Not a failure if Excel support is optional
    except Exception as e:
        print(f"❌ Excel functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all functionality tests."""
    print("🚀 Starting v0.4.0 API Functionality Tests")
    print("=" * 50)
    
    success = True
    
    # Test core functionality
    if not test_functionality():
        success = False
    
    print()
    
    # Test Excel functionality
    if not test_excel_functionality():
        success = False
    
    print()
    print("=" * 50)
    
    if success:
        print("🎉 All tests passed successfully!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())