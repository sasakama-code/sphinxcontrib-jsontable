"""統合データ変換テスト

TDD REDフェーズ: 失敗するテストを先に作成
Task 1.3.5: データ変換重複排除

データ変換処理の重複を排除し、パフォーマンス向上を実現：
- DataFrame→JSON変換の重複排除（5段階→3段階）
- ヘッダー処理重複排除（Stage 4 + Stage 5→統合処理）
- データ正規化処理統合（9ファイル→3ファイル）
- 中間データオブジェクト削減（5個→2個）

統合効果:
- 処理速度40-50%向上
- メモリ使用量30-40%削減
- コード保守性67%改善
- 統合テスト簡素化
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock

import pandas as pd
import pytest

# REDフェーズ: 存在しないクラスをインポート（意図的にエラー）
try:
    from sphinxcontrib.jsontable.integration.unified_data_conversion import (
        ConversionCacheManager,
        ConversionOptimizationResult,
        ConversionPerformanceAnalyzer,
        ConversionStageMetrics,
        DataTypeOptimizer,
        MemoryOptimizedConverter,
        OptimizedDataFlow,
        PerformanceComparisonResult,
        SinglePassProcessor,
        UnifiedConversionResult,
        UnifiedDataConversionEngine,
    )
    UNIFIED_DATA_CONVERSION_AVAILABLE = True
except ImportError:
    UNIFIED_DATA_CONVERSION_AVAILABLE = False

from sphinxcontrib.jsontable.core.data_converter import IDataConverter
from sphinxcontrib.jsontable.core.single_pass_data_converter import (
    SinglePassDataConverter,
)
from sphinxcontrib.jsontable.facade.excel_processing_pipeline import (
    ExcelProcessingPipeline,
)
from sphinxcontrib.jsontable.facade.unified_processing_pipeline import (
    UnifiedProcessingPipeline,
)


class TestUnifiedDataConversion:
    """統合データ変換テスト
    
    TDD REDフェーズ: 統合データ変換エンジンが存在しないため、
    これらのテストは意図的に失敗する。
    """

    def setup_method(self):
        """各テストメソッドの前に実行される設定."""
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # モックコンポーネント作成
        self.mock_converter = Mock(spec=IDataConverter)
        self.mock_excel_pipeline = Mock(spec=ExcelProcessingPipeline)
        self.mock_unified_pipeline = Mock(spec=UnifiedProcessingPipeline)
        self.mock_single_pass_converter = Mock(spec=SinglePassDataConverter)
        
    def teardown_method(self):
        """各テストメソッドの後に実行されるクリーンアップ."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_excel_file(self, filename: str = "test_data_conversion.xlsx") -> Path:
        """テスト用Excelファイル作成
        
        Args:
            filename: ファイル名
            
        Returns:
            Path: 作成されたファイルのパス
        """
        file_path = self.temp_dir / filename
        
        # データ変換テスト用データ作成
        data = {
            'ID': [1, 2, 3, 4, 5],
            'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
            'Score': [95.5, 87.2, 91.8, 76.3, 89.7],
            'Active': [True, False, True, True, False],
            'Notes': ['Excellent', None, 'Good', 'Needs improvement', 'Average']
        }
        
        df = pd.DataFrame(data)
        df.to_excel(file_path, index=False)
        
        return file_path

    @pytest.mark.integration
    def test_unified_data_conversion_engine_initialization(self):
        """統合データ変換エンジン初期化テスト
        
        RED: UnifiedDataConversionEngineクラスが存在しないため失敗する
        期待動作:
        - 複数変換エンジンの統合初期化
        - 重複排除設定の有効化
        - パフォーマンス最適化機能の初期化
        - キャッシュマネージャーの統合
        """
        # 統合データ変換エンジン初期化
        conversion_engine = UnifiedDataConversionEngine(
            enable_deduplication=True,
            enable_performance_optimization=True,
            enable_caching=True,
            enable_memory_optimization=True,
            single_pass_mode=True
        )
        
        # 初期化検証
        assert conversion_engine.deduplication_enabled is True
        assert conversion_engine.performance_optimization_enabled is True
        assert conversion_engine.caching_enabled is True
        assert conversion_engine.memory_optimization_enabled is True
        assert conversion_engine.single_pass_mode is True
        
        # 統合コンポーネント確認
        assert isinstance(conversion_engine.cache_manager, ConversionCacheManager)
        assert isinstance(conversion_engine.performance_analyzer, ConversionPerformanceAnalyzer)
        assert isinstance(conversion_engine.data_flow_optimizer, OptimizedDataFlow)
        assert isinstance(conversion_engine.type_optimizer, DataTypeOptimizer)
        assert isinstance(conversion_engine.memory_converter, MemoryOptimizedConverter)
        
        print("Unified data conversion engine initialized successfully")

    @pytest.mark.integration
    def test_duplication_elimination_across_pipelines(self):
        """パイプライン間重複排除テスト
        
        RED: 重複排除機能が存在しないため失敗する
        期待動作:
        - 5段階パイプライン→3段階パイプラインへの統合
        - DataFrame→JSON変換の重複排除
        - ヘッダー処理重複排除（Stage 4 + Stage 5統合）
        - 中間データオブジェクト削減効果測定
        """
        # テストファイル作成
        test_file = self.create_test_excel_file("duplication_test.xlsx")
        
        # 統合データ変換エンジン初期化
        conversion_engine = UnifiedDataConversionEngine(
            enable_deduplication=True,
            enable_performance_optimization=True
        )
        
        # 重複排除前後の比較テスト
        # Before: 5段階パイプライン（重複あり）
        from unittest.mock import Mock

        from sphinxcontrib.jsontable.core.excel_reader import IExcelReader
        from sphinxcontrib.jsontable.core.range_parser import IRangeParser
        from sphinxcontrib.jsontable.errors.error_handlers import IErrorHandler
        from sphinxcontrib.jsontable.security.security_scanner import ISecurityValidator
        
        mock_excel_reader = Mock(spec=IExcelReader)
        mock_range_parser = Mock(spec=IRangeParser)
        mock_security_validator = Mock(spec=ISecurityValidator)
        mock_error_handler = Mock(spec=IErrorHandler)
        
        _ = ExcelProcessingPipeline(
            excel_reader=mock_excel_reader,
            data_converter=self.mock_converter,
            range_parser=mock_range_parser,
            security_validator=mock_security_validator,
            error_handler=mock_error_handler
        )
        
        # After: 統合処理（重複排除）
        optimized_result = conversion_engine.process_file_with_deduplication(
            file_path=test_file,
            processing_options={
                'header_row': 0,
                'eliminate_duplications': True,
                'optimize_memory': True,
                'single_pass_conversion': True
            }
        )
        
        # 重複排除効果検証
        assert isinstance(optimized_result, ConversionOptimizationResult)
        assert optimized_result.success is True
        assert optimized_result.duplications_eliminated > 0
        assert optimized_result.performance_improvement >= 0.40  # 40%以上向上
        assert optimized_result.memory_reduction >= 0.30  # 30%以上削減
        
        # 重複排除統計確認
        deduplication_stats = conversion_engine.get_deduplication_statistics()
        assert deduplication_stats['dataframe_conversion_deduplicated'] is True
        assert deduplication_stats['header_processing_unified'] is True
        assert deduplication_stats['intermediate_objects_reduced'] >= 3  # 5個→2個
        assert deduplication_stats['pipeline_stages_optimized'] == 2  # 5段階→3段階
        
        # パフォーマンス改善確認
        performance_metrics = optimized_result.performance_metrics
        assert performance_metrics.processing_time_reduction >= 0.40
        assert performance_metrics.memory_usage_reduction >= 0.30
        assert performance_metrics.conversion_efficiency >= 0.95
        
        print(f"Performance improvement: {optimized_result.performance_improvement:.1%}")
        print(f"Memory reduction: {optimized_result.memory_reduction:.1%}")

    @pytest.mark.integration
    def test_single_pass_data_conversion(self):
        """単一パスデータ変換テスト
        
        RED: 単一パス変換機能が存在しないため失敗する
        期待動作:
        - DataFrame→JSON変換を1回のパスで完了
        - ヘッダー処理との統合実行
        - データ型最適化の同時実行
        - メモリ効率化された変換処理
        """
        # テストファイル作成
        test_file = self.create_test_excel_file("single_pass_test.xlsx")
        
        # 単一パス変換エンジン初期化
        single_pass_processor = SinglePassProcessor(
            enable_header_integration=True,
            enable_type_optimization=True,
            enable_memory_optimization=True
        )
        
        # 単一パス変換実行
        conversion_result = single_pass_processor.execute_single_pass_conversion(
            file_path=test_file,
            conversion_options={
                'header_processing': 'integrated',
                'type_optimization': 'automatic',
                'memory_mode': 'optimized',
                'output_format': 'json'
            }
        )
        
        # 単一パス変換結果検証
        assert isinstance(conversion_result, UnifiedConversionResult)
        assert conversion_result.success is True
        assert conversion_result.single_pass_completed is True
        assert conversion_result.conversion_passes == 1  # 1回のパスのみ
        assert conversion_result.header_processing_integrated is True
        
        # データ品質確認
        converted_data = conversion_result.data
        assert isinstance(converted_data, list)
        assert len(converted_data) == 5  # テストデータの行数
        assert len(converted_data[0]) == 5  # テストデータの列数
        
        # ヘッダー統合処理確認
        headers = conversion_result.headers
        assert headers == ['ID', 'Name', 'Score', 'Active', 'Notes']
        assert conversion_result.header_normalization_applied is True
        
        # データ型最適化確認
        type_optimization = conversion_result.type_optimization_result
        assert type_optimization.numeric_types_preserved is True
        assert type_optimization.boolean_types_preserved is True
        assert type_optimization.null_values_handled is True
        
        # パフォーマンス統計確認
        performance_stats = conversion_result.performance_stats
        assert performance_stats.memory_peak_usage < 50_000_000  # 50MB未満
        assert performance_stats.conversion_time_ms < 1000  # 1秒未満
        assert performance_stats.efficiency_score >= 0.90  # 90%以上効率
        
        print(f"Single pass conversion time: {performance_stats.conversion_time_ms}ms")
        print(f"Memory peak usage: {performance_stats.memory_peak_usage / 1024 / 1024:.1f}MB")

    @pytest.mark.integration
    def test_conversion_stage_metrics_analysis(self):
        """変換段階メトリクス分析テスト
        
        RED: 段階メトリクス分析機能が存在しないため失敗する
        期待動作:
        - 各変換段階のパフォーマンス測定
        - 重複処理の特定と分析
        - ボトルネック段階の識別
        - 最適化効果の定量化
        """
        # テストファイル作成
        test_file = self.create_test_excel_file("metrics_analysis_test.xlsx")
        
        # パフォーマンス分析器初期化
        performance_analyzer = ConversionPerformanceAnalyzer(
            enable_stage_profiling=True,
            enable_memory_tracking=True,
            enable_bottleneck_detection=True
        )
        
        # 統合データ変換エンジン（分析付き）
        conversion_engine = UnifiedDataConversionEngine(
            performance_analyzer=performance_analyzer,
            enable_detailed_metrics=True
        )
        
        # 変換処理実行（メトリクス収集付き）
        conversion_result = conversion_engine.process_with_metrics_analysis(
            file_path=test_file,
            analysis_options={
                'stage_profiling': True,
                'memory_tracking': True,
                'bottleneck_detection': True,
                'comparison_baseline': 'legacy_pipeline'
            }
        )
        
        # 段階メトリクス検証
        stage_metrics = conversion_result.stage_metrics
        assert isinstance(stage_metrics, list)
        assert len(stage_metrics) == 3  # 3段階統合パイプライン
        
        for stage_metric in stage_metrics:
            assert isinstance(stage_metric, ConversionStageMetrics)
            assert stage_metric.stage_name in ['data_acquisition', 'unified_conversion', 'result_construction']
            assert stage_metric.execution_time_ms > 0
            assert stage_metric.memory_usage_mb >= 0
            assert stage_metric.efficiency_score >= 0.0
        
        # ボトルネック分析確認
        bottleneck_analysis = conversion_result.bottleneck_analysis
        assert bottleneck_analysis.primary_bottleneck is not None
        assert bottleneck_analysis.optimization_suggestions is not None
        assert len(bottleneck_analysis.optimization_suggestions) > 0
        
        # ベースライン比較確認
        baseline_comparison = conversion_result.baseline_comparison
        assert isinstance(baseline_comparison, PerformanceComparisonResult)
        assert baseline_comparison.performance_improvement >= 0.30  # 30%以上改善
        assert baseline_comparison.memory_improvement >= 0.25  # 25%以上改善
        assert baseline_comparison.stage_reduction == 2  # 5段階→3段階（-2段階）
        
        # 詳細メトリクス確認
        detailed_metrics = conversion_result.detailed_metrics
        assert detailed_metrics.total_conversion_time_ms > 0
        assert detailed_metrics.peak_memory_usage_mb > 0
        assert detailed_metrics.cpu_usage_percentage >= 0
        assert detailed_metrics.io_operations_count >= 0
        
        print(f"Total stages: {len(stage_metrics)}")
        print(f"Performance improvement: {baseline_comparison.performance_improvement:.1%}")
        print(f"Memory improvement: {baseline_comparison.memory_improvement:.1%}")

    @pytest.mark.integration
    def test_memory_optimized_conversion(self):
        """メモリ最適化変換テスト
        
        RED: メモリ最適化機能が存在しないため失敗する
        期待動作:
        - 中間オブジェクト生成の最小化
        - メモリ使用量のリアルタイム監視
        - ガベージコレクション最適化
        - 大容量データでのメモリ効率確保
        """
        # 大容量テストデータ作成
        large_data = {
            'ID': list(range(1, 10001)),  # 10,000行
            'Data1': [f'Data_{i}' for i in range(1, 10001)],
            'Data2': [float(i * 1.5) for i in range(1, 10001)],
            'Data3': [bool(i % 2) for i in range(1, 10001)],
            'Data4': [f'Value_{i}' if i % 3 == 0 else None for i in range(1, 10001)]
        }
        
        large_df = pd.DataFrame(large_data)
        large_file = self.temp_dir / "large_data_test.xlsx"
        large_df.to_excel(large_file, index=False)
        
        # メモリ最適化変換器初期化
        memory_converter = MemoryOptimizedConverter(
            enable_incremental_processing=True,
            enable_garbage_collection_optimization=True,
            enable_memory_monitoring=True,
            memory_limit_mb=100  # 100MB制限
        )
        
        # メモリ最適化変換実行
        conversion_result = memory_converter.execute_memory_optimized_conversion(
            file_path=large_file,
            memory_options={
                'incremental_chunk_size': 1000,  # 1000行ずつ処理
                'memory_monitoring': True,
                'gc_optimization': True,
                'memory_limit_enforcement': True
            }
        )
        
        # メモリ最適化結果検証
        assert conversion_result.success is True
        assert conversion_result.memory_optimized is True
        assert conversion_result.incremental_processing_used is True
        assert conversion_result.gc_optimization_applied is True
        
        # メモリ使用量確認
        memory_metrics = conversion_result.memory_metrics
        assert memory_metrics.peak_memory_usage_mb <= 100  # 制限内
        assert memory_metrics.memory_efficiency >= 0.85  # 85%以上効率
        assert memory_metrics.gc_optimizations_count > 0
        assert memory_metrics.memory_leaks_detected == 0
        
        # 処理結果品質確認
        converted_data = conversion_result.data
        assert len(converted_data) == 10000  # 全データ処理
        assert len(converted_data[0]) == 5  # 全列処理
        
        # インクリメンタル処理統計確認
        incremental_stats = conversion_result.incremental_stats
        assert incremental_stats.total_chunks_processed >= 10  # 10,000行 ÷ 1,000
        assert incremental_stats.chunk_processing_consistent is True
        assert incremental_stats.data_integrity_maintained is True
        
        print(f"Peak memory usage: {memory_metrics.peak_memory_usage_mb:.1f}MB")
        print(f"Memory efficiency: {memory_metrics.memory_efficiency:.1%}")
        print(f"Total chunks processed: {incremental_stats.total_chunks_processed}")

    @pytest.mark.integration
    def test_conversion_caching_integration(self):
        """変換キャッシュ統合テスト
        
        RED: 変換キャッシュ機能が存在しないため失敗する
        期待動作:
        - 変換結果のインテリジェントキャッシング
        - ファイル変更検出による自動キャッシュ無効化
        - 型別最適化キャッシュ
        - キャッシュヒット率の最適化
        """
        # テストファイル作成
        test_file = self.create_test_excel_file("cache_test.xlsx")
        
        # 変換キャッシュマネージャー初期化
        cache_manager = ConversionCacheManager(
            enable_result_caching=True,
            enable_type_specific_caching=True,
            enable_file_change_detection=True,
            cache_size_limit_mb=50
        )
        
        # キャッシュ統合変換エンジン
        conversion_engine = UnifiedDataConversionEngine(
            cache_manager=cache_manager,
            enable_caching=True
        )
        
        # 初回変換実行（キャッシュミス）
        first_result = conversion_engine.process_with_caching(
            file_path=test_file,
            cache_options={
                'enable_result_caching': True,
                'cache_key_generation': 'smart',
                'type_specific_optimization': True
            }
        )
        
        # 初回変換結果検証
        assert first_result.success is True
        assert first_result.cache_hit is False
        assert first_result.cache_stored is True
        
        # 同一ファイル再変換（キャッシュヒット）
        second_result = conversion_engine.process_with_caching(
            file_path=test_file,
            cache_options={
                'enable_result_caching': True,
                'cache_key_generation': 'smart',
                'type_specific_optimization': True
            }
        )
        
        # キャッシュヒット結果検証
        assert second_result.success is True
        assert second_result.cache_hit is True
        assert second_result.cached_result_used is True
        assert second_result.processing_time_ms < first_result.processing_time_ms * 0.1  # 90%高速化
        
        # キャッシュ統計確認
        cache_stats = cache_manager.get_cache_statistics()
        assert cache_stats['total_requests'] == 2
        assert cache_stats['cache_hits'] == 1
        assert cache_stats['cache_misses'] == 1
        assert cache_stats['hit_ratio'] == 0.5  # 50%
        assert cache_stats['cache_entries'] == 1
        
        # 型別キャッシュ効率確認
        type_cache_stats = cache_manager.get_type_specific_cache_stats()
        assert type_cache_stats['dataframe_cache_hits'] >= 0
        assert type_cache_stats['json_cache_hits'] >= 0
        assert type_cache_stats['header_cache_hits'] >= 0
        assert type_cache_stats['type_optimization_cache_hits'] >= 0
        
        # ファイル変更検出テスト
        # ファイル更新
        updated_data = {
            'ID': [1, 2],
            'Name': ['Alice', 'Bob'],
            'Score': [95.5, 87.2]
        }
        updated_df = pd.DataFrame(updated_data)
        updated_df.to_excel(test_file, index=False)
        
        # 更新後変換（キャッシュ無効化）
        third_result = conversion_engine.process_with_caching(
            file_path=test_file,
            cache_options={
                'enable_result_caching': True,
                'cache_key_generation': 'smart',
                'type_specific_optimization': True
            }
        )
        
        # ファイル変更検出結果検証
        assert third_result.success is True
        assert third_result.cache_hit is False  # ファイル変更によりキャッシュ無効化
        assert third_result.file_change_detected is True
        assert third_result.cache_invalidated is True
        
        print(f"Cache hit ratio: {cache_stats['hit_ratio']:.1%}")
        print(f"Processing time reduction: {(1 - second_result.processing_time_ms / first_result.processing_time_ms):.1%}")

    @pytest.mark.integration
    def test_data_type_optimization_integration(self):
        """データ型最適化統合テスト
        
        RED: データ型最適化機能が存在しないため失敗する
        期待動作:
        - 自動データ型検出と最適化
        - 数値型・日付型・文字列型の最適化
        - メモリ使用量削減効果測定
        - 型変換精度の保証
        """
        # 多様なデータ型を含むテストファイル作成
        diverse_data = {
            'Integer': [1, 2, 3, 4, 5],
            'Float': [1.1, 2.2, 3.3, 4.4, 5.5],
            'String': ['A', 'B', 'C', 'D', 'E'],
            'Boolean': [True, False, True, False, True],
            'Date': pd.date_range('2023-01-01', periods=5),
            'Mixed': [1, 'text', 3.14, True, None]
        }
        
        diverse_df = pd.DataFrame(diverse_data)
        diverse_file = self.temp_dir / "diverse_types_test.xlsx"
        diverse_df.to_excel(diverse_file, index=False)
        
        # データ型最適化器初期化
        type_optimizer = DataTypeOptimizer(
            enable_automatic_detection=True,
            enable_memory_optimization=True,
            enable_precision_preservation=True,
            enable_mixed_type_handling=True
        )
        
        # データ型最適化変換実行
        optimization_result = type_optimizer.execute_type_optimized_conversion(
            file_path=diverse_file,
            optimization_options={
                'auto_type_detection': True,
                'memory_optimization': True,
                'precision_preservation': True,
                'mixed_type_strategy': 'smart_conversion'
            }
        )
        
        # データ型最適化結果検証
        assert optimization_result.success is True
        assert optimization_result.type_optimization_applied is True
        assert optimization_result.automatic_detection_used is True
        assert optimization_result.memory_optimization_applied is True
        
        # 型別最適化確認
        type_results = optimization_result.type_optimization_results
        assert type_results['integer_optimization']['memory_reduction'] > 0
        assert type_results['float_optimization']['precision_preserved'] is True
        assert type_results['string_optimization']['memory_efficient'] is True
        assert type_results['boolean_optimization']['optimized'] is True
        assert type_results['date_optimization']['format_standardized'] is True
        assert type_results['mixed_type_optimization']['strategy_applied'] == 'smart_conversion'
        
        # メモリ効率改善確認
        memory_improvement = optimization_result.memory_improvement_metrics
        assert memory_improvement.total_memory_reduction >= 0.20  # 20%以上削減
        assert memory_improvement.type_specific_reductions['integer'] > 0
        assert memory_improvement.type_specific_reductions['string'] > 0
        
        # データ品質保証確認
        quality_metrics = optimization_result.data_quality_metrics
        assert quality_metrics.data_integrity_preserved is True
        assert quality_metrics.precision_loss_percentage <= 0.01  # 1%以下
        assert quality_metrics.type_conversion_accuracy >= 0.99  # 99%以上
        
        # 変換結果データ確認
        converted_data = optimization_result.data
        assert len(converted_data) == 5  # 行数保持
        assert len(converted_data[0]) == 6  # 列数保持
        
        # 型変換精度確認
        type_accuracy = optimization_result.type_conversion_accuracy
        for _column_name, accuracy in type_accuracy.items():
            assert accuracy >= 0.95  # 各列95%以上精度
        
        print(f"Total memory reduction: {memory_improvement.total_memory_reduction:.1%}")
        print(f"Type conversion accuracy: {quality_metrics.type_conversion_accuracy:.1%}")
        print(f"Data integrity preserved: {quality_metrics.data_integrity_preserved}")