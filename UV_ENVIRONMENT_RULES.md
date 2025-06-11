# UV環境構築ルール - sphinxcontrib-jsontable

## 🎯 **必須ルール**: UV統一環境基準

**本プロジェクトでは、CIおよびローカル開発において、環境構築・依存関係管理にUVを使用することを必須とします。**

---

## 🔧 **1. ローカル開発環境構築**

### 基本セットアップ
```bash
# 1. UV のインストール（macOS）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. プロジェクトディレクトリで環境構築
cd sphinxcontrib-jsontable
uv sync

# 3. 開発依存関係の追加
uv add --dev mypy ruff pytest types-docutils
```

### 開発コマンド
```bash
# コード品質チェック
uv run ruff check .
uv run ruff format .
uv run mypy sphinxcontrib/jsontable/

# テスト実行
uv run pytest

# パッケージ構築
uv build
```

---

## 🏗️ **2. CI環境構築（GitHub Actions）**

### 必須設定例
```yaml
# .github/workflows/ci.yml
- name: Set up UV
  uses: astral-sh/setup-uv@v4
  with:
    version: "latest"

- name: Install dependencies
  run: |
    uv sync --dev
    uv add --dev mypy types-docutils

- name: Run mypy
  run: |
    uv run mypy sphinxcontrib/jsontable/ --config-file pyproject.toml
```

---

## 📋 **3. pyproject.toml設定規則**

### dependency-groups設定
```toml
[dependency-groups]
dev = [
    "mypy>=1.16.0",
    "types-docutils>=0.21.0.20250604",
    "ruff>=0.11.11",
    "pytest>=8.3.5",
    "pytest-cov>=5.0.0",
]
```

### mypy設定最適化
```toml
[tool.mypy]
python_version = "3.10"
ignore_missing_imports = true
show_error_codes = true

[[tool.mypy.overrides]]
module = "sphinxcontrib.jsontable.rag.*"
ignore_errors = true  # 段階的型導入
```

---

## ⚠️ **4. 禁止事項**

❌ **以下の環境構築方法は禁止**
- `pip install` の直接使用
- `poetry` の使用  
- `conda` の使用
- 仮想環境の手動作成（venv, virtualenv）

✅ **代わりにUVを使用**
- `uv add package-name`
- `uv run command`
- `uv sync`

---

## 🎯 **5. CI/CD品質ゲート**

### 必須チェック項目
```bash
# 1. コード品質
uv run ruff check .
uv run ruff format --check .

# 2. 型チェック  
uv run mypy sphinxcontrib/jsontable/

# 3. テスト実行
uv run pytest

# 4. パッケージ構築
uv build
```

### 成功基準
- ruff: 0 errors
- mypy: 警告継続実行OK
- pytest: 100% pass
- build: 成功

---

## 🚀 **6. 新機能開発時のワークフロー**

### 1. 環境準備
```bash
uv sync --dev
```

### 2. 開発・テスト
```bash
# コード編集後
uv run ruff format .
uv run pytest tests/
```

### 3. 品質チェック
```bash
uv run ruff check .
uv run mypy sphinxcontrib/jsontable/
```

### 4. コミット前
```bash
# 全チェック実行
uv run ruff check . && uv run mypy sphinxcontrib/jsontable/ && uv run pytest
```

---

## 📚 **7. トラブルシューティング**

### よくある問題と解決法

#### 「UVが見つからない」
```bash
# UVの再インストール
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc  # または ~/.zshrc
```

#### 「依存関係が古い」
```bash
uv sync --upgrade
```

#### 「mypyエラー」
```bash
uv add --dev types-{package-name}
```

---

## 🔒 **8. セキュリティ要件**

- UV lockfile（uv.lock）をバージョン管理に含める
- 依存関係の脆弱性チェック: `uv audit`
- 定期的な依存関係更新: `uv sync --upgrade`

---

## 📄 **9. 参考リンク**

- [UV公式ドキュメント](https://docs.astral.sh/uv/)
- [GitHub Actions setup-uv](https://github.com/astral-sh/setup-uv)
- [pyproject.toml仕様](https://peps.python.org/pep-0621/)

---

**🎉 このルールに従うことで、一貫性のある高品質な開発環境を維持できます。**