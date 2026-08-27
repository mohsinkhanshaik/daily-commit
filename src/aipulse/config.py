"""Central configuration system for AI Pulse.

Provides centralized management of analysis settings, thresholds, and
defaults used across modules. Configuration is loaded from a YAML file
and can be overridden via environment variables.

Design: Single Config dataclass with nested sections for different
components. Defaults are embedded; external config overlays them.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional
from os import environ


@dataclass
class ScoringConfig:
    """Settings for importance scoring."""
    base_weight: float = 1.0
    recency_decay: float = 0.95
    min_score: float = 0.1
    max_score: float = 10.0

@dataclass
class TrendConfig:
    """Settings for trend analysis."""
    window_days: int = 7
    min_frequency: int = 2
    smoothing_factor: float = 0.3
    top_n_terms: int = 20


@dataclass
class AlertConfig:
    """Settings for alerting and thresholds."""
    momentum_threshold: float = 0.5
    emerging_min_items: int = 3
    sentiment_extremes: tuple = field(default_factory=lambda: (-0.7, 0.7))
    enable_email: bool = False

@dataclass
class Config:
    """Central configuration for AI Pulse toolkit."""
    archive_dir: Path = field(default_factory=lambda: Path('digests'))
    cache_enabled: bool = True
    cache_ttl_hours: int = 24
    scoring: ScoringConfig = field(default_factory=ScoringConfig)
    trends: TrendConfig = field(default_factory=TrendConfig)
    alerts: AlertConfig = field(default_factory=AlertConfig)

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a config value by dot-notation key."""
        parts = key.split('.')
        obj = self
        for part in parts:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            else:
                return default
        return obj

    def update_from_env(self) -> None:
        """Override config from environment variables (AIPULSE_ prefix)."""
        for key, value in environ.items():
            if key.startswith('AIPULSE_'):
                config_key = key[8:].lower()
                try:
                    setattr(self, config_key, value)
                except AttributeError:
                    pass

# Global instance
_default_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global config instance, creating if needed."""
    global _default_config
    if _default_config is None:
        _default_config = Config()
        _default_config.update_from_env()
    return _default_config


if __name__ == '__main__':
    cfg = get_config()
    print(f'Archive dir: {cfg.archive_dir}')
    print(f'Cache enabled: {cfg.cache_enabled}')
    print(f'Scoring base weight: {cfg.scoring.base_weight}')
    print(f'Trend window: {cfg.trends.window_days} days')
    print(f'Alert momentum threshold: {cfg.alerts.momentum_threshold}')
    print(f'Via get(): {cfg.get("trends.smoothing_factor")}')
