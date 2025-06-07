# 📚 KPT分析ナレッジ抽出ルール

**作成日**: 2025年6月7日  
**目的**: KPT分析結果からの体系的ナレッジ抽出・管理の標準化  
**適用範囲**: sphinxcontrib-jsontableプロジェクト及び関連プロジェクト

---

## 🎯 ナレッジ抽出の基本原則

### 1. **実証ベース原則**
- 実際の成果・データに基づく知識のみを抽出
- 推測・仮説は明確に区別して記録
- 定量的指標による裏付けを必須とする

### 2. **再現可能性原則**
- 他プロジェクトで適用可能な形式で記録
- 具体的手順・コード例を含む実装可能な形式
- 前提条件・制約事項の明確化

### 3. **継続的更新原則**
- 新しいKPT分析毎に既存ナレッジを検証・更新
- 無効化された知識の明確な廃止
- バージョン管理による変更履歴の保持

---

## 🔄 ナレッジ抽出プロセス

### Phase 1: KPT分析実施
```markdown
📋 **KPT分析実施チェックリスト**

□ 分析対象期間の明確化
□ 定量的成果データの収集
□ Keep項目の具体的成功要因分析
□ Problem項目の根本原因分析  
□ Try項目の実現可能性評価
□ ステークホルダー別視点の整理
```

### Phase 2: ナレッジ候補抽出
```python
class KnowledgeExtractionCriteria:
    """ナレッジ抽出基準"""
    
    def __init__(self):
        self.extraction_criteria = {
            "technical_knowledge": {
                "minimum_success_rate": 0.80,    # 80%以上の成功率
                "replication_potential": "high",  # 高い再現可能性
                "documentation_completeness": "comprehensive",
                "code_examples_available": True
            },
            "strategic_knowledge": {
                "measurable_impact": True,       # 測定可能なインパクト
                "decision_rationale_clear": True, # 明確な判断根拠
                "stakeholder_alignment": "achieved",
                "timeline_efficiency": "> 150%"  # 150%以上の効率化
            },
            "process_knowledge": {
                "workflow_documentation": "complete",
                "quality_metrics": "defined",
                "automation_potential": "high",
                "scalability_proven": True
            }
        }
    
    def evaluate_knowledge_worthiness(self, kpt_item: Dict[str, Any]) -> bool:
        """ナレッジ価値評価"""
        
        # 成功実績の確認
        if kpt_item.get("success_rate", 0) < 0.80:
            return False
        
        # 再現可能性の確認
        if not kpt_item.get("has_concrete_examples", False):
            return False
        
        # インパクト測定可能性
        if not kpt_item.get("measurable_outcomes", False):
            return False
        
        return True
```

### Phase 3: ナレッジ分類・構造化
```markdown
📁 **ナレッジ分類マトリクス**

| 分類 | 抽出対象 | 保存先 | 更新頻度 |
|------|----------|--------|----------|
| **技術アーキテクチャ** | Keep項目の技術的成功要因 | `technical_architecture/` | プロジェクト完了時 |
| **開発パターン** | Keep項目の開発手法・プロセス | `development_patterns/` | フェーズ完了時 |
| **ビジネス洞察** | 市場・戦略的成功要因 | `business_insights/` | 四半期毎 |
| **プロジェクト管理** | 意思決定・計画手法 | `project_management/` | マイルストーン毎 |
| **教訓集** | Problem→Try の学習内容 | `lessons_learned/` | KPT分析毎 |
```

### Phase 4: ナレッジ文書化
```markdown
📝 **ナレッジ文書標準フォーマット**

```markdown
# 🎯 [ナレッジタイトル]

**抽出元**: KPT分析 ([対象期間・プロジェクト])  
**検証期間**: [実証期間]  
**実証効果**: [定量的成果]

---

## 📋 概要
[ナレッジの簡潔な説明]

## 🎯 核心原則
[適用可能な原則・パターン]

## 🔧 実装詳細
[具体的な実装方法・コード例]

## 📊 成功指標
[測定方法・基準値]

## 🎯 適用条件
[前提条件・制約事項]

## 🔄 継続的改善
[アップデート・拡張方法]

---

## 🏆 結論
[ナレッジの価値・影響]
```

---

## 📊 ナレッジ品質管理

### 品質基準チェックリスト
```markdown
✅ **ナレッジ品質基準**

