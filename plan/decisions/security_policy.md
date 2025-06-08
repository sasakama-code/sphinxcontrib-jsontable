# セキュリティポリシー決定事項

## 決定日時
2025年6月6日

## 決定内容
RAG統合プロジェクトにおけるセキュリティポリシーを確立

## 背景
- OpenAI APIキーなどの機密情報を適切に管理する必要
- PLaMo-Embedding-1Bとの統合で複数の認証方式を扱う
- オープンソースプロジェクトとしてのセキュリティベストプラクティス遵守

## 決定事項

### 1. 機密情報管理方針
- **原則**: APIキー・シークレットは決してコードやドキュメントに記載しない
- **管理方法**: 環境変数または設定ファイル（.gitignore対象）のみ
- **公開方法**: .env.example でプレースホルダーを提供

### 2. API戦略
- **PLaMo-Embedding-1B**: ローカルモデル優先（APIキー不要）
- **OpenAI API**: オプション機能として環境変数管理
- **フォールバック**: API失敗時はローカル処理に自動切り替え

### 3. 設定管理
```python
# 承認された設定パターン
import os

class SecurityConfig:
    # 環境変数からの取得
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # デフォルト値の提供
    DEBUG_MODE = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    
    # 必須チェック
    @classmethod
    def validate(cls):
        if cls.vector_mode == 'openai' and not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY required for OpenAI mode")
```

### 4. .gitignore拡張
以下のパターンを .gitignore に追加：
- .env系ファイル
- config/secrets.py
- *.key, *_key.txt
- api_keys.json

### 5. 開発フロー
1. **開発開始時**: .env.example から .env を作成
2. **テスト時**: モックAPIキーまたはローカルモード使用
3. **コミット前**: セキュリティチェック実行
4. **インシデント時**: 即座にAPIキー無効化

## 実装済み対策

### ファイル
- ✅ SECURITY_RULES.md: 詳細セキュリティルール
- ✅ .env.example: 安全な設定例
- ✅ .gitignore: 機密ファイル除外追加
- ✅ CLAUDE.md: セキュリティルール追記

### 監視・チェック
- ✅ コミット前チェックコマンド提供
- ✅ セキュリティインシデント対応手順
- ✅ 開発ベストプラクティス文書化

## 影響・効果

### 正の影響
- セキュリティリスクの大幅削減
- 開発者の意識向上
- オープンソースとしての信頼性確保

### 注意点
- 開発時の追加手順（環境変数設定）
- チーム内でのルール徹底が必要

## 今後の監視事項
1. 定期的なセキュリティチェック
2. 新メンバーへのセキュリティ教育
3. セキュリティツールの活用検討

## 承認
- 技術リード: 承認済み
- プロジェクトマネージャー: 承認済み

---

**重要**: このセキュリティポリシーは必須遵守事項です。