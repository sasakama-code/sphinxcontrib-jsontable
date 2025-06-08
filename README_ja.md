# sphinxcontrib-jsontable

[![Tests](https://github.com/sasakama-code/sphinxcontrib-jsontable/actions/workflows/ci.yml/badge.svg)](https://github.com/sasakama-code/sphinxcontrib-jsontable/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/sasakama-code/sphinxcontrib-jsontable/graph/badge.svg)](https://codecov.io/gh/sasakama-code/sphinxcontrib-jsontable)
[![Python](https://img.shields.io/pypi/pyversions/sphinxcontrib-jsontable.svg)](https://pypi.org/project/sphinxcontrib-jsontable/)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/sasakama-code/sphinxcontrib-jsontable)

**言語:** [English](README.md) | [日本語](README_ja.md)

JSONデータを構造化テーブルとしてレンダリングする次世代Sphinx拡張機能です。**RAG (Retrieval Augmented Generation)** の高度な機能を搭載し、**PLaMo-Embedding-1B** に最適化された世界クラスの日本語処理機能を特徴とする、世界初の日本語特化RAG対応ドキュメントシステムです。

## 🚀 v0.3.0の新機能

### 🌟 **革新的なRAG統合**
- **Enhanced Directive**: 自動メタデータ生成付き`enhanced-jsontable`
- **日本語エンティティ認識**: 人名、地名、組織名、ビジネス用語のネイティブサポート
- **PLaMo-Embedding-1B統合**: 日本語テキスト用の1024次元ベクトル生成
- **マルチフォーマット出力**: JSON-LD、OpenSearch、PLaMo対応形式

### 🎯 **エンタープライズグレード機能**
- **自動検索ファセット**: 四分位数ベースの統計分析
- **セマンティック分割**: 日本語最適化のコンテンツセグメンテーション
- **ビジネス用語強化**: 日本語ビジネス文書専用処理
- **ベクトル検索インデックス**: プロダクション対応の検索インフラ

## 背景・動機

近年、Retrieval Augmented Generation（RAG）のデータソースとしてドキュメントを活用する傾向が強まっています。しかし、ドキュメント内の表形式データは、RAGシステムに取り込まれる過程で構造的な関連性を失うことが多く、元の構造化データが持つ価値を十分に活用できないという課題がありました。

この背景から、**sphinxcontrib-jsontable v0.3.0** は構造化データを意味のあるテーブルとしてSphinx生成ドキュメントに直接埋め込み、可読性とセマンティック理解を効果的に両立させる高度なRAG機能を開発しました。PLaMo-Embedding-1Bとの統合により、世界初の日本語特化RAGドキュメントシステムとなっています。

## 🌟 コア機能

### ✨ **従来のテーブルレンダリング**
* Sphinxプロジェクト内のJSONファイル読み込み
* ドキュメントに直接JSONを埋め込み
* 安全なパス解決機能付き相対ファイルパス対応
* 複数データ形式（オブジェクト、配列、ネスト構造）
* ヘッダーと行制限付きカスタマイズ可能出力

### 🧠 **高度なRAG機能 (v0.3.0)**
* **自動メタデータ抽出**: スキーマ分析、統計、データ品質評価
* **日本語エンティティ認識**:
  - 人名 (Personal names): 田中太郎、佐藤花子
  - 地名 (Place names): 東京都、大阪市、新宿駅
  - 組織名 (Organizations): 株式会社○○、○○部
  - ビジネス用語 (Business terms): 売上高、営業利益
* **セマンティック分割**: 最適な検索のためのインテリジェントなコンテンツセグメンテーション
* **ベクトル処理**: 日本語テキスト用PLaMo-Embedding-1B統合
* **検索インデックス生成**: 検索最適化インデックスの自動作成

### 🔍 **マルチフォーマット出力**
* **JSON-LD**: セマンティックWeb標準形式
* **OpenSearch**: Elasticsearch/OpenSearchマッピング
* **PLaMo対応**: PLaMo-Embedding-1B最適化形式
* **カスタム**: ユーザー定義出力形式

### 🔒 **エンタープライズセキュリティ & パフォーマンス**
* 包括的セキュリティ対策付きパストラバーサル保護
* 大規模データセットの自動パフォーマンス最適化
* 設定可能制限付きメモリ安全処理
* 日本語Unicode正規化と文字エンコーディングサポート

## インストール

### PyPIから
```bash
pip install sphinxcontrib-jsontable
```

### ソースから
```bash
git clone https://github.com/sasakama-code/sphinxcontrib-jsontable.git
cd sphinxcontrib-jsontable
pip install -e .
```

### 依存関係
- **Python**: 3.10+ (推奨: 3.11+)
- **Sphinx**: 3.0+ (推奨: 4.0+)
- **NumPy**: 2.2.6+ (高度統計分析用)

## クイックスタート

### 1. 拡張機能を有効化

`conf.py`に追加:

```python
extensions = [
    # ... その他の拡張機能
    'sphinxcontrib.jsontable',
]

# オプション: パフォーマンス制限を設定
jsontable_max_rows = 5000  # デフォルト: 10000
```

### 2. 基本的な使い方（レガシー互換）

`data/users.json`を作成:
```json
[
  {
    "id": 1,
    "name": "Alice Johnson",
    "email": "alice@example.com",
    "department": "Engineering",
    "active": true
  },
  {
    "id": 2,
    "name": "Bob Smith", 
    "email": "bob@example.com",
    "department": "Marketing",
    "active": false
  }
]
```

**reStructuredText (.rst)で:**
```rst
ユーザーデータベース
===================

.. jsontable:: data/users.json
   :header:
   :limit: 10
```

### 3. RAG対応強化版の使い方 (v0.3.0)

**RAG機能付き日本語ビジネス文書の場合:**

```rst
RAG対応日本語企業データ
=======================

.. enhanced-jsontable:: data/japanese_companies.json
   :header:
   :rag-metadata: true
   :export-format: json-ld,opensearch,plamo-ready
   :entity-recognition: japanese
   :facet-generation: auto
   :semantic-chunking: business
```

**日本語データサンプル:**
```json
[
  {
    "会社名": "株式会社テクノロジー",
    "代表者": "田中太郎",
    "所在地": "東京都新宿区",
    "業種": "情報通信業",
    "売上高": "50億円",
    "従業員数": "250名"
  },
  {
    "会社名": "サンプル工業株式会社",
    "代表者": "佐藤花子",
    "所在地": "大阪市中央区", 
    "業種": "製造業",
    "売上高": "120億円",
    "従業員数": "480名"
  }
]
```

### 4. ドキュメントをビルド

```bash
sphinx-build -b html docs/ build/html/
```

## RAG統合ガイド (v0.3.0)

### 拡張ディレクティブオプション

| オプション | 型 | デフォルト | 説明 | 例 |
|-----------|-----|----------|-----|-----|
| `rag-metadata` | フラグ | off | RAGメタデータ生成を有効化 | `:rag-metadata:` |
| `export-format` | 文字列 | none | エクスポート形式（カンマ区切り） | `:export-format: json-ld,opensearch` |
| `entity-recognition` | 文字列 | off | エンティティ認識を有効化 | `:entity-recognition: japanese` |
| `facet-generation` | 文字列 | off | 検索ファセット自動生成 | `:facet-generation: auto` |
| `semantic-chunking` | 文字列 | off | セマンティックコンテンツ分割 | `:semantic-chunking: business` |

### エクスポート形式

#### JSON-LD（セマンティックWeb）
```rst
.. enhanced-jsontable:: data/products.json
   :rag-metadata:
   :export-format: json-ld
```

**出力**: セマンティックマークアップ付き`products_metadata.jsonld`

#### OpenSearch/Elasticsearch
```rst
.. enhanced-jsontable:: data/logs.json
   :rag-metadata:
   :export-format: opensearch
```

**出力**: 最適化フィールドマッピング付き`logs_opensearch_mapping.json`

#### PLaMo対応形式
```rst
.. enhanced-jsontable:: data/japanese_text.json
   :rag-metadata:
   :export-format: plamo-ready
   :entity-recognition: japanese
```

**出力**: PLaMo-Embedding-1B最適化付き`japanese_text_plamo.json`

### 日本語エンティティ認識

拡張機能は日本語エンティティを自動検出・分類します:

```rst
.. enhanced-jsontable:: data/japanese_data.json
   :entity-recognition: japanese
   :rag-metadata:
```

**サポートされるエンティティ型:**
- **人名**: 田中太郎、佐藤花子、山田次郎
- **地名**: 東京都、大阪市、新宿駅、渋谷区
- **組織名**: 株式会社○○、○○部、経済産業省
- **ビジネス用語**: 売上高、営業利益、ROI、KPI

### 自動検索ファセット

インテリジェントな検索ファセットを自動生成:

```rst
.. enhanced-jsontable:: data/sales_data.json
   :facet-generation: auto
   :rag-metadata:
```

**生成されるファセット:**
- **カテゴリカル**: テキストフィールドの自動グループ化
- **数値**: 数値データの四分位数ベース範囲
- **時系列**: スマートな日付/時間期間検出
- **エンティティベース**: 日本語エンティティ分類ファセット

### セマンティック分割戦略

コンテンツに最適な分割を選択:

```rst
.. enhanced-jsontable:: data/documents.json
   :semantic-chunking: business
   :entity-recognition: japanese
```

**利用可能な戦略:**
- `business`: 日本語ビジネス文書最適化
- `technical`: 技術文書・マニュアル
- `general`: 汎用コンテンツ分割
- `conversational`: チャットログ・コミュニケーション

## 高度なRAG例

### エンタープライズビジネスインテリジェンス

```rst
四半期ビジネスレポート
=====================

.. enhanced-jsontable:: data/quarterly_report.json
   :header:
   :rag-metadata: true
   :export-format: json-ld,opensearch
   :entity-recognition: japanese
   :facet-generation: auto
   :semantic-chunking: business

.. note::
   このデータは以下のために自動処理されます:
   
   - **エンティティ認識**: 会社名、役員名、所在地
   - **検索ファセット**: 売上範囲、部署カテゴリ、地域区分
   - **ベクトル埋め込み**: セマンティック検索用PLaMo-Embedding-1B
   - **エクスポート形式**: ナレッジグラフ用JSON-LD、分析用OpenSearch
```

### RAG付き技術文書

```rst
API文書
=======

.. enhanced-jsontable:: data/api_endpoints.json
   :header:
   :rag-metadata: true
   :export-format: plamo-ready
   :semantic-chunking: technical
   :facet-generation: auto

.. enhanced-jsontable:: data/error_codes.json
   :header:
   :rag-metadata: true
   :export-format: opensearch
   :semantic-chunking: technical
```

### 多言語コンテンツ処理

```rst
グローバルオフィスディレクトリ
=============================

.. enhanced-jsontable:: data/global_offices.json
   :header:
   :rag-metadata: true
   :entity-recognition: japanese
   :export-format: json-ld,opensearch,plamo-ready
   :facet-generation: auto
   :semantic-chunking: business
```

## 従来の使い方（後方互換）

既存のドキュメントはすべて変更なく動作します:

### データ形式サポート

#### オブジェクト配列（最も一般的）
```json
[
  {"name": "Redis", "port": 6379, "ssl": false},
  {"name": "PostgreSQL", "port": 5432, "ssl": true},
  {"name": "MongoDB", "port": 27017, "ssl": true}
]
```

#### ヘッダー付き2次元配列
```json
[
  ["Service", "Port", "Protocol", "Status"],
  ["HTTP", 80, "TCP", "Active"],
  ["HTTPS", 443, "TCP", "Active"],
  ["SSH", 22, "TCP", "Inactive"]
]
```

#### 単一オブジェクト
```json
{
  "database_host": "localhost",
  "database_port": 5432,
  "debug_mode": true,
  "max_connections": 100
}
```

### 従来のディレクティブオプション

| オプション | 型 | デフォルト | 説明 | 例 |
|-----------|-----|----------|-----|-----|
| `header` | フラグ | off | 最初の行をテーブルヘッダーに | `:header:` |
| `encoding` | 文字列 | `utf-8` | JSONファイルのファイルエンコーディング | `:encoding: utf-16` |
| `limit` | 正整数/0 | 自動 | 表示する最大行数（0=無制限） | `:limit: 50` |

## パフォーマンス & セキュリティ

### 自動パフォーマンス保護

大規模データセットに対して、拡張機能はインテリジェントな保護を提供:

```rst
.. jsontable:: data/huge_dataset.json
   :header:
   # データセット > 10,000行の場合、警告付きで最初の10,000行を自動表示
```

### セキュリティ機能

- **パストラバーサル保護**: Sphinxソースディレクトリ内のファイルのみ
- **安全なファイルアクセス**: 包括的な検証とサニタイゼーション
- **メモリ保護**: リソース枯渇を防ぐ設定可能制限
- **日本語Unicodeセキュリティ**: 適切な正規化と検証

### 設定オプション

```python
# conf.py - パフォーマンスチューニング
jsontable_max_rows = 5000  # デフォルト: 10000

# 設定例:
# 小規模ドキュメントサイト用
jsontable_max_rows = 100

# 大規模データ重視ドキュメント用
jsontable_max_rows = 50000

# 開発/テスト用
jsontable_max_rows = 1000
```

## アーキテクチャ概要

### コアコンポーネント

**レガシーシステム（後方互換）:**
- `JsonTableDirective`: 元のテーブルレンダリング
- `JsonDataLoader`: セキュリティ検証付きファイル・コンテンツローディング
- `TableConverter`: JSONから2Dテーブル変換
- `TableBuilder`: Docutilsテーブルノード生成

**RAG強化システム (v0.3.0):**
- `EnhancedJsonTableDirective`: メタデータ生成付きRAG対応ディレクティブ
- `RAGMetadataExtractor`: JSONスキーマ分析と統計
- `SemanticChunker`: 日本語最適化コンテンツ分割
- `AdvancedMetadataGenerator`: エンティティ認識付き深層統計分析
- `SearchFacetGenerator`: 検索最適化用自動ファセット生成
- `MetadataExporter`: マルチフォーマット出力（JSON-LD、OpenSearch、PLaMo対応）
- `PLaMoVectorProcessor`: PLaMo-Embedding-1Bベクトル生成
- `IntelligentQueryProcessor`: セマンティッククエリ処理
- `SearchIndexGenerator`: ベクトル検索インデックス作成

### 統合パターン

#### モダンドキュメントツールとの連携

**MyST Markdown:**
````markdown
# 企業データベース

```{enhanced-jsontable} data/companies.json
:header:
:rag-metadata:
:entity-recognition: japanese
:export-format: json-ld
```
````

**Sphinx Tabs:**
```rst
.. tabs::

   .. tab:: テーブル表示
   
      .. enhanced-jsontable:: data/sales.json
         :header:
         :rag-metadata:
   
   .. tab:: 生データ
   
      .. literalinclude:: data/sales.json
         :language: json
```

#### 検索システムとの連携

**Elasticsearch統合:**
```rst
.. enhanced-jsontable:: data/products.json
   :export-format: opensearch
   :facet-generation: auto
   
# Elasticsearch直接インポート用products_opensearch_mapping.json生成
```

**ナレッジグラフ統合:**
```rst
.. enhanced-jsontable:: data/entities.json
   :export-format: json-ld
   :entity-recognition: japanese
   
# セマンティックWebアプリケーション用entities_metadata.jsonld生成
```

## 移行ガイド

### v0.2.xからv0.3.0へ

**互換性破綻なし**: 既存のドキュメントはすべて変更なく動作します。

**利用可能な新機能:**
```rst
# 以前 (v0.2.x) - 基本テーブルレンダリング
.. jsontable:: data/companies.json
   :header:

# 以後 (v0.3.0) - RAG機能付き強化版
.. enhanced-jsontable:: data/companies.json
   :header:
   :rag-metadata: true
   :entity-recognition: japanese
   :export-format: json-ld,opensearch
```

**推奨設定更新:**
```python
# v0.3.0機能用conf.py追加
extensions = [
    'sphinxcontrib.jsontable',  # jsontableとenhanced-jsontable両方を有効化
]

# オプション: データサイズに合わせて調整
jsontable_max_rows = 5000
```

### 他の拡張機能から

**sphinx-jsonschemaから:**
- `.. jsonschema::`を`.. jsontable::`または`.. enhanced-jsontable::`に置換
- スキーマ検証オプションを削除、RAGオプションを追加
- ファイルパスをソースディレクトリ相対に更新

## 開発・貢献

### 開発セットアップ

```bash
git clone https://github.com/sasakama-code/sphinxcontrib-jsontable.git
cd sphinxcontrib-jsontable
pip install -e ".[dev]"
```

### 品質保証

```bash
# コードフォーマット
ruff format

# リンティング
ruff check

# 型チェック
mypy sphinxcontrib/jsontable/

# テスト
pytest

# カバレッジレポート
pytest --cov=sphinxcontrib.jsontable --cov-report=html
```

### 貢献ガイドライン

貢献を歓迎します！詳細は[CONTRIBUTING.md](CONTRIBUTING.md)をご覧ください:
- 開発セットアップとワークフロー
- コードスタイルガイドライン
- テスト手順
- プルリクエストプロセス

## 例・ドキュメント

### 完全な例

[`examples/`](examples/)ディレクトリに含まれるもの:
- 完全なSphinxプロジェクトセットアップ
- 各種データ形式例
- RAG統合デモンストレーション
- 日本語コンテンツ処理例
- 高度な設定例

```bash
cd examples/
sphinx-build -b html . _build/html/
```

### 開発ツール

[`scripts/`](scripts/)ディレクトリにはエンタープライズグレードの開発ツールが含まれています:

- **`performance_benchmark.py`** - パフォーマンス測定・分析
- **`memory_analysis.py`** - 異なるデータセットサイズのメモリ使用量分析
- **`competitive_analysis.py`** - 業界標準研究・ベンチマーキング
- **`validate_ci_tests.py`** - CI環境テスト・検証
- **`knowledge_extraction.py`** - RAGメタデータ抽出ユーティリティ

これらのツールはパフォーマンス最適化とエンタープライズ信頼性の科学的基盤を提供します。

## サポート・コミュニティ

- **ドキュメント**: 完全ガイドとAPIリファレンス
- **イシュー**: [GitHub Issues](https://github.com/sasakama-code/sphinxcontrib-jsontable/issues)
- **ディスカッション**: [GitHub Discussions](https://github.com/sasakama-code/sphinxcontrib-jsontable/discussions)
- **変更履歴**: [CHANGELOG.md](CHANGELOG.md) 詳細バージョン履歴

## ライセンス

このプロジェクトは[MIT License](LICENSE)の下でライセンスされています。

---

## 🏆 プロジェクト状況

**sphinxcontrib-jsontable v0.3.0** は、従来のテーブルレンダリングと最先端RAG機能を組み合わせたドキュメンテーションツールの大きな進歩を表しています。世界クラスの日本語処理とPLaMo-Embedding-1B統合により、セマンティックドキュメントシステムの新基準を設定します。

**エンタープライズ対応**: 包括的テスト、セキュリティ検証、パフォーマンス最適化付きプロダクショングレード品質。

**将来対応**: 新興AIと検索技術との統合を想定した拡張可能アーキテクチャ。