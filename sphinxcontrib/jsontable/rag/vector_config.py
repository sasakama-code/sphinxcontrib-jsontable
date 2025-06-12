"""Vector Processing Configuration Management System.

Advanced configuration system for Phase 3B VectorProcessor optimization
supporting multiple vector processing modes with flexible AI API integration.

Features:
- 3-mode support: local, openai, disabled
- Dynamic configuration loading
- Environment variable integration
- Fallback and validation mechanisms
- Performance optimization settings

Created: 2025-06-12
Author: Claude Code Assistant
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class VectorMode(Enum):
    """Vector processing mode enumeration."""

    LOCAL = "local"
    OPENAI = "openai"
    DISABLED = "disabled"


@dataclass
class VectorConfig:
    """Comprehensive vector processing configuration.

    Supports multiple processing modes with intelligent fallback
    and performance optimization settings.
    """

    # Primary processing mode
    mode: VectorMode = VectorMode.LOCAL

    # Local processing settings
    local_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    local_device: str = "cpu"
    local_max_length: int = 512

    # OpenAI settings
    openai_api_key: str | None = None
    openai_model: str = "text-embedding-3-small"
    openai_timeout: int = 30
    openai_max_retries: int = 3

    # Fallback configuration
    enable_fallback: bool = True
    fallback_mode: VectorMode = VectorMode.LOCAL

    # Performance settings
    batch_size: int = 32
    max_workers: int = 4
    cache_embeddings: bool = True
    cache_dir: str | None = None

    # Japanese optimization
    enable_japanese_optimization: bool = True
    japanese_model_boost: float = 1.2

    # Processing limits
    max_text_length: int = 8192
    embedding_dimension: int = 384

    # Metadata
    config_version: str = "1.0.0"
    custom_settings: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Post-initialization validation and environment variable loading."""
        self._load_environment_variables()
        self._validate_configuration()
        self._setup_cache_directory()

    def _load_environment_variables(self) -> None:
        """Load configuration from environment variables."""
        # Vector mode
        if mode_env := os.getenv("VECTOR_MODE"):
            try:
                self.mode = VectorMode(mode_env.lower())
            except ValueError:
                logger.warning(
                    f"Invalid VECTOR_MODE: {mode_env}, using default: {self.mode}"
                )

        # OpenAI configuration
        if api_key := os.getenv("OPENAI_API_KEY"):
            self.openai_api_key = api_key

        if model := os.getenv("OPENAI_EMBEDDING_MODEL"):
            self.openai_model = model

        # Local model configuration
        if local_model := os.getenv("LOCAL_EMBEDDING_MODEL"):
            self.local_model = local_model

        if device := os.getenv("TORCH_DEVICE"):
            self.local_device = device

        # Performance settings
        if batch_size := os.getenv("VECTOR_BATCH_SIZE"):
            try:
                self.batch_size = int(batch_size)
            except ValueError:
                logger.warning(f"Invalid VECTOR_BATCH_SIZE: {batch_size}")

        # Cache settings
        if cache_dir := os.getenv("VECTOR_CACHE_DIR"):
            self.cache_dir = cache_dir

    def _validate_configuration(self) -> None:
        """Validate configuration consistency and requirements."""
        # OpenAI mode validation
        if self.mode == VectorMode.OPENAI and not self.openai_api_key:
            logger.warning(
                "OpenAI mode selected but no API key provided, falling back to local mode"
            )
            self.mode = VectorMode.LOCAL

        # Fallback mode validation
        if self.enable_fallback and self.fallback_mode == self.mode:
            logger.warning("Fallback mode same as primary mode, disabling fallback")
            self.enable_fallback = False

        # Performance validation
        if self.batch_size <= 0:
            self.batch_size = 32
            logger.warning("Invalid batch_size, reset to 32")

        if self.max_workers <= 0:
            self.max_workers = 4
            logger.warning("Invalid max_workers, reset to 4")

    def _setup_cache_directory(self) -> None:
        """Setup cache directory if caching is enabled."""
        if self.cache_embeddings and not self.cache_dir:
            self.cache_dir = str(
                Path.home() / ".cache" / "sphinxcontrib-jsontable" / "embeddings"
            )

        if self.cache_dir:
            Path(self.cache_dir).mkdir(parents=True, exist_ok=True)

    def is_ai_enabled(self) -> bool:
        """Check if AI processing is enabled."""
        return self.mode in (VectorMode.LOCAL, VectorMode.OPENAI)

    def requires_internet(self) -> bool:
        """Check if configuration requires internet connection."""
        return self.mode == VectorMode.OPENAI

    def get_model_info(self) -> dict[str, Any]:
        """Get current model information."""
        if self.mode == VectorMode.LOCAL:
            return {
                "mode": "local",
                "model": self.local_model,
                "device": self.local_device,
                "max_length": self.local_max_length,
            }
        elif self.mode == VectorMode.OPENAI:
            return {
                "mode": "openai",
                "model": self.openai_model,
                "timeout": self.openai_timeout,
                "max_retries": self.openai_max_retries,
            }
        else:
            return {"mode": "disabled"}

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "mode": self.mode.value,
            "local_model": self.local_model,
            "local_device": self.local_device,
            "openai_model": self.openai_model,
            "batch_size": self.batch_size,
            "max_workers": self.max_workers,
            "cache_embeddings": self.cache_embeddings,
            "enable_japanese_optimization": self.enable_japanese_optimization,
            "config_version": self.config_version,
        }

    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> VectorConfig:
        """Create configuration from dictionary."""
        # Handle mode conversion
        if "mode" in config_dict:
            config_dict["mode"] = VectorMode(config_dict["mode"])

        return cls(**config_dict)

    @classmethod
    def get_default_config(cls) -> VectorConfig:
        """Get default configuration for development."""
        return cls(
            mode=VectorMode.LOCAL,
            enable_fallback=True,
            cache_embeddings=True,
            enable_japanese_optimization=True,
        )

    @classmethod
    def get_production_config(cls) -> VectorConfig:
        """Get optimized configuration for production."""
        return cls(
            mode=VectorMode.OPENAI,
            fallback_mode=VectorMode.LOCAL,
            enable_fallback=True,
            batch_size=64,
            max_workers=8,
            cache_embeddings=True,
            enable_japanese_optimization=True,
        )

    @classmethod
    def get_disabled_config(cls) -> VectorConfig:
        """Get configuration with vector processing disabled."""
        return cls(
            mode=VectorMode.DISABLED, enable_fallback=False, cache_embeddings=False
        )


