"""
Unit tests for ErrorHandler - extracted from monolithic ExcelDataLoader.

Tests the staged error handling logic that was previously in lines 413-434
of excel_data_loader.py. This provides improved testability and coverage
of complex error handling scenarios.
"""

from unittest.mock import Mock, patch

from sphinxcontrib.jsontable.errors.error_handlers import (
    ErrorHandler,
    ErrorSeverity,
    HandlingResult,
    IErrorHandler,
    MockErrorHandler,
    RecoveryStrategy,
)
from sphinxcontrib.jsontable.errors.excel_errors import (
    DataConversionError,
    ExcelProcessingError,
    FileAccessError,
    RangeValidationError,
    SecurityValidationError,
)


class TestErrorHandler:
    """Test suite for ErrorHandler class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.handler = ErrorHandler()
        self.strict_handler = ErrorHandler(default_strategy=RecoveryStrategy.FAIL_FAST)
        self.permissive_handler = ErrorHandler(default_strategy=RecoveryStrategy.IGNORE)

    def test_initialization(self):
        """Test ErrorHandler initialization."""
        # Default initialization
        handler = ErrorHandler()
        assert handler.default_strategy == RecoveryStrategy.GRACEFUL_DEGRADATION
        assert handler.enable_logging is True
        assert handler.logger is not None

        # Custom initialization
        custom_handler = ErrorHandler(
            default_strategy=RecoveryStrategy.FAIL_FAST, enable_logging=False
        )
        assert custom_handler.default_strategy == RecoveryStrategy.FAIL_FAST
        assert custom_handler.enable_logging is False
        assert custom_handler.logger is None

    def test_error_severity_mapping(self):
        """Test error severity determination."""
        # Test specific error types
        assert (
            self.handler._determine_severity(SecurityValidationError)
            == ErrorSeverity.CRITICAL
        )
        assert (
            self.handler._determine_severity(RangeValidationError) == ErrorSeverity.HIGH
        )
        assert (
            self.handler._determine_severity(DataConversionError)
            == ErrorSeverity.MEDIUM
        )
        assert self.handler._determine_severity(FileAccessError) == ErrorSeverity.HIGH
        assert self.handler._determine_severity(Exception) == ErrorSeverity.LOW

    def test_stage_1_error_analysis(self):
        """Test Stage 1: Error analysis functionality."""
        error = SecurityValidationError(
            [{"type": "dangerous_link", "severity": "high"}]
        )

        analysis = self.handler._analyze_error(error, "test_context")

        assert analysis["error_type"] == SecurityValidationError
        assert analysis["severity"] == ErrorSeverity.CRITICAL
        assert analysis["recovery_strategy"] == RecoveryStrategy.FAIL_FAST
        assert analysis["context"] == "test_context"
        assert "error_info" in analysis

    def test_stage_2_severity_assessment_override(self):
        """Test severity assessment with manual override."""
        error = Exception("Generic error")

        # Without override
        analysis1 = self.handler._analyze_error(error, "test")
        assert analysis1["severity"] == ErrorSeverity.LOW

        # With override
        analysis2 = self.handler._analyze_error(error, "test", ErrorSeverity.CRITICAL)
        assert analysis2["severity"] == ErrorSeverity.CRITICAL

    def test_stage_3_fail_fast_recovery(self):
        """Test Stage 3: Fail fast recovery strategy."""
        error = SecurityValidationError([{"type": "critical_threat"}])

        recovery = self.handler._fail_fast_recovery(error, "security_check")

        assert not recovery["recovery_applied"]
        assert not recovery["success"]
        assert recovery["strategy"] == "fail_fast"
        assert recovery["should_reraise"] is True

    def test_stage_3_graceful_degradation_recovery(self):
        """Test Stage 3: Graceful degradation recovery strategy."""
        error = DataConversionError("header_parsing")

        recovery = self.handler._graceful_degradation_recovery(error, "data_processing")

        assert recovery["recovery_applied"]
        assert recovery["success"]
        assert recovery["strategy"] == "graceful_degradation"
        assert "fallback_data" in recovery
        assert not recovery["should_reraise"]

    def test_stage_3_retry_recovery(self):
        """Test Stage 3: Retry recovery strategy."""
        error = FileAccessError("/path/to/file.xlsx")

        recovery = self.handler._retry_recovery(error, "file_access")

        assert recovery["recovery_applied"]
        assert not recovery["success"]
        assert recovery["strategy"] == "retry"
        assert recovery["should_retry"] is True
        assert recovery["max_retries"] == 3

    def test_stage_3_ignore_recovery(self):
        """Test Stage 3: Ignore recovery strategy."""
        error = Exception("Minor issue")

        recovery = self.handler._ignore_recovery(error, "minor_processing")

        assert recovery["recovery_applied"]
        assert recovery["success"]
        assert recovery["strategy"] == "ignore"
        assert not recovery["should_reraise"]
        assert "ignored_error" in recovery

    def test_stage_4_response_generation_critical_error(self):
        """Test Stage 4: Response generation for critical errors."""
        error = SecurityValidationError([{"type": "malware"}])
        recovery_result = {
            "success": False,
            "recovery_applied": False,
            "should_reraise": True,
        }

        response = self.handler._generate_response(
            error, recovery_result, "security_scan", ErrorSeverity.CRITICAL
        )

        assert not response.success
        assert response.error_handled
        assert not response.recovery_applied
        assert len(response.error_messages) > 0
        assert "Critical error" in response.error_messages[0]
        assert response.metadata["severity"] == "critical"

    def test_stage_4_response_generation_with_fallback(self):
        """Test Stage 4: Response generation with fallback data."""
        error = DataConversionError("json_conversion")
        recovery_result = {
            "success": True,
            "recovery_applied": True,
            "fallback_data": {"data": [], "metadata": {"warning": "partial"}},
            "warning": "Data conversion partially failed",
        }

        response = self.handler._generate_response(
            error, recovery_result, "conversion", ErrorSeverity.MEDIUM
        )

        assert response.success
        assert response.error_handled
        assert response.recovery_applied
        assert response.response_data is not None
        assert len(response.warning_messages) > 0
        assert "Graceful degradation" in response.warning_messages[0]

    def test_stage_5_logging_disabled(self):
        """Test Stage 5: Logging when disabled."""
        handler = ErrorHandler(enable_logging=False)
        error = Exception("Test error")
        result = HandlingResult(
            success=True,
            error_handled=True,
            recovery_applied=False,
            response_data=None,
            warning_messages=[],
            error_messages=[],
            metadata={"context": "test"},
        )

        # Should not raise any errors when logging is disabled
        handler._log_error_handling(error, "test_context", result)

    @patch("logging.getLogger")
    def test_stage_5_logging_error_case(self, mock_get_logger):
        """Test Stage 5: Logging for error cases."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        handler = ErrorHandler(enable_logging=True)
        error = SecurityValidationError([{"type": "threat"}])
        result = HandlingResult(
            success=False,
            error_handled=True,
            recovery_applied=False,
            response_data=None,
            warning_messages=[],
            error_messages=["Critical error occurred"],
            metadata={"context": "security", "severity": "critical"},
        )

        handler._log_error_handling(error, "security_check", result)

        mock_logger.error.assert_called_once()
        assert "Error handling failed" in str(mock_logger.error.call_args)

    def test_integrated_error_handling_security_error(self):
        """Test integrated error handling for security errors."""
        security_issues = [
            {"type": "malware", "severity": "high"},
            {"type": "suspicious_link", "severity": "medium"},
        ]
        error = SecurityValidationError(security_issues)

        result = self.handler.handle_error(error, "security_validation")

        # Should fail fast for security errors
        assert not result.success
        assert result.error_handled
        assert len(result.error_messages) > 0
        assert result.metadata["severity"] == "critical"

    def test_integrated_error_handling_data_conversion_error(self):
        """Test integrated error handling for data conversion errors."""
        error = DataConversionError("json_serialization")

        result = self.handler.handle_error(error, "data_processing")

        # Should apply graceful degradation
        assert result.success
        assert result.error_handled
        assert result.recovery_applied
        assert result.response_data is not None
        assert len(result.warning_messages) > 0

    def test_integrated_error_handling_with_permissive_strategy(self):
        """Test integrated handling with permissive default strategy."""
        error = RangeValidationError("A1:Z999999")

        # Use permissive handler that ignores errors by default
        result = self.permissive_handler.handle_error(error, "range_parsing")

        # Note: RangeValidationError has explicit FAIL_FAST strategy,
        # so it should still fail despite permissive default
        assert not result.success

    def test_create_error_response_excel_processing_error(self):
        """Test error response creation for ExcelProcessingError."""
        error = DataConversionError(
            "header_detection", context={"sheet": "Sheet1", "row": 5}
        )

        response = self.handler.create_error_response(error, "data_conversion")

        assert not response["success"]
        assert response["error"]["type"] == "DataConversionError"
        assert response["error"]["code"] == "DATA_CONVERSION_ERROR"
        assert response["error"]["severity"] == "medium"
        assert response["error"]["context"] == "data_conversion"
        assert "details" in response["error"]

    def test_create_error_response_generic_exception(self):
        """Test error response creation for generic exceptions."""
        error = ValueError("Invalid input format")

        response = self.handler.create_error_response(error, "input_validation")

        assert not response["success"]
        assert response["error"]["type"] == "ValueError"
        assert response["error"]["message"] == "Invalid input format"
        assert response["error"]["severity"] == "low"
        assert response["data"] is None

    def test_fallback_data_generation_security_error(self):
        """Test fallback data generation for security errors."""
        security_issues = [{"type": "dangerous_link"}]
        error = SecurityValidationError(security_issues)

        fallback = self.handler._generate_fallback_data(error, "security")

        assert fallback["data"] == []
        assert "security_warning" in fallback["metadata"]
        assert fallback["metadata"]["security_issues_count"] == 1

    def test_fallback_data_generation_conversion_error(self):
        """Test fallback data generation for conversion errors."""
        error = DataConversionError("json_parsing")

        fallback = self.handler._generate_fallback_data(error, "conversion")

        assert fallback["data"] == []
        assert "conversion_warning" in fallback["metadata"]
        assert fallback["metadata"]["partial_data_available"] is False

    def test_error_info_extraction(self):
        """Test structured error information extraction."""
        # Test with ExcelProcessingError
        error1 = SecurityValidationError([{"type": "test"}])
        info1 = self.handler._extract_error_info(error1)
        assert info1["error_type"] == "SecurityValidationError"
        assert info1["error_code"] == "SECURITY_VALIDATION_ERROR"

        # Test with generic exception
        error2 = ValueError("Test error")
        info2 = self.handler._extract_error_info(error2)
        assert info2["error_type"] == "ValueError"
        assert info2["message"] == "Test error"
        assert "traceback" in info2


