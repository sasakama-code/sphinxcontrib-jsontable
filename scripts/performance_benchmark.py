#!/usr/bin/env python3
"""
Performance benchmark script for large dataset analysis.

This script measures the actual performance characteristics of the TableConverter
with various data sizes to understand the current limitations and guide the
implementation of performance safeguards.
"""

import sys
import time
import traceback
import tracemalloc
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sphinxcontrib.jsontable.directives import TableConverter  # noqa: E402


def generate_large_dataset(size: int, keys_per_object: int = 10) -> list[dict]:
    """Generate a large dataset for performance testing."""
    print(f"🔄 Generating dataset: {size:,} objects, {keys_per_object} keys each...")

    dataset = []
    for i in range(size):
        obj = {}
        for j in range(keys_per_object):
            obj[f"field_{j:02d}"] = f"value_{i}_{j}"
        # Add some variable fields to simulate real-world data
        if i % 3 == 0:
            obj["optional_field"] = f"optional_{i}"
        if i % 5 == 0:
            obj["rare_field"] = f"rare_{i}"
        dataset.append(obj)

    return dataset


def measure_memory_usage(func, *args, **kwargs):
    """Measure peak memory usage during function execution."""
    tracemalloc.start()

    try:
        result = func(*args, **kwargs)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        return result, current, peak
    except Exception as e:
        tracemalloc.stop()
        raise e


def benchmark_table_converter():
    """Run comprehensive benchmarks on TableConverter."""
    print("🚀 Starting TableConverter Performance Benchmark")
    print("=" * 60)

    converter = TableConverter()

    # Test sizes: from small to very large
    test_sizes = [100, 1000, 5000, 10000, 25000, 50000, 100000]

    results = []

    for size in test_sizes:
        print(f"\n📊 Testing with {size:,} objects...")

        # Generate test data
        start_time = time.perf_counter()
        dataset = generate_large_dataset(size, keys_per_object=8)
        generation_time = time.perf_counter() - start_time

        print(f"   ⏱️  Data generation: {generation_time:.3f}s")

        # Test _extract_headers performance
        start_time = time.perf_counter()
        headers, current_mem, peak_mem = measure_memory_usage(
            converter._extract_headers, dataset
        )
        headers_time = time.perf_counter() - start_time

        print(f"   🏷️  Header extraction: {headers_time:.3f}s")
        print(f"   🧠 Memory usage: {peak_mem / 1024 / 1024:.1f} MB peak")
        print(f"   📝 Headers found: {len(headers)}")

        # Test full conversion performance
        start_time = time.perf_counter()
        table_data, current_mem_full, peak_mem_full = measure_memory_usage(
            converter.convert, dataset, include_header=True, limit=None
        )
        conversion_time = time.perf_counter() - start_time

        print(f"   🔄 Full conversion: {conversion_time:.3f}s")
        print(f"   🧠 Full memory: {peak_mem_full / 1024 / 1024:.1f} MB peak")
        print(f"   📋 Rows generated: {len(table_data):,}")

        # Calculate rates
        headers_rate = size / headers_time if headers_time > 0 else float("inf")
        conversion_rate = (
            size / conversion_time if conversion_time > 0 else float("inf")
        )

        print(f"   ⚡ Header rate: {headers_rate:,.0f} objects/sec")
        print(f"   ⚡ Conversion rate: {conversion_rate:,.0f} objects/sec")

        results.append(
            {
                "size": size,
                "headers_time": headers_time,
                "conversion_time": conversion_time,
                "headers_memory_mb": peak_mem / 1024 / 1024,
                "conversion_memory_mb": peak_mem_full / 1024 / 1024,
                "headers_rate": headers_rate,
                "conversion_rate": conversion_rate,
                "headers_count": len(headers),
                "rows_count": len(table_data),
            }
        )

        # Early exit if performance becomes unreasonable
        if conversion_time > 30.0:  # 30 seconds threshold
            print(f"   ⚠️  Performance threshold exceeded ({conversion_time:.1f}s)")
            break

    print("\n" + "=" * 60)
    print("📊 BENCHMARK RESULTS SUMMARY")
    print("=" * 60)

    for result in results:
        print(
            f"Size: {result['size']:>6,} | "
            f"Headers: {result['headers_time']:>6.3f}s | "
            f"Convert: {result['conversion_time']:>6.3f}s | "
            f"Memory: {result['conversion_memory_mb']:>5.1f}MB | "
            f"Rate: {result['conversion_rate']:>7,.0f} obj/s"
        )

    # Analysis and recommendations
    print("\n🔍 ANALYSIS & RECOMMENDATIONS")
    print("-" * 40)

    # Find performance degradation points
    large_datasets = [r for r in results if r["size"] >= 10000]
    if large_datasets:
        avg_rate = sum(r["conversion_rate"] for r in large_datasets) / len(
            large_datasets
        )
        max_memory = max(r["conversion_memory_mb"] for r in large_datasets)

        print(f"📈 Large dataset avg rate: {avg_rate:,.0f} objects/sec")
        print(f"🧠 Max memory usage: {max_memory:.1f} MB")

        # Recommend default limit based on performance
        recommended_limit = None
        for result in results:
            if result["conversion_time"] > 5.0:  # 5 second threshold
                recommended_limit = result["size"] // 2
                break

        if recommended_limit:
            print(f"💡 Recommended DEFAULT_MAX_ROWS: {recommended_limit:,}")
        else:
            print("💡 Recommended DEFAULT_MAX_ROWS: 10,000 (conservative)")

    return results


def benchmark_with_limit():
    """Test performance improvement with limit applied."""
    print("\n🎯 Testing Performance with Limit Applied")
    print("=" * 50)

    converter = TableConverter()

    # Generate very large dataset
    large_dataset = generate_large_dataset(50000, keys_per_object=10)

    limits = [None, 50000, 25000, 10000, 5000, 1000]

    for limit in limits:
        print(f"\n🔢 Testing with limit: {limit if limit else 'None'}")

        start_time = time.perf_counter()
        table_data, current_mem, peak_mem = measure_memory_usage(
            converter.convert, large_dataset, include_header=True, limit=limit
        )
        processing_time = time.perf_counter() - start_time

        actual_rows = len(table_data)
        memory_mb = peak_mem / 1024 / 1024
        rate = (
            (limit or len(large_dataset)) / processing_time
            if processing_time > 0
            else float("inf")
        )

        print(f"   ⏱️  Time: {processing_time:.3f}s")
        print(f"   🧠 Memory: {memory_mb:.1f} MB")
        print(f"   📋 Rows: {actual_rows:,}")
        print(f"   ⚡ Rate: {rate:,.0f} obj/s")


if __name__ == "__main__":
    try:
        # Run main benchmarks
        results = benchmark_table_converter()

        # Test limit effectiveness
        benchmark_with_limit()

        print("\n✅ Benchmark completed successfully!")

    except KeyboardInterrupt:
        print("\n⚠️  Benchmark interrupted by user")
    except Exception as e:
        print(f"\n❌ Benchmark failed: {e}")
        traceback.print_exc()
