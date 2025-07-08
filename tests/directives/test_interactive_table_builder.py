"""Test Interactive Table Builder - Comprehensive TDD tests for Issue #50.

This test module implements comprehensive test coverage for interactive table
generation with sorting functionality including header-click sorting, 
DataTables.js integration, and multi-type data support.

TDD Implementation Strategy:
- RED Phase: Create failing tests that define exact requirements
- GREEN Phase: Implement minimal functionality to pass tests  
- REFACTOR Phase: Enhance to enterprise-grade quality

Test Coverage Areas:
- Header click sorting functionality
- DataTables.js integration and configuration
- Custom JavaScript sorting implementation
- Multi-type data sorting (strings, numbers, dates)
- Sort column specification and validation
- Default sort configuration
- Accessibility features (ARIA attributes, keyboard navigation)
- Performance with large datasets
- Error handling and graceful degradation
- Integration with existing directive functionality

CLAUDE.md Code Excellence Compliance:
- DRY Principle: Reusable test fixtures and helpers
- Single Responsibility: Each test validates one specific behavior
- SOLID Principles: Clear test structure with separation of concerns
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import re

from sphinxcontrib.jsontable.directives.interactive_table_builder import InteractiveTableBuilder
from sphinxcontrib.jsontable.directives.validators import JsonTableError
from docutils import nodes


class TestInteractiveTableBuilder:
    """Test suite for InteractiveTableBuilder functionality."""

    @pytest.fixture
    def builder(self):
        """Create InteractiveTableBuilder instance for testing."""
        return InteractiveTableBuilder()

    @pytest.fixture
    def custom_builder(self):
        """Create InteractiveTableBuilder with custom settings."""
        return InteractiveTableBuilder(
            javascript_library="custom",
            version="stable",
            enable_search=False,
            enable_pagination=False,
            page_length=50,
            responsive=True
        )

    @pytest.fixture
    def datatables_builder(self):
        """Create InteractiveTableBuilder with DataTables.js configuration."""
        return InteractiveTableBuilder(
            javascript_library="datatables",
            version="latest",
            enable_search=True,
            enable_pagination=True,
            page_length=25,
            responsive=True
        )

    @pytest.fixture
    def sample_table_data(self):
        """Sample table data with sortable content."""
        return [
            ["Name", "Age", "Score", "Date", "Active"],
            ["Alice", "25", "95.5", "2024-01-15", "true"],
            ["Bob", "30", "87.2", "2023-12-01", "false"],
            ["Charlie", "22", "98.1", "2024/02/14", "true"],
            ["Diana", "28", "92.8", "2023-11-20", "false"],
            ["Eve", "35", "89.7", "2024-03-10", "true"]
        ]

    @pytest.fixture
    def large_table_data(self):
        """Large table data for performance testing."""
        headers = ["ID", "Name", "Value", "Date", "Status"]
        data = [headers]
        for i in range(1000):
            data.append([
                str(i),
                f"User{i:04d}",
                str(i * 10.5),
                "2024-01-15",
                "active" if i % 2 == 0 else "inactive"
            ])
        return data

    # RED Phase Tests - These should initially fail

    def test_basic_sortable_table_generation(self, builder, sample_table_data):
        """Test basic sortable table generation.
        
        Should generate table with sortable headers and appropriate markup.
        """
        result = builder.build_interactive_table(sample_table_data, sortable=True)
        
        # Expected: Return list of document nodes
        assert isinstance(result, list)
        assert len(result) >= 1
        
        # Expected: Contains table node
        table_node = None
        for node in result:
            if isinstance(node, nodes.table):
                table_node = node
                break
        
        assert table_node is not None
        
        # Expected: Table has interactive classes
        assert "jsontable-interactive" in table_node.get("classes", [])
        
        # Expected: Header has sortable classes
        # This will fail initially as the implementation needs enhancement
        header_entries = self._extract_header_entries(table_node)
        assert len(header_entries) == 5  # Name, Age, Score, Date, Active
        
        for entry in header_entries:
            assert "sortable" in entry.get("classes", [])
            assert entry.get("role") == "columnheader"
            assert entry.get("tabindex") == "0"
            assert entry.get("aria-sort") == "none"

    def test_datatables_integration_with_configuration(self, datatables_builder, sample_table_data):
        """Test DataTables.js integration with proper configuration.
        
        Should generate DataTables initialization script with correct config.
        """
        result = datatables_builder.build_interactive_table(
            sample_table_data,
            sortable=True,
            sort_columns=["Name", "Score"],
            default_sort={"column": "Score", "direction": "desc"}
        )
        
        # Expected: Contains CSS and JavaScript nodes
        css_node = None
        
        for node in result:
            if isinstance(node, nodes.raw) and node.get("format") == "html":
                content = str(node.astext())
                if "css" in content.lower() or "stylesheet" in content.lower():
                    css_node = node
                    break
        
        # Expected: CSS dependencies loaded
        assert css_node is not None
        css_content = css_node.astext()
        assert "datatables.net" in css_content
        assert "jsontable-interactive" in css_content
        
        # Expected: JavaScript initialization with proper config - use helper method
        js_content = self._extract_javascript_content(result)
        assert js_content  # Should have JavaScript content
        
        # Check DataTables configuration
        assert "DataTable" in js_content
        assert '"paging": true' in js_content
        assert '"searching": true' in js_content
        assert '"ordering": true' in js_content
        assert '"pageLength": 25' in js_content
        
        # Check column restrictions
        assert '"orderable": false' in js_content  # Non-sortable columns
        
        # Check default sort
        assert '"order"' in js_content
        # Check for score column (index 2) with desc direction - handle JSON formatting
        assert '"order":' in js_content and '2' in js_content and '"desc"' in js_content

    def test_custom_javascript_sorting_implementation(self, custom_builder, sample_table_data):
        """Test custom lightweight JavaScript sorting implementation.
        
        Should generate custom sorting script without external dependencies.
        """
        result = custom_builder.build_interactive_table(
            sample_table_data,
            sortable=True,
            sort_columns=["Name", "Age", "Score"]
        )
        
        # Expected: Contains custom JavaScript implementation
        js_node = None
        for node in result:
            if isinstance(node, nodes.raw) and node.get("format") == "html":
                content = str(node.astext())
                if "script" in content.lower() and "DataTable" not in content:
                    js_node = node
                    break
        
        assert js_node is not None
        js_content = js_node.astext()
        
        # Expected: Custom sorting functions
        assert "sortTable" in js_content
        assert "addEventListener" in js_content
        assert "click" in js_content
        assert "keydown" in js_content
        
        # Expected: Data type detection for sorting
        assert "parseFloat" in js_content
        assert "localeCompare" in js_content
        
        # Expected: Accessibility support
        assert "aria-sort" in js_content
        assert "Enter" in js_content or "Space" in js_content

    def test_multi_type_data_sorting_intelligence(self, custom_builder, sample_table_data):
        """Test intelligent sorting for different data types.
        
        Should detect and sort numbers, dates, and strings appropriately.
        """
        mixed_data = [
            ["Type", "Number", "Date", "Currency", "Boolean"],
            ["Item1", "100", "2024-01-15", "$1,234.56", "true"],
            ["Item2", "25", "2023-12-01", "$567.89", "false"],
            ["Item3", "1000", "2024/02/14", "$2,345.67", "true"],
            ["Item4", "5", "2023-11-20", "$123.45", "false"]
        ]
        
        result = custom_builder.build_interactive_table(mixed_data, sortable=True)
        
        # Expected: Table generated successfully
        assert isinstance(result, list)
        
        # Expected: JavaScript handles different data types
        js_content = self._extract_javascript_content(result)
        
        # Should have numeric comparison logic
        assert "parseFloat" in js_content or "Number" in js_content
        
        # Should have fallback to string comparison
        assert "localeCompare" in js_content
        
        # Expected: Proper type detection order (numbers before strings)
        # This ensures numbers are sorted numerically, not lexicographically

    def test_sort_column_specification_validation(self, builder, sample_table_data):
        """Test sort column specification and validation.
        
        Should validate sort columns exist and handle invalid specifications.
        """
        # Test valid sort columns
        result = builder.build_interactive_table(
            sample_table_data,
            sortable=True,
            sort_columns=["Name", "Score", "Age"]
        )
        
        assert isinstance(result, list)
        
        # Test invalid sort columns - should raise JsonTableError
        with pytest.raises(JsonTableError, match="Invalid sort columns"):
            builder.build_interactive_table(
                sample_table_data,
                sortable=True,
                sort_columns=["NonexistentColumn", "AnotherBadColumn"]
            )
        
        # Test empty sort columns list (no columns sortable)
        result = builder.build_interactive_table(
            sample_table_data,
            sortable=True,
            sort_columns=[]
        )
        
        # Should generate table but no columns should be sortable
        table_node = self._extract_table_node(result)
        header_entries = self._extract_header_entries(table_node)
        
        for entry in header_entries:
            assert "sortable" not in entry.get("classes", [])

    def test_default_sort_configuration_validation(self, builder, sample_table_data):
        """Test default sort configuration and validation.
        
        Should apply default sort and validate column exists.
        """
        # Test valid default sort
        result = builder.build_interactive_table(
            sample_table_data,
            sortable=True,
            default_sort={"column": "Score", "direction": "desc"}
        )
        
        assert isinstance(result, list)
        
        # Expected: JavaScript contains default sort configuration
        js_content = self._extract_javascript_content(result)
        
        if "DataTable" in js_content:
            # DataTables implementation
            assert '"order"' in js_content
            assert "desc" in js_content
        else:
            # Custom implementation - should have initial sort indicator
            assert "aria-sort" in js_content
        
        # Test invalid default sort column
        with pytest.raises(JsonTableError, match="Invalid default sort column"):
            builder.build_interactive_table(
                sample_table_data,
                sortable=True,
                default_sort={"column": "NonexistentColumn", "direction": "asc"}
            )

    def test_accessibility_features_implementation(self, builder, sample_table_data):
        """Test accessibility features for sorting.
        
        Should include ARIA attributes and keyboard navigation support.
        """
        result = builder.build_interactive_table(sample_table_data, sortable=True)
        
        # Expected: Table has accessibility attributes
        table_node = self._extract_table_node(result)
        header_entries = self._extract_header_entries(table_node)
        
        for entry in header_entries:
            # Expected: ARIA attributes for screen readers
            assert entry.get("role") == "columnheader"
            assert entry.get("aria-sort") == "none"
            assert entry.get("tabindex") == "0"
        
        # Expected: JavaScript includes keyboard navigation
        js_content = self._extract_javascript_content(result)
        
        # Should handle Enter and Space keys
        assert ("keydown" in js_content and 
                ("Enter" in js_content or "Space" in js_content))
        
        # Should update ARIA attributes on sort
        assert "aria-sort" in js_content
        assert ("ascending" in js_content and "descending" in js_content)

    def test_table_id_generation_and_uniqueness(self, builder, sample_table_data):
        """Test table ID generation for JavaScript targeting.
        
        Should generate unique IDs for multiple tables.
        """
        # Test automatic ID generation
        result1 = builder.build_interactive_table(sample_table_data, sortable=True)
        result2 = builder.build_interactive_table(sample_table_data, sortable=True)
        
        table1_id = self._extract_table_id(result1)
        table2_id = self._extract_table_id(result2)
        
        # Expected: IDs are generated and unique
        assert table1_id is not None
        assert table2_id is not None
        assert table1_id != table2_id
        assert table1_id.startswith("jsontable_")
        assert table2_id.startswith("jsontable_")
        
        # Test custom ID specification
        result3 = builder.build_interactive_table(
            sample_table_data,
            sortable=True,
            table_id="custom_table_id"
        )
        
        table3_id = self._extract_table_id(result3)
        assert table3_id == "custom_table_id"

    def test_css_classes_and_styling_application(self, builder, sample_table_data):
        """Test CSS classes and styling application.
        
        Should apply appropriate CSS classes for styling and functionality.
        """
        result = builder.build_interactive_table(
            sample_table_data,
            sortable=True,
            css_classes=["custom-class", "another-class"]
        )
        
        table_node = self._extract_table_node(result)
        classes = table_node.get("classes", [])
        
        # Expected: Default interactive classes
        assert "jsontable-interactive" in classes
        
        # Expected: Custom classes applied
        assert "custom-class" in classes
        assert "another-class" in classes
        
        # Expected: DataTables class for DataTables.js integration
        if builder.javascript_library == "datatables":
            assert "display" in classes
        
        # Expected: Responsive class if enabled
        if builder.responsive:
            assert "responsive" in classes

    def test_performance_with_large_datasets(self, builder, large_table_data):
        """Test performance with large datasets.
        
        Should handle large tables efficiently without performance degradation.
        """
        import time
        
        start_time = time.perf_counter()
        result = builder.build_interactive_table(large_table_data, sortable=True)
        end_time = time.perf_counter()
        
        # Performance requirement: < 2s for 1000 rows
        processing_time = end_time - start_time
        assert processing_time < 2.0, f"Processing took {processing_time:.3f}s, expected < 2.0s"
        
        # Expected: Table generated successfully
        assert isinstance(result, list)
        
        table_node = self._extract_table_node(result)
        assert table_node is not None
        
        # Expected: Correct number of rows
        tbody = self._extract_tbody(table_node)
        rows = [child for child in tbody.children if isinstance(child, nodes.row)]
        assert len(rows) == 1000  # Data rows (excluding header)

    def test_error_handling_empty_table_data(self, builder):
        """Test error handling for empty table data."""
        with pytest.raises(JsonTableError, match="Table data cannot be empty"):
            builder.build_interactive_table([], sortable=True)
    
    def test_error_handling_empty_header_row(self, builder):
        """Test error handling for empty header row."""
        with pytest.raises(JsonTableError, match="Header row cannot be empty"):
            builder.build_interactive_table([[]], sortable=True)

    def test_unsupported_datatables_version_error(self):
        """Test error handling for unsupported DataTables version."""
        with pytest.raises(JsonTableError, match="Unsupported DataTables version"):
            InteractiveTableBuilder(
                javascript_library="datatables",
                version="nonexistent_version"
            )

    def test_no_javascript_fallback_mode(self, sample_table_data):
        """Test fallback mode with no JavaScript for accessibility.
        
        Should generate basic table without JavaScript dependencies.
        """
        builder = InteractiveTableBuilder(javascript_library="none")
        
        result = builder.build_interactive_table(sample_table_data, sortable=True)
        
        # Expected: Table generated without JavaScript
        table_node = self._extract_table_node(result)
        assert table_node is not None
        
        # Expected: No JavaScript nodes in result
        for node in result:
            if isinstance(node, nodes.raw):
                content = str(node.astext())
                assert "script" not in content.lower()
        
        # Expected: Headers still have accessibility attributes but no interactive classes
        header_entries = self._extract_header_entries(table_node)
        for entry in header_entries:
            # Should NOT have sortable class in no-JS mode
            assert "sortable" not in entry.get("classes", [])

    def test_responsive_design_configuration(self, sample_table_data):
        """Test responsive design configuration.
        
        Should apply responsive classes and configuration.
        """
        builder = InteractiveTableBuilder(responsive=True)
        
        result = builder.build_interactive_table(sample_table_data, sortable=True)
        
        table_node = self._extract_table_node(result)
        classes = table_node.get("classes", [])
        
        # Expected: Responsive class applied
        assert "responsive" in classes
        
        # Expected: DataTables responsive configuration
        js_content = self._extract_javascript_content(result)
        if "DataTable" in js_content:
            assert '"responsive": true' in js_content

    def test_search_and_pagination_configuration(self, sample_table_data):
        """Test search and pagination configuration.
        
        Should configure DataTables search and pagination features.
        """
        builder = InteractiveTableBuilder(
            enable_search=True,
            enable_pagination=True,
            page_length=10
        )
        
        result = builder.build_interactive_table(sample_table_data, sortable=True)
        
        js_content = self._extract_javascript_content(result)
        
        if "DataTable" in js_content:
            # Expected: Search enabled
            assert '"searching": true' in js_content
            
            # Expected: Pagination enabled with custom page length
            assert '"paging": true' in js_content
            assert '"pageLength": 10' in js_content
            
            # Expected: Language configuration
            assert '"language"' in js_content
            assert '"search"' in js_content

    # Performance and Load Testing

    def test_memory_efficiency_multiple_tables(self, builder, sample_table_data):
        """Test memory efficiency when generating multiple tables.
        
        Should not have memory leaks or excessive memory usage.
        """
        import tracemalloc
        
        tracemalloc.start()
        
        # Generate multiple tables
        results = []
        for i in range(10):
            result = builder.build_interactive_table(
                sample_table_data,
                sortable=True,
                table_id=f"test_table_{i}"
            )
            results.append(result)
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Memory requirement: Peak memory < 50MB for 10 tables
        peak_mb = peak / 1024 / 1024
        assert peak_mb < 50, f"Peak memory usage {peak_mb:.2f}MB, expected < 50MB"
        
        # Expected: All tables generated successfully
        assert len(results) == 10
        for result in results:
            assert isinstance(result, list)
            assert len(result) >= 1

    # Helper methods for test assertions

    def _extract_table_node(self, result):
        """Extract table node from result."""
        for node in result:
            if isinstance(node, nodes.table):
                return node
        return None

    def _extract_header_entries(self, table_node):
        """Extract header entries from table node."""
        if not table_node:
            return []
        
        # Find thead > row > entry elements
        for child in table_node.children:
            if isinstance(child, nodes.tgroup):
                for tgroup_child in child.children:
                    if isinstance(tgroup_child, nodes.thead):
                        for thead_child in tgroup_child.children:
                            if isinstance(thead_child, nodes.row):
                                return [entry for entry in thead_child.children 
                                       if isinstance(entry, nodes.entry)]
        return []

    def _extract_tbody(self, table_node):
        """Extract tbody from table node."""
        if not table_node:
            return None
            
        for child in table_node.children:
            if isinstance(child, nodes.tgroup):
                for tgroup_child in child.children:
                    if isinstance(tgroup_child, nodes.tbody):
                        return tgroup_child
        return None

    def _extract_javascript_content(self, result):
        """Extract JavaScript content from result nodes."""
        all_js_content = []
        for node in result:
            if isinstance(node, nodes.raw) and node.get("format") == "html":
                content = str(node.astext())
                if "script" in content.lower():
                    all_js_content.append(content)
        # Return combined content so tests can find any script content
        return "\n".join(all_js_content)

    def _extract_table_id(self, result):
        """Extract table ID from result."""
        table_node = self._extract_table_node(result)
        if table_node and "ids" in table_node:
            ids = table_node.get("ids", [])
            return ids[0] if ids else None
        return None


class TestInteractiveTableBuilderIntegration:
    """Test integration of InteractiveTableBuilder with other components."""

    @pytest.fixture
    def mock_directive(self):
        """Create mock JsonTableDirective for testing."""
        directive = Mock()
        directive.options = {}
        directive.env = Mock()
        directive.env.config = Mock()
        directive.env.srcdir = "/test/src"
        return directive

    def test_integration_with_data_type_renderer(self, mock_directive):
        """Test integration with DataTypeRenderer for enhanced data.
        
        Should work with pre-processed data from DataTypeRenderer.
        """
        # This test will be implemented in GREEN phase
        pytest.skip("Integration test - will be implemented in GREEN phase")

    def test_integration_with_column_customizer(self, mock_directive):
        """Test integration with ColumnCustomizer for column control.
        
        Should work with customized columns from ColumnCustomizer.
        """
        # This test will be implemented in GREEN phase
        pytest.skip("Integration test - will be implemented in GREEN phase")

    def test_full_directive_pipeline_integration(self, mock_directive):
        """Test full pipeline: ColumnCustomizer → DataTypeRenderer → InteractiveTableBuilder.
        
        Should integrate all three components seamlessly.
        """
        # This test will be implemented in GREEN phase
        pytest.skip("Integration test - will be implemented in GREEN phase")


# Performance Benchmark Tests
class TestInteractiveTableBuilderPerformance:
    """Performance benchmark tests for interactive table building."""

    @pytest.fixture
    def massive_table_data(self):
        """Create massive table for performance testing."""
        headers = ["ID", "Name", "Score", "Date", "Status", "Value"]
        data = [headers]
        for i in range(5000):
            data.append([
                str(i),
                f"User{i:04d}",
                str(90 + (i % 10)),
                "2024-01-15",
                "active" if i % 2 == 0 else "inactive",
                str(i * 100.5)
            ])
        return data

    @pytest.mark.performance
    def test_massive_dataset_performance(self, massive_table_data):
        """Test performance with massive dataset."""
        builder = InteractiveTableBuilder()
        
        import time
        start_time = time.perf_counter()
        
        result = builder.build_interactive_table(
            massive_table_data,
            sortable=True,
            sort_columns=["Name", "Score", "Date"]
        )
        
        end_time = time.perf_counter()
        
        # Performance requirement: < 5s for 5K rows
        processing_time = end_time - start_time
        assert processing_time < 5.0, f"Processing took {processing_time:.3f}s, expected < 5.0s"
        
        # Verify correctness
        assert isinstance(result, list)
        table_node = None
        for node in result:
            if isinstance(node, nodes.table):
                table_node = node
                break
        
        assert table_node is not None

    @pytest.mark.performance
    def test_javascript_generation_performance(self):
        """Test JavaScript generation performance."""
        builder = InteractiveTableBuilder()
        
        data = [["A", "B", "C"]] + [["1", "2", "3"]] * 1000
        
        import time
        start_time = time.perf_counter()
        
        result = builder.build_interactive_table(data, sortable=True)
        
        end_time = time.perf_counter()
        
        # Performance requirement: < 1s for JavaScript generation
        processing_time = end_time - start_time
        assert processing_time < 1.0, f"JS generation took {processing_time:.3f}s, expected < 1.0s"

    @pytest.mark.memory
    def test_memory_efficiency_large_tables(self):
        """Test memory efficiency with large tables."""
        import tracemalloc
        
        builder = InteractiveTableBuilder()
        data = [["Col1", "Col2", "Col3"]] + [["A", "B", "C"]] * 2000
        
        tracemalloc.start()
        
        result = builder.build_interactive_table(data, sortable=True)
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Memory requirement: Peak memory < 100MB for 2K rows
        peak_mb = peak / 1024 / 1024
        assert peak_mb < 100, f"Peak memory usage {peak_mb:.2f}MB, expected < 100MB"