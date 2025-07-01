# 🚀 **ユニットテスト完全修正計画: 31件失敗・15件スキップ解消**

## **現状分析結果**

### **失敗テスト分布 (31件)**
- **test_json_table_directive.py** (11件): MockとAPIの引数形式不一致
- **test_json_data_loader.py** (9件): Loggerパス不一致、メソッド呼び出し形式問題
- **Excel処理パイプライン** (3件): facade統合の不整合
- **セキュリティスキャナー** (2件): ポリシー設定とエラーハンドリング
- **その他core/directives** (6件): アーキテクチャ変更による不整合

### **スキップテスト分布 (15件)**
- **test_json_table_directive_advanced.py** (5件): 機能未実装による動的スキップ
- **test_data_converter_core.py** (8件): メソッド不存在による動的スキップ
- **test_error_types.py** (2件): データクラス関連のスキップ

### **根本問題特定**
1. **Mock設定の不整合**: `@patch("sphinxcontrib.jsontable.directives.logger")` → 実際は `backward_compatibility.logger`
2. **API変更未対応**: 位置引数 `JsonDataLoader('utf-8')` → キーワード引数 `JsonDataLoader(encoding='utf-8')`
3. **動的スキップの乱用**: 機能保証すべきメソッドが未実装でスキップされている
4. **テスト品質の問題**: モック中心で実際の機能保証が不十分

## **Phase 1: 失敗テスト修正（優先順位順）**

### **1.1 test_json_data_loader.py (9件) - 基盤API修正**

#### **修正項目**:
- **Logger パス修正**: 
  ```python
  # 修正前
  @patch("sphinxcontrib.jsontable.directives.logger")
  # 修正後  
  @patch("sphinxcontrib.jsontable.directives.backward_compatibility.logger")
  ```

- **API呼び出し形式統一**: 
  ```python
  # 修正前（期待値）
  mock_loader.assert_called_once_with('utf-8')
  # 修正後（期待値）
  mock_loader.assert_called_once_with(encoding='utf-8')
  ```

- **is_safe_path パッチパス修正**: 実際のインポートパスと一致させる
- **ファイル読み込みテスト強化**: 実際のファイルI/O機能保証追加

#### **対象テスト**:
- `test_validate_encoding_logs_warning_for_invalid_encoding`
- `test_validate_file_path_with_unsafe_path_raises_error`
- `test_validate_file_path_calls_is_safe_path_with_correct_arguments`
- `test_load_from_file_*` (4件)
- `test_parse_inline_calls_validate_not_empty_with_content`

### **1.2 test_json_table_directive.py (11件) - 統合ディレクティブ修正**

#### **修正項目**:
- **初期化テスト修正**: キーワード引数形式の期待値に変更
- **コンポーネントアクセス修正**: loader/converter/builder エイリアス対応確認
- **run()メソッドテスト**: 実際のディレクティブ実行機能保証
- **エラーハンドリング**: 実際の例外処理とエラーノード生成テスト

#### **対象テスト**:
- `test_init_with_default_encoding`
- `test_init_with_custom_encoding`
- `test_run_with_inline_content_*` (2件)
- `test_load_json_data_*` (3件)
- `test_create_error_node_*` (2件)
- その他run/process関連 (3件)

### **1.3 Excel処理パイプライン (3件) - 統合機能修正**

#### **修正項目**:
- **セキュリティ検証**: 実際のExcelファイル脅威検出テスト
- **データ変換**: pandas DataFrameとJSON間の変換機能保証
- **エンドツーエンド**: 完全なExcel→JSON→テーブル変換フロー

#### **対象テスト**:
- `test_security_validation_success`
- `test_data_conversion_success`
- `test_complete_pipeline_success`

### **1.4 その他core/directives (6件) - アーキテクチャ整合性**

#### **修正項目**:
- **BaseDirective**: ファイル不存在エラーハンドリング実機能テスト
- **DirectiveCore**: データソース選択ロジック機能保証
- **JsonProcessor**: 構文エラー・エラーハンドリング強化
- **RangeParser**: 例外処理の実際の動作確認
- **DataConverter**: DataFrameとJSON変換機能
- **SecurityScanner**: セキュリティポリシーとエラーハンドリング

