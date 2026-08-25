"""config.py - Centralized configuration for AI Pulse.

Design: A single Config dataclass holds all runtime parameters: digest
source directory, output formats, archive cache location, entity lexicon
paths, scoring thresholds, max result counts, logging verbosity, and
custom watchlists. Functions load_config() and save_config() serialize
to JSON for disk persistence. Environment variables override file-based
config for deployment flexibility.
"""

import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path


@dataclass
class Config:
    """Central configuration holder."""
    digest_dir: str = "./digests"
    output_formats: list = field(default_factory=lambda: ["markdown", "json"])
    archive_cache: str = "./cache/archive.json"
    entity_lexicon_path: str = "./data/entities.json"
    importance_threshold: float = 0.5
    momentum_threshold: float = 0.3
    max_search_results: int = 50
    max_report_items: int = 20
    log_level: str = "INFO"
    watchlist_entities: list = field(default_factory=list)

    def to_dict(self):
        """Convert config to dict."""
        return asdict(self)


def load_config(path: str = None) -> Config:
    """Load config from JSON file or use defaults.

    Environment variables override file values with prefix AIPULSE_.
    Example: AIPULSE_DIGEST_DIR=/tmp/digests
    """
    if path and Path(path).exists():
        with open(path) as f:
            data = json.load(f)
            cfg = Config(**data)
    else:
        cfg = Config()

    # Environment variable overrides
    for field_name in cfg.__dataclass_fields__:
        env_key = f"AIPULSE_{field_name.upper()}"
        if env_key in os.environ:
            val = os.environ[env_key]
            setattr(cfg, field_name, val)

    return cfg


def save_config(cfg: Config, path: str) -> None:
    """Save config to JSON file."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(cfg.to_dict(), f, indent=2)

if __name__ == "__main__":
    # Demo: create, modify, and save a config
    cfg = load_config()
    print(f"Loaded config: digest_dir={cfg.digest_dir}")

    cfg.digest_dir = "./digests_prod"
    cfg.log_level = "DEBUG"
    cfg.watchlist_entities = ["OpenAI", "Anthropic", "DeepSeek"]

    save_config(cfg, "/tmp/aipulse_config.json")
    print("Config saved. Demonstrating environment override:")

    # Reload with env override
    os.environ["AIPULSE_LOG_LEVEL"] = "WARN"
    cfg2 = load_config("/tmp/aipulse_config.json")
    print(f"Loaded with env override: log_level={cfg2.log_level}")
    print(f"Watchlist: {cfg2.watchlist_entities}")
