"""
機能保証テスト for ExcelProcessingPipeline class.

このモジュールは ExcelProcessingPipeline の5段階処理パイプラインの包括的なテストを提供し、
セキュリティ検証、範囲解析、ファイル読み込み、データ変換、結果統合の
品質保証を行います。単なるカバレッジ向上ではなく、実際の機能品質保証に重点を置きます。
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
import pandas as pd

from sphinxcontrib.jsontable.facade.excel_processing_pipeline import (
    ExcelProcessingPipeline,
    ProcessingError,
    SecurityError
)


class TestExcelProcessingPipelineInitialization:
    """
    ExcelProcessingPipelineの初期化機能の品質保証テスト.
    
    パイプラインコンポーネントの適切な初期化、
    設定オプションの正確な適用を検証します。
    """
    
    @pytest.fixture
    def mock_components(self):
        """パイプラインコンポーネントのモックを作成する。"""
        components = {
            'excel_reader': Mock(),
            'data_converter': Mock(),
            'range_parser': Mock(),
            'security_validator': Mock(),
            'error_handler': Mock()
        }
        return components
    
    def test_pipeline_initialization_with_all_components(self, mock_components):
        """
        全コンポーネント付きパイプラインの初期化を検証する。
        
        機能保証項目:
        - 全コンポーネントの適切な設定
        - 設定オプションの正確な適用
        - 依存性注入の確実な実行
        
        品質保証の重要性:
        - アーキテクチャの健全性確保
        - コンポーネント間の整合性保証
        - 設定の一貫性確認
        """
        pipeline = ExcelProcessingPipeline(
            excel_reader=mock_components['excel_reader'],
            data_converter=mock_components['data_converter'],
            range_parser=mock_components['range_parser'],
            security_validator=mock_components['security_validator'],
            error_handler=mock_components['error_handler'],
            enable_security=True,
            enable_error_handling=True
        )
        
        # コンポーネントの設定確認
        assert pipeline.excel_reader == mock_components['excel_reader']
        assert pipeline.data_converter == mock_components['data_converter']
        assert pipeline.range_parser == mock_components['range_parser']
        assert pipeline.security_validator == mock_components['security_validator']
        assert pipeline.error_handler == mock_components['error_handler']
        
        # 設定オプションの確認
        assert pipeline.enable_security is True
        assert pipeline.enable_error_handling is True
    
    def test_pipeline_initialization_with_optional_components_disabled(self):
        """
        オプションコンポーネント無効時の初期化を検証する。
        
        機能保証項目:
        - 必須コンポーネントのみでの正常動作
        - オプションコンポーネントの適切な無効化
        - セキュリティ・エラーハンドリングの無効化
        
        機能品質の観点:
        - 柔軟な設定オプション対応
        - 最小構成での動作保証
        - グレースフル・デグラデーション
        """
        excel_reader = Mock()
        data_converter = Mock()
        range_parser = Mock()
        
        pipeline = ExcelProcessingPipeline(
            excel_reader=excel_reader,
            data_converter=data_converter,
            range_parser=range_parser,
            security_validator=None,
            error_handler=None,
            enable_security=False,
            enable_error_handling=False
        )
        
        # 必須コンポーネントの確認
        assert pipeline.excel_reader == excel_reader
        assert pipeline.data_converter == data_converter
        assert pipeline.range_parser == range_parser
        
        # オプションコンポーネントの無効化確認
        assert pipeline.security_validator is None
        assert pipeline.error_handler is None
        assert pipeline.enable_security is False
        assert pipeline.enable_error_handling is False


class TestExcelProcessingPipelineSecurityStage:
    """
    ExcelProcessingPipelineのセキュリティ検証段階の品質保証テスト。
    
    Stage 1のセキュリティ検証機能の適切な動作、
    脅威検出、エラーハンドリングを検証します。
    """
    
    @pytest.fixture
    def pipeline_with_security(self):
        """セキュリティ検証付きパイプラインを作成する。"""
        mock_components = {
            'excel_reader': Mock(),
            'data_converter': Mock(),
            'range_parser': Mock(),
            'security_validator': Mock(),
            'error_handler': Mock()
        }
        
        return ExcelProcessingPipeline(
            excel_reader=mock_components['excel_reader'],
            data_converter=mock_components['data_converter'],
            range_parser=mock_components['range_parser'],
            security_validator=mock_components['security_validator'],
            error_handler=mock_components['error_handler'],
            enable_security=True,
            enable_error_handling=True
        ), mock_components
    
    def test_security_validation_success_safe_file(self, pipeline_with_security):
        """
        セキュリティ検証成功（安全ファイル）の処理を検証する。
        
        機能保証項目:
        - 安全ファイルの適切な通過
        - セキュリティバリデーターの正確な呼び出し
        - 検証結果の正しい判定
        
        セキュリティ品質の重要性:
        - 正当ファイルの適切な処理
        - セキュリティチェックの確実な実行
        - 偽陽性の防止
        """
        pipeline, components = pipeline_with_security
        
        # 安全なファイルのセキュリティ結果を設定
        components['security_validator'].validate_file.return_value = {
            "is_safe": True,
            "threats": []
        }
        
        # セキュリティ検証の実行（例外が発生しないことを確認）
        pipeline._perform_security_validation("/test/safe_file.xlsx", "test_context")
        
        # セキュリティバリデーターが呼び出されることを確認
        components['security_validator'].validate_file.assert_called_once_with(
            Path("/test/safe_file.xlsx")
        )
    
    def test_security_validation_threat_detection_and_blocking(self, pipeline_with_security):
        """
        セキュリティ脅威検出とブロック処理を検証する。
        
        機能保証項目:
        - 脅威の確実な検出
        - 危険ファイルの適切なブロック
        - 脅威情報の正確な報告
        
        セキュリティ要件:
        - 悪意のあるファイルの確実な拒否
        - 脅威の詳細な分析結果報告
        - セキュリティ例外の適切な発生
        """
        pipeline, components = pipeline_with_security
        
        # 脅威を含むファイルのセキュリティ結果を設定
        components['security_validator'].validate_file.return_value = {
            "is_safe": False,
            "threats": [
                {"type": "macro", "severity": "high"},
                {"type": "external_link", "severity": "medium"}
            ]
        }
        
        # セキュリティ脅威による例外発生を確認
        with pytest.raises(SecurityError) as exc_info:
            pipeline._perform_security_validation("/test/malicious_file.xlsx", "test_context")
        
        # 脅威情報がエラーメッセージに含まれることを確認
        error_message = str(exc_info.value)
        assert "Security threats detected" in error_message
        assert "macro" in error_message
        assert "external_link" in error_message
    
    def test_security_validation_disabled_bypass(self):
        """
        セキュリティ検証無効時のバイパス処理を検証する。
        
        機能保証項目:
        - セキュリティ無効時の適切なスキップ
        - バリデーター呼び出しの回避
        - 正常な処理継続
        
        機能品質の観点:
        - 設定に基づく適切な機能制御
        - パフォーマンスの最適化
        - 柔軟な運用オプション提供
        """
        mock_components = {
            'excel_reader': Mock(),
            'data_converter': Mock(),
            'range_parser': Mock(),
            'security_validator': Mock(),
            'error_handler': Mock()
        }
        
        pipeline = ExcelProcessingPipeline(
            excel_reader=mock_components['excel_reader'],
            data_converter=mock_components['data_converter'],
            range_parser=mock_components['range_parser'],
            security_validator=mock_components['security_validator'],
            error_handler=mock_components['error_handler'],
            enable_security=False,  # セキュリティ無効
            enable_error_handling=True
        )
        
        # セキュリティ検証の実行（バイパス）
        pipeline._perform_security_validation("/test/file.xlsx", "test_context")
        
        # セキュリティバリデーターが呼び出されないことを確認
        mock_components['security_validator'].validate_file.assert_not_called()


class TestExcelProcessingPipelineRangeStage:
    """
    ExcelProcessingPipelineの範囲解析段階の品質保証テスト。
    
    Stage 2の範囲指定解析機能の適切な動作、
    エラーハンドリング、オプション処理を検証します。
    """
    
    @pytest.fixture
    def pipeline_with_range_parser(self):
        """範囲解析付きパイプラインを作成する。"""
        mock_components = {
            'excel_reader': Mock(),
            'data_converter': Mock(),
            'range_parser': Mock(),
            'security_validator': None,
            'error_handler': Mock()
        }
        
        return ExcelProcessingPipeline(
            excel_reader=mock_components['excel_reader'],
            data_converter=mock_components['data_converter'],
            range_parser=mock_components['range_parser'],
            security_validator=None,
            error_handler=mock_components['error_handler'],
            enable_security=False,
            enable_error_handling=True
        ), mock_components
    
    def test_range_parsing_success_valid_specification(self, pipeline_with_range_parser):
        """
        有効な範囲指定の解析成功を検証する。
        
        機能保証項目:
        - 有効範囲指定の正確な解析
        - RangeInfoオブジェクトの適切な生成
        - 範囲パーサーの正確な呼び出し
        
        機能品質の重要性:
        - 範囲指定の正確な処理
        - ユーザー入力の適切な解釈
        - データ範囲の確実な制限
        """
        pipeline, components = pipeline_with_range_parser
        
        # 有効な範囲情報のモック設定
        mock_range_info = Mock()
        mock_range_info.original_spec = "A1:C10"
        mock_range_info.normalized_spec = "A1:C10"
        mock_range_info.row_count = 10
        mock_range_info.col_count = 3
        
        components['range_parser'].parse.return_value = mock_range_info
        
        # 範囲解析の実行
        result = pipeline._parse_range_specification("A1:C10", "test_context")
        
        # 結果の検証
        assert result == mock_range_info
        components['range_parser'].parse.assert_called_once_with("A1:C10")
    
    def test_range_parsing_error_handling_invalid_specification(self, pipeline_with_range_parser):
        """
        無効な範囲指定のエラーハンドリングを検証する。
        
        機能保証項目:
        - 無効範囲指定の適切な検出
        - エラーハンドラーの正確な呼び出し
        - ProcessingErrorの適切な発生
        
        機能品質の観点:
        - 入力検証の確実性
        - エラー処理の堅牢性
        - ユーザーフレンドリーなエラー報告
        """
        pipeline, components = pipeline_with_range_parser
        
        # 範囲解析エラーの設定
        parse_error = ValueError("Invalid range specification")
        components['range_parser'].parse.side_effect = parse_error
        
        # エラーハンドラーのモック設定
        components['error_handler'].create_error_response.return_value = "Range parsing error"
        
        # 範囲解析エラーの確認
        with pytest.raises(ProcessingError) as exc_info:
            pipeline._parse_range_specification("INVALID:RANGE", "test_context")
        
        # エラーメッセージの確認
        assert "Range parsing failed" in str(exc_info.value)
        
        # エラーハンドラーの呼び出し確認
        components['error_handler'].create_error_response.assert_called_once_with(
            parse_error, "test_context"
        )


class TestExcelProcessingPipelineFileReadingStage:
    """
    ExcelProcessingPipelineのファイル読み込み段階の品質保証テスト。
    
    Stage 3のExcelファイル読み込み機能の適切な動作、
    シート選択、エラーハンドリングを検証します。
    """
    
    @pytest.fixture
    def pipeline_with_excel_reader(self):
        """Excelリーダー付きパイプラインを作成する。"""
        mock_components = {
            'excel_reader': Mock(),
            'data_converter': Mock(),
            'range_parser': Mock(),
            'security_validator': None,
            'error_handler': Mock()
        }
        
        return ExcelProcessingPipeline(
            excel_reader=mock_components['excel_reader'],
            data_converter=mock_components['data_converter'],
            range_parser=mock_components['range_parser'],
            security_validator=None,
            error_handler=mock_components['error_handler'],
            enable_security=False,
            enable_error_handling=True
        ), mock_components
    
    def test_excel_file_reading_success_with_sheet_name(self, pipeline_with_excel_reader):
        """
        シート名指定でのExcelファイル読み込み成功を検証する。
        
        機能保証項目:
        - シート名による正確なシート選択
        - ファイル読み込みの確実な実行
        - 読み込み結果の適切な返却
        
        機能品質の重要性:
        - ユーザー指定の正確な処理
        - データアクセスの確実性
        - ファイル操作の安全性
        """
        pipeline, components = pipeline_with_excel_reader
        
        # 読み込み結果のモック設定
        mock_read_result = Mock()
        mock_read_result.dataframe = pd.DataFrame([["A", "B"], ["1", "2"]])
        mock_read_result.workbook_info = Mock()
        
        components['excel_reader'].read_workbook.return_value = mock_read_result
        
        # ファイル読み込みの実行
        result = pipeline._read_excel_file(
            "/test/file.xlsx", "Sheet1", None, "test_context"
        )
        
        # 結果の検証
        assert result == mock_read_result
        components['excel_reader'].read_workbook.assert_called_once_with(
            "/test/file.xlsx", sheet_name="Sheet1", sheet_index=None
        )
    
    def test_excel_file_reading_success_with_sheet_index(self, pipeline_with_excel_reader):
        """
        シートインデックス指定でのExcelファイル読み込み成功を検証する。
        
        機能保証項目:
        - シートインデックスによる正確なシート選択
        - インデックスベースアクセスの確実性
        - 読み込み結果の適切な返却
        
        機能品質の観点:
        - 柔軟なシート選択オプション
        - インデックスベース操作の正確性
        - 複数シート対応の確実性
        """
        pipeline, components = pipeline_with_excel_reader
        
        # 読み込み結果のモック設定
        mock_read_result = Mock()
        components['excel_reader'].read_workbook.return_value = mock_read_result
        
        # シートインデックス指定での読み込み
        result = pipeline._read_excel_file(
            "/test/file.xlsx", None, 1, "test_context"
        )
        
        # 結果の検証
        assert result == mock_read_result
        components['excel_reader'].read_workbook.assert_called_once_with(
            "/test/file.xlsx", sheet_name=None, sheet_index=1
        )
    
    def test_excel_file_reading_error_handling_file_not_found(self, pipeline_with_excel_reader):
        """
        ファイル未発見エラーのハンドリングを検証する。
        
        機能保証項目:
        - ファイルシステムエラーの適切な捕捉
        - エラーハンドラーの正確な呼び出し
        - ProcessingErrorの適切な発生
        
        機能品質の重要性:
        - ファイル操作エラーの堅牢な処理
        - ユーザーフレンドリーなエラー報告
        - システムの安定性維持
        """
        pipeline, components = pipeline_with_excel_reader
        
        # ファイル読み込みエラーの設定
        file_error = FileNotFoundError("Excel file not found")
        components['excel_reader'].read_workbook.side_effect = file_error
        
        # エラーハンドラーのモック設定
        components['error_handler'].create_error_response.return_value = "File reading error"
        
        # ファイル読み込みエラーの確認
        with pytest.raises(ProcessingError) as exc_info:
            pipeline._read_excel_file("/test/missing.xlsx", None, None, "test_context")
        
        # エラーメッセージの確認
        assert "File reading failed" in str(exc_info.value)
        
        # エラーハンドラーの呼び出し確認
        components['error_handler'].create_error_response.assert_called_once_with(
            file_error, "test_context"
        )


class TestExcelProcessingPipelineDataConversionStage:
    """
    ExcelProcessingPipelineのデータ変換段階の品質保証テスト。
    
    Stage 4のデータ変換機能の適切な動作、
    ヘッダー処理、エラーハンドリングを検証します。
    """
    
    @pytest.fixture
    def pipeline_with_data_converter(self):
        """データコンバーター付きパイプラインを作成する。"""
        mock_components = {
            'excel_reader': Mock(),
            'data_converter': Mock(),
            'range_parser': Mock(),
            'security_validator': None,
            'error_handler': Mock()
        }
        
        return ExcelProcessingPipeline(
            excel_reader=mock_components['excel_reader'],
            data_converter=mock_components['data_converter'],
            range_parser=mock_components['range_parser'],
            security_validator=None,
            error_handler=mock_components['error_handler'],
            enable_security=False,
            enable_error_handling=True
        ), mock_components
    
    def test_data_conversion_success_with_header_row(self, pipeline_with_data_converter):
        """
        ヘッダー行指定でのデータ変換成功を検証する。
        
        機能保証項目:
        - ヘッダー行の正確な処理
        - DataFrameからJSONへの適切な変換
        - 変換結果の正確な返却
        
        機能品質の重要性:
        - データ構造の正確な変換
        - ヘッダー情報の適切な処理
        - データ品質の保証
        """
        pipeline, components = pipeline_with_data_converter
        
        # 入力データとして使用するDataFrame
        test_dataframe = pd.DataFrame([
            ["Name", "Age", "City"],
            ["Alice", "25", "Tokyo"],
            ["Bob", "30", "Osaka"]
        ])
        
        # 変換結果のモック設定
        mock_conversion_result = Mock()
        mock_conversion_result.data = [
            {"Name": "Alice", "Age": "25", "City": "Tokyo"},
            {"Name": "Bob", "Age": "30", "City": "Osaka"}
        ]
        mock_conversion_result.has_header = True
        mock_conversion_result.headers = ["Name", "Age", "City"]
        
        components['data_converter'].convert_dataframe_to_json.return_value = mock_conversion_result
        
        # データ変換の実行
        result = pipeline._convert_data_to_json(test_dataframe, 0, "test_context")
        
        # 結果の検証
        assert result == mock_conversion_result
        components['data_converter'].convert_dataframe_to_json.assert_called_once_with(
            test_dataframe, header_row=0
        )
    
    def test_data_conversion_success_without_header(self, pipeline_with_data_converter):
        """
        ヘッダー行なしでのデータ変換成功を検証する。
        
        機能保証項目:
        - ヘッダーなしデータの適切な処理
        - 自動ヘッダー生成の確実性
        - 変換処理の柔軟性
        
        機能品質の観点:
        - 多様なデータ形式への対応
        - 自動処理機能の確実性
        - ユーザビリティの向上
        """
        pipeline, components = pipeline_with_data_converter
        
        # ヘッダーなしのDataFrame
        test_dataframe = pd.DataFrame([
            ["Alice", "25", "Tokyo"],
            ["Bob", "30", "Osaka"]
        ])
        
        # ヘッダーなし変換結果のモック
        mock_conversion_result = Mock()
        mock_conversion_result.data = [
            {"col_0": "Alice", "col_1": "25", "col_2": "Tokyo"},
            {"col_0": "Bob", "col_1": "30", "col_2": "Osaka"}
        ]
        mock_conversion_result.has_header = False
        mock_conversion_result.headers = ["col_0", "col_1", "col_2"]
        
        components['data_converter'].convert_dataframe_to_json.return_value = mock_conversion_result
        
        # ヘッダーなしでのデータ変換
        result = pipeline._convert_data_to_json(test_dataframe, None, "test_context")
        
        # 結果の検証
        assert result == mock_conversion_result
        components['data_converter'].convert_dataframe_to_json.assert_called_once_with(
            test_dataframe, header_row=None
        )
    
    def test_data_conversion_error_handling_invalid_data(self, pipeline_with_data_converter):
        """
        無効データでのデータ変換エラーハンドリングを検証する。
        
        機能保証項目:
        - 無効データの適切な検出
        - 変換エラーの確実な捕捉
        - ProcessingErrorの適切な発生
        
        機能品質の重要性:
        - データ品質の確実な検証
        - エラー処理の堅牢性
        - 適切な障害回復
        """
        pipeline, components = pipeline_with_data_converter
        
        # データ変換エラーの設定
        conversion_error = ValueError("Invalid DataFrame structure")
        components['data_converter'].convert_dataframe_to_json.side_effect = conversion_error
        
        # エラーハンドラーのモック設定
        components['error_handler'].create_error_response.return_value = "Conversion error"
        
        # データ変換エラーの確認
        test_dataframe = pd.DataFrame()  # 空のDataFrame
        
        with pytest.raises(ProcessingError) as exc_info:
            pipeline._convert_data_to_json(test_dataframe, None, "test_context")
        
        # エラーメッセージの確認
        assert "Data conversion failed" in str(exc_info.value)
        
        # エラーハンドラーの呼び出し確認
        components['error_handler'].create_error_response.assert_called_once_with(
            conversion_error, "test_context"
        )


class TestExcelProcessingPipelineResultIntegration:
    """
    ExcelProcessingPipelineの結果統合段階の品質保証テスト。
    
    Stage 5の結果統合機能の適切な動作、
    メタデータ生成、コンポーネント情報の構築を検証します。
    """
    
    @pytest.fixture
    def pipeline_for_integration(self):
        """結果統合テスト用パイプラインを作成する。"""
        mock_components = {
            'excel_reader': Mock(),
            'data_converter': Mock(),
            'range_parser': Mock(),
            'security_validator': None,
            'error_handler': Mock()
        }
        
        # コンポーネント名の設定
        mock_components['excel_reader'].__class__.__name__ = "MockExcelReader"
        mock_components['data_converter'].__class__.__name__ = "MockDataConverter"
        mock_components['range_parser'].__class__.__name__ = "MockRangeParser"
        
        return ExcelProcessingPipeline(
            excel_reader=mock_components['excel_reader'],
            data_converter=mock_components['data_converter'],
            range_parser=mock_components['range_parser'],
            security_validator=None,
            error_handler=mock_components['error_handler'],
            enable_security=False,
            enable_error_handling=True
        ), mock_components
    
    def test_result_integration_success_with_range_info(self, pipeline_for_integration):
        """
        範囲情報付き結果統合の成功を検証する。
        
        機能保証項目:
        - 変換結果とメタデータの適切な統合
        - 範囲情報の正確な追加
        - コンポーネント情報の確実な生成
        - タイムスタンプの適切な追加
        
        機能品質の重要性:
        - 包括的な結果情報の提供
        - トレーサビリティの確保
        - デバッグ情報の充実
        """
        pipeline, components = pipeline_for_integration
        
        # 変換結果のモック
        mock_conversion_result = Mock()
        mock_conversion_result.data = [{"name": "test", "value": 123}]
        mock_conversion_result.has_header = True
        mock_conversion_result.headers = ["name", "value"]
        
        # 読み込み結果のモック
        mock_read_result = Mock()
        mock_read_result.workbook_info = Mock()
        mock_read_result.workbook_info.to_dict.return_value = {
            "filename": "test.xlsx",
            "sheet_count": 3
        }
        
        # 範囲情報のモック
        mock_range_info = Mock()
        mock_range_info.original_spec = "A1:B10"
        mock_range_info.normalized_spec = "A1:B10"
        mock_range_info.row_count = 10
        mock_range_info.col_count = 2
        
        # 結果統合の実行
        with patch('pandas.Timestamp') as mock_timestamp:
            mock_timestamp.now.return_value.isoformat.return_value = "2023-01-01T12:00:00"
            
            result = pipeline._build_integrated_result(
                mock_conversion_result, mock_read_result, mock_range_info, "test_context"
            )
        
        # 結果構造の検証
        assert result["success"] is True
        assert result["data"] == [{"name": "test", "value": 123}]
        
        # メタデータの検証
        metadata = result["metadata"]
        assert metadata["has_header"] is True
        assert metadata["headers"] == ["name", "value"]
        assert metadata["workbook_info"] == {"filename": "test.xlsx", "sheet_count": 3}
        assert metadata["processing_timestamp"] == "2023-01-01T12:00:00"
        
        # 範囲情報の検証
        range_info = metadata["range_info"]
        assert range_info["original_spec"] == "A1:B10"
        assert range_info["normalized_spec"] == "A1:B10"
        assert range_info["row_count"] == 10
        assert range_info["col_count"] == 2
        
        # コンポーネント情報の検証
        components_info = result["components_used"]
        assert "excel_reader" in components_info
        assert "data_converter" in components_info
        assert "range_parser" in components_info
    
    def test_result_integration_success_without_range_info(self, pipeline_for_integration):
        """
        範囲情報なし結果統合の成功を検証する。
        
        機能保証項目:
        - 範囲情報なしでの適切な統合
        - 必須メタデータの確実な生成
        - 条件付き情報の適切な除外
        
        機能品質の観点:
        - 柔軟な統合処理対応
        - オプション情報の適切な処理
        - 最小構成での動作保証
        """
        pipeline, components = pipeline_for_integration
        
        # 変換結果のモック
        mock_conversion_result = Mock()
        mock_conversion_result.data = [{"col_0": "value"}]
        mock_conversion_result.has_header = False
        mock_conversion_result.headers = ["col_0"]
        
        # 読み込み結果のモック
        mock_read_result = Mock()
        mock_read_result.workbook_info = Mock()
        mock_read_result.workbook_info.to_dict.return_value = {"filename": "simple.xlsx"}
        
        # 範囲情報なしでの結果統合
        with patch('pandas.Timestamp') as mock_timestamp:
            mock_timestamp.now.return_value.isoformat.return_value = "2023-01-01T12:00:00"
            
            result = pipeline._build_integrated_result(
                mock_conversion_result, mock_read_result, None, "test_context"
            )
        
        # 結果構造の検証
        assert result["success"] is True
        assert result["data"] == [{"col_0": "value"}]
        
        # メタデータの検証
        metadata = result["metadata"]
        assert metadata["has_header"] is False
        assert metadata["headers"] == ["col_0"]
        assert metadata["workbook_info"] == {"filename": "simple.xlsx"}
        
        # 範囲情報が含まれていないことを確認
        assert "range_info" not in metadata
    
    def test_components_info_generation_comprehensive(self, pipeline_for_integration):
        """
        コンポーネント情報の包括的な生成を検証する。
        
        機能保証項目:
        - 全コンポーネントの名前取得
        - オプションコンポーネントの適切な処理
        - 情報の正確性と完全性
        
        機能品質の重要性:
        - トレーサビリティの完全性
        - デバッグ情報の充実
        - システム構成の透明性
        """
        pipeline, components = pipeline_for_integration
        
        # コンポーネント情報の取得
        components_info = pipeline._get_components_info()
        
        # 必須コンポーネントの確認
        assert "excel_reader" in components_info
        assert "data_converter" in components_info
        assert "range_parser" in components_info
        
        # オプションコンポーネントの確認
        assert components_info["security_validator"] is None
        assert "error_handler" in components_info