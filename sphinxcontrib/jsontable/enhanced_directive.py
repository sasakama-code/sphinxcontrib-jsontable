"""Enhanced JSON Table Directive with RAG Integration.

Extended JsonTableDirective that provides RAG capabilities with zero impact
on existing functionality through opt-in features.

Integrated Components:
- RAGMetadataExtractor (Phase 1): Basic metadata extraction
- SemanticChunker (Phase 1): Content segmentation 
- AdvancedMetadataGenerator (Phase 2): Statistical analysis
- SearchFacetGenerator (Phase 2): Search facet generation
- MetadataExporter (Phase 2): Multi-format export

Created: 2025-06-07
Author: Claude Code Assistant
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.util import logging

from .directives import JsonTableDirective
from .rag.advanced_metadata import AdvancedMetadata, AdvancedMetadataGenerator
from .rag.metadata_exporter import MetadataExporter
from .rag.metadata_extractor import BasicMetadata, RAGMetadataExtractor
from .rag.search_facets import GeneratedFacets, SearchFacetGenerator
from .rag.semantic_chunker import SemanticChunk, SemanticChunker

logger = logging.getLogger(__name__)


@dataclass
class RAGProcessingResult:
    """Result container for RAG processing pipeline.
    
    Args:
        basic_metadata: Basic metadata extracted from JSON data.
        semantic_chunks: List of semantic chunks created from content.
        advanced_metadata: Advanced statistical analysis results (optional).
        generated_facets: Generated search facets (optional).
        export_data: Exported metadata in various formats (optional).
    """

    basic_metadata: BasicMetadata
    semantic_chunks: list[SemanticChunk]
    advanced_metadata: AdvancedMetadata | None = None
    generated_facets: GeneratedFacets | None = None
    export_data: dict[str, Any] | None = None


class EnhancedJsonTableDirective(JsonTableDirective):
    """
    RAG統合対応の拡張版JsonTableDirective

    既存のJsonTableDirectiveを継承し、RAG機能をオプト・イン形式で追加。
    Phase 1と2の機能を統合して提供します。
    """

    # 既存オプションに加えてRAG関連オプションを追加
    option_spec: ClassVar[dict] = {
        **JsonTableDirective.option_spec,
        "rag-enabled": directives.flag,
        "semantic-chunks": directives.flag,
        "advanced-metadata": directives.flag,
        "export-formats": directives.unchanged,
        "metadata-tags": directives.unchanged,
        "chunk-strategy": directives.unchanged,
        "facet-generation": directives.flag,
    }

    def __init__(self, *args, **kwargs):
        """拡張ディレクティブを初期化"""
        super().__init__(*args, **kwargs)

        # RAG処理コンポーネントの初期化
        self.metadata_extractor = RAGMetadataExtractor()
        self.semantic_chunker = None
        self.advanced_generator = None
        self.facet_generator = None
        self.metadata_exporter = None

        # RAGが有効な場合のみコンポーネントを初期化
        if "rag-enabled" in self.options:
            chunk_strategy = self.options.get("chunk-strategy", "adaptive")
            self.semantic_chunker = SemanticChunker(chunk_strategy=chunk_strategy)

            if "advanced-metadata" in self.options:
                self.advanced_generator = AdvancedMetadataGenerator()

                if "facet-generation" in self.options:
                    self.facet_generator = SearchFacetGenerator()

                export_formats = self._parse_export_formats()
                if export_formats:
                    self.metadata_exporter = MetadataExporter()

    def run(self) -> list[nodes.Node]:
        """ディレクティブの実行

        既存のテーブル生成機能に加えて、RAG機能が有効な場合は
        メタデータ抽出・チャンク化・高度分析を実行します。
        """
        try:
            # 既存のテーブル生成処理を実行
            table_nodes = super().run()

            # RAG機能が有効でない場合は既存動作をそのまま返す
            if "rag-enabled" not in self.options:
                return table_nodes

            # JSONデータを取得
            json_data = self._get_json_data()

            # RAG処理を実行
            rag_result = self._process_rag_pipeline(json_data)

            # テーブルノードにRAGメタデータを付加
            if table_nodes and rag_result:
                self._attach_rag_metadata(table_nodes[0], rag_result)

            # デバッグ出力
            if self.env.app.config.get("rag_debug_mode", False):
                self._output_debug_info(rag_result)

            return table_nodes

        except Exception as e:
            logger.error(f"Enhanced directive RAG integration error: {e}")
            # エラーが発生しても既存機能は動作させる
            return super().run()

    def _get_json_data(self) -> dict[str, Any] | list[Any]:
        """Get JSON data from file or inline content.
        
        Reuses existing JsonTableDirective processing to load and parse
        JSON data from either file paths or inline content.
        
        Returns:
            Parsed JSON data as dictionary or list.
            
        Raises:
            ValueError: If path is unsafe or JSON data is invalid.
        """
        # ファイルからの読み込み
        if self.arguments:
            file_path = Path(self.env.srcdir) / self.arguments[0]
            if not self._is_safe_path(file_path):
                raise ValueError(f"Unsafe file path: {file_path}")

            try:
                with open(file_path, encoding="utf-8") as f:
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                raise ValueError(f"Failed to load JSON file: {e}") from e

        # インラインコンテンツからの読み込み
        elif self.content:
            content_str = "\n".join(self.content)
            try:
                return json.loads(content_str)
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse inline JSON: {e}") from e

        else:
            raise ValueError("No JSON data specified")

    def _process_rag_pipeline(self, json_data: Any) -> RAGProcessingResult:
        """Execute the RAG processing pipeline.
        
        Args:
            json_data: Input JSON data to process.
            
        Returns:
            RAGProcessingResult containing all processing outputs.
        """
        # Phase 1: Basic metadata extraction
        options_dict = dict(self.options)
        basic_metadata = self.metadata_extractor.extract(json_data, options_dict)

        # Phase 1: Semantic chunking
        semantic_chunks = []
        if self.semantic_chunker and "semantic-chunks" in self.options:
            semantic_chunks = self.semantic_chunker.process(json_data, basic_metadata)

        # Phase 2: Advanced metadata generation
        advanced_metadata = None
        if self.advanced_generator and "advanced-metadata" in self.options:
            advanced_metadata = self.advanced_generator.generate_advanced_metadata(
                json_data, basic_metadata
            )

        # Phase 2: Search facet generation
        generated_facets = None
        if (
            self.facet_generator
            and advanced_metadata
            and "facet-generation" in self.options
        ):
            generated_facets = self.facet_generator.generate_facets(advanced_metadata)

        # Phase 2: Metadata export
        export_data = None
        if self.metadata_exporter and advanced_metadata and generated_facets:
            export_formats = self._parse_export_formats()
            if export_formats:
                export_data = self.metadata_exporter.export_metadata(
                    advanced_metadata, generated_facets, export_formats
                )

        return RAGProcessingResult(
            basic_metadata=basic_metadata,
            semantic_chunks=semantic_chunks,
            advanced_metadata=advanced_metadata,
            generated_facets=generated_facets,
            export_data=export_data,
        )

    def _attach_rag_metadata(
        self, table_node: nodes.Node, rag_result: RAGProcessingResult
    ) -> None:
        """Attach RAG metadata to table node as custom attributes.
        
        Args:
            table_node: Docutils table node to annotate.
            rag_result: RAG processing results to attach.
        """
        # Add RAG metadata as custom attributes
        if not hasattr(table_node, "attributes"):
            table_node.attributes = {}

        # Basic metadata
        table_node.attributes["rag_table_id"] = rag_result.basic_metadata.table_id
        table_node.attributes["rag_semantic_summary"] = (
            rag_result.basic_metadata.semantic_summary
        )
        table_node.attributes["rag_search_keywords"] = ",".join(
            rag_result.basic_metadata.search_keywords
        )

        # Semantic chunk count
        if rag_result.semantic_chunks:
            table_node.attributes["rag_chunk_count"] = len(rag_result.semantic_chunks)

        # Advanced metadata availability
        if rag_result.advanced_metadata:
            table_node.attributes["rag_advanced_enabled"] = "true"

            # Data quality score
            quality = rag_result.advanced_metadata.data_quality
            table_node.attributes["rag_quality_score"] = f"{quality.overall_score:.2f}"

        # Search facets availability
        if rag_result.generated_facets:
            categorical_count = len(rag_result.generated_facets.categorical_facets)
            numerical_count = len(rag_result.generated_facets.numerical_facets)
            table_node.attributes["rag_facet_count"] = (
                f"{categorical_count + numerical_count}"
            )

        # Export data availability
        if rag_result.export_data:
            export_formats = list(rag_result.export_data.keys())
            table_node.attributes["rag_export_formats"] = ",".join(export_formats)

    def _parse_export_formats(self) -> list[str]:
        """Parse export formats from directive options.
        
        Returns:
            List of export format names specified in options.
        """
        if "export-formats" not in self.options:
            return []

        formats_str = self.options["export-formats"]
        return [fmt.strip() for fmt in formats_str.split(",") if fmt.strip()]

    def _is_safe_path(self, path: Path) -> bool:
        """Check if file path is safe for access.
        
        Args:
            path: File path to validate.
            
        Returns:
            True if path is within source directory and safe to access.
        """
        try:
            # Restrict to source directory
            resolved_path = path.resolve()
            srcdir_path = Path(self.env.srcdir).resolve()
            return str(resolved_path).startswith(str(srcdir_path))
        except Exception:
            return False

    def _output_debug_info(self, rag_result: RAGProcessingResult) -> None:
        """Output debug information for RAG processing results.
        
        Args:
            rag_result: RAG processing results to log.
        """
        logger.info("=== RAG Processing Debug Information ===")
        logger.info(f"Table ID: {rag_result.basic_metadata.table_id}")
        logger.info(f"Summary: {rag_result.basic_metadata.semantic_summary}")
        logger.info(f"Chunk count: {len(rag_result.semantic_chunks)}")

        if rag_result.advanced_metadata:
            quality = rag_result.advanced_metadata.data_quality
            logger.info(f"Data quality score: {quality.overall_score:.2f}")

            entities = rag_result.advanced_metadata.entity_classification
            person_count = len(entities.persons)
            org_count = len(entities.organizations)
            logger.info(f"Detected entities: persons={person_count}, organizations={org_count}")

        if rag_result.generated_facets:
            cat_count = len(rag_result.generated_facets.categorical_facets)
            num_count = len(rag_result.generated_facets.numerical_facets)
            logger.info(f"Generated facets: categorical={cat_count}, numerical={num_count}")

        if rag_result.export_data:
            formats = list(rag_result.export_data.keys())
            logger.info(f"Export formats: {', '.join(formats)}")

        logger.info("=== End Debug Information ===")


def setup(app):
    """Setup function for Sphinx extension.
    
    Args:
        app: Sphinx application instance.
        
    Returns:
        Extension metadata dictionary.
    """
    # 既存のjsontableディレクティブを拡張版で上書き
    app.add_directive("jsontable-rag", EnhancedJsonTableDirective)

    # 設定値の追加
    app.add_config_value("rag_debug_mode", False, "env")
    app.add_config_value("rag_default_chunk_strategy", "adaptive", "env")
    app.add_config_value("rag_default_export_formats", [], "env")

    return {
        "version": "1.0.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
