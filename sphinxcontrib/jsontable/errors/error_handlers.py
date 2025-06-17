"""
Structured error handling for Excel processing.

This module extracts and improves upon the error handling logic that was
previously scattered throughout the monolithic ExcelDataLoader class.
Provides staged error handling for improved testability and maintainability.
"""

import logging
import traceback
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from .excel_errors import (
    DataConversionError,
    ExcelProcessingError,
    FileAccessError,
    RangeValidationError,
    SecurityValidationError,
)


class ErrorSeverity(Enum):
    """Error severity levels for handling strategy determination."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecoveryStrategy(Enum):
    """Error recovery strategies."""

    FAIL_FAST = "fail_fast"
    GRACEFUL_DEGRADATION = "graceful_degradation"
    RETRY = "retry"
    IGNORE = "ignore"


@dataclass
class HandlingResult:
    """Result of error handling operation."""

    success: bool
    error_handled: bool
    recovery_applied: bool
    response_data: Optional[Dict[str, Any]]
    warning_messages: List[str]
    error_messages: List[str]
    metadata: Dict[str, Any]


class IErrorHandler(ABC):
    """Abstract interface for error handling."""

    @abstractmethod
    def handle_error(
        self, error: Exception, context: str, severity: Optional[ErrorSeverity] = None
    ) -> HandlingResult:
        """Handle an error with appropriate strategy."""
        pass

    @abstractmethod
    def create_error_response(
        self, error: Exception, context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create standardized error response."""
        pass


