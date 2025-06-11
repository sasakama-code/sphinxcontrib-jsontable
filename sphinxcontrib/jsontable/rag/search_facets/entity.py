"""Entity-based facet generation for semantic filtering.

Specialized module for generating entity facets from classification results,
including person, place, organization, and business term entities.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .base import FacetConfig


@dataclass
class EntityFacet:
    """Entity-based facet definition for semantic filtering.

    Args:
        entity_type: Type of entity (person, place, organization, etc.).
        display_name: Human-readable display name.
        entities: List of detected entities with counts.
        confidence_scores: Confidence scores for entity detection.
        ui_config: UI-specific configuration parameters.
    """

    entity_type: str
    display_name: str
    facet_type: str = "entity_terms"
    entities: dict[str, dict[str, Any]] = field(default_factory=dict)
    confidence_threshold: float = 0.6
    ui_config: dict[str, Any] = field(default_factory=dict)


class EntityFacetGenerator:
    """Generator for entity-based search facets.
    
    Handles creation of entity facets from entity classification results
    with confidence filtering and Japanese entity processing.
    """

    def __init__(self, config: FacetConfig):
        """Initialize entity facet generator.

        Args:
            config: Configuration for facet generation parameters.
        """
        self.config = config

    def generate_entity_facets(self, entity_classification) -> list[EntityFacet]:
        """Generate entity-based facets from classification results.

        Args:
            entity_classification: Entity classification containing detected entities.

        Returns:
            List of entity facets for semantic search functionality.
        """
        entity_facets = []

        if not self.config.enable_entity_facets:
            return entity_facets

        # 人名ファセット
        if entity_classification.persons:
            person_facet = self._create_person_facet(entity_classification.persons)
            if person_facet:
                entity_facets.append(person_facet)

        # 場所ファセット
        if entity_classification.places:
            place_facet = self._create_place_facet(entity_classification.places)
            if place_facet:
                entity_facets.append(place_facet)

        # 組織ファセット
        if entity_classification.organizations:
            org_facet = self._create_organization_facet(
                entity_classification.organizations
            )
            if org_facet:
                entity_facets.append(org_facet)

        # ビジネス用語ファセット
        if entity_classification.business_terms:
            business_facet = self._create_business_facet(
                entity_classification.business_terms
            )
            if business_facet:
                entity_facets.append(business_facet)

        return entity_facets

    def _create_person_facet(self, persons) -> EntityFacet | None:
        """Create person name entity facet from detected persons.

        Args:
            persons: List of PersonEntity objects.

        Returns:
            EntityFacet for person names or None if insufficient data.
        """
        if not persons:
            return None

        # 信頼度フィルタリング
        high_confidence_persons = [
            p for p in persons if p.confidence >= self.config.confidence_threshold
        ]

        if not high_confidence_persons:
            return None

        # エンティティ情報構築
        entities = {}
        for person in high_confidence_persons:
            entities[person.name] = {
                "confidence": person.confidence,
                "name_type": person.name_type,
                "count": 1,  # 実際のデータではカウントを正確に計算
            }

        ui_config = {
            "icon": "👤",
            "color": "#3498db",
            "sortBy": "confidence",
            "displayFormat": "name_with_confidence",
        }

        return EntityFacet(
            entity_type="persons",
            display_name="人名",
            entities=entities,
            confidence_threshold=self.config.confidence_threshold,
            ui_config=ui_config,
        )

    def _create_place_facet(self, places) -> EntityFacet | None:
        """Create place/location entity facet from detected places.

        Args:
            places: List of PlaceEntity objects.

        Returns:
            EntityFacet for places or None if insufficient data.
        """
        if not places:
            return None

        high_confidence_places = [
            p for p in places if p.confidence >= self.config.confidence_threshold
        ]

        if not high_confidence_places:
            return None

        entities = {}
        for place in high_confidence_places:
            entities[place.place] = {
                "confidence": place.confidence,
                "place_type": place.place_type,
                "count": 1,
            }

        ui_config = {
            "icon": "📍",
            "color": "#e74c3c",
            "sortBy": "place_type",
            "displayFormat": "place_with_type",
            "groupBy": "place_type",
        }

        return EntityFacet(
            entity_type="places",
            display_name="場所",
            entities=entities,
            confidence_threshold=self.config.confidence_threshold,
            ui_config=ui_config,
        )

    def _create_organization_facet(self, organizations) -> EntityFacet | None:
        """Create organization entity facet from detected organizations.

        Args:
            organizations: List of OrganizationEntity objects.

        Returns:
            EntityFacet for organizations or None if insufficient data.
        """
        if not organizations:
            return None

        high_confidence_orgs = [
            o for o in organizations if o.confidence >= self.config.confidence_threshold
        ]

        if not high_confidence_orgs:
            return None

        entities = {}
        for org in high_confidence_orgs:
            entities[org.organization] = {
                "confidence": org.confidence,
                "org_type": org.org_type,
                "count": 1,
            }

        ui_config = {
            "icon": "🏢",
            "color": "#9b59b6",
            "sortBy": "org_type",
            "displayFormat": "org_with_type",
            "groupBy": "org_type",
        }

        return EntityFacet(
            entity_type="organizations",
            display_name="組織",
            entities=entities,
            confidence_threshold=self.config.confidence_threshold,
            ui_config=ui_config,
        )

    def _create_business_facet(self, business_terms) -> EntityFacet | None:
        """Create business term entity facet from detected business terms.

        Args:
            business_terms: List of BusinessTermEntity objects.

        Returns:
            EntityFacet for business terms or None if insufficient data.
        """
        if not business_terms:
            return None

        high_confidence_terms = [
            b
            for b in business_terms
            if b.confidence >= self.config.confidence_threshold
        ]

        if not high_confidence_terms:
            return None

        entities = {}
        for term in high_confidence_terms:
            entities[term.term] = {
                "confidence": term.confidence,
                "category": term.category,
                "count": 1,
            }

        ui_config = {
            "icon": "💼",
            "color": "#f39c12",
            "sortBy": "category",
            "displayFormat": "term_with_category",
            "groupBy": "category",
        }

        return EntityFacet(
            entity_type="business_terms",
            display_name="ビジネス用語",
            entities=entities,
            confidence_threshold=self.config.confidence_threshold,
            ui_config=ui_config,
        )
