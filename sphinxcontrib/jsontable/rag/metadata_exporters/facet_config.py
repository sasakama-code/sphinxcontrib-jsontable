"""Facet configuration exporter.

Specialized module for exporting facet-specific configuration
for search interface implementation with Japanese localization.
"""

from __future__ import annotations

from typing import Any

from ..search_facets import GeneratedFacets
from .base import BaseMetadataExporter


class FacetConfigExporter(BaseMetadataExporter):
    """Facet configuration exporter.
    
    Exports facet-specific configuration for search interface
    implementation with Japanese UI standards.
    """

    def __init__(self):
        """Initialize facet config exporter."""
        super().__init__()

    def export(self, facets: GeneratedFacets) -> dict[str, Any]:
        """Export facet-specific configuration.

        Args:
            facets: Generated facets for UI configuration.

        Returns:
            Facet configuration for search interface implementation.
        """
        return {
            "ui_configuration": self._create_ui_configuration(),
            "facet_groups": self._organize_facets_into_groups(facets),
            "interaction_config": self._create_interaction_config(),
            "display_config": self._create_display_config(),
            "responsive_config": self._create_responsive_config(),
        }

    def _create_ui_configuration(self) -> dict[str, Any]:
        """Create UI configuration for facets."""
        return {
            "layout": "sidebar",
            "collapsible_sections": True,
            "max_visible_facets": 8,
            "enable_facet_search": True,
        }

    def _create_interaction_config(self) -> dict[str, Any]:
        """Create interaction configuration."""
        return {
            "multiple_selection": True,
            "clear_all_button": True,
            "facet_counting": True,
            "dynamic_filtering": True,
        }

    def _create_display_config(self) -> dict[str, Any]:
        """Create display configuration."""
        return {
            "show_facet_counts": True,
            "show_zero_counts": False,
            "facet_sorting": "count_desc",
            "localization": "ja_JP",
        }

    def _create_responsive_config(self) -> dict[str, Any]:
        """Create responsive configuration."""
        return {
            "mobile_breakpoint": "768px",
            "tablet_breakpoint": "1024px",
            "mobile_layout": "bottom_sheet",
            "tablet_layout": "collapsible_sidebar",
        }
