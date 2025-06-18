"""
Test suite for table_converter.py module - TDD implementation

TDD for TableConverter class
- JSON→テーブル変換機能
- データ型安全性
- パフォーマンス最適化
- エラーハンドリング
"""

from unittest.mock import patch

import pytest

from sphinxcontrib.jsontable.directives.table_converter import (
    DEFAULT_MAX_ROWS,
    INVALID_JSON_DATA_ERROR,
    TableConverter,
)
from sphinxcontrib.jsontable.directives.validators import JsonTableError


class TestTableConverterInitialization:
    """TableConverter初期化テスト"""
    
    def test_default_initialization(self):
        """デフォルト初期化テスト"""
        converter = TableConverter()
        assert converter.max_rows == DEFAULT_MAX_ROWS
        assert converter.performance_mode is False
    
    def test_custom_initialization(self):
        """カスタム設定での初期化テスト"""
        converter = TableConverter(max_rows=5000, performance_mode=True)
        assert converter.max_rows == 5000
        assert converter.performance_mode is True
    
    def test_initialization_validation(self):
        """初期化パラメータ検証テスト"""
        # 無効なmax_rows
        with pytest.raises(ValueError):
            TableConverter(max_rows=-1)
        
        with pytest.raises(ValueError):
            TableConverter(max_rows=0)


class TestTableConverterObjectArrayConversion:
    """オブジェクト配列変換テスト"""
    
    @pytest.fixture
    def converter(self):
        """テスト用コンバーター"""
        return TableConverter()
    
    def test_simple_object_array(self, converter):
        """単純なオブジェクト配列変換テスト"""
        data = [
            {"name": "Alice", "age": 25},
            {"name": "Bob", "age": 30}
        ]
        
        result = converter.convert(data)
        
        # キーはソート済みなのでage, nameの順序
        expected = [
            ["age", "name"],
            ["25", "Alice"],
            ["30", "Bob"]
        ]
        assert result == expected
    
    def test_object_array_with_missing_keys(self, converter):
        """キー欠損オブジェクト配列テスト"""
        data = [
            {"name": "Alice", "age": 25, "city": "Tokyo"},
            {"name": "Bob", "age": 30},  # cityキーなし
            {"name": "Charlie", "city": "Osaka"}  # ageキーなし
        ]
        
        result = converter.convert(data)
        
        # キーはソート済み（age, city, name順）、欠損値は空文字列
        expected = [
            ["age", "city", "name"],
            ["25", "Tokyo", "Alice"],
            ["30", "", "Bob"],
            ["", "Osaka", "Charlie"]
        ]
        assert result == expected
    
    def test_empty_object_array(self, converter):
        """空オブジェクト配列テスト"""
        data = []
        
        # 空データは例外が発生する
        with pytest.raises(JsonTableError):
            converter.convert(data)
    
    def test_object_array_with_complex_values(self, converter):
        """複雑な値を持つオブジェクト配列テスト"""
        data = [
            {"name": "Alice", "skills": ["Python", "Java"], "active": True},
            {"name": "Bob", "skills": ["C++"], "active": False}
        ]
        
        result = converter.convert(data)
        
        # キーはソート済み（active, name, skills順）
        expected = [
            ["active", "name", "skills"],
            ["True", "Alice", "['Python', 'Java']"],
            ["False", "Bob", "['C++']"]
        ]
        assert result == expected


class TestTableConverter2DArrayConversion:
    """2D配列変換テスト"""
    
    @pytest.fixture
    def converter(self):
        """テスト用コンバーター"""
        return TableConverter()
    
    def test_simple_2d_array(self, converter):
        """単純な2D配列変換テスト"""
        data = [
            ["Name", "Age", "City"],
            ["Alice", 25, "Tokyo"],
            ["Bob", 30, "Osaka"]
        ]
        
        result = converter.convert(data)
        
        expected = [
            ["Name", "Age", "City"],
            ["Alice", "25", "Tokyo"],
            ["Bob", "30", "Osaka"]
        ]
        assert result == expected
    
    def test_2d_array_with_mixed_types(self, converter):
        """混合型2D配列テスト"""
        data = [
            ["Name", "Score", "Active", "Data"],
            ["Alice", 95.5, True, None],
            ["Bob", 87, False, {"key": "value"}]
        ]
        
        result = converter.convert(data)
        
        expected = [
            ["Name", "Score", "Active", "Data"],
            ["Alice", "95.5", "True", ""],
            ["Bob", "87", "False", "{'key': 'value'}"]
        ]
        assert result == expected
    
    def test_irregular_2d_array(self, converter):
        """不規則な2D配列テスト"""
        data = [
            ["Name", "Age"],
            ["Alice", 25, "Extra"],  # 余分な要素
            ["Bob"]  # 不足する要素
        ]
        
        result = converter.convert(data)
        
        # 最大列数に合わせて調整される
        expected = [
            ["Name", "Age", ""],
            ["Alice", "25", "Extra"],
            ["Bob", "", ""]
        ]
        assert result == expected


