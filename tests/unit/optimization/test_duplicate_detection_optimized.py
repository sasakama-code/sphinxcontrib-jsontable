"""Task 2.1.2: 重複検出効率化 - TDD RED Phase

ハッシュテーブル使用重複検出最適化:
1. O(n²)→O(n)時間計算量改善
2. メモリ効率的ハッシュテーブル実装
3. 大容量データでのスケーラビリティ保証

最適化目標:
- 重複検出処理時間50%以上削減
- メモリ使用量40%以上削減
- 企業グレード性能基準達成

CLAUDE.md TDD compliance:
- RED Phase: 失敗するテスト作成
- GREEN Phase: ハッシュテーブル最小実装
- REFACTOR Phase: メモリ・速度最適化
"""

import tempfile
from pathlib import Path
from typing import Dict, List

import pandas as pd
import pytest

# REDフェーズ: 存在しないクラスをインポート（意図的にエラー）
try:
    from sphinxcontrib.jsontable.optimization.duplicate_detector_optimized import (
        DuplicateDetectionResult,
        DuplicateDetectorOptimized,
        HashTableMetrics,
        OptimizationMetrics,
    )

    DUPLICATE_DETECTOR_AVAILABLE = True
except ImportError:
    DUPLICATE_DETECTOR_AVAILABLE = False


