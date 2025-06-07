#!/usr/bin/env python3
"""
KPT分析からナレッジ抽出・管理スクリプト

Usage:
    python scripts/knowledge_extraction.py extract --kpt-file plan/analysis/kpt_analysis.md
    python scripts/knowledge_extraction.py validate --knowledge-dir knowledge/
    python scripts/knowledge_extraction.py review --knowledge-file knowledge/technical_architecture/rag_pipeline.md
"""

import argparse
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import hashlib

class KnowledgeExtractionRules:
    """KPTナレッジ抽出ルール"""
    
    def __init__(self):
        self.extraction_criteria = {
            "technical_knowledge": {
                "minimum_success_rate": 0.80,
                "replication_potential": "high",
                "documentation_completeness": "comprehensive",
                "code_examples_available": True
            },
            "strategic_knowledge": {
                "measurable_impact": True,
                "decision_rationale_clear": True,
                "stakeholder_alignment": "achieved",
                "timeline_efficiency": 1.50  # 150%以上
            },
            "process_knowledge": {
                "workflow_documentation": "complete",
                "quality_metrics": "defined",
                "automation_potential": "high",
                "scalability_proven": True
            }
        }
        
        self.knowledge_categories = {
            "technical_architecture": {
                "path": "knowledge/technical_architecture/",
                "description": "技術アーキテクチャ・設計パターン",
                "examples": ["システム設計", "コンポーネント構成", "API設計"]
            },
            "development_patterns": {
                "path": "knowledge/development_patterns/",
                "description": "開発手法・プロセスパターン",
                "examples": ["テスト戦略", "実装パターン", "品質保証"]
            },
            "business_insights": {
                "path": "knowledge/business_insights/",
                "description": "ビジネス洞察・市場分析",
                "examples": ["市場戦略", "競合分析", "ROI分析"]
            },
            "project_management": {
                "path": "knowledge/project_management/",
                "description": "プロジェクト管理・意思決定",
                "examples": ["計画手法", "リスク管理", "ステークホルダー管理"]
            },
            "lessons_learned": {
                "path": "knowledge/lessons_learned/",
                "description": "教訓・改善点",
                "examples": ["成功要因", "失敗分析", "改善提案"]
            }
        }
        
        self.security_levels = {
            "public": {
                "description": "公開可能",
                "gitignore": False,
                "examples": ["一般的技術パターン", "オープンソース貢献"]
            },
            "internal": {
                "description": "内部限定",
                "gitignore": True,
                "examples": ["プロジェクト固有実装", "組織内学習"]
            },
            "confidential": {
                "description": "機密",
                "gitignore": True,
                "examples": ["戦略分析", "競合情報", "収益データ"]
            },
            "restricted": {
                "description": "制限",
                "gitignore": True,
                "examples": ["個人情報", "未発表情報", "パートナー機密"]
            }
        }