**内容品質**
□ 実証データによる裏付けあり
□ 具体的な実装例・コードサンプル含有
□ 成功指標・測定方法の明確化
□ 前提条件・制約事項の明記

**文書品質**  
□ 標準フォーマット準拠
□ 検索可能なタグ・キーワード
□ 関連ナレッジへのリンク
□ 図表・コード例の適切な配置

**実用性**
□ 他プロジェクトでの適用可能性
□ 段階的実装可能な構造
□ トラブルシューティング情報
□ ベストプラクティス・注意点

**保守性**
□ 更新日・バージョン情報
□ 変更履歴の記録
□ 関連文書との整合性
□ 定期レビュー計画
```

### 品質レビュープロセス
```python
class KnowledgeQualityReview:
    """ナレッジ品質レビュー"""
    
    def conduct_quality_review(self, knowledge_document: str) -> Dict[str, Any]:
        """品質レビュー実施"""
        
        review_results = {
            "content_quality": self._review_content_quality(knowledge_document),
            "documentation_quality": self._review_documentation_quality(knowledge_document),
            "practical_utility": self._review_practical_utility(knowledge_document),
            "maintainability": self._review_maintainability(knowledge_document)
        }
        
        overall_score = sum(result["score"] for result in review_results.values()) / len(review_results)
        
        return {
            "overall_quality_score": overall_score,
            "detailed_review": review_results,
            "approval_status": "approved" if overall_score >= 0.8 else "revision_required",
            "improvement_recommendations": self._generate_improvements(review_results)
        }
    
    def _review_content_quality(self, document: str) -> Dict[str, Any]:
        """内容品質レビュー"""
        
        quality_checks = {
            "has_empirical_evidence": self._check_empirical_evidence(document),
            "includes_concrete_examples": self._check_concrete_examples(document),
            "defines_success_metrics": self._check_success_metrics(document),
            "specifies_constraints": self._check_constraints(document)
        }
        
        score = sum(quality_checks.values()) / len(quality_checks)
        
        return {
            "score": score,
            "details": quality_checks,
            "status": "excellent" if score >= 0.9 else "good" if score >= 0.7 else "needs_improvement"
        }
```

---

## 🔒 ナレッジセキュリティ・アクセス管理

### gitignore設定
```bash
# knowledge/ ディレクトリ全体を非公開
knowledge/
*.knowledge.md
*_internal.md

# KPT分析ファイル（機密情報含む）
plan/analysis/
*_kpt_*.md

# 内部戦略文書
*_strategy_*.md
*_competitive_*.md
```

### アクセスレベル定義
```markdown
🔒 **ナレッジアクセスレベル**

**Level 1: Public (公開可能)**
- 一般的な技術パターン
- オープンソース貢献可能な知識
- 業界共有価値のあるベストプラクティス

**Level 2: Internal (内部限定)**  
- プロジェクト固有の実装詳細
- 組織内での学習・共有用知識
- 競合優位性に直結しない技術情報

**Level 3: Confidential (機密)**
- 戦略的意思決定プロセス
- 競合分析・市場戦略
- 収益・ROI分析データ
- 特許・知的財産関連情報

**Level 4: Restricted (制限)**
- 個人情報・機密データ
- 未発表の技術・製品情報
- パートナー・顧客関連の機密情報
```

### セキュリティガイドライン
```python
class KnowledgeSecurityGuidelines:
    """ナレッジセキュリティガイドライン"""
    
    def __init__(self):
        self.security_rules = {
            "data_classification": {
                "automatic_classification": True,
                "manual_review_required": True,
                "classification_tags": ["public", "internal", "confidential", "restricted"]
            },
            "access_control": {
                "role_based_access": True,
                "periodic_access_review": "quarterly",
                "access_logging": True
            },
            "data_protection": {
                "encryption_at_rest": True,
                "secure_transmission": True,
                "backup_encryption": True,
                "retention_policy": "7 years"
            }
        }
    
    def classify_knowledge_sensitivity(self, content: str, metadata: Dict[str, Any]) -> str:
        """ナレッジ機密度分類"""
        
        # 機密キーワードチェック
        confidential_keywords = [
            "競合", "戦略", "収益", "ROI", "市場分析", "特許",
            "顧客", "パートナー", "未発表", "内部"
        ]
        
        restricted_keywords = [
            "個人情報", "機密データ", "パスワード", "API key",
            "未公開", "秘密", "限定"
        ]
        
        if any(keyword in content for keyword in restricted_keywords):
            return "restricted"
        elif any(keyword in content for keyword in confidential_keywords):
            return "confidential"
        elif metadata.get("project_specific", False):
            return "internal"
        else:
            return "public"
