# Issue #53: アーキテクチャ設計書

## **Phase 2: アーキテクチャ設計 - 完了報告**

### **2.1 責務分離によるマイクロサービス的分割設計 ✅**

#### **新しいディレクトリ構造**
```
sphinxcontrib/jsontable/
├── core/
│   ├── __init__.py
│   ├── excel_reader.py          # ~800行（ファイル読み込み専用）
│   ├── data_converter.py        # ~600行（データ変換専用）
│   └── range_parser.py          # ~500行（範囲解析専用）
├── security/
│   ├── __init__.py
│   ├── file_validator.py        # ~400行（ファイル検証）
│   ├── security_scanner.py      # ~600行（セキュリティスキャン）
│   └── macro_validator.py       # ~300行（マクロ検証）
├── errors/
│   ├── __init__.py
│   ├── excel_errors.py          # ~400行（Excel固有エラー）
│   └── error_handlers.py        # ~300行（エラーハンドリング）
└── excel_data_loader.py         # ~200行（ファサードクラス）
```

#### **各モジュールの詳細責務定義**

**core/excel_reader.py**
- **責務**: Excelファイルの物理的読み込みのみ
- **対象機能**: openpyxl/xlrd操作、シート選択、セル読み込み
- **対象メソッド**: `load_workbook()`, `read_excel_file()`, `get_worksheet()`
- **除外**: セキュリティ検証、データ変換、範囲解析

**core/data_converter.py**
- **責務**: 読み込んだデータのJSON変換のみ
- **対象機能**: データ型変換、ヘッダー正規化、JSON構造化
- **対象メソッド**: `data_type_conversion()`, `header_detection()`, `_normalize_header_names()`
- **除外**: ファイル操作、セキュリティ処理

**core/range_parser.py**
- **責務**: Excel範囲指定の解析のみ
- **対象機能**: セル範囲解析、座標変換、境界値検証
- **対象メソッド**: `_parse_range_specification()`, `_split_range_specification()`, `_validate_range_bounds()`
- **除外**: ファイル読み込み、セキュリティ処理

**security/security_scanner.py**
- **責務**: セキュリティ脅威の検出のみ
- **対象機能**: 外部リンク検出、マクロスキャン、危険な参照チェック
- **対象メソッド**: `_validate_external_links()`, `_handle_external_link_detection()`
- **除外**: データ処理、ファイル読み込み

**security/macro_validator.py**
- **責務**: マクロ関連セキュリティのみ
- **対象機能**: マクロ検出、VBAコード解析、セキュリティレベル判定
- **対象メソッド**: `_validate_macro_security()`, `_handle_macro_detection()`
- **除外**: データ変換、範囲解析

**errors/error_handlers.py**
- **責務**: 統一されたエラーハンドリング戦略
- **対象機能**: エラーレベル判定、ログ記録、復旧処理
- **対象メソッド**: エラー処理の統一化、セキュリティエラー処理分離
- **除外**: ビジネスロジック

### **2.2 依存性注入パターンとインターフェース設計 ✅**

#### **抽象インターフェース定義**

```python
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass

# 結果オブジェクト定義
@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    security_issues: List[Dict[str, str]]

@dataclass
class RangeInfo:
    start_row: int
    end_row: int
    start_col: int
    end_col: int
    sheet_name: Optional[str]

@dataclass
class ConversionResult:
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    warnings: List[str]

# 抽象インターフェース群
class IExcelReader(ABC):
    """Excelファイル読み込みインターフェース"""
    @abstractmethod
    def read_file(self, file_path: Path, sheet_name: Optional[str] = None) -> Any:
        """Excelファイルを読み込み、ワークブックオブジェクトを返す"""
        pass
    
    @abstractmethod
    def get_worksheet_data(self, workbook: Any, range_info: RangeInfo) -> List[List[Any]]:
        """指定範囲のセルデータを取得"""
        pass

class ISecurityValidator(ABC):
    """セキュリティ検証インターフェース"""
    @abstractmethod
    def validate_file(self, file_path: Path) -> ValidationResult:
        """ファイル全体のセキュリティ検証"""
        pass
    
    @abstractmethod
    def scan_security_threats(self, workbook: Any) -> ValidationResult:
        """セキュリティ脅威スキャン"""
        pass

class IDataConverter(ABC):
    """データ変換インターフェース"""
    @abstractmethod
    def convert_to_json(self, raw_data: List[List[Any]], options: Dict[str, Any]) -> ConversionResult:
        """生データをJSON形式に変換"""
        pass
    
    @abstractmethod
    def normalize_headers(self, headers: List[str]) -> List[str]:
        """ヘッダー名の正規化"""
        pass

class IRangeParser(ABC):
    """範囲解析インターフェース"""
    @abstractmethod
    def parse_range(self, range_spec: str) -> RangeInfo:
        """範囲指定文字列を解析"""
        pass
    
    @abstractmethod
    def validate_range(self, range_info: RangeInfo) -> ValidationResult:
        """範囲の妥当性検証"""
        pass

class IErrorHandler(ABC):
    """エラーハンドリングインターフェース"""
    @abstractmethod
    def handle_error(self, error: Exception, context: str) -> None:
        """エラーの統一的処理"""
        pass
    
    @abstractmethod
    def create_error_response(self, error: Exception) -> Dict[str, Any]:
        """エラーレスポンス生成"""
        pass
```

#### **テスト可能な依存性注入パターン**

