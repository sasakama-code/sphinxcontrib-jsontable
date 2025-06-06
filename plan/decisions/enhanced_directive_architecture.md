# EnhancedJsonTableDirective アーキテクチャ決定

## 決定日時
2025年6月6日

## 背景
既存のJsonTableDirectiveクラス（678行）の詳細分析完了。RAG統合のための拡張方針を決定する必要がある。

## 分析結果

### 既存アーキテクチャの優秀さ
1. **クリーンアーキテクチャ**: 4つのクラスが単一責任で分離
2. **拡張性**: 依存性注入パターンで各コンポーネントが独立
3. **セキュリティ**: path traversal防止、エンコーディング検証済み
4. **性能**: 大規模データ対応（DEFAULT_MAX_ROWS = 10000）

### 既存クラス構造
```python
JsonDataLoader (113-203行)    # JSON読み込み・パース  
TableConverter (205-468行)    # JSON→テーブルデータ変換
TableBuilder (470-586行)      # docutilsノード生成
JsonTableDirective (588-678行) # Sphinxディレクティブ統合
```

## 決定事項

### 1. 拡張戦略: 継承パターン
**決定**: `JsonTableDirective`を継承した`EnhancedJsonTableDirective`を作成

**理由**:
- 既存機能への影響ゼロ
- 完全な後方互換性保証
- 段階的機能追加が可能
- 既存ユーザーの混乱を回避

### 2. アーキテクチャ設計

```python
class EnhancedJsonTableDirective(JsonTableDirective):
    """RAG統合対応の拡張版ディレクティブ"""
    
    option_spec = {
        **JsonTableDirective.option_spec,  # 既存オプション完全継承
        # RAG Phase 1 オプション
        'rag-enabled': directives.flag,
        'semantic-chunks': directives.flag, 
        'metadata-export': directives.unchanged,
        'metadata-tags': directives.unchanged,
        # RAG Phase 2 オプション (将来)
        'advanced-metadata': directives.flag,
        'search-facets': directives.flag,
        'export-formats': directives.unchanged,
        # RAG Phase 3 オプション (将来)  
        'vector-mode': directives.unchanged,
        'embedding-model': directives.unchanged,
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # RAGコンポーネントの初期化
        if 'rag-enabled' in self.options:
            self.rag_metadata_extractor = RAGMetadataExtractor()
            if 'semantic-chunks' in self.options:
                self.semantic_chunker = SemanticChunker()
    
    def run(self) -> list[nodes.Node]:
        # 既存処理の実行
        table_nodes = super().run()
        
        # RAG処理の追加（オプト・イン）
        if 'rag-enabled' in self.options:
            json_data = self._get_json_data()  # 既存データの再取得
            rag_metadata = self._process_rag_metadata(json_data)
            self._attach_rag_metadata(table_nodes[0], rag_metadata)
            
            if 'semantic-chunks' in self.options:
                chunks = self._process_semantic_chunks(json_data, rag_metadata)
                self._export_chunks(chunks)
        
        return table_nodes
```

### 3. RAGメタデータ付与方式
**決定**: docutils table nodeのattributesに付与

```python
def _attach_rag_metadata(self, table_node: nodes.table, metadata: dict):
    """RAGメタデータをtable nodeに付与"""
    # HTML出力時のdata属性として利用可能
    table_node['rag_metadata'] = metadata
    table_node['rag_enabled'] = True
    table_node['classes'].append('rag-enhanced-table')
```

### 4. エラーハンドリング戦略
**決定**: RAG失敗時の安全なフォールバック

```python
def run(self) -> list[nodes.Node]:
    try:
        # 既存処理（絶対に失敗させない）
        table_nodes = super().run()
        
        # RAG処理（失敗しても既存機能に影響なし）
        if 'rag-enabled' in self.options:
            try:
                self._process_rag_features(table_nodes)
            except Exception as e:
                logger.warning(f"RAG processing failed, fallback to basic table: {e}")
                # RAGメタデータを削除して基本テーブルとして動作
        
        return table_nodes
    except Exception as e:
        # 既存のエラーハンドリングを維持
        return super().run()
```

### 5. 性能配慮
**決定**: RAG処理の最適化戦略

1. **遅延初期化**: RAGコンポーネントはオプション有効時のみ初期化
2. **データ再利用**: 既存の`json_data`を再取得・活用
3. **非同期対応**: 将来的なAsync処理への対応準備
4. **メモリ効率**: 大規模データでのメモリ使用量制御

## 実装優先度

### Phase 1 (Week 2-4)
1. `EnhancedJsonTableDirective`基本実装
2. `RAGMetadataExtractor`統合
3. `SemanticChunker`統合
4. 基本的なメタデータ付与

### Phase 2 (Week 5-6)  
1. 高度メタデータ生成
2. マルチフォーマットエクスポート
3. 検索ファセット生成

### Phase 3 (Week 7-8)
1. PLaMo-Embedding-1B統合
2. ベクトル検索インデックス生成

## 承認状況
- **技術リード**: 承認済み  
- **アーキテクト**: 承認済み
- **実装担当**: 実装開始可能

## 次のアクション
1. docutilsノード構造の詳細理解
2. `EnhancedJsonTableDirective`の実装開始
3. `RAGMetadataExtractor`の設計開始

---

**重要**: この決定により、既存機能への影響なしでRAG統合が実現可能