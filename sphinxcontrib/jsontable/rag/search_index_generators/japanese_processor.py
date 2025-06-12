"""Japanese query processing and optimization engine.

Provides comprehensive Japanese language query processing including
synonym expansion, business term recognition, and morphological analysis.
"""

import re
from typing import Any

__all__ = ["JapaneseQueryProcessor"]


class JapaneseQueryProcessor:
    """Japanese query processing and optimization engine.

    Provides comprehensive Japanese language query processing including
    synonym expansion, business term recognition, and morphological analysis.
    """

    def __init__(self):
        """Initialize Japanese query processor with dictionaries."""

        # 日本語クエリ拡張辞書
        self.synonym_dict = {
            "会社": ["企業", "法人", "組織", "株式会社"],
            "売上": ["売上高", "収益", "売り上げ", "販売実績"],
            "利益": ["収益", "プロフィット", "純利益", "営業利益"],
            "従業員": ["社員", "職員", "スタッフ", "人員"],
            "年度": ["会計年度", "FY", "事業年度"],
            "四半期": ["Q1", "Q2", "Q3", "Q4", "クォーター"],
        }

        # ビジネス用語マッピング
        self.business_term_mapping = {
            "ROI": ["投資収益率", "リターン"],
            "KPI": ["重要業績評価指標", "主要指標"],
            "EBITDA": ["利払い前・税引き前・減価償却前利益"],
            "B2B": ["企業間取引"],
            "B2C": ["企業・消費者間取引"],
        }

    def expand_query(self, query: str) -> list[str]:
        """クエリ拡張処理.

        Args:
            query: 入力クエリ文字列.

        Returns:
            拡張されたクエリのリスト.
        """
        expanded_queries = [query]  # 元のクエリ

        # 同義語展開
        for term, synonyms in self.synonym_dict.items():
            if term in query:
                for synonym in synonyms:
                    expanded_queries.append(query.replace(term, synonym))

        # ビジネス用語展開
        for term, variations in self.business_term_mapping.items():
            if term.lower() in query.lower():
                for variation in variations:
                    expanded_queries.append(query + " " + variation)

        return list(set(expanded_queries))  # 重複除去

    def extract_japanese_features(self, query: str) -> dict[str, Any]:
        """日本語クエリ特徴抽出.

        Args:
            query: 分析対象のクエリ文字列.

        Returns:
            クエリの特徴を含む辞書.
        """
        features = {
            "has_hiragana": bool(re.search(r"[ひ-ん]", query)),
            "has_katakana": bool(re.search(r"[ア-ン]", query)),
            "has_kanji": bool(re.search(r"[一-龯]", query)),
            "has_numbers": bool(re.search(r"\d+", query)),
            "has_business_terms": False,
            "query_type": "general",
        }

        # ビジネス用語チェック
        business_keywords = [
            "会社",
            "売上",
            "利益",
            "従業員",
            "年度",
            "ROI",
            "KPI",
            "株式会社",
            "企業",
            "業績",
            "売上高",
            "製造業",
            "情報",
        ]
        if any(keyword in query for keyword in business_keywords):
            features["has_business_terms"] = True
            features["query_type"] = "business"

        return features

    def extract_keywords(self, content: str) -> list[str]:
        """コンテンツから日本語キーワードを抽出.

        Args:
            content: 抽出対象のコンテンツ.

        Returns:
            抽出されたキーワードのリスト.
        """
        # 日本語キーワード抽出
        japanese_words = re.findall(r"[一-龯ひ-んア-ン]+", content)

        # 英数字キーワード抽出
        alphanumeric_words = re.findall(r"[A-Za-z0-9]+", content)

        all_keywords = japanese_words + alphanumeric_words

        # 最小キーワード長でフィルタリング
        return [keyword for keyword in all_keywords if len(keyword) >= 2]

    def extract_business_terms(self, content: str) -> list[str]:
        """ビジネス用語抽出.

        Args:
            content: 抽出対象のコンテンツ.

        Returns:
            抽出されたビジネス用語のリスト.
        """
        # ビジネス用語パターン
        business_patterns = [
            r"[一-龯\w]+株式会社",  # 会社名 + 株式会社
            r"株式会社[一-龯]+",  # 株式会社 + 名前
            r"[一-龯]+部",
            r"[一-龯]+課",
            r"\d+(?:,\d{3})*円",
            r"\d+億円",
            r"\d+万円",
            r"\d{4}年度",
            r"第\d+四半期",
            r"売上",
            r"利益",
            r"収益",
            r"従業員",
            r"ROI",
            r"KPI",
            r"EBITDA",
        ]

        business_terms = []
        for pattern in business_patterns:
            matches = re.findall(pattern, content)
            business_terms.extend(matches)

        return list(set(business_terms))  # 重複除去

    def categorize_business_content(self, content: str, category: str) -> bool:
        """ビジネスコンテンツ分類.

        Args:
            content: 分類対象のコンテンツ.
            category: 分類カテゴリ.

        Returns:
            指定カテゴリに該当する場合True.
        """
        category_keywords = {
            "financial": [
                "売上",
                "利益",
                "収益",
                "売上高",
                "純利益",
                "営業利益",
                "財務",
                "予算",
            ],
            "organizational": [
                "組織",
                "部門",
                "人事",
                "従業員",
                "社員",
                "採用",
                "研修",
            ],
            "operational": ["業務", "運営", "プロセス", "効率", "品質", "生産"],
            "strategic": ["戦略", "計画", "方針", "目標", "市場", "競合", "成長"],
        }

        keywords = category_keywords.get(category, [])
        return any(keyword in content for keyword in keywords)

    def parse_japanese_amount(self, amount_str: str) -> int:
        """日本語金額パース.

        Args:
            amount_str: 日本語金額文字列.

        Returns:
            パースされた金額（整数）.
        """
        # 数値抽出
        numbers = re.findall(r"\d+(?:,\d{3})*", amount_str)
        if not numbers:
            return 0

        base_amount = int(numbers[0].replace(",", ""))

        # 単位変換
        if "万円" in amount_str:
            return base_amount * 10000
        elif "億円" in amount_str:
            return base_amount * 100000000
        else:
            return base_amount
