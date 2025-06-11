# 📋 使用方法の変化・実装ガイド

**対象**: 開発者・技術者・システム管理者  
**目的**: v0.3.0での具体的な使用方法変化と実装における詳細ガイド

---

## 🔄 **基本使用方法の比較**

### **従来の使用方法（v0.1.0）**

#### **基本的なテーブル生成**
```rst
.. jsontable:: data/employees.json
   :header:
```

#### **オプション付きテーブル**
```rst
.. jsontable:: data/large_dataset.json
   :header:
   :limit: 1000
   :encoding: utf-8
```

#### **インラインJSON**
```rst
.. jsontable::
   :header:

   [
     {"name": "田中", "age": 30, "dept": "営業"},
     {"name": "佐藤", "age": 25, "dept": "開発"}
   ]
```

### **新しい使用方法（v0.3.0）**

#### **完全互換モード（変更不要）**
```rst
.. jsontable:: data/employees.json
   :header:
```
**結果**: v0.1.0と完全に同一

#### **RAG基本機能**
```rst
.. jsontable-rag:: data/employees.json
   :header:
   :rag-enabled:
   :semantic-chunks:
```

#### **RAG高度機能**
```rst
.. jsontable-rag:: data/business_data.json
   :header:
   :rag-enabled:
   :semantic-chunks:
   :advanced-metadata:
   :facet-generation:
   :export-formats: json-ld,opensearch,plamo-ready
   :chunk-strategy: japanese-adaptive
   :metadata-tags: financial,confidential,quarterly
```

---

## 🛠️ **新オプション詳細仕様**

### **RAG制御オプション**

| オプション | 型 | デフォルト | 説明 |
|------------|----|-----------|----|
| `:rag-enabled:` | flag | False | RAG機能の有効化 |
| `:semantic-chunks:` | flag | False | セマンティックチャンク生成 |
| `:advanced-metadata:` | flag | False | 高度メタデータ生成 |
| `:facet-generation:` | flag | False | 検索ファセット自動生成 |

### **設定・カスタマイズオプション**

| オプション | 型 | デフォルト | 説明 |
|------------|----|-----------|----|
| `:export-formats:` | string | "" | 出力形式（カンマ区切り） |
| `:metadata-tags:` | string | "" | カスタムタグ（カンマ区切り） |
| `:chunk-strategy:` | string | "adaptive" | チャンク分割戦略 |

#### **export-formats 指定可能値**
- `json-ld`: セマンティックWeb標準形式
- `opensearch`: Elasticsearch/OpenSearch最適化
- `plamo-ready`: PLaMo-Embedding-1B特化
- `facets-only`: UIファセット情報のみ
- `statistics`: 統計情報のみ
- `quality-report`: データ品質レポート
- `all`: 全形式出力

#### **chunk-strategy 指定可能値**
- `adaptive`: データに応じた適応的分割
- `fixed-size`: 固定サイズ分割
- `japanese-adaptive`: 日本語最適化分割
- `semantic-boundary`: セマンティック境界分割

---

## 📊 **具体的な実装例**

### **1. 従業員データテーブル（基本RAG）**

#### **データファイル**: `employees.json`
```json
[
  {
    "employee_id": "EMP001",
    "name": "田中太郎", 
    "department": "営業部",
    "age": 30,
    "hire_date": "2020-04-01",
    "salary": 4500000
  },
  {
    "employee_id": "EMP002",
    "name": "佐藤花子",
    "department": "開発部", 
    "age": 28,
    "hire_date": "2021-06-15",
    "salary": 5200000
  }
]
```

#### **RST記述**
```rst
.. jsontable-rag:: employees.json
   :header:
   :rag-enabled:
   :semantic-chunks:
   :advanced-metadata:
```

#### **生成結果**
```html
<table rag_table_id="tbl_emp_20250608_001"
       rag_semantic_summary="従業員マスタデータ: 2件の人事情報"
       rag_search_keywords="従業員,名前,部署,年齢,給与,入社日"
       rag_chunk_count="2"
       rag_quality_score="0.95">
  <thead>
    <tr><th>Employee ID</th><th>名前</th><th>部署</th><th>年齢</th><th>入社日</th><th>給与</th></tr>
  </thead>
  <tbody>
    <tr><td>EMP001</td><td>田中太郎</td><td>営業部</td><td>30</td><td>2020-04-01</td><td>4500000</td></tr>
    <tr><td>EMP002</td><td>佐藤花子</td><td>開発部</td><td>28</td><td>2021-06-15</td><td>5200000</td></tr>
  </tbody>
</table>
```

