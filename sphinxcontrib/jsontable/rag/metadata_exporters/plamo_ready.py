"""PLaMo-Embedding-1B optimized format exporter.

Specialized module for exporting metadata in PLaMo-Embedding-1B optimized format
with Japanese language processing optimization and vector embedding preparation.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from ..advanced_metadata import AdvancedMetadata
from .base import BaseMetadataExporter


class PlamoReadyExporter(BaseMetadataExporter):
    """PLaMo-Embedding-1B optimized format exporter.
    
    Exports metadata in a format optimized for PLaMo-Embedding-1B processing
    with enhanced Japanese language features and embedding preparation.
    """

    def __init__(self):
        """Initialize PLaMo-ready exporter."""
        super().__init__()

    def export(self, metadata: AdvancedMetadata) -> dict[str, Any]:
        """Export PLaMo-Embedding-1B optimized format.

        Args:
            metadata: Advanced metadata with PLaMo features.

        Returns:
            PLaMo-ready configuration for optimal Japanese embedding generation.
        """
        plamo_features = metadata.plamo_features

        plamo_config = {
            "model_config": self._create_model_config(),
            "preprocessing_config": self._create_preprocessing_config(plamo_features),
            "text_segments": plamo_features.text_segments,
            "japanese_features": plamo_features.japanese_features,
            "embedding_hints": plamo_features.embedding_hints,
            "entity_enhancement": self._create_entity_enhancement(metadata.entity_classification),
            "quality_metrics": self._create_quality_metrics(metadata.data_quality, plamo_features),
            "optimization_config": self._create_optimization_config(plamo_features),
        }

        return plamo_config

    def _create_model_config(self) -> dict[str, Any]:
        """Create PLaMo model configuration.

        Returns:
            Model configuration optimized for PLaMo-Embedding-1B.
        """
        return {
            "model_name": "PLaMo-Embedding-1B",
            "embedding_dimension": 1024,
            "max_sequence_length": 512,
            "batch_size": 32,
            "model_precision": "float16",
            "device_preference": "cuda",
            "fallback_device": "cpu",
        }

    def _create_preprocessing_config(self, plamo_features) -> dict[str, Any]:
        """Create preprocessing configuration for PLaMo.

        Args:
            plamo_features: PLaMo-specific features.

        Returns:
            Preprocessing configuration optimized for Japanese text.
        """
        return {
            "text_segmentation": {
                "strategy": plamo_features.vector_optimization.get(
                    "chunk_strategy", "semantic_boundary"
                ),
                "max_chunk_length": plamo_features.vector_optimization.get(
                    "max_chunk_length", 512
                ),
                "overlap_ratio": plamo_features.vector_optimization.get(
                    "overlap_ratio", 0.1
                ),
                "prioritize_entities": plamo_features.vector_optimization.get(
                    "prioritize_entities", True
                ),
                "sentence_boundary_detection": "japanese_aware",
            },
            "japanese_optimization": {
                "enable_kuromoji": True,
                "normalize_kanji": True,
                "handle_katakana": True,
                "preserve_honorifics": True,
                "business_term_preservation": True,
                "number_normalization": "japanese_style",
            },
            "text_normalization": {
                "unicode_normalization": "NFKC",
                "remove_control_chars": True,
                "preserve_line_breaks": False,
                "whitespace_normalization": "standard",
            },
        }

    def _create_entity_enhancement(self, entity_classification) -> dict[str, Any]:
        """Create entity enhancement configuration.

        Args:
            entity_classification: Entity classification data.

        Returns:
            Entity enhancement configuration for improved embeddings.
        """
        return {
            "persons": [asdict(p) for p in entity_classification.persons],
            "places": [asdict(p) for p in entity_classification.places],
            "organizations": [asdict(o) for o in entity_classification.organizations],
            "business_terms": [asdict(b) for b in entity_classification.business_terms],
            "enhancement_strategies": {
                "entity_highlighting": True,
                "context_expansion": True,
                "confidence_weighting": True,
                "japanese_entity_priority": True,
            },
        }

    def _create_quality_metrics(self, data_quality, plamo_features) -> dict[str, Any]:
        """Create quality metrics for PLaMo processing.

        Args:
            data_quality: Data quality assessment.
            plamo_features: PLaMo-specific features.

        Returns:
            Quality metrics affecting embedding generation.
        """
        return {
            "overall_score": data_quality.overall_score,
            "text_quality_indicators": {
                "formality_level": plamo_features.embedding_hints.get("formality_level"),
                "technical_level": plamo_features.embedding_hints.get("technical_level"),
                "domain": plamo_features.embedding_hints.get("domain"),
                "language_consistency": data_quality.consistency_score,
            },
            "japanese_quality": {
                "kanji_density": plamo_features.japanese_features.get("kanji_ratio", 0.0),
                "vocabulary_richness": plamo_features.japanese_features.get("vocabulary_richness", 0.0),
                "business_term_density": len(plamo_features.embedding_hints.get("business_terms", [])),
            },
            "embedding_quality_prediction": {
                "expected_similarity_accuracy": min(0.95, data_quality.overall_score * 1.1),
                "domain_coherence": plamo_features.embedding_hints.get("domain_coherence", 0.8),
                "japanese_processing_confidence": 0.9,  # PLaMo特化
            },
        }

    def _create_optimization_config(self, plamo_features) -> dict[str, Any]:
        """Create optimization configuration for PLaMo processing.

        Args:
            plamo_features: PLaMo-specific features.

        Returns:
            Optimization configuration for embedding generation.
        """
        return {
            "chunk_optimization": {
                "adaptive_chunking": True,
                "entity_boundary_respect": True,
                "japanese_sentence_awareness": True,
                "business_context_preservation": True,
            },
            "embedding_optimization": {
                "japanese_token_priority": 1.2,
                "entity_token_boost": 1.5,
                "technical_term_boost": 1.3,
                "context_window_expansion": True,
            },
            "batch_processing": {
                "enable_batch_optimization": True,
                "optimal_batch_size": 32,
                "memory_efficiency_mode": True,
                "parallel_processing": True,
            },
            "output_optimization": {
                "vector_precision": "float32",
                "normalization": "l2",
                "dimension_reduction": False,  # PLaMoは1024次元が最適
                "similarity_metric": "cosine",
            },
        }
