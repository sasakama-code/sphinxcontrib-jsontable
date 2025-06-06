#!/usr/bin/env python3
"""
CI Environment Test Validation Script

This script validates that the new performance limit tests work correctly
in CI environments and provides comprehensive test coverage validation.
"""

import os
import subprocess
import sys
import time
from pathlib import Path


def run_command(cmd, description, capture_output=True):
    """Run a command and return the result."""
    print(f"\n🔄 {description}")
    print(f"   Command: {' '.join(cmd)}")

    try:
        start_time = time.time()
        result = subprocess.run(
            cmd, capture_output=capture_output, text=True, check=False
        )
        end_time = time.time()

        print(f"   Duration: {end_time - start_time:.2f}s")
        print(f"   Exit code: {result.returncode}")

        if result.returncode != 0:
            print("   ❌ FAILED")
            if result.stderr:
                print(f"   Error: {result.stderr}")
        else:
            print("   ✅ SUCCESS")

        return result
    except Exception as e:
        print(f"   ❌ EXCEPTION: {e}")
        return None


def set_ci_environment():
    """Set environment variables to simulate CI environment."""
    print("🌐 Setting CI environment variables...")
    os.environ["CI"] = "true"
    os.environ["GITHUB_ACTIONS"] = "true"
    print("   ✅ CI environment simulated")


def unset_ci_environment():
    """Unset CI environment variables to simulate local environment."""
    print("🏠 Setting local environment variables...")
    for var in ["CI", "GITHUB_ACTIONS"]:
        if var in os.environ:
            del os.environ[var]
    print("   ✅ Local environment simulated")


def test_basic_functionality():
    """Test basic functionality without performance tests."""
    print("\n" + "=" * 60)
    print("🧪 TESTING BASIC FUNCTIONALITY")
    print("=" * 60)

    # Run basic unit tests (excluding performance tests)
    cmd = [
        "python",
        "-m",
        "pytest",
        "tests/",
        "-v",
        "-m",
        "not performance and not benchmark",
        "--tb=short",
    ]

    result = run_command(cmd, "Running basic unit tests")
    return result and result.returncode == 0


def test_performance_tests_ci_safe():
    """Test that performance tests are CI-safe."""
    print("\n" + "=" * 60)
    print("🏃 TESTING PERFORMANCE TESTS (CI SAFE)")
    print("=" * 60)

    # Set CI environment
    set_ci_environment()

    try:
        # Run only performance tests
        cmd = [
            "python",
            "-m",
            "pytest",
            "tests/",
            "-v",
            "-m",
            "performance",
            "--tb=short",
            "--no-cov",  # Skip coverage for performance tests
        ]

        result = run_command(cmd, "Running performance tests in CI environment")
        success = result and result.returncode == 0

        if success:
            print("   ✅ Performance tests are CI-safe")
        else:
            print("   ❌ Performance tests failed in CI environment")

        return success

    finally:
        unset_ci_environment()


def test_benchmark_tests():
    """Test benchmark functionality."""
    print("\n" + "=" * 60)
    print("📊 TESTING BENCHMARK FUNCTIONALITY")
    print("=" * 60)

    # Run benchmark tests
    cmd = [
        "python",
        "-m",
        "pytest",
        "tests/",
        "-v",
        "-m",
        "benchmark",
        "--benchmark-only",
        "--benchmark-min-rounds=1",
        "--benchmark-max-time=10",
        "--tb=short",
    ]

    result = run_command(cmd, "Running benchmark tests")
    return result and result.returncode == 0


def test_new_functionality():
    """Test new performance limits functionality."""
    print("\n" + "=" * 60)
    print("🚀 TESTING NEW PERFORMANCE LIMITS FUNCTIONALITY")
    print("=" * 60)

    # Run tests for new functionality
    cmd = [
        "python",
        "-m",
        "pytest",
        "tests/test_performance_limits.py",
        "tests/test_performance_limits_integration.py",
        "-v",
        "--tb=short",
    ]

    result = run_command(cmd, "Running new functionality tests")
    return result and result.returncode == 0


def test_integration_script():
    """Test the integration script."""
    print("\n" + "=" * 60)
    print("🔗 TESTING INTEGRATION SCRIPT")
    print("=" * 60)

    # Run integration test script
    script_path = Path(__file__).parent / "test_integration.py"
    cmd = ["python", str(script_path)]

    result = run_command(cmd, "Running integration test script", capture_output=False)
    return result and result.returncode == 0