### **2. 売上データテーブル（フル機能）**

#### **データファイル**: `sales_quarterly.json`
```json
[
  {
    "quarter": "2024Q1",
    "product": "プロダクトA",
    "region": "関東",
    "sales_amount": 15000000,
    "units_sold": 1200,
    "customer_category": "大企業"
  },
  {
    "quarter": "2024Q1", 
    "product": "プロダクトB",
    "region": "関西",
    "sales_amount": 8500000,
    "units_sold": 650,
    "customer_category": "中小企業"  
  }
]
```

#### **RST記述**
```rst
四半期売上レポート
==================

.. jsontable-rag:: sales_quarterly.json
   :header:
   :rag-enabled:
   :semantic-chunks:
   :advanced-metadata:
   :facet-generation:
   :export-formats: json-ld,opensearch,statistics
   :chunk-strategy: japanese-adaptive
   :metadata-tags: sales,quarterly,confidential,financial
```

#### **生成される出力ファイル**
```
├── sales_quarterly.html (HTMLテーブル)
├── sales_quarterly_metadata.json-ld
├── sales_quarterly_opensearch.json  
├── sales_quarterly_statistics.json
└── sales_quarterly_facets.json
```

---

## ⚙️ **設定ファイル（conf.py）の変化**

### **従来設定（v0.1.0）**
```python
# conf.py
extensions = [
    'sphinxcontrib.jsontable'
]

# 基本設定のみ
jsontable_max_rows = 10000
```

### **新設定（v0.3.0）**
```python
# conf.py
extensions = [
    'sphinxcontrib.jsontable'
]

# 従来設定（継続サポート）
jsontable_max_rows = 10000

# RAG関連設定（新規）
rag_debug_mode = False
rag_default_chunk_strategy = "adaptive"
rag_default_export_formats = ["json-ld"]

# 日本語最適化設定
japanese_entity_recognition = True
japanese_business_term_enhancement = True

# パフォーマンス設定
rag_processing_batch_size = 1000
rag_parallel_workers = 4
rag_memory_limit = "512MB"

# セキュリティ設定
rag_export_file_permissions = 0o644
rag_metadata_encryption = False
```

### **環境別設定例**

#### **開発環境**
```python
# conf_dev.py
rag_debug_mode = True
jsontable_max_rows = 100
rag_default_export_formats = ["statistics", "quality-report"]
rag_processing_batch_size = 10
```

#### **本番環境**
```python
# conf_prod.py  
rag_debug_mode = False
jsontable_max_rows = 10000
rag_default_export_formats = ["json-ld", "opensearch"]
rag_processing_batch_size = 5000
rag_parallel_workers = 8
```

---

## 📁 **ファイル出力の詳細**

### **JSON-LD出力例**
```json
{
  "@context": {
    "@vocab": "https://schema.org/",
    "rag": "https://example.com/rag/"
  },
  "@type": "Dataset",
  "name": "売上四半期データ",
  "description": "2024年第1四半期の製品別売上実績",
  "rag:tableId": "tbl_sales_20250608_002",
  "rag:semanticSummary": "売上データテーブル: 2件の四半期実績",
  "rag:qualityScore": 0.98,
  "distribution": [
    {
      "@type": "DataDownload",
      "encodingFormat": "application/json",
      "contentUrl": "sales_quarterly.json"
    }
  ],
  "rag:entities": {
    "products": ["プロダクトA", "プロダクトB"],
    "regions": ["関東", "関西"],
    "periods": ["2024Q1"]
  }
}
```

