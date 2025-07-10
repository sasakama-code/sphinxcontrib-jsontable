"""大容量ファイル対応テスト

TDD REDフェーズ: 失敗するテストを先に作成
Task 1.1.6: 大容量ファイル対応テスト
"""

import gc
import tempfile
import time
from pathlib import Path

import pandas as pd
import pytest

from sphinxcontrib.jsontable.core.dataframe_memory_pool import DataFrameMemoryPool
from sphinxcontrib.jsontable.core.large_file_processor import (
    ComponentCoordinator,
    ConcurrentLargeFileProcessor,
    ErrorRecoveryProcessor,
    LargeFileProcessor,
    MemoryConstrainedProcessor,
    PerformanceBenchmarker,
)
from sphinxcontrib.jsontable.core.memory_monitor import MemoryMonitor
from sphinxcontrib.jsontable.core.optimized_chunk_processor import (
    OptimizedChunkProcessor,
)
from sphinxcontrib.jsontable.core.range_view_processor import RangeViewProcessor
from sphinxcontrib.jsontable.core.streaming_excel_reader import StreamingExcelReader


class TestLargeFileProcessing:
    """大容量ファイル処理テスト

    TDD REDフェーズ: 大容量ファイル処理機能が存在しないため、
    これらのテストは意図的に失敗する。
    """

    def setup_method(self):
        """各テストメソッドの前に実行される設定."""
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """各テストメソッドの後に実行されるクリーンアップ."""
        import shutil

        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_large_test_file(
        self, target_size_mb: int = 100, filename: str = "large_test.xlsx"
    ) -> Path:
        """大容量テストファイル作成

        Args:
            target_size_mb: 目標ファイルサイズ（MB）
            filename: ファイル名

        Returns:
            Path: 作成されたファイルのパス
        """
        file_path = self.temp_dir / filename

        # 目標サイズに達するまでデータを生成
        # 1行あたり約500バイト想定、100MB = 約200,000行
        estimated_rows = (target_size_mb * 1024 * 1024) // 500

        print(
            f"Creating large file: {target_size_mb}MB target, ~{estimated_rows:,} rows"
        )

        # 一括でDataFrame作成（メモリ効率的な方法）
        all_data = {
            "ID": [f"ID{i:08d}" for i in range(estimated_rows)],
            "Name": [
                f"Name_{i}_with_long_content_for_size" for i in range(estimated_rows)
            ],
            "Value": [i * 123.456789 for i in range(estimated_rows)],
            "Category": [
                f"Category_{i % 100}_with_extra_content" for i in range(estimated_rows)
            ],
            "Description": [
                f"Description for item {i} with detailed information and extra content for size"
                for i in range(estimated_rows)
            ],
            "Status": [
                f"Status_{i % 20}_active_inactive" for i in range(estimated_rows)
            ],
            "Timestamp": [
                f"2025-01-{(i % 28) + 1:02d} 12:34:56" for i in range(estimated_rows)
            ],
            "Score": [(i * 7) % 1000 for i in range(estimated_rows)],
            "Notes": [
                f"Notes for item {i} " * 3 for i in range(estimated_rows)
            ],  # 長いテキスト
            "Metadata": [
                f'{{"id": {i}, "type": "test", "extra": "data_content"}}'
                for i in range(estimated_rows)
            ],
        }

        # DataFrame作成とExcel出力
        large_df = pd.DataFrame(all_data)
        large_df.to_excel(file_path, index=False)

        # ファイルサイズ確認
        actual_size_mb = file_path.stat().st_size / 1024 / 1024
        print(f"Created file: {actual_size_mb:.1f}MB")

        # メモリクリーンアップ
        del large_df, all_data
        gc.collect()

        return file_path

    @pytest.mark.performance
    def test_large_file_processing_100mb(self):
        """大容量ファイル処理基本テスト（100MB）

        RED: 大容量ファイル処理統合機能が存在しないため失敗する
        期待動作:
        - 100MB以上ファイルの効率的処理
        - 全基盤コンポーネント統合動作
        - メモリ使用量制限遵守
        - パフォーマンス向上効果確認
        """
        # 大容量ファイル作成（テスト用に小さめ）
        large_file = self.create_large_test_file(target_size_mb=10)

        # 統合処理システム初期化
        integrated_processor = LargeFileProcessor(
            streaming_chunk_size=5000,
            memory_limit_mb=500,
            enable_all_optimizations=True,
            enable_performance_tracking=True,
        )

        # 処理開始前のメモリ使用量
        initial_memory = integrated_processor.get_initial_memory_usage()

        # 大容量ファイル処理実行
        start_time = time.perf_counter()

        processing_result = integrated_processor.process_large_file(
            file_path=large_file, processing_mode="streaming_optimized"
        )

        processing_time = time.perf_counter() - start_time

        # 処理結果検証
        assert processing_result is not None
        assert processing_result.success is True
        assert processing_result.rows_processed > 0
        assert processing_result.chunks_processed > 0

        # メモリ使用量確認
        peak_memory = integrated_processor.get_peak_memory_usage()
        memory_increase = peak_memory - initial_memory
        assert memory_increase <= 500 * 1024 * 1024  # 500MB以内

        # パフォーマンス統計確認
        perf_stats = integrated_processor.get_performance_statistics()
        assert "total_processing_time" in perf_stats
        assert "memory_efficiency_ratio" in perf_stats
        assert "component_utilization" in perf_stats

        # 統合コンポーネント効果確認
        component_stats = integrated_processor.get_component_statistics()
        assert component_stats["streaming_reader_usage"] > 0
        assert component_stats["chunk_processor_usage"] > 0
        assert component_stats["memory_monitor_alerts"] >= 0
        assert component_stats["range_processor_usage"] >= 0
        assert component_stats["memory_pool_hits"] >= 0

        # パフォーマンス向上効果確認
        efficiency_metrics = integrated_processor.get_efficiency_metrics()
        assert efficiency_metrics["overall_efficiency"] >= 1.2  # 20%以上改善
        assert efficiency_metrics["memory_optimization"] >= 1.1  # 10%以上メモリ効率化

        print(
            f"Large file processing completed: {processing_time:.2f}s, {memory_increase / 1024 / 1024:.1f}MB peak"
        )

    @pytest.mark.performance
    def test_integrated_component_coordination(self):
        """統合コンポーネント協調動作テスト

        RED: 統合コンポーネント協調機能が存在しないため失敗する
        期待動作:
        - 5つの基盤コンポーネント協調動作
        - 効率的リソース共有
        - 統合パフォーマンス最適化
        """
        # 中規模ファイル作成（協調動作テスト用）
        test_file = self.create_large_test_file(
            target_size_mb=50, filename="coordination_test.xlsx"
        )

        # 統合コンポーネント初期化
        coordinator = ComponentCoordinator(
            enable_resource_sharing=True,
            enable_cross_component_optimization=True,
            coordination_strategy="adaptive",
        )

        # 各コンポーネント登録
        streaming_reader = StreamingExcelReader(chunk_size=2000)
        chunk_processor = OptimizedChunkProcessor(
            chunk_size=2000, max_workers=2, enable_parallel_processing=True
        )
        memory_monitor = MemoryMonitor(monitoring_interval=1.0)
        range_processor = RangeViewProcessor(enable_view_optimization=True)
        memory_pool = DataFrameMemoryPool(max_pool_size=15, max_memory_mb=1000)

        coordinator.register_components(
            streaming_reader=streaming_reader,
            chunk_processor=chunk_processor,
            memory_monitor=memory_monitor,
            range_processor=range_processor,
            memory_pool=memory_pool,
        )

        # 協調処理実行
        coordination_result = coordinator.process_with_coordination(test_file)

        # 協調動作確認
        assert coordination_result.coordination_success is True
        assert coordination_result.component_interactions > 0
        assert coordination_result.resource_sharing_events > 0

        # 各コンポーネント利用確認
        component_usage = coordinator.get_component_usage_statistics()
        assert all(usage > 0 for usage in component_usage.values())

        # 協調効果確認
        coordination_efficiency = coordinator.get_coordination_efficiency()
        assert coordination_efficiency["resource_utilization"] >= 0.8  # 80%以上
        assert (
            coordination_efficiency["cross_component_synergy"] >= 1.1
        )  # 10%以上シナジー効果

    @pytest.mark.performance
    def test_memory_pressure_handling(self):
        """メモリ圧迫時処理テスト

        RED: メモリ圧迫時処理機能が存在しないため失敗する
        期待動作:
        - メモリ制限下での適切な処理継続
        - 自動最適化とリソース管理
        - 優雅なデグラデーション
        """
        # 大容量ファイル作成
        large_file = self.create_large_test_file(target_size_mb=80)

        # メモリ制限処理システム
        memory_constrained_processor = MemoryConstrainedProcessor(
            strict_memory_limit_mb=200,  # 厳しいメモリ制限
            enable_adaptive_processing=True,
            enable_graceful_degradation=True,
        )

        # メモリ圧迫シミュレーション
        with memory_constrained_processor.simulate_memory_pressure():
            processing_result = memory_constrained_processor.process_under_pressure(
                large_file
            )

        # メモリ制限遵守確認
        assert processing_result.memory_limit_exceeded is False
        assert processing_result.peak_memory_mb <= 200

        # 適応的処理確認
        adaptation_stats = memory_constrained_processor.get_adaptation_statistics()
        assert adaptation_stats["chunk_size_adaptations"] >= 0
        assert adaptation_stats["processing_mode_changes"] >= 0
        assert adaptation_stats["memory_optimization_triggers"] >= 0

        # 処理完了確認
        assert processing_result.processing_completed is True
        assert processing_result.data_integrity_maintained is True

    @pytest.mark.performance
    def test_concurrent_large_file_processing(self):
        """並行大容量ファイル処理テスト

        RED: 並行大容量ファイル処理機能が存在しないため失敗する
        期待動作:
        - 複数大容量ファイルの並行処理
        - リソース競合回避
        - スケーラブルな処理性能
        """
        import threading

        # 複数の大容量ファイル作成
        files = []
        for i in range(3):
            file_path = self.create_large_test_file(
                target_size_mb=40, filename=f"concurrent_test_{i}.xlsx"
            )
            files.append(file_path)

        # 並行処理システム
        concurrent_processor = ConcurrentLargeFileProcessor(
            max_concurrent_files=3,
            shared_resource_pool=True,
            enable_load_balancing=True,
        )

        results = []
        errors = []

        def process_file_concurrently(file_path, thread_id):
            try:
                result = concurrent_processor.process_file_async(
                    file_path=file_path, thread_id=thread_id
                )
                results.append(result)
            except Exception as e:
                errors.append({"thread_id": thread_id, "error": str(e)})

        # 並行スレッド実行
        threads = []
        for i, file_path in enumerate(files):
            thread = threading.Thread(
                target=process_file_concurrently, args=(file_path, i)
            )
            threads.append(thread)
            thread.start()

        # 全スレッド完了待機
        for thread in threads:
            thread.join()

        # 並行処理結果確認
        assert len(errors) == 0  # エラーなし
        assert len(results) == 3  # 全ファイル処理成功

        # 並行処理効率確認
        concurrent_stats = concurrent_processor.get_concurrent_statistics()
        assert concurrent_stats["resource_contention_ratio"] <= 0.2  # 20%以下の競合
        assert concurrent_stats["load_balancing_efficiency"] >= 0.8  # 80%以上の効率

    @pytest.mark.performance
    def test_error_recovery_large_files(self):
        """大容量ファイルエラー回復テスト

        RED: 大容量ファイルエラー回復機能が存在しないため失敗する
        期待動作:
        - ファイル破損時の適切な処理
        - 部分処理結果の保持
        - 自動回復とリトライ機能
        """
        # 正常ファイルと破損ファイル作成
        normal_file = self.create_large_test_file(
            target_size_mb=60, filename="normal_large.xlsx"
        )

        # 破損ファイルシミュレーション（存在しないファイル）
        corrupted_file = self.temp_dir / "corrupted_large.xlsx"

        # エラー回復処理システム
        error_recovery_processor = ErrorRecoveryProcessor(
            enable_automatic_retry=True,
            max_retry_attempts=3,
            enable_partial_processing=True,
            enable_corruption_detection=True,
        )

        # 破損ファイル処理テスト
        with pytest.raises(FileNotFoundError):
            error_recovery_processor.process_with_error_handling(corrupted_file)

        # エラー統計確認
        error_stats = error_recovery_processor.get_error_statistics()
        assert error_stats["file_errors"] >= 1
        assert error_stats["recovery_attempts"] >= 1

        # 正常ファイル処理確認（回復能力テスト）
        recovery_result = error_recovery_processor.process_with_error_handling(
            normal_file
        )
        assert recovery_result.processing_success is True
        assert recovery_result.error_recovery_triggered is False

        # 回復統計確認
        recovery_stats = error_recovery_processor.get_recovery_statistics()
        assert recovery_stats["successful_recoveries"] >= 0
        assert recovery_stats["partial_processing_events"] >= 0

    @pytest.mark.performance
    def test_performance_benchmarking(self):
        """パフォーマンスベンチマークテスト

        RED: パフォーマンスベンチマーク機能が存在しないため失敗する
        期待動作:
        - 従来処理vs最適化処理の比較
        - 定量的パフォーマンス改善測定
        - ベンチマーク結果の可視化
        """
        # ベンチマーク用ファイル作成
        benchmark_file = self.create_large_test_file(
            target_size_mb=70, filename="benchmark_test.xlsx"
        )

        # パフォーマンスベンチマーカー
        benchmarker = PerformanceBenchmarker(
            enable_detailed_metrics=True,
            enable_comparative_analysis=True,
            benchmark_iterations=3,
        )

        # 従来処理ベンチマーク
        traditional_metrics = benchmarker.benchmark_traditional_processing(
            benchmark_file
        )

        # 最適化処理ベンチマーク
        optimized_metrics = benchmarker.benchmark_optimized_processing(benchmark_file)

        # パフォーマンス比較
        comparison = benchmarker.compare_performance(
            traditional_metrics, optimized_metrics
        )

        # 改善効果確認
        assert comparison.processing_time_improvement >= 1.2  # 20%以上高速化
        assert comparison.memory_usage_improvement >= 1.1  # 10%以上メモリ効率化
        assert comparison.overall_efficiency_score >= 1.15  # 15%以上総合改善

        # ベンチマーク詳細確認
        detailed_metrics = benchmarker.get_detailed_metrics()
        assert "streaming_efficiency" in detailed_metrics
        assert "chunk_processing_efficiency" in detailed_metrics
        assert "memory_optimization_efficiency" in detailed_metrics
        assert "component_integration_efficiency" in detailed_metrics

        # 結果可視化確認
        visualization_data = benchmarker.generate_visualization_data()
        assert "performance_charts" in visualization_data
        assert "comparison_tables" in visualization_data

        print(
            f"Performance improvement: {comparison.processing_time_improvement:.1f}x speed, {comparison.memory_usage_improvement:.1f}x memory efficiency"
        )
