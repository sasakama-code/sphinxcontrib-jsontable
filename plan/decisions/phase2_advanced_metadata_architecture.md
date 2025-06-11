# Phase 2: AdvancedMetadataGenerator アーキテクチャ設計

## 決定日時
2025年6月7日 - Phase 2開始

## 背景・目的
Phase 1で基本的なRAGメタデータ抽出が完成。Phase 2では、日本語対応の高度な統計分析・エンティティ分類・検索ファセット生成機能を実装し、PLaMo-Embedding-1B統合への準備を完了する。

## Phase 2の核心目標

### 🎯 日本語特化RAGシステムの高度化
1. **統計分析の深化**: 基本統計から高度な分布分析・相関分析へ
2. **日本語エンティティ認識**: 名前・場所・組織の自動分類
3. **検索ファセット自動生成**: ユーザー体験向上
4. **多形式メタデータ出力**: JSON-LD、OpenSearch、Elasticsearch対応

---

## AdvancedMetadataGenerator 設計仕様

### クラス構造設計

```python
class AdvancedMetadataGenerator:
    """
    Phase 2: 高度なメタデータ生成機能
    
    Phase 1のRAGMetadataExtractorを拡張し、以下を追加:
    - 高度統計分析 (分布、相関、外れ値検出)
    - 日本語エンティティ分類 (人名、地名、組織名)
    - データ品質評価 (完全性、一貫性、妥当性)
    - PLaMo-Embedding-1B連携準備
    """
    
    def __init__(self, config: AdvancedConfig):
        self.statistical_analyzer = StatisticalAnalyzer()
        self.japanese_entity_classifier = JapaneseEntityClassifier()
        self.data_quality_assessor = DataQualityAssessor()
        self.plamo_preparation = PLaMoPreparationLayer()
    
    def generate_advanced_metadata(
        self, 
        json_data: Any, 
        basic_metadata: dict,
        context: AnalysisContext
    ) -> AdvancedMetadata:
        """高度メタデータの生成メイン処理"""
        
        return AdvancedMetadata(
            statistical_analysis=self._analyze_statistics(json_data),
            entity_classification=self._classify_entities(json_data),
            data_quality=self._assess_quality(json_data),
            search_optimization=self._optimize_for_search(json_data),
            plamo_features=self._prepare_plamo_features(json_data)
        )
```

### 1. StatisticalAnalyzer (統計分析器)

```python
class StatisticalAnalyzer:
    """高度統計分析機能"""
    
    def analyze_numerical_data(self, data: list) -> NumericalStats:
        """数値データの詳細分析"""
        return NumericalStats(
            descriptive_stats=self._calculate_descriptive_stats(data),
            distribution_analysis=self._analyze_distribution(data),
            outlier_detection=self._detect_outliers(data),
            correlation_matrix=self._calculate_correlations(data)
        )
    
    def analyze_categorical_data(self, data: list) -> CategoricalStats:
        """カテゴリデータの分析"""
        return CategoricalStats(
            frequency_distribution=self._calculate_frequencies(data),
            entropy=self._calculate_entropy(data),
            diversity_index=self._calculate_diversity(data),
            pattern_detection=self._detect_patterns(data)
        )
    
    def analyze_temporal_data(self, data: list) -> TemporalStats:
        """時系列データの分析"""
        return TemporalStats(
            time_range=self._extract_time_range(data),
            seasonal_patterns=self._detect_seasonal_patterns(data),
            trend_analysis=self._analyze_trends(data),
            frequency_patterns=self._analyze_frequency(data)
        )
```

### 2. JapaneseEntityClassifier (日本語エンティティ分類器)

```python
class JapaneseEntityClassifier:
    """日本語特化エンティティ認識・分類"""
    
    def __init__(self):
        # 日本語特化の正規表現パターン
        self.person_patterns = self._load_person_patterns()
        self.place_patterns = self._load_place_patterns()
        self.organization_patterns = self._load_organization_patterns()
        self.business_patterns = self._load_business_patterns()
    
    def classify_entities(self, text_data: list[str]) -> EntityClassification:
        """テキストデータからエンティティを分類"""
        entities = EntityClassification()
        
        for text in text_data:
            # 人名の検出
            persons = self._extract_persons(text)
            entities.persons.extend(persons)
            
            # 場所名の検出
            places = self._extract_places(text)
            entities.places.extend(places)
            
            # 組織名の検出
            organizations = self._extract_organizations(text)
            entities.organizations.extend(organizations)
            
            # 日本語特有のビジネス用語
            business_terms = self._extract_business_terms(text)
            entities.business_terms.extend(business_terms)
        
        return entities
    
    def _extract_persons(self, text: str) -> list[PersonEntity]:
        """日本語人名の抽出"""
        # 一般的な日本語姓名パターン
        patterns = [
            r'[一-龯]{1,4}[一-龯]{1,3}',  # 漢字姓名
            r'[ア-ン]{2,8}',               # カタカナ名
            r'[a-zA-Z]{2,20}\s[a-zA-Z]{2,20}'  # 英語名
        ]
        # 実装詳細は省略
        pass
    
    def _extract_places(self, text: str) -> list[PlaceEntity]:
        """日本語地名の抽出"""
        # 都道府県、市区町村、駅名等のパターン
        prefecture_pattern = r'[一-龯]{2,3}[都道府県]'
        city_pattern = r'[一-龯]{1,8}[市区町村]'
        # 実装詳細は省略
        pass
```

