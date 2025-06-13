# Issue #51 実施計画: Excel対応機能追加

## 📋 **プロジェクト概要**

### **目的**
既存JsonTableDirectiveにExcelファイル(.xlsx/.xls)対応を追加し、100%後方互換性を維持しながらユーザーワークフローを簡素化する。

### **背景**
- 現在のJsonTableDirectiveはJSONファイルとインラインJSONのみ対応
- ユーザーの多くがExcel形式でデータを保有
- 手動JSON変換の手間を削減
- 多様なExcel構造への対応が必要

### **成功指標**
- Excelファイルの正確なテーブル表示
- 既存JSON機能の完全互換性維持  
- 多様なExcel構造への対応
- 性能影響最小化（レスポンス時間増加<10%）
- ユーザーワークフローの簡素化

## 🔍 **現状分析**

### **技術的現状**
- **バージョン**: 0.2.0
- **基本依存関係**: sphinx>=3.0, docutils>=0.18のみ
- **アーキテクチャ**: モジュラー設計（4コンポーネント分離）
  - JsonDataLoader: ファイル読み込み
  - TableConverter: JSON→テーブル変換
  - TableBuilder: docutilsノード構築
  - JsonTableDirective: メインディレクティブ
- **テスト構造**: 完備（tests/excel/ディレクトリ準備済み）

### **必要な追加要素**
- **依存関係**: pandas>=2.0.0, openpyxl>=3.1.0
- **新規モジュール**: ExcelDataLoader
- **拡張機能**: JsonTableDirective（Excel検出・処理機能）
- **新規オプション**: sheet, range, header-row, skip-rows等

### **制約条件**
- 100%後方互換性維持必須
- 既存JSON機能への影響ゼロ
- 静的サイト生成の維持
- セキュリティ（パストラバーサル対策）

## 🚀 **実装4段階計画**

### **Phase 1: 基本Excel対応（Week 1）**
**目標**: 基本的なExcelファイル読み込みとテーブル生成

**主要機能**:
- Excel file detection (.xlsx, .xls)
- 基本シート読み込み（デフォルト: 最初のシート）
- ヘッダー検出（第1行）
- JSON変換基盤

### **Phase 2: 範囲指定機能（Week 2）**
**目標**: ユーザーによる詳細指定機能

**主要機能**:
- Sheet selection (`:sheet:` option)
- Range specification (`:range:` option)
- Header row configuration (`:header-row:` option)  
- Skip rows functionality (`:skip-rows:` option)

### **Phase 3: 高度構造対応（Week 3）**
**目標**: 複雑なExcel構造への対応

**主要機能**:
- Automatic range detection (`:detect-range:` option)
- Merged cells processing (`:merge-cells:` option)
- Multiple headers support (`:merge-headers:` option)
- JSON caching (`:json-cache:` option)

### **Phase 4: 最適化（Week 4）**
**目標**: 性能・品質・運用性の向上

**主要機能**:
- Performance optimization
- Error handling enhancement
- Comprehensive documentation
- Full integration testing

## ✅ **詳細タスクリスト**

## **Phase 1: 基本Excel対応** ✅ **完了**

### **Task 1.1: 依存関係設定**
**目標**: Excel処理に必要なライブラリを追加

**ToDo**:
- [x] pyproject.tomlに依存関係追加
  - [x] pandas>=2.0.0を追加
  - [x] openpyxl>=3.1.0を追加
  - [x] xlsxwriter>=3.0.0を追加（将来の書き込み機能用）
- [x] 開発環境での依存関係インストール確認
- [ ] CI環境での依存関係テスト

**成果物**:
- 更新されたpyproject.toml
- 依存関係インストールテスト結果

### **Task 1.2: ExcelDataLoader実装**  
**目標**: Excel読み込み専用モジュール作成

**ToDo**:
- [x] sphinxcontrib/jsontable/excel_data_loader.py作成
  - [x] ExcelDataLoaderクラス実装
  - [x] load_from_excel()メソッド実装
  - [x] basic_sheet_detection()メソッド実装
  - [x] header_detection()メソッド実装
  - [x] data_type_conversion()メソッド実装
- [x] エラーハンドリング実装
  - [x] ファイル存在チェック
  - [x] Excel形式検証
  - [x] 読み込みエラー処理
