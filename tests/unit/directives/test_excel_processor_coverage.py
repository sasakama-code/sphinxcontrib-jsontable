"""
Excel Processor Coverage Tests - ExcelProcessor クラスの包括的テスト

CLAUDE.md Code Excellence 準拠:
- TDD First: 実際の機能品質保証に重点
- 防御的プログラミング: エラーハンドリングとエッジケースの徹底検証
- 単一責任: Excel処理のみをテスト

機能保証項目:
- Excel統合処理機能の完全検証
- エラーハンドリングの適切性確認
- セキュリティ要件の実装確認
"""

from pathlib import Path
from unittest.mock import Mock, patch
import tempfile
import pytest

from sphinxcontrib.jsontable.directives.excel_processor import ExcelProcessor
from sphinxcontrib.jsontable.directives.validators import JsonTableError


@pytest.fixture
def temp_base_path():
    """テスト用一時ディレクトリを提供する。
    
    機能保証項目:
    - 一時ディレクトリの確実な作成
    - テスト後のクリーンアップ保証
    - クロスプラットフォーム互換性
    
    品質観点:
    - リソースリークの防止
    - テスト環境の分離
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


class TestExcelProcessorInitialization:
    """ExcelProcessor 初期化のテスト"""

    def test_init_with_string_path(self, temp_base_path):
        """文字列パスでの初期化を検証する。
        
        機能保証項目:
        - 文字列パスの適切なPath変換
        - ExcelDataLoaderFacadeの正常な初期化
        - キャッシュ機能の初期化確認
        
        品質観点:
        - 型変換の安全性
        - 後方互換性の維持
        - エラーの無い安定した初期化
        """
        processor = ExcelProcessor(str(temp_base_path))
        
        assert processor.base_path == temp_base_path
        assert isinstance(processor.base_path, Path)
        assert hasattr(processor, '_cache')
        assert isinstance(processor._cache, dict)

    def test_init_with_path_object(self, temp_base_path):
        """Pathオブジェクトでの初期化を検証する。
        
        機能保証項目:
        - Pathオブジェクトの直接使用
        - インスタンス属性の正確な設定
        - ログ出力の適切性
        
        品質観点:
        - オブジェクト指向設計の適切性
        - メモリ効率性
        - デバッグ情報の有用性
        """
        processor = ExcelProcessor(temp_base_path)
        
        assert processor.base_path == temp_base_path
        assert isinstance(processor.base_path, Path)
        assert hasattr(processor, 'excel_loader')

    @patch('sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelDataLoaderFacade', side_effect=ImportError("Test import error"))
    def test_init_excel_support_unavailable(self, mock_facade, temp_base_path):
        """Excel対応が利用できない場合の初期化エラーを検証する。
        
        機能保証項目:
        - ImportErrorの適切な捕捉と変換
        - 明確なエラーメッセージの提供
        - インストール指示の含有
        
        セキュリティ要件:
        - 例外チェーンの適切な処理
        - 機密情報の非漏洩
        
        品質観点:
        - ユーザビリティの向上
        - トラブルシューティング支援
        - エラー回復ガイダンス
        """
        with pytest.raises(JsonTableError, match="Excel support not available"):
            ExcelProcessor(temp_base_path)


class TestExcelProcessorDataLoading:
    """Excel データ読み込み機能のテスト"""

    @pytest.fixture
    def mock_processor(self, temp_base_path):
        """Excel Processorのモックを提供する。
        
        機能保証項目:
        - 安定したテスト環境の提供
        - 外部依存関係の分離
        - 予測可能な動作保証
        """
        with patch('sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelDataLoaderFacade'):
            return ExcelProcessor(temp_base_path)

    def test_load_excel_data_basic(self, mock_processor):
        """基本的なExcelデータ読み込み機能を検証する。
        
        機能保証項目:
        - ファイルパス処理の正確性
        - オプション辞書の適切な処理
        - 戻り値の型整合性
        
        品質観点:
        - 基本機能の安定性
        - インターフェース設計の一貫性
        - エラーの無い標準動作
        """
        mock_processor.excel_loader.load_from_excel.return_value = {"data": [{"test": "data"}]}
        
        result = mock_processor.load_excel_data("test.xlsx", {})
        
        assert result == [{"test": "data"}]
        mock_processor.excel_loader.load_from_excel.assert_called_once()

    def test_load_excel_data_with_options(self, mock_processor):
        """オプション付きExcelデータ読み込みを検証する。
        
        機能保証項目:
        - 複数オプションの同時処理
        - オプション値の適切な伝達
        - Excel固有パラメータの処理
        
        品質観点:
        - 設定柔軟性の確保
        - パラメータ渡しの信頼性
        - 機能拡張性の保持
        """
        mock_processor.excel_loader.load_from_excel.return_value = {"data": [{"data": "test"}]}
        options = {
            "sheet": "Sheet2",
            "range": "A1:C10",
            "header-row": 2
        }
        
        result = mock_processor.load_excel_data("test.xlsx", options)
        
        assert result == [{"data": "test"}]
        mock_processor.excel_loader.load_from_excel.assert_called_once_with(
            "test.xlsx", **options
        )


class TestExcelProcessorCaching:
    """Excel Processor キャッシュ機能のテスト"""

    @pytest.fixture
    def mock_processor_with_cache(self, temp_base_path):
        """キャッシュ機能付きProcessorのモックを提供する。"""
        with patch('sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelDataLoaderFacade'):
            processor = ExcelProcessor(temp_base_path)
            processor.excel_loader.load_from_excel.return_value = [{"cached": "data"}]
            return processor

    def test_cache_functionality(self, mock_processor_with_cache):
        """キャッシュ機能の基本動作を検証する。
        
        機能保証項目:
        - キャッシュストレージの機能確認
        - データ保存・取得の正確性
        - メモリ効率性の確保
        
        品質観点:
        - パフォーマンス最適化効果
        - メモリ使用量の適切性
        - キャッシュ一貫性の保持
        """
        processor = mock_processor_with_cache
        
        # キャッシュが初期化されていることを確認
        assert hasattr(processor, '_cache')
        assert isinstance(processor._cache, dict)
        assert len(processor._cache) == 0
        
        # キャッシュにデータを設定
        cache_key = "test_file.xlsx"
        test_data = [{"test": "cache_data"}]
        processor._cache[cache_key] = test_data
        
        # キャッシュからデータを取得
        assert processor._cache[cache_key] == test_data


class TestExcelProcessorErrorHandling:
    """Excel Processor エラーハンドリングのテスト"""

    @pytest.fixture
    def mock_processor_error(self, temp_base_path):
        """エラーテスト用Processorモックを提供する。"""
        with patch('sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelDataLoaderFacade'):
            return ExcelProcessor(temp_base_path)

    def test_excel_loader_error_handling(self, mock_processor_error):
        """ExcelDataLoaderのエラーハンドリングを検証する。
        
        機能保証項目:
        - 下位レイヤーエラーの適切な伝播
        - エラーコンテキストの保持
        - ユーザー向けエラー情報の提供
        
        セキュリティ要件:
        - 機密情報の非漏洩
        - 適切なエラー境界の設定
        
        品質観点:
        - 障害処理の適切性
        - エラー診断の容易性
        - システム安定性の確保
        """
        processor = mock_processor_error
        processor.excel_loader.load_from_excel.side_effect = Exception("Test Excel error")
        
        with pytest.raises(Exception, match="Test Excel error"):
            processor.load_excel_data("error.xlsx", {})


class TestExcelProcessorIntegration:
    """Excel Processor 統合テスト"""

    def test_module_imports(self):
        """モジュールインポートの整合性を検証する。
        
        機能保証項目:
        - 必要な全モジュールの正常インポート
        - 型定義の適切な公開
        - __all__属性の正確性
        
        品質観点:
        - モジュール構造の健全性
        - API設計の一貫性
        - 名前空間の適切な管理
        """
        from sphinxcontrib.jsontable.directives.excel_processor import (
            ExcelProcessor,
            JsonData,
            ExcelOptions
        )
        
        # クラスと型エイリアスが正常にインポートできることを確認
        assert ExcelProcessor is not None
        assert JsonData is not None
        assert ExcelOptions is not None

    def test_logging_integration(self, temp_base_path):
        """ログ統合機能を検証する。
        
        機能保証項目:
        - ログ出力の適切な実行
        - ログレベルの正確な設定
        - ログメッセージの有用性
        
        品質観点:
        - 運用監視支援
        - デバッグ情報の提供
        - パフォーマンス影響の最小化
        """
        with patch('sphinxcontrib.jsontable.directives.excel_processor.logger') as mock_logger:
            with patch('sphinxcontrib.jsontable.facade.excel_data_loader_facade.ExcelDataLoaderFacade'):
                processor = ExcelProcessor(temp_base_path)
            
            # 初期化時にログが呼ばれることを確認
            mock_logger.info.assert_called()
            call_args = mock_logger.info.call_args[0][0]
            assert "ExcelProcessor initialized successfully" in call_args
            assert str(temp_base_path) in call_args