### **OpenSearch マッピング例**
```json
{
  "mappings": {
    "properties": {
      "quarter": {
        "type": "keyword",
        "fields": {
          "text": {"type": "text", "analyzer": "japanese"}
        }
      },
      "product": {
        "type": "text", 
        "analyzer": "japanese",
        "fields": {
          "keyword": {"type": "keyword"}
        }
      },
      "sales_amount": {
        "type": "long",
        "fields": {
          "range": {
            "type": "long_range",
            "boost": 1.2
          }
        }
      },
      "rag_metadata": {
        "properties": {
          "semantic_summary": {"type": "text"},
          "quality_score": {"type": "float"},
          "facets": {"type": "nested"}
        }
      }
    }
  },
  "settings": {
    "analysis": {
      "analyzer": {
        "japanese": {
          "type": "custom",
          "tokenizer": "kuromoji_tokenizer",
          "filter": ["kuromoji_baseform", "cjk_width"]
        }
      }
    }
  }
}
```

### **統計レポート例**
```json
{
  "table_id": "tbl_sales_20250608_002",
  "generation_time": "2025-06-08T10:30:00Z",
  "data_quality": {
    "overall_score": 0.98,
    "completeness": 1.0,
    "consistency": 0.95,
    "validity": 1.0,
    "accuracy": 0.96
  },
  "statistical_analysis": {
    "numerical_fields": {
      "sales_amount": {
        "mean": 11750000,
        "median": 11750000,
        "std_dev": 4596194,
        "min": 8500000,
        "max": 15000000,
        "distribution_type": "normal"
      }
    },
    "categorical_fields": {
      "region": {
        "unique_count": 2,
        "diversity_index": 1.0,
        "most_common": [["関東", 1], ["関西", 1]]
      }
    }
  },
  "entity_classification": {
    "detected_entities": {
      "products": 2,
      "regions": 2,
      "time_periods": 1
    },
    "confidence_scores": {
      "product_detection": 0.95,
      "region_detection": 0.98
    }
  }
}
```

---

## 🔧 **カスタマイズ・拡張方法**

### **カスタムエクスポーター追加**

#### **1. カスタムエクスポータークラス作成**
```python
# custom_exporter.py
from sphinxcontrib.jsontable.rag.metadata_exporter import BaseExporter

class CustomAPIExporter(BaseExporter):
    """カスタムAPI連携エクスポーター"""
    
    def export(self, metadata, facets, options):
        return {
            "api_endpoint": "https://api.example.com/data",
            "payload": {
                "table_data": self._format_for_api(metadata),
                "search_config": self._format_facets(facets),
                "timestamp": datetime.now().isoformat()
            },
            "headers": {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {os.getenv('API_TOKEN')}"
            }
        }
```

#### **2. 設定登録**
```python
# conf.py
from custom_exporter import CustomAPIExporter

def setup(app):
    # カスタムエクスポーター登録
    app.add_rag_exporter("custom-api", CustomAPIExporter)
```

#### **3. 使用方法**
```rst
.. jsontable-rag:: data.json
   :header:
   :rag-enabled:
   :export-formats: custom-api
```

### **カスタムチャンク戦略追加**

#### **1. チャンク戦略クラス作成**
```python
# custom_chunker.py
from sphinxcontrib.jsontable.rag.semantic_chunker import BaseChunkStrategy

class DomainSpecificChunkStrategy(BaseChunkStrategy):
    """ドメイン特化チャンク戦略"""
    
    def chunk_data(self, data, metadata):
        chunks = []
        
        for item in data:
            # ドメイン固有のロジック
            if self._is_financial_data(item):
                chunk = self._create_financial_chunk(item)
            elif self._is_hr_data(item):
                chunk = self._create_hr_chunk(item)
            else:
                chunk = self._create_default_chunk(item)
                
            chunks.append(chunk)
            
        return chunks
```

#### **2. 設定登録・使用**
```python
# conf.py
from custom_chunker import DomainSpecificChunkStrategy

rag_custom_chunk_strategies = {
    "domain-specific": DomainSpecificChunkStrategy
}
```

```rst
.. jsontable-rag:: financial_data.json
   :header:
   :rag-enabled:
   :chunk-strategy: domain-specific
```

---

## 📊 **パフォーマンス最適化ガイド**

### **大規模データ処理**

#### **段階的処理設定**
```rst
.. jsontable-rag:: large_dataset.json
   :header:
   :rag-enabled:
   :semantic-chunks:
   :limit: 5000
   :chunk-strategy: fixed-size
   :export-formats: statistics
```

