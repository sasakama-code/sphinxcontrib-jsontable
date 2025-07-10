"""ヘッダー処理重複排除最適化テスト

TDD REDフェーズ: 失敗するテストを先に作成
Task 1.3.2: ヘッダー処理重複排除

現在の5段階パイプラインでのStage 4とStage 5での二重ヘッダー処理を排除:
- Stage 4: DataConverter内でのヘッダー検出処理
- Stage 5: _apply_header_row_processing()での追加ヘッダー処理
- Stage 5: _normalize_header_names()での正規化処理

統合後の期待効果:
- 単一パスヘッダー処理の実現
- 処理時間30-50%改善
- 中間データ生成削減
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock

import pandas as pd
import pytest

# REDフェーズ: 存在しないクラスをインポート（意図的にエラー）
try:
    from sphinxcontrib.jsontable.facade.optimized_header_processor import (
        HeaderProcessingMetrics,
        OptimizedHeaderProcessor,
        SinglePassHeaderResult,
    )

    OPTIMIZED_HEADER_AVAILABLE = True
except ImportError:
    OPTIMIZED_HEADER_AVAILABLE = False

from sphinxcontrib.jsontable.core.data_converter import IDataConverter
from sphinxcontrib.jsontable.core.excel_reader import IExcelReader
from sphinxcontrib.jsontable.core.range_parser import IRangeParser
from sphinxcontrib.jsontable.errors.error_handlers import IErrorHandler
from sphinxcontrib.jsontable.facade.excel_processing_pipeline import (
    ExcelProcessingPipeline,
)
from sphinxcontrib.jsontable.security.security_scanner import ISecurityValidator


class TestHeaderProcessingOptimization:
    """ヘッダー処理重複排除最適化テスト

    TDD REDフェーズ: 最適化クラスが存在しないため、
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

    def create_test_excel_file(self, filename: str = "test_header_opt.xlsx") -> Path:
        """テスト用Excelファイル作成

        Args:
            filename: ファイル名

        Returns:
            Path: 作成されたファイルのパス
        """
        file_path = self.temp_dir / filename

        # ヘッダー処理テスト用データ作成
        data = {
            "Employee ID": [1001, 1002, 1003, 1004, 1005],
            "Full Name": [
                "Alice Johnson",
                "Bob Smith",
                "Charlie Brown",
                "David Wilson",
                "Eve Davis",
            ],
            "Department Name": ["Engineering", "Sales", "Engineering", "HR", "Sales"],
            "Hire Date": [
                "2020-01-15",
                "2019-03-20",
                "2021-07-10",
                "2018-11-05",
                "2022-02-28",
            ],
            "Annual Salary": [75000, 65000, 80000, 55000, 70000],
        }

        df = pd.DataFrame(data)
        df.to_excel(file_path, index=False)

        return file_path

    @pytest.mark.performance
    def test_single_pass_header_processing(self):
        """単一パスヘッダー処理テスト

        RED: OptimizedHeaderProcessorクラスが存在しないため失敗する
        期待動作:
        - ヘッダー抽出・正規化・データ変換が単一パスで完了
        - 重複処理の完全排除
        - 処理ステップ数の削減（3ステップ→1ステップ）
        - 中間データ生成の排除
        """
        # テストファイル作成
        test_file = self.create_test_excel_file("single_pass_header.xlsx")

        # 最適化ヘッダープロセッサ初期化
        header_processor = OptimizedHeaderProcessor(
            excel_reader=self.mock_excel_reader,
            data_converter=self.mock_data_converter,
            enable_single_pass_processing=True,
            enable_duplicate_elimination=True,
            enable_performance_monitoring=True,
        )

        # ヘッダー処理オプション設定
        processing_options = {
            "header_row": 0,
            "enable_header_normalization": True,
            "enable_data_type_inference": True,
            "enable_process_tracking": True,
        }

        # 単一パスヘッダー処理実行
        result = header_processor.execute_single_pass_header_processing(
            file_path=test_file, **processing_options
        )

        # 基本結果検証
        assert isinstance(result, SinglePassHeaderResult)
        assert result.success is True
        assert result.headers is not None
        assert result.processed_data is not None
        assert result.has_header is True

        # 単一パス処理確認
        assert result.processing_steps == 1  # 単一ステップ
        assert result.duplicate_operations_eliminated >= 2  # 重複排除
        assert result.intermediate_data_objects == 0  # 中間データなし

        # ヘッダー正規化確認
        headers = result.headers
        assert len(headers) == 5
        assert "employee_id" in [h.lower().replace(" ", "_") for h in headers]
        assert "full_name" in [h.lower().replace(" ", "_") for h in headers]

        # パフォーマンスメトリクス確認
        metrics = result.performance_metrics
        assert isinstance(metrics, HeaderProcessingMetrics)
        assert metrics.total_processing_time > 0
        assert metrics.processing_efficiency >= 0.7  # 70%以上効率
        assert metrics.memory_efficiency >= 0.8  # 80%以上メモリ効率

        print(f"Processing efficiency: {metrics.processing_efficiency:.1%}")
        print(
            f"Duplicate operations eliminated: {result.duplicate_operations_eliminated}"
        )

    @pytest.mark.performance
    def test_header_processing_performance_improvement(self):
        """ヘッダー処理性能改善テスト

        RED: 性能比較機能が存在しないため失敗する
        期待動作:
        - 従来の二重処理 vs 単一パス処理の性能比較
        - 処理時間30-50%改善の確認
        - メモリ使用量削減の確認
        - 処理品質保証（結果一致性）
        """
        # テストファイル作成
        test_file = self.create_test_excel_file("performance_comparison.xlsx")

        # 従来パイプライン（二重ヘッダー処理）
        legacy_pipeline = ExcelProcessingPipeline(
            excel_reader=self.mock_excel_reader,
            data_converter=self.mock_data_converter,
            range_parser=self.mock_range_parser,
            security_validator=self.mock_security_validator,
            error_handler=self.mock_error_handler,
        )

        # 最適化ヘッダープロセッサ
        optimized_processor = OptimizedHeaderProcessor(
            excel_reader=self.mock_excel_reader,
            data_converter=self.mock_data_converter,
            enable_single_pass_processing=True,
            enable_performance_monitoring=True,
        )

        # 性能比較実行
        comparison_result = optimized_processor.compare_header_processing_performance(
            legacy_pipeline=legacy_pipeline,
            test_file=test_file,
            header_row=0,
            comparison_iterations=5,
        )

        # 比較結果検証
        assert comparison_result["comparison_success"] is True
        assert "legacy_metrics" in comparison_result
        assert "optimized_metrics" in comparison_result
        assert "improvement_analysis" in comparison_result

        # 従来処理結果
        legacy_metrics = comparison_result["legacy_metrics"]
        assert legacy_metrics["total_processing_time"] > 0
        assert legacy_metrics["header_processing_passes"] >= 2  # 二重処理
        assert legacy_metrics["duplicate_operations_count"] >= 2

        # 最適化処理結果
        optimized_metrics = comparison_result["optimized_metrics"]
        assert optimized_metrics["total_processing_time"] > 0
        assert optimized_metrics["header_processing_passes"] == 1  # 単一処理
        assert optimized_metrics["duplicate_operations_count"] == 0

        # 改善効果分析
        improvement = comparison_result["improvement_analysis"]
        assert improvement["processing_time_reduction"] >= 0.30  # 30%以上改善
        assert improvement["memory_usage_reduction"] >= 0.25  # 25%以上削減
        assert improvement["duplicate_operations_eliminated"] >= 2

        # 処理品質保証
        assert improvement["result_data_consistency"] is True
        assert improvement["header_normalization_consistency"] is True
        assert improvement["data_integrity_maintained"] is True

        print(
            f"Performance improvement: {improvement['processing_time_reduction']:.1%}"
        )
        print(f"Memory reduction: {improvement['memory_usage_reduction']:.1%}")

    @pytest.mark.performance
    def test_header_normalization_integration(self):
        """統合ヘッダー正規化処理テスト

        RED: 統合正規化機能が存在しないため失敗する
        期待動作:
        - ヘッダー抽出と正規化の統合処理
        - 空ヘッダー・重複ヘッダーの適切な処理
        - 正規化ルールの一貫性保証
        - カスタム正規化ルール対応
        """
        # テストファイル作成（問題のあるヘッダー含む）
        problematic_data = {
            "": ["Alice", "Bob", "Charlie"],  # 空ヘッダー
            "Name": ["Johnson", "Smith", "Brown"],  # 重複ヘッダー
            "Name ": ["Engineering", "Sales", "HR"],  # 重複ヘッダー（スペース付き）
            "Department/Team": ["Eng1", "Sales1", "HR1"],  # 特殊文字
            "Annual Salary ($)": [75000, 65000, 80000],  # 特殊文字・括弧
        }

        problematic_file = self.temp_dir / "problematic_headers.xlsx"
        df = pd.DataFrame(problematic_data)
        df.to_excel(problematic_file, index=False)

        # 統合ヘッダープロセッサ初期化
        header_processor = OptimizedHeaderProcessor(
            excel_reader=self.mock_excel_reader,
            data_converter=self.mock_data_converter,
            enable_advanced_normalization=True,
            enable_duplicate_resolution=True,
        )

        # カスタム正規化ルール設定
        normalization_rules = {
            "empty_header_prefix": "column",
            "duplicate_header_suffix": True,
            "special_char_replacement": "_",
            "case_conversion": "snake_case",
            "max_header_length": 50,
        }

        # 統合正規化処理実行
        result = header_processor.execute_integrated_header_normalization(
            file_path=problematic_file,
            header_row=0,
            normalization_rules=normalization_rules,
        )

        # 正規化結果検証
        assert result.success is True
        assert result.headers is not None
        assert len(result.headers) == 5

        # 正規化ルール適用確認
        headers = result.headers
        assert "column_1" in headers  # 空ヘッダー処理
        assert "name" in headers
        assert "name_2" in headers  # 重複解決
        assert "department_team" in headers  # 特殊文字処理
        assert "annual_salary" in headers  # 括弧・特殊文字処理

        # 正規化統計確認
        stats = result.normalization_statistics
        assert stats["empty_headers_resolved"] == 1
        assert stats["duplicate_headers_resolved"] == 1
        assert stats["special_chars_replaced"] >= 3
        assert stats["case_conversions_applied"] >= 4

        # 品質保証確認
        assert result.data_integrity_maintained is True
        assert result.column_count_preserved is True
        assert result.data_mapping_consistent is True

        print(f"Headers normalized: {', '.join(headers)}")
        print(f"Duplicate headers resolved: {stats['duplicate_headers_resolved']}")

    @pytest.mark.performance
    def test_legacy_pipeline_duplication_analysis(self):
        """従来パイプライン重複処理分析テスト

        RED: 重複分析機能が存在しないため失敗する
        期待動作:
        - ExcelProcessingPipelineでの重複処理の詳細分析
        - Stage 4とStage 5でのヘッダー処理重複の定量化
        - 重複排除可能性の評価
        - 最適化効果の予測
        """
        # テストファイル作成
        test_file = self.create_test_excel_file("duplication_analysis.xlsx")

        # 重複分析プロセッサ初期化
        duplication_analyzer = OptimizedHeaderProcessor(
            excel_reader=self.mock_excel_reader,
            data_converter=self.mock_data_converter,
            enable_duplication_analysis=True,
            enable_processing_tracing=True,
        )

        # 従来パイプライン重複分析実行
        analysis_result = duplication_analyzer.analyze_legacy_pipeline_duplication(
            pipeline_class=ExcelProcessingPipeline,
            test_file=test_file,
            processing_options={"header_row": 0, "enable_detailed_tracing": True},
        )

        # 重複分析結果検証
        assert analysis_result["analysis_success"] is True
        assert "duplication_details" in analysis_result
        assert "optimization_potential" in analysis_result

        # 重複処理詳細確認
        duplication = analysis_result["duplication_details"]
        assert duplication["stage_4_header_operations"] >= 1  # Stage 4でのヘッダー処理
        assert duplication["stage_5_header_operations"] >= 2  # Stage 5での重複処理
        assert duplication["total_duplicate_operations"] >= 2

        # 具体的重複箇所確認
        duplicate_operations = duplication["duplicate_operation_types"]
        assert "header_extraction" in duplicate_operations
        assert "header_normalization" in duplicate_operations
        assert "data_type_inference" in duplicate_operations

        # 最適化可能性評価
        optimization = analysis_result["optimization_potential"]
        assert optimization["processing_time_savings"] >= 0.30  # 30%以上削減可能
        assert optimization["memory_usage_savings"] >= 0.25  # 25%以上削減可能
        assert optimization["complexity_reduction"] >= 0.40  # 40%以上複雑性削減

        # 重複排除戦略確認
        strategy = optimization["elimination_strategy"]
        assert strategy["unified_processing_approach"] is True
        assert strategy["single_pass_processing"] is True
        assert strategy["intermediate_data_elimination"] is True

        print(
            f"Duplicate operations found: {duplication['total_duplicate_operations']}"
        )
        print(f"Potential time savings: {optimization['processing_time_savings']:.1%}")

    @pytest.mark.performance
    def test_optimized_pipeline_integration(self):
        """最適化パイプライン統合テスト

        RED: 統合最適化パイプラインが存在しないため失敗する
        期待動作:
        - ExcelProcessingPipelineへの最適化統合
        - 既存API完全互換性保証
        - 後方互換性維持
        - 段階的最適化移行サポート
        """
        # テストファイル作成
        test_file = self.create_test_excel_file("integration_test.xlsx")

        # 最適化統合パイプライン初期化
        optimized_pipeline = OptimizedHeaderProcessor.create_integrated_pipeline(
            excel_reader=self.mock_excel_reader,
            data_converter=self.mock_data_converter,
            range_parser=self.mock_range_parser,
            security_validator=self.mock_security_validator,
            error_handler=self.mock_error_handler,
            enable_header_optimization=True,
            maintain_backward_compatibility=True,
        )

        # 従来API互換性確認
        legacy_result = optimized_pipeline.process_excel_file(
            file_path=test_file, sheet_name="Sheet1", header_row=0, range_spec="A1:E6"
        )

        # 基本結果形式確認（従来と同じ）
        assert legacy_result["success"] is True
        assert legacy_result["data"] is not None
        assert legacy_result["headers"] is not None
        assert legacy_result["has_header"] is True
        assert "metadata" in legacy_result

        # 最適化情報追加確認
        optimization_info = legacy_result.get("optimization_info", {})
        assert optimization_info.get("header_processing_optimized") is True
        assert optimization_info.get("duplicate_operations_eliminated") >= 2
        assert optimization_info.get("processing_efficiency_gain") >= 0.30

        # 後方互換性確認
        compatibility = legacy_result.get("compatibility_validation", {})
        assert compatibility.get("api_compatibility_score", 0) >= 0.98  # 98%以上互換
        assert compatibility.get("result_format_consistency") is True
        assert compatibility.get("behavior_consistency") is True

        # 段階的移行サポート確認
        migration_support = optimization_info.get("migration_assistance", {})
        assert migration_support.get("optimization_enabled") is True
        assert migration_support.get("performance_improvement_available") is True
        assert migration_support.get("rollback_capability") is True

        print(
            f"API compatibility: {compatibility.get('api_compatibility_score', 0):.1%}"
        )
        print(
            f"Performance gain: {optimization_info.get('processing_efficiency_gain', 0):.1%}"
        )
