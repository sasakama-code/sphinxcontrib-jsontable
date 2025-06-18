"""Backward Compatibility - Legacy API compatibility layer.

Clean separation of backward compatibility functionality to maintain 100% API compatibility
while allowing main directive module to focus on core functionality.

CLAUDE.md Code Excellence Compliance:
- Single Responsibility: Backward compatibility only
- DRY Principle: Centralized compatibility layer
- YAGNI Principle: Essential compatibility features only
"""

from pathlib import Path
from typing import Any

from .json_processor import JsonProcessor
from .validators import ValidationUtils

# Type definitions for backward compatibility
JsonData = list[Any] | dict[str, Any]

# Constants for backward compatibility
DEFAULT_ENCODING = "utf-8"
DEFAULT_MAX_ROWS = 10000
NO_JSON_SOURCE_ERROR = "No JSON data source provided"
INVALID_JSON_DATA_ERROR = "JSON data must be an array or object"
EMPTY_CONTENT_ERROR = "No inline JSON content provided"


class JsonDataLoader:
    """
    Backward compatibility class - redirects to JsonProcessor.

    This class provides the same interface as the original JsonDataLoader
    while internally delegating to the new JsonProcessor implementation.
    """

    def __init__(self, encoding: str = DEFAULT_ENCODING):
        """Initialize with backward-compatible interface."""
        self._processor = JsonProcessor(base_path=Path.cwd(), encoding=encoding)

    def load_from_file(self, source: str, base_path: Path | None = None) -> JsonData:
        """Load JSON from file - backward compatible method."""
        if base_path:
            self._processor.base_path = base_path
        return self._processor.load_from_file(source)

    def parse_inline(self, content: list[str]) -> JsonData:
        """Parse inline JSON - backward compatible method."""
        return self._processor.parse_inline(content)


# Backward compatibility functions (preserve original function signatures)
def validate_not_empty(data: Any, error_msg: str) -> None:
    """Backward compatibility function - delegates to ValidationUtils."""
    return ValidationUtils.validate_not_empty(data, error_msg)


def safe_str(value: Any) -> str:
    """Backward compatibility function - delegates to ValidationUtils."""
    return ValidationUtils.safe_str(value)


def ensure_file_exists(path: Path) -> None:
    """Backward compatibility function - delegates to ValidationUtils."""
    return ValidationUtils.ensure_file_exists(path)


def format_error(context: str, error: Exception) -> str:
    """Backward compatibility function - delegates to ValidationUtils."""
    return ValidationUtils.format_error(context, error)


def is_safe_path(path: Path, base: Path) -> bool:
    """Backward compatibility function - delegates to ValidationUtils."""
    return ValidationUtils.is_safe_path(path, base)


# Export list for backward compatibility
__all__ = [
    # Data processing classes
    "JsonDataLoader",
    # Utility functions
    "validate_not_empty",
    "safe_str",
    "ensure_file_exists",
    "format_error",
    "is_safe_path",
    # Constants
    "DEFAULT_ENCODING",
    "DEFAULT_MAX_ROWS",
    "NO_JSON_SOURCE_ERROR",
    "INVALID_JSON_DATA_ERROR",
    "EMPTY_CONTENT_ERROR",
    # Type definitions
    "JsonData",
]
