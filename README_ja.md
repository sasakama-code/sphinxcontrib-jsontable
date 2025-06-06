# sphinxcontrib-jsontable

[![Tests](https://github.com/sasakama-code/sphinxcontrib-jsontable/actions/workflows/ci.yml/badge.svg)](https://github.com/sasakama-code/sphinxcontrib-jsontable/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/sasakama-code/sphinxcontrib-jsontable/graph/badge.svg)](https://codecov.io/gh/sasakama-code/sphinxcontrib-jsontable)
[![Python](https://img.shields.io/pypi/pyversions/sphinxcontrib-jsontable.svg)](https://pypi.org/project/sphinxcontrib-jsontable/)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/sasakama-code/sphinxcontrib-jsontable)

**言語:** [English](README.md) | [日本語](README_ja.md)

JSONデータ（ファイルまたはインラインコンテンツ）を美しくフォーマットされたreStructuredTextテーブルとしてレンダリングする強力なSphinx拡張機能です。構造化データ、APIサンプル、設定リファレンス、データ駆動型コンテンツを表示するドキュメントに最適です。

## 背景・動機

近年、Retrieval Augmented Generation（RAG）のデータソースとしてドキュメントを活用する傾向が強まっています。しかし、ドキュメント内の表形式データは、RAGシステムに取り込まれる過程で構造的な関連性を失うことが多く、元の構造化データが持つ価値を十分に活用できないという課題がありました。

このような背景から、JSONなどの構造化データをSphinxで生成されるドキュメントに直接、意味のあるテーブルとして埋め込むことで、可読性とデータソースとしての価値を効果的に両立させることを目的として、sphinxcontrib-jsontableが開発されました。

## 機能

✨ **柔軟なデータソース**
* Sphinxプロジェクト内のJSONファイルの読み込み
* ドキュメントに直接JSONを埋め込み
* 安全なパス解決機能付きの相対ファイルパス対応

📊 **複数のデータ形式**
* JSONオブジェクト（単一または配列）
* オプションヘッダー付きの2次元配列
* 自動文字列変換機能付きの混合データ型
* ネストされたデータ構造（適切にフラット化）

🎛️ **カスタマイズ可能な出力**
* 自動キー抽出機能付きのオプションヘッダー行
* 大規模データセット用の行制限
* カスタムファイルエンコーディング対応
* レスポンシブテーブルフォーマット

🔒 **堅牢で安全**
* パストラバーサル攻撃防止
* 包括的なエラーハンドリング
* エンコーディング検証
* デバッグ用詳細ログ

⚡ **パフォーマンス最適化**
* 大量データセットの自動行制限（デフォルト10,000行）
* 設定可能なパフォーマンス制限
* メモリ安全な処理
* 大量データ検出時のユーザーフレンドリーな警告

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

## クイックスタート

### 1. 拡張機能を有効化

`conf.py`に追加：

```python
extensions = [
    # ... その他の拡張機能
    'sphinxcontrib.jsontable',
]

# オプション: パフォーマンス制限を設定
jsontable_max_rows = 5000  # デフォルト: 10000
```

### 2. サンプルデータを作成

`data/users.json`を作成：
```json
[
  {
    "id": 1,
    "name": "田中太郎",
    "email": "tanaka@example.com",
    "department": "エンジニアリング",
    "active": true
  },
  {
    "id": 2,
    "name": "佐藤花子",
    "email": "sato@example.com", 
    "department": "マーケティング",
    "active": false
  }
]
```

### 3. ドキュメントに追加

**reStructuredText (.rst) の場合：**
```rst
ユーザーデータベース
==================

.. jsontable:: data/users.json
   :header:
   :limit: 10
```

**Markdown（myst-parser使用）の場合：**
````markdown
# ユーザーデータベース

```{jsontable} data/users.json
:header:
:limit: 10
```
````

### 4. ドキュメントをビルド

```bash
sphinx-build -b html docs/ build/html/
```

## 包括的な使用ガイド

### データ形式サポート

#### オブジェクトの配列（最も一般的）

データベースレコード、APIレスポンス、設定リストに最適：

```json
[
  {"name": "Redis", "port": 6379, "ssl": false},
  {"name": "PostgreSQL", "port": 5432, "ssl": true},
  {"name": "MongoDB", "port": 27017, "ssl": true}
]
```

```rst
.. jsontable:: data/services.json
   :header:
```

**出力：** オブジェクトキー（name、port、ssl）から自動的にヘッダーを生成。

#### ヘッダー付き2次元配列

CSV形式のデータ、レポート、マトリックスに最適：

```json
[
  ["サービス", "ポート", "プロトコル", "状態"],
  ["HTTP", 80, "TCP", "アクティブ"],
  ["HTTPS", 443, "TCP", "アクティブ"],
  ["SSH", 22, "TCP", "非アクティブ"]
]
```

```rst
.. jsontable:: data/ports.json
   :header:
```

**出力：** 最初の行がテーブルヘッダーになります。

#### ヘッダーなし2次元配列

シンプルな表形式データ：

```json
[
  ["月曜日", "晴れ", "24°C"],
  ["火曜日", "曇り", "20°C"],
  ["水曜日", "雨", "17°C"]
]
```

```rst
.. jsontable:: data/weather.json
```

**出力：** すべての行がデータとして扱われます（ヘッダーなし）。

#### 単一オブジェクト

設定オブジェクト、設定、メタデータ：

```json
{
  "database_host": "localhost",
  "database_port": 5432,
  "debug_mode": true,
  "max_connections": 100
}
```

```rst
.. jsontable:: data/config.json
   :header:
```

**出力：** キーが1つの列、値が別の列になります。

### ディレクティブオプション一覧

| オプション | 型 | デフォルト | 説明 | 例 |
|------------|----|-----------|----|---|
| `header` | フラグ | off | 最初の行をテーブルヘッダーとして含める | `:header:` |
| `encoding` | 文字列 | `utf-8` | JSONファイルのファイルエンコーディング | `:encoding: utf-16` |
| `limit` | 正の整数/0 | 自動 | 表示する最大行数（0=無制限） | `:limit: 50` |

## 設定オプション

`conf.py`でsphinxcontrib-jsontableを設定：

### パフォーマンス設定

```python
# 自動制限が有効になる最大行数（デフォルト: 10000）
jsontable_max_rows = 5000

# 異なる用途向けの設定例:

# 主に小さなデータセット用のドキュメント
jsontable_max_rows = 100

# 大量データ用のドキュメント
jsontable_max_rows = 50000

# 自動制限を完全に無効化（Webデプロイには非推奨）
# jsontable_max_rows = None  # デフォルトで無制限使用
```

### 高度な例

#### 自動パフォーマンス保護

`:limit:`が指定されていない場合、拡張機能は自動的に大量データセットから保護します：

```rst
.. jsontable:: data/huge_dataset.json
   :header:

# データセットが10,000行を超える場合、自動的に最初の10,000行を警告付きで表示
# ユーザーには以下が表示されます: "大量データセット検出（25,000行）。パフォーマンスのため
# 最初の10,000行を表示。:limit:オプションでカスタマイズしてください。"
```

#### 明示的な無制限処理

サイズに関係なく全データを表示する必要がある場合：

```rst
.. jsontable:: data/large_but_manageable.json
   :header:
   :limit: 0

# ⚠️ 全行表示 - Webデプロイには注意が必要
```

#### ページネーション付き大規模データセット

大規模データセットでのパフォーマンスと可読性のため：

```rst
.. jsontable:: data/large_dataset.json
   :header:
   :limit: 100

.. note::
   このテーブルは50,000+件のうち最初の100エントリを表示しています。
   完全なデータセットをダウンロード：:download:`large_dataset.json <data/large_dataset.json>`
```

#### 非UTF8エンコーディング

レガシーシステムや特定の文字エンコーディングでの作業：

```rst
.. jsontable:: data/legacy_data.json
   :encoding: iso-8859-1
   :header:
```

#### サンプル用インラインJSON

APIドキュメント、サンプル、チュートリアルに最適：

```rst
APIレスポンス形式
================

ユーザーエンドポイントは以下の形式でデータを返します：

.. jsontable::

   {
     "user_id": 12345,
     "username": "tanaka_taro",
     "email": "tanaka@example.com",
     "created_at": "2024-01-15T10:30:00Z",
     "is_verified": true,
     "profile": {
       "first_name": "太郎",
       "last_name": "田中",
       "avatar_url": "https://example.com/avatar.jpg"
     }
   }
```

#### 複雑なネストされたデータ

ネストされたJSONの場合、拡張機能は適切にフラット化します：

```rst
.. jsontable::

   [
     {
       "id": 1,
       "name": "製品A",
       "category": {"name": "電子機器", "id": 10},
       "tags": ["人気", "セール"],
       "price": 99.99
     }
   ]
```

**注意：** 値内のオブジェクトと配列は文字列表現に変換されます。

### 統合例

#### Sphinx Tabsとの連携

sphinx-tabsと組み合わせて多形式ドキュメント作成：

```rst
.. tabs::

   .. tab:: JSONデータ

      .. jsontable:: data/api_response.json
         :header:

   .. tab:: 生JSON

      .. literalinclude:: data/api_response.json
         :language: json
```

#### コードブロックとの連携

リクエスト/レスポンス例でAPIエンドポイントを文書化：

```rst
ユーザー取得エンドポイント
========================

**リクエスト：**

.. code-block:: http

   GET /api/v1/users HTTP/1.1
   Host: api.example.com
   Authorization: Bearer <token>

**レスポンス：**

.. jsontable::

   [
     {
       "id": 1,
       "username": "alice",
       "email": "alice@example.com",
       "status": "active"
     },
     {
       "id": 2, 
       "username": "bob",
       "email": "bob@example.com",
       "status": "inactive"
     }
   ]
```

#### MyST Markdownでの使用

モダンなドキュメントワークフロー用の完全なMyST Markdownサポート：

````markdown
# 設定リファレンス

## データベース設定

```{jsontable} config/database.json
:header:
:encoding: utf-8
```

## 機能フラグ

```{jsontable}
[
  {"feature": "ダークモード", "enabled": true, "rollout": "100%"},
  {"feature": "新ダッシュボード", "enabled": false, "rollout": "0%"},
  {"feature": "高度な検索", "enabled": true, "rollout": "50%"}
]
```
````

### ファイル構成のベストプラクティス

#### 推奨ディレクトリ構造

```
docs/
├── conf.py
├── index.rst
├── data/
│   ├── users.json
│   ├── products.json
│   ├── config/
│   │   ├── database.json
│   │   └── features.json
│   └── examples/
│       ├── api_responses.json
│       └── error_codes.json
└── api/
    └── endpoints.rst
```

#### 命名規則

- 説明的なファイル名を使用：`data1.json`ではなく`user_permissions.json`
- 関連データをサブディレクトリにグループ化：`config/`、`examples/`、`test_data/`
- 適切な場合はバージョンや日付を含める：`api_v2_responses.json`

### パフォーマンス考慮事項

#### 大量データセットの自動保護

拡張機能は自動的にパフォーマンス問題から保護します：

- **デフォルト制限**: デフォルトで最大10,000行
- **スマート検出**: データセットサイズを自動推定
- **ユーザー警告**: 制限が適用された際の明確なメッセージ
- **設定可能**: `jsontable_max_rows`設定で制限を調整

#### パフォーマンス動作

| データセットサイズ | デフォルト動作 | 必要なユーザーアクション |
|-------------------|---------------|----------------------|
| ≤ 10,000行 | ✅ 全行表示 | なし |
| > 10,000行 | ⚠️ 自動制限+警告 | `:limit:`でカスタマイズ |
| `:limit: 0`指定時 | 🚨 全表示（無制限） | 注意して使用 |

#### ビルド時間の最適化

**小さなデータセット（< 1,000行）:**
```rst
.. jsontable:: data/small_dataset.json
   :header:
   # 制限不要 - 高速処理
```

**中規模データセット（1,000-10,000行）:**
```rst
.. jsontable:: data/medium_dataset.json
   :header:
   # 自動保護適用 - 良好なパフォーマンス
```

**大規模データセット（> 10,000行）:**
```rst
.. jsontable:: data/large_dataset.json
   :header:
   :limit: 100
   # 予測可能なパフォーマンスのため明示的制限を推奨
```

#### メモリ考慮事項

**安全な設定:**
```python
# 保守的（低メモリ環境向け）
jsontable_max_rows = 1000

# バランス型（デフォルト - ほとんどの用途に適用）
jsontable_max_rows = 10000

# アグレッシブ（高メモリ環境のみ）
jsontable_max_rows = 100000
```

**メモリ使用量ガイドライン:**
- **~1MB JSON**: ~1,000-5,000行（全環境で安全）
- **~10MB JSON**: ~10,000-50,000行（十分なメモリが必要）
- **>50MB JSON**: データ前処理またはデータベースソリューションを検討

#### 大量データのベストプラクティス

1. **適切な制限を使用**:
   ```rst
   .. jsontable:: data/sales_data.json
      :header:
      :limit: 50
      
   *上位50件の売上記録を表示。完全データはソースファイルで利用可能。*
   ```

2. **データ前処理を検討**:
   - 大きなファイルを論理的なチャンクに分割
   - ドキュメント用のサマリーデータセットを作成
   - 静的ファイルの代わりにデータベースビューを使用

3. **ビルドパフォーマンスの最適化**:
   ```python
   # conf.py内 - 大規模プロジェクトの高速ビルド
   jsontable_max_rows = 100
   ```

4. **制限されたデータのコンテキスト提供**:
   ```rst
   .. jsontable:: data/user_activity.json
      :header:
      :limit: 20
      
   .. note::
      このテーブルは最近のアクティビティのみ表示。完全ログは
      :doc:`admin-dashboard`参照、または
      :download:`完全データセット <data/user_activity.json>`をダウンロード。
   ```

### 移行ガイド

#### 以前のバージョンからのアップグレード

**破壊的変更なし**: 既存のドキュメントは変更なしで動作継続。

**利用可能な新機能**:
```rst
# 以前: 大量データセットには手動制限が必要
.. jsontable:: large_data.json
   :header:
   :limit: 100

# 以降: 自動保護（手動制限も継続サポート）
.. jsontable:: large_data.json
   :header:
   # ユーザー警告付きで自動的に10,000行に制限
```

**推奨設定更新**:
```python
# カスタマイズされた動作のためconf.pyに追加
jsontable_max_rows = 5000  # ニーズに応じて調整
```

### トラブルシューティング

#### 一般的な問題

**エラー：「No JSON data source provided」**
```rst
# ❌ ファイルパスまたはコンテンツが不足
.. jsontable::

# ✅ ファイルパスまたはインラインコンテンツを提供  
.. jsontable:: data/example.json
```

**エラー：「JSON file not found」**
- ソースディレクトリからの相対ファイルパスを確認
- ファイルが存在し、正しい権限があることを確認
- ファイル名のタイプミスがないことを確認

**エラー：「Invalid inline JSON」**
- オンラインバリデーターでJSON構文を検証
- 末尾カンマ、引用符なしキーをチェック
- 特殊文字の適切なエスケープを確認

**パフォーマンス警告**
```
WARNING: 大量データセット検出（25,000行）。パフォーマンスのため最初の10,000行を表示。
```
**解決方法:**
- 明示的な`:limit:`オプション追加: `:limit: 50`
- 無制限に`:limit: 0`使用（必要時）
- グローバル制限増加: `jsontable_max_rows = 25000`
- より小さなファイル用のデータ前処理を検討

**エンコーディング問題**
```rst
# 非UTF8ファイルの場合
.. jsontable:: data/legacy.json
   :encoding: iso-8859-1
```

**空のテーブル**
- JSONファイルが空またはnullでないかチェック
- JSON構造を確認（配列またはオブジェクトである必要）
- 自動制限がデータを隠していないかチェック

#### デバッグモード

`conf.py`で詳細ログを有効化：

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Sphinx固有のログの場合
extensions = ['sphinxcontrib.jsontable']

# パフォーマンス監視
jsontable_max_rows = 1000  # デバッグ用低制限
```

#### 設定テスト

セットアップを確認するシンプルなテストファイルを作成：

```json
[{"test": "success", "status": "ok"}]
```

```rst
.. jsontable:: test.json
   :header:
```

### セキュリティ考慮事項

#### パストラバーサル攻撃の防止

拡張機能は自動的にディレクトリトラバーサル攻撃を防止します：

```rst
# ❌ これはブロックされます
.. jsontable:: ../../etc/passwd

# ✅ 安全な相対パスのみ
.. jsontable:: data/safe_file.json
```

#### ファイルアクセス

- Sphinxソースディレクトリ内のファイルのみアクセス可能
- ネットワークURLや絶対システムパスは許可されません
- システムによってファイル権限が尊重されます

#### パフォーマンスセキュリティ

- デフォルト制限が偶発的なリソース枯渇を防止
- メモリ使用量は設定可能な制限で制約
- 大量データセット警告が意図しないパフォーマンス影響を防止

### 移行ガイド

#### 他の拡張機能から

**sphinx-jsonschemaから：**
- `.. jsonschema::`を`.. jsontable::`に置換
- スキーマ検証オプションを削除
- 必要に応じて`:header:`オプションを追加

**カスタムソリューションから：**
- データをJSON形式にエクスポート
- カスタムテーブル生成を`.. jsontable::`に置換
- ファイルパスをソースディレクトリ相対に更新

#### バージョン互換性

- **Sphinx：** 3.0+（推奨：4.0+）
- **Python：** 3.10+（推奨：3.11+）
- **Docutils：** 0.14+

### APIリファレンス

#### コアクラス

**`JsonTableDirective`**
- メインのSphinxディレクティブクラス
- オプション解析と実行を処理
- データ読み込み、変換、レンダリングを調整

**`JsonDataLoader`**  
- ファイルまたはインラインコンテンツからJSONを読み込み
- エンコーディングとファイルパスを検証
- 安全なファイルアクセスを提供

**`TableConverter`**
- JSON構造を2次元テーブルデータに変換
- 異なるデータ形式を処理（オブジェクト、配列、混合）
- ヘッダー抽出と行制限を管理
- 自動パフォーマンス制限を適用

**`TableBuilder`**
- Docutilsテーブルノードを生成
- ヘッダー/ボディ付きの適切なテーブル構造を作成
- セルフォーマットとパディングを処理

#### エラーハンドリング

すべてのエラーは`JsonTableError`から継承：
- ファイルアクセスエラー
- JSON解析エラー  
- 無効なデータ構造エラー
- パストラバーサル試行

### コントリビューション

コントリビューションを歓迎します！詳細は[CONTRIBUTING.md](CONTRIBUTING.md)を参照：
- 開発環境セットアップ
- コードスタイルガイドライン
- テスト手順
- プルリクエストプロセス

#### 開発環境セットアップ

```bash
git clone https://github.com/sasakama-code/sphinxcontrib-jsontable.git
cd sphinxcontrib-jsontable
pip install -e ".[dev]"
pytest
```

#### テスト実行

```bash
# 全テスト実行
pytest

# カバレッジ付き実行
pytest --cov=sphinxcontrib.jsontable

# 特定テスト実行
pytest tests/test_directives.py::test_json_table_basic
```

### サンプルリポジトリ

[`examples/`](examples/)ディレクトリで以下を参照：
- 完全なSphinxプロジェクトセットアップ
- 様々なデータ形式の例  
- 他の拡張機能との統合
- 高度な設定例

```bash
cd examples/
sphinx-build -b html . _build/html/
```

### 開発ツール

[`scripts/`](scripts/)ディレクトリには、パフォーマンス機能開発時に使用された開発・分析ツールが含まれています：

- **`performance_benchmark.py`** - パフォーマンス測定・分析ツール
- **`memory_analysis.py`** - 異なるデータセットサイズのメモリ使用量分析
- **`competitive_analysis.py`** - 業界標準調査とベストプラクティス
- **`validate_ci_tests.py`** - CI環境テスト・検証
- **`test_integration.py`** - 包括的統合テスト

これらのツールは、パフォーマンス制限の科学的基盤確立と企業レベルの信頼性確保において重要な役割を果たしました。継続的なパフォーマンス監視と分析に活用できます。

```bash
# パフォーマンス分析実行
python scripts/performance_benchmark.py

# CI環境検証
python scripts/validate_ci_tests.py
```

### 変更履歴

詳細なバージョン履歴とリリースノートは[CHANGELOG.md](CHANGELOG.md)を参照してください。

### ライセンス

このプロジェクトは[MITライセンス](LICENSE)の下でライセンスされています。

### サポート

- **ドキュメント：** [GitHub Pages](https://sasakama-code.github.io/sphinxcontrib-jsontable/)
- **問題報告：** [GitHub Issues](https://github.com/sasakama-code/sphinxcontrib-jsontable/issues)
- **ディスカッション：** [GitHub Discussions](https://github.com/sasakama-code/sphinxcontrib-jsontable/discussions)