class TestTableConverterSingleObjectConversion:
    """単一オブジェクト変換テスト"""
    
    @pytest.fixture
    def converter(self):
        """テスト用コンバーター"""
        return TableConverter()
    
    def test_simple_single_object(self, converter):
        """単純な単一オブジェクト変換テスト"""
        data = {"name": "Alice", "age": 25, "city": "Tokyo"}
        
        result = converter.convert(data)
        
        # キーはソート済み（age, city, name順）
        expected = [
            ["age", "city", "name"],
            ["25", "Tokyo", "Alice"]
        ]
        assert result == expected
    
    def test_nested_single_object(self, converter):
        """ネストした単一オブジェクト変換テスト"""
        data = {
            "name": "Alice",
            "address": {"city": "Tokyo", "zip": "100-0001"},
            "skills": ["Python", "Java"]
        }
        
        result = converter.convert(data)
        
        # キーはソート済み（address, name, skills順）
        expected = [
            ["address", "name", "skills"],
            ["{'city': 'Tokyo', 'zip': '100-0001'}", "Alice", "['Python', 'Java']"]
        ]
        assert result == expected


class TestTableConverterErrorHandling:
    """エラーハンドリングテスト"""
    
    @pytest.fixture
    def converter(self):
        """テスト用コンバーター"""
        return TableConverter()
    
    def test_invalid_data_type(self, converter):
        """無効なデータ型テスト"""
        invalid_data = "not json data"
        
        with pytest.raises(JsonTableError) as exc_info:
            converter.convert(invalid_data)
        
        assert INVALID_JSON_DATA_ERROR in str(exc_info.value)
    
    def test_none_data(self, converter):
        """Noneデータテスト"""
        with pytest.raises(JsonTableError):
            converter.convert(None)
    
    def test_max_rows_exceeded(self, converter):
        """最大行数超過テスト"""
        # 最大行数を少なく設定
        small_converter = TableConverter(max_rows=2)
        
        large_data = [{"id": i} for i in range(5)]
        
        with pytest.raises(JsonTableError) as exc_info:
            small_converter.convert(large_data)
        
        assert "exceeds maximum" in str(exc_info.value)


class TestTableConverterPerformanceMode:
    """パフォーマンスモードテスト"""
    
    def test_performance_mode_enabled(self):
        """パフォーマンスモード有効時のテスト"""
        converter = TableConverter(performance_mode=True)
        
        data = [{"name": "Alice", "age": 25}]
        result = converter.convert(data)
        
        # パフォーマンスモードでも結果は同じ（キーはソート済み）
        expected = [
            ["age", "name"],
            ["25", "Alice"]
        ]
        assert result == expected
    
    def test_performance_vs_normal_mode(self):
        """パフォーマンスモードと通常モードの比較"""
        normal_converter = TableConverter(performance_mode=False)
        perf_converter = TableConverter(performance_mode=True)
        
        data = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]
        
        normal_result = normal_converter.convert(data)
        perf_result = perf_converter.convert(data)
        
        # 結果は同じはず
        assert normal_result == perf_result


