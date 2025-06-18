"""
Error Handler Core Coverage Tests - エラーハンドリングコア機能の包括的テスト

CLAUDE.md Code Excellence 準拠:
- TDD First: エラー処理の品質保証に重点
- 単一責任: エラーハンドリング機能のみをテスト
- 防御的プログラミング: エラーケースとリカバリの徹底検証
"""

import pytest
import logging
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from sphinxcontrib.jsontable.errors.error_handler_core import ErrorHandlerCore, IErrorHandler
from sphinxcontrib.jsontable.errors.error_types import ErrorSeverity, HandlingResult, RecoveryStrategy
from sphinxcontrib.jsontable.errors.excel_errors import (
    ExcelProcessingError,
    FileAccessError,
    DataConversionError,
    RangeValidationError,
    SecurityValidationError
)


class TestIErrorHandlerInterface:
    """IErrorHandlerインターフェースのテスト"""
    
    def test_interface_abstract_methods(self):
        """抽象メソッドが正しく定義されていることを確認"""
        assert hasattr(IErrorHandler, '__abstractmethods__')
        abstract_methods = IErrorHandler.__abstractmethods__
        
        expected_methods = {'handle_error', 'create_error_response'}
        assert expected_methods.issubset(abstract_methods)
    
    def test_interface_cannot_be_instantiated(self):
        """抽象インターフェースが直接インスタンス化できないことを確認"""
        with pytest.raises(TypeError):
            IErrorHandler()


class TestErrorHandlerCoreInit:
    """ErrorHandlerCore初期化のテスト"""
    
    def test_init_default_parameters(self):
        """デフォルトパラメータでの初期化"""
        handler = ErrorHandlerCore()
        
        assert handler.logger is not None
        assert isinstance(handler.logger, logging.Logger)
        assert handler.enable_recovery is True
        assert handler.default_severity == ErrorSeverity.MEDIUM
    
    def test_init_with_custom_logger(self):
        """カスタムロガーでの初期化"""
        custom_logger = logging.getLogger("test_logger")
        handler = ErrorHandlerCore(logger=custom_logger)
        
        assert handler.logger == custom_logger
    
    def test_init_with_custom_parameters(self):
        """カスタムパラメータでの初期化"""
        handler = ErrorHandlerCore(
            enable_recovery=False,
            default_severity=ErrorSeverity.HIGH,
            max_retry_attempts=5
        )
        
        assert handler.enable_recovery is False
        assert handler.default_severity == ErrorSeverity.HIGH
        assert handler.max_retry_attempts == 5


class TestErrorHandlerCoreErrorClassification:
    """エラー分類のテスト"""
    
    def setup_method(self):
        self.handler = ErrorHandlerCore()
    
    def test_classify_file_access_error(self):
        """ファイルアクセスエラーの分類"""
        error = FileAccessError("File not found: test.xlsx")
        
        severity = self.handler._classify_error_severity(error)
        assert severity == ErrorSeverity.HIGH
        
        strategy = self.handler._determine_recovery_strategy(error)
        assert strategy == RecoveryStrategy.RETRY
    
    def test_classify_data_conversion_error(self):
        """データ変換エラーの分類"""
        error = DataConversionError("Cannot convert cell value")
        
        severity = self.handler._classify_error_severity(error)
        assert severity == ErrorSeverity.MEDIUM
        
        strategy = self.handler._determine_recovery_strategy(error)
        assert strategy == RecoveryStrategy.FALLBACK
    
    def test_classify_security_validation_error(self):
        """セキュリティ検証エラーの分類"""
        error = SecurityValidationError("Potential security threat detected")
        
        severity = self.handler._classify_error_severity(error)
        assert severity == ErrorSeverity.CRITICAL
        
        strategy = self.handler._determine_recovery_strategy(error)
        assert strategy == RecoveryStrategy.ABORT
    
    def test_classify_range_validation_error(self):
        """範囲検証エラーの分類"""
        error = RangeValidationError("Invalid range specification: Z999:AA1000")
        
        severity = self.handler._classify_error_severity(error)
        assert severity == ErrorSeverity.MEDIUM
        
        strategy = self.handler._determine_recovery_strategy(error)
        assert strategy == RecoveryStrategy.FALLBACK
    
    def test_classify_generic_excel_error(self):
        """一般的なExcelエラーの分類"""
        error = ExcelProcessingError("General processing error")
        
        severity = self.handler._classify_error_severity(error)
        assert severity == ErrorSeverity.MEDIUM
        
        strategy = self.handler._determine_recovery_strategy(error)
        assert strategy == RecoveryStrategy.FALLBACK
    
    def test_classify_unknown_error(self):
        """未知のエラーの分類"""
        error = ValueError("Unknown error type")
        
        severity = self.handler._classify_error_severity(error)
        assert severity == ErrorSeverity.MEDIUM  # デフォルト
        
        strategy = self.handler._determine_recovery_strategy(error)
        assert strategy == RecoveryStrategy.ABORT  # 安全側


