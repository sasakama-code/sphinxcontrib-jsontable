"""
Excel Utilities Coverage Tests - ユーティリティ機能と後方互換性の包括的テスト

CLAUDE.md Code Excellence 準拠:
- TDD First: ユーティリティ機能の品質保証
- 単一責任: ユーティリティ機能のみをテスト
- 防御的プログラミング: エラーケースの徹底検証
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pandas as pd

from sphinxcontrib.jsontable.facade.excel_utilities import ExcelUtilities
from sphinxcontrib.jsontable.errors.excel_errors import ExcelProcessingError


class TestExcelUtilitiesInit:
    """初期化のテスト"""
    
    def test_init_required_components(self):
        """必須コンポーネントでの初期化"""
        excel_reader = Mock()
        data_converter = Mock()
        
        utilities = ExcelUtilities(
            excel_reader=excel_reader,
            data_converter=data_converter
        )
        
        assert utilities.excel_reader == excel_reader
        assert utilities.data_converter == data_converter
        assert utilities.error_handler is None
        assert utilities.enable_error_handling is True
    
    def test_init_with_error_handler(self):
        """エラーハンドラ付きの初期化"""
        excel_reader = Mock()
        data_converter = Mock()
        error_handler = Mock()
        
        utilities = ExcelUtilities(
            excel_reader=excel_reader,
            data_converter=data_converter,
            error_handler=error_handler,
            enable_error_handling=False
        )
        
        assert utilities.error_handler == error_handler
        assert utilities.enable_error_handling is False


class TestExcelUtilitiesValidation:
    """ファイル検証機能のテスト"""
    
    def setup_method(self):
        self.excel_reader = Mock()
        self.data_converter = Mock()
        self.utilities = ExcelUtilities(
            excel_reader=self.excel_reader,
            data_converter=self.data_converter
        )
    
    def test_validate_excel_file_success(self):
        """Excelファイル検証成功"""
        file_path = Path("test.xlsx")
        
        # モック設定
        mock_workbook_info = {
            "file_exists": True,
            "file_size": 1024,
            "sheet_count": 3,
            "sheet_names": ["Sheet1", "Sheet2", "Sheet3"],
            "readable": True
        }
        
        with patch.object(self.utilities, '_get_file_info') as mock_get_info:
            mock_get_info.return_value = mock_workbook_info
            
            result = self.utilities.validate_excel_file(file_path)
            
            assert result["file_exists"] is True
            assert result["readable"] is True
            assert result["sheet_count"] == 3
            assert "Sheet1" in result["sheet_names"]
    
    def test_validate_excel_file_not_found(self):
        """存在しないファイルの検証"""
        file_path = Path("nonexistent.xlsx")
        
        with patch.object(self.utilities, '_get_file_info') as mock_get_info:
            mock_get_info.side_effect = FileNotFoundError("File not found")
            
            result = self.utilities.validate_excel_file(file_path)
            
            assert result["file_exists"] is False
            assert result["error"] == "File not found"
    
    def test_validate_excel_file_permission_error(self):
        """権限エラーのファイル検証"""
        file_path = Path("restricted.xlsx")
        
        with patch.object(self.utilities, '_get_file_info') as mock_get_info:
            mock_get_info.side_effect = PermissionError("Permission denied")
            
            result = self.utilities.validate_excel_file(file_path)
            
            assert result["readable"] is False
            assert "Permission denied" in result["error"]
    
    def test_validate_excel_file_corrupted(self):
        """破損したExcelファイルの検証"""
        file_path = Path("corrupted.xlsx")
        
        with patch.object(self.utilities, '_get_file_info') as mock_get_info:
            mock_get_info.side_effect = Exception("File is corrupted")
            
            result = self.utilities.validate_excel_file(file_path)
            
            assert result["readable"] is False
            assert "corrupted" in result["error"].lower()


class TestExcelUtilitiesSheetOperations:
    """シート操作のテスト"""
    
    def setup_method(self):
        self.excel_reader = Mock()
        self.data_converter = Mock()
        self.utilities = ExcelUtilities(
            excel_reader=self.excel_reader,
            data_converter=self.data_converter
        )
    
    def test_get_sheet_names_success(self):
        """シート名取得成功"""
        file_path = Path("test.xlsx")
        expected_sheets = ["Sheet1", "Data", "Summary"]
        
        self.excel_reader.get_sheet_names.return_value = expected_sheets
        
        result = self.utilities.get_sheet_names(file_path)
        
        self.excel_reader.get_sheet_names.assert_called_once_with(file_path)
        assert result == expected_sheets
    
    def test_get_sheet_names_error(self):
        """シート名取得エラー"""
        file_path = Path("test.xlsx")
        
        self.excel_reader.get_sheet_names.side_effect = Exception("Cannot read file")
        
        with pytest.raises(Exception, match="Cannot read file"):
            self.utilities.get_sheet_names(file_path)
    
    def test_get_sheet_info_success(self):
        """シート情報取得成功"""
        file_path = Path("test.xlsx")
        sheet_name = "Data"
        
        mock_dataframe = pd.DataFrame({
            "A": [1, 2, 3],
            "B": ["x", "y", "z"]
        })
        
        self.excel_reader.read_excel.return_value = mock_dataframe
        
        result = self.utilities.get_sheet_info(file_path, sheet_name)
        
        assert result["sheet_name"] == sheet_name
        assert result["row_count"] == 3
        assert result["column_count"] == 2
        assert result["columns"] == ["A", "B"]
    
    def test_get_sheet_info_empty_sheet(self):
        """空のシート情報取得"""
        file_path = Path("test.xlsx")
        sheet_name = "Empty"
        
        empty_dataframe = pd.DataFrame()
        self.excel_reader.read_excel.return_value = empty_dataframe
        
        result = self.utilities.get_sheet_info(file_path, sheet_name)
        
        assert result["row_count"] == 0
        assert result["column_count"] == 0
        assert result["columns"] == []
    
    def test_get_sheet_info_with_nan_values(self):
        """NaN値を含むシート情報取得"""
        file_path = Path("test.xlsx")
        sheet_name = "DataWithNaN"
        
        dataframe_with_nan = pd.DataFrame({
            "A": [1, None, 3],
            "B": [None, "y", None]
        })
        
        self.excel_reader.read_excel.return_value = dataframe_with_nan
        
        result = self.utilities.get_sheet_info(file_path, sheet_name)
        
        assert result["row_count"] == 3
        assert result["column_count"] == 2
        assert result["has_missing_values"] is True


class TestExcelUtilitiesDataPreview:
    """データプレビュー機能のテスト"""
    
    def setup_method(self):
        self.excel_reader = Mock()
        self.data_converter = Mock()
        self.utilities = ExcelUtilities(
            excel_reader=self.excel_reader,
            data_converter=self.data_converter
        )
    
    def test_preview_data_default_rows(self):
        """デフォルト行数でのデータプレビュー"""
        file_path = Path("test.xlsx")
        
        large_dataframe = pd.DataFrame({
            "ID": list(range(1, 101)),
            "Name": [f"User{i}" for i in range(1, 101)]
        })
        
        self.excel_reader.read_excel.return_value = large_dataframe
        
        result = self.utilities.preview_data(file_path)
        
        # デフォルトで最初の5行が返されることを確認
        assert len(result) <= 5
        assert result[0]["ID"] == 1
        assert result[0]["Name"] == "User1"
    
    def test_preview_data_custom_rows(self):
        """カスタム行数でのデータプレビュー"""
        file_path = Path("test.xlsx")
        preview_rows = 10
        
        dataframe = pd.DataFrame({
            "A": list(range(1, 21)),
            "B": [f"Value{i}" for i in range(1, 21)]
        })
        
        self.excel_reader.read_excel.return_value = dataframe
        
        result = self.utilities.preview_data(file_path, rows=preview_rows)
        
        assert len(result) == preview_rows
    
    def test_preview_data_fewer_rows_than_requested(self):
        """要求より少ない行数のデータプレビュー"""
        file_path = Path("test.xlsx")
        preview_rows = 10
        
        small_dataframe = pd.DataFrame({
            "A": [1, 2, 3],
            "B": ["x", "y", "z"]
        })
        
        self.excel_reader.read_excel.return_value = small_dataframe
        
        result = self.utilities.preview_data(file_path, rows=preview_rows)
        
        # 実際のデータ行数が返されることを確認
        assert len(result) == 3
    
    def test_preview_data_with_sheet_name(self):
        """シート名指定でのデータプレビュー"""
        file_path = Path("test.xlsx")
        sheet_name = "SpecificSheet"
        
        dataframe = pd.DataFrame({"Test": [1, 2, 3]})
        self.excel_reader.read_excel.return_value = dataframe
        
        result = self.utilities.preview_data(file_path, sheet_name=sheet_name)
        
        self.excel_reader.read_excel.assert_called_once_with(
            file_path, sheet_name=sheet_name, range_info=None
        )
        assert len(result) == 3


class TestExcelUtilitiesFormatDetection:
    """フォーマット検出のテスト"""
    
    def setup_method(self):
        self.excel_reader = Mock()
        self.data_converter = Mock()
        self.utilities = ExcelUtilities(
            excel_reader=self.excel_reader,
            data_converter=self.data_converter
        )
    
    def test_detect_data_types_numeric(self):
        """数値データタイプの検出"""
        dataframe = pd.DataFrame({
            "Integer": [1, 2, 3],
            "Float": [1.1, 2.2, 3.3],
            "String": ["a", "b", "c"]
        })
        
        result = self.utilities.detect_data_types(dataframe)
        
        assert result["Integer"] == "integer"
        assert result["Float"] == "float"
        assert result["String"] == "string"
    
    def test_detect_data_types_datetime(self):
        """日時データタイプの検出"""
        dataframe = pd.DataFrame({
            "Date": pd.to_datetime(["2023-01-01", "2023-01-02"]),
            "Mixed": [1, "text"]
        })
        
        result = self.utilities.detect_data_types(dataframe)
        
        assert result["Date"] == "datetime"
        assert result["Mixed"] == "mixed"
    
    def test_detect_data_types_with_missing_values(self):
        """欠損値を含むデータタイプの検出"""
        dataframe = pd.DataFrame({
            "WithNaN": [1, None, 3],
            "AllNaN": [None, None, None]
        })
        
        result = self.utilities.detect_data_types(dataframe)
        
        assert result["WithNaN"] == "integer"  # NaN以外は整数
        assert result["AllNaN"] == "unknown"   # 全てNaN


class TestExcelUtilitiesBackwardCompatibility:
    """後方互換性のテスト"""
    
    def setup_method(self):
        self.excel_reader = Mock()
        self.data_converter = Mock()
        self.utilities = ExcelUtilities(
            excel_reader=self.excel_reader,
            data_converter=self.data_converter
        )
    
    def test_legacy_load_from_excel(self):
        """レガシーAPIでのExcel読み込み"""
        file_path = "test.xlsx"  # 文字列パス（レガシー）
        
        dataframe = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
        expected_json = [{"A": 1, "B": 3}, {"A": 2, "B": 4}]
        
        self.excel_reader.read_excel.return_value = dataframe
        self.data_converter.convert_dataframe_to_json.return_value = expected_json
        
        result = self.utilities.legacy_load_from_excel(file_path)
        
        # 文字列パスがPathオブジェクトに変換されることを確認
        call_args = self.excel_reader.read_excel.call_args[0]
        assert isinstance(call_args[0], Path)
        assert str(call_args[0]) == file_path
        
        assert result == expected_json
    
    def test_legacy_load_with_options(self):
        """オプション付きレガシーAPI"""
        file_path = "test.xlsx"
        options = {
            "sheet_name": "Data",
            "header_row": 1,
            "skip_rows": 2
        }
        
        dataframe = pd.DataFrame({"Name": ["Alice"], "Age": [30]})
        expected_json = [{"Name": "Alice", "Age": 30}]
        
        self.excel_reader.read_excel.return_value = dataframe
        self.data_converter.convert_dataframe_to_json.return_value = expected_json
        
        result = self.utilities.legacy_load_from_excel(file_path, **options)
        
        assert result == expected_json


class TestExcelUtilitiesErrorHandling:
    """エラーハンドリングのテスト"""
    
    def setup_method(self):
        self.excel_reader = Mock()
        self.data_converter = Mock()
        self.error_handler = Mock()
        
        self.utilities = ExcelUtilities(
            excel_reader=self.excel_reader,
            data_converter=self.data_converter,
            error_handler=self.error_handler,
            enable_error_handling=True
        )
    
    def test_error_handling_enabled(self):
        """エラーハンドリング有効時の処理"""
        file_path = Path("test.xlsx")
        error = ExcelProcessingError("Processing failed")
        
        self.excel_reader.read_excel.side_effect = error
        self.error_handler.handle_error.return_value = "Error handled gracefully"
        
        result = self.utilities.safe_load_data(file_path)
        
        self.error_handler.handle_error.assert_called_once_with(error)
        assert result == "Error handled gracefully"
    
    def test_error_handling_disabled(self):
        """エラーハンドリング無効時の処理"""
        utilities = ExcelUtilities(
            excel_reader=self.excel_reader,
            data_converter=self.data_converter,
            error_handler=self.error_handler,
            enable_error_handling=False
        )
        
        file_path = Path("test.xlsx")
        error = ExcelProcessingError("Processing failed")
        
        self.excel_reader.read_excel.side_effect = error
        
        with pytest.raises(ExcelProcessingError, match="Processing failed"):
            utilities.safe_load_data(file_path)
        
        # エラーハンドラは呼ばれない
        self.error_handler.handle_error.assert_not_called()
    
    def test_error_handler_none(self):
        """エラーハンドラがNoneの場合"""
        utilities = ExcelUtilities(
            excel_reader=self.excel_reader,
            data_converter=self.data_converter,
            error_handler=None,
            enable_error_handling=True
        )
        
        file_path = Path("test.xlsx")
        error = Exception("General error")
        
        self.excel_reader.read_excel.side_effect = error
        
        # エラーハンドラがNoneなので例外がそのまま発生
        with pytest.raises(Exception, match="General error"):
            utilities.safe_load_data(file_path)


class TestExcelUtilitiesPerformance:
    """パフォーマンス関連のテスト"""
    
    def setup_method(self):
        self.excel_reader = Mock()
        self.data_converter = Mock()
        self.utilities = ExcelUtilities(
            excel_reader=self.excel_reader,
            data_converter=self.data_converter
        )
    
    def test_large_file_handling(self):
        """大きなファイルの処理性能"""
        file_path = Path("large.xlsx")
        
        # 大きなデータセットをシミュレート
        large_dataframe = pd.DataFrame({
            "ID": list(range(1, 10001)),
            "Data": [f"Data{i}" for i in range(1, 10001)]
        })
        
        self.excel_reader.read_excel.return_value = large_dataframe
        self.data_converter.convert_dataframe_to_json.return_value = [
            {"ID": i, "Data": f"Data{i}"} for i in range(1, 10001)
        ]
        
        import time
        start_time = time.time()
        result = self.utilities.process_large_file(file_path)
        execution_time = time.time() - start_time
        
        assert len(result) == 10000
        assert execution_time < 10.0  # 10秒以内での完了を期待
    
    def test_memory_efficient_processing(self):
        """メモリ効率的な処理"""
        file_path = Path("test.xlsx")
        
        # メモリ使用量を意識した処理のテスト
        dataframe = pd.DataFrame({"A": [1, 2, 3]})
        self.excel_reader.read_excel.return_value = dataframe
        
        result = self.utilities.memory_efficient_load(file_path)
        
        # 基本的な動作確認
        assert result is not None