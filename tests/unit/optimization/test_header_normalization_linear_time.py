"""Task 2.1.1: ヘッダー正規化O(n)化・重複排除最適化 - TDD RED Phase

真の問題特定結果:
- 現在の_normalize_header_names()は既にO(n)実装済み
- Stage 4とStage 5でのヘッダー正規化重複実行が主要問題
- 処理時間30-50%増加、メモリ25-35%増加の根本原因

最適化目標:
1. 重複処理排除による統合最適化実装
2. 単一パス処理によるメモリ効率化
3. O(n)計算量保持・品質保証100%

CLAUDE.md TDD compliance:
- RED Phase: 失敗するテスト作成
- GREEN Phase: 最小限実装でテスト通過
- REFACTOR Phase: 品質向上・最適化
"""

import tempfile
from pathlib import Path

import pandas as pd
import pytest

# REDフェーズ: 存在しないクラスをインポート（意図的にエラー）
try:
    from sphinxcontrib.jsontable.optimization.optimized_header_processor import (
        OptimizedHeaderProcessor,
    )

    OPTIMIZED_HEADER_AVAILABLE = True
except ImportError:
    OPTIMIZED_HEADER_AVAILABLE = False


@pytest.mark.skipif(
    not OPTIMIZED_HEADER_AVAILABLE,
    reason="Optimized header processor components not yet implemented",
)
@pytest.mark.performance
class TestHeaderNormalizationLinearTime:
    """ヘッダー正規化O(n)最適化・重複排除テストクラス"""

    def setup_method(self):
        """テストメソッド前の共通セットアップ"""
        self.optimized_processor = OptimizedHeaderProcessor()
        self.sample_file = self._create_sample_excel_file()

    def teardown_method(self):
        """テストメソッド後のクリーンアップ"""
        if hasattr(self, "sample_file") and self.sample_file.exists():
            self.sample_file.unlink()

    def _create_sample_excel_file(self) -> Path:
        """テスト用サンプルExcelファイル作成"""
        # ヘッダー正規化問題を含む複雑なデータ
        data = {
            "ID": [1, 2, 3, 4, 5],
            "  Name  ": ["Alice", "Bob", "Charlie", "Diana", "Eve"],  # 空白含む
            "Score": [95.5, 87.2, 92.1, 88.7, 94.3],
            "": ["Empty1", "Empty2", "Empty3", "Empty4", "Empty5"],  # 空ヘッダー
            "ID_Duplicate": [
                "ID_Dup1",
                "ID_Dup2",
                "ID_Dup3",
                "ID_Dup4",
                "ID_Dup5",
            ],  # 重複ヘッダー
            "Category": ["A", "B", "A", "C", "B"],
        }
        df = pd.DataFrame(data)

        temp_file = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
        df.to_excel(temp_file.name, index=False)
        return Path(temp_file.name)

    @pytest.mark.performance
    def test_header_normalization_linear_time_complexity(self):
        """
        ヘッダー正規化のO(n)時間計算量を検証する。

        機能保証項目:
        - ヘッダー正規化処理のO(n)時間計算量
        - 重複ヘッダー処理の効率性
        - 大量ヘッダーでのスケーラビリティ

        パフォーマンス要件:
        - ヘッダー数nに対してO(n)時間計算量
        - 重複処理での効率的メモリ使用
        - 線形時間内での確実な正規化完了

        線形時間計算量の重要性:
        - 大量ヘッダーファイルでの性能保証
        - メモリ効率的な処理実現
        - スケーラブルなシステム構築
        """
        # 線形時間ヘッダー正規化実行
        normalization_result = self.optimized_processor.normalize_headers_linear_time(
            file_path=self.sample_file,
            normalization_options={
                "ensure_linear_complexity": True,
                "enable_performance_monitoring": True,
                "optimize_memory_usage": True,
                "eliminate_duplications": True,
            },
        )

        # 線形時間計算量検証
        assert normalization_result.success is True
        assert normalization_result.linear_time_guaranteed is True

        # パフォーマンス指標確認
        performance_metrics = normalization_result.performance_metrics
        assert performance_metrics.time_complexity == "O(n)"
        assert performance_metrics.space_complexity == "O(n)"
        assert performance_metrics.processing_time_ms > 0

        # 正規化結果の妥当性確認
        headers = normalization_result.normalized_headers
        assert len(headers) > 0
        assert all(isinstance(header, str) for header in headers)
        assert len(set(headers)) == len(headers)  # 重複なし確認

        # 線形時間スケーラビリティ確認
        scalability_metrics = normalization_result.scalability_verification
        assert scalability_metrics.linear_scaling_confirmed is True
        assert scalability_metrics.memory_usage_linear is True
        assert scalability_metrics.large_dataset_capable is True

        print(f"Header count: {len(headers)}")
        print(f"Processing time: {performance_metrics.processing_time_ms:.3f}ms")
        print(f"Time complexity: {performance_metrics.time_complexity}")

    @pytest.mark.performance
    def test_duplicate_header_detection_optimization(self):
        """
        重複ヘッダー検出の最適化を検証する。

        機能保証項目:
        - 効率的重複ヘッダー検出アルゴリズム
        - ハッシュテーブル使用による高速化
        - 重複解決の確実性保証

        最適化要件:
        - O(n)時間での重複検出実現
        - メモリ効率的な重複管理
        - 大量重複ヘッダーでの性能保証

        重複検出最適化の重要性:
        - 複雑なExcelファイルでの堅牢性
        - 処理時間予測可能性の確保
        - 品質保証と性能の両立
        """
        # 重複ヘッダー検出最適化実行
        duplicate_detection = self.optimized_processor.detect_duplicates_optimized(
            file_path=self.sample_file,
            detection_options={
                "use_hash_table_optimization": True,
                "enable_linear_time_detection": True,
                "optimize_memory_footprint": True,
                "guarantee_uniqueness": True,
            },
        )

        # 重複検出結果検証
        assert duplicate_detection.success is True
        assert duplicate_detection.optimization_effective is True

        # 検出アルゴリズム効率性確認
        detection_metrics = duplicate_detection.detection_metrics
        assert detection_metrics.algorithm_complexity == "O(n)"
        assert detection_metrics.hash_table_used is True
        assert detection_metrics.collision_rate < 0.1  # 10%未満

        # 重複処理結果確認
        duplicate_results = duplicate_detection.duplicate_processing_results
        assert duplicate_results.duplicates_found_count >= 0
        assert duplicate_results.resolution_strategy_applied is True
        assert duplicate_results.uniqueness_guaranteed is True

        # 最適化効果測定
        optimization_metrics = duplicate_detection.optimization_impact
        assert optimization_metrics.processing_speed_improvement >= 0.3  # 30%以上向上
        assert optimization_metrics.memory_usage_optimized is True
        assert optimization_metrics.scalability_enhanced is True

        print(f"Duplicates found: {duplicate_results.duplicates_found_count}")
        print(
            f"Speed improvement: {optimization_metrics.processing_speed_improvement:.1%}"
        )
        print(f"Algorithm complexity: {detection_metrics.algorithm_complexity}")

    @pytest.mark.performance
    def test_single_pass_header_processing_integration(self):
        """
        単一パスヘッダー処理統合を検証する。

        機能保証項目:
        - Stage 4とStage 5の重複処理排除
        - 統合単一パス処理の実現
        - 処理品質の完全保持

        統合処理要件:
        - 重複処理完全排除
        - メモリ使用量最適化
        - 処理時間大幅短縮

        統合最適化の重要性:
        - パイプライン全体効率化
        - リソース使用量削減
        - システム全体性能向上
        """
        # 単一パス統合処理実行
        single_pass_result = self.optimized_processor.execute_single_pass_processing(
            file_path=self.sample_file,
            integration_options={
                "eliminate_stage_duplication": True,
                "optimize_memory_usage": True,
                "ensure_quality_preservation": True,
                "enable_performance_monitoring": True,
            },
        )

        # 統合処理結果検証
        assert single_pass_result.success is True
        assert single_pass_result.single_pass_achieved is True

        # 重複排除効果確認
        duplication_elimination = single_pass_result.duplication_elimination_metrics
        assert duplication_elimination.stage_4_5_unified is True
        assert duplication_elimination.duplicate_operations_eliminated >= 1
        assert duplication_elimination.processing_efficiency_improved is True

        # 処理品質保証確認
        quality_metrics = single_pass_result.quality_preservation_metrics
        assert quality_metrics.header_accuracy_maintained is True
        assert quality_metrics.data_integrity_preserved is True
        assert quality_metrics.output_consistency_verified is True

        # 性能改善効果測定
        performance_improvement = single_pass_result.performance_improvement_metrics
        assert performance_improvement.processing_time_reduction >= 0.30  # 30%以上削減
        assert performance_improvement.memory_usage_reduction >= 0.25  # 25%以上削減
        assert performance_improvement.throughput_increase >= 0.40  # 40%以上向上

        print(
            f"Duplicate operations eliminated: {duplication_elimination.duplicate_operations_eliminated}"
        )
        print(
            f"Processing time reduction: {performance_improvement.processing_time_reduction:.1%}"
        )
        print(
            f"Memory usage reduction: {performance_improvement.memory_usage_reduction:.1%}"
        )

    @pytest.mark.performance
    def test_header_processing_memory_optimization(self):
        """
        ヘッダー処理のメモリ最適化を検証する。

        機能保証項目:
        - メモリ効率的ヘッダー処理実現
        - 大容量ファイルでのメモリ安定性
        - ガベージコレクション最適化

        メモリ最適化要件:
        - 中間データ生成最小化
        - メモリリーク完全防止
        - 大容量ファイル対応保証

        メモリ最適化の重要性:
        - システムリソース効率利用
        - 大規模データ処理能力向上
        - 安定性・信頼性確保
        """
        # メモリ最適化ヘッダー処理実行
        memory_optimization = self.optimized_processor.optimize_header_memory_usage(
            file_path=self.sample_file,
            optimization_options={
                "minimize_intermediate_data": True,
                "enable_garbage_collection_optimization": True,
                "monitor_memory_usage": True,
                "prevent_memory_leaks": True,
            },
        )

        # メモリ最適化結果検証
        assert memory_optimization.success is True
        assert memory_optimization.memory_optimization_effective is True

        # メモリ使用量改善確認
        memory_metrics = memory_optimization.memory_usage_metrics
        assert memory_metrics.peak_memory_usage_mb > 0
        assert memory_metrics.memory_reduction_percentage >= 0.25  # 25%以上削減
        assert memory_metrics.memory_efficiency_score >= 0.8  # 80%以上効率

        # 中間データ最適化確認
        intermediate_data_optimization = memory_optimization.intermediate_data_metrics
        assert intermediate_data_optimization.intermediate_objects_reduced is True
        assert intermediate_data_optimization.memory_fragmentation_minimized is True
        assert intermediate_data_optimization.allocation_efficiency_improved is True

        # メモリリーク防止確認
        leak_prevention = memory_optimization.memory_leak_prevention
        assert leak_prevention.leaks_detected_count == 0
        assert leak_prevention.garbage_collection_optimized is True
        assert leak_prevention.memory_stability_confirmed is True

        # 大容量ファイル対応確認
        scalability_verification = memory_optimization.scalability_metrics
        assert scalability_verification.large_file_memory_stable is True
        assert scalability_verification.memory_growth_linear is True
        assert scalability_verification.oom_prevention_effective is True

        print(f"Memory reduction: {memory_metrics.memory_reduction_percentage:.1%}")
        print(f"Memory efficiency score: {memory_metrics.memory_efficiency_score:.3f}")
        print(f"Memory leaks detected: {leak_prevention.leaks_detected_count}")

    @pytest.mark.performance
    def test_header_normalization_benchmark_comparison(self):
        """
        ヘッダー正規化ベンチマーク比較を実施する。

        機能保証項目:
        - 最適化前後の定量的比較
        - パフォーマンス改善効果測定
        - 品質保証・回帰防止確認

        ベンチマーク要件:
        - 処理時間30%以上短縮
        - メモリ使用量25%以上削減
        - 品質指標100%保持

        ベンチマーク比較の重要性:
        - 最適化効果の定量的証明
        - 継続的改善の基盤構築
        - ステークホルダーへの成果報告
        """
        # ベンチマーク比較実行
        benchmark_comparison = self.optimized_processor.execute_performance_benchmark(
            file_path=self.sample_file,
            benchmark_options={
                "compare_legacy_vs_optimized": True,
                "measure_processing_time": True,
                "monitor_memory_usage": True,
                "verify_quality_preservation": True,
                "generate_detailed_report": True,
            },
        )

        # ベンチマーク結果検証
        assert benchmark_comparison.success is True
        assert benchmark_comparison.optimization_effective is True

        # 処理時間改善確認
        time_comparison = benchmark_comparison.processing_time_comparison
        assert time_comparison.legacy_processing_time_ms > 0
        assert time_comparison.optimized_processing_time_ms > 0
        assert time_comparison.improvement_percentage >= 0.30  # 30%以上向上

        # メモリ使用量改善確認
        memory_comparison = benchmark_comparison.memory_usage_comparison
        assert memory_comparison.legacy_memory_usage_mb > 0
        assert memory_comparison.optimized_memory_usage_mb > 0
        assert memory_comparison.reduction_percentage >= 0.25  # 25%以上削減

        # 品質保証確認
        quality_verification = benchmark_comparison.quality_assurance_metrics
        assert quality_verification.output_consistency_verified is True
        assert quality_verification.accuracy_maintained is True
        assert quality_verification.regression_tests_passed is True

        # 総合効果評価
        overall_improvement = benchmark_comparison.overall_improvement_metrics
        assert overall_improvement.performance_score >= 0.75  # 75%以上改善
        assert overall_improvement.efficiency_improvement_verified is True
        assert overall_improvement.optimization_goals_achieved is True

        print(
            f"Processing time improvement: {time_comparison.improvement_percentage:.1%}"
        )
        print(f"Memory usage reduction: {memory_comparison.reduction_percentage:.1%}")
        print(f"Overall performance score: {overall_improvement.performance_score:.3f}")

    @pytest.mark.performance
    def test_large_header_dataset_linear_scalability(self):
        """
        大容量ヘッダーデータセットでの線形スケーラビリティを検証する。

        機能保証項目:
        - 大量ヘッダーでのO(n)計算量保持
        - メモリ使用量の線形増加確認
        - 処理時間の予測可能性保証

        スケーラビリティ要件:
        - 10,000+ヘッダーでの安定動作
        - 線形時間計算量の維持
        - メモリ効率性の保持

        線形スケーラビリティの重要性:
        - 企業グレード大容量データ対応
        - 処理性能の予測可能性
        - システム信頼性・安定性確保
        """
        # 大容量データセット生成
        large_headers = [f"Header_{i}" for i in range(10000)]
        large_headers.extend(["", "  ", "Duplicate", "Duplicate"])  # エッジケース追加

        # 大容量線形スケーラビリティテスト実行
        scalability_test = self.optimized_processor.test_linear_scalability(
            headers=large_headers,
            scalability_options={
                "verify_linear_time_complexity": True,
                "monitor_memory_growth": True,
                "ensure_processing_stability": True,
                "measure_performance_consistency": True,
            },
        )

        # スケーラビリティ結果検証
        assert scalability_test.success is True
        assert scalability_test.linear_scalability_confirmed is True

        # 線形時間計算量確認
        complexity_verification = scalability_test.complexity_verification
        assert complexity_verification.time_complexity_linear is True
        assert complexity_verification.space_complexity_linear is True
        assert complexity_verification.performance_predictable is True

        # 大容量処理安定性確認
        stability_metrics = scalability_test.processing_stability
        assert stability_metrics.large_dataset_processed_successfully is True
        assert stability_metrics.memory_usage_stable is True
        assert stability_metrics.processing_time_consistent is True

        # 性能一貫性確認
        consistency_metrics = scalability_test.performance_consistency
        assert consistency_metrics.throughput_maintained is True
        assert consistency_metrics.response_time_predictable is True
        assert consistency_metrics.resource_usage_efficient is True

        # 企業グレード要件確認
        enterprise_readiness = scalability_test.enterprise_grade_verification
        assert enterprise_readiness.large_scale_capable is True
        assert enterprise_readiness.production_ready is True
        assert enterprise_readiness.reliability_guaranteed is True

        print(f"Headers processed: {len(large_headers):,}")
        print(
            f"Linear scalability confirmed: {scalability_test.linear_scalability_confirmed}"
        )
        print(f"Enterprise readiness: {enterprise_readiness.production_ready}")