```

---

## 🎯 タスク着手前ナレッジ確認ルール

### 必須確認プロセス
```markdown
📋 **タスク開始前チェックリスト**

**Step 1: ナレッジベース事前確認 (必須)**
□ 関連技術アーキテクチャナレッジの確認
□ 類似開発パターンの実装事例検索
□ 過去の教訓・失敗事例の確認
□ 成功要因・ベストプラクティスの適用可能性評価

**Step 2: 戦略的意思決定ナレッジの活用**
□ VTRR意思決定フレームワークの適用
□ 類似判断事例の参照
□ リスク軽減戦略の確認
□ ステークホルダー整合手法の適用

**Step 3: 品質保証ナレッジの適用**
□ テスト戦略パターンの選択
□ 品質基準・成功指標の設定
□ エラーハンドリングパターンの確認
□ パフォーマンス最適化手法の適用

**Step 4: 実装効率化ナレッジの活用**
□ 高速実装パターンの適用
□ 日本語特化設計の確認
□ コード品質標準の確認
□ 統合・デプロイパターンの選択
```

### ナレッジ検索・発見システム
```python
class PreTaskKnowledgeCheck:
    """タスク着手前ナレッジ確認"""
    
    def __init__(self):
        self.knowledge_categories = {
            "technical_patterns": {
                "search_keywords": ["アーキテクチャ", "設計", "実装", "統合"],
                "priority": "high",
                "mandatory_check": True
            },
            "success_factors": {
                "search_keywords": ["成功要因", "ベストプラクティス", "効率化"],
                "priority": "high", 
                "mandatory_check": True
            },
            "risk_mitigation": {
                "search_keywords": ["リスク", "失敗", "問題", "教訓"],
                "priority": "medium",
                "mandatory_check": True
            },
            "decision_frameworks": {
                "search_keywords": ["意思決定", "判断", "選択", "戦略"],
                "priority": "medium",
                "mandatory_check": False
            }
        }
    
    def conduct_pre_task_knowledge_review(self, task_description: str) -> Dict[str, Any]:
        """タスク着手前ナレッジレビュー"""
        
        review_results = {
            "task_description": task_description,
            "knowledge_matches": {},
            "applicable_patterns": [],
            "risk_factors": [],
            "recommended_approaches": [],
            "quality_standards": []
        }
        
        # タスクキーワード抽出
        task_keywords = self._extract_task_keywords(task_description)
        
        # カテゴリ別ナレッジ検索
        for category, config in self.knowledge_categories.items():
            matches = self._search_knowledge_by_category(task_keywords, category, config)
            review_results["knowledge_matches"][category] = matches
        
        # 適用可能パターン特定
        review_results["applicable_patterns"] = self._identify_applicable_patterns(
            task_keywords, review_results["knowledge_matches"]
        )
        
        # リスク要因特定
        review_results["risk_factors"] = self._identify_risk_factors(
            task_keywords, review_results["knowledge_matches"]
        )
        
        # 推奨アプローチ生成
        review_results["recommended_approaches"] = self._generate_recommendations(
            task_keywords, review_results["knowledge_matches"]
        )
        
        return review_results
    
    def _extract_task_keywords(self, task_description: str) -> List[str]:
        """タスクキーワード抽出"""
        
        # 技術キーワード
        technical_keywords = [
            "実装", "設計", "統合", "テスト", "デプロイ", "最適化",
            "アーキテクチャ", "API", "データベース", "パフォーマンス"
        ]
        
        # ビジネスキーワード  
        business_keywords = [
            "戦略", "計画", "分析", "改善", "効率化", "品質",
            "ユーザー", "市場", "競合", "ROI"
        ]
        
        # プロセスキーワード
        process_keywords = [
            "プロジェクト", "管理", "レビュー", "承認", "リリース",
            "ドキュメント", "コミュニケーション", "協力"
        ]
        
        all_keywords = technical_keywords + business_keywords + process_keywords
        
        # タスク記述内のキーワード検出
        detected_keywords = []
        task_lower = task_description.lower()
        
        for keyword in all_keywords:
            if keyword in task_lower:
                detected_keywords.append(keyword)
        
        return detected_keywords
    
    def _search_knowledge_by_category(
        self, 
        task_keywords: List[str], 
        category: str, 
        config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """カテゴリ別ナレッジ検索"""
        
        # 実際の実装では、ナレッジベースファイルを検索
        # ここでは模擬的な結果を返す
        
        matches = []
        search_keywords = config["search_keywords"]
        
        # タスクキーワードと検索キーワードの一致度計算
        relevance_score = len(set(task_keywords) & set(search_keywords)) / len(search_keywords)
        
        if relevance_score > 0.3:  # 30%以上の関連性
            matches.append({
                "category": category,
                "relevance_score": relevance_score,
                "matching_keywords": list(set(task_keywords) & set(search_keywords)),
                "knowledge_files": self._find_relevant_knowledge_files(category, task_keywords)
            })
        
        return matches
    
    def _find_relevant_knowledge_files(self, category: str, keywords: List[str]) -> List[str]:
        """関連ナレッジファイル検索"""
        
        # 実際の実装では、knowledge/ディレクトリを検索
        # カテゴリとキーワードに基づいてファイルを特定
        
        category_file_map = {
            "technical_patterns": [
                "technical_architecture/rag_pipeline_design.md",
                "development_patterns/testing_strategies.md",
                "development_patterns/japanese_localization_patterns.md"
            ],
            "success_factors": [
                "lessons_learned/critical_success_factors.md",
                "development_patterns/phase_integration_methodology.md"
            ],
            "risk_mitigation": [
                "project_management/strategic_decision_patterns.md",
                "lessons_learned/common_pitfalls.md"
            ],
            "decision_frameworks": [
                "project_management/strategic_decision_patterns.md",
                "business_insights/market_differentiation.md"
            ]
        }
        
        return category_file_map.get(category, [])
```

### タスク着手前確認の自動化
```python
class AutomatedKnowledgeCheck:
    """自動ナレッジ確認システム"""
    
    def generate_task_guidance(self, task_description: str) -> str:
        """タスクガイダンス生成"""
        
        checker = PreTaskKnowledgeCheck()
        review_results = checker.conduct_pre_task_knowledge_review(task_description)
        
        guidance = f"""
# 🎯 タスク実行ガイダンス

**タスク**: {task_description}

## 📚 関連ナレッジ

### 適用推奨パターン
{self._format_applicable_patterns(review_results["applicable_patterns"])}

### 注意すべきリスク要因
{self._format_risk_factors(review_results["risk_factors"])}

### 推奨アプローチ
{self._format_recommendations(review_results["recommended_approaches"])}

## ✅ 実行前チェックリスト
□ 関連ナレッジの詳細確認完了
□ 適用パターンの実装準備完了
□ リスク軽減策の準備完了
□ 品質基準・成功指標の設定完了

## 🔗 参照ナレッジファイル
{self._format_knowledge_references(review_results["knowledge_matches"])}
"""
        
        return guidance
    
    def _format_applicable_patterns(self, patterns: List[str]) -> str:
        """適用パターン整形"""
        if not patterns:
            return "- 新規パターンの可能性 - 慎重な設計・実装を推奨"
        
        formatted = []
        for pattern in patterns:
            formatted.append(f"- {pattern}")
        
        return "\n".join(formatted)
    
    def _format_risk_factors(self, risks: List[str]) -> str:
        """リスク要因整形"""
        if not risks:
            return "- 特定の既知リスクなし - 一般的な注意事項を適用"
        
        formatted = []
        for risk in risks:
            formatted.append(f"⚠️ {risk}")
        
        return "\n".join(formatted)
```

## 🔄 ナレッジ活用・更新サイクル

### 定期レビュー・更新プロセス
```markdown
📅 **ナレッジ更新スケジュール**

**毎週** (Weekly)
- 新規KPT分析からのナレッジ抽出
- 緊急度高いナレッジの即座更新

**毎月** (Monthly)  
- ナレッジ利用状況の分析
- アクセス頻度に基づく優先度調整
- 関連ナレッジ間の整合性チェック

**四半期** (Quarterly)
- 全ナレッジの包括的品質レビュー
- 陳腐化したナレッジの特定・更新
- 新たなナレッジカテゴリの検討

**年次** (Annually)
- ナレッジベース全体の構造見直し
- 長期的価値のあるナレッジの特定
- アーカイブ・廃止判断
```

### ナレッジ活用促進
```python
class KnowledgeUtilizationPromotion:
    """ナレッジ活用促進"""
    
    def create_knowledge_discovery_system(self) -> Dict[str, Any]:
        """ナレッジ発見システム"""
        
        return {
            "search_optimization": {
                "full_text_search": "全文検索機能",
                "tag_based_filtering": "タグによる絞り込み",
                "similarity_search": "類似ナレッジ推奨",
                "usage_based_ranking": "利用頻度による優先表示"
            },
            "proactive_recommendations": {
                "project_context_matching": "プロジェクト文脈に基づく推奨",
                "problem_solution_mapping": "問題-解決策マッピング",
                "success_pattern_suggestions": "成功パターン提案",
                "risk_mitigation_guidance": "リスク軽減ガイダンス"
            },
            "learning_integration": {
                "onboarding_curriculum": "新メンバー学習カリキュラム",
                "best_practice_workshops": "ベストプラクティス勉強会",
                "case_study_sessions": "事例研究セッション",
                "knowledge_sharing_incentives": "知識共有インセンティブ"
            }
        }
```

---

## 🎯 実装チェックリスト

### タスク着手前ナレッジ確認実施チェックリスト
```markdown
📋 **タスク開始前ナレッジ確認チェックリスト (必須)**

**事前ナレッジ確認**
□ ナレッジベース検索実行完了
□ 関連技術パターンの確認完了
□ 過去の成功・失敗事例の確認完了
□ 適用可能なベストプラクティスの特定完了

**リスク・制約事項確認**
□ 既知のリスク要因の確認完了
□ 制約条件・前提条件の確認完了
□ 軽減策・対応策の準備完了
□ エスカレーション手順の確認完了

**品質・効率化確認**
□ 品質基準・成功指標の設定完了
□ テスト戦略・検証方法の確認完了
□ 効率化パターンの適用準備完了
□ 実装方針・アプローチの決定完了

**意思決定支援確認**
□ VTRR意思決定フレームワーク適用完了
□ ステークホルダー整合手法の確認完了
□ 類似判断事例の参照完了
□ 戦略的選択肢の評価完了
```

### ナレッジ抽出実施チェックリスト
```markdown
📋 **KPT→ナレッジ抽出実施チェックリスト**

**事前準備**
□ KPT分析の完了確認
□ 定量的成果データの整理
□ ステークホルダーからのフィードバック収集
□ 関連する既存ナレッジの確認

**抽出プロセス**
□ ナレッジ抽出基準による候補選定
□ 分類マトリクスによるカテゴリ決定
□ 標準フォーマットによる文書化
□ 品質基準チェックリストによる検証

**セキュリティ対応**
□ 機密度レベルの分類
□ 適切なアクセス制御の設定
□ gitignore設定の確認
□ セキュリティガイドライン準拠確認

**公開・活用**
□ 品質レビューの完了
□ 関連チームへの共有
□ 検索・発見しやすいタグ付け
□ 定期更新スケジュールの設定
```

---

## 🏆 期待効果

### 短期効果 (3ヶ月)
- プロジェクト成功パターンの即座再利用
- 意思決定品質の向上
- 新メンバーのオンボーディング効率化

### 中期効果 (6-12ヶ月)  
- 組織学習能力の飛躍的向上
- イノベーション創出サイクルの短縮
- 競争優位性の持続的強化

### 長期効果 (12ヶ月以上)
- 知識集約型組織への変革
- 業界リーダーシップの確立
- 持続可能な成長基盤の構築

---

**このナレッジ抽出ルールにより、KPT分析の価値が組織の持続的な知的資産として蓄積・活用され、継続的なイノベーション創出を支える強固な基盤が確立されます。** 📚🚀