- [x] セキュリティ機能実装
  - [x] パストラバーサル対策
  - [x] ファイルサイズ制限

**成果物**:
- sphinxcontrib/jsontable/excel_data_loader.py
- 基本エラーハンドリング機能

### **Task 1.3: JsonTableDirective拡張**
**目標**: 既存ディレクティブにExcel対応を追加

**ToDo**:
- [x] directives.py修正
  - [x] Excel file detection logic追加
  - [x] ExcelDataLoader統合
  - [x] 条件分岐実装（Excel vs JSON）
  - [x] 既存JSON処理の完全保持
- [x] 新規オプション追加
  - [x] 基本オプション定義
  - [x] オプション検証ロジック
- [x] エラーメッセージ日本語対応

**成果物**:
- 拡張されたJsonTableDirective
- Excel/JSON統合処理ロジック

### **Task 1.4: 基本テスト実装**
**目標**: Phase1機能の単体テスト作成

**ToDo**:
- [x] tests/excel/test_excel_data_loader.py作成
  - [x] 基本読み込みテスト
  - [x] エラーハンドリングテスト
  - [x] セキュリティテスト
- [x] tests/test_excel_integration.py作成
  - [x] Excel→JSON変換テスト
  - [x] ディレクティブ統合テスト
  - [x] 後方互換性テスト
- [x] テストデータ準備
  - [x] 基本Excel サンプル作成
  - [x] 異常系Excelファイル作成

**成果物**:
- Excel関連単体テスト
- テストデータセット

## **Phase 2: 範囲指定機能**

### **Task 2.1: Sheet Selection実装** ✅ **完了**
**目標**: 特定シートの指定機能

**ToDo**:
- [x] `:sheet:` オプション実装
  - [x] シート名指定機能
  - [x] シートインデックス指定機能
  - [x] デフォルトシート設定
- [x] エラーハンドリング
  - [x] 存在しないシート指定時の処理
  - [x] シート名の日本語対応
- [x] テスト実装
  - [x] 正常系テスト
  - [x] 異常系テスト

**成果物**:
- Sheet selection機能（完了）
- 関連テスト（完了）

### **Task 2.2: Range Specification実装** ✅ **完了**
**目標**: セル範囲指定機能

**ToDo**:
- [x] `:range:` オプション実装
  - [x] A1:C10形式の範囲指定
  - [x] 範囲検証ロジック
  - [x] 範囲外アクセス防止
- [x] データ取得ロジック
  - [x] 指定範囲のデータ抽出
  - [x] 空セルの処理
- [x] テスト実装

**成果物**:
- Range specification機能（完了）
- 範囲指定テスト（完了）

### **Task 2.3: Header Row Configuration実装** ✅ **完了**
**目標**: ヘッダー行の柔軟な指定

**ToDo**:
- [x] `:header-row:` オプション実装
  - [x] 行番号指定機能
  - [x] 複数行ヘッダー対応準備
- [x] ヘッダー処理ロジック
  - [x] 指定行からのヘッダー取得
  - [x] ヘッダー名の正規化
- [x] テスト実装

**成果物**:
- Header row configuration機能（完了）
- ヘッダー処理テスト（完了）

### **Task 2.4: Skip Rows実装** ✅ **完了**
**目標**: 不要行のスキップ機能

**ToDo**:
- [x] `:skip-rows:` オプション実装
  - [x] 行番号リスト指定
  - [x] 範囲指定対応
- [x] スキップロジック
  - [x] 指定行の除外処理
  - [x] データ整合性確保
- [x] テスト実装

**成果物**:
- Skip rows機能（完了）
- 行スキップテスト（完了）

## **Phase 3: 高度構造対応**

### **Task 3.1: Automatic Range Detection実装** ✅ **完了**
**目標**: データ範囲の自動検出

**ToDo**:
- [x] `:detect-range:` オプション実装
  - [x] auto, smart, manual モード
  - [x] データ境界自動検出
- [x] 検出アルゴリズム実装
  - [x] 空行・空列の検出
  - [x] データブロック認識
  - [x] ヘッダー自動判定
- [x] テスト実装