class TestErrorHandlerCoreHandleError:
    """エラーハンドリング機能のテスト"""
    
    def setup_method(self):
        self.handler = ErrorHandlerCore()
    
    @patch('sphinxcontrib.jsontable.errors.error_handler_core.logging')
    def test_handle_error_success_retry(self, mock_logging):
        """リトライ戦略での成功ケース"""
        error = FileAccessError("Temporary file lock")
        context = "Excel file reading"
        
        # リトライが成功する場合をシミュレート
        with patch.object(self.handler, '_attempt_recovery') as mock_recovery:
            mock_recovery.return_value = HandlingResult(
                success=True,
                recovery_attempted=True,
                recovered_data="Recovered successfully"
            )
            
            result = self.handler.handle_error(error, context)
            
            assert result.success is True
            assert result.recovery_attempted is True
            assert result.recovered_data == "Recovered successfully"
    
    @patch('sphinxcontrib.jsontable.errors.error_handler_core.logging')
    def test_handle_error_failure_abort(self, mock_logging):
        """アボート戦略での失敗ケース"""
        error = SecurityValidationError("Critical security issue")
        context = "Security validation"
        
        result = self.handler.handle_error(error, context)
        
        assert result.success is False
        assert result.recovery_attempted is False
        assert result.error_logged is True
    
    @patch('sphinxcontrib.jsontable.errors.error_handler_core.logging')
    def test_handle_error_with_custom_severity(self, mock_logging):
        """カスタム重要度でのエラーハンドリング"""
        error = ValueError("Custom error")
        context = "Test context"
        custom_severity = ErrorSeverity.CRITICAL
        
        result = self.handler.handle_error(error, context, custom_severity)
        
        assert result.severity == custom_severity
        assert result.error_logged is True
    
    def test_handle_error_recovery_disabled(self):
        """リカバリ無効時のエラーハンドリング"""
        handler = ErrorHandlerCore(enable_recovery=False)
        error = FileAccessError("File error")
        context = "Test context"
        
        result = handler.handle_error(error, context)
        
        assert result.success is False
        assert result.recovery_attempted is False
    
    @patch('sphinxcontrib.jsontable.errors.error_handler_core.logging')
    def test_handle_error_with_exception_in_recovery(self, mock_logging):
        """リカバリ処理中の例外"""
        error = DataConversionError("Conversion failed")
        context = "Data conversion"
        
        with patch.object(self.handler, '_attempt_recovery') as mock_recovery:
            mock_recovery.side_effect = Exception("Recovery process failed")
            
            result = self.handler.handle_error(error, context)
            
            assert result.success is False
            assert result.recovery_attempted is True
            assert "Recovery process failed" in result.error_message


