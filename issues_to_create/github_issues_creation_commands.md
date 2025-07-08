# GitHub Issues 作成コマンド集

**作成日**: 2025-07-08  
**目的**: GitHub Issues 調査・対応・追加の Phase 3 完了

## 📋 作成予定Issue一覧

### 1. 範囲検出アルゴリズム実装
```bash
gh issue create \
  --title "範囲検出アルゴリズム実装" \
  --body-file "issues_to_create/issue_range_detection_algorithms.md" \
  --label "enhancement,excel,algorithm"
```

### 2. 結合セル検出機能実装
```bash
gh issue create \
  --title "結合セル検出機能実装" \
  --body-file "issues_to_create/issue_merged_cells_detection.md" \
  --label "enhancement,excel,merged-cells"
```

### 3. ユーザー体験向上・ドキュメント充実化
```bash
gh issue create \
  --title "ユーザー体験向上・ドキュメント充実化" \
  --body-file "issues_to_create/issue_documentation_user_experience.md" \
  --label "documentation,user-experience,enhancement"
```

### 4. フォルダ構造最適化（既存計画書）
```bash
gh issue create \
  --title "CLAUDE.mdコードエクセレンス準拠: sphinxcontrib/jsontableフォルダ構造最適化" \
  --body-file "record/history/issue_folder_structure_optimization.md" \
  --label "enhancement,architecture,code-quality"
```

## 🎯 実行手順

### Step 1: GitHub認証
```bash
# ユーザーが実行する認証手順
gh auth login --web
```

### Step 2: Issues作成実行
```bash
# 一括作成スクリプト
#!/bin/bash
cd /Users/sasakama/Projects/sphinxcontrib-jsontable

echo "Creating GitHub Issues..."

# Issue 1: Range Detection
gh issue create \
  --title "範囲検出アルゴリズム実装" \
  --body-file "issues_to_create/issue_range_detection_algorithms.md" \
  --label "enhancement,excel,algorithm"

# Issue 2: Merged Cells
gh issue create \
  --title "結合セル検出機能実装" \
  --body-file "issues_to_create/issue_merged_cells_detection.md" \
  --label "enhancement,excel,merged-cells"

# Issue 3: Documentation
gh issue create \
  --title "ユーザー体験向上・ドキュメント充実化" \
  --body-file "issues_to_create/issue_documentation_user_experience.md" \
  --label "documentation,user-experience,enhancement"

# Issue 4: Folder Structure
gh issue create \
  --title "CLAUDE.mdコードエクセレンス準拠: sphinxcontrib/jsontableフォルダ構造最適化" \
  --body-file "record/history/issue_folder_structure_optimization.md" \
  --label "enhancement,architecture,code-quality"

echo "All issues created successfully!"
```

## 📊 Issue優先度マトリクス

| Issue | Priority | 実装工数 | ユーザー価値 | 技術価値 |
|-------|----------|----------|--------------|----------|
| ユーザー体験向上 | **High** | 2週間 | **High** | Medium |
| 範囲検出アルゴリズム | Medium | 1週間 | Medium | **High** |
| 結合セル検出 | Medium | 1週間 | Medium | **High** |
| フォルダ構造最適化 | Low | 3-5日 | Low | **High** |

## 🔗 Issue間の依存関係

```
ユーザー体験向上
├── 独立実行可能
└── 他Issueの成果を説明に活用

範囲検出アルゴリズム
├── 結合セル検出と相互連携
└── フォルダ構造最適化後により保守しやすく

結合セル検出
├── 範囲検出アルゴリズムと相互連携
└── 独立実行可能

フォルダ構造最適化
├── 全Issue実装の保守性向上
└── 独立実行可能
```

## ✅ 実行確認チェックリスト

- [ ] GitHub認証確認（`gh auth status`）
- [ ] Issue作成コマンド実行
- [ ] 各Issueの正常作成確認
- [ ] ラベル・優先度設定確認
- [ ] Issue間リンクの確認

## 📈 期待効果

### 短期効果（1ヶ月）
- 4つの重要Issue作成・プロジェクト方向性明確化
- ユーザー体験向上による満足度改善
- 技術的負債（TODO項目）の計画的解決

### 中期効果（3ヶ月）
- Excel機能の完全性向上
- システム全体のユーザビリティ大幅改善
- 企業グレード品質のより効果的活用

### 長期効果（6ヶ月+）
- ユーザーコミュニティの活性化
- システムの継続的改善サイクル確立
- 市場競争力の更なる向上