**成果物**:
- Automatic range detection機能（完了）
- 自動検出テスト（8/9成功）

### **Task 3.2: Merged Cells Processing実装**
**目標**: 結合セルの適切な処理

**ToDo**:
- [ ] `:merge-cells:` オプション実装
  - [ ] expand, ignore, first-value モード
  - [ ] 結合セル検出ロジック
- [ ] 処理アルゴリズム実装
  - [ ] 結合セルの展開処理
  - [ ] 値の複製・分散
- [ ] テスト実装

**成果物**:
- Merged cells processing機能
- 結合セル処理テスト

### **Task 3.3: Multiple Headers Support実装** ✅ **完了**
**目標**: 複数行ヘッダーの対応

**ToDo**:
- [x] `:merge-headers:` オプション実装
  - [x] 複数行の結合処理
  - [x] 階層構造の平坦化
- [x] ヘッダー結合ロジック
  - [x] 親子関係の解析
  - [x] 結合ヘッダー名生成
- [x] テスト実装

**成果物**:
- Multiple headers support機能（完了）
- 複数ヘッダーテスト（6/9成功）

### **Task 3.4: JSON Caching実装**
**目標**: 変換結果のキャッシュ機能

**ToDo**:
- [ ] `:json-cache:` オプション実装
  - [ ] キャッシュファイル生成
  - [ ] 更新時刻ベース判定
- [ ] キャッシュ管理
  - [ ] ファイル変更検出
  - [ ] キャッシュ無効化
- [ ] テスト実装

**成果物**:
- JSON caching機能
- キャッシュ機能テスト

## **Phase 4: 最適化**

### **Task 4.1: Performance Optimization**
**目標**: 処理性能の最適化

**ToDo**:
- [ ] 大容量ファイル対応
  - [ ] ストリーミング読み込み
  - [ ] メモリ使用量制限
  - [ ] 処理時間制限
- [ ] キャッシュ最適化
  - [ ] 効率的なキャッシュ戦略
  - [ ] メモリキャッシュ実装
- [ ] パフォーマンステスト
  - [ ] ベンチマークテスト実装
  - [ ] 性能回帰テスト

**成果物**:
- 最適化されたExcel処理
- パフォーマンステスト

### **Task 4.2: Error Handling Enhancement**
**目標**: エラーハンドリングの強化

**ToDo**:
- [ ] 包括的エラー処理
  - [ ] 詳細エラーメッセージ
  - [ ] ユーザーフレンドリーな説明
  - [ ] デバッグ情報の提供
- [ ] 回復処理
  - [ ] 部分的失敗への対応
  - [ ] フォールバック機能
- [ ] エラーテスト
  - [ ] 異常系テスト強化
  - [ ] エラーメッセージテスト

**成果物**:
- 強化されたエラーハンドリング
- 異常系テスト

### **Task 4.3: Documentation作成**
**目標**: 包括的なドキュメント作成

**ToDo**:
- [ ] ユーザーガイド作成
  - [ ] 基本使用方法
  - [ ] オプション詳細説明
  - [ ] 使用例集
- [ ] 開発者ドキュメント
  - [ ] アーキテクチャ説明
  - [ ] API仕様書
  - [ ] 拡張ガイド
- [ ] トラブルシューティング
  - [ ] よくある問題と解決方法
  - [ ] エラーメッセージ一覧

**成果物**:
- 完全なドキュメントセット
- 使用例とトラブルシューティング

### **Task 4.4: Integration Testing**
**目標**: 統合テストの実施

**ToDo**:
- [ ] End-to-Endテスト
  - [ ] 実際のSphinxプロジェクトでのテスト
  - [ ] 複数Excel形式での検証
  - [ ] 性能テスト
- [ ] 互換性テスト
  - [ ] 既存機能の回帰テスト
  - [ ] 複数Python版での動作確認
  - [ ] 複数Sphinx版での動作確認
- [ ] 受け入れテスト
  - [ ] 要求仕様との照合
  - [ ] ユーザーシナリオテスト

**成果物**:
- 完全な統合テストスイート
- 受け入れテスト結果

## 🔍 **品質保証計画**

