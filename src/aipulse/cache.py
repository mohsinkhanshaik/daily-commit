"""Simple in-memory caching layer for AI Pulse archive operations.

Provides TTL-based cache for parsed digests, search results, and archive
indices to avoid re-parsing and re-indexing on repeated queries.
"""

import time
from dataclasses import dataclass, field
from typing import Any, Callable, Optional


@dataclass
class CacheEntry:
    """A single cache entry with TTL tracking."""
    value: Any
    timestamp: float = field(default_factory=time.time)
    ttl: int = 3600

    def is_expired(self) -> bool:
        """Check if entry has exceeded its TTL."""
        return time.time() - self.timestamp > self.ttl


class Cache:
    """Thread-unsafe in-memory cache with TTL and invalidation.\"\"\"\n\n    def __init__(self, default_ttl: int = 3600):\n        \"\"\"Initialize cache with default TTL in seconds.\"\"\"\n        self.store = {}\n        self.default_ttl = default_ttl\n        self.hits = 0\n        self.misses = 0\n\n    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:\n        \"\"\"Cache a value with optional custom TTL.\"\"\"\n        self.store[key] = CacheEntry(value, ttl=ttl or self.default_ttl)\n\n    def get(self, key: str) -> Optional[Any]:\n        \"\"\"Retrieve a cached value, or None if missing/expired.\"\"\"\n        if key not in self.store:\n            self.misses += 1\n            return None\n\n        entry = self.store[key]\n        if entry.is_expired():\n            del self.store[key]\n            self.misses += 1\n            return None\n\n        self.hits += 1\n        return entry.value

    def invalidate(self, key: str) -> None:\n        \"\"\"Remove a specific key from cache.\"\"\"\n        self.store.pop(key, None)\n\n    def clear(self) -> None:\n        \"\"\"Clear all cached entries.\"\"\"\n        self.store.clear()\n\n    def prune_expired(self) -> int:\n        \"\"\"Remove all expired entries, return count.\"\"\"\n        expired = [k for k, v in self.store.items() if v.is_expired()]\n        for k in expired:\n            del self.store[k]\n        return len(expired)\n\n    def stats(self) -> dict:\n        \"\"\"Return cache statistics.\"\"\"\n        return {\n            'size': len(self.store),\n            'hits': self.hits,\n            'misses': self.misses,\n            'hitrate': self.hits / (self.hits + self.misses) if self.hits + self.misses > 0 else 0\n        }\n\n\nif __name__ == '__main__':\n    cache = Cache(default_ttl=10)\n    print(\"AI Pulse Archive Cache Demo\")\n    print(\"============================\")\n    cache.set('digest_2026-08-21', {'items': 42, 'sources': 15})\n    cache.set('search_llm', [{'title': 'New LLM', 'date': '2026-08-22'}])\n    print(f\"Cached: digest and search results\")\n    print(f\"Cache size: {cache.stats()['size']}\")\n    result = cache.get('digest_2026-08-21')\n    print(f\"Hit on digest: {result}\")\n    cache.get('missing_key')\n    cache.invalidate('search_llm')\n    print(f\"After invalidate: {cache.stats()}\")
