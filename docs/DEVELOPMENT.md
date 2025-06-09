# RAG統合開発ワークフロー

## 🌿 ブランチ戦略

### ブランチ構造
```
main
├── feature/rag-integration (メインRAG統合ブランチ)
    ├── feature/rag-phase1-semantic-data (Phase 1: セマンティック構造化データ出力)
    ├── feature/rag-phase2-metadata-generation (Phase 2: RAG用メタデータ生成)
    └── feature/rag-phase3-plamo-integration (Phase 3: PLaMo-Embedding-1B統合)
```

### 開発フロー

#### Phase 1 開発 (Week 1-4)
```bash
# Phase 1 開発開始
git checkout feature/rag-phase1-semantic-data

# 開発作業
# - EnhancedJsonTableDirective実装
# - RAGMetadataExtractor実装  
# - SemanticChunker実装

# 完了時
git add .
git commit -m "Implement Phase 1: [specific feature]"
git push origin feature/rag-phase1-semantic-data

# Phase 1完了後、統合ブランチにマージ
git checkout feature/rag-integration
git merge feature/rag-phase1-semantic-data
git push origin feature/rag-integration
```

#### Phase 2 開発 (Week 5-6)
```bash
# Phase 2 開発開始
git checkout feature/rag-phase2-metadata-generation

# 開発作業
# - AdvancedMetadataGenerator実装
# - SearchFacetGenerator実装
# - MetadataExporter実装

# 完了時マージ
git checkout feature/rag-integration
git merge feature/rag-phase2-metadata-generation
git push origin feature/rag-integration
```

#### Phase 3 開発 (Week 7-8)
```bash
# Phase 3 開発開始
git checkout feature/rag-phase3-plamo-integration

# 開発作業
# - VectorProcessor（PLaMo-Embedding-1B）実装
# - SearchIndexGenerator実装

# 完了時マージ
git checkout feature/rag-integration
git merge feature/rag-phase3-plamo-integration
git push origin feature/rag-integration
```

#### 最終統合 (Week 8完了時)
```bash
# 全Phase完了後、mainブランチへPR作成
git checkout feature/rag-integration
# GitHub上でPull Request作成
# main ← feature/rag-integration
```

---

## 🔧 開発環境セットアップ

### 必要な依存関係

#### Phase 1 (AI API不要)
```bash
pip install -e .[dev]
# 基本的な開発依存関係のみ
```

#### Phase 2 (統計処理追加)
```bash
pip install pandas numpy scikit-learn
# 高度メタデータ生成用
```

#### Phase 3 (PLaMo-Embedding-1B追加)
```bash
pip install torch transformers accelerate
# PLaMo-Embedding-1B統合用
```

### 開発用設定
```python
# 開発時のconf.py設定例
extensions = ['sphinxcontrib.jsontable']

jsontable_rag_config = {
    # 開発・テスト用設定
    'metadata_extraction': True,
    'semantic_chunking': True, 
    'vector_mode': 'plamo',  # PLaMo-Embedding-1B
    'debug_mode': True,      # 開発時のみ
    'cache_embeddings': True,
    'export_formats': ['json_ld']
}
```

---

## 🧪 テスト戦略

### Phase別テスト
```bash
# Phase 1 テスト
pytest tests/test_enhanced_directive.py
pytest tests/test_rag_metadata_extractor.py
pytest tests/test_semantic_chunker.py

# Phase 2 テスト  
pytest tests/test_advanced_metadata.py
pytest tests/test_search_facets.py
pytest tests/test_metadata_exporter.py

# Phase 3 テスト
pytest tests/test_vector_processor.py
pytest tests/test_plamo_integration.py
pytest tests/test_search_index.py

# 統合テスト
pytest tests/test_rag_integration.py
```

### 継続的インテグレーション
```yaml
# .github/workflows/rag-integration.yml
name: RAG Integration Tests
on:
  push:
    branches: [ feature/rag-* ]
  pull_request:
    branches: [ feature/rag-integration, main ]

jobs:
  test-phase1:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Test Phase 1
        run: pytest tests/test_*_phase1*.py
        
  test-phase2:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Test Phase 2
        run: pytest tests/test_*_phase2*.py
        
  test-phase3:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Test Phase 3
        run: pytest tests/test_*_phase3*.py
```

---

## 📊 進捗管理

### 週次チェックポイント
- **Week 1終了**: Phase 1基盤完了
- **Week 2終了**: EnhancedJsonTableDirective完了
- **Week 3終了**: RAGMetadataExtractor完了
- **Week 4終了**: Phase 1統合完了
- **Week 5終了**: Phase 2基盤完了
- **Week 6終了**: Phase 2統合完了
- **Week 7終了**: PLaMo統合完了
- **Week 8終了**: 全システム統合完了

### 品質ゲート
各Phase完了時：
- ✅ ユニットテストカバレッジ ≥ 85%
- ✅ 統合テスト成功
- ✅ パフォーマンステスト通過
- ✅ コードレビュー完了

---

## 🚀 リリース戦略

### Phase別リリース
1. **v0.1.0-alpha**: Phase 1完了時（基本RAG機能）
2. **v0.2.0-beta**: Phase 2完了時（高度メタデータ生成）
3. **v1.0.0**: Phase 3完了時（PLaMo統合完了）

### 後方互換性保証
- 既存のjsontableディレクティブは完全に動作継続
- RAG機能はオプト・イン方式
- 設定なしでの従来通りの動作保証

---

*このワークフローに従い、8週間でのRAG統合完了を目指します。*