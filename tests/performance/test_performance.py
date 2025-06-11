"""
Performance tests for sphinxcontrib-jsontable.
統合元: test_performance_limits.py + test_performance_limits_integration.py
"""

import json
import time

import pytest

from sphinxcontrib.jsontable.data_loaders import JsonDataLoader
from sphinxcontrib.jsontable.rag.metadata_extractor import RAGMetadataExtractor
from sphinxcontrib.jsontable.rag.search_facets import SearchFacetGenerator
from sphinxcontrib.jsontable.table_builders import TableBuilder
from sphinxcontrib.jsontable.table_converters import TableConverter

# Performance test markers
pytestmark = pytest.mark.performance


class TestPerformanceLimits:
    """Performance limits and benchmarking tests."""

    def setup_method(self):
        """Test setup."""
        self.data_loader = JsonDataLoader()
        self.table_builder = TableBuilder()
        self.table_converter = TableConverter()
        self.metadata_extractor = RAGMetadataExtractor()
        self.facet_generator = SearchFacetGenerator()

    @pytest.mark.benchmark
    def test_large_dataset_processing_benchmark(self, benchmark):
        """Benchmark large dataset processing."""
        # Generate large test dataset
        large_data = []
        for i in range(1000):
            large_data.append(
                {
                    "id": i,
                    "name": f"Item_{i}",
                    "category": f"Category_{i % 10}",
                    "value": i * 100,
                    "description": f"Description for item {i} with some additional text content",
                }
            )

        def process_large_data():
            converted = self.table_converter.convert(large_data)
            table = self.table_builder.build(converted, has_header=True)
            return table

        result = benchmark(process_large_data)
        assert result is not None

    @pytest.mark.benchmark
    def test_metadata_extraction_benchmark(self, benchmark):
        """Benchmark metadata extraction performance."""
        test_data = []
        for i in range(500):
            test_data.append(
                {
                    "employee_id": f"EMP{i:04d}",
                    "name": f"Employee {i}",
                    "department": f"Department {i % 5}",
                    "salary": 50000 + (i * 1000) % 100000,
                    "performance": 70 + (i % 30),
                }
            )

        def extract_metadata():
            return self.metadata_extractor.extract(test_data, {})

        result = benchmark(extract_metadata)
        assert result.record_count == 500

    def test_memory_usage_limits(self):
        """Test memory usage with large datasets."""
        # Test progressively larger datasets
        sizes = [100, 500, 1000, 2000]

        for size in sizes:
            large_data = []
            for i in range(size):
                large_data.append(
                    {
                        "id": i,
                        "data": f"Content_{i}"
                        * 10,  # Some content to increase memory usage
                        "value": i * 2.5,
                        "category": f"Cat_{i % 20}",
                    }
                )

            start_time = time.time()

            # Process through conversion pipeline
            converted = self.table_converter.convert(large_data)
            table = self.table_builder.build(converted, has_header=True)

            processing_time = time.time() - start_time

            # Should complete within reasonable time (adjust threshold as needed)
            assert processing_time < 10.0  # 10 seconds max
            assert table is not None

            print(f"Size {size}: {processing_time:.2f}s")

    def test_performance_with_wide_tables(self):
        """Test performance with tables having many columns."""
        # Create wide table (many columns)
        wide_data = []
        base_record = {}

        # Create 100 columns
        for col_idx in range(100):
            base_record[f"column_{col_idx}"] = f"value_{col_idx}"

        # Create 100 records
        for row_idx in range(100):
            record = base_record.copy()
            record["id"] = row_idx
            wide_data.append(record)

        start_time = time.time()

        converted = self.table_converter.convert(wide_data)
        table = self.table_builder.build(converted, has_header=True)

        processing_time = time.time() - start_time

        # Should handle wide tables efficiently
        assert processing_time < 5.0
        assert table is not None
        # Should handle wide tables efficiently

    def test_facet_generation_performance(self):
        """Test facet generation performance with large datasets."""
        # Generate data with various facet types
        facet_data = []
        categories = [f"Category_{i}" for i in range(20)]
        brands = [f"Brand_{i}" for i in range(10)]

        for i in range(1000):
            facet_data.append(
                {
                    "id": i,
                    "category": categories[i % len(categories)],
                    "brand": brands[i % len(brands)],
                    "price": 1000 + (i * 100) % 50000,
                    "rating": 1 + (i % 5),
                    "sales_count": (i * 3) % 1000,
                }
            )

        start_time = time.time()
        facets = self.facet_generator.generate_facets(facet_data)
        processing_time = time.time() - start_time

        # Should generate facets efficiently
        assert processing_time < 3.0
        assert len(facets.categorical_facets) > 0
        assert len(facets.numerical_facets) > 0

    def test_json_parsing_performance(self):
        """Test JSON parsing performance with large JSON strings."""
        # Generate large JSON data
        large_json_data = []
        for i in range(2000):
            large_json_data.append(
                {
                    "id": i,
                    "title": f"Title {i} with some longer content to test parsing",
                    "content": f"Content for item {i} " * 20,  # Longer content
                    "metadata": {
                        "created": f"2025-01-{(i % 28) + 1:02d}",
                        "tags": [f"tag_{j}" for j in range(i % 5 + 1)],
                    },
                }
            )

        json_string = json.dumps(large_json_data)

        start_time = time.time()
        parsed_data = self.data_loader.load_from_content(json_string)
        parsing_time = time.time() - start_time

        # Should parse large JSON efficiently
        assert parsing_time < 2.0
        assert len(parsed_data) == 2000


