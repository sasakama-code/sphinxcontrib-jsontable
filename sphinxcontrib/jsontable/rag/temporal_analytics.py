"""Temporal analytics and Japanese entity classification module.

Provides specialized entity recognition and classification capabilities optimized
for Japanese text including person names, place names, organizations, and business
terms with advanced pattern matching and confidence scoring.

Features:
- Japanese-specialized entity recognition
- Person name detection (Kanji, Katakana, Western)
- Geographic location classification
- Organization type identification
- Business terminology detection
- Confidence scoring for all entity types
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class PersonEntity:
    """Person name entity with confidence scoring and type classification.

    Attributes:
        name: Detected person name.
        confidence: Detection confidence score (0.0-1.0).
        name_type: Type of name format (japanese_kanji, katakana, western).
        position: Position in text as (start, end) tuple.
    """

    name: str
    confidence: float
    name_type: str  # "japanese_kanji", "katakana", "western"
    position: tuple[int, int]  # Position in text


@dataclass
class PlaceEntity:
    """Geographic location entity with type classification and confidence.

    Attributes:
        place: Detected place name.
        confidence: Detection confidence score (0.0-1.0).
        place_type: Type of place (prefecture, city, district, station).
        position: Position in text as (start, end) tuple.
    """

    place: str
    confidence: float
    place_type: str  # "prefecture", "city", "district", "station"
    position: tuple[int, int]


@dataclass
class OrganizationEntity:
    """Organization entity with type classification and confidence scoring.

    Attributes:
        organization: Detected organization name.
        confidence: Detection confidence score (0.0-1.0).
        org_type: Type of organization (company, department, government).
        position: Position in text as (start, end) tuple.
    """

    organization: str
    confidence: float
    org_type: str  # "company", "department", "government"
    position: tuple[int, int]


@dataclass
class BusinessTermEntity:
    """Business terminology entity with category classification.

    Attributes:
        term: Detected business term.
        confidence: Detection confidence score (0.0-1.0).
        category: Term category (job_title, industry, skill).
        position: Position in text as (start, end) tuple.
    """

    term: str
    confidence: float
    category: str  # "job_title", "industry", "skill"
    position: tuple[int, int]


@dataclass
class EntityClassification:
    """Comprehensive entity classification results with confidence metrics.

    Attributes:
        persons: List of detected person entities.
        places: List of detected place entities.
        organizations: List of detected organization entities.
        business_terms: List of detected business term entities.
        confidence_scores: Overall confidence scores by entity type.
    """

    persons: list[PersonEntity] = field(default_factory=list)
    places: list[PlaceEntity] = field(default_factory=list)
    organizations: list[OrganizationEntity] = field(default_factory=list)
    business_terms: list[BusinessTermEntity] = field(default_factory=list)
    confidence_scores: dict[str, float] = field(default_factory=dict)


@dataclass
class TemporalStats:
    """Statistical analysis results for temporal data with trend detection.

    Attributes:
        time_range: Start and end time range.
        duration: Total duration of the time series.
        frequency_pattern: Detected frequency pattern.
        seasonal_indicators: Seasonal pattern indicators.
        trend_direction: Overall trend direction.
    """

    time_range: tuple[str, str]
    duration: str
    frequency_pattern: str
    seasonal_indicators: dict[str, Any]
    trend_direction: str


class JapaneseEntityClassifier:
    """
    Japanese-specialized entity recognition and classification processor.

    Provides advanced entity recognition capabilities optimized for Japanese
    text including person names, place names, organizations, and business terms
    with high accuracy pattern matching and context awareness.
    """

    def __init__(self):
        """
        Initialize Japanese entity classifier with pattern recognition rules.

        Sets up comprehensive pattern matching for Japanese entity types
        including names, places, organizations, and business terminology.
        """
        # Japanese person name patterns
        self.person_patterns = [
            r"[一-龯]{1,4}[　\s][一-龯]{1,3}",  # 漢字姓名（スペース区切り）
            r"[一-龯]{2,4}",  # 漢字のみ（姓または名）
            r"[ア-ン]{2,8}",  # カタカナ名
            r"[a-zA-Z]{2,20}\s[a-zA-Z]{2,20}",  # 英語名
        ]

        # Japanese place name patterns
        self.place_patterns = [
            r"[一-龯]{2,3}[都道府県]",  # 都道府県
            r"[一-龯]{1,8}[市区町村]",  # 市区町村
            r"[一-龯]{1,10}駅",  # 駅名
            r"[一-龯]{1,8}[町丁目]",  # 町丁目
        ]

        # Japanese organization name patterns
        self.organization_patterns = [
            r"[一-龯ァ-ヴa-zA-Z0-9]+株式会社",  # 株式会社
            r"株式会社[一-龯ァ-ヴa-zA-Z0-9]+",  # 株式会社
            r"[一-龯ァ-ヴa-zA-Z0-9]+[部課係室]",  # 部署名
            r"[一-龯ァ-ヴa-zA-Z0-9]+省",  # 省庁
        ]

        # Japanese business term patterns
        self.business_patterns = [
            r"[一-龯]{2,6}[主任係長課長部長取締役社長]",  # 役職
            r"[エンジニアマネージャーディレクター]{4,12}",  # カタカナ職種
            r"[SE|PM|PL|QA]{2,3}",  # IT職種略語
        ]

    def classify_entities(self, text_data: list[str]) -> EntityClassification:
        """テキストデータからエンティティを分類"""
        classification = EntityClassification()

        for text in text_data:
            if not isinstance(text, str):
                continue

            # 人名の抽出
            persons = self._extract_persons(text)
            classification.persons.extend(persons)

            # 場所名の抽出
            places = self._extract_places(text)
            classification.places.extend(places)

            # 組織名の抽出
            organizations = self._extract_organizations(text)
            classification.organizations.extend(organizations)

            # ビジネス用語の抽出
            business_terms = self._extract_business_terms(text)
            classification.business_terms.extend(business_terms)

        # 信頼度スコアの計算
        classification.confidence_scores = self._calculate_confidence_scores(
            classification
        )

        return classification

    def _extract_persons(self, text: str) -> list[PersonEntity]:
        """日本語人名の抽出"""
        persons = []

        for pattern in self.person_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                name = match.group()
                confidence = self._calculate_person_confidence(name)
                name_type = self._classify_name_type(name)

                persons.append(
                    PersonEntity(
                        name=name,
                        confidence=confidence,
                        name_type=name_type,
                        position=(match.start(), match.end()),
                    )
                )

        return persons

    def _extract_places(self, text: str) -> list[PlaceEntity]:
        """日本語地名の抽出"""
        places = []

        for pattern in self.place_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                place = match.group()
                confidence = self._calculate_place_confidence(place)
                place_type = self._classify_place_type(place)

                places.append(
                    PlaceEntity(
                        place=place,
                        confidence=confidence,
                        place_type=place_type,
                        position=(match.start(), match.end()),
                    )
                )

        return places

    def _extract_organizations(self, text: str) -> list[OrganizationEntity]:
        """組織名の抽出"""
        organizations = []

        for pattern in self.organization_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                org = match.group()
                confidence = self._calculate_org_confidence(org)
                org_type = self._classify_org_type(org)

                organizations.append(
                    OrganizationEntity(
                        organization=org,
                        confidence=confidence,
                        org_type=org_type,
                        position=(match.start(), match.end()),
                    )
                )

        return organizations

    def _extract_business_terms(self, text: str) -> list[BusinessTermEntity]:
        """ビジネス用語の抽出"""
        business_terms = []

        for pattern in self.business_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                term = match.group()
                confidence = self._calculate_business_confidence(term)
                category = self._classify_business_category(term)

                business_terms.append(
                    BusinessTermEntity(
                        term=term,
                        confidence=confidence,
                        category=category,
                        position=(match.start(), match.end()),
                    )
                )

        return business_terms

    def _calculate_person_confidence(self, name: str) -> float:
        """人名の信頼度計算"""
        # 長さベースの基本信頼度
        if 2 <= len(name) <= 4:
            return 0.8
        elif 5 <= len(name) <= 8:
            return 0.6
        else:
            return 0.4

    def _classify_name_type(self, name: str) -> str:
        """名前の種類分類"""
        if re.match(r"[一-龯]+", name):
            return "japanese_kanji"
        elif re.match(r"[ア-ン]+", name):
            return "katakana"
        elif re.match(r"[a-zA-Z\s]+", name):
            return "western"
        else:
            return "mixed"

    def _calculate_place_confidence(self, place: str) -> float:
        """地名の信頼度計算"""
        if place.endswith(("都", "道", "府", "県")):
            return 0.9
        elif place.endswith(("市", "区", "町", "村")):
            return 0.8
        elif place.endswith("駅"):
            return 0.7
        else:
            return 0.5

    def _classify_place_type(self, place: str) -> str:
        """地名の種類分類"""
        if place.endswith(("都", "道", "府", "県")):
            return "prefecture"
        elif place.endswith(("市", "区", "町", "村")):
            return "city"
        elif place.endswith("駅"):
            return "station"
        else:
            return "district"

    def _calculate_org_confidence(self, org: str) -> float:
        """組織名の信頼度計算"""
        if "株式会社" in org:
            return 0.9
        elif org.endswith(("部", "課", "係", "室")):
            return 0.8
        elif org.endswith("省"):
            return 0.9
        else:
            return 0.6

    def _classify_org_type(self, org: str) -> str:
        """組織の種類分類"""
        if "株式会社" in org:
            return "company"
        elif org.endswith(("部", "課", "係", "室")):
            return "department"
        elif org.endswith("省"):
            return "government"
        else:
            return "other"

    def _calculate_business_confidence(self, term: str) -> float:
        """ビジネス用語の信頼度計算"""
        job_titles = ["主任", "係長", "課長", "部長", "取締役", "社長"]
        if any(title in term for title in job_titles):
            return 0.8
        else:
            return 0.6

    def _classify_business_category(self, term: str) -> str:
        """ビジネス用語のカテゴリ分類"""
        job_titles = ["主任", "係長", "課長", "部長", "取締役", "社長"]
        if any(title in term for title in job_titles):
            return "job_title"
        elif term in ["SE", "PM", "PL", "QA"]:
            return "it_role"
        else:
            return "general"

    def _calculate_confidence_scores(
        self, classification: EntityClassification
    ) -> dict[str, float]:
        """全体的な信頼度スコアの計算"""
        scores = {}

        if classification.persons:
            scores["persons"] = sum(p.confidence for p in classification.persons) / len(
                classification.persons
            )

        if classification.places:
            scores["places"] = sum(p.confidence for p in classification.places) / len(
                classification.places
            )

        if classification.organizations:
            scores["organizations"] = sum(
                o.confidence for o in classification.organizations
            ) / len(classification.organizations)

        if classification.business_terms:
            scores["business_terms"] = sum(
                b.confidence for b in classification.business_terms
            ) / len(classification.business_terms)

        return scores