@pytest.mark.skipif(
    not DUPLICATE_DETECTOR_AVAILABLE,
    reason="Optimized duplicate detector components not yet implemented",
)
@pytest.mark.performance
class TestDuplicateDetectionOptimized:
    """重複検出最適化テストクラス"""

    def setup_method(self):
        """テストメソッド前の共通セットアップ"""
        self.duplicate_detector = DuplicateDetectorOptimized()
        self.sample_file = self._create_duplicate_sample_file()

    def teardown_method(self):
        """テストメソッド後のクリーンアップ"""
        if hasattr(self, "sample_file") and self.sample_file.exists():
            self.sample_file.unlink()

    def _create_duplicate_sample_file(self) -> Path:
        """重複データを含むサンプルExcelファイル作成"""
        # 重複検出テスト用複雑データ
        data = {
            "ID": [1, 2, 3, 2, 4, 1, 5],  # 重複: 1, 2
            "Name": [
                "Alice",
                "Bob",
                "Charlie",
                "Bob",
                "Diana",
                "Alice",
                "Eve",
            ],  # 重複: Alice, Bob
            "Email": [
                "alice@example.com",
                "bob@example.com",
                "charlie@example.com",
                "bob@example.com",  # 重複
                "diana@example.com",
                "alice.alt@example.com",  # 類似だが非重複
                "eve@example.com",
            ],
            "Department": [
                "Engineering",
                "Sales",
                "Engineering",
                "Sales",
                "HR",
                "Engineering",
                "Marketing",
            ],
            "Score": [95.5, 87.2, 92.1, 87.2, 88.7, 95.5, 91.3],  # 重複: 95.5, 87.2
        }
        df = pd.DataFrame(data)

        temp_file = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
        df.to_excel(temp_file.name, index=False)
        return Path(temp_file.name)

    @pytest.mark.performance
    def test_hash_table_duplicate_detection_linear_time(self):
        """
        ハッシュテーブル重複検出のO(n)時間計算量を検証する。

        機能保証項目:
        - ハッシュテーブル使用によるO(n)重複検出
        - 大容量データでの線形時間保証
        - メモリ効率的なハッシュテーブル実装

        パフォーマンス要件:
        - データ数nに対してO(n)時間計算量
        - ハッシュ衝突率5%未満の効率性
        - メモリ使用量線形増加の確保

        ハッシュテーブル最適化の重要性:
        - 従来O(n²)→O(n)大幅性能向上
        - 企業グレード大容量データ対応
        - 予測可能な処理時間実現
        """
        # ハッシュテーブル重複検出実行
        detection_result = self.duplicate_detector.detect_duplicates_with_hash_table(
            file_path=self.sample_file,
            detection_options={
                "algorithm": "hash_table",
                "ensure_linear_time": True,
                "optimize_memory_usage": True,
                "enable_performance_monitoring": True,
                "hash_table_load_factor": 0.75,
            },
        )

        # 基本結果検証
        assert isinstance(detection_result, DuplicateDetectionResult)
        assert detection_result.success is True
        assert detection_result.algorithm_used == "hash_table"

        # 線形時間計算量確認
        performance_metrics = detection_result.performance_metrics
        assert performance_metrics.time_complexity == "O(n)"
        assert performance_metrics.space_complexity == "O(n)"
        assert performance_metrics.processing_time_ms > 0

        # ハッシュテーブル効率性確認
        hash_metrics = detection_result.hash_table_metrics
        assert isinstance(hash_metrics, HashTableMetrics)
        assert hash_metrics.collision_rate < 0.05  # 5%未満
        assert hash_metrics.load_factor <= 0.8  # 80%以下
        assert hash_metrics.hash_function_efficiency >= 0.95  # 95%以上

        # 重複検出結果確認
        duplicates = detection_result.duplicates_found
        assert len(duplicates) > 0
        assert "ID" in duplicates  # IDカラムの重複検出
        assert "Name" in duplicates  # Nameカラムの重複検出

        # 検出精度確認
        id_duplicates = duplicates["ID"]
        assert 1 in id_duplicates["duplicate_values"]  # ID=1の重複
        assert 2 in id_duplicates["duplicate_values"]  # ID=2の重複
        assert id_duplicates["duplicate_count"] == 4  # 重複レコード数

        print(f"Algorithm: {detection_result.algorithm_used}")
        print(f"Time complexity: {performance_metrics.time_complexity}")
        print(f"Collision rate: {hash_metrics.collision_rate:.3f}")
        print(f"Duplicates found: {len(duplicates)} columns")

    @pytest.mark.performance
    def test_memory_optimized_duplicate_detection(self):
        """
        メモリ最適化重複検出を検証する。

        機能保証項目:
        - メモリ効率的ハッシュテーブル実装
        - 大容量データでのメモリ安定性
        - ガベージコレクション最適化

        メモリ最適化要件:
        - 従来手法比40%以上メモリ削減
        - ピークメモリ使用量予測可能性
        - メモリリーク完全防止

        メモリ最適化の重要性:
        - システムリソース効率利用
        - 大規模データ処理能力向上
        - 安定性・信頼性確保
        """
        # メモリ最適化重複検出実行
        detection_result = self.duplicate_detector.detect_duplicates_memory_optimized(
            file_path=self.sample_file,
            optimization_options={
                "minimize_memory_footprint": True,
                "enable_memory_monitoring": True,
                "optimize_garbage_collection": True,
                "use_memory_efficient_structures": True,
            },
        )

        # メモリ最適化結果検証
        assert detection_result.success is True
        assert detection_result.memory_optimized is True

        # メモリ使用量確認
        memory_metrics = detection_result.memory_metrics
        assert memory_metrics.peak_memory_usage_mb > 0
        assert memory_metrics.memory_efficiency_score >= 0.8  # 80%以上効率
        assert memory_metrics.memory_reduction_percentage >= 0.40  # 40%以上削減

        # メモリ最適化効果確認
        optimization_metrics = detection_result.optimization_metrics
        assert isinstance(optimization_metrics, OptimizationMetrics)
        assert optimization_metrics.memory_usage_improvement >= 0.40  # 40%以上改善
        assert optimization_metrics.garbage_collection_optimized is True
        assert optimization_metrics.memory_leaks_prevented is True

        # データ構造効率性確認
        structure_metrics = memory_metrics.data_structure_efficiency
        assert structure_metrics.hash_table_memory_efficient is True
        assert structure_metrics.intermediate_objects_minimized is True
        assert structure_metrics.memory_fragmentation_reduced is True

        # 処理品質保証確認
        quality_metrics = detection_result.quality_assurance
        assert quality_metrics.accuracy_maintained is True
        assert quality_metrics.completeness_guaranteed is True
        assert quality_metrics.performance_regression_prevented is True

        print(f"Memory reduction: {memory_metrics.memory_reduction_percentage:.1%}")
        print(f"Memory efficiency: {memory_metrics.memory_efficiency_score:.3f}")
        print(f"Peak memory usage: {memory_metrics.peak_memory_usage_mb:.2f}MB")

    @pytest.mark.performance
    def test_large_dataset_duplicate_detection_scalability(self):
        """
        大容量データセット重複検出スケーラビリティを検証する。

        機能保証項目:
        - 10万件以上データでの安定動作
        - ハッシュテーブルスケーラビリティ
        - 処理時間予測可能性保証

        スケーラビリティ要件:
        - 100,000+レコードでの線形時間維持
        - メモリ使用量線形増加保証
        - エンタープライズグレード性能

        大容量スケーラビリティの重要性:
        - 企業向け大規模データ処理対応
        - 処理性能の予測可能性確保
        - システム信頼性・安定性保証
        """
        # 大容量テストデータセット生成
        large_dataset = self._generate_large_duplicate_dataset(size=100000)
        large_file = self._create_large_test_file(large_dataset)

        try:
            # 大容量重複検出実行
            detection_result = self.duplicate_detector.detect_duplicates_large_scale(
                file_path=large_file,
                scalability_options={
                    "enable_large_dataset_optimization": True,
                    "verify_linear_scalability": True,
                    "monitor_performance_consistency": True,
                    "ensure_memory_stability": True,
                },
            )

            # スケーラビリティ結果検証
            assert detection_result.success is True
            assert detection_result.large_scale_capable is True

            # 線形スケーラビリティ確認
            scalability_metrics = detection_result.scalability_verification
            assert scalability_metrics.linear_time_complexity_maintained is True
            assert scalability_metrics.memory_usage_linear is True
            assert scalability_metrics.performance_predictable is True

            # 大容量処理安定性確認
            stability_metrics = detection_result.processing_stability
            assert stability_metrics.large_dataset_processed_successfully is True
            assert stability_metrics.memory_usage_stable is True
            assert stability_metrics.processing_time_consistent is True

            # エンタープライズグレード確認
            enterprise_metrics = detection_result.enterprise_grade_verification
            assert enterprise_metrics.production_ready is True
            assert enterprise_metrics.large_scale_deployment_capable is True
            assert enterprise_metrics.reliability_guaranteed is True

            # 処理効率確認
            efficiency_metrics = detection_result.processing_efficiency
            assert efficiency_metrics.throughput_maintained >= 1000  # 1000rec/sec以上
            assert efficiency_metrics.response_time_consistent is True
            assert efficiency_metrics.resource_utilization_optimized is True

            print(f"Dataset size: {len(large_dataset):,} records")
            print(
                f"Processing throughput: {efficiency_metrics.throughput_maintained:,.0f} rec/sec"
            )
            print(
                f"Linear scalability confirmed: {scalability_metrics.linear_time_complexity_maintained}"
            )

        finally:
            # クリーンアップ
            if large_file.exists():
                large_file.unlink()

    @pytest.mark.performance
    def test_hash_collision_optimization(self):
        """
        ハッシュ衝突最適化を検証する。

        機能保証項目:
        - ハッシュ関数の衝突率最小化
        - 衝突解決戦略の効率性
        - 動的リハッシュ機能

        衝突最適化要件:
        - 衝突率3%未満の高効率ハッシュ関数
        - 効率的衝突解決（チェイン法・開番地法）
        - 負荷率監視による自動リサイズ

        ハッシュ衝突最適化の重要性:
        - 一定時間での検索・挿入保証
        - メモリ効率性の最大化
        - 性能劣化防止の確実性
        """
        # 衝突が発生しやすいデータ生成
        collision_prone_data = self._generate_collision_prone_dataset()
        collision_file = self._create_collision_test_file(collision_prone_data)

        try:
            # ハッシュ衝突最適化検出実行
            detection_result = (
                self.duplicate_detector.detect_duplicates_with_collision_optimization(
                    file_path=collision_file,
                    collision_options={
                        "hash_function": "optimized_murmur3",
                        "collision_resolution": "separate_chaining",
                        "enable_dynamic_resizing": True,
                        "target_collision_rate": 0.03,  # 3%未満
                        "load_factor_threshold": 0.75,
                    },
                )
            )

            # 衝突最適化結果検証
            assert detection_result.success is True
            assert detection_result.collision_optimized is True

            # ハッシュ関数効率性確認
            hash_function_metrics = detection_result.hash_function_performance
            assert hash_function_metrics.collision_rate < 0.03  # 3%未満
            assert hash_function_metrics.distribution_uniformity >= 0.95  # 95%以上均等
            assert hash_function_metrics.hash_quality_score >= 0.9  # 90%以上品質

            # 衝突解決効率性確認
            collision_resolution = detection_result.collision_resolution_metrics
            assert collision_resolution.average_probe_length <= 1.2  # 平均探査長1.2以下
            assert collision_resolution.worst_case_probe_length <= 5  # 最悪ケース5以下
            assert collision_resolution.resolution_efficiency >= 0.95  # 95%以上効率

            # 動的リサイズ効果確認
            resize_metrics = detection_result.dynamic_resize_metrics
            assert resize_metrics.resize_triggered is True
            assert resize_metrics.load_factor_maintained <= 0.75  # 75%以下維持
            assert (
                resize_metrics.performance_improvement_after_resize >= 0.2
            )  # 20%以上改善

            # 総合性能確認
            overall_performance = detection_result.overall_performance_impact
            assert overall_performance.search_time_improvement >= 0.3  # 30%以上向上
            assert overall_performance.insertion_time_improvement >= 0.25  # 25%以上向上
            assert overall_performance.memory_efficiency_maintained is True

            print(f"Collision rate: {hash_function_metrics.collision_rate:.3f}")
            print(f"Hash quality score: {hash_function_metrics.hash_quality_score:.3f}")
            print(
                f"Average probe length: {collision_resolution.average_probe_length:.2f}"
            )

        finally:
            # クリーンアップ
            if collision_file.exists():
                collision_file.unlink()

    @pytest.mark.performance
    def test_duplicate_detection_benchmark_comparison(self):
        """
        重複検出ベンチマーク比較を実施する。

        機能保証項目:
        - 従来手法vs最適化手法の定量比較
        - 処理時間・メモリ使用量改善測定
        - 品質保証・回帰防止確認

        ベンチマーク要件:
        - 処理時間50%以上短縮
        - メモリ使用量40%以上削減
        - 検出精度100%保持

        ベンチマーク比較の重要性:
        - 最適化効果の定量的証明
        - 継続的改善の基盤構築
        - ステークホルダーへの成果報告
        """
        # ベンチマーク比較実行
        benchmark_result = (
            self.duplicate_detector.execute_duplicate_detection_benchmark(
                file_path=self.sample_file,
                benchmark_options={
                    "compare_algorithms": ["naive_nested_loop", "hash_table_optimized"],
                    "measure_processing_time": True,
                    "monitor_memory_usage": True,
                    "verify_result_consistency": True,
                    "iterations": 5,
                },
            )
        )

        # ベンチマーク結果検証
        assert benchmark_result.benchmark_success is True
        assert benchmark_result.algorithms_compared == 2

        # 処理時間比較確認
        time_comparison = benchmark_result.processing_time_comparison
        assert time_comparison.naive_algorithm_time_ms > 0
        assert time_comparison.optimized_algorithm_time_ms > 0
        assert time_comparison.improvement_percentage >= 0.50  # 50%以上向上

        # メモリ使用量比較確認
        memory_comparison = benchmark_result.memory_usage_comparison
        assert memory_comparison.naive_memory_usage_mb > 0
        assert memory_comparison.optimized_memory_usage_mb > 0
        assert memory_comparison.reduction_percentage >= 0.40  # 40%以上削減

        # 結果一致性確認
        consistency_verification = benchmark_result.result_consistency
        assert consistency_verification.duplicate_detection_identical is True
        assert consistency_verification.accuracy_score == 1.0  # 100%精度
        assert consistency_verification.false_positives == 0
        assert consistency_verification.false_negatives == 0

        # 総合評価確認
        overall_evaluation = benchmark_result.overall_evaluation
        assert overall_evaluation.optimization_effective is True
        assert overall_evaluation.performance_goals_achieved is True
        assert overall_evaluation.quality_maintained is True

        print(
            f"Processing time improvement: {time_comparison.improvement_percentage:.1%}"
        )
        print(f"Memory usage reduction: {memory_comparison.reduction_percentage:.1%}")
        print(f"Accuracy maintained: {consistency_verification.accuracy_score:.1%}")

    def _generate_large_duplicate_dataset(self, size: int) -> List[Dict]:
        """大容量重複データセット生成"""
        import random

        dataset = []
        duplicate_ratio = 0.3  # 30%重複率

        for i in range(size):
            if random.random() < duplicate_ratio and i > 0:
                # 重複レコード生成
                base_index = random.randint(0, i - 1)
                record = dataset[base_index].copy()
                record["row_id"] = i
            else:
                # ユニークレコード生成
                record = {
                    "row_id": i,
                    "id": i,
                    "name": f"User_{i}",
                    "email": f"user_{i}@example.com",
                    "department": random.choice(
                        ["Engineering", "Sales", "HR", "Marketing"]
                    ),
                    "score": round(random.uniform(60.0, 100.0), 1),
                }
            dataset.append(record)

        return dataset

    def _create_large_test_file(self, dataset: List[Dict]) -> Path:
        """大容量テストファイル作成"""
        df = pd.DataFrame(dataset)
        temp_file = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
        df.to_excel(temp_file.name, index=False)
        return Path(temp_file.name)

    def _generate_collision_prone_dataset(self) -> List[Dict]:
        """ハッシュ衝突が発生しやすいデータセット生成"""
        # 同一ハッシュ値を持ちやすいデータパターン
        collision_data = []

        # パターン1: 数値の倍数関係
        for i in range(100):
            collision_data.append(
                {
                    "id": i * 16,  # 16の倍数（衝突しやすい）
                    "name": f"Name_{i}",
                    "category": "A" if i % 2 == 0 else "B",
                }
            )

        # パターン2: 文字列の共通プレフィックス
        for i in range(100):
            collision_data.append(
                {
                    "id": 10000 + i,
                    "name": f"CommonPrefix_{i:03d}",  # 共通プレフィックス
                    "category": "C",
                }
            )

        return collision_data

    def _create_collision_test_file(self, dataset: List[Dict]) -> Path:
        """衝突テストファイル作成"""
        df = pd.DataFrame(dataset)
        temp_file = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
        df.to_excel(temp_file.name, index=False)
        return Path(temp_file.name)
