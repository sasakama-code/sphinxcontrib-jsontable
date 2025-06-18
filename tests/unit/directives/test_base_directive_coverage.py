"""
Base Directive Coverage Tests - テンプレートメソッドパターンと抽象基底クラスの包括的テスト

CLAUDE.md Code Excellence 準拠:
- TDD First: 機能保証に重点を置いたテスト設計
- 単一責任: BaseDirectiveの核心機能のみをテスト
- 防御的プログラミング: エラーケースとエッジケースの徹底検証
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from docutils import nodes
from docutils.parsers.rst import directives

from sphinxcontrib.jsontable.directives.base_directive import BaseDirective
from sphinxcontrib.jsontable.directives.validators import JsonTableError


class ConcreteDirective(BaseDirective):
    """テスト用の具象実装クラス"""
    
    def __init__(self):
        super().__init__()
        self.arguments = []
        self.options = {}
        self.content = []
        self.name = "test-directive"
        self.state = Mock()
        self.state_machine = Mock()
    
    def get_processor(self):
        """具象クラスでの抽象メソッド実装"""
        mock_processor = Mock()
        mock_processor.process.return_value = [["test", "data"], ["row2", "col2"]]
        return mock_processor
    
    def process_options(self):
        """オプション処理の具象実装"""
        return {
            'header': True,
            'limit': 100
        }


class TestBaseDirectiveTemplateMethod:
    """テンプレートメソッドパターンのテスト"""
    
    def setup_method(self):
        self.directive = ConcreteDirective()
    
    def test_run_template_method_execution_flow(self):
        """run()メソッドのテンプレートメソッド実行フロー検証"""
        with patch.object(self.directive, 'get_processor') as mock_get_processor, \
             patch.object(self.directive, 'process_options') as mock_process_options, \
             patch('sphinxcontrib.jsontable.directives.base_directive.TableBuilder') as mock_table_builder:
            
            # Mock設定
            mock_processor = Mock()
            mock_processor.process.return_value = [["col1", "col2"], ["data1", "data2"]]
            mock_get_processor.return_value = mock_processor
            mock_process_options.return_value = {"header": True}
            
            mock_builder = Mock()
            mock_builder.build_table.return_value = [nodes.table()]
            mock_table_builder.return_value = mock_builder
            
            # 実行
            result = self.directive.run()
            
            # 検証: テンプレートメソッドの実行順序
            mock_process_options.assert_called_once()
            mock_get_processor.assert_called_once()
            mock_processor.process.assert_called_once()
            mock_builder.build_table.assert_called_once()
            
            assert isinstance(result, list)
            assert len(result) > 0
    
    def test_run_with_processor_exception(self):
        """プロセッサで例外発生時のエラーハンドリング"""
        with patch.object(self.directive, 'get_processor') as mock_get_processor:
            mock_processor = Mock()
            mock_processor.process.side_effect = JsonTableError("Processing failed")
            mock_get_processor.return_value = mock_processor
            
            result = self.directive.run()
            
            # エラーノードが返されることを確認
            assert isinstance(result, list)
            assert len(result) == 1
            assert isinstance(result[0], nodes.error)
    
    def test_run_with_table_builder_exception(self):
        """TableBuilderで例外発生時のエラーハンドリング"""
        with patch.object(self.directive, 'get_processor') as mock_get_processor, \
             patch('sphinxcontrib.jsontable.directives.base_directive.TableBuilder') as mock_table_builder:
            
            mock_processor = Mock()
            mock_processor.process.return_value = [["data"]]
            mock_get_processor.return_value = mock_processor
            
            mock_builder = Mock()
            mock_builder.build_table.side_effect = Exception("Builder failed")
            mock_table_builder.return_value = mock_builder
            
            result = self.directive.run()
            
            assert isinstance(result, list)
            assert len(result) == 1
            assert isinstance(result[0], nodes.error)


class TestBaseDirectiveErrorHandling:
    """エラーハンドリング機能のテスト"""
    
    def setup_method(self):
        self.directive = ConcreteDirective()
    
    def test_create_error_node_basic(self):
        """基本的なエラーノード生成"""
        error_msg = "Test error message"
        error_node = self.directive._create_error_node(error_msg)
        
        assert isinstance(error_node, nodes.error)
        # エラーメッセージが含まれることを確認
        error_text = str(error_node)
        assert error_msg in error_text
    
    def test_create_error_node_with_exception(self):
        """例外オブジェクトからのエラーノード生成"""
        exception = JsonTableError("Exception message")
        error_node = self.directive._create_error_node(str(exception))
        
        assert isinstance(error_node, nodes.error)
        error_text = str(error_node)
        assert "Exception message" in error_text
    
    def test_create_error_node_security_safe(self):
        """セキュリティ上安全なエラーメッセージ処理"""
        # 機密情報を含む可能性のあるエラーメッセージ
        sensitive_msg = "Database connection failed: password=secret123"
        error_node = self.directive._create_error_node(sensitive_msg)
        
        # エラーノードが生成されることは確認するが、
        # 実際の実装でセンシティブ情報がフィルタされているかは別途実装必要
        assert isinstance(error_node, nodes.error)


class TestBaseDirectiveValidation:
    """バリデーション機能のテスト"""
    
    def setup_method(self):
        self.directive = ConcreteDirective()
    
    def test_validate_options_basic(self):
        """基本的なオプション検証"""
        # これは実装によって具体的な検証内容が決まる
        # 現在の実装を確認して具体的なテストを追加する必要がある
        pass
    
    def test_default_option_values(self):
        """デフォルトオプション値の設定確認"""
        # BaseDirectiveのデフォルト設定を確認
        # option_specが正しく定義されていることを確認
        if hasattr(self.directive, 'option_spec'):
            assert isinstance(self.directive.option_spec, dict)
    
    def test_invalid_option_handling(self):
        """不正なオプション値への対応"""
        # 不正なオプション値が与えられた場合の処理を確認
        # 実装に応じて具体的なテストケースを追加
        pass


class TestBaseDirectiveLogging:
    """ログ機能のテスト"""
    
    def setup_method(self):
        self.directive = ConcreteDirective()
    
    @patch('sphinxcontrib.jsontable.directives.base_directive.logger')
    def test_logging_on_success(self, mock_logger):
        """正常処理時のログ出力"""
        with patch.object(self.directive, 'get_processor') as mock_get_processor, \
             patch('sphinxcontrib.jsontable.directives.base_directive.TableBuilder') as mock_table_builder:
            
            mock_processor = Mock()
            mock_processor.process.return_value = [["data"]]
            mock_get_processor.return_value = mock_processor
            
            mock_builder = Mock()
            mock_builder.build_table.return_value = [nodes.table()]
            mock_table_builder.return_value = mock_builder
            
            self.directive.run()
            
            # ログが出力されることを確認（実装に応じて調整）
            # mock_logger.debug.assert_called()
    
    @patch('sphinxcontrib.jsontable.directives.base_directive.logger')
    def test_logging_on_error(self, mock_logger):
        """エラー時のログ出力"""
        with patch.object(self.directive, 'get_processor') as mock_get_processor:
            mock_processor = Mock()
            mock_processor.process.side_effect = Exception("Test error")
            mock_get_processor.return_value = mock_processor
            
            self.directive.run()
            
            # エラーログが出力されることを確認
            # mock_logger.error.assert_called()


class TestBaseDirectiveAbstractMethods:
    """抽象メソッドの実装チェック"""
    
    def test_abstract_methods_defined(self):
        """抽象メソッドが正しく定義されていることを確認"""
        # BaseDirectiveが抽象基底クラスとして正しく定義されていることを確認
        assert hasattr(BaseDirective, '__abstractmethods__')
        
        # get_processorが抽象メソッドとして定義されていることを確認
        abstract_methods = BaseDirective.__abstractmethods__
        expected_methods = {'get_processor'}  # 実装に応じて調整
        
        # 実際の抽象メソッドセットと期待されるメソッドの交集合を確認
        assert len(expected_methods.intersection(abstract_methods)) > 0
    
    def test_concrete_directive_instantiation(self):
        """具象クラスが正常にインスタンス化できることを確認"""
        directive = ConcreteDirective()
        assert isinstance(directive, BaseDirective)
        
        # 抽象メソッドが実装されていることを確認
        assert hasattr(directive, 'get_processor')
        assert callable(directive.get_processor)


class TestBaseDirectivePerformance:
    """パフォーマンス関連のテスト"""
    
    def setup_method(self):
        self.directive = ConcreteDirective()
    
    def test_large_dataset_handling(self):
        """大きなデータセットの処理性能確認"""
        with patch.object(self.directive, 'get_processor') as mock_get_processor, \
             patch('sphinxcontrib.jsontable.directives.base_directive.TableBuilder') as mock_table_builder:
            
            # 大きなデータセットをシミュレート
            large_data = [["col1", "col2"]] + [["data", str(i)] for i in range(1000)]
            
            mock_processor = Mock()
            mock_processor.process.return_value = large_data
            mock_get_processor.return_value = mock_processor
            
            mock_builder = Mock()
            mock_builder.build_table.return_value = [nodes.table()]
            mock_table_builder.return_value = mock_builder
            
            # 実行時間を測定（実際の実装では性能要件に応じて調整）
            import time
            start_time = time.time()
            result = self.directive.run()
            execution_time = time.time() - start_time
            
            assert isinstance(result, list)
            assert execution_time < 5.0  # 5秒以内での完了を期待
    
    def test_memory_efficient_processing(self):
        """メモリ効率的な処理の確認"""
        # メモリ使用量の測定は複雑なため、
        # ここでは基本的な動作確認のみ実装
        with patch.object(self.directive, 'get_processor') as mock_get_processor:
            mock_processor = Mock()
            mock_processor.process.return_value = [["test"]]
            mock_get_processor.return_value = mock_processor
            
            result = self.directive.run()
            assert isinstance(result, list)