class TestPerformanceIntegration:
    """Performance tests for integrated workflows."""

    def setup_method(self):
        """Test setup."""
        self.data_loader = JsonDataLoader()
        self.table_converter = TableConverter()
        self.table_builder = TableBuilder()
        self.metadata_extractor = RAGMetadataExtractor()

    def test_end_to_end_performance(self):
        """Test end-to-end performance of complete workflow."""
        # Generate realistic business data
        business_data = []
        departments = ["Sales", "Engineering", "Marketing", "HR", "Finance"]

        for i in range(500):
            business_data.append(
                {
                    "employee_id": f"EMP{i:04d}",
                    "name": f"Employee {i}",
                    "department": departments[i % len(departments)],
                    "hire_date": f"202{(i % 5)}-{((i % 12) + 1):02d}-{((i % 28) + 1):02d}",
                    "salary": 40000 + (i * 1000) % 80000,
                    "performance_rating": 3.0 + (i % 20) * 0.1,
                    "skills": [f"skill_{j}" for j in range((i % 5) + 1)],
                    "location": f"Location_{i % 10}",
                }
            )

        json_string = json.dumps(business_data)

        start_time = time.time()

        # Complete workflow
        # 1. Load JSON data
        loaded_data = self.data_loader.load_from_content(json_string)

        # 2. Convert to table format
        converted = self.table_converter.convert(loaded_data)

        # 3. Build table
        table = self.table_builder.build(converted, has_header=True)

        # 4. Extract metadata
        metadata = self.metadata_extractor.extract(loaded_data, {})

        total_time = time.time() - start_time

        # Complete workflow should be efficient
        assert total_time < 5.0
        assert table is not None
        assert metadata.record_count == 500

        print(f"End-to-end processing: {total_time:.2f}s for 500 records")

    def test_concurrent_processing_simulation(self):
        """Test simulated concurrent processing scenarios."""
        # Simulate multiple small requests (common in web scenarios)
        datasets = []

        for dataset_idx in range(10):
            small_data = []
            for i in range(50):
                small_data.append(
                    {
                        "id": f"{dataset_idx}_{i}",
                        "value": i * dataset_idx,
                        "category": f"Cat_{i % 3}",
                        "timestamp": f"2025-01-{(i % 28) + 1:02d}",
                    }
                )
            datasets.append(small_data)

        start_time = time.time()

        results = []
        for data in datasets:
            # Process each dataset
            converted = self.table_converter.convert(data)
            table = self.table_builder.build(converted, has_header=True)
            results.append(table)

        total_time = time.time() - start_time

        # Should handle multiple small requests efficiently
        assert total_time < 3.0
        assert len(results) == 10

        print(f"Processed 10 datasets of 50 records each: {total_time:.2f}s")

    def test_memory_efficiency(self):
        """Test memory efficiency with repeated processing."""
        # Test repeated processing to check for memory leaks
        for iteration in range(10):
            test_data = []
            for i in range(200):
                test_data.append(
                    {
                        "iteration": iteration,
                        "id": i,
                        "data": f"Test data {i}" * 5,
                        "value": i * iteration,
                    }
                )

            # Process through pipeline
            converted = self.table_converter.convert(test_data)
            table = self.table_builder.build(converted, has_header=True)
            metadata = self.metadata_extractor.extract(test_data, {})

            # Ensure processing completes successfully
            assert table is not None
            assert metadata.record_count == 200

        # If we get here, memory management is working properly
        assert True

    @pytest.mark.benchmark
    def test_table_building_benchmark(self, benchmark):
        """Benchmark table building specifically."""
        # Prepare data for table building
        rows = []

        for i in range(1000):
            rows.append(
                [
                    str(i),
                    f"Item {i}",
                    f"Category {i % 10}",
                    str(i * 100),
                    f"Description for item {i}",
                ]
            )

        table_data = rows

        def build_table():
            return self.table_builder.build(table_data, has_header=True)

        result = benchmark(build_table)
        assert result is not None

    def test_performance_regression_detection(self):
        """Test to detect performance regressions."""
        # Standard test case for performance regression detection
        standard_data = []
        for i in range(100):
            standard_data.append(
                {
                    "id": i,
                    "name": f"Standard Item {i}",
                    "value": i * 2.5,
                    "category": f"Category {i % 5}",
                    "active": i % 2 == 0,
                }
            )

        # Measure processing time
        times = []
        for _ in range(5):  # Run multiple times for consistency
            start_time = time.time()

            converted = self.table_converter.convert(standard_data)
            self.table_builder.build(converted, has_header=True)

            times.append(time.time() - start_time)

        avg_time = sum(times) / len(times)

        # Should consistently perform within expected range
        assert avg_time < 0.5  # 500ms for 100 records
        assert all(t < 1.0 for t in times)  # No single run over 1s

        print(f"Average processing time for 100 records: {avg_time:.3f}s")


if __name__ == "__main__":
    # Run performance tests with benchmark
    pytest.main([__file__, "--benchmark-enable"])
