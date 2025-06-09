# sphinxcontrib-jsontable

[![Tests](https://github.com/sasakama-code/sphinxcontrib-jsontable/actions/workflows/ci.yml/badge.svg)](https://github.com/sasakama-code/sphinxcontrib-jsontable/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/sasakama-code/sphinxcontrib-jsontable/graph/badge.svg)](https://codecov.io/gh/sasakama-code/sphinxcontrib-jsontable)
[![Python](https://img.shields.io/pypi/pyversions/sphinxcontrib-jsontable.svg)](https://pypi.org/project/sphinxcontrib-jsontable/)

**言語:** [English](README.md) | [日本語](README_ja.md)

JSONデータを構造化テーブルとしてレンダリングするSphinx拡張機能です。**RAG (Retrieval Augmented Generation)** の高度な機能を搭載し、**PLaMo-Embedding-1B** に最適化された日本語処理機能を特徴とします。

## 🚀 v0.3.0の新機能

✨ **RAG統合** - 自動メタデータ生成付き`enhanced-jsontable`ディレクティブ  
🇯🇵 **日本語エンティティ認識** - 人名、地名、組織名、ビジネス用語のネイティブサポート  
📤 **マルチフォーマット出力** - JSON-LD、OpenSearch、PLaMo対応形式  
🤖 **PLaMo-Embedding-1B統合** - 日本語テキスト用の1024次元ベクトル生成  

### 📚 **クイックスタート・ドキュメント**
- **🚀 [5分クイックスタート](docs/v0.3.0_quick_start.md)** - 新機能をすぐに使い始める
- **🎓 [機能ガイド](docs/v0.3.0_feature_tutorial.md)** - 実例付き完全リファレンス

## 背景・動機

近年、Retrieval Augmented Generation（RAG）のデータソースとしてドキュメントを活用する傾向が強まっています。しかし、ドキュメント内の表形式データは、RAGシステムに取り込まれる過程で構造的な関連性を失うことが多く、元の構造化データが持つ価値を十分に活用できないという課題がありました。

この背景から、**sphinxcontrib-jsontable v0.3.0** は構造化データを意味のあるテーブルとしてSphinx生成ドキュメントに直接埋め込み、可読性とセマンティック理解を効果的に両立させる高度なRAG機能を開発しました。PLaMo-Embedding-1Bとの統合により、日本語特化RAGドキュメントシステムを提供しています。

## インストール

```bash
pip install sphinxcontrib-jsontable
```

## クイックスタート

### 1. 拡張機能を有効化
```python
# conf.py
extensions = ['sphinxcontrib.jsontable']
```

### 2. 基本的な使用方法
```rst
.. jsontable:: data/users.json
   :header:
```

### 3. 新しいRAG機能
```rst
.. enhanced-jsontable:: data/companies.json
   :header:
   :entity-recognition: japanese
   :export-format: opensearch
```

## コア機能

- **従来のテーブルレンダリング** - JSONファイルとインラインデータをHTMLテーブルに変換
- **日本語エンティティ認識** - 人名、地名、組織名の自動検出
- **多形式エクスポート** - 検索エンジンとAIシステム用の最適化ファイル生成
- **エンタープライズセキュリティ** - パス保護、パフォーマンス制限、メモリセーフ処理

## 使用例

- **ビジネスインテリジェンス** - 日本語企業データの自動エンティティ認識
- **技術文書** - 検索最適化付きAPI仕様書
- **ナレッジマネジメント** - RAGシステム用のセマンティックデータ抽出

## コントリビューション

コントリビューションを歓迎します！開発セットアップとガイドラインについては [CONTRIBUTING.md](CONTRIBUTING.md) をご覧ください。

## ライセンス・サードパーティコンポーネント

本プロジェクトはMITライセンスの下で公開されています。詳細は [LICENSE](LICENSE) をご覧ください。

PLaMo-Embedding-1Bモデルを含む全サードパーティ依存関係のライセンス情報については [LICENSES.md](LICENSES.md) をご覧ください。全コンポーネントは商用利用承認済みで、詳細なコンプライアンス情報を提供しています。