class ErrorHandler(IErrorHandler):
    """
    Structured error handler for Excel processing.

    Extracts and refactors the complex error handling logic from
    ExcelDataLoader to provide staged, testable error processing.
    """

    def __init__(
        self,
        default_strategy: RecoveryStrategy = RecoveryStrategy.GRACEFUL_DEGRADATION,
        enable_logging: bool = True,
        logger_name: str = "sphinxcontrib.jsontable.errors",
    ):
        """Initialize error handler with configuration."""
        self.default_strategy = default_strategy
        self.enable_logging = enable_logging
        self.logger = logging.getLogger(logger_name) if enable_logging else None

        # Error severity mapping
        self.severity_mapping = {
            SecurityValidationError: ErrorSeverity.CRITICAL,
            RangeValidationError: ErrorSeverity.HIGH,
            DataConversionError: ErrorSeverity.MEDIUM,
            FileAccessError: ErrorSeverity.HIGH,
            ExcelProcessingError: ErrorSeverity.MEDIUM,
            Exception: ErrorSeverity.LOW,
        }

        # Recovery strategy mapping by error type
        self.recovery_strategies = {
            SecurityValidationError: RecoveryStrategy.FAIL_FAST,
            RangeValidationError: RecoveryStrategy.FAIL_FAST,
            DataConversionError: RecoveryStrategy.GRACEFUL_DEGRADATION,
            FileAccessError: RecoveryStrategy.FAIL_FAST,
            ExcelProcessingError: RecoveryStrategy.GRACEFUL_DEGRADATION,
        }

    def handle_error(
        self, error: Exception, context: str, severity: Optional[ErrorSeverity] = None
    ) -> HandlingResult:
        """
        Handle error with staged processing approach.

        This method replaces the deep try-catch structures (lines 413-434)
        with a staged approach that allows for test insertion at each stage.
        """
        # Stage 1: Error Analysis
        analysis_result = self._analyze_error(error, context, severity)

        # Stage 2: Severity Assessment
        error_severity = analysis_result["severity"]
        recovery_strategy = analysis_result["recovery_strategy"]

        # Stage 3: Recovery Strategy Application
        recovery_result = self._apply_recovery_strategy(
            error, recovery_strategy, context
        )

        # Stage 4: Response Generation
        response = self._generate_response(
            error, recovery_result, context, error_severity
        )

        # Stage 5: Logging and Monitoring
        if self.enable_logging:
            self._log_error_handling(error, context, response)

        return response

    def _analyze_error(
        self,
        error: Exception,
        context: str,
        provided_severity: Optional[ErrorSeverity] = None,
    ) -> Dict[str, Any]:
        """
        Stage 1: Analyze error to determine handling approach.

        This stage is separately testable and allows for mock injection.
        """
        error_type = type(error)

        # Determine severity
        severity = provided_severity or self._determine_severity(error_type)

        # Determine recovery strategy
        recovery_strategy = self.recovery_strategies.get(
            error_type, self.default_strategy
        )

        # Extract structured information from error
        error_info = self._extract_error_info(error)

        return {
            "error_type": error_type,
            "severity": severity,
            "recovery_strategy": recovery_strategy,
            "error_info": error_info,
            "context": context,
        }

    def _determine_severity(self, error_type: type) -> ErrorSeverity:
        """Determine error severity based on type hierarchy."""
        for exception_type, severity in self.severity_mapping.items():
            if issubclass(error_type, exception_type):
                return severity
        return ErrorSeverity.LOW

    def _extract_error_info(self, error: Exception) -> Dict[str, Any]:
        """Extract structured information from error."""
        if isinstance(error, ExcelProcessingError):
            return error.to_dict()

        return {
            "error_type": type(error).__name__,
            "message": str(error),
            "traceback": traceback.format_exc(),
        }

    def _apply_recovery_strategy(
        self, error: Exception, strategy: RecoveryStrategy, context: str
    ) -> Dict[str, Any]:
        """
        Stage 3: Apply recovery strategy based on error analysis.

        Each strategy is testable in isolation with mock injection.
        """
        if strategy == RecoveryStrategy.FAIL_FAST:
            return self._fail_fast_recovery(error, context)

        elif strategy == RecoveryStrategy.GRACEFUL_DEGRADATION:
            return self._graceful_degradation_recovery(error, context)

        elif strategy == RecoveryStrategy.RETRY:
            return self._retry_recovery(error, context)

        elif strategy == RecoveryStrategy.IGNORE:
            return self._ignore_recovery(error, context)

        else:
            # Fallback to graceful degradation
            return self._graceful_degradation_recovery(error, context)

    def _fail_fast_recovery(self, error: Exception, context: str) -> Dict[str, Any]:
        """Fail fast strategy - do not attempt recovery."""
        return {
            "recovery_applied": False,
            "success": False,
            "strategy": "fail_fast",
            "error": error,
            "should_reraise": True,
        }

    def _graceful_degradation_recovery(
        self, error: Exception, context: str
    ) -> Dict[str, Any]:
        """Graceful degradation - provide partial functionality."""
        # Attempt to extract any usable data or provide fallback
        fallback_data = self._generate_fallback_data(error, context)

        return {
            "recovery_applied": True,
            "success": True,
            "strategy": "graceful_degradation",
            "fallback_data": fallback_data,
            "should_reraise": False,
            "warning": f"Partial processing due to error: {str(error)}",
        }

    def _retry_recovery(self, error: Exception, context: str) -> Dict[str, Any]:
        """Retry strategy - mark for retry (implementation depends on caller)."""
        return {
            "recovery_applied": True,
            "success": False,
            "strategy": "retry",
            "should_retry": True,
            "retry_delay": 1.0,  # seconds
            "max_retries": 3,
        }

    def _ignore_recovery(self, error: Exception, context: str) -> Dict[str, Any]:
        """Ignore strategy - continue processing as if no error occurred."""
        return {
            "recovery_applied": True,
            "success": True,
            "strategy": "ignore",
            "should_reraise": False,
            "ignored_error": str(error),
        }

    def _generate_fallback_data(self, error: Exception, context: str) -> Dict[str, Any]:
        """Generate fallback data when graceful degradation is applied."""
        if isinstance(error, SecurityValidationError):
            return {
                "data": [],
                "metadata": {
                    "security_warning": "Processing limited due to security restrictions",
                    "security_issues_count": len(error.security_issues),
                },
            }

        elif isinstance(error, DataConversionError):
            return {
                "data": [],
                "metadata": {
                    "conversion_warning": f"Data conversion failed at stage: {error.conversion_stage}",
                    "partial_data_available": False,
                },
            }

        else:
            return {
                "data": [],
                "metadata": {
                    "error_type": type(error).__name__,
                    "fallback_applied": True,
                },
            }

    def _generate_response(
        self,
        error: Exception,
        recovery_result: Dict[str, Any],
        context: str,
        severity: ErrorSeverity,
    ) -> HandlingResult:
        """
        Stage 4: Generate final response based on recovery results.

        This stage consolidates recovery results into a standardized response.
        """
        warning_messages = []
        error_messages = []
        response_data = None

        if recovery_result.get("should_reraise", False):
            # Critical errors that should be re-raised
            error_messages.append(f"Critical error in {context}: {str(error)}")

        elif recovery_result.get("recovery_applied", False):
            # Recovery was applied
            if "fallback_data" in recovery_result:
                response_data = recovery_result["fallback_data"]
                warning_messages.append(
                    f"Graceful degradation applied in {context}: {str(error)}"
                )

            if "warning" in recovery_result:
                warning_messages.append(recovery_result["warning"])

        return HandlingResult(
            success=recovery_result.get("success", False),
            error_handled=True,
            recovery_applied=recovery_result.get("recovery_applied", False),
            response_data=response_data,
            warning_messages=warning_messages,
            error_messages=error_messages,
            metadata={
                "context": context,
                "severity": severity.value,
                "strategy": recovery_result.get("strategy", "unknown"),
                "error_type": type(error).__name__,
            },
        )

    def _log_error_handling(
        self, error: Exception, context: str, result: HandlingResult
    ) -> None:
        """Stage 5: Log error handling for monitoring and debugging."""
        if not self.logger:
            return

        log_data = {
            "context": context,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "handling_result": {
                "success": result.success,
                "recovery_applied": result.recovery_applied,
                "strategy": result.metadata.get("strategy"),
                "severity": result.metadata.get("severity"),
            },
        }

        if result.error_messages:
            self.logger.error(f"Error handling failed: {log_data}")
        elif result.warning_messages:
            self.logger.warning(f"Error handled with warnings: {log_data}")
        else:
            self.logger.info(f"Error handled successfully: {log_data}")

    def create_error_response(
        self, error: Exception, context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create standardized error response for API consumers.

        This replaces scattered error response generation throughout
        the original ExcelDataLoader.
        """
        error_info = self._extract_error_info(error)
        severity = self._determine_severity(type(error))

        response = {
            "success": False,
            "error": {
                "type": error_info.get("error_type", type(error).__name__),
                "code": error_info.get("error_code", "UNKNOWN_ERROR"),
                "message": error_info.get("message", str(error)),
                "severity": severity.value,
                "context": context,
            },
            "data": None,
            "metadata": {
                "timestamp": "2025-06-17T00:00:00Z",  # Would use datetime in real implementation
                "processing_failed": True,
            },
        }

        # Add specific error details if available
        if isinstance(error, ExcelProcessingError):
            response["error"].update(
                {
                    "details": error_info.get("context", {}),
                    "original_error": error_info.get("original_error"),
                }
            )

        return response


# Default implementation for dependency injection
class DefaultErrorHandler(ErrorHandler):
    """Default error handler implementation."""

    def __init__(self):
        super().__init__(
            default_strategy=RecoveryStrategy.GRACEFUL_DEGRADATION, enable_logging=True
        )


# Mock implementation for testing
class MockErrorHandler(IErrorHandler):
    """Mock error handler for testing purposes."""

    def __init__(
        self,
        mock_result: Optional[HandlingResult] = None,
        mock_response: Optional[Dict[str, Any]] = None,
    ):
        self.mock_result = mock_result or HandlingResult(
            success=True,
            error_handled=True,
            recovery_applied=False,
            response_data=None,
            warning_messages=[],
            error_messages=[],
            metadata={},
        )
        self.mock_response = mock_response or {
            "success": False,
            "error": {"type": "MockError", "message": "Mock error response"},
            "data": None,
        }

        # Track calls for testing
        self.handle_error_calls = []
        self.create_error_response_calls = []

    def handle_error(
        self, error: Exception, context: str, severity: Optional[ErrorSeverity] = None
    ) -> HandlingResult:
        """Return mock handling result and track call."""
        self.handle_error_calls.append(
            {"error": error, "context": context, "severity": severity}
        )
        return self.mock_result

    def create_error_response(
        self, error: Exception, context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Return mock error response and track call."""
        self.create_error_response_calls.append({"error": error, "context": context})
        return self.mock_response
