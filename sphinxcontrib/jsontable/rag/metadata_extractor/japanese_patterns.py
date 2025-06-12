"""Japanese Language Processing Module for RAG Metadata Extraction.

This module provides Japanese-specific entity recognition patterns and 
language processing capabilities optimized for Japanese business documents.

Features:
- Japanese entity type recognition (names, organizations, dates, amounts)
- Business terminology detection
- Cultural context-aware pattern matching
- Optimized for enterprise documents and data analysis

Created: 2025-06-12 (split from metadata_extractor.py)
Author: Claude Code Assistant
"""

from __future__ import annotations

import re
from typing import Any


class JapanesePatternManager:
    """Manages Japanese language recognition patterns for entity detection.
    
    This class encapsulates all Japanese-specific pattern matching logic
    for accurate entity recognition in Japanese business data.
    """

    def __init__(self) -> None:
        """Initialize Japanese pattern recognition systems."""
        self.entity_patterns = self._init_japanese_patterns()
        self.type_patterns = self._init_type_patterns()

    def _init_japanese_patterns(self) -> dict[str, list[str]]:
        """Initialize Japanese language recognition patterns.

        Returns:
            Dictionary mapping entity types to field name patterns.
        """
        return {
            "name_indicators": [
                "名前",
                "name",
                "氏名",
                "担当者",
                "責任者",
                "作成者",
                "更新者",
                "申請者",
                "承認者",
                "姓名",
                "フルネーム",
                "full_name",
                "user_name",
                "username",
                "author",
                "creator",
                "manager",
                "assigned_to",
                "contact_person",
            ],
            "organization_indicators": [
                "会社",
                "company",
                "企業",
                "組織",
                "部署",
                "department",
                "部門",
                "課",
                "係",
                "班",
                "チーム",
                "team",
                "グループ",
                "group",
                "事業部",
                "営業所",
                "支店",
                "支社",
                "本社",
                "法人",
                "corporation",
                "organization",
                "affiliate",
                "subsidiary",
                "division",
            ],
            "date_indicators": [
                "日付",
                "date",
                "日時",
                "datetime",
                "作成日",
                "更新日",
                "登録日",
                "申請日",
                "承認日",
                "開始日",
                "終了日",
                "期限",
                "deadline",
                "due_date",
                "created_at",
                "updated_at",
                "registered_at",
                "start_date",
                "end_date",
                "timestamp",
                "年月日",
                "時刻",
                "time",
            ],
            "amount_indicators": [
                "金額",
                "amount",
                "価格",
                "price",
                "料金",
                "fee",
                "費用",
                "cost",
                "売上",
                "sales",
                "revenue",
                "利益",
                "profit",
                "損失",
                "loss",
                "予算",
                "budget",
                "単価",
                "unit_price",
                "合計",
                "total",
                "小計",
                "subtotal",
                "税込",
                "tax_included",
                "税抜",
                "tax_excluded",
                "消費税",
                "consumption_tax",
                "円",
                "yen",
                "dollar",
                "euro",
            ],
            "location_indicators": [
                "住所",
                "address",
                "所在地",
                "location",
                "場所",
                "place",
                "都道府県",
                "prefecture",
                "市区町村",
                "city",
                "郵便番号",
                "postal_code",
                "zip_code",
                "国",
                "country",
                "地域",
                "region",
                "エリア",
                "area",
                "地区",
                "district",
            ],
        }

    def _init_type_patterns(self) -> dict[str, dict[str, Any]]:
        """Initialize type inference patterns for Japanese data.

        Returns:
            Dictionary mapping data types to recognition patterns and metadata.
        """
        return {
            "email": {
                "pattern": re.compile(
                    r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
                ),
                "description": "メールアドレス",
                "semantic_type": "contact_info",
            },
            "phone_jp": {
                "pattern": re.compile(
                    r"^(\+81|0)[0-9\-\(\)\s]{8,15}$"
                ),
                "description": "電話番号（日本）",
                "semantic_type": "contact_info",
            },
            "postal_code_jp": {
                "pattern": re.compile(r"^\d{3}-\d{4}$"),
                "description": "郵便番号（日本）",
                "semantic_type": "location",
            },
            "url": {
                "pattern": re.compile(
                    r"^https?://[a-zA-Z0-9\-\._~:/?#[\]@!$&'()*+,;=]+$"
                ),
                "description": "URL",
                "semantic_type": "web_reference",
            },
            "japanese_name": {
                "pattern": re.compile(r"^[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF\s]+$"),
                "description": "日本語氏名",
                "semantic_type": "person_name",
            },
            "date_iso": {
                "pattern": re.compile(r"^\d{4}-\d{2}-\d{2}$"),
                "description": "ISO日付形式",
                "semantic_type": "temporal",
            },
            "datetime_iso": {
                "pattern": re.compile(
                    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?$"
                ),
                "description": "ISO日時形式",
                "semantic_type": "temporal",
            },
            "japanese_company": {
                "pattern": re.compile(
                    r".*(?:株式会社|有限会社|合同会社|合資会社|合名会社|㈱|㈲|Co\.|Corp\.|Inc\.|Ltd\.).*"
                ),
                "description": "日本企業名",
                "semantic_type": "organization",
            },
            "currency_yen": {
                "pattern": re.compile(r"^¥?[\d,]+(?:\.\d{2})?$"),
                "description": "日本円通貨",
                "semantic_type": "monetary",
            },
        }

    def get_entity_type_for_field(self, field_name: str) -> str | None:
        """Get the most likely entity type for a given field name.
        
        Args:
            field_name: The field name to analyze
            
        Returns:
            The detected entity type or None if no match found
        """
        field_lower = field_name.lower()
        
        for entity_type, indicators in self.entity_patterns.items():
            for indicator in indicators:
                if indicator.lower() in field_lower:
                    return entity_type.replace("_indicators", "")
        
        return None

    def infer_semantic_type(self, value: str) -> tuple[str | None, str | None]:
        """Infer semantic type from a string value using Japanese patterns.
        
        Args:
            value: The string value to analyze
            
        Returns:
            Tuple of (semantic_type, description) or (None, None) if no match
        """
        if not isinstance(value, str):
            return None, None
            
        value = value.strip()
        if not value:
            return None, None
            
        for type_name, type_info in self.type_patterns.items():
            if type_info["pattern"].match(value):
                return type_info["semantic_type"], type_info["description"]
                
        return None, None

    def is_japanese_text(self, text: str) -> bool:
        """Check if text contains Japanese characters.
        
        Args:
            text: Text to analyze
            
        Returns:
            True if text contains Japanese characters
        """
        if not isinstance(text, str):
            return False
            
        # Check for Hiragana, Katakana, or Kanji
        japanese_pattern = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]')
        return bool(japanese_pattern.search(text))

    def extract_business_terms(self, text: str) -> list[str]:
        """Extract Japanese business terminology from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of detected business terms
        """
        if not isinstance(text, str) or not text.strip():
            return []
            
        business_terms = [
            "売上", "利益", "損失", "予算", "コスト", "ROI", "KPI",
            "営業", "マーケティング", "販売", "購買", "調達",
            "製造", "品質", "保証", "検査", "監査",
            "人事", "労務", "給与", "賞与", "福利厚生",
            "経理", "財務", "会計", "税務", "資金",
            "企画", "戦略", "計画", "目標", "成果",
            "顧客", "クライアント", "取引先", "パートナー", "競合",
            "契約", "合意", "承認", "決裁", "稟議",
        ]
        
        detected_terms = []
        text_lower = text.lower()
        
        for term in business_terms:
            if term in text or term.lower() in text_lower:
                detected_terms.append(term)
                
        return list(set(detected_terms))  # Remove duplicates

    def normalize_company_name(self, company_name: str) -> str:
        """Normalize Japanese company name format.
        
        Args:
            company_name: Raw company name
            
        Returns:
            Normalized company name
        """
        if not isinstance(company_name, str):
            return company_name
            
        # Normalize common company suffixes
        normalized = company_name
        replacements = {
            "㈱": "株式会社",
            "㈲": "有限会社", 
            "(株)": "株式会社",
            "(有)": "有限会社",
            "Co.": "株式会社",
            "Corp.": "株式会社",
            "Inc.": "株式会社",
            "Ltd.": "株式会社",
        }
        
        for old, new in replacements.items():
            normalized = normalized.replace(old, new)
            
        return normalized.strip()