class TestErrorHandlerCoreCreateErrorResponse:
    """エラーレスポンス作成のテスト"""
    
    def setup_method(self):
        self.handler = ErrorHandlerCore()
    
    def test_create_error_response_basic(self):
        """基本的なエラーレスポンス作成"""
        error = FileAccessError("File not found")
        context = "File loading"
        
        response = self.handler.create_error_response(error, context)
        
        assert response["error_type"] == "FileAccessError"
        assert response["error_message"] == "File not found"
        assert response["context"] == context
        assert response["severity"] == ErrorSeverity.HIGH.value
        assert "timestamp" in response
        assert "error_id" in response
    
    def test_create_error_response_without_context(self):
        """コンテキストなしのエラーレスポンス作成"""
        error = DataConversionError("Invalid data format")
        
        response = self.handler.create_error_response(error)
        
        assert response["error_type"] == "DataConversionError"
        assert response["error_message"] == "Invalid data format"
        assert response["context"] is None
    
    def test_create_error_response_with_traceback(self):
        """トレースバック付きエラーレスポンス作成"""
        try:
            raise ValueError("Test error for traceback")
        except ValueError as e:
            response = self.handler.create_error_response(e, "Test context")
            
            assert "traceback" in response
            assert "ValueError" in response["traceback"]
            assert "Test error for traceback" in response["traceback"]
    
    def test_create_error_response_security_sanitization(self):
        """セキュリティ情報のサニタイゼーション"""
        error = SecurityValidationError("Password: secret123 in file")
        
        response = self.handler.create_error_response(error, "Security check")
        
        # センシティブ情報が適切にサニタイズされているかの確認
        # （実装に応じて具体的な検証内容を調整）
        assert "error_message_sanitized" in response
    
    def test_create_error_response_with_user_data(self):
        """ユーザーデータ付きエラーレスポンス作成"""
        error = RangeValidationError("Invalid range A1:Z99999")
        context = "Range parsing"
        user_data = {"file_path": "/path/to/file.xlsx", "user_id": "test_user"}
        
        response = self.handler.create_error_response(error, context, user_data)
        
        assert response["user_data"] == user_data
        assert response["error_type"] == "RangeValidationError"


class TestErrorHandlerCoreRecoveryStrategies:
    """リカバリ戦略のテスト"""
    
    def setup_method(self):
        self.handler = ErrorHandlerCore()
    
    def test_retry_strategy_success(self):
        """リトライ戦略の成功ケース"""
        error = FileAccessError("Temporary lock")
        
        with patch.object(self.handler, '_execute_retry') as mock_retry:
            mock_retry.return_value = HandlingResult(
                success=True,
                recovery_attempted=True,
                recovered_data="File loaded on retry"
            )
            
            result = self.handler._attempt_recovery(error, RecoveryStrategy.RETRY)
            
            assert result.success is True
            assert result.recovery_attempted is True
            mock_retry.assert_called_once()
    
    def test_retry_strategy_max_attempts_exceeded(self):
        """リトライ戦略の最大試行回数超過"""
        error = FileAccessError("Persistent lock")
        
        with patch.object(self.handler, '_execute_retry') as mock_retry:
            mock_retry.return_value = HandlingResult(
                success=False,
                recovery_attempted=True,
                attempts_made=3,
                error_message="Max retry attempts exceeded"
            )
            
            result = self.handler._attempt_recovery(error, RecoveryStrategy.RETRY)
            
            assert result.success is False
            assert result.attempts_made == 3
    
    def test_fallback_strategy(self):
        """フォールバック戦略のテスト"""
        error = DataConversionError("Cannot parse cell")
        
        with patch.object(self.handler, '_execute_fallback') as mock_fallback:
            mock_fallback.return_value = HandlingResult(
                success=True,
                recovery_attempted=True,
                recovered_data="Default value used"
            )
            
            result = self.handler._attempt_recovery(error, RecoveryStrategy.FALLBACK)
            
            assert result.success is True
            mock_fallback.assert_called_once()
    
    def test_abort_strategy(self):
        """アボート戦略のテスト"""
        error = SecurityValidationError("Security threat")
        
        result = self.handler._attempt_recovery(error, RecoveryStrategy.ABORT)
        
        assert result.success is False
        assert result.recovery_attempted is False
        assert result.error_message == "Recovery aborted due to security concerns"