### 3. DataQualityAssessor (データ品質評価器)

```python
class DataQualityAssessor:
    """データ品質の多角的評価"""
    
    def assess_data_quality(self, data: Any) -> DataQualityReport:
        """包括的なデータ品質評価"""
        return DataQualityReport(
            completeness=self._assess_completeness(data),
            consistency=self._assess_consistency(data),
            validity=self._assess_validity(data),
            accuracy=self._assess_accuracy(data),
            uniqueness=self._assess_uniqueness(data)
        )
    
    def _assess_completeness(self, data: Any) -> CompletenessScore:
        """データ完全性の評価"""
        return CompletenessScore(
            null_rate=self._calculate_null_rate(data),
            empty_string_rate=self._calculate_empty_rate(data),
            missing_field_rate=self._calculate_missing_fields(data),
            overall_score=self._calculate_completeness_score(data)
        )
    
    def _assess_consistency(self, data: Any) -> ConsistencyScore:
        """データ一貫性の評価"""
        return ConsistencyScore(
            format_consistency=self._check_format_consistency(data),
            value_consistency=self._check_value_consistency(data),
            schema_consistency=self._check_schema_consistency(data),
            overall_score=self._calculate_consistency_score(data)
        )
```

---

## SearchFacetGenerator 設計仕様

### 自動ファセット生成ロジック

```python
class SearchFacetGenerator:
    """検索ファセットの自動生成"""
    
    def generate_facets(self, metadata: AdvancedMetadata) -> SearchFacets:
        """メタデータから検索ファセットを自動生成"""
        facets = SearchFacets()
        
        # カテゴリカルファセット
        facets.categorical = self._generate_categorical_facets(metadata)
        
        # 数値範囲ファセット
        facets.numerical = self._generate_numerical_facets(metadata)
        
        # 時間範囲ファセット
        facets.temporal = self._generate_temporal_facets(metadata)
        
        # 日本語エンティティファセット
        facets.entities = self._generate_entity_facets(metadata)
        
        return facets
    
    def _generate_categorical_facets(self, metadata: AdvancedMetadata) -> dict:
        """カテゴリ別ファセット生成"""
        facets = {}
        
        for field, stats in metadata.categorical_stats.items():
            if stats.unique_count <= 50:  # ファセット化適正値
                facets[field] = {
                    "type": "terms",
                    "values": stats.value_counts,
                    "display_name": self._generate_display_name(field)
                }
        
        return facets
    
    def _generate_numerical_facets(self, metadata: AdvancedMetadata) -> dict:
        """数値範囲ファセット生成"""
        facets = {}
        
        for field, stats in metadata.numerical_stats.items():
            ranges = self._calculate_optimal_ranges(stats)
            facets[field] = {
                "type": "range",
                "ranges": ranges,
                "min": stats.min_value,
                "max": stats.max_value,
                "display_name": self._generate_display_name(field)
            }
        
        return facets
```

---

## MetadataExporter 設計仕様

### 多形式出力対応

```python
class MetadataExporter:
    """多形式メタデータ出力"""
    
    def export_metadata(
        self, 
        metadata: AdvancedMetadata, 
        formats: list[str]
    ) -> dict[str, Any]:
        """指定形式でメタデータを出力"""
        exports = {}
        
        for format_type in formats:
            if format_type == "json-ld":
                exports["json-ld"] = self._export_json_ld(metadata)
            elif format_type == "opensearch":
                exports["opensearch"] = self._export_opensearch(metadata)
            elif format_type == "elasticsearch":
                exports["elasticsearch"] = self._export_elasticsearch(metadata)
            elif format_type == "plamo-ready":
                exports["plamo-ready"] = self._export_plamo_ready(metadata)
        
        return exports
    
    def _export_json_ld(self, metadata: AdvancedMetadata) -> dict:
        """JSON-LD形式でのメタデータ出力"""
        return {
            "@context": {
                "@vocab": "http://schema.org/",
                "rag": "http://example.com/rag-schema/"
            },
            "@type": "Dataset",
            "name": metadata.dataset_info.name,
            "description": metadata.dataset_info.description,
            "rag:statisticalAnalysis": metadata.statistical_analysis,
            "rag:entityClassification": metadata.entity_classification,
            "rag:dataQuality": metadata.data_quality,
            "rag:searchFacets": metadata.search_facets
        }
    
    def _export_opensearch(self, metadata: AdvancedMetadata) -> dict:
        """OpenSearch用マッピング定義生成"""
        mapping = {
            "mappings": {
                "properties": {}
            }
        }
        
        # フィールド型の自動マッピング
        for field, field_metadata in metadata.field_analysis.items():
            if field_metadata.data_type == "text":
                mapping["mappings"]["properties"][field] = {
                    "type": "text",
                    "analyzer": "japanese",  # 日本語対応
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                }
            elif field_metadata.data_type == "number":
                mapping["mappings"]["properties"][field] = {
                    "type": "integer" if field_metadata.is_integer else "float"
                }
        
        return mapping
```

