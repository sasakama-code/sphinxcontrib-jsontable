# 🔒 セキュリティルール

## 機密情報の取り扱い厳守事項

### ❌ **絶対禁止**: 以下を決してコードやドキュメントに記載しない

1. **APIキー・認証情報**
   - OpenAI APIキー (`sk-...`)
   - PLaMo APIキー（将来的に使用する場合）
   - GitHub Personal Access Token
   - その他のAPIキー・シークレット

2. **データベース・インフラ情報**
   - データベース接続文字列
   - サーバーのパスワード
   - 内部IPアドレス・ポート情報

3. **個人・企業情報**
   - 実際の顧客データ
   - 個人識別情報
   - 社内機密情報

### ✅ **正しい機密情報管理方法**

#### 1. 環境変数での管理
```python
import os

# 推奨方法
openai_key = os.getenv('OPENAI_API_KEY')
if not openai_key:
    raise ValueError("OPENAI_API_KEY environment variable required")
```

#### 2. 設定ファイル（.gitignore対象）
```python
# config/secrets.py (gitignore対象ファイル)
OPENAI_API_KEY = "your-actual-key-here"
PLAMO_API_KEY = "your-plamo-key-here"

# config/settings.py (公開可能)
from .secrets import OPENAI_API_KEY
```

#### 3. .envファイル（.gitignore対象）
```bash
# .env (gitignore対象ファイル)
OPENAI_API_KEY=sk-your-actual-key-here
PLAMO_API_ENDPOINT=https://api.plamo.example.com
DEBUG_MODE=true
```

#### 4. 設定例の記載方法
```python
# 良い例：実際のキーを記載しない
jsontable_rag_config = {
    'vector_mode': 'plamo',
    'openai_api_key': None,  # 環境変数 OPENAI_API_KEY を使用
    'plamo_endpoint': None,  # 環境変数 PLAMO_ENDPOINT を使用
}

# 悪い例：実際のキーを記載（絶対禁止）
# 'openai_api_key': 'sk-1234567890abcdef...'  # ❌ 絶対ダメ
```

### 🔍 **コミット前チェックリスト**

コミット前に必ず確認：

```bash
# 1. APIキーが含まれていないか確認
git diff --cached | grep -i "sk-\|api.*key\|secret\|password"

# 2. 機密情報パターンの検索
git diff --cached | grep -E "(sk-[a-zA-Z0-9]{48}|password|secret)"

# 3. 設定ファイルの確認
git status | grep -E "\.env|config.*\.py|secrets"
```

### ⚠️ **セキュリティインシデント発生時の対応**

#### 万が一機密情報をコミットしてしまった場合：

1. **即座に対応**
   ```bash
   # 最新コミットから機密情報を削除
   git reset --soft HEAD~1
   # ファイルを修正後、再コミット
   ```

2. **リモートにプッシュ済みの場合**
   ```bash
   # ⚠️ 公開リポジトリの場合は API キーを即座に無効化
   # 履歴の完全削除（慎重に実行）
   git filter-branch --force --index-filter \
   'git rm --cached --ignore-unmatch path/to/secret/file' \
   --prune-empty --tag-name-filter cat -- --all
   ```

3. **APIキーの無効化**
   - OpenAI: API Keys設定でキーを即座に削除
   - その他サービス: 該当キーの無効化

### 📋 **開発時の推奨プラクティス**

1. **開発開始時**
   ```bash
   # .env.example を作成（公開可能）
   echo "OPENAI_API_KEY=your-openai-key-here
   PLAMO_ENDPOINT=your-plamo-endpoint-here" > .env.example
   
   # 実際の .env を作成（秘匿）
   cp .env.example .env
   # .env を編集して実際の値を設定
   ```

2. **テスト時**
   ```python
   # テスト用のモックキー使用
   @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
   def test_vector_processor():
       # テストコード
       pass
   ```

3. **ドキュメント記載時**
   ```markdown
   # 良い例
   設定例：
   ```
   export OPENAI_API_KEY="your-api-key-here"
   ```
   
   # 悪い例（絶対禁止）
   実際のキー: sk-1234567890...
   ```

### 🎯 **このプロジェクトでの適用**

#### RAG統合プロジェクトにおける重要ポイント：

1. **PLaMo-Embedding-1B**: ローカルモデルのため基本的にAPIキー不要
2. **OpenAI API**: オプション機能のため環境変数での管理
3. **設定例**: 常にプレースホルダーまたは環境変数参照を使用

#### 設定ファイル例：
```python
# sphinxcontrib/jsontable/config.py
import os

class RAGConfig:
    # PLaMo設定（APIキー不要）
    PLAMO_MODEL = "plamo-embedding-1b"
    PLAMO_LOCAL = True
    
    # OpenAI設定（環境変数から取得）
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = "text-embedding-3-small"
    
    # フォールバック設定
    FALLBACK_TO_KEYWORD = True
```

---

**🚨 重要**: このセキュリティルールの遵守は必須です。違反は重大なセキュリティリスクを引き起こします。