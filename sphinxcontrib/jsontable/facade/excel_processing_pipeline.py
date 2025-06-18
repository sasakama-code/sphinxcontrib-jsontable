"""Excel Processing Pipeline - Multi-stage Excel processing workflow.

This module contains the core processing pipeline for Excel data loading,
implementing a 5-stage processing workflow with error handling and validation.

CLAUDE.md Code Excellence Compliance:
- Single Responsibility: Excel processing workflow
- DRY Principle: Centralized processing logic
- SOLID Principles: Interface segregation and dependency injection
"""

from pathlib import Path
from typing import Any, Dict, Optional, Union

import pandas as pd

from ..core.data_converter import IDataConverter
from ..core.excel_reader import IExcelReader
from ..core.range_parser import IRangeParser, RangeInfo
from ..errors.error_handlers import IErrorHandler
from ..security.security_scanner import ISecurityValidator


class ExcelProcessingPipeline:
    """5-stage Excel processing pipeline with integrated error handling.

    This class implements the core processing workflow for Excel data loading,
    coordinating security validation, range parsing, file reading, data conversion,
    and result integration.

    Processing Stages:
        1. Security validation
        2. Range parsing (if specified)
        3. File reading
        4. Data conversion
        5. Result integration
    """

    def __init__(
        self,
        excel_reader: IExcelReader,
        data_converter: IDataConverter,
        range_parser: IRangeParser,
        security_validator: Optional[ISecurityValidator] = None,
        error_handler: Optional[IErrorHandler] = None,
        enable_security: bool = True,
        enable_error_handling: bool = True,
    ):
        """Initialize processing pipeline with components."""
        self.excel_reader = excel_reader
        self.data_converter = data_converter
        self.range_parser = range_parser
        self.security_validator = security_validator
        self.error_handler = error_handler
        self.enable_security = enable_security
        self.enable_error_handling = enable_error_handling

    def process_excel_file(
        self,
        file_path: Union[str, Path],
        sheet_name: Optional[str] = None,
        sheet_index: Optional[int] = None,
        range_spec: Optional[str] = None,
        header_row: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Execute 5-stage Excel processing pipeline.

        Args:
            file_path: Path to Excel file
            sheet_name: Target sheet name
            sheet_index: Target sheet index (0-based)
            range_spec: Excel range specification (e.g., "A1:C10")
            header_row: Header row number (0-based)

        Returns:
            Processing result with data and metadata
        """
        context = "excel_processing_pipeline"

        try:
            # Stage 1: Security validation
            if self.enable_security and self.security_validator:
                self._perform_security_validation(file_path, context)

            # Stage 2: Range parsing (if specified)
            range_info = None
            if range_spec:
                range_info = self._parse_range_specification(range_spec, context)

            # Stage 3: File reading
            read_result = self._read_excel_file(
                file_path, sheet_name, sheet_index, context
            )

            # Stage 4: Data conversion
            conversion_result = self._convert_data_to_json(
                read_result.dataframe, header_row, context
            )

            # Stage 5: Result integration
            return self._build_integrated_result(
                conversion_result, read_result, range_info, context
            )

        except Exception as e:
            return self._handle_processing_error(e, context)

    def _perform_security_validation(
        self, file_path: Union[str, Path], context: str
    ) -> None:
        """Stage 1: Perform security validation."""
        if not self.security_validator:
            return

        try:
            security_result = self.security_validator.validate_file(Path(file_path))
            if not security_result.get("is_safe", True):
                threats = security_result.get("threats", [])
                threat_summary = ", ".join([t.get("type", "Unknown") for t in threats])
                raise SecurityError(f"Security threats detected: {threat_summary}")

        except Exception as e:
            if self.enable_error_handling and self.error_handler:
                error_response = self.error_handler.create_error_response(e, context)
                raise ProcessingError(
                    f"Security validation failed: {error_response}"
                ) from e
            else:
                raise

    def _parse_range_specification(
        self, range_spec: str, context: str
    ) -> Optional[RangeInfo]:
        """Stage 2: Parse range specification."""
        try:
            return self.range_parser.parse(range_spec)
        except Exception as e:
            if self.enable_error_handling and self.error_handler:
                error_response = self.error_handler.create_error_response(e, context)
                raise ProcessingError(f"Range parsing failed: {error_response}") from e
            else:
                raise

    def _read_excel_file(
        self,
        file_path: Union[str, Path],
        sheet_name: Optional[str],
        sheet_index: Optional[int],
        context: str,
    ) -> Any:
        """Stage 3: Read Excel file."""
        try:
            return self.excel_reader.read_workbook(
                file_path, sheet_name=sheet_name, sheet_index=sheet_index
            )
        except Exception as e:
            if self.enable_error_handling and self.error_handler:
                error_response = self.error_handler.create_error_response(e, context)
                raise ProcessingError(f"File reading failed: {error_response}") from e
            else:
                raise

    def _convert_data_to_json(
        self, dataframe: pd.DataFrame, header_row: Optional[int], context: str
    ) -> Any:
        """Stage 4: Convert data to JSON format."""
        try:
            return self.data_converter.convert_dataframe_to_json(
                dataframe, header_row=header_row
            )
        except Exception as e:
            if self.enable_error_handling and self.error_handler:
                error_response = self.error_handler.create_error_response(e, context)
                raise ProcessingError(
                    f"Data conversion failed: {error_response}"
                ) from e
            else:
                raise

    def _build_integrated_result(
        self,
        conversion_result: Any,
        read_result: Any,
        range_info: Optional[RangeInfo],
        context: str,
    ) -> Dict[str, Any]:
        """Stage 5: Build integrated result."""
        try:
            result = {
                "success": True,
                "data": conversion_result.data,
                "metadata": {
                    "has_header": conversion_result.has_header,
                    "headers": conversion_result.headers,
                    "workbook_info": read_result.workbook_info.to_dict(),
                    "processing_timestamp": pd.Timestamp.now().isoformat(),
                },
                "components_used": self._get_components_info(),
            }

            # Add range information if available
            if range_info:
                result["metadata"]["range_info"] = {
                    "original_spec": range_info.original_spec,
                    "normalized_spec": range_info.normalized_spec,
                    "row_count": range_info.row_count,
                    "col_count": range_info.col_count,
                }

            return result

        except Exception as e:
            if self.enable_error_handling and self.error_handler:
                error_response = self.error_handler.create_error_response(e, context)
                raise ProcessingError(
                    f"Result integration failed: {error_response}"
                ) from e
            else:
                raise

    def _handle_processing_error(
        self, error: Exception, context: str
    ) -> Dict[str, Any]:
        """Handle processing errors."""
        if self.enable_error_handling and self.error_handler:
            return self.error_handler.create_error_response(error, context)
        else:
            return {
                "success": False,
                "error": {
                    "type": type(error).__name__,
                    "message": str(error),
                    "context": context,
                },
                "data": None,
            }

    def _get_components_info(self) -> Dict[str, str]:
        """Get information about pipeline components."""
        return {
            "excel_reader": type(self.excel_reader).__name__,
            "data_converter": type(self.data_converter).__name__,
            "range_parser": type(self.range_parser).__name__,
            "security_validator": type(self.security_validator).__name__
            if self.security_validator
            else None,
            "error_handler": type(self.error_handler).__name__
            if self.error_handler
            else None,
        }


class ProcessingError(Exception):
    """Exception raised during pipeline processing."""

    pass


class SecurityError(Exception):
    """Exception raised during security validation."""

    pass