class TestTableConverterUtilityMethods:
    """ユーティリティメソッドテスト"""
    
    @pytest.fixture
    def converter(self):
        """テスト用コンバーター"""
        return TableConverter()
    
    def test_safe_str_conversion(self, converter):
        """安全な文字列変換テスト"""
        # _safe_str メソッドは非公開だが、間接的にテスト
        data = [{"value": None}, {"value": 42}, {"value": True}]
        
        result = converter.convert(data)
        
        expected = [
            ["value"],
            [""],  # None → 空文字列
            ["42"],  # int → 文字列
            ["True"]  # bool → 文字列
        ]
        assert result == expected
    
    def test_data_validation(self, converter):
        """データ検証テスト"""
        # ValidationUtilsのvalidate_not_emptyが呼ばれることを確認
        with patch('sphinxcontrib.jsontable.directives.validators.ValidationUtils.validate_not_empty') as mock_validate:
            data = [{"test": "data"}]
            converter.convert(data)
            mock_validate.assert_called()
    
    def test_header_extraction(self, converter):
        """ヘッダー抽出テスト"""
        data = [
            {"z_field": 1, "a_field": 2, "m_field": 3},
            {"a_field": 4, "z_field": 5, "m_field": 6}
        ]
        
        result = converter.convert(data)
        
        # ヘッダーはアルファベット順にソートされている
        assert result[0] == ["a_field", "m_field", "z_field"]


class TestTableConverterEdgeCases:
    """エッジケーステスト"""
    
    @pytest.fixture
    def converter(self):
        """テスト用コンバーター"""
        return TableConverter()
    
    def test_empty_objects_in_array(self, converter):
        """空オブジェクトを含む配列テスト"""
        data = [{}, {"name": "Alice"}, {}]
        
        result = converter.convert(data)
        
        expected = [
            ["name"],
            [""],  # 空オブジェクト
            ["Alice"],
            [""]  # 空オブジェクト
        ]
        assert result == expected
    
    def test_deep_nesting(self, converter):
        """深いネスト構造テスト"""
        data = [{
            "level1": {
                "level2": {
                    "level3": "deep_value"
                }
            }
        }]
        
        result = converter.convert(data)
        
        # ネストしたオブジェクトは文字列として変換される
        assert len(result) == 2
        assert result[0] == ["level1"]
        assert "level2" in result[1][0]
    
    def test_unicode_and_special_characters(self, converter):
        """Unicode文字と特殊文字テスト"""
        data = [
            {"name": "田中太郎", "emoji": "😊", "special": "tab\there"},
            {"name": "佐藤花子", "emoji": "🎉", "special": "new\nline"}
        ]
        
        result = converter.convert(data)
        
        # キーはソート済み（emoji, name, special順）
        assert result[0] == ["emoji", "name", "special"]
        assert result[1][1] == "田中太郎"  # name列
        assert result[1][0] == "😊"       # emoji列
        assert result[2][1] == "佐藤花子"  # name列
        assert result[2][0] == "🎉"       # emoji列


class TestTableConverterIntegration:
    """統合テスト"""
    
    def test_real_world_data_conversion(self):
        """実世界データ変換テスト"""
        converter = TableConverter(max_rows=1000)
        
        # 実際のAPIレスポンス形式のデータ
        data = [
            {
                "id": 1,
                "name": "Product A",
                "price": 29.99,
                "in_stock": True,
                "categories": ["electronics", "gadgets"],
                "metadata": {"weight": 0.5, "color": "black"}
            },
            {
                "id": 2,
                "name": "Product B",
                "price": 19.99,
                "in_stock": False,
                "categories": ["books"],
                "metadata": {"pages": 200}
            }
        ]
        
        result = converter.convert(data)
        
        # 基本構造の確認
        assert len(result) == 3  # ヘッダー + 2データ行
        assert len(result[0]) == 6  # 6つのカラム
        assert "id" in result[0]
        assert "name" in result[0]
        assert "price" in result[0]
        
        # データ型変換の確認
        assert "29.99" in result[1]
        assert "True" in result[1]
        assert "False" in result[2]
    
    def test_error_recovery_and_logging(self):
        """エラー回復とログ記録テスト"""
        converter = TableConverter()
        
        with patch('sphinxcontrib.jsontable.directives.table_converter.logger') as mock_logger:
            # 正常なデータで開始
            data = [{"test": "normal"}]
            result = converter.convert(data)
            
            # ログが記録されることを確認
            mock_logger.debug.assert_called()
            
            # 結果が正しいことを確認
            assert result == [["test"], ["normal"]]