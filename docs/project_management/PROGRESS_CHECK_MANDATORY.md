# 🚨 **必須**: 作業開始前の進捗確認ルール

## **作業を開始する前に必ず以下を確認してください：**

```bash
# 1. 現在の状況を必ず確認
cat plan/current_status.md

# 2. 最新の進捗状況を確認  
ls plan/progress/daily_logs/ | tail -3

# 3. 未解決の課題を確認
cat plan/issues/technical_issues.md 2>/dev/null || echo "課題ファイルなし"
```

## **作業中断時は必ず記録：**
```bash
# 現在の作業状況を記録
echo "## $(date '+%Y-%m-%d %H:%M') 作業中断
- 作業内容: [具体的な作業内容]
- 進捗: [完了した部分]  
- 次回開始ポイント: [次にやるべきこと]
- 注意事項: [重要な引き継ぎ事項]" >> plan/progress/daily_logs/$(date +%Y-%m-%d).md
```

## **作業再開時の確認：**
```bash
# 前回の作業内容を確認
tail -20 plan/progress/daily_logs/$(ls plan/progress/daily_logs/ | tail -1)

# 今日のタスクを確認・更新
cat plan/current_status.md
```

---

**📁 進捗管理の詳細は `plan/progress_management_rules.md` を参照**

**⚠️ このルールは必須です。作業継続性確保のため厳守してください。**