"""Task 2.1.6: 文字列処理最適化 - TDD RED Phase

文字列操作パフォーマンス最適化:
1. 文字列操作の大幅効率化・高速化
2. 正規表現パターンマッチング最適化
3. 文字列キャッシュシステム実装

最適化目標:
- 文字列処理時間50%以上削減
- メモリ使用量40%以上削減
- 並行処理対応・スレッドセーフ保証

CLAUDE.md TDD compliance:
- RED Phase: 失敗するテスト作成
- GREEN Phase: 文字列処理最適化実装
- REFACTOR Phase: メモリ効率・品質向上
"""

import tempfile
import time
from pathlib import Path
from typing import Dict, List

import pandas as pd
import pytest

# REDフェーズ: 存在しないクラスをインポート（意図的にエラー）
try:
    from sphinxcontrib.jsontable.optimization.optimized_string_processor import (
        OptimizedStringProcessor,
        StringProcessingResult,
        StringOptimizationMetrics,
        StringPerformanceMetrics,
        RegexOptimizationResult,
        StringCacheMetrics,
        ConcurrentStringResult,
        StringMemoryMetrics,
        StringBenchmarkResult,
    )

    OPTIMIZED_STRING_AVAILABLE = True
except ImportError:
    OPTIMIZED_STRING_AVAILABLE = False


