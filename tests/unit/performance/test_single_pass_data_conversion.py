"""単一パスデータ変換統合テスト

TDD REDフェーズ: 失敗するテストを先に作成
Task 1.3.3: パイプライン統合テスト

3つの実装済みコンポーネントを統合してデータ変換の単一パス処理を実現:
- UnifiedProcessingPipeline (Task 1.3.1) - 5段階→3段階統合
- OptimizedHeaderProcessor (Task 1.3.2) - 単一パスヘッダー処理
- CacheIntegratedPipeline (Task 1.2.8) - キャッシュ最適化

統合効果:
- JSON→DataFrame→JSON重複排除
- 処理速度40%以上向上
- メモリ使用量30%以上削減
- 中間データ削減50%以上
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock

import pandas as pd
import pytest

# REDフェーズ: 存在しないクラスをインポート（意図的にエラー）
try:
    from sphinxcontrib.jsontable.core.single_pass_data_converter import (
        DataConversionMetrics,
        IntegratedPipelineResult,
        PipelineIntegrationManager,
        SinglePassDataConverter,
    )

    SINGLE_PASS_CONVERTER_AVAILABLE = True
except ImportError:
    SINGLE_PASS_CONVERTER_AVAILABLE = False

# 実装済みコンポーネント
from sphinxcontrib.jsontable.core.cache_integrated_pipeline import (
    CacheIntegratedPipeline,
)
from sphinxcontrib.jsontable.core.data_converter import IDataConverter
from sphinxcontrib.jsontable.core.distributed_cache import DistributedCacheConfiguration
from sphinxcontrib.jsontable.core.excel_reader import IExcelReader
from sphinxcontrib.jsontable.core.file_level_cache import CacheConfiguration
from sphinxcontrib.jsontable.core.range_parser import IRangeParser
from sphinxcontrib.jsontable.errors.error_handlers import IErrorHandler
from sphinxcontrib.jsontable.facade.optimized_header_processor import (
    OptimizedHeaderProcessor,
)
from sphinxcontrib.jsontable.facade.unified_processing_pipeline import (
    UnifiedProcessingPipeline,
)
from sphinxcontrib.jsontable.security.security_scanner import ISecurityValidator


class TestSinglePassDataConversion:
    """単一パスデータ変換統合テスト

    TDD REDフェーズ: 統合コンポーネントが存在しないため、
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

    def create_test_excel_file(self, filename: str = "test_integration.xlsx") -> Path:
        """テスト用Excelファイル作成

        Args:
            filename: ファイル名

        Returns:
            Path: 作成されたファイルのパス
        """
        file_path = self.temp_dir / filename

        # データ変換統合テスト用データ作成
        data = {
            "Product ID": ["PRD001", "PRD002", "PRD003", "PRD004", "PRD005"],
            "Product Name": [
                "Laptop Pro",
                "Mouse Wireless",
                "Keyboard RGB",
                "Monitor 4K",
                "Webcam HD",
            ],
            "Category": [
                "Electronics",
                "Accessories",
                "Accessories",
                "Electronics",
                "Electronics",
            ],
            "Price (USD)": [1299.99, 49.99, 129.99, 699.99, 199.99],
            "Stock Quantity": [150, 500, 250, 75, 300],
            "Supplier Region": [
                "North America",
                "Asia",
                "Europe",
                "North America",
                "Asia",
            ],
        }

        df = pd.DataFrame(data)
        df.to_excel(file_path, index=False)

        return file_path

    @pytest.mark.performance
    def test_single_pass_data_conversion(self):
        """単一パスデータ変換統合テスト

        RED: SinglePassDataConverterクラスが存在しないため失敗する
        期待動作:
        - 3つのコンポーネント統合による単一パス処理実現
        - JSON→DataFrame→JSON重複処理完全排除
        - 処理速度40%以上向上、メモリ30%以上削減
        - データ変換精度100%保証
        """
        # テストファイル作成
        test_file = self.create_test_excel_file("single_pass_test.xlsx")

        # 単一パスデータコンバーター初期化
        converter = SinglePassDataConverter(
            unified_pipeline=UnifiedProcessingPipeline(
                excel_reader=self.mock_excel_reader,
                data_converter=self.mock_data_converter,
                range_parser=self.mock_range_parser,
            ),
            header_processor=OptimizedHeaderProcessor(
                excel_reader=self.mock_excel_reader,
                data_converter=self.mock_data_converter,
            ),
            cache_pipeline=CacheIntegratedPipeline(
                cache_config=CacheConfiguration(
                    max_memory_mb=100,
                    enable_compression=False,
                    enable_performance_tracking=True,
                ),
                distributed_config=DistributedCacheConfiguration(
                    cache_node_count=2,
                    replication_factor=1,
                    enable_cache_clustering=False,
                ),
            ),
            enable_single_pass_optimization=True,
            enable_data_conversion_monitoring=True,
        )

        # 処理オプション設定
        conversion_options = {
            "header_row": 0,
            "enable_performance_tracking": True,
            "enable_precision_validation": True,
            "enable_memory_optimization": True,
        }

        # 単一パスデータ変換実行
        result = converter.execute_single_pass_conversion(
            file_path=test_file, **conversion_options
        )

        # 基本結果検証
        assert isinstance(result, IntegratedPipelineResult)
        assert result.success is True
        assert result.converted_data is not None
        assert result.original_data_preserved is True

        # 単一パス処理確認
        assert result.conversion_passes == 1  # 単一パス
        assert result.intermediate_conversions == 0  # 中間変換なし
        assert result.duplicate_operations_eliminated >= 3  # 重複排除

        # データ変換精度確認
        metrics = result.conversion_metrics
        assert isinstance(metrics, DataConversionMetrics)
        assert metrics.data_integrity_score >= 1.0  # 100%精度
        assert metrics.schema_consistency_maintained is True
        assert metrics.type_inference_accuracy >= 0.95  # 95%以上精度

        # パフォーマンス改善確認
        assert metrics.processing_speed_improvement >= 0.40  # 40%以上向上
        assert metrics.memory_usage_reduction >= 0.30  # 30%以上削減
        assert metrics.intermediate_data_reduction >= 0.50  # 50%以上削減

        # JSON→DataFrame→JSON最適化確認
        conversion_flow = result.conversion_flow_analysis
        assert conversion_flow["json_to_dataframe_optimized"] is True
        assert conversion_flow["dataframe_to_json_optimized"] is True
        assert conversion_flow["redundant_conversions_eliminated"] >= 2

        print(
            f"Processing speed improvement: {metrics.processing_speed_improvement:.1%}"
        )
        print(f"Memory reduction: {metrics.memory_usage_reduction:.1%}")
        print(f"Data integrity: {metrics.data_integrity_score:.1%}")

    @pytest.mark.performance
    def test_integrated_pipeline_components(self):
        """統合パイプラインコンポーネントテスト

        RED: パイプライン統合管理機能が存在しないため失敗する
        期待動作:
        - UnifiedProcessingPipeline + OptimizedHeaderProcessor + CacheIntegratedPipeline統合
        - コンポーネント間データフロー最適化
        - 統合エラーハンドリング動作確認
        - 処理効率シナジー効果測定
        """
        # テストファイル作成
        test_file = self.create_test_excel_file("component_integration.xlsx")

        # パイプライン統合管理インスタンス作成
        integration_manager = PipelineIntegrationManager(
            enable_component_optimization=True,
            enable_data_flow_optimization=True,
            enable_error_handling_integration=True,
            enable_performance_monitoring=True,
        )

        # 統合コンポーネント設定
        components_config = {
            "unified_pipeline": {
                "enable_three_stage_optimization": True,
                "enable_performance_monitoring": True,
            },
            "header_processor": {
                "enable_single_pass_processing": True,
                "enable_advanced_normalization": True,
            },
            "cache_pipeline": {
                "enable_distributed_caching": True,
                "enable_performance_optimization": True,
            },
        }

        # 統合パイプライン初期化
        integrated_result = integration_manager.initialize_integrated_pipeline(
            excel_reader=self.mock_excel_reader,
            data_converter=self.mock_data_converter,
            range_parser=self.mock_range_parser,
            security_validator=self.mock_security_validator,
            error_handler=self.mock_error_handler,
            components_config=components_config,
        )

        # 統合初期化結果検証
        assert integrated_result.initialization_success is True
        assert integrated_result.components_count == 3
        assert integrated_result.integration_conflicts == 0

        # コンポーネント間データフロー確認
        data_flow = integrated_result.data_flow_analysis
        assert data_flow["unified_to_header_processor_optimized"] is True
        assert data_flow["header_processor_to_cache_optimized"] is True
        assert data_flow["end_to_end_optimization_enabled"] is True

        # 統合処理実行
        processing_result = integration_manager.execute_integrated_processing(
            file_path=test_file,
            processing_options={
                "header_row": 0,
                "enable_full_integration": True,
                "enable_performance_tracking": True,
            },
        )

        # 統合処理結果検証
        assert processing_result.success is True
        assert processing_result.all_components_executed is True
        assert processing_result.integration_efficiency >= 0.85  # 85%以上効率

        # シナジー効果確認
        synergy_metrics = processing_result.synergy_analysis
        assert synergy_metrics["component_synergy_score"] >= 0.80  # 80%以上シナジー
        assert synergy_metrics["performance_amplification"] >= 1.2  # 20%以上増幅
        assert synergy_metrics["combined_optimization_effect"] >= 0.60  # 60%以上効果

        print(f"Integration efficiency: {processing_result.integration_efficiency:.1%}")
        print(f"Synergy score: {synergy_metrics['component_synergy_score']:.1%}")

    @pytest.mark.performance
    def test_json_dataframe_json_optimization(self):
        """JSON→DataFrame→JSON変換最適化テスト

        RED: JSON変換最適化機能が存在しないため失敗する
        期待動作:
        - JSON→DataFrame→JSON変換サイクルの完全最適化
        - 重複変換処理の完全排除
        - データ形式変換効率の最大化
        - 型推論・スキーマ保持最適化
        """
        # テストファイル作成
        test_file = self.create_test_excel_file("json_optimization.xlsx")

        # 単一パスデータコンバーター初期化
        converter = SinglePassDataConverter(
            unified_pipeline=Mock(),
            header_processor=Mock(),
            cache_pipeline=Mock(),
            enable_json_dataframe_optimization=True,
            enable_type_inference_optimization=True,
            enable_schema_preservation=True,
        )

        # JSON変換最適化オプション設定
        optimization_options = {
            "eliminate_redundant_conversions": True,
            "optimize_type_inference": True,
            "preserve_schema_consistency": True,
            "enable_conversion_caching": True,
            "monitor_conversion_efficiency": True,
        }

        # JSON→DataFrame→JSON最適化実行
        optimization_result = converter.optimize_json_dataframe_conversion_cycle(
            file_path=test_file, optimization_options=optimization_options
        )

        # 最適化結果検証
        assert optimization_result.optimization_success is True
        assert optimization_result.conversion_cycle_optimized is True
        assert optimization_result.redundant_conversions_eliminated >= 2

        # JSON→DataFrame最適化確認
        json_to_df = optimization_result.json_to_dataframe_analysis
        assert json_to_df["conversion_efficiency"] >= 0.90  # 90%以上効率
        assert json_to_df["type_inference_optimized"] is True
        assert json_to_df["schema_detection_optimized"] is True

        # DataFrame→JSON最適化確認
        df_to_json = optimization_result.dataframe_to_json_analysis
        assert df_to_json["serialization_efficiency"] >= 0.90  # 90%以上効率
        assert df_to_json["type_preservation_optimized"] is True
        assert df_to_json["structure_preservation_optimized"] is True

        # 重複排除効果確認
        elimination_metrics = optimization_result.duplication_elimination
        assert elimination_metrics["duplicate_type_inference_eliminated"] >= 1
        assert elimination_metrics["duplicate_schema_detection_eliminated"] >= 1
        assert elimination_metrics["redundant_validation_eliminated"] >= 2

        # 変換サイクル効率確認
        cycle_efficiency = optimization_result.conversion_cycle_metrics
        assert cycle_efficiency["overall_efficiency"] >= 0.85  # 85%以上効率
        assert cycle_efficiency["data_loss_prevention"] >= 0.99  # 99%以上保持
        assert cycle_efficiency["performance_gain"] >= 0.35  # 35%以上向上

        print(
            f"Conversion cycle efficiency: {cycle_efficiency['overall_efficiency']:.1%}"
        )
        print(f"Performance gain: {cycle_efficiency['performance_gain']:.1%}")

    @pytest.mark.performance
    def test_performance_improvement_measurement(self):
        """パフォーマンス改善定量測定テスト

        RED: パフォーマンス測定機能が存在しないため失敗する
        期待動作:
        - 統合前後のパフォーマンス定量比較
        - 処理時間・メモリ使用量・スループット改善測定
        - ベンチマーク結果の信頼性確保
        - 回帰防止のための継続監視
        """
        # 複数サイズのテストファイル作成
        test_files = {
            "small": self.create_test_excel_file("perf_small.xlsx"),
            "medium": self.create_test_excel_file("perf_medium.xlsx"),
            "large": self.create_test_excel_file("perf_large.xlsx"),
        }

        # パフォーマンス測定器初期化
        converter = SinglePassDataConverter(
            unified_pipeline=Mock(),
            header_processor=Mock(),
            cache_pipeline=Mock(),
            enable_performance_benchmarking=True,
            enable_regression_monitoring=True,
        )

        # ベンチマーク設定
        benchmark_config = {
            "iterations_per_size": 5,
            "enable_memory_profiling": True,
            "enable_cpu_profiling": True,
            "enable_throughput_measurement": True,
            "baseline_comparison": True,
        }

        # 統合パフォーマンス測定実行
        benchmark_result = converter.execute_performance_benchmark(
            test_files=test_files, benchmark_config=benchmark_config
        )

        # ベンチマーク結果検証
        assert benchmark_result.benchmark_success is True
        assert benchmark_result.all_file_sizes_tested is True
        assert benchmark_result.measurement_reliability_score >= 0.95  # 95%以上信頼性

        # 処理時間改善確認
        time_metrics = benchmark_result.processing_time_analysis
        assert time_metrics["small_file_improvement"] >= 0.30  # 30%以上改善
        assert time_metrics["medium_file_improvement"] >= 0.35  # 35%以上改善
        assert time_metrics["large_file_improvement"] >= 0.40  # 40%以上改善

        # メモリ使用量改善確認
        memory_metrics = benchmark_result.memory_usage_analysis
        assert memory_metrics["peak_memory_reduction"] >= 0.30  # 30%以上削減
        assert memory_metrics["average_memory_reduction"] >= 0.25  # 25%以上削減
        assert (
            memory_metrics["memory_efficiency_improvement"] >= 0.40
        )  # 40%以上効率向上

        # スループット改善確認
        throughput_metrics = benchmark_result.throughput_analysis
        assert (
            throughput_metrics["records_per_second_improvement"] >= 0.50
        )  # 50%以上向上
        assert (
            throughput_metrics["data_volume_throughput_improvement"] >= 0.45
        )  # 45%以上向上

        # 統合効果定量化確認
        integration_impact = benchmark_result.integration_impact_analysis
        assert (
            integration_impact["unified_pipeline_contribution"] >= 0.15
        )  # 15%以上貢献
        assert (
            integration_impact["header_optimization_contribution"] >= 0.10
        )  # 10%以上貢献
        assert (
            integration_impact["cache_optimization_contribution"] >= 0.15
        )  # 15%以上貢献

        # 回帰監視確認
        regression_monitoring = benchmark_result.regression_monitoring
        assert regression_monitoring["performance_regression_detected"] is False
        assert regression_monitoring["quality_regression_detected"] is False
        assert regression_monitoring["monitoring_coverage"] >= 0.90  # 90%以上カバレッジ

        print(f"Overall improvement: {time_metrics['large_file_improvement']:.1%}")
        print(f"Memory reduction: {memory_metrics['peak_memory_reduction']:.1%}")
        print(
            f"Throughput gain: {throughput_metrics['records_per_second_improvement']:.1%}"
        )

    @pytest.mark.performance
    def test_data_conversion_precision_guarantee(self):
        """データ変換精度保証テスト

        RED: データ精度保証機能が存在しないため失敗する
        期待動作:
        - データ変換前後の完全一致性保証
        - 型情報・構造・メタデータの完全保持
        - 精度低下の検出・防止機能
        - 品質回帰テストの自動化
        """
        # 複雑なデータ型を含むテストファイル作成
        complex_data = {
            "String Field": ["Text A", "Text B", "Text C"],
            "Integer Field": [100, 200, 300],
            "Float Field": [10.5, 20.7, 30.9],
            "Boolean Field": [True, False, True],
            "Date Field": ["2023-01-01", "2023-06-15", "2023-12-31"],
            "Mixed Field": ["Value1", 42, "Value3"],
        }

        complex_file = self.temp_dir / "precision_test.xlsx"
        df = pd.DataFrame(complex_data)
        df.to_excel(complex_file, index=False)

        # データ精度保証コンバーター初期化
        converter = SinglePassDataConverter(
            unified_pipeline=Mock(),
            header_processor=Mock(),
            cache_pipeline=Mock(),
            enable_precision_guarantee=True,
            enable_quality_monitoring=True,
            enable_regression_testing=True,
        )

        # 精度保証設定
        precision_config = {
            "enforce_type_consistency": True,
            "preserve_data_structure": True,
            "maintain_metadata_integrity": True,
            "enable_precision_validation": True,
            "quality_threshold": 0.999,  # 99.9%以上精度要求
        }

        # データ変換精度保証実行
        precision_result = converter.execute_precision_guaranteed_conversion(
            file_path=complex_file, precision_config=precision_config
        )

        # 精度保証結果検証
        assert precision_result.precision_guarantee_success is True
        assert precision_result.data_integrity_maintained is True
        assert precision_result.quality_score >= 0.999  # 99.9%以上品質

        # 型精度確認
        type_precision = precision_result.type_precision_analysis
        assert type_precision["string_type_preserved"] is True
        assert type_precision["numeric_type_preserved"] is True
        assert type_precision["boolean_type_preserved"] is True
        assert type_precision["date_type_preserved"] is True
        assert type_precision["type_inference_accuracy"] >= 0.95  # 95%以上精度

        # 構造精度確認
        structure_precision = precision_result.structure_precision_analysis
        assert structure_precision["row_count_preserved"] is True
        assert structure_precision["column_count_preserved"] is True
        assert structure_precision["column_order_preserved"] is True
        assert structure_precision["data_relationships_preserved"] is True

        # メタデータ精度確認
        metadata_precision = precision_result.metadata_precision_analysis
        assert metadata_precision["header_information_preserved"] is True
        assert metadata_precision["schema_information_preserved"] is True
        assert metadata_precision["processing_metadata_consistent"] is True

        # 品質回帰テスト確認
        regression_testing = precision_result.quality_regression_testing
        assert regression_testing["regression_tests_passed"] is True
        assert regression_testing["quality_degradation_detected"] is False
        assert regression_testing["continuous_monitoring_enabled"] is True

        # 精度検証統計確認
        validation_stats = precision_result.precision_validation_statistics
        assert validation_stats["data_consistency_score"] >= 1.0  # 100%一致
        assert validation_stats["conversion_accuracy_score"] >= 0.999  # 99.9%以上精度
        assert (
            validation_stats["quality_assurance_coverage"] >= 0.95
        )  # 95%以上カバレッジ

        print(f"Data integrity: {precision_result.quality_score:.3%}")
        print(
            f"Type inference accuracy: {type_precision['type_inference_accuracy']:.1%}"
        )
        print(
            f"Conversion accuracy: {validation_stats['conversion_accuracy_score']:.3%}"
        )

    @pytest.mark.performance
    def test_backward_compatibility_integration(self):
        """後方互換性統合テスト

        RED: 後方互換性統合機能が存在しないため失敗する
        期待動作:
        - 既存API完全互換性保証
        - 統合最適化の透明性確保
        - 段階的移行サポート
        - レガシーシステム完全対応
        """
        # テストファイル作成
        test_file = self.create_test_excel_file("compatibility_test.xlsx")

        # 後方互換性統合コンバーター初期化
        converter = SinglePassDataConverter(
            unified_pipeline=Mock(),
            header_processor=Mock(),
            cache_pipeline=Mock(),
            enable_backward_compatibility=True,
            enable_legacy_api_support=True,
            enable_migration_assistance=True,
        )

        # レガシーAPI互換実行
        legacy_result = converter.process_with_legacy_api(
            file_path=test_file, sheet_name="Sheet1", header_row=0, range_spec="A1:F6"
        )

        # 基本結果形式確認（完全互換）
        assert legacy_result["success"] is True
        assert legacy_result["data"] is not None
        assert legacy_result["headers"] is not None
        assert legacy_result["has_header"] is True
        assert "metadata" in legacy_result

        # API互換性確認
        compatibility = legacy_result.get("compatibility_validation", {})
        assert compatibility.get("api_compatibility_score", 0) >= 0.98  # 98%以上互換
        assert compatibility.get("result_format_compatibility") is True
        assert compatibility.get("behavior_consistency") is True

        # 統合最適化透明性確認
        optimization_transparency = legacy_result.get("optimization_info", {})
        assert (
            optimization_transparency.get("optimizations_applied_transparently") is True
        )
        assert optimization_transparency.get("performance_improvement_achieved") is True
        assert optimization_transparency.get("user_experience_unchanged") is True

        # 段階移行サポート確認
        migration_support = legacy_result.get("migration_assistance", {})
        assert migration_support.get("migration_path_available") is True
        assert migration_support.get("rollback_capability") is True
        assert migration_support.get("progressive_enhancement_supported") is True

        print(
            f"API compatibility: {compatibility.get('api_compatibility_score', 0):.1%}"
        )
        print(
            f"Performance gain (transparent): {optimization_transparency.get('performance_improvement_percentage', 0):.1%}"
        )