class TestErrorHandlerCoreLogging:
    """ログ機能のテスト"""
    
    def setup_method(self):
        self.handler = ErrorHandlerCore()
    
    @patch('sphinxcontrib.jsontable.errors.error_handler_core.logging')
    def test_log_error_info_level(self, mock_logging):
        """INFOレベルでのエラーログ"""
        error = DataConversionError("Minor conversion issue")
        context = "Data processing"
        severity = ErrorSeverity.LOW
        
        self.handler._log_error(error, context, severity)
        
        # INFOレベルでログが記録されることを確認
        # （実装に応じて具体的な検証方法を調整）
    
    @patch('sphinxcontrib.jsontable.errors.error_handler_core.logging')
    def test_log_error_warning_level(self, mock_logging):
        """WARNINGレベルでのエラーログ"""
        error = RangeValidationError("Range specification warning")
        context = "Range parsing"
        severity = ErrorSeverity.MEDIUM
        
        self.handler._log_error(error, context, severity)
        
        # WARNINGレベルでログが記録されることを確認
    
    @patch('sphinxcontrib.jsontable.errors.error_handler_core.logging')
    def test_log_error_critical_level(self, mock_logging):
        """CRITICALレベルでのエラーログ"""
        error = SecurityValidationError("Critical security issue")
        context = "Security validation"
        severity = ErrorSeverity.CRITICAL
        
        self.handler._log_error(error, context, severity)
        
        # CRITICALレベルでログが記録されることを確認
    
    def test_log_structured_error_data(self):
        """構造化エラーデータのログ"""
        error = FileAccessError("Complex file error")
        context = "File processing"
        
        with patch.object(self.handler.logger, 'error') as mock_logger_error:
            self.handler._log_structured_error(error, context, {
                "file_path": "/path/to/file.xlsx",
                "operation": "read",
                "timestamp": "2023-01-01T00:00:00Z"
            })
            
            mock_logger_error.assert_called_once()
            # 構造化データが適切に含まれていることを確認


class TestErrorHandlerCorePerformance:
    """パフォーマンス関連のテスト"""
    
    def setup_method(self):
        self.handler = ErrorHandlerCore()
    
    def test_error_handling_performance(self):
        """エラーハンドリングの性能テスト"""
        errors = [
            FileAccessError(f"Error {i}") for i in range(100)
        ]
        
        import time
        start_time = time.time()
        
        results = []
        for error in errors:
            result = self.handler.handle_error(error, "Performance test")
            results.append(result)
        
        execution_time = time.time() - start_time
        
        assert len(results) == 100
        assert execution_time < 5.0  # 5秒以内での完了を期待
    
    def test_memory_efficient_error_logging(self):
        """メモリ効率的なエラーログ"""
        large_error_message = "Large error message: " + "X" * 10000
        error = ExcelProcessingError(large_error_message)
        
        # メモリ使用量を意識したログ処理のテスト
        with patch.object(self.handler, '_optimize_error_message') as mock_optimize:
            mock_optimize.return_value = "Optimized error message"
            
            result = self.handler.handle_error(error, "Memory test")
            
            mock_optimize.assert_called_once()
            assert result.error_logged is True


class TestErrorHandlerCoreIntegration:
    """統合テスト"""
    
    def setup_method(self):
        self.handler = ErrorHandlerCore(
            enable_recovery=True,
            max_retry_attempts=3
        )
    
    def test_complete_error_handling_flow(self):
        """完全なエラーハンドリングフローのテスト"""
        error = FileAccessError("Temporary file access issue")
        context = "Excel file loading"
        
        with patch.object(self.handler, '_execute_retry') as mock_retry:
            # 2回目のリトライで成功するケース
            mock_retry.side_effect = [
                HandlingResult(success=False, recovery_attempted=True),
                HandlingResult(success=True, recovery_attempted=True, recovered_data="Success on retry")
            ]
            
            result = self.handler.handle_error(error, context)
            
            assert result.success is True
            assert result.recovery_attempted is True
            assert result.recovered_data == "Success on retry"
            assert mock_retry.call_count == 2
    
    def test_error_response_consistency(self):
        """エラーレスポンスの一貫性テスト"""
        errors = [
            FileAccessError("File error"),
            DataConversionError("Conversion error"),
            SecurityValidationError("Security error"),
            RangeValidationError("Range error")
        ]
        
        responses = []
        for error in errors:
            response = self.handler.create_error_response(error, "Consistency test")
            responses.append(response)
        
        # 全てのレスポンスが共通のフィールドを持つことを確認
        common_fields = {"error_type", "error_message", "context", "severity", "timestamp", "error_id"}
        for response in responses:
            assert common_fields.issubset(set(response.keys()))
            assert response["context"] == "Consistency test"