"""Task 2.1.4: データ検証統合 - TDD RED Phase

複数検証パス→単一パス統合:
1. 複数の個別検証プロセスを統合
2. 単一パスでの包括的データ検証
3. 検証効率の大幅改善

最適化目標:
- 検証処理時間50%以上削減
- メモリ使用量30%以上削減
- 検証品質100%保持

CLAUDE.md TDD compliance:
- RED Phase: 失敗するテスト作成
- GREEN Phase: 統合検証システム実装
- REFACTOR Phase: 品質保証強化
"""

import tempfile
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import pytest

# REDフェーズ: 存在しないクラスをインポート（意図的にエラー）
try:
    from sphinxcontrib.jsontable.optimization.unified_data_validator import (
        DataValidationMetrics,
        SecurityValidationMetrics,
        UnifiedDataValidator,
        UnifiedValidationResult,
        ValidationEfficiencyMetrics,
        ValidationIntegrationMetrics,
        ValidationPerformanceMetrics,
        ValidationQualityMetrics,
    )

    UNIFIED_VALIDATOR_AVAILABLE = True
except ImportError:
    UNIFIED_VALIDATOR_AVAILABLE = False


@pytest.mark.skipif(
    not UNIFIED_VALIDATOR_AVAILABLE,
    reason="Unified data validator components not yet implemented",
)
@pytest.mark.performance
class TestUnifiedDataValidation:
    """統合データ検証テストクラス"""

    def setup_method(self):
        """テストメソッド前の共通セットアップ"""
        self.unified_validator = UnifiedDataValidator()
        self.sample_files = self._create_validation_test_files()

    def teardown_method(self):
        """テストメソッド後のクリーンアップ"""
        for file_path in self.sample_files.values():
            if file_path.exists():
                file_path.unlink()

    def _create_validation_test_files(self) -> Dict[str, Path]:
        """検証テスト用ファイル作成"""
        files = {}

        # 標準データファイル
        standard_data = {
            "name": ["Alice", "Bob", "Charlie", "Diana"],
            "age": [25, 30, 35, 28],
            "email": ["alice@test.com", "bob@test.com", "charlie@test.com", "diana@test.com"],
            "department": ["Sales", "Engineering", "Marketing", "HR"],
        }
        
        temp_file = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
        pd.DataFrame(standard_data).to_excel(temp_file.name, index=False)
        files["standard"] = Path(temp_file.name)

        # 問題のあるデータファイル
        problematic_data = {
            "name": ["Valid Name", "", None, "Another Name"],
            "age": [25, "invalid_age", -5, 150],  # 無効な年齢データ
            "email": ["valid@email.com", "invalid_email", "", "another@valid.com"],
            "score": [85.5, None, "not_number", 92.0],
        }
        
        temp_file = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
        pd.DataFrame(problematic_data).to_excel(temp_file.name, index=False)
        files["problematic"] = Path(temp_file.name)

        # セキュリティ問題のあるファイル（マクロ有効）
        security_data = {
            "data": ["normal_data", "SYSTEM('rm -rf /')", "safe_data", "another_normal"],
            "formula": ["SUM(A1:A10)", "CALL('dangerous.dll')", "AVERAGE(B1:B5)", "COUNT(C1:C10)"],
        }
        
        temp_file = tempfile.NamedTemporaryFile(suffix=".xlsm", delete=False)  # マクロ有効形式
        pd.DataFrame(security_data).to_excel(temp_file.name, index=False)
        files["security_risk"] = Path(temp_file.name)

        return files

    @pytest.mark.performance
    def test_unified_data_validation_single_pass_processing(self):
        """
        統合データ検証単一パス処理を検証する。

        機能保証項目:
        - 複数検証ステップの単一パス統合
        - データ検証・型検証・セキュリティ検証の同時実行
        - 処理効率の大幅改善

        パフォーマンス要件:
        - 従来多段階検証比50%以上処理時間削減
        - メモリ使用量30%以上削減
        - 検証品質100%保持

        統合検証の重要性:
        - 大量データ処理での効率性
        - リソース使用量最適化
        - システム応答性向上
        """
        # 統合検証実行
        validation_result = self.unified_validator.execute_unified_validation(
            file_path=self.sample_files["standard"],
            validation_options={
                "enable_single_pass_processing": True,
                "integrate_data_validation": True,
                "integrate_security_validation": True,
                "integrate_type_validation": True,
                "optimize_memory_usage": True,
                "enable_performance_monitoring": True,
            },
        )

        # 基本結果検証
        assert isinstance(validation_result, UnifiedValidationResult)
        assert validation_result.validation_success is True
        assert validation_result.single_pass_executed is True
        assert validation_result.all_validations_completed is True

        # 統合検証メトリクス確認
        integration_metrics = validation_result.integration_metrics
        assert isinstance(integration_metrics, ValidationIntegrationMetrics)
        assert integration_metrics.validation_passes_unified == 1  # 単一パス
        assert integration_metrics.original_validation_passes >= 3  # 元は3パス以上
        assert integration_metrics.integration_efficiency >= 0.75  # 75%以上効率

        # パフォーマンス改善確認
        performance_metrics = validation_result.performance_metrics
        assert isinstance(performance_metrics, ValidationPerformanceMetrics)
        assert performance_metrics.processing_time_reduction >= 0.50  # 50%以上削減
        assert performance_metrics.memory_usage_reduction >= 0.30  # 30%以上削減
        assert performance_metrics.cpu_efficiency_improvement >= 0.40  # 40%以上向上

        # 検証品質保証確認
        quality_metrics = validation_result.quality_metrics
        assert isinstance(quality_metrics, ValidationQualityMetrics)
        assert quality_metrics.validation_accuracy == 1.0  # 100%精度
        assert quality_metrics.false_positive_rate == 0.0  # 偽陽性なし
        assert quality_metrics.false_negative_rate == 0.0  # 偽陰性なし
        assert quality_metrics.coverage_completeness >= 0.95  # 95%以上カバレッジ

        # データ検証結果確認
        data_validation = validation_result.data_validation_results
        assert isinstance(data_validation, DataValidationMetrics)
        assert data_validation.valid_records_count == 4  # 4レコード全て有効
        assert data_validation.invalid_records_count == 0
        assert data_validation.data_types_verified is True
        assert data_validation.data_constraints_satisfied is True

        print(f"Processing time reduction: {performance_metrics.processing_time_reduction:.1%}")
        print(f"Memory usage reduction: {performance_metrics.memory_usage_reduction:.1%}")
        print(f"Integration efficiency: {integration_metrics.integration_efficiency:.1%}")

    @pytest.mark.performance
    def test_unified_validation_with_data_quality_issues(self):
        """
        データ品質問題のある場合の統合検証を検証する。

        機能保証項目:
        - 無効データの効率的検出
        - 品質問題の包括的レポート
        - 部分的成功の適切な処理

        品質保証要件:
        - 全ての品質問題を単一パスで検出
        - 詳細なエラー情報提供
        - グレースフルデグラデーション

        データ品質統合検証の重要性:
        - データ整合性の確保
        - 処理前の問題発見
        - 下流処理への影響防止
        """
        # 品質問題データでの統合検証実行
        validation_result = self.unified_validator.execute_unified_validation(
            file_path=self.sample_files["problematic"],
            validation_options={
                "enable_single_pass_processing": True,
                "strict_data_validation": True,
                "detailed_error_reporting": True,
                "graceful_degradation": True,
                "enable_quality_metrics": True,
            },
        )

        # 検証結果確認
        assert validation_result.validation_success is False  # 品質問題により失敗
        assert validation_result.partial_success is True  # 部分的成功
        assert validation_result.quality_issues_detected is True

        # データ検証詳細確認
        data_validation = validation_result.data_validation_results
        assert data_validation.valid_records_count == 1  # 1レコードのみ有効
        assert data_validation.invalid_records_count == 3  # 3レコード無効
        assert len(data_validation.data_quality_issues) >= 5  # 最低5つの品質問題

        # 品質問題詳細確認
        quality_issues = data_validation.data_quality_issues
        issue_types = [issue["type"] for issue in quality_issues]
        
        # 期待される問題タイプ（Excel読み込み後の実際の状態に基づく）
        assert "null_value" in issue_types  # null値（空文字列もNaNに変換される）
        assert "invalid_type" in issue_types  # 無効な型
        assert "value_out_of_range" in issue_types  # 範囲外値
        assert "invalid_format" in issue_types  # 無効フォーマット

        # エラー報告品質確認
        error_reporting = validation_result.error_reporting_quality
        assert error_reporting.error_messages_descriptive is True
        assert error_reporting.location_information_provided is True
        assert error_reporting.correction_suggestions_included is True

        # 効率性確認（問題があっても効率的）
        efficiency_metrics = validation_result.efficiency_metrics
        assert isinstance(efficiency_metrics, ValidationEfficiencyMetrics)
        assert efficiency_metrics.single_pass_problem_detection is True
        assert efficiency_metrics.error_detection_overhead_ms < 20  # 20ms未満
        assert efficiency_metrics.processing_continuation_possible is True

        print(f"Quality issues detected: {len(quality_issues)}")
        print(f"Valid records: {data_validation.valid_records_count}")
        print(f"Invalid records: {data_validation.invalid_records_count}")

    @pytest.mark.performance  
    def test_unified_security_validation_integration(self):
        """
        セキュリティ検証統合を検証する。

        機能保証項目:
        - セキュリティ脅威の統合検出
        - ファイル・内容・式の包括スキャン
        - セキュリティポリシーの一括適用

        セキュリティ要件:
        - 全セキュリティチェックの単一パス実行
        - 脅威検出精度100%保持
        - セキュリティオーバーヘッド最小化

        統合セキュリティ検証の重要性:
        - 包括的脅威防止
        - セキュリティ処理効率化
        - 企業セキュリティ基準達成
        """
        # セキュリティリスクファイルでの統合検証
        validation_result = self.unified_validator.execute_unified_validation(
            file_path=self.sample_files["security_risk"],
            validation_options={
                "enable_single_pass_processing": True,
                "integrate_security_validation": True,
                "security_policy_level": "strict",
                "scan_file_properties": True,
                "scan_cell_contents": True,
                "scan_formulas": True,
                "detect_macro_threats": True,
            },
        )

        # セキュリティ検証結果確認
        assert validation_result.security_validation_executed is True
        assert validation_result.security_threats_detected is True
        assert validation_result.security_policy_applied is True

        # セキュリティ検証詳細
        security_validation = validation_result.security_validation_results
        assert isinstance(security_validation, SecurityValidationMetrics)
        assert security_validation.threats_detected_count >= 2  # 最低2つの脅威
        assert security_validation.macro_enabled_file_detected is True
        assert security_validation.dangerous_formulas_detected is True

        # 脅威詳細確認
        security_threats = security_validation.detected_threats
        threat_types = [threat["type"] for threat in security_threats]
        
        assert "macro_file" in threat_types  # マクロファイル
        assert "dangerous_formula" in threat_types  # 危険な数式
        
        # 危険数式の具体的検出確認
        dangerous_formulas = [
            threat for threat in security_threats 
            if threat["type"] == "dangerous_formula"
        ]
        assert len(dangerous_formulas) >= 2  # SYSTEM, CALL関数検出

        # セキュリティ統合効率確認
        security_efficiency = security_validation.security_efficiency_metrics
        assert security_efficiency.single_pass_threat_detection is True
        assert security_efficiency.security_scan_time_ms < 100  # 100ms未満
        assert security_efficiency.threat_detection_accuracy >= 0.95  # 95%以上精度

        # セキュリティポリシー適用確認
        policy_application = security_validation.policy_application_results
        assert policy_application.strict_policy_applied is True
        assert policy_application.threats_blocked is True
        assert policy_application.security_recommendations_provided is True

        print(f"Security threats detected: {security_validation.threats_detected_count}")
        print(f"Security scan time: {security_efficiency.security_scan_time_ms:.1f}ms")
        print(f"Threat detection accuracy: {security_efficiency.threat_detection_accuracy:.1%}")

    @pytest.mark.performance
    def test_unified_validation_performance_benchmark(self):
        """
        統合検証パフォーマンスベンチマークを実施する。

        機能保証項目:
        - 従来分離検証vs統合検証の定量比較
        - 処理時間・メモリ・CPU使用率の測定
        - スケーラビリティ確認

        ベンチマーク要件:
        - 処理時間50%以上短縮
        - メモリ使用量30%以上削減
        - CPU効率40%以上向上

        統合検証ベンチマークの重要性:
        - 最適化効果の定量証明
        - 性能回帰の防止
        - 継続改善の基盤構築
        """
        # ベンチマーク実行
        benchmark_result = self.unified_validator.execute_validation_benchmark(
            test_files=[
                self.sample_files["standard"],
                self.sample_files["problematic"],
                self.sample_files["security_risk"],
            ],
            benchmark_options={
                "compare_approaches": ["separated_validation", "unified_validation"],
                "measure_processing_time": True,
                "monitor_memory_usage": True,
                "track_cpu_utilization": True,
                "iterations": 5,
                "enable_detailed_metrics": True,
            },
        )

        # ベンチマーク結果検証
        assert benchmark_result.benchmark_success is True
        assert benchmark_result.approaches_compared == 2
        assert benchmark_result.test_files_processed == 3

        # 処理時間比較確認
        time_comparison = benchmark_result.processing_time_comparison
        assert time_comparison.separated_validation_time_ms > 0
        assert time_comparison.unified_validation_time_ms > 0
        assert time_comparison.improvement_percentage >= 0.50  # 50%以上向上

        # メモリ使用量比較確認
        memory_comparison = benchmark_result.memory_usage_comparison
        assert memory_comparison.separated_validation_memory_mb > 0
        assert memory_comparison.unified_validation_memory_mb > 0
        assert memory_comparison.reduction_percentage >= 0.30  # 30%以上削減

        # CPU効率比較確認
        cpu_comparison = benchmark_result.cpu_efficiency_comparison
        assert cpu_comparison.separated_validation_cpu_usage > 0
        assert cpu_comparison.unified_validation_cpu_usage > 0
        assert cpu_comparison.efficiency_improvement >= 0.40  # 40%以上向上

        # 品質一致性確認
        quality_consistency = benchmark_result.validation_quality_consistency
        assert quality_consistency.results_identical is True
        assert quality_consistency.accuracy_maintained == 1.0  # 100%精度保持
        assert quality_consistency.no_regressions_detected is True

        # スケーラビリティ確認
        scalability_metrics = benchmark_result.scalability_metrics
        assert scalability_metrics.linear_performance_scaling is True
        assert scalability_metrics.memory_usage_predictable is True
        assert scalability_metrics.large_file_support_verified is True

        print(f"Processing time improvement: {time_comparison.improvement_percentage:.1%}")
        print(f"Memory usage reduction: {memory_comparison.reduction_percentage:.1%}")
        print(f"CPU efficiency improvement: {cpu_comparison.efficiency_improvement:.1%}")

    @pytest.mark.performance
    def test_unified_validation_concurrent_processing(self):
        """
        統合検証並行処理を検証する。

        機能保証項目:
        - 複数ファイルの並行統合検証
        - スレッドセーフな検証処理
        - 並行処理での性能向上

        並行処理要件:
        - スレッドプール活用による高速化
        - リソース競合の最小化
        - 結果一致性の保証

        統合検証並行処理の重要性:
        - 大量ファイル処理の効率化
        - システムリソース最大活用
        - エンタープライズ性能基準達成
        """
        # 並行処理実行
        concurrent_result = self.unified_validator.execute_concurrent_unified_validation(
            file_paths=list(self.sample_files.values()),
            concurrent_options={
                "enable_parallel_processing": True,
                "max_worker_threads": 4,
                "enable_resource_monitoring": True,
                "ensure_thread_safety": True,
                "optimize_memory_sharing": True,
            },
        )

        # 並行処理結果検証
        assert concurrent_result.concurrent_processing_success is True
        assert concurrent_result.all_files_processed is True
        assert concurrent_result.thread_safety_maintained is True

        # 並行処理効率確認
        concurrency_metrics = concurrent_result.concurrency_metrics
        assert concurrency_metrics.parallel_speedup_factor >= 2.0  # 2倍以上高速化
        assert concurrency_metrics.thread_utilization_efficiency >= 0.75  # 75%以上効率
        assert concurrency_metrics.resource_contention_minimal is True

        # 各ファイルの検証結果確認
        validation_results = concurrent_result.individual_validation_results
        assert len(validation_results) == 3  # 3ファイル全て処理

        # 標準ファイル結果
        standard_result = validation_results[str(self.sample_files["standard"])]
        assert standard_result.validation_success is True

        # 問題ファイル結果
        problematic_result = validation_results[str(self.sample_files["problematic"])]
        assert problematic_result.validation_success is False
        assert problematic_result.partial_success is True

        # セキュリティリスクファイル結果
        security_result = validation_results[str(self.sample_files["security_risk"])]
        assert security_result.security_threats_detected is True

        # リソース効率性確認
        resource_efficiency = concurrent_result.resource_efficiency_metrics
        assert resource_efficiency.memory_usage_optimized is True
        assert resource_efficiency.cpu_utilization_balanced is True
        assert resource_efficiency.io_efficiency_maintained is True

        # 結果一致性確認
        result_consistency = concurrent_result.result_consistency_verification
        assert result_consistency.sequential_parallel_results_match is True
        assert result_consistency.validation_quality_preserved is True
        assert result_consistency.no_race_conditions_detected is True

        print(f"Parallel speedup: {concurrency_metrics.parallel_speedup_factor:.1f}x")
        print(f"Thread utilization: {concurrency_metrics.thread_utilization_efficiency:.1%}")
        print(f"Files processed: {len(validation_results)}")