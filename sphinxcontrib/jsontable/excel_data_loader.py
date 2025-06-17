"""Excel Data Loader - Legacy API with New Architecture.

This module provides backward compatibility for the legacy ExcelDataLoader API
while internally using the new component-based architecture.

Migration Status: Phase 3 Complete - Using new architecture internally
Components: SecurityScanner, ErrorHandler, RangeParser, DataConverter, ExcelReader
Architecture: Facade pattern with dependency injection
"""

from pathlib import Path
from typing import Any, Dict, List, Union

from .facade.excel_data_loader_facade import ExcelDataLoaderFacade


class ExcelDataLoader:
    """Legacy ExcelDataLoader API with new architecture backend.

    This class maintains 100% backward compatibility with the original 5,441-line
    monolithic ExcelDataLoader while internally using the new component-based
    architecture for improved testability, maintainability, and coverage.

    Architecture Components:
    - SecurityScanner: Security validation (99.24% coverage)
    - ErrorHandler: 5-stage error processing (89.02% coverage)
    - RangeParser: Functional composition range parsing (97.33% coverage)
    - DataConverter: JSON conversion & header processing (95.28% coverage)
    - ExcelReader: File I/O operations (94.88% coverage)
    """

    def __init__(self, base_path: Union[str, Path] = "", lazy_init: bool = True):
        """Initialize with legacy API compatibility and performance optimization.

        Args:
            base_path: Base directory path (legacy parameter, maintained for compatibility)
            lazy_init: Whether to use lazy initialization for facade (default True for performance)
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()

        # Lazy initialization for performance
        self._facade = None
        self._lazy_init = lazy_init

        # Cache for resolved paths to improve performance
        self._path_cache = {}

        # Legacy properties for backward compatibility
        self.encoding = "utf-8"
        self.MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB (legacy constant)
        self.SUPPORTED_EXTENSIONS = {
            ".xlsx",
            ".xls",
            ".xlsm",
            ".xltm",
        }  # Legacy constant

        # Initialize facade immediately if not using lazy initialization
        if not lazy_init:
            self._initialize_facade()

    def _initialize_facade(self) -> None:
        """Initialize the new architecture facade (called on first use if lazy_init=True)."""
        if self._facade is None:
            self._facade = ExcelDataLoaderFacade(
                enable_security=True, enable_error_handling=True
            )

    @property
    def facade(self) -> ExcelDataLoaderFacade:
        """Get facade instance with lazy initialization."""
        if self._facade is None:
            self._initialize_facade()
        return self._facade

    # Core loading methods (unified delegation pattern)

    def _delegate_to_facade(
        self, method_name: str, file_path: Union[str, Path], *args, **kwargs
    ) -> Any:
        """Unified delegation to facade with path resolution and error handling.

        Args:
            method_name: Name of the facade method to call
            file_path: Path to Excel file (str or Path object)
            *args: Positional arguments for the facade method
            **kwargs: Keyword arguments for the facade method

        Returns:
            Result from the facade method

        Raises:
            AttributeError: If facade method doesn't exist
            TypeError: If file_path is not str or Path
            ValueError: If file_path is invalid
        """
        # Input validation - defensive programming
        if not isinstance(file_path, (str, Path)):
            raise TypeError(f"file_path must be str or Path, got {type(file_path)}")

        if not method_name or not isinstance(method_name, str):
            raise ValueError(f"method_name must be non-empty string, got {method_name}")

        # Check if facade method exists (triggers lazy initialization)
        if not hasattr(self.facade, method_name):
            raise AttributeError(f"Facade method '{method_name}' not found")

        try:
            # Path resolution with validation and caching
            resolved_path = self._resolve_path_cached(file_path)
            facade_method = getattr(self.facade, method_name)
            return facade_method(resolved_path, *args, **kwargs)
        except Exception as e:
            # Enhanced error context for debugging
            raise type(e)(f"Error in {method_name} with path '{file_path}': {e}") from e

    def load_from_excel(self, file_path: Union[str, Path], **kwargs) -> Dict[str, Any]:
        """Load Excel file using new architecture."""
        return self._delegate_to_facade("load_from_excel", file_path, **kwargs)

    def load_from_excel_with_detect_range(
        self, file_path: Union[str, Path], detect_range: str = "auto", **kwargs
    ) -> Dict[str, Any]:
        """Load with range detection."""
        return self._delegate_to_facade(
            "load_from_excel_with_detect_range", file_path, detect_range, **kwargs
        )

    def load_from_excel_with_skip_rows_range_and_header(
        self,
        file_path: Union[str, Path],
        skip_rows: Any,
        range_spec: str,
        header_row: int,
        **kwargs,
    ) -> Dict[str, Any]:
        """Load with skip rows, range, and header."""
        return self._delegate_to_facade(
            "load_from_excel_with_skip_rows_range_and_header",
            file_path,
            skip_rows,
            range_spec,
            header_row,
            **kwargs,
        )

    def load_from_excel_with_skip_rows_and_range(
        self, file_path: Union[str, Path], skip_rows: Any, range_spec: str, **kwargs
    ) -> Dict[str, Any]:
        """Load with skip rows and range."""
        return self._delegate_to_facade(
            "load_from_excel_with_skip_rows_and_range",
            file_path,
            skip_rows,
            range_spec,
            **kwargs,
        )

    def load_from_excel_with_skip_rows_and_header(
        self, file_path: Union[str, Path], skip_rows: Any, header_row: int, **kwargs
    ) -> Dict[str, Any]:
        """Load with skip rows and header."""
        return self._delegate_to_facade(
            "load_from_excel_with_skip_rows_and_header",
            file_path,
            skip_rows,
            header_row,
            **kwargs,
        )

    def load_from_excel_with_skip_rows(
        self, file_path: Union[str, Path], skip_rows: Any, **kwargs
    ) -> Dict[str, Any]:
        """Load with skip rows."""
        return self._delegate_to_facade(
            "load_from_excel_with_skip_rows", file_path, skip_rows, **kwargs
        )

    def load_from_excel_with_merge_cells_and_range(
        self, file_path: Union[str, Path], merge_cells: str, range_spec: str, **kwargs
    ) -> Dict[str, Any]:
        """Load with merge cells and range."""
        return self._delegate_to_facade(
            "load_from_excel_with_merge_cells_and_range",
            file_path,
            merge_cells,
            range_spec,
            **kwargs,
        )

    def load_from_excel_with_header_row_and_range(
        self, file_path: Union[str, Path], header_row: int, range_spec: str, **kwargs
    ) -> Dict[str, Any]:
        """Load with header row and range."""
        return self._delegate_to_facade(
            "load_from_excel_with_header_row_and_range",
            file_path,
            header_row,
            range_spec,
            **kwargs,
        )

    def load_from_excel_with_merge_cells_and_header(
        self, file_path: Union[str, Path], merge_cells: str, header_row: int, **kwargs
    ) -> Dict[str, Any]:
        """Load with merge cells and header."""
        return self._delegate_to_facade(
            "load_from_excel_with_merge_cells_and_header",
            file_path,
            merge_cells,
            header_row,
            **kwargs,
        )

    def load_from_excel_with_header_row(
        self, file_path: Union[str, Path], header_row: int, **kwargs
    ) -> Dict[str, Any]:
        """Load with header row."""
        return self._delegate_to_facade(
            "load_from_excel_with_header_row", file_path, header_row, **kwargs
        )

    def load_from_excel_with_merge_cells(
        self, file_path: Union[str, Path], merge_cells: str, **kwargs
    ) -> Dict[str, Any]:
        """Load with merge cells."""
        return self._delegate_to_facade(
            "load_from_excel_with_merge_cells", file_path, merge_cells, **kwargs
        )

    def load_from_excel_with_range(
        self, file_path: Union[str, Path], range_spec: str, **kwargs
    ) -> Dict[str, Any]:
        """Load with range."""
        return self._delegate_to_facade(
            "load_from_excel_with_range", file_path, range_spec, **kwargs
        )

    def load_from_excel_with_cache(
        self, file_path: Union[str, Path], **kwargs
    ) -> Dict[str, Any]:
        """Load with cache."""
        return self._delegate_to_facade(
            "load_from_excel_with_cache", file_path, **kwargs
        )

    # Utility methods (unified delegation pattern)

    def get_sheet_name_by_index(
        self, file_path: Union[str, Path], sheet_index: int
    ) -> str:
        """Get sheet name by index."""
        return self._delegate_to_facade(
            "get_sheet_name_by_index", file_path, sheet_index
        )

    def validate_excel_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Validate Excel file."""
        return self._delegate_to_facade("validate_excel_file", file_path)

    def get_sheet_names(self, file_path: Union[str, Path]) -> List[str]:
        """Get sheet names."""
        return self._delegate_to_facade("get_sheet_names", file_path)

    def is_safe_path(self, file_path: Union[str, Path]) -> bool:
        """Check if path is safe."""
        return self._delegate_to_facade("is_safe_path", file_path)

    def basic_sheet_detection(self, file_path: Union[str, Path]) -> str:
        """Get first sheet name."""
        return self._delegate_to_facade("basic_sheet_detection", file_path)

    # DataFrame processing methods (no path resolution needed)

    def header_detection(self, dataframe) -> bool:
        """Simple header detection (direct facade access)."""
        return self.facade.header_detection(dataframe)

    def data_type_conversion(self, dataframe) -> List[List[Any]]:
        """Convert DataFrame to 2D array (direct facade access)."""
        return self.facade.data_type_conversion(dataframe)

    # Legacy method aliases for full compatibility

    def load_from_excel_by_index(
        self, file_path: Union[str, Path], sheet_index: int, **kwargs
    ) -> Dict[str, Any]:
        """Load by sheet index (legacy method)."""
        return self._delegate_to_facade(
            "load_from_excel", file_path, sheet_index=sheet_index, **kwargs
        )

    # Internal helper methods

    def _resolve_path(self, file_path: Union[str, Path]) -> Path:
        """Resolve file path relative to base path with security validation.

        Args:
            file_path: Input file path (str or Path)

        Returns:
            Resolved absolute Path object

        Raises:
            ValueError: If path is invalid or contains security risks
            TypeError: If file_path is not str or Path
        """
        # Input validation
        if not isinstance(file_path, (str, Path)):
            raise TypeError(f"file_path must be str or Path, got {type(file_path)}")

        # Convert to Path and validate
        try:
            path = Path(file_path)
        except (ValueError, OSError) as e:
            raise ValueError(f"Invalid file path '{file_path}': {e}") from e

        # Security check - prevent path traversal attacks
        if ".." in str(path):
            raise ValueError(
                f"Path traversal detected in '{file_path}' - '..' not allowed"
            )

        # Resolve relative paths
        if not path.is_absolute():
            path = self.base_path / path

        # Additional security validation
        try:
            # Resolve to canonical path to prevent symlink attacks
            resolved_path = path.resolve()

            # Ensure resolved path is within allowed base path (if relative was used)
            if not str(resolved_path).startswith(str(self.base_path.resolve())):
                if not Path(file_path).is_absolute():
                    raise ValueError(
                        f"Resolved path '{resolved_path}' outside base directory '{self.base_path}'"
                    )

            return resolved_path

        except (OSError, RuntimeError) as e:
            raise ValueError(f"Cannot resolve path '{file_path}': {e}") from e

    def _resolve_path_cached(self, file_path: Union[str, Path]) -> Path:
        """Resolve file path with caching for performance optimization.

        Args:
            file_path: Input file path (str or Path)

        Returns:
            Resolved absolute Path object (from cache if available)
        """
        # Create cache key
        cache_key = str(file_path)

        # Return cached result if available
        if cache_key in self._path_cache:
            return self._path_cache[cache_key]

        # Resolve path and cache result
        resolved_path = self._resolve_path(file_path)

        # Limit cache size to prevent memory issues
        if len(self._path_cache) >= 100:  # Max 100 cached paths
            # Remove oldest entry (FIFO)
            oldest_key = next(iter(self._path_cache))
            del self._path_cache[oldest_key]

        self._path_cache[cache_key] = resolved_path
        return resolved_path

    # Component access for advanced usage

    @property
    def security_scanner(self):
        """Access to SecurityScanner component (lazy initialization)."""
        return self.facade.security_validator

    @property
    def error_handler(self):
        """Access to ErrorHandler component (lazy initialization)."""
        return self.facade.error_handler

    @property
    def range_parser(self):
        """Access to RangeParser component (lazy initialization)."""
        return self.facade.range_parser

    @property
    def data_converter(self):
        """Access to DataConverter component (lazy initialization)."""
        return self.facade.data_converter

    @property
    def excel_reader(self):
        """Access to ExcelReader component (lazy initialization)."""
        return self.facade.excel_reader

    # Missing legacy methods for test compatibility

    def _parse_skip_rows_specification(self, skip_rows: Any) -> Any:
        """Parse skip rows specification (delegate to facade)."""
        return self.facade._parse_skip_rows_specification(skip_rows)

    def _validate_skip_rows_specification(self, skip_rows: Any) -> None:
        """Validate skip rows specification."""
        if skip_rows is None:
            return None

        if not isinstance(skip_rows, str):
            raise TypeError("Skip rows must be a string")

        if not skip_rows.strip():
            raise ValueError("Skip rows specification cannot be empty")

        try:
            self._parse_skip_rows_specification(skip_rows)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid skip_rows specification: {skip_rows}") from e

    # Architecture information

    def get_architecture_info(self) -> Dict[str, Any]:
        """Get information about the new architecture with caching."""
        # Cache architecture info to avoid repeated file reads
        if not hasattr(self, "_architecture_info_cache"):
            current_lines = len(open(__file__).readlines())
            self._architecture_info_cache = {
                "version": "3.0.0",  # Updated for best practices version
                "architecture": "component-based",
                "pattern": "facade_with_lazy_initialization",
                "components": self.facade._get_components_info(),
                "legacy_api_compatible": True,
                "lazy_initialization": self._lazy_init,
                "path_caching": True,
                "security_enhanced": True,
                "original_lines": 5441,
                "new_lines": current_lines,
                "reduction_percentage": round((1 - current_lines / 5441) * 100, 1),
                "optimization_features": [
                    "lazy_facade_initialization",
                    "path_resolution_caching",
                    "unified_delegation_pattern",
                    "enhanced_security_validation",
                    "defensive_programming",
                ],
            }
        return self._architecture_info_cache


# Backward compatibility aliases
ExcelLoader = ExcelDataLoader  # Common alias used in some tests