class TestMockErrorHandler:
    """Test suite for MockErrorHandler."""

    def test_mock_handler_default_behavior(self):
        """Test MockErrorHandler with default responses."""
        mock_handler = MockErrorHandler()

        error = Exception("Test error")
        result = mock_handler.handle_error(error, "test_context")

        assert result.success
        assert result.error_handled
        assert len(mock_handler.handle_error_calls) == 1

        response = mock_handler.create_error_response(error, "test_context")
        assert not response["success"]
        assert len(mock_handler.create_error_response_calls) == 1

    def test_mock_handler_custom_responses(self):
        """Test MockErrorHandler with custom responses."""
        custom_result = HandlingResult(
            success=False,
            error_handled=True,
            recovery_applied=True,
            response_data={"custom": "data"},
            warning_messages=["Custom warning"],
            error_messages=[],
            metadata={"custom": "metadata"},
        )

        custom_response = {
            "success": False,
            "error": {"type": "CustomError", "message": "Custom error"},
            "data": {"custom": "response_data"},
        }

        mock_handler = MockErrorHandler(
            mock_result=custom_result, mock_response=custom_response
        )

        error = Exception("Test")
        result = mock_handler.handle_error(error, "test")
        response = mock_handler.create_error_response(error, "test")

        assert result.response_data == {"custom": "data"}
        assert result.warning_messages == ["Custom warning"]
        assert response["data"] == {"custom": "response_data"}

    def test_mock_handler_call_tracking(self):
        """Test MockErrorHandler call tracking functionality."""
        mock_handler = MockErrorHandler()

        error1 = SecurityValidationError([])
        error2 = DataConversionError("test")

        mock_handler.handle_error(error1, "context1", ErrorSeverity.HIGH)
        mock_handler.handle_error(error2, "context2")
        mock_handler.create_error_response(error1, "response_context")

        assert len(mock_handler.handle_error_calls) == 2
        assert len(mock_handler.create_error_response_calls) == 1

        # Verify call details
        call1 = mock_handler.handle_error_calls[0]
        assert isinstance(call1["error"], SecurityValidationError)
        assert call1["context"] == "context1"
        assert call1["severity"] == ErrorSeverity.HIGH

        response_call = mock_handler.create_error_response_calls[0]
        assert isinstance(response_call["error"], SecurityValidationError)
        assert response_call["context"] == "response_context"


