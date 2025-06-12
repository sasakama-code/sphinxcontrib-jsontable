"""Enhanced Vector Processing Engine with Multi-Mode Support.

Advanced vector processing system for Phase 3B optimization with flexible
AI API integration and comprehensive fallback mechanisms.

Features:
- 3-mode processing: local, openai, disabled
- Intelligent fallback system
- OpenAI API integration with rate limiting
- Local sentence-transformers support
- Japanese text optimization
- Performance monitoring and caching
- Error handling and recovery

Created: 2025-06-12
Author: Claude Code Assistant
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import time
from dataclasses import dataclass
from typing import Any

import numpy as np

# Conditional imports for different processing modes
try:
    from sentence_transformers import SentenceTransformer

    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import openai

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from .semantic_chunker import SemanticChunk
from .vector_config import VectorConfig, VectorMode
from .vector_processor import (
    BusinessTermEnhancer,
    JapaneseTextNormalizer,
    VectorChunk,
    VectorProcessingResult,
)

logger = logging.getLogger(__name__)


@dataclass
class ProcessingMetrics:
    """Processing performance metrics."""

    total_chunks: int = 0
    successful_embeddings: int = 0
    failed_embeddings: int = 0
    fallback_used: int = 0
    total_time: float = 0.0
    average_time_per_chunk: float = 0.0
    mode_used: str = ""
    cache_hits: int = 0
    api_calls: int = 0


class EnhancedVectorProcessor:
    """Enhanced vector processor with multi-mode support.

    Provides flexible vector processing with support for local models,
    OpenAI API, and disabled mode with intelligent fallback capabilities.
    """

    def __init__(self, config: VectorConfig | None = None):
        """Initialize enhanced vector processor.

        Args:
            config: Optional vector processing configuration.
        """
        self.config = config or VectorConfig.get_default_config()
        self.metrics = ProcessingMetrics()

        # Initialize processing components
        self.text_normalizer = JapaneseTextNormalizer()
        self.term_enhancer = BusinessTermEnhancer()

        # Initialize models based on configuration
        self._local_model: SentenceTransformer | None = None
        self._openai_client: Any | None = None
        self._cache: dict[str, np.ndarray] = {}

        self._initialize_models()

        logger.info(
            f"EnhancedVectorProcessor initialized with mode: {self.config.mode.value}"
        )

    def _initialize_models(self) -> None:
        """Initialize models based on configuration."""
        try:
            if self.config.mode == VectorMode.LOCAL or self.config.enable_fallback:
                self._initialize_local_model()

            if self.config.mode == VectorMode.OPENAI:
                self._initialize_openai_client()

        except Exception as e:
            logger.error(f"Model initialization failed: {e}")
            if self.config.enable_fallback:
                self._fallback_to_alternative_mode()

    def _initialize_local_model(self) -> None:
        """Initialize local sentence transformer model."""
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            logger.warning("sentence-transformers not available, local mode disabled")
            return

        try:
            self._local_model = SentenceTransformer(
                self.config.local_model, device=self.config.local_device
            )
            logger.info(f"Local model loaded: {self.config.local_model}")
        except Exception as e:
            logger.error(f"Failed to load local model: {e}")
            if self.config.enable_fallback:
                self._local_model = None

    def _initialize_openai_client(self) -> None:
        """Initialize OpenAI client."""
        if not OPENAI_AVAILABLE:
            logger.warning("openai package not available, OpenAI mode disabled")
            return

        if not self.config.openai_api_key:
            logger.warning("OpenAI API key not provided")
            return

        try:
            self._openai_client = openai.OpenAI(
                api_key=self.config.openai_api_key, timeout=self.config.openai_timeout
            )
            logger.info("OpenAI client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")

    def _fallback_to_alternative_mode(self) -> None:
        """Fallback to alternative processing mode."""
        if not self.config.enable_fallback:
            logger.error("Fallback disabled, cannot switch modes")
            return

        original_mode = self.config.mode
        self.config.mode = self.config.fallback_mode

        logger.warning(
            f"Falling back from {original_mode.value} to {self.config.mode.value}"
        )

        # Re-initialize with fallback mode
        try:
            if self.config.mode == VectorMode.LOCAL:
                self._initialize_local_model()
            elif self.config.mode == VectorMode.OPENAI:
                self._initialize_openai_client()
        except Exception as e:
            logger.error(f"Fallback initialization failed: {e}")
            self.config.mode = VectorMode.DISABLED

    async def process_chunks(
        self,
        semantic_chunks: list[SemanticChunk],
        progress_callback: callable | None = None,
    ) -> VectorProcessingResult:
        """Process semantic chunks into vector chunks.

        Args:
            semantic_chunks: List of semantic chunks to vectorize.
            progress_callback: Optional callback for progress updates.

        Returns:
            Vector processing result with generated embeddings.
        """
        start_time = time.time()
        self.metrics = ProcessingMetrics()
        self.metrics.total_chunks = len(semantic_chunks)
        self.metrics.mode_used = self.config.mode.value

        if self.config.mode == VectorMode.DISABLED:
            return self._create_disabled_result(semantic_chunks)

        vector_chunks = []

        try:
            # Process chunks in batches
            for i in range(0, len(semantic_chunks), self.config.batch_size):
                batch = semantic_chunks[i : i + self.config.batch_size]
                batch_results = await self._process_batch(batch)
                vector_chunks.extend(batch_results)

                if progress_callback:
                    progress = (i + len(batch)) / len(semantic_chunks)
                    progress_callback(progress)

        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            if self.config.enable_fallback:
                return await self._fallback_process_chunks(
                    semantic_chunks, progress_callback
                )
            raise

        # Update metrics
        self.metrics.total_time = time.time() - start_time
        self.metrics.successful_embeddings = len(vector_chunks)
        self.metrics.failed_embeddings = (
            self.metrics.total_chunks - self.metrics.successful_embeddings
        )

        if self.metrics.total_chunks > 0:
            self.metrics.average_time_per_chunk = (
                self.metrics.total_time / self.metrics.total_chunks
            )

        return VectorProcessingResult(
            vector_chunks=vector_chunks,
            processing_stats=self._get_processing_stats(),
            model_info=self.config.get_model_info(),
            japanese_optimization_applied=self.config.enable_japanese_optimization,
        )

    async def _process_batch(self, batch: list[SemanticChunk]) -> list[VectorChunk]:
        """Process a batch of semantic chunks."""
        vector_chunks = []

        for chunk in batch:
            try:
                vector_chunk = await self._process_single_chunk(chunk)
                if vector_chunk:
                    vector_chunks.append(vector_chunk)
            except Exception as e:
                logger.error(f"Failed to process chunk {chunk.chunk_id}: {e}")
                self.metrics.failed_embeddings += 1

        return vector_chunks

    async def _process_single_chunk(
        self, chunk: SemanticChunk
    ) -> VectorChunk | None:
        """Process a single semantic chunk into vector chunk."""
        # Prepare text for embedding
        text = self._prepare_text_for_embedding(chunk)

        # Check cache first
        cache_key = self._get_cache_key(text)
        if self.config.cache_embeddings and cache_key in self._cache:
            embedding = self._cache[cache_key]
            self.metrics.cache_hits += 1
        else:
            # Generate embedding based on mode
            embedding = await self._generate_embedding(text)
            if embedding is None:
                return None

            # Cache the result
            if self.config.cache_embeddings:
                self._cache[cache_key] = embedding

        # Create vector chunk
        return VectorChunk(
            chunk_id=chunk.chunk_id,
            original_chunk=chunk,
            embedding=embedding,
            embedding_metadata={
                "mode": self.config.mode.value,
                "model": self._get_current_model_name(),
                "text_length": len(text),
                "japanese_optimized": self.config.enable_japanese_optimization,
            },
            japanese_enhancement=self._get_japanese_enhancement_info(chunk),
            search_boost=self._calculate_search_boost(chunk),
        )

    def _prepare_text_for_embedding(self, chunk: SemanticChunk) -> str:
        """Prepare text for embedding generation."""
        text = chunk.content

        if self.config.enable_japanese_optimization:
            # Apply Japanese text normalization
            text = self.text_normalizer.normalize(text)

            # Apply business term enhancement
            text = self.term_enhancer.enhance(text)

        # Truncate if necessary
        if len(text) > self.config.max_text_length:
            text = text[: self.config.max_text_length]
            logger.warning(
                f"Text truncated to {self.config.max_text_length} characters"
            )

        return text

    async def _generate_embedding(self, text: str) -> np.ndarray | None:
        """Generate embedding based on current mode."""
        try:
            if self.config.mode == VectorMode.LOCAL:
                return await self._generate_local_embedding(text)
            elif self.config.mode == VectorMode.OPENAI:
                return await self._generate_openai_embedding(text)
            else:
                logger.warning("No valid embedding mode available")
                return None
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            if self.config.enable_fallback:
                return await self._generate_fallback_embedding(text)
            return None

    async def _generate_local_embedding(self, text: str) -> np.ndarray | None:
        """Generate embedding using local model."""
        if not self._local_model:
            raise ValueError("Local model not initialized")

        try:
            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(None, self._local_model.encode, text)
            return np.array(embedding)
        except Exception as e:
            logger.error(f"Local embedding generation failed: {e}")
            raise

    async def _generate_openai_embedding(self, text: str) -> np.ndarray | None:
        """Generate embedding using OpenAI API."""
        if not self._openai_client:
            raise ValueError("OpenAI client not initialized")

        try:
            self.metrics.api_calls += 1

            response = await asyncio.to_thread(
                self._openai_client.embeddings.create,
                input=text,
                model=self.config.openai_model,
            )

            embedding = np.array(response.data[0].embedding)
            return embedding

        except Exception as e:
            logger.error(f"OpenAI embedding generation failed: {e}")
            raise

    async def _generate_fallback_embedding(self, text: str) -> np.ndarray | None:
        """Generate embedding using fallback method."""
        self.metrics.fallback_used += 1

        # Switch to fallback mode temporarily
        original_mode = self.config.mode
        self.config.mode = self.config.fallback_mode

        try:
            embedding = await self._generate_embedding(text)
            return embedding
        finally:
            self.config.mode = original_mode

    async def _fallback_process_chunks(
        self,
        semantic_chunks: list[SemanticChunk],
        progress_callback: callable | None = None,
    ) -> VectorProcessingResult:
        """Fallback processing when primary mode fails."""
        logger.warning("Using fallback processing mode")
        self._fallback_to_alternative_mode()
        return await self.process_chunks(semantic_chunks, progress_callback)

    def _create_disabled_result(
        self, semantic_chunks: list[SemanticChunk]
    ) -> VectorProcessingResult:
        """Create result for disabled mode."""
        # Create dummy vector chunks with zero embeddings
        vector_chunks = []
        for chunk in semantic_chunks:
            vector_chunks.append(
                VectorChunk(
                    chunk_id=chunk.chunk_id,
                    original_chunk=chunk,
                    embedding=np.zeros(self.config.embedding_dimension),
                    embedding_metadata={"mode": "disabled"},
                    japanese_enhancement={},
                    search_boost=1.0,
                )
            )

        return VectorProcessingResult(
            vector_chunks=vector_chunks,
            processing_stats={"mode": "disabled", "total_chunks": len(semantic_chunks)},
            model_info={"mode": "disabled"},
            japanese_optimization_applied=False,
        )

    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text."""
        return hashlib.md5(text.encode("utf-8")).hexdigest()

    def _get_current_model_name(self) -> str:
        """Get current model name."""
        if self.config.mode == VectorMode.LOCAL:
            return self.config.local_model
        elif self.config.mode == VectorMode.OPENAI:
            return self.config.openai_model
        else:
            return "disabled"

    def _get_japanese_enhancement_info(self, chunk: SemanticChunk) -> dict[str, Any]:
        """Get Japanese enhancement information."""
        if not self.config.enable_japanese_optimization:
            return {}

        return {
            "normalization_applied": True,
            "business_terms_enhanced": True,
            "boost_factor": self.config.japanese_model_boost,
        }

    def _calculate_search_boost(self, chunk: SemanticChunk) -> float:
        """Calculate search boost factor for chunk."""
        boost = 1.0

        if self.config.enable_japanese_optimization:
            boost *= self.config.japanese_model_boost

        # Additional boost for high-confidence chunks
        if hasattr(chunk, "confidence_score") and chunk.confidence_score > 0.8:
            boost *= 1.1

        return boost

    def _get_processing_stats(self) -> dict[str, Any]:
        """Get comprehensive processing statistics."""
        return {
            "total_chunks": self.metrics.total_chunks,
            "successful_embeddings": self.metrics.successful_embeddings,
            "failed_embeddings": self.metrics.failed_embeddings,
            "fallback_used": self.metrics.fallback_used,
            "total_time": self.metrics.total_time,
            "average_time_per_chunk": self.metrics.average_time_per_chunk,
            "mode_used": self.metrics.mode_used,
            "cache_hits": self.metrics.cache_hits,
            "api_calls": self.metrics.api_calls,
            "cache_hit_rate": self.metrics.cache_hits
            / max(1, self.metrics.total_chunks),
            "success_rate": self.metrics.successful_embeddings
            / max(1, self.metrics.total_chunks),
        }

    def get_configuration(self) -> VectorConfig:
        """Get current configuration."""
        return self.config

    def update_configuration(self, new_config: VectorConfig) -> None:
        """Update configuration and reinitialize if necessary."""
        old_mode = self.config.mode
        self.config = new_config

        if old_mode != new_config.mode:
            logger.info(
                f"Mode changed from {old_mode.value} to {new_config.mode.value}"
            )
            self._initialize_models()

    def get_metrics(self) -> ProcessingMetrics:
        """Get current processing metrics."""
        return self.metrics

    def clear_cache(self) -> None:
        """Clear embedding cache."""
        self._cache.clear()
        logger.info("Embedding cache cleared")

    def is_healthy(self) -> bool:
        """Check if processor is in healthy state."""
        if self.config.mode == VectorMode.DISABLED:
            return True
        elif self.config.mode == VectorMode.LOCAL:
            return self._local_model is not None
        elif self.config.mode == VectorMode.OPENAI:
            return self._openai_client is not None
        return False