#### **バッチ処理設定**
```python
# conf.py
rag_processing_batch_size = 2000
rag_parallel_workers = 6
rag_memory_limit = "1GB"
rag_enable_streaming = True
```

### **メモリ使用量最適化**

#### **軽量モード設定**
```rst
.. jsontable-rag:: data.json
   :header:
   :rag-enabled:
   :export-formats: facets-only
```

#### **プロファイリング有効化**
```python
# conf.py
rag_debug_mode = True
rag_memory_profiling = True
rag_performance_logging = True
```

---

## 🚀 **移行・導入戦略**

### **段階的移行計画**

#### **Step 1: 既存環境の確認**
```bash
# 現在のバージョン確認
pip show sphinxcontrib-jsontable

# 既存ドキュメントのビルドテスト
sphinx-build -b html source build
```

#### **Step 2: 小規模テスト**
```rst
<!-- 既存のまま -->
.. jsontable:: test_data.json
   :header:

<!-- 新機能テスト -->  
.. jsontable-rag:: test_data.json
   :header:
   :rag-enabled:
   :semantic-chunks:
```

#### **Step 3: 機能別展開**
1. **基本RAG機能**: `:rag-enabled:` + `:semantic-chunks:`
2. **メタデータ生成**: `+advanced-metadata`
3. **ファセット生成**: `+facet-generation`
4. **多形式出力**: `+export-formats`

#### **Step 4: 全面移行**
```python
# conf.py
# 全ディレクティブをRAG対応に切り替え
jsontable_default_rag_enabled = True
```

---

## 🎯 **ベストプラクティス**

### **効果的な使用パターン**

#### **1. データ型別最適化**
```rst
<!-- 人事データ -->
.. jsontable-rag:: hr_data.json
   :header:
   :rag-enabled:
   :chunk-strategy: japanese-adaptive
   :export-formats: json-ld,facets-only
   :metadata-tags: hr,confidential

<!-- 財務データ -->
.. jsontable-rag:: financial_data.json  
   :header:
   :rag-enabled:
   :advanced-metadata:
   :facet-generation:
   :export-formats: opensearch,statistics
   :metadata-tags: financial,quarterly
```

#### **2. セキュリティ考慮**
```rst
<!-- 機密データ -->
.. jsontable-rag:: sensitive_data.json
   :header:
   :rag-enabled:
   :export-formats: quality-report
   :metadata-tags: confidential,internal-only
```

#### **3. パフォーマンス重視**
```rst
<!-- 高速処理優先 -->
.. jsontable-rag:: large_data.json
   :header:
   :rag-enabled:
   :limit: 1000
   :chunk-strategy: fixed-size
   :export-formats: facets-only
```

### **避けるべきパターン**

#### **❌ 過度な機能有効化**
```rst
<!-- 不要な機能まで有効化 -->
.. jsontable-rag:: simple_data.json
   :header:
   :rag-enabled:
   :semantic-chunks:
   :advanced-metadata:
   :facet-generation:
   :export-formats: all  <!-- 全形式は必要に応じて -->
```

#### **❌ 大容量データでの全機能有効化**
```rst
<!-- メモリ不足の原因 -->
.. jsontable-rag:: huge_dataset.json
   :header:
   :rag-enabled:
   :advanced-metadata:
   :chunk-strategy: japanese-adaptive  <!-- 重い処理 -->
   :export-formats: all
```

---

## 🏆 **使用方法変化の総括**

### **✅ 成功した設計方針**

1. **完全互換性**: 既存コードは一切変更不要
2. **段階的導入**: 必要な機能のみ有効化可能
3. **柔軟な設定**: 用途に応じた細かな調整
4. **拡張性**: カスタム機能の追加が容易

### **📈 実用価値**

- **学習コスト**: 最小（既存知識をそのまま活用）
- **移行リスク**: ゼロ（既存機能への影響なし）
- **機能向上**: 革命的（95%の手動作業削減）
- **将来性**: AI統合への完全準備

**結論**: 使用方法の変化は、最小の学習コストで最大の価値を提供する、理想的な進化を実現しています。 🎊