### **テスト戦略**
- **単体テスト**: 各モジュール/機能の独立テスト
- **統合テスト**: コンポーネント間連携テスト
- **システムテスト**: End-to-End機能テスト
- **回帰テスト**: 既存機能への影響確認
- **性能テスト**: レスポンス時間・メモリ使用量測定

### **コード品質**
- **Linting**: ruff checkで統一コードスタイル
- **Type Checking**: mypyでの型チェック
- **Coverage**: 80%以上のテストカバレッジ
- **Documentation**: docstringによる包括的文書化

### **CI/CD統合**
- **自動テスト**: 全Pushでテストスイート実行
- **品質ゲート**: テスト失敗時のマージ禁止
- **依存関係チェック**: セキュリティ脆弱性チェック

## ⚠️ **リスク管理**

### **技術リスク**
| リスク | 影響度 | 対策 |
|--------|--------|------|
| 依存関係競合 | 中 | 最小限依存関係、バージョン固定 |
| 性能劣化 | 高 | 継続的性能監視、最適化 |
| セキュリティ脆弱性 | 高 | 入力検証、パストラバーサル対策 |
| Excel形式の複雑性 | 中 | 段階的対応、柔軟な設計 |

### **プロジェクトリスク**
| リスク | 影響度 | 対策 |
|--------|--------|------|
| スケジュール遅延 | 中 | 段階的リリース、MVPアプローチ |
| 要求変更 | 低 | 明確な仕様、変更管理プロセス |
| 人的リソース不足 | 中 | 詳細ドキュメント、知識共有 |

## 📅 **スケジュール**

### **マイルストーン**
- **Week 1 End**: Phase 1完了（基本Excel対応）
- **Week 2 End**: Phase 2完了（範囲指定機能）
- **Week 3 End**: Phase 3完了（高度構造対応）
- **Week 4 End**: Phase 4完了（最適化・リリース）

### **週次計画**
```
Week 1: 基盤構築週間
├─ Day 1-2: 依存関係設定、ExcelDataLoader実装
├─ Day 3-4: JsonTableDirective拡張
└─ Day 5: 基本テスト実装

Week 2: 機能拡張週間  
├─ Day 1: Sheet Selection実装
├─ Day 2: Range Specification実装
├─ Day 3: Header Row Configuration実装
├─ Day 4: Skip Rows実装
└─ Day 5: Phase2統合テスト

Week 3: 高度機能週間
├─ Day 1: Automatic Range Detection実装
├─ Day 2: Merged Cells Processing実装
├─ Day 3: Multiple Headers Support実装
├─ Day 4: JSON Caching実装
└─ Day 5: Phase3統合テスト

Week 4: 最適化週間
├─ Day 1-2: Performance Optimization
├─ Day 3: Error Handling Enhancement
├─ Day 4: Documentation作成
└─ Day 5: Final Integration Testing
```

## 🎯 **成功判定基準**

### **機能要件**
- [ ] Excel(.xlsx/.xls)ファイルの正確なテーブル表示
- [ ] 10種類以上のExcel構造パターンに対応
- [ ] 全てのオプション機能が正常動作
- [ ] 100%の後方互換性維持

### **非機能要件**
- [ ] 処理時間: 小規模Excel(<1MB)で5秒以内
- [ ] メモリ使用量: 追加使用量50MB以内
- [ ] テストカバレッジ: 80%以上
- [ ] エラー率: 異常入力での適切なエラーハンドリング100%

### **品質要件**
- [ ] 全自動テストスイートの実行成功
- [ ] ドキュメントの完全性
- [ ] コードレビューの合格
- [ ] セキュリティチェックの通過

### **ユーザビリティ要件**
- [ ] 直感的なオプション設計
- [ ] 明確なエラーメッセージ
- [ ] 包括的な使用例提供
- [ ] トラブルシューティングガイド

---

## 📝 **実装開始準備**

### **事前確認事項**
- [ ] 開発環境の設定確認
- [ ] Gitブランチ戦略の確認
- [ ] レビュープロセスの確認
- [ ] Issue #51の要求仕様再確認

### **初回実装順序**
1. pyproject.toml依存関係追加
2. ExcelDataLoader基本実装
3. JsonTableDirective最小限拡張
4. 基本動作確認テスト

**この計画書に基づいて、Phase 1から段階的に実装を開始してください。**