---

## PLaMo-Embedding-1B連携準備

### PLaMoPreparationLayer設計

```python
class PLaMoPreparationLayer:
    """PLaMo-Embedding-1B統合への準備機能"""
    
    def prepare_for_plamo(self, metadata: AdvancedMetadata) -> PLaMoFeatures:
        """PLaMo-Embedding-1B用の特徴量準備"""
        return PLaMoFeatures(
            text_segments=self._extract_text_segments(metadata),
            japanese_specific_features=self._extract_japanese_features(metadata),
            embedding_hints=self._generate_embedding_hints(metadata),
            vector_optimization=self._prepare_vector_optimization(metadata)
        )
    
    def _extract_japanese_features(self, metadata: AdvancedMetadata) -> JapaneseFeatures:
        """日本語特有の特徴量抽出"""
        return JapaneseFeatures(
            kanji_density=self._calculate_kanji_density(metadata),
            katakana_terms=self._extract_katakana_terms(metadata),
            business_terminology=self._extract_business_terms(metadata),
            honorific_patterns=self._analyze_honorifics(metadata)
        )
```

---

## データクラス定義

```python
@dataclass
class AdvancedMetadata:
    """Phase 2高度メタデータ構造"""
    basic_metadata: dict  # Phase 1からの継承
    statistical_analysis: StatisticalAnalysis
    entity_classification: EntityClassification
    data_quality: DataQualityReport
    search_facets: SearchFacets
    export_formats: dict[str, Any]
    plamo_features: PLaMoFeatures

@dataclass
class StatisticalAnalysis:
    """統計分析結果"""
    numerical_stats: dict[str, NumericalStats]
    categorical_stats: dict[str, CategoricalStats]
    temporal_stats: dict[str, TemporalStats]
    correlation_matrix: np.ndarray
    outlier_analysis: OutlierAnalysis

@dataclass
class EntityClassification:
    """エンティティ分類結果"""
    persons: list[PersonEntity]
    places: list[PlaceEntity]
    organizations: list[OrganizationEntity]
    business_terms: list[BusinessTermEntity]
    confidence_scores: dict[str, float]

@dataclass  
class DataQualityReport:
    """データ品質評価レポート"""
    completeness: CompletenessScore
    consistency: ConsistencyScore
    validity: ValidityScore
    accuracy: AccuracyScore
    overall_score: float
```

---

## 実装優先度とマイルストーン

### Week 1: 基盤実装
1. **AdvancedMetadataGenerator基本クラス** (2日)
2. **StatisticalAnalyzer実装** (2日)
3. **既存Phase 1との統合テスト** (1日)

### Week 2: 日本語対応実装
1. **JapaneseEntityClassifier実装** (3日)
2. **DataQualityAssessor実装** (2日)

### Week 3: 検索・出力機能
1. **SearchFacetGenerator実装** (2日)
2. **MetadataExporter実装** (2日)
3. **包括的テスト作成** (1日)

### Week 4: PLaMo準備・最適化
1. **PLaMoPreparationLayer実装** (2日)
2. **性能最適化・ベンチマーク** (2日)
3. **Phase 3準備完了** (1日)

---

## 技術的考慮事項

### 性能最適化
- **遅延評価**: 必要な分析のみ実行
- **キャッシング**: 計算結果の効率的キャッシュ
- **並列処理**: 独立分析の並行実行

### エラーハンドリング
- **段階的縮退**: 一部分析失敗時の安全な動作
- **リソース制限**: メモリ・時間制限の厳格管理
- **ログ記録**: 詳細な分析ログの出力

### 拡張性確保
- **プラグイン形式**: 新しい分析器の容易な追加
- **設定駆動**: 分析パラメータの外部設定
- **API一貫性**: Phase 1との一貫したインターフェース

---

## 次のアクション

1. **AdvancedMetadataGenerator基本実装開始**
2. **StatisticalAnalyzer詳細設計**
3. **日本語エンティティパターン収集**
4. **PLaMo-Embedding-1B連携仕様詳細化**

---

**承認状況**: Phase 2設計承認済み
**実装開始**: 即座に開始可能
**目標**: 4週間でPhase 2完全実装完了

この設計により、世界最高レベルの日本語特化RAGシステムの基盤が完成します。