class TestInterface:
    """Test interface implementation."""

    def test_interface_implementation(self):
        """Test that ErrorHandler implements IErrorHandler."""
        handler = ErrorHandler()
        assert isinstance(handler, IErrorHandler)

        # Verify all abstract methods are implemented
        assert hasattr(handler, "handle_error")
        assert hasattr(handler, "create_error_response")
        assert callable(handler.handle_error)
        assert callable(handler.create_error_response)


class TestRecoveryStrategies:
    """Test different recovery strategies in isolation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.handler = ErrorHandler()

    def test_recovery_strategy_assignment(self):
        """Test that error types are assigned correct recovery strategies."""
        # Critical errors should fail fast
        assert (
            self.handler.recovery_strategies[SecurityValidationError]
            == RecoveryStrategy.FAIL_FAST
        )
        assert (
            self.handler.recovery_strategies[RangeValidationError]
            == RecoveryStrategy.FAIL_FAST
        )
        assert (
            self.handler.recovery_strategies[FileAccessError]
            == RecoveryStrategy.FAIL_FAST
        )

        # Recoverable errors should use graceful degradation
        assert (
            self.handler.recovery_strategies[DataConversionError]
            == RecoveryStrategy.GRACEFUL_DEGRADATION
        )
        assert (
            self.handler.recovery_strategies[ExcelProcessingError]
            == RecoveryStrategy.GRACEFUL_DEGRADATION
        )

    def test_fallback_to_default_strategy(self):
        """Test fallback to default strategy for unknown error types."""

        class UnknownError(Exception):
            pass

        error = UnknownError("Unknown error type")

        # Should use the default strategy (graceful degradation)
        recovery = self.handler._apply_recovery_strategy(
            error, self.handler.default_strategy, "test"
        )

        assert recovery["strategy"] == "graceful_degradation"
        assert recovery["recovery_applied"]


# Integration test with realistic scenarios
class TestIntegration:
    """Integration tests simulating real Excel processing error scenarios."""

    def test_integration_with_dependency_injection(self):
        """Test integration with dependency injection pattern."""
        # This would be used in the main ExcelDataLoader
        custom_handler = MockErrorHandler(
            mock_result=HandlingResult(
                success=True,
                error_handled=True,
                recovery_applied=True,
                response_data={"fallback": "data"},
                warning_messages=["Custom recovery applied"],
                error_messages=[],
                metadata={"strategy": "custom"},
            )
        )

        # Simulate how it would be used in ExcelDataLoader
        def mock_excel_loader_method(error_handler: IErrorHandler):
            error = DataConversionError("json_conversion")
            result = error_handler.handle_error(error, "data_processing")
            response = error_handler.create_error_response(error, "api_response")
            return result, response

        result, response = mock_excel_loader_method(custom_handler)

        assert result.success
        assert result.recovery_applied
        assert len(result.warning_messages) == 1
        assert "Custom recovery applied" in result.warning_messages[0]
        assert not response["success"]  # Error response format

    def test_complex_error_scenario_with_multiple_stages(self):
        """Test complex error scenario covering all handling stages."""
        handler = ErrorHandler(enable_logging=False)  # Disable logging for test

        # Simulate a complex security error with context
        security_issues = [
            {"type": "malware_link", "severity": "high", "location": "A1"},
            {"type": "external_script", "severity": "high", "location": "B2"},
            {"type": "suspicious_formula", "severity": "medium", "location": "C3"},
        ]
        error = SecurityValidationError(
            security_issues,
            context={"file_path": "/path/to/dangerous.xlsm", "sheet": "Data"},
        )

        # Process through all stages
        result = handler.handle_error(
            error, "security_validation", ErrorSeverity.CRITICAL
        )

        # Verify staged processing results
        assert not result.success  # Should fail for security errors
        assert result.error_handled
        assert not result.recovery_applied  # Fail fast strategy
        assert len(result.error_messages) > 0
        assert result.metadata["severity"] == "critical"
        assert result.metadata["strategy"] == "fail_fast"

        # Test error response generation
        response = handler.create_error_response(error, "excel_processing")
        assert response["error"]["code"] == "SECURITY_VALIDATION_ERROR"
        assert response["error"]["severity"] == "critical"
        assert "details" in response["error"]
