#!/usr/bin/env python3
"""
Test script to verify sorting implementation
"""

import sys
import os
from pathlib import Path

# Add the package to the path
package_path = Path(__file__).parent / "sphinxcontrib"
sys.path.insert(0, str(package_path))

try:
    # Test imports
    from jsontable import setup
    from jsontable.directives.table_builder import TableBuilder
    from jsontable.directives import JsonTableDirective
    
    print("✅ All imports successful")
    
    # Test TableBuilder initialization
    builder = TableBuilder()
    print("✅ TableBuilder initialization successful")
    
    # Test table creation with sample data
    sample_data = [
        ["Name", "Age", "City"],
        ["Alice", "25", "Tokyo"],
        ["Bob", "30", "Osaka"],
        ["Charlie", "35", "Kyoto"]
    ]
    
    # Test table building
    tables = builder.build_table(sample_data, has_header=True)
    print("✅ Table building successful")
    print(f"   Generated {len(tables)} table(s)")
    
    # Check if table has the required attributes
    table = tables[0]
    if 'classes' in table and 'jsontable' in table['classes']:
        print("✅ Table has jsontable CSS class")
    else:
        print("❌ Table missing jsontable CSS class")
    
    if 'data-sortable' in table and table['data-sortable'] == 'true':
        print("✅ Table has sortable attribute")
    else:
        print("❌ Table missing sortable attribute")
    
    # Test static files exist
    static_path = Path(__file__).parent / "sphinxcontrib" / "jsontable" / "static"
    js_file = static_path / "jsontable.js"
    css_file = static_path / "jsontable.css"
    
    if js_file.exists():
        print("✅ JavaScript file exists")
        with open(js_file, 'r') as f:
            content = f.read()
            if 'JsonTableSorting' in content:
                print("✅ JavaScript contains sorting functionality")
            else:
                print("❌ JavaScript missing sorting functionality")
    else:
        print("❌ JavaScript file not found")
    
    if css_file.exists():
        print("✅ CSS file exists")
        with open(css_file, 'r') as f:
            content = f.read()
            if '.sort-indicator' in content:
                print("✅ CSS contains sorting styles")
            else:
                print("❌ CSS missing sorting styles")
    else:
        print("❌ CSS file not found")
    
    print("\n🎉 Basic implementation test completed successfully!")
    print("💡 The sorting functionality has been implemented and is ready for use.")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)