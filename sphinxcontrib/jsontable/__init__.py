"""
Sphinx extension for rendering JSON data as tables with advanced RAG capabilities.

This extension provides multiple directive options:

🔹 **JsonTableDirective** (推奨):
   標準的なJSONテーブル機能 - 軽量・高速・安定

🔹 **EnhancedJsonTableDirective** (RAG機能):
   RAG統合機能付き - メタデータ生成・セマンティック処理・PLaMo対応

⚠️  **LegacyJsonTableDirective** (非推奨):
   後方互換性のみ - 新規開発では使用非推奨

使用例:
    .. jsontable:: data.json          # 推奨：標準機能
    .. enhanced-jsontable:: data.json # RAG機能
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

# ⚠️ 非推奨：後方互換性維持のみ
from .directives import JsonTableDirective as LegacyJsonTableDirective

# 🔹 RAG機能拡張版
# Import from the refactored enhanced_directive module
try:
    from .enhanced_directive import EnhancedJsonTableDirective
except ImportError:
    # Fallback: create a dummy class if module structure issues exist
    from .json_table_directive import JsonTableDirective

    EnhancedJsonTableDirective = JsonTableDirective

# 🔹 推奨：標準jsontableディレクティブ
from .json_table_directive import JsonTableDirective

# パフォーマンス設定
from .table_converters import DEFAULT_MAX_ROWS

if TYPE_CHECKING:
    from sphinx.application import Sphinx

__version__ = "0.3.0"
__author__ = "sasakama-code"
__email__ = "sasakamacode@gmail.com"

# 明確なエクスポート構造
__all__ = [
    # 設定・メタデータ
    "DEFAULT_MAX_ROWS",
    "EnhancedJsonTableDirective",  # RAG機能
    # 🔹 推奨クラス
    "JsonTableDirective",  # 標準機能（推奨）
    # ⚠️ 非推奨クラス（移行期間のみ）
    "LegacyJsonTableDirective",  # 後方互換性維持
    "setup",
]


def setup(app: Sphinx) -> dict[str, Any]:
    """
    Sphinx extension setup function.

    登録されるディレクティブ:
    - jsontable: 標準機能（推奨）
    - enhanced-jsontable: RAG機能付き

    Args:
        app: Sphinx application instance

    Returns:
        Extension metadata
    """
    # 🔹 推奨：標準jsontableディレクティブ
    app.add_directive("jsontable", JsonTableDirective)

    # 🔹 RAG機能：拡張jsontableディレクティブ
    app.add_directive("enhanced-jsontable", EnhancedJsonTableDirective)

    # パフォーマンス制限の設定値追加
    app.add_config_value(
        "jsontable_max_rows",
        DEFAULT_MAX_ROWS,
        "env",  # 環境変更時に再ビルド
        [int],  # 型検証
    )

    return {
        "version": __version__,
        "parallel_read_safe": True,  # 並列読み取り安全
        "parallel_write_safe": True,  # 並列書き込み安全
    }