class KPTAnalyzer:
    """KPT分析ファイル解析"""
    
    def __init__(self):
        self.kpt_patterns = {
            "keep_section": r"##\s*🟢\s*\*\*Keep[^#]*?(?=##|\Z)",
            "problem_section": r"##\s*🔴\s*\*\*Problem[^#]*?(?=##|\Z)",
            "try_section": r"##\s*🚀\s*\*\*Try[^#]*?(?=##|\Z)",
            "success_metrics": r"([0-9]+(?:\.[0-9]+)?%|[0-9]+(?:\.[0-9]+)?倍|[0-9]+(?:\.[0-9]+)?x)",
            "implementation_details": r"```(?:python|javascript|bash|sql)(.*?)```",
            "quantitative_results": r"([0-9,]+(?:\.[0-9]+)?)\s*(行|件|秒|ヶ月|%)"
        }
    
    def parse_kpt_file(self, kpt_file_path: str) -> Dict[str, Any]:
        """KPTファイル解析"""
        
        with open(kpt_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        analysis_result = {
            "file_path": kpt_file_path,
            "extraction_date": datetime.now().isoformat(),
            "sections": {},
            "success_metrics": [],
            "implementation_details": [],
            "quantitative_results": []
        }
        
        # 各セクション抽出
        for section_name, pattern in self.kpt_patterns.items():
            if section_name.endswith('_section'):
                matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
                if matches:
                    analysis_result["sections"][section_name] = matches[0]
        
        # 成功指標抽出
        success_metrics = re.findall(self.kpt_patterns["success_metrics"], content)
        analysis_result["success_metrics"] = success_metrics
        
        # 実装詳細抽出
        implementation_details = re.findall(self.kpt_patterns["implementation_details"], content, re.DOTALL)
        analysis_result["implementation_details"] = implementation_details
        
        # 定量的結果抽出
        quantitative_results = re.findall(self.kpt_patterns["quantitative_results"], content)
        analysis_result["quantitative_results"] = quantitative_results
        
        return analysis_result
    
    def extract_knowledge_candidates(self, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """ナレッジ候補抽出"""
        
        candidates = []
        
        # Keep項目からナレッジ抽出
        if "keep_section" in analysis_result["sections"]:
            keep_content = analysis_result["sections"]["keep_section"]
            keep_items = self._parse_keep_items(keep_content)
            
            for item in keep_items:
                if self._meets_extraction_criteria(item):
                    candidate = {
                        "type": "success_pattern",
                        "source_section": "keep",
                        "title": item.get("title", "Unknown"),
                        "content": item.get("content", ""),
                        "success_evidence": item.get("evidence", []),
                        "replication_potential": self._assess_replication_potential(item),
                        "suggested_category": self._suggest_knowledge_category(item),
                        "security_level": self._assess_security_level(item)
                    }
                    candidates.append(candidate)
        
        # Try項目から改善提案抽出
        if "try_section" in analysis_result["sections"]:
            try_content = analysis_result["sections"]["try_section"]
            try_items = self._parse_try_items(try_content)
            
            for item in try_items:
                candidate = {
                    "type": "improvement_opportunity",
                    "source_section": "try",
                    "title": item.get("title", "Unknown"),
                    "content": item.get("content", ""),
                    "expected_impact": item.get("impact", ""),
                    "implementation_approach": item.get("approach", ""),
                    "suggested_category": self._suggest_knowledge_category(item),
                    "security_level": self._assess_security_level(item)
                }
                candidates.append(candidate)
        
        return candidates
    
    def _parse_keep_items(self, keep_content: str) -> List[Dict[str, Any]]:
        """Keep項目解析"""
        
        # 項目分割（### で始まる項目）
        items = re.split(r'\n###\s*\*?\*?([^#\n]+)', keep_content)
        
        parsed_items = []
        for i in range(1, len(items), 2):
            if i + 1 < len(items):
                title = items[i].strip()
                content = items[i + 1].strip()
                
                # 成功証拠抽出
                evidence = re.findall(r'\*\*実績\*\*:(.*?)(?=\*\*|$)', content, re.DOTALL)
                
                parsed_items.append({
                    "title": title,
                    "content": content,
                    "evidence": [e.strip() for e in evidence]
                })
        
        return parsed_items
    
    def _parse_try_items(self, try_content: str) -> List[Dict[str, Any]]:
        """Try項目解析"""
        
        items = re.split(r'\n###\s*\*?\*?([^#\n]+)', try_content)
        
        parsed_items = []
        for i in range(1, len(items), 2):
            if i + 1 < len(items):
                title = items[i].strip()
                content = items[i + 1].strip()
                
                # 期待効果抽出
                impact = re.findall(r'\*\*期待効果\*\*:(.*?)(?=\*\*|$)', content, re.DOTALL)
                approach = re.findall(r'\*\*アプローチ\*\*:(.*?)(?=\*\*|$)', content, re.DOTALL)
                
                parsed_items.append({
                    "title": title,
                    "content": content,
                    "impact": impact[0].strip() if impact else "",
                    "approach": approach[0].strip() if approach else ""
                })
        
        return parsed_items
    
    def _meets_extraction_criteria(self, item: Dict[str, Any]) -> bool:
        """抽出基準チェック"""
        
        # 成功証拠の有無
        if not item.get("evidence"):
            return False
        
        # 具体的な実装詳細の有無
        content = item.get("content", "")
        if not re.search(r'```|実装|コード|手法', content):
            return False
        
        # 定量的指標の有無
        if not re.search(r'[0-9]+(?:\.[0-9]+)?[%倍x]', content):
            return False
        
        return True
    
    def _assess_replication_potential(self, item: Dict[str, Any]) -> str:
        """再現可能性評価"""
        
        content = item.get("content", "")
        
        # 具体的な手順・コードの有無
        has_concrete_steps = bool(re.search(r'```|手順|ステップ|実装', content))
        
        # 前提条件の明記
        has_prerequisites = bool(re.search(r'前提|条件|要件', content))
        
        # 成功指標の定義
        has_metrics = bool(re.search(r'指標|メトリクス|測定', content))
        
        score = sum([has_concrete_steps, has_prerequisites, has_metrics])
        
        if score >= 3:
            return "high"
        elif score >= 2:
            return "medium"
        else:
            return "low"
    
    def _suggest_knowledge_category(self, item: Dict[str, Any]) -> str:
        """ナレッジカテゴリ推定"""
        
        content = item.get("content", "") + " " + item.get("title", "")
        content_lower = content.lower()
        
        # キーワードマッピング
        category_keywords = {
            "technical_architecture": ["アーキテクチャ", "設計", "API", "システム", "統合", "モジュール"],
            "development_patterns": ["テスト", "実装", "開発", "コード", "品質", "パターン"],
            "business_insights": ["市場", "競合", "戦略", "ROI", "収益", "ビジネス"],
            "project_management": ["計画", "意思決定", "管理", "リスク", "ステークホルダー"],
            "lessons_learned": ["教訓", "改善", "失敗", "成功要因", "学習"]
        }
        
        scores = {}
        for category, keywords in category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            scores[category] = score
        
        # 最高スコアのカテゴリを返す
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def _assess_security_level(self, item: Dict[str, Any]) -> str:
        """セキュリティレベル評価"""
        
        content = item.get("content", "") + " " + item.get("title", "")
        content_lower = content.lower()
        
        # 機密キーワード
        restricted_keywords = ["個人情報", "機密", "秘密", "パスワード", "api key"]
        confidential_keywords = ["戦略", "競合", "収益", "roi", "市場分析", "特許"]
        internal_keywords = ["内部", "プロジェクト固有", "組織", "チーム"]
        
        if any(keyword in content_lower for keyword in restricted_keywords):
            return "restricted"
        elif any(keyword in content_lower for keyword in confidential_keywords):
            return "confidential"
        elif any(keyword in content_lower for keyword in internal_keywords):
            return "internal"
        else:
            return "public"

class KnowledgeDocumentGenerator:
    """ナレッジ文書生成"""
    
    def __init__(self):
        self.document_template = """# 🎯 {title}

**抽出元**: KPT分析 ({source_file})  
**検証期間**: {validation_period}  
**実証効果**: {proven_effects}

---

## 📋 概要

{overview}

## 🎯 核心原則

{core_principles}

## 🔧 実装詳細

{implementation_details}

## 📊 成功指標

{success_metrics}

## 🎯 適用条件

{application_conditions}

## 🔄 継続的改善

{continuous_improvement}

---

## 🏆 結論

{conclusion}
"""
    
    def generate_knowledge_document(
        self, 
        candidate: Dict[str, Any], 
        kpt_analysis: Dict[str, Any]
    ) -> str:
        """ナレッジ文書生成"""
        
        # テンプレート変数の準備
        template_vars = {
            "title": candidate.get("title", "Unknown Knowledge"),
            "source_file": os.path.basename(kpt_analysis.get("file_path", "unknown")),
            "validation_period": self._extract_validation_period(kpt_analysis),
            "proven_effects": self._extract_proven_effects(candidate),
            "overview": self._generate_overview(candidate),
            "core_principles": self._extract_core_principles(candidate),
            "implementation_details": self._extract_implementation_details(candidate),
            "success_metrics": self._extract_success_metrics(candidate),
            "application_conditions": self._generate_application_conditions(candidate),
            "continuous_improvement": self._generate_improvement_section(candidate),
            "conclusion": self._generate_conclusion(candidate)
        }
        
        return self.document_template.format(**template_vars)
    
    def _extract_validation_period(self, kpt_analysis: Dict[str, Any]) -> str:
        """検証期間抽出"""
        
        # ファイル名から日付抽出を試行
        file_path = kpt_analysis.get("file_path", "")
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', file_path)
        
        if date_match:
            return date_match.group(1)
        else:
            return datetime.now().strftime("%Y年%m月%d日")
    
    def _extract_proven_effects(self, candidate: Dict[str, Any]) -> str:
        """実証効果抽出"""
        
        content = candidate.get("content", "")
        
        # 定量的効果を検索
        effects = re.findall(r'([0-9]+(?:\.[0-9]+)?[%倍x][^。]*)', content)
        
        if effects:
            return "、".join(effects[:3])  # 最大3つの効果
        else:
            return "定性的改善効果確認済み"
    
    def _generate_overview(self, candidate: Dict[str, Any]) -> str:
        """概要生成"""
        
        content = candidate.get("content", "")
        
        # 最初の段落を概要として使用
        paragraphs = content.split('\n\n')
        overview = paragraphs[0] if paragraphs else content[:200]
        
        return overview.strip()
    
    def _extract_core_principles(self, candidate: Dict[str, Any]) -> str:
        """核心原則抽出"""
        
        content = candidate.get("content", "")
        
        # 原則・アプローチに関する記述を検索
        principles = []
        
        # 番号付きリストを検索
        numbered_items = re.findall(r'\d+\.\s*\*\*([^*]+)\*\*[^0-9]*', content)
        principles.extend(numbered_items)
        
        # 箇条書きを検索
        bullet_items = re.findall(r'-\s*\*\*([^*]+)\*\*', content)
        principles.extend(bullet_items)
        
        if principles:
            formatted_principles = []
            for i, principle in enumerate(principles[:5], 1):
                formatted_principles.append(f"### {i}. **{principle.strip()}**")
            return "\n\n".join(formatted_principles)
        else:
            return "### 1. **実証済み手法の適用**\n- 成功事例に基づく確実なアプローチ"
    
    def _extract_implementation_details(self, candidate: Dict[str, Any]) -> str:
        """実装詳細抽出"""
        
        content = candidate.get("content", "")
        
        # コードブロックを検索
        code_blocks = re.findall(r'```(\w+)?\n(.*?)```', content, re.DOTALL)
        
        if code_blocks:
            formatted_code = []
            for lang, code in code_blocks:
                lang = lang or "python"
                formatted_code.append(f"```{lang}\n{code.strip()}\n```")
            return "\n\n".join(formatted_code)
        else:
            # 実装に関する記述を検索
            impl_patterns = [
                r'実装[^。]*。',
                r'手法[^。]*。',
                r'アプローチ[^。]*。'
            ]
            
            implementations = []
            for pattern in impl_patterns:
                matches = re.findall(pattern, content)
                implementations.extend(matches)
            
            return "\n".join(implementations) if implementations else "具体的な実装手順は元のKPT分析を参照してください。"
    
    def _extract_success_metrics(self, candidate: Dict[str, Any]) -> str:
        """成功指標抽出"""
        
        content = candidate.get("content", "")
        
        # 成功指標・メトリクスを検索
        metrics = re.findall(r'([0-9]+(?:\.[0-9]+)?[%倍x][^。]*)', content)
        
        if metrics:
            formatted_metrics = []
            for metric in metrics:
                formatted_metrics.append(f"- {metric}")
            return "\n".join(formatted_metrics)
        else:
            return "- 品質目標の達成\n- プロセス効率の改善\n- ステークホルダー満足度向上"
    
    def _generate_application_conditions(self, candidate: Dict[str, Any]) -> str:
        """適用条件生成"""
        
        content = candidate.get("content", "")
        
        # 前提条件・制約を検索
        conditions = []
        
        condition_patterns = [
            r'前提[^。]*。',
            r'条件[^。]*。',
            r'要件[^。]*。',
            r'制約[^。]*。'
        ]
        
        for pattern in condition_patterns:
            matches = re.findall(pattern, content)
            conditions.extend(matches)
        
        if conditions:
            formatted_conditions = []
            for condition in conditions:
                formatted_conditions.append(f"- {condition}")
            return "\n".join(formatted_conditions)
        else:
            return "- 類似のプロジェクト環境での適用\n- 十分なリソース・時間の確保\n- チームの技術レベル・学習意欲"
    
    def _generate_improvement_section(self, candidate: Dict[str, Any]) -> str:
        """改善セクション生成"""
        
        return """### 学習ループ
- 実装 → 測定 → 分析 → 改善 → 次プロジェクト適用

### ナレッジ蓄積
- 成功パターンの標準化
- 失敗事例の分析と対策
- 手法の他プロジェクトへの適用"""
    
    def _generate_conclusion(self, candidate: Dict[str, Any]) -> str:
        """結論生成"""
        
        title = candidate.get("title", "この手法")
        
        return f"**{title}により、実証済みの高い効果が期待できます。**\n\n### 核心的価値\n1. **効率性**: 実装・運用効率の大幅向上\n2. **品質**: 確実な品質目標達成\n3. **再現性**: 他プロジェクトでの適用可能性\n4. **学習**: 組織能力の継続的向上\n\nこの手法は、類似プロジェクトにおける新しいスタンダードとなります。 🚀"

class KnowledgeValidator:
    """ナレッジ品質検証"""
    
    def __init__(self):
        self.quality_criteria = {
            "content_quality": {
                "has_empirical_evidence": 0.25,
                "includes_concrete_examples": 0.25,
                "defines_success_metrics": 0.25,
                "specifies_constraints": 0.25
            },
            "documentation_quality": {
                "follows_standard_format": 0.30,
                "has_searchable_keywords": 0.25,
                "includes_code_examples": 0.25,
                "proper_categorization": 0.20
            },
            "practical_utility": {
                "replication_feasibility": 0.40,
                "clear_implementation_steps": 0.30,
                "troubleshooting_info": 0.30
            },
            "maintainability": {
                "version_info": 0.25,
                "update_schedule": 0.25,
                "related_documents": 0.25,
                "review_history": 0.25
            }
        }
    
    def validate_knowledge_document(self, file_path: str) -> Dict[str, Any]:
        """ナレッジ文書検証"""
        
        if not os.path.exists(file_path):
            return {"error": "File not found", "file_path": file_path}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        validation_results = {}
        overall_score = 0.0
        
        for dimension, criteria in self.quality_criteria.items():
            dimension_score = 0.0
            dimension_details = {}
            
            for criterion, weight in criteria.items():
                score = self._evaluate_criterion(content, criterion)
                dimension_details[criterion] = score
                dimension_score += score * weight
            
            validation_results[dimension] = {
                "score": dimension_score,
                "details": dimension_details
            }
            overall_score += dimension_score
        
        overall_score /= len(self.quality_criteria)
        
        return {
            "file_path": file_path,
            "overall_quality_score": overall_score,
            "validation_results": validation_results,
            "approval_status": "approved" if overall_score >= 0.8 else "revision_required",
            "recommendations": self._generate_recommendations(validation_results)
        }
    
    def _evaluate_criterion(self, content: str, criterion: str) -> float:
        """基準評価"""
        
        evaluation_map = {
            "has_empirical_evidence": lambda c: 1.0 if re.search(r'実証|実績|データ|結果|成果', c) else 0.0,
            "includes_concrete_examples": lambda c: 1.0 if re.search(r'```|例:|実装|コード', c) else 0.0,
            "defines_success_metrics": lambda c: 1.0 if re.search(r'指標|メトリクス|測定|[0-9]+%', c) else 0.0,
            "specifies_constraints": lambda c: 1.0 if re.search(r'前提|条件|制約|要件', c) else 0.0,
            "follows_standard_format": lambda c: 1.0 if re.search(r'# 🎯.*\*\*抽出元\*\*.*## 📋 概要', c, re.DOTALL) else 0.0,
            "has_searchable_keywords": lambda c: 1.0 if re.search(r'🎯|📋|🔧|📊', c) else 0.0,
            "includes_code_examples": lambda c: min(1.0, len(re.findall(r'```', c)) / 4),
            "proper_categorization": lambda c: 1.0 if re.search(r'technical_|development_|business_|project_|lessons_', c) else 0.0,
            "replication_feasibility": lambda c: 1.0 if re.search(r'手順|ステップ|実装|方法', c) else 0.0,
            "clear_implementation_steps": lambda c: min(1.0, len(re.findall(r'\d+\.|###|\*\*手順', c)) / 5),
            "troubleshooting_info": lambda c: 1.0 if re.search(r'注意|問題|エラー|対応', c) else 0.0,
            "version_info": lambda c: 1.0 if re.search(r'\d{4}-\d{2}-\d{2}|\d{4}年\d{1,2}月', c) else 0.0,
            "update_schedule": lambda c: 1.0 if re.search(r'更新|見直し|レビュー', c) else 0.0,
            "related_documents": lambda c: 1.0 if re.search(r'関連|参照|参考', c) else 0.0,
            "review_history": lambda c: 1.0 if re.search(r'履歴|バージョン|変更', c) else 0.0
        }
        
        evaluator = evaluation_map.get(criterion, lambda c: 0.5)
        return evaluator(content)
    
    def _generate_recommendations(self, validation_results: Dict[str, Any]) -> List[str]:
        """改善推奨生成"""
        
        recommendations = []
        
        for dimension, results in validation_results.items():
            if results["score"] < 0.7:
                low_criteria = [
                    criterion for criterion, score in results["details"].items()
                    if score < 0.5
                ]
                
                if low_criteria:
                    recommendations.append(f"{dimension}の改善が必要: {', '.join(low_criteria)}")
        
        return recommendations

def main():
    """メイン処理"""
    
    parser = argparse.ArgumentParser(description="KPT分析ナレッジ抽出・管理ツール")
    subparsers = parser.add_subparsers(dest="command", help="利用可能なコマンド")
    
    # extract コマンド
    extract_parser = subparsers.add_parser("extract", help="KPT分析からナレッジ抽出")
    extract_parser.add_argument("--kpt-file", required=True, help="KPT分析ファイルパス")
    extract_parser.add_argument("--output-dir", default="knowledge/", help="出力ディレクトリ")
    extract_parser.add_argument("--auto-generate", action="store_true", help="自動文書生成")
    
    # validate コマンド
    validate_parser = subparsers.add_parser("validate", help="ナレッジ文書検証")
    validate_parser.add_argument("--knowledge-dir", default="knowledge/", help="ナレッジディレクトリ")
    validate_parser.add_argument("--knowledge-file", help="特定ファイル検証")
    
    # review コマンド
    review_parser = subparsers.add_parser("review", help="ナレッジ品質レビュー")
    review_parser.add_argument("--knowledge-file", required=True, help="レビュー対象ファイル")
    review_parser.add_argument("--output-report", help="レビューレポート出力先")
    
    args = parser.parse_args()
    
    if args.command == "extract":
        extract_knowledge(args)
    elif args.command == "validate":
        validate_knowledge(args)
    elif args.command == "review":
        review_knowledge(args)
    else:
        parser.print_help()

def extract_knowledge(args):
    """ナレッジ抽出実行"""
    
    print(f"🔍 KPT分析ファイルを解析中: {args.kpt_file}")
    
    # KPT分析ファイル解析
    analyzer = KPTAnalyzer()
    analysis_result = analyzer.parse_kpt_file(args.kpt_file)
    
    # ナレッジ候補抽出
    candidates = analyzer.extract_knowledge_candidates(analysis_result)
    
    print(f"📋 {len(candidates)}個のナレッジ候補を抽出")
    
    # 候補一覧表示
    for i, candidate in enumerate(candidates, 1):
        print(f"{i}. {candidate['title']} ({candidate['suggested_category']}) - {candidate['security_level']}")
    
    if args.auto_generate:
        # 自動文書生成
        generator = KnowledgeDocumentGenerator()
        
        for candidate in candidates:
            if candidate['security_level'] in ['internal', 'confidential']:
                # ナレッジ文書生成
                document_content = generator.generate_knowledge_document(candidate, analysis_result)
                
                # ファイル保存
                category = candidate['suggested_category']
                title_safe = re.sub(r'[^\w\-_]', '_', candidate['title'])
                file_name = f"{title_safe}.md"
                
                output_path = Path(args.output_dir) / category / file_name
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(document_content)
                
                print(f"✅ ナレッジ文書生成: {output_path}")
    
    print("🎯 ナレッジ抽出完了")

def validate_knowledge(args):
    """ナレッジ検証実行"""
    
    validator = KnowledgeValidator()
    
    if args.knowledge_file:
        # 特定ファイル検証
        result = validator.validate_knowledge_document(args.knowledge_file)
        print(f"📋 検証結果: {args.knowledge_file}")
        print(f"総合品質スコア: {result['overall_quality_score']:.2f}")
        print(f"承認状況: {result['approval_status']}")
        
        if result['recommendations']:
            print("推奨改善点:")
            for rec in result['recommendations']:
                print(f"  - {rec}")
    
    else:
        # ディレクトリ全体検証
        knowledge_dir = Path(args.knowledge_dir)
        
        if not knowledge_dir.exists():
            print(f"❌ ナレッジディレクトリが見つかりません: {knowledge_dir}")
            return
        
        md_files = list(knowledge_dir.rglob("*.md"))
        
        print(f"🔍 {len(md_files)}個のナレッジファイルを検証中")
        
        total_score = 0.0
        approved_count = 0
        
        for md_file in md_files:
            result = validator.validate_knowledge_document(str(md_file))
            
            if 'error' not in result:
                total_score += result['overall_quality_score']
                if result['approval_status'] == 'approved':
                    approved_count += 1
                
                print(f"  {md_file.name}: {result['overall_quality_score']:.2f} ({result['approval_status']})")
        
        if md_files:
            avg_score = total_score / len(md_files)
            approval_rate = approved_count / len(md_files) * 100
            
            print(f"\n📊 検証サマリー:")
            print(f"  平均品質スコア: {avg_score:.2f}")
            print(f"  承認率: {approval_rate:.1f}%")

def review_knowledge(args):
    """ナレッジレビュー実行"""
    
    validator = KnowledgeValidator()
    result = validator.validate_knowledge_document(args.knowledge_file)
    
    print(f"📋 詳細レビュー: {args.knowledge_file}")
    print("=" * 50)
    
    if 'error' in result:
        print(f"❌ エラー: {result['error']}")
        return
    
    print(f"総合品質スコア: {result['overall_quality_score']:.2f}")
    print(f"承認状況: {result['approval_status']}")
    print()
    
    for dimension, dim_result in result['validation_results'].items():
        print(f"## {dimension}")
        print(f"スコア: {dim_result['score']:.2f}")
        
        for criterion, score in dim_result['details'].items():
            status = "✅" if score > 0.7 else "⚠️" if score > 0.3 else "❌"
            print(f"  {status} {criterion}: {score:.2f}")
        print()
    
    if result['recommendations']:
        print("## 改善推奨")
        for rec in result['recommendations']:
            print(f"  🔧 {rec}")
    
    # レポート出力
    if args.output_report:
        with open(args.output_report, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n📄 レポート出力: {args.output_report}")

if __name__ == "__main__":
    main()