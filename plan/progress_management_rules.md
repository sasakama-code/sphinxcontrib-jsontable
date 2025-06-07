# 進捗管理ルール

## 📋 基本ルール

### 1. **planフォルダでの一元管理**
- すべての進捗情報は`plan/`フォルダ内で管理
- 作業開始・中断・再開時は必ず進捗状況を確認・更新
- 最新状況を常に文書化

### 2. **必須確認タイミング**
- ✅ **作業開始時**: `plan/current_status.md`を確認
- ✅ **作業中断時**: 進捗を`plan/progress/`に記録
- ✅ **作業再開時**: 前回の状況と次のタスクを確認
- ✅ **フェーズ完了時**: `plan/milestones/`に完了報告

### 3. **進捗追跡ファイル構造**
```
plan/
├── current_status.md           # 現在の状況（必ず最新に保つ）
├── progress/                   # 日次・週次進捗記録
│   ├── week1_progress.md
│   ├── week2_progress.md
│   └── daily_logs/
├── milestones/                 # フェーズ・マイルストーン完了記録
│   ├── phase1_completion.md
│   ├── phase2_completion.md
│   └── phase3_completion.md
├── issues/                     # 課題・問題の記録と解決策
│   ├── technical_issues.md
│   └── blockers_resolved.md
└── decisions/                  # 重要な技術的決定の記録
    ├── architecture_decisions.md
    └── implementation_choices.md
```

---

## 🔄 作業フロー

### 作業開始時のチェックリスト
```bash
# 1. 現在状況の確認
cat plan/current_status.md

# 2. 最新の進捗確認
ls plan/progress/ | tail -5

# 3. 未解決課題の確認
cat plan/issues/technical_issues.md

# 4. 今日のタスク決定
# → plan/progress/daily_logs/YYYY-MM-DD.md に記録
```

### 作業中断時の記録
```bash
# 1. 現在の作業状況を記録
echo "## $(date '+%Y-%m-%d %H:%M') 作業中断
- 作業内容: [具体的な作業]
- 進捗: [完了した部分]
- 次回の開始ポイント: [次にやるべきこと]
- 注意事項: [引き継ぎ事項]" >> plan/progress/daily_logs/$(date +%Y-%m-%d).md

# 2. current_status.mdを更新
```

### 作業再開時の確認
```bash
# 1. 前回の中断ポイント確認
tail -20 plan/progress/daily_logs/$(date +%Y-%m-%d).md

# 2. 全体状況の再確認
cat plan/current_status.md

# 3. 今日のタスクプラン更新
```

---

## 📊 進捗トラッキング

### 週次進捗レビュー
毎週金曜日に実施：
- 週次目標の達成度評価
- 発生した課題と解決策の記録
- 次週の計画調整
- `plan/progress/weekN_progress.md`の更新

### マイルストーン管理
Phase完了時に実施：
- 完了した機能の詳細記録
- 品質メトリクスの測定結果
- 次フェーズへの引き継ぎ事項
- `plan/milestones/phaseN_completion.md`の作成

---

## ⚠️ 必須遵守事項

### 1. **現在状況の常時更新**
- `plan/current_status.md`は常に最新状態を反映
- 作業の開始・終了時に必ず更新
- 他のメンバーが状況を理解できる詳細度

### 2. **課題の即座記録**
- 技術的な問題が発生したら即座に`plan/issues/`に記録
- 解決策も同時に記録
- 同じ問題の再発防止策も文書化

### 3. **決定事項の文書化**
- アーキテクチャや実装の重要な決定は`plan/decisions/`に記録
- 決定の理由と代替案の検討結果も含める
- 後からの振り返りと改善に活用

### 4. **🚨 進捗報告時の必須コミット**
- **フェーズ完了時**: 必ずgitコミット実行
- **重要な進捗報告後**: 作業内容をコミット
- **コード品質改善後**: 改善結果をコミット
- **統合テスト成功後**: テスト結果をコミット
- **バグ修正・機能追加後**: 変更内容をコミット

**コミットルール**:
```bash
# 進捗報告時の自動コミット
git add .
git commit -m "具体的な作業内容の説明

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## 🎯 成功のための重要ポイント

### プロジェクト継続性の確保
- 誰でも現在の状況を理解できる詳細度
- 作業の中断・再開が円滑に行える情報量
- 問題の早期発見と解決のための透明性

### 品質向上への活用
- 定期的な振り返りによる改善点の特定
- 成功パターンの識別と横展開
- リスクの早期発見と対策実行

---

*このルールに従い、RAG統合プロジェクトの確実な進捗管理を実現します。*