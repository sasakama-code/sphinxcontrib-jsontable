# 結合セル検出機能実装

**Issue Type**: Enhancement  
**Priority**: Medium  
**Labels**: enhancement, excel, merged-cells  
**Created**: 2025-07-08

## 📋 Issue概要

ExcelProcessingPipeline で結合セルの検出が未実装のため、`has_merged_cells` が常に False のプレースホルダーになっている。

## 🔍 現状分析

### 該当コード
```python
# sphinxcontrib/jsontable/facade/excel_processing_pipeline.py:305
"has_merged_cells": False,  # Placeholder - TODO: implement actual detection
"merged_ranges": [],  # Placeholder
```

### 問題点
- 結合セルの存在検出が未実装
- 結合範囲情報が提供されていない
- merge_mode パラメータの効果が限定的

## 🎯 実装要件

### 1. 結合セル検出機能
```python
def detect_merged_cells(self, worksheet) -> Dict[str, Any]:
    """結合セルの検出と情報収集"""
    return {
        "has_merged_cells": bool,
        "merged_ranges": List[str],  # ["A1:B2", "C3:D4"]
        "merge_count": int,
        "detection_confidence": float
    }
```

### 2. 結合セル処理モード
- **expand**: 結合セルを展開して各セルに同じ値を設定
- **first**: 結合範囲の最初のセルの値のみ使用
- **skip**: 結合セルを含む行をスキップ

### 3. メタデータ統合
- 検出された結合範囲の詳細情報
- 処理モードと実際の処理結果
- 結合セルが含まれる行・列の特定

## 📈 期待効果

- **データ精度**: 結合セルを含むExcelファイルの正確な処理
- **処理選択**: ユーザーの用途に応じた処理モード選択
- **メタデータ品質**: 結合セル情報の提供

## 🔧 実装計画

### Phase 1: 基本検出機能
```python
class MergedCellDetector:
    def __init__(self, worksheet):
        self.worksheet = worksheet
        
    def detect_merged_ranges(self) -> List[str]:
        """結合範囲をA1:B2形式のリストで返却"""
        
    def has_merged_cells(self) -> bool:
        """結合セルの存在確認"""
        
    def get_merge_info(self) -> Dict[str, Any]:
        """包括的な結合セル情報"""
```

### Phase 2: 処理モード実装
```python
class MergedCellProcessor:
    def process_expand_mode(self, data, merged_ranges):
        """結合セル展開処理"""
        
    def process_first_mode(self, data, merged_ranges):
        """最初のセル値使用処理"""
        
    def process_skip_mode(self, data, merged_ranges):
        """結合セル行スキップ処理"""
```

### Phase 3: パイプライン統合
- ExcelProcessingPipeline への統合
- 範囲検出アルゴリズムとの連携
- パフォーマンス最適化

## ✅ 完了判定基準

- [ ] 結合セルを100%正確に検出
- [ ] 3つの処理モードが正常動作
- [ ] メタデータに正確な結合セル情報が含まれる
- [ ] 大容量ファイルでのパフォーマンス確保
- [ ] 既存機能への影響なし

## 🔗 関連Issue

- Range Detection Algorithms (#新規作成予定)
- Folder Structure Optimization (#計画済み)