"""UI configuration generation for search facets.

Specialized module for generating user interface configurations
for all facet types with Japanese localization support.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .base import GeneratedFacets


class UIConfigGenerator:
    """Generator for facet UI configurations.

    Handles creation of user interface configurations for all facet types
    with responsive design, accessibility, and Japanese localization.
    """

    def __init__(self, locale: str = "ja_JP"):
        """Initialize UI config generator.

        Args:
            locale: Locale for UI configuration (default: ja_JP).
        """
        self.locale = locale

    def create_generation_metadata(self, facets: GeneratedFacets) -> dict:
        """Create metadata about the facet generation process.

        Args:
            facets: Generated facets container with all facet types.

        Returns:
            Dictionary with generation timestamp, counts, and configuration.
        """
        return {
            "generation_timestamp": datetime.now().isoformat(),
            "facet_counts": {
                "categorical": len(facets.categorical_facets),
                "numerical": len(facets.numerical_facets),
                "temporal": len(facets.temporal_facets),
                "entity": len(facets.entity_facets),
            },
            "total_facets": (
                len(facets.categorical_facets)
                + len(facets.numerical_facets)
                + len(facets.temporal_facets)
                + len(facets.entity_facets)
            ),
            "ui_locale": self.locale,
            "accessibility_enabled": True,
            "responsive_design": True,
        }

    def generate_search_interface_config(self, facets: GeneratedFacets) -> dict:
        """Generate complete search interface configuration.

        Args:
            facets: Generated facets for UI configuration.

        Returns:
            Comprehensive UI configuration for search interface implementation.
        """
        return {
            "layout_config": self._generate_layout_config(),
            "facet_panel_config": self._generate_facet_panel_config(facets),
            "search_bar_config": self._generate_search_bar_config(),
            "results_config": self._generate_results_config(),
            "interaction_config": self._generate_interaction_config(),
            "accessibility_config": self._generate_accessibility_config(),
            "responsive_config": self._generate_responsive_config(),
            "localization_config": self._generate_localization_config(),
        }

    def _generate_layout_config(self) -> dict:
        """Generate layout configuration for search interface.

        Returns:
            Layout configuration with Japanese UI standards.
        """
        return {
            "main_layout": "two_column",
            "facet_position": "left_sidebar",
            "facet_width": "300px",
            "content_width": "calc(100% - 320px)",
            "header_height": "60px",
            "footer_height": "40px",
            "spacing": {
                "margin": "16px",
                "padding": "12px",
                "gap": "8px",
            },
            "breakpoints": {
                "mobile": "768px",
                "tablet": "1024px",
                "desktop": "1200px",
            },
        }

    def _generate_facet_panel_config(self, facets: GeneratedFacets) -> dict:
        """Generate facet panel configuration.

        Args:
            facets: Generated facets for panel organization.

        Returns:
            Facet panel configuration with groups and ordering.
        """
        return {
            "collapsible_sections": True,
            "max_visible_facets": 8,
            "enable_facet_search": True,
            "enable_clear_all": True,
            "facet_groups": self._organize_facets_into_groups(facets),
            "default_collapsed": {
                "categorical": False,
                "numerical": False,
                "temporal": True,
                "entity": True,
            },
            "animation": {
                "enable_transitions": True,
                "transition_duration": "200ms",
                "easing": "ease-in-out",
            },
        }

    def _generate_search_bar_config(self) -> dict:
        """Generate search bar configuration.

        Returns:
            Search bar configuration with Japanese input support.
        """
        return {
            "placeholder_text": "検索キーワードを入力...",
            "enable_autocomplete": True,
            "enable_suggestions": True,
            "enable_voice_input": False,  # 将来の拡張
            "input_validation": {
                "min_length": 1,
                "max_length": 200,
                "allow_japanese": True,
                "allow_symbols": True,
            },
            "search_behavior": {
                "auto_search_delay": 300,  # ms
                "enable_enter_to_search": True,
                "clear_on_escape": True,
            },
        }

    def _generate_results_config(self) -> dict:
        """Generate search results configuration.

        Returns:
            Results display configuration with pagination and sorting.
        """
        return {
            "items_per_page": 20,
            "pagination_type": "numbered",  # or "infinite_scroll"
            "enable_sorting": True,
            "sort_options": [
                {"key": "relevance", "label": "関連度順"},
                {"key": "date_desc", "label": "新しい順"},
                {"key": "date_asc", "label": "古い順"},
                {"key": "name_asc", "label": "名前順（昇順）"},
                {"key": "name_desc", "label": "名前順（降順）"},
            ],
            "highlight_config": {
                "enable_highlighting": True,
                "highlight_class": "search-highlight",
                "max_highlighted_length": 200,
            },
            "summary_config": {
                "show_result_count": True,
                "show_search_time": True,
                "result_count_format": "{count}件の結果 ({time}秒)",
            },
        }

    def _generate_interaction_config(self) -> dict:
        """Generate interaction configuration.

        Returns:
            User interaction configuration for faceted search.
        """
        return {
            "multiple_selection": True,
            "clear_all_button": True,
            "facet_counting": True,
            "dynamic_filtering": True,
            "keyboard_shortcuts": {
                "search_focus": "/",
                "clear_all": "ctrl+r",
                "toggle_facets": "ctrl+f",
            },
            "mouse_interactions": {
                "enable_hover_effects": True,
                "enable_drag_resize": True,
                "double_click_behavior": "select_all",
            },
        }

    def _generate_accessibility_config(self) -> dict:
        """Generate accessibility configuration.

        Returns:
            Accessibility configuration for inclusive design.
        """
        return {
            "aria_labels": {
                "search_input": "検索入力フィールド",
                "facet_panel": "検索フィルター",
                "results_area": "検索結果",
                "pagination": "ページナビゲーション",
            },
            "keyboard_navigation": {
                "enable_tab_navigation": True,
                "enable_arrow_navigation": True,
                "focus_indicators": True,
                "skip_links": True,
            },
            "screen_reader": {
                "announce_results": True,
                "announce_filters": True,
                "live_region_updates": True,
            },
            "color_contrast": {
                "minimum_ratio": 4.5,
                "large_text_ratio": 3.0,
                "check_compliance": True,
            },
        }

    def _generate_responsive_config(self) -> dict:
        """Generate responsive design configuration.

        Returns:
            Responsive configuration for mobile/tablet/desktop.
        """
        return {
            "mobile": {
                "facet_position": "bottom_sheet",
                "search_layout": "stacked",
                "items_per_page": 10,
                "enable_swipe_gestures": True,
            },
            "tablet": {
                "facet_position": "collapsible_sidebar",
                "search_layout": "side_by_side",
                "items_per_page": 15,
                "enable_touch_gestures": True,
            },
            "desktop": {
                "facet_position": "fixed_sidebar",
                "search_layout": "three_column",
                "items_per_page": 20,
                "enable_hover_interactions": True,
            },
        }

    def _generate_localization_config(self) -> dict:
        """Generate localization configuration for Japanese UI.

        Returns:
            Localization configuration with Japanese text and formatting.
        """
        return {
            "locale": self.locale,
            "language": "ja",
            "text_direction": "ltr",
            "date_format": "YYYY年MM月DD日",
            "number_format": "ja-JP",
            "currency_format": "¥#,##0",
            "ui_texts": {
                "search_placeholder": "検索...",
                "no_results": "結果が見つかりませんでした",
                "loading": "読み込み中...",
                "error": "エラーが発生しました",
                "clear_all": "すべてクリア",
                "show_more": "さらに表示",
                "show_less": "表示を減らす",
                "apply_filters": "フィルターを適用",
                "reset_filters": "フィルターをリセット",
            },
        }

    def _organize_facets_into_groups(self, facets: GeneratedFacets) -> list[dict]:
        """Organize facets into logical groups for UI presentation.

        Args:
            facets: Generated facets to organize.

        Returns:
            List of facet groups with display order and metadata.
        """
        groups = []

        if facets.categorical_facets:
            groups.append(
                {
                    "group_name": "カテゴリ",
                    "group_id": "categorical",
                    "facets": [f.field_name for f in facets.categorical_facets],
                    "collapsed": False,
                    "icon": "📂",
                    "order": 1,
                }
            )

        if facets.numerical_facets:
            groups.append(
                {
                    "group_name": "数値範囲",
                    "group_id": "numerical",
                    "facets": [f.field_name for f in facets.numerical_facets],
                    "collapsed": False,
                    "icon": "📊",
                    "order": 2,
                }
            )

        if facets.temporal_facets:
            groups.append(
                {
                    "group_name": "日付・時間",
                    "group_id": "temporal",
                    "facets": [f.field_name for f in facets.temporal_facets],
                    "collapsed": True,
                    "icon": "📅",
                    "order": 3,
                }
            )

        if facets.entity_facets:
            groups.append(
                {
                    "group_name": "エンティティ",
                    "group_id": "entities",
                    "facets": [f.entity_type for f in facets.entity_facets],
                    "collapsed": True,
                    "icon": "🏷️",
                    "order": 4,
                }
            )

        return sorted(groups, key=lambda g: g["order"])