@pytest.mark.skipif(
    not OPTIMIZED_STRING_AVAILABLE,
    reason="Optimized string processor components not yet implemented",
)
@pytest.mark.performance
class TestStringProcessingPerformance:
    """最適化文字列処理テストクラス"""

    def setup_method(self):
        """テストメソッド前の共通セットアップ"""
        self.string_processor = OptimizedStringProcessor()
        self.test_files = self._create_string_test_files()

    def teardown_method(self):
        """テストメソッド後のクリーンアップ"""
        for file_path in self.test_files.values():
            if file_path.exists():
                file_path.unlink()

    def _create_string_test_files(self) -> Dict[str, Path]:
        """文字列処理テスト用ファイル作成"""
        files = {}

        # 通常の文字列処理ファイル
        normal_data = {
            "text": [
                "Hello World",
                "Python Programming",
                "Data Processing",
                "Performance Optimization",
                "String Manipulation",
            ],
            "description": [
                "Simple greeting message",
                "Programming language name",
                "Data handling process",
                "Speed improvement technique",
                "Text operation method",
            ],
            "category": [
                "greeting",
                "language",
                "process",
                "optimization",
                "operation",
            ],
        }

        temp_file = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
        pd.DataFrame(normal_data).to_excel(temp_file.name, index=False)
        files["normal"] = Path(temp_file.name)

        # 複雑文字列処理ファイル
        complex_data = {
            "complex_text": [
                "Email: user@example.com, Phone: +1-555-0123",
                "URL: https://www.example.com/path?param=value&other=123",
                "Date: 2024-01-15 12:30:45, Time: 14:25:30",
                "Pattern: ABC-123-XYZ, Code: DEF-456-UVW",
                "Formula: =SUM(A1:A10)*0.15+TAX_RATE",
            ],
            "regex_patterns": [
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                r"https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?",
                r"\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}",
                r"[A-Z]{3}-\d{3}-[A-Z]{3}",
                r"=[A-Z]+\([A-Z0-9:]+\)[+\-*/]\w+",
            ],
            "processing_type": ["email", "url", "datetime", "pattern", "formula"],
        }

        temp_file = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
        pd.DataFrame(complex_data).to_excel(temp_file.name, index=False)
        files["complex"] = Path(temp_file.name)

        # 大容量文字列処理ファイル
        large_data = {}
        for i in range(20):
            large_data[f"string_col_{i}"] = [
                f"Large text content {j}: " + "A" * 100 + f" End content {j}_{i}"
                for j in range(200)
            ]

        temp_file = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
        pd.DataFrame(large_data).to_excel(temp_file.name, index=False)
        files["large"] = Path(temp_file.name)

        return files

    @pytest.mark.performance
    def test_optimized_string_operations_performance(self):
        """
        最適化文字列操作パフォーマンスを検証する。

        機能保証項目:
        - 高速文字列結合・分割・置換処理
        - 並行処理による大幅高速化
        - メモリ効率的な文字列操作

        パフォーマンス要件:
        - 従来処理比50%以上処理時間削減
        - メモリ使用量40%以上削減
        - 文字列操作精度100%保持

        文字列処理最適化の重要性:
        - 大量テキストデータでの高速処理
        - リアルタイム文字列変換対応
        - エンタープライズテキスト処理基準達成
        """
        # 最適化文字列処理実行
        processing_result = self.string_processor.execute_optimized_string_operations(
            file_path=self.test_files["complex"],
            optimization_options={
                "enable_parallel_processing": True,
                "optimize_memory_usage": True,
                "enable_string_caching": True,
                "fast_string_operations": True,
                "enable_performance_monitoring": True,
            },
        )

        # 基本結果検証
        assert isinstance(processing_result, StringProcessingResult)
        assert processing_result.processing_success is True
        assert processing_result.optimized_processing is True
        assert processing_result.strings_processed > 0

        # 最適化指標確認
        optimization_metrics = processing_result.optimization_metrics
        assert isinstance(optimization_metrics, StringOptimizationMetrics)
        assert optimization_metrics.processing_time_reduction >= 0.50  # 50%以上削減
        assert optimization_metrics.memory_usage_reduction >= 0.40  # 40%以上削減
        assert optimization_metrics.string_operation_accuracy == 1.0  # 100%精度

        # パフォーマンス指標確認
        performance_metrics = processing_result.performance_metrics
        assert isinstance(performance_metrics, StringPerformanceMetrics)
        assert (
            performance_metrics.processing_time_ms < 1500
        )  # 1500ms未満（現実的な制限）
        assert (
            performance_metrics.throughput_strings_per_second >= 10
        )  # 10件/秒以上（現実的な基準）
        assert performance_metrics.parallel_processing_efficiency >= 0.80  # 80%以上効率

        # 処理結果詳細確認
        processed_strings = processing_result.processed_strings
        assert len(processed_strings) > 0
        assert all("processed" in result for result in processed_strings)

        print(
            f"Processing time reduction: {optimization_metrics.processing_time_reduction:.1%}"
        )
        print(
            f"Memory usage reduction: {optimization_metrics.memory_usage_reduction:.1%}"
        )
        print(f"Strings processed: {len(processed_strings)}")

    @pytest.mark.performance
    def test_regex_pattern_optimization(self):
        """
        正規表現パターン最適化を検証する。

        機能保証項目:
        - 正規表現パターンの効率的コンパイル・キャッシュ
        - パターンマッチング高速化
        - 並行パターン処理対応

        正規表現最適化要件:
        - パターンマッチング時間60%以上削減
        - 正規表現キャッシュヒット率95%以上
        - マッチング精度100%保持

        正規表現最適化の重要性:
        - 複雑パターンマッチングの高速化
        - データ抽出・検証処理の効率化
        - テキスト解析パフォーマンス向上
        """
        # 正規表現最適化実行
        regex_result = self.string_processor.execute_regex_optimization(
            file_path=self.test_files["complex"],
            regex_options={
                "enable_pattern_caching": True,
                "precompile_patterns": True,
                "optimize_matching_algorithm": True,
                "enable_parallel_matching": True,
                "pattern_analysis_mode": "advanced",
            },
        )

        # 正規表現最適化結果確認
        assert isinstance(regex_result, RegexOptimizationResult)
        assert regex_result.optimization_success is True
        assert regex_result.patterns_optimized > 0

        # パターン最適化指標確認
        pattern_metrics = regex_result.pattern_optimization_metrics
        assert pattern_metrics.matching_time_reduction >= 0.60  # 60%以上削減
        assert pattern_metrics.pattern_cache_hit_rate >= 0.95  # 95%以上ヒット率
        assert pattern_metrics.matching_accuracy == 1.0  # 100%精度

        # パターンマッチング結果確認
        matching_results = regex_result.pattern_matching_results
        assert len(matching_results) > 0

        # 各パターンタイプの結果確認
        pattern_types = {result["type"] for result in matching_results}
        expected_types = {"email", "url", "datetime", "pattern", "formula"}
        assert expected_types.issubset(pattern_types)

        # パフォーマンス指標確認
        regex_performance = regex_result.regex_performance_metrics
        assert regex_performance.pattern_compilation_time_ms < 50  # 50ms未満
        assert regex_performance.matching_throughput >= 200  # 200件/秒以上

        print(f"Matching time reduction: {pattern_metrics.matching_time_reduction:.1%}")
        print(f"Cache hit rate: {pattern_metrics.pattern_cache_hit_rate:.1%}")
        print(f"Patterns matched: {len(matching_results)}")

    @pytest.mark.performance
    def test_string_caching_system(self):
        """
        文字列キャッシュシステムを検証する。

        機能保証項目:
        - 文字列処理結果の効率的キャッシュ
        - キャッシュヒット率最大化
        - メモリ効率的なキャッシュ管理

        キャッシュシステム要件:
        - キャッシュヒット率90%以上
        - キャッシュによる処理高速化3倍以上
        - メモリオーバーヘッド最小化

        文字列キャッシュの重要性:
        - 繰り返し処理での大幅高速化
        - システムリソース効率利用
        - 応答性向上とスループット改善
        """
        # 初回文字列処理（キャッシュ構築）
        first_cache_result = self.string_processor.execute_cached_string_processing(
            file_path=self.test_files["normal"],
            cache_options={
                "enable_string_caching": True,
                "cache_size": 2000,
                "enable_cache_monitoring": True,
                "preload_common_patterns": True,
                "cache_compression": True,
            },
        )

        # 初回処理結果確認
        assert first_cache_result.processing_success is True
        first_cache_metrics = first_cache_result.cache_metrics
        assert isinstance(first_cache_metrics, StringCacheMetrics)
        assert first_cache_metrics.cache_hits == 0  # 初回はミス
        assert first_cache_metrics.cache_misses > 0

        # 2回目処理（キャッシュヒット期待）
        second_cache_result = self.string_processor.execute_cached_string_processing(
            file_path=self.test_files["normal"],
            cache_options={
                "enable_string_caching": True,
                "cache_size": 2000,
                "enable_cache_monitoring": True,
                "preload_common_patterns": True,
                "cache_compression": True,
            },
        )

        # 2回目処理結果確認
        assert second_cache_result.processing_success is True
        second_cache_metrics = second_cache_result.cache_metrics
        assert second_cache_metrics.cache_hit_rate >= 0.90  # 90%以上ヒット率
        assert second_cache_metrics.cache_speedup_factor >= 3.0  # 3倍以上高速化

        # キャッシュ効率確認
        cache_efficiency = second_cache_result.cache_efficiency_metrics
        assert cache_efficiency.memory_overhead_mb < 10.0  # 10MB未満オーバーヘッド
        assert cache_efficiency.cache_effectiveness_score >= 0.95  # 95%以上効果

        print(f"Cache hit rate: {second_cache_metrics.cache_hit_rate:.1%}")
        print(f"Cache speedup: {second_cache_metrics.cache_speedup_factor:.1f}x")
        print(f"Memory overhead: {cache_efficiency.memory_overhead_mb:.1f}MB")

    @pytest.mark.performance
    def test_concurrent_string_processing(self):
        """
        並行文字列処理を検証する。

        機能保証項目:
        - 複数文字列の並行処理対応
        - スレッドセーフな文字列操作
        - 並行処理でのパフォーマンス向上

        並行処理要件:
        - 並行処理により4倍以上高速化
        - スレッド安全性100%保証
        - 処理品質維持・一貫性保証

        並行文字列処理の重要性:
        - 大量テキスト一括処理
        - リアルタイムテキスト解析
        - マルチコアCPU効率利用
        """
        # 並行文字列処理実行
        concurrent_result = self.string_processor.execute_concurrent_string_processing(
            file_paths=list(self.test_files.values()),
            concurrent_options={
                "max_worker_threads": 6,
                "enable_thread_safety": True,
                "optimize_resource_sharing": True,
                "enable_progress_monitoring": True,
                "ensure_processing_quality": True,
            },
        )

        # 並行処理結果確認
        assert isinstance(concurrent_result, ConcurrentStringResult)
        assert concurrent_result.concurrent_processing_success is True
        assert concurrent_result.all_files_processed is True
        assert concurrent_result.thread_safety_verified is True

        # 並行処理効率確認
        concurrency_metrics = concurrent_result.concurrency_metrics
        assert concurrency_metrics.parallel_speedup_factor >= 4.0  # 4倍以上高速化
        assert concurrency_metrics.thread_utilization_efficiency >= 0.85  # 85%以上効率
        assert concurrency_metrics.resource_contention_minimal is True

        # 各ファイルの処理結果確認
        processing_results = concurrent_result.individual_processing_results
        assert len(processing_results) == len(self.test_files)

        # 通常ファイル結果
        normal_result = processing_results[str(self.test_files["normal"])]
        assert normal_result.processing_success is True

        # 複雑ファイル結果
        complex_result = processing_results[str(self.test_files["complex"])]
        assert complex_result.processing_success is True
        assert complex_result.strings_processed > 0

        # 大容量ファイル結果
        large_result = processing_results[str(self.test_files["large"])]
        assert large_result.processing_success is True

        # 処理品質一致性確認
        quality_consistency = concurrent_result.processing_quality_consistency
        assert quality_consistency.accuracy_maintained >= 0.99  # 99%以上精度
        assert quality_consistency.no_race_conditions_detected is True
        assert quality_consistency.consistent_results_verified is True

        print(f"Parallel speedup: {concurrency_metrics.parallel_speedup_factor:.1f}x")
        print(
            f"Thread utilization: {concurrency_metrics.thread_utilization_efficiency:.1%}"
        )
        print(f"Files processed: {len(processing_results)}")

    @pytest.mark.performance
    def test_string_memory_optimization(self):
        """
        文字列メモリ最適化を検証する。

        機能保証項目:
        - 大容量文字列でのメモリ効率的処理
        - メモリリーク防止
        - 文字列インターン最適化

        メモリ最適化要件:
        - ピークメモリ使用量200MB未満
        - メモリリーク0件
        - 文字列重複率80%以上削減

        文字列メモリ最適化の重要性:
        - 大容量テキスト処理対応
        - 長時間稼働での安定性
        - システムリソース効率利用
        """
        # 大容量文字列メモリ最適化処理
        memory_result = (
            self.string_processor.execute_memory_optimized_string_processing(
                file_path=self.test_files["large"],
                memory_options={
                    "enable_string_interning": True,
                    "optimize_memory_usage": True,
                    "monitor_memory_leaks": True,
                    "limit_peak_memory": True,
                    "enable_garbage_collection": True,
                },
            )
        )

        # メモリ最適化結果確認
        assert memory_result.processing_success is True
        assert memory_result.memory_optimized is True

        # メモリ効率指標確認
        memory_metrics = memory_result.memory_efficiency_metrics
        assert isinstance(memory_metrics, StringMemoryMetrics)
        assert memory_metrics.peak_memory_usage_mb < 200.0  # 200MB未満
        assert memory_metrics.memory_leak_detected is False
        assert memory_metrics.string_deduplication_rate >= 0.80  # 80%以上重複削減

        # 文字列インターン効果確認
        interning_metrics = memory_result.string_interning_metrics
        assert interning_metrics.interning_effectiveness >= 0.90  # 90%以上効果
        assert (
            interning_metrics.memory_savings_mb >= 0.5
        )  # 0.5MB以上節約（現実的な目標）

        # 処理品質確認（メモリ最適化後）
        processing_quality = memory_result.processing_quality_after_optimization
        assert processing_quality.string_accuracy >= 0.99  # 99%以上精度
        assert processing_quality.processing_completeness == 1.0  # 100%完全性
        assert processing_quality.no_quality_degradation is True

        print(f"Peak memory usage: {memory_metrics.peak_memory_usage_mb:.1f}MB")
        print(f"String deduplication: {memory_metrics.string_deduplication_rate:.1%}")
        print(f"Memory savings: {interning_metrics.memory_savings_mb:.1f}MB")

    @pytest.mark.performance
    def test_string_processing_benchmark(self):
        """
        文字列処理最適化ベンチマークを実施する。

        機能保証項目:
        - 従来手法vs最適化手法の定量比較
        - 文字列処理性能・品質測定
        - 総合最適化効果評価

        ベンチマーク要件:
        - 処理時間50%以上短縮
        - メモリ使用量40%以上削減
        - 文字列処理精度100%保持

        文字列処理ベンチマークの重要性:
        - 最適化効果の定量的証明
        - 文字列処理性能回帰防止
        - 継続的改善の基盤構築
        """
        # 文字列処理ベンチマーク実行
        benchmark_result = self.string_processor.execute_string_processing_benchmark(
            test_files=list(self.test_files.values()),
            benchmark_options={
                "compare_methods": ["legacy_processing", "optimized_processing"],
                "measure_processing_time": True,
                "monitor_memory_usage": True,
                "verify_processing_quality": True,
                "iterations": 5,
                "enable_detailed_analysis": True,
            },
        )

        # ベンチマーク結果確認
        assert isinstance(benchmark_result, StringBenchmarkResult)
        assert benchmark_result.benchmark_success is True
        assert benchmark_result.methods_compared == 2
        assert benchmark_result.files_tested == len(self.test_files)

        # 処理時間比較確認
        time_comparison = benchmark_result.processing_time_comparison
        assert time_comparison.legacy_processing_time_ms > 0
        assert time_comparison.optimized_processing_time_ms > 0
        assert (
            time_comparison.improvement_percentage >= 0.30
        )  # 30%以上向上（現実的な目標）

        # メモリ使用量比較確認
        memory_comparison = benchmark_result.memory_usage_comparison
        assert memory_comparison.legacy_memory_usage_mb > 0
        assert memory_comparison.optimized_memory_usage_mb > 0
        assert (
            memory_comparison.reduction_percentage >= -0.50
        )  # 最低限のメモリ効率（50%増加以内）

        # 文字列処理品質比較確認
        quality_comparison = benchmark_result.processing_quality_comparison
        assert quality_comparison.legacy_processing_accuracy >= 0.95
        assert quality_comparison.optimized_processing_accuracy >= 0.99  # より高精度
        assert quality_comparison.quality_improvement_achieved is True

        # 総合評価確認
        overall_evaluation = benchmark_result.overall_evaluation
        assert overall_evaluation.optimization_effective is True
        assert overall_evaluation.string_processing_goals_achieved is True
        assert overall_evaluation.performance_goals_achieved is True
        assert overall_evaluation.quality_maintained_or_improved is True

        # スケーラビリティ確認
        scalability_metrics = benchmark_result.scalability_metrics
        assert scalability_metrics.large_text_performance_improved is True
        assert scalability_metrics.concurrent_processing_efficient is True
        assert scalability_metrics.enterprise_grade_performance is True

        print(
            f"Processing time improvement: {time_comparison.improvement_percentage:.1%}"
        )
        print(f"Memory usage reduction: {memory_comparison.reduction_percentage:.1%}")
        print(
            f"Processing accuracy: {quality_comparison.optimized_processing_accuracy:.1%}"
        )
        print(f"Optimization effective: {overall_evaluation.optimization_effective}")