## **Phase 2: スキップテスト解析・修正**

### **2.1 妥当でないスキップの機能実装**

#### **test_data_converter_core.py (8件)**:
**問題**: 必須メソッドが未実装でスキップされている

**実装すべきメソッド**:
- `convert_to_json()`: データをJSON形式に変換
- `convert_dataframe_to_json()`: pandas DataFrameをJSON変換
- `normalize_data_structure()`: データ構造正規化
- `handle_missing_values()`: 欠損値処理
- `convert_data_types()`: データ型変換
- `process_headers()`: ヘッダー処理
- `validate_data_structure()`: データ構造検証
- 性能保証テスト・大容量データセット処理

**修正方針**: 機能保証に必要な実装を追加し、動的スキップを削除

#### **test_json_table_directive_advanced.py (5件)**:
**問題**: 高度機能が未実装で動的スキップされている

**実装すべき機能**:
- Excel統合処理の完全対応
- インライン機能の実装
- オプション処理の完全対応
- テーブル生成機能の強化
- データ読み込みメソッドのアクセス改善

**修正方針**: 実装不十分な機能を完成させ、機能保証テストに変換

### **2.2 妥当なスキップの条件改善**

#### **改善項目**:
- **動的スキップの条件明確化**: 実装状況の事前チェック追加
- **機能保証テスト変換**: モック中心から実際の機能動作確認へ
- **エラーメッセージの改善**: スキップ理由の明確化

## **Phase 3: テスト品質向上**

### **3.1 機能保証テスト強化**

#### **統合テスト追加**:
- **ファイルI/O**: 実際のファイル読み書き機能
- **データ変換**: JSON↔Excel変換の完全性
- **エラーハンドリング**: 例外処理の実動作確認

#### **性能保証テスト**:
- **大容量データ処理**: 10MB+のExcel/JSONファイル処理
- **メモリ使用量**: メモリリーク検出
- **実行時間測定**: パフォーマンス回帰防止

#### **セキュリティテスト**:
- **脅威ファイル検証**: 実際のマクロ・外部リンク検出
- **エラー情報漏洩防止**: 機密情報のサニタイゼーション

### **3.2 テスト保守性向上**

#### **Mock設定の統一**:
- **正しいパッチパス**: インポートパスとの一致確認
- **一貫したMock構造**: 再利用可能なMockフィクスチャ

#### **テストデータ標準化**:
- **共通テストファイル**: 一貫したExcel/JSONサンプル
- **エッジケースデータセット**: 境界値・異常値テスト用

#### **エラーメッセージの明確化**:
- **失敗理由の特定**: デバッグ時間短縮
- **テスト意図の明示**: 何を保証するテストかの明確化

## **📊 期待成果**

### **定量的目標**:
- **失敗テスト**: 31件 → 0件（100%解消）
- **スキップテスト**: 15件 → 2-3件（妥当なスキップのみ残存）
- **テスト成功率**: 94% → 99%+
- **テスト実行時間**: 15-20%高速化（不要なスキップ・try-except除去）

### **定性的改善**:
- **機能保証**: Mock中心 → 実機能保証への転換
- **保守性**: テスト失敗原因の特定時間90%短縮
- **信頼性**: 実際の使用シナリオでの動作保証
- **開発効率**: CI/CDでの早期問題発見能力向上

## **実行手順**

### **Step 1**: Phase 1.1 実行（test_json_data_loader.py 修正）
### **Step 2**: Phase 1.2 実行（test_json_table_directive.py 修正）  
### **Step 3**: Phase 1.3-1.4 実行（その他失敗テスト修正）
### **Step 4**: Phase 2 実行（スキップテスト解消・機能実装）
### **Step 5**: Phase 3 実行（テスト品質向上）
### **Step 6**: 全体検証・最終確認

---

**作成日**: 2025-06-21
**対象**: sphinxcontrib-jsontable v0.3.1
**責任者**: Claude Code  
**承認待ち**: ユーザー確認後実行開始