"""Enhanced directive modular components.

Provides a modular architecture for the enhanced JSON table directive
with clear separation of concerns and SOLID principle compliance.

Modules:
- rag_processing_result: Data container for RAG processing results
- rag_pipeline_processor: RAG processing pipeline execution logic
- options_manager: Options parsing and component lifecycle management

Created: 2025-06-12
"""

# Re-export the main class from the parent module
import sys
from pathlib import Path

from .options_manager import EnhancedDirectiveOptionsManager
from .rag_pipeline_processor import RAGPipelineProcessor
from .rag_processing_result import RAGProcessingResult

# Import EnhancedJsonTableDirective from the main enhanced_directive.py
parent_dir = Path(__file__).parent.parent
enhanced_directive_path = parent_dir / "enhanced_directive.py"

if enhanced_directive_path.exists():
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "enhanced_directive_main", enhanced_directive_path
    )
    enhanced_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(enhanced_module)
    EnhancedJsonTableDirective = enhanced_module.EnhancedJsonTableDirective
else:
    # Fallback if file structure issues
    EnhancedJsonTableDirective = None

__all__ = [
    "EnhancedDirectiveOptionsManager",
    "EnhancedJsonTableDirective",
    "RAGPipelineProcessor",
    "RAGProcessingResult",
]
