"""統合エラーハンドリングテスト

TDD REDフェーズ: 失敗するテストを先に作成
Task 1.3.4: エラーハンドリング重複排除

パイプライン間で重複するエラーハンドリング処理の統合:
- ExcelProcessingPipeline: 8箇所の重複エラー処理
- UnifiedProcessingPipeline: 統合エラーハンドリング機能
- OptimizedHeaderProcessor: 基本的なエラー処理
- CacheIntegratedPipeline: 軽微なエラー処理

統合効果:
- エラーハンドリング重複処理70%削減
- エラー処理コード量40%削減
- エラー回復成功率25%向上
- 統合ログ・監視100%統一
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock

import pandas as pd
import pytest

# REDフェーズ: 存在しないクラスをインポート（意図的にエラー）
try:
    from sphinxcontrib.jsontable.integration.unified_error_handler import (
        ErrorCategory,
        ErrorSeverity,
        OperationContext,
        PipelineContext,
        PipelineErrorClassification,
        PipelineStage,
        RecoveryResult,
        RetryContext,
        UnifiedErrorMonitor,
        UnifiedHandlingResult,
        UnifiedPipelineErrorHandler,
        UnifiedRecoveryStrategies,
    )

    UNIFIED_ERROR_HANDLER_AVAILABLE = True
except ImportError:
    UNIFIED_ERROR_HANDLER_AVAILABLE = False

from sphinxcontrib.jsontable.core.data_converter import IDataConverter
from sphinxcontrib.jsontable.core.excel_reader import IExcelReader
from sphinxcontrib.jsontable.core.range_parser import IRangeParser
from sphinxcontrib.jsontable.errors.error_handlers import IErrorHandler
from sphinxcontrib.jsontable.security.security_scanner import ISecurityValidator


class TestUnifiedErrorHandling:
    """統合エラーハンドリングテスト

    TDD REDフェーズ: 統合エラーハンドラーが存在しないため、
    これらのテストは意図的に失敗する。
    """

    def setup_method(self):
        """各テストメソッドの前に実行される設定."""
        self.temp_dir = Path(tempfile.mkdtemp())

        # モックコンポーネント作成
        self.mock_excel_reader = Mock(spec=IExcelReader)
        self.mock_data_converter = Mock(spec=IDataConverter)
        self.mock_range_parser = Mock(spec=IRangeParser)
        self.mock_security_validator = Mock(spec=ISecurityValidator)
        self.mock_error_handler = Mock(spec=IErrorHandler)

    def teardown_method(self):
        """各テストメソッドの後に実行されるクリーンアップ."""
        import shutil

        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_excel_file(
        self, filename: str = "test_error_handling.xlsx"
    ) -> Path:
        """テスト用Excelファイル作成

        Args:
            filename: ファイル名

        Returns:
            Path: 作成されたファイルのパス
        """
        file_path = self.temp_dir / filename

        # エラーハンドリングテスト用データ作成
        data = {
            "ErrorTest ID": ["ERR001", "ERR002", "ERR003"],
            "Error Type": ["FileError", "RangeError", "DataError"],
            "Severity": ["High", "Medium", "Low"],
            "Recovery": ["Retry", "Fallback", "Skip"],
        }

        df = pd.DataFrame(data)
        df.to_excel(file_path, index=False)

        return file_path

    @pytest.mark.integration
    def test_error_deduplication_across_pipelines(self):
        """パイプライン間エラー重複排除テスト

        RED: UnifiedPipelineErrorHandlerクラスが存在しないため失敗する
        期待動作:
        - 同一エラーの重複ハンドリング検出・排除
        - パイプライン間でのエラー情報共有
        - 重複処理削減効果測定
        - エラーキャッシュ効率確認
        """
        # テストファイル作成
        test_file = self.create_test_excel_file("deduplication_test.xlsx")

        # 統合エラーハンドラー初期化
        unified_handler = UnifiedPipelineErrorHandler(
            core_handler=self.mock_error_handler,
            enable_cross_pipeline_recovery=True,
            enable_error_deduplication=True,
            enable_unified_logging=True,
        )

        # 同一エラーを複数パイプラインでシミュレート
        test_error = FileNotFoundError("Test file not found")
        pipeline_contexts = [
            PipelineContext(
                pipeline_name="ExcelProcessingPipeline",
                stage=PipelineStage.FILE_READING,
                operation="load_excel_file",
            ),
            PipelineContext(
                pipeline_name="UnifiedProcessingPipeline",
                stage=PipelineStage.DATA_ACQUISITION,
                operation="execute_stage_one_data_acquisition",
            ),
            PipelineContext(
                pipeline_name="OptimizedHeaderProcessor",
                stage=PipelineStage.HEADER_PROCESSING,
                operation="execute_single_pass_header_processing",
            ),
        ]

        operation_context = OperationContext(
            file_path=test_file,
            processing_options={"header_row": 0},
            user_context={"request_id": "test_001"},
        )

        # 各パイプラインでエラーハンドリング実行
        handling_results = []
        for context in pipeline_contexts:
            result = unified_handler.handle_pipeline_error(
                error=test_error,
                pipeline_context=context,
                operation_context=operation_context,
            )
            handling_results.append(result)

        # 重複排除結果検証
        for result in handling_results:
            assert isinstance(result, UnifiedHandlingResult)
            assert result.success is True  # 統合処理成功
            assert result.error_handled is True
            assert result.recovery_attempted is True

        # 重複排除効果確認
        deduplication_stats = unified_handler.get_deduplication_statistics()
        assert deduplication_stats["total_errors_processed"] == 3
        assert deduplication_stats["duplicate_errors_detected"] >= 2  # 重複検出
        assert deduplication_stats["deduplication_efficiency"] >= 0.70  # 70%効率
        assert deduplication_stats["processing_time_saved"] > 0

        # エラーキャッシュ効率確認
        cache_stats = unified_handler.get_error_cache_statistics()
        assert cache_stats["cache_hit_ratio"] >= 0.66  # 2/3がキャッシュヒット
        assert cache_stats["cache_entries"] == 1  # 1つのユニークエラー

        print(
            f"Deduplication efficiency: {deduplication_stats['deduplication_efficiency']:.1%}"
        )
        print(f"Cache hit ratio: {cache_stats['cache_hit_ratio']:.1%}")

    @pytest.mark.integration
    def test_cross_pipeline_error_recovery(self):
        """段階横断エラー回復テスト

        RED: 段階横断エラー回復機能が存在しないため失敗する
        期待動作:
        - パイプライン横断でのエラー回復戦略適用
        - フォールバック処理の自動選択
        - 回復成功率向上効果測定
        - 段階的な回復試行
        """
        # テストファイル作成
        test_file = self.create_test_excel_file("recovery_test.xlsx")

        # 統合エラーハンドラー初期化
        unified_handler = UnifiedPipelineErrorHandler(
            core_handler=self.mock_error_handler,
            enable_cross_pipeline_recovery=True,
            enable_intelligent_fallback=True,
            enable_recovery_optimization=True,
        )

        # 複数のエラーシナリオでテスト
        error_scenarios = [
            {
                "error": ValueError("Invalid range specification"),
                "category": ErrorCategory.RANGE_VALIDATION,
                "severity": ErrorSeverity.MEDIUM,
                "pipeline_stage": PipelineStage.DATA_ACQUISITION,
            },
            {
                "error": PermissionError("File access denied"),
                "category": ErrorCategory.FILE_ACCESS,
                "severity": ErrorSeverity.HIGH,
                "pipeline_stage": PipelineStage.FILE_READING,
            },
            {
                "error": KeyError("Header column not found"),
                "category": ErrorCategory.HEADER_PROCESSING,
                "severity": ErrorSeverity.MEDIUM,
                "pipeline_stage": PipelineStage.HEADER_PROCESSING,
            },
        ]

        recovery_results = []
        for scenario in error_scenarios:
            # エラー分類作成
            classification = PipelineErrorClassification(
                error_category=scenario["category"],
                severity_level=scenario["severity"],
                pipeline_stage=scenario["pipeline_stage"],
                recovery_priority=2,  # 高優先度
                cross_pipeline_impact=True,
            )

            # パイプラインコンテキスト
            pipeline_context = PipelineContext(
                pipeline_name="TestPipeline",
                stage=scenario["pipeline_stage"],
                operation="test_operation",
                error_classification=classification,
            )

            operation_context = OperationContext(
                file_path=test_file,
                processing_options={"enable_recovery": True},
                user_context={"request_id": "recovery_test"},
            )

            # 段階横断エラー回復実行
            result = unified_handler.handle_pipeline_error(
                error=scenario["error"],
                pipeline_context=pipeline_context,
                operation_context=operation_context,
            )

            recovery_results.append(result)

        # 回復結果検証
        for result in recovery_results:
            assert isinstance(result, UnifiedHandlingResult)
            assert result.recovery_attempted is True
            assert len(result.recovery_strategies_applied) > 0
            assert result.cross_pipeline_recovery_used is True

        # 回復統計確認
        recovery_stats = unified_handler.get_recovery_statistics()
        assert recovery_stats["total_recovery_attempts"] == len(error_scenarios)
        assert recovery_stats["recovery_success_rate"] >= 0.75  # 75%以上成功率
        assert recovery_stats["cross_pipeline_recoveries"] >= 2
        assert recovery_stats["fallback_strategies_used"] >= 1

        # 段階横断効果確認
        cross_pipeline_stats = unified_handler.get_cross_pipeline_statistics()
        assert cross_pipeline_stats["pipeline_collaboration_count"] >= 2
        assert cross_pipeline_stats["shared_recovery_resources"] >= 1
        assert cross_pipeline_stats["collaborative_recovery_success_rate"] >= 0.70

        print(f"Recovery success rate: {recovery_stats['recovery_success_rate']:.1%}")
        print(
            f"Cross-pipeline recoveries: {cross_pipeline_stats['pipeline_collaboration_count']}"
        )

    @pytest.mark.integration
    def test_unified_error_classification(self):
        """統合エラー分類テスト

        RED: エラー分類システムが存在しないため失敗する
        期待動作:
        - 自動エラー分類・優先度付け
        - カテゴリ別エラー統計
        - 重要度に基づく処理優先順位
        - 分類精度測定
        """
        # 多様なエラータイプのテストケース
        test_errors = [
            (
                FileNotFoundError("File not found"),
                ErrorCategory.FILE_ACCESS,
                ErrorSeverity.HIGH,
            ),
            (
                ValueError("Invalid range: A1:Z999"),
                ErrorCategory.RANGE_VALIDATION,
                ErrorSeverity.MEDIUM,
            ),
            (
                KeyError("Column 'Name' not found"),
                ErrorCategory.HEADER_PROCESSING,
                ErrorSeverity.MEDIUM,
            ),
            (
                PermissionError("Access denied"),
                ErrorCategory.SECURITY_VALIDATION,
                ErrorSeverity.CRITICAL,
            ),
            (
                TypeError("Cannot convert data type"),
                ErrorCategory.DATA_CONVERSION,
                ErrorSeverity.HIGH,
            ),
            (
                ConnectionError("Cache server unreachable"),
                ErrorCategory.PIPELINE_INTEGRATION,
                ErrorSeverity.LOW,
            ),
        ]

        # 統合エラーハンドラー初期化
        unified_handler = UnifiedPipelineErrorHandler(
            core_handler=self.mock_error_handler,
            enable_automatic_classification=True,
            enable_priority_processing=True,
            enable_classification_learning=True,
        )

        # エラー分類実行
        classification_results = []
        for error, expected_category, expected_severity in test_errors:
            classification = unified_handler.classify_error(
                error=error,
                pipeline_context=PipelineContext(
                    pipeline_name="TestPipeline",
                    stage=PipelineStage.DATA_ACQUISITION,
                    operation="test_operation",
                ),
            )

            classification_results.append(
                (classification, expected_category, expected_severity)
            )

        # 分類精度検証
        correct_categories = 0
        correct_severities = 0

        for (
            classification,
            expected_category,
            expected_severity,
        ) in classification_results:
            assert isinstance(classification, PipelineErrorClassification)

            # カテゴリ分類精度
            if classification.error_category == expected_category:
                correct_categories += 1

            # 重要度分類精度
            if classification.severity_level == expected_severity:
                correct_severities += 1

            # 基本分類項目確認
            assert isinstance(classification.error_category, ErrorCategory)
            assert isinstance(classification.severity_level, ErrorSeverity)
            assert isinstance(classification.pipeline_stage, PipelineStage)
            assert 1 <= classification.recovery_priority <= 5
            assert isinstance(classification.cross_pipeline_impact, bool)

        # 分類精度計算
        category_accuracy = correct_categories / len(test_errors)
        severity_accuracy = correct_severities / len(test_errors)

        assert category_accuracy >= 0.90  # 90%以上のカテゴリ分類精度
        assert severity_accuracy >= 0.85  # 85%以上の重要度分類精度

        # 分類統計確認
        classification_stats = unified_handler.get_classification_statistics()
        assert classification_stats["total_classifications"] == len(test_errors)
        assert (
            classification_stats["category_distribution"][ErrorCategory.FILE_ACCESS]
            >= 1
        )
        assert classification_stats["severity_distribution"][ErrorSeverity.HIGH] >= 2
        assert classification_stats["classification_accuracy"] >= 0.85

        print(f"Category accuracy: {category_accuracy:.1%}")
        print(f"Severity accuracy: {severity_accuracy:.1%}")

    @pytest.mark.integration
    def test_integrated_error_monitoring(self):
        """統合エラー監視テスト

        RED: 統合エラー監視機能が存在しないため失敗する
        期待動作:
        - リアルタイムエラー監視・統計
        - エラートレンド分析
        - アラート・通知機能
        - 分析レポート生成
        """
        # 統合エラー監視システム初期化
        error_monitor = UnifiedErrorMonitor(
            enable_realtime_monitoring=True,
            enable_trend_analysis=True,
            enable_alert_system=True,
            monitoring_interval=0.1,  # 100ms間隔
        )

        # 統合エラーハンドラーと連携
        unified_handler = UnifiedPipelineErrorHandler(
            core_handler=self.mock_error_handler,
            error_monitor=error_monitor,
            enable_monitoring_integration=True,
        )

        # 複数エラーイベントをシミュレート
        error_events = [
            FileNotFoundError("File A not found"),
            ValueError("Invalid range B"),
            KeyError("Column C missing"),
            PermissionError("Access denied D"),
            FileNotFoundError("File E not found"),  # 重複カテゴリ
            ValueError("Invalid range F"),  # 重複カテゴリ
        ]

        # エラーイベント記録
        for i, error in enumerate(error_events):
            classification = PipelineErrorClassification(
                error_category=ErrorCategory.FILE_ACCESS
                if isinstance(error, (FileNotFoundError, PermissionError))
                else ErrorCategory.RANGE_VALIDATION,
                severity_level=ErrorSeverity.HIGH
                if isinstance(error, (FileNotFoundError, PermissionError))
                else ErrorSeverity.MEDIUM,
                pipeline_stage=PipelineStage.DATA_ACQUISITION,
                recovery_priority=1,
                cross_pipeline_impact=True,
            )

            pipeline_context = PipelineContext(
                pipeline_name=f"Pipeline_{i % 3}",  # 3つのパイプラインで分散
                stage=classification.pipeline_stage,
                operation=f"operation_{i}",
            )

            # エラーハンドリング実行（監視記録含む）
            result = unified_handler.handle_pipeline_error(
                error=error,
                pipeline_context=pipeline_context,
                operation_context=OperationContext(
                    file_path=Path("test_file.xlsx"),
                    processing_options={},
                    user_context={"event_id": f"event_{i}"},
                ),
            )

            assert result.monitoring_recorded is True

        # 監視統計確認
        monitoring_stats = error_monitor.get_monitoring_statistics()
        assert monitoring_stats["total_errors"] == len(error_events)
        assert monitoring_stats["errors_by_category"][ErrorCategory.FILE_ACCESS] >= 3
        assert (
            monitoring_stats["errors_by_category"][ErrorCategory.RANGE_VALIDATION] >= 2
        )
        assert monitoring_stats["errors_by_pipeline"]["Pipeline_0"] >= 2
        assert monitoring_stats["errors_by_pipeline"]["Pipeline_1"] >= 2
        assert monitoring_stats["errors_by_pipeline"]["Pipeline_2"] >= 2

        # エラートレンド分析確認
        trend_analysis = error_monitor.get_trend_analysis()
        assert trend_analysis["error_frequency_trend"] is not None
        assert trend_analysis["category_trend_analysis"] is not None
        assert trend_analysis["pipeline_error_distribution"] is not None
        assert trend_analysis["severity_escalation_detected"] is False  # テストでは正常

        # アラート機能確認
        alerts = error_monitor.get_current_alerts()
        assert isinstance(alerts, list)
        # 高頻度エラーでアラート発生の可能性
        if len(alerts) > 0:
            for alert in alerts:
                assert "alert_type" in alert
                assert "severity" in alert
                assert "message" in alert
                assert "timestamp" in alert

        # 分析レポート生成確認
        analytics_report = error_monitor.generate_error_analytics()
        assert analytics_report["monitoring_period"] > 0
        assert analytics_report["total_events_monitored"] == len(error_events)
        assert analytics_report["error_diversity_score"] >= 0.5  # 複数エラータイプ
        assert analytics_report["pipeline_health_score"] >= 0.7  # 健全性スコア
        assert analytics_report["recovery_effectiveness"] >= 0.0

        print(f"Monitoring coverage: {monitoring_stats['total_errors']} events")
        print(f"Pipeline health score: {analytics_report['pipeline_health_score']:.1%}")

    @pytest.mark.integration
    def test_performance_impact_minimal(self):
        """パフォーマンス影響最小化テスト

        RED: パフォーマンス最適化機能が存在しないため失敗する
        期待動作:
        - 統合エラーハンドリングのオーバーヘッド最小化
        - 通常処理への影響5%以下
        - エラーハンドリング処理時間最適化
        - メモリ使用量効率化
        """
        import time

        # 統合エラーハンドラー初期化（最適化有効）
        unified_handler = UnifiedPipelineErrorHandler(
            core_handler=self.mock_error_handler,
            enable_performance_optimization=True,
            enable_lightweight_monitoring=True,
            enable_async_processing=True,
            cache_optimization_level="high",
        )

        # ベースライン測定（エラーハンドリングなし）
        baseline_iterations = 1000
        start_time = time.perf_counter()

        for i in range(baseline_iterations):
            # 通常処理シミュレート
            data = {"test": f"value_{i}"}
            result = data.copy()
            result["processed"] = True

        baseline_time = time.perf_counter() - start_time

        # 統合エラーハンドリング付き測定
        test_file = self.create_test_excel_file("performance_test.xlsx")

        start_time = time.perf_counter()

        for i in range(baseline_iterations):
            # 通常処理 + エラーハンドリング
            try:
                data = {"test": f"value_{i}"}
                result = data.copy()
                result["processed"] = True

                # エラーハンドリング統合チェック（軽量）
                if i % 100 == 0:  # 1%の頻度でエラーハンドリング
                    context = PipelineContext(
                        pipeline_name="PerformanceTest",
                        stage=PipelineStage.DATA_ACQUISITION,
                        operation="test_operation",
                    )

                    # 軽量エラーチェック
                    is_error_prone = unified_handler.check_error_proneness(
                        operation_context=OperationContext(
                            file_path=test_file,
                            processing_options={"test": True},
                            user_context={"iteration": i},
                        ),
                        pipeline_context=context,
                    )

                    assert isinstance(is_error_prone, bool)

            except Exception:
                pass  # パフォーマンステストでは例外無視

        enhanced_time = time.perf_counter() - start_time

        # パフォーマンス影響測定
        performance_overhead = (enhanced_time - baseline_time) / baseline_time

        assert performance_overhead <= 0.05  # 5%以下のオーバーヘッド

        # エラーハンドリング効率確認
        efficiency_stats = unified_handler.get_performance_statistics()
        assert efficiency_stats["average_handling_time_ms"] <= 1.0  # 1ms以下
        assert efficiency_stats["memory_overhead_ratio"] <= 0.02  # 2%以下
        assert efficiency_stats["cache_hit_ratio"] >= 0.85  # 85%以上
        assert efficiency_stats["async_processing_efficiency"] >= 0.90  # 90%以上

        # 最適化効果確認
        optimization_stats = unified_handler.get_optimization_statistics()
        assert optimization_stats["deduplication_time_saved"] > 0
        assert optimization_stats["cache_memory_saved"] > 0
        assert optimization_stats["async_processing_speedup"] >= 1.1  # 10%以上高速化

        print(f"Performance overhead: {performance_overhead:.1%}")
        print(
            f"Average handling time: {efficiency_stats['average_handling_time_ms']:.2f}ms"
        )
        print(f"Memory overhead: {efficiency_stats['memory_overhead_ratio']:.1%}")

    @pytest.mark.integration
    def test_unified_recovery_strategies(self):
        """統合リカバリ戦略テスト

        RED: 統合リカバリ戦略が存在しないため失敗する
        期待動作:
        - 複数リカバリ戦略の統合適用
        - インテリジェント戦略選択
        - パイプライン横断フォールバック
        - リカバリ成功率最大化
        """
        # 統合リカバリ戦略システム初期化
        recovery_strategies = UnifiedRecoveryStrategies(
            enable_graceful_degradation=True,
            enable_intelligent_retry=True,
            enable_cross_pipeline_fallback=True,
            enable_adaptive_strategy_selection=True,
        )

        # 統合エラーハンドラーに統合
        unified_handler = UnifiedPipelineErrorHandler(
            core_handler=self.mock_error_handler,
            recovery_strategies=recovery_strategies,
            enable_strategy_optimization=True,
        )

        # 複数リカバリシナリオテスト
        recovery_scenarios = [
            {
                "error": FileNotFoundError("Primary file missing"),
                "strategy_preference": "cross_pipeline_fallback",
                "expected_recovery": True,
            },
            {
                "error": ValueError("Corrupted data detected"),
                "strategy_preference": "graceful_degradation",
                "expected_recovery": True,
            },
            {
                "error": TimeoutError("Network timeout"),
                "strategy_preference": "intelligent_retry",
                "expected_recovery": True,
            },
            {
                "error": MemoryError("Insufficient memory"),
                "strategy_preference": "adaptive_strategy_selection",
                "expected_recovery": True,
            },
        ]

        recovery_results = []

        for scenario in recovery_scenarios:
            # リカバリコンテキスト作成
            RetryContext(
                max_attempts=3, backoff_strategy="exponential", timeout_seconds=30
            )

            pipeline_context = PipelineContext(
                pipeline_name="RecoveryTestPipeline",
                stage=PipelineStage.DATA_ACQUISITION,
                operation="test_recovery_operation",
            )

            operation_context = OperationContext(
                file_path=Path("test_recovery.xlsx"),
                processing_options={"recovery_enabled": True},
                user_context={"scenario": scenario["strategy_preference"]},
            )

            # 統合リカバリ実行
            result = unified_handler.handle_pipeline_error(
                error=scenario["error"],
                pipeline_context=pipeline_context,
                operation_context=operation_context,
            )

            recovery_results.append(result)

        # リカバリ結果検証
        successful_recoveries = 0
        for result in recovery_results:
            assert isinstance(result, UnifiedHandlingResult)
            assert result.recovery_attempted is True
            assert len(result.recovery_strategies_applied) > 0

            if result.recovery_successful:
                successful_recoveries += 1

        # リカバリ成功率確認
        recovery_success_rate = successful_recoveries / len(recovery_scenarios)
        assert recovery_success_rate >= 0.75  # 75%以上成功率

        # 戦略効果測定
        strategy_stats = recovery_strategies.get_strategy_statistics()
        assert strategy_stats["graceful_degradation_success_rate"] >= 0.80
        assert strategy_stats["intelligent_retry_success_rate"] >= 0.70
        assert strategy_stats["cross_pipeline_fallback_success_rate"] >= 0.85
        assert strategy_stats["adaptive_selection_accuracy"] >= 0.80

        # パイプライン横断効果確認
        cross_pipeline_results = recovery_strategies.get_cross_pipeline_statistics()
        assert cross_pipeline_results["successful_fallbacks"] >= 1
        assert cross_pipeline_results["pipeline_collaboration_events"] >= 2
        assert cross_pipeline_results["shared_resource_utilization"] >= 0.60

        print(f"Recovery success rate: {recovery_success_rate:.1%}")
        print(
            f"Cross-pipeline fallbacks: {cross_pipeline_results['successful_fallbacks']}"
        )
