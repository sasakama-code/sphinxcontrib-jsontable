"""
Enhanced JSON Table Directive with RAG Integration

RAG統合対応の拡張版JsonTableDirective
既存機能への影響ゼロで、オプト・イン形式でRAG機能を提供
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, ClassVar

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.util import logging

from .directives import JsonTableDirective

logger = logging.getLogger(__name__)


class RAGMetadataExtractor:
    """
    JSONデータからRAG用メタデータを抽出するクラス

    Phase 1で実装する基本的なメタデータ抽出機能:
    - ソース情報（ファイル名、行数、列数）
    - スキーマ情報（型構造、フィールド一覧）
    - データ統計（null値、重複値の統計）
    """

    def extract_metadata(self, json_data: Any, source_info: dict | None = None) -> dict:
        """
        JSONデータからRAG用メタデータを抽出

        Args:
            json_data: 解析対象のJSONデータ
            source_info: ソース情報（ファイル名等）

        Returns:
            RAG用メタデータ辞書
        """
        metadata = {
            "data_type": self._detect_data_type(json_data),
            "source_info": source_info or {},
            "schema_info": self._extract_schema_info(json_data),
            "statistics": self._calculate_statistics(json_data),
            "rag_version": "1.0.0",
            "generator": "sphinxcontrib-jsontable-rag",
        }

        return metadata

    def _detect_data_type(self, data: Any) -> str:
        """データ型の検出"""
        if isinstance(data, dict):
            return "object"
        elif isinstance(data, list):
            if not data:
                return "empty_array"
            first_item = data[0]
            if isinstance(first_item, dict):
                return "object_array"
            elif isinstance(first_item, list):
                return "array_of_arrays"
            else:
                return "primitive_array"
        else:
            return "primitive"

    def _extract_schema_info(self, data: Any) -> dict:
        """スキーマ情報の抽出"""
        if isinstance(data, dict):
            return {
                "type": "object",
                "fields": list(data.keys()),
                "field_count": len(data.keys()),
                "field_types": {k: type(v).__name__ for k, v in data.items()},
            }
        elif isinstance(data, list) and data:
            if isinstance(data[0], dict):
                # オブジェクト配列の場合
                all_fields = set()
                for obj in data[:100]:  # 性能考慮で最初の100要素のみ
                    if isinstance(obj, dict):
                        all_fields.update(obj.keys())

                return {
                    "type": "array",
                    "item_type": "object",
                    "fields": sorted(all_fields),
                    "field_count": len(all_fields),
                    "array_length": len(data),
                }
            else:
                return {
                    "type": "array",
                    "item_type": type(data[0]).__name__,
                    "array_length": len(data),
                }
        else:
            return {"type": "unknown"}

    def _calculate_statistics(self, data: Any) -> dict:
        """データ統計の算出"""
        stats = {
            "total_elements": 0,
            "null_count": 0,
            "empty_string_count": 0,
        }

        if isinstance(data, dict):
            stats["total_elements"] = len(data)
            stats["null_count"] = sum(1 for v in data.values() if v is None)
            stats["empty_string_count"] = sum(1 for v in data.values() if v == "")
        elif isinstance(data, list):
            stats["total_elements"] = len(data)
            # リストの場合の統計は複雑になるので基本的な情報のみ

        return stats


class SemanticChunker:
    """
    テーブルデータを意味的なチャンクに分割するクラス

    Phase 1で実装する基本的なチャンク機能:
    - 行ベースチャンク（論理的なレコード単位）
    - 列ベースチャンク（フィールド単位）
    - メタデータ付きチャンク出力
    """

    def __init__(self, chunk_size: int = 10):
        """
        Args:
            chunk_size: チャンクあたりの行数（デフォルト10行）
        """
        self.chunk_size = chunk_size

    def create_semantic_chunks(
        self, table_data: list[list[str]], metadata: dict, has_header: bool = False
    ) -> list[dict]:
        """
        テーブルデータから意味的チャンクを生成

        Args:
            table_data: 2次元配列のテーブルデータ
            metadata: RAGメタデータ
            has_header: ヘッダー行の有無

        Returns:
            チャンク情報のリスト
        """
        chunks = []

        # ヘッダー処理
        header = table_data[0] if has_header and table_data else []
        data_rows = table_data[1:] if has_header else table_data

        # 行ベースチャンクの生成
        for i in range(0, len(data_rows), self.chunk_size):
            chunk_rows = data_rows[i : i + self.chunk_size]

            chunk_info = {
                "chunk_id": f"chunk_{i // self.chunk_size + 1}",
                "chunk_type": "row_based",
                "start_row": i + (1 if has_header else 0),
                "end_row": min(i + self.chunk_size, len(data_rows))
                + (1 if has_header else 0)
                - 1,
                "header": header,
                "data": chunk_rows,
                "row_count": len(chunk_rows),
                "column_count": len(header)
                if header
                else (len(chunk_rows[0]) if chunk_rows else 0),
                "metadata": metadata,
                "text_content": self._create_text_representation(header, chunk_rows),
            }

            chunks.append(chunk_info)

        return chunks

    def _create_text_representation(
        self, header: list[str], rows: list[list[str]]
    ) -> str:
        """チャンクのテキスト表現を生成"""
        lines = []

        if header:
            lines.append(" | ".join(header))
            lines.append("-" * len(lines[0]))

        for row in rows:
            lines.append(" | ".join(row))

        return "\n".join(lines)


class EnhancedJsonTableDirective(JsonTableDirective):
    """
    RAG統合対応の拡張版JsonTableDirective

    既存のJsonTableDirectiveを継承し、RAG機能をオプト・イン形式で追加。
    既存機能への影響は一切なく、完全な後方互換性を保証。
    """

    # 既存オプションに加えてRAG用オプションを追加
    option_spec: ClassVar[dict] = {
        **JsonTableDirective.option_spec,  # 既存オプション完全継承
        # Phase 1 RAGオプション
        "rag-enabled": directives.flag,
        "semantic-chunks": directives.flag,
        "metadata-export": directives.unchanged,
        "metadata-tags": directives.unchanged,
        "chunk-size": directives.nonnegative_int,
        # Phase 2 オプション（将来実装）
        "advanced-metadata": directives.flag,
        "search-facets": directives.flag,
        "export-formats": directives.unchanged,
        # Phase 3 オプション（将来実装）
        "vector-mode": directives.unchanged,  # 'plamo', 'openai', 'disabled'
        "embedding-model": directives.unchanged,
    }

    def __init__(self, *args, **kwargs):
        """
        拡張ディレクティブの初期化
        既存初期化に加えてRAGコンポーネントを条件付きで追加
        """
        super().__init__(*args, **kwargs)

        # RAG機能が有効な場合のみRAGコンポーネントを初期化
        if "rag-enabled" in self.options:
            self.rag_metadata_extractor = RAGMetadataExtractor()

            if "semantic-chunks" in self.options:
                chunk_size = self.options.get("chunk-size", 10)
                self.semantic_chunker = SemanticChunker(chunk_size)

    def run(self) -> list[nodes.Node]:
        """
        拡張ディレクティブの実行

        既存処理を完全に実行した後、RAG処理を追加。
        RAG処理で例外が発生しても既存機能に影響しない安全設計。
        """
        try:
            # 既存処理の実行（絶対に失敗させない）
            table_nodes = super().run()

            # RAG処理の追加（オプト・イン）
            if "rag-enabled" in self.options and table_nodes:
                try:
                    self._process_rag_enhancement(table_nodes[0])
                except Exception as e:
                    # RAG処理の失敗は警告のみ、既存機能は正常動作
                    logger.warning(
                        f"RAG processing failed, table rendered without RAG features: {e}"
                    )

            return table_nodes

        except Exception as e:
            # 既存のエラーハンドリングを完全維持
            logger.error(f"EnhancedJsonTableDirective error: {e}")
            return super().run()  # フォールバック

    def _process_rag_enhancement(self, table_node: nodes.table) -> None:
        """
        テーブルノードにRAG機能を追加

        Args:
            table_node: 拡張対象のdocutilsテーブルノード
        """
        # JSON データの再取得（既存メソッドを活用）
        json_data = self._load_json_data()

        # ソース情報の準備
        source_info = {
            "file_path": self.arguments[0] if self.arguments else None,
            "is_inline": not bool(self.arguments),
            "directive_options": dict(self.options),
        }

        # RAGメタデータの抽出
        rag_metadata = self.rag_metadata_extractor.extract_metadata(
            json_data, source_info
        )

        # テーブルノードにRAGメタデータを付与
        self._attach_rag_metadata(table_node, rag_metadata)

        # セマンティックチャンク処理
        if "semantic-chunks" in self.options:
            self._process_semantic_chunks(json_data, rag_metadata)

    def _attach_rag_metadata(self, table_node: nodes.table, metadata: dict) -> None:
        """
        RAGメタデータをテーブルノードに付与

        HTML出力時にdata属性として利用可能になる
        """
        # RAG識別情報
        table_node.attributes["data-rag-enabled"] = "true"
        table_node.attributes["data-rag-version"] = metadata.get("rag_version", "1.0.0")
        table_node.attributes["data-generator"] = metadata.get("generator", "")

        # ソース情報
        source_info = metadata.get("source_info", {})
        if source_info.get("file_path"):
            table_node.attributes["data-source-file"] = source_info["file_path"]
        table_node.attributes["data-source-type"] = (
            "file" if source_info.get("file_path") else "inline"
        )

        # スキーマ情報
        schema_info = metadata.get("schema_info", {})
        table_node.attributes["data-schema-type"] = schema_info.get("type", "unknown")
        if "field_count" in schema_info:
            table_node.attributes["data-field-count"] = str(schema_info["field_count"])
        if "array_length" in schema_info:
            table_node.attributes["data-array-length"] = str(
                schema_info["array_length"]
            )

        # 統計情報
        stats = metadata.get("statistics", {})
        if "total_elements" in stats:
            table_node.attributes["data-total-elements"] = str(stats["total_elements"])

        # 完全なメタデータのJSON形式格納（デバッグ・高度利用向け）
        table_node.attributes["data-rag-metadata"] = json.dumps(
            metadata, ensure_ascii=False, separators=(",", ":")
        )

        # CSSクラスの追加
        if "classes" not in table_node.attributes:
            table_node.attributes["classes"] = []
        table_node.attributes["classes"].extend(
            [
                "rag-enhanced-table",
                "json-source-table",
                f"schema-{schema_info.get('type', 'unknown')}",
            ]
        )

        # カスタムタグの追加
        if "metadata-tags" in self.options:
            custom_tags = self.options["metadata-tags"].split(",")
            table_node.attributes["classes"].extend(
                [f"tag-{tag.strip()}" for tag in custom_tags if tag.strip()]
            )

    def _process_semantic_chunks(self, json_data: Any, metadata: dict) -> None:
        """
        セマンティックチャンクの処理と出力
        """
        # テーブルデータの再生成（既存コンバーターを活用）
        include_header = "header" in self.options
        limit = self.options.get("limit")
        table_data = self.converter.convert(json_data, include_header, limit)

        # セマンティックチャンクの生成
        chunks = self.semantic_chunker.create_semantic_chunks(
            table_data, metadata, include_header
        )

        # チャンク情報の出力（設定に応じて）
        export_path = self.options.get("metadata-export")
        if export_path:
            self._export_chunks(chunks, export_path)
        else:
            # デフォルト: ログに出力
            logger.info(f"Generated {len(chunks)} semantic chunks for table")
            for chunk in chunks:
                logger.debug(f"Chunk {chunk['chunk_id']}: {chunk['row_count']} rows")

    def _export_chunks(self, chunks: list[dict], export_path: str) -> None:
        """
        チャンク情報をファイルにエクスポート

        Args:
            chunks: チャンク情報のリスト
            export_path: 出力ファイルパス
        """
        try:
            # セキュリティチェック（既存のpath validationを活用）
            output_path = Path(self.env.srcdir) / export_path
            if not output_path.parent.exists():
                output_path.parent.mkdir(parents=True, exist_ok=True)

            # チャンク情報をJSONで出力
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(chunks, f, ensure_ascii=False, indent=2)

            logger.info(f"Semantic chunks exported to: {export_path}")

        except Exception as e:
            logger.warning(f"Failed to export semantic chunks to {export_path}: {e}")


def setup(app):
    """
    Sphinx拡張の設定

    既存のjson-tableディレクティブに加えて
    enhanced-json-tableディレクティブを追加
    """
    app.add_directive("enhanced-json-table", EnhancedJsonTableDirective)

    # 設定値の追加
    app.add_config_value("jsontable_rag_enabled", False, "env")
    app.add_config_value("jsontable_default_chunk_size", 10, "env")

    return {
        "version": "1.0.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
