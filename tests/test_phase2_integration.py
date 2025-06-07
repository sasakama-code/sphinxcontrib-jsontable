"""
Phase 2統合テスト: 全コンポーネント連携検証

統合テストの目的:
1. AdvancedMetadataGenerator, SearchFacetGenerator, MetadataExporter の連携
2. 日本語データでの全パイプライン検証
3. 実用的なパフォーマンス確認
4. エラーハンドリング検証
"""

import json
import tempfile
from pathlib import Path

import pytest

from sphinxcontrib.jsontable.rag.advanced_metadata import AdvancedMetadataGenerator
from sphinxcontrib.jsontable.rag.metadata_exporter import MetadataExporter
from sphinxcontrib.jsontable.rag.search_facets import SearchFacetGenerator


class TestPhase2Integration:
    """Phase 2全体統合テスト"""

    def setup_method(self):
        """テスト準備"""
        self.advanced_generator = AdvancedMetadataGenerator()
        self.facet_generator = SearchFacetGenerator()
        self.metadata_exporter = MetadataExporter()

    @pytest.fixture
    def japanese_employee_data(self):
        """日本語従業員データサンプル"""
        return [
            {
                "name": "田中太郎",
                "age": 30,
                "department": "開発部",
                "salary": 700000,
                "email": "tanaka@company.co.jp",
                "hire_date": "2020-04-01",
                "skills": ["Python", "機械学習", "データ分析"],
                "position": "シニアエンジニア"
            },
            {
                "name": "佐藤花子",
                "age": 28,
                "department": "営業部",
                "salary": 600000,
                "email": "sato@company.co.jp",
                "hire_date": "2021-07-15",
                "skills": ["営業戦略", "顧客管理", "プレゼンテーション"],
                "position": "営業マネージャー"
            },
            {
                "name": "山田次郎",
                "age": 35,
                "department": "開発部",
                "salary": 850000,
                "email": "yamada@company.co.jp",
                "hire_date": "2018-03-01",
                "skills": ["Java", "システム設計", "チームリーダーシップ"],
                "position": "テックリード"
            },
            {
                "name": "鈴木美咲",
                "age": 26,
                "department": "人事部",
                "salary": 500000,
                "email": "suzuki@company.co.jp",
                "hire_date": "2022-01-10",
                "skills": ["採用", "労務管理", "人材育成"],
                "position": "人事スペシャリスト"
            }
        ]

    @pytest.fixture
    def business_data(self):
        """ビジネスデータサンプル"""
        return [
            {
                "product_name": "スマートフォンアプリ開発サービス",
                "category": "IT サービス",
                "price": 2000000,
                "client": "株式会社アクメテック",
                "project_duration": "3ヶ月",
                "completion_date": "2024-03-15",
                "team_size": 5,
                "technologies": ["React Native", "Firebase", "Node.js"]
            },
            {
                "product_name": "Webサイトリニューアル",
                "category": "IT サービス",  # categoryを重複させてファセット化可能に
                "price": 800000,
                "client": "有限会社ベストフーズ",
                "project_duration": "2ヶ月",
                "completion_date": "2024-02-20",
                "team_size": 3,
                "technologies": ["Vue.js", "WordPress", "PHP"]
            },
            {
                "product_name": "データ分析システム構築",
                "category": "システム開発",
                "price": 5000000,
                "client": "大手製造業A社",
                "project_duration": "6ヶ月",
                "completion_date": "2024-06-30",
                "team_size": 8,
                "technologies": ["Python", "PostgreSQL", "Apache Spark"]
            },
            {
                "product_name": "モバイルアプリ保守",
                "category": "IT サービス",  # categoryを更に重複させる
                "price": 1200000,
                "client": "株式会社テックフロー",
                "project_duration": "12ヶ月",
                "completion_date": "2024-12-31",
                "team_size": 4,
                "technologies": ["React Native", "AWS", "MongoDB"]
            }
        ]

    def test_complete_pipeline_japanese_employees(self, japanese_employee_data):
        """日本語従業員データでの完全パイプラインテスト"""
        # 基本メタデータ準備
        basic_metadata = {
            "source_info": {"file_path": "employees.json", "data_type": "json"},
            "processing_timestamp": "2024-06-07T10:00:00Z",
            "rag_version": "2.0.0"
        }

        # Phase 2 Step 1: 高度メタデータ生成
        advanced_metadata = self.advanced_generator.generate_advanced_metadata(
            json_data=japanese_employee_data,
            basic_metadata=basic_metadata
        )

        # 統計分析結果の検証
        assert "numerical_fields" in advanced_metadata.statistical_analysis
        assert "categorical_fields" in advanced_metadata.statistical_analysis
        
        # 年齢フィールドの統計分析検証
        age_stats = advanced_metadata.statistical_analysis["numerical_fields"].get("age")
        assert age_stats is not None
        assert age_stats["min_value"] == 26
        assert age_stats["max_value"] == 35
        assert 29 <= age_stats["mean"] <= 30  # 平均年齢検証

        # 部署フィールドのカテゴリ分析検証
        dept_stats = advanced_metadata.statistical_analysis["categorical_fields"].get("department")
        assert dept_stats is not None
        assert "開発部" in dept_stats["value_counts"]
        assert dept_stats["value_counts"]["開発部"] == 2  # 開発部は2名

        # 日本語エンティティ検証
        entities = advanced_metadata.entity_classification
        assert len(entities.persons) >= 4  # 4名の名前を検出
        
        # 組織エンティティ検証（部署名）
        detected_orgs = [org.organization for org in entities.organizations]
        expected_departments = ["開発部", "営業部", "人事部"]
        for dept in expected_departments:
            assert any(dept in org for org in detected_orgs)

        # データ品質評価検証
        quality = advanced_metadata.data_quality
        assert quality.overall_score >= 0.8  # 高品質データ期待
        assert quality.completeness_score >= 0.9  # 完全性

        # Phase 2 Step 2: 検索ファセット生成
        generated_facets = self.facet_generator.generate_facets(advanced_metadata)

        # カテゴリカルファセット検証
        assert len(generated_facets.categorical_facets) >= 1
        dept_facet = next(
            (f for f in generated_facets.categorical_facets if f.field_name == "department"),
            None
        )
        assert dept_facet is not None
        assert dept_facet.display_name == "部署"
        assert "開発部" in dept_facet.values

        # 数値ファセット検証
        assert len(generated_facets.numerical_facets) >= 2
        salary_facet = next(
            (f for f in generated_facets.numerical_facets if f.field_name == "salary"),
            None
        )
        assert salary_facet is not None
        assert salary_facet.display_name == "給与"
        assert salary_facet.min_value == 500000
        assert salary_facet.max_value == 850000

        # エンティティファセット検証
        assert len(generated_facets.entity_facets) >= 1
        person_facet = next(
            (f for f in generated_facets.entity_facets if f.entity_type == "persons"),
            None
        )
        assert person_facet is not None
        assert person_facet.display_name == "人名"

        # Phase 2 Step 3: メタデータ出力
        export_formats = ["json-ld", "opensearch", "plamo-ready"]
        exported_data = self.metadata_exporter.export_metadata(
            advanced_metadata=advanced_metadata,
            generated_facets=generated_facets,
            formats=export_formats
        )

        # JSON-LD出力検証
        assert "json-ld" in exported_data
        json_ld = exported_data["json-ld"]
        assert json_ld["@type"] == "Dataset"
        assert "rag:statisticalAnalysis" in json_ld
        assert "rag:entityClassification" in json_ld

        # OpenSearch出力検証
        assert "opensearch" in exported_data
        opensearch = exported_data["opensearch"]
        assert "mappings" in opensearch
        assert "properties" in opensearch["mappings"]
        
        # 日本語解析器の設定確認
        settings = opensearch.get("settings", {})
        analysis = settings.get("index", {}).get("analysis", {})
        assert "japanese_analyzer" in analysis.get("analyzer", {})

        # PLaMo-ready出力検証
        assert "plamo-ready" in exported_data
        plamo_config = exported_data["plamo-ready"]
        assert plamo_config["model_config"]["model_name"] == "PLaMo-Embedding-1B"
        assert plamo_config["model_config"]["embedding_dimension"] == 1024
        assert "entity_enhancement" in plamo_config

    def test_business_data_pipeline(self, business_data):
        """ビジネスデータでのパイプラインテスト"""
        basic_metadata = {
            "source_info": {"file_path": "projects.json"},
            "processing_timestamp": "2024-06-07T10:00:00Z",
            "rag_version": "2.0.0"
        }

        # 高度メタデータ生成
        advanced_metadata = self.advanced_generator.generate_advanced_metadata(
            json_data=business_data,
            basic_metadata=basic_metadata
        )

        # ビジネス用語の検出検証
        business_terms = advanced_metadata.entity_classification.business_terms
        expected_terms = ["株式会社", "有限会社"]
        detected_terms = [term.term for term in business_terms]
        
        for expected in expected_terms:
            assert any(expected in term for term in detected_terms)

        # 価格分析検証
        price_stats = advanced_metadata.statistical_analysis["numerical_fields"].get("price")
        assert price_stats is not None
        assert price_stats["min_value"] == 800000
        assert price_stats["max_value"] == 5000000

        # ファセット生成
        facets = self.facet_generator.generate_facets(advanced_metadata)
        
        # 価格範囲ファセット検証
        price_facet = next(
            (f for f in facets.numerical_facets if f.field_name == "price"),
            None
        )
        assert price_facet is not None
        assert len(price_facet.ranges) >= 3  # 適切な範囲分割

        # カテゴリファセット検証
        category_facet = next(
            (f for f in facets.categorical_facets if f.field_name == "category"),
            None
        )
        assert category_facet is not None
        assert "IT サービス" in category_facet.values

    def test_performance_large_dataset(self):
        """大規模データセットでのパフォーマンステスト"""
        import time

        # 1000件のデータを生成
        large_dataset = []
        for i in range(1000):
            large_dataset.append({
                "id": i,
                "name": f"テストユーザー{i}",
                "category": f"カテゴリ{i % 10}",
                "value": i * 1000,
                "date": f"2024-{(i % 12) + 1:02d}-01",
                "description": f"これはテストデータ{i}の説明です。"
            })

        basic_metadata = {"source_info": {"file_path": "large_test.json"}}

        # パフォーマンス測定
        start_time = time.time()
        
        advanced_metadata = self.advanced_generator.generate_advanced_metadata(
            json_data=large_dataset,
            basic_metadata=basic_metadata
        )
        
        facets = self.facet_generator.generate_facets(advanced_metadata)
        
        exported = self.metadata_exporter.export_metadata(
            advanced_metadata=advanced_metadata,
            generated_facets=facets,
            formats=["opensearch", "plamo-ready"]
        )
        
        processing_time = time.time() - start_time
        
        # パフォーマンス検証（30秒以内で完了すること）
        assert processing_time < 30.0
        
        # 結果の妥当性検証
        assert len(facets.categorical_facets) > 0
        assert len(facets.numerical_facets) > 0
        assert "opensearch" in exported
        assert "plamo-ready" in exported

    def test_error_handling_invalid_data(self):
        """不正データでのエラーハンドリングテスト"""
        # 空データ
        advanced_metadata = self.advanced_generator.generate_advanced_metadata(
            json_data=[],
            basic_metadata={}
        )
        assert advanced_metadata is not None
        assert advanced_metadata.data_quality.overall_score >= 0.0

        # 不正なデータ構造
        invalid_data = [
            {"valid_field": "value"},
            None,
            {"another_field": 123},
            {"mixed": [1, 2, "three"]}
        ]
        
        advanced_metadata = self.advanced_generator.generate_advanced_metadata(
            json_data=invalid_data,
            basic_metadata={}
        )
        
        # エラーが発生しても処理は完了すること
        assert advanced_metadata is not None
        
        # 品質スコアが妥当な範囲であること
        quality_score = advanced_metadata.data_quality.overall_score
        assert 0.0 <= quality_score <= 1.0

    def test_file_integration_test(self, japanese_employee_data):
        """ファイル経由での統合テスト"""
        # 一時ファイルに書き込み
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(japanese_employee_data, f, ensure_ascii=False, indent=2)
            temp_file_path = f.name

        try:
            # ファイルから読み込んで処理
            with open(temp_file_path, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)

            basic_metadata = {
                "source_info": {"file_path": temp_file_path},
                "processing_timestamp": "2024-06-07T10:00:00Z"
            }

            # パイプライン実行
            advanced_metadata = self.advanced_generator.generate_advanced_metadata(
                json_data=loaded_data,
                basic_metadata=basic_metadata
            )

            facets = self.facet_generator.generate_facets(advanced_metadata)

            # ファイルパス情報の保持確認
            assert temp_file_path in str(advanced_metadata.basic_metadata)
            
            # メタデータ出力にファイル情報が含まれること
            exported = self.metadata_exporter.export_metadata(
                advanced_metadata=advanced_metadata,
                generated_facets=facets,
                formats=["json-ld"]
            )
            
            json_ld = exported["json-ld"]
            assert temp_file_path in json_ld["name"]

        finally:
            # クリーンアップ
            Path(temp_file_path).unlink()

    def test_multilingual_support(self):
        """多言語対応テスト（日本語 + 英語）"""
        mixed_data = [
            {
                "name": "田中太郎",
                "english_name": "Taro Tanaka",
                "department": "Engineering",
                "部署": "開発部",
                "skills": ["Python", "機械学習", "Machine Learning"],
                "location": "Tokyo, Japan"
            },
            {
                "name": "John Smith",
                "japanese_name": "ジョン・スミス",
                "department": "Sales",
                "部署": "営業部",
                "skills": ["Salesforce", "CRM", "営業戦略"],
                "location": "New York, USA"
            }
        ]

        basic_metadata = {"source_info": {"file_path": "multilingual.json"}}

        advanced_metadata = self.advanced_generator.generate_advanced_metadata(
            json_data=mixed_data,
            basic_metadata=basic_metadata
        )

        # 日本語名・英語名両方の検出確認
        persons = advanced_metadata.entity_classification.persons
        person_names = [p.name for p in persons]
        
        # 日本語名が検出されること
        japanese_names = [name for name in person_names if any(char >= '\u3040' for char in name)]
        assert len(japanese_names) >= 1

        # 組織名（部署）の検出
        organizations = advanced_metadata.entity_classification.organizations
        org_names = [o.organization for o in organizations]
        
        # 日本語部署名が検出されること
        assert any("部" in org for org in org_names)

    def test_facet_ui_configuration(self, japanese_employee_data):
        """ファセットUI設定の検証"""
        basic_metadata = {"source_info": {"file_path": "ui_test.json"}}

        advanced_metadata = self.advanced_generator.generate_advanced_metadata(
            json_data=japanese_employee_data,
            basic_metadata=basic_metadata
        )

        facets = self.facet_generator.generate_facets(advanced_metadata)

        # 給与ファセットのUI設定検証
        salary_facet = next(
            (f for f in facets.numerical_facets if f.field_name == "salary"),
            None
        )
        assert salary_facet is not None
        
        ui_config = salary_facet.ui_config
        assert ui_config["widget_type"] == "range_slider"
        assert ui_config["number_format"] == "currency"
        assert ui_config["currency_symbol"] == "¥"

        # 年齢ファセットのUI設定検証
        age_facet = next(
            (f for f in facets.numerical_facets if f.field_name == "age"),
            None
        )
        assert age_facet is not None
        
        age_ui_config = age_facet.ui_config
        assert age_ui_config["number_format"] == "integer"
        assert age_ui_config["suffix"] == "歳"

        # エンティティファセットのUI設定検証
        person_facet = next(
            (f for f in facets.entity_facets if f.entity_type == "persons"),
            None
        )
        assert person_facet is not None
        
        person_ui_config = person_facet.ui_config
        assert person_ui_config["icon"] == "👤"
        assert "color" in person_ui_config
        assert person_ui_config["displayFormat"] == "name_with_confidence"

    def test_export_format_completeness(self, japanese_employee_data):
        """全出力形式の完全性テスト"""
        basic_metadata = {"source_info": {"file_path": "export_test.json"}}

        advanced_metadata = self.advanced_generator.generate_advanced_metadata(
            json_data=japanese_employee_data,
            basic_metadata=basic_metadata
        )

        facets = self.facet_generator.generate_facets(advanced_metadata)

        # 全形式での出力テスト
        all_formats = ["json-ld", "opensearch", "elasticsearch", "plamo-ready", "search-config", "facet-config"]
        exported = self.metadata_exporter.export_metadata(
            advanced_metadata=advanced_metadata,
            generated_facets=facets,
            formats=all_formats
        )

        # 全形式が正常に出力されること
        for format_name in all_formats:
            assert format_name in exported
            assert isinstance(exported[format_name], dict)
            assert len(exported[format_name]) > 0

        # Elasticsearch特有の設定確認
        elasticsearch = exported["elasticsearch"]
        assert "embedding_vector" in elasticsearch["mappings"]["properties"]
        assert elasticsearch["mappings"]["properties"]["embedding_vector"]["dims"] == 1024

        # PLaMo-ready形式の詳細確認
        plamo_ready = exported["plamo-ready"]
        assert plamo_ready["model_config"]["embedding_dimension"] == 1024
        assert plamo_ready["model_config"]["max_sequence_length"] == 512
        assert "japanese_optimization" in plamo_ready["preprocessing_config"]

        # 検索設定の確認
        search_config = exported["search-config"]
        assert "facet_settings" in search_config
        assert "suggestion_config" in search_config
        assert search_config["suggestion_config"]["japanese_reading_support"] is True

        # ファセット設定の確認
        facet_config = exported["facet-config"]
        assert facet_config["display_config"]["localization"] == "ja_JP"
        assert "facet_groups" in facet_config