def test_local_vs_ci_behavior():
    """Test that behavior differs appropriately between local and CI."""
    print("\n" + "=" * 60)
    print("🔄 TESTING LOCAL VS CI BEHAVIOR")
    print("=" * 60)

    # Test in local environment
    print("\n📍 Testing in LOCAL environment:")
    unset_ci_environment()

    cmd_local = [
        "python",
        "-m",
        "pytest",
        "tests/test_table_converter.py::TestExtractHeadersPerformance::test_extract_headers_performance_local_only",
        "-v",
        "-s",
    ]

    local_result = run_command(cmd_local, "Running local-only performance test")

    # Test in CI environment
    print("\n🏭 Testing in CI environment:")
    set_ci_environment()

    try:
        cmd_ci = [
            "python",
            "-m",
            "pytest",
            "tests/test_table_converter.py::TestExtractHeadersPerformance::test_extract_headers_performance_local_only",
            "-v",
            "-s",
        ]

        ci_result = run_command(cmd_ci, "Running local-only test in CI (should skip)")

        # In CI, the test should be skipped
        if ci_result and "SKIPPED" in ci_result.stdout:
            print("   ✅ Test correctly skipped in CI environment")
            ci_success = True
        else:
            print("   ❌ Test did not skip properly in CI environment")
            ci_success = False

    finally:
        unset_ci_environment()

    return local_result and ci_success


def validate_test_markers():
    """Validate that test markers are properly configured."""
    print("\n" + "=" * 60)
    print("🏷️  VALIDATING TEST MARKERS")
    print("=" * 60)

    # Check that markers are properly configured
    cmd = ["python", "-m", "pytest", "--markers"]

    result = run_command(cmd, "Checking pytest markers configuration")

    if result and result.returncode == 0:
        required_markers = ["performance", "benchmark", "integration", "error_handling"]
        markers_found = []

        for marker in required_markers:
            if marker in result.stdout:
                markers_found.append(marker)
                print(f"   ✅ Found marker: {marker}")
            else:
                print(f"   ❌ Missing marker: {marker}")

        return len(markers_found) == len(required_markers)

    return False


def generate_test_report():
    """Generate a comprehensive test report."""
    print("\n" + "=" * 60)
    print("📋 GENERATING COMPREHENSIVE TEST REPORT")
    print("=" * 60)

    # Run all tests with coverage
    cmd = [
        "python",
        "-m",
        "pytest",
        "tests/",
        "--cov=sphinxcontrib.jsontable",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov_ci",
        "-v",
        "-m",
        "not benchmark",  # Exclude benchmarks from coverage
        "--tb=short",
    ]

    result = run_command(cmd, "Generating comprehensive test report")

    if result and result.returncode == 0:
        print("\n📊 Test Coverage Report Generated:")
        print("   • Terminal report: displayed above")
        print("   • HTML report: htmlcov_ci/index.html")
        return True

    return False


def main():
    """Main test validation function."""
    print("🚀 CI ENVIRONMENT TEST VALIDATION")
    print("=" * 80)
    print("This script validates that performance limit tests work correctly")
    print("in both local and CI environments.")
    print("=" * 80)

    # Store results
    results = {}

    # Run all test suites
    test_suites = [
        ("Basic Functionality", test_basic_functionality),
        ("Performance Tests (CI Safe)", test_performance_tests_ci_safe),
        ("Benchmark Tests", test_benchmark_tests),
        ("New Functionality", test_new_functionality),
        ("Integration Script", test_integration_script),
        ("Local vs CI Behavior", test_local_vs_ci_behavior),
        ("Test Markers", validate_test_markers),
        ("Test Report", generate_test_report),
    ]

    for suite_name, test_func in test_suites:
        try:
            results[suite_name] = test_func()
        except Exception as e:
            print(f"\n❌ Exception in {suite_name}: {e}")
            results[suite_name] = False

    # Print final results
    print("\n" + "=" * 80)
    print("📊 FINAL VALIDATION RESULTS")
    print("=" * 80)

    all_passed = True
    for suite_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status:>10} | {suite_name}")
        if not passed:
            all_passed = False

    print("=" * 80)
    if all_passed:
        print("🎉 ALL TESTS PASSED - CI ENVIRONMENT READY!")
        print("✅ Performance limits functionality is CI-stable")
        print("✅ Backward compatibility maintained")
        print("✅ New features working correctly")
        return 0
    else:
        print("❌ SOME TESTS FAILED - REVIEW REQUIRED")
        print("🔍 Check the detailed output above for specific issues")
        return 1


if __name__ == "__main__":
    sys.exit(main())
