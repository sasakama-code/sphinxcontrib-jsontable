"""統合パイプライン3段階テスト

TDD REDフェーズ: 失敗するテストを先に作成
Task 1.3.1: パイプライン統合設計

現在の5段階パイプラインを3段階に統合:
Stage 1: データ取得・前処理統合 (Security + File Reading + Range/Skip処理)
Stage 2: データ変換・ヘッダー処理統合 (Data Conversion + Header Processing)
Stage 3: 結果構築・メタデータ統合 (Result Building + Metadata Integration)
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock

import pandas as pd
import pytest

# REDフェーズ: 存在しないクラスをインポート（意図的にエラー）
try:
    from sphinxcontrib.jsontable.facade.unified_processing_pipeline import (
        PipelineStageResult,
        ProcessingContext,
        UnifiedProcessingPipeline,
    )

    UNIFIED_PIPELINE_AVAILABLE = True
except ImportError:
    UNIFIED_PIPELINE_AVAILABLE = False

from sphinxcontrib.jsontable.core.data_converter import IDataConverter
from sphinxcontrib.jsontable.core.excel_reader import IExcelReader
from sphinxcontrib.jsontable.core.range_parser import IRangeParser
from sphinxcontrib.jsontable.errors.error_handlers import IErrorHandler
from sphinxcontrib.jsontable.security.security_scanner import ISecurityValidator


class TestUnifiedPipelineThreeStages:
    """統合パイプライン3段階テスト

    TDD REDフェーズ: 統合パイプラインクラスが存在しないため、
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

    def create_test_excel_file(self, filename: str = "test_unified.xlsx") -> Path:
        """テスト用Excelファイル作成

        Args:
            filename: ファイル名

        Returns:
            Path: 作成されたファイルのパス
        """
        file_path = self.temp_dir / filename

        # テスト用データ作成
        data = {
            "ID": [1, 2, 3, 4, 5],
            "Name": ["Alice", "Bob", "Charlie", "David", "Eve"],
            "Age": [25, 30, 35, 28, 32],
            "Department": ["Engineering", "Sales", "Engineering", "HR", "Sales"],
        }

        df = pd.DataFrame(data)
        df.to_excel(file_path, index=False)

        return file_path

    @pytest.mark.performance
    def test_unified_pipeline_three_stage_basic_processing(self):
        """統合パイプライン3段階基本処理テスト

        RED: UnifiedProcessingPipelineクラスが存在しないため失敗する
        期待動作:
        - 5段階→3段階統合パイプライン実行
        - 処理効率の大幅向上（30%以上の高速化）
        - 重複処理排除の確認
        - 既存機能の完全保持
        """
        # テストファイル作成
        test_file = self.create_test_excel_file("three_stage_basic.xlsx")

        # 統合パイプライン初期化
        unified_pipeline = UnifiedProcessingPipeline(
            excel_reader=self.mock_excel_reader,
            data_converter=self.mock_data_converter,
            range_parser=self.mock_range_parser,
            security_validator=self.mock_security_validator,
            error_handler=self.mock_error_handler,
            enable_three_stage_optimization=True,
            enable_duplicate_elimination=True,
            enable_performance_monitoring=True,
        )

        # 処理オプション設定
        processing_options = {
            "sheet_name": "Sheet1",
            "header_row": 0,
            "enable_stage_profiling": True,
        }

        # 統合パイプライン実行
        result = unified_pipeline.process_excel_file(
            file_path=test_file, **processing_options
        )

        # 基本結果検証
        assert result["success"] is True
        assert result["data"] is not None
        assert len(result["data"]) > 0
        assert result["rows"] > 0
        assert result["columns"] > 0

        # 3段階実行確認
        assert "stage_execution_info" in result
        stage_info = result["stage_execution_info"]
        assert len(stage_info) == 3
        assert "stage_1_data_acquisition" in stage_info
        assert "stage_2_data_transformation" in stage_info
        assert "stage_3_result_construction" in stage_info

        # 各段階の成功確認
        for _stage_name, stage_result in stage_info.items():
            assert stage_result["success"] is True
            assert stage_result["processing_time"] > 0
            assert "operations_performed" in stage_result

        # パフォーマンス改善確認
        assert "performance_metrics" in result
        perf_metrics = result["performance_metrics"]
        assert perf_metrics["efficiency_improvement_ratio"] >= 1.3  # 30%以上改善
        assert perf_metrics["duplicate_elimination_count"] >= 2
        assert perf_metrics["total_processing_stages"] == 3

        # 既存機能保持確認
        assert result["headers"] is not None
        assert result["has_header"] is True
        assert "metadata" in result

        print(
            f"Efficiency improvement: {perf_metrics['efficiency_improvement_ratio']:.1f}x"
        )

    @pytest.mark.performance
    def test_unified_pipeline_stage_one_data_acquisition(self):
        """統合パイプライン - Stage 1: データ取得・前処理統合テスト

        RED: Stage 1統合処理が存在しないため失敗する
        期待動作:
        - セキュリティ検証 + ファイル読み込み + 範囲・スキップ処理の統合
        - 中間データ生成削減
        - エラーハンドリング統合
        - 処理効率向上
        """
        # テストファイル作成
        test_file = self.create_test_excel_file("stage_one_test.xlsx")

        # 統合パイプライン初期化
        unified_pipeline = UnifiedProcessingPipeline(
            excel_reader=self.mock_excel_reader,
            data_converter=self.mock_data_converter,
            range_parser=self.mock_range_parser,
            security_validator=self.mock_security_validator,
            error_handler=self.mock_error_handler,
        )

        # Stage 1専用処理オプション
        stage_one_options = {
            "range_spec": "A1:C4",
            "skip_rows": "1,3",
            "enable_security_validation": True,
            "enable_integrated_error_handling": True,
        }

        # Stage 1単体実行
        stage_result = unified_pipeline.execute_stage_one_data_acquisition(
            file_path=test_file,
            sheet_name="Sheet1",
            processing_options=stage_one_options,
        )

        # Stage 1結果検証
        assert isinstance(stage_result, PipelineStageResult)
        assert stage_result.success is True
        assert stage_result.stage_name == "data_acquisition"
        assert stage_result.processed_data is not None
        assert stage_result.processing_context is not None

        # 統合処理確認
        context = stage_result.processing_context
        assert context.security_validated is True
        assert context.file_loaded is True
        assert context.range_applied is True
        assert context.skip_rows_applied is True

        # 中間データ削減確認
        assert stage_result.intermediate_data_count <= 2  # 大幅削減
        assert stage_result.memory_efficiency_score >= 0.7

        # エラーハンドリング統合確認
        assert context.error_handling_integrated is True
        assert len(context.error_handlers_used) == 1  # 統合ハンドラー

        # パフォーマンスメトリクス確認
        assert stage_result.execution_time > 0
        assert stage_result.operations_eliminated >= 3  # 重複処理削除
        assert stage_result.efficiency_gain >= 0.2  # 20%以上効率向上

    @pytest.mark.performance
    def test_unified_pipeline_stage_two_data_transformation(self):
        """統合パイプライン - Stage 2: データ変換・ヘッダー処理統合テスト

        RED: Stage 2統合処理が存在しないため失敗する
        期待動作:
        - データ変換 + ヘッダー処理の一元化
        - 重複変換の排除
        - ヘッダー正規化の最適化
        - 単一パス処理実現
        """
        # 統合パイプライン初期化
        unified_pipeline = UnifiedProcessingPipeline(
            excel_reader=self.mock_excel_reader,
            data_converter=self.mock_data_converter,
            range_parser=self.mock_range_parser,
        )

        # Stage 1結果をモック（Stage 2の入力データ）
        mock_stage_one_result = PipelineStageResult(
            success=True,
            stage_name="data_acquisition",
            processed_data=pd.DataFrame(
                {
                    "Name": ["Alice", "Bob", "Charlie"],
                    "Age": [25, 30, 35],
                    "Dept": ["Eng", "Sales", "Eng"],
                }
            ),
            processing_context=ProcessingContext(
                security_validated=True, file_loaded=True
            ),
        )

        # Stage 2専用処理オプション
        stage_two_options = {
            "header_row": 0,
            "enable_header_normalization": True,
            "enable_single_pass_conversion": True,
            "data_type_inference": True,
        }

        # Stage 2単体実行
        stage_result = unified_pipeline.execute_stage_two_data_transformation(
            stage_one_result=mock_stage_one_result, processing_options=stage_two_options
        )

        # Stage 2結果検証
        assert isinstance(stage_result, PipelineStageResult)
        assert stage_result.success is True
        assert stage_result.stage_name == "data_transformation"
        assert stage_result.processed_data is not None

        # データ変換統合確認
        context = stage_result.processing_context
        assert context.data_converted is True
        assert context.headers_processed is True
        assert context.single_pass_conversion is True

        # ヘッダー処理統合確認
        transformed_data = stage_result.processed_data
        assert "normalized_headers" in transformed_data
        assert "processed_data_rows" in transformed_data
        assert transformed_data["header_normalization_applied"] is True

        # 重複処理排除確認
        assert stage_result.duplicate_conversions_eliminated >= 1
        assert stage_result.header_processing_cycles == 1  # 単一サイクル

        # 最適化効果確認
        assert stage_result.conversion_efficiency >= 0.8  # 80%以上効率
        assert stage_result.header_normalization_time <= 0.01  # 高速化
        assert stage_result.memory_usage_reduction >= 0.3  # 30%削減

    @pytest.mark.performance
    def test_unified_pipeline_stage_three_result_construction(self):
        """統合パイプライン - Stage 3: 結果構築・メタデータ統合テスト

        RED: Stage 3統合処理が存在しないため失敗する
        期待動作:
        - 結果構築 + メタデータ生成の統合
        - 冗長なメタデータ処理削除
        - 統合結果オブジェクト構築
        - エンドツーエンド最適化
        """
        # 統合パイプライン初期化
        unified_pipeline = UnifiedProcessingPipeline(
            excel_reader=self.mock_excel_reader,
            data_converter=self.mock_data_converter,
            range_parser=self.mock_range_parser,
        )

        # Stage 2結果をモック（Stage 3の入力データ）
        mock_stage_two_result = PipelineStageResult(
            success=True,
            stage_name="data_transformation",
            processed_data={
                "normalized_headers": ["Name", "Age", "Department"],
                "processed_data_rows": [
                    ["Alice", 25, "Engineering"],
                    ["Bob", 30, "Sales"],
                    ["Charlie", 35, "Engineering"],
                ],
                "data_types": ["string", "integer", "string"],
            },
            processing_context=ProcessingContext(
                data_converted=True, headers_processed=True
            ),
        )

        # Stage 3専用処理オプション
        stage_three_options = {
            "include_metadata": True,
            "include_performance_metrics": True,
            "enable_result_validation": True,
            "metadata_optimization": True,
        }

        # Stage 3単体実行
        stage_result = unified_pipeline.execute_stage_three_result_construction(
            stage_two_result=mock_stage_two_result,
            processing_options=stage_three_options,
        )

        # Stage 3結果検証
        assert isinstance(stage_result, PipelineStageResult)
        assert stage_result.success is True
        assert stage_result.stage_name == "result_construction"

        # 統合結果構築確認
        final_result = stage_result.processed_data
        assert final_result["success"] is True
        assert final_result["data"] is not None
        assert final_result["headers"] is not None
        assert final_result["rows"] == 3
        assert final_result["columns"] == 3

        # メタデータ統合確認
        metadata = final_result["metadata"]
        assert metadata["has_header"] is True
        assert metadata["headers"] == ["Name", "Age", "Department"]
        assert "processing_timestamp" in metadata
        assert "performance_metrics" in metadata

        # 冗長処理削除確認
        assert stage_result.redundant_metadata_operations == 0
        assert stage_result.metadata_consolidation_ratio >= 0.6

        # 結果検証機能確認
        context = stage_result.processing_context
        assert context.result_validated is True
        assert context.integrity_checked is True

        # エンドツーエンド最適化確認
        assert stage_result.end_to_end_optimization_applied is True
        assert stage_result.total_pipeline_efficiency >= 0.75

    @pytest.mark.performance
    def test_unified_pipeline_performance_comparison(self):
        """統合パイプライン性能比較テスト

        RED: 性能比較機能が存在しないため失敗する
        期待動作:
        - 5段階 vs 3段階パイプライン性能比較
        - 処理時間削減効果測定
        - メモリ使用量改善測定
        - 重複処理排除効果確認
        """
        # テストファイル作成
        test_file = self.create_test_excel_file("performance_comparison.xlsx")

        # 統合パイプライン初期化
        unified_pipeline = UnifiedProcessingPipeline(
            excel_reader=self.mock_excel_reader,
            data_converter=self.mock_data_converter,
            range_parser=self.mock_range_parser,
            enable_performance_benchmarking=True,
        )

        # 処理オプション設定
        processing_options = {
            "sheet_name": "Sheet1",
            "header_row": 0,
            "range_spec": "A1:D5",
            "enable_comparison_mode": True,
        }

        # 性能比較実行
        comparison_result = unified_pipeline.compare_pipeline_performance(
            file_path=test_file,
            processing_options=processing_options,
            comparison_iterations=3,
        )

        # 比較結果検証
        assert comparison_result["comparison_success"] is True
        assert "five_stage_metrics" in comparison_result
        assert "three_stage_metrics" in comparison_result
        assert "improvement_analysis" in comparison_result

        # 5段階パイプライン結果
        five_stage = comparison_result["five_stage_metrics"]
        assert five_stage["total_processing_time"] > 0
        assert five_stage["memory_peak_usage"] > 0
        assert five_stage["intermediate_objects_created"] >= 5

        # 3段階パイプライン結果
        three_stage = comparison_result["three_stage_metrics"]
        assert three_stage["total_processing_time"] > 0
        assert three_stage["memory_peak_usage"] > 0
        assert three_stage["intermediate_objects_created"] <= 3

        # 改善効果分析
        improvement = comparison_result["improvement_analysis"]
        assert improvement["processing_time_reduction"] >= 0.25  # 25%以上削減
        assert improvement["memory_usage_reduction"] >= 0.20  # 20%以上削減
        assert improvement["intermediate_objects_reduction"] >= 0.40  # 40%以上削減
        assert improvement["duplicate_operations_eliminated"] >= 3

        # 品質保証確認
        assert improvement["data_integrity_maintained"] is True
        assert improvement["functionality_preserved"] is True
        assert improvement["backward_compatibility"] is True

        print(
            f"Performance improvement: {improvement['processing_time_reduction']:.1%}"
        )
        print(f"Memory reduction: {improvement['memory_usage_reduction']:.1%}")

    @pytest.mark.performance
    def test_unified_pipeline_error_handling_integration(self):
        """統合パイプライン統合エラーハンドリングテスト

        RED: 統合エラーハンドリング機能が存在しないため失敗する
        期待動作:
        - 3段階統合エラーハンドリング
        - エラー伝播最適化
        - 段階横断エラー回復
        - エラーコンテキスト統合
        """
        # 不正なテストファイル作成
        invalid_file = self.temp_dir / "invalid_test.xlsx"
        invalid_file.write_text("invalid excel content")

        # 統合パイプライン初期化
        unified_pipeline = UnifiedProcessingPipeline(
            excel_reader=self.mock_excel_reader,
            data_converter=self.mock_data_converter,
            range_parser=self.mock_range_parser,
            security_validator=self.mock_security_validator,
            error_handler=self.mock_error_handler,
            enable_integrated_error_handling=True,
            enable_cross_stage_error_recovery=True,
        )

        # エラー発生条件設定
        error_scenarios = [
            {"sheet_name": "NonExistentSheet"},  # Stage 1エラー
            {"header_row": 999},  # Stage 2エラー
            {"range_spec": "ZZ1:ZZ999"},  # Stage 3エラー
        ]

        for _i, scenario in enumerate(error_scenarios):
            # エラーシナリオ実行
            result = unified_pipeline.process_excel_file(
                file_path=invalid_file, **scenario
            )

            # エラーハンドリング結果検証
            assert result["success"] is False
            assert "error" in result
            assert "integrated_error_handling" in result

            # 統合エラー情報確認
            error_info = result["integrated_error_handling"]
            assert error_info["error_stage_detected"] in [
                "stage_1",
                "stage_2",
                "stage_3",
            ]
            assert error_info["cross_stage_recovery_attempted"] is True
            assert error_info["error_context_integrated"] is True

            # エラー伝播最適化確認
            assert error_info["error_propagation_optimized"] is True
            assert error_info["unnecessary_stage_executions_prevented"] >= 1

            # エラー回復試行確認
            recovery_info = error_info["recovery_attempts"]
            assert len(recovery_info) >= 1
            assert any(
                attempt["stage"] == error_info["error_stage_detected"]
                for attempt in recovery_info
            )

    @pytest.mark.performance
    def test_unified_pipeline_backward_compatibility(self):
        """統合パイプライン後方互換性テスト

        RED: 後方互換性機能が存在しないため失敗する
        期待動作:
        - 既存5段階パイプラインAPI完全互換
        - 結果形式完全保持
        - 機能動作一致性保証
        - 移行支援機能
        """
        # テストファイル作成
        test_file = self.create_test_excel_file("compatibility_test.xlsx")

        # 統合パイプライン初期化（互換モード）
        unified_pipeline = UnifiedProcessingPipeline(
            excel_reader=self.mock_excel_reader,
            data_converter=self.mock_data_converter,
            range_parser=self.mock_range_parser,
            enable_backward_compatibility=True,
            compatibility_validation=True,
        )

        # 既存APIでの処理実行
        legacy_options = {
            "sheet_name": "Sheet1",
            "sheet_index": None,
            "range_spec": "A1:D4",
            "header_row": 0,
            "skip_rows": "1",
            "merge_mode": "expand",
        }

        # 互換性モードでの実行
        result = unified_pipeline.process_excel_file(
            file_path=test_file, **legacy_options
        )

        # 基本結果形式確認
        assert result["success"] is True
        assert result["data"] is not None
        assert result["rows"] >= 0
        assert result["columns"] >= 0
        assert result["headers"] is not None
        assert result["has_header"] is not None
        assert "metadata" in result

        # 完全互換性確認
        assert "range" in result  # 既存フィールド保持
        assert "skip_rows" in result if legacy_options.get("skip_rows") else True
        assert (
            "header_row" in result
            if legacy_options.get("header_row") is not None
            else True
        )
        assert "merge_mode" in result if legacy_options.get("merge_mode") else True

        # メタデータ互換性確認
        metadata = result["metadata"]
        assert "has_header" in metadata
        assert "headers" in metadata
        assert "workbook_info" in metadata
        assert "processing_timestamp" in metadata

        # 互換性検証結果確認
        assert "compatibility_validation" in result
        compatibility = result["compatibility_validation"]
        assert compatibility["api_compatibility_score"] >= 0.95  # 95%以上互換
        assert compatibility["result_format_compatibility"] is True
        assert compatibility["functionality_parity"] is True

        # 移行支援情報確認
        assert "migration_assistance" in result
        migration = result["migration_assistance"]
        assert migration["performance_improvement_available"] is True
        assert migration["optimization_recommendations"] is not None
        assert len(migration["optimization_recommendations"]) >= 2

        print(f"API compatibility: {compatibility['api_compatibility_score']:.1%}")
