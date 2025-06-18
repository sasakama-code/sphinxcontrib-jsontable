"""
Test suite for excel_processor.py module - TDD implementation

TDD for ExcelProcessor class
- Excelファイル読み込み統合機能
- シート名解決処理
- 範囲指定処理
- エラーハンドリング統合
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from sphinxcontrib.jsontable.directives.excel_processor import ExcelProcessor
from sphinxcontrib.jsontable.directives.validators import JsonTableError


class TestExcelProcessorInitialization:
    """ExcelProcessor初期化テスト"""
    
    def test_initialization_with_valid_path(self):
        """有効なパスでの初期化テスト"""
        base_path = Path("/test/path")
        processor = ExcelProcessor(base_path)
        
        assert processor.base_path == base_path
        assert hasattr(processor, 'excel_loader')
    
    def test_initialization_with_string_path(self):
        """文字列パスでの初期化テスト"""
        base_path_str = "/test/path"
        processor = ExcelProcessor(base_path_str)
        
        assert processor.base_path == Path(base_path_str)
    
    def test_initialization_sets_attributes(self):
        """必要な属性が設定されることをテスト"""
        processor = ExcelProcessor(Path("/test"))
        
        assert hasattr(processor, 'base_path')
        assert hasattr(processor, 'excel_loader')
        assert hasattr(processor, '_cache')


class TestExcelProcessorFilePathResolution:
    """ファイルパス解決テスト"""
    
    @pytest.fixture
    def processor(self):
        """テスト用プロセッサー"""
        return ExcelProcessor(Path("/test/base"))
    
    def test_resolve_absolute_path(self, processor):
        """絶対パスの解決テスト"""
        absolute_path = "/absolute/test.xlsx"
        resolved = processor._resolve_file_path(absolute_path)
        
        assert resolved == Path(absolute_path)
    
    def test_resolve_relative_path(self, processor):
        """相対パスの解決テスト"""
        relative_path = "data/test.xlsx"
        resolved = processor._resolve_file_path(relative_path)
        
        expected = processor.base_path / relative_path
        assert resolved == expected
    
    def test_path_security_validation(self, processor):
        """パスセキュリティ検証テスト"""
        malicious_path = "../../../etc/passwd"
        
        with pytest.raises(JsonTableError) as exc_info:
            processor._resolve_file_path(malicious_path)
        
        assert "security" in str(exc_info.value).lower()


class TestExcelProcessorDataLoading:
    """データ読み込みテスト"""
    
    @pytest.fixture
    def mock_processor(self):
        """モック済みプロセッサー"""
        processor = ExcelProcessor(Path("/test"))
        processor.excel_loader = Mock()
        return processor
    
    def test_load_excel_data_basic(self, mock_processor):
        """基本的なExcelデータ読み込みテスト"""
        # モックデータ設定
        mock_data = [
            ['Name', 'Age', 'City'],
            ['Alice', '25', 'Tokyo'],
            ['Bob', '30', 'Osaka']
        ]
        mock_processor.excel_loader.load_from_excel.return_value = {
            'data': mock_data,
            'meta': {'sheet': 'Sheet1'}
        }
        
        # テスト実行
        result = mock_processor.load_excel_data("test.xlsx", {})
        
        # 検証
        assert result == mock_data
        mock_processor.excel_loader.load_from_excel.assert_called_once()
    
    def test_load_excel_data_with_options(self, mock_processor):
        """オプション付きデータ読み込みテスト"""
        options = {
            'sheet': 'DataSheet',
            'range': 'A1:C10',
            'header_row': 0
        }
        
        mock_processor.excel_loader.load_from_excel.return_value = {
            'data': [['test', 'data']],
            'meta': {'sheet': 'DataSheet'}
        }
        
        mock_processor.load_excel_data("test.xlsx", options)
        
        # ローダーが適切な引数で呼ばれることを確認
        call_args = mock_processor.excel_loader.load_from_excel.call_args
        assert 'sheet' in str(call_args) or 'DataSheet' in str(call_args)
    
    def test_load_excel_data_error_handling(self, mock_processor):
        """エラーハンドリングテスト"""
        # ExcelLoaderでエラーが発生する場合
        mock_processor.excel_loader.load_from_excel.side_effect = FileNotFoundError("File not found")
        
        with pytest.raises(JsonTableError) as exc_info:
            mock_processor.load_excel_data("nonexistent.xlsx", {})
        
        assert "Excel file processing failed" in str(exc_info.value)


class TestExcelProcessorSheetResolution:
    """シート名解決テスト"""
    
    @pytest.fixture
    def mock_processor(self):
        """モック済みプロセッサー"""
        processor = ExcelProcessor(Path("/test"))
        processor.excel_loader = Mock()
        return processor
    
    def test_resolve_sheet_name_explicit(self, mock_processor):
        """明示的シート名解決テスト"""
        mock_processor.excel_loader.get_sheet_names.return_value = ['Sheet1', 'Data', 'Summary']
        
        result = mock_processor._resolve_sheet_name("/test.xlsx", "Data")
        
        assert result == "Data"
    
    def test_resolve_sheet_name_auto(self, mock_processor):
        """自動シート名解決テスト"""
        mock_processor.excel_loader.get_sheet_names.return_value = ['Sheet1', 'Data']
        
        result = mock_processor._resolve_sheet_name("/test.xlsx", None)
        
        assert result == 'Sheet1'  # 最初のシートを返す
    
    def test_resolve_sheet_name_invalid(self, mock_processor):
        """無効シート名エラーテスト"""
        mock_processor.excel_loader.get_sheet_names.return_value = ['Sheet1', 'Data']
        
        with pytest.raises(JsonTableError) as exc_info:
            mock_processor._resolve_sheet_name("/test.xlsx", "NonExistent")
        
        assert "Sheet 'NonExistent' not found" in str(exc_info.value)


class TestExcelProcessorCaching:
    """キャッシュ機能テスト"""
    
    @pytest.fixture
    def processor(self):
        """キャッシュテスト用プロセッサー"""
        processor = ExcelProcessor(Path("/test"))
        processor.excel_loader = Mock()
        return processor
    
    def test_cache_enabled_by_default(self, processor):
        """デフォルトでキャッシュが有効であることをテスト"""
        assert hasattr(processor, '_cache')
    
    def test_load_with_cache_hit(self, processor):
        """キャッシュヒット時のテスト"""
        # キャッシュにデータを設定
        test_options = {}
        cache_key = processor._generate_cache_key("test.xlsx", test_options)
        cached_data = [['cached', 'data']]
        processor._cache[cache_key] = cached_data
        
        # キャッシュ付き読み込み実行
        result = processor._load_with_cache("test.xlsx", test_options)
        
        # キャッシュからデータが返されることを確認
        assert result == cached_data
        # 実際のローダーは呼ばれないことを確認
        processor.excel_loader.load_from_excel.assert_not_called()
    
    def test_load_with_cache_miss(self, processor):
        """キャッシュミス時のテスト"""
        # ローダーの返り値を設定
        loader_data = [['new', 'data']]
        processor.excel_loader.load_from_excel.return_value = {
            'data': loader_data,
            'meta': {}
        }
        
        # キャッシュミス時の読み込み実行
        result = processor._load_with_cache("new_file.xlsx", {})
        
        # ローダーから新しいデータが返されることを確認
        assert result == loader_data
        # ローダーが呼ばれることを確認
        processor.excel_loader.load_from_excel.assert_called_once()


class TestExcelProcessorValidation:
    """入力検証テスト"""
    
    def test_validate_file_path_none(self):
        """Noneファイルパス検証テスト"""
        processor = ExcelProcessor(Path("/test"))
        
        with pytest.raises(JsonTableError) as exc_info:
            processor._validate_file_path(None)
        
        assert "File path cannot be None" in str(exc_info.value)
    
    def test_validate_file_path_empty(self):
        """空ファイルパス検証テスト"""
        processor = ExcelProcessor(Path("/test"))
        
        with pytest.raises(JsonTableError) as exc_info:
            processor._validate_file_path("")
        
        assert "File path cannot be empty" in str(exc_info.value)
    
    def test_validate_options_none(self):
        """Noneオプション検証テスト"""
        processor = ExcelProcessor(Path("/test"))
        
        # Noneオプションは空辞書として扱われる
        validated = processor._validate_options(None)
        assert validated == {}
    
    def test_validate_options_invalid_type(self):
        """無効オプション型検証テスト"""
        processor = ExcelProcessor(Path("/test"))
        
        with pytest.raises(JsonTableError) as exc_info:
            processor._validate_options("invalid_options")
        
        assert "Options must be a dictionary" in str(exc_info.value)


class TestExcelProcessorUtilityMethods:
    """ユーティリティメソッドテスト"""
    
    @pytest.fixture
    def processor(self):
        """テスト用プロセッサー"""
        return ExcelProcessor(Path("/test"))
    
    def test_generate_cache_key(self, processor):
        """キャッシュキー生成テスト"""
        file_path = "data/test.xlsx"
        options = {'sheet': 'Data', 'range': 'A1:C10'}
        
        cache_key = processor._generate_cache_key(file_path, options)
        
        # キーにファイルパスが含まれることを確認
        assert file_path in cache_key
        # キーが一意であることを確認（ハッシュベース）
        assert isinstance(cache_key, str)
        assert len(cache_key) > len(file_path)
    
    def test_generate_cache_key_empty_options(self, processor):
        """空オプションでのキャッシュキー生成テスト"""
        file_path = "test.xlsx"
        options = {}
        
        cache_key = processor._generate_cache_key(file_path, options)
        
        assert isinstance(cache_key, str)
        assert len(cache_key) > 0
    
    def test_clear_cache(self, processor):
        """キャッシュクリアテスト"""
        # キャッシュにデータを追加
        processor._cache['test_key'] = ['test_data']
        assert len(processor._cache) > 0
        
        # キャッシュクリア
        processor.clear_cache()
        
        # キャッシュが空になることを確認
        assert len(processor._cache) == 0


class TestExcelProcessorIntegration:
    """統合テスト"""
    
    def test_complete_workflow(self):
        """完全なワークフローテスト"""
        with patch('sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelDataLoaderFacade') as MockFacade:
            # モック設定
            mock_facade_instance = MockFacade.return_value
            mock_facade_instance.load_from_excel.return_value = {
                'data': [['Name', 'Age'], ['Alice', '25']],
                'meta': {'sheet': 'Sheet1'}
            }
            mock_facade_instance.get_sheet_names.return_value = ['Sheet1']
            
            # プロセッサー初期化
            processor = ExcelProcessor(Path("/test"))
            
            # データ読み込み実行
            result = processor.load_excel_data("data.xlsx", {'sheet': 'Sheet1'})
            
            # 結果検証
            assert isinstance(result, list)
            assert len(result) == 2
            assert result[0] == ['Name', 'Age']
            assert result[1] == ['Alice', '25']
    
    def test_error_recovery(self):
        """エラー回復テスト"""
        with patch('sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelDataLoaderFacade') as MockFacade:
            # エラーを発生させるモック設定
            mock_facade_instance = MockFacade.return_value
            mock_facade_instance.load_from_excel.side_effect = Exception("Mock error")
            
            processor = ExcelProcessor(Path("/test"))
            
            # エラーが適切にJsonTableErrorとしてラップされることを確認
            with pytest.raises(JsonTableError) as exc_info:
                processor.load_excel_data("error.xlsx", {})
            
            assert "Excel file processing failed" in str(exc_info.value)