```python
class ExcelDataLoader:
    """ファサードクラス - 各コンポーネントの協調のみ"""
    
    def __init__(
        self,
        base_path: Path,
        excel_reader: Optional[IExcelReader] = None,
        security_validator: Optional[ISecurityValidator] = None,
        data_converter: Optional[IDataConverter] = None,
        range_parser: Optional[IRangeParser] = None,
        error_handler: Optional[IErrorHandler] = None
    ):
        self.base_path = base_path
        
        # 依存性注入（デフォルト実装 or 注入された実装）
        self.excel_reader = excel_reader or DefaultExcelReader()
        self.security_validator = security_validator or DefaultSecurityValidator()
        self.data_converter = data_converter or DefaultDataConverter()
        self.range_parser = range_parser or DefaultRangeParser()
        self.error_handler = error_handler or DefaultErrorHandler()
    
    def load_from_excel(
        self,
        file_path: Union[str, Path],
        sheet_name: Optional[str] = None,
        range_spec: Optional[str] = None,
        **options
    ) -> Dict[str, Any]:
        """
        メイン処理 - 各コンポーネントの協調のみ
        実際の処理は各専門コンポーネントに委譲
        """
        try:
            # 1. ファイルセキュリティ検証
            validation_result = self.security_validator.validate_file(Path(file_path))
            if not validation_result.is_valid:
                return self.error_handler.create_error_response(
                    SecurityValidationError(validation_result.errors)
                )
            
            # 2. 範囲解析（必要な場合）
            range_info = None
            if range_spec:
                range_info = self.range_parser.parse_range(range_spec)
                range_validation = self.range_parser.validate_range(range_info)
                if not range_validation.is_valid:
                    return self.error_handler.create_error_response(
                        RangeValidationError(range_validation.errors)
                    )
            
            # 3. Excelファイル読み込み
            workbook = self.excel_reader.read_file(Path(file_path), sheet_name)
            
            # 4. セキュリティスキャン
            security_scan = self.security_validator.scan_security_threats(workbook)
            if not security_scan.is_valid:
                return self.error_handler.create_error_response(
                    SecurityThreatError(security_scan.errors)
                )
            
            # 5. データ取得
            if range_info:
                raw_data = self.excel_reader.get_worksheet_data(workbook, range_info)
            else:
                # デフォルト範囲でデータ取得
                raw_data = self.excel_reader.get_worksheet_data(workbook, self._get_default_range())
            
            # 6. データ変換
            conversion_result = self.data_converter.convert_to_json(raw_data, options)
            
            return {
                "data": conversion_result.data,
                "metadata": conversion_result.metadata,
                "warnings": conversion_result.warnings + security_scan.warnings
            }
        
        except Exception as e:
            self.error_handler.handle_error(e, "load_from_excel")
            return self.error_handler.create_error_response(e)
```

### **2.3 後方互換性設計と段階的移行計画 ✅**

#### **既存directives.py統合の保持設計**

```python
# 既存のdirectives.pyでの統合方法
class JsonTableDirective(Directive):
    def run(self):
        # 既存のインターフェースを完全保持
        excel_loader = ExcelDataLoader(base_path=self.base_path)
        
        # 内部実装のみ新アーキテクチャを使用
        # 外部からは変更を感知できない
        result = excel_loader.load_from_excel(
            file_path=self.arguments[0],
            sheet_name=self.options.get('sheet'),
            range_spec=self.options.get('range'),
            **self._extract_options()
        )
        
        return self._build_table_from_result(result)
```

#### **段階的移行スケジュール**

**Phase A: 基盤構築（並行開発）**
1. 新しいアーキテクチャコンポーネント実装
2. 既存ExcelDataLoaderは保持
3. 新旧両方のテスト実行

**Phase B: 切り替え準備**
1. 新アーキテクチャでの全機能実装完了
2. パフォーマンス・品質検証
3. フォールバック機能の準備

**Phase C: 段階的移行**
1. 内部実装を新アーキテクチャに切り替え
2. 外部APIは変更なし
3. 既存テストがすべて通過することを確認

**Phase D: 最適化**
1. 旧実装の除去
2. 新アーキテクチャでの最適化
3. ドキュメント更新

#### **フォールバック機能設計**

```python
class ExcelDataLoader:
    def __init__(self, use_legacy: bool = False, **kwargs):
        self.use_legacy = use_legacy
        
        if use_legacy:
            # 旧実装を使用
            self._legacy_loader = LegacyExcelDataLoader(**kwargs)
        else:
            # 新アーキテクチャを使用
            self._setup_new_architecture(**kwargs)
    
    def load_from_excel(self, *args, **kwargs):
        if self.use_legacy:
            return self._legacy_loader.load_from_excel(*args, **kwargs)
        else:
            return self._load_with_new_architecture(*args, **kwargs)
```

## **設計完了サマリー**

### **✅ 完了済み項目**
- [x] マイクロサービス的分割設計（8モジュール構成）
- [x] 各モジュールの責務定義と境界設定
- [x] 抽象インターフェース設計（5つのABCクラス）
- [x] 依存性注入パターン実装設計
- [x] テスト可能性確保のためのMock対応設計
- [x] 後方互換性保持設計
- [x] 段階的移行計画策定
- [x] フォールバック機能設計

### **期待される効果**
- **コード行数削減**: 5,441行 → 平均400-600行/モジュール
- **テストカバレッジ向上**: 75.75% → 85-90%
- **保守性向上**: 単一責任原則の徹底
- **開発効率向上**: 影響範囲の限定化
- **品質向上**: 各コンポーネントの独立テスト可能

### **次のステップ**
Phase 3: TDD実装・カバレッジ向上（90分）に進行可能

---
**作成日**: 2025-06-17  
**Phase**: 2完了  
**設計コンポーネント数**: 8モジュール + 5インターフェース  
**後方互換性**: 100%保持