class VectorConfigManager:
    """Vector configuration management utility."""

    def __init__(self, config_path: str | None = None):
        """Initialize configuration manager.

        Args:
            config_path: Optional path to configuration file.
        """
        self.config_path = config_path
        self._config: VectorConfig | None = None

    def load_config(self) -> VectorConfig:
        """Load configuration from file or environment."""
        if self._config is None:
            if self.config_path and Path(self.config_path).exists():
                self._config = self._load_from_file()
            else:
                self._config = VectorConfig.get_default_config()
                logger.info("Using default vector configuration")

        return self._config

    def _load_from_file(self) -> VectorConfig:
        """Load configuration from JSON file."""
        import json

        try:
            with open(self.config_path, encoding="utf-8") as f:
                config_data = json.load(f)
            return VectorConfig.from_dict(config_data)
        except Exception as e:
            logger.error(f"Failed to load config from {self.config_path}: {e}")
            return VectorConfig.get_default_config()

    def save_config(self, config: VectorConfig) -> None:
        """Save configuration to file."""
        if not self.config_path:
            logger.warning("No config path specified, cannot save configuration")
            return

        import json

        try:
            config_dir = Path(self.config_path).parent
            config_dir.mkdir(parents=True, exist_ok=True)

            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)

            logger.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save config to {self.config_path}: {e}")

    def get_config(self) -> VectorConfig:
        """Get current configuration."""
        return self.load_config()

    def update_config(self, **kwargs) -> VectorConfig:
        """Update configuration with new values."""
        current_config = self.load_config()
        config_dict = current_config.to_dict()
        config_dict.update(kwargs)

        self._config = VectorConfig.from_dict(config_dict)
        return self._config
